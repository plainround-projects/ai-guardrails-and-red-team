"""Two-way redaction: personal values become typed placeholders on the way in; on the way out only this request's own
placeholders are restored. The mapping lives as long as one request."""

from __future__ import annotations

import re

PATTERNS: dict[str, re.Pattern[str]] = {
    "EMAIL": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "CARD": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "PHONE": re.compile(r"\+?\d[\d ()-]{8,}\d"),
}
PLACEHOLDER = re.compile(r"<(?:EMAIL|CARD|PHONE)_\d+>")


def redact(text: str, mapping: dict[str, str] | None = None) -> tuple[str, dict[str, str]]:
    """Swap personal values for typed placeholders; the mapping lives only as long as this request.

    Passing the mapping of an earlier call continues its numbering, so the customer's message and the data fetched for
    it (a tool result) can share one request without two different values getting the same placeholder.
    """
    mapping = {} if mapping is None else mapping
    for label, pattern in PATTERNS.items():

        def swap(match: re.Match[str], label: str = label) -> str:
            placeholder = f"<{label}_{len(mapping) + 1}>"
            mapping[placeholder] = match.group()
            return placeholder

        text = pattern.sub(swap, text)
    return text, mapping


def restore(reply: str, mapping: dict[str, str]) -> str:
    """Put back only this customer's own values; any other placeholder stays redacted."""
    for placeholder, value in mapping.items():
        reply = reply.replace(placeholder, value)
    return reply


def unresolved_placeholders(text: str) -> list[str]:
    """Placeholders still present in a text (after `restore`, these are the ones that were not this request's own)."""
    return PLACEHOLDER.findall(text)


def scrub(text: str) -> tuple[str, list[str]]:
    """Replace any placeholder still in the text (one the model invented, or another request's) with a neutral note,
    and return the text and the placeholders that were replaced. A customer never sees a raw `<EMAIL_2>`."""
    found = PLACEHOLDER.findall(text)
    return PLACEHOLDER.sub(lambda m: f"[{m.group().strip('<>').split('_')[0].lower()} hidden]", text), found
