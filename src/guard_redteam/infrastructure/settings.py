"""Settings from the environment, validated once at start-up."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from guard_redteam.infrastructure.env import read_float, read_int, read_str


@dataclass(frozen=True)
class Settings:
    """Everything configurable about a run."""

    assistant_model: str
    guard_model: str
    temperature: float
    runs: int
    workers: int
    log_level: str
    data_dir: Path
    prompts_dir: Path
    fixtures_dir: Path
    reports_dir: Path
    evidence_dir: Path
    evals_dir: Path

    @classmethod
    def from_env(cls, env: Mapping[str, str], root: Path) -> Settings:
        """Read and validate; raises ConfigError on a bad value."""
        return cls(
            assistant_model=read_str(env, "ASSISTANT_MODEL", "qwen2.5:1.5b"),
            guard_model=read_str(env, "GUARD_MODEL", "qwen2.5:1.5b"),
            temperature=read_float(env, "TEMPERATURE", 0.7),
            runs=read_int(env, "RUNS", 3, minimum=1),
            workers=read_int(env, "WORKERS", 1, minimum=1),
            log_level=read_str(env, "LOG_LEVEL", "INFO"),
            data_dir=root / "data",
            prompts_dir=root / "prompts",
            fixtures_dir=Path(read_str(env, "FIXTURES_DIR", str(root / "tests" / "fixtures"))),
            reports_dir=Path(read_str(env, "REPORTS_DIR", str(root / "reports"))),
            evidence_dir=Path(read_str(env, "EVIDENCE_DIR", str(root / "evidence"))),
            evals_dir=root / "evals",
        )
