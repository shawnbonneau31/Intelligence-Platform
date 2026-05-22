# Namara Water Risk Intelligence Platform

Property-level water risk scoring across 5 data layers for insurance carriers.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database with seed data
python seed_data.py

# Start the server
python server.py
```

Open http://localhost:8080 — login with `demo@namarawater.ai` / `demo2026`

## API Usage

```bash
# Score a property
curl -H "X-API-Key: YOUR_KEY" "http://localhost:8080/api/v1/score?zip=33139"

# Batch score
curl -X POST -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"zip_codes":["33139","77001","85001"]}' \
  "http://localhost:8080/api/v1/score"

# Download PDF report
curl -H "X-API-Key: YOUR_KEY" -o report.pdf \
  "http://localhost:8080/api/v1/report?zip=33139"

# Search builders
curl -H "X-API-Key: YOUR_KEY" "http://localhost:8080/api/v1/builders?state=FL&grade=A"
```

## Deploy

**Docker:**
```bash
docker-compose up -d
```

**Render.com:** Push to GitHub, connect repo — `render.yaml` configures automatically.

**Railway:** `railway up` from project root.

## Architecture

- **Server:** Python/Tornado
- **Database:** SQLite (WAL mode)
- **Auth:** JWT tokens + API keys with rate limiting
- **Climate Data:** Open-Meteo Archive API (live, no key needed)
- **Reports:** ReportLab PDF generation
# Intelligence-Platform
# Intelligence-Platform
# Intelligence-Platform
