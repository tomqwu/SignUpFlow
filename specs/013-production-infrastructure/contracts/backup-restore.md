# Contract: Backup and Restore Interface

**Feature**: Production Infrastructure Deployment (013)
**Contract Type**: Command-Line Interface Specification
**Version**: 1.0
**Status**: Draft

---

## Overview

The backup and restore interface defines the command-line contracts for automated database backups and manual disaster recovery operations. This contract specifies how operations teams interact with backup systems to protect data and recover from failures.

**Purpose**: Establish standardized, repeatable, and testable backup/restore procedures with automated scheduling and point-in-time recovery capabilities.

---

## Command Interface

### Backup Command

**Purpose**: Create a database backup and upload to S3 storage

**Command**:
```bash
scripts/backup-database.sh [options]
```

**Options**:
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--environment` | `-e` | Target environment: staging, production | `production` |
| `--format` | `-f` | Backup format: sql, custom | `custom` (PostgreSQL custom format) |
| `--compression` | `-c` | Compression level (0-9) | `6` (balanced) |
| `--local-only` | | Skip S3 upload (local backup only) | `false` |
| `--retention-days` | `-r` | S3 lifecycle retention period | `30` |
| `--verbose` | `-v` | Verbose output (debugging) | `false` |
| `--help` | `-h` | Show help message | |

**Examples**:
```bash
# Standard production backup (automated)
scripts/backup-database.sh

# Staging backup (manual)
scripts/backup-database.sh --environment staging

# Local backup only (no S3 upload)
scripts/backup-database.sh --local-only

# High-compression backup (slower but smaller)
scripts/backup-database.sh --compression 9

# Verbose debugging output
scripts/backup-database.sh --verbose
```

**Output**:
```
🔄 Starting database backup...
📋 Environment: production
📦 Format: custom (PostgreSQL binary)
🗜️ Compression: level 6

[2025-10-23 14:32:15] Connecting to database...
[2025-10-23 14:32:16] Connection established
[2025-10-23 14:32:16] Starting pg_dump...
[2025-10-23 14:35:42] Backup completed (3m 26s)
[2025-10-23 14:35:42] Backup size: 1.2 GB (compressed)
[2025-10-23 14:35:43] Uploading to S3: s3://signupflow-backups/production/backup-20251023-143215.dump
[2025-10-23 14:38:12] Upload completed (2m 29s)
[2025-10-23 14:38:13] Verifying backup integrity...
[2025-10-23 14:38:14] ✅ Backup verification successful

📊 Backup Summary:
   File: /tmp/signupflow-backup-20251023-143215.dump
   Size: 1.2 GB
   Duration: 5m 58s
   S3 Location: s3://signupflow-backups/production/backup-20251023-143215.dump
   Retention: 30 days (expires 2025-11-22)

✅ Backup completed successfully
```

**Exit Codes**:
- `0` - Backup successful
- `1` - Database connection failure
- `2` - pg_dump execution failure
- `3` - S3 upload failure
- `4` - Backup verification failure
- `5` - Insufficient disk space
- `6` - Invalid configuration

---

### Restore Command

**Purpose**: Restore database from backup file (local or S3)

**Command**:
```bash
scripts/restore-database.sh [options] <backup-file>
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `<backup-file>` | Yes | Backup file path or S3 URL |

**Options**:
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--environment` | `-e` | Target environment: staging, production | `staging` (safety) |
| `--force` | | Skip confirmation prompts (dangerous) | `false` |
| `--verify` | | Verify backup before restore | `true` |
| `--dry-run` | | Simulate restore without modifying database | `false` |
| `--point-in-time` | `-p` | Restore to specific timestamp (ISO 8601) | Latest |
| `--verbose` | `-v` | Verbose output (debugging) | `false` |
| `--help` | `-h` | Show help message | |

**Examples**:
```bash
# Restore from local backup file
scripts/restore-database.sh /tmp/backup-20251023-143215.dump

# Restore from S3 backup
scripts/restore-database.sh s3://signupflow-backups/production/backup-20251023-143215.dump

# Restore to staging environment (safe testing)
scripts/restore-database.sh --environment staging /tmp/backup.dump

# Force restore without confirmation (automated restore)
scripts/restore-database.sh --force --environment staging s3://signupflow-backups/production/backup-20251023-143215.dump

# Dry-run to validate backup without restoring
scripts/restore-database.sh --dry-run /tmp/backup.dump

# Point-in-time recovery (if supported)
scripts/restore-database.sh --point-in-time "2025-10-23T12:00:00Z" s3://signupflow-backups/production/backup-20251023-143215.dump

