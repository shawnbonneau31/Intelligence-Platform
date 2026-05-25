"""
Property Data Enrichment Module
Pulls property characteristics from ATTOM Data API to auto-populate
scoring factors instead of relying on manual user input.

Supports: ATTOM Data (primary), with architecture for additional providers.
Falls back gracefully when no API key is configured or API is unreachable.
"""

import os
import json
import sqlite3
import logging
import time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)

# ─── Configuration ───
ATTOM_API_KEY = os.environ.get("ATTOM_API_KEY", "")
ATTOM_BASE_URL = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"

# Cache settings: avoid repeat API calls for same property
ENRICHMENT_CACHE_HOURS = 24 * 7  # 7 days
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "namara.db")


# ─── Database Cache ───

def init_enrichment_cache():
    """Create the enrichment cache table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS property_enrichment_cache (
            cache_key TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            raw_response TEXT,
            enriched_data TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _cache_key(address, city, state, zip_code):
    """Generate a normalized cache key from address components."""
    parts = [
        (address or "").strip().lower(),
        (city or "").strip().lower(),
        (state or "").strip().upper(),
        str(zip_code or "").strip()
    ]
    return "|".join(parts)


def get_cached_enrichment(address, city, state, zip_code):
    """Return cached enrichment data if fresh, else None."""
    key = _cache_key(address, city, state, zip_code)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT enriched_data, expires_at FROM property_enrichment_cache WHERE cache_key = ?",
        (key,)
    ).fetchone()
    conn.close()

    if row and row["expires_at"] > datetime.utcnow().isoformat():
        return json.loads(row["enriched_data"])
    return None


def save_enrichment_cache(address, city, state, zip_code, provider, enriched_data, raw_response=None):
    """Save enrichment result to cache."""
    key = _cache_key(address, city, state, zip_code)
    now = datetime.utcnow()
    expires = now + timedelta(hours=ENRICHMENT_CACHE_HOURS)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT OR REPLACE INTO property_enrichment_cache
        (cache_key, provider, raw_response, enriched_data, fetched_at, expires_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        key, provider,
        json.dumps(raw_response) if raw_response else None,
        json.dumps(enriched_data),
        now.isoformat(), expires.isoformat()
    ))
    conn.commit()
    conn.close()


# ─── ATTOM Data API ───

def _attom_request(endpoint, params):
    """Make authenticated GET request to ATTOM API. Returns parsed JSON or None."""
    if not ATTOM_API_KEY:
        return None

    url = f"{ATTOM_BASE_URL}{endpoint}?{urlencode(params)}"
    req = Request(url)
    req.add_header("Accept", "application/json")
    req.add_header("APIKey", ATTOM_API_KEY)

    try:
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except HTTPError as e:
        logger.warning(f"ATTOM API HTTP error {e.code}: {e.reason} for {endpoint}")
        if e.code == 429:
            logger.warning("ATTOM rate limit hit — will use cached/fallback data")
        return None
    except (URLError, TimeoutError, json.JSONDecodeError) as e:
        logger.warning(f"ATTOM API request failed: {e}")
        return None


def fetch_attom_property_detail(address, city, state, zip_code):
    """
    Fetch property detail from ATTOM /property/detail endpoint.
    Uses address1 (street) + address2 (city, state zip) format.

    Returns raw API response or None.
    """
    address1 = address.strip()
    address2 = f"{city}, {state} {zip_code}".strip() if city else f"{state} {zip_code}".strip()

    params = {
        "address1": address1,
        "address2": address2,
    }

    return _attom_request("/property/detail", params)


def parse_attom_property(raw_response):
    """
    Extract property characteristics from ATTOM property/detail response.
    Returns a standardized dict of enrichment fields.

    ATTOM response structure:
    {
      "status": {...},
      "property": [{
        "identifier": {"attomId": ..., "fips": ..., "apn": ...},
        "lot": {"lotSize1": ..., "lotSize2": ...},
        "area": {"countrySecSubd": ..., "countyUse1": ...},
        "address": {...},
        "location": {"latitude": ..., "longitude": ...},
        "summary": {
          "yearBuilt": 1995,
          "propClass": "Single Family Residence",
          "propType": "SFR",
          "propSubType": "Residential",
          "beds": 3,
          "bathsFull": 2,
          "bathsHalf": 1,
          "bathsTotal": 2.5
        },
        "utilities": {"heatingType": ..., "coolingType": ...},
        "building": {
          "size": {"universalSize": 2100, "livingSize": 1900},
          "rooms": {"beds": 3, "bathsFull": 2, "bathsHalf": 1, "bathsTotal": 2.5},
          "interior": {"fplcCount": 1},
          "construction": {"constructionType": "Frame", "roofCover": "Composition Shingle"},
          "parking": {"garageType": "Attached"},
          "summary": {"levels": 2, "yearBuilt": 1995, "quality": "Average"}
        },
        "vintage": {"lastModified": ..., "pubDate": ...}
      }]
    }
    """
    if not raw_response:
        return None

    properties = raw_response.get("property", [])
    if not properties:
        return None

    prop = properties[0]
    summary = prop.get("summary", {})
    building = prop.get("building", {})
    building_summary = building.get("summary", {})
    building_size = building.get("size", {})
    building_rooms = building.get("rooms", {})
    building_construction = building.get("construction", {})
    utilities = prop.get("utilities", {})
    lot = prop.get("lot", {})
    location = prop.get("location", {})
    identifier = prop.get("identifier", {})

    # Extract year built — check multiple locations
    year_built = (
        building_summary.get("yearBuilt")
        or summary.get("yearBuilt")
    )

    # Extract square footage
    sqft = (
        building_size.get("universalSize")
        or building_size.get("livingSize")
        or building_size.get("bldgSize")
    )

    # Extract bathrooms
    baths_total = (
        building_rooms.get("bathsTotal")
        or summary.get("bathsTotal")
    )

    # Extract bedrooms (useful context for risk)
    beds = (
        building_rooms.get("beds")
        or summary.get("beds")
    )

    # Extract stories/levels
    stories = building_summary.get("levels") or summary.get("levels")

    # Construction type (can inform pipe material estimation)
    construction_type = (
        building_construction.get("constructionType")
        or summary.get("constructionType")
    )

    # Heating type — relevant for water heater risk
    heating_type = utilities.get("heatingType")

    # Quality rating from assessor
    quality = building_summary.get("quality")

    # Property type
    prop_type = summary.get("propType") or summary.get("propClass")
    prop_subtype = summary.get("propSubType")

    # Lot size in sqft
    lot_size_sqft = lot.get("lotSize2")
    lot_size_acres = lot.get("lotSize1")

    # Roof — relevant for overall property condition
    roof_cover = building_construction.get("roofCover")

    # Location
    latitude = location.get("latitude")
    longitude = location.get("longitude")

    enriched = {
        "provider": "attom",
        "attom_id": identifier.get("attomId"),
        "year_built": int(year_built) if year_built else None,
        "sqft": int(sqft) if sqft else None,
        "bathrooms": float(baths_total) if baths_total else None,
        "bedrooms": int(beds) if beds else None,
        "stories": int(stories) if stories else None,
        "construction_type": construction_type,
        "heating_type": heating_type,
        "quality_rating": quality,
        "property_type": prop_type,
        "property_subtype": prop_subtype,
        "lot_size_sqft": int(lot_size_sqft) if lot_size_sqft else None,
        "lot_size_acres": float(lot_size_acres) if lot_size_acres else None,
        "roof_cover": roof_cover,
        "latitude": float(latitude) if latitude else None,
        "longitude": float(longitude) if longitude else None,
        "fetched_at": datetime.utcnow().isoformat(),
    }

    # Remove None values for clean output
    return {k: v for k, v in enriched.items() if v is not None}


# ─── Main Enrichment Function ───

def enrich_property(address, city, state, zip_code):
    """
    Enrich property data from external APIs.

    Priority:
    1. Return cached data if fresh
    2. Call ATTOM API if key is configured
    3. Return None if no enrichment available (scoring falls back to manual/estimated)

    Returns dict with property characteristics or None.
    """
    if not address or not zip_code:
        return None

    # 1. Check cache
    cached = get_cached_enrichment(address, city, state, zip_code)
    if cached:
        logger.info(f"Property enrichment cache hit for {address}")
        cached["from_cache"] = True
        return cached

    # 2. Try ATTOM
    if ATTOM_API_KEY:
        logger.info(f"Fetching ATTOM property detail for {address}, {city}, {state} {zip_code}")
        raw = fetch_attom_property_detail(address, city, state, zip_code)
        enriched = parse_attom_property(raw)

        if enriched:
            # Cache the result
            save_enrichment_cache(address, city, state, zip_code, "attom", enriched, raw)
            enriched["from_cache"] = False
            return enriched
        else:
            logger.info(f"ATTOM returned no data for {address}")

    # 3. No enrichment available
    return None


def get_enrichment_status():
    """Return status info about the enrichment system for the admin panel."""
    has_attom = bool(ATTOM_API_KEY)

    # Count cached entries
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM property_enrichment_cache").fetchone()[0] if has_attom else 0
    active = conn.execute(
        "SELECT COUNT(*) FROM property_enrichment_cache WHERE expires_at > ?",
        (datetime.utcnow().isoformat(),)
    ).fetchone()[0] if has_attom else 0
    conn.close()

    return {
        "attom_configured": has_attom,
        "attom_key_prefix": ATTOM_API_KEY[:8] + "..." if has_attom else None,
        "cache_total": total,
        "cache_active": active,
        "cache_ttl_hours": ENRICHMENT_CACHE_HOURS,
        "providers_available": ["attom"] if has_attom else [],
        "fallback": "manual_input_and_estimation",
    }


# Initialize cache table on import
init_enrichment_cache()
