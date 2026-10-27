"""The study replays from the recorded fixtures to the committed results, and the gate catches a planted weakening."""

import json
from pathlib import Path

import pytest

from guard_redteam.interfaces import cli

pytestmark = pytest.mark.e2e

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def env(tmp_path: Path, monkeypatch):
    values = {
        "REPORTS_DIR": str(tmp_path / "reports"),
        "EVIDENCE_DIR": str(tmp_path / "evidence"),
        "LLM_PROVIDER": "recorded",
    }
    monkeypatch.setattr(cli, "process_env", lambda: values)
    return tmp_path


def test_the_whole_study_replays_to_the_committed_results_and_evidence(env: Path):
    assert cli.main(["all"]) == 0
    for name in ("baseline.json", "guarded.json", "comparison.json", "heldout.json", "redaction_scan.json"):
        assert json.loads((env / "reports" / name).read_text()) == json.loads((ROOT / "reports" / name).read_text()), (
            name
        )
    for name in ("table.md", "MANIFEST.json", "recorded_rates.json", "open_attacks.json"):
        assert (env / "evidence" / name).read_text() == (ROOT / "evidence" / name).read_text(), name
    assert (env / "reports" / "REPORT.md").read_text() == (ROOT / "reports" / "REPORT.md").read_text()


def test_the_committed_gate_passes_and_fails_when_the_guard_layer_is_deleted(monkeypatch, capsys):
    values = {
        "EVIDENCE_DIR": str(ROOT / "evidence"),
        "REPORTS_DIR": "/tmp/unused-guard-reports",
        "LLM_PROVIDER": "recorded",
    }
    monkeypatch.setattr(cli, "process_env", lambda: values)
    assert cli.main(["gate"]) == 0
    assert "GATE PASSED" in capsys.readouterr().out
    assert cli.main(["gate", "--weaken", "remove_guards"]) == 1
    out = capsys.readouterr().out
    assert "GATE FAILED (planted weakening: remove_guards)" in out
    for family in ("direct_injection", "cross_customer", "roleplay", "prompt_extraction", "indirect_injection"):
        assert family in out
    assert "cases: a0" in out
    assert cli.main(["gate", "--weaken", "remove_canary_check"]) in (0, 1)
