# Stella

Stella is an astrology plugin that combines chart calculation with interpretation workflows.

It is built for:

- natal chart calculation and interpretation
- synastry and relationship comparison
- transit snapshots
- solar and lunar return work
- validation-aware astrology outputs

## What Stella Includes

- focused skills for natal, synastry, transits, returns, reports, and validation
- a Kerykeion-backed Python runtime for deterministic chart data
- output guardrails that block common overreach and unsupported certainty

## Requirements

Stella requires Python 3 and the `kerykeion` package.

Install the dependency with:

```bash
python3 -m pip install kerykeion
```

## Main Commands

Natal chart:

```bash
python3 scripts/stella_kerykeion.py natal --name "Ada" --date 1990-01-01 --time 12:00 --lat 40.7128 --lng -74.0060 --tz America/New_York
```

Synastry:

```bash
python3 scripts/stella_kerykeion.py synastry --name "Ada" --date 1990-01-01 --time 12:00 --lat 40.7128 --lng -74.0060 --tz America/New_York --name2 "Bea" --date2 1992-02-02 --time2 13:00 --lat2 34.0522 --lng2 -118.2437 --tz2 America/Los_Angeles
```

Transits:

```bash
python3 scripts/stella_kerykeion.py transits --name "Ada" --date 1990-01-01 --time 12:00 --lat 40.7128 --lng -74.0060 --tz America/New_York --transit-date 2026-05-04
```

Solar return:

```bash
python3 scripts/stella_kerykeion.py solar-return --name "Ada" --date 1990-01-01 --time 12:00 --lat 40.7128 --lng -74.0060 --tz America/New_York --year 2026
```

Lunar return:

```bash
python3 scripts/stella_kerykeion.py lunar-return --name "Ada" --date 1990-01-01 --time 12:00 --lat 40.7128 --lng -74.0060 --tz America/New_York --target-date 2026-05-04
```

## Output Style

Stella is designed to keep:

- chart facts separate from interpretation
- unsupported claims marked clearly
- deterministic medical, legal, financial, and relationship certainty blocked

## Legal

- Privacy policy: `legal/privacy-policy.md`
- Terms of service: `legal/terms-of-service.md`

## Support

Creatorship  
https://www.creatorship.pro  
stella@creatorship.pro
