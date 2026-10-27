"""The evidence pack's content: the before-and-after table and the attacks that still work, each with a decision."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from guard_redteam.application.suites import BenignSummary, CaseRun, FamilyRate

DECISIONS = ("fix", "accept", "out_of_scope")


def pct(value: float) -> str:
    """A rate as a percentage with one decimal."""
    return f"{value * 100:.1f}%"


def comparison_table(
    before: dict[str, FamilyRate],
    after: dict[str, FamilyRate],
    benign_before: BenignSummary,
    benign_after: BenignSummary,
    limit: float,
    runs: int,
) -> str:
    """Attack success per family and the false-block rate, before and after, with 95% Wilson intervals."""
    out = [
        "| Family | Cases x runs | Before: bare assistant | After: guard layer | Successes per run after |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name in before:
        b, a = before[name].rate, after[name].rate
        out.append(
            f"| {name} | {b.trials} | {b.successes}/{b.trials} = {pct(b.value)} [{pct(b.low)}, {pct(b.high)}] | "
            f"{a.successes}/{a.trials} = {pct(a.value)} [{pct(a.low)}, {pct(a.high)}] | "
            f"{', '.join(str(n) for n in after[name].per_run)} |"
        )
    fb, fa = benign_before.false_blocks, benign_after.false_blocks
    rb, ra = benign_before.risky_false_blocks, benign_after.risky_false_blocks
    out += [
        "",
        "| Benign suite | Before | After | Limit written in advance | Within the limit |",
        "| --- | --- | --- | --- | --- |",
        f"| False blocks, all 100 questions x {runs} runs | {fb.successes}/{fb.trials} = {pct(fb.value)} | "
        f"{fa.successes}/{fa.trials} = {pct(fa.value)} [{pct(fa.low)}, {pct(fa.high)}] | {pct(limit)} | "
        f"{'yes' if benign_after.within_limit else 'NO'} |",
        f"| False blocks, the 20 risky-looking questions | {rb.successes}/{rb.trials} = {pct(rb.value)} | "
        f"{ra.successes}/{ra.trials} = {pct(ra.value)} [{pct(ra.low)}, {pct(ra.high)}] | | |",
    ]
    return "\n".join(out) + "\n"


def open_attacks(rows: Sequence[CaseRun], decisions: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Attacks that still succeed in at least one guarded run, each with the decision recorded for it. The second
    value lists case ids that have no valid decision yet."""
    by_case: dict[str, list[CaseRun]] = {}
    for row in rows:
        if row.succeeded:
            by_case.setdefault(row.case_id, []).append(row)
    open_rows = []
    undecided = []
    for case_id in sorted(by_case):
        decision = decisions.get(case_id) or {}
        valid = decision.get("decision") in DECISIONS and bool(decision.get("reason"))
        if not valid:
            undecided.append(case_id)
        first = by_case[case_id][0]
        open_rows.append(
            {
                "case_id": case_id,
                "family": first.family,
                "runs_succeeded": sorted(r.run for r in by_case[case_id]),
                "evidence": first.evidence,
                "decision": decision.get("decision", "UNDECIDED"),
                "reason": decision.get("reason", ""),
            }
        )
    return open_rows, undecided
