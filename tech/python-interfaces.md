# Python code: the interfaces layer, file by file

## What it is

The **interfaces layer**: how a person or another program starts the code. The command-line program, the HTTP routes and the *wiring* that builds all the parts and connects them live here.

## Why this repository uses it

Someone has to decide which adapter is used with which experiment. That decision is made in one place, the wiring, so the rest of the code stays independent of it.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/guard_redteam/interfaces/__init__.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/interfaces/cli.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/interfaces/wiring.py` | Quoted and explained in the walkthrough below. |


## How it works underneath

The command-line file defines one function per command (`cmd_...`), each taking the wired services and returning an exit code (0 means success). `main` reads the arguments, builds the services and calls the right command. Nothing depends on this layer; it depends on everything below.

## Walkthrough of this repository's use

### Files in this note

| File | Lines | What it is |
| --- | --- | --- |
| `src/guard_redteam/interfaces/__init__.py` | 1 | The interfaces layer. |
| `src/guard_redteam/interfaces/cli.py` | 341 | Command-line entry point: one program, one sub-command per step of the lesson. |
| `src/guard_redteam/interfaces/wiring.py` | 87 | The composition root: build the adapters, the assistant and the guard layer from settings. |

Each file below is quoted exactly, in order, in pieces of about a dozen lines. Under each piece, a bullet list explains every statement in the order it appears. The first time an idea shows up in this note it is explained in a bullet that begins **New idea**.

#### `src/guard_redteam/interfaces/__init__.py`

<!-- fmt: off -->
```python
"""The interfaces layer."""
```
<!-- fmt: on -->

- **New idea.** A **docstring** is a text in triple quotes as the first statement of a module, class or function. Python keeps it as documentation and tools can show it.
- `"""The interfaces layer."""`: a docstring (documentation text). It says: "The interfaces layer."

#### `src/guard_redteam/interfaces/cli.py`

<!-- fmt: off -->
```python
"""Command-line entry point: one program, one sub-command per step of the lesson."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any
```
<!-- fmt: on -->

- `"""Command-line entry point: one program, one sub-command per step of the lesson."""`: a docstring (documentation text). It says: "Command-line entry point: one program, one sub-command per step of the lesson."
- **New idea.** `from __future__ import annotations` turns on a newer behaviour: type annotations are stored as text instead of being evaluated when the file loads.
- **New idea.** An **import** makes the code of another module available. `import x` gives the whole module under the name `x`; `from x import y` gives just the name `y`.
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import argparse`: imports the module(s) `argparse` so this file can use them. `argparse` is command-line option parsing.
- `import hashlib`: imports the module(s) `hashlib` so this file can use them. `hashlib` is hash functions such as SHA-256.
- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `import logging`: imports the module(s) `logging` so this file can use them. `logging` is the standard logging system.
- `import os`: imports the module(s) `os` so this file can use them. `os` is operating-system services such as environment variables and paths.
- `import sys`: imports the module(s) `sys` so this file can use them. `sys` is the running interpreter: arguments, standard streams, exit.
- `from collections.abc import Sequence`: takes the name(s) `Sequence` from the module `collections.abc` (abstract container types used in annotations).
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).

<!-- fmt: off -->
```python
from guard_redteam.application.evidence import comparison_table, open_attacks
from guard_redteam.application.gate import evaluate_gate, recorded_from
from guard_redteam.application.suites import (
    BenignSummary,
    CaseRun,
    FamilyRate,
    benign_summary,
    confusion,
    family_rates,
    run_attacks,
    run_benign,
)
from guard_redteam.domain.redaction import PATTERNS
from guard_redteam.infrastructure.capture import CapturingChatModel, LogCapture
```
<!-- fmt: on -->

- `from guard_redteam.application.evidence import comparison_table, open_attacks`: takes the name(s) `comparison_table, open_attacks` from the module `guard_redteam.application.evidence` (a module of this project).
- `from guard_redteam.application.gate import evaluate_gate, recorded_from`: takes the name(s) `evaluate_gate, recorded_from` from the module `guard_redteam.application.gate` (a module of this project).
- `from guard_redteam.application.suites import (`: takes the name(s) `BenignSummary, CaseRun, FamilyRate, benign_summary, confusion, family_rates, run_attacks, run_benign` from the module `guard_redteam.application.suites` (a module of this project).
- `from guard_redteam.domain.redaction import PATTERNS`: takes the name(s) `PATTERNS` from the module `guard_redteam.domain.redaction` (a module of this project).
- `from guard_redteam.infrastructure.capture import CapturingChatModel, LogCapture`: takes the name(s) `CapturingChatModel, LogCapture` from the module `guard_redteam.infrastructure.capture` (a module of this project).

<!-- fmt: off -->
```python
from guard_redteam.infrastructure.data import load_rows
from guard_redteam.infrastructure.env import ConfigError, process_env
from guard_redteam.infrastructure.logging_setup import configure_logging
from guard_redteam.infrastructure.reports import dump_json, dump_jsonl, load_json
from guard_redteam.interfaces.wiring import WEAKENINGS, Services, build_services

LOG = logging.getLogger("guard_redteam")
# The project folder holds data/, prompts/ and the fixtures; an installed copy (the Docker image) sets PROJECT_ROOT.
ROOT = Path(os.environ.get("PROJECT_ROOT") or Path(__file__).resolve().parents[3])


def _suites(s: Services, guarded: bool, weaken: str | None = None) -> tuple[list[CaseRun], list[CaseRun]]:
    pipeline = s.pipeline(guarded, weaken)
    runs = s.settings.runs
```
<!-- fmt: on -->

- `from guard_redteam.infrastructure.data import load_rows`: takes the name(s) `load_rows` from the module `guard_redteam.infrastructure.data` (a module of this project).
- `from guard_redteam.infrastructure.env import ConfigError, process_env`: takes the name(s) `ConfigError, process_env` from the module `guard_redteam.infrastructure.env` (a module of this project).
- `from guard_redteam.infrastructure.logging_setup import configure_logging`: takes the name(s) `configure_logging` from the module `guard_redteam.infrastructure.logging_setup` (a module of this project).
- `from guard_redteam.infrastructure.reports import dump_json, dump_jsonl, load_json`: takes the name(s) `dump_json, dump_jsonl, load_json` from the module `guard_redteam.infrastructure.reports` (a module of this project).
- `from guard_redteam.interfaces.wiring import WEAKENINGS, Services, build_services`: takes the name(s) `WEAKENINGS, Services, build_services` from the module `guard_redteam.interfaces.wiring` (a module of this project).
- **New idea.** An **assignment** `name = value` makes the name point at the value. A name written in capital letters is, by convention, a constant: it is not meant to change.
- `LOG = logging.getLogger("guard_redteam")`: sets `LOG` to the value of `logging.getLogger('guard_redteam')`. `logging.getLogger('guard_redteam')` is the logger named `'guard_redteam'`.
- `ROOT = Path(os.environ.get("PROJECT_ROOT") or Path(__file__).resolve().parents[3])`: sets `ROOT` to the value of `Path(os.environ.get('PROJECT_ROOT') or Path(__file__).resolve().parents[3])`. `Path(os.environ.get('PROJECT_ROOT') or Path(__file__).resolve().par...` is the file path `os.environ.get('PROJECT_ROOT') or Path(__file__).resolve(...`; `os.environ.get('PROJECT_ROOT')` is the environment variable `'PROJECT_ROOT'` (default (nothing)); `Path(__file__).resolve()` is the absolute form of the path `Path(__file__)`.
- **New idea.** A **function** is a named block of code. `def name(a, b):` defines it; the indented lines are its body. Calling `name(1, 2)` runs the body with `a = 1` and `b = 2`. `return` hands a value back. A parameter written `b=3` has a **default**: it may be left out when calling.
- `def _suites(s: Services, guarded: bool, weaken: str | None = None) -> tuple[list[CaseRu...`: defines the function `_suites` taking s (Services); guarded (bool); weaken (str | None), default None and returns `tuple[list[CaseRun], list[CaseRun]]`.
- `pipeline = s.pipeline(guarded, weaken)`: sets `pipeline` to the value of `s.pipeline(guarded, weaken)`.
- `runs = s.settings.runs`: sets `runs` to the value of `s.settings.runs`.

<!-- fmt: off -->
```python
    attacks = run_attacks(s.attacks, pipeline, s.canary, s.orders.own_values, runs, s.mapper)
    benign = run_benign(s.benign, pipeline, s.orders.own_values, runs, s.mapper)
    return attacks, benign


def _summary(s: Services, attacks: list[CaseRun], benign: list[CaseRun]) -> dict[str, Any]:
    return {
        "runs": s.settings.runs,
        "families": family_rates(attacks, s.settings.runs),
        "benign": benign_summary(benign, s.false_block_limit),
        "input_guard_confusion": confusion(attacks, benign),
    }
```
<!-- fmt: on -->

- `attacks = run_attacks(s.attacks, pipeline, s.canary, s.orders.own_values, runs, s.mapper)`: sets `attacks` to the value of `run_attacks(s.attacks, pipeline, s.canary, s.orders.own_values, runs, s.mapper)`.
- `benign = run_benign(s.benign, pipeline, s.orders.own_values, runs, s.mapper)`: sets `benign` to the value of `run_benign(s.benign, pipeline, s.orders.own_values, runs, s.mapper)`.
- **New idea.** `return value` ends the function and hands the value to the caller. A function that reaches its end without `return` gives back `None` (nothing).
- `return attacks, benign`: ends the function and hands back `(attacks, benign)`.
- `def _summary(s: Services, attacks: list[CaseRun], benign: list[CaseRun]) -> dict[str, A...`: defines the function `_summary` taking s (Services); attacks (list[CaseRun]); benign (list[CaseRun]) and returns `dict[str, Any]`.
- `return {`: ends the function and hands back `{'runs': s.settings.runs, 'families': family_rates(attacks, s.settings.runs),...`.

<!-- fmt: off -->
```python
def _write_side(s: Services, name: str, attacks: list[CaseRun], benign: list[CaseRun]) -> dict[str, Any]:
    out = s.settings.reports_dir
    dump_jsonl(out / f"{name}_attacks.jsonl", attacks)
    dump_jsonl(out / f"{name}_benign.jsonl", benign)
    summary = _summary(s, attacks, benign)
    dump_json(out / f"{name}.json", summary)
    return summary


def _print_side(name: str, summary: dict[str, Any], limit: float) -> None:
    for family, f in summary["families"].items():
        r = f.rate
        print(
            f"{name:9} {family:19} attack success {r.successes}/{r.trials} = {r.value:.1%}  per run {list(f.per_run)}"
        )
```
<!-- fmt: on -->

- `def _write_side(s: Services, name: str, attacks: list[CaseRun], benign: list[CaseRun]) ...`: defines the function `_write_side` taking s (Services); name (str); attacks (list[CaseRun]); benign (list[CaseRun]) and returns `dict[str, Any]`.
- `out = s.settings.reports_dir`: sets `out` to the value of `s.settings.reports_dir`.
- `dump_jsonl(out / f"{name}_attacks.jsonl", attacks)`: runs `dump_jsonl(out / f'{name}_attacks.jsonl', attacks)` for its effect and ignores the result. the f-string inserts `name` into the text.
- `dump_jsonl(out / f"{name}_benign.jsonl", benign)`: runs `dump_jsonl(out / f'{name}_benign.jsonl', benign)` for its effect and ignores the result. the f-string inserts `name` into the text.
- `summary = _summary(s, attacks, benign)`: sets `summary` to the value of `_summary(s, attacks, benign)`.
- `dump_json(out / f"{name}.json", summary)`: runs `dump_json(out / f'{name}.json', summary)` for its effect and ignores the result. the f-string inserts `name` into the text.
- `return summary`: ends the function and hands back `summary`.
- `def _print_side(name: str, summary: dict[str, Any], limit: float) -> None:`: defines the function `_print_side` taking name (str); summary (dict[str, Any]); limit (float) and returns `None`.
- **New idea.** A **for loop** `for x in items:` runs its block once for each item, with `x` naming the current item. `break` leaves the loop early; `continue` skips to the next item.
- `for family, f in summary["families"].items():`: repeats the block below once for each `(family, f)` in `summary['families'].items()`. `summary['families'].items()` is the (key, value) pairs of `summary['families']`.
- `r = f.rate`: sets `r` to the value of `f.rate`.
- `print(`: runs `print(f'{name:9} {family:19} attack success {r.successes}/{r.trials} = {r.value:.1%} pe...` for its effect and ignores the result. `print(f'{name:9} {family:19} attack success {r.successes}/{r.trials...` prints `f'{name:9} {family:19} attack success {r.successes}/{r.tr...`; the f-string inserts `name`, `family`, `r.successes`, `r.trials` into the text; `list(f.per_run)` is `f.per_run` copied into a list.

<!-- fmt: off -->
```python
    b = summary["benign"]
    fb, risky = b.false_blocks, b.risky_false_blocks
    print(
        f"{name:9} false blocks {fb.successes}/{fb.trials} = {fb.value:.1%} (limit {limit:.0%}); "
        f"risky-looking {risky.successes}/{risky.trials}"
    )


def cmd_baseline(s: Services) -> None:
    """Step 1: both suites against the bare assistant."""
    attacks, benign = _suites(s, guarded=False)
    _print_side("bare", _write_side(s, "baseline", attacks, benign), s.false_block_limit)
```
<!-- fmt: on -->

- `b = summary["benign"]`: sets `b` to the value of `summary['benign']`.
- `fb, risky = b.false_blocks, b.risky_false_blocks`: sets `(fb, risky)` to a tuple of 2 items.
- `print(`: runs `print(f'{name:9} false blocks {fb.successes}/{fb.trials} = {fb.value:.1%} (limit {limit...` for its effect and ignores the result. `print(f'{name:9} false blocks {fb.successes}/{fb.trials} = {fb.valu...` prints `f'{name:9} false blocks {fb.successes}/{fb.trials} = {fb....`; the f-string inserts `name`, `fb.successes`, `fb.trials`, `fb.value` into the text.
- `def cmd_baseline(s: Services) -> None:`: defines the function `cmd_baseline` taking s (Services) and returns `None`. Purpose: Step 1: both suites against the bare assistant.
- `"""Step 1: both suites against the bare assistant."""`: a docstring (documentation text). It says: "Step 1: both suites against the bare assistant."
- `attacks, benign = _suites(s, guarded=False)`: sets `(attacks, benign)` to the value of `_suites(s, guarded=False)`.
- `_print_side("bare", _write_side(s, "baseline", attacks, benign), s.false_block_limit)`: runs `_print_side('bare', _write_side(s, 'baseline', attacks, benign), s.false_block_limit)` for its effect and ignores the result.

<!-- fmt: off -->
```python
def cmd_guarded(s: Services) -> None:
    """Steps 2 to 4: both suites against the guarded assistant."""
    attacks, benign = _suites(s, guarded=True)
    summary = _write_side(s, "guarded", attacks, benign)
    _print_side("guarded", summary, s.false_block_limit)
    print(f"input guard confusion matrix over all cases and runs: {summary['input_guard_confusion']}")
    risky = sorted({r.case_id: None for r in benign if r.risky and r.blocked})
    print(f"false blocks among the risky-looking benign questions, by case id: {risky or 'none'}")


def cmd_heldout(s: Services) -> None:
    """Twenty-five attacks written after the guard layer was frozen: what the suite's 0% is worth on new wording."""
    runs = s.settings.runs
    result: dict[str, Any] = {"runs": runs, "cases": len(s.heldout)}
