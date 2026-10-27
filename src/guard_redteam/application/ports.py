"""Ports: what the application needs from the outside world, written as protocols."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol, TypeVar

from guard_redteam.domain.llm import ChatRequest, ChatResponse


class ChatModel(Protocol):
    """One chat-completion call. Adapters raise RetryableModelError or PermanentModelError on failure."""

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Send the request and return the finished response."""
        ...


class Clock(Protocol):
    """Time, replaceable so that tests and simulations are deterministic."""

    def monotonic(self) -> float:
        """Seconds from an arbitrary fixed start; never goes backward."""
        ...

    def sleep(self, seconds: float) -> None:
        """Wait (a manual clock just advances)."""
        ...


class PromptStore(Protocol):
    """Versioned prompt templates, looked up by name such as `assistant.v1`."""

    def get(self, name: str) -> str:
        """The template text."""
        ...


class OrderLookup(Protocol):
    """The read-only `find_order` tool: the record of any order, or None."""

    def find(self, order_id: str, note: str | None = None) -> str | None:
        """The rendered record; `note` replaces the order's note for this call (a planted indirect injection)."""
        ...

    def owner_of(self, order_id: str) -> str | None:
        """The customer id that owns the order."""
        ...


class Classifier(Protocol):
    """A small model that labels a message ALLOW or BLOCK."""

    def classify(self, message: str) -> str:
        """`allow` or `block`."""
        ...


T = TypeVar("T")
R = TypeVar("R")


class Mapper(Protocol):
    """Apply a function to items, possibly on several threads, returning results in input order."""

    def __call__(self, function: Callable[[T], R], items: Sequence[T], /) -> list[R]:
        """Map."""
        ...
