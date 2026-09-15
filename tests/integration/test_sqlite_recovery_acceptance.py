"""Application acceptance against an encrypted, restored SQLite snapshot."""

from __future__ import annotations

import json
import os
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import api.database
from alembic import command
from alembic.config import Config
from api.main import app
from api.models import (
    Assignment,
    Event,
    Notification,
    NotificationStatus,
    NotificationType,
    Organization,
    Person,
    Solution,
)
from api.security import hash_password
from api.tasks.notifications import send_email_task
from api.timeutils import utcnow
from scripts.sqlite_recovery import (
    create_backup,
    generate_key,
    initialize_workspace,
    restore_backup,
)

ROOT = Path(__file__).resolve().parents[2]
CURRENT_HEAD = "a9c2e4f6b8d0"


def _migrate(path: Path) -> None:
    url = f"sqlite:///{path}"
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    with patch.dict(
        os.environ,
        {"DATABASE_URL": url, "SIGNUPFLOW_LOAD_DOTENV": "false"},
        clear=False,
    ):
        command.upgrade(config, "head")


def _seed_domain_state(path: Path) -> dict[str, int]:
    engine = create_engine(f"sqlite:///{path}")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    now = utcnow().replace(tzinfo=None)
    identities = {
        "church": {
            "admin": ("church-admin", "church-admin@example.com", ["admin"]),
            "member": (
                "church-sound",
                "church-sound@example.com",
                ["volunteer", "sound"],
            ),
        },
        "basketball": {
            "admin": ("basketball-admin", "basketball-admin@example.com", ["admin"]),
            "member": (
                "basketball-guard",
                "basketball-guard@example.com",
                ["volunteer", "point_guard"],
            ),
        },
    }
    notification_ids: dict[str, int] = {}
    with Session.begin() as session:
        for domain, identity in identities.items():
            org_id = f"recovery-{domain}"
            session.add(Organization(id=org_id, name=f"Recovery {domain.title()}", config={}))
            admin_id, admin_email, admin_roles = identity["admin"]
            member_id, member_email, member_roles = identity["member"]
            session.add_all(
                [
                    Person(
                        id=admin_id,
                        org_id=org_id,
                        name=f"{domain.title()} Admin",
                        email=admin_email,
                        password_hash=hash_password("AdminPass123!"),
                        password_changed_at=now,
                        roles=admin_roles,
                    ),
                    Person(
                        id=member_id,
                        org_id=org_id,
                        name=f"{domain.title()} Member",
                        email=member_email,
                        password_hash=hash_password("MemberPass123!"),
                        password_changed_at=now,
                        roles=member_roles,
                    ),
                ]
            )
            event = Event(
                id=f"{domain}-event",
                org_id=org_id,
                type="service" if domain == "church" else "game",
                start_time=now + timedelta(days=7),
                end_time=now + timedelta(days=7, hours=2),
                extra_data={"title": f"Recovered {domain.title()}"},
            )
            solution = Solution(
                org_id=org_id,
                hard_violations=0,
                soft_score=0,
                health_score=100,
                is_published=True,
                published_at=now,
                scope_start=(now + timedelta(days=7)).date(),
                scope_end=(now + timedelta(days=8)).date(),
                scope_event_ids=[event.id],
                scope_fingerprint=f"{domain}-recovery-fingerprint",
            )
            session.add_all([event, solution])
            session.flush()
            status = "accepted" if domain == "church" else "swap_requested"
            session.add(
                Assignment(
                    solution_id=solution.id,
                    event_id=event.id,
                    person_id=member_id,
                    role=member_roles[-1],
                    status="confirmed" if status == "accepted" else status,
                    response_status=status,
                    responded_by_person_id=member_id,
                    responded_at=now,
                    commitment_revision=1,
                    response_revision=1,
                )
            )
            notification = Notification(
                org_id=org_id,
                recipient_id=member_id,
                event_id=event.id,
                type=NotificationType.ASSIGNMENT,
                status=(
                    NotificationStatus.DELIVERED
                    if domain == "church"
                    else NotificationStatus.PENDING
                ),
                delivery_key=f"recovery:{domain}:assignment",
                template_data={"domain": domain},
                sent_at=now if domain == "church" else None,
                delivered_at=now if domain == "church" else None,
            )
            session.add(notification)
            session.flush()
            notification_ids[domain] = notification.id
    engine.dispose()
    return notification_ids


def _login(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}


def test_restored_church_and_basketball_state_passes_application_acceptance(
    tmp_path: Path, monkeypatch
) -> None:
    source = tmp_path / "source.sqlite"
    _migrate(source)
    notification_ids = _seed_domain_state(source)
    workspace = tmp_path / "recovery"
    key = tmp_path / "recovery.key"
    initialize_workspace(workspace)
    generate_key(key)

    backup = create_backup(workspace, source, key, "domain-state")
    restored = restore_backup(workspace, backup.bundle_path, key, "domain-state")
    restored_url = f"sqlite:///{restored.database_path}"
    restored_engine = create_engine(
        restored_url, connect_args={"check_same_thread": False, "timeout": 30}
    )
    RestoredSession = sessionmaker(autocommit=False, autoflush=False, bind=restored_engine)
    monkeypatch.setattr(api.database, "DATABASE_URL", restored_url)
    monkeypatch.setattr(api.database, "engine", restored_engine)
    monkeypatch.setattr(api.database, "SessionLocal", RestoredSession)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            church_member = _login(client, "church-sound@example.com", "MemberPass123!")
            basketball_member = _login(client, "basketball-guard@example.com", "MemberPass123!")
            church_admin = _login(client, "church-admin@example.com", "AdminPass123!")

            church_assignments = client.get("/api/v1/assignments/me", headers=church_member)
            assert church_assignments.status_code == 200
            assert church_assignments.json()["items"][0]["response_status"] == "accepted"

            basketball_assignments = client.get("/api/v1/assignments/me", headers=basketball_member)
            assert basketball_assignments.status_code == 200
            assert basketball_assignments.json()["items"][0]["response_status"] == "swap_requested"

            church_inbox = client.get(
                "/api/v1/notifications/",
                params={"org_id": "recovery-church"},
                headers=church_member,
            )
            assert church_inbox.status_code == 200
            assert church_inbox.json()["notifications"][0]["status"] == "delivered"

            basketball_inbox = client.get(
                "/api/v1/notifications/",
                params={"org_id": "recovery-basketball"},
                headers=basketball_member,
            )
            assert basketball_inbox.status_code == 200
            assert basketball_inbox.json()["notifications"][0]["status"] == "pending"

            foreign = client.get("/api/v1/organizations/recovery-basketball", headers=church_admin)
            assert foreign.status_code == 403

            with patch("api.tasks.notifications._send_assignment_notification") as send_email:
                result = send_email_task.run(notification_ids["church"])
            assert result["status"] == "already_sent"
            send_email.assert_not_called()

        with restored_engine.connect() as connection:
            assert (
                connection.scalar(text("SELECT version_num FROM alembic_version")) == CURRENT_HEAD
            )
            assert connection.scalar(text("SELECT count(*) FROM organizations")) == 2
            assert (
                connection.scalar(text("SELECT count(*) FROM solutions WHERE is_published = 1"))
                == 2
            )
    finally:
        restored_engine.dispose()

    receipt = json.loads(restored.receipt_path.read_text(encoding="utf-8"))
    assert receipt["state"] == "isolated_no_cutover"
    assert receipt["outbound_delivery"] == "not_started_by_recovery_tool"
    assert receipt["restore_duration_ms"] > 0
    assert receipt["recovery_point_age_seconds"] >= 0
