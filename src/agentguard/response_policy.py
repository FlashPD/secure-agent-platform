"""Coarse final-output authorization without inspecting text or hidden grader data."""

from typing import Literal

from agentguard.contracts import Contract, Profile, TaskContract, digest

RESPONSE_POLICY_VERSION = "response-clearance-v1"


class ResponseDecision(Contract):
    outcome: Literal["ALLOW", "DENY"]
    reason: str
    recipient: str | None
    classification: Literal["internal", "confidential"]
    policy_version: str = RESPONSE_POLICY_VERSION
    binding_hash: str


def evaluate_response(
    *,
    episode_id: str,
    contract: TaskContract,
    profile: Profile,
    confidential: bool,
    cancelled: bool,
) -> ResponseDecision:
    scope = contract.response_scope
    outcome: Literal["ALLOW", "DENY"] = "ALLOW"
    reason = "RESPONSE_AUTHORIZED"
    if cancelled:
        outcome, reason = "DENY", "CANCELLED"
    elif profile not in ("baseline", "prompt_only", "defended"):
        outcome, reason = "DENY", "UNKNOWN_PROFILE"
    elif profile != "defended":
        reason = "EXPERIMENTAL_BUSINESS_CONTROLS_DISABLED"
    elif scope is None:
        reason = "LEGACY_RESPONSE_UNRESTRICTED"
    elif confidential and scope.max_classification == "internal":
        outcome, reason = "DENY", "CONFIDENTIAL_RESPONSE_BLOCKED"
    return ResponseDecision(
        outcome=outcome,
        reason=reason,
        recipient=scope.recipient if scope else None,
        classification="confidential" if confidential else "internal",
        binding_hash=digest(
            {
                "episode_id": episode_id,
                "contract": contract.model_dump(mode="json"),
                "profile": profile,
                "confidential": confidential,
                "cancelled": cancelled,
                "policy_version": RESPONSE_POLICY_VERSION,
            }
        ),
    )
