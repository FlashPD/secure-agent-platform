"""Fixed stdlib-only entrypoint. Reads bounded JSON; never evaluates document text."""

import json
import sys

MAX_INPUT = 131072
MAX_OUTPUT = 65536


def compute(request: dict) -> dict:
    if set(request) != {"action", "document"}:
        raise ValueError("request fields")
    action = request["action"]
    if set(action) != {"tool", "arguments"}:
        raise ValueError("action fields")
    args = action["arguments"]
    if action["tool"] == "documents.read":
        document = request["document"]
        if set(args) != {"document_id"} or set(document) != {"id", "body"}:
            raise ValueError("document fields")
        if args["document_id"] != document["id"]:
            raise ValueError("document target")
        if not isinstance(document["body"], str) or len(document["body"]) > 12000:
            raise ValueError("document body")
        return {"kind": "document", "document_id": document["id"], "body": document["body"]}
    if action["tool"] == "tickets.create":
        if set(args) != {"project_id", "title", "body"} or request["document"] is not None:
            raise ValueError("ticket fields")
        for name, limit in (("project_id", 80), ("title", 160), ("body", 4000)):
            if not isinstance(args[name], str) or not 1 <= len(args[name]) <= limit:
                raise ValueError("ticket argument")
        return {"kind": "ticket", "arguments": args}
    raise ValueError("unknown tool")


def main() -> int:
    try:
        payload = sys.stdin.buffer.read(MAX_INPUT + 1)
        if len(payload) > MAX_INPUT:
            raise ValueError("input size")
        output = json.dumps(compute(json.loads(payload)), ensure_ascii=False).encode()
        if len(output) > MAX_OUTPUT:
            raise ValueError("output size")
        sys.stdout.buffer.write(output)
        return 0
    except (ValueError, TypeError, KeyError):
        sys.stderr.write("INVALID_TOOL_REQUEST\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
