"""
Sample Data Generator Service

Generates sample data for new organizations to explore features:
- 5 sample events (various dates and times)
- 3 sample teams (Greeters, Worship, Tech)
- 10 sample volunteers (with availability)

All sample data is marked with "SAMPLE" prefix for easy identification
and can be cleaned up with one click.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session

from api.models import Organization, Person, Team, Event, Availability
from api.timeutils import utcnow
from api.security import hash_password
import random


def generate_sample_data(org_id: str, db: Session) -> Dict[str, List[str]]:
    """
    Generate sample data for an organization.

    Args:
        org_id: Organization ID to generate data for
        db: Database session

    Returns:
        Dictionary with IDs of created entities:
        {
            "events": [event_id1, event_id2, ...],
            "teams": [team_id1, team_id2, ...],
            "people": [person_id1, person_id2, ...]
        }
    """
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise ValueError(f"Organization {org_id} not found")

    created_ids = {
        "events": [],
        "teams": [],
        "people": []
    }

    # Generate sample teams
    teams_data = [
        {
            "name": "SAMPLE - Greeters Team",
            "role": "greeter",
            "description": "Welcome guests at the entrance"
        },
        {
            "name": "SAMPLE - Worship Team",
            "role": "worship",
            "description": "Lead music and worship"
        },
        {
            "name": "SAMPLE - Tech Team",
            "role": "tech",
            "description": "Audio, video, and lighting"
        }
    ]

    created_teams = []
    for team_data in teams_data:
        team = Team(
            org_id=org_id,
            name=team_data["name"],
            description=team_data.get("description"),
            is_sample=True,  # Mark as sample data
            extra_data={"role": team_data["role"]}  # Store role in extra_data
        )
        db.add(team)
        db.flush()  # Get team.id
        created_teams.append(team)
        created_ids["teams"].append(team.id)

    # Generate sample volunteers
    sample_names = [
        "John Doe", "Jane Smith", "Bob Johnson", "Alice Williams",
        "Charlie Brown", "Diana Martinez", "Eric Taylor", "Fiona Garcia",
        "George Anderson", "Hannah Lee"
    ]

    created_people = []
    for i, name in enumerate(sample_names):
        email = f"sample.volunteer{i+1}@example.com"
        person = Person(
            org_id=org_id,
            name=f"SAMPLE - {name}",
            email=email,
            password_hash=hash_password("SamplePassword123!"),  # All samples have same password
            roles=["volunteer"],
            language="en",
            is_sample=True  # Mark as sample data
        )
        db.add(person)
        db.flush()  # Get person.id
        created_people.append(person)
        created_ids["people"].append(person.id)

        # Assign to random teams (1-2 teams per person)
        num_teams = random.randint(1, 2)
        assigned_teams = random.sample(created_teams, num_teams)
        for team in assigned_teams:
            from api.models import TeamMember
            team_member = TeamMember(
                team_id=team.id,
                person_id=person.id
            )
            db.add(team_member)

        # Add some random availability (time off)
        if random.random() < 0.3:  # 30% of people have time off
            start_date = utcnow() + timedelta(days=random.randint(7, 30))
            end_date = start_date + timedelta(days=random.randint(1, 7))
            availability = Availability(
                person_id=person.id,
                start_date=start_date.date(),
                end_date=end_date.date(),
                reason="SAMPLE - Personal time off"
            )
            db.add(availability)

    # Generate sample events
    base_date = utcnow() + timedelta(days=7)  # Start 1 week from now
    events_data = [
        {
            "title": "SAMPLE - Sunday Service 10am",
            "days_offset": 0,
            "hour": 10,
            "duration": 90,
            "roles": {"greeter": 2, "worship": 3, "tech": 1}
        },
        {
            "title": "SAMPLE - Wednesday Prayer Meeting",
            "days_offset": 3,
            "hour": 19,
            "duration": 60,
            "roles": {"greeter": 1, "worship": 2}
        },
        {
            "title": "SAMPLE - Sunday Service 10am",
            "days_offset": 7,
            "hour": 10,
            "duration": 90,
            "roles": {"greeter": 2, "worship": 3, "tech": 1}
        },
        {
            "title": "SAMPLE - Youth Group Friday",
            "days_offset": 11,
            "hour": 18,
            "duration": 120,
            "roles": {"greeter": 1, "tech": 1}
        },
        {
            "title": "SAMPLE - Sunday Service 10am",
            "days_offset": 14,
            "hour": 10,
            "duration": 90,
            "roles": {"greeter": 2, "worship": 3, "tech": 1}
        }
    ]

    for event_data in events_data:
        start_datetime = base_date + timedelta(days=event_data["days_offset"], hours=event_data["hour"])
        end_datetime = start_datetime + timedelta(minutes=event_data["duration"])
        event = Event(
            org_id=org_id,
            type=event_data["title"],  # Use title as type
            start_time=start_datetime,
            end_time=end_datetime,
            is_sample=True,  # Mark as sample data
            extra_data={"role_requirements": event_data["roles"]}  # Store roles in extra_data
        )
        db.add(event)
        db.flush()  # Get event.id
        created_ids["events"].append(event.id)

    db.commit()

    return created_ids


def cleanup_sample_data(org_id: str, db: Session) -> Dict[str, int]:
    """
    Remove all sample data for an organization.

    Args:
        org_id: Organization ID to clean up
        db: Database session

    Returns:
        Dictionary with counts of deleted entities:
        {
            "events": 5,
            "teams": 3,
            "people": 10,
            "availability": 3
        }
    """
    deleted_counts = {
        "events": 0,
        "teams": 0,
        "people": 0,
        "availability": 0
    }

    # Delete sample events (using is_sample flag)
    events = db.query(Event).filter(
        Event.org_id == org_id,
        Event.is_sample == True
    ).all()
    deleted_counts["events"] = len(events)
    for event in events:
        db.delete(event)

    # Delete sample availability (for sample people)
    sample_people = db.query(Person).filter(
        Person.org_id == org_id,
        Person.is_sample == True
    ).all()

    for person in sample_people:
        availability_records = db.query(Availability).filter(
            Availability.person_id == person.id
        ).all()
        deleted_counts["availability"] += len(availability_records)
        for avail in availability_records:
            db.delete(avail)

    # Delete sample people (using is_sample flag)
    deleted_counts["people"] = len(sample_people)
    for person in sample_people:
        db.delete(person)

    # Delete sample teams (using is_sample flag)
    teams = db.query(Team).filter(
        Team.org_id == org_id,
        Team.is_sample == True
    ).all()
    deleted_counts["teams"] = len(teams)
    for team in teams:
        db.delete(team)

    db.commit()

    return deleted_counts


def has_sample_data(org_id: str, db: Session) -> bool:
    """
    Check if organization has any sample data.

    Args:
        org_id: Organization ID to check
        db: Database session

    Returns:
        True if any sample data exists, False otherwise
    """
    # Check for any sample entities (using is_sample flag)
    sample_events = db.query(Event).filter(
        Event.org_id == org_id,
        Event.is_sample == True
    ).count()

    sample_people = db.query(Person).filter(
        Person.org_id == org_id,
        Person.is_sample == True
    ).count()

    sample_teams = db.query(Team).filter(
        Team.org_id == org_id,
        Team.is_sample == True
    ).count()

    return (sample_events > 0 or sample_people > 0 or sample_teams > 0)


def get_sample_data_summary(org_id: str, db: Session) -> Dict[str, int]:
    """
    Get summary counts of sample data.

    Args:
        org_id: Organization ID to check
        db: Database session

    Returns:
        Dictionary with counts:
        {
            "events": 5,
            "teams": 3,
            "people": 10
        }
    """
    summary = {
        "events": db.query(Event).filter(
            Event.org_id == org_id,
            Event.is_sample == True
        ).count(),
        "teams": db.query(Team).filter(
            Team.org_id == org_id,
            Team.is_sample == True
        ).count(),
        "people": db.query(Person).filter(
            Person.org_id == org_id,
            Person.is_sample == True
        ).count()
    }

    return summary
