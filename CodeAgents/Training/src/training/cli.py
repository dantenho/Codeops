"""
[CREATE] Training System CLI

Command-line interface for the Agent Training System.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:00:00Z
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import random
import time
import uuid

import typer
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .models.activity import ActivityResult, ActivityType
from .models.session import SessionType
from .models.token_metrics import TokenBudget
from .services.memory_service import MemoryService
from .services.reflex_service import ReflexService
from .services.token_tracker import TokenTracker
from .services.training_manager import TrainingManager

app = typer.Typer(
    name="training",
    help="Agent Training System (ATS) - SkeletalMind",
    no_args_is_help=True,
)
console = Console()

TRAINING_ROOT = Path(__file__).parent.parent.parent
PROJECT_ROOT = TRAINING_ROOT.parent.parent
FLASHCARD_DECKS_DIR = TRAINING_ROOT / "Flashcards" / "decks"

token_tracker = TokenTracker(PROJECT_ROOT / "token_metrics")

# Initialize services
training_manager = TrainingManager(TRAINING_ROOT)
reflex_service = ReflexService(TRAINING_ROOT)
memory_service = MemoryService()


def _load_token_budget_config() -> Dict[str, Any]:
    config_path = PROJECT_ROOT / "config" / "token_budgets.yaml"
    if not config_path.exists():
        return {}

    with open(config_path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


TOKEN_BUDGET_CONFIG = _load_token_budget_config()


@app.command()
def init(
    agent: str = typer.Argument(..., help="Agent ID to initialize"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing profile"),
) -> None:
    """Initialize a new agent profile."""
    existing = training_manager.get_progress(agent)
    if existing and not force:
        console.print(
            "[yellow]⚠ Agent already initialized. Use --force to recreate the profile.[/yellow]"
        )
        raise typer.Exit(0)

    if existing and force:
        training_manager.progress_repo.delete(agent)  # type: ignore[attr-defined]

    progress = training_manager.initialize_agent(agent)
    console.print(f"[green]✅ Initialized profile for {agent} (level {progress.current_level})[/green]")


@app.command()
def start(
    agent: str = typer.Argument(..., help="Agent ID"),
    session_type: str = typer.Option("daily", "--type", "-t", help="Session type"),
    topic: Optional[str] = typer.Option(None, "--topic", help="Topic to focus on for solo sessions"),
) -> None:
    """Start a training session."""
    console.print(f"[blue]Starting {session_type} session for {agent}[/blue]")

    if session_type == "solo":
        if not topic:
            console.print("[red]Error: --topic is required for solo sessions.[/red]")
            raise typer.Exit(1)

        result = _run_training_session(agent, topic)
        console.print(
            f"[green]Solo session complete. Score={result['score']:.2f} | File Reads={result['files_processed']}[/green]"
        )
        return

    try:
        session_enum = SessionType(session_type)
    except ValueError:
        console.print(f"[red]Unknown session type: {session_type}[/red]")
        raise typer.Exit(1)

    session = training_manager.start_session(agent, session_enum)

    table = Table(title=f"{session_enum.value.replace('_', ' ').title()} Activities")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Type")
    table.add_column("XP", justify="right")
    table.add_column("Difficulty", justify="right")

    for activity in session.activities:
        table.add_row(
            activity.activity_id.split("-")[0],
            activity.title,
            activity.activity_type.value,
            str(activity.xp_reward),
            str(activity.difficulty),
        )

    if session.activities:
        console.print(table)
    else:
        console.print("[yellow]No activities generated for this session yet.[/yellow]")

    warnings = _complete_structured_session(agent, session)
    progress = training_manager.update_progress_after_session(agent, session)

    summary = token_tracker.get_session_summary(session.session_id)
    console.print(
        f"[green]✅ Session complete. XP earned: {session.total_xp_earned}, "
        f"Level: {progress.current_level}, Avg quality: {summary.average_quality_score:.1f}[/green]"
    )

    if warnings:
        console.print("[yellow]Token Budget Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")

    suggestions = token_tracker.analyze_optimization_opportunities(session.session_id)
    if suggestions:
        console.print("\n[blue]Optimization Suggestions[/blue]")
        for suggestion in suggestions:
            console.print(f"  • ({suggestion.priority}) {suggestion.description}")


@app.command("threndia-sync")
def threndia_sync(
    agent: str = typer.Argument(..., help="Agent ID configured for Threndia"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate sync without logging"),
) -> None:
    """Sync Threndia intel packets and emit telemetry."""
    console.print(f"[blue]🔗 Threndia sync for {agent} (dry_run={dry_run})[/blue]")
    try:
        summary = training_manager.threndia_service.sync_intel(agent, dry_run=dry_run)
        console.print(
            f"[green]Batch {summary['intel_batch_id']} with {summary['payload_count']} payload(s) from {len(summary['sources'])} source(s).[/green]"
        )
    except Exception as exc:
        console.print(f"[red]Threndia sync failed: {exc}[/red]")


@app.command("market-analysis")
def market_analysis(
    agent: str = typer.Argument(..., help="Agent ID"),
) -> None:
    """Run a Threndia-informed market analysis session."""
    console.print(f"[blue]📊 Launching market analysis session for {agent}[/blue]")
    try:
        session = training_manager.start_session(agent, SessionType.MARKET_ANALYSIS)
        metadata = training_manager.get_threndia_metadata(agent) or {}

        table = Table(title=f"Market Analysis Activities ({len(session.activities)})")
        table.add_column("Title", style="cyan")
        table.add_column("Source", style="magenta")
        table.add_column("XP", justify="right")

        for activity in session.activities:
            source = activity.metadata.get("source") if activity.metadata else "n/a"
            table.add_row(activity.title, str(source), str(activity.xp_reward))

        console.print(table)
        console.print(f"[dim]Focus areas: {', '.join(session.focus_areas) or 'n/a'}[/dim]")

        session.complete()
        training_manager.threndia_service.record_market_session(session, metadata)
        console.print("[green]✅ Market analysis session logged[/green]")
    except Exception as exc:
        console.print(f"[red]Market analysis session failed: {exc}[/red]")

def _run_training_session(
    agent: str,
    topic: str,
    fatigue_level: float = 0.0,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Runs a single training session and returns the score."""
    session_identifier = session_id or f"solo-{agent}-{uuid.uuid4().hex[:8]}"
    if topic == "dsa":
        dsa_dirs = [
            "Level_02_Intermediate/07_data_structures",
            "Level_02_Intermediate/08_algorithms",
        ]
        base_path = Path("SkeletalStructure")
        start_time = time.time()

        try:
            # Simulate work
            time.sleep(0.1 + fatigue_level) # Fatigue slows down processing

            # Simulate reading files (mocked for now if dirs don't exist)
            files_processed = 0
            for dsa_dir in dsa_dirs:
                dir_path = base_path / dsa_dir
                if dir_path.exists() and dir_path.is_dir():
                    for file_path in dir_path.glob("*.py"):
                        files_processed += 1
                        # console.print(f"[dim]Processing {file_path.name}...[/dim]")
                        with open(file_path, "r") as f:
                            content = f.read()
                            memory_service.add_training_material(topic, file_path.name, content, agent_id=agent)

            # Simulate error based on fatigue
            if random.random() < (0.05 + fatigue_level * 0.5):
                raise Exception("Simulated cognitive fatigue error")

            end_time = time.time()
            time_taken = end_time - start_time

            # Score calculation: 100 base - time penalty
            score = max(0, 100 - (time_taken * 10))

            metrics = {
                "fatigue_level": fatigue_level,
                "files_processed": files_processed,
                "session_type": "solo_dsa"
            }

            memory_service.add_score(topic, score, time_taken, agent_id=agent, metrics=metrics)
            memory_service.log_daily_activity(agent, "training_session", {"topic": topic, "score": score, "status": "success"})

            summary = _record_simulation_tokens(
                session_identifier,
                agent,
                files_processed=files_processed,
                fatigue_level=fatigue_level,
                score=score,
            )

            return {
                "score": score,
                "files_processed": files_processed,
                "session_id": session_identifier,
                "token_summary": summary.model_dump() if summary else None,
            }

        except Exception as e:
            end_time = time.time()
            time_taken = end_time - start_time
            memory_service.add_error(str(e), f"Error during solo training on {topic}", agent_id=agent)
            memory_service.log_daily_activity(agent, "training_error", {"topic": topic, "error": str(e)})
            console.print(f"[red]Error during training: {e}[/red]")
            return {
                "score": 0.0,
                "files_processed": files_processed,
                "session_id": session_identifier,
                "token_summary": None,
            }
    else:
        console.print(f"[red]Error: Unknown topic {topic}[/red]")
        return {"score": 0.0, "files_processed": 0, "session_id": session_identifier, "token_summary": None}

