import json
import logging
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import pytest

from guard_redteam.domain.cases import Family
from guard_redteam.infrastructure.capture import CapturingChatModel, LogCapture
from guard_redteam.infrastructure.clock import ManualClock, SystemClock
from guard_redteam.infrastructure.data import (
    InMemoryOrders,
    load_attacks,
    load_benign,
    load_canary,
    load_customers,
    load_orders,
    load_rows,
)
from guard_redteam.infrastructure.env import ConfigError, read_float, read_int, read_str
from guard_redteam.infrastructure.logging_setup import JsonFormatter, configure_logging
from guard_redteam.infrastructure.parallel import thread_mapper
from guard_redteam.infrastructure.prompts import FilePromptStore
from guard_redteam.infrastructure.reports import dump_json, dump_jsonl, load_json, to_jsonable
from guard_redteam.infrastructure.settings import Settings

ROOT = Path(__file__).resolve().parents[3]


def test_settings_have_validated_defaults_and_overrides(tmp_path: Path):
    defaults = Settings.from_env({}, tmp_path)
    assert defaults.runs == 3 and defaults.temperature == 0.7 and defaults.reports_dir == tmp_path / "reports"
    assert defaults.assistant_model == "qwen2.5:1.5b" and defaults.evidence_dir == tmp_path / "evidence"
    custom = Settings.from_env(
        {"RUNS": "5", "REPORTS_DIR": "/x", "ASSISTANT_MODEL": "m", "TEMPERATURE": "0.2"}, tmp_path
    )
    assert (
        custom.runs == 5
        and custom.reports_dir == Path("/x")
        and custom.assistant_model == "m"
        and custom.temperature == 0.2
    )
    with pytest.raises(ConfigError, match="at least"):
        Settings.from_env({"RUNS": "0"}, tmp_path)
    with pytest.raises(ConfigError, match="integer"):
        Settings.from_env({"WORKERS": "many"}, tmp_path)


def test_env_readers_validate():
    assert read_str({"A": " x "}, "A") == "x" and read_str({}, "A", "d") == "d"
    with pytest.raises(ConfigError, match="required"):
        read_str({}, "A")
    assert read_float({"F": "1.5"}, "F", 0.0) == 1.5 and read_float({}, "F", 2.0) == 2.0
    with pytest.raises(ConfigError, match="number"):
        read_float({"F": "x"}, "F", 0.0)
    with pytest.raises(ConfigError, match="at least"):
        read_float({"F": "-1"}, "F", 0.0)
    assert read_int({}, "I", 3) == 3


def test_prompt_store_reads_a_file_without_its_trailing_newline(tmp_path: Path):
    (tmp_path / "a.v1.md").write_text("hello {{x}}\n\n")
    assert FilePromptStore(tmp_path).get("a.v1") == "hello {{x}}"
    with pytest.raises(FileNotFoundError, match="nope"):
        FilePromptStore(tmp_path).get("nope")


@pytest.mark.parametrize("workers", [1, 3])
def test_thread_mapper_keeps_input_order(workers):
    assert thread_mapper(workers)(lambda x: x * 2, list(range(20))) == [x * 2 for x in range(20)]


class Color(StrEnum):
    RED = "red"


@dataclass(frozen=True)
class Thing:
    color: Color
    values: tuple[float, ...]
    ratio: float


def test_reports_serialize_dataclasses_enums_and_infinity(tmp_path: Path):
    value = {"t": Thing(Color.RED, (1.23456789, 2.0), float("inf"))}
    assert to_jsonable(value) == {"t": {"color": "red", "values": [1.234568, 2.0], "ratio": None}}
    dump_json(tmp_path / "a" / "x.json", value)
    assert load_json(tmp_path / "a" / "x.json")["t"]["color"] == "red"
    dump_jsonl(tmp_path / "rows.jsonl", [{"b": 1}, {"a": 2}])
    assert [json.loads(line) for line in (tmp_path / "rows.jsonl").read_text().splitlines()] == [{"b": 1}, {"a": 2}]


def test_json_log_lines_carry_extra_fields_and_no_prompt_text(capsys):
    configure_logging("INFO")
    configure_logging("INFO")
    logging.getLogger("t").info("call finished", extra={"model": "m", "tokens": 7})
    root = logging.getLogger()
    assert len([h for h in root.handlers if getattr(h, "_json_handler", False)]) == 1
    line = json.loads(capsys.readouterr().err.strip().splitlines()[-1])
    assert line["msg"] == "call finished" and line["model"] == "m" and line["tokens"] == 7 and line["level"] == "INFO"
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        record = logging.getLogger("t").makeRecord("t", logging.ERROR, "f", 1, "bad", (), logging.sys.exc_info())
    assert "RuntimeError" in json.loads(JsonFormatter().format(record))["exc"]


def test_clocks():
    clock = ManualClock(5.0)
    clock.sleep(2.5)
    assert clock.monotonic() == 7.5
    with pytest.raises(ValueError, match="backward"):
        clock.advance(-1)
    real = SystemClock()
    before = real.monotonic()
    real.sleep(0)
    real.sleep(0.001)
    assert real.monotonic() >= before


def test_the_committed_suites_and_shop_load():
    data = ROOT / "data"
    attacks, benign = load_attacks(data), load_benign(data)
    assert len(attacks) == 100 and len(benign) == 100 and sum(b.risky for b in benign) == 20
    assert {a.family for a in attacks} == set(Family) and all(sum(a.family is f for a in attacks) == 20 for f in Family)
    assert len(load_customers(data)) == 10 and len(load_orders(data)) == 40
    assert load_canary(data) == "CANARY-7Q2X"
    assert load_rows(ROOT / "no-such-file.jsonl") == []


def test_the_order_lookup_is_read_only_and_names_everything_that_belongs_to_someone_else():
    shop = InMemoryOrders(load_orders(ROOT / "data"), load_customers(ROOT / "data"))
    record = shop.find("PR-4401")
    assert record is not None and "customer: alice" in record and "email: alice@example.com" in record
    assert "note: planted" in (shop.find("PR-4401", "planted") or "")
    assert shop.find("PR-0000") is None and shop.owner_of("PR-4405") == "bob" and shop.owner_of("PR-0000") is None
    forbidden = shop.forbidden_for("alice")
    assert "bob@example.com" in forbidden and "PR-4405" in forbidden and "alice@example.com" not in forbidden
    assert shop.own_values("alice") == ("alice@example.com", "+1 415 555 1000")


def test_every_poisoned_case_points_at_an_order_of_its_own_customer():
    data = ROOT / "data"
    shop = InMemoryOrders(load_orders(data), load_customers(data))
    for case in load_attacks(data):
        if case.note_order:
            assert shop.owner_of(case.note_order) == case.customer
        if case.family is Family.CROSS:
            assert any(v in shop.forbidden_for(case.customer) for v in case.leak_values)


def test_the_capture_wrappers_keep_what_leaves_the_process():
    from guard_redteam.domain.llm import ChatRequest, ChatResponse, Message, Usage

    class Echo:
        def complete(self, request, timeout_s=60.0):
            return ChatResponse("ok", Usage(1, 1), request.model)

    wrapped = CapturingChatModel(Echo())
    wrapped.complete(ChatRequest("m", (Message("system", "a"), Message("user", "b"))))
    assert wrapped.requests == ["a\nb"]
    handler = LogCapture()
    log = logging.getLogger("capture-test")
    log.addHandler(handler)
    log.warning("hello", extra={"stage": "input"})
    assert "hello" in handler.lines[0] and "'stage': 'input'" in handler.lines[0]
