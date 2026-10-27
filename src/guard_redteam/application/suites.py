"""Running the two suites through a pipeline, and the rates they produce."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from guard_redteam.application.pipeline import Pipeline, Request
from guard_redteam.application.ports import Mapper
from guard_redteam.domain.cases import AttackCase, BenignCase, Family
from guard_redteam.domain.effects import attack_effect
from guard_redteam.domain.metrics import Rate, rate

OwnValues = Callable[[str], tuple[str, ...]]


@dataclass(frozen=True)
class CaseRun:
    """One case in one run. For an attack, `succeeded` and `evidence` say whether and how it worked; for a benign
    question, `blocked` is a false block."""

    case_id: str
    kind: str
    family: str
    risky: bool
    run: int
    succeeded: bool
    evidence: str
    blocked: bool
    stage: str
    reasons: tuple[str, ...]
    tool_called: bool
    unresolved: tuple[str, ...]


def run_attacks(
    cases: Sequence[AttackCase], pipeline: Pipeline, canary: str, own_values: OwnValues, runs: int, mapper: Mapper
) -> list[CaseRun]:
    """Every attack, `runs` times (the run number is the decoding seed)."""
    jobs = [(case, run) for case in cases for run in range(1, runs + 1)]

    def one(job: tuple[AttackCase, int]) -> CaseRun:
        case, run = job
        request = Request(case.customer, case.message, run, case.help_page, case.note_order, case.note)
        response = pipeline.respond(request, own_values(case.customer))
        effect = attack_effect(case, response.reply, canary, pipeline.system_prompt(case.customer))
        return CaseRun(
            case.case_id,
            "attack",
            case.family.value,
            False,
            run,
            effect is not None,
            effect or "none",
            response.blocked,
            response.stage or "",
            response.reasons,
            response.tool_called,
            response.unresolved,
        )

    return mapper(one, jobs)


def run_benign(
    cases: Sequence[BenignCase], pipeline: Pipeline, own_values: OwnValues, runs: int, mapper: Mapper
) -> list[CaseRun]:
    """Every benign question, `runs` times."""
    jobs = [(case, run) for case in cases for run in range(1, runs + 1)]

    def one(job: tuple[BenignCase, int]) -> CaseRun:
        case, run = job
        response = pipeline.respond(Request(case.customer, case.message, run), own_values(case.customer))
        return CaseRun(
            case.case_id,
            "benign",
            "benign",
            case.risky,
            run,
            False,
            "none",
            response.blocked,
            response.stage or "",
            response.reasons,
            response.tool_called,
            response.unresolved,
        )

    return mapper(one, jobs)


@dataclass(frozen=True)
class FamilyRate:
    """Attack success for one family over all runs, with the per-run counts that show the run-to-run spread."""

    rate: Rate
    per_run: tuple[int, ...]
    succeeding_cases: tuple[str, ...]
    blocked: int


def family_rates(rows: Sequence[CaseRun], runs: int) -> dict[str, FamilyRate]:
    """Attack success per family."""
    out: dict[str, FamilyRate] = {}
    for family in Family:
        subset = [r for r in rows if r.family == family.value]
        wins = [r for r in subset if r.succeeded]
        out[family.value] = FamilyRate(
            rate(len(wins), len(subset)),
            tuple(sum(1 for r in wins if r.run == run) for run in range(1, runs + 1)),
            tuple(sorted({r.case_id for r in wins})),
            sum(1 for r in subset if r.blocked),
        )
    return out


@dataclass(frozen=True)
class BenignSummary:
    """False blocks over all runs, the risky-looking ones by case id, and replies with an unresolved placeholder."""

    false_blocks: Rate
    risky_false_blocks: Rate
    blocked_cases: dict[str, int]
    unresolved_replies: int
    within_limit: bool


def benign_summary(rows: Sequence[CaseRun], limit: float) -> BenignSummary:
    """Summarize a benign run against the false-block limit written down in advance."""
    blocked = [r for r in rows if r.blocked]
    risky = [r for r in rows if r.risky]
    cases: dict[str, int] = {}
    for r in blocked:
        cases[r.case_id] = cases.get(r.case_id, 0) + 1
    overall = rate(len(blocked), len(rows))
    return BenignSummary(
        overall,
        rate(sum(1 for r in risky if r.blocked), len(risky)),
        dict(sorted(cases.items())),
        sum(1 for r in rows if r.unresolved),
        overall.value <= limit,
    )


def confusion(attack_rows: Sequence[CaseRun], benign_rows: Sequence[CaseRun]) -> dict[str, Any]:
    """The input guard's confusion matrix over all 200 cases and all runs: attack/benign against blocked/allowed at the
    input stage (a case blocked later, by the data scan or the output guard, counts as allowed here)."""

    def at_input(r: CaseRun) -> bool:
        return r.blocked and r.stage == "input"

    return {
        "attack_blocked_at_input": sum(1 for r in attack_rows if at_input(r)),
        "attack_allowed_by_input": sum(1 for r in attack_rows if not at_input(r)),
        "benign_blocked_at_input": sum(1 for r in benign_rows if at_input(r)),
        "benign_allowed_by_input": sum(1 for r in benign_rows if not at_input(r)),
    }
