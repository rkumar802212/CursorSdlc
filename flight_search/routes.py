"""HTTP routes for KAN-1 flight search."""

from __future__ import annotations

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_wtf.csrf import CSRFError

from flight_search.dates import today_iso
from flight_search.forms import SearchForm
from flight_search.safe_log import log_exception
from flight_search.validator import parse_passengers, validate_search

bp = Blueprint("main", __name__)


def _render_search(
    form: SearchForm,
    *,
    validation_errors: list[str] | None = None,
    flights: list | None = None,
    show_no_flights: bool = False,
    passenger_context: int | None = None,
):
    return render_template(
        "search.html",
        form=form,
        server_today=today_iso(),
        validation_errors=validation_errors or [],
        flights=flights or [],
        show_no_flights=show_no_flights,
        passenger_context=passenger_context,
    )


@bp.get("/")
def index():
    return _render_search(SearchForm())


@bp.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("main.index"), code=302)

    form = SearchForm()
    errors = validate_search(
        form.departure_city.data,
        form.arrival_city.data,
        form.travel_date.data,
        form.passengers.data,
    )
    if errors:
        return _render_search(form, validation_errors=errors), 200

    try:
        passengers = parse_passengers(form.passengers.data)
        repo = current_app.extensions["flights"]
        results = repo.search(
            form.departure_city.data,
            form.arrival_city.data,
            form.travel_date.data.strip(),
            passengers=passengers,
        )
    except Exception as exc:  # noqa: BLE001 — unexpected errors become generic 500
        log_exception("search_failed", exc)
        return render_template("errors/500.html"), 500

    if results:
        return (
            _render_search(
                form,
                flights=results,
                passenger_context=passengers,
            ),
            200,
        )
    return (
        _render_search(
            form,
            show_no_flights=True,
            passenger_context=passengers,
        ),
        200,
    )


@bp.get("/health")
def health():
    if "flights" not in current_app.extensions:
        return jsonify({"status": "unavailable"}), 503
    return jsonify({"status": "ok"})


def register_error_handlers(app):
    @app.errorhandler(CSRFError)
    def handle_csrf(err):
        log_exception("csrf_failed", err)
        return render_template("errors/400.html"), 400

    @app.errorhandler(404)
    def handle_404(_err):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def handle_500(err):
        log_exception("internal_error", err)
        return render_template("errors/500.html"), 500
