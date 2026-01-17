import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from flask import Flask, session
from werkzeug.security import generate_password_hash
import json
import auth.auth.auth as auth_module


@pytest.fixture
def app(tmp_path):
    """
    Izolowana aplikacja Flask do testów auth
    """

    users = {
        "admin": {
            "password": generate_password_hash("admin123"),
            "role": "admin",
        }
    }

    auth_dir = tmp_path / "auth"
    auth_dir.mkdir()

    (auth_dir / "users.json").write_text(json.dumps(users))
    (auth_dir / "login-failures.json").write_text("{}")

    auth_module.BASE_DIR = auth_dir
    auth_module.USERS_FILE = auth_dir / "users.json"
    auth_module.LOGIN_FAILURES_FILE = auth_dir / "login-failures.json"

    auth_bp = auth_module.auth_bp
    require_login = auth_module.require_login

    app = Flask(__name__)
    app.secret_key = "test-secret"
    app.config["TESTING"] = True

    app.register_blueprint(auth_bp)

    @app.route("/")
    @require_login
    def index():
        return "INDEX OK"

    return app


@pytest.fixture
def client(app):
    return app.test_client()


# =========================
# TESTY
# =========================

def test_login_page_available(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert b"LOGIN PAGE" in r.data


def test_login_success_sets_session(client):
    with client:
        r = client.post(
            "/login",
            data={"username": "admin", "password": "admin123"},
        )

        assert r.status_code == 200
        assert session.get("user") == "admin"
        assert session.get("role") == "admin"


def test_login_failure(client):
    r = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
    )

    assert r.status_code == 200
    assert b"Invalid credentials" in r.data


def test_ip_block_after_failures(client):
    for _ in range(3):
        client.post(
            "/login",
            data={"username": "admin", "password": "wrong"},
        )

    r = client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
    )

    assert b"Too many failed attempts" in r.data


def test_logout_clears_session(client):
    with client:
        client.post(
            "/login",
            data={"username": "admin", "password": "admin123"},
        )

        r = client.get("/logout", follow_redirects=True)

        assert r.status_code == 200
        assert session.get("user") is None
