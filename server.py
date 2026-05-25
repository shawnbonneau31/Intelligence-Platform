"""
Namara Water Risk Intelligence Platform — Main Server
Tornado-based web application with REST API, JWT auth, and dashboard UI.
"""

import tornado.ioloop
import tornado.web
import tornado.escape
import jwt
import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from functools import wraps

from database import (
    init_db, get_db, authenticate_user, validate_api_key,
    check_rate_limit, log_request, create_user, generate_api_key
)
from scoring import (
    compute_composite_score, compute_property_score, search_builders,
    zip_to_state, lookup_property, lookup_builder_by_name, lookup_builder_by_id,
    score_individual_builder
)
from reports import generate_report

# ─── Configuration ───
SECRET_KEY = os.environ.get("NAMARA_SECRET", "namara-dev-secret-change-in-production")
PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ─── Auth Helpers ───

def create_jwt(user_data):
    payload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "tier": user_data["tier"],
        "is_admin": user_data["is_admin"],
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Content-Type", "application/json")

    def options(self, *args):
        self.set_status(204)
        self.finish()

    def get_current_user_jwt(self):
        auth = self.request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
            return decode_jwt(token)
        return None

    def get_api_key_user(self):
        key = self.request.headers.get("X-API-Key", "")
        if not key:
            key = self.get_argument("api_key", "")
        if key:
            return validate_api_key(key)
        return None

    def require_auth(self):
        """Returns user info or sends 401."""
        user = self.get_current_user_jwt()
        if user:
            return user

        api_key = self.get_api_key_user()
        if api_key:
            if not check_rate_limit(api_key["id"], api_key["rate_limit_per_min"]):
                self.set_status(429)
                self.write({"error": "Rate limit exceeded", "limit": api_key["rate_limit_per_min"]})
                return None
            return {"user_id": api_key["user_id"], "email": api_key["email"],
                    "tier": api_key["tier"], "api_key_id": api_key["id"]}

        self.set_status(401)
        self.write({"error": "Authentication required. Provide Bearer token or X-API-Key header."})
        return None

    def write_error(self, status_code, **kwargs):
        self.write({"error": self.reason or "Unknown error", "status": status_code})


# ─── Auth Endpoints ───

class LoginHandler(BaseHandler):
    def post(self):
        try:
            body = tornado.escape.json_decode(self.request.body)
        except:
            self.set_status(400)
            return self.write({"error": "Invalid JSON"})

        email = body.get("email", "")
        password = body.get("password", "")

        user = authenticate_user(email, password)
        if user:
            token = create_jwt(user)
            self.write({
                "token": token,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "company": user["company"],
                    "tier": user["tier"]
                }
            })
        else:
            self.set_status(401)
            self.write({"error": "Invalid credentials"})


class RegisterHandler(BaseHandler):
    def post(self):
        try:
            body = tornado.escape.json_decode(self.request.body)
        except:
            self.set_status(400)
            return self.write({"error": "Invalid JSON"})

        email = body.get("email", "")
        password = body.get("password", "")
        company = body.get("company", "")

        if not email or not password:
            self.set_status(400)
            return self.write({"error": "Email and password required"})

        user_id, api_key = create_user(email, password, company)
        if user_id:
            self.set_status(201)
            self.write({
                "message": "Account created",
                "user_id": user_id,
                "api_key": api_key,
                "note": "Save your API key — it cannot be retrieved later."
            })
        else:
            self.set_status(409)
            self.write({"error": "Email already registered"})


class ProfileHandler(BaseHandler):
    def get(self):
        user = self.require_auth()
        if not user:
            return

        conn = get_db()
        u = conn.execute("SELECT id, email, company, tier, created_at, last_login FROM users WHERE id = ?",
                         (user["user_id"],)).fetchone()
        keys = conn.execute("SELECT key_prefix, name, tier, rate_limit_per_min, rate_limit_per_day, is_active, created_at, last_used FROM api_keys WHERE user_id = ?",
                            (user["user_id"],)).fetchall()
        usage = conn.execute("SELECT COUNT(*) as total, MAX(created_at) as last_request FROM audit_log WHERE user_id = ?",
                             (user["user_id"],)).fetchone()
        conn.close()

        self.write({
            "user": dict(u) if u else {},
            "api_keys": [dict(k) for k in keys],
            "usage": dict(usage) if usage else {}
        })


# ─── Core API Endpoints ───

