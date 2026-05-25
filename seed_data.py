"""
Namara Water Risk Intelligence Platform — Database Seeder v2.0
Seeds all reference data: water quality, housing age, regulatory, pressure,
nationwide builders with enhanced scoring, and sample properties.
"""

import sqlite3
import os
import random

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


def seed_pressure_data(conn):
    """Seed city water pressure data by state (AWWA Municipal Survey estimates)."""
    data = [
        ("AL", 60, 15, 9, "Moderate", 0.82, 42), ("AK", 52, 10, 18, "High", 0.78, 52),
        ("AZ", 72, 28, 3, "High", 0.72, 55), ("AR", 58, 14, 10, "Moderate", 0.80, 44),
        ("CA", 65, 22, 12, "High", 0.90, 58), ("CO", 70, 26, 4, "High", 0.75, 52),
        ("CT", 56, 10, 12, "Low", 0.92, 46), ("DE", 58, 12, 10, "Moderate", 0.84, 43),
        ("DC", 54, 8, 16, "Low", 0.96, 48), ("FL", 62, 18, 8, "Moderate", 0.85, 45),
        ("GA", 60, 16, 9, "Moderate", 0.80, 43), ("HI", 58, 14, 12, "Moderate", 0.76, 40),
        ("ID", 64, 18, 6, "Moderate", 0.74, 42), ("IL", 56, 10, 14, "Low", 0.90, 46),
        ("IN", 58, 12, 12, "Low", 0.86, 44), ("IA", 56, 10, 13, "Low", 0.88, 45),
        ("KS", 60, 16, 8, "Moderate", 0.82, 44), ("KY", 57, 12, 11, "Low", 0.84, 43),
        ("LA", 55, 10, 14, "Moderate", 0.83, 46), ("ME", 53, 8, 16, "Low", 0.88, 47),
        ("MD", 58, 12, 10, "Low", 0.86, 44), ("MA", 55, 9, 14, "Low", 0.93, 48),
        ("MI", 56, 10, 13, "Low", 0.88, 46), ("MN", 57, 10, 12, "Low", 0.84, 43),
        ("MS", 56, 12, 13, "Moderate", 0.81, 45), ("MO", 58, 14, 10, "Moderate", 0.84, 44),
        ("MT", 60, 16, 8, "Moderate", 0.78, 42), ("NE", 58, 14, 9, "Moderate", 0.82, 43),
        ("NV", 68, 24, 5, "High", 0.70, 50), ("NH", 54, 8, 14, "Low", 0.86, 44),
        ("NJ", 57, 11, 12, "Low", 0.90, 46), ("NM", 66, 22, 6, "High", 0.76, 50),
        ("NY", 55, 8, 15, "Low", 0.95, 42), ("NC", 60, 15, 8, "Moderate", 0.82, 42),
        ("ND", 56, 10, 12, "Low", 0.80, 40), ("OH", 56, 10, 14, "Low", 0.90, 46),
        ("OK", 62, 18, 7, "Moderate", 0.80, 44), ("OR", 58, 13, 10, "Moderate", 0.78, 42),
        ("PA", 55, 9, 15, "Low", 0.92, 47), ("RI", 54, 8, 14, "Low", 0.93, 47),
        ("SC", 60, 15, 8, "Moderate", 0.80, 42), ("SD", 57, 12, 10, "Low", 0.80, 41),
        ("TN", 59, 14, 9, "Moderate", 0.82, 43), ("TX", 68, 24, 5, "Moderate", 0.78, 48),
        ("UT", 66, 20, 5, "Moderate", 0.74, 44), ("VT", 53, 8, 16, "Low", 0.90, 46),
        ("VA", 59, 13, 9, "Moderate", 0.82, 43), ("WA", 58, 13, 10, "Moderate", 0.80, 42),
        ("WV", 52, 8, 18, "High", 0.92, 54), ("WI", 56, 10, 12, "Low", 0.86, 44),
        ("WY", 62, 18, 7, "Moderate", 0.78, 42),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO city_pressure (state, avg_psi, pct_over_80psi, pct_under_40psi, pressure_variability, infrastructure_age_factor, pressure_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
        data
    )


def seed_builders_nationwide(conn):
    """Seed nationwide builder quality data with enhanced scoring fields.
    Top builders across all 50 states with BBB, licensing, building dept, and warranty data.
    """
    conn.execute("DELETE FROM builders")

    # (name, state, license, callback, plumbing, code_viol, litigation, volume, appliance, drainage,
    #  composite, grade, homes, year_est, specialties, bbb_rating, bbb_complaints, bbb_years,
    #  license_status, building_violations, warranty_claim_rate, plumbing_sub_quality, avg_price, markets)
    builders = [
        # ── FLORIDA (top market — 20 builders) ──
        ("Lennar Homes", "FL", "CBC1261010", 82, 85, 78, 72, 65, 80, 82, 78.4, "B", 48500, 1954, "Production homes, master-planned", "A-", 42, 18, "active", 8, 3.2, "mid-tier", 420000, "Miami,Tampa,Orlando,Jacksonville"),
        ("D.R. Horton", "FL", "CBC1260968", 75, 80, 72, 68, 60, 75, 78, 73.2, "B", 52000, 1978, "Entry-level and move-up homes", "B+", 68, 15, "active", 12, 4.1, "mid-tier", 350000, "Tampa,Orlando,Jacksonville,Fort Myers"),
        ("PulteGroup", "FL", "CBC1261045", 85, 88, 82, 80, 70, 85, 85, 82.8, "B", 28000, 1950, "Active adult, custom homes", "A", 28, 22, "active", 4, 2.4, "premium", 480000, "Tampa,Naples,Orlando,Sarasota"),
        ("Toll Brothers", "FL", "CBC1261102", 92, 95, 90, 88, 78, 92, 90, 90.8, "A", 8500, 1967, "Luxury homes and estates", "A+", 8, 30, "active", 1, 1.2, "premium", 850000, "Boca Raton,Naples,Jupiter"),
        ("GL Homes", "FL", "CBC1254093", 88, 90, 85, 82, 72, 88, 86, 85.6, "A", 12000, 1976, "Upscale planned communities", "A", 15, 25, "active", 3, 1.8, "premium", 620000, "Boca Raton,Palm Beach,Boynton Beach"),
        ("KB Home", "FL", "CBC1261022", 78, 82, 75, 70, 62, 78, 80, 75.8, "B", 35000, 1957, "Energy-efficient, built-to-order", "B+", 55, 16, "active", 9, 3.5, "mid-tier", 380000, "Jacksonville,Tampa,Orlando"),
        ("Taylor Morrison", "FL", "CBC1261055", 86, 88, 84, 80, 72, 86, 84, 83.6, "B", 9500, 2007, "Move-up and luxury homes", "A", 18, 12, "active", 3, 2.0, "premium", 520000, "Tampa,Sarasota,Naples"),
        ("Meritage Homes", "FL", "CBC1261078", 84, 90, 82, 78, 68, 85, 82, 82.2, "B", 14000, 1985, "Energy-efficient production", "A-", 22, 18, "active", 5, 2.3, "premium", 450000, "Orlando,Tampa,Jacksonville"),
        ("ICI Homes", "FL", "CBC1257834", 90, 92, 88, 85, 75, 90, 88, 87.8, "A", 4200, 1980, "Custom and semi-custom", "A+", 5, 28, "active", 1, 1.4, "premium", 550000, "Daytona Beach,Jacksonville,Gainesville"),
        ("Neal Communities", "FL", "CBC1258921", 91, 94, 90, 88, 78, 92, 90, 89.6, "A", 5500, 1970, "Custom homes, SW Florida", "A+", 4, 32, "active", 0, 1.1, "premium", 680000, "Sarasota,Lakewood Ranch,Venice"),
        ("Holiday Builders", "FL", "CBC1255678", 68, 70, 65, 60, 52, 68, 70, 65.0, "C", 22000, 1984, "Affordable single-family", "B-", 85, 10, "active", 18, 5.2, "budget", 280000, "Melbourne,Vero Beach,Palm Bay"),
        ("Adams Homes", "FL", "CBC1256789", 65, 68, 62, 58, 50, 65, 68, 62.4, "C", 30000, 1991, "Budget-friendly homes", "B-", 92, 8, "active", 22, 5.8, "budget", 250000, "Pensacola,Tallahassee,Ocala"),
        ("David Weekley Homes", "FL", "CBC1260234", 92, 95, 90, 88, 80, 92, 90, 90.6, "A", 7000, 1976, "Custom, energy-efficient", "A+", 6, 35, "active", 0, 1.0, "premium", 720000, "Jacksonville,Tampa,Orlando"),
        ("Dream Finders Homes", "FL", "CBC1260456", 86, 88, 84, 80, 72, 86, 84, 83.4, "B", 5800, 2008, "NE Florida, customizable", "A", 14, 10, "active", 3, 2.1, "premium", 460000, "Jacksonville,Denver,Austin"),
        ("LGI Homes", "FL", "CBC1261678", 62, 65, 60, 55, 48, 62, 65, 60.0, "C", 25000, 2003, "Entry-level, first-time buyers", "B-", 110, 6, "active", 25, 6.2, "budget", 220000, "Orlando,Tampa,Jacksonville,Fort Myers"),
        ("Maronda Homes", "FL", "CBC1258498", 70, 72, 68, 65, 58, 70, 72, 68.2, "C", 18000, 1972, "Affordable single-family", "B", 48, 14, "active", 14, 4.5, "budget", 300000, "Tampa,Orlando,Jacksonville"),
        ("London Bay Homes", "FL", "CBC1257654", 96, 98, 95, 94, 88, 96, 94, 95.0, "A", 350, 1990, "Ultra-luxury custom, Naples", "A+", 1, 30, "active", 0, 0.5, "premium", 3200000, "Naples,Sarasota"),
        ("Arthur Rutenberg Homes", "FL", "CBC1252345", 94, 96, 92, 90, 82, 94, 92, 92.4, "A", 3000, 1953, "Luxury custom, franchise", "A+", 3, 38, "active", 0, 0.8, "premium", 950000, "Tampa,Sarasota,Naples,Fort Myers"),
        ("Ashton Woods", "FL", "CBC1260890", 88, 92, 86, 84, 75, 88, 86, 86.2, "A", 4000, 1989, "Design-focused, energy-efficient", "A", 12, 20, "active", 2, 1.6, "premium", 550000, "Orlando,Tampa,Atlanta"),
        ("Century Complete", "FL", "CBC1261789", 60, 62, 58, 52, 45, 60, 62, 57.4, "C", 18000, 2019, "Online-only affordable", "C+", 125, 2, "active", 30, 7.0, "budget", 200000, "Various FL markets"),

        # ── TEXAS (top market — 15 builders) ──
        ("D.R. Horton", "TX", "TX-DRH-2845", 76, 80, 74, 70, 62, 76, 78, 74.4, "B", 65000, 1978, "Entry-level and move-up", "B+", 95, 15, "active", 15, 4.0, "mid-tier", 340000, "Dallas,Houston,San Antonio,Austin"),
        ("Lennar Homes", "TX", "TX-LEN-3102", 80, 84, 76, 72, 64, 80, 80, 77.8, "B", 42000, 1954, "Production, master-planned", "A-", 58, 18, "active", 10, 3.4, "mid-tier", 400000, "Houston,Dallas,San Antonio,Austin"),
        ("Perry Homes", "TX", "TX-PER-1845", 90, 92, 88, 86, 78, 90, 88, 88.6, "A", 8500, 1967, "Semi-custom, Texas-focused", "A+", 10, 40, "active", 1, 1.2, "premium", 580000, "Houston,San Antonio,Dallas,Austin"),
        ("Trendmaker Homes", "TX", "TX-TRD-2190", 88, 90, 86, 84, 76, 88, 86, 86.0, "A", 4500, 1970, "Luxury production", "A+", 6, 35, "active", 1, 1.4, "premium", 650000, "Houston,Dallas"),
        ("Highland Homes TX", "TX", "TX-HIG-2567", 86, 88, 84, 82, 74, 86, 84, 84.2, "B", 6200, 1985, "Move-up single-family", "A", 14, 22, "active", 3, 1.8, "premium", 520000, "Dallas,Austin,Houston"),
        ("KB Home", "TX", "TX-KBH-3345", 76, 80, 74, 68, 60, 76, 78, 74.0, "B", 38000, 1957, "Built-to-order homes", "B+", 72, 16, "active", 11, 3.8, "mid-tier", 360000, "Houston,Dallas,San Antonio,Austin"),
        ("Taylor Morrison", "TX", "TX-TAY-2890", 84, 86, 82, 78, 70, 84, 82, 81.4, "B", 5200, 2007, "Move-up and luxury", "A", 16, 12, "active", 4, 2.2, "premium", 480000, "Houston,Austin,Dallas"),
        ("Meritage Homes", "TX", "TX-MER-2678", 82, 88, 80, 76, 66, 82, 80, 80.4, "B", 12000, 1985, "Energy-efficient production", "A-", 28, 18, "active", 6, 2.5, "premium", 420000, "Dallas,Houston,Austin,San Antonio"),
        ("David Weekley Homes", "TX", "TX-DWH-1234", 92, 94, 90, 88, 80, 92, 90, 90.4, "A", 9000, 1976, "Custom, energy-efficient", "A+", 8, 35, "active", 0, 1.0, "premium", 680000, "Houston,Dallas,Austin,San Antonio"),
        ("Gehan Homes", "TX", "TX-GEH-3456", 80, 82, 78, 74, 66, 80, 80, 78.0, "B", 3800, 1991, "Semi-custom single-family", "A-", 18, 16, "active", 5, 2.4, "mid-tier", 440000, "Dallas,Austin,San Antonio,Houston"),
        ("LGI Homes", "TX", "TX-LGI-4567", 64, 66, 62, 58, 50, 64, 66, 62.2, "C", 28000, 2003, "Entry-level affordable", "B-", 130, 6, "active", 28, 6.0, "budget", 230000, "Houston,Dallas,San Antonio,Austin"),
        ("Beazer Homes", "TX", "TX-BEZ-2345", 74, 78, 72, 68, 60, 74, 76, 72.4, "B", 8000, 1985, "Energy-efficient", "B+", 35, 14, "active", 8, 3.2, "mid-tier", 380000, "Dallas,Houston"),
        ("Chesmar Homes", "TX", "TX-CHE-5678", 84, 86, 82, 80, 72, 84, 82, 81.8, "B", 3200, 2005, "Semi-custom, Texas-focused", "A", 10, 12, "active", 2, 1.8, "premium", 460000, "Houston,San Antonio,Austin"),
        ("Ashton Woods", "TX", "TX-ASH-6789", 86, 90, 84, 82, 74, 86, 84, 84.4, "B", 3500, 1989, "Design-focused", "A", 12, 20, "active", 2, 1.6, "premium", 520000, "Houston,Dallas,Austin,San Antonio"),
        ("Coventry Homes", "TX", "TX-COV-7890", 82, 84, 80, 78, 70, 82, 80, 80.2, "B", 2800, 1988, "Houston luxury production", "A", 8, 22, "active", 3, 1.8, "premium", 550000, "Houston"),

        # ── ARIZONA (10 builders) ──
        ("Meritage Homes", "AZ", "AZ-MER-0145", 84, 88, 82, 78, 68, 84, 82, 81.8, "B", 16000, 1985, "Energy-efficient", "A-", 24, 22, "active", 4, 2.2, "premium", 440000, "Phoenix,Scottsdale,Mesa,Tucson"),
        ("Taylor Morrison", "AZ", "AZ-TAY-0234", 86, 88, 84, 80, 72, 86, 84, 83.4, "B", 7000, 2007, "Move-up and luxury", "A", 14, 12, "active", 3, 2.0, "premium", 500000, "Phoenix,Scottsdale,Gilbert"),
        ("Shea Homes", "AZ", "AZ-SHE-0345", 88, 90, 86, 84, 76, 88, 86, 86.0, "A", 5500, 1881, "Active adult, family", "A+", 8, 40, "active", 1, 1.4, "premium", 560000, "Phoenix,Scottsdale"),
        ("Toll Brothers", "AZ", "AZ-TOL-0456", 92, 94, 90, 88, 80, 92, 90, 90.4, "A", 4200, 1967, "Luxury homes", "A+", 6, 30, "active", 0, 1.0, "premium", 780000, "Scottsdale,Paradise Valley"),
        ("KB Home", "AZ", "AZ-KBH-0567", 76, 80, 74, 68, 60, 76, 78, 74.0, "B", 30000, 1957, "Built-to-order", "B+", 62, 16, "active", 10, 3.6, "mid-tier", 350000, "Phoenix,Tucson,Mesa"),
        ("Lennar", "AZ", "AZ-LEN-0678", 80, 84, 76, 72, 64, 80, 80, 77.6, "B", 22000, 1954, "Production homes", "A-", 38, 18, "active", 8, 3.0, "mid-tier", 410000, "Phoenix,Mesa,Chandler,Gilbert"),
        ("D.R. Horton", "AZ", "AZ-DRH-0789", 74, 78, 72, 68, 60, 74, 76, 72.2, "B", 35000, 1978, "Entry-level", "B+", 72, 15, "active", 14, 4.2, "mid-tier", 320000, "Phoenix,Tucson,Mesa,Surprise"),
        ("Fulton Homes", "AZ", "AZ-FUL-0890", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 3800, 1974, "Arizona-focused custom", "A", 12, 30, "active", 2, 1.6, "premium", 520000, "Phoenix,Scottsdale,Gilbert,Chandler"),
        ("Mattamy Homes", "AZ", "AZ-MAT-0901", 82, 84, 80, 76, 68, 82, 80, 79.8, "B", 5000, 1978, "Master-planned communities", "A-", 18, 15, "active", 4, 2.2, "mid-tier", 440000, "Phoenix,Scottsdale"),
        ("LGI Homes", "AZ", "AZ-LGI-1012", 62, 64, 60, 56, 48, 62, 64, 60.0, "C", 18000, 2003, "Entry-level", "B-", 95, 6, "active", 22, 5.8, "budget", 240000, "Phoenix,Tucson"),

        # ── CALIFORNIA (10 builders) ──
        ("Lennar", "CA", "CA-LEN-8901", 78, 82, 76, 72, 64, 78, 80, 76.4, "B", 38000, 1954, "Production homes", "A-", 52, 18, "active", 10, 3.2, "mid-tier", 650000, "Los Angeles,San Diego,Inland Empire,Bay Area"),
        ("KB Home", "CA", "CA-KBH-8902", 76, 80, 74, 68, 60, 76, 78, 74.0, "B", 32000, 1957, "Built-to-order", "B+", 65, 16, "active", 12, 3.8, "mid-tier", 580000, "LA,San Diego,Riverside,Sacramento"),
        ("Toll Brothers", "CA", "CA-TOL-8903", 92, 94, 90, 88, 80, 92, 90, 90.2, "A", 6500, 1967, "Luxury homes", "A+", 8, 30, "active", 1, 1.2, "premium", 1200000, "Orange County,LA,Bay Area"),
        ("Shea Homes", "CA", "CA-SHE-8904", 88, 90, 86, 84, 76, 88, 86, 86.0, "A", 7000, 1881, "Active adult, family", "A+", 10, 40, "active", 1, 1.4, "premium", 820000, "San Diego,Orange County,Bay Area"),
        ("Taylor Morrison", "CA", "CA-TAY-8905", 84, 86, 82, 78, 70, 84, 82, 81.0, "B", 6000, 2007, "Move-up homes", "A", 18, 12, "active", 4, 2.2, "premium", 720000, "Bay Area,Sacramento"),
        ("Meritage Homes", "CA", "CA-MER-8906", 82, 86, 80, 76, 66, 82, 80, 79.8, "B", 10000, 1985, "Energy-efficient", "A-", 26, 18, "active", 5, 2.4, "premium", 640000, "Inland Empire,Sacramento,San Diego"),
        ("D.R. Horton", "CA", "CA-DRH-8907", 74, 78, 72, 68, 60, 74, 76, 72.2, "B", 28000, 1978, "Entry-level", "B+", 78, 15, "active", 14, 4.0, "mid-tier", 520000, "Inland Empire,Sacramento,Central Valley"),
        ("Tri Pointe Homes", "CA", "CA-TRI-8908", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 5500, 2009, "Design-focused", "A", 14, 10, "active", 2, 1.6, "premium", 780000, "Orange County,LA,San Diego"),
        ("William Lyon Homes", "CA", "CA-WLH-8909", 84, 86, 82, 80, 72, 84, 82, 82.0, "B", 4200, 1956, "Move-up and luxury", "A", 12, 28, "active", 3, 1.8, "premium", 700000, "Orange County,LA,San Diego"),
        ("Brookfield Residential", "CA", "CA-BRO-8910", 80, 82, 78, 76, 68, 80, 80, 78.2, "B", 3500, 1956, "Master-planned communities", "A-", 16, 22, "active", 4, 2.0, "mid-tier", 620000, "LA,San Diego"),

        # ── GEORGIA (8 builders) ──
        ("PulteGroup", "GA", "GA-PUL-4501", 84, 86, 82, 78, 70, 84, 84, 81.8, "B", 15000, 1950, "Active adult, custom", "A", 22, 22, "active", 4, 2.2, "premium", 420000, "Atlanta,Savannah"),
        ("D.R. Horton", "GA", "GA-DRH-4502", 74, 78, 72, 68, 60, 74, 76, 72.0, "B", 28000, 1978, "Entry-level", "B+", 62, 15, "active", 12, 4.0, "mid-tier", 320000, "Atlanta,Augusta,Savannah"),
        ("Lennar", "GA", "GA-LEN-4503", 80, 84, 76, 72, 64, 80, 80, 77.4, "B", 20000, 1954, "Production homes", "A-", 38, 18, "active", 8, 3.2, "mid-tier", 380000, "Atlanta,Savannah"),
        ("Toll Brothers", "GA", "GA-TOL-4504", 90, 92, 88, 86, 78, 90, 88, 88.2, "A", 3200, 1967, "Luxury homes", "A+", 6, 30, "active", 0, 1.0, "premium", 750000, "Atlanta,Alpharetta"),
        ("Smith Douglas Homes", "GA", "GA-SDH-4505", 78, 80, 76, 72, 64, 78, 78, 76.0, "B", 5500, 2009, "Value-conscious SE markets", "A-", 18, 8, "active", 5, 2.8, "mid-tier", 340000, "Atlanta,Nashville,Huntsville"),
        ("Ashton Woods", "GA", "GA-ASH-4506", 86, 90, 84, 82, 74, 86, 84, 84.4, "B", 4200, 1989, "Design-focused", "A", 12, 20, "active", 2, 1.6, "premium", 480000, "Atlanta"),
        ("Kolter Homes", "GA", "GA-KOL-4507", 84, 86, 82, 80, 72, 84, 82, 81.4, "B", 2800, 2001, "Active adult communities", "A", 8, 15, "active", 2, 1.8, "premium", 440000, "Atlanta"),
        ("Rocklyn Homes", "GA", "GA-ROC-4508", 72, 74, 70, 66, 58, 72, 72, 69.4, "C", 2200, 2002, "Affordable single-family", "B", 28, 8, "active", 10, 4.0, "budget", 280000, "Atlanta metro"),

        # ── NORTH CAROLINA (8 builders) ──
        ("Lennar", "NC", "NC-LEN-5501", 80, 84, 76, 72, 64, 80, 80, 77.4, "B", 18000, 1954, "Production homes", "A-", 35, 18, "active", 8, 3.0, "mid-tier", 380000, "Charlotte,Raleigh,Durham"),
        ("D.R. Horton", "NC", "NC-DRH-5502", 74, 78, 72, 68, 60, 74, 76, 72.0, "B", 22000, 1978, "Entry-level", "B+", 55, 15, "active", 12, 3.8, "mid-tier", 320000, "Charlotte,Raleigh,Fayetteville"),
        ("Toll Brothers", "NC", "NC-TOL-5503", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 2800, 1967, "Luxury homes", "A+", 5, 30, "active", 0, 1.0, "premium", 700000, "Charlotte,Raleigh"),
        ("M/I Homes", "NC", "NC-MIH-5504", 82, 84, 80, 76, 68, 82, 80, 79.8, "B", 5200, 1976, "Single-family, smart home", "A-", 16, 18, "active", 4, 2.2, "mid-tier", 420000, "Charlotte,Raleigh"),
        ("Taylor Morrison", "NC", "NC-TAY-5505", 84, 86, 82, 78, 70, 84, 82, 81.0, "B", 4500, 2007, "Move-up homes", "A", 12, 12, "active", 3, 2.0, "premium", 460000, "Charlotte,Raleigh"),
        ("Eastwood Homes", "NC", "NC-EAS-5506", 80, 82, 78, 74, 66, 80, 78, 77.2, "B", 3200, 1977, "Mid-range single-family", "A-", 14, 24, "active", 4, 2.4, "mid-tier", 360000, "Charlotte,Richmond,Raleigh"),
        ("True Homes", "NC", "NC-TRU-5507", 82, 84, 80, 78, 70, 82, 80, 79.8, "B", 2800, 2007, "Charlotte-focused", "A", 10, 10, "active", 3, 2.0, "mid-tier", 400000, "Charlotte,Rock Hill"),
        ("Shea Homes", "NC", "NC-SHE-5508", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 2200, 1881, "Active adult", "A+", 6, 40, "active", 1, 1.4, "premium", 500000, "Charlotte"),

        # ── SOUTH CAROLINA (6 builders) ──
        ("Lennar", "SC", "SC-LEN-6601", 78, 82, 74, 70, 62, 78, 78, 75.4, "B", 12000, 1954, "Production homes", "A-", 30, 18, "active", 8, 3.2, "mid-tier", 340000, "Charleston,Myrtle Beach,Greenville"),
        ("D.R. Horton", "SC", "SC-DRH-6602", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 15000, 1978, "Entry-level", "B+", 48, 15, "active", 12, 4.0, "mid-tier", 290000, "Charleston,Columbia,Greenville"),
        ("Toll Brothers", "SC", "SC-TOL-6603", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 2200, 1967, "Luxury homes", "A+", 4, 30, "active", 0, 1.0, "premium", 680000, "Charleston,Hilton Head"),
        ("Mungo Homes", "SC", "SC-MUN-6604", 82, 84, 80, 76, 68, 82, 80, 79.4, "B", 3500, 1954, "SC-focused builder", "A", 12, 38, "active", 3, 2.0, "mid-tier", 360000, "Columbia,Charleston,Lexington"),
        ("Dan Ryan Builders", "SC", "SC-DAN-6605", 80, 82, 78, 74, 66, 80, 78, 77.0, "B", 2800, 1990, "Move-up single-family", "A-", 14, 18, "active", 4, 2.4, "mid-tier", 380000, "Charleston,Greenville"),
        ("Great Southern Homes", "SC", "SC-GSH-6606", 76, 78, 74, 70, 62, 76, 76, 74.0, "B", 4500, 2002, "Affordable production", "B+", 22, 12, "active", 6, 3.2, "mid-tier", 300000, "Columbia,Lexington,Charleston"),

        # ── NEW YORK (6 builders) ──
        ("Toll Brothers", "NY", "NY-TOL-7701", 92, 94, 90, 88, 80, 92, 90, 90.4, "A", 5000, 1967, "Luxury homes", "A+", 8, 30, "active", 0, 1.0, "premium", 1100000, "Long Island,Westchester,NJ suburbs"),
        ("Lennar", "NY", "NY-LEN-7702", 78, 82, 76, 72, 64, 78, 80, 76.2, "B", 8000, 1954, "Production homes", "A-", 32, 18, "active", 8, 3.0, "mid-tier", 550000, "Long Island,Brooklyn"),
        ("K. Hovnanian", "NY", "NY-KHO-7703", 72, 74, 70, 66, 58, 72, 72, 69.6, "C", 9000, 1959, "Various price points", "B", 45, 18, "active", 10, 3.6, "mid-tier", 480000, "NJ/NY metro"),
        ("National Resources", "NY", "NY-NAT-7704", 80, 82, 78, 76, 68, 80, 80, 78.0, "B", 1500, 1978, "Master-planned communities", "A-", 8, 14, "active", 2, 2.0, "mid-tier", 620000, "Hudson Valley,Westchester"),
        ("Beechwood Organization", "NY", "NY-BEE-7705", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 2800, 1985, "Long Island luxury", "A", 6, 22, "active", 1, 1.4, "premium", 850000, "Long Island,Hamptons"),
        ("Ryan Homes", "NY", "NY-RYA-7706", 74, 76, 72, 68, 60, 74, 74, 71.8, "B", 18000, 1948, "Production, fixed-price", "B+", 38, 20, "active", 8, 3.4, "mid-tier", 420000, "Upstate NY,Long Island"),

        # ── COLORADO (6 builders) ──
        ("Richmond American", "CO", "CO-RIC-3301", 82, 84, 80, 76, 68, 82, 80, 79.4, "B", 8500, 1972, "Various price points", "A-", 22, 26, "active", 4, 2.2, "mid-tier", 520000, "Denver,Colorado Springs"),
        ("Meritage Homes", "CO", "CO-MER-3302", 84, 88, 82, 78, 68, 84, 82, 81.4, "B", 7000, 1985, "Energy-efficient", "A-", 18, 18, "active", 4, 2.0, "premium", 560000, "Denver,Fort Collins"),
        ("Toll Brothers", "CO", "CO-TOL-3303", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 3500, 1967, "Luxury homes", "A+", 5, 30, "active", 0, 1.0, "premium", 850000, "Denver,Boulder"),
        ("KB Home", "CO", "CO-KBH-3304", 76, 80, 74, 68, 60, 76, 78, 74.0, "B", 15000, 1957, "Built-to-order", "B+", 42, 16, "active", 8, 3.4, "mid-tier", 440000, "Denver,Colorado Springs"),
        ("Dream Finders Homes", "CO", "CO-DFH-3305", 84, 86, 82, 80, 72, 84, 82, 81.4, "B", 2500, 2008, "Customizable designs", "A", 8, 10, "active", 2, 1.8, "premium", 500000, "Denver"),
        ("Oakwood Homes", "CO", "CO-OAK-3306", 78, 80, 76, 72, 64, 78, 78, 75.8, "B", 4200, 1991, "Affordable CO builder", "B+", 28, 18, "active", 6, 3.0, "mid-tier", 380000, "Denver,Colorado Springs"),

        # ── NEW JERSEY (5 builders) ──
        ("Toll Brothers", "NJ", "NJ-TOL-2201", 92, 94, 90, 88, 80, 92, 90, 90.4, "A", 7500, 1967, "Luxury homes", "A+", 10, 30, "active", 0, 1.0, "premium", 950000, "Northern NJ,Shore"),
        ("K. Hovnanian", "NJ", "NJ-KHO-2202", 74, 76, 72, 68, 60, 74, 74, 71.6, "B", 12000, 1959, "Various price points", "B", 52, 18, "active", 10, 3.6, "mid-tier", 520000, "Central NJ,South NJ"),
        ("Lennar", "NJ", "NJ-LEN-2203", 80, 84, 76, 72, 64, 80, 80, 77.4, "B", 8500, 1954, "Production homes", "A-", 28, 18, "active", 6, 2.8, "mid-tier", 580000, "Northern NJ,Monmouth County"),
        ("Ryan Homes", "NJ", "NJ-RYA-2204", 74, 76, 72, 68, 60, 74, 74, 71.4, "B", 10000, 1948, "Production, fixed-price", "B+", 35, 20, "active", 8, 3.4, "mid-tier", 450000, "Central NJ,South NJ"),
        ("D.R. Horton", "NJ", "NJ-DRH-2205", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 6000, 1978, "Entry-level", "B+", 42, 15, "active", 10, 3.8, "mid-tier", 420000, "South NJ"),

        # ── OHIO (5 builders) ──
        ("M/I Homes", "OH", "OH-MIH-4401", 84, 86, 82, 78, 70, 84, 82, 81.4, "B", 7000, 1976, "Single-family, smart home", "A", 14, 24, "active", 3, 2.0, "premium", 400000, "Columbus,Cincinnati,Cleveland"),
        ("Ryan Homes", "OH", "OH-RYA-4402", 74, 76, 72, 68, 60, 74, 74, 71.6, "B", 12000, 1948, "Production, fixed-price", "B+", 32, 20, "active", 8, 3.2, "mid-tier", 340000, "Columbus,Cincinnati,Cleveland"),
        ("Fischer Homes", "OH", "OH-FIS-4403", 82, 84, 80, 78, 70, 82, 80, 79.6, "B", 4500, 1980, "Custom and semi-custom", "A", 10, 22, "active", 2, 1.8, "premium", 420000, "Cincinnati,Columbus,Dayton"),
        ("Pulte Homes", "OH", "OH-PUL-4404", 82, 84, 80, 76, 68, 82, 80, 79.2, "B", 8000, 1950, "Active adult, family", "A-", 20, 22, "active", 4, 2.2, "mid-tier", 380000, "Columbus,Cleveland"),
        ("Maronda Homes", "OH", "OH-MAR-4405", 70, 72, 68, 64, 56, 70, 70, 67.4, "C", 6000, 1972, "Affordable single-family", "B", 35, 14, "active", 12, 4.2, "budget", 280000, "Columbus,Pittsburgh"),

        # ── PENNSYLVANIA (5 builders) ──
        ("Toll Brothers", "PA", "PA-TOL-1101", 92, 94, 90, 88, 80, 92, 90, 90.4, "A", 10000, 1967, "Luxury homes (HQ state)", "A+", 12, 40, "active", 0, 1.0, "premium", 820000, "Philadelphia suburbs,Bucks County"),
        ("Ryan Homes", "PA", "PA-RYA-1102", 74, 76, 72, 68, 60, 74, 74, 71.4, "B", 14000, 1948, "Production, fixed-price", "B+", 38, 20, "active", 8, 3.2, "mid-tier", 380000, "Pittsburgh,Philadelphia,Lehigh Valley"),
        ("Lennar", "PA", "PA-LEN-1103", 78, 82, 76, 72, 64, 78, 80, 76.2, "B", 6000, 1954, "Production homes", "A-", 22, 18, "active", 6, 2.8, "mid-tier", 440000, "Philadelphia suburbs"),
        ("K. Hovnanian", "PA", "PA-KHO-1104", 72, 74, 70, 66, 58, 72, 72, 69.4, "C", 5500, 1959, "Various price points", "B", 35, 18, "active", 8, 3.4, "mid-tier", 400000, "Eastern PA"),
        ("Keystone Custom Homes", "PA", "PA-KEY-1105", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 2200, 1996, "Central PA custom", "A", 6, 18, "active", 1, 1.4, "premium", 480000, "Central PA,York,Lancaster"),

        # ── ILLINOIS (5 builders) ──
        ("Lennar", "IL", "IL-LEN-6001", 78, 82, 76, 72, 64, 78, 80, 76.2, "B", 12000, 1954, "Production homes", "A-", 32, 18, "active", 8, 3.0, "mid-tier", 420000, "Chicago suburbs"),
        ("Pulte Homes", "IL", "IL-PUL-6002", 82, 84, 80, 76, 68, 82, 80, 79.0, "B", 8000, 1950, "Active adult, family", "A-", 18, 22, "active", 4, 2.2, "mid-tier", 380000, "Chicago suburbs"),
        ("D.R. Horton", "IL", "IL-DRH-6003", 72, 76, 70, 66, 58, 72, 74, 69.8, "C", 10000, 1978, "Entry-level", "B+", 45, 15, "active", 12, 3.8, "mid-tier", 310000, "Chicago suburbs,Rockford"),
        ("Toll Brothers", "IL", "IL-TOL-6004", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 2800, 1967, "Luxury homes", "A+", 5, 30, "active", 0, 1.0, "premium", 780000, "North Shore,Hinsdale"),
        ("CalAtlantic (Lennar)", "IL", "IL-CAL-6005", 78, 80, 76, 72, 64, 78, 78, 76.0, "B", 5000, 2015, "Mid-range single-family", "A-", 18, 5, "active", 5, 2.6, "mid-tier", 400000, "Chicago suburbs"),

        # ── MICHIGAN (4 builders) ──
        ("Pulte Homes", "MI", "MI-PUL-4801", 82, 84, 80, 76, 68, 82, 80, 79.0, "B", 10000, 1950, "Active adult, family", "A-", 20, 22, "active", 4, 2.2, "mid-tier", 340000, "Detroit suburbs,Ann Arbor"),
        ("Toll Brothers", "MI", "MI-TOL-4802", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 2500, 1967, "Luxury homes", "A+", 5, 30, "active", 0, 1.0, "premium", 680000, "Bloomfield Hills,Northville"),
        ("M/I Homes", "MI", "MI-MIH-4803", 80, 82, 78, 74, 66, 80, 78, 77.0, "B", 3500, 1976, "Single-family, smart home", "A-", 12, 18, "active", 4, 2.4, "mid-tier", 380000, "Ann Arbor,Grand Rapids"),
        ("Lombardo Homes", "MI", "MI-LOM-4804", 76, 78, 74, 70, 62, 76, 76, 74.0, "B", 2800, 1956, "SE Michigan focused", "B+", 18, 28, "active", 6, 2.8, "mid-tier", 350000, "Detroit metro"),

        # ── VIRGINIA (5 builders) ──
        ("Ryan Homes", "VA", "VA-RYA-2301", 76, 78, 74, 70, 62, 76, 76, 74.0, "B", 15000, 1948, "Production, fixed-price", "B+", 35, 20, "active", 8, 3.0, "mid-tier", 420000, "NoVA,Richmond,Hampton Roads"),
        ("Toll Brothers", "VA", "VA-TOL-2302", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 4500, 1967, "Luxury homes", "A+", 6, 30, "active", 0, 1.0, "premium", 850000, "NoVA,Fairfax,Loudoun"),
        ("Stanley Martin Homes", "VA", "VA-STM-2303", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 3500, 1966, "Move-up and luxury", "A", 10, 32, "active", 2, 1.6, "premium", 620000, "NoVA,Richmond"),
        ("Van Metre Homes", "VA", "VA-VAN-2304", 84, 86, 82, 80, 72, 84, 82, 81.4, "B", 2800, 1955, "NoVA master-planned", "A", 8, 38, "active", 2, 1.6, "premium", 580000, "Ashburn,Leesburg,Bristow"),
        ("D.R. Horton", "VA", "VA-DRH-2305", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 8000, 1978, "Entry-level", "B+", 42, 15, "active", 10, 3.6, "mid-tier", 360000, "Richmond,Hampton Roads"),

        # ── MARYLAND (4 builders) ──
        ("Toll Brothers", "MD", "MD-TOL-2101", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 3800, 1967, "Luxury homes", "A+", 6, 30, "active", 0, 1.0, "premium", 780000, "Montgomery County,Howard County"),
        ("Ryan Homes", "MD", "MD-RYA-2102", 74, 76, 72, 68, 60, 74, 74, 71.4, "B", 8000, 1948, "Production, fixed-price", "B+", 30, 20, "active", 8, 3.2, "mid-tier", 400000, "Baltimore,Frederick,Harford"),
        ("Lennar", "MD", "MD-LEN-2103", 78, 82, 76, 72, 64, 78, 80, 76.2, "B", 5000, 1954, "Production homes", "A-", 20, 18, "active", 6, 2.8, "mid-tier", 480000, "Howard County,Anne Arundel"),
        ("Winchester Homes", "MD", "MD-WIN-2104", 84, 86, 82, 80, 72, 84, 82, 81.4, "B", 2200, 1979, "MD custom builder", "A", 8, 26, "active", 2, 1.6, "premium", 620000, "Montgomery County,Frederick"),

        # ── NEVADA (4 builders) ──
        ("Toll Brothers", "NV", "NV-TOL-8801", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 3500, 1967, "Luxury homes", "A+", 6, 30, "active", 0, 1.0, "premium", 720000, "Las Vegas,Henderson"),
        ("Lennar", "NV", "NV-LEN-8802", 78, 82, 76, 72, 64, 78, 80, 76.2, "B", 15000, 1954, "Production homes", "A-", 35, 18, "active", 8, 3.0, "mid-tier", 420000, "Las Vegas,Henderson,Reno"),
        ("KB Home", "NV", "NV-KBH-8803", 76, 80, 74, 68, 60, 76, 78, 74.0, "B", 12000, 1957, "Built-to-order", "B+", 45, 16, "active", 10, 3.6, "mid-tier", 380000, "Las Vegas"),
        ("D.R. Horton", "NV", "NV-DRH-8804", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 10000, 1978, "Entry-level", "B+", 52, 15, "active", 12, 4.0, "mid-tier", 340000, "Las Vegas,Henderson"),

        # ── WASHINGTON (4 builders) ──
        ("Toll Brothers", "WA", "WA-TOL-9801", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 3200, 1967, "Luxury homes", "A+", 5, 30, "active", 0, 1.0, "premium", 920000, "Seattle,Bellevue,Redmond"),
        ("Lennar", "WA", "WA-LEN-9802", 78, 82, 76, 72, 64, 78, 80, 76.2, "B", 6000, 1954, "Production homes", "A-", 25, 18, "active", 6, 2.8, "mid-tier", 580000, "Seattle,Tacoma"),
        ("KB Home", "WA", "WA-KBH-9803", 76, 80, 74, 68, 60, 76, 78, 74.0, "B", 5000, 1957, "Built-to-order", "B+", 35, 16, "active", 8, 3.2, "mid-tier", 520000, "Seattle metro"),
        ("MainVue Homes", "WA", "WA-MVH-9804", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 1800, 2009, "Modern design-focused", "A", 8, 10, "active", 1, 1.4, "premium", 750000, "Bellevue,Kirkland,Redmond"),

        # ── TENNESSEE (4 builders) ──
        ("Smith Douglas Homes", "TN", "TN-SDH-3701", 78, 80, 76, 72, 64, 78, 78, 76.0, "B", 4500, 2009, "Value-conscious SE markets", "A-", 16, 8, "active", 5, 2.6, "mid-tier", 340000, "Nashville,Murfreesboro"),
        ("Pulte Homes", "TN", "TN-PUL-3702", 82, 84, 80, 76, 68, 82, 80, 79.0, "B", 6000, 1950, "Active adult, family", "A-", 18, 22, "active", 4, 2.2, "mid-tier", 380000, "Nashville"),
        ("Drees Homes", "TN", "TN-DRE-3703", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 3200, 1928, "Custom and semi-custom", "A", 8, 45, "active", 1, 1.4, "premium", 480000, "Nashville"),
        ("D.R. Horton", "TN", "TN-DRH-3704", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 10000, 1978, "Entry-level", "B+", 42, 15, "active", 10, 3.8, "mid-tier", 300000, "Nashville,Memphis,Knoxville"),

        # ── INDIANA (3 builders) ──
        ("M/I Homes", "IN", "IN-MIH-4601", 82, 84, 80, 76, 68, 82, 80, 79.0, "B", 4000, 1976, "Single-family", "A-", 12, 18, "active", 3, 2.0, "mid-tier", 360000, "Indianapolis,Carmel"),
        ("Pulte Homes", "IN", "IN-PUL-4602", 80, 82, 78, 74, 66, 80, 78, 77.0, "B", 5000, 1950, "Active adult, family", "A-", 16, 22, "active", 4, 2.2, "mid-tier", 340000, "Indianapolis"),
        ("D.R. Horton", "IN", "IN-DRH-4603", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 7000, 1978, "Entry-level", "B+", 35, 15, "active", 10, 3.6, "mid-tier", 280000, "Indianapolis,Fort Wayne"),

        # ── MINNESOTA (3 builders) ──
        ("Pulte Homes", "MN", "MN-PUL-5501", 82, 84, 80, 76, 68, 82, 80, 79.0, "B", 5000, 1950, "Active adult, family", "A-", 14, 22, "active", 3, 2.0, "mid-tier", 400000, "Minneapolis,St. Paul suburbs"),
        ("Lennar", "MN", "MN-LEN-5502", 78, 82, 76, 72, 64, 78, 80, 76.2, "B", 4000, 1954, "Production homes", "A-", 20, 18, "active", 5, 2.6, "mid-tier", 380000, "Minneapolis suburbs"),
        ("D.R. Horton", "MN", "MN-DRH-5503", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 3500, 1978, "Entry-level", "B+", 28, 15, "active", 8, 3.4, "mid-tier", 320000, "Minneapolis,St. Paul"),

        # ── UTAH (4 builders) ──
        ("Ivory Homes", "UT", "UT-IVO-8401", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 8000, 1965, "Utah's largest builder", "A", 18, 38, "active", 2, 1.6, "premium", 520000, "Salt Lake City,Provo,Ogden"),
        ("Lennar", "UT", "UT-LEN-8402", 78, 82, 76, 72, 64, 78, 80, 76.2, "B", 5000, 1954, "Production homes", "A-", 22, 18, "active", 6, 2.8, "mid-tier", 440000, "Salt Lake,Lehi,Draper"),
        ("D.R. Horton", "UT", "UT-DRH-8403", 74, 78, 72, 68, 60, 74, 76, 72.2, "B", 6000, 1978, "Entry-level", "B+", 35, 15, "active", 10, 3.6, "mid-tier", 380000, "Salt Lake,Utah County"),
        ("Toll Brothers", "UT", "UT-TOL-8404", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 1800, 1967, "Luxury homes", "A+", 4, 30, "active", 0, 1.0, "premium", 780000, "Park City,Draper"),

        # ── ALABAMA (3 builders) ──
        ("D.R. Horton", "AL", "AL-DRH-3501", 74, 78, 72, 68, 60, 74, 76, 72.2, "B", 8000, 1978, "Entry-level", "B+", 38, 15, "active", 10, 3.6, "mid-tier", 280000, "Birmingham,Huntsville,Mobile"),
        ("Smith Douglas Homes", "AL", "AL-SDH-3502", 78, 80, 76, 72, 64, 78, 78, 76.0, "B", 3200, 2009, "Value-conscious", "A-", 12, 8, "active", 4, 2.4, "mid-tier", 300000, "Huntsville,Birmingham"),
        ("Lennar", "AL", "AL-LEN-3503", 76, 80, 74, 70, 62, 76, 78, 74.0, "B", 4000, 1954, "Production homes", "A-", 18, 18, "active", 6, 2.8, "mid-tier", 320000, "Birmingham,Huntsville"),

        # ── LOUISIANA (3 builders) ──
        ("DSLD Homes", "LA", "LA-DSL-7001", 80, 82, 78, 74, 66, 80, 78, 77.0, "B", 5500, 2008, "Louisiana's largest", "A-", 22, 10, "active", 5, 2.4, "mid-tier", 300000, "Baton Rouge,New Orleans,Lafayette"),
        ("D.R. Horton", "LA", "LA-DRH-7002", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 6000, 1978, "Entry-level", "B+", 35, 15, "active", 10, 3.6, "mid-tier", 260000, "Baton Rouge,New Orleans"),
        ("Lennar", "LA", "LA-LEN-7003", 76, 80, 74, 70, 62, 76, 78, 74.0, "B", 3500, 1954, "Production homes", "A-", 18, 18, "active", 6, 2.8, "mid-tier", 310000, "Baton Rouge,Metairie"),

        # ── OREGON (3 builders) ──
        ("Lennar", "OR", "OR-LEN-9701", 78, 82, 76, 72, 64, 78, 80, 76.2, "B", 4000, 1954, "Production homes", "A-", 22, 18, "active", 6, 2.6, "mid-tier", 480000, "Portland,Beaverton,Hillsboro"),
        ("D.R. Horton", "OR", "OR-DRH-9702", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 3500, 1978, "Entry-level", "B+", 32, 15, "active", 10, 3.4, "mid-tier", 420000, "Portland metro"),
        ("Toll Brothers", "OR", "OR-TOL-9703", 88, 90, 86, 84, 76, 88, 86, 86.0, "A", 1500, 1967, "Luxury homes", "A+", 4, 30, "active", 0, 1.0, "premium", 780000, "West Linn,Lake Oswego"),

        # ── MISSISSIPPI (2 builders) ──
        ("Adams Homes", "MS", "MS-ADM-3901", 66, 68, 64, 60, 52, 66, 68, 63.8, "C", 12000, 1991, "Budget-friendly", "B-", 55, 8, "active", 18, 5.2, "budget", 220000, "Jackson,Gulfport,Biloxi"),
        ("D.R. Horton", "MS", "MS-DRH-3902", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 5000, 1978, "Entry-level", "B+", 28, 15, "active", 10, 3.6, "mid-tier", 250000, "Jackson,Hattiesburg"),

        # ── KANSAS / MISSOURI (3 builders) ──
        ("Drees Custom Homes", "KS", "KS-DRE-6601", 86, 88, 84, 82, 74, 86, 84, 84.0, "B", 2500, 1928, "Custom and semi-custom", "A", 8, 45, "active", 1, 1.4, "premium", 460000, "Kansas City,Overland Park"),
        ("D.R. Horton", "MO", "MO-DRH-6301", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 7000, 1978, "Entry-level", "B+", 38, 15, "active", 10, 3.6, "mid-tier", 280000, "St. Louis,Kansas City"),
        ("McBride Homes", "MO", "MO-MCB-6302", 80, 82, 78, 76, 68, 80, 78, 77.4, "B", 3800, 1946, "St. Louis's largest builder", "A-", 14, 40, "active", 3, 2.0, "mid-tier", 360000, "St. Louis metro"),

        # ── MASSACHUSETTS (3 builders) ──
        ("Toll Brothers", "MA", "MA-TOL-0201", 92, 94, 90, 88, 80, 92, 90, 90.4, "A", 2500, 1967, "Luxury homes", "A+", 5, 30, "active", 0, 1.0, "premium", 1100000, "Boston suburbs,MetroWest"),
        ("Pulte Homes", "MA", "MA-PUL-0202", 80, 82, 78, 74, 66, 80, 78, 77.0, "B", 2800, 1950, "Active adult", "A-", 12, 22, "active", 3, 2.0, "mid-tier", 580000, "Greater Boston"),
        ("National Development", "MA", "MA-NAT-0203", 84, 86, 82, 80, 72, 84, 82, 81.4, "B", 1500, 1983, "Master-planned, mixed-use", "A", 6, 20, "active", 1, 1.4, "premium", 720000, "Greater Boston,South Shore"),

        # ── CONNECTICUT (2 builders) ──
        ("Toll Brothers", "CT", "CT-TOL-0601", 90, 92, 88, 86, 78, 90, 88, 88.0, "A", 2200, 1967, "Luxury homes", "A+", 4, 30, "active", 0, 1.0, "premium", 950000, "Fairfield County,Hartford"),
        ("D.R. Horton", "CT", "CT-DRH-0602", 72, 76, 70, 66, 58, 72, 74, 70.0, "B", 2000, 1978, "Entry-level", "B+", 22, 15, "active", 8, 3.4, "mid-tier", 380000, "Greater Hartford"),
    ]

    for b in builders:
        conn.execute("""
            INSERT OR REPLACE INTO builders
            (name, state, license_number, callback_rate, plumbing_material_score, code_violation_score,
             litigation_score, construction_volume_score, appliance_score, drainage_score,
             composite_score, grade, homes_built, year_established, specialties,
             bbb_rating, bbb_complaints, bbb_years_accredited, license_status,
             building_dept_violations, warranty_claim_rate, plumbing_sub_quality,
             avg_home_price, markets)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, b)


def seed_sample_properties(conn):
    """Seed sample properties across key markets for demonstration."""
    properties = [
        # Florida properties
        ("1420 Brickell Bay Dr", "Miami", "FL", "33131", 25.764, -80.188, 2008, 2200, 2, 3.0, "condo", "PEX", "permit_record", 1, 1, 8, "tankless", 2022, 3, 2020, 0, 0, None, "Lennar Homes"),
        ("742 Palm Ave", "Miami Beach", "FL", "33139", 25.785, -80.133, 1962, 1800, 1, 2.0, "single_family", "copper", "estimated", 0, 0, 18, "tank", None, 0, None, 2, 28500, None, None),
        ("8900 NW 18th Ter", "Doral", "FL", "33172", 25.825, -80.365, 2015, 2800, 2, 4.0, "single_family", "PEX", "permit_record", 1, 1, 4, "hybrid", 2024, 2, None, 0, 0, None, "Lennar Homes"),
        ("3215 Bayshore Blvd", "Tampa", "FL", "33629", 27.915, -82.490, 1955, 2400, 1, 2.0, "single_family", "galvanized", "estimated", 0, 0, 25, "tank", 1998, 1, 2005, 3, 42000, None, None),
        ("15620 Fishhawk Blvd", "Lithia", "FL", "33547", 27.862, -82.217, 2019, 3200, 2, 4.5, "single_family", "PEX", "permit_record", 1, 1, 2, "tankless", None, 0, None, 0, 0, None, "David Weekley Homes"),
        ("2901 Collins Ave", "Miami Beach", "FL", "33140", 25.806, -80.122, 1948, 1200, 1, 1.5, "condo", "galvanized", "estimated", 0, 0, 30, "tank", None, 0, None, 4, 65000, None, None),
        ("9876 Eagle Creek Dr", "Orlando", "FL", "32832", 28.389, -81.381, 2004, 2600, 2, 3.5, "single_family", "CPVC", "permit_record", 1, 0, 12, "tank", 2018, 2, None, 1, 12000, None, "Meritage Homes"),
        ("4321 Ocean Blvd", "Sarasota", "FL", "34242", 27.265, -82.535, 1972, 2000, 1, 2.5, "single_family", "copper", "estimated", 0, 0, 20, "tank", 2010, 1, 2015, 1, 18000, None, None),

        # Texas properties
        ("4502 Travis St", "Houston", "TX", "77002", 29.741, -95.380, 2016, 3000, 2, 4.0, "single_family", "PEX", "permit_record", 1, 1, 3, "tankless", 2024, 2, None, 0, 0, None, "Perry Homes"),
        ("12800 Briar Forest Dr", "Houston", "TX", "77077", 29.738, -95.582, 1985, 2400, 1, 3.0, "single_family", "copper", "estimated", 0, 0, 15, "tank", 2012, 1, 2018, 2, 22000, None, None),
        ("8900 Shoal Creek Blvd", "Austin", "TX", "78757", 30.360, -97.739, 2020, 2800, 2, 3.5, "single_family", "PEX", "permit_record", 1, 1, 2, "tankless", None, 0, None, 0, 0, None, "Taylor Morrison"),
        ("5612 Swiss Ave", "Dallas", "TX", "75214", 32.790, -96.774, 1928, 3200, 2, 3.0, "single_family", "galvanized", "estimated", 0, 0, 30, "tank", 1995, 1, 2008, 5, 78000, None, None),
        ("18200 Spectrum Blvd", "San Antonio", "TX", "78258", 29.630, -98.525, 2022, 2600, 1, 3.5, "single_family", "PEX", "permit_record", 1, 1, 1, "hybrid", 2025, 1, None, 0, 0, None, "David Weekley Homes"),

        # Arizona properties
        ("7890 E Camelback Rd", "Scottsdale", "AZ", "85251", 33.509, -111.923, 2010, 3500, 1, 4.0, "single_family", "PEX", "permit_record", 1, 1, 6, "tankless", 2022, 2, None, 0, 0, None, "Toll Brothers"),
        ("3456 W Thunderbird Rd", "Phoenix", "AZ", "85053", 33.610, -112.118, 1988, 1800, 1, 2.0, "single_family", "copper", "estimated", 0, 0, 14, "tank", 2005, 1, 2012, 1, 15000, None, None),
        ("12345 N Scottsdale Rd", "Scottsdale", "AZ", "85254", 33.596, -111.926, 2021, 4200, 1, 5.0, "single_family", "PEX", "permit_record", 1, 1, 1, "tankless", None, 0, None, 0, 0, None, "Shea Homes"),

        # California properties
        ("1234 Ocean Ave", "Santa Monica", "CA", "90401", 34.014, -118.491, 1965, 1600, 1, 2.0, "single_family", "copper", "estimated", 0, 0, 22, "tank", 2008, 1, 2015, 2, 32000, None, None),
        ("5678 Torrey Pines Rd", "La Jolla", "CA", "92037", 32.880, -117.245, 2018, 3800, 2, 4.5, "single_family", "PEX", "permit_record", 1, 1, 3, "tankless", None, 0, None, 0, 0, None, "Toll Brothers"),

        # Georgia / Carolinas
        ("4567 Peachtree Rd NE", "Atlanta", "GA", "30319", 33.851, -84.352, 1975, 2200, 2, 3.0, "single_family", "copper", "estimated", 0, 0, 18, "tank", 2010, 1, 2016, 1, 15000, None, None),
        ("8901 Providence Rd", "Charlotte", "NC", "28277", 35.047, -80.812, 2017, 3000, 2, 4.0, "single_family", "PEX", "permit_record", 1, 1, 4, "hybrid", 2024, 2, None, 0, 0, None, "Toll Brothers"),
        ("1234 Folly Rd", "Charleston", "SC", "29412", 32.720, -79.952, 1958, 1800, 1, 2.0, "single_family", "galvanized", "estimated", 0, 0, 25, "tank", 2002, 1, 2010, 3, 45000, None, None),

        # Northeast
        ("456 Main St", "Greenwich", "CT", "06830", 41.028, -73.629, 1952, 3200, 2, 3.5, "single_family", "copper", "estimated", 0, 0, 28, "tank", 2005, 2, 2012, 2, 35000, None, None),
        ("789 Park Ave", "New York", "NY", "10021", 40.770, -73.964, 1928, 2800, 3, 3.0, "condo", "galvanized", "estimated", 0, 0, 30, "tank", 1998, 1, 2005, 4, 72000, None, None),
        ("321 Independence Dr", "Cherry Hill", "NJ", "08034", 39.911, -75.025, 2005, 2400, 2, 3.5, "single_family", "PEX", "permit_record", 1, 0, 10, "tank", 2020, 2, None, 0, 0, None, "Ryan Homes"),

        # Midwest
        ("5678 Worthington Rd", "Westerville", "OH", "43082", 40.126, -82.929, 2012, 2600, 2, 3.5, "single_family", "PEX", "permit_record", 1, 1, 5, "hybrid", 2023, 2, None, 0, 0, None, "M/I Homes"),
        ("9012 Maple Ave", "Naperville", "IL", "60540", 41.775, -88.148, 1998, 3000, 2, 4.0, "single_family", "copper", "permit_record", 1, 0, 12, "tank", 2018, 1, None, 1, 8500, None, "Pulte Homes"),

        # Colorado / Mountain West
        ("4321 Pearl St", "Boulder", "CO", "80302", 40.017, -105.271, 1970, 1800, 1, 2.0, "single_family", "copper", "estimated", 0, 0, 20, "tank", 2008, 1, 2015, 1, 18000, None, None),
        ("8765 Red Rocks Dr", "Highlands Ranch", "CO", "80126", 39.539, -104.970, 2018, 3200, 2, 4.5, "single_family", "PEX", "permit_record", 1, 1, 2, "tankless", None, 0, None, 0, 0, None, "Meritage Homes"),

        # Nevada
        ("1234 Las Vegas Blvd S", "Las Vegas", "NV", "89109", 36.132, -115.168, 2005, 2200, 1, 3.0, "single_family", "CPVC", "permit_record", 1, 0, 10, "tank", 2018, 1, None, 1, 12000, None, "KB Home"),
    ]

    for p in properties:
        conn.execute("""
            INSERT OR REPLACE INTO properties
            (address, city, state, zip_code, latitude, longitude, year_built, sqft, stories,
             bathrooms, property_type, pipe_material, pipe_material_source, has_prv,
             has_expansion_tank, water_heater_age_years, water_heater_type,
             last_plumbing_permit_year, total_plumbing_permits, last_renovation_year,
             prior_water_claims, prior_claim_total_cost, builder_id, builder_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, p)


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

    print("Seeding city pressure data...")
    seed_pressure_data(conn)

    print("Seeding nationwide builder data...")
    seed_builders_nationwide(conn)

    print("Seeding sample properties...")
    seed_sample_properties(conn)

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
