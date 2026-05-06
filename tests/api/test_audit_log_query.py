"""Audit log read endpoint tests.

GET /api/v1/audit-logs is admin-only and scoped to the caller's organization.
The endpoint itself emits a `data.exported` audit row each time it's read.
"""

from datetime import UTC, datetime, timedelta

import pytest

from api.models import AuditAction, AuditLog
from tests.api.conftest import auth_headers, seed_org, seed_user


def _seed_audit_row(db, *, action: str, org_id: str, when: datetime, user_id: str = "test-user"):
    """Insert one AuditLog row directly. Bypasses the tenancy guard."""
    row = AuditLog(
        id=f"audit_{action}_{when.timestamp()}_{org_id}",
        user_id=user_id,
        user_email="seed@example.com",
        organization_id=org_id,
        action=action,
        resource_type="person",
        resource_id=user_id,
        details={},
        timestamp=when,
        status="success",
    )
    db.add(row)
    db.commit()


def _admin_setup(client, suffix: str):
    org_id = f"audit-org-{suffix}"
    seed_org(client, org_id)
    seed_user(
        client,
        org_id,
        email=f"admin-{suffix}@audit.org",
        name="Admin",
        password="AdminPass1!",
    )
    return org_id, auth_headers(client, email=f"admin-{suffix}@audit.org", password="AdminPass1!")


@pytest.mark.no_mock_auth
class TestAuditLogReadAccess:
    def test_volunteer_cannot_read_audit_logs(self, client, db):
        org_id = "audit-org-vol"
        seed_org(client, org_id)
        seed_user(client, org_id, email="admin@v.org", name="Admin", password="AdminPass1!")
        seed_user(
            client,
            org_id,
            email="vol@v.org",
            name="Vol",
            password="VolPass1!",
            roles=["volunteer"],
        )
        vol_hdrs = auth_headers(client, email="vol@v.org", password="VolPass1!")
        resp = client.get("/api/v1/audit-logs", headers=vol_hdrs)
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestAuditLogScoping:
    def test_admin_sees_only_own_org_rows(self, client, db):
        org_id, admin_hdrs = _admin_setup(client, "scope")
        other_org = "audit-org-other"
        seed_org(client, other_org)

        now = datetime.now(UTC)
        _seed_audit_row(db, action=AuditAction.LOGIN_SUCCESS, org_id=org_id, when=now)
        _seed_audit_row(db, action=AuditAction.LOGIN_SUCCESS, org_id=other_org, when=now)

        resp = client.get("/api/v1/audit-logs", headers=admin_hdrs)
        assert resp.status_code == 200
        rows = resp.json()
        assert all(r["organization_id"] == org_id for r in rows)


@pytest.mark.no_mock_auth
class TestAuditLogFilters:
    def test_filter_by_action(self, client, db):
        org_id, admin_hdrs = _admin_setup(client, "action")
        now = datetime.now(UTC)
        _seed_audit_row(db, action=AuditAction.LOGIN_SUCCESS, org_id=org_id, when=now)
        _seed_audit_row(db, action=AuditAction.PASSWORD_RESET_REQUESTED, org_id=org_id, when=now)

        resp = client.get(
            f"/api/v1/audit-logs?action={AuditAction.LOGIN_SUCCESS}", headers=admin_hdrs
        )
        assert resp.status_code == 200
        rows = resp.json()
        assert all(r["action"] == AuditAction.LOGIN_SUCCESS for r in rows)
        assert len(rows) >= 1

    def test_filter_by_date_range(self, client, db):
        org_id, admin_hdrs = _admin_setup(client, "date")
        now = datetime.now(UTC)
        old = now - timedelta(days=10)
        _seed_audit_row(db, action=AuditAction.LOGIN_SUCCESS, org_id=org_id, when=old)
        _seed_audit_row(db, action=AuditAction.LOGIN_SUCCESS, org_id=org_id, when=now)

        # Request only the last day; old row excluded.
        # Use Z suffix so the URL doesn't need to escape '+' (which becomes space).
        start = (now - timedelta(days=1)).isoformat().replace("+00:00", "Z")
        resp = client.get("/api/v1/audit-logs", params={"start_date": start}, headers=admin_hdrs)
        assert resp.status_code == 200
        rows = resp.json()
        # All returned rows must be within the range
        for r in rows:
            assert r["timestamp"] >= start

    def test_ordering_is_desc_by_timestamp(self, client, db):
        org_id, admin_hdrs = _admin_setup(client, "order")
        t1 = datetime.now(UTC) - timedelta(minutes=5)
        t2 = datetime.now(UTC) - timedelta(minutes=1)
        _seed_audit_row(
            db, action=AuditAction.LOGIN_SUCCESS, org_id=org_id, when=t1, user_id="u-old"
        )
        _seed_audit_row(
            db, action=AuditAction.LOGIN_SUCCESS, org_id=org_id, when=t2, user_id="u-new"
        )

        resp = client.get(
            f"/api/v1/audit-logs?action={AuditAction.LOGIN_SUCCESS}", headers=admin_hdrs
        )
        rows = resp.json()
        timestamps = [r["timestamp"] for r in rows]
        assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.no_mock_auth
class TestAuditLogPagination:
    def test_limit_caps_results(self, client, db):
        org_id, admin_hdrs = _admin_setup(client, "page")
        now = datetime.now(UTC)
        for i in range(5):
            _seed_audit_row(
                db,
                action=AuditAction.LOGIN_SUCCESS,
                org_id=org_id,
                when=now - timedelta(seconds=i),
                user_id=f"u{i}",
            )

        resp = client.get("/api/v1/audit-logs?limit=2", headers=admin_hdrs)
        assert resp.status_code == 200
        rows = resp.json()
        assert len(rows) == 2


@pytest.mark.no_mock_auth
class TestAuditLogSelfAuditing:
    def test_query_emits_data_exported_row(self, client, db):
        org_id, admin_hdrs = _admin_setup(client, "self")
        before = (
            db.query(AuditLog)
            .filter(AuditLog.action == AuditAction.DATA_EXPORTED)
            .filter(AuditLog.organization_id == org_id)
            .count()
        )
        client.get("/api/v1/audit-logs", headers=admin_hdrs)
        after = (
            db.query(AuditLog)
            .filter(AuditLog.action == AuditAction.DATA_EXPORTED)
            .filter(AuditLog.organization_id == org_id)
            .count()
        )
        assert after == before + 1
