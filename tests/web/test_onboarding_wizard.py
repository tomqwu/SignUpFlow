"""Overnight B3 — first-run onboarding wizard."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Event, Invitation, OnboardingProgress, Solution
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="ob_o", pid="ob_admin", email="admin@ob.test"):
    seed_person(db, person_id=pid, org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _invite(db, org, by, *, iid, token):
    db.add(
        Invitation(
            id=iid,
            org_id=org,
            email=f"{iid}@ob.test",
            name="Invitee",
            roles=["volunteer"],
            invited_by=by,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
    )
    db.commit()


def test_onboarding_requires_auth(client):
    assert client.get("/a/onboarding").status_code == 303


def test_fresh_admin_sees_zero_progress(client, db):
    tok = _admin(client, db)
    r = client.get("/a/onboarding", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    assert "0 of 4 done" in r.text
    row = (
        db.query(OnboardingProgress)
        .filter(
            OnboardingProgress.person_id == "ob_admin",
            OnboardingProgress.org_id == "ob_o",
        )
        .first()
    )
    assert row is not None and row.wizard_step_completed == 0


def test_partial_progress_and_dashboard_banner(client, db):
    tok = _admin(client, db, org="ob_o3", pid="ob_a3", email="a3@ob.test")
    _invite(db, "ob_o3", "ob_a3", iid="inv3", token="tk3")
    r = client.get("/a/onboarding", cookies={SESSION_COOKIE: tok})
    assert "1 of 4 done" in r.text
    d = client.get("/a/dashboard", cookies={SESSION_COOKIE: tok})
    assert 'id="onboarding-banner"' in d.text and "1/4" in d.text


def test_full_progress_marks_complete(client, db):
    tok = _admin(client, db, org="ob_o2", pid="ob_a2", email="a2@ob.test")
    _invite(db, "ob_o2", "ob_a2", iid="inv2", token="tk2")
    start = datetime.utcnow() + timedelta(days=3)
    db.add(
        Event(
            id="ev1",
            org_id="ob_o2",
            type="Svc",
            start_time=start,
            end_time=start + timedelta(hours=1),
        )
    )
    db.add(
        Solution(
            org_id="ob_o2",
            hard_violations=0,
            soft_score=1.0,
            health_score=90.0,
            is_published=True,
            published_at=datetime.utcnow(),
        )
    )
    db.commit()
    r = client.get("/a/onboarding", cookies={SESSION_COOKIE: tok})
    assert "4 of 4 done" in r.text
    assert 'id="onboarding-complete"' in r.text
    # complete → no dashboard nudge.
    d = client.get("/a/dashboard", cookies={SESSION_COOKIE: tok})
    assert 'id="onboarding-banner"' not in d.text


def test_skip_persists_and_hides_banner(client, db):
    tok = _admin(client, db, org="ob_o4", pid="ob_a4", email="a4@ob.test")
    r = client.post("/a/onboarding/skip", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 303 and r.headers["location"] == "/a/dashboard"
    row = (
        db.query(OnboardingProgress)
        .filter(
            OnboardingProgress.person_id == "ob_a4",
            OnboardingProgress.org_id == "ob_o4",
        )
        .first()
    )
    assert row.onboarding_skipped is True
    d = client.get("/a/dashboard", cookies={SESSION_COOKIE: tok})
    assert 'id="onboarding-banner"' not in d.text
