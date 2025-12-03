"""
[CREATE] Training System CLI

Command-line interface for the Agent Training System.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:00:00Z
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, List, Any, Dict
from datetime import datetime, timezone
import os
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
from .utils.gpu_monitor import GpuMonitor
from .utils.dedupe import find_duplicates, remove_duplicates


def _resolve_base_path() -> Path:
    """
    [CREATE] Locate the training project root regardless of install context.

    Returns:
        Path: Directory containing the `config/` folder.
    """
    env_override = os.getenv("TRAINING_BASE_PATH")
    if env_override:
        candidate = Path(env_override).expanduser()
        if (candidate / "config").exists():
            return candidate

    resolved = Path(__file__).resolve()
    candidate_paths = [
        resolved.parent.parent.parent,
        resolved.parent.parent.parent.parent,
        Path.cwd(),
    ]

    for candidate in candidate_paths:
        if candidate and (candidate / "config").exists():
            return candidate

    raise FileNotFoundError("Unable to locate training base path with config directory.")


BASE_PATH = _resolve_base_path()

app = typer.Typer(
    name="training",
    help="Agent Training System (ATS) - SkeletalMind",
    no_args_is_help=True,
)
console = Console()

# Initialize services
training_manager = TrainingManager(BASE_PATH)
reflex_service = ReflexService(BASE_PATH)
memory_service = MemoryService()
gpu_monitor = GpuMonitor()


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

def _run_training_session(agent: str, topic: str, fatigue_level: float = 0.0) -> float:
    """Runs a single training session and returns the score."""
    tokens_processed = 0
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
                            tokens_processed += len(content.split())
                            memory_service.add_training_material(topic, file_path.name, content, agent_id=agent)

            # Simulate error based on fatigue
            if random.random() < (0.05 + fatigue_level * 0.5):
                raise Exception("Simulated cognitive fatigue error")

            end_time = time.time()
            time_taken = end_time - start_time

            # Score calculation: 100 base - time penalty
            score = max(0, 100 - (time_taken * 10))
            tokens_per_second = (tokens_processed / time_taken) if time_taken > 0 else 0.0
            score_per_token = (score / tokens_processed) if tokens_processed > 0 else 0.0
            gpu_end = gpu_monitor.capture_snapshot()
            gpu_metrics = gpu_monitor.summarize_snapshot(gpu_end)

            metrics = {
                "fatigue_level": fatigue_level,
                "files_processed": files_processed,
                "session_type": "solo_dsa",
                "tokens_processed": tokens_processed,
                "tokens_per_second": tokens_per_second,
                "score_per_token": score_per_token,
                **gpu_metrics,
            }

            memory_service.add_score(topic, score, time_taken, agent_id=agent, metrics=metrics)
            memory_service.log_daily_activity(agent, "training_session", {"topic": topic, "score": score, "status": "success"})

            return score

        except Exception as e:
            end_time = time.time()
            time_taken = end_time - start_time
            gpu_end = gpu_monitor.capture_snapshot()
            gpu_metrics = gpu_monitor.summarize_snapshot(gpu_end)
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
def dedupe(
    path: Path = typer.Option(Path("SkeletalStructure"), "--path", "-p", help="Directory to scan for duplicate files"),
    apply: bool = typer.Option(False, "--apply/--dry-run", help="Remove duplicates instead of simulation"),
    ext: List[str] = typer.Option([], "--ext", help="Optional list of file extensions to include"),
    dedupe_memory: bool = typer.Option(True, "--dedupe-memory/--skip-memory", help="Also dedupe stored training materials"),
) -> None:
    """
    Remove duplicate training assets generated by past agent runs.
    """
    normalized_ext = [(e if e.startswith(".") else f".{e}") for e in ext] or None
    if not path.exists():
        console.print(f"[red]Path not found: {path}[/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Scanning {path} for duplicate files...[/blue]")
    duplicates = find_duplicates(path, normalized_ext)

    if not duplicates:
        console.print("[green]No duplicate files detected.[/green]")
    else:
        table = Table(title="Duplicate Files")
        table.add_column("Hash", style="dim")
        table.add_column("Copies", justify="right")
        table.add_column("Examples")

        for group in duplicates[:20]:
            sample = "\n".join(str(f) for f in group.files[:3])
            table.add_row(group.hash[:12], str(len(group.files)), sample)

        console.print(table)

        if apply:
            removed_files = remove_duplicates(duplicates)
            console.print(f"[yellow]Removed {removed_files} duplicate files from {path}[/yellow]")
        else:
            console.print("[cyan]Dry run complete. Re-run with --apply to remove duplicates.[/cyan]")

    if dedupe_memory:
        removed_docs = memory_service.dedupe_training_materials()
        if removed_docs:
            console.print(f"[yellow]Removed {removed_docs} duplicate training documents from ChromaDB[/yellow]")
        else:
            console.print("[green]No duplicate training documents detected in ChromaDB.[/green]")


@app.command()
def progress(
    agent: str = typer.Argument(..., help="Agent ID"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed stats"),
) -> None:
    """View agent progress."""
    # TODO: Implement progress display


@app.command("gpu")
def gpu_metrics() -> None:
    """
    Display structured GPU telemetry for real-time analysis.
    """
    payload = gpu_monitor.structured_snapshot()
    if not payload.get("available"):
        console.print("[yellow]GPU monitoring not available. Install pynvml and ensure a compatible GPU is present.[/yellow]")
        return

    table = Table(title="GPU Snapshot", show_lines=True)
    table.add_column("Index", justify="right")
    table.add_column("Name")
    table.add_column("Utilization %", justify="right")
    table.add_column("Memory Used (MB)", justify="right")
    table.add_column("Memory Total (MB)", justify="right")

    for device in payload.get("devices", []):
        table.add_row(
            str(device.get("index")),
            device.get("name", "unknown"),
            f"{device.get('utilization', 0.0):.2f}",
            f"{device.get('memory_used_mb', 0.0):.2f}",
            f"{device.get('memory_total_mb', 0.0):.2f}",
        )

    console.print(table)
    console.print(
        f"[cyan]Average Utilization:[/cyan] {payload.get('gpu_utilization_avg', 0.0):.2f}% | "
        f"[cyan]Average Memory Used:[/cyan] {payload.get('gpu_memory_used_mb', 0.0):.2f} MB"
    )


@app.command()
def orchestrate(
    agents: Optional[List[str]] = typer.Option(
        None,
        "--agent",
        "-a",
        help="Agent IDs to orchestrate (repeat the flag for multiple agents)",
        show_default=False,
    ),
    topic: str = typer.Option("dsa", "--topic", "-t", help="Training topic to run"),
    iterations: int = typer.Option(1, "--iterations", "-i", min=1, help="Number of rounds to execute"),
    max_agents: int = typer.Option(4, "--max-agents", min=1, help="Maximum agents to coordinate at once"),
    fatigue_increment: float = typer.Option(
        0.1,
        "--fatigue-increment",
        help="Incremental fatigue applied per iteration (capped internally to 1.0)",
    ),
    show_errors: bool = typer.Option(
        True,
        "--show-errors/--hide-errors",
        help="Toggle inclusion of recent error data in the analysis",
    ),
) -> None:
    """
    Coordinate multi-agent training runs and analyze Chroma memory outputs.

    This command sequentially executes solo sessions for up to `max_agents`
    agents, then aggregates score/time metrics plus recent errors from
    MemoryService to provide an orchestration dashboard.
    """
    available_agents = training_manager.config_service.list_agents()
    if not available_agents:
        console.print("[red]No agent profiles found in configuration.[/red]")
        raise typer.Exit(1)

    selected_agents = list(dict.fromkeys(agents)) if agents else available_agents
    missing_agents = [agent for agent in selected_agents if agent not in available_agents]
    if missing_agents:
        console.print(f"[yellow]Skipping unknown agents: {', '.join(missing_agents)}[/yellow]")
        selected_agents = [agent for agent in selected_agents if agent in available_agents]

    if fatigue_increment < 0:
        console.print("[red]Fatigue increment must be non-negative.[/red]")
        raise typer.Exit(1)

    if not selected_agents:
        console.print("[yellow]No valid agents provided; defaulting to configuration order.[/yellow]")
        selected_agents = available_agents

    if len(selected_agents) > max_agents:
        console.print(f"[yellow]Limiting orchestration to first {max_agents} agents.[/yellow]")
        selected_agents = selected_agents[:max_agents]

    console.print(
        f"[bold blue]Coordinating {len(selected_agents)} agent(s) on topic '{topic}' "
        f"for {iterations} iteration(s).[/bold blue]"
    )

    run_history: List[dict[str, Any]] = []
    for iteration in range(iterations):
        console.print(f"\n[cyan]Iteration {iteration + 1}/{iterations}[/cyan]")
        for idx, agent_id in enumerate(selected_agents):
            fatigue_level = min(1.0, max(0.0, (iteration * fatigue_increment) + (idx * fatigue_increment * 0.5)))
            console.print(
                f"[dim]→ Running solo session for {agent_id} (fatigue={fatigue_level:.2f})[/dim]"
            )
            score = _run_training_session(agent_id, topic, fatigue_level=fatigue_level)
            run_history.append({"agent_id": agent_id, "score": score})

    summary_table = Table(title="Agent Performance Summary")
    summary_table.add_column("Agent")
    summary_table.add_column("Runs", justify="right")
    summary_table.add_column("Last Score", justify="right")
    summary_table.add_column("Avg Score", justify="right")
    summary_table.add_column("Avg Time (s)", justify="right")
    summary_table.add_column("Avg Score/min", justify="right")
    summary_table.add_column("Tokens", justify="right")
    summary_table.add_column("Tokens/s", justify="right")
    summary_table.add_column("Score/token", justify="right")
    summary_table.add_column("GPU Util %", justify="right")

    aggregated_stats = []
    for agent_id in selected_agents:
        recent_run = next((entry for entry in reversed(run_history) if entry["agent_id"] == agent_id), None)
        sample_limit = max(5, iterations * 3)
        memory_summary = memory_service.summarize_agent_performance(agent_id, topic=topic, limit=sample_limit)
        stats = memory_summary.get("summary", {})

        aggregated_stats.append(
            {
                "agent_id": agent_id,
                "average_score": stats.get("average_score", 0.0),
                "average_time": stats.get("average_time_seconds", 0.0),
                "average_spm": stats.get("average_score_per_minute", 0.0),
                "average_tokens": stats.get("average_tokens_processed", 0.0),
                "average_tokens_per_second": stats.get("average_tokens_per_second", 0.0),
                "average_score_per_token": stats.get("average_score_per_token", 0.0),
                "average_gpu_utilization": stats.get("average_gpu_utilization", 0.0),
                "sample_size": stats.get("sample_size", 0),
            }
        )

        summary_table.add_row(
            agent_id,
            str(stats.get("sample_size", 0)),
            f"{recent_run['score']:.2f}" if recent_run else "n/a",
            f"{stats.get('average_score', 0.0):.2f}",
            f"{stats.get('average_time_seconds', 0.0):.2f}",
            f"{stats.get('average_score_per_minute', 0.0):.2f}",
            f"{stats.get('average_tokens_processed', 0.0):.0f}",
            f"{stats.get('average_tokens_per_second', 0.0):.2f}",
            f"{stats.get('average_score_per_token', 0.0):.5f}",
            f"{stats.get('average_gpu_utilization', 0.0):.2f}",
        )

    console.print("\n")
    console.print(summary_table)

    if aggregated_stats:
        top_agent = max(aggregated_stats, key=lambda entry: entry["average_score"])
        console.print(
            f"[green]Top performer:[/green] {top_agent['agent_id']} "
            f"(avg score {top_agent['average_score']:.2f}, "
            f"avg score/min {top_agent['average_spm']:.2f})"
        )

    if show_errors:
        error_table = Table(title="Recent Error Events")
        error_table.add_column("Agent")
        error_table.add_column("Timestamp", style="dim")
        error_table.add_column("Severity")
        error_table.add_column("Context")
        error_table.add_column("Message")

        any_errors = False
        for agent_id in selected_agents:
            errors = memory_service.get_recent_errors(agent_id, limit=3)
            for entry in errors.get("entries", []):
                any_errors = True
                error_table.add_row(
                    agent_id,
                    entry.get("timestamp", "n/a") or "n/a",
                    entry.get("severity", "unknown"),
                    entry.get("context", "-") or "-",
                    entry.get("message", "-") or "-",
                )

        if any_errors:
            console.print("\n")
            console.print(error_table)
        else:
            console.print("[green]No recent errors detected for the selected agents.[/green]")


@app.command()
def diagnostics(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Limit diagnostics to a single agent"),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of records to inspect per agent"),
) -> None:
    """
    Analyze collection health, metrics, logs, and errors.
    """
    console.print("[blue]Gathering datastore diagnostics...[/blue]")
    stats = memory_service.get_collection_metrics()

    stats_table = Table(title="Collection Metrics")
    stats_table.add_column("Collection")
    stats_table.add_column("Documents", justify="right")
    for name, count in stats.items():
        stats_table.add_row(name, str(count))
    console.print(stats_table)

    agents = [agent] if agent else training_manager.config_service.list_agents()
    perf_table = Table(title="Performance Snapshot")
    perf_table.add_column("Agent")
    perf_table.add_column("Samples", justify="right")
    perf_table.add_column("Avg Score", justify="right")
    perf_table.add_column("Avg Score/min", justify="right")
    perf_table.add_column("Tokens", justify="right")
    perf_table.add_column("GPU Util %", justify="right")

    for agent_id in agents:
        summary = memory_service.summarize_agent_performance(agent_id, limit=limit)
        stats_summary = summary.get("summary", {})
        perf_table.add_row(
            agent_id,
            str(stats_summary.get("sample_size", 0)),
            f"{stats_summary.get('average_score', 0.0):.2f}",
            f"{stats_summary.get('average_score_per_minute', 0.0):.2f}",
            f"{stats_summary.get('average_tokens_processed', 0.0):.0f}",
            f"{stats_summary.get('average_gpu_utilization', 0.0):.2f}",
        )

    console.print(perf_table)

    error_table = Table(title="Recent Errors")
    error_table.add_column("Agent")
    error_table.add_column("Timestamp", style="dim")
    error_table.add_column("Severity")
    error_table.add_column("Context")
    error_table.add_column("Message")

    if agent:
        error_payloads = [memory_service.get_recent_errors(agent, limit=min(limit, 10))]
    else:
        error_payloads = [memory_service.get_recent_errors(None, limit=min(limit * len(agents), 20))]

    has_errors = False
    for payload in error_payloads:
        for entry in payload.get("entries", []):
            has_errors = True
            error_table.add_row(
                entry.get("agent_id", payload.get("agent_id", "n/a")),
                entry.get("timestamp", "n/a") or "n/a",
                entry.get("severity", "unknown"),
                entry.get("context", "-") or "-",
                entry.get("message", "-") or "-",
            )

    if has_errors:
        console.print(error_table)
    else:
        console.print("[green]No recent error events recorded.[/green]")


@app.command("structure-report")
def structure_report(
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional file path to save the structural JSON report",
    ),
    include_performance: bool = typer.Option(
        True,
        "--include-performance/--no-performance",
        help="Include summarized agent performance metrics",
    ),
) -> None:
    """
    Export structured YAML/code metadata for pre-merge comparisons.
    """
    report = _build_structure_report(include_performance=include_performance)
    payload = json.dumps(report, indent=2, default=_json_default_serializer)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        console.print(f"[green]Structure report saved to {output}[/green]")
    else:
        console.print(payload)


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


def _build_structure_report(include_performance: bool = True) -> Dict[str, Any]:
    """
    [CREATE] Construct structured metadata for YAML/code comparison workflows.

    Args:
        include_performance (bool): When True, include summarized agent metrics.

    Returns:
        Dict[str, Any]: Structured document combining configuration and runtime data.

    Agent: GPT-5.1 Codex
    Timestamp: 2025-12-03T06:45:00Z
    """
    config_service = training_manager.config_service
    timestamp = datetime.now(timezone.utc).isoformat()

    report: Dict[str, Any] = {
        "metadata": {
            "generated_at": timestamp,
            "generator": "training structure-report",
            "schema_version": "1.0.0",
        },
        "configs": {
            "agent_profiles": config_service.load_config("agent_profiles.yaml"),
            "training_schedule": config_service.load_config("training_schedule.yaml"),
            "difficulty_curves": config_service.load_config("difficulty_curves.yaml"),
            "multi_modal_training": config_service.load_config("multi_modal_training.yaml"),
            "reflection_prompts": config_service.load_config("reflection_prompts.yaml"),
            "spaced_repetition": config_service.load_config("spaced_repetition.yaml"),
        },
    }

    if include_performance:
        performance: Dict[str, Any] = {}
        for agent_id in config_service.list_agents():
            summary = memory_service.summarize_agent_performance(agent_id, limit=5)
            performance[agent_id] = summary.get("summary", {})
        report["performance"] = performance

    return report


def _json_default_serializer(value: Any) -> Any:
    """
    [CREATE] JSON serializer for datetime and Path objects.

    Args:
        value (Any): Value to serialize.

    Returns:
        Any: JSON-safe representation.
    """
    if isinstance(value, (datetime, )):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


if __name__ == "__main__":
    app()
