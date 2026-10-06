from pathlib import Path

import pytest

from flight_search import create_app
from flight_search.repository import CatalogLoadError


def test_create_app_fail_fast_missing_catalog(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-not-for-production")
    with pytest.raises(CatalogLoadError):
        create_app(catalog_path=tmp_path / "missing.json")


def test_create_app_requires_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app()