# Verbose debugging output
scripts/restore-database.sh --verbose /tmp/backup.dump
```

**Output**:
```
⚠️  DATABASE RESTORE OPERATION ⚠️

You are about to OVERWRITE the database with data from backup.
This operation is IRREVERSIBLE and will DELETE all current data.

📋 Restore Details:
   Backup File: s3://signupflow-backups/production/backup-20251023-143215.dump
   Backup Date: 2025-10-23 14:32:15 UTC
   Backup Size: 1.2 GB
   Target Environment: staging
   Target Database: postgresql://staging-db:5432/signupflow_staging

Are you sure you want to continue? [y/N]: y

🔄 Starting database restore...

[2025-10-23 15:10:12] Downloading backup from S3...
[2025-10-23 15:12:45] Download completed (2m 33s)
[2025-10-23 15:12:46] Verifying backup integrity...
[2025-10-23 15:12:48] ✅ Backup verification successful
[2025-10-23 15:12:48] Creating pre-restore backup...
[2025-10-23 15:14:20] Pre-restore backup saved: /tmp/pre-restore-20251023-151220.dump
[2025-10-23 15:14:21] Terminating active database connections...
[2025-10-23 15:14:22] Dropping existing database...
[2025-10-23 15:14:23] Creating new database...
[2025-10-23 15:14:24] Starting pg_restore...
[2025-10-23 15:28:15] Restore completed (13m 51s)
[2025-10-23 15:28:16] Analyzing database statistics...
[2025-10-23 15:29:02] Rebuilding indexes...
[2025-10-23 15:30:45] Vacuuming database...
[2025-10-23 15:31:22] Verifying data integrity...
[2025-10-23 15:31:45] ✅ Data integrity verification successful

📊 Restore Summary:
   Backup File: backup-20251023-143215.dump
   Backup Date: 2025-10-23 14:32:15 UTC
   Restore Duration: 19m 33s
   Database Size: 1.8 GB (uncompressed)
   Tables Restored: 15
   Rows Restored: 1,245,678

✅ Database restore completed successfully
```

**Exit Codes**:
- `0` - Restore successful
- `1` - Backup file not found
- `2` - Backup verification failure
- `3` - Database connection failure
- `4` - pg_restore execution failure
- `5` - Data integrity verification failure
- `6` - User cancelled operation
- `7` - Invalid configuration

---

## Backup Strategy

### Automated Daily Backups

**Schedule**: Every day at 2:00 AM UTC (low-traffic period)

**Implementation**:
```bash
# /etc/cron.d/signupflow-backup
0 2 * * * ubuntu /home/ubuntu/SignUpFlow/scripts/backup-database.sh --environment production >> /var/log/signupflow-backup.log 2>&1
```

**OR** using systemd timer:
```bash
# /etc/systemd/system/signupflow-backup.timer
[Unit]
Description=SignUpFlow Daily Database Backup

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

**Backup Retention Policy**:
- **Daily backups**: Retained for 30 days
- **Weekly backups**: Retained for 90 days (first backup of week)
- **Monthly backups**: Retained for 1 year (first backup of month)
- **Lifecycle management**: S3 lifecycle policy automatically deletes expired backups

### Local Backup Cache

**Purpose**: Keep recent backups on local disk for fast restore

**Strategy**:
- Last 7 daily backups cached locally (`/var/backups/signupflow/`)
- Older backups: S3 only (deleted from local disk)
- **Fast restore**: <5 minutes from local cache (vs <30 minutes from S3)

**Disk Space Management**:
```bash
# Cleanup old local backups (keep last 7 days)
find /var/backups/signupflow/ -name "backup-*.dump" -mtime +7 -delete
```

---

## S3 Bucket Structure

### Backup File Organization

```
s3://signupflow-backups/
├── production/
│   ├── daily/
│   │   ├── backup-20251023-020000.dump
│   │   ├── backup-20251022-020000.dump
│   │   └── ... (30 days)
│   ├── weekly/
│   │   ├── backup-20251020-020000.dump  (Sunday)
│   │   ├── backup-20251013-020000.dump
│   │   └── ... (12 weeks)
│   └── monthly/
│       ├── backup-20251001-020000.dump
│       ├── backup-20250901-020000.dump
│       └── ... (12 months)
│
├── staging/
│   └── daily/
│       ├── backup-20251023-020000.dump
│       └── ... (7 days only)
│
└── manual/
    ├── pre-migration-20251015-120000.dump
    ├── pre-upgrade-20251018-140000.dump
    └── ... (manual backups, retained indefinitely)
```

