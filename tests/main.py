from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestType(StrEnum):
    UNIT = "unit"
    INTEGRATION = "integration"
    ALL = "all"


@dataclass(frozen=True)
class SuiteConfig:
    paths: tuple[str, ...]


SUITE_CONFIGS: dict[TestType, SuiteConfig] = {
    TestType.UNIT: SuiteConfig(paths=("tests/unit",)),
    TestType.INTEGRATION: SuiteConfig(paths=("tests/integration",)),
    TestType.ALL: SuiteConfig(paths=("tests",)),
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=("Unified pytest runner for this project. Supports running unit, integration, or all tests.")
    )
    parser.add_argument(
        "-t",
        "--type",
        dest="test_type",
        type=str,
        choices=[item.value for item in TestType],
        default=TestType.ALL.value,
        help="Choose which test suite to run (default: all).",
    )
    parser.add_argument(
        "-k",
        "--keyword",
        help="Only run tests that match a given expression (pytest -k).",
    )
    parser.add_argument(
        "-m",
        "--marker",
        help="Only run tests matching the provided marker expression (pytest -m).",
    )
    parser.add_argument(
        "-x",
        "--fail-fast",
        action="store_true",
        help="Stop at first failure (pytest -x).",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Enable coverage report with missing lines.",
    )
    parser.add_argument(
        "-n",
        "--parallel",
        metavar="WORKERS",
        help=("Run tests in parallel with pytest-xdist (example: -n auto). Requires pytest-xdist to be installed."),
    )
    parser.add_argument(
        "--pytest-args",
        default="",
        help=('Additional raw pytest args as a single string. Example: --pytest-args "--maxfail=2 --disable-warnings"'),
    )
    return parser


def _build_pytest_command(args: argparse.Namespace) -> list[str]:
    suite = SUITE_CONFIGS[TestType(args.test_type)]
    cmd: list[str] = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        *suite.paths,
    ]

    if args.keyword:
        cmd.extend(["-k", args.keyword])

    if args.marker:
        cmd.extend(["-m", args.marker])

    if args.fail_fast:
        cmd.append("-x")

    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing"])

    if args.parallel:
        cmd.extend(["-n", args.parallel])

    if args.pytest_args:
        cmd.extend(shlex.split(args.pytest_args))

    return cmd


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    cmd = _build_pytest_command(args)

    completed = subprocess.run(cmd, cwd=PROJECT_ROOT, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
