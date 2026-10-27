"""Command-line entry point: one program, one sub-command per step of the lesson."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from guard_redteam.application.evidence import comparison_table, open_attacks
from guard_redteam.application.gate import evaluate_gate, recorded_from
from guard_redteam.application.suites import (
    BenignSummary,
    CaseRun,
    FamilyRate,
    benign_summary,
    confusion,
    family_rates,
    run_attacks,
    run_benign,
)
from guard_redteam.domain.redaction import PATTERNS
from guard_redteam.infrastructure.capture import CapturingChatModel, LogCapture
from guard_redteam.infrastructure.data import load_rows
from guard_redteam.infrastructure.env import ConfigError, process_env
from guard_redteam.infrastructure.logging_setup import configure_logging
from guard_redteam.infrastructure.reports import dump_json, dump_jsonl, load_json
from guard_redteam.interfaces.wiring import WEAKENINGS, Services, build_services

LOG = logging.getLogger("guard_redteam")
# The project folder holds data/, prompts/ and the fixtures; an installed copy (the Docker image) sets PROJECT_ROOT.
ROOT = Path(os.environ.get("PROJECT_ROOT") or Path(__file__).resolve().parents[3])


def _suites(s: Services, guarded: bool, weaken: str | None = None) -> tuple[list[CaseRun], list[CaseRun]]:
    pipeline = s.pipeline(guarded, weaken)
    runs = s.settings.runs
    attacks = run_attacks(s.attacks, pipeline, s.canary, s.orders.own_values, runs, s.mapper)
    benign = run_benign(s.benign, pipeline, s.orders.own_values, runs, s.mapper)
    return attacks, benign


def _summary(s: Services, attacks: list[CaseRun], benign: list[CaseRun]) -> dict[str, Any]:
    return {
        "runs": s.settings.runs,
        "families": family_rates(attacks, s.settings.runs),
        "benign": benign_summary(benign, s.false_block_limit),
        "input_guard_confusion": confusion(attacks, benign),
    }


def _write_side(s: Services, name: str, attacks: list[CaseRun], benign: list[CaseRun]) -> dict[str, Any]:
    out = s.settings.reports_dir
    dump_jsonl(out / f"{name}_attacks.jsonl", attacks)
    dump_jsonl(out / f"{name}_benign.jsonl", benign)
    summary = _summary(s, attacks, benign)
    dump_json(out / f"{name}.json", summary)
    return summary


def _print_side(name: str, summary: dict[str, Any], limit: float) -> None:
    for family, f in summary["families"].items():
        r = f.rate
        print(
            f"{name:9} {family:19} attack success {r.successes}/{r.trials} = {r.value:.1%}  per run {list(f.per_run)}"
        )
    b = summary["benign"]
    fb, risky = b.false_blocks, b.risky_false_blocks
    print(
        f"{name:9} false blocks {fb.successes}/{fb.trials} = {fb.value:.1%} (limit {limit:.0%}); "
        f"risky-looking {risky.successes}/{risky.trials}"
    )


def cmd_baseline(s: Services) -> None:
    """Step 1: both suites against the bare assistant."""
    attacks, benign = _suites(s, guarded=False)
    _print_side("bare", _write_side(s, "baseline", attacks, benign), s.false_block_limit)


def cmd_guarded(s: Services) -> None:
    """Steps 2 to 4: both suites against the guarded assistant."""
    attacks, benign = _suites(s, guarded=True)
    summary = _write_side(s, "guarded", attacks, benign)
    _print_side("guarded", summary, s.false_block_limit)
    print(f"input guard confusion matrix over all cases and runs: {summary['input_guard_confusion']}")
    risky = sorted({r.case_id: None for r in benign if r.risky and r.blocked})
    print(f"false blocks among the risky-looking benign questions, by case id: {risky or 'none'}")


def _load_side(s: Services, name: str) -> tuple[list[CaseRun], list[CaseRun]]:
    out = s.settings.reports_dir

    def rows(kind: str) -> list[CaseRun]:
        return [
            CaseRun(**{**r, "reasons": tuple(r["reasons"]), "unresolved": tuple(r["unresolved"])})
            for r in load_rows(out / f"{name}_{kind}.jsonl")
        ]

    return rows("attacks"), rows("benign")


def cmd_compare(s: Services) -> None:
    """Step 5: the before-and-after table."""
    runs = s.settings.runs
    before_a, before_b = _load_side(s, "baseline")
    after_a, after_b = _load_side(s, "guarded")
    before, after = family_rates(before_a, runs), family_rates(after_a, runs)
    bb, ab = benign_summary(before_b, s.false_block_limit), benign_summary(after_b, s.false_block_limit)
    table = comparison_table(before, after, bb, ab, s.false_block_limit, runs)
    dump_json(
        s.settings.reports_dir / "comparison.json",
        {
            "before": before,
            "after": after,
            "benign_before": bb,
            "benign_after": ab,
            "false_block_limit": s.false_block_limit,
        },
    )
    (s.settings.reports_dir / "REPORT.md").write_text(
        "# Guardrails and red team: results\n\n" + table, encoding="utf-8"
    )
    print(table)


def cmd_scan(s: Services) -> None:
    """Step 2: no planted raw value reaches a captured model request or a log line."""
    capture = CapturingChatModel(s.model)
    handler = LogCapture()
    root = logging.getLogger()
    root.addHandler(handler)
    try:
        pipeline = s.pipeline(True, model=capture)
        rows = run_benign(s.benign, pipeline, s.orders.own_values, s.settings.runs, s.mapper)
    finally:
        root.removeHandler(handler)
    planted = sorted(
        {m.strip(" .,;") for case in s.benign for pattern in PATTERNS.values() for m in pattern.findall(case.message)}
    )
    haystacks = [*capture.requests, *handler.lines]
    leaks = [
        {"value": v, "occurrences": sum(h.count(v) for h in haystacks)}
        for v in planted
        if any(v in h for h in haystacks)
    ]
    result = {
        "planted_values": planted,
        "model_requests_scanned": len(capture.requests),
        "log_lines_scanned": len(handler.lines),
        "leaks": leaks,
        "replies_with_unresolved_placeholder": sum(1 for r in rows if r.unresolved),
    }
    dump_json(s.settings.reports_dir / "redaction_scan.json", result)
    print(
        f"redaction scan: {len(planted)} planted values, {len(capture.requests)} requests, "
        f"{len(handler.lines)} log lines, leaks: {len(leaks)}, unresolved placeholders in replies: "
        f"{result['replies_with_unresolved_placeholder']}"
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cmd_evidence(s: Services) -> int:
    """Step 6: build evidence/ and fail if an attack that still works has no recorded decision."""
    runs = s.settings.runs
    out, ev = s.settings.reports_dir, s.settings.evidence_dir
    ev.mkdir(parents=True, exist_ok=True)
    (ev / "results").mkdir(exist_ok=True)
    for name in ("baseline_attacks", "baseline_benign", "guarded_attacks", "guarded_benign"):
        (ev / "results" / f"{name}.jsonl").write_text(
            (out / f"{name}.jsonl").read_text(encoding="utf-8"), encoding="utf-8"
        )
    before_a, before_b = _load_side(s, "baseline")
    after_a, after_b = _load_side(s, "guarded")
    before, after = family_rates(before_a, runs), family_rates(after_a, runs)
    bb, ab = benign_summary(before_b, s.false_block_limit), benign_summary(after_b, s.false_block_limit)
    (ev / "table.md").write_text(comparison_table(before, after, bb, ab, s.false_block_limit, runs), encoding="utf-8")
    dump_json(ev / "recorded_rates.json", recorded_from(after, ab, s.false_block_limit))
    decisions_path = s.settings.evals_dir / "decisions.json"
    decisions = json.loads(decisions_path.read_text(encoding="utf-8")) if decisions_path.exists() else {}
    open_rows, undecided = open_attacks(after_a, decisions)
    dump_json(ev / "open_attacks.json", open_rows)
    files = {
        **{f"data/{p.name}": _sha256(p) for p in sorted(s.settings.data_dir.glob("*.jsonl"))},
        "data/canary.txt": _sha256(s.settings.data_dir / "canary.txt"),
        **{f"prompts/{p.name}": _sha256(p) for p in sorted(s.settings.prompts_dir.glob("*.md"))},
        "evals/limits.json": _sha256(s.settings.evals_dir / "limits.json"),
    }
    fixtures = sorted(s.settings.fixtures_dir.glob("*.jsonl"))
    manifest = {
        "assistant_model": s.settings.assistant_model,
        "guard_model": s.settings.guard_model,
        "temperature": s.settings.temperature,
        "runs": runs,
        "guard_version": "guard.v1",
        "hashes": files,
        "fixtures": {p.name: _sha256(p) for p in fixtures},
        "reproduce": "make run   (offline, from tests/fixtures); then make evidence",
    }
    dump_json(ev / "MANIFEST.json", manifest)
    (ev / "REPRODUCE.md").write_text(
        "# Reproduce\n\n```bash\nmake up && make run\n```\n\n"
        "From a clean checkout this rebuilds `reports/` and `evidence/` offline from the recorded fixtures; "
        "`table.md` must match the committed one exactly.\n",
        encoding="utf-8",
    )
    print(f"evidence pack written to {ev}; attacks still working: {len(open_rows)}; undecided: {undecided or 'none'}")
    return 1 if undecided else 0


def cmd_gate(s: Services, weaken: str | None) -> int:
    """Step 7: run the guarded suites (optionally with a planted weakening) and compare with the recorded rates."""
    attacks, benign = _suites(s, guarded=True, weaken=weaken)
    recorded = load_json(s.settings.evidence_dir / "recorded_rates.json")
    families: dict[str, FamilyRate] = family_rates(attacks, s.settings.runs)
    summary: BenignSummary = benign_summary(benign, s.false_block_limit)
    result = evaluate_gate(families, summary, recorded, s.false_block_limit)
    label = f" (planted weakening: {weaken})" if weaken else ""
    if result.passed:
        print(
            f"GATE PASSED{label}: no family is above its recorded attack success and false blocks are within the limit"
        )
        return 0
    print(f"GATE FAILED{label}:")
    for failure in result.failures:
        print(f"  - {failure}")
    return 1


def cmd_health(s: Services) -> int:
    """Exit 0 when the suites and prompts are in place."""
    s.prompts.get("assistant.v1")
    s.prompts.get("input_guard.v2")
    ok = len(s.attacks) == 100 and len(s.benign) == 100
    print(f"attacks={len(s.attacks)} benign={len(s.benign)} canary_set={bool(s.canary)} -> {'ok' if ok else 'FAILED'}")
    return 0 if ok else 1


def cmd_parity(java: Path, python: Path) -> int:
    """The Java results must equal the Python results (numbers to 1e-6)."""
    mismatches: list[str] = []
    for name in ("baseline.json", "guarded.json", "comparison.json"):
        _diff(load_json(python / name), load_json(java / name), name, mismatches)
    for mismatch in mismatches[:20]:
        print("MISMATCH", mismatch)
    verdict = "OK, the Java results equal the Python results" if not mismatches else f"{len(mismatches)} differences"
    print("parity:", verdict)
    return 1 if mismatches else 0


def _diff(a: Any, b: Any, path: str, out: list[str]) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append(f"{path}.{key} is missing on one side")
            else:
                _diff(a[key], b[key], f"{path}.{key}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path} has length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b, strict=False)):
            _diff(x, y, f"{path}[{i}]", out)
    elif isinstance(a, int | float) and isinstance(b, int | float) and not isinstance(a, bool):
        if abs(a - b) > 1e-6:
            out.append(f"{path}: {a} vs {b}")
    elif a != b:
        out.append(f"{path}: {a!r} vs {b!r}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run one sub-command; returns the process exit code."""
    parser = argparse.ArgumentParser(prog="guard-redteam", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("baseline", "guarded", "compare", "scan", "evidence", "all", "health"):
        sub.add_parser(name)
    gate = sub.add_parser("gate")
    gate.add_argument("--weaken", choices=WEAKENINGS, default=None)
    parity = sub.add_parser("parity")
    parity.add_argument("--java", type=Path, required=True)
    parity.add_argument("--python", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "parity":
        return cmd_parity(args.java, args.python)
    env = dict(process_env())
    configure_logging(env.get("LOG_LEVEL", "INFO"))
    try:
        services = build_services(env, ROOT)
        if args.command == "health":
            return cmd_health(services)
        if args.command == "gate":
            return cmd_gate(services, args.weaken)
        steps = {
            "baseline": cmd_baseline,
            "guarded": cmd_guarded,
            "scan": cmd_scan,
            "compare": cmd_compare,
        }
        for step in list(steps) if args.command == "all" else [args.command]:
            if step == "evidence":
                return cmd_evidence(services)
            steps[step](services)
        if args.command == "all":
            code = cmd_evidence(services)
            return max(code, cmd_gate(services, None))
    except ConfigError as error:
        print(f"configuration error: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        LOG.warning("interrupted; exchanges already recorded are kept, rerun to resume")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