### S3 Lifecycle Policy

```json
{
  "Rules": [
    {
      "Id": "delete-daily-backups-after-30-days",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "production/daily/"
      },
      "Expiration": {
        "Days": 30
      }
    },
    {
      "Id": "delete-weekly-backups-after-90-days",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "production/weekly/"
      },
      "Expiration": {
        "Days": 90
      }
    },
    {
      "Id": "delete-monthly-backups-after-365-days",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "production/monthly/"
      },
      "Expiration": {
        "Days": 365
      }
    },
    {
      "Id": "delete-staging-backups-after-7-days",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "staging/daily/"
      },
      "Expiration": {
        "Days": 7
      }
    }
  ]
}
```

---

## Backup Verification

### Integrity Checks

**Automatic Verification** (performed after every backup):

1. **File Integrity**: Verify backup file can be read by `pg_restore --list`
2. **Checksum Validation**: Compare MD5 checksum before and after S3 upload
3. **Metadata Extraction**: Verify database name, version, timestamp match expected values

**Example Verification**:
```bash
# Test backup can be restored (dry-run)
pg_restore --list backup-20251023-143215.dump > /dev/null

# Verify checksum
md5sum backup-20251023-143215.dump
echo "abc123def456 backup-20251023-143215.dump" | md5sum --check

# Extract metadata
pg_restore --schema-only backup-20251023-143215.dump | head -20
```

### Monthly Restore Tests

**Purpose**: Verify backups can actually be restored (disaster recovery drill)

**Schedule**: First Sunday of each month at 4:00 AM

**Procedure**:
1. Download latest production backup from S3
2. Restore to staging environment
3. Run smoke tests (verify application connects and serves traffic)
4. Compare row counts (production vs restored staging)
5. Generate restore test report
6. Alert if any verification step fails

**Implementation**:
```bash
# /etc/cron.d/signupflow-restore-test
0 4 1 * * ubuntu /home/ubuntu/SignUpFlow/scripts/test-restore.sh >> /var/log/signupflow-restore-test.log 2>&1
```

---

## Disaster Recovery Scenarios

### Scenario 1: Accidental Data Deletion

**Situation**: Admin accidentally deletes critical data (e.g., all events for an organization)

**Recovery Steps**:
```bash
# 1. Identify last known good backup (before deletion)
aws s3 ls s3://signupflow-backups/production/daily/ | grep "2025-10-23"

# 2. Restore to staging for verification
scripts/restore-database.sh --environment staging \
  s3://signupflow-backups/production/daily/backup-20251023-020000.dump

# 3. Verify data is present in staging
psql $STAGING_DATABASE_URL -c "SELECT COUNT(*) FROM events WHERE org_id='org_123';"

# 4. Extract specific data from backup
pg_restore --data-only --table=events backup-20251023-020000.dump > events.sql

# 5. Import into production (selective restore)
psql $PRODUCTION_DATABASE_URL < events.sql
```

**Recovery Time**: 15-30 minutes

### Scenario 2: Complete Database Failure

**Situation**: PostgreSQL instance becomes completely unavailable (hardware failure, corruption)

**Recovery Steps**:
```bash
# 1. Provision new PostgreSQL instance (or use backup replica)
# (Manual step via cloud provider console)

# 2. Download latest backup from S3
scripts/restore-database.sh --force --environment production \
  s3://signupflow-backups/production/daily/backup-20251023-020000.dump

# 3. Update DATABASE_URL environment variable
export DATABASE_URL="postgresql://new-db-host:5432/signupflow_production"

# 4. Restart application
docker-compose -f docker-compose.prod.yml restart api

# 5. Verify health check
curl https://api.signupflow.io/health
```

**Recovery Time**: 30-60 minutes (depends on database size and S3 download speed)

### Scenario 3: Regional Outage (Complete Infrastructure Loss)

**Situation**: Entire AWS region becomes unavailable (rare but possible)

**Recovery Steps**:
1. Provision new infrastructure in different region (VPS, database, load balancer)
2. Download latest backup from S3 (S3 is multi-region redundant)
3. Restore database to new PostgreSQL instance
4. Deploy application containers to new VPS
5. Update DNS to point to new region
6. Verify application health

**Recovery Time**: 2-4 hours (infrastructure provisioning + restore)

---

## Backup Monitoring and Alerts

### Monitoring Requirements

Track the following backup metrics:

