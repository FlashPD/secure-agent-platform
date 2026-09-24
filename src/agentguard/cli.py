import json
import subprocess
from pathlib import Path
from typing import Annotated, cast

import typer

from agentguard.analysis import write_analysis
from agentguard.contracts import Profile
from agentguard.doctor import inventory
from agentguard.durable_demo import run_durable_demo
from agentguard.live import prepare_local_model, run_live_smoke
from agentguard.model import inference_environment
from agentguard.model_setup import fetch_models, serve_command
from agentguard.replay import run_replay
from agentguard.sandbox_setup import build_images, smoke
from agentguard.suite import VARIANTS, run_suite
from agentguard.supervisor import DockerComputer

app = typer.Typer(
    no_args_is_help=True, help="Agent authorization laboratory. Replay is not live inference."
)


@app.command()
def demo_durable(
    output: Annotated[Path, typer.Option()] = Path("artifacts/durable"),
) -> None:
    """Scripted approval and post-commit recovery demo; zero model trials."""
    directory = run_durable_demo(Path("scenarios/dev/suite/authorized-shared-write.json"), output)
    typer.echo((directory / "report.md").read_text())
    typer.echo(f"Report and database: {directory}")
    if not json.loads((directory / "report.json").read_text())["passed"]:
        raise typer.Exit(1)


@app.command()
def eval_analyze(
    run_directory: Annotated[Path, typer.Argument(exists=True, file_okay=False)],
    output: Annotated[Path, typer.Option()],
    resamples: Annotated[int, typer.Option(min=100, max=100000)] = 5000,
    seed: Annotated[int, typer.Option()] = 42,
) -> None:
    """Verify a completed suite and export paired analysis without changing its evidence."""
    try:
        result = write_analysis(run_directory, output, resamples=resamples, seed=seed)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise typer.BadParameter(f"Unusable suite evidence: {exc}") from exc
    typer.echo(f"Analysis: {result / 'analysis.md'}")
    typer.echo(f"Standalone viewer: {result / 'explorer.html'}")
    typer.echo((result / "analysis.md").read_text())


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


@app.command()
def models_fetch(
    profile: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path(
        "config/model-mac-small.json"
    ),
) -> None:
    """Explicitly download and verify pinned local weights/runtime and their licenses."""
    fetch_models(Path.cwd(), profile)
    typer.echo("Pinned model and runtime verified. Start with: make model-serve")


@app.command()
def model_serve(
    profile: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path(
        "config/model-mac-small.json"
    ),
) -> None:
    """Serve verified project-local weights on loopback in the foreground; no downloads."""
    raise typer.Exit(
        subprocess.call(serve_command(Path.cwd(), profile), env=inference_environment())
    )


@app.command()
def eval_smoke(
    scenario: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path(
        "scenarios/dev/launch-ticket.json"
    ),
    profile: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path(
        "config/model-mac-small.json"
    ),
    sandbox_manifest: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path(
        "artifacts/sandbox/manifest.json"
    ),
    output: Annotated[Path, typer.Option()] = Path("artifacts/live"),
) -> None:
    """Explicit synthetic benchmark: 6 fresh local-model trials, including unsafe baselines."""
    result = run_live_smoke(scenario, profile, sandbox_manifest, output, root=Path.cwd())
    typer.echo(f"Report: {result / 'report.md'}")
    typer.echo((result / "report.md").read_text())
    report = json.loads((result / "report.json").read_text())
    if any(
        row["status"] != "COMPLETED" or (not row["attacked"] and not row["grade"]["task_success"])
        for row in report["episodes"]
    ):
        raise typer.Exit(1)


@app.command()
def eval_suite(
    suite: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path(
        "scenarios/dev/suite-v1.json"
    ),
    live: Annotated[bool, typer.Option("--live")] = False,
    variants: Annotated[str, typer.Option()] = "baseline,prompt_only,defended",
    simulate_approvals: Annotated[bool, typer.Option()] = True,
    model_profile: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path(
        "config/model-mac-small.json"
    ),
    sandbox_manifest: Annotated[Path | None, typer.Option(exists=True, dir_okay=False)] = None,
    output: Annotated[Path, typer.Option()] = Path("artifacts/suites"),
) -> None:
    """Run a synthetic development suite; default is authored replay, not model inference."""
    selected = tuple(v.strip() for v in variants.split(","))
    if len(set(selected)) != len(selected) or not set(selected) <= set(VARIANTS):
        raise typer.BadParameter("Select unique variants from baseline,prompt_only,defended")
    model, evidence = None, None
    if live:
        model, profile, server = prepare_local_model(Path.cwd(), model_profile)
        evidence = {"profile": profile, "server": server}
        sandbox_manifest = sandbox_manifest or Path("artifacts/sandbox/manifest.json")
    computer = DockerComputer.from_manifest(sandbox_manifest) if sandbox_manifest else None

    def progress(directory: Path, completed: int, total: int) -> None:
        if completed == 0:
            typer.echo(f"Artifacts: {directory}")
        typer.echo(f"Episodes recorded: {completed}/{total}")

    result = run_suite(
        suite,
        output,
        computer=computer,
        variants=cast(tuple[Profile, ...], selected),
        simulate_approvals=simulate_approvals,
        model=model,
        model_evidence=evidence,
        progress=progress,
    )
    typer.echo("FRESH LOCAL INFERENCE" if live else "SCRIPTED REPLAY — 0 model trials")
    typer.echo(f"Report: {result / 'report.md'}")
    report = json.loads((result / "report.json").read_text())
    typer.echo(json.dumps(report["counts"], indent=2))
    if any(
        r["status"] != "COMPLETED"
        or (
            r["profile"] == "defended"
            and (
                (not r["attacked"] and not r["grade"]["task_success"])
                or r["grade"]["attack_success"]
            )
        )
        for r in report["episodes"]
    ):
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
