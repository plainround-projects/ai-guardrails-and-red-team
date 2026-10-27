"""The input guard (rules first, a small classifier second) and the output guard."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from guard_redteam.application.ports import ChatModel, Classifier, PromptStore
from guard_redteam.application.templates import render
from guard_redteam.domain.llm import ChatRequest, Message
from guard_redteam.domain.output_checks import canary_leaked, foreign_values_in, prompt_overlap
from guard_redteam.domain.rules import has_soft_signal, scan

REFUSAL = (
    "I'm sorry, I can't help with that request. I can help with your own orders and with our returns, refunds, "
    "delivery and cancellation policies."
)


class ModelClassifier:
    """Labels a message `allow` or `block` with a small model and the policy in prompts/input_guard.v2.md."""

    def __init__(self, model: ChatModel, prompts: PromptStore, model_id: str) -> None:
        self._model = model
        self._prompts = prompts
        self._model_id = model_id

    def classify(self, message: str) -> str:
        """`block` only when the model says BLOCK; an unreadable answer is `allow` (the output guard backs it up)."""
        prompt = render(self._prompts.get("input_guard.v2"), message=message)
        request = ChatRequest(self._model_id, (Message("user", prompt),), temperature=0.0, max_tokens=4)
        text = self._model.complete(request).text.upper()
        return "block" if "BLOCK" in text else "allow"


@dataclass(frozen=True)
class InputDecision:
    """The input guard's verdict: allow or block, and which rule or classifier decided."""

    label: str
    reasons: tuple[str, ...] = ()


class InputGuard:
    """Rules first (they cost nothing). The classifier is a second opinion for a message the rules let through that
    contains a soft signal (a word such as "ignore", "system" or "token"); an ordinary message never reaches it."""

    def __init__(self, use_rules: bool = True, classifier: Classifier | None = None) -> None:
        self._use_rules = use_rules
        self._classifier = classifier

    def decide(self, message: str) -> InputDecision:
        """Label a message."""
        if self._use_rules:
            hits = scan(message)
            if hits:
                return InputDecision("block", tuple(hits))
        if self._classifier is not None and has_soft_signal(message) and self._classifier.classify(message) == "block":
            return InputDecision("block", ("classifier",))
        return InputDecision("allow")

    def scan_data(self, text: str) -> list[str]:
        """Rule hits in outside data (a tool result or a help page); data is never sent to the classifier."""
        return scan(text) if self._use_rules else []


@dataclass(frozen=True)
class OutputDecision:
    """The output guard's verdict, with a reason code for every block."""

    blocked: bool
    reasons: tuple[str, ...] = ()


class OutputGuard:
    """Checks a reply before it leaves: the canary, another customer's identifiers, a long prompt overlap."""

    def __init__(
        self,
        canary: str,
        forbidden_for: Callable[[str], Iterable[str]],
        *,
        check_canary: bool = True,
        check_foreign: bool = True,
        check_overlap: bool = True,
    ) -> None:
        self._canary = canary
        self._forbidden_for = forbidden_for
        self._check_canary = check_canary
        self._check_foreign = check_foreign
        self._check_overlap = check_overlap

    def check(self, customer: str, reply: str, system_prompt: str) -> OutputDecision:
        """Reason codes: `canary`, `foreign_identifier`, `prompt_overlap`."""
        reasons: list[str] = []
        if self._check_canary and canary_leaked(reply, self._canary):
            reasons.append("canary")
        if self._check_foreign and foreign_values_in(reply, self._forbidden_for(customer)):
            reasons.append("foreign_identifier")
        if self._check_overlap and prompt_overlap(reply, system_prompt):
            reasons.append("prompt_overlap")
        return OutputDecision(bool(reasons), tuple(reasons))