| Metric | Alert Threshold | Action |
|--------|----------------|--------|
| **Backup Success Rate** | <100% (any failure) | Immediate alert to DevOps |
| **Backup Duration** | >60 minutes | Investigate performance |
| **Backup Size Growth** | >50% increase in 7 days | Investigate data growth |
| **S3 Upload Failure** | Any failure | Retry + alert |
| **Last Successful Backup** | >25 hours ago | Critical alert |
| **Restore Test Success** | <100% (any failure) | Critical alert + manual restore test |

### Alert Integration

**Slack Notifications** (sent to #infrastructure channel):
```json
{
  "text": "❌ Database backup failed",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Database Backup Failed*\n\nEnvironment: production\nError: Database connection timeout\nTime: 2025-10-23 02:00:15 UTC\n\n*Action Required*: Investigate database connectivity"
      }
    }
  ]
}
```

**Email Alerts** (to DevOps team):
- Critical: Backup failure (immediate)
- Warning: Backup duration >60 minutes (daily digest)
- Info: Backup successful (weekly summary)

---

## Security Requirements

### Backup Encryption

**Encryption at Rest**: All backups encrypted using AES-256 encryption

**S3 Server-Side Encryption**:
```bash
# Enable SSE-S3 (AWS-managed keys)
aws s3api put-bucket-encryption --bucket signupflow-backups --server-side-encryption-configuration '{
  "Rules": [{
    "ApplyServerSideEncryptionByDefault": {
      "SSEAlgorithm": "AES256"
    }
  }]
}'
```

**Encryption in Transit**:
- S3 uploads via HTTPS only (TLS 1.2+)
- Database connections via SSL/TLS

### Access Control

**S3 Bucket Policy** (principle of least privilege):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBackupScriptWrite",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/signupflow-backup-role"
      },
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::signupflow-backups/production/*"
    },
    {
      "Sid": "AllowRestoreScriptRead",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/signupflow-restore-role"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::signupflow-backups/production/*",
        "arn:aws:s3:::signupflow-backups"
      ]
    },
    {
      "Sid": "DenyUnencryptedUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::signupflow-backups/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

### Audit Logging

**Backup Audit Log** (`/var/log/signupflow-backup-audit.log`):
```
[2025-10-23 02:00:15] INFO Backup started (user: ubuntu, pid: 12345)
[2025-10-23 02:05:42] INFO Backup completed (duration: 5m 27s, size: 1.2GB)
[2025-10-23 02:08:13] INFO S3 upload completed (location: s3://signupflow-backups/production/daily/backup-20251023-020000.dump)
[2025-10-23 02:08:14] INFO Backup verification successful (checksum: abc123def456)
```

**Restore Audit Log** (`/var/log/signupflow-restore-audit.log`):
```
[2025-10-23 15:10:12] WARNING Restore initiated (user: ubuntu, backup: backup-20251023-020000.dump, target: staging)
[2025-10-23 15:29:45] INFO Restore completed (duration: 19m 33s)
[2025-10-23 15:31:45] INFO Data integrity verification successful
```

---

## Testing Requirements

### Unit Tests

```bash
# tests/unit/test_backup_restore.py
def test_backup_script_creates_file():
    """Test backup script creates valid backup file."""
    result = subprocess.run(
        ["bash", "scripts/backup-database.sh", "--local-only"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert os.path.exists("/tmp/signupflow-backup-*.dump")

def test_restore_script_validates_backup():
    """Test restore script validates backup before restoring."""
    result = subprocess.run(
        ["bash", "scripts/restore-database.sh", "--verify", "/tmp/backup.dump"],
        capture_output=True,
        text=True
    )
    assert "Backup verification successful" in result.stdout
```

### Integration Tests

```bash
# tests/integration/test_backup_restore.py
def test_backup_and_restore_round_trip(db):
    """Test backup and restore preserve data integrity."""
    # Insert test data
    db.execute("INSERT INTO events (title) VALUES ('Test Event')")
    original_count = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    # Create backup
    subprocess.run(["bash", "scripts/backup-database.sh", "--local-only"])

    # Delete data
    db.execute("DELETE FROM events WHERE title='Test Event'")

    # Restore from backup
    subprocess.run(["bash", "scripts/restore-database.sh", "--force", "/tmp/backup.dump"])

    # Verify data restored
    restored_count = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert restored_count == original_count
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-23 | Initial backup and restore interface specification |

---

**Contract Status**: Draft - Ready for Implementation
**Dependencies**: None (foundational contract)
**Dependent Systems**: Cron/systemd (automation), S3 (storage), PostgreSQL (database)
