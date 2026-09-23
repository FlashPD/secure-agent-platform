# Development hardware

Observed September 23, 2026. Only non-identifying fields are recorded.

| Item | Observation |
|---|---|
| Mac | MacBook Pro, Apple M1, 8 CPU cores, arm64 |
| Unified memory | 16 GB |
| Free filesystem space | Approximately 33 GiB at initial inventory |
| Project Python | Homebrew CPython 3.12.12 |
| Default shell Python | 3.10.0; do not use for this project |
| Docker CLI | 29.7.2, desktop-linux context |
| Docker daemon | Not running at initial inventory |
| Native llama.cpp | `llama-server` not found on PATH |
| Model files | No GGUF files found in the project or user cache inspected |
| PC OS / driver / runtime | Unverified; PC not needed for scripted replay |
| Live latency / memory / model compatibility | Not measured |

Follow-up on the same date: Docker Desktop was started and server version 29.7.2
was verified. The fixed-tool container smoke passed 20 checks; isolated document
read and ticket computation each took about 0.3 seconds in that smoke, including
container startup/cleanup. These are two individual observations, not percentiles
or model inference measurements. See [sandbox evidence](sandbox.md).

`make doctor` emits a fresh JSON inventory. It checks project-local models in
`artifacts/models/`, performs no downloads, and does not start services. System
profiler output is reduced to model name, chip, and memory before reporting;
serial numbers and device identifiers are excluded.

This inventory supports starting a small-model feasibility test. It is not proof
that a specific model fits an 8K context or meets a latency target. Reserve disk
for the container image, weights, temporary downloads, and retained artifacts.
