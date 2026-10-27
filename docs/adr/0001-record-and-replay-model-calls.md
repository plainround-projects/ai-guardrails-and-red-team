# 1. Record and replay model calls

Status: accepted, 2026-10-27

## Context

The study makes about 750 distinct model calls. It must be reviewable and runnable without a key, a network or a GPU, and the Java port must be able to check itself against the Python results.

## Decision

All model calls go through the `ChatModel` port. The default adapter replays `tests/fixtures/*.jsonl`, whose lines hold a SHA-256 key over the model id, decoding settings (temperature, max tokens, seed) and every message, plus the response with its billed token counts and latency. A recording wrapper appends new exchanges while a real adapter runs and answers from the file when it already holds the key, so a recording run can be interrupted and resumed. A request with no recorded response is a named error (`FixtureMissError`). The Java port computes the same key. The run number is the decoding seed, so three runs are three recorded samples, not one repeated.

## Consequences

- Every number is reproducible offline, and `make test-e2e` proves it byte for byte, including the evidence pack.
- Changing the post-processing (an output check, a rule, a threshold) needs no new recording; changing a prompt or the redaction (which changes what the model sees) does.
- Fixtures keep a readable summary of each request; the key identifies the full request.
