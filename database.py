"""
Namara Water Risk Intelligence Platform — Database Layer
SQLite database with tables for users, API keys, builder quality, scoring cache, and audit log.
"""

import sqlite3
import os
import hashlib
import secrets
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "namara.db")


def get_db():
    """Get a database connection with row factory."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize database schema."""
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        company TEXT,
        tier TEXT DEFAULT 'lookup' CHECK(tier IN ('lookup', 'portfolio', 'enterprise')),
        is_admin INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        last_login TEXT
    );

    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        key_hash TEXT UNIQUE NOT NULL,
        key_prefix TEXT NOT NULL,
        name TEXT DEFAULT 'Default',
        tier TEXT DEFAULT 'lookup',
        rate_limit_per_min INTEGER DEFAULT 10,
        rate_limit_per_day INTEGER DEFAULT 100,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        last_used TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS builders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        license_number TEXT UNIQUE,
        callback_rate REAL,
        plumbing_material_score REAL,
        code_violation_score REAL,
        litigation_score REAL,
        construction_volume_score REAL,
        appliance_score REAL,
        drainage_score REAL,
        composite_score REAL,
        grade TEXT CHECK(grade IN ('A', 'B', 'C', 'D', 'F')),
        homes_built INTEGER,
        year_established INTEGER,
        specialties TEXT,
        notes TEXT,
        bbb_rating TEXT DEFAULT 'NR',
        bbb_complaints INTEGER DEFAULT 0,
        bbb_years_accredited INTEGER DEFAULT 0,
        license_status TEXT DEFAULT 'active',
        license_expiry TEXT,
        building_dept_violations INTEGER DEFAULT 0,
        building_dept_last_violation TEXT,
        warranty_claim_rate REAL DEFAULT 0,
        plumbing_sub_quality TEXT DEFAULT 'unknown',
        avg_home_price INTEGER DEFAULT 0,
        markets TEXT,
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS water_quality (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state TEXT UNIQUE NOT NULL,
        violations_per_100k REAL,
        lead_copper_exceedances REAL,
        treatment_age_score REAL,
        composite_score REAL,
        data_source TEXT DEFAULT 'EPA SDWIS',
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS housing_age (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state TEXT UNIQUE NOT NULL,
        median_year_built INTEGER,
        pct_pre_1980 REAL,
        pct_pre_1960 REAL,
        infrastructure_score REAL,
        data_source TEXT DEFAULT 'Census ACS',
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS regulatory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state TEXT UNIQUE NOT NULL,
        leak_detection_mandate INTEGER DEFAULT 0,
        auto_shutoff_mandate INTEGER DEFAULT 0,
        insurance_incentive INTEGER DEFAULT 0,
        building_code_year INTEGER,
        compliance_score REAL,
        notes TEXT,
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS city_pressure (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state TEXT NOT NULL,
        avg_psi REAL,
        pct_over_80psi REAL,
        pct_under_40psi REAL,
        pressure_variability TEXT,
        infrastructure_age_factor REAL,
        pressure_score REAL,
        data_source TEXT DEFAULT 'AWWA Municipal Survey',
        updated_at TEXT DEFAULT (datetime('now')),
        UNIQUE(state)
    );

    CREATE TABLE IF NOT EXISTS score_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address_hash TEXT UNIQUE NOT NULL,
        zip_code TEXT,
        state TEXT,
        latitude REAL,
        longitude REAL,
        climate_score REAL,
        water_quality_score REAL,
        infrastructure_score REAL,
        builder_score REAL,
        regulatory_score REAL,
        composite_score REAL,
        risk_level TEXT,
        full_report JSON,
        created_at TEXT DEFAULT (datetime('now')),
        expires_at TEXT
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        api_key_id INTEGER,
        action TEXT NOT NULL,
        endpoint TEXT,
        address TEXT,
        zip_code TEXT,
        response_code INTEGER,
        response_time_ms REAL,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS rate_limits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_key_id INTEGER NOT NULL,
        window_start TEXT NOT NULL,
        request_count INTEGER DEFAULT 1,
        UNIQUE(api_key_id, window_start)
    );

    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        zip_code TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        year_built INTEGER,
        sqft INTEGER,
        stories INTEGER DEFAULT 1,
        bathrooms REAL DEFAULT 2.0,
        property_type TEXT DEFAULT 'single_family',
        pipe_material TEXT,
        pipe_material_source TEXT DEFAULT 'estimated',
        has_prv INTEGER DEFAULT 0,
        has_expansion_tank INTEGER DEFAULT 0,
        water_heater_age_years INTEGER,
        water_heater_type TEXT DEFAULT 'tank',
        last_plumbing_permit_year INTEGER,
        total_plumbing_permits INTEGER DEFAULT 0,
        last_renovation_year INTEGER,
        prior_water_claims INTEGER DEFAULT 0,
        prior_claim_total_cost REAL DEFAULT 0,
        builder_id INTEGER,
        builder_name TEXT,
        property_risk_score REAL,
        namara_device_installed INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (builder_id) REFERENCES builders(id)
    );

    CREATE TABLE IF NOT EXISTS namara_pressure_zones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zip_code TEXT NOT NULL,
        neighborhood TEXT,
        avg_psi REAL,
        min_psi REAL,
        max_psi REAL,
        device_count INTEGER DEFAULT 0,
        last_reading TEXT,
        device_address TEXT,
        high_pressure_events_per_day REAL,
        water_savings_pct REAL,
        output_set_point REAL,
        telemetry_data TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        UNIQUE(zip_code, neighborhood)
    );

    CREATE INDEX IF NOT EXISTS idx_properties_address ON properties(address, city, state);
    CREATE INDEX IF NOT EXISTS idx_properties_zip ON properties(zip_code);
    CREATE INDEX IF NOT EXISTS idx_properties_state ON properties(state);
    CREATE INDEX IF NOT EXISTS idx_properties_builder ON properties(builder_id);
    CREATE INDEX IF NOT EXISTS idx_builders_state ON builders(state);
    CREATE INDEX IF NOT EXISTS idx_builders_grade ON builders(grade);
    CREATE INDEX IF NOT EXISTS idx_score_cache_hash ON score_cache(address_hash);
    CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
    CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);
    CREATE INDEX IF NOT EXISTS idx_namara_pressure_zip ON namara_pressure_zones(zip_code);
    CREATE INDEX IF NOT EXISTS idx_namara_pressure_neighborhood ON namara_pressure_zones(zip_code, neighborhood);
    """)

    conn.commit()

    # Migrate existing namara_pressure_zones table if missing new columns
    try:
        cols = [row[1] for row in conn.execute("PRAGMA table_info(namara_pressure_zones)").fetchall()]
        migrations = {
            "neighborhood": "TEXT",
            "device_address": "TEXT",
            "high_pressure_events_per_day": "REAL",
            "water_savings_pct": "REAL",
            "output_set_point": "REAL",
            "telemetry_data": "TEXT",
        }
        for col, ctype in migrations.items():
            if col not in cols:
                conn.execute(f"ALTER TABLE namara_pressure_zones ADD COLUMN {col} {ctype}")
        conn.commit()
    except Exception:
        pass

    conn.close()


def seed_device_zones():
    """Seed Namara device zones with real device data from deployed units."""
    conn = get_db()

    # Check if PHR zone already exists
    existing = conn.execute(
        "SELECT id FROM namara_pressure_zones WHERE zip_code = ? AND neighborhood = ?",
        ("92130", "Pacific Highlands Ranch")
    ).fetchone()

    # Always reload telemetry from file so edits take effect
    # Load telemetry data from the Bonneau house device
    telemetry_path = os.path.join(os.path.dirname(__file__), "data", "phr_telemetry.json")
    telemetry_json = None
    if os.path.exists(telemetry_path):
        with open(telemetry_path) as f:
            telemetry_json = f.read()

    if existing:
        # Update telemetry data from file so edits propagate
        conn.execute(
            "UPDATE namara_pressure_zones SET telemetry_data = ?, updated_at = datetime('now') WHERE id = ?",
            (telemetry_json, existing['id'])
        )
    else:
        conn.execute("""
            INSERT INTO namara_pressure_zones
            (zip_code, neighborhood, avg_psi, min_psi, max_psi, device_count,
             last_reading, device_address, high_pressure_events_per_day,
             water_savings_pct, output_set_point, telemetry_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "92130",
            "Pacific Highlands Ranch",
            72.1,   # avg_psi — measured from Bonneau device
            0.0,    # min_psi — drops to 0 during surges
            200.0,  # max_psi — peak surge recorded Sept 26
            1,      # device_count
            "2025-09-29T09:49:54",
            "6085 African Holly Trl",
            23.3,   # high_pressure_events_per_day
            19.7,   # water_savings_pct
            48.0,   # output_set_point
            telemetry_json,
        ))

    conn.commit()
    conn.close()


