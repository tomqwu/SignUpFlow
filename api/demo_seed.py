"""Demo organization loaded by ``make setup``, built the way a real church uses it.

The demo is the README's Church playbook (``docs/playbooks/church.json``) run
for real: an administrator signs up, invites the band, the production crew,
the welcome team and the children's leaders, sets up teams and scheduling
rules, books Sunday services and band rehearsals, records who is away, runs
the solver and publishes the result. Volunteers then accept their shifts, one
declines, and one asks for a swap. There are two weeks of history and six
weeks ahead, so every screen has something on it.

Everything goes through the public API, in process, so the data obeys the same
rules as data a person creates: tenancy, qualifications, publication checks and
notifications. Nothing is inserted behind the application's back.

Every account shares one password that is printed by setup and published in
the README. That is only acceptable because this is local demo data: the seed
refuses a production environment, and every address is on ``example.com``,
which is reserved and can never receive mail.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Any

DEMO_ORG_ID = "grace-community-church-demo"
DEMO_ORG_NAME = "Grace Community Church (demo)"
DEMO_PASSWORD = "DemoPass123!"
DEMO_ADMIN_EMAIL = "admin@example.com"
DEMO_ADMIN_NAME = "Dana Whitfield"

#: One Sunday service needs the whole team; rehearsal needs only the band.
SERVICE_ROLES = {
    "worship_leader": 1,
    "musician": 2,
    "sound": 1,
    "usher": 2,
    "children_leader": 1,
}
REHEARSAL_ROLES = {"worship_leader": 1, "musician": 2, "sound": 1}

#: Two qualified people for every slot, as in the Church playbook, so the
#: solver has a choice and one absence never leaves a service uncovered.
VOLUNTEERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Grace Park", ("worship_leader",)),
    ("Daniel Okafor", ("worship_leader", "musician")),
    ("Mia Chen", ("musician",)),
    ("Luis Romero", ("musician",)),
    ("Hannah Lee", ("musician",)),
    ("Samuel Adeyemi", ("musician",)),
    ("Ethan Brooks", ("sound",)),
    ("Priya Nair", ("sound",)),
    ("Olivia Martin", ("usher",)),
    ("James Walker", ("usher",)),
    ("Sofia Rossi", ("usher",)),
    ("Noah Kim", ("usher",)),
    ("Emma Johansson", ("children_leader",)),
    ("Caleb Wright", ("children_leader",)),
)

#: Invited but not yet joined, so the people page shows a pending invitation.
PENDING_INVITE = ("Ava Thompson", ("usher",))

TEAMS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    (
        "demo-worship-team",
        "Worship team",
        "Leads and plays Sunday worship.",
        ("worship_leader", "musician"),
    ),
    ("demo-production", "Production", "Sound desk and livestream.", ("sound",)),
    ("demo-welcome-team", "Welcome team", "Greets and seats the congregation.", ("usher",)),
    (
        "demo-kids-ministry",
        "Kids ministry",
        "Runs Sunday school during the service.",
        ("children_leader",),
    ),
)

HISTORY_WEEKS = 2
UPCOMING_WEEKS = 6


class DemoSeedRefusedError(RuntimeError):
    """Raised instead of publishing a known password into a real deployment."""


class DemoSeedConflictError(RuntimeError):
    """The demo login exists but cannot be used, so the demo cannot be managed."""


@dataclass(frozen=True)
class DemoLogin:
    label: str
    email: str


@dataclass(frozen=True)
class DemoSeedResult:
    created: bool
    logins: tuple[DemoLogin, ...]
    password: str = DEMO_PASSWORD
    summary: dict[str, int] = field(default_factory=dict)


def email_for(name: str) -> str:
    return f"{name.lower().replace(' ', '.')}@example.com"


def _logins() -> tuple[DemoLogin, ...]:
    return (
        DemoLogin("Admin", DEMO_ADMIN_EMAIL),
        DemoLogin("Volunteer, musician (has time off)", email_for("Mia Chen")),
        DemoLogin("Volunteer, worship leader", email_for("Grace Park")),
        DemoLogin("Volunteer, sound (asked for a swap)", email_for("Priya Nair")),
    )


def _sundays(today: date) -> list[date]:
    """Sundays from HISTORY_WEEKS back to UPCOMING_WEEKS ahead of ``today``."""
    next_sunday = today + timedelta(days=(6 - today.weekday()) % 7 or 7)
    return [next_sunday + timedelta(weeks=week) for week in range(-HISTORY_WEEKS, UPCOMING_WEEKS)]


class _Api:
    """Thin wrapper that fails loudly with the response when a call is refused."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def call(
        self,
        method: str,
        path: str,
        token: str | None = None,
        expect: tuple[int, ...] = (200, 201, 204),
        **kwargs: Any,
    ) -> Any:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = self.client.request(method, f"/api/v1{path}", headers=headers, **kwargs)
        if response.status_code not in expect:
            raise RuntimeError(
                f"Demo seed step {method} {path} failed with {response.status_code}: "
                f"{response.text[:500]}"
            )
        return response.json() if response.content else None


