# Data Model: Production Infrastructure & Deployment

**Feature Branch**: `003-production-infrastructure`
**Date**: 2025-10-20
**Phase**: 1 (Data Model - Entity Definitions)

## Overview

This document defines the data entities for production infrastructure and deployment features. These entities track deployment history, health status, backup operations, and scaling policies.

**Note**: Infrastructure entities are separate from core application entities (Person, Organization, Event). They support operational workflows rather than user-facing features.

---

## Entity Definitions

### 1. Deployment

**Purpose**: Tracks deployment events for audit trail, rollback capability, and deployment analytics.

**Database Table**: `deployments`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String | Primary Key, Auto-generated | Unique deployment ID (e.g., `deploy_20251020_143052`) |
| `version` | String | Not Null | Application version deployed (Git commit SHA or tag) |
| `environment` | Enum | Not Null | Environment: `development`, `staging`, `production` |
| `status` | Enum | Not Null | Deployment status: `in_progress`, `completed`, `failed`, `rolled_back` |
| `triggered_by` | String | Not Null | GitHub username or `automated` |
| `started_at` | DateTime | Not Null | Deployment start timestamp (UTC) |
| `completed_at` | DateTime | Nullable | Deployment completion timestamp (UTC), null if in progress |
| `duration_seconds` | Integer | Nullable | Deployment duration in seconds, null if in progress |
| `github_run_id` | String | Nullable | GitHub Actions run ID for traceability |
| `commit_sha` | String | Not Null | Full Git commit SHA (40 characters) |
| `commit_message` | String | Not Null | Git commit message (truncated to 500 chars) |
| `migration_applied` | Boolean | Not Null, Default: False | Whether database migration was applied |
| `migration_version` | String | Nullable | Alembic migration version applied (if any) |
| `health_check_passed` | Boolean | Not Null, Default: False | Whether post-deployment health check passed |
| `rollback_reason` | String | Nullable | Reason for rollback (if status = `rolled_back`) |
| `error_message` | Text | Nullable | Error details (if status = `failed`) |
| `deployment_log_url` | String | Nullable | URL to full deployment logs (GitHub Actions log) |
| `instances_deployed` | Integer | Not Null, Default: 1 | Number of application instances deployed |
| `created_at` | DateTime | Not Null, Default: NOW() | Record creation timestamp |
| `updated_at` | DateTime | Not Null, Default: NOW() | Record last update timestamp |

**Indexes**:
- `idx_deployments_environment_status` on `(environment, status)`
- `idx_deployments_started_at` on `started_at` (for time-based queries)

**Sample Data**:
```json
{
  "id": "deploy_20251020_143052",
  "version": "v1.2.3",
  "environment": "production",
  "status": "completed",
  "triggered_by": "tomqwu",
  "started_at": "2025-10-20T14:30:52Z",
  "completed_at": "2025-10-20T14:38:15Z",
  "duration_seconds": 443,
  "github_run_id": "1234567890",
  "commit_sha": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
  "commit_message": "feat: Add calendar export feature",
  "migration_applied": true,
  "migration_version": "2025_10_20_1430_add_calendar_export",
  "health_check_passed": true,
  "rollback_reason": null,
  "error_message": null,
  "deployment_log_url": "https://github.com/tomqwu/SignUpFlow/actions/runs/1234567890",
  "instances_deployed": 2,
  "created_at": "2025-10-20T14:30:52Z",
  "updated_at": "2025-10-20T14:38:15Z"
}
```

**Business Logic**:
- Deployment status transitions: `in_progress` → `completed` OR `failed`
- Rollback creates new deployment with status `rolled_back` pointing to previous version
- Deployments older than 90 days archived for compliance but kept for audit trail

---

### 2. HealthCheck

**Purpose**: Tracks application health status for monitoring, alerting, and automatic failover decisions.

