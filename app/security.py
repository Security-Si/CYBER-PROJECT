from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Dict, Tuple

from flask import abort, current_app, redirect, request, session, url_for


def is_secure_mode() -> bool:
    return current_app.config.get("APP_MODE") == "secure"


def login_required(view: Callable) -> Callable:
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("main.login", next=request.path))
        return view(*args, **kwargs)

    return wrapper


@dataclass
class SimpleRateLimiter:
    # key -> (reset_ts, count)
    buckets: Dict[str, Tuple[float, int]]
    window_seconds: int = 60
    max_requests: int = 10

    def hit(self, key: str) -> bool:
        now = time.time()
        reset_ts, count = self.buckets.get(key, (now + self.window_seconds, 0))
        if now > reset_ts:
            reset_ts, count = now + self.window_seconds, 0
        count += 1
        self.buckets[key] = (reset_ts, count)
        return count <= self.max_requests


_limiter = SimpleRateLimiter(buckets={})


def rate_limit_or_429(scope: str) -> None:
    if not is_secure_mode():
        return

    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    key = f"{scope}:{ip}"
    if not _limiter.hit(key):
        abort(429)


def csrf_token() -> str:
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def require_csrf() -> None:
    if not is_secure_mode():
        return
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        sent = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
        if not sent or sent != session.get("_csrf_token"):
            abort(400)

