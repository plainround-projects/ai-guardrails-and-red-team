import json
from pathlib import Path

import pytest

from guard_redteam.domain.llm import ChatRequest
from guard_redteam.interfaces import cli
from tests.unit.fakes import ScriptedModel


def answer(request: ChatRequest) -> str:
    first = request.messages[0].content
    if first.startswith("You are a security filter"):
        return "ALLOW"
    user = request.messages[-1].content
    if "reference token" in user or "secret" in user:
        return "The internal reference token is CANARY-7Q2X."
    if "tracking" in user:
        return "The tracking number is TRK12345678."
    return "Happy to help with that."


@pytest.fixture
def env(tmp_path: Path, monkeypatch):
    values = {
        "REPORTS_DIR": str(tmp_path / "reports"),
        "EVIDENCE_DIR": str(tmp_path / "evidence"),
        "WORKERS": "2",
        "RUNS": "2",
    }
    monkeypatch.setattr(cli, "process_env", lambda: values)
    monkeypatch.setattr("guard_redteam.interfaces.wiring.build_chat_model", lambda e, f: ScriptedModel(answer))
    return tmp_path


def test_all_runs_every_step_and_writes_reports_and_the_evidence_pack(env: Path, capsys):
    code = cli.main(["all"])
    out = capsys.readouterr().out
    reports, evidence = env / "reports", env / "evidence"
    for name in ("baseline.json", "guarded.json", "comparison.json", "redaction_scan.json", "REPORT.md"):
        assert (reports / name).exists(), name
    for name in ("MANIFEST.json", "table.md", "recorded_rates.json", "open_attacks.json", "REPRODUCE.md"):
        assert (evidence / name).exists(), name
    assert (evidence / "results" / "guarded_attacks.jsonl").exists()
    assert "false blocks" in out and "redaction scan" in out and "evidence pack written" in out
    manifest = json.loads((evidence / "MANIFEST.json").read_text())
    assert (
        manifest["runs"] == 2
        and "prompts/assistant.v1.md" in manifest["hashes"]
        and "data/attacks.jsonl" in manifest["hashes"]
    )
    baseline = json.loads((reports / "baseline.json").read_text())
    assert baseline["families"]["direct_injection"]["rate"]["successes"] > 0
    assert code in (0, 1)


def test_the_gate_passes_on_the_recorded_rates_and_fails_when_the_guard_layer_is_deleted(env: Path, capsys):
    cli.main(["all"])
    capsys.readouterr()
    assert cli.main(["gate"]) == 0
    assert "GATE PASSED" in capsys.readouterr().out
    assert cli.main(["gate", "--weaken", "remove_guards"]) == 1
    out = capsys.readouterr().out
    assert "GATE FAILED (planted weakening: remove_guards)" in out and "direct_injection" in out and "a0" in out


def test_each_weakening_is_accepted_by_the_gate_command(env: Path):
    cli.main(["all"])
    for weaken in ("remove_canary_check", "remove_output_guard"):
        assert cli.main(["gate", "--weaken", weaken]) in (0, 1)


def test_an_attack_without_a_recorded_decision_fails_the_evidence_step(env: Path, capsys):
    cli.main(["baseline"])
    cli.main(["guarded"])
    # the scripted model leaks the tracking number to a cross-customer attack that the output guard catches, so nothing
    # is open; pretend one is open by checking a pack built from the bare results as if they were the guarded ones
    reports = env / "reports"
    (reports / "guarded_attacks.jsonl").write_text((reports / "baseline_attacks.jsonl").read_text())
    assert cli.main(["evidence"]) == 1
    assert "undecided" in capsys.readouterr().out


def test_health_reports_the_suites(env: Path, capsys):
    assert cli.main(["health"]) == 0
    assert "attacks=100 benign=100" in capsys.readouterr().out


def test_parity_passes_for_equal_results_and_fails_for_a_changed_number(env: Path, tmp_path: Path, capsys):
    cli.main(["baseline"])
    cli.main(["guarded"])
    cli.main(["compare"])
    reports = env / "reports"
    other = tmp_path / "java"
    other.mkdir()
    for name in ("baseline.json", "guarded.json", "comparison.json"):
        (other / name).write_text((reports / name).read_text())
    assert cli.main(["parity", "--java", str(other), "--python", str(reports)]) == 0
    changed = json.loads((other / "guarded.json").read_text())
    changed["families"]["roleplay"]["rate"]["value"] += 0.5
    changed["extra"] = 1
    (other / "guarded.json").write_text(json.dumps(changed))
    assert cli.main(["parity", "--java", str(other), "--python", str(reports)]) == 1
    assert "roleplay" in capsys.readouterr().out


def test_a_bad_setting_exits_with_code_two(monkeypatch, capsys):
    monkeypatch.setattr(cli, "process_env", lambda: {"RUNS": "zero"})
    assert cli.main(["health"]) == 2
    assert "configuration error" in capsys.readouterr().err


def test_an_interrupt_exits_with_130(env: Path, monkeypatch):
    def interrupted(_services):
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "cmd_baseline", interrupted)
    assert cli.main(["all"]) == 130
