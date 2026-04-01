from __future__ import annotations

import sqlite3
from datetime import datetime
from urllib.parse import urlparse

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    jsonify,
    render_template,
    request,
    session,
    url_for,
)
from markupsafe import Markup
from werkzeug.security import check_password_hash

from .db import close_db, get_db
from .security import csrf_token, is_secure_mode, login_required, rate_limit_or_429, require_csrf


bp = Blueprint("main", __name__)


@bp.before_app_request
def _csrf_and_db_hooks():
    require_csrf()


@bp.teardown_app_request
def _teardown_db(_):
    close_db()


@bp.app_context_processor
def inject_globals():
    return {
        "APP_MODE": current_app.config.get("APP_MODE"),
        "csrf_token": csrf_token,
    }


@bp.get("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        rate_limit_or_429("login")

        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        next_url = request.args.get("next") or url_for("main.dashboard")

        db = get_db()
        user = None

        if is_secure_mode():
            user = db.execute(
                "SELECT id, username, role, display_name, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            if not user or not check_password_hash(user["password_hash"], password):
                error = "Identifiants invalides."
            else:
                session.clear()
                session["user_id"] = int(user["id"])
                session["username"] = user["username"]
                session["role"] = user["role"]
                session["display_name"] = user["display_name"]
                return redirect(_safe_next(next_url))
        else:
            query = (
                "SELECT id, username, role, display_name FROM users "
                f"WHERE username = '{username}' AND password_plain = '{password}'"
            )
            try:
                user = db.execute(query).fetchone()
            except sqlite3.Error:
                user = None
            if not user:
                error = "Identifiants invalides."
            else:
                session["user_id"] = int(user["id"])
                session["username"] = user["username"]
                session["role"] = user["role"]
                session["display_name"] = user["display_name"]
                return redirect(next_url)

    return render_template("login.html", error=error)


def _safe_next(next_url: str) -> str:
    # En mode secure: éviter open redirect (autoriser seulement path relatif local).
    if not is_secure_mode():
        return next_url
    parsed = urlparse(next_url)
    if parsed.scheme or parsed.netloc:
        return url_for("main.dashboard")
    if not next_url.startswith("/"):
        return url_for("main.dashboard")
    return next_url


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.after_app_request
def add_security_headers(resp):
    if is_secure_mode():
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        resp.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        )
    return resp


@bp.get("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user_id = int(session["user_id"])

    courses = db.execute(
        """
        SELECT c.id, c.code, c.title, c.teacher
        FROM courses c
        JOIN enrollments e ON e.course_id = c.id
        WHERE e.user_id = ?
        ORDER BY c.code ASC
        """,
        (user_id,),
    ).fetchall()

    upcoming = db.execute(
        """
        SELECT a.start_time, a.end_time, a.title, a.location
        FROM agenda_items a
        ORDER BY a.start_time ASC
        LIMIT 5
        """
    ).fetchall()

    stats = {
        "courses": len(courses),
        "messages": db.execute("SELECT COUNT(*) AS c FROM messages WHERE user_id = ?", (user_id,)).fetchone()["c"],
        "notes": db.execute("SELECT COUNT(*) AS c FROM notes WHERE user_id = ?", (user_id,)).fetchone()["c"],
    }

    return render_template("dashboard.html", courses=courses, upcoming=upcoming, stats=stats)


@bp.get("/courses")
@login_required
def courses():
    db = get_db()
    user_id = int(session["user_id"])
    rows = db.execute(
        """
        SELECT c.id, c.code, c.title, c.teacher, c.summary
        FROM courses c
        JOIN enrollments e ON e.course_id = c.id
        WHERE e.user_id = ?
        ORDER BY c.code ASC
        """,
        (user_id,),
    ).fetchall()
    return render_template("courses.html", courses=rows)


@bp.get("/courses/<int:course_id>")
@login_required
def course_detail(course_id: int):
    db = get_db()
    user_id = int(session["user_id"])

    enrolled = db.execute(
        "SELECT 1 FROM enrollments WHERE user_id = ? AND course_id = ?",
        (user_id, course_id),
    ).fetchone()
    if not enrolled and is_secure_mode():
        abort(403)

    course = db.execute("SELECT id, code, title, teacher, summary FROM courses WHERE id = ?", (course_id,)).fetchone()
    if not course:
        abort(404)

    ann = db.execute(
        "SELECT created_at, title, body FROM announcements WHERE course_id = ? ORDER BY created_at DESC",
        (course_id,),
    ).fetchall()
    return render_template("course_detail.html", course=course, announcements=ann)


@bp.get("/messages")
@login_required
def messages():
    db = get_db()
    user_id = int(session["user_id"])
    rows = db.execute(
        "SELECT id, created_at, sender, subject FROM messages WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    return render_template("messages.html", messages=rows)


@bp.get("/messages/<int:message_id>")
@login_required
def message_detail(message_id: int):
    db = get_db()
    user_id = int(session["user_id"])

    if is_secure_mode():
        msg = db.execute(
            "SELECT id, created_at, sender, subject, body FROM messages WHERE id = ? AND user_id = ?",
            (message_id, user_id),
        ).fetchone()
    else:
        msg = db.execute(
            "SELECT id, created_at, sender, subject, body FROM messages WHERE id = ?",
            (message_id,),
        ).fetchone()

    if not msg:
        abort(404)
    return render_template("message_detail.html", msg=msg)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    user_id = int(session["user_id"])

    if request.method == "POST":
        display_name = (request.form.get("display_name") or "").strip()
        bio = request.form.get("bio") or ""

        if is_secure_mode():
            if not display_name or len(display_name) > 40:
                abort(400)
            if len(bio) > 800:
                abort(400)
        else:
            # Vulnérable: aucune validation.
            pass

        db.execute(
            "UPDATE users SET display_name = ?, bio = ? WHERE id = ?",
            (display_name or session.get("username") or "user", bio, user_id),
        )
        db.commit()
        session["display_name"] = display_name or session.get("username")
        return redirect(url_for("main.profile"))

    user = db.execute(
        "SELECT username, role, display_name, bio FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()

    bio = user["bio"]
    if not is_secure_mode():
        bio = Markup(bio)

    return render_template("profile.html", user=user, bio=bio)


@bp.get("/search")
@login_required
def search():
    q = request.args.get("q") or ""
    q_display = q
    if not is_secure_mode():
        q_display = Markup(q)
    return render_template("search.html", q=q, q_display=q_display)

@bp.get("/admin/users")
@login_required
def admin_users():
    db = get_db()
    if is_secure_mode() and session.get("role") != "teacher":
        abort(403)

    users = db.execute(
        "SELECT id, username, role, display_name, bio, password_plain FROM users ORDER BY id ASC"
    ).fetchall()
    return render_template("admin_users.html", users=users)


@bp.get("/api/users")
@login_required
def api_users():
    db = get_db()

    if is_secure_mode() and session.get("role") != "teacher":
        abort(403)

    if is_secure_mode():
        rows = db.execute("SELECT id, username, role, display_name FROM users ORDER BY id ASC").fetchall()
    else:
        rows = db.execute("SELECT id, username, role, display_name, password_plain FROM users ORDER BY id ASC").fetchall()
    data = [dict(r) for r in rows]
    return jsonify({"users": data})



@bp.route("/agenda", methods=["GET", "POST"])
@login_required
def agenda():
    db = get_db()
    user_id = int(session["user_id"])

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        note = request.form.get("note") or ""

        if is_secure_mode():
            if not title or len(title) > 80:
                abort(400)
            if len(note) > 2000:
                abort(400)
        else:
            # Vulnérable: pas de validation, permet de pousser des payloads.
            pass

        now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        db.execute(
            "INSERT INTO notes(user_id, created_at, title, body) VALUES (?, ?, ?, ?)",
            (user_id, now, title or "Sans titre", note),
        )
        db.commit()
        return redirect(url_for("main.agenda"))

    items = db.execute(
        "SELECT start_time, end_time, title, location, description FROM agenda_items ORDER BY start_time ASC"
    ).fetchall()

    notes = db.execute(
        "SELECT created_at, title, body FROM notes WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
        (user_id,),
    ).fetchall()

    # En mode vulnérable: marquer le body comme sûr (stored XSS).
    rendered_notes = []
    for n in notes:
        body = n["body"]
        if not is_secure_mode():
            body = Markup(body)
        rendered_notes.append({"created_at": n["created_at"], "title": n["title"], "body": body})

    return render_template("agenda.html", items=items, notes=rendered_notes)
