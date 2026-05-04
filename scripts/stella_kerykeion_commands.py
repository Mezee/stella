from __future__ import annotations

import argparse
from datetime import datetime
from typing import Any

from kerykeion import to_context
from kerykeion.chart_data_factory import ChartDataFactory

from stella_kerykeion_core import (
    LUNAR_RETURN_PLANETS,
    PLANET_NAMES,
    add_optional_points,
    angular_distance,
    build_angles,
    build_birth,
    build_birth_payload,
    build_houses,
    build_planets,
    build_return_factory,
    build_second_birth,
    build_subject_model,
    build_transit_birth,
    envelope,
    extract_return_date,
    house_data,
    make_subject,
    matched_aspect,
    planet_data,
)


def build_return_payload(
    args: argparse.Namespace,
    chart: Any,
    command: str,
    result: dict[str, Any],
):
    result_with_angles = result | {
        "angles": build_angles(chart.first_house, chart.tenth_house)
    }
    return envelope(command, args, result_with_angles)


def build_transit_aspects(
    natal_planets: dict[str, Any],
    transit_planets: dict[str, Any],
):
    rows = []
    for transit_name, transit_planet in transit_planets.items():
        for natal_name, natal_planet in natal_planets.items():
            distance = angular_distance(
                transit_planet["abs_pos"],
                natal_planet["abs_pos"],
            )
            match = matched_aspect(distance)
            if not match:
                continue
            rows.append(
                {
                    "transit_planet": transit_planet.get("name")
                    or transit_name.title(),
                    "natal_planet": natal_planet.get("name") or natal_name.title(),
                    "aspect": match["aspect"],
                    "orb": match["orb"],
                    "distance": distance,
                }
            )
    return sorted(
        rows,
        key=lambda row: (
            row["orb"],
            row["transit_planet"],
            row["natal_planet"],
        ),
    )


def aspects(planets: dict[str, dict[str, Any]]):
    rows = []
    keys = [key for key in PLANET_NAMES if key in planets]
    for index, left_key in enumerate(keys):
        for right_key in keys[index + 1 :]:
            left = planets[left_key]
            right = planets[right_key]
            distance = angular_distance(left["abs_pos"], right["abs_pos"])
            match = matched_aspect(distance)
            if not match:
                continue
            rows.append(
                {
                    "planet_a": left.get("name") or left_key.title(),
                    "planet_b": right.get("name") or right_key.title(),
                    "aspect": match["aspect"],
                    "orb": match["orb"],
                    "distance": distance,
                }
            )
    return sorted(
        rows,
        key=lambda row: (row["orb"], row["planet_a"], row["planet_b"]),
    )


def natal_payload(args: argparse.Namespace):
    birth = build_birth(args)
    subject = make_subject(birth, args)
    planets = add_optional_points(subject, build_planets(subject, PLANET_NAMES))
    result = {
        "name": birth.name,
        "birth_data": build_birth_payload(birth),
        "planets": planets,
        "houses": build_houses(subject),
        "angles": build_angles(subject.first_house, subject.tenth_house),
        "aspects": aspects(planets),
    }
    return envelope("natal", args, result)


def context_payload(args: argparse.Namespace):
    subject = make_subject(build_birth(args), args)
    return envelope("context", args, {"context": to_context(subject)})


def build_synastry_people(first: Any, second: Any, args: argparse.Namespace):
    return {
        "person_one": {
            "name": args.name,
            "sun": planet_data(first.sun),
            "moon": planet_data(first.moon),
            "venus": planet_data(first.venus),
            "mars": planet_data(first.mars),
            "asc": house_data(first.first_house),
        },
        "person_two": {
            "name": args.name2,
            "sun": planet_data(second.sun),
            "moon": planet_data(second.moon),
            "venus": planet_data(second.venus),
            "mars": planet_data(second.mars),
            "asc": house_data(second.first_house),
        },
    }


def synastry_payload(args: argparse.Namespace):
    first = make_subject(build_birth(args), args)
    second = make_subject(build_second_birth(args), args)
    data = ChartDataFactory.create_synastry_chart_data(
        build_subject_model(first),
        build_subject_model(second),
    )
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    result = build_synastry_people(first, second, args)
    result["synastry"] = dumped
    return envelope("synastry", args, result)


def solar_return_payload(args: argparse.Namespace):
    birth = build_birth(args)
    subject = make_subject(birth, args)
    _, month, day, _, _ = birth.parts()
    factory = build_return_factory(
        subject,
        args.return_lng if args.return_lng is not None else args.lng,
        args.return_lat if args.return_lat is not None else args.lat,
        args.return_tz or args.tz,
    )
    chart = factory.next_return_from_date(
        args.year,
        month,
        day,
        return_type="Solar",
    )
    result = {
        "name": args.name,
        "year": args.year,
        "solar_return_date": extract_return_date(chart),
        "planets": build_planets(chart, PLANET_NAMES),
        "aspects": aspects(build_planets(chart, PLANET_NAMES)),
    }
    return build_return_payload(args, chart, "solar_return", result)


def lunar_return_payload(args: argparse.Namespace):
    target = datetime.strptime(args.target_date, "%Y-%m-%d")
    subject = make_subject(build_birth(args), args)
    factory = build_return_factory(subject, args.lng, args.lat, args.tz)
    chart = factory.next_return_from_date(
        target.year,
        target.month,
        target.day,
        return_type="Lunar",
    )
    result = {
        "name": args.name,
        "target_date": args.target_date,
        "lunar_return_date": extract_return_date(chart),
        "planets": build_planets(chart, LUNAR_RETURN_PLANETS),
    }
    return build_return_payload(args, chart, "lunar_return", result)


def transits_payload(args: argparse.Namespace):
    natal = make_subject(build_birth(args), args)
    transit = make_subject(build_transit_birth(args), args)
    natal_planets = build_planets(natal, PLANET_NAMES)
    transit_planets = build_planets(transit, PLANET_NAMES)
    result = {
        "name": args.name,
        "transit_date": args.transit_date,
        "natal_planets": natal_planets,
        "transit_planets": transit_planets,
        "transit_to_natal_aspects": build_transit_aspects(
            natal_planets,
            transit_planets,
        ),
    }
    return envelope("transits", args, result)