def _existing_admin_token(api: _Api) -> str | None:
    response = api.client.post(
        "/api/v1/auth/login", json={"email": DEMO_ADMIN_EMAIL, "password": DEMO_PASSWORD}
    )
    if response.status_code == 200:
        if response.json().get("org_id") != DEMO_ORG_ID:
            raise DemoSeedConflictError(
                f"{DEMO_ADMIN_EMAIL} belongs to another organization, so the demo "
                "cannot be loaded here."
            )
        return str(response.json()["token"])
    return None


def seed_demo(client: Any, *, reset: bool = False, today: date | None = None) -> DemoSeedResult:
    """Load the demo once through the API. Later calls change nothing unless ``reset``."""
    if os.getenv("ENVIRONMENT", "").strip().lower() == "production":
        raise DemoSeedRefusedError(
            "Refusing to load demo accounts with a published password into a "
            "production environment."
        )

    api = _Api(client)
    existing = _existing_admin_token(api)
    if existing and not reset:
        return DemoSeedResult(created=False, logins=_logins())
    if existing:
        # The application's own hard delete, so nothing is left half-removed.
        api.call("DELETE", f"/organizations/{DEMO_ORG_ID}", existing)

    today = today or date.today()
    return DemoSeedResult(created=True, logins=_logins(), summary=_build(api, today))


