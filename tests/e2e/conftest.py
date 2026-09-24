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
def mail_db_path(tmp_path_factory) -> str:
    """Separate database for workflows that intentionally enable local mail capture."""
    return str(tmp_path_factory.mktemp("e2e-mail") / "e2e-mail.db")


@pytest.fixture(scope="session")
def mail_capture_dir(tmp_path_factory) -> Path:
    """Owned local RFC 822 sink; no provider or non-loopback connection is used."""
    return tmp_path_factory.mktemp("e2e-mail-capture")


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
def mail_live_server(mail_db_path, mail_capture_dir):
    """Real app with only the owned local `.eml` delivery backend enabled."""
    import os

    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    env = build_test_environment(
        os.environ,
        database_url=f"sqlite:///{mail_db_path}",
        secret_key="e2e-mail-secret-key-min-32-chars-long-xxxx",
        email_capture_dir=str(mail_capture_dir),
        frontend_url=base,
    )
    log_path = Path(mail_db_path).with_name("server.log")
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
        deadline = time.time() + 60
        try:
            while time.time() < deadline:
                if proc.poll() is not None:
                    raise RuntimeError(
                        "mail uvicorn exited before becoming ready\n" + read_server_log(log_path)
                    )
                try:
                    with urllib.request.urlopen(f"{base}/health", timeout=2) as response:
                        if response.status == 200:
                            break
                except Exception:
                    time.sleep(0.5)
            else:
                raise RuntimeError(
                    "mail live server did not become healthy in 60s\n" + read_server_log(log_path)
                )
            yield base
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


#: Every engine a user might bring. Chromium alone missed a Safari-only
#: failure that left the whole UI unstyled, so the cross-browser tour runs all
#: three, and SIGNUPFLOW_E2E_BROWSER picks the engine for the rest of the suite.
ENGINES = ("chromium", "webkit", "firefox")

#: The app's own assets. A page whose stylesheet or scripts fail to load does
#: not raise a JavaScript error, so without this check an unstyled, script-less
#: page passed every test.
_ASSET_TYPES = {"stylesheet", "script", "font", "image"}
_ASSET_PREFIX = "/web/static/"


@pytest.fixture(scope="session")
def _playwright():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        yield p


def launch_engine(playwright, name: str):
    """Launch one engine, failing with the fix when it is not installed."""
    try:
        return getattr(playwright, name).launch()
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.fail(
                f"Playwright {name} is not installed. Run: "
                "poetry run playwright install chromium webkit firefox"
            )
        raise


@pytest.fixture(scope="session")
def engine_browser(_playwright):
    """Launch-once factory: engine_browser("webkit") returns a shared browser."""
    launched: dict = {}

    def _get(name: str):
        if name not in launched:
            launched[name] = launch_engine(_playwright, name)
        return launched[name]

    yield _get
    for browser in launched.values():
        browser.close()


@pytest.fixture(scope="session")
def _browser(engine_browser):
    import os

    return engine_browser(os.getenv("SIGNUPFLOW_E2E_BROWSER", "chromium"))


def track_page_health(ctx) -> None:
    """Record uncaught JavaScript errors and failed app assets on a context."""
    from urllib.parse import urlsplit

    ctx.signupflow_javascript_errors = []
    ctx.signupflow_asset_failures = []

    def is_app_asset(request) -> bool:
        return request.resource_type in _ASSET_TYPES and urlsplit(request.url).path.startswith(
            _ASSET_PREFIX
        )

    def on_failed(request):
        if is_app_asset(request):
            ctx.signupflow_asset_failures.append(f"{request.url}: {request.failure}")

    def on_response(response):
        if response.status >= 400 and is_app_asset(response.request):
            ctx.signupflow_asset_failures.append(f"{response.url}: HTTP {response.status}")

    def track_page(pg):
        pg.on("pageerror", lambda error: ctx.signupflow_javascript_errors.append(str(error)))

    ctx.on("page", track_page)
    ctx.on("requestfailed", on_failed)
    ctx.on("response", on_response)


@pytest.fixture
def new_context(_browser):
    """Factory for isolated browser contexts. Multi-actor flows (admin +
    volunteers) MUST each get their own context — pages in one context
    share cookies, so a second login silently overwrites the session."""
    made = []

    def _make():
        ctx = _browser.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=2)
        track_page_health(ctx)
        made.append(ctx)
        return ctx

    yield _make
    for context in made:
        assert_page_health(context)
        context.close()


def assert_no_javascript_errors(context) -> None:
    """Fail every browser context on uncaught JavaScript errors."""
    assert not context.signupflow_javascript_errors, context.signupflow_javascript_errors


def assert_page_health(context) -> None:
    """Fail on uncaught JavaScript errors and on app assets that did not load."""
    assert_no_javascript_errors(context)
    assert not context.signupflow_asset_failures, context.signupflow_asset_failures


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
