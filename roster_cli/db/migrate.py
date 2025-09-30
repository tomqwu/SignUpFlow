"""Migrate YAML data to database."""

from pathlib import Path
from datetime import datetime
from roster_cli.db.models import (
    create_database,
    get_session,
    Organization,
    Person,
    Team,
    TeamMember,
    Resource,
    Event,
    EventTeam,
    Availability,
    VacationPeriod,
    AvailabilityException,
    Holiday,
    Constraint,
)
from roster_cli.core.loader import (
    load_org,
    load_people,
    load_teams,
    load_resources,
    load_events,
    load_holidays,
    load_constraint_files,
    load_yaml,
)
from roster_cli.core.models import Availability as AvailabilityModel


def migrate_workspace_to_db(workspace_path: Path, db_url: str = "sqlite:///roster.db"):
    """Migrate a workspace directory to database."""

    print(f"🔄 Migrating workspace: {workspace_path}")
    print(f"📁 Database: {db_url}\n")

    # Create database
    engine = create_database(db_url)
    session = get_session(engine)

    try:
        # Load YAML data
        print("📥 Loading YAML data...")
        org_file = load_org(workspace_path)
        people_file = load_people(workspace_path)
        teams_file = load_teams(workspace_path)
        resources_file = load_resources(workspace_path)
        events_file = load_events(workspace_path)
        holidays_file = load_holidays(workspace_path)
        constraints = load_constraint_files(workspace_path)

        # Load availability
        availability_list = []
        avail_file = workspace_path / "availability.yaml"
        if avail_file.exists():
            avail_data = load_yaml(avail_file)
            if "availability" in avail_data:
                availability_list = [AvailabilityModel(**a) for a in avail_data["availability"]]

        # Migrate Organization
        print(f"✓ Organization: {org_file.org_id}")
        org = Organization(
            id=org_file.org_id,
            name=org_file.org_id,
            region=org_file.region,
            config={
                "change_min_weight": org_file.defaults.change_min_weight if org_file.defaults else None,
                "fairness_weight": org_file.defaults.fairness_weight if org_file.defaults else None,
                "cooldown_days": org_file.defaults.cooldown_days if org_file.defaults else None,
            }
        )
        session.add(org)

        # Migrate People
        print(f"✓ People: {len(people_file.people)} persons")
        for person in people_file.people:
            p = Person(
                id=person.id,
                org_id=org_file.org_id,
                name=person.name,
                email=getattr(person, 'email', None),
                roles=person.roles if person.roles else [],
                extra_data={}
            )
            session.add(p)

        # Migrate Teams
        if teams_file:
            print(f"✓ Teams: {len(teams_file.teams)} teams")
            for team in teams_file.teams:
                t = Team(
                    id=team.id,
                    org_id=org_file.org_id,
                    name=team.name,
                    description=None,
                    extra_data={}
                )
                session.add(t)

                # Add team members
                for member_id in team.members:
                    tm = TeamMember(
                        team_id=team.id,
                        person_id=member_id
                    )
                    session.add(tm)

        # Migrate Resources
        if resources_file:
            print(f"✓ Resources: {len(resources_file.resources)} resources")
            for resource in resources_file.resources:
                r = Resource(
                    id=resource.id,
                    org_id=org_file.org_id,
                    type=resource.type,
                    location=resource.location,
                    capacity=resource.capacity,
                    extra_data={}
                )
                session.add(r)

        # Migrate Events
        print(f"✓ Events: {len(events_file.events)} events")
        for event in events_file.events:
            e = Event(
                id=event.id,
                org_id=org_file.org_id,
                type=event.type,
                start_time=event.start,
                end_time=event.end,
                resource_id=event.resource_id,
                extra_data={}
            )
            session.add(e)

            # Add event teams
            for team_id in event.team_ids:
                et = EventTeam(
                    event_id=event.id,
                    team_id=team_id
                )
                session.add(et)

        # Migrate Holidays
        if holidays_file:
            print(f"✓ Holidays: {len(holidays_file.days)} holidays")
            for holiday in holidays_file.days:
                h = Holiday(
                    org_id=org_file.org_id,
                    date=holiday.date,
                    label=holiday.label,
                    is_long_weekend=holiday.is_long_weekend
                )
                session.add(h)

        # Migrate Availability
        if availability_list:
            print(f"✓ Availability: {len(availability_list)} records")
            for avail in availability_list:
                a = Availability(
                    person_id=avail.person_id,
                    rrule=avail.rrule,
                    extra_data={}
                )
                session.add(a)
                session.flush()  # Get the ID

                # Add vacations
                for vacation in avail.vacations:
                    vp = VacationPeriod(
                        availability_id=a.id,
                        start_date=vacation.start,
                        end_date=vacation.end
                    )
                    session.add(vp)

                # Add exceptions
                for exception in avail.exceptions:
                    ae = AvailabilityException(
                        availability_id=a.id,
                        exception_date=exception
                    )
                    session.add(ae)

        # Migrate Constraints
        if constraints:
            print(f"✓ Constraints: {len(constraints)} constraints")
            for constraint in constraints:
                c = Constraint(
                    org_id=org_file.org_id,
                    key=constraint.key,
                    type=constraint.severity,
                    weight=constraint.weight if constraint.weight else None,
                    predicate=str(constraint.then),
                    params=constraint.params if constraint.params else {}
                )
                session.add(c)

        # Commit all changes
        session.commit()
        print("\n✅ Migration completed successfully!")

        # Print summary
        print("\n📊 Database Summary:")
        print(f"   • Organizations: {session.query(Organization).count()}")
        print(f"   • People: {session.query(Person).count()}")
        print(f"   • Teams: {session.query(Team).count()}")
        print(f"   • Resources: {session.query(Resource).count()}")
        print(f"   • Events: {session.query(Event).count()}")
        print(f"   • Holidays: {session.query(Holiday).count()}")
        print(f"   • Availability: {session.query(Availability).count()}")
        print(f"   • Constraints: {session.query(Constraint).count()}")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m roster_cli.db.migrate <workspace_path> [db_url]")
        print("Example: python -m roster_cli.db.migrate test_data/cricket_custom")
        sys.exit(1)

    workspace = Path(sys.argv[1])
    db_url = sys.argv[2] if len(sys.argv) > 2 else "sqlite:///roster.db"

    migrate_workspace_to_db(workspace, db_url)
