# 4. The runtime plays the tool

Status: accepted, 2026-10-27

## Context

The lesson's assistant answers through a read-only `find_order` tool. The first trial with `qwen2.5:1.5b` and a "reply with `TOOL find_order <id>`" protocol showed the model ignoring the protocol in four of five attempts, which made the cross-customer and indirect families unmeasurable.

## Decision

When the customer's message mentions an order id, the runtime calls `find_order` and puts the record in the prompt between `[TOOL_RESULT]` markers, as an agent framework does after a tool request. The tool stays read-only and unscoped (any order, any customer), because the guard layer is what scopes it. The record includes the order's free-text note, the place an indirect injection hides.

## Consequences

- One model call per request, deterministic tool use, and all five families measurable.
- A model that decides for itself whether to use a tool is not exercised; with a model that follows the protocol the original loop can be restored behind the same port.
