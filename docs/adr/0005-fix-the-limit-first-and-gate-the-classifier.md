# 5. Fix the limit first, and gate the classifier

Status: accepted, 2026-10-27

## Context

A false-block limit chosen after seeing the guard's results is a justification. The first classifier prompt blocked 10 of 100 benign questions (10%) against a 3% limit.

## Decision

`evals/limits.json` (3%) was committed before the first suite ran. To meet it the classifier prompt was rewritten (v2: a general statement of what is normal and six examples outside both suites), the classifier became a second opinion that only sees messages containing a soft signal, and the `system override` rule became case-sensitive and bracket-aware so that "a system override flag on my parcel" is not blocked. The prompt changelog records each change.

## Consequences

- False blocks went from 10% to 2.3% (7 of 300); of the 20 risky-looking questions 7 of 60 runs are still blocked.
- These changes were made while looking at the benign suite, so the figure is optimistic; the README and the held-out set say so.
