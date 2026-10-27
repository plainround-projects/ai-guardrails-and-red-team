PYTHON ?= $(shell command -v python3.13 || command -v python3.12 || command -v python3)
VENV := .venv
PY := $(VENV)/bin/python
STAMP := $(VENV)/.installed
PKG := guard_redteam

-include .env
export

.PHONY: help install env up run test test-live lint format audit lock check docker-build down clean baseline guarded compare redaction-scan evidence gate gate-weakened record test-e2e java-test parity

help: ## list the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/' | sort

$(STAMP): requirements-dev.lock pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -q --require-hashes -r requirements-dev.lock
	$(VENV)/bin/pip install -q --no-deps -e .
	touch $@

install: $(STAMP) ## create .venv from the hash-pinned lock file

env:
	@[ -f .env ] || { cp .env.example .env; echo "created .env from .env.example"; }

CLI := $(PY) -m guard_redteam.interfaces.cli
RECORD ?= tests/fixtures/recorded.jsonl

up: env $(STAMP) ## create .venv and .env (no services: the default adapter replays recorded responses)
	@echo "ready: make run | make test | make lint"

run: $(STAMP) env ## the whole study from recorded responses: baseline, guarded, comparison, redaction scan, evidence pack
	$(CLI) all

baseline: $(STAMP) env ## step 1: both suites against the bare assistant (3 runs)
	$(CLI) baseline

guarded: $(STAMP) env ## steps 2 to 4: both suites against the guarded assistant (3 runs)
	$(CLI) guarded

compare: $(STAMP) env ## step 5: before-and-after table with Wilson intervals
	$(CLI) compare

redaction-scan: $(STAMP) env ## step 2: no raw email, card or phone in any captured request or log line
	$(CLI) scan

evidence: $(STAMP) env ## step 6: build evidence/ (hashes, versions, raw results, table, open attacks)
	$(CLI) evidence

gate: $(STAMP) env ## step 7: fail when an attack family's success rises above the recorded value or false blocks pass the limit
	$(CLI) gate

gate-weakened: $(STAMP) env ## step 7: plant a weakening (guard layer deleted) and show that the gate fails and names the cases
	$(CLI) gate --weaken remove_guards

# Needs ollama running with the models in .env.example. New exchanges are appended; known ones are not repeated.
record: $(STAMP) ## re-run everything against local models and append the exchanges to $(RECORD)
	LLM_PROVIDER=local LLM_RECORD_TO=$(RECORD) WORKERS=$${WORKERS:-3} $(CLI) all

test-e2e: $(STAMP) ## replay the study and compare with the committed results, and check the gate catches a weakening
	$(PY) -m pytest tests/e2e -m e2e

java-test: ## step 7 (Java): build and test the Java (Spring AI) port
	cd java && mvn -q -B verify

parity: $(STAMP) ## the Java port reproduces the Python results from the same suites and fixtures
	cd java && mvn -q -B -DskipTests package
	java -jar java/target/guard-redteam-java.jar --data data --prompts prompts --fixtures tests/fixtures --out reports/java
	$(PY) -m guard_redteam.interfaces.cli parity --java reports/java --python reports

down: ## nothing to stop: this project starts no services
	@echo "no services to stop"

lint: $(STAMP) ## ruff check, ruff format check, mypy, import-linter
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy
	$(VENV)/bin/lint-imports

format: $(STAMP) ## apply ruff's formatting and safe fixes
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/ruff format .

# Unit tests run offline against recorded model responses. The domain and application layers must stay at 95% or more.
test: $(STAMP) ## unit tests with coverage (offline, recorded model responses)
	$(PY) -m pytest tests/unit --cov=$(PKG) --cov-report=term
	$(PY) -m coverage report --include='src/$(PKG)/domain/*,src/$(PKG)/application/*' --fail-under=95

test-live: $(STAMP) ## opt-in tests against real models (RUN_LIVE=1; Claude also needs ANTHROPIC_API_KEY)
	RUN_LIVE=1 $(PY) -m pytest tests/live -m live -ra

audit: $(STAMP) ## check the locked dependencies for known vulnerabilities
	$(VENV)/bin/pip-audit --no-deps --disable-pip -r requirements-dev.lock

lock: ## regenerate requirements.lock and requirements-dev.lock (needs uv)
	uv pip compile pyproject.toml --universal --generate-hashes --python-version 3.12 -o requirements.lock
	uv pip compile pyproject.toml --universal --generate-hashes --python-version 3.12 --extra dev -o requirements-dev.lock

check: lint test ## everything that needs no services

docker-build: ## build the container image
	docker build -t ai-guardrails-and-red-team:dev .

clean: down
	rm -rf $(VENV) logs .pytest_cache .mypy_cache .ruff_cache .import_linter_cache .coverage htmlcov