class ScoreHandler(BaseHandler):
    def get(self):
        user = self.require_auth()
        if not user:
            return

        zip_code = self.get_argument("zip", "")
        if not zip_code or len(zip_code) < 3:
            self.set_status(400)
            return self.write({"error": "Valid zip code required (parameter: zip)"})

        start = time.time()
        result = compute_composite_score(zip_code)
        elapsed = round((time.time() - start) * 1000, 1)

        result["response_time_ms"] = elapsed

        log_request(user.get("user_id"), user.get("api_key_id"),
                    "score", "/api/v1/score", zip_code=zip_code,
                    response_time_ms=elapsed)

        self.write(result)

    def post(self):
        """Batch scoring — portfolio tier and above."""
        user = self.require_auth()
        if not user:
            return

        if user.get("tier") == "lookup":
            self.set_status(403)
            return self.write({"error": "Batch scoring requires Portfolio or Enterprise tier"})

        try:
            body = tornado.escape.json_decode(self.request.body)
        except:
            self.set_status(400)
            return self.write({"error": "Invalid JSON"})

        zip_codes = body.get("zip_codes", [])
        if not zip_codes or len(zip_codes) > 100:
            self.set_status(400)
            return self.write({"error": "Provide 1-100 zip codes in 'zip_codes' array"})

        start = time.time()
        results = []
        for zc in zip_codes:
            result = compute_composite_score(str(zc))
            results.append(result)

        elapsed = round((time.time() - start) * 1000, 1)

        log_request(user.get("user_id"), user.get("api_key_id"),
                    "batch_score", "/api/v1/score", zip_code=",".join(str(z) for z in zip_codes[:5]),
                    response_time_ms=elapsed)

        self.write({
            "count": len(results),
            "response_time_ms": elapsed,
            "scores": results
        })


class ReportHandler(BaseHandler):
    def get(self):
        user = self.require_auth()
        if not user:
            return

        zip_code = self.get_argument("zip", "")
        if not zip_code:
            self.set_status(400)
            return self.write({"error": "Valid zip code required"})

        score_data = compute_composite_score(zip_code)
        if "error" in score_data:
            self.set_status(400)
            return self.write(score_data)

        pdf_bytes = generate_report(score_data)

        log_request(user.get("user_id"), user.get("api_key_id"),
                    "report", "/api/v1/report", zip_code=zip_code)

        self.set_header("Content-Type", "application/pdf")
        self.set_header("Content-Disposition", f'attachment; filename="namara_risk_report_{zip_code}.pdf"')
        self.write(pdf_bytes)


class BuilderHandler(BaseHandler):
    def get(self):
        user = self.require_auth()
        if not user:
            return

        state = self.get_argument("state", "")
        name = self.get_argument("name", "")
        grade = self.get_argument("grade", "")
        limit = int(self.get_argument("limit", "50"))

        results = search_builders(
            state=state or None,
            name=name or None,
            grade=grade or None,
            limit=min(limit, 100)
        )

        log_request(user.get("user_id"), user.get("api_key_id"),
                    "builders", "/api/v1/builders")

        self.write({"count": len(results), "builders": results})


class UsageHandler(BaseHandler):
    def get(self):
        user = self.require_auth()
        if not user:
            return

        conn = get_db()
        # Last 30 days of usage
        rows = conn.execute("""
            SELECT DATE(created_at) as date, action, COUNT(*) as count
            FROM audit_log WHERE user_id = ? AND created_at > datetime('now', '-30 days')
            GROUP BY date, action ORDER BY date DESC
        """, (user["user_id"],)).fetchall()

        totals = conn.execute("""
            SELECT action, COUNT(*) as count FROM audit_log WHERE user_id = ?
            GROUP BY action
        """, (user["user_id"],)).fetchall()
        conn.close()

        self.write({
            "daily": [dict(r) for r in rows],
            "totals": [dict(t) for t in totals]
        })


# ─── Property-Level Scoring Endpoints ───

