import os

from dotenv import load_dotenv
from flask import Flask

from .bootstrap import ensure_db
from .config import AppConfig
from .routes import bp


def create_app() -> Flask:
    load_dotenv()

    config = AppConfig.from_env(os.environ)
    app = Flask(__name__, static_folder="static", template_folder="templates")

    app.secret_key = config.secret_key or os.environ.get("FALLBACK_SECRET_KEY") or "change-me-in-prod"

    app.config.update(
        APP_MODE=config.mode,
        DB_PATH=config.db_path,
        SESSION_COOKIE_HTTPONLY=True if config.mode == "secure" else False,
        SESSION_COOKIE_SAMESITE="Lax" if config.mode == "secure" else None,
        # En dev local HTTP, laisser False. En prod derrière HTTPS, mettre True.
        SESSION_COOKIE_SECURE=config.mode == "secure" and bool(os.environ.get("FORCE_SECURE_COOKIE")),
    )

    # Bootstrap DB (utile en serverless / Vercel où la DB peut être absente).
    ensure_db(app.config["DB_PATH"])

    app.register_blueprint(bp)
    return app
