"""Sprint 11.10 — single-date availability exceptions."""

from __future__ import annotations

import re

from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _login(client, db, email="ex@web.test", pid="ex_user"):
    seed_person(db, person_id=pid, email=email)
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_exceptions_section_empty(client, db):
    token = _login(client, db)
    resp = client.get("/v/availability", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Single-date blocks" in resp.text
    assert "No single-date blocks" in resp.text


def test_add_exception_then_listed(client, db):
    token = _login(client, db, email="exa@web.test", pid="exa")
    resp = client.post(
        "/v/availability/exception",
        data={"exception_date": "2026-09-13"},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert 'id="exceptions-section"' in resp.text
    assert "13 SEP 2026" in resp.text.upper()
    assert "No single-date blocks" not in resp.text


def test_add_exception_idempotent(client, db):
    token = _login(client, db, email="exi@web.test", pid="exi")
    for _ in range(2):
        resp = client.post(
            "/v/availability/exception",
            data={"exception_date": "2026-09-20"},
            cookies={SESSION_COOKIE: token},
        )
    assert resp.status_code == 200
    # Only one row despite two adds.
    assert resp.text.upper().count("20 SEP 2026") == 1


def test_invalid_date_rejected(client, db):
    token = _login(client, db, email="exb@web.test", pid="exb")
    resp = client.post(
        "/v/availability/exception",
        data={"exception_date": "not-a-date"},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "form-error" in resp.text
    assert "No single-date blocks" in resp.text


def test_delete_exception(client, db):
    token = _login(client, db, email="exd@web.test", pid="exd")
    client.post(
        "/v/availability/exception",
        data={"exception_date": "2026-10-01"},
        cookies={SESSION_COOKIE: token},
    )
    page = client.get("/v/availability", cookies={SESSION_COOKIE: token})
    m = re.search(r"/v/availability/exception/(\d+)/delete", page.text)
    assert m
    resp = client.post(
        f"/v/availability/exception/{m.group(1)}/delete",
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "No single-date blocks" in resp.text


def test_exception_endpoints_require_auth(client):
    r1 = client.post("/v/availability/exception", data={"exception_date": "2026-09-13"})
    assert r1.status_code == 303
    r2 = client.post("/v/availability/exception/1/delete")
    assert r2.status_code == 303
