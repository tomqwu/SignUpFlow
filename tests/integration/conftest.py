"""Integration-tier fixtures (Sprint 4 PR 4.6a).

Resurrects the `api_server` fixture as a uvicorn.Server running in a daemon
thread on an ephemeral port. Lifespan events fire normally so the API
behaves like production.

This is the foundation for PR 4.6b which will revive the previously-failing
integration files file-by-file.
"""

from __future__ import annotations

import contextlib
import os
import socket
import threading
import time
from collections.abc import Iterator

import httpx
import pytest
import uvicorn


def _pick_free_port() -> int:
    """Bind to an ephemeral port, close, and return the port number."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
    finally:
        sock.close()


class _ServerHandle:
    """Tiny container for the running uvicorn instance + connection info."""

    def __init__(self, server: uvicorn.Server, host: str, port: int) -> None:
        self.server = server
        self.host = host
        self.port = port

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


@pytest.fixture(scope="session")
def api_server() -> Iterator[_ServerHandle]:
    """Start uvicorn in a daemon thread on an ephemeral port for the session.

    Tests can hit the server via `api_server.base_url` (e.g.
    `f"{api_server.base_url}/health"`).
    """
    # Disable CSP / rate limits / outbound side-effects for the test process.
    os.environ.setdefault("TESTING", "true")
    os.environ.setdefault("DISABLE_RATE_LIMITS", "true")
    os.environ.setdefault("EMAIL_ENABLED", "false")
    os.environ.setdefault("SMS_ENABLED", "false")
    os.environ.setdefault("SECURITY_CSP_ENABLED", "false")

    # Import the app *after* env is set so module-level config picks it up.
    from api.main import app

    host = "127.0.0.1"
    port = _pick_free_port()

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="warning",
        lifespan="on",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True, name="api_server")
    thread.start()

    # Wait for the server to start accepting connections (or fail fast).
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        if server.started:
            break
        time.sleep(0.05)
    else:  # pragma: no cover - defensive
        raise RuntimeError("api_server failed to start within 10s")

    handle = _ServerHandle(server=server, host=host, port=port)
    try:
        yield handle
    finally:
        server.should_exit = True
        thread.join(timeout=5.0)


@pytest.fixture(scope="session")
def api_client(api_server: _ServerHandle) -> Iterator[httpx.Client]:
    """Reusable httpx.Client pinned to the running api_server."""
    with httpx.Client(base_url=api_server.base_url, timeout=10.0) as client:
        yield client


# Override root conftest's autouse fixtures so the integration tier owns its
# own lifecycle. Without these, tests/conftest.py's reset_database_between_tests
# fights uvicorn's session-scoped engine.
@pytest.fixture(autouse=True)
def mock_authentication() -> Iterator[None]:
    """Suppress root conftest auth mocking — integration tier uses real HTTP."""
    yield


@pytest.fixture(autouse=True)
def reset_database_between_tests() -> Iterator[None]:
    """Suppress root conftest DB reset — integration tier owns the DB lifecycle."""
    yield


@contextlib.contextmanager
def _suppress_keyboard_interrupt() -> Iterator[None]:
    """Used by the fixture teardown so a slow shutdown doesn't bubble up."""
    try:
        yield
    except KeyboardInterrupt:  # pragma: no cover
        pass
