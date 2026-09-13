"""Committed browser e2e harness (overnight marathon, 2026-05-19).

Boots the real app (uvicorn) against a throwaway SQLite DB and drives it
with Playwright — the durable replacement for the prior throwaway
`/tmp/*_driver.py` scripts. Deterministic: fresh DB per session, no
external network, sandbox env (Stripe/SMS/email all disabled by default).

Run only via the dedicated e2e lane: `pytest tests/e2e/`.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

from tests.test_environment import build_test_environment

pytestmark = pytest.mark.e2e


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def read_server_log(path: Path) -> str:
    """Return a bounded diagnostic tail from the owned test server."""
    try:
        return path.read_text(errors="replace")[-4000:]
    except OSError as exc:
        return f"Could not read test server log: {exc}"


@pytest.fixture(scope="session")
def db_path(tmp_path_factory) -> str:
    """Filesystem path of the throwaway SQLite DB the live server uses —
    e2e tests may seed rows directly through it (sqlite3)."""
    return str(tmp_path_factory.mktemp("e2e") / "e2e.db")


@pytest.fixture(scope="session")
def live_server(db_path):
    """Real uvicorn process on an ephemeral port, fresh DB, /health-gated."""
    import os

    port = _free_port()
    dsn = f"sqlite:///{db_path}"
    env = build_test_environment(
        os.environ,
        database_url=dsn,
        secret_key="e2e-overnight-secret-key-min-32-chars-long-xx",
    )
    log_path = Path(db_path).with_name("server.log")
    with log_path.open("w", encoding="utf-8") as server_log:
        proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=str(Path(__file__).resolve().parents[2]),
            env=env,
            stdout=server_log,
            stderr=subprocess.STDOUT,
        )
        base = f"http://127.0.0.1:{port}"
        deadline = time.time() + 60
        try:
            while time.time() < deadline:
                if proc.poll() is not None:
                    raise RuntimeError(
                        "uvicorn exited before becoming ready\n" + read_server_log(log_path)
                    )
                try:
                    with urllib.request.urlopen(f"{base}/health", timeout=2) as response:
                        if response.status == 200:
                            break
                except Exception:
                    time.sleep(0.5)
            else:
                raise RuntimeError(
                    "live server did not become healthy in 60s\n" + read_server_log(log_path)
                )
            yield base
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


@pytest.fixture(scope="session")
def _browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def new_context(_browser):
    """Factory for isolated browser contexts. Multi-actor flows (admin +
    volunteers) MUST each get their own context — pages in one context
    share cookies, so a second login silently overwrites the session."""
    made = []

    def _make():
        ctx = _browser.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=2)
        ctx.signupflow_javascript_errors = []

        def track_page(pg):
            pg.on("pageerror", lambda error: ctx.signupflow_javascript_errors.append(str(error)))

        ctx.on("page", track_page)
        made.append(ctx)
        return ctx

    yield _make
    for context in made:
        assert_no_javascript_errors(context)
        context.close()


def assert_no_javascript_errors(context) -> None:
    """Fail every browser context on uncaught JavaScript errors."""
    assert not context.signupflow_javascript_errors, context.signupflow_javascript_errors


@pytest.fixture
def context(new_context):
    """Fresh isolated browser context per test (clean cookies)."""
    return new_context()


@pytest.fixture
def page(context):
    """A page that auto-accepts hx-confirm dialogs and fails the test on
    any uncaught JS error (catches the CSP/Alpine class of bug)."""
    pg = context.new_page()
    errors: list[str] = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("dialog", lambda d: d.accept())
    pg.test_errors = errors  # asserted by tests/helpers at end
    yield pg
