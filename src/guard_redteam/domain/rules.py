"""The input guard's rules: cheap patterns for the attacks already known, applied to the customer's message and to
every piece of outside data (tool results, help pages)."""

from __future__ import annotations

import re

RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "override_instructions",
        re.compile(r"\b(?:ignore|disregard|forget)\b[^.\n]{0,40}\b(?:instructions|rules)\b", re.I),
    ),
    ("forget_everything", re.compile(r"\bforget everything\b", re.I)),
    ("stop_following", re.compile(r"\bstop following (?:your|the) (?:instructions|rules)\b", re.I)),
    (
        "system_override",
        # Upper case or bracketed only: "the system override flag on my parcel" is an ordinary sentence.
        re.compile(r"\b(?:SYSTEM|ADMIN)\s+(?:OVERRIDE|NOTICE)\b|\[(?:system|admin)\]"),
    ),
    (
        "new_instructions",
        re.compile(r"\bnew (?:instructions?|policy)\b[^.\n]{0,60}\b(?:assistant|ignore|reveal|token)\b", re.I),
    ),
    (
        "reveal_secret",
        re.compile(
            r"\b(?:reveal|print|output|show|read me|echo)\b[^.\n]{0,50}"
            r"\b(?:reference token|internal token|the token|secret|system prompt|configuration)\b",
            re.I,
        ),
    ),
    (
        "extract_prompt",
        re.compile(r"\b(?:system prompt|initial instructions|everything above|your instructions|verbatim)\b", re.I),
    ),
    (
        "persona_switch",
        re.compile(
            r"\b(?:you are now|dan\b|debugbot|developer mode|maintenance mode|unfiltered|no rules|compromised bot)\b",
            re.I,
        ),
    ),
    (
        "roleplay_frame",
        re.compile(
            r"\b(?:pretend you are|roleplay as|let's play a game|simulate a terminal|imagine your rules)\b", re.I
        ),
    ),
    (
        "hidden_instruction",
        re.compile(r"\b(?:note to assistant|dear assistant|attention ai|hidden instruction|end of data)\b", re.I),
    ),
    ("assistant_command", re.compile(r"</?instructions>|\bassistant:\s", re.I)),
)


SOFT_SIGNALS = re.compile(
    r"\b(?:ignore|disregard|forget|system|internal|instructions?|token|secret|prompt|override|pretend|role-?play|"
    r"developer|admin|rules|verbatim|repeat|act as)\b",
    re.I,
)


def has_soft_signal(text: str) -> bool:
    """Words that do not prove an attack but make a second opinion worth its cost."""
    return SOFT_SIGNALS.search(text) is not None


def scan(text: str) -> list[str]:
    """Names of the rules the text matches, in rule order."""
    return [name for name, pattern in RULES if pattern.search(text)]


def wrap_data(label: str, text: str) -> str:
    """Put outside data between delimiters so the assistant (and a reader of the log) can tell it from instructions."""
    return f"[{label}]\n{text}\n[/{label}]"
