"""PDF export utility for schedules."""

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_schedule_pdf(org_name: str, events: list, people: dict, assignments: dict, events_db_map: dict = None, blocked_dates_map: dict = None) -> BytesIO:
    """
    Generate a formatted PDF schedule.

    Args:
        org_name: Organization name
        events: List of event dicts with id, type, start_time, end_time
        people: Dict mapping person_id to {'name': str, 'roles': list}
        assignments: Dict mapping event_id to list of person_ids
        events_db_map: Optional dict mapping event_id to event database object (for role requirements)
        blocked_dates_map: Optional dict mapping person_id to list of {'start': date, 'end': date}

    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Container for flowables
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    # Title
    elements.append(Paragraph(f"{org_name} - Schedule", title_style))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))

    # Sort events by date
    sorted_events = sorted(events, key=lambda e: e['start_time'])

    # Group events by date
    events_by_date = {}
    for event in sorted_events:
        date_str = event['start_time'].strftime('%A, %B %d, %Y')
        if date_str not in events_by_date:
            events_by_date[date_str] = []
        events_by_date[date_str].append(event)

    # Create tables for each date
    for date_str, date_events in events_by_date.items():
        # Date header
        date_style = ParagraphStyle(
            'DateHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=10,
            spaceBefore=20,
        )
        elements.append(Paragraph(date_str, date_style))
        elements.append(Spacer(1, 0.1*inch))

        # Create table data
        table_data = [['Time', 'Event', 'Assigned']]

        for event in date_events:
            start_time = event['start_time'].strftime('%I:%M %p')
            event_type = event['type']

            # Get assigned people grouped by role
            assignees_str = 'Not assigned'
            if event['id'] in assignments:
                assigned_ids = assignments[event['id']]

                # Get event role requirements if available
                role_counts = {}
                if events_db_map and event['id'] in events_db_map:
                    event_db = events_db_map[event['id']]
                    if hasattr(event_db, 'extra_data') and event_db.extra_data:
                        role_counts = event_db.extra_data.get('role_counts', {})

                # Group people by their roles that match event requirements
                if role_counts:
                    role_assignments = {role: [] for role in role_counts.keys()}
                    assigned_people = set()

                    # Helper function to check if person is blocked on event date
                    def is_person_blocked(person_id, event_date):
                        if not blocked_dates_map:
                            return False
                        blocked_periods = blocked_dates_map.get(person_id, [])
                        for period in blocked_periods:
                            if period['start'] <= event_date.date() <= period['end']:
                                return True
                        return False

                    # First pass: assign people who only have ONE matching role
                    for pid in assigned_ids:
                        person = people.get(pid)
                        if person and pid not in assigned_people:
                            person_roles = person.get('roles', [])
                            matching_roles = [r for r in role_counts.keys() if r in person_roles]
                            if len(matching_roles) == 1:
                                name = person['name']
                                if is_person_blocked(pid, event['start_time']):
                                    name += " [BLOCKED]"
                                role_assignments[matching_roles[0]].append(name)
                                assigned_people.add(pid)

                    # Second pass: assign people with multiple roles to roles that need filling
                    for pid in assigned_ids:
                        person = people.get(pid)
                        if person and pid not in assigned_people:
                            person_roles = person.get('roles', [])
                            matching_roles = [r for r in role_counts.keys() if r in person_roles]
                            # Assign to the role that needs the most people (by required count)
                            for role in sorted(matching_roles, key=lambda r: role_counts.get(r, 0) - len(role_assignments.get(r, [])), reverse=True):
                                if len(role_assignments[role]) < role_counts[role]:
                                    name = person['name']
                                    if is_person_blocked(pid, event['start_time']):
                                        name += " [BLOCKED]"
                                    role_assignments[role].append(name)
                                    assigned_people.add(pid)
                                    break

                    # Format as "Role: name1, name2"
                    role_lines = []
                    for role, names in role_assignments.items():
                        if names:
                            role_lines.append(f"{role.title()}: {', '.join(names)}")

                    assignees_str = '\n'.join(role_lines) if role_lines else 'Not assigned'
                else:
                    # No role requirements, just list names
                    def is_person_blocked(person_id, event_date):
                        if not blocked_dates_map:
                            return False
                        blocked_periods = blocked_dates_map.get(person_id, [])
                        for period in blocked_periods:
                            if period['start'] <= event_date.date() <= period['end']:
                                return True
                        return False

                    assigned_names = []
                    for pid in assigned_ids:
                        if people.get(pid):
                            name = people.get(pid, {}).get('name', pid)
                            if is_person_blocked(pid, event['start_time']):
                                name += " [BLOCKED]"
                            assigned_names.append(name)
                    assignees_str = ', '.join(assigned_names) if assigned_names else 'Not assigned'

            table_data.append([start_time, event_type, assignees_str])

        # Create table
        col_widths = [1.2*inch, 2.5*inch, 3.5*inch]
        table = Table(table_data, colWidths=col_widths)

        # Style the table
        table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Body style
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Time column centered
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),   # Other columns left
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