class PropertyScoreHandler(BaseHandler):
    def get(self):
        """Score a property by address parameters."""
        user = self.require_auth()
        if not user:
            return

        address = self.get_argument("address", "")
        city = self.get_argument("city", "")
        state = self.get_argument("state", "")
        zip_code = self.get_argument("zip", "")

        if not address or not zip_code:
            self.set_status(400)
            return self.write({"error": "Required: address, zip. Optional: city, state, year_built, pipe_material, builder_name, water_heater_age, has_prv, has_expansion_tank, prior_claims, prior_claim_cost, total_permits, last_permit_year"})

        start = time.time()
        result = compute_property_score(
            address=address,
            city=city,
            state=state or None,
            zip_code=zip_code,
            year_built=int(self.get_argument("year_built", "0")) or None,
            pipe_material=self.get_argument("pipe_material", "") or None,
            builder_name=self.get_argument("builder_name", "") or None,
            water_heater_age=int(self.get_argument("water_heater_age", "0")) or None,
            water_heater_type=self.get_argument("water_heater_type", "tank"),
            has_prv=self.get_argument("has_prv", "false").lower() == "true",
            has_expansion_tank=self.get_argument("has_expansion_tank", "false").lower() == "true",
            prior_claims=int(self.get_argument("prior_claims", "0")),
            prior_claim_cost=float(self.get_argument("prior_claim_cost", "0")),
            total_permits=int(self.get_argument("total_permits", "0")),
            last_permit_year=int(self.get_argument("last_permit_year", "0")) or None,
            sqft=int(self.get_argument("sqft", "0")) or None,
            stories=int(self.get_argument("stories", "0")) or None,
            bathrooms=float(self.get_argument("bathrooms", "0")) or None,
        )
        elapsed = round((time.time() - start) * 1000, 1)
        result["response_time_ms"] = elapsed

        log_request(user.get("user_id"), user.get("api_key_id"),
                    "property_score", "/api/v1/property/score",
                    address=address, zip_code=zip_code,
                    response_time_ms=elapsed)
        self.write(result)

    def post(self):
        """Score a property with JSON body (supports richer input)."""
        user = self.require_auth()
        if not user:
            return

        try:
            body = tornado.escape.json_decode(self.request.body)
        except:
            self.set_status(400)
            return self.write({"error": "Invalid JSON"})

        address = body.get("address", "")
        zip_code = body.get("zip_code", body.get("zip", ""))

        if not address or not zip_code:
            self.set_status(400)
            return self.write({"error": "Required: address, zip_code"})

        start = time.time()
        result = compute_property_score(
            address=address,
            city=body.get("city", ""),
            state=body.get("state", ""),
            zip_code=str(zip_code),
            year_built=body.get("year_built"),
            pipe_material=body.get("pipe_material"),
            builder_name=body.get("builder_name"),
            builder_id=body.get("builder_id"),
            water_heater_age=body.get("water_heater_age"),
            water_heater_type=body.get("water_heater_type", "tank"),
            has_prv=body.get("has_prv", False),
            has_expansion_tank=body.get("has_expansion_tank", False),
            prior_claims=body.get("prior_claims", 0),
            prior_claim_cost=body.get("prior_claim_cost", 0),
            total_permits=body.get("total_permits", 0),
            last_permit_year=body.get("last_permit_year"),
            sqft=body.get("sqft"),
            stories=body.get("stories"),
            bathrooms=body.get("bathrooms"),
        )
        elapsed = round((time.time() - start) * 1000, 1)
        result["response_time_ms"] = elapsed

        log_request(user.get("user_id"), user.get("api_key_id"),
                    "property_score", "/api/v1/property/score",
                    address=address, zip_code=str(zip_code),
                    response_time_ms=elapsed)
        self.write(result)


class PropertyLookupHandler(BaseHandler):
    def get(self):
        """Look up a property in the database."""
        user = self.require_auth()
        if not user:
            return

        address = self.get_argument("address", "")
        city = self.get_argument("city", "")
        state = self.get_argument("state", "")
        zip_code = self.get_argument("zip", "")

        if not address:
            self.set_status(400)
            return self.write({"error": "Address required"})

        prop = lookup_property(address, city, state or "", zip_code)
        if prop:
            self.write({"found": True, "property": prop})
        else:
            self.write({"found": False, "message": "Property not found in database. You can still score it by providing property details."})


class BuilderDetailHandler(BaseHandler):
    def get(self, builder_id):
        """Get detailed builder info and risk scoring."""
        user = self.require_auth()
        if not user:
            return

        builder = lookup_builder_by_id(int(builder_id))
        if not builder:
            self.set_status(404)
            return self.write({"error": "Builder not found"})

        risk_score, risk_factors = score_individual_builder(builder)
        self.write({
            "builder": builder,
            "risk_score": risk_score,
            "risk_factors": risk_factors
        })


