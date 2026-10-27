"""Small fakes shared by the unit tests."""

from __future__ import annotations

from collections.abc import Callable

from guard_redteam.application.assistant import SupportAssistant
from guard_redteam.application.guards import InputGuard, ModelClassifier, OutputGuard
from guard_redteam.application.pipeline import GuardFlags, Pipeline
from guard_redteam.domain.llm import ChatRequest, ChatResponse, Usage
from guard_redteam.domain.shop import Customer, Order
from guard_redteam.infrastructure.data import InMemoryOrders

CANARY = "CANARY-7Q2X"
CUSTOMERS = [
    Customer("alice", "Alice", "alice@example.com", "+1 415 555 0101"),
    Customer("bob", "Bob", "bob@example.com", "+1 415 555 0202"),
]
ORDERS = [
    Order("PR-4401", "alice", "shipped", ("Lamp",), 4500, "1 Oak Street, Leeds", "TRK11111111"),
    Order("PR-4405", "bob", "delivered", ("Mug",), 1800, "2 Mill Street, Perth", "TRK22222222"),
]


class ScriptedModel:
    """A chat model whose answer is computed from the request by a function."""

    def __init__(self, answer: Callable[[ChatRequest], str]) -> None:
        self.answer = answer
        self.requests: list[ChatRequest] = []

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        self.requests.append(request)
        return ChatResponse(self.answer(request), Usage(100, 10), request.model, latency_s=0.1)


class DictPrompts:
    def __init__(self) -> None:
        self.templates = {
            "assistant.v1": "SYSTEM for {{customer}} token {{canary}}",
            "input_guard.v2": "CLASSIFY {{message}}",
        }

    def get(self, name: str) -> str:
        return self.templates[name]


def sequential(function, items):
    return [function(item) for item in items]


def orders() -> InMemoryOrders:
    return InMemoryOrders(ORDERS, CUSTOMERS)


def pipeline(model: ScriptedModel, flags: GuardFlags | None = None, check_canary: bool = True) -> Pipeline:
    prompts = DictPrompts()
    shop = orders()
    guard = InputGuard(True, ModelClassifier(model, prompts, "guard-model"))
    flags = GuardFlags() if flags is None else flags
    assistant = SupportAssistant(
        model, prompts, "assistant-model", CANARY, shop, 0.7, guard.scan_data if flags.data_scan else None
    )
    return Pipeline(assistant, guard, OutputGuard(CANARY, shop.forbidden_for, check_canary=check_canary), flags)
