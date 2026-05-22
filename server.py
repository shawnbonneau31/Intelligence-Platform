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
from scoring import compute_composite_score, search_builders, zip_to_state
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
        score_count = conn.execute("SELECT COUNT(*) FROM audit_log WHERE action = 'score'").fetchone()[0]
        conn.close()

        self.write({
            "status": "healthy",
            "version": "1.0.0",
            "platform": "Namara Water Risk Intelligence",
            "stats": {
                "users": user_count,
                "builders_in_db": builder_count,
                "scores_generated": score_count
            },
            "timestamp": datetime.utcnow().isoformat()
        })


class InfoHandler(BaseHandler):
    def get(self):
        self.write({
            "name": "Namara Water Risk Intelligence API",
            "version": "1.0.0",
            "description": "Property-level water risk scoring across 5 data layers",
            "endpoints": {
                "POST /api/v1/auth/login": "Authenticate and get JWT token",
                "POST /api/v1/auth/register": "Create new account (returns API key)",
                "GET /api/v1/auth/profile": "Get user profile and API keys",
                "GET /api/v1/score?zip=XXXXX": "Score a single address by zip code",
                "POST /api/v1/score": "Batch score multiple zip codes (Portfolio+)",
                "GET /api/v1/report?zip=XXXXX": "Generate PDF risk report",
                "GET /api/v1/builders?state=FL": "Search builder quality database",
                "GET /api/v1/usage": "View API usage statistics",
                "GET /api/v1/health": "Platform health check",
            },
            "authentication": {
                "jwt": "POST to /api/v1/auth/login, use token as 'Bearer <token>' in Authorization header",
                "api_key": "Pass API key as 'X-API-Key' header or 'api_key' query parameter"
            },
            "data_layers": [
                "Climate & Freeze Risk (Open-Meteo Archive API)",
                "Water Quality (EPA SDWIS / USGS)",
                "Infrastructure Aging (Census ACS)",
                "Builder Quality (State contractor boards, permits, court records)",
                "Regulatory & Mandate Landscape (State legislature records)"
            ],
            "scoring": {
                "formula": "Climate(25%) + WaterQuality(25%) + Infrastructure(25%) + BuilderQuality(15%) + Regulatory(10%)",
                "scale": "0-100",
                "levels": {"0-30": "Low (Green)", "31-60": "Moderate (Yellow)", "61-80": "High (Orange)", "81-100": "Critical (Red)"}
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

        # Core
        (r"/api/v1/score", ScoreHandler),
        (r"/api/v1/report", ReportHandler),
        (r"/api/v1/builders", BuilderHandler),
        (r"/api/v1/usage", UsageHandler),

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
║   NAMARA Water Risk Intelligence Platform v1.0.0             ║
║                                                              ║
║   Dashboard:  http://localhost:{PORT}                          ║
║   API Info:   http://localhost:{PORT}/api/v1                   ║
║   Health:     http://localhost:{PORT}/api/v1/health             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    tornado.ioloop.IOLoop.current().start()
