"""WSGI entrypoint. Catalog load happens in create_app (fail-fast)."""

from dotenv import load_dotenv

load_dotenv()

from flight_search import create_app  # noqa: E402

app = create_app()
