"""
CLI entry point for the GitHub optimization service.

Allows local or CI workflows to process PR payloads and fetch recommendations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from CodeAgents.GitHub.optimization_service import OptimizationService

app = typer.Typer(help="Run GitHub optimization workflows.")


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise typer.BadParameter(f"File not found: {path}")

    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


@app.command("process-pr")
def process_pr(
    pr_payload: Path = typer.Argument(..., help="Path to GitHub PR payload JSON."),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Override optimization config path (defaults to config/optimization_patterns.yaml).",
    ),
    catalog_dir: Optional[Path] = typer.Option(
        None,
        "--catalog-dir",
        help="Optional override for catalog output directory.",
    ),
) -> None:
    """
    Process a GitHub pull request payload and update the optimization catalog.
    """
    service = OptimizationService(
        config_path=config,
        catalog_path=catalog_dir,
    )
    payload = _load_json(pr_payload)
    summary = service.process_pull_request(payload)
    typer.echo(json.dumps(summary, indent=2))


@app.command()
def recommend(
    code_file: Path = typer.Argument(..., help="Source file to analyze."),
    language: str = typer.Option("python", "--language", "-l", help="Programming language."),
    limit: int = typer.Option(5, "--limit", "-n", help="Maximum recommendations to print."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Optional config override."),
) -> None:
    """
    Print catalog recommendations for a given source file.
    """
    service = OptimizationService(config_path=config)

    if not code_file.exists():
        raise typer.BadParameter(f"File not found: {code_file}")

    with open(code_file, "r", encoding="utf-8") as handle:
        code = handle.read()

    entries = service.recommend_for_code(code, language=language, limit=limit)

    if not entries:
        typer.echo("No recommendations found.")
        raise typer.Exit(0)

    for entry in entries:
        opt = entry.optimization
        typer.echo(
            typer.style(f"{opt.title} [{opt.category.value}/{opt.impact.value}]", fg=typer.colors.GREEN)
        )
        typer.echo(f"  Success Rate: {opt.success_rate:.2f} | Avg Improvement: {opt.avg_improvement:.2f}")
        typer.echo(f"  Before Pattern: {opt.pattern_before}")
        typer.echo(f"  After Pattern:  {opt.pattern_after}")
        if entry.training_material_path:
            typer.echo(f"  Training Material: {entry.training_material_path}")
        typer.echo("")


@app.command("export-catalog")
def export_catalog(
    output: Path = typer.Argument(..., help="Output YAML path."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Optional config override."),
) -> None:
    """
    Export the current optimization catalog to a YAML file.
    """
    service = OptimizationService(config_path=config)
    export_path = service.export_catalog(output)
    typer.echo(f"Catalog exported to {export_path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
