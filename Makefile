UV ?= $(shell command -v uv 2>/dev/null || echo .venv/bin/uv)
export UV_CACHE_DIR ?= $(CURDIR)/artifacts/uv-cache

.PHONY: setup check doctor demo-replay sandbox-build sandbox-smoke demo-isolated models-fetch model-serve eval-smoke
PROFILE ?= mac-small
NODE_BIN := $(CURDIR)/artifacts/runtime/node-v24.21.0-darwin-arm64/bin
export PATH := $(NODE_BIN):$(PATH)
export npm_config_cache ?= $(CURDIR)/artifacts/npm-cache

.PHONY: ui-setup ui-build ui-check ui-test
ui-setup:
	cd frontend && npm ci --ignore-scripts --no-audit --no-fund

ui-build:
	cd frontend && npm run build

ui-check:
	cd frontend && npm run check

ui-test:
	cd frontend && npm test

.PHONY: eval-suite eval-suite-live eval-tools eval-tools-isolated eval-tools-live
.PHONY: eval-multi-attack
eval-multi-attack:
	$(UV) run --locked agentguard eval-suite --suite scenarios/dev/multi-attack-v1.json

eval-tools:
	$(UV) run --locked agentguard eval-suite --suite scenarios/dev/tools-v1.json

eval-tools-isolated:
	$(UV) run --locked agentguard eval-suite --suite scenarios/dev/tools-v1.json --sandbox-manifest artifacts/sandbox/manifest.json

eval-tools-live:
	$(UV) run --locked agentguard eval-suite --suite scenarios/dev/tools-v1.json --live --model-profile config/model-$(PROFILE).json

.PHONY: demo-durable
.PHONY: control-smoke api-serve worker
control-smoke:
	$(UV) run --locked agentguard control-smoke

api-serve:
	$(UV) run --locked agentguard api-serve

worker:
	$(UV) run --locked agentguard worker

demo-durable:
	$(UV) run --locked agentguard demo-durable

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
