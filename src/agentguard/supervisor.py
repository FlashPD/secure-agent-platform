"""Host-only Docker access with fixed options, bounded pipes, and explicit cleanup."""

import json
import os
import re
import selectors
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from agentguard.computation import RESULT_ADAPTER, ToolFailure, ToolRequest, ToolResult

MAX_INPUT = 131072
MAX_OUTPUT = 65536
MAX_STDERR = 4096
IMAGE_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")


def bounded_process(
    command: list[str], payload: bytes, *, timeout: float, output_limit: int = MAX_OUTPUT
) -> bytes:
    """Bound input writes as well as output reads; never buffer unbounded child output."""
    if len(payload) > MAX_INPUT:
        raise ToolFailure("INPUT_TOO_LARGE")
    deadline = time.monotonic() + timeout
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        raise ToolFailure("RUNTIME_UNAVAILABLE") from exc
    assert process.stdin and process.stdout and process.stderr
    stdout, stderr = bytearray(), bytearray()
    sent = 0
    try:
        with selectors.DefaultSelector() as selector:
            for stream, event, label in (
                (process.stdin, selectors.EVENT_WRITE, "stdin"),
                (process.stdout, selectors.EVENT_READ, "stdout"),
                (process.stderr, selectors.EVENT_READ, "stderr"),
            ):
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, event, label)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ToolFailure("TOOL_TIMEOUT")
                for key, _ in selector.select(remaining):
                    if key.data == "stdin":
                        try:
                            sent += os.write(key.fd, payload[sent : sent + 4096])
                        except BrokenPipeError:
                            sent = len(payload)
                        if sent == len(payload):
                            selector.unregister(key.fileobj)
                            process.stdin.close()
                    else:
                        chunk = os.read(key.fd, 4096)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        buffer = stdout if key.data == "stdout" else stderr
                        limit = output_limit if key.data == "stdout" else MAX_STDERR
                        if len(buffer) + len(chunk) > limit:
                            raise ToolFailure("OUTPUT_TOO_LARGE")
                        buffer.extend(chunk)
            try:
                status = process.wait(timeout=max(0.001, deadline - time.monotonic()))
            except subprocess.TimeoutExpired as exc:
                raise ToolFailure("TOOL_TIMEOUT") from exc
            if status != 0:
                raise ToolFailure("TOOL_PROCESS_FAILED", exit_status=status)
            return bytes(stdout)
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()
        for stream in (process.stdin, process.stdout, process.stderr):
            stream.close()


class DockerComputer:
    mode = "docker_isolated"

    def __init__(self, image_id: str, *, timeout: float = 10):
        if IMAGE_PATTERN.fullmatch(image_id) is None:
            raise ValueError("Container image must be an immutable local sha256 image ID")
        if not 0 < timeout <= 30:
            raise ValueError("Tool timeout must be within 0..30 seconds")
        self.image_id = image_id
        self.timeout = timeout

    @classmethod
    def from_manifest(cls, path: Path) -> "DockerComputer":
        manifest = json.loads(path.read_text())
        if manifest.get("schema_version") != 1:
            raise ValueError("Unsupported sandbox manifest")
        return cls(manifest["tool_image_id"])

    def command(self, name: str, *, probe: bool = False) -> list[str]:
        # Only the trusted smoke harness can select the separately built probe image.
        entry = "/tool/probe.py" if probe else "/tool/runner.py"
        return [
            "docker",
            "run",
            "--rm",
            "--interactive",
            "--pull=never",
            "--name",
            name,
            "--network=none",
            "--read-only",
            "--user=65532:65532",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges:true",
            "--pids-limit=64",
            "--memory=256m",
            "--memory-swap=256m",
            "--cpus=1",
            "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=16m,mode=1777",
            "--ulimit=nofile=64:64",
            "--log-driver=none",
            "--workdir=/tool",
            "--entrypoint=/usr/local/bin/python",
            self.image_id,
            "-I",
            "-B",
            entry,
        ]

    def run(self, payload: bytes, *, probe: bool = False) -> bytes:
        name = "agentguard-" + uuid.uuid4().hex
        try:
            return bounded_process(self.command(name, probe=probe), payload, timeout=self.timeout)
        finally:
            # Killing the docker CLI alone does not reliably kill the container.
            self._remove(name)

    @staticmethod
    def _remove(name: str) -> None:
        # --rm and an explicit kill can race. Confirm removal; do not confuse an
        # in-progress removal with either successful cleanup or a leaked container.
        for _ in range(3):
            try:
                cleanup = subprocess.run(
                    ["docker", "rm", "--force", name],
                    capture_output=True,
                    timeout=2,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise ToolFailure("CLEANUP_UNCONFIRMED") from exc
            if cleanup.returncode == 0 or b"No such container" in cleanup.stderr:
                return
            if b"already in progress" not in cleanup.stderr:
                break
            time.sleep(0.05)
        raise ToolFailure("CLEANUP_UNCONFIRMED")

    def compute(self, request: ToolRequest) -> ToolResult:
        output = self.run(request.model_dump_json().encode())
        try:
            return RESULT_ADAPTER.validate_json(output)
        except ValidationError as exc:
            raise ToolFailure("INVALID_TOOL_RESPONSE") from exc

    def diagnostic(self, operation: str) -> dict[str, Any]:
        """Trusted smoke harness only; this method is absent from agent tool schemas."""
        result: dict[str, Any] = json.loads(
            self.run(json.dumps({"probe": operation}).encode(), probe=True)
        )
        return result
