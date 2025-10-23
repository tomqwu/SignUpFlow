# Research: Production Infrastructure & Deployment

**Feature Branch**: `003-production-infrastructure`
**Date**: 2025-10-20
**Phase**: 0 (Research - Resolving NEEDS CLARIFICATION items)

## Overview

This document resolves all "NEEDS CLARIFICATION" items from the Technical Context section of [plan.md](./plan.md) by researching production deployment options, best practices, and technical requirements for SignUpFlow's infrastructure.

## NEEDS CLARIFICATION Items

### 1. Cloud Provider Selection

**Question**: Which cloud provider should SignUpFlow deploy to (AWS, GCP, Azure, DigitalOcean)?

**Research**:

**Option A: DigitalOcean (RECOMMENDED)**
- **Pros**:
  - Simple, developer-friendly managed services
  - App Platform provides managed containers with zero-downtime deployments
  - Managed PostgreSQL with automated backups (point-in-time recovery)
  - Managed Spaces (S3-compatible) for backup storage
  - Cost-effective for small-to-medium scale ($12-50/month initially)
  - Built-in load balancer with health checks
  - GitHub Actions integration via doctl CLI
  - Strong documentation for Docker deployments
- **Cons**:
  - Limited geographic regions compared to AWS/GCP/Azure
  - Fewer advanced features (no Lambda equivalent, basic monitoring)
  - Smaller ecosystem

**Option B: AWS ECS Fargate**
- **Pros**:
  - Industry standard, extensive documentation
  - Serverless containers (no EC2 management)
  - Robust ecosystem (RDS PostgreSQL, S3, CloudWatch, Secrets Manager)
  - Global regions, enterprise features
- **Cons**:
  - Higher complexity (VPC, security groups, IAM roles, ECS task definitions)
  - Higher cost ($50-200/month initially)
  - Steeper learning curve

**Option C: Google Cloud Run**
- **Pros**:
  - Fully managed serverless containers
  - Pay-per-request pricing (cost-effective for low traffic)
  - Simple deployment (gcloud run deploy)
  - Cloud SQL for PostgreSQL with automated backups
- **Cons**:
  - Less mature than AWS for production workloads
  - Limited customization compared to AWS
  - Vendor lock-in to Google Cloud

**Decision**: **DigitalOcean App Platform (RECOMMENDED)**

**Rationale**:
- SignUpFlow is a startup/small business application optimizing for rapid launch
- Managed services reduce operational complexity (no Kubernetes, no VPC management)
- Cost-effective pricing matches target customer segment (churches, non-profits)
- Built-in features (load balancing, SSL, health checks, zero-downtime deployments) align with requirements
- Can migrate to AWS/GCP later if scaling demands increase

---

### 2. Container Orchestration Platform

**Question**: What container orchestration platform should be used (Docker Compose, Cloud Run, ECS Fargate, Kubernetes)?

**Research**:

**Option A: Docker Compose + Cloud VM (NOT RECOMMENDED)**
- **Pros**: Simple, familiar, low cost
- **Cons**: Manual scaling, no zero-downtime deployments, single point of failure

**Option B: DigitalOcean App Platform (RECOMMENDED)**
- **Pros**:
  - Managed platform handling orchestration, scaling, health checks automatically
  - Zero-downtime deployments built-in
  - Git-based deployment workflow (push to main → auto-deploy)
  - Integrated load balancer with horizontal scaling
  - No orchestration complexity (no YAML manifests, no cluster management)
- **Cons**:
  - Platform-specific (not portable to other clouds without re-architecting)

**Option C: Kubernetes (EKS, GKE, DOKS)**
- **Pros**: Industry standard, portable, advanced features
- **Cons**: **Massive overkill** for SignUpFlow's scale (100s of users, not 100,000s)
  - Requires: cluster setup, Helm charts, ingress controllers, persistent volumes, service mesh
  - 10x operational complexity vs managed platform
  - Higher cost ($70+ per month for control plane alone)

**Decision**: **DigitalOcean App Platform (RECOMMENDED)**

**Rationale**:
- Spec explicitly states "Container orchestration: Kubernetes or advanced orchestration platforms not required"
- Managed platform provides all required features (zero-downtime, scaling, health checks) without orchestration overhead
- Kubernetes is premature optimization for SignUpFlow's current scale
- Simple deployment workflow enables rapid iteration

---

### 3. Log Aggregation Service

**Question**: Which centralized logging service should be used (CloudWatch, Stackdriver, Papertrail)?

**Research**:

**Option A: DigitalOcean Monitoring + Papertrail (RECOMMENDED)**
- **Pros**:
  - DigitalOcean App Platform auto-forwards logs to built-in monitoring
  - Papertrail integration for advanced search (free tier: 50MB/day, 7-day retention)
  - Upgrade path to paid Papertrail for longer retention (90 days)
  - Simple webhook integration for log forwarding
- **Cons**:
  - Basic features compared to ELK stack or Datadog

**Option B: Cloud Provider Native (CloudWatch, Cloud Logging)**
- **Pros**: Deep integration with cloud provider
- **Cons**: Vendor lock-in, additional cost, complexity

**Option C: Self-Hosted ELK Stack (Elasticsearch, Logstash, Kibana)**
- **Pros**: Full control, powerful search
- **Cons**: **Massive operational overhead** - adds entire stack to manage

**Decision**: **DigitalOcean Monitoring + Papertrail free tier (RECOMMENDED)**

**Rationale**:
- Spec states "Basic logging to stdout works initially while centralized solution is implemented"
- DigitalOcean App Platform provides built-in log aggregation (60-second forwarding requirement met)
- Papertrail free tier sufficient for initial launch (7-day retention meets troubleshooting needs)
- Upgrade to paid Papertrail ($7/month) when 90-day retention needed for compliance
- Avoid operational complexity of self-hosted logging

---

### 4. Secrets Management Approach

**Question**: Environment variables vs dedicated secrets management service (Vault, AWS Secrets Manager)?

**Research**:

**Option A: Environment Variables (RECOMMENDED for initial launch)**
- **Pros**:
  - Simple configuration via cloud provider UI or CLI
  - DigitalOcean App Platform encrypts environment variables at rest
  - No additional service to manage or pay for
  - Meets security requirements for non-regulated industries
- **Cons**:
  - No secret rotation automation
  - No fine-grained access control
  - Not suitable for highly regulated industries (healthcare, finance)

**Option B: HashiCorp Vault**
- **Pros**: Advanced features (secret rotation, audit logs, dynamic secrets)
- **Cons**: Self-hosted operational complexity, overkill for initial launch

**Option C: Cloud Provider Secrets Manager (AWS, GCP)**
- **Pros**: Managed service, secret rotation, audit logs
- **Cons**: Additional cost ($0.40 per secret per month), vendor lock-in

**Decision**: **Environment Variables (RECOMMENDED for initial launch)**

**Upgrade Path**: Migrate to secrets manager if:
- Onboarding regulated customers (HIPAA, SOC 2 Type II)
- Managing >20 secrets requiring frequent rotation
- Multiple developers need different secret access levels

**Rationale**:
- Spec states "Environment variables sufficient for initial secrets"
- DigitalOcean App Platform provides encrypted environment variable storage
- Simpler alternative rejected: Hardcoding secrets in code (security violation)
- Cost-benefit: $0 vs $5-10/month for secrets manager (unnecessary initially)

---

### 5. Backup Storage Destination

**Question**: Where should database backups be stored (S3, GCS, Azure Blob, DigitalOcean Spaces)?

**Research**:

**Option A: DigitalOcean Spaces (RECOMMENDED)**
- **Pros**:
  - S3-compatible API (use AWS SDK/boto3)
  - Low cost ($5/month for 250GB storage, $0.02/GB transfer)
  - Built-in encryption at rest
  - Integrated with DigitalOcean ecosystem
  - Cross-region replication available
- **Cons**:
  - Vendor lock-in (but S3 API compatibility enables migration)

**Option B: AWS S3**
- **Pros**: Industry standard, feature-rich, global availability
- **Cons**: Higher cost for small workloads, cross-cloud networking complexity

**Decision**: **DigitalOcean Spaces (RECOMMENDED)**

**Backup Strategy**:
- Daily automated backups via cron job: `pg_dump` → encrypt with GPG → upload to Spaces
- Retention: 30 daily backups, 12 monthly archives
- Encryption: AES-256 via GPG with key stored in environment variables
- Testing: Monthly restore drill to staging environment

**Rationale**:
- Meets FR-031 requirement: "Encrypt database backups at rest using AES-256"
- Meets FR-032 requirement: "Retain daily backups for 30 days and monthly backups for 12 months"
- Cost-effective for SignUpFlow's data volume (estimated <5GB initially)

---

### 6. Container Registry

**Question**: Which container registry should be used (Docker Hub, GitHub Container Registry, private registry)?

**Research**:

**Option A: GitHub Container Registry (ghcr.io) (RECOMMENDED)**
- **Pros**:
  - **Free** for public and private repositories
  - Native GitHub Actions integration (no separate credentials)
  - Unlimited bandwidth and storage for public images
  - Private images: 500MB storage + 1GB bandwidth free (sufficient for SignUpFlow)
  - Built-in security scanning
  - Tight integration with GitHub workflow
- **Cons**:
  - GitHub vendor lock-in

**Option B: Docker Hub**
- **Pros**: Industry standard, public image hosting
- **Cons**: Rate limiting (100 pulls per 6 hours for unauthenticated), paid tier required for private images

**Option C: DigitalOcean Container Registry**
- **Pros**: Integrated with DigitalOcean, no egress charges
- **Cons**: Costs $5/month (unnecessary when GitHub provides free alternative)

**Decision**: **GitHub Container Registry (ghcr.io) (RECOMMENDED)**

**Rationale**:
- SignUpFlow already uses GitHub for code hosting
- GitHub Actions CI/CD pipeline natively integrates with ghcr.io
- Zero additional cost (free tier sufficient for private images <500MB)
- Simpler alternative rejected: Docker Hub (rate limiting issues, paid tier required)

---

### 7. Infrastructure Testing Approach

**Question**: How should infrastructure be tested (Testinfra, ServerSpec, manual testing)?

**Research**:

**Option A: Pytest + Docker + subprocess (RECOMMENDED)**
- **Approach**:
  - E2E tests simulate operational workflows using pytest
  - Spin up Docker containers locally for testing deployment scenarios
  - Use subprocess to run deployment scripts and verify outcomes
  - Test health checks, database migrations, graceful shutdown directly
- **Example Test Flow**:
  ```python
  def test_health_check_endpoint():
      # Start Docker container
      subprocess.run(["docker-compose", "up", "-d"])
      # Wait for container ready
      time.sleep(5)
      # Call health endpoint
      response = requests.get("http://localhost:8000/health")
      assert response.status_code == 200
      assert response.json()["status"] == "healthy"
      # Cleanup
      subprocess.run(["docker-compose", "down"])
  ```
- **Pros**:
  - Reuses existing pytest test infrastructure
  - Tests infrastructure in local development environment
  - Fast feedback loop
  - No additional tools or dependencies
- **Cons**:
  - Local Docker testing may differ from production cloud environment

**Option B: Testinfra (SSH-based infrastructure testing)**
- **Pros**: Tests actual production-like VMs via SSH
- **Cons**: **Unnecessary complexity** - SignUpFlow uses managed containers, not VMs

**Option C: Manual Testing Checklist**
- **Pros**: Simple, no code required
- **Cons**: **Violates Constitution Principle 1** - "E2E tests mandatory for all features"

**Decision**: **Pytest + Docker + subprocess (RECOMMENDED)**

**Rationale**:
- Aligns with Constitution Principle 1 (E2E testing mandatory)
- Reuses existing pytest infrastructure (no new test framework)
- Tests verify "what operations team EXPERIENCES" (deployment works, SSL configured, backups restorable)
- Local Docker testing sufficient for initial launch (cloud-specific testing deferred)

---

### 8. Hosting Environment Specifics

**Question**: Managed container service vs VM-based vs serverless containers?

**Research**:

**Option A: DigitalOcean App Platform (Managed Container Service) (RECOMMENDED)**
- **Architecture**:
  - Platform-as-a-Service (PaaS) abstracting infrastructure management
  - Containers deployed from GitHub repository or container registry
  - Managed load balancer with automatic SSL (Let's Encrypt)
  - Managed PostgreSQL database (separate service)
  - Managed Redis (separate service for sessions)
  - Auto-scaling based on CPU/memory thresholds
- **Deployment Flow**:
  1. Push code to GitHub main branch
  2. GitHub Actions builds Docker image → pushes to ghcr.io
  3. DigitalOcean App Platform pulls image from ghcr.io
  4. Runs database migrations (Alembic)
  5. Performs rolling deployment (blue-green style)
  6. Health checks verify new instances before routing traffic
- **Pros**:
  - Zero-downtime deployments built-in (rolling restart)
  - Automatic SSL certificate management (Let's Encrypt)
  - Integrated load balancer
  - Horizontal scaling with simple UI/API
  - Managed database backups (automated daily)
  - No server management (patching, OS updates handled by platform)
- **Cons**:
  - Platform lock-in (not directly portable to AWS without re-architecting)

**Option B: VM-Based (Droplets + Docker Compose)**
- **Pros**: Full control, lower monthly cost ($6-12/month)
- **Cons**: **Manual operational burden** - no zero-downtime deployments, manual scaling, single point of failure

**Option C: Serverless Containers (Google Cloud Run, AWS Fargate)**
- **Pros**: Pay-per-request pricing, automatic scaling to zero
- **Cons**: Cold start latency (200-500ms), higher complexity

**Decision**: **DigitalOcean App Platform (RECOMMENDED)**

**Rationale**:
- Meets all FR requirements: zero-downtime deployments, horizontal scaling, automated SSL
- Managed services reduce operational complexity (no server patching, no manual scaling)
- Built-in features align perfectly with spec requirements:
  - FR-004: Rolling deployments ✅
  - FR-005: Automatic rollback on health check failure ✅
  - FR-017-023: Let's Encrypt SSL automation ✅
  - FR-044-049: Horizontal scaling and load balancing ✅
- Cost-effective for initial launch ($30-70/month for app + database + Redis)

---

## Recommended Technology Stack Summary

Based on research above, the complete production infrastructure stack:

### Core Infrastructure

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Cloud Provider** | DigitalOcean | Simple managed services, cost-effective, rapid launch |
| **Container Platform** | DigitalOcean App Platform | Zero-downtime deployments, auto-scaling, managed SSL |
| **Container Registry** | GitHub Container Registry (ghcr.io) | Free, native GitHub Actions integration |
| **Reverse Proxy** | DigitalOcean App Platform (built-in) | Managed Traefik-like functionality |
| **SSL Certificates** | Let's Encrypt (via App Platform) | Automatic provisioning and renewal |
| **Database** | DigitalOcean Managed PostgreSQL 14 | Automated backups, high availability option |
| **Session Storage** | DigitalOcean Managed Redis | Stateless scaling support |
| **Backup Storage** | DigitalOcean Spaces | S3-compatible, encrypted, cross-region replication |
| **Logging** | DigitalOcean Monitoring + Papertrail | Built-in aggregation, advanced search |
| **Secrets** | Environment Variables (encrypted) | Simple, secure for initial launch |
| **CI/CD** | GitHub Actions | Native integration, familiar workflow |

### Development Tools

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Local Development** | Docker Compose | PostgreSQL + Redis locally |
| **Database Migrations** | Alembic (existing) | Version-controlled schema changes |
| **Testing** | Pytest + Docker + subprocess | E2E infrastructure tests |
| **Monitoring** | Sentry (error tracking) + Uptime checks | Integration points from spec |

### Configuration

**Environment Variables (all environments)**:
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/signupflow
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis (sessions)
REDIS_URL=redis://host:6379/0

# Application
SECRET_KEY=<generated-secret>
ENVIRONMENT=production  # or staging, development
ALLOWED_HOSTS=signupflow.io,www.signupflow.io

# External Services
SENTRY_DSN=<sentry-project-dsn>

# Backup
BACKUP_ENCRYPTION_KEY=<gpg-key>
SPACES_ACCESS_KEY=<digitalocean-spaces-key>
SPACES_SECRET_KEY=<digitalocean-spaces-secret>
SPACES_BUCKET=signupflow-backups
```

**Docker Compose (local development)**:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://signupflow:password@db:5432/signupflow
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: signupflow
      POSTGRES_USER: signupflow
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## Deployment Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Internet (HTTPS)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────▼──────────────┐
         │   Let's Encrypt SSL        │
         │   (Auto-provisioned)       │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │  DigitalOcean Load Balancer │
         │  (Health checks enabled)    │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │  DigitalOcean App Platform  │
         │  (Managed Containers)       │
         │                             │
         │  ┌──────────┐ ┌──────────┐ │
         │  │ Instance 1│ │ Instance 2│ │
         │  │  FastAPI  │ │  FastAPI  │ │
         │  │  Uvicorn  │ │  Uvicorn  │ │
         │  └─────┬────┘ └─────┬────┘ │
         └────────┼────────────┼──────┘
                  │            │
      ┌───────────▼────────────▼───────────┐
      │                                     │
┌─────▼───────┐               ┌───────────▼─────┐
│  Managed    │               │  Managed         │
│  PostgreSQL │               │  Redis           │
│  (Primary)  │               │  (Sessions)      │
│             │               │                  │
│  - Automated│               │  - High Avail.   │
│    Backups  │               │  - Persistence   │
│  - Replicas │               │                  │
└──────┬──────┘               └──────────────────┘
       │
       │ (Backup every 24h)
       │
┌──────▼──────────────────┐
│  DigitalOcean Spaces    │
│  (Backup Storage)       │
│                         │
│  - AES-256 Encrypted    │
│  - 30-day retention     │
│  - 12-month archives    │
└─────────────────────────┘
```

---

## Migration Path from Current State

**Current State**: SignUpFlow runs locally with SQLite, no production deployment

**Phase 1: Local PostgreSQL Development** (Week 1)
1. Add Docker Compose with PostgreSQL and Redis
2. Update `api/database.py` with PostgreSQL connection pooling
3. Test all existing features with PostgreSQL locally
4. Create Alembic migration for SQLite → PostgreSQL schema

**Phase 2: Dockerization** (Week 1-2)
1. Create `Dockerfile` for application container
2. Test Docker build and run locally
3. Ensure health check endpoint works (`/health`)
4. Add graceful shutdown handling

**Phase 3: DigitalOcean Setup** (Week 2)
1. Create DigitalOcean account and project
2. Provision Managed PostgreSQL database
3. Provision Managed Redis
4. Create DigitalOcean Space for backups
5. Configure environment variables in App Platform

**Phase 4: CI/CD Pipeline** (Week 2-3)
1. Create GitHub Actions workflow (`.github/workflows/deploy.yml`)
2. Build Docker image on push to main
3. Push image to GitHub Container Registry
4. Deploy to DigitalOcean App Platform
5. Run database migrations automatically
6. Perform health checks before routing traffic

**Phase 5: Production Cutover** (Week 3-4)
1. Migrate production data from SQLite to PostgreSQL
2. Configure custom domain and SSL
3. Enable monitoring and logging
4. Test backup and restore procedures
5. Document runbooks for operations team

---

## Cost Estimate (Monthly)

### DigitalOcean Services

| Service | Tier | Cost | Notes |
|---------|------|------|-------|
| App Platform | Basic (1GB RAM, 1 vCPU) | $12 | 2 instances = $24 |
| Managed PostgreSQL | Basic (1GB RAM, 10GB storage) | $15 | Includes automated backups |
| Managed Redis | Basic (1GB RAM) | $15 | Session storage |
| Spaces (Object Storage) | 250GB | $5 | Backup storage |
| Container Registry | N/A | $0 | Using GitHub Container Registry |
| Load Balancer | N/A | $0 | Included in App Platform |
| **Total** | | **$59/month** | Initial launch scale |

### Additional Services

| Service | Cost | Notes |
|---------|------|-------|
| GitHub Actions | $0 | 2,000 minutes/month free (sufficient) |
| Let's Encrypt SSL | $0 | Free automated SSL |
| Sentry (Error Tracking) | $0 | 5,000 events/month free tier |
| Papertrail (Logging) | $0 | 50MB/day free tier (upgrade $7/month for 90-day retention) |
| **Total Additional** | **$0-7/month** | |

**Grand Total**: $59-66/month for initial production launch

**Scaling Costs** (as usage grows):
- 100 organizations (~1,000 users): $59/month (current estimate)
- 500 organizations (~5,000 users): $120/month (4GB RAM, 2 vCPU instances)
- 1,000 organizations (~10,000 users): $240/month (8GB RAM, 4 vCPU instances)

---

## Open Questions for Implementation Phase

1. **Database Connection Pooling**: What pool size and max overflow? (Recommend: pool_size=20, max_overflow=10 based on expected concurrency)

2. **Health Check Endpoint Response**: What specific health metrics to include? (Recommend: database ping, Redis ping, version, uptime, memory usage)

3. **Backup Schedule**: What time to run daily backups? (Recommend: 2:00 AM UTC - lowest traffic window based on church/volunteer usage patterns)

4. **Monitoring Alerts**: What metrics to alert on? (Recommend: health check failures, deployment failures, database connection errors, SSL certificate expiration <7 days)

5. **Graceful Shutdown Timeout**: 30 seconds sufficient? (Recommend: yes - typical request completion <5 seconds, 30s buffer for solver operations)

---

## Next Steps

**Phase 0 Complete** - All NEEDS CLARIFICATION items resolved.

**Proceed to Phase 1** (Data Model & API Contracts):
1. Generate `data-model.md` with infrastructure entities (Deployment, HealthCheck, BackupJob)
2. Generate API contracts in `contracts/` directory (health check endpoint)
3. Create `quickstart.md` for developers (setup PostgreSQL locally, run Docker)
4. Update agent context file with infrastructure knowledge

**Ready for `/speckit.plan` Phase 1 execution**.