def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{h.hex()}"


def verify_password(password, password_hash):
    salt, h = password_hash.split(':')
    check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return check.hex() == h


def generate_api_key():
    """Generate a new API key. Returns (full_key, prefix, hash)."""
    key = f"nmr_{secrets.token_hex(24)}"
    prefix = key[:12]
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, prefix, key_hash


def create_user(email, password, company=None, tier='lookup', is_admin=False):
    conn = get_db()
    pw_hash = hash_password(password)
    try:
        conn.execute(
            "INSERT INTO users (email, password_hash, company, tier, is_admin) VALUES (?, ?, ?, ?, ?)",
            (email, pw_hash, company, tier, int(is_admin))
        )
        conn.commit()
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Auto-generate an API key
        key, prefix, key_hash = generate_api_key()
        rate_limits = {'lookup': (10, 100), 'portfolio': (60, 5000), 'enterprise': (120, 50000)}
        rpm, rpd = rate_limits.get(tier, (10, 100))
        conn.execute(
            "INSERT INTO api_keys (user_id, key_hash, key_prefix, tier, rate_limit_per_min, rate_limit_per_day) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, key_hash, prefix, tier, rpm, rpd)
        )
        conn.commit()
        conn.close()
        return user_id, key
    except sqlite3.IntegrityError:
        conn.close()
        return None, None


