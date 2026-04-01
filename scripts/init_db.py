from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS agenda_items;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL,
  display_name TEXT NOT NULL,
  bio TEXT NOT NULL,
  password_plain TEXT NOT NULL,
  password_hash TEXT NOT NULL
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
  PRIMARY KEY(user_id, course_id),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE announcements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  course_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  sender TEXT NOT NULL,
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE agenda_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  course_id INTEGER,
  start_time TEXT NOT NULL,
  end_time TEXT NOT NULL,
  title TEXT NOT NULL,
  location TEXT NOT NULL,
  description TEXT NOT NULL,
  FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE SET NULL
);

CREATE TABLE notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


def main() -> None:
    db_path = Path(os.environ.get("DB_PATH") or Path("instance") / "app.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)

    users = [
        ("student", "student", "Keis Student", "Compte étudiant de démo.", "password123"),
        ("teacher", "teacher", "Tristan Teacher", "Compte enseignant de démo.", "Password!2026"),
    ]
    for username, role, display_name, bio, pw in users:
        conn.execute(
            "INSERT INTO users(username, role, display_name, bio, password_plain, password_hash) VALUES (?, ?, ?, ?, ?, ?)",
            (username, role, display_name, bio, pw, generate_password_hash(pw, method="pbkdf2:sha256")),
        )

    courses = [
        ("SSI101", "Sécurité des SI — Web", "Badr Tajini", "Authentification, sessions, XSS, injections."),
        ("NET202", "Réseaux & Protocoles", "Tristan Hardouin", "TCP/IP, DNS, TLS, analyse réseau."),
        ("DEV150", "Dév Web (mini LMS)", "Keis Aissaoui", "Front minimal, back simulé, SQLite."),
    ]
    for code, title, teacher, summary in courses:
        conn.execute("INSERT INTO courses(code, title, teacher, summary) VALUES (?, ?, ?, ?)", (code, title, teacher, summary))

    # Enrollments (student inscrit partout, teacher sur 2 cours pour démo)
    student_id = conn.execute("SELECT id FROM users WHERE username='student'").fetchone()[0]
    teacher_id = conn.execute("SELECT id FROM users WHERE username='teacher'").fetchone()[0]
    course_ids = [r[0] for r in conn.execute("SELECT id FROM courses").fetchall()]
    for cid in course_ids:
        conn.execute("INSERT INTO enrollments(user_id, course_id) VALUES (?, ?)", (student_id, cid))
    conn.execute("INSERT INTO enrollments(user_id, course_id) VALUES (?, ?)", (teacher_id, course_ids[0]))
    conn.execute("INSERT INTO enrollments(user_id, course_id) VALUES (?, ?)", (teacher_id, course_ids[1]))

    # Announcements
    conn.executemany(
        "INSERT INTO announcements(course_id, created_at, title, body) VALUES (?, ?, ?, ?)",
        [
            (course_ids[0], "2026-04-01T08:00:00Z", "Bienvenue", "Ce cours sert de terrain de jeu pour le Cyber Challenge."),
            (course_ids[0], "2026-04-01T09:00:00Z", "Rappel", "Ne testez que l'application locale du projet."),
            (course_ids[1], "2026-04-01T10:00:00Z", "TP Wireshark", "Capture + analyse DNS/TLS en environnement contrôlé."),
        ],
    )

    # Messages
    conn.executemany(
        "INSERT INTO messages(user_id, created_at, sender, subject, body) VALUES (?, ?, ?, ?, ?)",
        [
            (student_id, "2026-04-01T08:30:00Z", "noreply@moodle.local", "Compte activé", "Votre compte étudiant est prêt."),
            (student_id, "2026-04-01T08:45:00Z", "teacher@moodle.local", "Devoir", "Pensez à lire les consignes du projet SSI."),
            (teacher_id, "2026-04-01T08:55:00Z", "admin@moodle.local", "Accès enseignant", "Vous avez accès au mode admin."),
        ],
    )

    # Agenda items
    conn.executemany(
        "INSERT INTO agenda_items(course_id, start_time, end_time, title, location, description) VALUES (?, ?, ?, ?, ?, ?)",
        [
            (course_ids[0], "2026-04-02 09:00", "2026-04-02 10:30", "SSI — Auth & Sessions", "B-204", "Cookies, sessions, CSRF"),
            (course_ids[0], "2026-04-03 14:00", "2026-04-03 16:00", "SSI — XSS & Injections", "C-110", "Reflected / Stored XSS, SQLi"),
            (course_ids[1], "2026-04-04 11:00", "2026-04-04 12:30", "NET — TLS", "A-301", "Handshake, certificats, notions d'HSTS"),
        ],
    )

    conn.commit()
    conn.close()
    print(f"DB initialisée: {db_path}")


if __name__ == "__main__":
    main()