```
<!-- fmt: on -->

- `def cmd_guarded(s: Services) -> None:`: defines the function `cmd_guarded` taking s (Services) and returns `None`. Purpose: Steps 2 to 4: both suites against the guarded assistant.
- `"""Steps 2 to 4: both suites against the guarded assistant."""`: a docstring (documentation text). It says: "Steps 2 to 4: both suites against the guarded assistant."
- `attacks, benign = _suites(s, guarded=True)`: sets `(attacks, benign)` to the value of `_suites(s, guarded=True)`.
- `summary = _write_side(s, "guarded", attacks, benign)`: sets `summary` to the value of `_write_side(s, 'guarded', attacks, benign)`.
- `_print_side("guarded", summary, s.false_block_limit)`: runs `_print_side('guarded', summary, s.false_block_limit)` for its effect and ignores the result.
- `print(f"input guard confusion matrix over all cases and runs: {summary['input_guard_con...`: runs `print(f"input guard confusion matrix over all cases and runs: {summary['input_guard_con...` for its effect and ignores the result. `print(f"input guard confusion matrix over all cases and runs: {summ...` prints `f"input guard confusion matrix over all cases and runs: {...`; the f-string inserts `summary['input_guard_confus...` into the text.
- `risky = sorted({r.case_id: None for r in benign if r.risky and r.blocked})`: sets `risky` to the value of `sorted({r.case_id: None for r in benign if r.risky and r.blocked})`. `sorted({r.case_id: None for r in benign if r.risky and r.blocked})` is `{r.case_id: None for r in benign if r.risky and r.blocked}` in sorted order; `{r.case_id: None for r in benign if r.risky and r.blocked}` builds a dictionary: for each `r` in `benign`, keeping only those for which `r.risky and r.blocked` is true.
- `print(f"false blocks among the risky-looking benign questions, by case id: {risky or 'n...`: runs `print(f"false blocks among the risky-looking benign questions, by case id: {risky or 'n...` for its effect and ignores the result. `print(f"false blocks among the risky-looking benign questions, by c...` prints `f"false blocks among the risky-looking benign questions, ...`; the f-string inserts `risky or 'none'` into the text.
- `def cmd_heldout(s: Services) -> None:`: defines the function `cmd_heldout` taking s (Services) and returns `None`. Purpose: Twenty-five attacks written after the guard layer was frozen: what the suite's 0% is worth on new wording.
- `"""Twenty-five attacks written after the guard layer was frozen: what the suite's 0% is...`: a docstring (documentation text). It says: "Twenty-five attacks written after the guard layer was frozen: what the suite's 0% is worth on new wording."
- `runs = s.settings.runs`: sets `runs` to the value of `s.settings.runs`.
- **New idea.** An **annotated assignment** `name: type = value` also says what kind of value the name should hold. The annotation is a hint for readers and for mypy (`mypy.md`); Python does not enforce it.
- `result: dict[str, Any] = {"runs": runs, "cases": len(s.heldout)}`: declares a variable `result` of type `dict[str, Any]` and sets it to `{'runs': runs, 'cases': len(s.heldout)}`. `len(s.heldout)` is the number of items in `s.heldout`.

<!-- fmt: off -->
```python
    for name, guarded in (("bare", False), ("guarded", True)):
        pipeline = s.pipeline(guarded)
        rows = run_attacks(s.heldout, pipeline, s.canary, s.orders.own_values, runs, s.mapper)
        dump_jsonl(s.settings.reports_dir / f"heldout_{name}.jsonl", rows)
        result[name] = family_rates(rows, runs)
        total = sum(1 for r in rows if r.succeeded)
        winners = sorted({r.case_id for r in rows if r.succeeded})
        share = total / len(rows)
        worked = winners or "none"
        print(f"held-out {name:8} attack success {total}/{len(rows)} = {share:.1%}; cases that worked: {worked}")
    dump_json(s.settings.reports_dir / "heldout.json", result)


def _load_side(s: Services, name: str) -> tuple[list[CaseRun], list[CaseRun]]:
```
<!-- fmt: on -->

- `for name, guarded in (("bare", False), ("guarded", True)):`: repeats the block below once for each `(name, guarded)` in `(('bare', False), ('guarded', True))`.
- `pipeline = s.pipeline(guarded)`: sets `pipeline` to the value of `s.pipeline(guarded)`.
- `rows = run_attacks(s.heldout, pipeline, s.canary, s.orders.own_values, runs, s.mapper)`: sets `rows` to the value of `run_attacks(s.heldout, pipeline, s.canary, s.orders.own_values, runs, s.mapper)`.
- `dump_jsonl(s.settings.reports_dir / f"heldout_{name}.jsonl", rows)`: runs `dump_jsonl(s.settings.reports_dir / f'heldout_{name}.jsonl', rows)` for its effect and ignores the result. the f-string inserts `name` into the text.
- `result[name] = family_rates(rows, runs)`: sets `result[name]` to the value of `family_rates(rows, runs)`.
- `total = sum(1 for r in rows if r.succeeded)`: sets `total` to the value of `sum((1 for r in rows if r.succeeded))`. `sum((1 for r in rows if r.succeeded))` is the sum of `(1 for r in rows if r.succeeded)`; `(1 for r in rows if r.succeeded)` builds a generator of values: for each `r` in `rows`, keeping only those for which `r.succeeded` is true.
- `winners = sorted({r.case_id for r in rows if r.succeeded})`: sets `winners` to the value of `sorted({r.case_id for r in rows if r.succeeded})`. `sorted({r.case_id for r in rows if r.succeeded})` is `{r.case_id for r in rows if r.succeeded}` in sorted order; `{r.case_id for r in rows if r.succeeded}` builds a set: for each `r` in `rows`, keeping only those for which `r.succeeded` is true.
- `share = total / len(rows)`: sets `share` to the value of `total / len(rows)`. `len(rows)` is the number of items in `rows`.
- `worked = winners or "none"`: sets `worked` to the value of `winners or 'none'`.
- `print(f"held-out {name:8} attack success {total}/{len(rows)} = {share:.1%}; cases that ...`: runs `print(f'held-out {name:8} attack success {total}/{len(rows)} = {share:.1%}; cases that ...` for its effect and ignores the result. `print(f'held-out {name:8} attack success {total}/{len(rows)} = {sha...` prints `f'held-out {name:8} attack success {total}/{len(rows)} = ...`; the f-string inserts `name`, `total`, `len(rows)`, `share` into the text; `len(rows)` is the number of items in `rows`.
- `dump_json(s.settings.reports_dir / "heldout.json", result)`: runs `dump_json(s.settings.reports_dir / 'heldout.json', result)` for its effect and ignores the result.
- `def _load_side(s: Services, name: str) -> tuple[list[CaseRun], list[CaseRun]]:`: defines the function `_load_side` taking s (Services); name (str) and returns `tuple[list[CaseRun], list[CaseRun]]`.

<!-- fmt: off -->
```python
    out = s.settings.reports_dir

    def rows(kind: str) -> list[CaseRun]:
        return [
            CaseRun(**{**r, "reasons": tuple(r["reasons"]), "unresolved": tuple(r["unresolved"])})
            for r in load_rows(out / f"{name}_{kind}.jsonl")
        ]

    return rows("attacks"), rows("benign")


def cmd_compare(s: Services) -> None:
    """Step 5: the before-and-after table."""
    runs = s.settings.runs
```
<!-- fmt: on -->

- `out = s.settings.reports_dir`: sets `out` to the value of `s.settings.reports_dir`.
- **New idea.** A function defined inside another function is a **closure**: it can read the variables of the function around it, even after that function has returned.
- `def rows(kind: str) -> list[CaseRun]:`: defines the function `rows` taking kind (str) and returns `list[CaseRun]`.
- `return [`: ends the function and hands back `[CaseRun(**{**r, 'reasons': tuple(r['reasons']), 'unresolved': tuple(r['unres...`. `[CaseRun(**{**r, 'reasons': tuple(r['reasons']), 'unresolved': tupl...` builds a list: for each `r` in `load_rows(out / f'{name}_{kind}.jsonl')`; `tuple(r['reasons'])` is `r['reasons']` as a tuple; `tuple(r['unresolved'])` is `r['unresolved']` as a tuple.
- `return rows("attacks"), rows("benign")`: ends the function and hands back `(rows('attacks'), rows('benign'))`.
- `def cmd_compare(s: Services) -> None:`: defines the function `cmd_compare` taking s (Services) and returns `None`. Purpose: Step 5: the before-and-after table.
- `"""Step 5: the before-and-after table."""`: a docstring (documentation text). It says: "Step 5: the before-and-after table."
- `runs = s.settings.runs`: sets `runs` to the value of `s.settings.runs`.

<!-- fmt: off -->
```python
    before_a, before_b = _load_side(s, "baseline")
    after_a, after_b = _load_side(s, "guarded")
    before, after = family_rates(before_a, runs), family_rates(after_a, runs)
    bb, ab = benign_summary(before_b, s.false_block_limit), benign_summary(after_b, s.false_block_limit)
    table = comparison_table(before, after, bb, ab, s.false_block_limit, runs)
    dump_json(
        s.settings.reports_dir / "comparison.json",
        {
            "before": before,
            "after": after,
            "benign_before": bb,
            "benign_after": ab,
            "false_block_limit": s.false_block_limit,
        },
    )
```
<!-- fmt: on -->

- `before_a, before_b = _load_side(s, "baseline")`: sets `(before_a, before_b)` to the value of `_load_side(s, 'baseline')`.
- `after_a, after_b = _load_side(s, "guarded")`: sets `(after_a, after_b)` to the value of `_load_side(s, 'guarded')`.
- `before, after = family_rates(before_a, runs), family_rates(after_a, runs)`: sets `(before, after)` to a tuple of 2 items.
- `bb, ab = benign_summary(before_b, s.false_block_limit), benign_summary(after_b, s.false...`: sets `(bb, ab)` to a tuple of 2 items.
- `table = comparison_table(before, after, bb, ab, s.false_block_limit, runs)`: sets `table` to the value of `comparison_table(before, after, bb, ab, s.false_block_limit, runs)`.
- `dump_json(`: runs `dump_json(s.settings.reports_dir / 'comparison.json', {'before': before, 'after': after...` for its effect and ignores the result.

<!-- fmt: off -->
```python
    (s.settings.reports_dir / "REPORT.md").write_text(
        "# Guardrails and red team: results\n\n" + table, encoding="utf-8"
    )
    print(table)


def cmd_scan(s: Services) -> None:
    """Step 2: no planted raw value reaches a captured model request or a log line."""
    capture = CapturingChatModel(s.model)
    handler = LogCapture()
    root = logging.getLogger()
    root.addHandler(handler)
    try:
        pipeline = s.pipeline(True, model=capture)
```
<!-- fmt: on -->

- `(s.settings.reports_dir / "REPORT.md").write_text(`: runs `(s.settings.reports_dir / 'REPORT.md').write_text('# Guardrails and red team: results\n...` for its effect and ignores the result. `(s.settings.reports_dir / 'REPORT.md').write_text('# Guardrails and...` writes `'# Guardrails and red team: results\n\n' + table` as the content of the file `s.settings.reports_dir / 'REPORT.md'`.
- `print(table)`: runs `print(table)` for its effect and ignores the result. `print(table)` prints `table`.
- `def cmd_scan(s: Services) -> None:`: defines the function `cmd_scan` taking s (Services) and returns `None`. Purpose: Step 2: no planted raw value reaches a captured model request or a log line.
- `"""Step 2: no planted raw value reaches a captured model request or a log line."""`: a docstring (documentation text). It says: "Step 2: no planted raw value reaches a captured model request or a log line."
- `capture = CapturingChatModel(s.model)`: sets `capture` to the value of `CapturingChatModel(s.model)`.
- `handler = LogCapture()`: sets `handler` to the value of `LogCapture()`.
- `root = logging.getLogger()`: sets `root` to the value of `logging.getLogger()`. `logging.getLogger()` is the logger named (nothing).
- `root.addHandler(handler)`: runs `root.addHandler(handler)` for its effect and ignores the result. `root.addHandler(handler)` adds a handler to the logger `root`.
- **New idea.** **try/except** handles errors. The code in `try:` runs; if it raises an error of the type named in `except`, Python jumps to that block instead of stopping. `finally:` always runs, error or not. `else:` runs only when no error occurred.
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.
- `pipeline = s.pipeline(True, model=capture)`: sets `pipeline` to the value of `s.pipeline(True, model=capture)`.

<!-- fmt: off -->
```python
        rows = run_benign(s.benign, pipeline, s.orders.own_values, s.settings.runs, s.mapper)
    finally:
        root.removeHandler(handler)
    planted = sorted(
        {m.strip(" .,;") for case in s.benign for pattern in PATTERNS.values() for m in pattern.findall(case.message)}
    )
    haystacks = [*capture.requests, *handler.lines]
    leaks = [
        {"value": v, "occurrences": sum(h.count(v) for h in haystacks)}
        for v in planted
        if any(v in h for h in haystacks)
    ]
    result = {
        "planted_values": planted,
        "model_requests_scanned": len(capture.requests),
        "log_lines_scanned": len(handler.lines),
        "leaks": leaks,
        "replies_with_unresolved_placeholder": sum(1 for r in rows if r.unresolved),
    }
```
<!-- fmt: on -->

- `rows = run_benign(s.benign, pipeline, s.orders.own_values, s.settings.runs, s.mapper)`: sets `rows` to the value of `run_benign(s.benign, pipeline, s.orders.own_values, s.settings.runs, s.mapper)`.
- `finally:` runs always, whether or not an error occurred (used for clean-up).
- `root.removeHandler(handler)`: runs `root.removeHandler(handler)` for its effect and ignores the result.
- `planted = sorted(`: sets `planted` to the value of `sorted({m.strip(' .,;') for case in s.benign for pattern in PATTERNS.values()...`. `sorted({m.strip(' .,;') for case in s.benign for pattern in PATTERN...` is `{m.strip(' .,;') for case in s.benign for pattern in PATT...` in sorted order; `{m.strip(' .,;') for case in s.benign for pattern in PATTERNS.value...` builds a set: for each `case` in `s.benign`; `m.strip(' .,;')` is `m` without white space at both ends.
- `haystacks = [*capture.requests, *handler.lines]`: sets `haystacks` to a list of 2 items. `*capture.requests` spreads the items of `capture.requests` into separate values; `*handler.lines` spreads the items of `handler.lines` into separate values.
- `leaks = [`: sets `leaks` to the value of `[{'value': v, 'occurrences': sum((h.count(v) for h in haystacks))} for v in p...`. `[{'value': v, 'occurrences': sum((h.count(v) for h in haystacks))} ...` builds a list: for each `v` in `planted`, keeping only those for which `any((v in h for h in haystacks))` is true; `sum((h.count(v) for h in haystacks))` is the sum of `(h.count(v) for h in haystacks)`; `any((v in h for h in haystacks))` is true if any item of `(v in h for h in haystacks)` is true.
- `result = {`: sets `result` to a dictionary with 5 entries. `len(capture.requests)` is the number of items in `capture.requests`; `len(handler.lines)` is the number of items in `handler.lines`; `sum((1 for r in rows if r.unresolved))` is the sum of `(1 for r in rows if r.unresolved)`.

<!-- fmt: off -->
```python
    dump_json(s.settings.reports_dir / "redaction_scan.json", result)
    print(
        f"redaction scan: {len(planted)} planted values, {len(capture.requests)} requests, "
        f"{len(handler.lines)} log lines, leaks: {len(leaks)}, unresolved placeholders in replies: "
        f"{result['replies_with_unresolved_placeholder']}"
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cmd_evidence(s: Services) -> int:
    """Step 6: build evidence/ and fail if an attack that still works has no recorded decision."""
```
<!-- fmt: on -->

- `dump_json(s.settings.reports_dir / "redaction_scan.json", result)`: runs `dump_json(s.settings.reports_dir / 'redaction_scan.json', result)` for its effect and ignores the result.
- `print(`: runs `print(f"redaction scan: {len(planted)} planted values, {len(capture.requests)} requests...` for its effect and ignores the result. `print(f"redaction scan: {len(planted)} planted values, {len(capture...` prints `f"redaction scan: {len(planted)} planted values, {len(cap...`; the f-string inserts `len(planted)`, `len(capture.requests)`, `len(handler.lines)`, `len(leaks)` into the text; `len(planted)` is the number of items in `planted`.
- `def _sha256(path: Path) -> str:`: defines the function `_sha256` taking path (Path) and returns `str`.
- `return hashlib.sha256(path.read_bytes()).hexdigest()`: ends the function and hands back `hashlib.sha256(path.read_bytes()).hexdigest()`. `hashlib.sha256(path.read_bytes()).hexdigest()` is the hash as hexadecimal text; `hashlib.sha256(path.read_bytes())` is a SHA-256 hash object of `path.read_bytes()`; `path.read_bytes()` is the bytes of the file `path`.
- `def cmd_evidence(s: Services) -> int:`: defines the function `cmd_evidence` taking s (Services) and returns `int`. Purpose: Step 6: build evidence/ and fail if an attack that still works has no recorded decision.
- `"""Step 6: build evidence/ and fail if an attack that still works has no recorded decis...`: a docstring (documentation text). It says: "Step 6: build evidence/ and fail if an attack that still works has no recorded decision."

<!-- fmt: off -->
```python
    runs = s.settings.runs
    out, ev = s.settings.reports_dir, s.settings.evidence_dir
    ev.mkdir(parents=True, exist_ok=True)
    (ev / "results").mkdir(exist_ok=True)
    for name in ("baseline_attacks", "baseline_benign", "guarded_attacks", "guarded_benign"):
        (ev / "results" / f"{name}.jsonl").write_text(
            (out / f"{name}.jsonl").read_text(encoding="utf-8"), encoding="utf-8"
        )
    before_a, before_b = _load_side(s, "baseline")
    after_a, after_b = _load_side(s, "guarded")
    before, after = family_rates(before_a, runs), family_rates(after_a, runs)
    bb, ab = benign_summary(before_b, s.false_block_limit), benign_summary(after_b, s.false_block_limit)
    (ev / "table.md").write_text(comparison_table(before, after, bb, ab, s.false_block_limit, runs), encoding="utf-8")
    dump_json(ev / "recorded_rates.json", recorded_from(after, ab, s.false_block_limit))
```
<!-- fmt: on -->

- `runs = s.settings.runs`: sets `runs` to the value of `s.settings.runs`.
- `out, ev = s.settings.reports_dir, s.settings.evidence_dir`: sets `(out, ev)` to a tuple of 2 items.
- `ev.mkdir(parents=True, exist_ok=True)`: runs `ev.mkdir(parents=True, exist_ok=True)` for its effect and ignores the result. `ev.mkdir(parents=True, exist_ok=True)` creates the folder `ev`.
- `(ev / "results").mkdir(exist_ok=True)`: runs `(ev / 'results').mkdir(exist_ok=True)` for its effect and ignores the result. `(ev / 'results').mkdir(exist_ok=True)` creates the folder `ev / 'results'`.
- `for name in ("baseline_attacks", "baseline_benign", "guarded_attacks", "guarded_benign"):`: repeats the block below once for each `name` in `('baseline_attacks', 'baseline_benign', 'guarded_attacks', 'guarded...`.
- `(ev / "results" / f"{name}.jsonl").write_text(`: runs `(ev / 'results' / f'{name}.jsonl').write_text((out / f'{name}.jsonl').read_text(encodin...` for its effect and ignores the result. `(ev / 'results' / f'{name}.jsonl').write_text((out / f'{name}.jsonl...` writes `(out / f'{name}.jsonl').read_text(encoding='utf-8')` as the content of the file `ev / 'results' / f'{name}.jsonl'`; `(out / f'{name}.jsonl').read_text(encoding='utf-8')` is the whole text of the file `out / f'{name}.jsonl'`; the f-string inserts `name` into the text.
- `before_a, before_b = _load_side(s, "baseline")`: sets `(before_a, before_b)` to the value of `_load_side(s, 'baseline')`.
- `after_a, after_b = _load_side(s, "guarded")`: sets `(after_a, after_b)` to the value of `_load_side(s, 'guarded')`.
- `before, after = family_rates(before_a, runs), family_rates(after_a, runs)`: sets `(before, after)` to a tuple of 2 items.
- `bb, ab = benign_summary(before_b, s.false_block_limit), benign_summary(after_b, s.false...`: sets `(bb, ab)` to a tuple of 2 items.
- `(ev / "table.md").write_text(comparison_table(before, after, bb, ab, s.false_block_limi...`: runs `(ev / 'table.md').write_text(comparison_table(before, after, bb, ab, s.false_block_limi...` for its effect and ignores the result. `(ev / 'table.md').write_text(comparison_table(before, after, bb, ab...` writes `comparison_table(before, after, bb, ab, s.false_block_lim...` as the content of the file `ev / 'table.md'`.
- `dump_json(ev / "recorded_rates.json", recorded_from(after, ab, s.false_block_limit))`: runs `dump_json(ev / 'recorded_rates.json', recorded_from(after, ab, s.false_block_limit))` for its effect and ignores the result.

<!-- fmt: off -->
```python
    decisions_path = s.settings.evals_dir / "decisions.json"
    decisions = json.loads(decisions_path.read_text(encoding="utf-8")) if decisions_path.exists() else {}
    open_rows, undecided = open_attacks(after_a, decisions)
    dump_json(ev / "open_attacks.json", open_rows)
    files = {
        **{f"data/{p.name}": _sha256(p) for p in sorted(s.settings.data_dir.glob("*.jsonl"))},
        "data/canary.txt": _sha256(s.settings.data_dir / "canary.txt"),
        **{f"prompts/{p.name}": _sha256(p) for p in sorted(s.settings.prompts_dir.glob("*.md"))},
        "evals/limits.json": _sha256(s.settings.evals_dir / "limits.json"),
    }
    fixtures = sorted(s.settings.fixtures_dir.glob("*.jsonl"))
    manifest = {
        "assistant_model": s.settings.assistant_model,
        "guard_model": s.settings.guard_model,
        "temperature": s.settings.temperature,
        "runs": runs,
        "guard_version": "guard.v1",
        "hashes": files,
        "fixtures": {p.name: _sha256(p) for p in fixtures},
        "reproduce": "make run   (offline, from tests/fixtures); then make evidence",
    }
```
<!-- fmt: on -->

- `decisions_path = s.settings.evals_dir / "decisions.json"`: sets `decisions_path` to the value of `s.settings.evals_dir / 'decisions.json'`.
- `decisions = json.loads(decisions_path.read_text(encoding="utf-8")) if decisions_path.ex...`: sets `decisions` to the value of `json.loads(decisions_path.read_text(encoding='utf-8')) if decisions_path.exis...`. `json.loads(decisions_path.read_text(encoding='utf-8')) if decisions...` gives `json.loads(decisions_path.read_text(e...` when `decisions_path.exists()` is true, otherwise `{}`; `decisions_path.exists()` is whether `decisions_path` exists; `json.loads(decisions_path.read_text(encoding='utf-8'))` is the JSON text `decisions_path.read_text(encoding='utf-8')` turned into Python values.
- `open_rows, undecided = open_attacks(after_a, decisions)`: sets `(open_rows, undecided)` to the value of `open_attacks(after_a, decisions)`.
- `dump_json(ev / "open_attacks.json", open_rows)`: runs `dump_json(ev / 'open_attacks.json', open_rows)` for its effect and ignores the result.
- `files = {`: sets `files` to a dictionary with 4 entries. `{f'data/{p.name}': _sha256(p) for p in sorted(s.settings.data_dir.g...` builds a dictionary: for each `p` in `sorted(s.settings.data_dir.glob('*.js...`; `{f'prompts/{p.name}': _sha256(p) for p in sorted(s.settings.prompts...` builds a dictionary: for each `p` in `sorted(s.settings.prompts_dir.glob('*...`; the f-string inserts `p.name` into the text.
- `fixtures = sorted(s.settings.fixtures_dir.glob("*.jsonl"))`: sets `fixtures` to the value of `sorted(s.settings.fixtures_dir.glob('*.jsonl'))`. `sorted(s.settings.fixtures_dir.glob('*.jsonl'))` is `s.settings.fixtures_dir.glob('*.jsonl')` in sorted order; `s.settings.fixtures_dir.glob('*.jsonl')` is the files of `s.settings.fixtures_dir` that match `'*.jsonl'`.
- `manifest = {`: sets `manifest` to a dictionary with 8 entries. `{p.name: _sha256(p) for p in fixtures}` builds a dictionary: for each `p` in `fixtures`.

````python
    dump_json(ev / "MANIFEST.json", manifest)
    (ev / "REPRODUCE.md").write_text(
        "# Reproduce\n\n```bash\nmake up && make run\n```\n\n"
        "From a clean checkout this rebuilds `reports/` and `evidence/` offline from the recorded fixtures; "
        "`table.md` must match the committed one exactly.\n",
        encoding="utf-8",
    )
    print(f"evidence pack written to {ev}; attacks still working: {len(open_rows)}; undecided: {undecided or 'none'}")
    return 1 if undecided else 0


def cmd_gate(s: Services, weaken: str | None) -> int:
    """Step 7: run the guarded suites (optionally with a planted weakening) and compare with the recorded rates."""
    attacks, benign = _suites(s, guarded=True, weaken=weaken)
````

- `dump_json(ev / "MANIFEST.json", manifest)`: runs `dump_json(ev / 'MANIFEST.json', manifest)` for its effect and ignores the result.
- `(ev / "REPRODUCE.md").write_text(`: runs `(ev / 'REPRODUCE.md').write_text('# Reproduce\n\n'''bash\nmake up && make run\n'''\n\nF...` for its effect and ignores the result. `(ev / 'REPRODUCE.md').write_text('# Reproduce\n\n'''bash\nmake up &...` writes `'# Reproduce\n\n'''bash\nmake up && make run\n'''\n\nFrom...` as the content of the file `ev / 'REPRODUCE.md'`.
- `print(f"evidence pack written to {ev}; attacks still working: {len(open_rows)}; undecid...`: runs `print(f"evidence pack written to {ev}; attacks still working: {len(open_rows)}; undecid...` for its effect and ignores the result. `print(f"evidence pack written to {ev}; attacks still working: {len(...` prints `f"evidence pack written to {ev}; attacks still working: {...`; the f-string inserts `ev`, `len(open_rows)`, `undecided or 'none'` into the text; `len(open_rows)` is the number of items in `open_rows`.
- `return 1 if undecided else 0`: ends the function and hands back `1 if undecided else 0`. `1 if undecided else 0` gives `1` when `undecided` is true, otherwise `0`.
- `def cmd_gate(s: Services, weaken: str | None) -> int:`: defines the function `cmd_gate` taking s (Services); weaken (str | None) and returns `int`. Purpose: Step 7: run the guarded suites (optionally with a planted weakening) and compare with the recorded rates.
- `"""Step 7: run the guarded suites (optionally with a planted weakening) and compare wit...`: a docstring (documentation text). It says: "Step 7: run the guarded suites (optionally with a planted weakening) and compare with the recorded rates."
- `attacks, benign = _suites(s, guarded=True, weaken=weaken)`: sets `(attacks, benign)` to the value of `_suites(s, guarded=True, weaken=weaken)`.

<!-- fmt: off -->
```python
    recorded = load_json(s.settings.evidence_dir / "recorded_rates.json")
    families: dict[str, FamilyRate] = family_rates(attacks, s.settings.runs)
    summary: BenignSummary = benign_summary(benign, s.false_block_limit)
    result = evaluate_gate(families, summary, recorded, s.false_block_limit)
    label = f" (planted weakening: {weaken})" if weaken else ""
    if result.passed:
        print(
            f"GATE PASSED{label}: no family is above its recorded attack success and false blocks are within the limit"
        )
        return 0
    print(f"GATE FAILED{label}:")
    for failure in result.failures:
        print(f"  - {failure}")
    return 1
```
<!-- fmt: on -->

- `recorded = load_json(s.settings.evidence_dir / "recorded_rates.json")`: sets `recorded` to the value of `load_json(s.settings.evidence_dir / 'recorded_rates.json')`.
- `families: dict[str, FamilyRate] = family_rates(attacks, s.settings.runs)`: declares a variable `families` of type `dict[str, FamilyRate]` and sets it to `family_rates(attacks, s.settings.runs)`.
- `summary: BenignSummary = benign_summary(benign, s.false_block_limit)`: declares a variable `summary` of type `BenignSummary` and sets it to `benign_summary(benign, s.false_block_limit)`.
- `result = evaluate_gate(families, summary, recorded, s.false_block_limit)`: sets `result` to the value of `evaluate_gate(families, summary, recorded, s.false_block_limit)`.
- `label = f" (planted weakening: {weaken})" if weaken else ""`: sets `label` to the value of `f' (planted weakening: {weaken})' if weaken else ''`. `f' (planted weakening: {weaken})' if weaken else ''` gives `f' (planted weakening: {weaken})'` when `weaken` is true, otherwise `''`; the f-string inserts `weaken` into the text.
- **New idea.** An **if** statement runs its indented block only when the condition is true. `elif` adds another condition to try; `else` runs when none held.
- `if result.passed:`: runs the block below only if `result.passed` is true.
- `print(`: runs `print(f'GATE PASSED{label}: no family is above its recorded attack success and false bl...` for its effect and ignores the result. `print(f'GATE PASSED{label}: no family is above its recorded attack ...` prints `f'GATE PASSED{label}: no family is above its recorded att...`; the f-string inserts `label` into the text.
- `return 0`: ends the function and hands back `0`.
- `print(f"GATE FAILED{label}:")`: runs `print(f'GATE FAILED{label}:')` for its effect and ignores the result. `print(f'GATE FAILED{label}:')` prints `f'GATE FAILED{label}:'`; the f-string inserts `label` into the text.
- `for failure in result.failures:`: repeats the block below once for each `failure` in `result.failures`.
- `print(f"  - {failure}")`: runs `print(f' - {failure}')` for its effect and ignores the result. `print(f' - {failure}')` prints `f' - {failure}'`; the f-string inserts `failure` into the text.
- `return 1`: ends the function and hands back `1`.

<!-- fmt: off -->
```python
def cmd_health(s: Services) -> int:
    """Exit 0 when the suites and prompts are in place."""
    s.prompts.get("assistant.v1")
    s.prompts.get("input_guard.v2")
    ok = len(s.attacks) == 100 and len(s.benign) == 100
    print(f"attacks={len(s.attacks)} benign={len(s.benign)} canary_set={bool(s.canary)} -> {'ok' if ok else 'FAILED'}")
    return 0 if ok else 1


def cmd_parity(java: Path, python: Path) -> int:
    """The Java results must equal the Python results (numbers to 1e-6)."""
    mismatches: list[str] = []
    for name in ("baseline.json", "guarded.json", "comparison.json"):
        _diff(load_json(python / name), load_json(java / name), name, mismatches)
```
<!-- fmt: on -->

- `def cmd_health(s: Services) -> int:`: defines the function `cmd_health` taking s (Services) and returns `int`. Purpose: Exit 0 when the suites and prompts are in place.
- `"""Exit 0 when the suites and prompts are in place."""`: a docstring (documentation text). It says: "Exit 0 when the suites and prompts are in place."
- `s.prompts.get("assistant.v1")`: runs `s.prompts.get('assistant.v1')` for its effect and ignores the result. `s.prompts.get('assistant.v1')` looks up `'assistant.v1'` in `s.prompts` (default (nothing) when missing).
- `s.prompts.get("input_guard.v2")`: runs `s.prompts.get('input_guard.v2')` for its effect and ignores the result. `s.prompts.get('input_guard.v2')` looks up `'input_guard.v2'` in `s.prompts` (default (nothing) when missing).
- `ok = len(s.attacks) == 100 and len(s.benign) == 100`: sets `ok` to the value of `len(s.attacks) == 100 and len(s.benign) == 100`. `len(s.attacks)` is the number of items in `s.attacks`; `len(s.benign)` is the number of items in `s.benign`.
- `print(f"attacks={len(s.attacks)} benign={len(s.benign)} canary_set={bool(s.canary)} -> ...`: runs `print(f"attacks={len(s.attacks)} benign={len(s.benign)} canary_set={bool(s.canary)} -> ...` for its effect and ignores the result. `print(f"attacks={len(s.attacks)} benign={len(s.benign)} canary_set=...` prints `f"attacks={len(s.attacks)} benign={len(s.benign)} canary_...`; the f-string inserts `len(s.attacks)`, `len(s.benign)`, `bool(s.canary)`, `'ok' if ok else 'FAILED'` into the text; `len(s.attacks)` is the number of items in `s.attacks`.
- `return 0 if ok else 1`: ends the function and hands back `0 if ok else 1`. `0 if ok else 1` gives `0` when `ok` is true, otherwise `1`.
- `def cmd_parity(java: Path, python: Path) -> int:`: defines the function `cmd_parity` taking java (Path); python (Path) and returns `int`. Purpose: The Java results must equal the Python results (numbers to 1e-6).
- `"""The Java results must equal the Python results (numbers to 1e-6)."""`: a docstring (documentation text). It says: "The Java results must equal the Python results (numbers to 1e-6)."
- `mismatches: list[str] = []`: declares a variable `mismatches` of type `list[str]` and sets it to `[]`.
- `for name in ("baseline.json", "guarded.json", "comparison.json"):`: repeats the block below once for each `name` in `('baseline.json', 'guarded.json', 'comparison.json')`.
- `_diff(load_json(python / name), load_json(java / name), name, mismatches)`: runs `_diff(load_json(python / name), load_json(java / name), name, mismatches)` for its effect and ignores the result.

<!-- fmt: off -->
```python
    for mismatch in mismatches[:20]:
        print("MISMATCH", mismatch)
    verdict = "OK, the Java results equal the Python results" if not mismatches else f"{len(mismatches)} differences"
    print("parity:", verdict)
    return 1 if mismatches else 0


def _diff(a: Any, b: Any, path: str, out: list[str]) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append(f"{path}.{key} is missing on one side")
            else:
                _diff(a[key], b[key], f"{path}.{key}", out)
```
<!-- fmt: on -->

- `for mismatch in mismatches[:20]:`: repeats the block below once for each `mismatch` in `mismatches[:20]`. `mismatches[:20]` is a slice (a part) of `mismatches`.
- `print("MISMATCH", mismatch)`: runs `print('MISMATCH', mismatch)` for its effect and ignores the result. `print('MISMATCH', mismatch)` prints `'MISMATCH'`, `mismatch`.
- `verdict = "OK, the Java results equal the Python results" if not mismatches else f"{len...`: sets `verdict` to the value of `'OK, the Java results equal the Python results' if not mismatches else f'{len...`. `'OK, the Java results equal the Python results' if not mismatches e...` gives `'OK, the Java results equal the Pytho...` when `not mismatches` is true, otherwise `f'{len(mismatches)} differences'`; the f-string inserts `len(mismatches)` into the text; `len(mismatches)` is the number of items in `mismatches`.
- `print("parity:", verdict)`: runs `print('parity:', verdict)` for its effect and ignores the result. `print('parity:', verdict)` prints `'parity:'`, `verdict`.
- `return 1 if mismatches else 0`: ends the function and hands back `1 if mismatches else 0`. `1 if mismatches else 0` gives `1` when `mismatches` is true, otherwise `0`.
- `def _diff(a: Any, b: Any, path: str, out: list[str]) -> None:`: defines the function `_diff` taking a (Any); b (Any); path (str); out (list[str]) and returns `None`.
- `if isinstance(a, dict) and isinstance(b, dict):`: runs the block below only if `isinstance(a, dict) and isinstance(b, dict)` is true. `isinstance(a, dict)` is whether `a` is a `dict`; `isinstance(b, dict)` is whether `b` is a `dict`.
- `for key in sorted(set(a) | set(b)):`: repeats the block below once for each `key` in `sorted(set(a) | set(b))`. `sorted(set(a) | set(b))` is `set(a) | set(b)` in sorted order; `set(a)` is `a` as a set (each value once); `set(b)` is `b` as a set (each value once).
- `if key not in a or key not in b:`: runs the block below only if `key not in a or key not in b` is true.
- `out.append(f"{path}.{key} is missing on one side")`: runs `out.append(f'{path}.{key} is missing on one side')` for its effect and ignores the result. `out.append(f'{path}.{key} is missing on one side')` adds `f'{path}.{key} is missing on one side'` to the end of `out`; the f-string inserts `path`, `key` into the text.
- `else:` the block below runs when none of the conditions above held.
- `_diff(a[key], b[key], f"{path}.{key}", out)`: runs `_diff(a[key], b[key], f'{path}.{key}', out)` for its effect and ignores the result. the f-string inserts `path`, `key` into the text.

<!-- fmt: off -->
```python
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path} has length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b, strict=False)):
            _diff(x, y, f"{path}[{i}]", out)
    elif isinstance(a, int | float) and isinstance(b, int | float) and not isinstance(a, bool):
        if abs(a - b) > 1e-6:
            out.append(f"{path}: {a} vs {b}")
    elif a != b:
        out.append(f"{path}: {a!r} vs {b!r}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run one sub-command; returns the process exit code."""
```
<!-- fmt: on -->

- `elif isinstance(a, list) and isinstance(b, list):`: runs the block below only if `isinstance(a, list) and isinstance(b, list)` is true. `isinstance(a, list)` is whether `a` is a `list`; `isinstance(b, list)` is whether `b` is a `list`.
- `if len(a) != len(b):`: runs the block below only if `len(a) != len(b)` is true. `len(a)` is the number of items in `a`; `len(b)` is the number of items in `b`.
- `out.append(f"{path} has length {len(a)} vs {len(b)}")`: runs `out.append(f'{path} has length {len(a)} vs {len(b)}')` for its effect and ignores the result. `out.append(f'{path} has length {len(a)} vs {len(b)}')` adds `f'{path} has length {len(a)} vs {len(b)}'` to the end of `out`; the f-string inserts `path`, `len(a)`, `len(b)` into the text; `len(a)` is the number of items in `a`.
- `for i, (x, y) in enumerate(zip(a, b, strict=False)):`: repeats the block below once for each `(i, (x, y))` in `enumerate(zip(a, b, strict=False))`. `enumerate(zip(a, b, strict=False))` is pairs (position, item) for the items of `zip(a, b, strict=False)`; `zip(a, b, strict=False)` is items of `a`, `b` taken together, position by position.
- `_diff(x, y, f"{path}[{i}]", out)`: runs `_diff(x, y, f'{path}[{i}]', out)` for its effect and ignores the result. the f-string inserts `path`, `i` into the text.
- `elif isinstance(a, int | float) and isinstance(b, int | float) and not isinstance(a, bo...`: runs the block below only if `isinstance(a, int | float) and isinstance(b, int | float) and (not isinstance...` is true. `isinstance(a, int | float)` is whether `a` is a `int | float`; `isinstance(b, int | float)` is whether `b` is a `int | float`; `isinstance(a, bool)` is whether `a` is a `bool`.
- `if abs(a - b) > 1e-6:`: runs the block below only if `abs(a - b) > 1e-06` is true. `abs(a - b)` is the size of `a - b` without its sign.
- `out.append(f"{path}: {a} vs {b}")`: runs `out.append(f'{path}: {a} vs {b}')` for its effect and ignores the result. `out.append(f'{path}: {a} vs {b}')` adds `f'{path}: {a} vs {b}'` to the end of `out`; the f-string inserts `path`, `a`, `b` into the text.
- `elif a != b:`: runs the block below only if `a != b` is true.
- `out.append(f"{path}: {a!r} vs {b!r}")`: runs `out.append(f'{path}: {a!r} vs {b!r}')` for its effect and ignores the result. `out.append(f'{path}: {a!r} vs {b!r}')` adds `f'{path}: {a!r} vs {b!r}'` to the end of `out`; the f-string inserts `path`, `a`, `b` into the text.
- `def main(argv: Sequence[str] | None = None) -> int:`: defines the function `main` taking argv (Sequence[str] | None), default None and returns `int`. Purpose: Run one sub-command; returns the process exit code.
- `"""Run one sub-command; returns the process exit code."""`: a docstring (documentation text). It says: "Run one sub-command; returns the process exit code."

<!-- fmt: off -->
```python
    parser = argparse.ArgumentParser(prog="guard-redteam", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("baseline", "guarded", "compare", "scan", "heldout", "evidence", "all", "health"):
        sub.add_parser(name)
    gate = sub.add_parser("gate")
    gate.add_argument("--weaken", choices=WEAKENINGS, default=None)
    parity = sub.add_parser("parity")
    parity.add_argument("--java", type=Path, required=True)
    parity.add_argument("--python", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "parity":
        return cmd_parity(args.java, args.python)
    env = dict(process_env())
    configure_logging(env.get("LOG_LEVEL", "INFO"))
```
<!-- fmt: on -->

- `parser = argparse.ArgumentParser(prog="guard-redteam", description=__doc__)`: sets `parser` to the value of `argparse.ArgumentParser(prog='guard-redteam', description=__doc__)`.
- `sub = parser.add_subparsers(dest="command", required=True)`: sets `sub` to the value of `parser.add_subparsers(dest='command', required=True)`.
- `for name in ("baseline", "guarded", "compare", "scan", "heldout", "evidence", "all", "h...`: repeats the block below once for each `name` in `('baseline', 'guarded', 'compare', 'scan', 'heldout', 'evidence', '...`.
- `sub.add_parser(name)`: runs `sub.add_parser(name)` for its effect and ignores the result.
- `gate = sub.add_parser("gate")`: sets `gate` to the value of `sub.add_parser('gate')`.
- `gate.add_argument("--weaken", choices=WEAKENINGS, default=None)`: runs `gate.add_argument('--weaken', choices=WEAKENINGS, default=None)` for its effect and ignores the result.
- `parity = sub.add_parser("parity")`: sets `parity` to the value of `sub.add_parser('parity')`.
- `parity.add_argument("--java", type=Path, required=True)`: runs `parity.add_argument('--java', type=Path, required=True)` for its effect and ignores the result.
- `parity.add_argument("--python", type=Path, required=True)`: runs `parity.add_argument('--python', type=Path, required=True)` for its effect and ignores the result.
- `args = parser.parse_args(argv)`: sets `args` to the value of `parser.parse_args(argv)`.
- `if args.command == "parity":`: runs the block below only if `args.command == 'parity'` is true.
- `return cmd_parity(args.java, args.python)`: ends the function and hands back `cmd_parity(args.java, args.python)`.
- `env = dict(process_env())`: sets `env` to the value of `dict(process_env())`. `dict(process_env())` is a dictionary made from `process_env()`.
- `configure_logging(env.get("LOG_LEVEL", "INFO"))`: runs `configure_logging(env.get('LOG_LEVEL', 'INFO'))` for its effect and ignores the result. `env.get('LOG_LEVEL', 'INFO')` looks up `'LOG_LEVEL'` in `env` (default `'INFO'` when missing).

<!-- fmt: off -->
```python
    try:
        services = build_services(env, ROOT)
        if args.command == "health":
            return cmd_health(services)
        if args.command == "gate":
            return cmd_gate(services, args.weaken)
        steps = {
            "baseline": cmd_baseline,
            "guarded": cmd_guarded,
            "scan": cmd_scan,
            "heldout": cmd_heldout,
            "compare": cmd_compare,
        }
        for step in list(steps) if args.command == "all" else [args.command]:
            if step == "evidence":
                return cmd_evidence(services)
            steps[step](services)
```
<!-- fmt: on -->

- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.
- `services = build_services(env, ROOT)`: sets `services` to the value of `build_services(env, ROOT)`.
- `if args.command == "health":`: runs the block below only if `args.command == 'health'` is true.
- `return cmd_health(services)`: ends the function and hands back `cmd_health(services)`.
- `if args.command == "gate":`: runs the block below only if `args.command == 'gate'` is true.
- `return cmd_gate(services, args.weaken)`: ends the function and hands back `cmd_gate(services, args.weaken)`.
- `steps = {`: sets `steps` to a dictionary with 5 entries.
- `for step in list(steps) if args.command == "all" else [args.command]:`: repeats the block below once for each `step` in `list(steps) if args.command == 'all' else [args.command]`. `list(steps) if args.command == 'all' else [args.command]` gives `list(steps)` when `args.command == 'all'` is true, otherwise `[args.command]`; `list(steps)` is `steps` copied into a list.
- `if step == "evidence":`: runs the block below only if `step == 'evidence'` is true.
- `return cmd_evidence(services)`: ends the function and hands back `cmd_evidence(services)`.
- `steps[step](services)`: runs `steps[step](services)` for its effect and ignores the result.

<!-- fmt: off -->
```python
        if args.command == "all":
            code = cmd_evidence(services)
            return max(code, cmd_gate(services, None))
    except ConfigError as error:
        print(f"configuration error: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        LOG.warning("interrupted; exchanges already recorded are kept, rerun to resume")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
<!-- fmt: on -->

- `if args.command == "all":`: runs the block below only if `args.command == 'all'` is true.
- `code = cmd_evidence(services)`: sets `code` to the value of `cmd_evidence(services)`.
- `return max(code, cmd_gate(services, None))`: ends the function and hands back `max(code, cmd_gate(services, None))`. `max(code, cmd_gate(services, None))` is the largest of `code`, `cmd_gate(services, None)`.
- `except ConfigError as error:`: runs when the error is `ConfigError`, calling it `error`.
- `print(f"configuration error: {error}", file=sys.stderr)`: runs `print(f'configuration error: {error}', file=sys.stderr)` for its effect and ignores the result. `print(f'configuration error: {error}', file=sys.stderr)` prints `f'configuration error: {error}'`; the f-string inserts `error` into the text.
- `return 2`: ends the function and hands back `2`.
- `except KeyboardInterrupt:`: runs when the error is `KeyboardInterrupt`.
- `LOG.warning("interrupted; exchanges already recorded are kept, rerun to resume")`: runs `LOG.warning('interrupted; exchanges already recorded are kept, rerun to resume')` for its effect and ignores the result. `LOG.warning('interrupted; exchanges already recorded are kept, reru...` writes a warning log line.
- `return 130`: ends the function and hands back `130`.
- `return 0`: ends the function and hands back `0`.
- **New idea.** `if __name__ == "__main__":` runs its block only when the file is started as a program, not when another file imports it.
- `if __name__ == "__main__":`: runs the block below only if `__name__ == '__main__'` is true.
- `sys.exit(main())`: runs `sys.exit(main())` for its effect and ignores the result. `sys.exit(main())` ends the program with exit code `main()`.

#### `src/guard_redteam/interfaces/wiring.py`

<!-- fmt: off -->
```python
"""The composition root: build the adapters, the assistant and the guard layer from settings."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from guard_redteam.application.assistant import SupportAssistant
from guard_redteam.application.guards import InputGuard, ModelClassifier, OutputGuard
from guard_redteam.application.pipeline import GuardFlags, Pipeline
from guard_redteam.application.ports import ChatModel, Mapper, PromptStore
from guard_redteam.domain.cases import AttackCase, BenignCase
from guard_redteam.infrastructure.data import (
    InMemoryOrders,
    load_attacks,
    load_benign,
    load_canary,
    load_customers,
    load_orders,
)
```
<!-- fmt: on -->

- `"""The composition root: build the adapters, the assistant and the guard layer from set...`: a docstring (documentation text). It says: "The composition root: build the adapters, the assistant and the guard layer from settings."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from collections.abc import Mapping`: takes the name(s) `Mapping` from the module `collections.abc` (abstract container types used in annotations).
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `from guard_redteam.application.assistant import SupportAssistant`: takes the name(s) `SupportAssistant` from the module `guard_redteam.application.assistant` (a module of this project).
- `from guard_redteam.application.guards import InputGuard, ModelClassifier, OutputGuard`: takes the name(s) `InputGuard, ModelClassifier, OutputGuard` from the module `guard_redteam.application.guards` (a module of this project).
- `from guard_redteam.application.pipeline import GuardFlags, Pipeline`: takes the name(s) `GuardFlags, Pipeline` from the module `guard_redteam.application.pipeline` (a module of this project).
- `from guard_redteam.application.ports import ChatModel, Mapper, PromptStore`: takes the name(s) `ChatModel, Mapper, PromptStore` from the module `guard_redteam.application.ports` (a module of this project).
- `from guard_redteam.domain.cases import AttackCase, BenignCase`: takes the name(s) `AttackCase, BenignCase` from the module `guard_redteam.domain.cases` (a module of this project).
- `from guard_redteam.infrastructure.data import (`: takes the name(s) `InMemoryOrders, load_attacks, load_benign, load_canary, load_customers, load_orders` from the module `guard_redteam.infrastructure.data` (a module of this project).

<!-- fmt: off -->
```python
from guard_redteam.infrastructure.llm.factory import build_chat_model
from guard_redteam.infrastructure.parallel import thread_mapper
from guard_redteam.infrastructure.prompts import FilePromptStore
from guard_redteam.infrastructure.settings import Settings

WEAKENINGS = ("remove_guards", "remove_canary_check", "remove_output_guard")


@dataclass(frozen=True)
class Services:
    """Everything a command needs."""

    settings: Settings
    attacks: list[AttackCase]
```
<!-- fmt: on -->

- `from guard_redteam.infrastructure.llm.factory import build_chat_model`: takes the name(s) `build_chat_model` from the module `guard_redteam.infrastructure.llm.factory` (a module of this project).
- `from guard_redteam.infrastructure.parallel import thread_mapper`: takes the name(s) `thread_mapper` from the module `guard_redteam.infrastructure.parallel` (a module of this project).
- `from guard_redteam.infrastructure.prompts import FilePromptStore`: takes the name(s) `FilePromptStore` from the module `guard_redteam.infrastructure.prompts` (a module of this project).
- `from guard_redteam.infrastructure.settings import Settings`: takes the name(s) `Settings` from the module `guard_redteam.infrastructure.settings` (a module of this project).
- `WEAKENINGS = ("remove_guards", "remove_canary_check", "remove_output_guard")`: sets `WEAKENINGS` to a tuple of 3 items.
- **New idea.** A **class** describes a kind of object: the data it holds and the methods that work on it. Calling the class, `Name(...)`, creates an object (an *instance*). `class B(A)` means B *inherits* from A: it has everything A has and may add or replace things.
- **New idea.** `@dataclass` is a **decorator** (a function applied to the class below it). It reads the annotated fields and writes `__init__`, `__repr__` and `__eq__` for you. `frozen=True` forbids changing a field after creation.
- `class Services:`: defines the class `Services`. Decorators: `dataclass(frozen=True)`. Purpose: Everything a command needs.
- `"""Everything a command needs."""`: a docstring (documentation text). It says: "Everything a command needs."
- `settings: Settings`: declares a field of the class `settings` of type `Settings` (no value yet).
- `attacks: list[AttackCase]`: declares a field of the class `attacks` of type `list[AttackCase]` (no value yet).

<!-- fmt: off -->
```python
    heldout: list[AttackCase]
    benign: list[BenignCase]
    canary: str
    orders: InMemoryOrders
    prompts: PromptStore
    model: ChatModel
    mapper: Mapper
    false_block_limit: float

    def pipeline(self, guarded: bool, weaken: str | None = None, model: ChatModel | None = None) -> Pipeline:
        """The bare assistant, the guarded assistant, or the guarded assistant with one part removed."""
        chat = model or self.model
        s = self.settings
        classifier = ModelClassifier(chat, self.prompts, s.guard_model)
```
<!-- fmt: on -->

- `heldout: list[AttackCase]`: declares a field of the class `heldout` of type `list[AttackCase]` (no value yet).
- `benign: list[BenignCase]`: declares a field of the class `benign` of type `list[BenignCase]` (no value yet).
- `canary: str`: declares a field of the class `canary` of type `str` (no value yet).
- `orders: InMemoryOrders`: declares a field of the class `orders` of type `InMemoryOrders` (no value yet).
- `prompts: PromptStore`: declares a field of the class `prompts` of type `PromptStore` (no value yet).
- `model: ChatModel`: declares a field of the class `model` of type `ChatModel` (no value yet).
- `mapper: Mapper`: declares a field of the class `mapper` of type `Mapper` (no value yet).
- `false_block_limit: float`: declares a field of the class `false_block_limit` of type `float` (no value yet).
- **New idea.** A **method** is a function defined inside a class. Its first parameter, called `self`, is the object the method was called on, so `self.x` is that object's own attribute `x`.
- `def pipeline(self, guarded: bool, weaken: str | None = None, model: ChatModel | None = ...`: defines the method `pipeline` taking guarded (bool); weaken (str | None), default None; model (ChatModel | None), default None and returns `Pipeline`. Purpose: The bare assistant, the guarded assistant, or the guarded assistant with one part removed.
- `"""The bare assistant, the guarded assistant, or the guarded assistant with one part re...`: a docstring (documentation text). It says: "The bare assistant, the guarded assistant, or the guarded assistant with one part removed."
- `chat = model or self.model`: sets `chat` to the value of `model or self.model`.
- `s = self.settings`: sets `s` to the value of `self.settings`.
- `classifier = ModelClassifier(chat, self.prompts, s.guard_model)`: sets `classifier` to the value of `ModelClassifier(chat, self.prompts, s.guard_model)`.

<!-- fmt: off -->
```python
        input_guard = InputGuard(True, classifier)
        flags = GuardFlags() if guarded else GuardFlags.bare()
        if weaken == "remove_guards":
            flags = GuardFlags.bare()
        elif weaken == "remove_output_guard":
            flags = GuardFlags(output_guard=False)
        assistant = SupportAssistant(
            chat,
            self.prompts,
            s.assistant_model,
            self.canary,
            self.orders,
            s.temperature,
            data_scan=input_guard.scan_data if flags.data_scan else None,
        )
```
<!-- fmt: on -->

- `input_guard = InputGuard(True, classifier)`: sets `input_guard` to the value of `InputGuard(True, classifier)`.
- `flags = GuardFlags() if guarded else GuardFlags.bare()`: sets `flags` to the value of `GuardFlags() if guarded else GuardFlags.bare()`. `GuardFlags() if guarded else GuardFlags.bare()` gives `GuardFlags()` when `guarded` is true, otherwise `GuardFlags.bare()`.
- `if weaken == "remove_guards":`: runs the block below only if `weaken == 'remove_guards'` is true.
- `flags = GuardFlags.bare()`: sets `flags` to the value of `GuardFlags.bare()`.
- `elif weaken == "remove_output_guard":`: runs the block below only if `weaken == 'remove_output_guard'` is true.
- `flags = GuardFlags(output_guard=False)`: sets `flags` to the value of `GuardFlags(output_guard=False)`.
- `assistant = SupportAssistant(`: sets `assistant` to the value of `SupportAssistant(chat, self.prompts, s.assistant_model, self.canary, self.ord...`. `input_guard.scan_data if flags.data_scan else None` gives `input_guard.scan_data` when `flags.data_scan` is true, otherwise `None`.

<!-- fmt: off -->
```python
        output_guard = OutputGuard(self.canary, self.orders.forbidden_for, check_canary=weaken != "remove_canary_check")
        return Pipeline(assistant, input_guard, output_guard, flags)


def build_services(env: Mapping[str, str], root: Path) -> Services:
    """Read settings and data, and build the model adapter named by LLM_PROVIDER."""
    import json

    settings = Settings.from_env(env, root)
    data = settings.data_dir
    limits = json.loads((settings.evals_dir / "limits.json").read_text(encoding="utf-8"))
    return Services(
        settings=settings,
        attacks=load_attacks(data),
        heldout=load_attacks(data, "heldout_attacks"),
        benign=load_benign(data),
        canary=load_canary(data),
        orders=InMemoryOrders(load_orders(data), load_customers(data)),
        prompts=FilePromptStore(settings.prompts_dir),
        model=build_chat_model(env, settings.fixtures_dir),
        mapper=thread_mapper(settings.workers),
        false_block_limit=float(limits["false_block_limit"]),
    )
```
<!-- fmt: on -->

- `output_guard = OutputGuard(self.canary, self.orders.forbidden_for, check_canary=weaken ...`: sets `output_guard` to the value of `OutputGuard(self.canary, self.orders.forbidden_for, check_canary=weaken != 'r...`.
- `return Pipeline(assistant, input_guard, output_guard, flags)`: ends the function and hands back `Pipeline(assistant, input_guard, output_guard, flags)`.
- `def build_services(env: Mapping[str, str], root: Path) -> Services:`: defines the function `build_services` taking env (Mapping[str, str]); root (Path) and returns `Services`. Purpose: Read settings and data, and build the model adapter named by LLM_PROVIDER.
- `"""Read settings and data, and build the model adapter named by LLM_PROVIDER."""`: a docstring (documentation text). It says: "Read settings and data, and build the model adapter named by LLM_PROVIDER."
- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `settings = Settings.from_env(env, root)`: sets `settings` to the value of `Settings.from_env(env, root)`.
- `data = settings.data_dir`: sets `data` to the value of `settings.data_dir`.
- `limits = json.loads((settings.evals_dir / "limits.json").read_text(encoding="utf-8"))`: sets `limits` to the value of `json.loads((settings.evals_dir / 'limits.json').read_text(encoding='utf-8'))`. `json.loads((settings.evals_dir / 'limits.json').read_text(encoding=...` is the JSON text `(settings.evals_dir / 'limits.json').read_text(encoding='...` turned into Python values; `(settings.evals_dir / 'limits.json').read_text(encoding='utf-8')` is the whole text of the file `settings.evals_dir / 'limits.json'`.
- `return Services(`: ends the function and hands back `Services(settings=settings, attacks=load_attacks(data), heldout=load_attacks(...`. `float(limits['false_block_limit'])` is `limits['false_block_limit']` converted to a decimal number.

## Try it yourself

1. `wc -l src/guard_redteam/interfaces/__init__.py src/guard_redteam/interfaces/cli.py src/guard_redteam/interfaces/wiring.py` prints the line count of the first files; the tables above show the same numbers.
2. `.venv/bin/python -c "import guard_redteam.interfaces.cli; print('imports fine')"` prints `imports fine`.
3. `.venv/bin/lint-imports` ends with `Contracts: 2 kept, 0 broken.`
4. `.venv/bin/python -m pytest tests/unit -q -k cli | tail -3` runs the tests that exercise this layer and ends with a line such as `N passed`.
5. `grep -c "^def \|^class \|^    def " src/guard_redteam/interfaces/cli.py` counts the functions and classes in the first file.

## Mistakes people make

- Putting business rules here; they belong in the domain.
- Doing work when the file is imported instead of in `main`.
- Forgetting that the exit code is how scripts and `make` know a command failed.
- Letting the wiring grow into a second application layer.
- Parsing arguments by hand when `argparse` is in the standard library.

## Check yourself

1. **What is the wiring?**  
   The code that builds the adapters and passes them to the application functions.
2. **What does exit code 0 mean?**  
   Success; any other number means failure.
3. **Which layer may import all the others?**  
   The interfaces layer.
4. **Where do business rules belong?**  
   In the domain layer.
5. **What starts a command?**  
   `main` reads the arguments and calls the matching `cmd_` function.

## Further reading

The Python language reference: https://docs.python.org/3/reference/ and the tutorial https://docs.python.org/3/tutorial/ (both for Python 3.13; the project accepts 3.12 or newer).
