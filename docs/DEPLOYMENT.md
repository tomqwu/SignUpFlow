# SignUpFlow Deployment Guide

**For:** Production deployment of SignUpFlow
**Last Updated:** 2024-10-24
**Prerequisites:** Docker, Docker Compose, domain name (optional)

---

## 📋 Table of Contents

1. [Quick Start (Docker Compose)](#quick-start-docker-compose)
2. [Environment Configuration](#environment-configuration)
3. [Deployment Platforms](#deployment-platforms)
4. [Database Migrations](#database-migrations)
5. [SSL/HTTPS Setup](#sslhttps-setup)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [Scaling & Performance](#scaling--performance)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start (Docker Compose)

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Domain name (recommended for production)
- Minimum 2GB RAM, 2 CPU cores

### 1. Clone Repository

```bash
git clone https://github.com/tomqwu/signupflow.git
cd signupflow
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with production values
nano .env
```

**Critical values to update:**
```bash
# Database (use strong passwords!)
POSTGRES_PASSWORD=CHANGE_ME_strong_random_password_123
REDIS_PASSWORD=CHANGE_ME_another_strong_password_456

# Security (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=CHANGE_ME_random_32_char_secret

# URLs (use your actual domain)
API_BASE_URL=https://yourdomain.com
FRONTEND_URL=https://yourdomain.com

# Email (SendGrid)
SENDGRID_API_KEY=SG.your_actual_key_here
FROM_EMAIL=noreply@yourdomain.com

# Stripe (use live keys for production!)
STRIPE_SECRET_KEY=sk_live_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 3. Build and Start Services

```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### 4. Run Database Migrations

```bash
# Run Alembic migrations
docker-compose exec api alembic upgrade head

# Verify database schema
docker-compose exec db psql -U signupflow -d signupflow -c "\dt"
```

### 5. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status": "healthy", "database": "connected"}

# View logs
docker-compose logs -f
```

### 6. Access Application

Open browser: `http://localhost:8000`

Default admin login:
- Email: `jane@test.com`
- Password: `password`

**⚠️ Change default password immediately in production!**

---

## Environment Configuration

### Required Environment Variables

#### Database (PostgreSQL)
```bash
POSTGRES_DB=signupflow
POSTGRES_USER=signupflow
POSTGRES_PASSWORD=<strong-password-here>
DATABASE_URL=postgresql://signupflow:<password>@db:5432/signupflow
```

#### Redis (Caching & Sessions)
```bash
REDIS_PASSWORD=<strong-password-here>
REDIS_URL=redis://:<password>@redis:6379/0
```

#### Application Security
```bash
SECRET_KEY=<random-32-char-string>
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
```

#### Email (SendGrid - Production)
```bash
SENDGRID_API_KEY=SG.your_api_key
FROM_EMAIL=noreply@yourdomain.com
EMAIL_ENABLED=true
```

#### SMS (Twilio - Optional)
```bash
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
SMS_ENABLED=true
```

#### Stripe Billing
```bash
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### Optional Configuration

#### Feature Flags
```bash
RATE_LIMITING_ENABLED=true
SESSION_TTL_HOURS=24
```

#### Logging
```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENVIRONMENT=production
```

#### Server
```bash
PORT=8000
HOST=0.0.0.0
WORKERS=4  # Number of Uvicorn workers (2 x CPU cores recommended)
```

---

## Deployment Platforms

### Option 1: Railway (Easiest - Recommended)

**Why Railway:**
- One-click PostgreSQL + Redis
- Automatic HTTPS/SSL
- Simple GitHub deployment
- Free tier available ($5/month credit)

**Steps:**

1. **Sign up:** https://railway.app

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your SignUpFlow fork

3. **Add PostgreSQL:**
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway automatically sets `DATABASE_URL`

4. **Add Redis:**
   - Click "+ New"
   - Select "Database" → "Redis"
   - Railway automatically sets `REDIS_URL`

5. **Configure Environment Variables:**
   - Click on your service
   - Go to "Variables" tab
   - Add all required variables from `.env.example`

6. **Deploy:**
   - Railway automatically deploys on git push
   - Custom domain: Settings → Domains → Add Custom Domain

**Cost:** ~$10-20/month (Starter plan with PostgreSQL + Redis)

---

### Option 2: Render (Simple + Affordable)

**Why Render:**
- Free tier for PostgreSQL
- Automatic deploys from GitHub
- Built-in SSL
- Docker support

**Steps:**

1. **Sign up:** https://render.com

2. **Create PostgreSQL Database:**
   - Dashboard → New → PostgreSQL
   - Name: `signupflow-db`
   - Copy Internal Database URL

3. **Create Redis Instance:**
   - Dashboard → New → Redis
   - Name: `signupflow-redis`
   - Copy Internal Redis URL

4. **Create Web Service:**
   - Dashboard → New → Web Service
   - Connect GitHub repository
   - Runtime: Docker
   - Build Command: (leave empty - uses Dockerfile)
   - Start Command: (leave empty - uses Dockerfile CMD)

5. **Add Environment Variables:**
   - Environment tab
   - Add all variables from `.env.example`
   - Use Internal Database/Redis URLs from steps 2-3

6. **Deploy:**
   - Click "Manual Deploy" or push to GitHub

**Cost:**
- Free tier: 1 web service + PostgreSQL (limited resources)
- Starter: $7/month web service + $7/month Redis = $14/month

---

### Option 3: DigitalOcean App Platform

**Why DigitalOcean:**
- Managed databases (PostgreSQL + Redis)
- Automatic scaling
- Integrated monitoring
- Reliable infrastructure

**Steps:**

1. **Sign up:** https://www.digitalocean.com

2. **Create Database Cluster:**
   - Create → Databases → PostgreSQL
   - Name: `signupflow-db`
   - Region: Choose closest to users
   - Size: Basic ($15/month)

3. **Create Redis Cluster:**
   - Create → Databases → Redis
   - Name: `signupflow-redis`
   - Region: Same as PostgreSQL
   - Size: Basic ($15/month)

4. **Create App:**
   - Create → App Platform
   - Connect GitHub repository
   - Detect Dockerfile automatically

5. **Add Environment Variables:**
   - App → Settings → App-Level Environment Variables
   - Add all variables
   - Use DigitalOcean database connection strings

6. **Deploy:**
   - Automatic deployment on git push

**Cost:** ~$40-50/month (Basic app + databases)

---

### Option 4: Self-Hosted (VPS)

**Why Self-Hosted:**
- Full control
- Cost-effective for high traffic
- Custom configurations

**Requirements:**
- VPS with 2GB+ RAM (e.g., Linode, Vultr, AWS EC2)
- Ubuntu 22.04 LTS
- Domain name pointing to server IP

**Setup:**

#### 1. Install Dependencies

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Install Nginx (reverse proxy)
apt install nginx certbot python3-certbot-nginx -y
```

#### 2. Clone Repository

```bash
cd /opt
git clone https://github.com/tomqwu/signupflow.git
cd signupflow
```

#### 3. Configure Environment

```bash
cp .env.example .env
nano .env
# Update all production values
```

#### 4. Start Services

```bash
docker-compose up -d
```

#### 5. Configure Nginx Reverse Proxy

```bash
# Create Nginx config
nano /etc/nginx/sites-available/signupflow
```

Add configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Increase upload size for file attachments
    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/signupflow /etc/nginx/sites-enabled/
nginx -t  # Test configuration
systemctl reload nginx
```

#### 6. Setup SSL with Let's Encrypt

```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow prompts:
- Enter email
- Agree to terms
- Choose redirect HTTP to HTTPS: Yes

SSL auto-renews every 90 days.

---

## Database Migrations

### Running Migrations

**After deployment:**

```bash
# Docker Compose
docker-compose exec api alembic upgrade head

# Railway/Render (using CLI)
railway run alembic upgrade head
# or
render shell
alembic upgrade head
```

### Creating New Migrations

**After model changes:**

```bash
# Generate migration
docker-compose exec api alembic revision --autogenerate -m "Add new field to User model"

# Review migration file
cat alembic/versions/xxxx_add_new_field.py

# Apply migration
docker-compose exec api alembic upgrade head
```

### Rollback Migrations

```bash
# Rollback one migration
docker-compose exec api alembic downgrade -1

# Rollback to specific version
docker-compose exec api alembic downgrade <revision_id>
```

---

## SSL/HTTPS Setup

### Using Let's Encrypt (Self-Hosted)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d yourdomain.com

# Auto-renewal (already configured)
certbot renew --dry-run
```

### Using Cloudflare (Recommended)

**Why Cloudflare:**
- Free SSL
- DDoS protection
- CDN for static files
- Analytics

**Setup:**

1. Add domain to Cloudflare
2. Update nameservers at domain registrar
3. SSL/TLS → Full (strict)
4. Enable "Always Use HTTPS"
5. Page Rules → Cache Everything for `/frontend/*`

---

## Monitoring & Logging

### Docker Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api
```

### Application Logs

Logs are stored in `/app/logs/` directory:

```bash
# View application logs
docker-compose exec api tail -f logs/app.log

# Error logs only
docker-compose exec api grep ERROR logs/app.log
```

### Database Logs

```bash
# PostgreSQL logs
docker-compose logs -f db

# Connect to database
docker-compose exec db psql -U signupflow -d signupflow

# Check active connections
SELECT * FROM pg_stat_activity;
```

### Health Checks

```bash
# Application health
curl https://yourdomain.com/health

# Database connection
docker-compose exec api python -c "from api.database import SessionLocal; db = SessionLocal(); print('DB OK')"

# Redis connection
docker-compose exec redis redis-cli ping
```

### Monitoring Tools (Recommended)

1. **Sentry** (Error Tracking)
   ```bash
   # Add to .env
   SENTRY_DSN=https://your-sentry-dsn
   ```

2. **Uptime Robot** (Uptime Monitoring)
   - Free: https://uptimerobot.com
   - Monitor: `https://yourdomain.com/health`

3. **Better Stack** (Log Management)
   - Free tier: https://betterstack.com

---

## Backup & Recovery

### Automated Database Backups

Create backup script:

```bash
# /opt/signupflow/backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/signupflow/backups"
BACKUP_FILE="$BACKUP_DIR/signupflow_$DATE.sql.gz"

# Create backup
docker-compose exec -T db pg_dump -U signupflow signupflow | gzip > $BACKUP_FILE

# Keep last 30 days
find $BACKUP_DIR -name "signupflow_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

Make executable:
```bash
chmod +x /opt/signupflow/backup.sh
```

**Schedule daily backups** (cron):
```bash
crontab -e

# Add line:
0 2 * * * /opt/signupflow/backup.sh >> /var/log/signupflow-backup.log 2>&1
```

### Manual Backup

```bash
# Backup database
docker-compose exec db pg_dump -U signupflow signupflow > backup_$(date +%Y%m%d).sql

# Backup with compression
docker-compose exec db pg_dump -U signupflow signupflow | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore from Backup

```bash
# Stop API (to prevent connections)
docker-compose stop api

# Restore database
gunzip -c backup_20241024.sql.gz | docker-compose exec -T db psql -U signupflow -d signupflow

# Start API
docker-compose start api
```

### Backup to S3 (Recommended for Production)

```bash
# Install AWS CLI
apt install awscli

# Configure AWS
aws configure

# Backup script with S3 upload
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/tmp/signupflow_$DATE.sql.gz"

docker-compose exec -T db pg_dump -U signupflow signupflow | gzip > $BACKUP_FILE
aws s3 cp $BACKUP_FILE s3://your-bucket/backups/
rm $BACKUP_FILE
```

---

## Scaling & Performance

### Vertical Scaling (Single Server)

Increase resources in `docker-compose.yml`:

```yaml
api:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
```

### Horizontal Scaling (Multiple Servers)

**Load Balancer + Multiple API Instances:**

```yaml
# docker-compose.yml
api:
  image: signupflow-api:latest
  deploy:
    replicas: 3  # Run 3 instances
  depends_on:
    - db
    - redis
```

**Add Nginx Load Balancer:**

```nginx
upstream signupflow_backend {
    least_conn;  # Load balancing method
    server api1.internal:8000;
    server api2.internal:8000;
    server api3.internal:8000;
}

server {
    location / {
        proxy_pass http://signupflow_backend;
    }
}
```

### Database Performance

**Connection Pooling:**

```python
# api/database.py
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,       # Max connections
    max_overflow=10,    # Extra connections when pool full
    pool_pre_ping=True  # Test connections before use
)
```

**Indexes for Common Queries:**

```sql
-- Add indexes for performance
CREATE INDEX idx_person_org_id ON persons(org_id);
CREATE INDEX idx_event_datetime ON events(datetime);
CREATE INDEX idx_assignment_person ON event_assignments(person_id);
```

### Redis Caching

Enable Redis caching for frequent queries:

```python
# Cache subscription data
@cache.cached(timeout=300, key_prefix='subscription')
def get_subscription(org_id):
    # ... query logic
```

---

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker-compose logs api

# Rebuild image
docker-compose build --no-cache api
docker-compose up -d
```

#### 2. Database Connection Failed

```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec api python -c "from api.database import engine; engine.connect()"

# Check DATABASE_URL
docker-compose exec api printenv DATABASE_URL
```

#### 3. Redis Connection Failed

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping

# Check password
docker-compose exec api printenv REDIS_URL
```

#### 4. Migrations Failed

```bash
# Check current version
docker-compose exec api alembic current

# Show migration history
docker-compose exec api alembic history

# Force to specific version
docker-compose exec api alembic stamp head
```

#### 5. Out of Memory

```bash
# Check memory usage
docker stats

# Increase limits in docker-compose.yml
mem_limit: 2g

# Or increase VPS RAM
```

#### 6. Slow Performance

```bash
# Check database connections
docker-compose exec db psql -U signupflow -d signupflow
SELECT count(*) FROM pg_stat_activity;

# Check slow queries
SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

# Restart services
docker-compose restart
```

### Debug Mode

Enable debug logging:

```bash
# In .env
LOG_LEVEL=DEBUG

# Restart
docker-compose restart api

# Watch logs
docker-compose logs -f api
```

---

## Production Checklist

Before going live:

### Security
- [ ] Changed all default passwords
- [ ] Using strong SECRET_KEY (32+ chars)
- [ ] SSL/HTTPS enabled
- [ ] Firewall configured (only 80, 443, 22)
- [ ] Rate limiting enabled
- [ ] Using Stripe live keys (not test keys)

### Configuration
- [ ] Database using PostgreSQL (not SQLite)
- [ ] Redis enabled for sessions/caching
- [ ] SendGrid configured for emails
- [ ] Twilio configured for SMS (if enabled)
- [ ] Environment variables all set
- [ ] ENVIRONMENT=production in .env

### Monitoring
- [ ] Health check endpoint working
- [ ] Sentry error tracking configured
- [ ] Uptime monitoring setup
- [ ] Log aggregation configured
- [ ] Backup script scheduled (daily)

### Performance
- [ ] Database indexes created
- [ ] Connection pooling configured
- [ ] Caching enabled (Redis)
- [ ] CDN configured for static files
- [ ] Gzip compression enabled

### Testing
- [ ] All migrations applied
- [ ] Test signup/login flow
- [ ] Test billing checkout
- [ ] Test email delivery
- [ ] Test SMS delivery (if enabled)
- [ ] Load testing performed

---

## Support & Resources

- **Documentation:** https://docs.signupflow.io
- **GitHub Issues:** https://github.com/tomqwu/signupflow/issues
- **Docker Docs:** https://docs.docker.com
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

**Last Updated:** 2024-10-24
**Guide Version:** 1.0.0
**Tested Platforms:** Railway, Render, DigitalOcean, AWS, Self-hosted VPS
