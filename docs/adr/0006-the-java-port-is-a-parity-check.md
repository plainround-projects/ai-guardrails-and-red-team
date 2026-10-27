# 6. The Java port is a parity check

Status: accepted, 2026-10-27

## Context

The lesson asks for the guard layer in Python and in Java on Spring AI, driven by one set of suite files.

## Decision

The Java program reads the same `data/`, `prompts/`, `evals/` and `tests/fixtures/` and writes `baseline.json`, `guarded.json` and `comparison.json` in the Python format. The fixture hash, the regular expressions, the redaction numbering, the prompt rendering and the order of cases are written to match, and `ParityTest` / `make parity` compare every number to 1e-6. The live adapter is Spring AI's `ChatClient` over `OpenAiChatModel`, in the infrastructure package only; ArchUnit forbids `domain` and `application` from touching Spring or the OpenAI SDK. The gate and the evidence pack are Python tools; the Java port covers the guard layer and the suites.

## Consequences

- The Java guard layer demonstrably behaves as the Python one on all 400 cases and 3 runs.
