from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    severity: str = "warning"


FORBIDDEN_PATTERNS = (
    (
        "deterministic_relationship",
        re.compile(
            r"\b(guarantees?|definitely|certainly|will)\b.{0,80}\b"
            r"(marry|marriage|break ?up|divorce|soulmate|cheat(?:ing)?)\b",
            re.I | re.S,
        ),
        "Avoid deterministic relationship claims. Reframe as symbolic synastry dynamics.",
    ),
    (
        "medical_diagnosis",
        re.compile(
            r"\b(diagnose|diagnosis|disease|illness|cancer|pregnan(?:t|cy)|"
            r"medical condition)\b",
            re.I,
        ),
        "Do not provide medical diagnosis from astrology.",
    ),
    (
        "death_prediction",
        re.compile(
            r"\b(cause of death|death date|when (?:i|they|you) will die|will die)\b",
            re.I,
        ),
        "Do not make death predictions from astrology.",
    ),
    (
        "legal_financial_certainty",
        re.compile(
            r"\b(guarantees?|definitely|certainly|will)\b.{0,80}\b"
            r"(win the case|lose the case|get rich|become rich|go bankrupt)\b",
            re.I | re.S,
        ),
        "Avoid legal or financial certainty claims.",
    ),
    (
        "validation_bypass",
        re.compile(
            r"\b(hide|ignore|skip|bypass)\b.{0,80}\b"
            r"(validation|validator|validation failures?|contradictions?)\b",
            re.I | re.S,
        ),
        "Do not hide or bypass validation failures.",
    ),
)

UNSUPPORTED_TECHNIQUE_PATTERNS = (
    (
        "composite_from_synastry",
        re.compile(
            r"\bcomposite chart\b|\bcomposite (sun|moon|ascendant|venus|mars)\b",
            re.I,
        ),
        "Composite chart facts require a composite payload; synastry alone is not enough.",
    ),
    (
        "unsupported_timing",
        re.compile(
            r"\b(profection|zodiacal releasing|dasha|horary|electional)\b",
            re.I,
        ),
        "Do not present this technique unless it was separately calculated.",
    ),
)

ASTROLOGY_FACT_PATTERN = re.compile(
    r"\b("
    r"sun|moon|mercury|venus|mars|jupiter|saturn|uranus|neptune|pluto|"
    r"ascendant|midheaven|mc|north node|south node|chiron"
    r")\b.{0,80}\b("
    r"aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|"
    r"aquarius|pisces|house|conjunction|sextile|square|trine|opposition"
    r")\b",
    re.I | re.S,
)

VALIDATION_NOTE_PATTERN = re.compile(
    r"\b(validation|validated|not checked|needs review|unsupported|chart facts|payload)\b",
    re.I,
)


def has_validation_context(text):
    return bool(VALIDATION_NOTE_PATTERN.search(text))


def collect_matches(text, patterns, severity=None):
    findings = []
    for code, pattern, message in patterns:
        if pattern.search(text):
            findings.append(
                Finding(code=code, message=message, severity=severity or "warning")
            )
    return findings


def needs_validation_context(text):
    return ASTROLOGY_FACT_PATTERN.search(text) and not has_validation_context(text)


def check_text(text):
    findings = []
    normalized = text.strip()
    if not normalized:
        return findings

    findings.extend(collect_matches(normalized, FORBIDDEN_PATTERNS, "block"))
    findings.extend(collect_matches(normalized, UNSUPPORTED_TECHNIQUE_PATTERNS))

    if needs_validation_context(normalized):
        findings.append(
            Finding(
                code="missing_validation_context",
                message=(
                    "Computed astrology facts should include validation status "
                    "or a clear chart-fact/payload caveat."
                ),
            )
        )

    return findings
