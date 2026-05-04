from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, Iterable

from kerykeion import AstrologicalSubjectFactory


PLANET_NAMES = (
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
)
LUNAR_RETURN_PLANETS = ("moon", "sun", "mercury", "venus", "mars")
MAJOR_ASPECTS = (
    ("conjunction", 0.0, 5.0),
    ("sextile", 60.0, 4.0),
    ("square", 90.0, 4.0),
    ("trine", 120.0, 4.0),
    ("opposition", 180.0, 5.0),
)
HOUSE_NAMES = (
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
    "eleventh",
    "twelfth",
)
OPTIONAL_POINTS = {
    "chiron": "chiron",
    "north_node": "true_north_lunar_node",
    "south_node": "true_south_lunar_node",
    "part_of_fortune": "pars_fortunae",
}
HOUSE_SYSTEMS = {
    "placidus": "P",
    "koch": "K",
    "whole_sign": "W",
    "equal": "A",
    "regiomontanus": "R",
    "campanus": "C",
}
ZODIACS = {
    "tropical": "Tropical",
    "sidereal": "Sidereal",
}


@dataclass(frozen=True)
class Birth:
    name: str
    date: str
    time: str
    lat: float
    lng: float
    tz: str

    def parts(self):
        try:
            year, month, day = (int(part) for part in self.date.split("-"))
            hour, minute = (int(part) for part in self.time.split(":"))
        except ValueError as exc:
            raise ValueError("Use YYYY-MM-DD for dates, HH:MM for times.") from exc
        return year, month, day, hour, minute


def object_value(source: Any, key: str, default: Any = None):
    if isinstance(source, dict):
        return source.get(key, default)
    return getattr(source, key, default)


def normalize_float(source: Any, key: str):
    return round(float(object_value(source, key, 0.0)), 2)


def planet_data(planet: Any):
    return {
        "name": object_value(planet, "name", ""),
        "sign": object_value(planet, "sign", ""),
        "sign_num": object_value(planet, "sign_num", 0),
        "position": normalize_float(planet, "position"),
        "abs_pos": normalize_float(planet, "abs_pos"),
        "house": object_value(planet, "house", ""),
        "retrograde": bool(object_value(planet, "retrograde", False)),
    }


def house_data(house: Any):
    return {
        "name": object_value(house, "name", ""),
        "sign": object_value(house, "sign", ""),
        "position": normalize_float(house, "position"),
        "abs_pos": normalize_float(house, "abs_pos"),
    }


def angular_distance(left: float, right: float):
    distance = abs(left - right)
    return round(min(distance, 360.0 - distance), 2)


def matched_aspect(distance: float):
    for name, angle, max_orb in MAJOR_ASPECTS:
        orb = abs(distance - angle)
        if orb <= max_orb:
            return {
                "aspect": name,
                "angle": angle,
                "orb": round(orb, 2),
                "max_orb": max_orb,
            }
    return None


def build_birth(args: argparse.Namespace):
    return Birth(args.name, args.date, args.time, args.lat, args.lng, args.tz)


def build_second_birth(args: argparse.Namespace):
    return Birth(
        args.name2,
        args.date2,
        args.time2,
        args.lat2,
        args.lng2,
        args.tz2,
    )


def build_transit_birth(args: argparse.Namespace):
    return Birth(
        "Transits",
        args.transit_date,
        args.transit_time,
        args.transit_lat if args.transit_lat is not None else args.lat,
        args.transit_lng if args.transit_lng is not None else args.lng,
        args.transit_tz or args.tz,
    )


def make_subject(birth: Birth, args: argparse.Namespace):
    year, month, day, hour, minute = birth.parts()
    return AstrologicalSubjectFactory.from_birth_data(
        name=birth.name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        lng=birth.lng,
        lat=birth.lat,
        tz_str=birth.tz,
        online=False,
        zodiac_type=ZODIACS[args.zodiac],
        houses_system_identifier=HOUSE_SYSTEMS[args.house_system],
    )


def build_subject_model(subject: Any):
    return subject.model() if hasattr(subject, "model") else subject


def build_planets(subject: Any, planet_names: Iterable[str]):
    return {name: planet_data(getattr(subject, name)) for name in planet_names}


def add_optional_points(subject: Any, planets: dict[str, Any]):
    enriched = dict(planets)
    for output_name, attr_name in OPTIONAL_POINTS.items():
        point = getattr(subject, attr_name, None)
        if point:
            enriched[output_name] = planet_data(point)
    return enriched


def build_houses(subject: Any):
    return {
        house_name: house_data(getattr(subject, f"{house_name}_house"))
        for house_name in HOUSE_NAMES
    }


def build_angles(first_house: Any, tenth_house: Any):
    return {"asc": house_data(first_house), "mc": house_data(tenth_house)}


def build_birth_payload(birth: Birth):
    return {
        "date": birth.date,
        "time": birth.time,
        "latitude": birth.lat,
        "longitude": birth.lng,
        "timezone": birth.tz,
    }


def build_return_factory(subject: Any, lng: float, lat: float, tz: str):
    from kerykeion.planetary_return_factory import PlanetaryReturnFactory

    return PlanetaryReturnFactory(
        subject,
        lng=lng,
        lat=lat,
        tz_str=tz,
        online=False,
    )


def extract_return_date(chart: Any):
    return chart.iso_formatted_local_datetime.split("T")[0]


def envelope(command: str, args: argparse.Namespace, result: dict[str, Any]):
    return {
        "status": "OK",
        "backend": "kerykeion",
        "plugin": "stella",
        "command": command,
        "config": {
            "house_system": args.house_system,
            "zodiac": args.zodiac,
        },
        "result": result,
    }
