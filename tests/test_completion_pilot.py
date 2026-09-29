import copy
import runpy
from pathlib import Path

import pytest

PILOT = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/completion_pilot.py"))


def rows():
    return [
        {
            "episode_id": f"{case}-{arm}-{attack}",
            "task_id": f"completion-capacity-{case}-{arm}",
            "attacked": attack,
            "status": "COMPLETED",
            "grade": {"task_success": arm == "guard", "attack_success": False},
        }
        for case in ("boundary", "counterexample")
        for arm in ("control", "guard")
        for attack in (False, True)
    ]


def test_candidate_requires_complete_matched_improvement():
    assert PILOT["summarize"](rows())["eligible_for_broader_development"]
    for incomplete in (rows()[:-1], rows() + rows()[:1]):
        with pytest.raises(ValueError):
            PILOT["summarize"](incomplete)
    duplicate = rows()
    duplicate[1] = copy.deepcopy(duplicate[0])
    duplicate[1]["episode_id"] = "different"
    with pytest.raises(ValueError):
        PILOT["summarize"](duplicate)


@pytest.mark.parametrize("failure", ["guard_failure", "attacker_win", "timeout", "tie"])
def test_selection_rejects_failure_safety_regression_and_no_improvement(failure):
    values = rows()
    if failure == "guard_failure":
        values[2]["grade"]["task_success"] = False
    elif failure == "attacker_win":
        values[3]["grade"]["attack_success"] = True
    elif failure == "timeout":
        values[0]["status"] = "BUDGET_EXHAUSTED"
    else:
        for row in values:
            row["grade"]["task_success"] = True
    assert not PILOT["summarize"](values)["eligible_for_broader_development"]
