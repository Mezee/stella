#!/usr/bin/env python3
"""Kerykeion-backed script tools for the Stella Codex plugin."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from kerykeion import to_context  # noqa: F401
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Kerykeion is not installed. Run: python3 -m pip install kerykeion"
    ) from exc

from stella_kerykeion_commands import (
    aspects,
    build_return_payload,
    build_transit_aspects,
    context_payload,
    lunar_return_payload,
    natal_payload,
    solar_return_payload,
    synastry_payload,
    transits_payload,
)
from stella_kerykeion_core import (
    HOUSE_SYSTEMS,
    ZODIACS,
    Birth,
    build_birth,
    build_houses,
    build_planets,
    build_return_factory,
    build_second_birth,
    build_subject_model,
    build_transit_birth,
    envelope,
    extract_return_date,
    make_subject,
    matched_aspect,
)


def add_birth_args(parser: argparse.ArgumentParser):
    parser.add_argument("--name", required=True)
    parser.add_argument("--date", required=True, help="Birth date as YYYY-MM-DD")
    parser.add_argument("--time", required=True, help="Birth time as HH:MM")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lng", type=float, required=True)
    parser.add_argument("--tz", required=True)
    parser.add_argument(
        "--house-system",
        default="placidus",
        choices=sorted(HOUSE_SYSTEMS),
    )
    parser.add_argument(
        "--zodiac",
        default="tropical",
        choices=sorted(ZODIACS),
    )


def add_output_args(parser: argparse.ArgumentParser):
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")


def add_natal_parser(subparsers: Any):
    parser = subparsers.add_parser("natal", help="Calculate a natal chart")
    add_birth_args(parser)
    add_output_args(parser)


def add_context_parser(subparsers: Any):
    parser = subparsers.add_parser("context", help="Generate context text")
    add_birth_args(parser)
    add_output_args(parser)


def add_synastry_parser(subparsers: Any):
    parser = subparsers.add_parser("synastry", help="Calculate synastry")
    add_birth_args(parser)
    parser.add_argument("--name2", required=True)
    parser.add_argument("--date2", required=True)
    parser.add_argument("--time2", required=True)
    parser.add_argument("--lat2", type=float, required=True)
    parser.add_argument("--lng2", type=float, required=True)
    parser.add_argument("--tz2", required=True)
    add_output_args(parser)


def add_transits_parser(subparsers: Any):
    parser = subparsers.add_parser("transits", help="Calculate transits")
    add_birth_args(parser)
    parser.add_argument("--transit-date", required=True)
    parser.add_argument("--transit-time", default="12:00")
    parser.add_argument("--transit-lat", type=float)
    parser.add_argument("--transit-lng", type=float)
    parser.add_argument("--transit-tz")
    add_output_args(parser)


def add_solar_return_parser(subparsers: Any):
    parser = subparsers.add_parser("solar-return", help="Calculate solar return")
    add_birth_args(parser)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--return-lat", type=float)
    parser.add_argument("--return-lng", type=float)
    parser.add_argument("--return-tz")
    add_output_args(parser)


def add_lunar_return_parser(subparsers: Any):
    parser = subparsers.add_parser("lunar-return", help="Calculate lunar return")
    add_birth_args(parser)
    parser.add_argument("--target-date", required=True)
    add_output_args(parser)


def build_parser():
    parser = argparse.ArgumentParser(description="Run Stella Kerykeion chart tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_natal_parser(subparsers)
    add_context_parser(subparsers)
    add_synastry_parser(subparsers)
    add_transits_parser(subparsers)
    add_solar_return_parser(subparsers)
    add_lunar_return_parser(subparsers)
    return parser


def emit(payload: dict[str, Any], compact: bool):
    if compact:
        print(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))
        return
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def build_handlers():
    return {
        "natal": natal_payload,
        "context": context_payload,
        "synastry": synastry_payload,
        "transits": transits_payload,
        "solar-return": solar_return_payload,
        "lunar-return": lunar_return_payload,
    }


def main():
    parser = build_parser()
    args = parser.parse_args()
    payload = build_handlers()[args.command](args)
    emit(payload, args.compact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
