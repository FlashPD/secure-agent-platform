UV ?= $(shell command -v uv 2>/dev/null || echo .venv/bin/uv)
export UV_CACHE_DIR ?= $(CURDIR)/artifacts/uv-cache

.PHONY: setup check doctor demo-replay sandbox-build sandbox-smoke demo-isolated models-fetch model-serve eval-smoke
PROFILE ?= mac-small

.PHONY: eval-suite eval-suite-live
eval-suite:
	$(UV) run --locked agentguard eval-suite

eval-suite-live:
	$(UV) run --locked agentguard eval-suite --live --model-profile config/model-$(PROFILE).json

setup:
	$(UV) sync --locked

check:
	$(UV) run --locked ruff check .
	$(UV) run --locked ruff format --check .
	$(UV) run --locked mypy src
	$(UV) run --locked pytest

doctor:
	$(UV) run --locked agentguard doctor

demo-replay:
	$(UV) run --locked agentguard demo-replay

sandbox-build:
	$(UV) run --locked agentguard sandbox-build

sandbox-smoke:
	$(UV) run --locked agentguard sandbox-smoke

demo-isolated:
	$(UV) run --locked agentguard demo-replay --sandbox-manifest artifacts/sandbox/manifest.json

models-fetch:
	$(UV) run --locked agentguard models-fetch --profile config/model-$(PROFILE).json

model-serve:
	$(UV) run --locked agentguard model-serve --profile config/model-$(PROFILE).json

eval-smoke:
	$(UV) run --locked agentguard eval-smoke --profile config/model-$(PROFILE).json
