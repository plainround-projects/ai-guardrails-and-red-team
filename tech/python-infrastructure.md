# Python code: the infrastructure layer, file by file

## What it is

The **infrastructure layer**: the adapters that touch the outside world. Files, environment variables, HTTP calls, processes, the clock, JSON on disk, databases and model servers are handled here.

## Why this repository uses it

Everything that can fail for reasons outside the program (a missing file, a slow server) is confined to this layer, with the failure turned into an error type the inner layers understand.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/guard_redteam/infrastructure/__init__.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/capture.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/clock.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/data.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/env.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/llm/__init__.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/llm/anthropic.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/llm/factory.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/llm/openai_compat.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/llm/recorded.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/llm/retry.py` | Quoted and explained in the walkthrough below. |
| `src/guard_redteam/infrastructure/logging_setup.py` | Quoted and explained in the walkthrough below. |
| `... 4 more files` | All files are listed in the first table of the walkthrough. |


## How it works underneath

Each class here implements a port from the application layer. Adapters translate: JSON files into domain records, a domain request into an HTTP call, an HTTP status into a retryable or permanent error. They read settings from the environment (`dotenv.md`) and use libraries such as `httpx` (`httpx.md`).

## Walkthrough of this repository's use

### Files in this note

| File | Lines | What it is |
| --- | --- | --- |
| `src/guard_redteam/infrastructure/__init__.py` | 1 | The infrastructure layer. |
| `src/guard_redteam/infrastructure/capture.py` | 44 | Capturing what leaves the process: every model request, and every log line, for the redaction scan. |
| `src/guard_redteam/infrastructure/clock.py` | 39 | Clocks: the real one, and a manual one for tests and simulations. |
| `src/guard_redteam/infrastructure/data.py` | 106 | Reading the sample shop and the two suites, and the read-only order lookup built on them. |
| `src/guard_redteam/infrastructure/env.py` | 53 | Validated reads from the process environment (twelve-factor configuration). |
| `src/guard_redteam/infrastructure/llm/__init__.py` | 1 | Chat-model adapters: recorded, OpenAI-compatible, Anthropic. |
| `src/guard_redteam/infrastructure/llm/anthropic.py` | 80 | An adapter for the Anthropic Messages API, over plain HTTP. |
| `src/guard_redteam/infrastructure/llm/factory.py` | 45 | Choose a chat-model adapter from the environment: recorded (the default, offline), a local OpenAI-compatible server, a hosted OpenAI-compatible provider, or Anthropic. |
| `src/guard_redteam/infrastructure/llm/openai_compat.py` | 87 | An adapter for any server that speaks the OpenAI chat-completions protocol (a local ollama or llama.cpp server, or a hosted provider). |
| `src/guard_redteam/infrastructure/llm/recorded.py` | 139 | The recorded adapter replays real responses from JSONL fixtures; the recording adapter writes them. |
| `src/guard_redteam/infrastructure/llm/retry.py` | 32 | Retry with exponential backoff and jitter, for adapters that call a network. |
| `src/guard_redteam/infrastructure/logging_setup.py` | 41 | Structured logging: one JSON object per line on standard error, never prompt or reply text at info level. |
| `src/guard_redteam/infrastructure/parallel.py` | 22 | Run independent jobs on a few threads, keeping the input order of the results. |
| `src/guard_redteam/infrastructure/prompts.py` | 19 | Prompt templates read from versioned files under prompts/. |
| `src/guard_redteam/infrastructure/reports.py` | 45 | Writing reports as JSON, JSONL and Markdown with stable key order and rounded floats. |
| `src/guard_redteam/infrastructure/settings.py` | 45 | Settings from the environment, validated once at start-up. |

Each file below is quoted exactly, in order, in pieces of about a dozen lines. Under each piece, a bullet list explains every statement in the order it appears. The first time an idea shows up in this note it is explained in a bullet that begins **New idea**.

#### `src/guard_redteam/infrastructure/__init__.py`

<!-- fmt: off -->
```python
"""The infrastructure layer."""
```
<!-- fmt: on -->

- **New idea.** A **docstring** is a text in triple quotes as the first statement of a module, class or function. Python keeps it as documentation and tools can show it.
- `"""The infrastructure layer."""`: a docstring (documentation text). It says: "The infrastructure layer."

#### `src/guard_redteam/infrastructure/capture.py`

<!-- fmt: off -->
```python
"""Capturing what leaves the process: every model request, and every log line, for the redaction scan."""

from __future__ import annotations

import logging
import threading

from guard_redteam.application.ports import ChatModel
from guard_redteam.domain.llm import ChatRequest, ChatResponse


class CapturingChatModel:
    """Wraps a model and keeps the text of every request it was asked to send."""
```
<!-- fmt: on -->

- `"""Capturing what leaves the process: every model request, and every log line, for the ...`: a docstring (documentation text). It says: "Capturing what leaves the process: every model request, and every log line, for the redaction scan."
- **New idea.** `from __future__ import annotations` turns on a newer behaviour: type annotations are stored as text instead of being evaluated when the file loads.
- **New idea.** An **import** makes the code of another module available. `import x` gives the whole module under the name `x`; `from x import y` gives just the name `y`.
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import logging`: imports the module(s) `logging` so this file can use them. `logging` is the standard logging system.
- `import threading`: imports the module(s) `threading` so this file can use them. `threading` is threads and locks.
- `from guard_redteam.application.ports import ChatModel`: takes the name(s) `ChatModel` from the module `guard_redteam.application.ports` (a module of this project).
- `from guard_redteam.domain.llm import ChatRequest, ChatResponse`: takes the name(s) `ChatRequest, ChatResponse` from the module `guard_redteam.domain.llm` (a module of this project).
- **New idea.** A **class** describes a kind of object: the data it holds and the methods that work on it. Calling the class, `Name(...)`, creates an object (an *instance*). `class B(A)` means B *inherits* from A: it has everything A has and may add or replace things.
- `class CapturingChatModel:`: defines the class `CapturingChatModel`. Purpose: Wraps a model and keeps the text of every request it was asked to send.
- `"""Wraps a model and keeps the text of every request it was asked to send."""`: a docstring (documentation text). It says: "Wraps a model and keeps the text of every request it was asked to send."

<!-- fmt: off -->
```python
    def __init__(self, inner: ChatModel) -> None:
        self._inner = inner
        self._lock = threading.Lock()
        self.requests: list[str] = []

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Record the request text, then forward."""
        text = "\n".join(m.content for m in request.messages)
        with self._lock:
            self.requests.append(text)
        return self._inner.complete(request, timeout_s)


class LogCapture(logging.Handler):
```
<!-- fmt: on -->

- **New idea.** A **function** is a named block of code. `def name(a, b):` defines it; the indented lines are its body. Calling `name(1, 2)` runs the body with `a = 1` and `b = 2`. `return` hands a value back. A parameter written `b=3` has a **default**: it may be left out when calling.
- **New idea.** A **method** is a function defined inside a class. Its first parameter, called `self`, is the object the method was called on, so `self.x` is that object's own attribute `x`.
- `def __init__(self, inner: ChatModel) -> None:`: defines the method `__init__` taking inner (ChatModel) and returns `None`.
- **New idea.** An **assignment** `name = value` makes the name point at the value. A name written in capital letters is, by convention, a constant: it is not meant to change.
- `self._inner = inner`: sets `self._inner` to the value of `inner`.
- `self._lock = threading.Lock()`: sets `self._lock` to the value of `threading.Lock()`. `threading.Lock()` is a lock.
- **New idea.** An **annotated assignment** `name: type = value` also says what kind of value the name should hold. The annotation is a hint for readers and for mypy (`mypy.md`); Python does not enforce it.
- `self.requests: list[str] = []`: declares a variable `self.requests` of type `list[str]` and sets it to `[]`.
- `def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:`: defines the method `complete` taking request (ChatRequest); timeout_s (float), default 60.0 and returns `ChatResponse`. Purpose: Record the request text, then forward.
- `"""Record the request text, then forward."""`: a docstring (documentation text). It says: "Record the request text, then forward."
- `text = "\n".join(m.content for m in request.messages)`: sets `text` to the value of `'\n'.join((m.content for m in request.messages))`. `'\n'.join((m.content for m in request.messages))` is the items of `(m.content for m in request.messages)` joined into one text with `'\n'` between them; `(m.content for m in request.messages)` builds a generator of values: for each `m` in `request.messages`.
- **New idea.** A **with** statement runs set-up code, then the block, then clean-up code even if the block fails. It is used for files, locks and pools: the file is closed, the lock released, when the block ends.
- `with self._lock:`: opens `self._lock` for the duration of the block below and cleans up afterwards.
- `self.requests.append(text)`: runs `self.requests.append(text)` for its effect and ignores the result. `self.requests.append(text)` adds `text` to the end of `self.requests`.
- **New idea.** `return value` ends the function and hands the value to the caller. A function that reaches its end without `return` gives back `None` (nothing).
- `return self._inner.complete(request, timeout_s)`: ends the function and hands back `self._inner.complete(request, timeout_s)`.
- `class LogCapture(logging.Handler):`: defines the class `LogCapture` that inherits from `logging.Handler`. Purpose: Collects the formatted log lines produced while it is installed.

<!-- fmt: off -->
```python
    """Collects the formatted log lines produced while it is installed."""

    def __init__(self) -> None:
        super().__init__()
        self.lines: list[str] = []
        self._guard = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        """Keep the message and every extra field as one string."""
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord("", 0, "", 0, "", None, None).__dict__
        }