class BuilderSearchHandler(BaseHandler):
    def get(self):
        """Enhanced builder search with more filters."""
        user = self.require_auth()
        if not user:
            return

        state = self.get_argument("state", "")
        name = self.get_argument("name", "")
        grade = self.get_argument("grade", "")
        limit = min(int(self.get_argument("limit", "50")), 200)

        conn = get_db()
        query = "SELECT * FROM builders WHERE 1=1"
        params = []

        if state:
            query += " AND state = ?"
            params.append(state.upper())
        if name:
            query += " AND LOWER(name) LIKE ?"
            params.append(f"%{name.lower()}%")
        if grade:
            query += " AND grade = ?"
            params.append(grade.upper())

        # Additional filters
        min_score = self.get_argument("min_score", "")
        max_score = self.get_argument("max_score", "")
        bbb_rating = self.get_argument("bbb_rating", "")
        license_status = self.get_argument("license_status", "")

        if min_score:
            query += " AND composite_score >= ?"
            params.append(float(min_score))
        if max_score:
            query += " AND composite_score <= ?"
            params.append(float(max_score))
        if bbb_rating:
            query += " AND bbb_rating = ?"
            params.append(bbb_rating)
        if license_status:
            query += " AND license_status = ?"
            params.append(license_status)

        query += f" ORDER BY composite_score DESC LIMIT {limit}"
        rows = conn.execute(query, params).fetchall()

        # Get state summary
        state_summary = None
        if state:
            summary = conn.execute("""
                SELECT COUNT(*) as total, AVG(composite_score) as avg_score,
                       MIN(composite_score) as min_score, MAX(composite_score) as max_score,
                       AVG(bbb_complaints) as avg_complaints, AVG(warranty_claim_rate) as avg_warranty
                FROM builders WHERE state = ?
            """, (state.upper(),)).fetchone()
            if summary:
                grade_dist = conn.execute(
                    "SELECT grade, COUNT(*) as count FROM builders WHERE state = ? GROUP BY grade ORDER BY grade",
                    (state.upper(),)
                ).fetchall()
                state_summary = {
                    "total_builders": summary["total"],
                    "avg_score": round(summary["avg_score"], 1) if summary["avg_score"] else 0,
                    "score_range": [round(summary["min_score"], 1) if summary["min_score"] else 0,
                                    round(summary["max_score"], 1) if summary["max_score"] else 0],
                    "avg_complaints": round(summary["avg_complaints"], 1) if summary["avg_complaints"] else 0,
                    "avg_warranty_rate": round(summary["avg_warranty"], 4) if summary["avg_warranty"] else 0,
                    "grade_distribution": {r["grade"]: r["count"] for r in grade_dist}
                }
        conn.close()

        builders_list = [dict(r) for r in rows]
        response = {"count": len(builders_list), "builders": builders_list}
        if state_summary:
            response["state_summary"] = state_summary

        log_request(user.get("user_id"), user.get("api_key_id"),
                    "builder_search", "/api/v1/builders/search")
        self.write(response)


class CompareHandler(BaseHandler):
    def post(self):
        """Compare multiple properties side by side."""
        user = self.require_auth()
        if not user:
            return

        if user.get("tier") == "lookup":
            self.set_status(403)
            return self.write({"error": "Comparison requires Portfolio or Enterprise tier"})

        try:
            body = tornado.escape.json_decode(self.request.body)
        except:
            self.set_status(400)
            return self.write({"error": "Invalid JSON"})

        properties = body.get("properties", [])
        if not properties or len(properties) > 10:
            self.set_status(400)
            return self.write({"error": "Provide 1-10 properties in 'properties' array"})

        start = time.time()
        results = []
        for prop in properties:
            result = compute_property_score(
                address=prop.get("address", ""),
                city=prop.get("city", ""),
                state=prop.get("state", ""),
                zip_code=str(prop.get("zip_code", prop.get("zip", ""))),
                year_built=prop.get("year_built"),
                pipe_material=prop.get("pipe_material"),
                builder_name=prop.get("builder_name"),
                builder_id=prop.get("builder_id"),
                water_heater_age=prop.get("water_heater_age"),
                water_heater_type=prop.get("water_heater_type", "tank"),
                has_prv=prop.get("has_prv", False),
                has_expansion_tank=prop.get("has_expansion_tank", False),
                prior_claims=prop.get("prior_claims", 0),
                prior_claim_cost=prop.get("prior_claim_cost", 0),
                total_permits=prop.get("total_permits", 0),
                last_permit_year=prop.get("last_permit_year"),
            )
            results.append(result)

        elapsed = round((time.time() - start) * 1000, 1)

        # Build comparison summary
        scores = [r.get("composite_score", 0) for r in results if "error" not in r]
        summary = {
            "properties_scored": len(results),
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "highest_risk": max(results, key=lambda x: x.get("composite_score", 0)).get("address", "") if results else "",
            "lowest_risk": min(results, key=lambda x: x.get("composite_score", 0)).get("address", "") if results else "",
        }

        log_request(user.get("user_id"), user.get("api_key_id"),
                    "compare", "/api/v1/compare",
                    response_time_ms=elapsed)

        self.write({
            "summary": summary,
            "response_time_ms": elapsed,
            "properties": results
        })


