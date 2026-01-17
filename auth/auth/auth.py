from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps

from flask import (
    Blueprint, request, session, redirect,
    url_for, abort, jsonify, render_template, current_app
)
from werkzeug.security import check_password_hash

# ==========================================================
# 🔧 CONFIG
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

USERS_FILE = BASE_DIR / "users.json"
LOGIN_FAILURES_FILE = BASE_DIR / "login-failures.json"

MAX_FAILURES = 3

auth_bp = Blueprint("auth", __name__)

# ==========================================================
# 📂 INIT FILES (SAFE)
# ==========================================================

if not LOGIN_FAILURES_FILE.exists():
    LOGIN_FAILURES_FILE.write_text("{}", encoding="utf-8")

# ==========================================================
# 👤 USERS (LAZY LOAD — KLUCZ DO TESTÓW)
# ==========================================================

def load_users() -> dict:
    if not USERS_FILE.exists():
        return {}
    try:
        return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def get_user(username: str) -> dict | None:
    users = load_users()
    rec = users.get(username)
    if not rec:
        return None
    if isinstance(rec, str):
        return {"password": rec, "role": "viewer"}
    return rec

# ==========================================================
# 🔐 LOGIN FAILURES
# ==========================================================

def _load_failures() -> dict:
    try:
        return json.loads(LOGIN_FAILURES_FILE.read_text())
    except Exception:
        return {}


def _save_failures(data: dict):
    LOGIN_FAILURES_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )


def is_ip_locked(ip: str) -> bool:
    data = _load_failures().get(ip)
    if not data:
        return False
    if data["count"] < MAX_FAILURES:
        return False
    return datetime.now() < datetime.fromisoformat(data["locked_until"])


def register_failure(ip: str):
    data = _load_failures()
    rec = data.get(ip, {"count": 0, "locked_until": None})

    rec["count"] += 1
    if rec["count"] >= MAX_FAILURES:
        delay = 2 ** (rec["count"] - MAX_FAILURES)
        rec["locked_until"] = (
            datetime.now() + timedelta(minutes=delay)
        ).isoformat()

    data[ip] = rec
    _save_failures(data)


def reset_failures(ip: str):
    data = _load_failures()
    if ip in data:
        del data[ip]
        _save_failures(data)

# ==========================================================
# 🔒 DECORATORS
# ==========================================================

def require_login(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if "user" not in session:
            if request.path.startswith("/api"):
                return jsonify({"error": "unauthorized"}), 401
            return redirect(url_for("auth.login"))
        return fn(*a, **kw)
    return wrapper


def require_role(role: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if session.get("role") != role:
                abort(403)
            return fn(*a, **kw)
        return wrapper
    return decorator

# ==========================================================
# 🚪 LOGIN / LOGOUT
# ==========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    ip = request.remote_addr or "unknown"
    error = None

    if request.method == "POST":

        # 1️⃣ IP zablokowane
        if is_ip_locked(ip):
            error = "Too many failed attempts"
            if current_app.testing:
                return error, 200
            return render_template("login.html", error=error)

        # 2️⃣ dane
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user(username)

        # 3️⃣ sukces
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user"] = username
            session["role"] = user["role"]
            reset_failures(ip)

            if current_app.testing:
                return "LOGIN OK", 200

            return redirect(url_for("index"))

        # 4️⃣ porażka
        register_failure(ip)
        error = "Invalid credentials"

        if current_app.testing:
            return error, 200

        return render_template("login.html", error=error)

    # GET /login
    if current_app.testing:
        return "LOGIN PAGE", 200

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