**Database Table**: `health_checks`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String | Primary Key, Auto-generated | Unique health check ID |
| `instance_id` | String | Not Null | Application instance identifier (container ID or hostname) |
| `environment` | Enum | Not Null | Environment: `development`, `staging`, `production` |
| `timestamp` | DateTime | Not Null | Health check execution timestamp (UTC) |
| `overall_status` | Enum | Not Null | Overall health: `healthy`, `degraded`, `unhealthy` |
| `response_time_ms` | Integer | Not Null | Health check response time in milliseconds |
| `database_status` | Enum | Not Null | Database connectivity: `connected`, `disconnected`, `slow` |
| `database_response_ms` | Integer | Nullable | Database ping response time (null if disconnected) |
| `redis_status` | Enum | Not Null | Redis connectivity: `connected`, `disconnected`, `slow` |
| `redis_response_ms` | Integer | Nullable | Redis ping response time (null if disconnected) |
| `memory_usage_mb` | Integer | Not Null | Process memory usage in megabytes |
| `memory_usage_percent` | Float | Not Null | Memory usage as percentage of available memory |
| `cpu_usage_percent` | Float | Not Null | CPU usage percentage (0-100) |
| `uptime_seconds` | Integer | Not Null | Application uptime in seconds since last restart |
| `version` | String | Not Null | Application version (Git commit SHA or tag) |
| `total_requests` | Integer | Not Null | Total requests handled since startup |
| `active_connections` | Integer | Not Null | Current active database connections |
| `error_rate_5min` | Float | Not Null | Error rate in last 5 minutes (0.0-1.0) |
| `created_at` | DateTime | Not Null, Default: NOW() | Record creation timestamp |

**Indexes**:
- `idx_health_checks_instance_timestamp` on `(instance_id, timestamp)`
- `idx_health_checks_environment_status` on `(environment, overall_status)`

**Sample Data**:
```json
{
  "id": "health_20251020_143100",
  "instance_id": "signupflow-prod-instance-1",
  "environment": "production",
  "timestamp": "2025-10-20T14:31:00Z",
  "overall_status": "healthy",
  "response_time_ms": 45,
  "database_status": "connected",
  "database_response_ms": 12,
  "redis_status": "connected",
  "redis_response_ms": 3,
  "memory_usage_mb": 450,
  "memory_usage_percent": 44.5,
  "cpu_usage_percent": 15.2,
  "uptime_seconds": 86400,
  "version": "v1.2.3",
  "total_requests": 125340,
  "active_connections": 8,
  "error_rate_5min": 0.002,
  "created_at": "2025-10-20T14:31:00Z"
}
```

**Business Logic**:
- Health check status determination:
  - `healthy`: Database connected, Redis connected, error_rate < 0.01, response_time < 200ms
  - `degraded`: Database slow (>100ms) OR Redis slow (>50ms) OR error_rate 0.01-0.05
  - `unhealthy`: Database disconnected OR Redis disconnected OR error_rate > 0.05
- Health checks executed every 60 seconds per instance
- Retention: Keep last 24 hours in database, aggregate to hourly for historical analysis (90 days)

---

### 3. BackupJob

**Purpose**: Tracks database backup operations for compliance, restore capability, and backup health monitoring.

