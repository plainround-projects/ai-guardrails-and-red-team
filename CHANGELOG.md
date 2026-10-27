# Changelog

## 0.1.0 - 2026-10-27

- Domain: shop records, two-way redaction with a request-scoped mapping, the input rules and soft signals, the output checks, attack effects, rates with Wilson intervals.
- Application: the support assistant (runtime-played `find_order` tool, data markers), the input guard (rules, then a small classifier for soft signals), the output guard (canary, another customer's identifiers, prompt overlap), the guarded pipeline with a weakening flag, the suites, the gate and the evidence helpers.
- Infrastructure: recorded, OpenAI-compatible and Anthropic chat-model adapters behind one port, the in-memory order lookup, request and log capture for the redaction scan, JSON logging, validated settings.
- Data: 10 customers, 40 orders, 100 attacks, 100 benign questions, 25 held-out attacks, the canary; the false-block limit committed before the first run.
- Evidence pack: manifest with hashes, raw results, table, gate baseline.
- Recorded fixtures: 748 real exchanges with `qwen2.5:1.5b` served by ollama 0.40.6.
- Java (Spring AI 2.0.1) port with ArchUnit and a parity test against the Python results.
- CI: format, lint, types, import rules, unit tests with coverage, audit, e2e replay, the release gate, Java build.
