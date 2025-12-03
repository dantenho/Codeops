"""
[CREATE] Training System CLI

Command-line interface for the Agent Training System.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:00:00Z
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
import time
import random

from .services.training_manager import TrainingManager
from .services.reflex_service import ReflexService
from .services.memory_service import MemoryService
from .models.session import SessionType

app = typer.Typer(
    name="training",
    help="Agent Training System (ATS) - SkeletalMind",
    no_args_is_help=True,
)
console = Console()

# Initialize services
training_manager = TrainingManager(Path(__file__).parent.parent.parent)
reflex_service = ReflexService(Path(__file__).parent.parent.parent)
memory_service = MemoryService()


@app.command()
def init(
    agent: str = typer.Argument(..., help="Agent ID to initialize"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing profile"),
) -> None:
    """Initialize a new agent profile."""
    console.print(f"[green]Initializing agent: {agent}[/green]")
    # TODO: Implement initialization


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

        _run_training_session(agent, topic)
    else:
        # TODO: Implement other session types
        console.print(f"[yellow]Session type {session_type} not yet implemented[/yellow]")


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

def _run_training_session(agent: str, topic: str, fatigue_level: float = 0.0) -> float:
    """Runs a single training session and returns the score."""
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

            return score

        except Exception as e:
            end_time = time.time()
            time_taken = end_time - start_time
            memory_service.add_error(str(e), f"Error during solo training on {topic}", agent_id=agent)
            memory_service.log_daily_activity(agent, "training_error", {"topic": topic, "error": str(e)})
            console.print(f"[red]Error during training: {e}[/red]")
            return 0.0
    else:
        console.print(f"[red]Error: Unknown topic {topic}[/red]")
        return 0.0

@app.command()
def simulate(
    agent: str = typer.Argument(..., help="Agent ID"),
    topic: str = typer.Option("dsa", "--topic", help="Topic to simulate"),
    iterations: int = typer.Option(10, "--iterations", "-i", help="Number of iterations"),
) -> None:
    """Simulate training over time until performance degrades."""
    console.print(f"[bold blue]🚀 Starting Simulation for {agent} on {topic}[/bold blue]")

    scores = []
    fatigue = 0.0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"Simulating {iterations} sessions...", total=iterations)

        for i in range(iterations):
            progress.update(task, description=f"Session {i+1}/{iterations} (Fatigue: {fatigue:.2f})")

            score = _run_training_session(agent, topic, fatigue_level=fatigue)
            scores.append(score)

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
    # TODO: Implement progress display


@app.command()
def recommend(
    agent: str = typer.Argument(..., help="Agent ID"),
) -> None:
    """Get next session recommendation."""
    # TODO: Implement recommendation


@app.command()
def flashcards(
    agent: str = typer.Argument(..., help="Agent ID"),
    deck: Optional[str] = typer.Option(None, "--deck", "-d", help="Specific deck ID"),
) -> None:
    """Review flashcards."""
    # TODO: Implement flashcard review


@app.command()
def leaderboard(
    top: int = typer.Option(10, "--top", "-t"),
) -> None:
    """View training leaderboard."""
    # TODO: Implement leaderboard


@app.command()
def report(
    agent: str = typer.Argument(..., help="Agent ID"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Generate progress report."""
    # TODO: Implement report generation


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