**Database Table**: `backup_jobs`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String | Primary Key, Auto-generated | Unique backup job ID (e.g., `backup_20251020_020000`) |
| `backup_type` | Enum | Not Null | Backup type: `full`, `incremental`, `manual` |
| `environment` | Enum | Not Null | Environment: `staging`, `production` (dev doesn't back up) |
| `status` | Enum | Not Null | Backup status: `in_progress`, `completed`, `failed` |
| `started_at` | DateTime | Not Null | Backup start timestamp (UTC) |
| `completed_at` | DateTime | Nullable | Backup completion timestamp (UTC), null if in progress |
| `duration_seconds` | Integer | Nullable | Backup duration in seconds |
| `database_name` | String | Not Null | Database name backed up |
| `backup_size_mb` | Integer | Nullable | Backup file size in megabytes (null if failed) |
| `compressed_size_mb` | Integer | Nullable | Compressed backup size in megabytes |
| `compression_ratio` | Float | Nullable | Compression ratio (compressed / original) |
| `encrypted` | Boolean | Not Null, Default: True | Whether backup is encrypted (AES-256) |
| `encryption_algorithm` | String | Not Null, Default: "AES-256" | Encryption algorithm used |
| `storage_location` | String | Not Null | Storage path (e.g., `s3://bucket/path` or `spaces://bucket/path`) |
| `storage_url` | String | Not Null | Full URL to backup file |
| `integrity_check_passed` | Boolean | Nullable | Whether integrity check passed (null if not run yet) |
| `integrity_check_at` | DateTime | Nullable | Timestamp of integrity check |
| `restore_tested` | Boolean | Not Null, Default: False | Whether restore was tested (monthly drill) |
| `restore_tested_at` | DateTime | Nullable | Last restore test timestamp |
| `retention_expires_at` | DateTime | Not Null | Backup expiration date (30 days for daily, 12 months for monthly) |
| `is_monthly_archive` | Boolean | Not Null, Default: False | Whether this is a monthly archive (longer retention) |
| `triggered_by` | String | Not Null | Backup trigger: `scheduled`, `manual`, `pre_deployment` |
| `error_message` | Text | Nullable | Error details (if status = `failed`) |
| `retry_count` | Integer | Not Null, Default: 0 | Number of retry attempts (max 3) |
| `created_at` | DateTime | Not Null, Default: NOW() | Record creation timestamp |
| `updated_at` | DateTime | Not Null, Default: NOW() | Record last update timestamp |

**Indexes**:
- `idx_backup_jobs_environment_status` on `(environment, status)`
- `idx_backup_jobs_retention_expires_at` on `retention_expires_at` (for cleanup)
- `idx_backup_jobs_started_at` on `started_at` (for time-based queries)

**Sample Data**:
```json
{
  "id": "backup_20251020_020000",
  "backup_type": "full",
  "environment": "production",
  "status": "completed",
  "started_at": "2025-10-20T02:00:00Z",
  "completed_at": "2025-10-20T02:15:34Z",
  "duration_seconds": 934,
  "database_name": "signupflow_production",
  "backup_size_mb": 1250,
  "compressed_size_mb": 380,
  "compression_ratio": 0.304,
  "encrypted": true,
  "encryption_algorithm": "AES-256",
  "storage_location": "spaces://signupflow-backups/production/2025/10/20",
  "storage_url": "https://signupflow-backups.nyc3.digitaloceanspaces.com/production/2025/10/20/backup_20251020_020000.sql.gz.enc",
  "integrity_check_passed": true,
  "integrity_check_at": "2025-10-20T02:16:00Z",
  "restore_tested": false,
  "restore_tested_at": null,
  "retention_expires_at": "2025-11-19T02:00:00Z",
  "is_monthly_archive": false,
  "triggered_by": "scheduled",
  "error_message": null,
  "retry_count": 0,
  "created_at": "2025-10-20T02:00:00Z",
  "updated_at": "2025-10-20T02:16:00Z"
}
```

**Business Logic**:
- Daily backups: Full backup every 24 hours at 2:00 AM UTC
- Monthly archives: First backup of each month marked as `is_monthly_archive=true` with 12-month retention
- Failed backups retry 3 times with 5-minute delays
- Integrity check runs immediately after backup completes
- Restore testing: Monthly drill on last Sunday of month
- Cleanup job: Delete backups past `retention_expires_at` (runs daily at 3:00 AM UTC)

---

### 4. ScalingPolicy

**Purpose**: Defines rules for horizontal scaling decisions (when to add/remove instances).

**Database Table**: `scaling_policies`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String | Primary Key, Auto-generated | Unique scaling policy ID |
| `environment` | Enum | Not Null, Unique | Environment: `staging`, `production` (one policy per environment) |
| `enabled` | Boolean | Not Null, Default: True | Whether scaling policy is active |
| `min_instances` | Integer | Not Null | Minimum number of instances (cannot scale below) |
| `max_instances` | Integer | Not Null | Maximum number of instances (cannot scale above) |
| `target_cpu_percent` | Float | Not Null | Target CPU utilization (0-100) triggering scale decisions |
| `target_memory_percent` | Float | Not Null | Target memory utilization (0-100) triggering scale decisions |
| `scale_up_threshold` | Float | Not Null | Metric threshold to trigger scale up (e.g., 0.75 = 75% utilization) |
| `scale_down_threshold` | Float | Not Null | Metric threshold to trigger scale down (e.g., 0.30 = 30% utilization) |
| `scale_up_cooldown_seconds` | Integer | Not Null | Minimum time between scale-up actions (prevent thrashing) |
| `scale_down_cooldown_seconds` | Integer | Not Null | Minimum time between scale-down actions (prevent thrashing) |
| `evaluation_period_seconds` | Integer | Not Null | Time window for metric evaluation (e.g., 300 = 5 minutes) |
| `datapoints_to_trigger` | Integer | Not Null | Number of consecutive periods above threshold to trigger scaling |
| `created_at` | DateTime | Not Null, Default: NOW() | Record creation timestamp |
| `updated_at` | DateTime | Not Null, Default: NOW() | Record last update timestamp |

**Indexes**:
- `idx_scaling_policies_environment` on `environment` (for quick lookups)

**Sample Data**:
```json
{
  "id": "policy_production",
  "environment": "production",
  "enabled": true,
  "min_instances": 2,
  "max_instances": 10,
  "target_cpu_percent": 70.0,
  "target_memory_percent": 75.0,
  "scale_up_threshold": 0.80,
  "scale_down_threshold": 0.40,
  "scale_up_cooldown_seconds": 300,
  "scale_down_cooldown_seconds": 600,
  "evaluation_period_seconds": 300,
  "datapoints_to_trigger": 2,
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-20T10:00:00Z"
}
```

**Business Logic**:
- Scale up decision: If average CPU/memory > `scale_up_threshold` for `datapoints_to_trigger` consecutive periods AND `scale_up_cooldown_seconds` elapsed since last scale-up → add 1 instance
- Scale down decision: If average CPU/memory < `scale_down_threshold` for `datapoints_to_trigger` consecutive periods AND `scale_down_cooldown_seconds` elapsed since last scale-down → remove 1 instance
- Respect `min_instances` and `max_instances` boundaries
- Evaluation runs every `evaluation_period_seconds` (default: 5 minutes)

---

### 5. ScalingEvent

**Purpose**: Tracks scaling actions for audit trail and scaling behavior analysis.

**Database Table**: `scaling_events`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String | Primary Key, Auto-generated | Unique scaling event ID |
| `environment` | Enum | Not Null | Environment: `staging`, `production` |
| `timestamp` | DateTime | Not Null | Scaling event timestamp (UTC) |
| `action` | Enum | Not Null | Scaling action: `scale_up`, `scale_down`, `manual_scale` |
| `instances_before` | Integer | Not Null | Number of instances before scaling |
| `instances_after` | Integer | Not Null | Number of instances after scaling |
| `trigger_reason` | String | Not Null | Reason for scaling (e.g., "CPU 85% for 10 minutes") |
| `cpu_percent_avg` | Float | Not Null | Average CPU utilization during evaluation period |
| `memory_percent_avg` | Float | Not Null | Average memory utilization during evaluation period |
| `triggered_by` | String | Not Null | Scaling trigger: `autoscaler`, `manual`, `deployment` |
| `triggered_by_user` | String | Nullable | Username if manually triggered |
| `success` | Boolean | Not Null | Whether scaling action completed successfully |
| `error_message` | Text | Nullable | Error details if scaling failed |
| `created_at` | DateTime | Not Null, Default: NOW() | Record creation timestamp |

**Indexes**:
- `idx_scaling_events_environment_timestamp` on `(environment, timestamp)`
- `idx_scaling_events_action` on `action` (for analytics)

**Sample Data**:
```json
{
  "id": "scale_20251020_150000",
  "environment": "production",
  "timestamp": "2025-10-20T15:00:00Z",
  "action": "scale_up",
  "instances_before": 2,
  "instances_after": 3,
  "trigger_reason": "CPU utilization 82% for 10 minutes (threshold 80%)",
  "cpu_percent_avg": 82.3,
  "memory_percent_avg": 68.5,
  "triggered_by": "autoscaler",
  "triggered_by_user": null,
  "success": true,
  "error_message": null,
  "created_at": "2025-10-20T15:00:00Z"
}
```

**Business Logic**:
- Scaling events logged for audit trail
- Analytics: Identify scaling patterns, optimize scaling policies
- Retention: Keep last 90 days of scaling events

---

## Entity Relationships

```
┌─────────────────┐
│   Deployment    │
└────────┬────────┘
         │ 1:N
         │ (deployment triggers health checks)
         ▼
┌─────────────────┐
│   HealthCheck   │
└────────┬────────┘
         │ M:1
         │ (health checks inform scaling)
         ▼
┌─────────────────┐       1:1       ┌─────────────────┐
│ ScalingPolicy   │◄────────────────│   Environment    │
└────────┬────────┘                 └──────────────────┘
         │ 1:N
         │ (policy triggers scaling events)
         ▼
┌─────────────────┐
│  ScalingEvent   │
└─────────────────┘

┌─────────────────┐
│   BackupJob     │  (Independent entity - no direct relationships)
└─────────────────┘
```

**Relationships Explained**:
- **Deployment → HealthCheck**: Each deployment triggers health checks on new instances
- **HealthCheck → ScalingPolicy**: Health checks provide metrics for scaling decisions
- **ScalingPolicy → ScalingEvent**: Policy triggers scaling events when thresholds met
- **BackupJob**: Independent operational entity (not tied to deployments or scaling)

---

## Database Migrations

**Alembic Migration Script**: `alembic/versions/2025_10_20_infrastructure_tables.py`

**Migration Operations**:
1. Create `deployments` table with indexes
2. Create `health_checks` table with indexes
3. Create `backup_jobs` table with indexes
4. Create `scaling_policies` table with unique constraint on environment
5. Create `scaling_events` table with indexes
6. Seed initial scaling policies for staging and production environments

**Rollback Strategy**: Drop all created tables in reverse order

---

## SQLAlchemy Models

**File**: `api/models.py`

**New Models Added**:
```python
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from api.database import Base
import enum

class DeploymentStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class HealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class BackupStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(String, primary_key=True, index=True)
    version = Column(String, nullable=False)
    environment = Column(String, nullable=False, index=True)
    status = Column(SQLEnum(DeploymentStatus), nullable=False, index=True)
    # ... (additional fields as per data model above)

class HealthCheck(Base):
    __tablename__ = "health_checks"

    id = Column(String, primary_key=True, index=True)
    instance_id = Column(String, nullable=False, index=True)
    # ... (additional fields)

class BackupJob(Base):
    __tablename__ = "backup_jobs"

    id = Column(String, primary_key=True, index=True)
    backup_type = Column(String, nullable=False)
    # ... (additional fields)

class ScalingPolicy(Base):
    __tablename__ = "scaling_policies"

    id = Column(String, primary_key=True, index=True)
    environment = Column(String, nullable=False, unique=True)
    # ... (additional fields)

class ScalingEvent(Base):
    __tablename__ = "scaling_events"

    id = Column(String, primary_key=True, index=True)
    environment = Column(String, nullable=False, index=True)
    # ... (additional fields)
```

---

## Next Steps

**Phase 1 Continuation**:
1. ✅ Data model defined (this document)
2. ⏳ Generate API contracts in `contracts/` directory (health check endpoint)
3. ⏳ Create `quickstart.md` for developers (setup PostgreSQL locally)
4. ⏳ Update agent context file with infrastructure knowledge

**Ready for Contracts Generation** - Proceed to define `/health` endpoint specification.
