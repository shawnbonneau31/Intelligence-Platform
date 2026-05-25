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
    req.add_header("apikey", ATTOM_API_KEY)

    try:
        logger.info(f"ATTOM API request: {endpoint} params={params}")
        with urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            logger.info(f"ATTOM API success: {endpoint} — {len(raw)} bytes")
            return data
    except HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:500]
        except:
            pass
        logger.warning(f"ATTOM API HTTP error {e.code}: {e.reason} for {endpoint} — {body}")
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


def _safe_int(val):
    """Safely convert a value to int, handling strings, floats, and None."""
    if val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _safe_float(val):
    """Safely convert a value to float, handling strings and None."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _first_valid(*values):
    """Return the first non-None, non-zero, non-empty value."""
    for v in values:
        if v is not None and v != 0 and v != "" and v != "0":
            return v
    return None


def parse_attom_property(raw_response):
    """
    Extract property characteristics from ATTOM property/detail response.
    Handles multiple response formats — ATTOM nests data differently by
    property type (SFR vs condo vs multi-family) and by data availability.
    """
    if not raw_response:
        return None

    properties = raw_response.get("property", [])
    if not properties:
        return None

    prop = properties[0]

    # Log the top-level keys we received for debugging
    logger.info(f"ATTOM property keys: {list(prop.keys())}")

    summary = prop.get("summary", {})
    building = prop.get("building", {})
    utilities = prop.get("utilities", {})
    lot = prop.get("lot", {})
    location = prop.get("location", {})
    identifier = prop.get("identifier", {})

    # Some ATTOM responses nest building as a list — normalize first
    if isinstance(building, list) and len(building) > 0:
        building = building[0]
    elif not isinstance(building, dict):
        building = {}

    building_summary = building.get("summary", {})
    building_size = building.get("size", {})
    building_rooms = building.get("rooms", {})
    building_construction = building.get("construction", {})

    # Year built — check every known location
    year_built = _safe_int(_first_valid(
        building_summary.get("yearBuilt"),
        summary.get("yearBuilt"),
        prop.get("yearBuilt"),
        summary.get("yearbuilt"),       # lowercase variant
        building_summary.get("yearbuilt"),
    ))

    # Square footage — multiple possible keys
    sqft = _safe_int(_first_valid(
        building_size.get("universalSize"),
        building_size.get("livingSize"),
        building_size.get("bldgSize"),
        building_size.get("grossSize"),
        building_size.get("groundFloorSize"),
        summary.get("aboveGradeFinishedArea"),
        summary.get("livingSize"),
    ))

    # Bathrooms — total, or compute from full + half
    baths_total = _safe_float(_first_valid(
        building_rooms.get("bathsTotal"),
        summary.get("bathsTotal"),
    ))
    if baths_total is None:
        baths_full = _safe_float(_first_valid(
            building_rooms.get("bathsFull"),
            summary.get("bathsFull"),
        ))
        baths_half = _safe_float(_first_valid(
            building_rooms.get("bathsHalf"),
            summary.get("bathsHalf"),
        ))
        if baths_full is not None:
            baths_total = baths_full + (baths_half or 0) * 0.5

    # Bedrooms
    beds = _safe_int(_first_valid(
        building_rooms.get("beds"),
        building_rooms.get("bedrooms"),
        summary.get("beds"),
        summary.get("bedrooms"),
    ))

    # Stories/levels
    stories = _safe_int(_first_valid(
        building_summary.get("levels"),
        summary.get("levels"),
        summary.get("stories"),
        building_summary.get("stories"),
    ))

    # Construction type
    construction_type = _first_valid(
        building_construction.get("constructionType"),
        summary.get("constructionType"),
        building_construction.get("frameType"),
    )

    # Heating type
    heating_type = _first_valid(
        utilities.get("heatingType"),
        utilities.get("heatingFuel"),
    )

    # Quality rating
    quality = _first_valid(
        building_summary.get("quality"),
        summary.get("quality"),
    )

    # Property type
    prop_type = _first_valid(
        summary.get("propType"),
        summary.get("propClass"),
    )
    prop_subtype = summary.get("propSubType")

    # Lot size
    lot_size_sqft = _safe_int(lot.get("lotSize2") or lot.get("lotsize2"))
    lot_size_acres = _safe_float(lot.get("lotSize1") or lot.get("lotsize1"))

    # Roof
    roof_cover = _first_valid(
        building_construction.get("roofCover"),
        building_construction.get("roofType"),
    )

    # Location
    latitude = _safe_float(location.get("latitude"))
    longitude = _safe_float(location.get("longitude"))

    enriched = {
        "provider": "attom",
        "attom_id": identifier.get("attomId") or identifier.get("obPropId"),
        "year_built": year_built,
        "sqft": sqft,
        "bathrooms": baths_total,
        "bedrooms": beds,
        "stories": stories,
        "construction_type": construction_type,
        "heating_type": heating_type,
        "quality_rating": quality,
        "property_type": prop_type,
        "property_subtype": prop_subtype,
        "lot_size_sqft": lot_size_sqft,
        "lot_size_acres": lot_size_acres,
        "roof_cover": roof_cover,
        "latitude": latitude,
        "longitude": longitude,
        "fetched_at": datetime.utcnow().isoformat(),
    }

    # Remove None values for clean output
    result = {k: v for k, v in enriched.items() if v is not None}
    logger.info(f"ATTOM parsed fields: {list(result.keys())}")
    return result


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


def clear_enrichment_cache(address=None, city=None, state=None, zip_code=None):
    """
    Clear enrichment cache entries.
    If address components provided, clear only that property.
    If no args, clear ALL cached entries.
    Returns number of entries deleted.
    """
    conn = sqlite3.connect(DB_PATH)
    if address:
        key = _cache_key(address, city, state, zip_code)
        cursor = conn.execute("DELETE FROM property_enrichment_cache WHERE cache_key = ?", (key,))
    else:
        cursor = conn.execute("DELETE FROM property_enrichment_cache")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    logger.info(f"Cleared {deleted} enrichment cache entries")
    return deleted


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
