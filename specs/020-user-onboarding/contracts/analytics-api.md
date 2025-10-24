# API Contract: Onboarding Analytics Events

**Feature**: User Onboarding System | **Branch**: `020-user-onboarding` | **Date**: 2025-10-23

API endpoints for tracking onboarding analytics events and generating funnel reports.

---

## Base URL

```
/api/analytics/onboarding-events
```

**Authentication**: Required (JWT Bearer token)
**Rate Limit**: 500 requests per minute per organization
**RBAC**: All authenticated users (event tracking), Admin only (reports)

---

## Endpoints

### 1. Track Onboarding Event

**Endpoint**: `POST /api/analytics/onboarding-events`

**Description**: Record analytics event for onboarding funnel analysis.

**Query Parameters**: None

**Request Body**:

```json
{
  "organization_id": "org_123",
  "event_type": "wizard_step_completed",
  "event_data": {
    "step_number": 2,
    "step_name": "first_event",
    "validation_errors": 0,
    "time_spent_seconds": 45
  },
  "wizard_step_reached": 2,
  "step_duration_seconds": 45,
  "session_id": "session_abc123",
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}
```

**Request Body Schema**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `organization_id` | string | Yes | Organization ID |
| `event_type` | string | Yes | Event name (see event types below) |
| `event_data` | object | No | Custom event properties |
| `wizard_step_reached` | integer | No | Wizard step number reached (1-5) |
| `wizard_step_dropped` | integer | No | Wizard step number where user abandoned |
| `step_duration_seconds` | integer | No | Time spent on step |
| `completion_time_minutes` | integer | No | Total time to complete onboarding |
| `session_id` | string | No | Session ID for grouping events |
| `user_agent` | string | No | Browser user agent |

**Success Response** (201 Created):

```json
{
  "event": {
    "id": "metric_1234567890",
    "organization_id": "org_123",
    "event_type": "wizard_step_completed",
    "timestamp": "2025-10-23T15:30:00Z"
  },
  "message": "Event tracked successfully"
}
```

**Error Responses**:

```json
// 400 Bad Request - Invalid event type
{
  "error": "Bad Request",
  "message": "Invalid event_type. Must be one of: wizard_started, wizard_step_completed, ..."
}

// 422 Validation Error - Missing required event data
{
  "error": "Validation Error",
  "message": "Missing required field for event type 'wizard_step_completed': step_number"
}
```

---

### 2. Get Onboarding Funnel Report

**Endpoint**: `GET /api/analytics/onboarding-funnel`

**Description**: Generate funnel report showing wizard completion rates and drop-off points.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | No | Filter by organization (admin only) |
| `start_date` | string | No | Start date (ISO 8601, default: 30 days ago) |
| `end_date` | string | No | End date (ISO 8601, default: today) |

**Request Example**:

```http
GET /api/analytics/onboarding-funnel?start_date=2025-10-01&end_date=2025-10-23 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response** (200 OK):

```json
{
  "funnel": {
    "period": {
      "start_date": "2025-10-01",
      "end_date": "2025-10-23",
      "days": 23
    },
    "steps": [
      {
        "step": 0,
        "step_name": "signup",
        "organizations": 150,
        "conversion_rate": 100.0,
        "drop_off_count": 0,
        "drop_off_rate": 0.0
      },
      {
        "step": 1,
        "step_name": "wizard_started",
        "organizations": 142,
        "conversion_rate": 94.7,
        "drop_off_count": 8,
        "drop_off_rate": 5.3
      },
      {
        "step": 1,
        "step_name": "organization_profile",
        "organizations": 135,
        "conversion_rate": 95.1,
        "drop_off_count": 7,
        "drop_off_rate": 4.9
      },
      {
        "step": 2,
        "step_name": "first_event",
        "organizations": 120,
        "conversion_rate": 88.9,
        "drop_off_count": 15,
        "drop_off_rate": 11.1
      },
      {
        "step": 3,
        "step_name": "first_team",
        "organizations": 108,
        "conversion_rate": 90.0,
        "drop_off_count": 12,
        "drop_off_rate": 10.0
      },
      {
        "step": 4,
        "step_name": "invite_volunteers",
        "organizations": 95,
        "conversion_rate": 88.0,
        "drop_off_count": 13,
        "drop_off_rate": 12.0
      },
      {
        "step": 5,
        "step_name": "tutorial_intro",
        "organizations": 87,
        "conversion_rate": 91.6,
        "drop_off_count": 8,
        "drop_off_rate": 8.4
      },
      {
        "step": "completed",
        "step_name": "wizard_completed",
        "organizations": 82,
        "conversion_rate": 94.3,
        "drop_off_count": 5,
        "drop_off_rate": 5.7
      }
    ],
    "overall": {
      "started": 150,
      "completed": 82,
      "completion_rate": 54.7,
      "skipped": 15,
      "skip_rate": 10.0,
      "abandoned": 53,
      "abandonment_rate": 35.3
    },
    "drop_off_analysis": {
      "highest_drop_off_step": 2,
      "highest_drop_off_name": "first_event",
      "highest_drop_off_rate": 11.1,
      "lowest_drop_off_step": 1,
      "lowest_drop_off_name": "organization_profile",
      "lowest_drop_off_rate": 4.9
    }
  }
}
```

---

### 3. Get Completion Time Distribution

**Endpoint**: `GET /api/analytics/onboarding-completion-time`

**Description**: Analyze time taken to complete onboarding wizard.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Start date (ISO 8601) |
| `end_date` | string | No | End date (ISO 8601) |

**Success Response** (200 OK):

```json
{
  "completion_time": {
    "period": {
      "start_date": "2025-10-01",
      "end_date": "2025-10-23"
    },
    "statistics": {
      "count": 82,
      "mean_minutes": 18.5,
      "median_minutes": 15.0,
      "min_minutes": 5,
      "max_minutes": 120,
      "std_dev_minutes": 12.3,
      "percentiles": {
        "p25": 12,
        "p50": 15,
        "p75": 22,
        "p90": 35,
        "p95": 45
      }
    },
    "distribution": {
      "0-10_min": 15,
      "10-20_min": 42,
      "20-30_min": 18,
      "30-60_min": 5,
      "60+_min": 2
    },
    "success_criteria": {
      "target_time_minutes": 15,
      "organizations_under_target": 57,
      "percentage_under_target": 69.5
    }
  }
}
```

---

### 4. Get Feature Usage Report

**Endpoint**: `GET /api/analytics/onboarding-features`

**Description**: Analyze which onboarding features are most used.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Start date (ISO 8601) |
| `end_date` | string | No | End date (ISO 8601) |

**Success Response** (200 OK):

```json
{
  "feature_usage": {
    "period": {
      "start_date": "2025-10-01",
      "end_date": "2025-10-23"
    },
    "features": {
      "sample_data": {
        "total_generated": 95,
        "usage_rate": 63.3,
        "avg_exploration_time_minutes": 8.5,
        "cleared_count": 12,
        "clear_rate": 12.6
      },
      "tutorials": {
        "total_started": 120,
        "total_completed": 87,
        "completion_rate": 72.5,
        "skipped": 33,
        "skip_rate": 27.5,
        "avg_duration_minutes": 4.2,
        "most_popular": [
          {
            "tutorial_id": "events_intro",
            "started": 110,
            "completed": 95,
            "completion_rate": 86.4
          },
          {
            "tutorial_id": "solver_run",
            "started": 85,
            "completed": 62,
            "completion_rate": 72.9
          }
        ]
      },
      "videos": {
        "total_played": 145,
        "total_completed": 78,
        "completion_rate": 53.8,
        "avg_watch_percentage": 68.5,
        "most_watched": [
          {
            "video_id": "create_event",
            "plays": 120,
            "avg_watch_percent": 85.3
          },
          {
            "video_id": "invite_volunteers",
            "plays": 95,
            "avg_watch_percent": 72.1
          }
        ]
      },
      "checklist": {
        "organizations_viewed": 135,
        "avg_tasks_completed": 4.2,
        "full_completion_rate": 28.9,
        "task_completion_rates": [
          {
            "task_id": "complete_profile",
            "completion_rate": 89.6
          },
          {
            "task_id": "create_first_event",
            "completion_rate": 72.6
          },
          {
            "task_id": "add_team",
            "completion_rate": 65.2
          },
          {
            "task_id": "invite_volunteers",
            "completion_rate": 58.5
          },
          {
            "task_id": "run_first_schedule",
            "completion_rate": 45.2
          },
          {
            "task_id": "view_reports",
            "completion_rate": 32.6
          }
        ]
      },
      "wizard_skip": {
        "total_skipped": 15,
        "skip_rate": 10.0,
        "skip_by_step": [
          {
            "step": 1,
            "count": 3,
            "skip_reason": "experienced_user"
          },
          {
            "step": 2,
            "count": 7,
            "skip_reason": "return_later"
          },
          {
            "step": 3,
            "count": 5,
            "skip_reason": "other"
          }
        ]
      }
    }
  }
}
```

---

### 5. Get Onboarding Cohort Analysis

**Endpoint**: `GET /api/analytics/onboarding-cohorts`

**Description**: Analyze onboarding completion by signup date cohort.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cohort_size` | string | No | Cohort grouping: `day`, `week`, `month` (default: `week`) |
| `start_date` | string | No | Start date (ISO 8601) |
| `end_date` | string | No | End date (ISO 8601) |

