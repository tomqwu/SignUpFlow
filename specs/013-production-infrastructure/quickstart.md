# Infrastructure Quickstart: 5-Minute Production Deployment

**Feature**: Production Infrastructure Deployment (013)
**Purpose**: Get SignUpFlow running in production in <10 minutes
**Audience**: DevOps engineers, system administrators

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **VPS or Cloud Server** (4-core, 8GB RAM, Ubuntu 22.04 LTS)
- [ ] **Domain Name** (e.g., `api.signupflow.io`)
- [ ] **Domain DNS Access** (to configure A records)
- [ ] **PostgreSQL Database** (managed service recommended: AWS RDS, DigitalOcean, Azure)
- [ ] **S3-Compatible Storage** (AWS S3, Backblaze B2, DigitalOcean Spaces)
- [ ] **SSH Access** to server
- [ ] **Docker** and **Docker Compose** installed on server
- [ ] **Git** installed on server

**Estimated Cost**: $69-140/month
- VPS: $50-80/month
- PostgreSQL: $15-50/month
- S3 Storage: $2-5/month
- Domain: $2-5/month

---

## Step 1: Server Preparation (2 minutes)

### 1.1 SSH into Server

```bash
ssh ubuntu@your-server-ip
```

### 1.2 Install Docker and Docker Compose

```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (avoid sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

### 1.3 Clone Repository

```bash
git clone https://github.com/tomqwu/signupflow.git
cd signupflow
```

---

## Step 2: Environment Configuration (3 minutes)

### 2.1 Create Production Environment File

```bash
cp .env.example .env.production
nano .env.production
```

### 2.2 Configure Environment Variables

```bash
# .env.production

# Application Configuration
ENVIRONMENT=production
SECRET_KEY=<generate-random-secret-key>  # openssl rand -hex 32
ALLOWED_HOSTS=api.signupflow.io,signupflow.io

# Database Configuration (from managed PostgreSQL provider)
DATABASE_URL=postgresql://username:password@db-host:5432/signupflow_production

# Email Configuration (optional - for future features)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>

# Monitoring (optional)
SENTRY_DSN=https://<key>@sentry.io/<project>

# Backup Configuration
S3_BUCKET=signupflow-backups
S3_REGION=us-east-1
S3_ACCESS_KEY=<aws-access-key>
S3_SECRET_KEY=<aws-secret-key>
```

**Generate Secret Key**:
```bash
openssl rand -hex 32
```

**Get Database URL** from managed PostgreSQL provider:
- **AWS RDS**: `postgresql://username:password@signupflow-db.xyz.rds.amazonaws.com:5432/signupflow`
- **DigitalOcean**: `postgresql://username:password@signupflow-db-do-user-xyz.db.ondigitalocean.com:25060/signupflow?sslmode=require`
- **Azure**: `postgresql://username:password@signupflow-db.postgres.database.azure.com:5432/signupflow`

---

## Step 3: Domain Configuration (2 minutes)

### 3.1 Point Domain to Server

Add A record in your domain registrar's DNS settings:

```
Type: A
Name: api
Value: your-server-ip
TTL: 300 (5 minutes)
```

**Example** (if your domain is `signupflow.io` and server IP is `203.0.113.42`):
```
api.signupflow.io → 203.0.113.42
```

### 3.2 Verify DNS Propagation

```bash
dig api.signupflow.io +short
# Should return: 203.0.113.42
```

**Wait**: DNS propagation takes 5-15 minutes (check with `dig` command)

---

## Step 4: Traefik Setup (1 minute)

### 4.1 Create Traefik Configuration

```bash
mkdir -p deploy/traefik
nano deploy/traefik/traefik.yml
```

```yaml
# deploy/traefik/traefik.yml

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true

  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: devops@signupflow.io  # Change to your email
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    exposedByDefault: false

api:
  dashboard: false  # Disable dashboard in production
```

### 4.2 Create Let's Encrypt Storage

```bash
mkdir -p deploy/traefik/letsencrypt
touch deploy/traefik/letsencrypt/acme.json
chmod 600 deploy/traefik/letsencrypt/acme.json
```

---

## Step 5: Docker Compose Production Configuration (2 minutes)

### 5.1 Create Production Compose File

```bash
nano docker-compose.prod.yml
```

