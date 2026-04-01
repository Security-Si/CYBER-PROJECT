import os
import re
import sqlite3
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

from app import create_app


SCHEMA = """
PRAGMA foreign_keys=ON;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL,
  display_name TEXT NOT NULL,
  bio TEXT NOT NULL,
  password_plain TEXT NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE agenda_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  course_id INTEGER,
  start_time TEXT NOT NULL,
  end_time TEXT NOT NULL,
  title TEXT NOT NULL,
  location TEXT NOT NULL,
  description TEXT NOT NULL
);

CREATE TABLE notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  sender TEXT NOT NULL,
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE courses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  teacher TEXT NOT NULL,
  summary TEXT NOT NULL
);

CREATE TABLE enrollments (
  user_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  PRIMARY KEY(user_id, course_id)
);
"""


def seed_db(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.execute(
        "INSERT INTO users(username, role, display_name, bio, password_plain, password_hash) VALUES (?, ?, ?, ?, ?, ?)",
        (
            "student",
            "student",
            "Student",
            "bio",
            "password123",
            generate_password_hash("password123", method="pbkdf2:sha256"),
        ),
    )
    conn.execute(
        "INSERT INTO courses(code, title, teacher, summary) VALUES (?, ?, ?, ?)",
        ("SSI101", "SSI", "Teacher", "x"),
    )
    conn.execute(
        "INSERT INTO enrollments(user_id, course_id) VALUES (?, ?)",
        (1, 1),
    )
    conn.execute(
        "INSERT INTO agenda_items(course_id, start_time, end_time, title, location, description) VALUES (?, ?, ?, ?, ?, ?)",
        (1, "2026-04-02 09:00", "2026-04-02 10:30", "SSI", "B-204", "Test"),
    )
    conn.commit()
    conn.close()


@pytest.fixture()
def app_tmp(tmp_path: Path):
    db_path = tmp_path / "app.db"
    seed_db(db_path)
    os.environ["DB_PATH"] = str(db_path)
    yield
    os.environ.pop("DB_PATH", None)


def _csrf_from(html: bytes) -> str:
    m = re.search(rb'name="_csrf" value="([^"]+)"', html)
    assert m, "CSRF token introuvable"
    return m.group(1).decode()


def test_vuln_sqli_bypass(app_tmp):
    os.environ["APP_MODE"] = "vuln"
    app = create_app()
    app.testing = True
    with app.test_client() as c:
        r = c.post("/login", data={"username": "x' OR 1=1 -- ", "password": "x"}, follow_redirects=False)
        assert r.status_code == 302
        assert r.headers["Location"].endswith("/dashboard")


def test_secure_blocks_open_redirect_and_requires_csrf(app_tmp):
    os.environ["APP_MODE"] = "secure"
    app = create_app()
    app.testing = True
    with app.test_client() as c:
        page = c.get("/login?next=https://evil.example")
        token = _csrf_from(page.data)
        r = c.post(
            "/login?next=https://evil.example",
            data={"_csrf": token, "username": "student", "password": "password123"},
            follow_redirects=False,
        )
        assert r.status_code == 302
        assert r.headers["Location"] == "/dashboard"


def test_xss_stored_vuln_vs_secure(app_tmp):
    payload = '<img src=x onerror="alert(1)">'

    # Vuln: payload revient tel quel
    os.environ["APP_MODE"] = "vuln"
    app = create_app()
    app.testing = True
    with app.test_client() as c:
        r = c.post("/login", data={"username": "student", "password": "password123"}, follow_redirects=True)
        assert r.status_code == 200
        c.post("/agenda", data={"title": "x", "note": payload}, follow_redirects=True)
        page = c.get("/agenda")
        assert payload.encode() in page.data

    # Secure: payload échappé
    os.environ["APP_MODE"] = "secure"
    app = create_app()
    app.testing = True
    with app.test_client() as c:
        login_page = c.get("/login")
        token = _csrf_from(login_page.data)
        r = c.post(
            "/login",
            data={"_csrf": token, "username": "student", "password": "password123"},
            follow_redirects=True,
        )
        assert r.status_code == 200
        agenda_page = c.get("/agenda")
        token2 = _csrf_from(agenda_page.data)
        c.post("/agenda", data={"_csrf": token2, "title": "x", "note": payload}, follow_redirects=True)
        page = c.get("/agenda")
        assert payload.encode() not in page.data
        assert b"&lt;img" in page.data
