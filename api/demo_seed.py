"""Demo organization loaded by ``make setup`` so a new install has a login.

The data mirrors ``examples/church``: the same people with the same
qualifications, and the same weekly pattern of a Saturday rehearsal and a
Sunday service. Event dates are computed from today rather than copied, so
the demo is always upcoming whenever it is loaded.

Every account shares one password that is printed by setup and published in
the README. That is only acceptable because this is local demo data: the seed
refuses a production environment, and every address is on ``example.com``,
which is reserved and can never receive mail.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from api.models import Event, Organization, Person
from api.security import hash_password
from api.timeutils import utcnow

DEMO_ORG_ID = "grace-community-church-demo"
DEMO_ORG_NAME = "Grace Community Church (demo)"
DEMO_PASSWORD = "DemoPass123!"
DEMO_ADMIN_EMAIL = "admin@example.com"

#: (id, name, qualification), as in examples/church/people.yaml.
_VOLUNTEERS = (
    ("worship-leader-a", "Worship Leader A", "worship_leader"),
    ("worship-leader-b", "Worship Leader B", "worship_leader"),
    ("musician-a", "Musician A", "musician"),
    ("musician-b", "Musician B", "musician"),
)

_WEEKS = 6


class DemoSeedRefusedError(RuntimeError):
    """Raised instead of publishing a known password into a real deployment."""


@dataclass(frozen=True)
class DemoLogin:
    label: str
    email: str


@dataclass(frozen=True)
class DemoSeedResult:
    created: bool
    logins: tuple[DemoLogin, ...]
    password: str = DEMO_PASSWORD


def _logins() -> tuple[DemoLogin, ...]:
    volunteers = tuple(
        DemoLogin(f"Volunteer ({qualification})", f"{person_id}@example.com")
        for person_id, _name, qualification in _VOLUNTEERS
    )
    return (DemoLogin("Admin", DEMO_ADMIN_EMAIL), *volunteers)


def _weekly_events(now: datetime) -> list[Event]:
    """A rehearsal each Saturday evening and a service each Sunday morning."""
    days_to_saturday = (5 - now.weekday()) % 7 or 7
    first_saturday = (now + timedelta(days=days_to_saturday)).date()
    events: list[Event] = []
    for week in range(1, _WEEKS + 1):
        saturday = first_saturday + timedelta(weeks=week - 1)
        sunday = saturday + timedelta(days=1)
        events.append(
            Event(
                id=f"demo-rehearsal-w{week}",
                org_id=DEMO_ORG_ID,
                type="Rehearsal",
                start_time=datetime.combine(saturday, time(18, 0)),
                end_time=datetime.combine(saturday, time(20, 0)),
                extra_data={"role_counts": {"musician": 1}},
            )
        )
        events.append(
            Event(
                id=f"demo-service-w{week}",
                org_id=DEMO_ORG_ID,
                type="Sunday worship",
                start_time=datetime.combine(sunday, time(10, 0)),
                end_time=datetime.combine(sunday, time(12, 0)),
                extra_data={"role_counts": {"worship_leader": 1}},
            )
        )
    return events


def seed_demo(db: Session) -> DemoSeedResult:
    """Load the demo organization once. Later calls change nothing."""
    if os.getenv("ENVIRONMENT", "").strip().lower() == "production":
        raise DemoSeedRefusedError(
            "Refusing to load demo accounts with a published password into a "
            "production environment."
        )

    if db.query(Organization).filter(Organization.id == DEMO_ORG_ID).first():
        return DemoSeedResult(created=False, logins=_logins())

    now = utcnow()
    password_hash = hash_password(DEMO_PASSWORD)
    people = [
        Person(
            id="demo-admin",
            org_id=DEMO_ORG_ID,
            name="Demo Admin",
            email=DEMO_ADMIN_EMAIL,
            password_hash=password_hash,
            roles=["admin"],
            status="active",
            password_changed_at=now,
            extra_data={},
        )
    ]
    for person_id, name, qualification in _VOLUNTEERS:
        people.append(
            Person(
                id=f"demo-{person_id}",
                org_id=DEMO_ORG_ID,
                name=name,
                email=f"{person_id}@example.com",
                password_hash=password_hash,
                roles=["volunteer", qualification],
                status="active",
                password_changed_at=now,
                extra_data={},
            )
        )

    db.add(Organization(id=DEMO_ORG_ID, name=DEMO_ORG_NAME, region="CA-ON", config={}))
    db.add_all(people)
    db.add_all(_weekly_events(now))
    db.commit()
    return DemoSeedResult(created=True, logins=_logins())
