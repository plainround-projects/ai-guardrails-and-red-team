"""The guard layer around the assistant: redact in, guard the input and the data, guard the output, restore."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from guard_redteam.application.assistant import AssistantTurn, SupportAssistant
from guard_redteam.application.guards import REFUSAL, InputGuard, OutputGuard
from guard_redteam.domain.redaction import redact, restore, scrub

LOG = logging.getLogger("guard_redteam.pipeline")

WEAKENINGS = ("remove_guards", "remove_canary_check", "remove_input_guard", "remove_output_guard")


@dataclass(frozen=True)
class GuardFlags:
    """Which parts of the guard layer are switched on. `bare()` is the assistant with nothing around it."""

    redact: bool = True
    input_guard: bool = True
    data_scan: bool = True
    output_guard: bool = True

    @classmethod
    def bare(cls) -> GuardFlags:
        """No guard layer at all."""
        return cls(False, False, False, False)


@dataclass(frozen=True)
class Request:
    """One customer request."""

    customer: str
    message: str
    seed: int
    help_page: str | None = None
    note_order: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class Response:
    """What the customer sees, and why."""

    reply: str
    blocked: bool
    stage: str | None
    reasons: tuple[str, ...]
    raw_reply: str
    tool_called: bool
    unresolved: tuple[str, ...]  # placeholders that were not this request's own and were replaced by a neutral note


class Pipeline:
    """The guarded assistant. With `GuardFlags.bare()` it is the bare assistant, so one class serves both sides of
    every comparison and a weakening is a flag, not a different code path."""

    def __init__(
        self,
        assistant: SupportAssistant,
        input_guard: InputGuard,
        output_guard: OutputGuard,
        flags: GuardFlags,
    ) -> None:
        self._assistant = assistant
        self._input = input_guard
        self._output = output_guard
        self._flags = flags

    def system_prompt(self, customer: str) -> str:
        """The assistant's system prompt for a customer (the attack judge needs it to detect prompt extraction)."""
        return self._assistant.system_prompt(customer)

    def respond(self, request: Request, customer_values: tuple[str, ...] = ()) -> Response:
        """Serve one request. `customer_values` are the signed-in customer's own email and phone: placeholders for
        them in outside data may be restored in the reply; every other placeholder stays redacted."""
        flags = self._flags
        text, mapping = (request.message, {}) if not flags.redact else redact(request.message)
        if flags.input_guard:
            decision = self._input.decide(text)
            if decision.label == "block":
                return self._refuse(request, "input", decision.reasons)
        turn = AssistantTurn(request.customer, text, request.seed, request.help_page, request.note_order, request.note)
        data_mapping = dict(mapping)

        def redact_data(data: str) -> str:
            redacted, _ = redact(data, data_mapping)
            return redacted

        result = self._assistant.answer(turn, redact_data=redact_data if flags.redact else None)
        if result.data_flagged:
            return self._refuse(request, "data", result.data_flagged)
        raw = result.reply
        system_prompt = self._assistant.system_prompt(request.customer)
        if flags.output_guard:
            verdict = self._output.check(request.customer, raw, system_prompt)
            if verdict.blocked:
                return self._refuse(request, "output", verdict.reasons, raw, result.tool_called)
        allowed = {p: v for p, v in data_mapping.items() if p in mapping or v in customer_values}
        final, scrubbed = scrub(restore(raw, allowed)) if flags.redact else (raw, [])
        LOG.info("served", extra={"stage": "served", "tool_called": result.tool_called, "seed": request.seed})
        return Response(final, False, None, (), raw, result.tool_called, tuple(scrubbed))

    def _refuse(
        self, request: Request, stage: str, reasons: tuple[str, ...], raw: str = "", tool_called: bool = False
    ) -> Response:
        LOG.info("blocked", extra={"stage": stage, "reasons": list(reasons), "seed": request.seed})
        return Response(REFUSAL, True, stage, reasons, raw, tool_called, ())