def _build(api: _Api, today: date) -> dict[str, int]:
    signup = api.call(
        "POST",
        "/auth/signup",
        json={
            "org_id": DEMO_ORG_ID,
            "org_name": DEMO_ORG_NAME,
            "region": "CA-ON",
            "name": DEMO_ADMIN_NAME,
            "email": DEMO_ADMIN_EMAIL,
            "password": DEMO_PASSWORD,
        },
        expect=(201, 409),
    )
    if "token" not in signup:
        raise DemoSeedConflictError(
            f"{DEMO_ADMIN_EMAIL} is already registered with a different password, so "
            "the demo cannot be managed. Delete that account or its organization first."
        )
    admin = str(signup["token"])

    # People: every volunteer accepts an invitation and sets the demo password.
    tokens: dict[str, str] = {}
    ids: dict[str, str] = {}
    for name, qualifications in VOLUNTEERS:
        invitation = api.call(
            "POST",
            f"/invitations?org_id={DEMO_ORG_ID}",
            admin,
            json={"name": name, "email": email_for(name), "roles": ["volunteer", *qualifications]},
        )
        joined = api.call(
            "POST",
            f"/invitations/{invitation['token']}/accept",
            json={"password": DEMO_PASSWORD, "timezone": "America/Toronto"},
        )
        tokens[name] = str(joined["token"])
        ids[name] = str(joined["person_id"])
    pending_name, pending_roles = PENDING_INVITE
    api.call(
        "POST",
        f"/invitations?org_id={DEMO_ORG_ID}",
        admin,
        json={
            "name": pending_name,
            "email": email_for(pending_name),
            "roles": ["volunteer", *pending_roles],
        },
    )

    for team_id, team_name, description, qualifications in TEAMS:
        members = [ids[name] for name, quals in VOLUNTEERS if set(quals) & set(qualifications)]
        api.call(
            "POST",
            "/teams/",
            admin,
            json={
                "id": team_id,
                "org_id": DEMO_ORG_ID,
                "name": team_name,
                "description": description,
                "member_ids": members,
            },
        )

    # Rules a real coordinator sets: nobody serves more than twice a week, and
    # the solver prefers to rest people between Sunday services.
    api.call(
        "POST",
        "/constraints/",
        admin,
        json={
            "org_id": DEMO_ORG_ID,
            "key": "two-services-per-week",
            "type": "hard",
            "predicate": "max_assignments",
            "params": {"period": "P7D", "max_count": 2},
        },
    )
    api.call(
        "POST",
        "/constraints/",
        admin,
        json={
            "org_id": DEMO_ORG_ID,
            "key": "rest-between-sundays",
            "type": "soft",
            "weight": 20,
            "predicate": "cooldown",
            "params": {"cooldown_days": 6, "applies_to": ["Sunday worship"]},
        },
    )

    sundays = _sundays(today)
    for sunday in sundays:
        rehearsal = sunday - timedelta(days=3)
        for event_id, event_type, day, start, hours, roles, location in (
            (
                f"band-rehearsal-{rehearsal.isoformat()}",
                "Band rehearsal",
                rehearsal,
                time(19),
                2,
                REHEARSAL_ROLES,
                "Music room",
            ),
            (
                f"sunday-worship-{sunday.isoformat()}",
                "Sunday worship",
                sunday,
                time(10),
                2,
                SERVICE_ROLES,
                "Main sanctuary",
            ),
        ):
            begins = datetime.combine(day, start)
            api.call(
                "POST",
                "/events/",
                admin,
                json={
                    "id": event_id,
                    "org_id": DEMO_ORG_ID,
                    "type": event_type,
                    "start_time": begins.isoformat(),
                    "end_time": (begins + timedelta(hours=hours)).isoformat(),
                    "extra_data": {"role_counts": roles, "location": location},
                },
            )

    # Time away, booked before the schedule is made so the solver respects it.
    first_upcoming = sundays[HISTORY_WEEKS]
    away = [
        (
            "Mia Chen",
            first_upcoming + timedelta(weeks=1),
            first_upcoming + timedelta(weeks=2),
            "Family visit",
        ),
        ("Noah Kim", first_upcoming, first_upcoming, "Out of town"),
    ]
    for name, start_day, end_day, reason in away:
        api.call(
            "POST",
            f"/availability/{ids[name]}/timeoff",
            tokens[name],
            json={
                "start_date": (start_day - timedelta(days=3)).isoformat(),
                "end_date": end_day.isoformat(),
                "reason": reason,
            },
        )

    solution = api.call(
        "POST",
        "/solver/solve",
        admin,
        json={
            "org_id": DEMO_ORG_ID,
            "from_date": (sundays[0] - timedelta(days=7)).isoformat(),
            "to_date": sundays[-1].isoformat(),
            "mode": "strict",
        },
    )
    if solution["metrics"]["hard_violations"]:
        raise RuntimeError(f"Demo schedule has hard violations: {solution['violations']}")
    api.call("POST", f"/solutions/{solution['solution_id']}/publish", admin)

    entries = api.call("GET", f"/solutions/{solution['solution_id']}/assignments", admin)["events"]
    by_person = {person_id: name for name, person_id in ids.items()}
    now = datetime.combine(today, time(0))

    # Luis declines a shift Mia can pick up, so the sample musician login has
    # an open shift: one she is not already on, on a day she is not away.
    def mia_is_free(entry: dict[str, Any]) -> bool:
        day = datetime.fromisoformat(entry["event_start"]).date()
        on_it = any(by_person[a["person_id"]] == "Mia Chen" for a in entry["assignees"])
        away_from, away_to = away[0][1] - timedelta(days=3), away[0][2]
        return not on_it and not away_from <= day <= away_to

    declined = swapped = accepted = 0
    for entry in sorted(entries, key=lambda e: e["event_start"]):
        starts = datetime.fromisoformat(entry["event_start"]).replace(tzinfo=None)
        weeks_out = (starts - now).days // 7
        for assignee in entry["assignees"]:
            name = by_person[assignee["person_id"]]
            path = f"/assignments/{assignee['assignment_id']}"
            # A few real-life responses, on upcoming shifts so they are actionable.
            if name == "Priya Nair" and weeks_out >= 0 and not swapped:
                api.call("POST", f"{path}/accept", tokens[name])
                api.call(
                    "POST",
                    f"{path}/swap-request",
                    tokens[name],
                    json={"note": "My daughter's recital moved to that morning. Can anyone cover?"},
                )
                swapped += 1
            elif name == "Luis Romero" and weeks_out >= 1 and not declined and mia_is_free(entry):
                api.call(
                    "POST",
                    f"{path}/decline",
                    tokens[name],
                    json={"decline_reason": "Travelling for work that weekend"},
                )
                declined += 1
            elif weeks_out < 2:
                # History and the next fortnight are confirmed; later weeks are
                # still awaiting replies, as they would be in practice.
                api.call("POST", f"{path}/accept", tokens[name])
                accepted += 1

    return {
        "volunteers": len(VOLUNTEERS),
        "events": len(sundays) * 2,
        "assignments": sum(len(e["assignees"]) for e in entries),
        "accepted": accepted,
        "declined": declined,
        "swap_requests": swapped,
    }


def run_seed_demo(*, reset: bool = False) -> DemoSeedResult:
    """Seed the configured database through an in-process API client.

    Email and SMS are forced off first: the demo addresses cannot receive mail,
    and seeding should never try to reach a provider.
    """
    os.environ["EMAIL_ENABLED"] = "false"
    os.environ["SMS_ENABLED"] = "false"
    os.environ.setdefault("DISABLE_RATE_LIMITS", "true")

    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        return seed_demo(client, reset=reset)