```
<!-- fmt: on -->

- `"""Collects the formatted log lines produced while it is installed."""`: a docstring (documentation text). It says: "Collects the formatted log lines produced while it is installed."
- `def __init__(self) -> None:`: defines the method `__init__` taking no arguments and returns `None`.
- `super().__init__()`: runs `super().__init__()` for its effect and ignores the result. `super()` is the parent class.
- `self.lines: list[str] = []`: declares a variable `self.lines` of type `list[str]` and sets it to `[]`.
- `self._guard = threading.Lock()`: sets `self._guard` to the value of `threading.Lock()`. `threading.Lock()` is a lock.
- `def emit(self, record: logging.LogRecord) -> None:`: defines the method `emit` taking record (logging.LogRecord) and returns `None`. Purpose: Keep the message and every extra field as one string.
- `"""Keep the message and every extra field as one string."""`: a docstring (documentation text). It says: "Keep the message and every extra field as one string."
- `extras = {`: sets `extras` to the value of `{k: v for k, v in record.__dict__.items() if k not in logging.LogRecord('', 0...`. `{k: v for k, v in record.__dict__.items() if k not in logging.LogRe...` builds a dictionary: for each `(k, v)` in `record.__dict__.items()`, keeping only those for which `k not in logging.LogRecord('', 0, '', 0, '', No...` is true; `record.__dict__.items()` is the (key, value) pairs of `record.__dict__`.

<!-- fmt: off -->
```python
        with self._guard:
            self.lines.append(f"{record.getMessage()} {extras}")
```
<!-- fmt: on -->

- `with self._guard:`: opens `self._guard` for the duration of the block below and cleans up afterwards.
- `self.lines.append(f"{record.getMessage()} {extras}")`: runs `self.lines.append(f'{record.getMessage()} {extras}')` for its effect and ignores the result. `self.lines.append(f'{record.getMessage()} {extras}')` adds `f'{record.getMessage()} {extras}'` to the end of `self.lines`; the f-string inserts `record.getMessage()`, `extras` into the text.

#### `src/guard_redteam/infrastructure/clock.py`

<!-- fmt: off -->
```python
"""Clocks: the real one, and a manual one for tests and simulations."""

from __future__ import annotations

import time


class SystemClock:
    """Wall time and real sleeping."""

    def monotonic(self) -> float:
        """Seconds from the monotonic clock."""
        return time.monotonic()
```
<!-- fmt: on -->

- `"""Clocks: the real one, and a manual one for tests and simulations."""`: a docstring (documentation text). It says: "Clocks: the real one, and a manual one for tests and simulations."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import time`: imports the module(s) `time` so this file can use them. `time` is clocks and sleeping.
- `class SystemClock:`: defines the class `SystemClock`. Purpose: Wall time and real sleeping.
- `"""Wall time and real sleeping."""`: a docstring (documentation text). It says: "Wall time and real sleeping."
- `def monotonic(self) -> float:`: defines the method `monotonic` taking no arguments and returns `float`. Purpose: Seconds from the monotonic clock.
- `"""Seconds from the monotonic clock."""`: a docstring (documentation text). It says: "Seconds from the monotonic clock."
- `return time.monotonic()`: ends the function and hands back `time.monotonic()`. `time.monotonic()` is the monotonic clock in seconds.

<!-- fmt: off -->
```python
    def sleep(self, seconds: float) -> None:
        """Block for the given seconds."""
        if seconds > 0:
            time.sleep(seconds)


class ManualClock:
    """A clock that only moves when told to; `sleep` advances it instead of waiting."""

    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def monotonic(self) -> float:
        """The current manual time."""
```
<!-- fmt: on -->

- `def sleep(self, seconds: float) -> None:`: defines the method `sleep` taking seconds (float) and returns `None`. Purpose: Block for the given seconds.
- `"""Block for the given seconds."""`: a docstring (documentation text). It says: "Block for the given seconds."
- **New idea.** An **if** statement runs its indented block only when the condition is true. `elif` adds another condition to try; `else` runs when none held.
- `if seconds > 0:`: runs the block below only if `seconds > 0` is true.
- `time.sleep(seconds)`: runs `time.sleep(seconds)` for its effect and ignores the result. `time.sleep(seconds)` waits `seconds` seconds.
- `class ManualClock:`: defines the class `ManualClock`. Purpose: A clock that only moves when told to; `sleep` advances it instead of waiting.
- `"""A clock that only moves when told to; 'sleep' advances it instead of waiting."""`: a docstring (documentation text). It says: "A clock that only moves when told to; `sleep` advances it instead of waiting."
- `def __init__(self, start: float = 0.0) -> None:`: defines the method `__init__` taking start (float), default 0.0 and returns `None`.
- `self._now = start`: sets `self._now` to the value of `start`.
- `def monotonic(self) -> float:`: defines the method `monotonic` taking no arguments and returns `float`. Purpose: The current manual time.
- `"""The current manual time."""`: a docstring (documentation text). It says: "The current manual time."

<!-- fmt: off -->
```python
        return self._now

    def sleep(self, seconds: float) -> None:
        """Advance the manual time."""
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        """Move time forward."""
        if seconds < 0:
            raise ValueError("time cannot go backward")
        self._now += seconds
```
<!-- fmt: on -->

- `return self._now`: ends the function and hands back `self._now`.
- `def sleep(self, seconds: float) -> None:`: defines the method `sleep` taking seconds (float) and returns `None`. Purpose: Advance the manual time.
- `"""Advance the manual time."""`: a docstring (documentation text). It says: "Advance the manual time."
- `self.advance(seconds)`: runs `self.advance(seconds)` for its effect and ignores the result.
- `def advance(self, seconds: float) -> None:`: defines the method `advance` taking seconds (float) and returns `None`. Purpose: Move time forward.
- `"""Move time forward."""`: a docstring (documentation text). It says: "Move time forward."
- `if seconds < 0:`: runs the block below only if `seconds < 0` is true.
- **New idea.** `raise Error("message")` stops normal flow and signals an error. The nearest `except` that matches the type catches it; if none does, the program stops with the message. `raise ... from error` records the original error as the cause.
- `raise ValueError("time cannot go backward")`: signals an error, `ValueError('time cannot go backward')`; normal flow stops here and the nearest matching `except` takes over. `ValueError('time cannot go backward')` is a ValueError.
- **New idea.** An **augmented assignment** such as `x += 1` changes the value in place: it means `x = x + 1`.
- `self._now += seconds`: adds `seconds` to `self._now` and stores the result back.

#### `src/guard_redteam/infrastructure/data.py`

<!-- fmt: off -->
```python
"""Reading the sample shop and the two suites, and the read-only order lookup built on them."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from guard_redteam.domain.cases import AttackCase, BenignCase, Family
from guard_redteam.domain.shop import Customer, Order, render_record


def _rows(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
```
<!-- fmt: on -->

- `"""Reading the sample shop and the two suites, and the read-only order lookup built on ...`: a docstring (documentation text). It says: "Reading the sample shop and the two suites, and the read-only order lookup built on them."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).
- `from guard_redteam.domain.cases import AttackCase, BenignCase, Family`: takes the name(s) `AttackCase, BenignCase, Family` from the module `guard_redteam.domain.cases` (a module of this project).
- `from guard_redteam.domain.shop import Customer, Order, render_record`: takes the name(s) `Customer, Order, render_record` from the module `guard_redteam.domain.shop` (a module of this project).
- `def _rows(path: Path) -> list[dict[str, Any]]:`: defines the function `_rows` taking path (Path) and returns `list[dict[str, Any]]`.
- `with path.open(encoding="utf-8") as handle:`: opens `path.open(encoding='utf-8')` (named `handle`) for the duration of the block below and cleans up afterwards. `path.open(encoding='utf-8')` opens `path`.

<!-- fmt: off -->
```python
        return [json.loads(line) for line in handle if line.strip()]


def load_customers(data_dir: Path) -> list[Customer]:
    """The ten sample customers."""
    return [Customer(r["customer_id"], r["name"], r["email"], r["phone"]) for r in _rows(data_dir / "customers.jsonl")]


def load_orders(data_dir: Path) -> list[Order]:
    """The forty sample orders."""
    return [
        Order(
            r["order_id"],
            r["customer_id"],
            r["status"],
            tuple(r["items"]),
            r["total_cents"],
            r["ship_to"],
            r["tracking"],
            r["note"],
        )
        for r in _rows(data_dir / "orders.jsonl")
    ]
```
<!-- fmt: on -->

- `return [json.loads(line) for line in handle if line.strip()]`: ends the function and hands back `[json.loads(line) for line in handle if line.strip()]`. `[json.loads(line) for line in handle if line.strip()]` builds a list: for each `line` in `handle`, keeping only those for which `line.strip()` is true; `json.loads(line)` is the JSON text `line` turned into Python values; `line.strip()` is `line` without white space at both ends.
- `def load_customers(data_dir: Path) -> list[Customer]:`: defines the function `load_customers` taking data_dir (Path) and returns `list[Customer]`. Purpose: The ten sample customers.
- `"""The ten sample customers."""`: a docstring (documentation text). It says: "The ten sample customers."
- `return [Customer(r["customer_id"], r["name"], r["email"], r["phone"]) for r in _rows(da...`: ends the function and hands back `[Customer(r['customer_id'], r['name'], r['email'], r['phone']) for r in _rows...`. `[Customer(r['customer_id'], r['name'], r['email'], r['phone']) for ...` builds a list: for each `r` in `_rows(data_dir / 'customers.jsonl')`.
- `def load_orders(data_dir: Path) -> list[Order]:`: defines the function `load_orders` taking data_dir (Path) and returns `list[Order]`. Purpose: The forty sample orders.
- `"""The forty sample orders."""`: a docstring (documentation text). It says: "The forty sample orders."
- `return [`: ends the function and hands back `[Order(r['order_id'], r['customer_id'], r['status'], tuple(r['items']), r['to...`. `[Order(r['order_id'], r['customer_id'], r['status'], tuple(r['items...` builds a list: for each `r` in `_rows(data_dir / 'orders.jsonl')`; `tuple(r['items'])` is `r['items']` as a tuple.

<!-- fmt: off -->
```python
def load_attacks(data_dir: Path, name: str = "attacks") -> list[AttackCase]:
    """The 100 attacks, 20 in each family (or the 25 held-out ones, with name `heldout_attacks`)."""
    cases = []
    for r in _rows(data_dir / f"{name}.jsonl"):
        override = r.get("note_override") or {}
        cases.append(
            AttackCase(
                r["case_id"],
                Family(r["family"]),
                r["customer"],
                r["message"],
                override.get("order_id"),
                override.get("note"),
                r.get("help_page"),
                tuple(r.get("leak_values", ())),
            )
        )
```
<!-- fmt: on -->

- `def load_attacks(data_dir: Path, name: str = "attacks") -> list[AttackCase]:`: defines the function `load_attacks` taking data_dir (Path); name (str), default 'attacks' and returns `list[AttackCase]`. Purpose: The 100 attacks, 20 in each family (or the 25 held-out ones, with name `heldout_attacks`).
- `"""The 100 attacks, 20 in each family (or the 25 held-out ones, with name 'heldout_atta...`: a docstring (documentation text). It says: "The 100 attacks, 20 in each family (or the 25 held-out ones, with name `heldout_attacks`)."
- `cases = []`: sets `cases` to a list of 0 items.
- **New idea.** A **for loop** `for x in items:` runs its block once for each item, with `x` naming the current item. `break` leaves the loop early; `continue` skips to the next item.
- `for r in _rows(data_dir / f"{name}.jsonl"):`: repeats the block below once for each `r` in `_rows(data_dir / f'{name}.jsonl')`. the f-string inserts `name` into the text.
- `override = r.get("note_override") or {}`: sets `override` to the value of `r.get('note_override') or {}`. `r.get('note_override')` looks up `'note_override'` in `r` (default (nothing) when missing).
- `cases.append(`: runs `cases.append(AttackCase(r['case_id'], Family(r['family']), r['customer'], r['message'],...` for its effect and ignores the result. `cases.append(AttackCase(r['case_id'], Family(r['family']), r['custo...` adds `AttackCase(r['case_id'], Family(r['family']), r['customer...` to the end of `cases`; `override.get('order_id')` looks up `'order_id'` in `override` (default (nothing) when missing); `override.get('note')` looks up `'note'` in `override` (default (nothing) when missing).

<!-- fmt: off -->
```python
    return cases


def load_benign(data_dir: Path) -> list[BenignCase]:
    """The 100 benign questions, 20 of them risky-looking."""
    return [BenignCase(r["case_id"], r["customer"], r["message"], r["risky"]) for r in _rows(data_dir / "benign.jsonl")]


def load_canary(data_dir: Path) -> str:
    """The canary string planted in the system prompt."""
    return (data_dir / "canary.txt").read_text(encoding="utf-8").strip()


class InMemoryOrders:
```
<!-- fmt: on -->

- `return cases`: ends the function and hands back `cases`.
- `def load_benign(data_dir: Path) -> list[BenignCase]:`: defines the function `load_benign` taking data_dir (Path) and returns `list[BenignCase]`. Purpose: The 100 benign questions, 20 of them risky-looking.
- `"""The 100 benign questions, 20 of them risky-looking."""`: a docstring (documentation text). It says: "The 100 benign questions, 20 of them risky-looking."
- `return [BenignCase(r["case_id"], r["customer"], r["message"], r["risky"]) for r in _row...`: ends the function and hands back `[BenignCase(r['case_id'], r['customer'], r['message'], r['risky']) for r in _...`. `[BenignCase(r['case_id'], r['customer'], r['message'], r['risky']) ...` builds a list: for each `r` in `_rows(data_dir / 'benign.jsonl')`.
- `def load_canary(data_dir: Path) -> str:`: defines the function `load_canary` taking data_dir (Path) and returns `str`. Purpose: The canary string planted in the system prompt.
- `"""The canary string planted in the system prompt."""`: a docstring (documentation text). It says: "The canary string planted in the system prompt."
- `return (data_dir / "canary.txt").read_text(encoding="utf-8").strip()`: ends the function and hands back `(data_dir / 'canary.txt').read_text(encoding='utf-8').strip()`. `(data_dir / 'canary.txt').read_text(encoding='utf-8').strip()` is `(data_dir / 'canary.txt').read_text(e...` without white space at both ends; `(data_dir / 'canary.txt').read_text(encoding='utf-8')` is the whole text of the file `data_dir / 'canary.txt'`.
- `class InMemoryOrders:`: defines the class `InMemoryOrders`. Purpose: The `find_order` tool: read-only, and, like the tool in the lesson, not scoped to the signed-in customer.

<!-- fmt: off -->
```python
    """The `find_order` tool: read-only, and, like the tool in the lesson, not scoped to the signed-in customer."""

    def __init__(self, orders: list[Order], customers: list[Customer]) -> None:
        self._orders = {o.order_id: o for o in orders}
        self._customers = {c.customer_id: c for c in customers}

    def find(self, order_id: str, note: str | None = None) -> str | None:
        """The record of any order, or None."""
        order = self._orders.get(order_id)
        return None if order is None else render_record(order, self._customers[order.customer_id], note)

    def owner_of(self, order_id: str) -> str | None:
        """The customer who owns an order."""
        order = self._orders.get(order_id)
```
<!-- fmt: on -->

- `"""The 'find_order' tool: read-only, and, like the tool in the lesson, not scoped to th...`: a docstring (documentation text). It says: "The `find_order` tool: read-only, and, like the tool in the lesson, not scoped to the signed-in customer."
- `def __init__(self, orders: list[Order], customers: list[Customer]) -> None:`: defines the method `__init__` taking orders (list[Order]); customers (list[Customer]) and returns `None`.
- `self._orders = {o.order_id: o for o in orders}`: sets `self._orders` to the value of `{o.order_id: o for o in orders}`. `{o.order_id: o for o in orders}` builds a dictionary: for each `o` in `orders`.
- `self._customers = {c.customer_id: c for c in customers}`: sets `self._customers` to the value of `{c.customer_id: c for c in customers}`. `{c.customer_id: c for c in customers}` builds a dictionary: for each `c` in `customers`.
- `def find(self, order_id: str, note: str | None = None) -> str | None:`: defines the method `find` taking order_id (str); note (str | None), default None and returns `str | None`. Purpose: The record of any order, or None.
- `"""The record of any order, or None."""`: a docstring (documentation text). It says: "The record of any order, or None."
- `order = self._orders.get(order_id)`: sets `order` to the value of `self._orders.get(order_id)`. `self._orders.get(order_id)` looks up `order_id` in `self._orders` (default (nothing) when missing).
- `return None if order is None else render_record(order, self._customers[order.customer_i...`: ends the function and hands back `None if order is None else render_record(order, self._customers[order.custome...`. `None if order is None else render_record(order, self._customers[ord...` gives `None` when `order is None` is true, otherwise `render_record(order, self._customers[...`; `order is None` tests that there is nothing (`None`) in `order`.
- `def owner_of(self, order_id: str) -> str | None:`: defines the method `owner_of` taking order_id (str) and returns `str | None`. Purpose: The customer who owns an order.
- `"""The customer who owns an order."""`: a docstring (documentation text). It says: "The customer who owns an order."
- `order = self._orders.get(order_id)`: sets `order` to the value of `self._orders.get(order_id)`. `self._orders.get(order_id)` looks up `order_id` in `self._orders` (default (nothing) when missing).

<!-- fmt: off -->
```python
        return None if order is None else order.customer_id

    def forbidden_for(self, customer_id: str) -> set[str]:
        """Every identifier that belongs to someone else: their emails, phones, order ids and tracking numbers."""
        values: set[str] = set()
        for customer in self._customers.values():
            if customer.customer_id != customer_id:
                values.update({customer.email, customer.phone})
        for order in self._orders.values():
            if order.customer_id != customer_id:
                values.update({order.order_id, order.tracking})
        return values

    def own_values(self, customer_id: str) -> tuple[str, ...]:
```
<!-- fmt: on -->

- `return None if order is None else order.customer_id`: ends the function and hands back `None if order is None else order.customer_id`. `None if order is None else order.customer_id` gives `None` when `order is None` is true, otherwise `order.customer_id`; `order is None` tests that there is nothing (`None`) in `order`.
- `def forbidden_for(self, customer_id: str) -> set[str]:`: defines the method `forbidden_for` taking customer_id (str) and returns `set[str]`. Purpose: Every identifier that belongs to someone else: their emails, phones, order ids and tracking numbers.
- `"""Every identifier that belongs to someone else: their emails, phones, order ids and t...`: a docstring (documentation text). It says: "Every identifier that belongs to someone else: their emails, phones, order ids and tracking numbers."
- `values: set[str] = set()`: declares a variable `values` of type `set[str]` and sets it to `set()`. `set()` is (nothing) as a set (each value once).
- `for customer in self._customers.values():`: repeats the block below once for each `customer` in `self._customers.values()`. `self._customers.values()` is the values of `self._customers`.
- `if customer.customer_id != customer_id:`: runs the block below only if `customer.customer_id != customer_id` is true.
- `values.update({customer.email, customer.phone})`: runs `values.update({customer.email, customer.phone})` for its effect and ignores the result. `values.update({customer.email, customer.phone})` adds the entries of `{customer.email, customer.phone}` to `values`.
- `for order in self._orders.values():`: repeats the block below once for each `order` in `self._orders.values()`. `self._orders.values()` is the values of `self._orders`.
- `if order.customer_id != customer_id:`: runs the block below only if `order.customer_id != customer_id` is true.
- `values.update({order.order_id, order.tracking})`: runs `values.update({order.order_id, order.tracking})` for its effect and ignores the result. `values.update({order.order_id, order.tracking})` adds the entries of `{order.order_id, order.tracking}` to `values`.
- `return values`: ends the function and hands back `values`.
- `def own_values(self, customer_id: str) -> tuple[str, ...]:`: defines the method `own_values` taking customer_id (str) and returns `tuple[str, ...]`. Purpose: The signed-in customer's own email and phone.

<!-- fmt: off -->
```python
        """The signed-in customer's own email and phone."""
        customer = self._customers[customer_id]
        return (customer.email, customer.phone)


def load_rows(path: Path) -> list[dict[str, Any]]:
    """Any JSONL file as dictionaries; an absent file is an empty list."""
    return _rows(path) if path.exists() else []
```
<!-- fmt: on -->

- `"""The signed-in customer's own email and phone."""`: a docstring (documentation text). It says: "The signed-in customer's own email and phone."
- `customer = self._customers[customer_id]`: sets `customer` to the value of `self._customers[customer_id]`.
- `return (customer.email, customer.phone)`: ends the function and hands back `(customer.email, customer.phone)`.
- `def load_rows(path: Path) -> list[dict[str, Any]]:`: defines the function `load_rows` taking path (Path) and returns `list[dict[str, Any]]`. Purpose: Any JSONL file as dictionaries; an absent file is an empty list.
- `"""Any JSONL file as dictionaries; an absent file is an empty list."""`: a docstring (documentation text). It says: "Any JSONL file as dictionaries; an absent file is an empty list."
- `return _rows(path) if path.exists() else []`: ends the function and hands back `_rows(path) if path.exists() else []`. `_rows(path) if path.exists() else []` gives `_rows(path)` when `path.exists()` is true, otherwise `[]`; `path.exists()` is whether `path` exists.

#### `src/guard_redteam/infrastructure/env.py`

<!-- fmt: off -->
```python
"""Validated reads from the process environment (twelve-factor configuration)."""

from __future__ import annotations

import os
from collections.abc import Mapping


class ConfigError(ValueError):
    """An environment variable is missing or has an invalid value."""


def read_str(env: Mapping[str, str], name: str, default: str | None = None) -> str:
    """A non-empty string variable, or the default when it is unset."""
```
<!-- fmt: on -->

- `"""Validated reads from the process environment (twelve-factor configuration)."""`: a docstring (documentation text). It says: "Validated reads from the process environment (twelve-factor configuration)."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import os`: imports the module(s) `os` so this file can use them. `os` is operating-system services such as environment variables and paths.
- `from collections.abc import Mapping`: takes the name(s) `Mapping` from the module `collections.abc` (abstract container types used in annotations).
- `class ConfigError(ValueError):`: defines the class `ConfigError` that inherits from `ValueError`. Purpose: An environment variable is missing or has an invalid value.
- `"""An environment variable is missing or has an invalid value."""`: a docstring (documentation text). It says: "An environment variable is missing or has an invalid value."
- `def read_str(env: Mapping[str, str], name: str, default: str | None = None) -> str:`: defines the function `read_str` taking env (Mapping[str, str]); name (str); default (str | None), default None and returns `str`. Purpose: A non-empty string variable, or the default when it is unset.
- `"""A non-empty string variable, or the default when it is unset."""`: a docstring (documentation text). It says: "A non-empty string variable, or the default when it is unset."

<!-- fmt: off -->
```python
    value = env.get(name, "").strip()
    if value:
        return value
    if default is None:
        raise ConfigError(f"{name} is required")
    return default


def read_int(env: Mapping[str, str], name: str, default: int, minimum: int = 0) -> int:
    """An integer variable at or above a minimum."""
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
```
<!-- fmt: on -->

- `value = env.get(name, "").strip()`: sets `value` to the value of `env.get(name, '').strip()`. `env.get(name, '').strip()` is `env.get(name, '')` without white space at both ends; `env.get(name, '')` looks up `name` in `env` (default `''` when missing).
- `if value:`: runs the block below only if `value` is true.
- `return value`: ends the function and hands back `value`.
- `if default is None:`: runs the block below only if `default is None` is true. `default is None` tests that there is nothing (`None`) in `default`.
- `raise ConfigError(f"{name} is required")`: signals an error, `ConfigError(f'{name} is required')`; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `name` into the text.
- `return default`: ends the function and hands back `default`.
- `def read_int(env: Mapping[str, str], name: str, default: int, minimum: int = 0) -> int:`: defines the function `read_int` taking env (Mapping[str, str]); name (str); default (int); minimum (int), default 0 and returns `int`. Purpose: An integer variable at or above a minimum.
- `"""An integer variable at or above a minimum."""`: a docstring (documentation text). It says: "An integer variable at or above a minimum."
- `raw = env.get(name, "").strip()`: sets `raw` to the value of `env.get(name, '').strip()`. `env.get(name, '').strip()` is `env.get(name, '')` without white space at both ends; `env.get(name, '')` looks up `name` in `env` (default `''` when missing).
- `if not raw:`: runs the block below only if `not raw` is true.
- `return default`: ends the function and hands back `default`.
- **New idea.** **try/except** handles errors. The code in `try:` runs; if it raises an error of the type named in `except`, Python jumps to that block instead of stopping. `finally:` always runs, error or not. `else:` runs only when no error occurred.
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.

<!-- fmt: off -->
```python
        value = int(raw)
    except ValueError as error:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from error
    if value < minimum:
        raise ConfigError(f"{name} must be at least {minimum}, got {value}")
    return value


def read_float(env: Mapping[str, str], name: str, default: float, minimum: float = 0.0) -> float:
    """A float variable at or above a minimum."""
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
```
<!-- fmt: on -->

- `value = int(raw)`: sets `value` to the value of `int(raw)`. `int(raw)` is `raw` converted to a whole number.
- `except ValueError as error:`: runs when the error is `ValueError`, calling it `error`.
- `raise ConfigError(f"{name} must be an integer, got {raw!r}") from error`: signals an error, `ConfigError(f'{name} must be an integer, got {raw!r}')` with `error` recorded as the cause; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `name`, `raw` into the text.
- `if value < minimum:`: runs the block below only if `value < minimum` is true.
- `raise ConfigError(f"{name} must be at least {minimum}, got {value}")`: signals an error, `ConfigError(f'{name} must be at least {minimum}, got {value}')`; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `name`, `minimum`, `value` into the text.
- `return value`: ends the function and hands back `value`.
- `def read_float(env: Mapping[str, str], name: str, default: float, minimum: float = 0.0)...`: defines the function `read_float` taking env (Mapping[str, str]); name (str); default (float); minimum (float), default 0.0 and returns `float`. Purpose: A float variable at or above a minimum.
- `"""A float variable at or above a minimum."""`: a docstring (documentation text). It says: "A float variable at or above a minimum."
- `raw = env.get(name, "").strip()`: sets `raw` to the value of `env.get(name, '').strip()`. `env.get(name, '').strip()` is `env.get(name, '')` without white space at both ends; `env.get(name, '')` looks up `name` in `env` (default `''` when missing).
- `if not raw:`: runs the block below only if `not raw` is true.
- `return default`: ends the function and hands back `default`.
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.

<!-- fmt: off -->
```python
        value = float(raw)
    except ValueError as error:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from error
    if value < minimum:
        raise ConfigError(f"{name} must be at least {minimum}, got {value}")
    return value


def process_env() -> Mapping[str, str]:
    """The real environment (a function so that tests can pass a dict instead)."""
    return os.environ
```
<!-- fmt: on -->

- `value = float(raw)`: sets `value` to the value of `float(raw)`. `float(raw)` is `raw` converted to a decimal number.
- `except ValueError as error:`: runs when the error is `ValueError`, calling it `error`.
- `raise ConfigError(f"{name} must be a number, got {raw!r}") from error`: signals an error, `ConfigError(f'{name} must be a number, got {raw!r}')` with `error` recorded as the cause; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `name`, `raw` into the text.
- `if value < minimum:`: runs the block below only if `value < minimum` is true.
- `raise ConfigError(f"{name} must be at least {minimum}, got {value}")`: signals an error, `ConfigError(f'{name} must be at least {minimum}, got {value}')`; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `name`, `minimum`, `value` into the text.
- `return value`: ends the function and hands back `value`.
- `def process_env() -> Mapping[str, str]:`: defines the function `process_env` taking no arguments and returns `Mapping[str, str]`. Purpose: The real environment (a function so that tests can pass a dict instead).
- `"""The real environment (a function so that tests can pass a dict instead)."""`: a docstring (documentation text). It says: "The real environment (a function so that tests can pass a dict instead)."
- `return os.environ`: ends the function and hands back `os.environ`.

#### `src/guard_redteam/infrastructure/llm/__init__.py`

<!-- fmt: off -->
```python
"""Chat-model adapters: recorded, OpenAI-compatible, Anthropic."""
```
<!-- fmt: on -->

- `"""Chat-model adapters: recorded, OpenAI-compatible, Anthropic."""`: a docstring (documentation text). It says: "Chat-model adapters: recorded, OpenAI-compatible, Anthropic."

#### `src/guard_redteam/infrastructure/llm/anthropic.py`

<!-- fmt: off -->
```python
"""An adapter for the Anthropic Messages API, over plain HTTP. The key comes from the environment; this adapter
is exercised only by the opt-in live test (`make test-live`)."""

from __future__ import annotations

import time
from typing import Any

import httpx

from guard_redteam.application.ports import Clock
from guard_redteam.domain.llm import (
    ChatRequest,
    ChatResponse,
    PermanentModelError,
    RetryableModelError,
    Usage,
)
```
<!-- fmt: on -->

- `"""An adapter for the Anthropic Messages API, over plain HTTP. The key comes from the e...`: a docstring (documentation text). It says: "An adapter for the Anthropic Messages API, over plain HTTP."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import time`: imports the module(s) `time` so this file can use them. `time` is clocks and sleeping.
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).
- `import httpx`: imports the module(s) `httpx` so this file can use them. `httpx` is the HTTP client (`httpx.md`).
- `from guard_redteam.application.ports import Clock`: takes the name(s) `Clock` from the module `guard_redteam.application.ports` (a module of this project).
- `from guard_redteam.domain.llm import (`: takes the name(s) `ChatRequest, ChatResponse, PermanentModelError, RetryableModelError, Usage` from the module `guard_redteam.domain.llm` (a module of this project).

<!-- fmt: off -->
```python
from guard_redteam.infrastructure.clock import SystemClock
from guard_redteam.infrastructure.llm.openai_compat import raise_for_status
from guard_redteam.infrastructure.llm.retry import retry_call

API_VERSION = "2023-06-01"


class AnthropicChatModel:
    """Messages API calls with a timeout, retries and backoff."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.anthropic.com",
        client: httpx.Client | None = None,
        attempts: int = 3,
        clock: Clock | None = None,
    ) -> None:
```
<!-- fmt: on -->

- `from guard_redteam.infrastructure.clock import SystemClock`: takes the name(s) `SystemClock` from the module `guard_redteam.infrastructure.clock` (a module of this project).
- `from guard_redteam.infrastructure.llm.openai_compat import raise_for_status`: takes the name(s) `raise_for_status` from the module `guard_redteam.infrastructure.llm.openai_compat` (a module of this project).
- `from guard_redteam.infrastructure.llm.retry import retry_call`: takes the name(s) `retry_call` from the module `guard_redteam.infrastructure.llm.retry` (a module of this project).
- `API_VERSION = "2023-06-01"`: sets `API_VERSION` to the constant `'2023-06-01'`.
- `class AnthropicChatModel:`: defines the class `AnthropicChatModel`. Purpose: Messages API calls with a timeout, retries and backoff.
- `"""Messages API calls with a timeout, retries and backoff."""`: a docstring (documentation text). It says: "Messages API calls with a timeout, retries and backoff."
- **New idea.** A bare `*` in a parameter list makes every parameter after it **keyword-only**: callers must name them, for example `attempts=3`.
- `def __init__(`: defines the method `__init__` taking api_key (str); base_url (str, keyword only), default 'https://api.anth...; client (httpx.Client | None, keyword only), default None; attempts (int, keyword only), default 3; clock (Clock | None, keyword only), default None and returns `None`.

<!-- fmt: off -->
```python
        if not api_key:
            raise PermanentModelError("ANTHROPIC_API_KEY is not set")
        self._base_url = base_url.rstrip("/")
        self._headers = {"x-api-key": api_key, "anthropic-version": API_VERSION, "content-type": "application/json"}
        self._client = client or httpx.Client()
        self._attempts = attempts
        self._clock = clock or SystemClock()

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Send the request, retrying timeouts, 429 and 5xx."""
        return retry_call(lambda: self._once(request, timeout_s), attempts=self._attempts, clock=self._clock)

    def _once(self, request: ChatRequest, timeout_s: float) -> ChatResponse:
        body: dict[str, Any] = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages if m.role != "system"],
        }
```
<!-- fmt: on -->

- `if not api_key:`: runs the block below only if `not api_key` is true.
- `raise PermanentModelError("ANTHROPIC_API_KEY is not set")`: signals an error, `PermanentModelError('ANTHROPIC_API_KEY is not set')`; normal flow stops here and the nearest matching `except` takes over.
- `self._base_url = base_url.rstrip("/")`: sets `self._base_url` to the value of `base_url.rstrip('/')`. `base_url.rstrip('/')` is `base_url` without the given characters at the end.
- `self._headers = {"x-api-key": api_key, "anthropic-version": API_VERSION, "content-type"...`: sets `self._headers` to a dictionary with 3 entries.
- `self._client = client or httpx.Client()`: sets `self._client` to the value of `client or httpx.Client()`. `httpx.Client()` is a reusable HTTP client.
- `self._attempts = attempts`: sets `self._attempts` to the value of `attempts`.
- `self._clock = clock or SystemClock()`: sets `self._clock` to the value of `clock or SystemClock()`.
- `def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:`: defines the method `complete` taking request (ChatRequest); timeout_s (float), default 60.0 and returns `ChatResponse`. Purpose: Send the request, retrying timeouts, 429 and 5xx.
- `"""Send the request, retrying timeouts, 429 and 5xx."""`: a docstring (documentation text). It says: "Send the request, retrying timeouts, 429 and 5xx."
- `return retry_call(lambda: self._once(request, timeout_s), attempts=self._attempts, cloc...`: ends the function and hands back `retry_call(lambda: self._once(request, timeout_s), attempts=self._attempts, c...`. `lambda: self._once(request, timeout_s)` is a small unnamed function of no arguments that gives `self._once(request, timeout_s)`.
- `def _once(self, request: ChatRequest, timeout_s: float) -> ChatResponse:`: defines the method `_once` taking request (ChatRequest); timeout_s (float) and returns `ChatResponse`.
- `body: dict[str, Any] = {`: declares a variable `body` of type `dict[str, Any]` and sets it to `{'model': request.model, 'max_tokens': request.max_tokens, 'message...`. `[{'role': m.role, 'content': m.content} for m in request.messages i...` builds a list: for each `m` in `request.messages`, keeping only those for which `m.role != 'system'` is true.

<!-- fmt: off -->
```python
        system = request.system_text()
        if system:
            body["system"] = system
        started = time.perf_counter()
        try:
            response = self._client.post(
                f"{self._base_url}/v1/messages", json=body, headers=self._headers, timeout=timeout_s
            )
        except (httpx.TimeoutException, httpx.TransportError) as error:
            raise RetryableModelError(f"transport failure: {type(error).__name__}") from error
        raise_for_status(response)
        elapsed = time.perf_counter() - started
        try:
            data = response.json()
            text = "".join(block["text"] for block in data["content"] if block.get("type") == "text")
            usage = data["usage"]
            return ChatResponse(
                text=text,
                usage=Usage(int(usage["input_tokens"]), int(usage["output_tokens"])),
                model=str(data.get("model", request.model)),
                finish_reason=str(data.get("stop_reason") or "stop"),
                latency_s=elapsed,
            )
```
<!-- fmt: on -->

- `system = request.system_text()`: sets `system` to the value of `request.system_text()`.
- `if system:`: runs the block below only if `system` is true.
- `body["system"] = system`: sets `body['system']` to the value of `system`.
- `started = time.perf_counter()`: sets `started` to the value of `time.perf_counter()`. `time.perf_counter()` is a precise stopwatch reading.
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.
- `response = self._client.post(`: sets `response` to the value of `self._client.post(f'{self._base_url}/v1/messages', json=body, headers=self._h...`. the f-string inserts `self._base_url` into the text.
- `except (httpx.TimeoutException, httpx.TransportError) as error:`: runs when the error is `(httpx.TimeoutException, httpx.TransportError)`, calling it `error`.
- `raise RetryableModelError(f"transport failure: {type(error).__name__}") from error`: signals an error, `RetryableModelError(f'transport failure: {type(error).__name__}')` with `error` recorded as the cause; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `type(error).__name__` into the text; `type(error)` is the type of `error`.
- `raise_for_status(response)`: runs `raise_for_status(response)` for its effect and ignores the result.
- `elapsed = time.perf_counter() - started`: sets `elapsed` to the value of `time.perf_counter() - started`. `time.perf_counter()` is a precise stopwatch reading.
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.
- `data = response.json()`: sets `data` to the value of `response.json()`.
- `text = "".join(block["text"] for block in data["content"] if block.get("type") == "text")`: sets `text` to the value of `''.join((block['text'] for block in data['content'] if block.get('type') == '...`. `''.join((block['text'] for block in data['content'] if block.get('t...` is the items of `(block['text'] for block in data['content'] if block.get(...` joined into one text with `''` between them; `(block['text'] for block in data['content'] if block.get('type') ==...` builds a generator of values: for each `block` in `data['content']`, keeping only those for which `block.get('type') == 'text'` is true; `block.get('type')` looks up `'type'` in `block` (default (nothing) when missing).
- `usage = data["usage"]`: sets `usage` to the value of `data['usage']`.
- `return ChatResponse(`: ends the function and hands back `ChatResponse(text=text, usage=Usage(int(usage['input_tokens']), int(usage['ou...`. `str(data.get('model', request.model))` is `data.get('model', request.model)` converted to text; `str(data.get('stop_reason') or 'stop')` is `data.get('stop_reason') or 'stop'` converted to text; `int(usage['input_tokens'])` is `usage['input_tokens']` converted to a whole number.

<!-- fmt: off -->
```python
        except (KeyError, ValueError, TypeError) as error:
            raise PermanentModelError("the provider's reply did not have the expected shape") from error
```
<!-- fmt: on -->

- `except (KeyError, ValueError, TypeError) as error:`: runs when the error is `(KeyError, ValueError, TypeError)`, calling it `error`.
- `raise PermanentModelError("the provider's reply did not have the expected shape") from ...`: signals an error, `PermanentModelError("the provider's reply did not have the expected shape")` with `error` recorded as the cause; normal flow stops here and the nearest matching `except` takes over.

#### `src/guard_redteam/infrastructure/llm/factory.py`

<!-- fmt: off -->
```python
"""Choose a chat-model adapter from the environment: recorded (the default, offline), a local OpenAI-compatible
server, a hosted OpenAI-compatible provider, or Anthropic."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from guard_redteam.application.ports import ChatModel
from guard_redteam.infrastructure.env import ConfigError, read_int, read_str
from guard_redteam.infrastructure.llm.anthropic import AnthropicChatModel
from guard_redteam.infrastructure.llm.openai_compat import OpenAICompatibleChatModel
from guard_redteam.infrastructure.llm.recorded import RecordedChatModel, RecordingChatModel
```
<!-- fmt: on -->

- `"""Choose a chat-model adapter from the environment: recorded (the default, offline), a...`: a docstring (documentation text). It says: "Choose a chat-model adapter from the environment: recorded (the default, offline), a local OpenAI-compatible server, a hosted OpenAI-compatible provider, or Anthropic."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from collections.abc import Mapping`: takes the name(s) `Mapping` from the module `collections.abc` (abstract container types used in annotations).
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `from guard_redteam.application.ports import ChatModel`: takes the name(s) `ChatModel` from the module `guard_redteam.application.ports` (a module of this project).
- `from guard_redteam.infrastructure.env import ConfigError, read_int, read_str`: takes the name(s) `ConfigError, read_int, read_str` from the module `guard_redteam.infrastructure.env` (a module of this project).
- `from guard_redteam.infrastructure.llm.anthropic import AnthropicChatModel`: takes the name(s) `AnthropicChatModel` from the module `guard_redteam.infrastructure.llm.anthropic` (a module of this project).
- `from guard_redteam.infrastructure.llm.openai_compat import OpenAICompatibleChatModel`: takes the name(s) `OpenAICompatibleChatModel` from the module `guard_redteam.infrastructure.llm.openai_compat` (a module of this project).
- `from guard_redteam.infrastructure.llm.recorded import RecordedChatModel, RecordingChatM...`: takes the name(s) `RecordedChatModel, RecordingChatModel` from the module `guard_redteam.infrastructure.llm.recorded` (a module of this project).

<!-- fmt: off -->
```python
PROVIDERS = ("recorded", "local", "openai", "anthropic")
LOCAL_BASE_URL = "http://localhost:11434/v1"


def build_chat_model(env: Mapping[str, str], fixtures: Path) -> ChatModel:
    """Build the adapter named by LLM_PROVIDER.

    - recorded (default): replay `fixtures`; needs no network and no key.
    - local: an OpenAI-compatible server on this machine (ollama, llama.cpp); LLM_BASE_URL overrides the address.
    - openai: a hosted OpenAI-compatible provider; LLM_BASE_URL and OPENAI_API_KEY come from the environment.
    - anthropic: the Messages API; ANTHROPIC_API_KEY comes from the environment.

    When LLM_RECORD_TO is set, every real exchange is also appended to that fixture file.
    """
```
<!-- fmt: on -->

- `PROVIDERS = ("recorded", "local", "openai", "anthropic")`: sets `PROVIDERS` to a tuple of 4 items.
- `LOCAL_BASE_URL = "http://localhost:11434/v1"`: sets `LOCAL_BASE_URL` to the constant `'http://localhost:11434/v1'`.
- `def build_chat_model(env: Mapping[str, str], fixtures: Path) -> ChatModel:`: defines the function `build_chat_model` taking env (Mapping[str, str]); fixtures (Path) and returns `ChatModel`. Purpose: Build the adapter named by LLM_PROVIDER.
- `"""Build the adapter named by LLM_PROVIDER.`: a docstring (documentation text). It says: "Build the adapter named by LLM_PROVIDER."

<!-- fmt: off -->
```python
    provider = read_str(env, "LLM_PROVIDER", "recorded")
    if provider not in PROVIDERS:
        raise ConfigError(f"LLM_PROVIDER must be one of {', '.join(PROVIDERS)}, got {provider!r}")
    attempts = read_int(env, "LLM_ATTEMPTS", 3, minimum=1)
    model: ChatModel
    if provider == "recorded":
        return RecordedChatModel(fixtures)
    if provider == "local":
        model = OpenAICompatibleChatModel(read_str(env, "LLM_BASE_URL", LOCAL_BASE_URL), attempts=attempts)
    elif provider == "openai":
        model = OpenAICompatibleChatModel(
            read_str(env, "LLM_BASE_URL"), read_str(env, "OPENAI_API_KEY"), attempts=attempts
        )
    else:
```
<!-- fmt: on -->

- `provider = read_str(env, "LLM_PROVIDER", "recorded")`: sets `provider` to the value of `read_str(env, 'LLM_PROVIDER', 'recorded')`.
- `if provider not in PROVIDERS:`: runs the block below only if `provider not in PROVIDERS` is true.
- `raise ConfigError(f"LLM_PROVIDER must be one of {', '.join(PROVIDERS)}, got {provider!r}")`: signals an error, `ConfigError(f"LLM_PROVIDER must be one of {', '.join(PROVIDERS)}, got {provid...`; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `', '.join(PROVIDERS)`, `provider` into the text; `', '.join(PROVIDERS)` is the items of `PROVIDERS` joined into one text with `', '` between them.
- `attempts = read_int(env, "LLM_ATTEMPTS", 3, minimum=1)`: sets `attempts` to the value of `read_int(env, 'LLM_ATTEMPTS', 3, minimum=1)`.
- `model: ChatModel`: declares a variable `model` of type `ChatModel` (no value yet).
- `if provider == "recorded":`: runs the block below only if `provider == 'recorded'` is true.
- `return RecordedChatModel(fixtures)`: ends the function and hands back `RecordedChatModel(fixtures)`.
- `if provider == "local":`: runs the block below only if `provider == 'local'` is true.
- `model = OpenAICompatibleChatModel(read_str(env, "LLM_BASE_URL", LOCAL_BASE_URL), attemp...`: sets `model` to the value of `OpenAICompatibleChatModel(read_str(env, 'LLM_BASE_URL', LOCAL_BASE_URL), atte...`.
- `elif provider == "openai":`: runs the block below only if `provider == 'openai'` is true.
- `model = OpenAICompatibleChatModel(`: sets `model` to the value of `OpenAICompatibleChatModel(read_str(env, 'LLM_BASE_URL'), read_str(env, 'OPENA...`.
- `else:` the block below runs when none of the conditions above held.

<!-- fmt: off -->
```python
        model = AnthropicChatModel(read_str(env, "ANTHROPIC_API_KEY"), attempts=attempts)
    record_to = env.get("LLM_RECORD_TO", "").strip()
    return RecordingChatModel(model, Path(record_to)) if record_to else model
```
<!-- fmt: on -->

- `model = AnthropicChatModel(read_str(env, "ANTHROPIC_API_KEY"), attempts=attempts)`: sets `model` to the value of `AnthropicChatModel(read_str(env, 'ANTHROPIC_API_KEY'), attempts=attempts)`.
- `record_to = env.get("LLM_RECORD_TO", "").strip()`: sets `record_to` to the value of `env.get('LLM_RECORD_TO', '').strip()`. `env.get('LLM_RECORD_TO', '').strip()` is `env.get('LLM_RECORD_TO', '')` without white space at both ends; `env.get('LLM_RECORD_TO', '')` looks up `'LLM_RECORD_TO'` in `env` (default `''` when missing).
- `return RecordingChatModel(model, Path(record_to)) if record_to else model`: ends the function and hands back `RecordingChatModel(model, Path(record_to)) if record_to else model`. `RecordingChatModel(model, Path(record_to)) if record_to else model` gives `RecordingChatModel(model, Path(record...` when `record_to` is true, otherwise `model`; `Path(record_to)` is the file path `record_to`.

#### `src/guard_redteam/infrastructure/llm/openai_compat.py`

<!-- fmt: off -->
```python
"""An adapter for any server that speaks the OpenAI chat-completions protocol (a local ollama or llama.cpp
server, or a hosted provider). The key, when there is one, comes from the environment."""

from __future__ import annotations

import time
from typing import Any

import httpx

from guard_redteam.application.ports import Clock
from guard_redteam.domain.llm import (
    ChatRequest,
    ChatResponse,
    PermanentModelError,
    RetryableModelError,
    Usage,
)
```
<!-- fmt: on -->

- `"""An adapter for any server that speaks the OpenAI chat-completions protocol (a local ...`: a docstring (documentation text). It says: "An adapter for any server that speaks the OpenAI chat-completions protocol (a local ollama or llama.cpp server, or a hosted provider)."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import time`: imports the module(s) `time` so this file can use them. `time` is clocks and sleeping.
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).
- `import httpx`: imports the module(s) `httpx` so this file can use them. `httpx` is the HTTP client (`httpx.md`).
- `from guard_redteam.application.ports import Clock`: takes the name(s) `Clock` from the module `guard_redteam.application.ports` (a module of this project).
- `from guard_redteam.domain.llm import (`: takes the name(s) `ChatRequest, ChatResponse, PermanentModelError, RetryableModelError, Usage` from the module `guard_redteam.domain.llm` (a module of this project).

<!-- fmt: off -->
```python
from guard_redteam.infrastructure.clock import SystemClock
from guard_redteam.infrastructure.llm.retry import retry_call


def raise_for_status(response: httpx.Response) -> None:
    """Map an HTTP status to the retryable or permanent error the application understands."""
    status = response.status_code
    if status < 400:
        return
    detail = response.text[:200]
    if status == 429 or status >= 500:
        raise RetryableModelError(f"provider returned {status}: {detail}")
    raise PermanentModelError(f"provider returned {status}: {detail}")
```
<!-- fmt: on -->

- `from guard_redteam.infrastructure.clock import SystemClock`: takes the name(s) `SystemClock` from the module `guard_redteam.infrastructure.clock` (a module of this project).
- `from guard_redteam.infrastructure.llm.retry import retry_call`: takes the name(s) `retry_call` from the module `guard_redteam.infrastructure.llm.retry` (a module of this project).
- `def raise_for_status(response: httpx.Response) -> None:`: defines the function `raise_for_status` taking response (httpx.Response) and returns `None`. Purpose: Map an HTTP status to the retryable or permanent error the application understands.
- `"""Map an HTTP status to the retryable or permanent error the application understands."""`: a docstring (documentation text). It says: "Map an HTTP status to the retryable or permanent error the application understands."
- `status = response.status_code`: sets `status` to the value of `response.status_code`.
- `if status < 400:`: runs the block below only if `status < 400` is true.
- `return`: ends the function and returns nothing (`None`).
- `detail = response.text[:200]`: sets `detail` to the value of `response.text[:200]`. `response.text[:200]` is a slice (a part) of `response.text`.
- `if status == 429 or status >= 500:`: runs the block below only if `status == 429 or status >= 500` is true.
- `raise RetryableModelError(f"provider returned {status}: {detail}")`: signals an error, `RetryableModelError(f'provider returned {status}: {detail}')`; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `status`, `detail` into the text.
- `raise PermanentModelError(f"provider returned {status}: {detail}")`: signals an error, `PermanentModelError(f'provider returned {status}: {detail}')`; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `status`, `detail` into the text.

<!-- fmt: off -->
```python
class OpenAICompatibleChatModel:
    """Chat completions over HTTP with a timeout, retries and backoff."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        client: httpx.Client | None = None,
        attempts: int = 3,
        clock: Clock | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
```
<!-- fmt: on -->

- `class OpenAICompatibleChatModel:`: defines the class `OpenAICompatibleChatModel`. Purpose: Chat completions over HTTP with a timeout, retries and backoff.
- `"""Chat completions over HTTP with a timeout, retries and backoff."""`: a docstring (documentation text). It says: "Chat completions over HTTP with a timeout, retries and backoff."
- `def __init__(`: defines the method `__init__` taking base_url (str); api_key (str | None), default None; client (httpx.Client | None, keyword only), default None; attempts (int, keyword only), default 3; clock (Clock | None, keyword only), default None and returns `None`.
- `self._base_url = base_url.rstrip("/")`: sets `self._base_url` to the value of `base_url.rstrip('/')`. `base_url.rstrip('/')` is `base_url` without the given characters at the end.
- `self._headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}`: sets `self._headers` to the value of `{'Authorization': f'Bearer {api_key}'} if api_key else {}`. `{'Authorization': f'Bearer {api_key}'} if api_key else {}` gives `{'Authorization': f'Bearer {api_key}'}` when `api_key` is true, otherwise `{}`; the f-string inserts `api_key` into the text.

<!-- fmt: off -->
```python
        self._client = client or httpx.Client()
        self._attempts = attempts
        self._clock = clock or SystemClock()

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Send the request, retrying timeouts, 429 and 5xx."""
        return retry_call(lambda: self._once(request, timeout_s), attempts=self._attempts, clock=self._clock)

    def _once(self, request: ChatRequest, timeout_s: float) -> ChatResponse:
        body: dict[str, Any] = {
            "model": request.model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": False,
        }
```
<!-- fmt: on -->

- `self._client = client or httpx.Client()`: sets `self._client` to the value of `client or httpx.Client()`. `httpx.Client()` is a reusable HTTP client.
- `self._attempts = attempts`: sets `self._attempts` to the value of `attempts`.
- `self._clock = clock or SystemClock()`: sets `self._clock` to the value of `clock or SystemClock()`.
- `def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:`: defines the method `complete` taking request (ChatRequest); timeout_s (float), default 60.0 and returns `ChatResponse`. Purpose: Send the request, retrying timeouts, 429 and 5xx.
- `"""Send the request, retrying timeouts, 429 and 5xx."""`: a docstring (documentation text). It says: "Send the request, retrying timeouts, 429 and 5xx."
- `return retry_call(lambda: self._once(request, timeout_s), attempts=self._attempts, cloc...`: ends the function and hands back `retry_call(lambda: self._once(request, timeout_s), attempts=self._attempts, c...`. `lambda: self._once(request, timeout_s)` is a small unnamed function of no arguments that gives `self._once(request, timeout_s)`.
- `def _once(self, request: ChatRequest, timeout_s: float) -> ChatResponse:`: defines the method `_once` taking request (ChatRequest); timeout_s (float) and returns `ChatResponse`.
- `body: dict[str, Any] = {`: declares a variable `body` of type `dict[str, Any]` and sets it to `{'model': request.model, 'messages': [{'role': m.role, 'content': m...`. `[{'role': m.role, 'content': m.content} for m in request.messages]` builds a list: for each `m` in `request.messages`.

<!-- fmt: off -->
```python
        if request.seed is not None:
            body["seed"] = request.seed
        started = time.perf_counter()
        try:
            response = self._client.post(
                f"{self._base_url}/chat/completions", json=body, headers=self._headers, timeout=timeout_s
            )
        except (httpx.TimeoutException, httpx.TransportError) as error:
            raise RetryableModelError(f"transport failure: {type(error).__name__}") from error
        raise_for_status(response)
        elapsed = time.perf_counter() - started
        try:
            data = response.json()
            choice = data["choices"][0]
            usage = data.get("usage") or {}
            return ChatResponse(
                text=choice["message"]["content"] or "",
                usage=Usage(int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))),
                model=str(data.get("model", request.model)),
                finish_reason=str(choice.get("finish_reason") or "stop"),
                latency_s=elapsed,
            )
```
<!-- fmt: on -->

- `if request.seed is not None:`: runs the block below only if `request.seed is not None` is true. `request.seed is not None` tests that there is something in `request.seed`.
- `body["seed"] = request.seed`: sets `body['seed']` to the value of `request.seed`.
- `started = time.perf_counter()`: sets `started` to the value of `time.perf_counter()`. `time.perf_counter()` is a precise stopwatch reading.
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.
- `response = self._client.post(`: sets `response` to the value of `self._client.post(f'{self._base_url}/chat/completions', json=body, headers=se...`. the f-string inserts `self._base_url` into the text.
- `except (httpx.TimeoutException, httpx.TransportError) as error:`: runs when the error is `(httpx.TimeoutException, httpx.TransportError)`, calling it `error`.
- `raise RetryableModelError(f"transport failure: {type(error).__name__}") from error`: signals an error, `RetryableModelError(f'transport failure: {type(error).__name__}')` with `error` recorded as the cause; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `type(error).__name__` into the text; `type(error)` is the type of `error`.
- `raise_for_status(response)`: runs `raise_for_status(response)` for its effect and ignores the result.
- `elapsed = time.perf_counter() - started`: sets `elapsed` to the value of `time.perf_counter() - started`. `time.perf_counter()` is a precise stopwatch reading.
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.
- `data = response.json()`: sets `data` to the value of `response.json()`.
- `choice = data["choices"][0]`: sets `choice` to the value of `data['choices'][0]`.
- `usage = data.get("usage") or {}`: sets `usage` to the value of `data.get('usage') or {}`. `data.get('usage')` looks up `'usage'` in `data` (default (nothing) when missing).
- `return ChatResponse(`: ends the function and hands back `ChatResponse(text=choice['message']['content'] or '', usage=Usage(int(usage.g...`. `str(data.get('model', request.model))` is `data.get('model', request.model)` converted to text; `str(choice.get('finish_reason') or 'stop')` is `choice.get('finish_reason') or 'stop'` converted to text; `int(usage.get('prompt_tokens', 0))` is `usage.get('prompt_tokens', 0)` converted to a whole number.

<!-- fmt: off -->
```python
        except (KeyError, IndexError, ValueError, TypeError) as error:
            raise PermanentModelError("the provider's reply did not have the expected shape") from error
```
<!-- fmt: on -->

- `except (KeyError, IndexError, ValueError, TypeError) as error:`: runs when the error is `(KeyError, IndexError, ValueError, TypeError)`, calling it `error`.
- `raise PermanentModelError("the provider's reply did not have the expected shape") from ...`: signals an error, `PermanentModelError("the provider's reply did not have the expected shape")` with `error` recorded as the cause; normal flow stops here and the nearest matching `except` takes over.

#### `src/guard_redteam/infrastructure/llm/recorded.py`

<!-- fmt: off -->
```python
"""The recorded adapter replays real responses from JSONL fixtures; the recording adapter writes them.

A fixture line holds the request's hash, the request itself (so a human can read it) and the response. The
Java port reads the same files with the same hash.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from guard_redteam.application.ports import ChatModel
```
<!-- fmt: on -->

- `"""The recorded adapter replays real responses from JSONL fixtures; the recording adapt...`: a docstring (documentation text). It says: "The recorded adapter replays real responses from JSONL fixtures; the recording adapter writes them."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `import threading`: imports the module(s) `threading` so this file can use them. `threading` is threads and locks.
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).
- `from guard_redteam.application.ports import ChatModel`: takes the name(s) `ChatModel` from the module `guard_redteam.application.ports` (a module of this project).

<!-- fmt: off -->
```python
from guard_redteam.domain.llm import ChatRequest, ChatResponse, FixtureMissError, Message, Usage


def request_to_json(request: ChatRequest) -> dict[str, Any]:
    """The request as plain JSON data."""
    return {
        "model": request.model,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "seed": request.seed,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
    }
```
<!-- fmt: on -->

- `from guard_redteam.domain.llm import ChatRequest, ChatResponse, FixtureMissError, Messa...`: takes the name(s) `ChatRequest, ChatResponse, FixtureMissError, Message, Usage` from the module `guard_redteam.domain.llm` (a module of this project).
- `def request_to_json(request: ChatRequest) -> dict[str, Any]:`: defines the function `request_to_json` taking request (ChatRequest) and returns `dict[str, Any]`. Purpose: The request as plain JSON data.
- `"""The request as plain JSON data."""`: a docstring (documentation text). It says: "The request as plain JSON data."
- `return {`: ends the function and hands back `{'model': request.model, 'temperature': request.temperature, 'max_tokens': re...`. `[{'role': m.role, 'content': m.content} for m in request.messages]` builds a list: for each `m` in `request.messages`.

<!-- fmt: off -->
```python
def summarize_request(request: ChatRequest, limit: int = 160) -> dict[str, Any]:
    """The request for a fixture line: the decoding settings and each message cut to `limit` characters.

    The fixture key already identifies the full request; the summary only lets a human see what was asked.
    """
    data = request_to_json(request)
    data["messages"] = [
        {
            "role": m.role,
            "content": m.content if len(m.content) <= limit else f"{m.content[:limit]}...[{len(m.content)} chars]",
        }
        for m in request.messages
    ]
    return data
```
<!-- fmt: on -->

- `def summarize_request(request: ChatRequest, limit: int = 160) -> dict[str, Any]:`: defines the function `summarize_request` taking request (ChatRequest); limit (int), default 160 and returns `dict[str, Any]`. Purpose: The request for a fixture line: the decoding settings and each message cut to `limit` characters.
- `"""The request for a fixture line: the decoding settings and each message cut to 'limit...`: a docstring (documentation text). It says: "The request for a fixture line: the decoding settings and each message cut to `limit` characters."
- `data = request_to_json(request)`: sets `data` to the value of `request_to_json(request)`.
- `data["messages"] = [`: sets `data['messages']` to the value of `[{'role': m.role, 'content': m.content if len(m.content) <= limit else f'{m.c...`. `[{'role': m.role, 'content': m.content if len(m.content) <= limit e...` builds a list: for each `m` in `request.messages`; `m.content if len(m.content) <= limit else f'{m.content[:limit]}...[...` gives `m.content` when `len(m.content) <= limit` is true, otherwise `f'{m.content[:limit]}...[{len(m.conte...`; the f-string inserts `m.content[:limit]`, `len(m.content)` into the text.
- `return data`: ends the function and hands back `data`.

<!-- fmt: off -->
```python
def request_from_json(data: dict[str, Any]) -> ChatRequest:
    """Rebuild a request from `request_to_json` output."""
    return ChatRequest(
        model=data["model"],
        messages=tuple(Message(m["role"], m["content"]) for m in data["messages"]),
        temperature=float(data["temperature"]),
        max_tokens=int(data["max_tokens"]),
        seed=data.get("seed"),
    )


def response_to_json(response: ChatResponse) -> dict[str, Any]:
    """The response as plain JSON data."""
    return {
        "text": response.text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "model": response.model,
        "finish_reason": response.finish_reason,
        "latency_s": round(response.latency_s, 4),
    }
```
<!-- fmt: on -->

- `def request_from_json(data: dict[str, Any]) -> ChatRequest:`: defines the function `request_from_json` taking data (dict[str, Any]) and returns `ChatRequest`. Purpose: Rebuild a request from `request_to_json` output.
- `"""Rebuild a request from 'request_to_json' output."""`: a docstring (documentation text). It says: "Rebuild a request from `request_to_json` output."
- `return ChatRequest(`: ends the function and hands back `ChatRequest(model=data['model'], messages=tuple((Message(m['role'], m['conten...`. `tuple((Message(m['role'], m['content']) for m in data['messages']))` is `(Message(m['role'], m['content']) for m in data['messages'])` as a tuple; `float(data['temperature'])` is `data['temperature']` converted to a decimal number; `int(data['max_tokens'])` is `data['max_tokens']` converted to a whole number.
- `def response_to_json(response: ChatResponse) -> dict[str, Any]:`: defines the function `response_to_json` taking response (ChatResponse) and returns `dict[str, Any]`. Purpose: The response as plain JSON data.
- `"""The response as plain JSON data."""`: a docstring (documentation text). It says: "The response as plain JSON data."
- `return {`: ends the function and hands back `{'text': response.text, 'input_tokens': response.usage.input_tokens, 'output_...`. `round(response.latency_s, 4)` is `response.latency_s` rounded to `4` decimals.

<!-- fmt: off -->
```python
def response_from_json(data: dict[str, Any]) -> ChatResponse:
    """Rebuild a response from `response_to_json` output."""
    return ChatResponse(
        text=data["text"],
        usage=Usage(int(data["input_tokens"]), int(data["output_tokens"])),
        model=data["model"],
        finish_reason=data.get("finish_reason", "stop"),
        latency_s=float(data.get("latency_s", 0.0)),
    )


def load_fixtures(path: Path) -> dict[str, ChatResponse]:
    """Read every `*.jsonl` file under `path` (or the one file) into a key -> response map."""
    files = sorted(path.glob("*.jsonl")) if path.is_dir() else [path]
```
<!-- fmt: on -->

- `def response_from_json(data: dict[str, Any]) -> ChatResponse:`: defines the function `response_from_json` taking data (dict[str, Any]) and returns `ChatResponse`. Purpose: Rebuild a response from `response_to_json` output.
- `"""Rebuild a response from 'response_to_json' output."""`: a docstring (documentation text). It says: "Rebuild a response from `response_to_json` output."
- `return ChatResponse(`: ends the function and hands back `ChatResponse(text=data['text'], usage=Usage(int(data['input_tokens']), int(da...`. `data.get('finish_reason', 'stop')` looks up `'finish_reason'` in `data` (default `'stop'` when missing); `float(data.get('latency_s', 0.0))` is `data.get('latency_s', 0.0)` converted to a decimal number; `int(data['input_tokens'])` is `data['input_tokens']` converted to a whole number.
- `def load_fixtures(path: Path) -> dict[str, ChatResponse]:`: defines the function `load_fixtures` taking path (Path) and returns `dict[str, ChatResponse]`. Purpose: Read every `*.jsonl` file under `path` (or the one file) into a key -> response map.
- `"""Read every '*.jsonl' file under 'path' (or the one file) into a key -> response map."""`: a docstring (documentation text). It says: "Read every `*.jsonl` file under `path` (or the one file) into a key -> response map."
- `files = sorted(path.glob("*.jsonl")) if path.is_dir() else [path]`: sets `files` to the value of `sorted(path.glob('*.jsonl')) if path.is_dir() else [path]`. `sorted(path.glob('*.jsonl')) if path.is_dir() else [path]` gives `sorted(path.glob('*.jsonl'))` when `path.is_dir()` is true, otherwise `[path]`; `path.is_dir()` is whether `path` is a folder; `sorted(path.glob('*.jsonl'))` is `path.glob('*.jsonl')` in sorted order.

<!-- fmt: off -->
```python
    found: dict[str, ChatResponse] = {}
    for file in files:
        with file.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    found[row["key"]] = response_from_json(row["response"])
    return found


class RecordedChatModel:
    """Answers from fixtures only; an unknown request is a FixtureMissError, never a silent guess."""

    def __init__(self, fixtures: Path) -> None:
```
<!-- fmt: on -->

- `found: dict[str, ChatResponse] = {}`: declares a variable `found` of type `dict[str, ChatResponse]` and sets it to `{}`.
- `for file in files:`: repeats the block below once for each `file` in `files`.
- `with file.open(encoding="utf-8") as handle:`: opens `file.open(encoding='utf-8')` (named `handle`) for the duration of the block below and cleans up afterwards. `file.open(encoding='utf-8')` opens `file`.
- `for line in handle:`: repeats the block below once for each `line` in `handle`.
- `if line.strip():`: runs the block below only if `line.strip()` is true. `line.strip()` is `line` without white space at both ends.
- `row = json.loads(line)`: sets `row` to the value of `json.loads(line)`. `json.loads(line)` is the JSON text `line` turned into Python values.
- `found[row["key"]] = response_from_json(row["response"])`: sets `found[row['key']]` to the value of `response_from_json(row['response'])`.
- `return found`: ends the function and hands back `found`.
- `class RecordedChatModel:`: defines the class `RecordedChatModel`. Purpose: Answers from fixtures only; an unknown request is a FixtureMissError, never a silent guess.
- `"""Answers from fixtures only; an unknown request is a FixtureMissError, never a silent...`: a docstring (documentation text). It says: "Answers from fixtures only; an unknown request is a FixtureMissError, never a silent guess."
- `def __init__(self, fixtures: Path) -> None:`: defines the method `__init__` taking fixtures (Path) and returns `None`.

<!-- fmt: off -->
```python
        self._responses = load_fixtures(fixtures)

    def __len__(self) -> int:
        return len(self._responses)

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Return the recorded response for this exact request."""
        try:
            return self._responses[request.fixture_key()]
        except KeyError:
            raise FixtureMissError(
                f"no recorded response for model={request.model} key={request.fixture_key()[:12]} "
                f"({len(request.messages)} messages); run `make record` with a local model to add it"
            ) from None
```
<!-- fmt: on -->

- `self._responses = load_fixtures(fixtures)`: sets `self._responses` to the value of `load_fixtures(fixtures)`.
- `def __len__(self) -> int:`: defines the method `__len__` taking no arguments and returns `int`.
- `return len(self._responses)`: ends the function and hands back `len(self._responses)`. `len(self._responses)` is the number of items in `self._responses`.
- `def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:`: defines the method `complete` taking request (ChatRequest); timeout_s (float), default 60.0 and returns `ChatResponse`. Purpose: Return the recorded response for this exact request.
- `"""Return the recorded response for this exact request."""`: a docstring (documentation text). It says: "Return the recorded response for this exact request."
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.
- `return self._responses[request.fixture_key()]`: ends the function and hands back `self._responses[request.fixture_key()]`.
- `except KeyError:`: runs when the error is `KeyError`.
- `raise FixtureMissError(`: signals an error, `FixtureMissError(f'no recorded response for model={request.model} key={reques...` with `None` recorded as the cause; normal flow stops here and the nearest matching `except` takes over. the f-string inserts `request.model`, `request.fixture_key()[:12]`, `len(request.messages)` into the text; `request.fixture_key()[:12]` is a slice (a part) of `request.fixture_key()`; `len(request.messages)` is the number of items in `request.messages`.

<!-- fmt: off -->
```python
class RecordingChatModel:
    """Wraps a real model and appends every new exchange to a fixture file, so a run can be replayed offline.

    A request already in the file is answered from the file, so a recording run can be interrupted and resumed.
    """

    def __init__(self, inner: ChatModel, path: Path) -> None:
        self._inner = inner
        self._path = path
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._seen = load_fixtures(path) if path.exists() else {}

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
```
<!-- fmt: on -->

- `class RecordingChatModel:`: defines the class `RecordingChatModel`. Purpose: Wraps a real model and appends every new exchange to a fixture file, so a run can be replayed offline.
- `"""Wraps a real model and appends every new exchange to a fixture file, so a run can be...`: a docstring (documentation text). It says: "Wraps a real model and appends every new exchange to a fixture file, so a run can be replayed offline."
- `def __init__(self, inner: ChatModel, path: Path) -> None:`: defines the method `__init__` taking inner (ChatModel); path (Path) and returns `None`.
- `self._inner = inner`: sets `self._inner` to the value of `inner`.
- `self._path = path`: sets `self._path` to the value of `path`.
- `self._lock = threading.Lock()`: sets `self._lock` to the value of `threading.Lock()`. `threading.Lock()` is a lock.
- `path.parent.mkdir(parents=True, exist_ok=True)`: runs `path.parent.mkdir(parents=True, exist_ok=True)` for its effect and ignores the result. `path.parent.mkdir(parents=True, exist_ok=True)` creates the folder `path.parent`.
- `self._seen = load_fixtures(path) if path.exists() else {}`: sets `self._seen` to the value of `load_fixtures(path) if path.exists() else {}`. `load_fixtures(path) if path.exists() else {}` gives `load_fixtures(path)` when `path.exists()` is true, otherwise `{}`; `path.exists()` is whether `path` exists.
- `def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:`: defines the method `complete` taking request (ChatRequest); timeout_s (float), default 60.0 and returns `ChatResponse`. Purpose: Answer from the file when the request is known, else call the inner model and store the exchange.

<!-- fmt: off -->
```python
        """Answer from the file when the request is known, else call the inner model and store the exchange."""
        key = request.fixture_key()
        with self._lock:
            known = self._seen.get(key)
        if known is not None:
            return known
        response = self._inner.complete(request, timeout_s)
        with self._lock:
            if key not in self._seen:
                row = {"key": key, "request": summarize_request(request), "response": response_to_json(response)}
                with self._path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                self._seen[key] = response
        return response
```
<!-- fmt: on -->

- `"""Answer from the file when the request is known, else call the inner model and store ...`: a docstring (documentation text). It says: "Answer from the file when the request is known, else call the inner model and store the exchange."
- `key = request.fixture_key()`: sets `key` to the value of `request.fixture_key()`.
- `with self._lock:`: opens `self._lock` for the duration of the block below and cleans up afterwards.
- `known = self._seen.get(key)`: sets `known` to the value of `self._seen.get(key)`. `self._seen.get(key)` looks up `key` in `self._seen` (default (nothing) when missing).
- `if known is not None:`: runs the block below only if `known is not None` is true. `known is not None` tests that there is something in `known`.
- `return known`: ends the function and hands back `known`.
- `response = self._inner.complete(request, timeout_s)`: sets `response` to the value of `self._inner.complete(request, timeout_s)`.
- `with self._lock:`: opens `self._lock` for the duration of the block below and cleans up afterwards.
- `if key not in self._seen:`: runs the block below only if `key not in self._seen` is true.
- `row = {"key": key, "request": summarize_request(request), "response": response_to_json(...`: sets `row` to a dictionary with 3 entries.
- `with self._path.open("a", encoding="utf-8") as handle:`: opens `self._path.open('a', encoding='utf-8')` (named `handle`) for the duration of the block below and cleans up afterwards. `self._path.open('a', encoding='utf-8')` opens `self._path`.
- `handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")`: runs `handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')` for its effect and ignores the result. `handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + ...` writes `json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n'` to `handle`; `json.dumps(row, ensure_ascii=False, sort_keys=True)` is `row` written as JSON text.
- `self._seen[key] = response`: sets `self._seen[key]` to the value of `response`.
- `return response`: ends the function and hands back `response`.

#### `src/guard_redteam/infrastructure/llm/retry.py`

<!-- fmt: off -->
```python
"""Retry with exponential backoff and jitter, for adapters that call a network."""

from __future__ import annotations

import random
from collections.abc import Callable

from guard_redteam.application.ports import Clock
from guard_redteam.domain.llm import RetryableModelError


def retry_call[T](
    operation: Callable[[], T],
    *,
    attempts: int,
    clock: Clock,
    base_delay_s: float = 0.5,
    max_delay_s: float = 8.0,
    rng: random.Random | None = None,
) -> T:
```
<!-- fmt: on -->

- `"""Retry with exponential backoff and jitter, for adapters that call a network."""`: a docstring (documentation text). It says: "Retry with exponential backoff and jitter, for adapters that call a network."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import random`: imports the module(s) `random` so this file can use them. `random` is random numbers.
- `from collections.abc import Callable`: takes the name(s) `Callable` from the module `collections.abc` (abstract container types used in annotations).
- `from guard_redteam.application.ports import Clock`: takes the name(s) `Clock` from the module `guard_redteam.application.ports` (a module of this project).
- `from guard_redteam.domain.llm import RetryableModelError`: takes the name(s) `RetryableModelError` from the module `guard_redteam.domain.llm` (a module of this project).
- **New idea.** `def name[T](...)` (Python 3.12) declares a generic function: `T` is a placeholder type.
- `def retry_call[T](`: defines the function `retry_call` taking operation (Callable[[], T]); attempts (int, keyword only); clock (Clock, keyword only); base_delay_s (float, keyword only), default 0.5; max_delay_s (float, keyword only), default 8.0; rng (random.Random | None, keyword only), default None and returns `T`. Purpose: Run `operation`, retrying only RetryableModelError with backoff and full-range jitter (50% to 100%).

<!-- fmt: off -->
```python
    """Run `operation`, retrying only RetryableModelError with backoff and full-range jitter (50% to 100%)."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    jitter = rng or random.Random()
    for attempt in range(attempts):
        try:
            return operation()
        except RetryableModelError:
            if attempt == attempts - 1:
                raise
            clock.sleep(min(max_delay_s, base_delay_s * 2**attempt) * jitter.uniform(0.5, 1.0))
    raise AssertionError("unreachable")  # pragma: no cover
```
<!-- fmt: on -->

- `"""Run 'operation', retrying only RetryableModelError with backoff and full-range jitte...`: a docstring (documentation text). It says: "Run `operation`, retrying only RetryableModelError with backoff and full-range jitter (50% to 100%)."
- `if attempts < 1:`: runs the block below only if `attempts < 1` is true.
- `raise ValueError("attempts must be at least 1")`: signals an error, `ValueError('attempts must be at least 1')`; normal flow stops here and the nearest matching `except` takes over. `ValueError('attempts must be at least 1')` is a ValueError.
- `jitter = rng or random.Random()`: sets `jitter` to the value of `rng or random.Random()`. `random.Random()` is a random number generator.
- `for attempt in range(attempts):`: repeats the block below once for each `attempt` in `range(attempts)`. `range(attempts)` is the whole numbers from `0` up to, not including, `attempts`.
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.
- `return operation()`: ends the function and hands back `operation()`.
- `except RetryableModelError:`: runs when the error is `RetryableModelError`.
- `if attempt == attempts - 1:`: runs the block below only if `attempt == attempts - 1` is true.
- `raise`: signals an error, the error being handled; normal flow stops here and the nearest matching `except` takes over.
- `clock.sleep(min(max_delay_s, base_delay_s * 2**attempt) * jitter.uniform(0.5, 1.0))`: runs `clock.sleep(min(max_delay_s, base_delay_s * 2 ** attempt) * jitter.uniform(0.5, 1.0))` for its effect and ignores the result. `clock.sleep(min(max_delay_s, base_delay_s * 2 ** attempt) * jitter....` waits `min(max_delay_s, base_delay_s * 2 ** attempt) * jitter.un...` seconds; `min(max_delay_s, base_delay_s * 2 ** attempt)` is the smallest of `max_delay_s`, `base_delay_s * 2 ** attempt`; `jitter.uniform(0.5, 1.0)` is a random decimal between `0.5` and `1.0`.
- `raise AssertionError("unreachable")  # pragma: no cover`: signals an error, `AssertionError('unreachable')`; normal flow stops here and the nearest matching `except` takes over. `AssertionError('unreachable')` is an AssertionError.

#### `src/guard_redteam/infrastructure/logging_setup.py`

<!-- fmt: off -->
```python
"""Structured logging: one JSON object per line on standard error, never prompt or reply text at info level."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

_RESERVED = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    """Format a record as a single JSON line with its `extra` fields included."""
```
<!-- fmt: on -->

- `"""Structured logging: one JSON object per line on standard error, never prompt or repl...`: a docstring (documentation text). It says: "Structured logging: one JSON object per line on standard error, never prompt or reply text at info level."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `import logging`: imports the module(s) `logging` so this file can use them. `logging` is the standard logging system.
- `import sys`: imports the module(s) `sys` so this file can use them. `sys` is the running interpreter: arguments, standard streams, exit.
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).
- `_RESERVED = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message",...`: sets `_RESERVED` to the value of `set(logging.LogRecord('', 0, '', 0, '', None, None).__dict__) | {'message', '...`. `set(logging.LogRecord('', 0, '', 0, '', None, None).__dict__)` is `logging.LogRecord('', 0, '', 0, '', None, None).__dict__` as a set (each value once).
- `class JsonFormatter(logging.Formatter):`: defines the class `JsonFormatter` that inherits from `logging.Formatter`. Purpose: Format a record as a single JSON line with its `extra` fields included.
- `"""Format a record as a single JSON line with its 'extra' fields included."""`: a docstring (documentation text). It says: "Format a record as a single JSON line with its `extra` fields included."

<!-- fmt: off -->
```python
    def format(self, record: logging.LogRecord) -> str:
        """Render the record."""
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        payload.update({k: v for k, v in record.__dict__.items() if k not in _RESERVED})
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, sort_keys=True)
```
<!-- fmt: on -->

- `def format(self, record: logging.LogRecord) -> str:`: defines the method `format` taking record (logging.LogRecord) and returns `str`. Purpose: Render the record.
- `"""Render the record."""`: a docstring (documentation text). It says: "Render the record."
- `payload: dict[str, Any] = {`: declares a variable `payload` of type `dict[str, Any]` and sets it to `{'ts': self.formatTime(record, '%Y-%m-%dT%H:%M:%S'), 'level': recor...`.
- `payload.update({k: v for k, v in record.__dict__.items() if k not in _RESERVED})`: runs `payload.update({k: v for k, v in record.__dict__.items() if k not in _RESERVED})` for its effect and ignores the result. `payload.update({k: v for k, v in record.__dict__.items() if k not i...` adds the entries of `{k: v for k, v in record.__dict__.items() if k not in _RE...` to `payload`; `{k: v for k, v in record.__dict__.items() if k not in _RESERVED}` builds a dictionary: for each `(k, v)` in `record.__dict__.items()`, keeping only those for which `k not in _RESERVED` is true; `record.__dict__.items()` is the (key, value) pairs of `record.__dict__`.
- `if record.exc_info:`: runs the block below only if `record.exc_info` is true.
- `payload["exc"] = self.formatException(record.exc_info)`: sets `payload['exc']` to the value of `self.formatException(record.exc_info)`.
- `return json.dumps(payload, default=str, sort_keys=True)`: ends the function and hands back `json.dumps(payload, default=str, sort_keys=True)`. `json.dumps(payload, default=str, sort_keys=True)` is `payload` written as JSON text.

<!-- fmt: off -->
```python
def configure_logging(level: str = "INFO") -> None:
    """Install the JSON formatter on the root logger (idempotent)."""
    root = logging.getLogger()
    root.setLevel(level.upper())
    for handler in list(root.handlers):
        if getattr(handler, "_json_handler", False):
            root.removeHandler(handler)
    handler = logging.StreamHandler(sys.stderr)
    handler._json_handler = True  # type: ignore[attr-defined]
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    logging.getLogger("httpx").setLevel(logging.WARNING)
```
<!-- fmt: on -->

- `def configure_logging(level: str = "INFO") -> None:`: defines the function `configure_logging` taking level (str), default 'INFO' and returns `None`. Purpose: Install the JSON formatter on the root logger (idempotent).
- `"""Install the JSON formatter on the root logger (idempotent)."""`: a docstring (documentation text). It says: "Install the JSON formatter on the root logger (idempotent)."
- `root = logging.getLogger()`: sets `root` to the value of `logging.getLogger()`. `logging.getLogger()` is the logger named (nothing).
- `root.setLevel(level.upper())`: runs `root.setLevel(level.upper())` for its effect and ignores the result. `root.setLevel(level.upper())` sets how chatty the logger `root` is; `level.upper()` is `level` in upper case.
- `for handler in list(root.handlers):`: repeats the block below once for each `handler` in `list(root.handlers)`. `list(root.handlers)` is `root.handlers` copied into a list.
- `if getattr(handler, "_json_handler", False):`: runs the block below only if `getattr(handler, '_json_handler', False)` is true. `getattr(handler, '_json_handler', False)` is the attribute `'_json_handler'` of `handler`.
- `root.removeHandler(handler)`: runs `root.removeHandler(handler)` for its effect and ignores the result.
- `handler = logging.StreamHandler(sys.stderr)`: sets `handler` to the value of `logging.StreamHandler(sys.stderr)`.
- `handler._json_handler = True  # type: ignore[attr-defined]`: sets `handler._json_handler` to the constant `True`.
- `handler.setFormatter(JsonFormatter())`: runs `handler.setFormatter(JsonFormatter())` for its effect and ignores the result.
- `root.addHandler(handler)`: runs `root.addHandler(handler)` for its effect and ignores the result. `root.addHandler(handler)` adds a handler to the logger `root`.
- `logging.getLogger("httpx").setLevel(logging.WARNING)`: runs `logging.getLogger('httpx').setLevel(logging.WARNING)` for its effect and ignores the result. `logging.getLogger('httpx').setLevel(logging.WARNING)` sets how chatty the logger `logging.getLogger('httpx')` is; `logging.getLogger('httpx')` is the logger named `'httpx'`.

#### `src/guard_redteam/infrastructure/parallel.py`

<!-- fmt: off -->
```python
"""Run independent jobs on a few threads, keeping the input order of the results."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def thread_mapper(workers: int) -> Callable[[Callable[[T], R], Sequence[T]], list[R]]:
    """A mapper that uses `workers` threads (one means no threads at all)."""
```
<!-- fmt: on -->

- `"""Run independent jobs on a few threads, keeping the input order of the results."""`: a docstring (documentation text). It says: "Run independent jobs on a few threads, keeping the input order of the results."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from collections.abc import Callable, Sequence`: takes the name(s) `Callable, Sequence` from the module `collections.abc` (abstract container types used in annotations).
- `from concurrent.futures import ThreadPoolExecutor`: takes the name(s) `ThreadPoolExecutor` from the module `concurrent.futures` (thread and process pools).
- `from typing import TypeVar`: takes the name(s) `TypeVar` from the module `typing` (names used in type annotations).
- `T = TypeVar("T")`: sets `T` to the value of `TypeVar('T')`. `TypeVar('T')` is a placeholder type.
- `R = TypeVar("R")`: sets `R` to the value of `TypeVar('R')`. `TypeVar('R')` is a placeholder type.
- `def thread_mapper(workers: int) -> Callable[[Callable[[T], R], Sequence[T]], list[R]]:`: defines the function `thread_mapper` taking workers (int) and returns `Callable[[Callable[[T], R], Sequence[T]], list[R]]`. Purpose: A mapper that uses `workers` threads (one means no threads at all).
- `"""A mapper that uses 'workers' threads (one means no threads at all)."""`: a docstring (documentation text). It says: "A mapper that uses `workers` threads (one means no threads at all)."

<!-- fmt: off -->
```python
    def run(function: Callable[[T], R], items: Sequence[T]) -> list[R]:
        if workers <= 1:
            return [function(item) for item in items]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(function, items))

    return run
```
<!-- fmt: on -->

- **New idea.** A function defined inside another function is a **closure**: it can read the variables of the function around it, even after that function has returned.
- `def run(function: Callable[[T], R], items: Sequence[T]) -> list[R]:`: defines the function `run` taking function (Callable[[T], R]); items (Sequence[T]) and returns `list[R]`.
- `if workers <= 1:`: runs the block below only if `workers <= 1` is true.
- `return [function(item) for item in items]`: ends the function and hands back `[function(item) for item in items]`. `[function(item) for item in items]` builds a list: for each `item` in `items`.
- `with ThreadPoolExecutor(max_workers=workers) as pool:`: opens `ThreadPoolExecutor(max_workers=workers)` (named `pool`) for the duration of the block below and cleans up afterwards. `ThreadPoolExecutor(max_workers=workers)` is a pool of worker threads.
- `return list(pool.map(function, items))`: ends the function and hands back `list(pool.map(function, items))`. `list(pool.map(function, items))` is `pool.map(function, items)` copied into a list; `pool.map(function, items)` applies `function` to each item, on the pool `pool`.
- `return run`: ends the function and hands back `run`.

#### `src/guard_redteam/infrastructure/prompts.py`

<!-- fmt: off -->
```python
"""Prompt templates read from versioned files under prompts/."""

from __future__ import annotations

from pathlib import Path


class FilePromptStore:
    """Looks up `<name>.md` in a directory; a missing prompt is a clear error."""

    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def get(self, name: str) -> str:
```
<!-- fmt: on -->

- `"""Prompt templates read from versioned files under prompts/."""`: a docstring (documentation text). It says: "Prompt templates read from versioned files under prompts/."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `class FilePromptStore:`: defines the class `FilePromptStore`. Purpose: Looks up `<name>.md` in a directory; a missing prompt is a clear error.
- `"""Looks up '<name>.md' in a directory; a missing prompt is a clear error."""`: a docstring (documentation text). It says: "Looks up `<name>.md` in a directory; a missing prompt is a clear error."
- `def __init__(self, directory: Path) -> None:`: defines the method `__init__` taking directory (Path) and returns `None`.
- `self._directory = directory`: sets `self._directory` to the value of `directory`.
- `def get(self, name: str) -> str:`: defines the method `get` taking name (str) and returns `str`. Purpose: The template text with the trailing newline removed (the Java port does the same).

<!-- fmt: off -->
```python
        """The template text with the trailing newline removed (the Java port does the same)."""
        path = self._directory / f"{name}.md"
        if not path.is_file():
            raise FileNotFoundError(f"no prompt named {name!r} in {self._directory}")
        return path.read_text(encoding="utf-8").rstrip("\n")
```
<!-- fmt: on -->

- `"""The template text with the trailing newline removed (the Java port does the same)."""`: a docstring (documentation text). It says: "The template text with the trailing newline removed (the Java port does the same)."
- `path = self._directory / f"{name}.md"`: sets `path` to the value of `self._directory / f'{name}.md'`. the f-string inserts `name` into the text.
- `if not path.is_file():`: runs the block below only if `not path.is_file()` is true. `path.is_file()` is whether `path` is a file.
- `raise FileNotFoundError(f"no prompt named {name!r} in {self._directory}")`: signals an error, `FileNotFoundError(f'no prompt named {name!r} in {self._directory}')`; normal flow stops here and the nearest matching `except` takes over. `FileNotFoundError(f'no prompt named {name!r} in {self._directory}')` is a FileNotFoundError; the f-string inserts `name`, `self._directory` into the text.
- `return path.read_text(encoding="utf-8").rstrip("\n")`: ends the function and hands back `path.read_text(encoding='utf-8').rstrip('\n')`. `path.read_text(encoding='utf-8').rstrip('\n')` is `path.read_text(encoding='utf-8')` without the given characters at the end; `path.read_text(encoding='utf-8')` is the whole text of the file `path`.

#### `src/guard_redteam/infrastructure/reports.py`

<!-- fmt: off -->
```python
"""Writing reports as JSON, JSONL and Markdown with stable key order and rounded floats."""

from __future__ import annotations

import dataclasses
import json
from enum import Enum
from pathlib import Path
from typing import Any


def to_jsonable(value: Any) -> Any:
    """Dataclasses, enums and tuples as plain JSON data; floats rounded to 6 places."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
```
<!-- fmt: on -->

- `"""Writing reports as JSON, JSONL and Markdown with stable key order and rounded floats...`: a docstring (documentation text). It says: "Writing reports as JSON, JSONL and Markdown with stable key order and rounded floats."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import dataclasses`: imports the module(s) `dataclasses` so this file can use them. `dataclasses` is classes that are mostly data.
- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `from enum import Enum`: takes the name(s) `Enum` from the module `enum` (named constants).
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).
- `def to_jsonable(value: Any) -> Any:`: defines the function `to_jsonable` taking value (Any) and returns `Any`. Purpose: Dataclasses, enums and tuples as plain JSON data; floats rounded to 6 places.
- `"""Dataclasses, enums and tuples as plain JSON data; floats rounded to 6 places."""`: a docstring (documentation text). It says: "Dataclasses, enums and tuples as plain JSON data; floats rounded to 6 places."
- `if dataclasses.is_dataclass(value) and not isinstance(value, type):`: runs the block below only if `dataclasses.is_dataclass(value) and (not isinstance(value, type))` is true. `isinstance(value, type)` is whether `value` is a `type`.

<!-- fmt: off -->
```python
        return {f.name: to_jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [to_jsonable(v) for v in value]
    if isinstance(value, float):
        return round(value, 6) if value != float("inf") else None
    return value


def dump_json(path: Path, value: Any) -> None:
    """Write one JSON document, indented, keys sorted."""
```
<!-- fmt: on -->

- `return {f.name: to_jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}`: ends the function and hands back `{f.name: to_jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}`. `{f.name: to_jsonable(getattr(value, f.name)) for f in dataclasses.f...` builds a dictionary: for each `f` in `dataclasses.fields(value)`; `getattr(value, f.name)` is the attribute `f.name` of `value`.
- `if isinstance(value, Enum):`: runs the block below only if `isinstance(value, Enum)` is true. `isinstance(value, Enum)` is whether `value` is a `Enum`.
- `return value.value`: ends the function and hands back `value.value`.
- `if isinstance(value, dict):`: runs the block below only if `isinstance(value, dict)` is true. `isinstance(value, dict)` is whether `value` is a `dict`.
- `return {str(k): to_jsonable(v) for k, v in value.items()}`: ends the function and hands back `{str(k): to_jsonable(v) for k, v in value.items()}`. `{str(k): to_jsonable(v) for k, v in value.items()}` builds a dictionary: for each `(k, v)` in `value.items()`; `str(k)` is `k` converted to text; `value.items()` is the (key, value) pairs of `value`.
- `if isinstance(value, list | tuple):`: runs the block below only if `isinstance(value, list | tuple)` is true. `isinstance(value, list | tuple)` is whether `value` is a `list | tuple`.
- `return [to_jsonable(v) for v in value]`: ends the function and hands back `[to_jsonable(v) for v in value]`. `[to_jsonable(v) for v in value]` builds a list: for each `v` in `value`.
- `if isinstance(value, float):`: runs the block below only if `isinstance(value, float)` is true. `isinstance(value, float)` is whether `value` is a `float`.
- `return round(value, 6) if value != float("inf") else None`: ends the function and hands back `round(value, 6) if value != float('inf') else None`. `round(value, 6) if value != float('inf') else None` gives `round(value, 6)` when `value != float('inf')` is true, otherwise `None`; `round(value, 6)` is `value` rounded to `6` decimals; `float('inf')` is `'inf'` converted to a decimal number.
- `return value`: ends the function and hands back `value`.
- `def dump_json(path: Path, value: Any) -> None:`: defines the function `dump_json` taking path (Path); value (Any) and returns `None`. Purpose: Write one JSON document, indented, keys sorted.
- `"""Write one JSON document, indented, keys sorted."""`: a docstring (documentation text). It says: "Write one JSON document, indented, keys sorted."

<!-- fmt: off -->
```python
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(to_jsonable(value), indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def dump_jsonl(path: Path, rows: list[Any]) -> None:
    """Write one JSON object per line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(to_jsonable(row), sort_keys=True, ensure_ascii=False) + "\n")
```
<!-- fmt: on -->

- `path.parent.mkdir(parents=True, exist_ok=True)`: runs `path.parent.mkdir(parents=True, exist_ok=True)` for its effect and ignores the result. `path.parent.mkdir(parents=True, exist_ok=True)` creates the folder `path.parent`.
- `path.write_text(`: runs `path.write_text(json.dumps(to_jsonable(value), indent=2, sort_keys=True, ensure_ascii=F...` for its effect and ignores the result. `path.write_text(json.dumps(to_jsonable(value), indent=2, sort_keys=...` writes `json.dumps(to_jsonable(value), indent=2, sort_keys=True, ...` as the content of the file `path`; `json.dumps(to_jsonable(value), indent=2, sort_keys=True, ensure_asc...` is `to_jsonable(value)` written as JSON text.
- `def dump_jsonl(path: Path, rows: list[Any]) -> None:`: defines the function `dump_jsonl` taking path (Path); rows (list[Any]) and returns `None`. Purpose: Write one JSON object per line.
- `"""Write one JSON object per line."""`: a docstring (documentation text). It says: "Write one JSON object per line."
- `path.parent.mkdir(parents=True, exist_ok=True)`: runs `path.parent.mkdir(parents=True, exist_ok=True)` for its effect and ignores the result. `path.parent.mkdir(parents=True, exist_ok=True)` creates the folder `path.parent`.
- `with path.open("w", encoding="utf-8") as handle:`: opens `path.open('w', encoding='utf-8')` (named `handle`) for the duration of the block below and cleans up afterwards. `path.open('w', encoding='utf-8')` opens `path`.
- `for row in rows:`: repeats the block below once for each `row` in `rows`.
- `handle.write(json.dumps(to_jsonable(row), sort_keys=True, ensure_ascii=False) + "\n")`: runs `handle.write(json.dumps(to_jsonable(row), sort_keys=True, ensure_ascii=False) + '\n')` for its effect and ignores the result. `handle.write(json.dumps(to_jsonable(row), sort_keys=True, ensure_as...` writes `json.dumps(to_jsonable(row), sort_keys=True, ensure_ascii...` to `handle`; `json.dumps(to_jsonable(row), sort_keys=True, ensure_ascii=False)` is `to_jsonable(row)` written as JSON text.

<!-- fmt: off -->
```python
def load_json(path: Path) -> Any:
    """Read one JSON document."""
    return json.loads(path.read_text(encoding="utf-8"))
```
<!-- fmt: on -->

- `def load_json(path: Path) -> Any:`: defines the function `load_json` taking path (Path) and returns `Any`. Purpose: Read one JSON document.
- `"""Read one JSON document."""`: a docstring (documentation text). It says: "Read one JSON document."
- `return json.loads(path.read_text(encoding="utf-8"))`: ends the function and hands back `json.loads(path.read_text(encoding='utf-8'))`. `json.loads(path.read_text(encoding='utf-8'))` is the JSON text `path.read_text(encoding='utf-8')` turned into Python values; `path.read_text(encoding='utf-8')` is the whole text of the file `path`.

#### `src/guard_redteam/infrastructure/settings.py`

<!-- fmt: off -->
```python
"""Settings from the environment, validated once at start-up."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from guard_redteam.infrastructure.env import read_float, read_int, read_str


@dataclass(frozen=True)
class Settings:
    """Everything configurable about a run."""
```
<!-- fmt: on -->

- `"""Settings from the environment, validated once at start-up."""`: a docstring (documentation text). It says: "Settings from the environment, validated once at start-up."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from collections.abc import Mapping`: takes the name(s) `Mapping` from the module `collections.abc` (abstract container types used in annotations).
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `from guard_redteam.infrastructure.env import read_float, read_int, read_str`: takes the name(s) `read_float, read_int, read_str` from the module `guard_redteam.infrastructure.env` (a module of this project).
- **New idea.** `@dataclass` is a **decorator** (a function applied to the class below it). It reads the annotated fields and writes `__init__`, `__repr__` and `__eq__` for you. `frozen=True` forbids changing a field after creation.
- `class Settings:`: defines the class `Settings`. Decorators: `dataclass(frozen=True)`. Purpose: Everything configurable about a run.
- `"""Everything configurable about a run."""`: a docstring (documentation text). It says: "Everything configurable about a run."

<!-- fmt: off -->
```python
    assistant_model: str
    guard_model: str
    temperature: float
    runs: int
    workers: int
    log_level: str
    data_dir: Path
    prompts_dir: Path
    fixtures_dir: Path
    reports_dir: Path
    evidence_dir: Path
    evals_dir: Path

    @classmethod
    def from_env(cls, env: Mapping[str, str], root: Path) -> Settings:
```
<!-- fmt: on -->

- `assistant_model: str`: declares a field of the class `assistant_model` of type `str` (no value yet).
- `guard_model: str`: declares a field of the class `guard_model` of type `str` (no value yet).
- `temperature: float`: declares a field of the class `temperature` of type `float` (no value yet).
- `runs: int`: declares a field of the class `runs` of type `int` (no value yet).
- `workers: int`: declares a field of the class `workers` of type `int` (no value yet).
- `log_level: str`: declares a field of the class `log_level` of type `str` (no value yet).
- `data_dir: Path`: declares a field of the class `data_dir` of type `Path` (no value yet).
- `prompts_dir: Path`: declares a field of the class `prompts_dir` of type `Path` (no value yet).
- `fixtures_dir: Path`: declares a field of the class `fixtures_dir` of type `Path` (no value yet).
- `reports_dir: Path`: declares a field of the class `reports_dir` of type `Path` (no value yet).
- `evidence_dir: Path`: declares a field of the class `evidence_dir` of type `Path` (no value yet).
- `evals_dir: Path`: declares a field of the class `evals_dir` of type `Path` (no value yet).
- **New idea.** A **decorator** is a line `@name` above a function or class. It passes the function to `name` and uses what comes back instead. It is a way to add behaviour without editing the function.
- `def from_env(cls, env: Mapping[str, str], root: Path) -> Settings:`: defines the method `from_env` taking env (Mapping[str, str]); root (Path) and returns `Settings`. Decorators: `classmethod`. Purpose: Read and validate; raises ConfigError on a bad value.

<!-- fmt: off -->
```python
        """Read and validate; raises ConfigError on a bad value."""
        return cls(
            assistant_model=read_str(env, "ASSISTANT_MODEL", "qwen2.5:1.5b"),
            guard_model=read_str(env, "GUARD_MODEL", "qwen2.5:1.5b"),
            temperature=read_float(env, "TEMPERATURE", 0.7),
            runs=read_int(env, "RUNS", 3, minimum=1),
            workers=read_int(env, "WORKERS", 1, minimum=1),
            log_level=read_str(env, "LOG_LEVEL", "INFO"),
            data_dir=root / "data",
            prompts_dir=root / "prompts",
            fixtures_dir=Path(read_str(env, "FIXTURES_DIR", str(root / "tests" / "fixtures"))),
            reports_dir=Path(read_str(env, "REPORTS_DIR", str(root / "reports"))),
            evidence_dir=Path(read_str(env, "EVIDENCE_DIR", str(root / "evidence"))),
            evals_dir=root / "evals",
        )
```
<!-- fmt: on -->

- `"""Read and validate; raises ConfigError on a bad value."""`: a docstring (documentation text). It says: "Read and validate; raises ConfigError on a bad value."
- `return cls(`: ends the function and hands back `cls(assistant_model=read_str(env, 'ASSISTANT_MODEL', 'qwen2.5:1.5b'), guard_m...`. `Path(read_str(env, 'FIXTURES_DIR', str(root / 'tests' / 'fixtures')))` is the file path `read_str(env, 'FIXTURES_DIR', str(root / 'tests' / 'fixtu...`; `Path(read_str(env, 'REPORTS_DIR', str(root / 'reports')))` is the file path `read_str(env, 'REPORTS_DIR', str(root / 'reports'))`; `Path(read_str(env, 'EVIDENCE_DIR', str(root / 'evidence')))` is the file path `read_str(env, 'EVIDENCE_DIR', str(root / 'evidence'))`.

## Try it yourself

1. `wc -l src/guard_redteam/infrastructure/__init__.py src/guard_redteam/infrastructure/capture.py src/guard_redteam/infrastructure/clock.py` prints the line count of the first files; the tables above show the same numbers.
2. `.venv/bin/python -c "import guard_redteam.infrastructure.capture; print('imports fine')"` prints `imports fine`.
3. `.venv/bin/lint-imports` ends with `Contracts: 2 kept, 0 broken.`
4. `.venv/bin/python -m pytest tests/unit -q -k infrastructure | tail -3` runs the tests that exercise this layer and ends with a line such as `N passed`.
5. `grep -c "^def \|^class \|^    def " src/guard_redteam/infrastructure/capture.py` counts the functions and classes in the first file.

## Mistakes people make

- Letting a library's exception types leak into the inner layers; adapters convert them.
- Reading settings in many places; they are read once and passed on.
- Doing work at import time (opening files, connecting); do it when the adapter is built.
- Not closing files, connections or processes.
- Hard-coding addresses and paths; they come from settings.

## Check yourself

1. **What does an adapter do?**  
   It implements a port using a concrete tool or service.
2. **Which layer may import `httpx`?**  
   Infrastructure (and interfaces); the domain and application layers may not.
3. **Why convert library errors into project errors?**  
   So the inner layers do not depend on the library.
4. **Where are settings read?**  
   In the infrastructure layer, once, and then passed on.
5. **What should happen at import time?**  
   Nothing that has side effects.

## Further reading

The Python language reference: https://docs.python.org/3/reference/ and the tutorial https://docs.python.org/3/tutorial/ (both for Python 3.13; the project accepts 3.12 or newer).
