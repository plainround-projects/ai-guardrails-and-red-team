"""The sample shop: customers, orders and the record the read-only `find_order` tool returns."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    """A signed-in customer."""

    customer_id: str
    name: str
    email: str
    phone: str


@dataclass(frozen=True)
class Order:
    """An order. `note` is free text written by whoever placed it, which makes it an injection channel."""

    order_id: str
    customer_id: str
    status: str
    items: tuple[str, ...]
    total_cents: int
    ship_to: str
    tracking: str
    note: str = ""


def render_record(order: Order, customer: Customer, note: str | None = None) -> str:
    """The text the tool returns: the whole record, whoever owns it (the tool is read-only but not scoped)."""
    total = f"${order.total_cents // 100}.{order.total_cents % 100:02d}"
    shown_note = order.note if note is None else note
    return (
        f"Order {order.order_id} | customer: {customer.customer_id} | email: {customer.email} | "
        f"status: {order.status} | "
        f"items: {', '.join(order.items)} | total: {total} | ship to: {order.ship_to} | tracking: {order.tracking} | "
        f"note: {shown_note or 'none'}"
    )
