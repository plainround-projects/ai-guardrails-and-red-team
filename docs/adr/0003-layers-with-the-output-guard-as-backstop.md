# 3. Layers, with the output guard as the backstop

Status: accepted, 2026-10-27

## Context

The input rules were written from the attack suite's phrasing and will miss new wording. Indirect injections do not appear in the customer's message at all.

## Decision

Four layers: redaction (so the model never sees raw personal values), the input guard on the message, the same rules on outside data (tool results, help pages), and the output guard on the reply. The output guard checks effects (canary, another customer's identifiers, overlap with the confidential prompt), so it holds when the input wording is new.

## Consequences

- On 25 held-out attacks in fresh wording, the input rules let most through and the output guard still stopped every leak (0 of 75), against 48% for the bare assistant.
- The output guard cannot stop behavior that leaks nothing checkable, and every layer costs false blocks; the report keeps both numbers.
- The public shop-policy paragraph is excluded from the prompt-overlap check: with it included, 23 of 300 benign runs were blocked for repeating the return policy.
