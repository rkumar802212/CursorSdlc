"""Live Flask process for Playwright E2E (debug=False)."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE = "http://127.0.0.1:5000"


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: Playwright browser tests against live Flask")


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex((host, port)) == 0


def _free_port(host: str = "127.0.0.1") -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def _health_ok(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/health", timeout=2) as resp:
            body = resp.read().decode("utf-8")
            return resp.status == 200 and '"ok"' in body
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


@pytest.fixture(scope="session")
def e2e_base_url():
    configured = os.environ.get("E2E_BASE_URL")
    if configured:
        configured = configured.rstrip("/")
        if not _health_ok(configured):
            pytest.fail(f"E2E_BASE_URL {configured} did not return /health ok")
        yield configured
        return

    default = DEFAULT_BASE.rstrip("/")
    if _health_ok(default):
        yield default
        return

    host = "127.0.0.1"
    port = 5000 if not _port_open(host, 5000) else _free_port(host)
    base = f"http://{host}:{port}"

    env = os.environ.copy()
    env.setdefault("SECRET_KEY", "e2e-local-secret-not-for-production")
    env["FLASK_DEBUG"] = "0"
    env["FLIGHT_SEARCH_PORT"] = str(port)
    proc = subprocess.Popen(
        [sys.executable, "-m", "flight_search"],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 30
    ready = False
    while time.time() < deadline:
        if proc.poll() is not None:
            out = proc.stdout.read().decode("utf-8", errors="replace") if proc.stdout else ""
            pytest.fail(f"Flask exited before health ok. Output:\n{out[:2000]}")
        if _health_ok(base):
            ready = True
            break
        time.sleep(0.2)
    if not ready:
        proc.terminate()
        pytest.fail("Timed out waiting for GET /health {\"status\":\"ok\"}")
    try:
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
