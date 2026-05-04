from __future__ import annotations

import json
import sys


def extract_text(payload):
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        return "\n".join(extract_text(value) for value in payload.values())
    if isinstance(payload, list):
        return "\n".join(extract_text(item) for item in payload)
    return ""


def read_payload():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}, ""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw, raw
    return payload, extract_text(payload)


def status_for(findings):
    rows = [finding.__dict__ for finding in findings]
    if any(row["severity"] == "block" for row in rows):
        return rows, "blocked"
    if rows:
        return rows, "warning"
    return rows, "ok"


def as_json(findings):
    rows, status = status_for(findings)
    return json.dumps(
        {"plugin": "stella", "status": status, "findings": rows},
        indent=2,
    )
