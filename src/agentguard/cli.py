import json
from pathlib import Path
from typing import Annotated

import typer

from agentguard.doctor import inventory
from agentguard.replay import run_replay
from agentguard.sandbox_setup import build_images, smoke
from agentguard.supervisor import DockerComputer

app = typer.Typer(
    no_args_is_help=True, help="Agent authorization laboratory. Replay is not live inference."
)


@app.command()
def doctor() -> None:
    """Inspect this machine without changing services or downloading weights."""
    typer.echo(json.dumps(inventory(Path.cwd()), indent=2))


@app.command()
def demo_replay(
    scenario: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path(
        "scenarios/dev/launch-ticket.json"
    ),
    output: Annotated[Path, typer.Option()] = Path("artifacts/replays"),
    sandbox_manifest: Annotated[Path | None, typer.Option(exists=True, dir_okay=False)] = None,
) -> None:
    """Run four scripted clean/attacked episodes; no inference or container claims."""
    computer = DockerComputer.from_manifest(sandbox_manifest) if sandbox_manifest else None
    result = run_replay(scenario, output, computer=computer)
    mode = computer.mode if computer else "trusted_python_simulation_only"
    typer.echo(f"SCRIPTED REPLAY — 4 episodes; 0 model trials; {mode}.")
    typer.echo(f"Report: {result / 'report.md'}")
    typer.echo((result / "report.md").read_text())


@app.command()
def sandbox_build() -> None:
    """Explicitly download the pinned base image and build fixed tools/probe images."""
    typer.echo(f"Sandbox manifest: {build_images(Path.cwd())}")


@app.command()
def sandbox_smoke(
    manifest: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path(
        "artifacts/sandbox/manifest.json"
    ),
    output: Annotated[Path, typer.Option()] = Path("artifacts/sandbox-smoke"),
) -> None:
    """Measure tool computation and containment using a separate diagnostic image."""
    report = smoke(manifest, output)
    typer.echo(f"Container smoke report: {report}")
    result = json.loads(report.read_text())
    typer.echo(json.dumps(result["checks"], indent=2))
    if not result["passed"]:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