```yaml
# docker-compose.prod.yml

version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    container_name: traefik
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./deploy/traefik/traefik.yml:/traefik.yml:ro
      - ./deploy/traefik/letsencrypt:/letsencrypt
    networks:
      - web

  api:
    image: signupflow-api:latest
    container_name: signupflow-api
    restart: unless-stopped
    env_file:
      - .env.production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.signupflow.io`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
      - "traefik.http.services.api.loadbalancer.server.port=8000"
    networks:
      - web

networks:
  web:
    external: false
```

---

## Step 6: Deploy Application (1 minute)

### 6.1 Build Container Image

```bash
docker build -t signupflow-api:latest .
```

### 6.2 Run Database Migrations

```bash
# Create database tables
docker run --rm \
  --env-file .env.production \
  signupflow-api:latest \
  python -c "from api.database import init_db; init_db()"
```

### 6.3 Start Services

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 6.4 Verify Health

```bash
# Wait for services to start (30 seconds)
sleep 30

# Check health endpoint
curl https://api.signupflow.io/health

# Expected output:
# {"status":"healthy","components":{"api":"healthy","database":"healthy"}}
```

---

## Step 7: Verify Deployment (1 minute)

### 7.1 Test HTTPS Certificate

```bash
curl -I https://api.signupflow.io/health

# Should see:
# HTTP/2 200
# certificate issued by Let's Encrypt
```

### 7.2 Test API Endpoints

```bash
# Test authentication endpoint
curl https://api.signupflow.io/api/auth/health

# Test frontend
curl -I https://api.signupflow.io/
```

### 7.3 Check Container Logs

```bash
# API logs
docker logs signupflow-api --tail 50

# Traefik logs
docker logs traefik --tail 50
```

---

## Step 8: Setup Automated Backups (2 minutes)

### 8.1 Configure Backup Script

```bash
nano scripts/backup-database.sh
```

```bash
#!/bin/bash
# scripts/backup-database.sh

# Configuration
BACKUP_DIR="/var/backups/signupflow"
S3_BUCKET="signupflow-backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup-$TIMESTAMP.dump"

# Create backup directory
mkdir -p $BACKUP_DIR

# Run pg_dump
pg_dump $DATABASE_URL -Fc -f $BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE s3://$S3_BUCKET/production/daily/backup-$TIMESTAMP.dump

# Cleanup old local backups (keep last 7 days)
find $BACKUP_DIR -name "backup-*.dump" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

```bash
chmod +x scripts/backup-database.sh
```

### 8.2 Schedule Daily Backups

```bash
# Add to crontab
crontab -e
```

Add this line:
```
0 2 * * * /home/ubuntu/signupflow/scripts/backup-database.sh >> /var/log/signupflow-backup.log 2>&1
```

### 8.3 Test Backup Script

```bash
./scripts/backup-database.sh
```

---

## Troubleshooting

### Issue 1: HTTPS Certificate Not Provisioning

**Symptom**: `curl https://api.signupflow.io` returns connection error

**Solution**:
```bash
# Check Traefik logs
docker logs traefik | grep -i "certificate"

# Verify DNS resolves correctly
dig api.signupflow.io +short

# Ensure port 80 and 443 are open
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Restart Traefik
docker-compose -f docker-compose.prod.yml restart traefik

# Wait 2-3 minutes for certificate provisioning
```

### Issue 2: Database Connection Failure

**Symptom**: Health check returns `{"status":"degraded","components":{"database":"unhealthy"}}`

**Solution**:
```bash
# Test database connectivity directly
psql $DATABASE_URL -c "SELECT 1"

# Check environment variables loaded correctly
docker exec signupflow-api env | grep DATABASE_URL

# Verify PostgreSQL allows connections from server IP
# (Check security group/firewall rules in cloud provider console)

# Restart API container
docker-compose -f docker-compose.prod.yml restart api
```

### Issue 3: Container Fails to Start

**Symptom**: `docker ps` shows container exited

**Solution**:
```bash
# Check container logs
docker logs signupflow-api --tail 100

# Common issues:
# - Missing environment variables (check .env.production)
# - Database migration failure (check DATABASE_URL)
# - Port conflict (ensure no other service on port 8000)

# Restart with verbose logging
docker-compose -f docker-compose.prod.yml up api
```

### Issue 4: High Memory Usage

**Symptom**: Server runs out of memory, containers killed by OOM

