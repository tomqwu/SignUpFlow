# API Contract: SMS Templates Endpoints

**Feature**: SMS Notification System | **Branch**: `009-sms-notifications` | **Date**: 2025-10-23

Message template management endpoints for creating, editing, and using reusable SMS templates with variable substitution.

---

## Overview

SMS templates provide:
1. **Reusability**: Define message patterns once, reuse for multiple events
2. **Consistency**: Standardized messaging across organization
3. **Localization**: Translations for English/Spanish messaging
4. **Variable Substitution**: Dynamic placeholders ({{event_name}}, {{date}}, {{time}})
5. **Character Count Tracking**: Ensure messages fit within SMS segment limits

---

## Endpoints

### 1. List SMS Templates

**Endpoint**: `GET /api/sms/templates`

**Purpose**: Retrieve all SMS templates for organization (system + custom templates)

**Authentication**: Required (JWT Bearer token)

**Authorization**:
- Admins: Can view all organization templates + system templates
- Volunteers: Can view system templates only (readonly)

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID
- `message_type` (optional, string): Filter by type (`assignment`, `reminder`, `cancellation`, `broadcast`)
- `include_system` (optional, boolean, default: true): Include system templates in results

**Response**:

**Success (200 OK)**:
```json
{
  "templates": [
    {
      "id": 1,
      "organization_id": null,
      "name": "Assignment Notification",
      "template_text": "{{event_name}} - {{date}} at {{time}} - Role: {{role}}. Reply YES to confirm, NO to decline",
      "message_type": "assignment",
      "character_count": 85,
      "is_system": true,
      "translations": {
        "en": "{{event_name}} - {{date}} at {{time}} - Role: {{role}}. Reply YES to confirm, NO to decline",
        "es": "{{event_name}} - {{date}} a las {{time}} - Rol: {{role}}. Responde SÍ para confirmar, NO para declinar"
      },
      "usage_count": 1247,
      "created_by": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 15,
      "organization_id": 123,
      "name": "Church Service Reminder",
      "template_text": "Reminder: {{event_name}} tomorrow at {{time}}. Role: {{role}}. See you there!",
      "message_type": "reminder",
      "character_count": 72,
      "is_system": false,
      "translations": {
        "en": "Reminder: {{event_name}} tomorrow at {{time}}. Role: {{role}}. See you there!"
      },
      "usage_count": 43,
      "created_by": 456,
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T10:00:00Z"
    }
  ],
  "pagination": {
    "total_count": 12,
    "system_count": 5,
    "custom_count": 7
  }
}
```

**Field Descriptions**:
- `is_system`: True for SignUpFlow-provided templates (readonly, cannot be edited/deleted)
- `organization_id`: Null for system templates, set for custom organization templates
- `character_count`: Length of template_text (helps ensure <160 chars for single SMS segment)
- `usage_count`: Number of times template has been used (analytics)
- `translations`: Multilingual versions of template (keyed by language code)

**Error Responses**:

**403 Forbidden**:
```json
{
  "detail": "Access denied: wrong organization"
}
```

---

### 2. Get Template by ID

**Endpoint**: `GET /api/sms/templates/{template_id}`

**Purpose**: Retrieve single template details (for editing or previewing)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Same as list (admins see all, volunteers see system only)

**Request Parameters**:

**Path Parameters**:
- `template_id` (required, integer): Template ID

**Query Parameters**:
- `org_id` (required, string): Organization ID

**Response**:

**Success (200 OK)**:
```json
{
  "id": 15,
  "organization_id": 123,
  "name": "Church Service Reminder",
  "template_text": "Reminder: {{event_name}} tomorrow at {{time}}. Role: {{role}}. See you there!",
  "message_type": "reminder",
  "character_count": 72,
  "is_system": false,
  "translations": {
    "en": "Reminder: {{event_name}} tomorrow at {{time}}. Role: {{role}}. See you there!",
    "es": "Recordatorio: {{event_name}} mañana a las {{time}}. Rol: {{role}}. ¡Nos vemos!"
  },
  "usage_count": 43,
  "created_by": 456,
  "created_by_name": "Pastor John",
  "created_at": "2024-12-01T10:00:00Z",
  "updated_at": "2024-12-01T10:00:00Z",
  "variables": [
    "event_name",
    "time",
    "role"
  ],
  "preview": "Reminder: Sunday Service tomorrow at 10:00AM. Role: Usher. See you there!"
}
```

