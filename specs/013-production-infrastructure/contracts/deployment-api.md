# Contract: CI/CD Deployment Interface

**Feature**: Production Infrastructure Deployment (013)
**Contract Type**: Deployment Automation Interface
**Version**: 1.0
**Status**: Draft

---

## Overview

The CI/CD deployment interface defines the automation contract between source code changes and production deployment. This contract specifies how GitHub Actions workflows orchestrate testing, building, and deploying the SignUpFlow application across environments (staging, production).

**Purpose**: Establish standardized, repeatable, and automated deployment processes with safety gates and rollback capabilities.

---

## Deployment Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Code Commit to main branch                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: Testing (Parallel Execution)                           │
│  ──────────────────────────────────────────────────────────     │
│  • Unit Tests (Python 3.11)           → 2 minutes               │
│  • Integration Tests (PostgreSQL)     → 3 minutes               │
│  • E2E Tests (Playwright + Chrome)    → 4 minutes               │
│  • Frontend Tests (Jest + Node 18)    → 2 minutes               │
│                                                                  │
│  Duration: 4 minutes (parallel), 11 minutes (sequential)        │
│  Gate: ALL tests must pass                                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 2: Container Build                                        │
│  ──────────────────────────────────────────────────────────     │
│  • Build backend container image      → 2 minutes               │
│  • Tag with commit SHA and version                              │
│  • Push to container registry                                   │
│                                                                  │
│  Duration: 2 minutes                                             │
│  Gate: Container build must succeed                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 3: Deploy to Staging (Automated)                          │
│  ──────────────────────────────────────────────────────────     │
│  • Pull container image from registry                           │
│  • Update docker-compose.staging.yml                            │
│  • Rolling update (zero-downtime)                               │
│  • Verify health check returns 200                              │
│  • Notify Slack: "Staging deployed, ready for production"      │
│                                                                  │
│  Duration: 3 minutes                                             │
│  Gate: Health check must pass                                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  🛑 MANUAL APPROVAL GATE 🛑                                      │
│  ──────────────────────────────────────────────────────────     │
│  DevOps Engineer Reviews:                                        │
│  • Staging environment smoke testing                            │
│  • Recent commits and change scope                              │
│  • Production traffic patterns                                  │
│                                                                  │
│  Actions:                                                        │
│  ✅ Approve: Continue to production deployment                  │
│  ❌ Reject: Stop pipeline, rollback staging if needed           │
│                                                                  │
│  Approval Timeout: 24 hours (auto-reject if not approved)       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼ (Only if approved)
┌─────────────────────────────────────────────────────────────────┐
│  Phase 4: Deploy to Production (Manual Trigger)                 │
│  ──────────────────────────────────────────────────────────     │
│  • Pull container image (same as staging)                       │
│  • Update docker-compose.prod.yml                               │
│  • Rolling update (zero-downtime, 2-instance deployment)        │
│  • Verify health check returns 200                              │
│  • Smoke tests: curl /health, /api/auth/health                 │
│  • Monitor error rates for 5 minutes                            │
│                                                                  │
│  Auto-Rollback Triggers:                                         │
│  • Health check fails 3 consecutive times                       │
│  • Error rate >5% for 2 minutes                                 │
│  • Manual rollback button clicked                               │
│                                                                  │
│  Duration: 5 minutes deployment + 5 minutes monitoring          │
│  Gate: Health checks + error rate thresholds                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 5: Post-Deployment Verification                           │
│  ──────────────────────────────────────────────────────────     │
│  • Tag Git commit with production deployment timestamp         │
│  • Update deployment dashboard (deployment #123, v1.2.0)       │
│  • Notify Slack: "Production deployed successfully (v1.2.0)"   │
│  • Create deployment record for audit log                       │
│                                                                  │
│  Duration: 1 minute                                              │
└─────────────────────────────────────────────────────────────────┘

Total Duration:
- Staging deployment: 9 minutes (commit to staging live)
- Production deployment: 10 minutes (approval to production live)
- Total: ~30 minutes (commit to production, with approval wait)
```

---

## GitHub Actions Workflows

### Workflow 1: ci.yml (Continuous Integration)

**Trigger**: Push to any branch

**Purpose**: Run all tests and build containers for every code change

**Configuration**:
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: ['**']
  pull_request:
    branches: [main]

jobs:
  test:
    strategy:
      matrix:
        test-type: [unit, integration, e2e, frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run ${{ matrix.test-type }} tests
        run: |
          case "${{ matrix.test-type }}" in
            unit)
              poetry run pytest tests/unit/ -v --tb=short
              ;;
            integration)
              poetry run pytest tests/integration/ -v --tb=short
              ;;
            e2e)
              poetry run pytest tests/e2e/ -v --tb=short
              ;;
            frontend)
              npm test -- --coverage
              ;;
          esac

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build container image
        run: |
          docker build -t signupflow-api:${{ github.sha }} .

      - name: Push to registry
        run: |
          echo "${{ secrets.REGISTRY_TOKEN }}" | docker login -u "${{ secrets.REGISTRY_USER }}" --password-stdin
          docker push signupflow-api:${{ github.sha }}
```

**Outputs**:
- Test results (JUnit XML format)
- Container image tagged with commit SHA
- Build artifacts (logs, coverage reports)

---

### Workflow 2: deploy-staging.yml

**Trigger**: Push to `main` branch (automatically after CI passes)

**Purpose**: Automatically deploy to staging environment for testing

**Configuration**:
```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [main]
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.signupflow.io

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to staging
        env:
          SSH_PRIVATE_KEY: ${{ secrets.STAGING_SSH_KEY }}
          STAGING_HOST: staging.signupflow.io
        run: |
          # Copy deployment script to staging server
          scp scripts/deploy.sh ubuntu@$STAGING_HOST:/tmp/

          # Execute deployment
          ssh ubuntu@$STAGING_HOST "bash /tmp/deploy.sh staging ${{ github.sha }}"

      - name: Verify health check
        run: |
          sleep 30  # Wait for deployment to complete
          curl --fail https://staging.signupflow.io/health || exit 1

      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ Staging deployed: v${{ github.sha }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Staging Deployment Successful*\n\nCommit: `${{ github.sha }}`\nBranch: `main`\nAuthor: ${{ github.actor }}\n\n<https://staging.signupflow.io|View Staging Environment>\n\n*Ready for production approval* 🚀"
                  }
                }
              ]
            }
```

**Outputs**:
- Staging deployment status (success/failure)
- Health check verification result
- Slack notification to #deployments channel

---

### Workflow 3: deploy-production.yml

**Trigger**: Manual approval (workflow_dispatch) after staging deployment

**Purpose**: Deploy to production with manual safety gate

**Configuration**:
```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  workflow_dispatch:
    inputs:
      commit_sha:
        description: 'Commit SHA to deploy (from staging)'
        required: true
        type: string

jobs:
  approve:
    runs-on: ubuntu-latest
    environment:
      name: production
      # Requires approval from DevOps team
    steps:
      - name: Manual Approval Gate
        run: echo "Deploying ${{ inputs.commit_sha }} to production"

  deploy:
    needs: approve
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://api.signupflow.io

    steps:
      - uses: actions/checkout@v3
        with:
          ref: ${{ inputs.commit_sha }}

      - name: Deploy to production
        env:
          SSH_PRIVATE_KEY: ${{ secrets.PRODUCTION_SSH_KEY }}
          PRODUCTION_HOST: api.signupflow.io
        run: |
          # Execute rolling deployment
          scp scripts/deploy.sh ubuntu@$PRODUCTION_HOST:/tmp/
          ssh ubuntu@$PRODUCTION_HOST "bash /tmp/deploy.sh production ${{ inputs.commit_sha }}"

      - name: Verify health check
        run: |
          sleep 30
          for i in {1..5}; do
            curl --fail https://api.signupflow.io/health && break
            echo "Retry $i/5..."
            sleep 10
          done

      - name: Monitor error rates
        run: |
          # Check error rate for 5 minutes
          for i in {1..10}; do
            error_rate=$(curl -s https://api.signupflow.io/metrics | jq '.error_rate')
            if (( $(echo "$error_rate > 0.05" | bc -l) )); then
              echo "❌ Error rate too high: $error_rate (>5%)"
              exit 1
            fi
            sleep 30
          done

      - name: Rollback on failure
        if: failure()
        run: |
          echo "🔴 Deployment failed, rolling back..."
          ssh ubuntu@$PRODUCTION_HOST "bash /tmp/deploy.sh rollback"
          exit 1

      - name: Tag release
        if: success()
        run: |
          git tag -a "prod-${{ github.sha }}" -m "Production deployment $(date)"
          git push origin "prod-${{ github.sha }}"

      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "🎉 Production deployed: v${{ inputs.commit_sha }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Production Deployment Successful* 🚀\n\nCommit: `${{ inputs.commit_sha }}`\nDeployed by: ${{ github.actor }}\nTime: $(date)\n\n<https://api.signupflow.io|View Production Environment>"
                  }
                }
              ]
            }
```

**Outputs**:
- Production deployment status (success/failure/rolled back)
- Git tag for production release
- Slack notification to #deployments channel

---

## Deployment Script Interface

### scripts/deploy.sh

**Purpose**: Standardized deployment script executed on target server via SSH

**Interface**:
```bash
bash deploy.sh <environment> <commit_sha> [rollback]

Arguments:
  environment   - Target environment: staging, production
  commit_sha    - Git commit SHA to deploy (container image tag)
  rollback      - Optional: rollback to previous version

Examples:
  bash deploy.sh staging abc123def456
  bash deploy.sh production abc123def456
  bash deploy.sh production rollback
```

**Functionality**:
1. Pull container image from registry (tagged with commit SHA)
2. Update docker-compose.<environment>.yml with new image tag
3. Execute rolling update (docker-compose up -d)
4. Verify health check passes
5. Monitor for errors (5-minute observation period)
6. Rollback if health check fails or error rate exceeds threshold

**Exit Codes**:
- `0` - Deployment successful
- `1` - Deployment failed (health check failure)
- `2` - Configuration error (missing environment variables)
- `3` - Container registry authentication failure

---

## Environment Configuration

### Staging Environment

**Server**: staging.signupflow.io
**Instances**: 1 (single instance for cost efficiency)
**Database**: Managed PostgreSQL (staging database)
**Domain**: https://staging.signupflow.io
**Certificate**: Let's Encrypt (automatic renewal)
**Deployment Frequency**: Every commit to `main` (fully automated)

**Environment Variables**:
```bash
# /home/ubuntu/SignUpFlow/.env.staging
DATABASE_URL=postgresql://user:pass@staging-db.provider.com:5432/signupflow_staging
SECRET_KEY=<staging-secret>
ALLOWED_HOSTS=staging.signupflow.io
SENTRY_DSN=<sentry-staging-dsn>
ENVIRONMENT=staging
```

### Production Environment

**Server**: api.signupflow.io
**Instances**: 2 (load balanced for high availability)
**Database**: Managed PostgreSQL (production database)
**Domain**: https://api.signupflow.io
**Certificate**: Let's Encrypt (automatic renewal)
**Deployment Frequency**: Manual approval after staging validation

**Environment Variables**:
```bash
# /home/ubuntu/SignUpFlow/.env.production
DATABASE_URL=postgresql://user:pass@prod-db.provider.com:5432/signupflow_production
SECRET_KEY=<production-secret>
ALLOWED_HOSTS=api.signupflow.io,signupflow.io
SENTRY_DSN=<sentry-production-dsn>
ENVIRONMENT=production
```

---

## Rollback Procedures

### Automatic Rollback Triggers

Production deployment automatically rolls back if:

1. **Health check failure**: `/health` endpoint returns HTTP 503 for 3 consecutive checks (90 seconds)
2. **Error rate spike**: Application error rate >5% for 2 minutes (120 seconds)
3. **Database connectivity loss**: Database connection fails for >1 minute
4. **Manual rollback**: DevOps engineer clicks "Rollback" button in GitHub Actions

### Manual Rollback Process

```bash
# SSH into production server
ssh ubuntu@api.signupflow.io

# Execute rollback script
bash /tmp/deploy.sh production rollback

# Verify previous version restored
curl https://api.signupflow.io/health
```

**Rollback Duration**: <5 minutes (revert to previous container image)

**Rollback Verification**:
- Health check returns HTTP 200
- Error rate returns to baseline (<1%)
- Application version matches previous deployment

---

## Security Requirements

### Secrets Management

**Required Secrets** (stored in GitHub Secrets):
- `REGISTRY_USER` - Container registry username
- `REGISTRY_TOKEN` - Container registry authentication token
- `STAGING_SSH_KEY` - SSH private key for staging server access
- `PRODUCTION_SSH_KEY` - SSH private key for production server access
- `SLACK_WEBHOOK_URL` - Slack notifications webhook
- `SENTRY_AUTH_TOKEN` - Sentry deployment tracking token

**Secret Rotation**:
- SSH keys: Rotate every 90 days
- Registry tokens: Rotate every 180 days
- Webhook URLs: Rotate on security incident

### Access Control

**Production Deployment Approval**:
- Required: 1 approval from DevOps team
- Timeout: 24 hours (auto-reject if not approved)
- Audit log: All approvals/rejections logged

**GitHub Actions Environments**:
- `staging` - No approval required, auto-deploy
- `production` - Manual approval required from DevOps team

---

## Monitoring and Observability

### Deployment Metrics

Track the following deployment metrics:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Deployment Frequency** | 1-5 per week | GitHub Actions workflow runs |
| **Lead Time (Commit to Production)** | <30 minutes | Time from commit to production live |
| **Deployment Success Rate** | >95% | Successful deployments / total attempts |
| **Mean Time to Recovery (MTTR)** | <15 minutes | Time to rollback on failure |
| **Change Failure Rate** | <5% | Failed deployments / total deployments |

### Deployment Notifications

**Slack Notifications** (sent to #deployments channel):
- ✅ Staging deployment successful
- ⏳ Production approval pending
- 🚀 Production deployment successful
- 🔴 Deployment failed + rollback initiated
- ⚠️ Manual rollback triggered

---

## Testing Requirements

### Integration Tests

```bash
# tests/integration/test_deployment.py
def test_deployment_script_staging():
    """Test deployment script executes successfully for staging."""
    result = subprocess.run(
        ["bash", "scripts/deploy.sh", "staging", "abc123"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Deployment successful" in result.stdout

def test_deployment_rollback():
    """Test rollback restores previous version."""
    # Deploy version 1
    deploy("abc123")

    # Deploy version 2
    deploy("def456")

    # Rollback
    rollback()

    # Verify version 1 restored
    response = requests.get("https://staging.signupflow.io/health")
    assert response.json()["version"] == "1.0.0"
```

### E2E Tests

```bash
# tests/e2e/test_cicd_pipeline.py
def test_automated_staging_deployment():
    """Test that pushing to main triggers automated staging deployment."""
    # Push commit to main
    git_push("main", "Test commit")

    # Wait for CI/CD pipeline
    time.sleep(600)  # 10 minutes

    # Verify staging deployment
    response = requests.get("https://staging.signupflow.io/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-23 | Initial CI/CD deployment interface specification |

---

**Contract Status**: Draft - Ready for Implementation
**Dependencies**: health-check.md (health check endpoint contract)
**Dependent Systems**: GitHub Actions, Docker, Traefik, Slack notifications