**Solution**:
```bash
# Add resource limits to docker-compose.prod.yml
services:
  api:
    mem_limit: 2g
    mem_reservation: 1g
    cpus: 2

# Restart services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

## Post-Deployment Checklist

After deployment, verify:

- [ ] **HTTPS Working**: `curl https://api.signupflow.io/health` returns HTTP 200
- [ ] **Database Connected**: Health check shows `"database":"healthy"`
- [ ] **Certificate Valid**: Let's Encrypt certificate issued (check browser)
- [ ] **HTTP Redirects**: `curl http://api.signupflow.io` redirects to HTTPS
- [ ] **Auto-Restart Working**: `docker restart signupflow-api` → service recovers automatically
- [ ] **Logs Accessible**: `docker logs signupflow-api` shows application logs
- [ ] **Backups Scheduled**: `crontab -l` shows daily backup cron job
- [ ] **Monitoring Configured**: (Optional) Sentry receiving error reports

---

## Next Steps

### Security Hardening

```bash
# 1. Setup firewall (allow only 80, 443, 22)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP (Traefik)
sudo ufw allow 443/tcp # HTTPS (Traefik)
sudo ufw enable

# 2. Disable password authentication (SSH keys only)
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd

# 3. Setup fail2ban (prevent brute force)
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
```

### Monitoring Setup

```bash
# 1. Install monitoring agent (optional - Sentry, Datadog, etc.)
# Follow provider's instructions

# 2. Setup uptime monitoring
# Use: UptimeRobot, Pingdom, or StatusCake (free tier available)

# 3. Configure alerts
# Slack webhook for deployment notifications
```

### CI/CD Integration

```bash
# 1. Setup GitHub Actions secrets
# Go to: GitHub repo → Settings → Secrets → Actions
# Add: PRODUCTION_SSH_KEY, DATABASE_URL, SECRET_KEY

# 2. Configure GitHub Actions workflows
# .github/workflows/deploy-production.yml (created in Phase 2)

# 3. Test automated deployment
git push origin main
# Verify staging deployment → manual approval → production deployment
```

---

## Production Checklist

Before going live with real users:

- [ ] **Database Backups**: Automated daily backups working
- [ ] **Restore Tested**: Successfully restored from backup at least once
- [ ] **HTTPS Certificate**: Valid and auto-renewing (check expiry date)
- [ ] **Health Monitoring**: Uptime monitoring configured (UptimeRobot, Pingdom)
- [ ] **Error Tracking**: Sentry or equivalent configured
- [ ] **Firewall Configured**: Only necessary ports open (22, 80, 443)
- [ ] **DNS Configured**: Domain points to server, propagated globally
- [ ] **Secrets Secured**: No credentials in version control, all in .env files
- [ ] **Logs Rotation**: Logrotate configured to prevent disk full
- [ ] **Resource Monitoring**: CPU/memory/disk usage monitoring
- [ ] **Disaster Recovery Plan**: Documented runbook for complete restore
- [ ] **Rollback Tested**: Verified ability to rollback to previous version

---

## Deployment Timeline

| Step | Duration | Critical? |
|------|----------|-----------|
| Server preparation | 2 min | ✅ Yes |
| Environment config | 3 min | ✅ Yes |
| Domain config | 2 min | ✅ Yes (wait for DNS) |
| Traefik setup | 1 min | ✅ Yes |
| Docker Compose config | 2 min | ✅ Yes |
| Deploy application | 1 min | ✅ Yes |
| Verify deployment | 1 min | ✅ Yes |
| Setup backups | 2 min | ⚠️ Important (can defer) |

**Total Critical Path**: ~12 minutes (with DNS propagation wait)

**First-Time Deployment**: ~30 minutes (includes troubleshooting)

---

## Support and Resources

- **Documentation**: `/docs/deployment/` (comprehensive guides)
- **Troubleshooting**: `/docs/operations/` (runbooks and procedures)
- **Health Check**: `https://api.signupflow.io/health`
- **API Docs**: `https://api.signupflow.io/docs` (Swagger UI)
- **GitHub Issues**: `https://github.com/tomqwu/signupflow/issues`

---

**Quickstart Status**: ✅ Production-Ready
**Last Updated**: 2025-10-23
**Tested On**: Ubuntu 22.04 LTS, Docker 24+, Docker Compose 2.x
