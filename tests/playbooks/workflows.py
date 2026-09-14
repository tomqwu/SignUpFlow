"""Reusable lifecycle assertions, independent of pytest fixtures and domain names."""

from collections import Counter
from datetime import datetime, timedelta

from tests.playbooks.runtime import Playbook


def run_six_week_roster(client, playbook_spec):
    p = Playbook(client, playbook_spec)
    for week in range(6):
        p.event(week)
        p.event(week, playbook_spec.secondary_event, hour=18, day_offset=3)

    # Week 1: complete baseline. Fairness is checked against actual assignments.
    baseline = p.solve()
    assert baseline["metrics"]["hard_violations"] == 0
    p.assert_complete(baseline["solution_id"])
    initial = p.assignments(baseline["solution_id"])[0]["assignees"][0]
    member = p.people[initial["person_id"]]
    login = p.request(
        "POST", "/auth/login", data={"email": member["email"], "password": p.password}
    )
    member_headers = {"Authorization": f"Bearer {login['token']}"}
    assert p.request("GET", "/assignments/me", headers=member_headers)["total"] == 0
    for action, body in [
        ("accept", None),
        ("decline", {"decline_reason": "Unavailable"}),
        ("swap-request", {}),
    ]:
        p.request(
            "POST",
            f"/assignments/{initial['assignment_id']}/{action}",
            404,
            body,
            headers=member_headers,
        )
    counts = Counter(
        a["person_id"] for e in p.assignments(baseline["solution_id"]) for a in e["assignees"]
    )
    for role in p.spec["roles"]:
        loads = [counts[pid] for pid, person in p.people.items() if role in person["roles"]]
        assert max(loads) - min(loads) <= 1
    p.request("POST", f"/solutions/{baseline['solution_id']}/publish")
    assert p.request("GET", "/assignments/me", headers=member_headers)["total"] > 0
    p.request("POST", f"/assignments/{initial['assignment_id']}/accept", headers=member_headers)

    # Week 2: an assigned member is absent; the qualified reserve must cover.
    critical = playbook_spec.critical_role
    absent = next(pid for pid, person in p.people.items() if critical in person["roles"])
    p.timeoff(absent, 1)
    # Week 3: simultaneous events require disjoint people, not double-booking.
    p.event(2, "second", hour=11)
    revised = p.solve()
    assert revised["metrics"]["hard_violations"] == 0
    p.assert_complete(revised["solution_id"])

    # Week 4: remove every qualified person for a critical role. Never publish this draft.
    for pid, person in list(p.people.items()):
        if critical in person["roles"]:
            p.timeoff(pid, 3)
    shortage = p.solve()
    assert shortage["metrics"]["hard_violations"] == 1
    assert all(v["constraint_key"] == "require_role_coverage" for v in shortage["violations"])
    assert p.request("GET", f"/solutions/{baseline['solution_id']}")["is_published"]
    assert not p.request("GET", f"/solutions/{shortage['solution_id']}")["is_published"]

    # Week 5: onboard a qualified replacement, repairing the week-4 shortage too.
    p.invite("Qualified replacement", [critical])
    # Week 6: move the game/service; solve from the changed source, not stale times.
    event_id = f"{p.org}-w6-main"
    event = p.events[event_id]
    start = datetime.fromisoformat(event["start_time"]) + timedelta(days=1)
    changes = {
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(hours=2)).isoformat(),
    }
    p.request("PUT", f"/events/{event_id}", data=changes)
    event.update(changes)
    repaired = p.solve()
    assert repaired["metrics"]["hard_violations"] == 0
    p.assert_complete(repaired["solution_id"])
    entry = next(e for e in p.assignments(repaired["solution_id"]) if e["event_id"] == event_id)
    assert datetime.fromisoformat(entry["event_start"]) == start
    p.request("POST", f"/solutions/{repaired['solution_id']}/publish")
    assert not p.request("GET", f"/solutions/{baseline['solution_id']}")["is_published"]
    assert p.request("GET", f"/solutions/{repaired['solution_id']}")["is_published"]
    p.request(
        "POST", f"/assignments/{initial['assignment_id']}/accept", 404, headers=member_headers
    )
    visible_ids = {
        a["id"] for a in p.request("GET", "/assignments/me", headers=member_headers)["items"]
    }
    assert initial["assignment_id"] not in visible_ids

    # Volunteers and another organization's admin cannot run/publish this roster.
    person = p.people[absent]
    auth = p.request("POST", "/auth/login", data={"email": person["email"], "password": p.password})
    volunteer = {"Authorization": f"Bearer {auth['token']}"}
    p.request("POST", f"/solutions/{repaired['solution_id']}/publish", 403, headers=volunteer)
    other = Playbook(client, playbook_spec)
    p.request("POST", f"/solutions/{repaired['solution_id']}/publish", 404, headers=other.headers)
    p.request("POST", f"/solutions/{repaired['solution_id']}/publish", 403, headers={})
