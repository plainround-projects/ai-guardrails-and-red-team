"""Reading the sample shop and the two suites, and the read-only order lookup built on them."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from guard_redteam.domain.cases import AttackCase, BenignCase, Family
from guard_redteam.domain.shop import Customer, Order, render_record


def _rows(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_customers(data_dir: Path) -> list[Customer]:
    """The ten sample customers."""
    return [Customer(r["customer_id"], r["name"], r["email"], r["phone"]) for r in _rows(data_dir / "customers.jsonl")]


def load_orders(data_dir: Path) -> list[Order]:
    """The forty sample orders."""
    return [
        Order(
            r["order_id"],
            r["customer_id"],
            r["status"],
            tuple(r["items"]),
            r["total_cents"],
            r["ship_to"],
            r["tracking"],
            r["note"],
        )
        for r in _rows(data_dir / "orders.jsonl")
    ]


def load_attacks(data_dir: Path, name: str = "attacks") -> list[AttackCase]:
    """The 100 attacks, 20 in each family (or the 25 held-out ones, with name `heldout_attacks`)."""
    cases = []
    for r in _rows(data_dir / f"{name}.jsonl"):
        override = r.get("note_override") or {}
        cases.append(
            AttackCase(
                r["case_id"],
                Family(r["family"]),
                r["customer"],
                r["message"],
                override.get("order_id"),
                override.get("note"),
                r.get("help_page"),
                tuple(r.get("leak_values", ())),
            )
        )
    return cases


def load_benign(data_dir: Path) -> list[BenignCase]:
    """The 100 benign questions, 20 of them risky-looking."""
    return [BenignCase(r["case_id"], r["customer"], r["message"], r["risky"]) for r in _rows(data_dir / "benign.jsonl")]


def load_canary(data_dir: Path) -> str:
    """The canary string planted in the system prompt."""
    return (data_dir / "canary.txt").read_text(encoding="utf-8").strip()


class InMemoryOrders:
    """The `find_order` tool: read-only, and, like the tool in the lesson, not scoped to the signed-in customer."""

    def __init__(self, orders: list[Order], customers: list[Customer]) -> None:
        self._orders = {o.order_id: o for o in orders}
        self._customers = {c.customer_id: c for c in customers}

    def find(self, order_id: str, note: str | None = None) -> str | None:
        """The record of any order, or None."""
        order = self._orders.get(order_id)
        return None if order is None else render_record(order, self._customers[order.customer_id], note)

    def owner_of(self, order_id: str) -> str | None:
        """The customer who owns an order."""
        order = self._orders.get(order_id)
        return None if order is None else order.customer_id

    def forbidden_for(self, customer_id: str) -> set[str]:
        """Every identifier that belongs to someone else: their emails, phones, order ids and tracking numbers."""
        values: set[str] = set()
        for customer in self._customers.values():
            if customer.customer_id != customer_id:
                values.update({customer.email, customer.phone})
        for order in self._orders.values():
            if order.customer_id != customer_id:
                values.update({order.order_id, order.tracking})
        return values

    def own_values(self, customer_id: str) -> tuple[str, ...]:
        """The signed-in customer's own email and phone."""
        customer = self._customers[customer_id]
        return (customer.email, customer.phone)


def load_rows(path: Path) -> list[dict[str, Any]]:
    """Any JSONL file as dictionaries; an absent file is an empty list."""
    return _rows(path) if path.exists() else []
