"""Rates with Wilson intervals, per family and per run."""

from __future__ import annotations

from dataclasses import dataclass

from guard_redteam.domain.stats import wilson_interval


@dataclass(frozen=True)
class Rate:
    """A proportion, its trial counts and its 95% Wilson interval."""

    successes: int
    trials: int
    value: float
    low: float
    high: float


def rate(successes: int, trials: int) -> Rate:
    """A rate and its interval; zero trials gives value 0 and the whole range."""
    low, high = wilson_interval(successes, trials)
    return Rate(successes, trials, successes / trials if trials else 0.0, low, high)