**Additional Fields** (vs list endpoint):
- `created_by_name`: Creator's name (for audit trail)
- `variables`: Extracted variable names from template (for UI guidance)
- `preview`: Example rendered template (using sample data)

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Template not found"
}
```

---

### 3. Create Template

**Endpoint**: `POST /api/sms/templates`

**Purpose**: Create new custom SMS template for organization

**Authentication**: Required (JWT Bearer token)

**Authorization**: Admin only

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID

**Request Body**:
```json
{
  "name": "Cancellation Notice",
  "template_text": "CANCELLED: {{event_name}} on {{date}} has been cancelled due to weather. Stay safe!",
  "message_type": "cancellation",
  "translations": {
    "es": "CANCELADO: {{event_name}} del {{date}} ha sido cancelado por el clima. ¡Mantente seguro!"
  }
}
```

**Field Specifications**:
- `name` (required, string, 1-100 chars): Template name (must be unique within organization)
- `template_text` (required, string, 1-1600 chars): Template content with {{variable}} placeholders
- `message_type` (required, string): Template category (`assignment`, `reminder`, `cancellation`, `broadcast`)
- `translations` (optional, object): Language-specific versions (keyed by language code: `es`, `pt`)

**Validation Rules**:
1. Name must be unique within organization (case-insensitive)
2. Template text must contain at least one variable (e.g., {{event_name}})
3. Template text recommended <160 chars for single SMS segment (warning if >160)
4. Variables must use {{variable_name}} format (double curly braces)
5. Supported variables:
   - `{{event_name}}` - Event title
   - `{{date}}` - Event date (formatted, e.g., "Jan 1")
   - `{{time}}` - Event time (formatted, e.g., "10:00AM")
   - `{{volunteer_name}}` - Recipient name
   - `{{role}}` - Assignment role
   - `{{location}}` - Event location
6. Translations must use same variables as template_text

**Response**:

**Success (201 Created)**:
```json
{
  "id": 20,
  "organization_id": 123,
  "name": "Cancellation Notice",
  "template_text": "CANCELLED: {{event_name}} on {{date}} has been cancelled due to weather. Stay safe!",
  "message_type": "cancellation",
  "character_count": 87,
  "is_system": false,
  "translations": {
    "en": "CANCELLED: {{event_name}} on {{date}} has been cancelled due to weather. Stay safe!",
    "es": "CANCELADO: {{event_name}} del {{date}} ha sido cancelado por el clima. ¡Mantente seguro!"
  },
  "usage_count": 0,
  "created_by": 456,
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

**Error Responses**:

**400 Bad Request** - Validation failure:
```json
{
  "detail": "Template text must contain at least one variable (e.g., {{event_name}})"
}
```

**409 Conflict** - Duplicate name:
```json
{
  "detail": "Template with name 'Cancellation Notice' already exists for this organization"
}
```

**422 Unprocessable Entity** - Invalid variable:
```json
{
  "detail": "Invalid variable '{{custom_field}}'. Supported: event_name, date, time, volunteer_name, role, location"
}
```

---

### 4. Update Template

**Endpoint**: `PUT /api/sms/templates/{template_id}`

**Purpose**: Update existing custom template (system templates cannot be edited)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Admin only

**Request Parameters**:

**Path Parameters**:
- `template_id` (required, integer): Template ID to update

**Query Parameters**:
- `org_id` (required, string): Organization ID

**Request Body**:
```json
{
  "name": "Cancellation Notice - Updated",
  "template_text": "URGENT: {{event_name}} on {{date}} at {{time}} has been cancelled. Stay safe!",
  "translations": {
    "es": "URGENTE: {{event_name}} del {{date}} a las {{time}} ha sido cancelado. ¡Mantente seguro!"
  }
}
```

**Field Specifications**: Same as Create endpoint (all fields optional for partial update)

**Validation Rules**:
1. Cannot update system templates (is_system = true)
2. Cannot change message_type (recreate template if type changes)
3. Same validation as Create endpoint for provided fields

**Response**:

**Success (200 OK)**:
```json
{
  "id": 20,
  "organization_id": 123,
  "name": "Cancellation Notice - Updated",
  "template_text": "URGENT: {{event_name}} on {{date}} at {{time}} has been cancelled. Stay safe!",
  "message_type": "cancellation",
  "character_count": 93,
  "is_system": false,
  "translations": {
    "en": "URGENT: {{event_name}} on {{date}} at {{time}} has been cancelled. Stay safe!",
    "es": "URGENTE: {{event_name}} del {{date}} a las {{time}} ha sido cancelado. ¡Mantente seguro!"
  },
  "usage_count": 5,
  "created_by": 456,
  "created_at": "2024-12-01T10:00:00Z",
  "updated_at": "2025-01-01T10:15:00Z"
}
```

**Error Responses**:

**403 Forbidden** - Attempting to edit system template:
```json
{
  "detail": "Cannot edit system templates. Create a custom template instead."
}
```

**404 Not Found**:
```json
{
  "detail": "Template not found"
}
```

---

### 5. Delete Template

**Endpoint**: `DELETE /api/sms/templates/{template_id}`

**Purpose**: Delete custom template (system templates cannot be deleted)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Admin only

**Request Parameters**:

**Path Parameters**:
- `template_id` (required, integer): Template ID to delete

**Query Parameters**:
- `org_id` (required, string): Organization ID

**Response**:

**Success (200 OK)**:
```json
{
  "message": "Template deleted successfully",
  "template_id": 20,
  "template_name": "Cancellation Notice"
}
```

**Error Responses**:

**403 Forbidden** - Attempting to delete system template:
```json
{
  "detail": "Cannot delete system templates"
}
```

**404 Not Found**:
```json
{
  "detail": "Template not found"
}
```

---

### 6. Preview Template

**Endpoint**: `POST /api/sms/templates/{template_id}/preview`

**Purpose**: Render template with sample or real data (test before sending)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Admin only

**Request Parameters**:

**Path Parameters**:
- `template_id` (required, integer): Template ID to preview

**Query Parameters**:
- `org_id` (required, string): Organization ID

**Request Body**:
```json
{
  "event_id": 456,
  "volunteer_id": 123,
  "language": "es"
}
```

**Field Specifications**:
- `event_id` (optional, integer): Use real event data for preview
- `volunteer_id` (optional, integer): Use real volunteer data for preview
- `language` (optional, string, default: "en"): Language for preview

**If event_id/volunteer_id not provided, uses sample data.**

**Response**:

**Success (200 OK)** - With real data:
```json
{
  "template_id": 1,
  "template_name": "Assignment Notification",
  "language": "es",
  "rendered_message": "Servicio Dominical - 1 de enero a las 10:00AM - Rol: Ujier. Responde SÍ para confirmar, NO para declinar",
  "character_count": 115,
  "sms_segment_count": 1,
  "estimated_cost_cents": 79,
  "variables_used": {
    "event_name": "Servicio Dominical",
    "date": "1 de enero",
    "time": "10:00AM",
    "role": "Ujier"
  }
}
```

**Success (200 OK)** - With sample data:
```json
{
  "template_id": 1,
  "template_name": "Assignment Notification",
  "language": "en",
  "rendered_message": "Sunday Service - Jan 1 at 10:00AM - Role: Usher. Reply YES to confirm, NO to decline",
  "character_count": 85,
  "sms_segment_count": 1,
  "estimated_cost_cents": 79,
  "variables_used": {
    "event_name": "Sunday Service",
    "date": "Jan 1",
    "time": "10:00AM",
    "role": "Usher"
  },
  "note": "Preview uses sample data. Provide event_id and volunteer_id for real data."
}
```

**Field Descriptions**:
- `sms_segment_count`: Number of SMS segments (1 segment = 160 chars, 2 segments = 306 chars, etc.)
- `estimated_cost_cents`: Cost estimate ($0.0079 per segment for US)
- `variables_used`: Actual values substituted into template

**Error Responses**:

**400 Bad Request** - Missing required variable data:
```json
{
  "detail": "Event 456 does not have a location, but template requires {{location}} variable"
}
```

---

## Template Variables

### Supported Variables

| Variable | Description | Example Value | Required Data |
|----------|-------------|---------------|---------------|
| `{{event_name}}` | Event title | "Sunday Service" | Event.title |
| `{{date}}` | Event date (formatted) | "Jan 1" | Event.datetime |
| `{{time}}` | Event time (formatted) | "10:00AM" | Event.datetime |
| `{{volunteer_name}}` | Recipient's name | "John Smith" | Person.name |
| `{{role}}` | Assignment role | "Usher" | Event.role or EventAssignment.role |
| `{{location}}` | Event location | "Main Sanctuary" | Event.location |

### Variable Formatting

**Date Formatting**:
- Short format: "Jan 1" (month abbrev + day)
- Medium format: "January 1" (full month + day)
- Long format: "January 1, 2025" (full month + day + year)

**Time Formatting**:
- 12-hour format: "10:00AM", "3:30PM"
- 24-hour format: "10:00", "15:30" (optional, for international)

**Language-Specific Formatting**:
```json
{
  "en": {
    "date_format": "%b %d",
    "time_format": "%I:%M%p",
    "example": "Jan 1 at 10:00AM"
  },
  "es": {
    "date_format": "%d de %B",
    "time_format": "%H:%M",
    "example": "1 de enero a las 10:00"
  }
}
```

---

## System Templates

### Pre-Defined Templates

SignUpFlow provides 5 system templates (is_system = true, organization_id = null):

#### 1. Assignment Notification
```
{{event_name}} - {{date}} at {{time}} - Role: {{role}}. Reply YES to confirm, NO to decline
```
- **Type**: `assignment`
- **Variables**: event_name, date, time, role
- **Character Count**: 85
- **Translations**: en, es

#### 2. 24-Hour Reminder
```
Reminder: {{event_name}} tomorrow at {{time}}. Role: {{role}}. See you there!
```
- **Type**: `reminder`
- **Variables**: event_name, time, role
- **Character Count**: 72
- **Translations**: en, es

#### 3. Event Cancellation
```
CANCELLED: {{event_name}} on {{date}} has been cancelled. We'll reschedule soon.
```
- **Type**: `cancellation`
- **Variables**: event_name, date
- **Character Count**: 78
- **Translations**: en, es

#### 4. Schedule Change
```
CHANGE: {{event_name}} moved from {{old_time}} to {{time}} on {{date}}. Role: {{role}}
```
- **Type**: `broadcast`
- **Variables**: event_name, old_time, time, date, role
- **Character Count**: 82
- **Translations**: en, es

#### 5. Welcome Message
```
Welcome to {{org_name}} volunteer notifications! Reply STOP to unsubscribe. Questions? Contact {{org_email}}
```
- **Type**: `system`
- **Variables**: org_name, org_email
- **Character Count**: 98
- **Translations**: en, es

**System templates cannot be edited or deleted** (read-only for all users).

---

## Template Rendering

### Jinja2 Template Engine

**Implementation**:
```python
# api/services/sms_service.py
from jinja2 import Template, TemplateSyntaxError

class SMSService:
    def render_template(
        self,
        template_text: str,
        context: dict,
        max_length: int = 1600
    ) -> str:
        """Render Jinja2 template with context variables."""
        try:
            template = Template(template_text)
            rendered = template.render(context)

            # Truncate if exceeds max length (with ellipsis)
            if len(rendered) > max_length:
                rendered = rendered[:max_length - 3] + "..."

            return rendered
        except TemplateSyntaxError as e:
            raise ValueError(f"Invalid template syntax: {e}")

    def prepare_context(
        self,
        event: Event,
        volunteer: Person,
        language: str = "en"
    ) -> dict:
        """Prepare template rendering context."""
        return {
            "event_name": event.title,
            "date": format_date(event.datetime, language),
            "time": format_time(event.datetime, language),
            "volunteer_name": volunteer.name,
            "role": event.role or "Volunteer",
            "location": event.location or ""
        }

def format_date(dt: datetime, language: str) -> str:
    """Format date for template (language-specific)."""
    if language == "es":
        return dt.strftime("%d de %B")  # "1 de enero"
    else:
        return dt.strftime("%b %d")  # "Jan 1"

def format_time(dt: datetime, language: str) -> str:
    """Format time for template (language-specific)."""
    if language == "es":
        return dt.strftime("%H:%M")  # "10:00" (24-hour)
    else:
        return dt.strftime("%I:%M%p")  # "10:00AM" (12-hour)
```

---

## Character Count & SMS Segments

### SMS Segment Limits

| Segment | Characters | Cost (US) | Notes |
|---------|-----------|-----------|-------|
| 1 segment | 1-160 | $0.0079 | Single message |
| 2 segments | 161-306 | $0.0158 | Split message (header overhead: 7 chars) |
| 3 segments | 307-459 | $0.0237 | Split message |
| 4 segments | 460-612 | $0.0316 | Split message |
| Max | 1600 | $0.0790+ | 10 segments (Twilio limit) |

**Recommendation**: Keep templates <160 chars to minimize cost and ensure single SMS delivery.

**UI Warning**: Display warning in template editor if character_count > 160:
```
⚠️ This template is 215 characters and will cost 2 SMS segments ($0.0158 per send).
Consider shortening to <160 characters for single SMS segment.
```

---

## Frontend Integration

### Template Management UI

```javascript
// frontend/js/sms-templates.js

async function loadTemplates() {
    const response = await authFetch(
        `${API_BASE_URL}/sms/templates?org_id=${currentUser.org_id}`
    );
    const data = await response.json();

    renderTemplateList(data.templates);
}

async function createTemplate() {
    const name = document.getElementById('template-name').value;
    const text = document.getElementById('template-text').value;
    const type = document.getElementById('template-type').value;

    const response = await authFetch(
        `${API_BASE_URL}/sms/templates?org_id=${currentUser.org_id}`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                template_text: text,
                message_type: type
            })
        }
    );

    if (response.ok) {
        showToast(i18n.t('sms.template_created'), 'success');
        loadTemplates();
    } else {
        const error = await response.json();
        showToast(error.detail, 'error');
    }
}

async function previewTemplate(templateId) {
    const eventId = document.getElementById('preview-event').value;
    const volunteerId = document.getElementById('preview-volunteer').value;

    const response = await authFetch(
        `${API_BASE_URL}/sms/templates/${templateId}/preview?org_id=${currentUser.org_id}`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_id: eventId ? parseInt(eventId) : null,
                volunteer_id: volunteerId ? parseInt(volunteerId) : null,
                language: currentUser.language
            })
        }
    );

    const data = await response.json();
    displayPreview(data);
}

function displayPreview(preview) {
    document.getElementById('preview-message').textContent = preview.rendered_message;
    document.getElementById('preview-chars').textContent = preview.character_count;
    document.getElementById('preview-segments').textContent = preview.sms_segment_count;
    document.getElementById('preview-cost').textContent = `$${(preview.estimated_cost_cents / 100).toFixed(4)}`;

    // Show warning if multi-segment
    if (preview.sms_segment_count > 1) {
        showSegmentWarning(preview.sms_segment_count);
    }
}
```

---

## Testing

### Unit Tests

```python
# tests/unit/test_sms_templates.py

def test_render_template_substitutes_variables():
    """Test that template variables are substituted correctly."""
    template_text = "{{event_name}} on {{date}} at {{time}}"
    context = {
        "event_name": "Sunday Service",
        "date": "Jan 1",
        "time": "10:00AM"
    }
    result = sms_service.render_template(template_text, context)
    assert result == "Sunday Service on Jan 1 at 10:00AM"

def test_template_character_count_calculated():
    """Test that character count is stored correctly."""
    template_text = "{{event_name}} - {{date}} at {{time}}"
    char_count = len(template_text.replace("{{event_name}}", "X" * 20)
                                  .replace("{{date}}", "X" * 6)
                                  .replace("{{time}}", "X" * 7))
    assert char_count == calculate_character_count(template_text)
```

### Integration Tests

```python
# tests/integration/test_sms_templates.py

def test_create_template(client, admin_auth_headers):
    """Test creating custom SMS template."""
    response = client.post(
        "/api/sms/templates?org_id=test_org",
        json={
            "name": "Test Template",
            "template_text": "{{event_name}} on {{date}}",
            "message_type": "reminder"
        },
        headers=admin_auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Template"
    assert response.json()["is_system"] == False

def test_cannot_edit_system_template(client, admin_auth_headers):
    """Test that system templates cannot be edited."""
    response = client.put(
        "/api/sms/templates/1?org_id=test_org",  # ID 1 = system template
        json={"template_text": "Modified text"},
        headers=admin_auth_headers
    )
    assert response.status_code == 403
    assert "Cannot edit system templates" in response.json()["detail"]
```

### E2E Tests

```python
# tests/e2e/test_sms_templates.py

def test_create_and_preview_template(page: Page):
    """Test creating template and previewing with real data."""
    page.goto("http://localhost:8000/app/admin")
    page.locator('[data-i18n="admin.tabs.sms_templates"]').click()

    # Create template
    page.locator('[data-i18n="sms.create_template"]').click()
    page.locator('#template-name').fill("Test Reminder")
    page.locator('#template-text').fill("{{event_name}} tomorrow at {{time}}")
    page.locator('#template-type').select_option("reminder")
    page.locator('[data-i18n="common.buttons.save"]').click()

    # Preview template
    page.locator('.template-preview-btn').first.click()
    page.locator('#preview-event').select_option("Sunday Service")
    page.locator('[data-i18n="sms.generate_preview"]').click()

    # Verify preview shows rendered message
    expect(page.locator('#preview-message')).to_contain_text("Sunday Service tomorrow at")
```

---

## Related Documentation

- **Data Model**: `../data-model.md` - sms_templates schema with translations
- **SMS API**: `sms-api.md` - Sending SMS using templates (template_id parameter)
- **Quick Start**: `../quickstart.md` - Creating first custom template tutorial
- **Research**: `../research.md` - Jinja2 template engine decision analysis

---

**Last Updated**: 2025-10-23
**API Version**: v1
**Feature**: 019 - SMS Notification System
