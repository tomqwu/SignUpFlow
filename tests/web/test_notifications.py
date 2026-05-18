"""Marathon P1.5 — notifications inbox + unread badge + email prefs."""

from __future__ import annotations

from api.models import EmailPreference, Notification
from api.timeutils import utcnow
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _login(client, db, *, pid, org, email, roles=None):
    seed_person(db, person_id=pid, org_id=org, email=email, roles=roles or ["volunteer"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _notif(db, *, org, recipient, ntype="assignment", opened=False):
    n = Notification(
        org_id=org,
        recipient_id=recipient,
        type=ntype,
        status="sent",
        created_at=utcnow(),
        opened_at=utcnow() if opened else None,
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def test_inbox_requires_auth(client):
    assert client.get("/v/inbox").status_code == 303


def test_inbox_lists_and_unread_badge(client, db):
    tok = _login(client, db, pid="n1", org="n_o1", email="n1@web.test")
    _notif(db, org="n_o1", recipient="n1", ntype="assignment")
    _notif(db, org="n_o1", recipient="n1", ntype="reminder", opened=True)

    inbox = client.get("/v/inbox", cookies={SESSION_COOKIE: tok})
    assert inbox.status_code == 200
    assert 'id="inbox-list"' in inbox.text
    assert 'id="notif-prefs"' in inbox.text
    assert "New assignment" in inbox.text
    assert "1 unread" in inbox.text

    # Schedule header shows the unread badge.
    sched = client.get("/v/schedule", cookies={SESSION_COOKIE: tok})
    assert "Inbox (1)" in sched.text


def test_mark_read_and_read_all(client, db):
    tok = _login(client, db, pid="n2", org="n_o2", email="n2@web.test")
    a = _notif(db, org="n_o2", recipient="n2")
    b = _notif(db, org="n_o2", recipient="n2")

    r = client.post(f"/v/inbox/{a.id}/read", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    db.refresh(a)
    assert a.opened_at is not None

    r2 = client.post("/v/inbox/read-all", cookies={SESSION_COOKIE: tok})
    assert r2.status_code == 200
    db.refresh(b)
    assert b.opened_at is not None
    assert "No notifications yet" not in r2.text
    assert "unread" not in r2.text  # all read → no "unread" anywhere


def test_cannot_read_another_users_notification(client, db):
    tok = _login(client, db, pid="n3", org="n_o3", email="n3@web.test")
    seed_person(db, person_id="n3b", org_id="n_o3", email="n3b@web.test", roles=["volunteer"])
    other = _notif(db, org="n_o3", recipient="n3b")

    r = client.post(f"/v/inbox/{other.id}/read", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200  # handled gracefully
    db.refresh(other)
    assert other.opened_at is None  # untouched


def test_preferences_save_and_validate(client, db):
    tok = _login(client, db, pid="n4", org="n_o4", email="n4@web.test")
    r = client.post(
        "/v/inbox/preferences",
        data={
            "frequency": "daily",
            "digest_hour": "9",
            "types": ["assignment", "cancellation"],
        },
        cookies={SESSION_COOKIE: tok},
    )
    assert r.status_code == 200
    assert "Preferences saved" in r.text
    pref = (
        db.query(EmailPreference)
        .filter(EmailPreference.org_id == "n_o4", EmailPreference.person_id == "n4")
        .first()
    )
    assert pref.frequency == "daily"
    assert pref.digest_hour == 9
    assert set(pref.enabled_types) == {"assignment", "cancellation"}

    bad = client.post(
        "/v/inbox/preferences",
        data={"frequency": "daily", "digest_hour": "99", "types": ["assignment"]},
        cookies={SESSION_COOKIE: tok},
    )
    assert bad.status_code == 400
    assert "between 0 and 23" in bad.text