class StatesHandler(BaseHandler):
    def get(self):
        """Get list of states with builder coverage."""
        user = self.require_auth()
        if not user:
            return

        conn = get_db()
        rows = conn.execute("""
            SELECT state, COUNT(*) as builder_count, AVG(composite_score) as avg_score,
                   SUM(CASE WHEN grade = 'A' THEN 1 ELSE 0 END) as grade_a,
                   SUM(CASE WHEN grade = 'B' THEN 1 ELSE 0 END) as grade_b,
                   SUM(CASE WHEN grade = 'C' THEN 1 ELSE 0 END) as grade_c,
                   SUM(CASE WHEN grade IN ('D', 'F') THEN 1 ELSE 0 END) as grade_df
            FROM builders GROUP BY state ORDER BY state
        """).fetchall()
        conn.close()

        states = []
        for r in rows:
            states.append({
                "state": r["state"],
                "builder_count": r["builder_count"],
                "avg_score": round(r["avg_score"], 1) if r["avg_score"] else 0,
                "grade_distribution": {
                    "A": r["grade_a"], "B": r["grade_b"],
                    "C": r["grade_c"], "D/F": r["grade_df"]
                }
            })

        self.write({"count": len(states), "states": states})


# ─── Admin Endpoints ───

class AdminUsersHandler(BaseHandler):
    def get(self):
        user = self.require_auth()
        if not user or not user.get("is_admin"):
            self.set_status(403)
            return self.write({"error": "Admin access required"})

        conn = get_db()
        users = conn.execute("""
            SELECT u.id, u.email, u.company, u.tier, u.created_at, u.last_login,
                   COUNT(al.id) as total_requests
            FROM users u LEFT JOIN audit_log al ON u.id = al.user_id
            GROUP BY u.id ORDER BY u.created_at DESC
        """).fetchall()
        conn.close()

        self.write({"users": [dict(u) for u in users]})


# ─── Health & Info ───

class HealthHandler(BaseHandler):
    def get(self):
        conn = get_db()
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        builder_count = conn.execute("SELECT COUNT(*) FROM builders").fetchone()[0]
        property_count = conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
        state_count = conn.execute("SELECT COUNT(DISTINCT state) FROM builders").fetchone()[0]
        score_count = conn.execute("SELECT COUNT(*) FROM audit_log WHERE action IN ('score', 'property_score')").fetchone()[0]
        conn.close()

        # Get enrichment status
        enrichment_status = {}
        try:
            from property_enrichment import get_enrichment_status
            enrichment_status = get_enrichment_status()
        except Exception:
            enrichment_status = {"attom_configured": False}

        self.write({
            "status": "healthy",
            "version": "2.1.0",
            "platform": "Namara Water Risk Intelligence",
            "stats": {
                "users": user_count,
                "builders_in_db": builder_count,
                "properties_in_db": property_count,
                "states_covered": state_count,
                "scores_generated": score_count
            },
            "enrichment": enrichment_status,
            "timestamp": datetime.utcnow().isoformat()
        })