**Success Response** (200 OK):

```json
{
  "cohort_analysis": {
    "cohort_size": "week",
    "cohorts": [
      {
        "cohort_start": "2025-10-01",
        "cohort_end": "2025-10-07",
        "organizations": 35,
        "completed": 22,
        "completion_rate": 62.9,
        "avg_completion_time_minutes": 20.3,
        "skipped": 4,
        "abandoned": 9
      },
      {
        "cohort_start": "2025-10-08",
        "cohort_end": "2025-10-14",
        "organizations": 42,
        "completed": 28,
        "completion_rate": 66.7,
        "avg_completion_time_minutes": 17.8,
        "skipped": 5,
        "abandoned": 9
      },
      {
        "cohort_start": "2025-10-15",
        "cohort_end": "2025-10-21",
        "organizations": 38,
        "completed": 32,
        "completion_rate": 84.2,
        "avg_completion_time_minutes": 15.2,
        "skipped": 2,
        "abandoned": 4
      }
    ],
    "trend": {
      "completion_rate_trend": "increasing",
      "avg_time_trend": "decreasing",
      "skip_rate_trend": "decreasing"
    }
  }
}
```

---

## Event Types

### Wizard Events

| Event Type | Description | Required Fields |
|------------|-------------|-----------------|
| `wizard_started` | User began onboarding wizard | `event_data.entry_point` |
| `wizard_step_completed` | User completed specific wizard step | `wizard_step_reached`, `step_duration_seconds` |
| `wizard_completed` | User finished entire wizard | `completion_time_minutes` |
| `wizard_skipped` | User clicked "Skip Onboarding" | `wizard_step_dropped`, `event_data.skip_reason` |
| `wizard_reset` | User reset wizard to beginning | `event_data.previous_step` |

### Sample Data Events

| Event Type | Description | Required Fields |
|------------|-------------|-----------------|
| `sample_data_generated` | User generated sample data | `event_data.dataset_size`, `event_data.generation_time_seconds` |
| `sample_data_cleared` | User cleared sample data | `event_data.data_age_days` |
| `sample_data_regenerated` | User regenerated sample data | `event_data.previous_size`, `event_data.new_size` |

### Tutorial Events

| Event Type | Description | Required Fields |
|------------|-------------|-----------------|
| `tutorial_started` | User started interactive tutorial | `event_data.tutorial_id` |
| `tutorial_completed` | User completed tutorial | `event_data.tutorial_id`, `event_data.duration_seconds` |
| `tutorial_skipped` | User skipped tutorial | `event_data.tutorial_id`, `event_data.step_reached` |
| `tutorial_replayed` | User replayed tutorial | `event_data.tutorial_id`, `event_data.replay_count` |

### Video Events

| Event Type | Description | Required Fields |
|------------|-------------|-----------------|
| `video_played` | User played quick start video | `event_data.video_id`, `event_data.video_title` |
| `video_completed` | User watched video to end | `event_data.video_id`, `event_data.watch_percentage` |
| `video_seeked` | User jumped to specific time | `event_data.video_id`, `event_data.seek_position_seconds` |

### Checklist Events

| Event Type | Description | Required Fields |
|------------|-------------|-----------------|
| `checklist_viewed` | User viewed checklist | `event_data.completed_count`, `event_data.total_count` |
| `checklist_task_completed` | User completed checklist task | `event_data.task_id`, `event_data.time_to_complete_minutes` |
| `checklist_quick_action_clicked` | User clicked quick action button | `event_data.task_id`, `event_data.target_url` |

### Feature Unlock Events

| Event Type | Description | Required Fields |
|------------|-------------|-----------------|
| `feature_unlocked` | Feature unlocked via milestone | `event_data.feature_id`, `event_data.milestone_type` |
| `feature_toggled` | User toggled "Show all features" | `event_data.show_all_features` |

---

## Business Logic Rules

### Event Tracking Rules

1. **Automatic Tracking**: Core events tracked automatically by API endpoints
2. **Optional Manual Tracking**: Frontend can send additional events (video plays, UI interactions)
3. **Session Grouping**: Events grouped by `session_id` for workflow analysis
4. **Append-Only**: Events never updated or deleted (time-series data)
5. **Privacy**: No PII stored (only `organization_id`, no user names or emails)

### Report Generation Rules

1. **Real-Time**: Reports generated on-demand from raw event data
2. **Aggregation**: Pre-aggregated tables for fast dashboard loading (future optimization)
3. **Time Filters**: Default 30-day window, maximum 365 days
4. **Permissions**: Individual org analytics visible to org admins, global analytics visible to system admins only