@app.command()
def simulate(
    agent: str = typer.Argument(..., help="Agent ID"),
    topic: str = typer.Option("dsa", "--topic", help="Topic to simulate"),
    iterations: int = typer.Option(10, "--iterations", "-i", help="Number of iterations"),
) -> None:
    """Simulate training over time until performance degrades."""
    console.print(f"[bold blue]🚀 Starting Simulation for {agent} on {topic}[/bold blue]")

    scores: List[float] = []
    fatigue = 0.0
    session_results: List[Dict[str, Any]] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"Simulating {iterations} sessions...", total=iterations)

        for i in range(iterations):
            progress.update(task, description=f"Session {i+1}/{iterations} (Fatigue: {fatigue:.2f})")

            session_id = f"sim-{agent}-{i}"
            result = _run_training_session(agent, topic, fatigue_level=fatigue, session_id=session_id)
            scores.append(result["score"])
            session_results.append(result)

            # Increase fatigue
            fatigue += 0.1

            # Log daily summary every 5 iterations
            if (i + 1) % 5 == 0:
                avg_score = sum(scores[-5:]) / 5
                memory_service.log_daily_activity(agent, "daily_summary", {
                    "average_score": avg_score,
                    "fatigue_level": fatigue,
                    "sessions_completed": i + 1
                })

            time.sleep(0.1) # Brief pause

    # Report results
    console.print("\n[bold green]Simulation Complete![/bold green]")
    table = Table(title="Simulation Results")
    table.add_column("Session", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Fatigue", justify="right")

    for i, score in enumerate(scores):
        color = "green" if score > 80 else "yellow" if score > 50 else "red"
        table.add_row(str(i+1), f"[{color}]{score:.2f}[/{color}]", f"{i * 0.1:.2f}")

    console.print(table)

    total_tokens = sum(
        summary["total_tokens"]
        for summary in (r["token_summary"] for r in session_results)
        if summary
    )
    console.print(f"\n[blue]Total Tokens Consumed:[/blue] {int(total_tokens)}")

    recent_suggestions = []
    for result in session_results[-3:]:
        recent_suggestions.extend(token_tracker.analyze_optimization_opportunities(result["session_id"]))

    if recent_suggestions:
        console.print("\n[magenta]Recent Optimization Opportunities[/magenta]")
        for suggestion in recent_suggestions[:5]:
            console.print(f"  • {suggestion.description} (est. save {suggestion.estimated_tokens_saved} tokens)")

    if scores[-1] < scores[0]:
        console.print(f"\n[red]📉 Performance degraded by {scores[0] - scores[-1]:.2f} points due to fatigue.[/red]")
    else:
        console.print("\n[green]📈 Performance remained stable.[/green]")


@app.command()
def recall(
    topic: str = typer.Argument(..., help="Topic to recall"),
) -> None:
    """Recall information from memory."""
    console.print(f"[blue]Recalling information for topic: {topic}[/blue]")
    results = memory_service.recall_training_material(topic)
    if results and results['documents']:
        for doc in results['documents']:
            console.print(f"[green]--- Recalled Document ---[/green]")
            console.print(doc)
            console.print(f"[green]--- End of Document ---[/green]")
    else:
        console.print(f"[yellow]No information found for topic: {topic}[/yellow]")


@app.command()
def progress(
    agent: str = typer.Argument(..., help="Agent ID"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed stats"),
) -> None:
    """View agent progress."""
    progress = training_manager.get_progress(agent)
    if not progress:
        console.print("[red]No progress found. Initialize the agent first with `training init`.[/red]")
        raise typer.Exit(1)

    stats = token_tracker.get_agent_stats(agent)

    table = Table(title=f"{agent} Progress Overview")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Level", str(progress.current_level))
    table.add_row("Total XP", str(progress.xp.total))
    table.add_row("Daily Streak", str(progress.daily_streak.current))
    table.add_row("Sessions Completed", str(progress.completions.sessions_completed))
    if progress.last_activity:
        table.add_row("Last Activity", progress.last_activity.isoformat())
    table.add_row("Avg Tokens/Session", f"{stats.avg_tokens_per_session:.0f}")
    table.add_row("Avg Quality Score", f"{stats.avg_quality_score:.1f}")
    console.print(table)

    if detailed:
        _print_xp_breakdown(progress)
        _print_badges(progress)


@app.command()
def recommend(
    agent: str = typer.Argument(..., help="Agent ID"),
) -> None:
    """Get next session recommendation."""
    recommendation = _build_recommendation(agent)
    if not recommendation:
        console.print("[red]No profile found. Initialize the agent first.[/red]")
        raise typer.Exit(1)

    console.print(f"[green]Suggested session:[/green] {recommendation['session_type']}")
    if recommendation.get("focus"):
        console.print(f"[blue]Focus Area:[/blue] {recommendation['focus']}")
    console.print(f"[dim]{recommendation['reason']}[/dim]")


@app.command()
def flashcards(
    agent: str = typer.Argument(..., help="Agent ID"),
    deck: Optional[str] = typer.Option(None, "--deck", "-d", help="Specific deck ID"),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of cards to preview"),
    list_only: bool = typer.Option(False, "--list", help="Only list available decks"),
) -> None:
    """Review flashcards."""
    deck_paths = sorted(FLASHCARD_DECKS_DIR.glob("*.json"))
    if not deck_paths:
        console.print("[yellow]No flashcard decks found.[/yellow]")
        return

    if list_only:
        console.print("[green]Available decks:[/green]")
        for path in deck_paths:
            console.print(f"  • {path.stem}")
        return

    if not deck:
        deck_path = deck_paths[0]
    else:
        deck_path = FLASHCARD_DECKS_DIR / (deck if deck.endswith(".json") else f"{deck}.json")
        if not deck_path.exists():
            console.print(f"[red]Deck not found: {deck_path.name}[/red]")
            return

    with open(deck_path, "r", encoding="utf-8") as handle:
        deck_data = json.load(handle)

    cards = deck_data.get("cards", [])[:limit]
    console.print(f"[blue]Reviewing {len(cards)} card(s) from {deck_data.get('name')}[/blue]")
    for idx, card in enumerate(cards, 1):
        console.print(f"\n[cyan]{idx}. {card['front'].get('question')}[/cyan]")
        hints = card["front"].get("hints", [])
        if hints:
            console.print(f"[dim]Hints: {', '.join(hints)}[/dim]")
        console.print(f"[green]Answer:[/green] {card['back'].get('answer')}")

    memory_service.log_daily_activity(
        agent,
        "flashcard_review",
        {"deck": deck_data.get("deck_id"), "cards_viewed": len(cards)},
    )


@app.command()
def leaderboard(
    top: int = typer.Option(10, "--top", "-t"),
) -> None:
    """View training leaderboard."""
    progress_map = training_manager.progress_repo.load_all()  # type: ignore[attr-defined]
    if not progress_map:
        console.print("[yellow]No agents have recorded progress yet.[/yellow]")
        return

    ranked = sorted(progress_map.values(), key=lambda p: p.xp.total, reverse=True)[:top]
    table = Table(title="Agent Leaderboard")
    table.add_column("#", justify="right")
    table.add_column("Agent")
    table.add_column("Level", justify="right")
    table.add_column("XP", justify="right")
    table.add_column("Streak", justify="right")

    for idx, progress in enumerate(ranked, 1):
        table.add_row(
            str(idx),
            progress.agent_id,
            str(progress.current_level),
            str(progress.xp.total),
            str(progress.daily_streak.current),
        )

    console.print(table)


@app.command()
def report(
    agent: str = typer.Argument(..., help="Agent ID"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Generate progress report."""
    progress = training_manager.get_progress(agent)
    if not progress:
        console.print("[red]Agent not found. Initialize the agent first.[/red]")
        raise typer.Exit(1)

    stats = token_tracker.get_agent_stats(agent)
    recommendation = _build_recommendation(agent) or {}

    report_data = {
        "agent": agent,
        "level": progress.current_level,
        "xp": progress.xp.model_dump(),
        "streak": progress.daily_streak.model_dump(),
        "token_stats": stats.model_dump(),
        "recommendation": recommendation,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf-8") as handle:
            json.dump(report_data, handle, indent=2, default=str)
        console.print(f"[green]Report written to {output}[/green]")
    else:
        console.print(json.dumps(report_data, indent=2))


def _complete_structured_session(agent: str, session) -> List[str]:
    warnings: List[str] = []
    for activity in session.activities:
        start_time = datetime.now(timezone.utc)
        duration_factor = random.uniform(0.6, 1.4)
        completed_at = start_time + timedelta(
            minutes=activity.estimated_duration_minutes * duration_factor
        )
        score = max(60.0, min(100.0, 85 + random.uniform(-12, 8)))
        result = ActivityResult(
            activity=activity,
            started_at=start_time,
            completed_at=completed_at,
            score=score,
            passed=score >= 70,
            xp_earned=activity.xp_reward,
        )
        session.record_result(result)
        warnings.extend(
            _record_token_usage(
                session.session_id,
                agent,
                activity,
                score,
            )
        )

    session.complete()
    return warnings


def _record_token_usage(
    session_id: str,
    agent_id: str,
    activity,
    score: float,
) -> List[str]:
    prompt_tokens = 180 + activity.difficulty * 30
    context_tokens = 100 + activity.difficulty * 40
    user_input_tokens = 60 + activity.difficulty * 10
    completion_tokens = 140 + activity.difficulty * 35
    cached_tokens = 25 + activity.difficulty * 5

    metrics = token_tracker.record_operation(
        session_id=session_id,
        agent_id=agent_id,
        operation_id=activity.activity_id,
        prompt_tokens=prompt_tokens,
        context_tokens=context_tokens,
        user_input_tokens=user_input_tokens,
        completion_tokens=completion_tokens,
        cached_tokens=cached_tokens,
        output_quality_score=score,
        context_utilization_score=max(50, min(95, 75 + random.uniform(-15, 15))),
        operation_type=activity.activity_type.value,
        language=activity.language or "python",
    )

    warnings: List[str] = []
    budget_key = _budget_key_for_activity(activity.activity_type)
    budget = _get_operation_budget(budget_key)
    if budget:
        budget_result = token_tracker.check_budget(metrics, budget)
        warnings.extend(budget_result.get("warnings", []))
    return warnings


def _record_simulation_tokens(
    session_id: str,
    agent_id: str,
    files_processed: int,
    fatigue_level: float,
    score: float,
):
    prompt_tokens = 120 + files_processed * 20
    context_tokens = files_processed * 40
    completion_tokens = 100 + int(score)
    cached_tokens = max(0, int(prompt_tokens * 0.1))

    metrics = token_tracker.record_operation(
        session_id=session_id,
        agent_id=agent_id,
        operation_id=f"{session_id}-summary",
        prompt_tokens=prompt_tokens,
        context_tokens=context_tokens,
        user_input_tokens=80,
        completion_tokens=completion_tokens,
        cached_tokens=cached_tokens,
        output_quality_score=score,
        context_utilization_score=max(40, 80 - fatigue_level * 10),
        operation_type="coding_exercise",
        language="python",
    )

    budget = _get_operation_budget("coding_exercise")
    if budget:
        token_tracker.check_budget(metrics, budget)

    return token_tracker.get_session_summary(session_id)


def _get_operation_budget(operation_key: str) -> Optional[TokenBudget]:
    operations = TOKEN_BUDGET_CONFIG.get("operations", {})
    data = operations.get(operation_key)
    if not data:
        return None
    payload = {"operation_type": operation_key}
    payload.update(data)
    return TokenBudget(**payload)


def _budget_key_for_activity(activity_type: ActivityType) -> str:
    mapping = {
        ActivityType.SYNTAX_DRILL: "coding_exercise",
        ActivityType.CODING_EXERCISE: "coding_exercise",
        ActivityType.ALGORITHM_CHALLENGE: "coding_exercise",
        ActivityType.ASSESSMENT: "assessment",
        ActivityType.FLASHCARD_REVIEW: "flashcard_review",
        ActivityType.REFLECTION: "flashcard_review",
        ActivityType.RESEARCH: "coding_exercise",
    }
    return mapping.get(activity_type, "coding_exercise")


def _print_xp_breakdown(progress) -> None:
    if not progress.xp.by_category:
        return
    table = Table(title="XP by Category")
    table.add_column("Category")
    table.add_column("XP", justify="right")
    for category, xp in sorted(progress.xp.by_category.items(), key=lambda item: item[1], reverse=True):
        table.add_row(category, str(xp))
    console.print(table)

    if progress.xp.by_language:
        lang_table = Table(title="XP by Language")
        lang_table.add_column("Language")
        lang_table.add_column("XP", justify="right")
        for language, xp in sorted(progress.xp.by_language.items(), key=lambda item: item[1], reverse=True):
            lang_table.add_row(language, str(xp))
        console.print(lang_table)


def _print_badges(progress) -> None:
    if not progress.badges:
        console.print("[dim]No badges earned yet.[/dim]")
        return
    table = Table(title="Recent Badges")
    table.add_column("Name")
    table.add_column("Earned At")
    for badge in progress.badges[-5:]:
        table.add_row(f"{badge.icon} {badge.name}", badge.earned_at.isoformat())
    console.print(table)


def _build_recommendation(agent: str) -> Optional[Dict[str, Any]]:
    progress = training_manager.get_progress(agent)
    if not progress:
        return None

    stats = token_tracker.get_agent_stats(agent)
    session_type = SessionType.DAILY.value
    focus = None
    reason = "Maintain daily cadence."

    if progress.weaknesses:
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        weakness = sorted(
            progress.weaknesses,
            key=lambda w: priority_order.get(w.priority, 4),
        )[0]
        session_type = SessionType.REMEDIAL.value
        focus = weakness.skill
        reason = f"Address weakness in {weakness.skill}."
    elif progress.current_level >= 4:
        session_type = SessionType.ADVANCEMENT.value
        reason = "Agent eligible for advancement drills."

    if stats.avg_efficiency_score and stats.avg_efficiency_score < 3.5:
        reason += " Optimize context usage to boost efficiency."

    return {
        "session_type": session_type,
        "focus": focus,
        "reason": reason,
    }


# Reflex Commands
@app.command()
def reflect(
    agent: str = typer.Argument(..., help="Agent ID"),
    context: str = typer.Option("post_exercise", "--context", "-c", help="Reflection context"),
) -> None:
    """Get reflection prompts for learning assessment."""
    console.print(f"[blue]🧠 Getting reflection prompt for {agent} ({context})[/blue]")

    try:
        prompt_data = reflex_service.get_reflection_prompt(agent, context)

        console.print(f"\n[green]Reflection Context:[/green] {context}")
        console.print(f"[green]Performance Level:[/green] {prompt_data['performance_level']}")
        console.print(f"\n[yellow]Reflection Prompts:[/yellow]")

        prompts = prompt_data.get("prompts", {})
        for category, questions in prompts.items():
            if isinstance(questions, list):
                console.print(f"\n[cyan]{category.upper()}:[/cyan]")
                for i, question in enumerate(questions, 1):
                    console.print(f"  {i}. {question}")
            elif isinstance(questions, dict):
                console.print(f"\n[cyan]{category.upper()}:[/cyan]")
                for sub_category, sub_questions in questions.items():
                    console.print(f"  [magenta]{sub_category}:[/magenta]")
                    if isinstance(sub_questions, list):
                        for i, question in enumerate(sub_questions, 1):
                            console.print(f"    {i}. {question}")

        console.print(f"\n[dim]Use 'training reflex-record {agent}' to save your reflection[/dim]")

    except Exception as e:
        console.print(f"[red]Error getting reflection prompt: {e}[/red]")


@app.command("reflex-record")
def reflex_record(
    agent: str = typer.Argument(..., help="Agent ID"),
    reflection_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file with reflection data"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i/-n", help="Interactive mode"),
) -> None:
    """Record agent reflection responses."""
    console.print(f"[blue]📝 Recording reflection for {agent}[/blue]")

    try:
        if reflection_file and reflection_file.exists():
            # Load reflection from file
            with open(reflection_file, 'r') as f:
                reflection_data = json.load(f)
        elif interactive:
            # Interactive mode
            console.print("[yellow]Enter your reflection responses (press Enter twice to finish):[/yellow]")
            reflection_data = {}

            questions = [
                "What was the most challenging part of this exercise?",
                "What new concept or pattern did you learn?",
                "How would you explain this solution to another agent?",
                "What alternative approaches could you use?",
                "What will you do differently next time?"
            ]

            for question in questions:
                console.print(f"\n[cyan]{question}[/cyan]")
                response = input("> ").strip()
                if response:
                    reflection_data[question] = response

            # Filter out empty responses
            reflection_data = {k: v for k, v in reflection_data.items() if v}
        else:
            console.print("[red]No reflection data provided. Use --file or --interactive[/red]")
            return

        if reflection_data:
            reflection_id = reflex_service.record_reflection(agent, reflection_data)
            console.print(f"[green]✅ Reflection recorded: {reflection_id}[/green]")

            # Show quality assessment
            quality_score = reflex_service._assess_reflection_quality(reflection_data)
            console.print(f"[dim]Quality Score: {quality_score:.2f}[/dim]")
        else:
            console.print("[yellow]⚠️ No reflection data recorded[/yellow]")

    except Exception as e:
        console.print(f"[red]Error recording reflection: {e}[/red]")


@app.command("reflex-analyze")
def reflex_analyze(
    agent: str = typer.Argument(..., help="Agent ID"),
    days: int = typer.Option(30, "--days", "-d", help="Analysis period in days"),
    detailed: bool = typer.Option(False, "--detailed", help="Show detailed analysis"),
) -> None:
    """Analyze learning patterns from reflections."""
    console.print(f"[blue]📊 Analyzing learning patterns for {agent} ({days} days)[/blue]")

    try:
        analysis = reflex_service.analyze_learning_patterns(agent, days)

        console.print(f"\n[green]Learning Pattern Analysis[/green]")
        console.print(f"[dim]Period: {analysis['analysis_period_days']} days[/dim]")

        patterns = analysis.get("patterns", {})

        # Display key metrics
        table = Table(title="Learning Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Consistency Score", f"{patterns.get('consistency_score', 0):.2f}")
        table.add_row("Challenge Areas", str(len(patterns.get('challenge_areas', []))))
        table.add_row("Strength Areas", str(len(patterns.get('strength_areas', []))))
        table.add_row("Improvement Trends", str(len(patterns.get('improvement_trends', []))))

        console.print(table)

        if detailed:
            console.print(f"\n[yellow]Detailed Analysis:[/yellow]")

            if patterns.get('improvement_trends'):
                console.print(f"\n[green]Improvement Trends:[/green]")
                for trend in patterns['improvement_trends']:
                    console.print(f"  • {trend}")

            if patterns.get('challenge_areas'):
                console.print(f"\n[red]Challenge Areas:[/red]")
                for challenge in patterns['challenge_areas']:
                    console.print(f"  • {challenge}")

            if patterns.get('strength_areas'):
                console.print(f"\n[blue]Strength Areas:[/blue]")
                for strength in patterns['strength_areas']:
                    console.print(f"  • {strength}")

            if patterns.get('recommended_adjustments'):
                console.print(f"\n[cyan]Recommended Adjustments:[/cyan]")
                for adjustment in patterns['recommended_adjustments']:
                    console.print(f"  • {adjustment}")

    except Exception as e:
        console.print(f"[red]Error analyzing patterns: {e}[/red]")


@app.command("reflex-recommend")
def reflex_recommend(
    agent: str = typer.Argument(..., help="Agent ID"),
) -> None:
    """Get adaptive learning recommendations based on reflex analysis."""
    console.print(f"[blue]🎯 Getting adaptive recommendations for {agent}[/blue]")

    try:
        recommendations = reflex_service.get_adaptive_recommendations(agent)

        console.print(f"\n[green]Adaptive Learning Recommendations[/green]")

        recs = recommendations.get("recommendations", {})

        table = Table(title="Next Session Recommendations")
        table.add_column("Aspect", style="cyan")
        table.add_column("Recommendation", style="magenta")

        table.add_row("Session Type", recs.get("session_type", "N/A"))
        table.add_row("Difficulty Adjustment", recs.get("difficulty_adjustment", "N/A"))
        table.add_row("Learning Strategy", recs.get("learning_strategy", "N/A"))
        table.add_row("Estimated Duration", recs.get("estimated_duration", "N/A"))

        if recs.get("focus_topics"):
            table.add_row("Focus Topics", ", ".join(recs["focus_topics"]))

        console.print(table)

        # Show analysis summary
        analysis = recommendations.get("based_on_analysis", {})
        patterns = analysis.get("patterns", {})

        console.print(f"\n[yellow]Based on Analysis:[/yellow]")
        console.print(f"  • Consistency Score: {patterns.get('consistency_score', 0):.2f}")
        console.print(f"  • Active Challenges: {len(patterns.get('challenge_areas', []))}")
        console.print(f"  • Identified Strengths: {len(patterns.get('strength_areas', []))}")

    except Exception as e:
        console.print(f"[red]Error getting recommendations: {e}[/red]")


if __name__ == "__main__":
    app()
