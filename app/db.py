import sqlite3
from typing import Any

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    conn = getattr(g, "_db", None)
    if conn is None:
        conn = sqlite3.connect(current_app.config["DB_PATH"], check_same_thread=False)
        conn.row_factory = sqlite3.Row
        setattr(g, "_db", conn)
    return conn


def close_db(_: Any = None) -> None:
    conn = getattr(g, "_db", None)
    if conn is None:
        return
    try:
        conn.close()
    finally:
        delattr(g, "_db")
