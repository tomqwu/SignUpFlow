"""
Seed system SMS message templates.

Creates default templates for Assignment Notification, 24-Hour Reminder,
and Event Cancellation messages in English and Spanish.
"""

from api.database import SessionLocal, engine
from api.models import SmsTemplate, Organization, Person
import sys


def seed_templates():
    """Create system SMS templates for all organizations."""
    db = SessionLocal()

    try:
        # Get all organizations
        organizations = db.query(Organization).all()

        if not organizations:
            print("❌ No organizations found. Please create at least one organization first.")
            return False

        for org in organizations:
            print(f"\n📋 Seeding templates for organization: {org.name} (ID: {org.id})")

            # Get first admin user for created_by field
            admin = db.query(Person).filter(
                Person.org_id == org.id,
                Person.roles.contains('"admin"')
            ).first()

            if not admin:
                print(f"⚠️  No admin found for {org.name}, skipping...")
                continue

            # Template 1: Assignment Notification
            assignment_template = SmsTemplate(
                organization_id=org.id,
                name="Assignment Notification",
                template_text=(
                    "{{volunteer_name}}, you're assigned to {{event_name}} "
                    "on {{date}} at {{time}}. Location: {{location}}. "
                    "Reply YES to confirm, NO to decline."
                ),
                message_type="assignment",
                character_count=160,  # Approximate, will be updated on first use
                translations={
                    "en": (
                        "{{volunteer_name}}, you're assigned to {{event_name}} "
                        "on {{date}} at {{time}}. Location: {{location}}. "
                        "Reply YES to confirm, NO to decline."
                    ),
                    "es": (
                        "{{volunteer_name}}, estás asignado a {{event_name}} "
                        "el {{date}} a las {{time}}. Ubicación: {{location}}. "
                        "Responde SÍ para confirmar, NO para rechazar."
                    )
                },
                is_system=True,
                usage_count=0,
                created_by=admin.id
            )

            # Template 2: 24-Hour Reminder
            reminder_template = SmsTemplate(
                organization_id=org.id,
                name="24-Hour Reminder",
                template_text=(
                    "Reminder: {{event_name}} tomorrow at {{time}}. "
                    "Location: {{location}}. See you there!"
                ),
                message_type="reminder",
                character_count=120,
                translations={
                    "en": (
                        "Reminder: {{event_name}} tomorrow at {{time}}. "
                        "Location: {{location}}. See you there!"
                    ),
                    "es": (
                        "Recordatorio: {{event_name}} mañana a las {{time}}. "
                        "Ubicación: {{location}}. ¡Nos vemos allí!"
                    )
                },
                is_system=True,
                usage_count=0,
                created_by=admin.id
            )

            # Template 3: Event Cancellation
            cancellation_template = SmsTemplate(
                organization_id=org.id,
                name="Event Cancellation",
                template_text=(
                    "CANCELLED: {{event_name}} on {{date}} has been cancelled. "
                    "Apologies for any inconvenience."
                ),
                message_type="cancellation",
                character_count=100,
                translations={
                    "en": (
                        "CANCELLED: {{event_name}} on {{date}} has been cancelled. "
                        "Apologies for any inconvenience."
                    ),
                    "es": (
                        "CANCELADO: {{event_name}} el {{date}} ha sido cancelado. "
                        "Disculpas por las molestias."
                    )
                },
                is_system=True,
                usage_count=0,
                created_by=admin.id
            )

            # Check if templates already exist
            existing = db.query(SmsTemplate).filter(
                SmsTemplate.organization_id == org.id,
                SmsTemplate.is_system == True
            ).count()

            if existing > 0:
                print(f"   ⏭️  System templates already exist ({existing} found), skipping...")
                continue

            # Add templates
            db.add(assignment_template)
            db.add(reminder_template)
            db.add(cancellation_template)
            db.commit()

            print(f"   ✅ Created 3 system templates:")
            print(f"      • Assignment Notification ({assignment_template.character_count} chars)")
            print(f"      • 24-Hour Reminder ({reminder_template.character_count} chars)")
            print(f"      • Event Cancellation ({cancellation_template.character_count} chars)")

        print(f"\n✅ Template seeding complete!")
        return True

    except Exception as e:
        print(f"\n❌ Error seeding templates: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding SMS Templates...")
    success = seed_templates()
    sys.exit(0 if success else 1)