---

## Analytics Dashboard Integration

### Frontend Analytics Tracking

```javascript
// frontend/js/analytics.js
class OnboardingAnalytics {
    constructor(orgId, sessionId) {
        this.orgId = orgId;
        this.sessionId = sessionId || this.generateSessionId();
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async trackEvent(eventType, eventData = {}) {
        const payload = {
            organization_id: this.orgId,
            event_type: eventType,
            event_data: eventData,
            session_id: this.sessionId,
            user_agent: navigator.userAgent,
            timestamp: new Date().toISOString()
        };

        try {
            const response = await authFetch('/api/analytics/onboarding-events', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                console.error('Failed to track analytics event:', eventType);
            }
        } catch (error) {
            console.error('Analytics tracking error:', error);
            // Silently fail - don't block user experience
        }
    }

    // Convenience methods
    async trackWizardStepCompleted(stepNumber, stepName, durationSeconds) {
        return this.trackEvent('wizard_step_completed', {
            step_number: stepNumber,
            step_name: stepName,
            time_spent_seconds: durationSeconds
        });
    }

    async trackVideoPlayed(videoId, videoTitle) {
        return this.trackEvent('video_played', {
            video_id: videoId,
            video_title: videoTitle
        });
    }

    async trackChecklistTaskCompleted(taskId, timeToCompleteMinutes) {
        return this.trackEvent('checklist_task_completed', {
            task_id: taskId,
            time_to_complete_minutes: timeToCompleteMinutes
        });
    }
}

// Initialize analytics for session
const analytics = new OnboardingAnalytics(currentUser.org_id);

// Track wizard step completion
await analytics.trackWizardStepCompleted(2, 'first_event', 45);
```

### Video Tracking Example

```javascript
// Track video events with HTML5 Video API
function setupVideoAnalytics(videoElement, videoId, videoTitle) {
    const analytics = new OnboardingAnalytics(currentUser.org_id);
    let playStartTime = null;

    videoElement.addEventListener('play', () => {
        playStartTime = Date.now();
        analytics.trackVideoPlayed(videoId, videoTitle);
    });

    videoElement.addEventListener('ended', () => {
        const watchDuration = (Date.now() - playStartTime) / 1000;
        const videoDuration = videoElement.duration;
        const watchPercentage = (watchDuration / videoDuration) * 100;

        analytics.trackEvent('video_completed', {
            video_id: videoId,
            video_title: videoTitle,
            watch_percentage: Math.min(watchPercentage, 100),
            watch_duration_seconds: watchDuration
        });
    });

    videoElement.addEventListener('seeked', () => {
        analytics.trackEvent('video_seeked', {
            video_id: videoId,
            seek_position_seconds: videoElement.currentTime
        });
    });
}
```

---

## Error Handling

### Common Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid event type or missing required fields |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User not authorized to view analytics |
| 422 | Validation Error | Event data validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Database error |

---

## Testing Requirements

### Unit Tests
- [ ] Test event tracking validates event types
- [ ] Test event tracking validates required fields
- [ ] Test funnel report calculation logic
- [ ] Test completion time statistics (mean, median, percentiles)
- [ ] Test cohort grouping (day, week, month)

### Integration Tests
- [ ] Test POST event creates record in database
- [ ] Test GET funnel report aggregates events correctly
- [ ] Test completion time report filters by date range
- [ ] Test feature usage report counts events by type
- [ ] Test cohort analysis groups by signup date

### E2E Tests
- [ ] Test analytics events tracked during wizard flow
- [ ] Test video play events tracked when video played
- [ ] Test checklist task events tracked when task completed
- [ ] Test analytics dashboard displays funnel report
- [ ] Test reports update when date range changed

---

## Performance Considerations

### Query Optimization
- Indexes on `(organization_id, event_type, timestamp)` for fast aggregation
- Pre-aggregated tables for frequently accessed reports (future)
- Limit time ranges to prevent full table scans (max 365 days)

### Caching Strategy
- Cache funnel reports for 1 hour (Redis)
- Cache feature usage reports for 6 hours
- Invalidate cache when new events added (or accept staleness)

---

## Privacy & Security

### Data Anonymization
- No user names, emails, or PII stored in analytics events
- Only `organization_id` and `session_id` for grouping
- User agent truncated to prevent fingerprinting

### GDPR Compliance
- Analytics data deleted when organization account deleted
- Organization can request analytics data export
- Session IDs rotated daily to prevent long-term tracking

---

**API Version**: v1
**Last Updated**: 2025-10-23
**Feature**: 020 - User Onboarding System
