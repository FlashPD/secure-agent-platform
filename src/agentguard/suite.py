"""Paired development evaluation with explicit replay/live modes and exact-action review."""

import hashlib
import json
import platform
import sqlite3
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from agentguard.computation import Computer, ToolFailure
from agentguard.contracts import Profile, digest
from agentguard.live import atomic_json
from agentguard.model import LocalModel
from agentguard.policy import POLICY_VERSION
from agentguard.reviewer import REVIEWER_VERSION, ExactActionReviewer
from agentguard.runtime import (
    BASE_PROMPT,
    FEEDBACK_VERSION,
    HARDENED_PROMPT,
    Budgets,
    Runtime,
    turn_schema,
)
from agentguard.scenarios import (
    GRADER_VERSION,
    Script,
    episode_documents,
    grade_episode,
    load_suite,
)
from agentguard.storage import ReviewRejected, Store

VARIANTS: tuple[Profile, ...] = ("baseline", "prompt_only", "defended")


def run_script(
    store: Store, episode: str, script: Script, reviewer: ExactActionReviewer | None
) -> dict[str, Any]:
    start = time.monotonic()
    trace: list[dict[str, Any]] = []
    status, reason, final = "COMPLETED", "AUTHORED_SCRIPT", script.final_response
    try:
        for index, action in enumerate(script.actions):
            key = f"step-{index}:call-0"
            result = store.execute(episode, key, action)
            entry: dict[str, Any] = {"action": action.model_dump(mode="json")}
            if result.decision.outcome == "REQUIRE_APPROVAL" and reviewer is not None:
                assert result.approval_id is not None
                approved = reviewer.review(store, result.approval_id)
                entry["simulated_review"] = {
                    "approved": approved,
                    "initial_decision": result.decision.model_dump(),
                }
                result = store.execute(
                    episode, key, action, approval_id=result.approval_id if approved else None
                )
            entry["execution"] = result.model_dump(mode="json")
            trace.append(entry)
            if result.decision.outcome == "REQUIRE_APPROVAL":
                status, reason, final = "WAITING_APPROVAL", "SENSITIVE_WRITE", ""
                break
            if result.decision.reason in ("CANCELLED", "BUDGET_EXHAUSTED"):
                status, reason, final = result.decision.reason, result.decision.reason, ""
                break
    except (ToolFailure, ReviewRejected) as exc:
        status, reason, final = "FAILED", type(exc).__name__, ""
    return {
        "status": status,
        "reason": reason,
        "final_response": final,
        "trace": trace,
        "model_calls": 0,
        "generated_tokens": 0,
        "elapsed_seconds": round(time.monotonic() - start, 4),
    }


def summarize(rows: list[dict[str, Any]], variants: tuple[Profile, ...]) -> dict[str, Any]:
    counts: dict[str, Any] = {}
    for variant in variants:
        group = [r for r in rows if r["profile"] == variant]
        clean = [r for r in group if not r["attacked"]]
        attacked = [r for r in group if r["attacked"]]
        wins = sum(bool(r["grade"]["attack_success"]) for r in attacked)
        unresolved = sum(
            r["status"] != "COMPLETED" and not r["grade"]["attack_success"] for r in attacked
        )
        counts[variant] = {
            "scheduled_clean": len(clean),
            "scheduled_attacked": len(attacked),
            "clean_success": sum(r["grade"]["task_success"] for r in clean),
            "attacked_task_success": sum(r["grade"]["task_success"] for r in attacked),
            "observed_attack_wins": wins,
            "unresolved_attacked": unresolved,
            "worst_case_attack_wins": wins + unresolved,
            "noncompleted": sum(r["status"] != "COMPLETED" for r in group),
            "simulated_reviews": sum("simulated_review" in t for r in group for t in r["trace"]),
        }
    return counts


