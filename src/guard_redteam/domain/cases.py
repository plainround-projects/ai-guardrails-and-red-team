"""The two fixed suites: attacks in five families and benign questions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Family(StrEnum):
    """The five attack families."""

    DIRECT = "direct_injection"
    INDIRECT = "indirect_injection"
    ROLEPLAY = "roleplay"
    CROSS = "cross_customer"
    EXTRACTION = "prompt_extraction"


@dataclass(frozen=True)
class AttackCase:
    """One attack. The optional fields describe where it hides: an order note, a help page, or a target order."""

    case_id: str
    family: Family
    customer: str
    message: str
    note_order: str | None = None
    note: str | None = None
    help_page: str | None = None
    leak_values: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BenignCase:
    """One ordinary question; `risky` marks the ones that look like attacks but are fine."""

    case_id: str
    customer: str
    message: str
    risky: bool
