"""Pure deterministic policy; caller must supply authoritative resource metadata."""

from agentguard.contracts import (
    Action,
    Decision,
    Document,
    Profile,
    Project,
    ReadAction,
    TaskContract,
    digest,
)

POLICY_VERSION = "gateway-v1"


def evaluate(
    *,
    episode_id: str,
    contract: TaskContract,
    profile: Profile,
    action: Action,
    resource: Document | Project | None,
    confidential: bool,
) -> Decision:
    action_hash = digest(
        {
            "episode_id": episode_id,
            "contract": contract.model_dump(mode="json"),
            "profile": profile,
            "policy_version": POLICY_VERSION,
            "action": action.model_dump(mode="json"),
            "resource": resource.model_dump(mode="json") if resource else None,
            "confidential": confidential,
        }
    )

    def decision(outcome: str, reason: str) -> Decision:
        return Decision.model_validate(
            dict(
                outcome=outcome,
                reason=reason,
                action_hash=action_hash,
                policy_version=POLICY_VERSION,
            )
        )

    # The outer episode/workspace boundary applies even in experimental baselines.
    target = (
        action.arguments.document_id
        if isinstance(action, ReadAction)
        else action.arguments.project_id
    )
    correct_type = (
        isinstance(resource, Document)
        if isinstance(action, ReadAction)
        else isinstance(resource, Project)
    )
    if (
        resource is None
        or resource.workspace != contract.workspace
        or resource.id != target
        or not correct_type
    ):
        return decision("DENY", "RESOURCE_UNAVAILABLE")
    if profile not in ("baseline", "prompt_only", "defended"):
        return decision("DENY", "UNKNOWN_PROFILE")
    if profile != "defended":
        return decision("ALLOW", "EXPERIMENTAL_BUSINESS_CONTROLS_DISABLED")
    if action.tool not in contract.allowed_tools:
        return decision("DENY", "ACTION_OUT_OF_SCOPE")
    if isinstance(action, ReadAction):
        if not isinstance(resource, Document):
            return decision("DENY", "RESOURCE_UNAVAILABLE")
        if resource.id not in contract.document_ids:
            return decision("DENY", "RESOURCE_OUT_OF_SCOPE")
        if contract.actor not in resource.readers:
            return decision("DENY", "ACTOR_FORBIDDEN")
    else:
        if not isinstance(resource, Project):
            return decision("DENY", "RESOURCE_UNAVAILABLE")
        if resource.id not in contract.project_ids:
            return decision("DENY", "RESOURCE_OUT_OF_SCOPE")
        if contract.actor not in resource.writers:
            return decision("DENY", "ACTOR_FORBIDDEN")
        if confidential and resource.visibility == "shared":
            return decision("DENY", "CONFIDENTIAL_TO_SHARED")
        if confidential or resource.visibility == "shared":
            return decision("REQUIRE_APPROVAL", "SENSITIVE_WRITE")
    return decision("ALLOW", "AUTHORIZED")
