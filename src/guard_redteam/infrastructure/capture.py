"""Capturing what leaves the process: every model request, and every log line, for the redaction scan."""

from __future__ import annotations

import logging
import threading

from guard_redteam.application.ports import ChatModel
from guard_redteam.domain.llm import ChatRequest, ChatResponse


class CapturingChatModel:
    """Wraps a model and keeps the text of every request it was asked to send."""

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
        with self._guard:
            self.lines.append(f"{record.getMessage()} {extras}")
