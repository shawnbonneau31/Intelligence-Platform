"""
Namara Water Risk Intelligence Platform — Database Seeder
Seeds all reference data: water quality, housing age, regulatory, and sample FL builders.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "namara.db")


def seed_water_quality(conn):
    """Seed EPA/USGS water quality data by state."""
    data = [
        ("AL", 18.5, 3.2, 62, 52), ("AK", 8.2, 1.1, 45, 28), ("AZ", 22.7, 4.8, 58, 55),
        ("AR", 15.3, 2.8, 65, 48), ("CA", 19.8, 3.5, 52, 49), ("CO", 12.1, 2.0, 48, 38),
        ("CT", 10.5, 1.8, 72, 45), ("DE", 14.2, 2.5, 68, 47), ("DC", 16.8, 3.8, 75, 56),
        ("FL", 24.6, 5.2, 55, 58), ("GA", 20.1, 3.9, 60, 54), ("HI", 6.8, 0.8, 42, 22),
        ("ID", 9.5, 1.5, 44, 30), ("IL", 17.2, 3.1, 70, 52), ("IN", 19.5, 3.6, 68, 55),
        ("IA", 21.3, 4.0, 66, 56), ("KS", 16.8, 3.0, 62, 50), ("KY", 18.0, 3.3, 64, 51),
        ("LA", 23.5, 4.5, 70, 60), ("ME", 8.8, 1.2, 55, 32), ("MD", 15.5, 2.8, 65, 48),
        ("MA", 11.2, 1.9, 70, 44), ("MI", 16.5, 3.2, 72, 52), ("MN", 10.8, 1.6, 55, 36),
        ("MS", 22.0, 4.2, 72, 60), ("MO", 17.5, 3.2, 65, 52), ("MT", 7.5, 1.0, 42, 24),
        ("NE", 14.2, 2.4, 58, 42), ("NV", 20.5, 3.8, 50, 50), ("NH", 9.2, 1.3, 58, 34),
        ("NJ", 14.8, 2.6, 72, 50), ("NM", 18.8, 3.5, 55, 50), ("NY", 13.5, 2.2, 75, 48),
        ("NC", 16.2, 2.9, 58, 46), ("ND", 11.5, 1.8, 52, 36), ("OH", 18.8, 3.5, 72, 55),
        ("OK", 19.2, 3.6, 60, 53), ("OR", 8.5, 1.2, 48, 28), ("PA", 15.8, 2.8, 75, 52),
        ("RI", 11.8, 2.0, 70, 44), ("SC", 17.5, 3.2, 58, 48), ("SD", 12.2, 1.8, 52, 36),
        ("TN", 16.8, 3.0, 62, 50), ("TX", 21.5, 4.2, 58, 56), ("UT", 10.2, 1.5, 45, 32),
        ("VT", 8.5, 1.2, 60, 34), ("VA", 14.5, 2.5, 60, 44), ("WA", 9.8, 1.4, 50, 30),
        ("WV", 20.2, 3.8, 75, 58), ("WI", 11.5, 1.8, 62, 40), ("WY", 7.8, 1.0, 40, 22),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO water_quality (state, violations_per_100k, lead_copper_exceedances, treatment_age_score, composite_score) VALUES (?, ?, ?, ?, ?)",
        data
    )


def seed_housing_age(conn):
    """Seed Census ACS housing age data by state."""
    data = [
        ("AL", 1985, 28.5, 12.8, 48), ("AK", 1982, 22.0, 8.5, 42), ("AZ", 1992, 18.2, 6.5, 35),
        ("AR", 1980, 32.5, 15.2, 55), ("CA", 1975, 38.5, 18.8, 58), ("CO", 1990, 22.8, 8.2, 38),
        ("CT", 1966, 48.5, 28.2, 72), ("DE", 1978, 35.2, 16.5, 56), ("DC", 1952, 55.0, 38.5, 80),
        ("FL", 1990, 20.5, 7.8, 38), ("GA", 1992, 18.8, 7.2, 35), ("HI", 1980, 28.0, 12.0, 45),
        ("ID", 1992, 16.5, 5.8, 32), ("IL", 1968, 45.2, 25.5, 68), ("IN", 1972, 40.8, 22.2, 62),
        ("IA", 1965, 48.0, 28.8, 72), ("KS", 1972, 38.5, 20.5, 60), ("KY", 1980, 32.0, 15.0, 52),
        ("LA", 1982, 30.5, 14.2, 50), ("ME", 1970, 42.5, 24.0, 65), ("MD", 1978, 35.8, 17.2, 56),
        ("MA", 1960, 52.0, 32.5, 76), ("MI", 1970, 42.0, 23.5, 64), ("MN", 1978, 32.5, 14.8, 52),
        ("MS", 1982, 30.0, 13.8, 48), ("MO", 1972, 38.0, 20.2, 58), ("MT", 1978, 30.5, 14.5, 48),
        ("NE", 1972, 38.2, 20.0, 58), ("NV", 1998, 12.5, 4.2, 25), ("NH", 1975, 35.0, 16.8, 55),
        ("NJ", 1965, 48.8, 28.5, 72), ("NM", 1985, 25.8, 10.5, 42), ("NY", 1958, 52.5, 34.0, 78),
        ("NC", 1988, 22.5, 8.8, 38), ("ND", 1972, 35.5, 18.0, 55), ("OH", 1968, 44.0, 25.0, 66),
        ("OK", 1978, 32.8, 15.5, 52), ("OR", 1980, 30.2, 13.5, 48), ("PA", 1962, 50.0, 30.5, 74),
        ("RI", 1958, 52.8, 34.5, 78), ("SC", 1990, 20.8, 8.0, 36), ("SD", 1975, 35.0, 18.5, 55),
        ("TN", 1985, 27.5, 12.0, 45), ("TX", 1990, 20.0, 7.5, 36), ("UT", 1992, 18.0, 6.0, 32),
        ("VT", 1968, 45.0, 26.0, 68), ("VA", 1985, 26.5, 11.5, 44), ("WA", 1982, 28.0, 11.8, 44),
        ("WV", 1970, 42.0, 24.5, 66), ("WI", 1972, 38.5, 20.8, 60), ("WY", 1980, 28.5, 12.5, 45),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO housing_age (state, median_year_built, pct_pre_1980, pct_pre_1960, infrastructure_score) VALUES (?, ?, ?, ?, ?)",
        data
    )


def seed_regulatory(conn):
    """Seed regulatory/mandate data by state."""
    data = [
        ("AL", 0, 0, 0, 2015, 72), ("AK", 0, 0, 0, 2012, 78), ("AZ", 0, 0, 0, 2018, 65),
        ("AR", 0, 0, 0, 2012, 75), ("CA", 1, 1, 1, 2022, 25), ("CO", 0, 0, 0, 2018, 62),
        ("CT", 0, 0, 0, 2015, 68), ("DE", 0, 0, 0, 2015, 70), ("DC", 0, 0, 1, 2018, 55),
        ("FL", 1, 0, 1, 2023, 35), ("GA", 0, 0, 0, 2018, 65), ("HI", 0, 0, 0, 2012, 72),
        ("ID", 0, 0, 0, 2015, 75), ("IL", 0, 0, 0, 2018, 65), ("IN", 0, 0, 0, 2015, 72),
        ("IA", 0, 0, 0, 2012, 75), ("KS", 0, 0, 0, 2012, 78), ("KY", 0, 0, 0, 2012, 75),
        ("LA", 0, 0, 0, 2015, 72), ("ME", 0, 0, 0, 2012, 75), ("MD", 0, 0, 0, 2018, 65),
        ("MA", 0, 0, 1, 2018, 52), ("MI", 0, 0, 0, 2015, 70), ("MN", 0, 0, 0, 2018, 65),
        ("MS", 0, 0, 0, 2012, 78), ("MO", 0, 0, 0, 2012, 75), ("MT", 0, 0, 0, 2012, 80),
        ("NE", 0, 0, 0, 2012, 78), ("NV", 0, 0, 0, 2018, 65), ("NH", 0, 0, 0, 2012, 75),
        ("NJ", 0, 0, 0, 2018, 68), ("NM", 0, 0, 0, 2015, 72), ("NY", 0, 0, 1, 2020, 50),
        ("NC", 0, 0, 0, 2018, 68), ("ND", 0, 0, 0, 2012, 80), ("OH", 0, 0, 0, 2015, 72),
        ("OK", 0, 0, 0, 2012, 78), ("OR", 0, 0, 0, 2018, 65), ("PA", 0, 0, 0, 2015, 70),
        ("RI", 0, 0, 0, 2015, 72), ("SC", 0, 0, 0, 2018, 68), ("SD", 0, 0, 0, 2012, 80),
        ("TN", 0, 0, 0, 2015, 72), ("TX", 0, 0, 0, 2018, 65), ("UT", 0, 0, 0, 2018, 65),
        ("VT", 0, 0, 0, 2012, 75), ("VA", 0, 0, 0, 2018, 68), ("WA", 0, 0, 0, 2020, 58),
        ("WV", 0, 0, 0, 2012, 78), ("WI", 0, 0, 0, 2015, 72), ("WY", 0, 0, 0, 2012, 82),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO regulatory (state, leak_detection_mandate, auto_shutoff_mandate, insurance_incentive, building_code_year, compliance_score) VALUES (?, ?, ?, ?, ?, ?)",
        data
    )


def seed_builders_fl(conn):
    """Seed sample Florida builder quality data — top 50 builders."""
    # Clear existing builders to prevent duplicates on re-seed
    conn.execute("DELETE FROM builders")
    builders = [
        # (name, state, license, callback_rate, plumbing, code_viol, litigation, volume, appliance, drainage, composite, grade, homes, year_est, specialties)
        ("Lennar Homes", "FL", "CBC1261010", 82, 85, 78, 72, 65, 80, 82, 78.4, "B", 48500, 1954, "Production homes, master-planned communities"),
        ("D.R. Horton", "FL", "CBC1260968", 75, 80, 72, 68, 60, 75, 78, 73.2, "B", 52000, 1978, "Entry-level and move-up homes"),
        ("PulteGroup", "FL", "CBC1261045", 85, 88, 82, 80, 70, 85, 85, 82.8, "B", 28000, 1950, "Active adult communities, custom homes"),
        ("Toll Brothers", "FL", "CBC1261102", 92, 95, 90, 88, 78, 92, 90, 90.8, "A", 8500, 1967, "Luxury homes and estates"),
        ("GL Homes", "FL", "CBC1254093", 88, 90, 85, 82, 72, 88, 86, 85.6, "A", 12000, 1976, "Upscale planned communities"),
        ("Maronda Homes", "FL", "CBC1258498", 70, 72, 68, 65, 58, 70, 72, 68.2, "C", 18000, 1972, "Affordable single-family homes"),
        ("KB Home", "FL", "CBC1261022", 78, 82, 75, 70, 62, 78, 80, 75.8, "B", 35000, 1957, "Energy-efficient, built-to-order homes"),
        ("Taylor Morrison", "FL", "CBC1261055", 86, 88, 84, 80, 72, 86, 84, 83.6, "B", 9500, 2007, "Move-up and luxury homes"),
        ("Meritage Homes", "FL", "CBC1261078", 84, 90, 82, 78, 68, 85, 82, 82.2, "B", 14000, 1985, "Energy-efficient production homes"),
        ("WCI Communities", "FL", "CBC1253890", 72, 75, 70, 62, 55, 72, 74, 69.2, "C", 6500, 1946, "Waterfront and tower communities"),
        ("ICI Homes", "FL", "CBC1257834", 90, 92, 88, 85, 75, 90, 88, 87.8, "A", 4200, 1980, "Custom and semi-custom homes"),
        ("Kolter Homes", "FL", "CBC1260145", 88, 90, 86, 82, 72, 88, 86, 85.4, "A", 3800, 2001, "Upscale active adult and family communities"),
        ("Neal Communities", "FL", "CBC1258921", 91, 94, 90, 88, 78, 92, 90, 89.6, "A", 5500, 1970, "Custom homes, Southwest FL"),
        ("Holiday Builders", "FL", "CBC1255678", 68, 70, 65, 60, 52, 68, 70, 65.0, "C", 22000, 1984, "Affordable single-family, entry-level"),
        ("Adams Homes", "FL", "CBC1256789", 65, 68, 62, 58, 50, 65, 68, 62.4, "C", 30000, 1991, "Budget-friendly homes"),
        ("David Weekley Homes", "FL", "CBC1260234", 92, 95, 90, 88, 80, 92, 90, 90.6, "A", 7000, 1976, "Custom homes, energy-efficient design"),
        ("Minto Communities", "FL", "CBC1259876", 87, 90, 85, 82, 74, 88, 86, 85.0, "A", 5000, 1955, "Master-planned, active adult"),
        ("AV Homes / Taylor Morrison", "FL", "CBC1260567", 80, 82, 78, 75, 65, 80, 80, 78.0, "B", 8000, 2003, "55+ active adult communities"),
        ("M/I Homes", "FL", "CBC1261234", 84, 86, 82, 78, 70, 84, 82, 81.6, "B", 6200, 1976, "Single-family, smart home features"),
        ("Centex (PulteGroup)", "FL", "CBC1261045", 76, 80, 74, 70, 62, 76, 78, 74.8, "B", 15000, 1950, "Value-oriented production homes"),
        ("CalAtlantic (Lennar)", "FL", "CBC1261010", 80, 84, 78, 74, 66, 80, 80, 78.4, "B", 12000, 2015, "Mid-range single-family"),
        ("Ashton Woods", "FL", "CBC1260890", 88, 92, 86, 84, 75, 88, 86, 86.2, "A", 4000, 1989, "Design-focused, energy-efficient"),
        ("Park Square Homes", "FL", "CBC1259012", 82, 85, 80, 76, 68, 82, 82, 80.0, "B", 3500, 2006, "Central FL, family-oriented"),
        ("Dream Finders Homes", "FL", "CBC1260456", 86, 88, 84, 80, 72, 86, 84, 83.4, "B", 5800, 2008, "Northeast FL, customizable designs"),
        ("Mattamy Homes", "FL", "CBC1261345", 84, 86, 82, 78, 70, 84, 82, 81.4, "B", 7500, 1978, "Canadian builder, master-planned communities"),
        ("Beazer Homes", "FL", "CBC1260678", 74, 78, 72, 68, 60, 74, 76, 72.4, "B", 10000, 1985, "Mortgage Choice, energy-efficient"),
        ("Stanley Martin Homes", "FL", "CBC1261456", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 3200, 1966, "Move-up and luxury homes"),
        ("Ryan Homes (NVR)", "FL", "CBC1261567", 72, 76, 70, 66, 58, 72, 74, 70.4, "B", 20000, 1948, "Production homes, fixed-price"),
        ("LGI Homes", "FL", "CBC1261678", 62, 65, 60, 55, 48, 62, 65, 60.0, "C", 25000, 2003, "Entry-level, first-time buyers"),
        ("Century Complete", "FL", "CBC1261789", 60, 62, 58, 52, 45, 60, 62, 57.4, "C", 18000, 2019, "Online-only, affordable homes"),
        ("Smith Douglas Homes", "FL", "CBC1261890", 78, 80, 76, 72, 64, 78, 78, 76.0, "B", 4500, 2009, "Value-conscious, Southeast markets"),
        ("Cardel Homes", "FL", "CBC1261901", 90, 92, 88, 86, 78, 90, 88, 88.2, "A", 2000, 1973, "Custom homes, Tampa Bay area"),
        ("William Ryan Homes", "FL", "CBC1262012", 88, 90, 86, 84, 76, 88, 86, 86.0, "A", 2500, 1992, "Semi-custom, Midwest and FL"),
        ("Highland Homes", "FL", "CBC1259234", 82, 84, 80, 76, 68, 82, 82, 79.8, "B", 6000, 1996, "Central FL, affordable luxury"),
        ("Mercedes Homes", "FL", "CBC1254567", 70, 72, 68, 62, 55, 70, 72, 67.6, "C", 9000, 1984, "Now Lennar subsidiary"),
        ("Arthur Rutenberg Homes", "FL", "CBC1252345", 94, 96, 92, 90, 82, 94, 92, 92.4, "A", 3000, 1953, "Luxury custom, franchise model"),
        ("Homes by WestBay", "FL", "CBC1260789", 88, 90, 86, 84, 76, 88, 86, 86.0, "A", 2800, 2009, "Tampa Bay, luxury single-family"),
        ("Standard Pacific (CalAtlantic)", "FL", "CBC1259345", 78, 80, 76, 72, 64, 78, 78, 75.8, "B", 5000, 1991, "Now merged into Lennar"),
        ("M.D.C. Holdings", "FL", "CBC1261098", 80, 82, 78, 74, 66, 80, 80, 78.0, "B", 8500, 1972, "Richmond American Homes brand"),
        ("Shea Homes", "FL", "CBC1260987", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 4200, 1881, "Active adult and family communities"),
        ("Ryland Homes (CalAtlantic)", "FL", "CBC1259456", 76, 78, 74, 70, 62, 76, 76, 74.0, "B", 7000, 1967, "Now merged into Lennar"),
        ("K. Hovnanian", "FL", "CBC1260876", 72, 74, 70, 65, 58, 72, 72, 69.8, "C", 11000, 1959, "Production homes, various price points"),
        ("Crespo Custom Homes", "FL", "CBC1258765", 95, 98, 94, 92, 85, 96, 94, 94.2, "A", 400, 1998, "Ultra-luxury custom, South FL"),
        ("London Bay Homes", "FL", "CBC1257654", 96, 98, 95, 94, 88, 96, 94, 95.0, "A", 350, 1990, "Ultra-luxury custom, Naples area"),
        ("Stock Development", "FL", "CBC1258543", 92, 94, 90, 88, 80, 92, 90, 90.4, "A", 1800, 2001, "Luxury communities, Southwest FL"),
        ("WCI Homes", "FL", "CBC1253980", 74, 76, 72, 68, 60, 74, 74, 72.0, "B", 5000, 1946, "Coastal and tower communities"),
        ("Medallion Homes", "FL", "CBC1259098", 84, 86, 82, 80, 72, 84, 82, 82.0, "B", 3200, 1984, "Sarasota/Manatee area"),
        ("Lee Wetherington Homes", "FL", "CBC1258432", 92, 94, 90, 88, 80, 92, 90, 90.2, "A", 1200, 1975, "Luxury custom, Sarasota area"),
        ("Divosta Homes (PulteGroup)", "FL", "CBC1254321", 80, 82, 78, 75, 66, 80, 80, 78.0, "B", 4500, 1946, "Concrete block construction specialist"),
        ("Avex Homes", "FL", "CBC1261543", 78, 80, 76, 72, 64, 78, 78, 75.4, "B", 1500, 2014, "Central FL, modern designs"),
    ]

    for b in builders:
        conn.execute("""
            INSERT OR REPLACE INTO builders
            (name, state, license_number, callback_rate, plumbing_material_score, code_violation_score,
             litigation_score, construction_volume_score, appliance_score, drainage_score,
             composite_score, grade, homes_built, year_established, specialties)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, b)


def seed_all():
    """Run all seeders."""
    from database import init_db, create_user
    init_db()

    conn = sqlite3.connect(DB_PATH)

    print("Seeding water quality data...")
    seed_water_quality(conn)

    print("Seeding housing age data...")
    seed_housing_age(conn)

    print("Seeding regulatory data...")
    seed_regulatory(conn)

    print("Seeding FL builder data (50 builders)...")
    seed_builders_fl(conn)

    conn.commit()
    conn.close()

    # Create default admin user and demo user
    print("Creating admin user...")
    uid, key = create_user("admin@namarawater.ai", "namara2026!", "Namara Water Technologies", "enterprise", True)
    if uid:
        print(f"  Admin API key: {key}")

    print("Creating demo user...")
    uid, key = create_user("demo@namarawater.ai", "demo2026", "Demo Account", "portfolio")
    if uid:
        print(f"  Demo API key: {key}")

    print("Database seeded successfully!")


if __name__ == "__main__":
    seed_all()