def authenticate_user(email, password):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row and verify_password(password, row['password_hash']):
        conn.execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (row['id'],))
        conn.commit()
        conn.close()
        return dict(row)
    conn.close()
    return None


def validate_api_key(key):
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    conn = get_db()
    row = conn.execute("""
        SELECT ak.*, u.email, u.company, u.tier as user_tier
        FROM api_keys ak JOIN users u ON ak.user_id = u.id
        WHERE ak.key_hash = ? AND ak.is_active = 1
    """, (key_hash,)).fetchone()
    if row:
        conn.execute("UPDATE api_keys SET last_used = datetime('now') WHERE id = ?", (row['id'],))
        conn.commit()
    conn.close()
    return dict(row) if row else None


def check_rate_limit(api_key_id, rate_limit_per_min):
    conn = get_db()
    window = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    row = conn.execute(
        "SELECT request_count FROM rate_limits WHERE api_key_id = ? AND window_start = ?",
        (api_key_id, window)
    ).fetchone()
    if row:
        if row['request_count'] >= rate_limit_per_min:
            conn.close()
            return False
        conn.execute(
            "UPDATE rate_limits SET request_count = request_count + 1 WHERE api_key_id = ? AND window_start = ?",
            (api_key_id, window)
        )
    else:
        conn.execute(
            "INSERT OR IGNORE INTO rate_limits (api_key_id, window_start) VALUES (?, ?)",
            (api_key_id, window)
        )
    conn.commit()
    conn.close()
    return True


def log_request(user_id, api_key_id, action, endpoint, address=None, zip_code=None, response_code=200, response_time_ms=0):
    conn = get_db()
    conn.execute(
        "INSERT INTO audit_log (user_id, api_key_id, action, endpoint, address, zip_code, response_code, response_time_ms) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, api_key_id, action, endpoint, address, zip_code, response_code, response_time_ms)
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
