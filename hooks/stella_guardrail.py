#!/usr/bin/env python3
"""Automatic guardrails for Stella astrology outputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from stella_guardrail_io import as_json, read_payload
from stella_guardrail_rules import check_text


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run Stella astrology output guardrails."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when blocking findings are present.",
    )
    parser.add_argument("--text", help="Text to check instead of stdin.")
    args = parser.parse_args(argv)

    text = args.text if args.text is not None else read_payload()[1]
    findings = check_text(text)
    output = as_json(findings)

    if args.strict and any(finding.severity == "block" for finding in findings):
        print(output, file=sys.stderr)
        return 2

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
