#!/usr/bin/env python3
"""Calculate and enforce a SkillBench model-session budget."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BudgetPlan:
    case_count: int
    variant_count: int
    repetitions: int
    codex_analysis_sessions: int
    benchmark_sessions: int
    total_model_sessions: int


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be zero or greater")
    return parsed


def make_plan(
    case_count: int,
    variant_count: int,
    repetitions: int,
    codex_analysis_sessions: int,
) -> BudgetPlan:
    benchmark_sessions = case_count * variant_count * repetitions
    return BudgetPlan(
        case_count=case_count,
        variant_count=variant_count,
        repetitions=repetitions,
        codex_analysis_sessions=codex_analysis_sessions,
        benchmark_sessions=benchmark_sessions,
        total_model_sessions=benchmark_sessions + codex_analysis_sessions,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculate SkillBench sessions before launching a real run."
    )
    parser.add_argument("--cases", type=positive_int, default=1)
    parser.add_argument("--variants", type=positive_int, default=2)
    parser.add_argument("--runs", type=positive_int, default=1)
    parser.add_argument(
        "--codex-analysis-sessions", type=nonnegative_int, default=0
    )
    parser.add_argument(
        "--max-sessions",
        type=nonnegative_int,
        help="Exit with status 2 when the plan exceeds this cap.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    plan = make_plan(
        case_count=args.cases,
        variant_count=args.variants,
        repetitions=args.runs,
        codex_analysis_sessions=args.codex_analysis_sessions,
    )

    if args.as_json:
        print(json.dumps(asdict(plan), indent=2, sort_keys=True))
    else:
        print(
            "SkillBench model sessions: "
            f"{plan.total_model_sessions} "
            f"({plan.benchmark_sessions} benchmark + "
            f"{plan.codex_analysis_sessions} Codex analysis)"
        )

    if args.max_sessions is not None and plan.total_model_sessions > args.max_sessions:
        print(
            f"Budget exceeded: {plan.total_model_sessions} > {args.max_sessions}"
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

