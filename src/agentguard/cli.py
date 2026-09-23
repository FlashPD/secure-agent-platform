import json
from pathlib import Path
from typing import Annotated

import typer

from agentguard.doctor import inventory
from agentguard.replay import run_replay

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
) -> None:
    """Run four scripted clean/attacked episodes; no inference or container claims."""
    result = run_replay(scenario, output)
    typer.echo("SCRIPTED REPLAY — 4 episodes; 0 model trials; trusted Python simulation.")
    typer.echo(f"Report: {result / 'report.md'}")
    typer.echo((result / "report.md").read_text())


if __name__ == "__main__":
    app()
