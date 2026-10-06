"""Flask application factory for KAN-1 Search flight."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from flight_search.repository import CatalogLoadError, FlightRepository
from flight_search.routes import bp, register_error_handlers
from flight_search.safe_log import configure_logging, log_event

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = PROJECT_ROOT / "data" / "flights.json"

csrf = CSRFProtect()


def create_app(
    *,
    catalog_path: Path | None = None,
    testing: bool = False,
) -> Flask:
    """Create the Flask app. Fail-fast if the catalog cannot be loaded (D8)."""
    configure_logging()

    secret = os.environ.get("SECRET_KEY")
    if not secret:
        raise RuntimeError("SECRET_KEY environment variable is required")

    app = Flask(
        __name__,
        template_folder="templates",
    )
    app.config["SECRET_KEY"] = secret
    app.config["TESTING"] = testing
    app.config["DEBUG"] = False
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["WTF_CSRF_TIME_LIMIT"] = None

    path = Path(catalog_path) if catalog_path is not None else DEFAULT_CATALOG
    try:
        repo = FlightRepository.load(path)
    except CatalogLoadError:
        log_event("Refusing to bind HTTP: catalog load failed")
        raise

    app.extensions["flights"] = repo
    app.extensions["catalog_path"] = str(path)

    csrf.init_app(app)
    app.register_blueprint(bp)
    register_error_handlers(app)
    return app