class InfoHandler(BaseHandler):
    def get(self):
        conn = get_db()
        builder_count = conn.execute("SELECT COUNT(*) FROM builders").fetchone()[0]
        state_count = conn.execute("SELECT COUNT(DISTINCT state) FROM builders").fetchone()[0]
        property_count = conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
        conn.close()

        self.write({
            "name": "Namara Water Risk Intelligence API",
            "version": "2.0.0",
            "description": "Address-level water risk scoring with property-specific and environmental risk factors",
            "coverage": {
                "builders_in_database": builder_count,
                "states_covered": state_count,
                "properties_in_database": property_count,
            },
            "endpoints": {
                "auth": {
                    "POST /api/v1/auth/login": "Authenticate and get JWT token",
                    "POST /api/v1/auth/register": "Create new account (returns API key)",
                    "GET /api/v1/auth/profile": "Get user profile and API keys",
                },
                "scoring": {
                    "GET /api/v1/score?zip=XXXXX": "Score by zip code (area-level, 7 layers)",
                    "POST /api/v1/score": "Batch score multiple zip codes (Portfolio+)",
                    "GET /api/v1/property/score": "Score by address (property-level factors + environment)",
                    "POST /api/v1/property/score": "Score by address with JSON body",
                    "GET /api/v1/property/lookup": "Look up property in database",
                    "POST /api/v1/compare": "Compare multiple properties side by side (Portfolio+)",
                },
                "builders": {
                    "GET /api/v1/builders?state=FL": "Search builder database",
                    "GET /api/v1/builders/search": "Enhanced builder search with filters",
                    "GET /api/v1/builders/<id>": "Get builder detail with risk scoring",
                    "GET /api/v1/builders/states": "Get builder coverage by state",
                },
                "other": {
                    "GET /api/v1/report?zip=XXXXX": "Generate PDF risk report",
                    "GET /api/v1/usage": "View API usage statistics",
                    "GET /api/v1/health": "Platform health check",
                }
            },
            "authentication": {
                "jwt": "POST to /api/v1/auth/login, use token as 'Bearer <token>' in Authorization header",
                "api_key": "Pass API key as 'X-API-Key' header or 'api_key' query parameter"
            },
            "scoring_models": {
                "zip_level": {
                    "description": "7-layer area-level composite scoring",
                    "formula": "Claims(20%) + Climate(15%) + WaterQuality(15%) + Infrastructure(15%) + Pressure(15%) + Builder(10%) + Regulatory(10%)",
                    "scale": "0-100",
                },
                "property_level": {
                    "description": "Address-level scoring combining property-specific factors with environmental context",
                    "property_factors_weight": "60%",
                    "environmental_weight": "40%",
                    "property_factors": "HomeAge(15%) + PipeMaterial(15%) + WaterHeater(10%) + PermitHistory(8%) + PriorClaims(7%) + ProtectionDevices(5%)",
                    "environmental_factors": "Climate(10%) + WaterQuality(8%) + Pressure(8%) + AreaClaims(8%) + Regulatory(6%)",
                    "scale": "0-100",
                }
            }
        })


# ─── Dashboard (serves frontend) ───

class DashboardHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/html")
        html_path = os.path.join(BASE_DIR, "static", "index.html")
        with open(html_path, "r") as f:
            self.write(f.read())


# ─── Application Setup ───

def make_app():
    init_db()

    return tornado.web.Application([
        # Frontend
        (r"/", DashboardHandler),

        # API Info
        (r"/api/v1", InfoHandler),
        (r"/api/v1/info", InfoHandler),
        (r"/api/v1/health", HealthHandler),

        # Auth
        (r"/api/v1/auth/login", LoginHandler),
        (r"/api/v1/auth/register", RegisterHandler),
        (r"/api/v1/auth/profile", ProfileHandler),

        # Core — zip-level scoring
        (r"/api/v1/score", ScoreHandler),
        (r"/api/v1/report", ReportHandler),
        (r"/api/v1/usage", UsageHandler),

        # Property-level scoring (v2)
        (r"/api/v1/property/score", PropertyScoreHandler),
        (r"/api/v1/property/lookup", PropertyLookupHandler),
        (r"/api/v1/compare", CompareHandler),

        # Builders
        (r"/api/v1/builders", BuilderHandler),
        (r"/api/v1/builders/search", BuilderSearchHandler),
        (r"/api/v1/builders/(\d+)", BuilderDetailHandler),
        (r"/api/v1/builders/states", StatesHandler),

        # Admin
        (r"/api/v1/admin/users", AdminUsersHandler),

        # Static files
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(BASE_DIR, "static")}),
    ],
        debug=os.environ.get("DEBUG", "false").lower() == "true",
        cookie_secret=SECRET_KEY,
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(PORT)
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   NAMARA Water Risk Intelligence Platform v2.0.0             ║
║                                                              ║
║   Dashboard:  http://localhost:{PORT}                          ║
║   API Info:   http://localhost:{PORT}/api/v1                   ║
║   Health:     http://localhost:{PORT}/api/v1/health             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    tornado.ioloop.IOLoop.current().start()
