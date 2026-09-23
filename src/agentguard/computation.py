"""Only validated data crosses the computation boundary; effects stay on the host."""

from typing import Annotated, Literal, Protocol

from pydantic import Field, TypeAdapter

from agentguard.contracts import Action, Contract, CreateArguments, Identifier, ReadAction


class DocumentSnapshot(Contract):
    id: Identifier
    body: str = Field(max_length=12000)


class ToolRequest(Contract):
    action: Action
    document: DocumentSnapshot | None = None


class DocumentResult(Contract):
    kind: Literal["document"] = "document"
    document_id: Identifier
    body: str = Field(max_length=12000)


class TicketEffect(Contract):
    kind: Literal["ticket"] = "ticket"
    arguments: CreateArguments


ToolResult = Annotated[DocumentResult | TicketEffect, Field(discriminator="kind")]
RESULT_ADAPTER: TypeAdapter[ToolResult] = TypeAdapter(ToolResult)


class ToolFailure(RuntimeError):
    """Bounded reason code; raw process stderr must not become model-visible output."""

    def __init__(self, code: str, *, exit_status: int | None = None):
        self.code = code
        self.exit_status = exit_status
        super().__init__(code)


class Computer(Protocol):
    mode: str

    def compute(self, request: ToolRequest) -> ToolResult: ...


def expected_result(request: ToolRequest) -> ToolResult:
    if isinstance(request.action, ReadAction):
        if request.document is None or request.document.id != request.action.arguments.document_id:
            raise ToolFailure("INVALID_SNAPSHOT")
        return DocumentResult(document_id=request.document.id, body=request.document.body)
    if request.document is not None:
        raise ToolFailure("INVALID_SNAPSHOT")
    return TicketEffect(arguments=request.action.arguments)


def validate_result(request: ToolRequest, result: ToolResult) -> None:
    # These fixed tools must preserve the authorized target and exact content.
    # A future transforming tool needs its own validator, not a relaxed version of this one.
    if result != expected_result(request):
        raise ToolFailure("EFFECT_MISMATCH")


class InProcessComputer:
    mode = "trusted_python_simulation_only"

    def compute(self, request: ToolRequest) -> ToolResult:
        return expected_result(request)
