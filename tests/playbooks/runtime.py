"""Executable domain fixtures shared by API acceptance and real-browser tests."""

from datetime import UTC, date, datetime, time, timedelta
from uuid import uuid4

from tests.playbooks.registry import PlaybookSpec


class Playbook:
    """Use public API writes, real identities, and a fresh organization per run."""

    password = "PlaybookTest123!"

    def __init__(
        self,
        client,
        definition: PlaybookSpec,
        *,
        seed_people: bool = True,
        bootstrap_admin: bool = True,
        instance_id: str | None = None,
        start_date: date | None = None,
    ):
        self.client = client
        self.spec = definition.model_dump()
        self.org = instance_id or f"{definition.id}-{uuid4().hex[:10]}"
        self.people = {}
        self.events = {}
        self.blocked = set()
        today = date.today()
        self.start = start_date or today + timedelta(days=(6 - today.weekday()) % 7 + 14)
        self.email = f"admin@{self.org}.example"
        self.headers = {}
        if seed_people and not bootstrap_admin:
            raise ValueError("Cannot seed people before the playbook administrator exists")
        if bootstrap_admin:
            self.bootstrap_admin()
        if seed_people:
            for role, count in self.spec["roles"].items():
                for index in range(count * 2):
                    self.invite(f"{role} {index + 1}", [role])

    def bootstrap_admin(self):
        admin = self.request(
            "POST",
            "/auth/signup",
            201,
            {
                "org_id": self.org,
                "org_name": self.spec["name"],
                "region": "US",
                "name": "Scheduling administrator",
                "email": self.email,
                "password": self.password,
            },
        )
        self.headers = {"Authorization": f"Bearer {admin['token']}"}

    def authenticate_admin(self):
        auth = self.request(
            "POST",
            "/auth/login",
            data={"email": self.email, "password": self.password},
            headers={},
        )
        self.org = auth["org_id"]
        self.headers = {"Authorization": f"Bearer {auth['token']}"}

    def member_headers(self, person_id):
        person = self.people[person_id]
        auth = self.request(
            "POST",
            "/auth/login",
            data={"email": person["email"], "password": self.password},
            headers={},
        )
        return {"Authorization": f"Bearer {auth['token']}"}

    def request(self, method, path, status=200, data=None, headers=None):
        response = self.client.request(
            method,
            f"/api/v1{path}",
            json=data,
            headers=self.headers if headers is None else headers,
        )
        assert response.status_code == status, (path, response.status_code, response.text)
        return response.json() if response.content else None

    def invite(self, name, roles):
        email = f"person{len(self.people)}@{self.org}.example"
        invitation = self.request(
            "POST",
            f"/invitations?org_id={self.org}",
            201,
            {
                "name": name,
                "email": email,
                "roles": ["volunteer", *roles],
            },
        )
        person = self.request(
            "POST",
            f"/invitations/{invitation['token']}/accept",
            201,
            {
                "password": self.password,
                "timezone": "UTC",
            },
            headers={},
        )
        self.people[person["person_id"]] = {"name": name, "roles": roles, "email": email}
        return person["person_id"]

    def event(self, week, label="main", hour=10, roles=None, day_offset=0):
        start = datetime.combine(self.start + timedelta(weeks=week, days=day_offset), time(hour))
        event_id = f"{self.org}-w{week + 1}-{label}"
        data = {
            "id": event_id,
            "org_id": self.org,
            "type": f"{self.spec['event']} W{week + 1} {label}",
            "start_time": start.isoformat(),
            "end_time": (start + timedelta(hours=2)).isoformat(),
            "extra_data": {"role_counts": roles or self.spec["roles"]},
        }
        self.request("POST", "/events/", 201, data)
        self.events[event_id] = data
        return event_id

    def timeoff(self, person_id, week):
        day = (self.start + timedelta(weeks=week)).isoformat()
        self.request(
            "POST",
            f"/availability/{person_id}/timeoff",
            201,
            {
                "start_date": day,
                "end_date": day,
                "reason": "Playbook absence",
            },
        )
        self.blocked.add((person_id, day))

    def solve(self):
        return self.request(
            "POST",
            "/solver/solve",
            200,
            {
                "org_id": self.org,
                "from_date": self.start.isoformat(),
                "to_date": (self.start + timedelta(weeks=6)).isoformat(),
                "mode": "strict",
                "change_min": True,
            },
        )

    def assignments(self, solution_id):
        return self.request("GET", f"/solutions/{solution_id}/assignments")["events"]

    def assert_complete(self, solution_id, event_ids=None):
        """Independent oracle: exact slots, eligibility, absence and time conflicts."""
        from collections import Counter, defaultdict

        entries = self.assignments(solution_id)
        expected_event_ids = set(self.events) if event_ids is None else set(event_ids)
        assert {entry["event_id"] for entry in entries} == expected_event_ids
        calendars = defaultdict(list)
        for entry in entries:
            event = self.events[entry["event_id"]]
            assigned = entry["assignees"]
            expected = event["extra_data"]["role_counts"]
            assert Counter(a["role"] for a in assigned) == Counter(expected)
            assert len({a["person_id"] for a in assigned}) == sum(expected.values())
            start = datetime.fromisoformat(event["start_time"])
            end = datetime.fromisoformat(event["end_time"])
            # Fixtures use UTC; response serializers may add an explicit offset.
            start = start.replace(tzinfo=start.tzinfo or UTC)
            end = end.replace(tzinfo=end.tzinfo or UTC)
            for assignment in assigned:
                pid = assignment["person_id"]
                assert assignment["role"] in self.people[pid]["roles"]
                assert (pid, start.date().isoformat()) not in self.blocked
                assert all(end <= a or start >= b for a, b in calendars[pid])
                calendars[pid].append((start, end))
