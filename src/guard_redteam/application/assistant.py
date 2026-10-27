"""The sample support assistant: a system prompt with a canary, and a read-only `find_order` tool.

The 1.5-billion-parameter model used here did not reliably ask for a tool (in the first trial it ignored the
`TOOL find_order` protocol in four of five attempts), so the runtime plays the tool's part: when the customer mentions
an order id, the runtime calls `find_order` and puts the record in the prompt between [TOOL_RESULT] markers, the way an
agent framework does after a model's tool request. The record is outside data, and so a place an injection can hide.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from guard_redteam.application.ports import ChatModel, OrderLookup, PromptStore
from guard_redteam.application.templates import render
from guard_redteam.domain.llm import ChatRequest, Message
from guard_redteam.domain.rules import wrap_data

ORDER_ID = re.compile(r"\bPR-\d+\b")
DataScan = Callable[[str], list[str]]


@dataclass(frozen=True)
class AssistantTurn:
    """One request to the assistant. The note and the help page are the outside data a case may poison."""

    customer: str
    message: str
    seed: int
    help_page: str | None = None
    note_order: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class AssistantResult:
    """What the assistant answered, or why it never answered."""

    reply: str
    tool_called: bool
    data: tuple[str, ...] = ()
    data_flagged: tuple[str, ...] = ()
    tokens: int = 0


class SupportAssistant:
    """Answers with the model; looks up the orders a customer mentions; treats help pages and tool results as data."""

    def __init__(
        self,
        model: ChatModel,
        prompts: PromptStore,
        model_id: str,
        canary: str,
        orders: OrderLookup,
        temperature: float,
        data_scan: DataScan | None = None,
        max_tokens: int = 200,
    ) -> None:
        self._model = model
        self._prompts = prompts
        self._model_id = model_id
        self._canary = canary
        self._orders = orders
        self._temperature = temperature
        self._data_scan = data_scan
        self._max_tokens = max_tokens

    def system_prompt(self, customer: str) -> str:
        """The system prompt for a signed-in customer (it contains the canary)."""
        return render(self._prompts.get("assistant.v1"), customer=customer, canary=self._canary)

    def answer(self, turn: AssistantTurn, *, redact_data: Callable[[str], str] | None = None) -> AssistantResult:
        """Run one turn. `redact_data` rewrites outside data before the model sees it. If a data scan is set and finds
        something in a help page or a tool result, the turn stops with `data_flagged` set and no model call."""
        blocks: list[str] = []
        shown: list[str] = []
        if turn.help_page:
            flagged = self._data_scan(turn.help_page) if self._data_scan else []
            if flagged:
                return AssistantResult("", False, (turn.help_page,), tuple(flagged))
            page = redact_data(turn.help_page) if redact_data else turn.help_page
            shown.append(page)
            blocks.append(wrap_data("HELP_PAGE", page))
        tool_called = False
        for order_id in dict.fromkeys(ORDER_ID.findall(turn.message)):
            record = self._orders.find(order_id, turn.note if turn.note_order == order_id else None)
            record = record or f"no order {order_id}"
            tool_called = True
            flagged = self._data_scan(record) if self._data_scan else []
            if flagged:
                return AssistantResult("", True, (*shown, record), tuple(flagged))
            record = redact_data(record) if redact_data else record
            shown.append(record)
            blocks.append(wrap_data("TOOL_RESULT", record))
        user_text = "\n".join([*blocks, turn.message]) if blocks else turn.message
        messages = (Message("system", self.system_prompt(turn.customer)), Message("user", user_text))
        response = self._model.complete(
            ChatRequest(self._model_id, messages, self._temperature, self._max_tokens, turn.seed)
        )
        return AssistantResult(response.text.strip(), tool_called, tuple(shown), (), response.usage.total)