def run_suite(
    suite_path: Path,
    output_root: Path,
    *,
    computer: Computer | None = None,
    variants: tuple[Profile, ...] = VARIANTS,
    simulate_approvals: bool = True,
    model: LocalModel | None = None,
    model_evidence: dict[str, Any] | None = None,
    progress: Callable[[Path, int, int], None] | None = None,
) -> Path:
    if not variants or len(set(variants)) != len(variants) or not set(variants) <= set(VARIANTS):
        raise ValueError("Select unique known benchmark variants")
    if model is not None and (computer is None or computer.mode != "docker_isolated"):
        raise ValueError("Live suite evaluation requires isolated tools")
    if model is not None and model_evidence is None:
        raise ValueError("Live evaluation requires pinned model evidence")
    suite, fixtures = load_suite(suite_path)
    run_dir = output_root / str(uuid.uuid4())
    run_dir.mkdir(parents=True, exist_ok=False)
    store = Store(run_dir / "state.sqlite3", computer=computer)
    budgets = Budgets(context_tokens=model.config.context_tokens) if model else Budgets()
    source = {p.name: p.read_text() for p in sorted(Path(__file__).parent.glob("*.py"))}
    atomic_json(run_dir / "source.json", source)
    fixture_root = run_dir / "fixtures"
    fixture_root.mkdir()
    (fixture_root / suite_path.name).write_bytes(suite_path.read_bytes())
    fixture_manifest = []
    tasks = {task.id: task for _, _, task in fixtures}
    schedule: list[dict[str, Any]] = []
    for relative, raw, task in fixtures:
        snapshot = fixture_root / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(raw)
        fixture_manifest.append(
            {
                "id": task.id,
                "family": task.family,
                "file": str(snapshot.relative_to(run_dir)),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "attack_family": task.attack_family,
                "attack_document_id": task.attack_document_id,
                "attack_payload_sha256": hashlib.sha256(task.attack_payload.encode()).hexdigest(),
            }
        )
        for variant in variants:
            for attacked in (False, True):
                episode = store.create_episode(
                    task.contract,
                    episode_documents(task, attacked=attacked),
                    task.projects,
                    experimental_profile=variant,
                    max_actions=budgets.max_steps,
                )
                schedule.append(
                    {
                        "episode_id": episode,
                        "task_id": task.id,
                        "profile": variant,
                        "attacked": attacked,
                    }
                )
    manifest = {
        "schema_version": 1,
        "suite_id": suite.id,
        "split": suite.split,
        "hardware": {"os": platform.system(), "architecture": platform.machine()},
        "python": platform.python_version(),
        "mode": "fresh_local_inference" if model else "scripted_suite_replay",
        "fresh_inference": model is not None,
        "release_evidence": False,
        "suite_sha256": hashlib.sha256(suite_path.read_bytes()).hexdigest(),
        "source_sha256": digest(
            {name: hashlib.sha256(text.encode()).hexdigest() for name, text in source.items()}
        ),
        "fixtures": fixture_manifest,
        "schedule": schedule,
        "scheduled_episodes": len(schedule),
        "variants": variants,
        "containment": store.computer.mode,
        "tool_image_id": getattr(store.computer, "image_id", None),
        "model": model_evidence,
        "budgets": budgets.model_dump(),
        "policy_version": POLICY_VERSION,
        "grader_version": GRADER_VERSION,
        "feedback_version": FEEDBACK_VERSION,
        "prompts_sha256": digest({"base": BASE_PROMPT, "hardened": HARDENED_PROMPT}),
        "output_schema_sha256": digest(json.dumps(turn_schema(), separators=(",", ":"))),
        "simulated_approvals": simulate_approvals,
        "reviewer_version": REVIEWER_VERSION if simulate_approvals else None,
    }
    atomic_json(run_dir / "manifest.json", manifest)
    if progress is not None:
        progress(run_dir, 0, len(schedule))
    rows: list[dict[str, Any]] = []
    for scheduled in schedule:
        task = tasks[scheduled["task_id"]]
        reviewer = (
            ExactActionReviewer(task.contract, task.review_contract) if simulate_approvals else None
        )
        if model is not None:
            result = Runtime(store, model, budgets, reviewer=reviewer).run(
                scheduled["episode_id"], task.task
            )
        else:
            result = run_script(
                store,
                scheduled["episode_id"],
                task.attacked_script if scheduled["attacked"] else task.clean_script,
                reviewer,
            )
        state_grade = grade_episode(
            store,
            scheduled["episode_id"],
            result["final_response"],
            task.expectation,
            attacked=scheduled["attacked"],
        )
        rows.append(
            scheduled
            | result
            | {
                "grade": state_grade
                | {
                    "state_task_success": state_grade["task_success"],
                    "task_success": state_grade["task_success"] and result["status"] == "COMPLETED",
                }
            }
        )
        atomic_json(run_dir / "episodes.json", rows)
        if progress is not None:
            progress(run_dir, len(rows), len(schedule))
    report = {"manifest": manifest, "counts": summarize(rows, variants), "episodes": rows}
    atomic_json(run_dir / "report.json", report)
    label = "Live development suite" if model else "Scripted suite replay — no model inference"
    lines = [
        f"# {label}",
        "",
        "Development fixtures; not a held-out release benchmark.",
        "",
        "| Task | Profile | Input | Status | Task success | Attack success |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['task_id']} | {row['profile']} | "
            f"{'attacked' if row['attacked'] else 'clean'} | {row['status']} | "
            f"{row['grade']['task_success']} | {row['grade']['attack_success']} |"
        )
    lines += [
        "",
        f"Scheduled: {len(schedule)}. Accounted for: {len(rows)}.",
        f"Simulated approvals enabled: {simulate_approvals}.",
        "Authored replay is contract/grader evidence, not measured model utility or security."
        if model is None
        else "Fresh local inference; all failures remain in denominators.",
        "",
    ]
    (run_dir / "report.md").write_text("\n".join(lines))
    with store.connection() as db, sqlite3.connect(run_dir / "evidence.sqlite3") as snapshot_db:
        db.backup(snapshot_db)
        atomic_json(
            run_dir / "model-calls.json", [dict(r) for r in db.execute("SELECT * FROM model_calls")]
        )
    atomic_json(
        run_dir / "checksums.json",
        {
            str(p.relative_to(run_dir)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(run_dir.rglob("*"))
            if p.is_file() and (p.suffix in (".json", ".md") or p.name == "evidence.sqlite3")
        },
    )
    return run_dir
