"""The composition root: build the adapters, the assistant and the guard layer from settings."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from guard_redteam.application.assistant import SupportAssistant
from guard_redteam.application.guards import InputGuard, ModelClassifier, OutputGuard
from guard_redteam.application.pipeline import GuardFlags, Pipeline
from guard_redteam.application.ports import ChatModel, Mapper, PromptStore
from guard_redteam.domain.cases import AttackCase, BenignCase
from guard_redteam.infrastructure.data import (
    InMemoryOrders,
    load_attacks,
    load_benign,
    load_canary,
    load_customers,
    load_orders,
)
from guard_redteam.infrastructure.llm.factory import build_chat_model
from guard_redteam.infrastructure.parallel import thread_mapper
from guard_redteam.infrastructure.prompts import FilePromptStore
from guard_redteam.infrastructure.settings import Settings

WEAKENINGS = ("remove_guards", "remove_canary_check", "remove_output_guard")


@dataclass(frozen=True)
class Services:
    """Everything a command needs."""

    settings: Settings
    attacks: list[AttackCase]
    heldout: list[AttackCase]
    benign: list[BenignCase]
    canary: str
    orders: InMemoryOrders
    prompts: PromptStore
    model: ChatModel
    mapper: Mapper
    false_block_limit: float

    def pipeline(self, guarded: bool, weaken: str | None = None, model: ChatModel | None = None) -> Pipeline:
        """The bare assistant, the guarded assistant, or the guarded assistant with one part removed."""
        chat = model or self.model
        s = self.settings
        classifier = ModelClassifier(chat, self.prompts, s.guard_model)
        input_guard = InputGuard(True, classifier)
        flags = GuardFlags() if guarded else GuardFlags.bare()
        if weaken == "remove_guards":
            flags = GuardFlags.bare()
        elif weaken == "remove_output_guard":
            flags = GuardFlags(output_guard=False)
        assistant = SupportAssistant(
            chat,
            self.prompts,
            s.assistant_model,
            self.canary,
            self.orders,
            s.temperature,
            data_scan=input_guard.scan_data if flags.data_scan else None,
        )
        output_guard = OutputGuard(self.canary, self.orders.forbidden_for, check_canary=weaken != "remove_canary_check")
        return Pipeline(assistant, input_guard, output_guard, flags)


def build_services(env: Mapping[str, str], root: Path) -> Services:
    """Read settings and data, and build the model adapter named by LLM_PROVIDER."""
    import json

    settings = Settings.from_env(env, root)
    data = settings.data_dir
    limits = json.loads((settings.evals_dir / "limits.json").read_text(encoding="utf-8"))
    return Services(
        settings=settings,
        attacks=load_attacks(data),
        heldout=load_attacks(data, "heldout_attacks"),
        benign=load_benign(data),
        canary=load_canary(data),
        orders=InMemoryOrders(load_orders(data), load_customers(data)),
        prompts=FilePromptStore(settings.prompts_dir),
        model=build_chat_model(env, settings.fixtures_dir),
        mapper=thread_mapper(settings.workers),
        false_block_limit=float(limits["false_block_limit"]),
    )
