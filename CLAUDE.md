# Namara Water Risk Intelligence Platform

## Critical Rules

- **Data sources AND scoring weights/percentages are trade secrets. Never expose in UI or API responses.**
- **Ask before making any changes** — confirm with Shawn before editing code or files.
- **Shawn handles git** — make changes, he will add, commit, and push.

## Project Overview

Property-level water risk scoring platform for insurance carriers. Scores properties across 11 factors, provides claims intelligence, device prevention mapping, and builder ratings.

- **Stack:** Python/Tornado backend, single-page HTML frontend, SQLite (WAL mode), deployed on Render.com
- **Auth:** JWT tokens + API keys with rate limiting
- **External APIs:** ATTOM (property enrichment), Open-Meteo (climate data)

## Architecture

| File | Purpose |
|------|---------|
| `server.py` | Tornado web server, API endpoints, JWT auth |
| `scoring.py` | 11-factor property scoring, builder grading, claims risk scoring |
| `static/index.html` | Single-page frontend — all tabs, ROI calculator, fleet view |
| `property_enrichment.py` | ATTOM API integration (construction_type, heating_type, quality_rating) |
| `database.py` | SQLite setup, WAL mode |
| `seed_data.py` | Builder and zip code seed data |
| `reports.py` | ReportLab PDF generation |

## Scoring Model

- **Property factors (60%):** 11 factors including pipe age, water heater, construction type, etc.
- **Environmental factors (40%):** Climate, freeze risk, soil, flood zone, water quality, infrastructure
- **Claims Risk Score:** 0-100, combining claim frequency (60%) and avg claim cost (40%) per zip code. Defaults to 50 if no data.
- **Builder grading:** Standard academic scale — A >= 90, B >= 80, C >= 70, D >= 60, F < 60
- **Data cascade:** User input > local DB > ATTOM API (3-tier fallback)

## Namara Device

- **Leak detection:** 1 GPD sensitivity
- **Static pressure management:** Closes valve and bleeds pressure when water is off. Opens to optimal pressure when water turns on, then closes and bleeds back down when it stops.
- **Install complexity:** Based on pipe material (galvanized=High, copper/CPVC=Moderate, PEX=Low) and main line accessibility

## Pricing

- **Purchase:** $1,250 device + $1,000 professional install ($2,250 total per home)
- **Subscription:** $49/month, homeowner covers $1,000 install

## Display Conventions

- All scores display with exactly one decimal place via `d1()` helper function
- Claims and environmental scores note they are zip code averages, not property-specific
- Est. Savings percentages in prevention mapping include explainer text

## Pending Work

- Expand builder database to all 50 states with enhanced scoring
- San Diego County assessor integration as secondary enrichment source
- Builder data improvements and rescoring
