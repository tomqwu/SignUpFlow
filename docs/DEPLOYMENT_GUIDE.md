# SignUpFlow Deployment Guide

**Last Updated:** 2025-10-20
**Target Environment:** Production (Railway/Render/DigitalOcean)
**Status:** Planning → Implementation Ready

---

## 🎯 Deployment Overview

This guide covers deploying SignUpFlow from development (SQLite + localhost) to production (PostgreSQL + cloud hosting).

**Deployment Options:**
1. **Railway** (Recommended for MVP) - $12/mo, easiest setup
2. **Render** - $7/mo, great for startups
3. **DigitalOcean** - $24/mo, more control

---

## 📋 Pre-Deployment Checklist

### ✅ Code Readiness
- [ ] All tests passing (281+ tests)
- [ ] No critical bugs
- [ ] Environment variables documented
- [ ] Database migrations ready
- [ ] Frontend built and optimized

### ✅ Infrastructure Accounts
- [ ] Cloud hosting account (Railway/Render/DO)
- [ ] PostgreSQL database provisioned
- [ ] Domain name registered (signupflow.io)
- [ ] SSL certificate (free with Let's Encrypt)
- [ ] SendGrid account for emails
- [ ] Stripe account for billing
- [ ] Sentry account for error tracking

### ✅ Security
- [ ] JWT secret key generated (256-bit)
- [ ] Database credentials secured
- [ ] API keys in environment variables (not in code)
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] HTTPS enforced

---

## 🐳 Docker Setup

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root

# Copy application code
COPY api/ ./api/
COPY frontend/ ./frontend/
COPY locales/ ./locales/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Expose port
EXPOSE 8000

# Run database migrations and start server
CMD alembic upgrade head && \
    uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### docker-compose.yml (Local Testing)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: signupflow
      POSTGRES_USER: signupflow
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://signupflow:${DB_PASSWORD}@db:5432/signupflow
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
      STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY}
      SENDGRID_API_KEY: ${SENDGRID_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./frontend:/app/frontend  # For development

volumes:
  postgres_data:
```

---

## 🗄️ PostgreSQL Migration

### Step 1: Export SQLite Data

```bash
# Export existing data to SQL
sqlite3 roster.db .dump > data_export.sql

# Or use Python script for complex migrations
python scripts/migrate_sqlite_to_postgres.py
```

### Step 2: PostgreSQL Setup

```sql
-- Create database
CREATE DATABASE signupflow;
CREATE USER signupflow WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE signupflow TO signupflow;

-- Connect to database
\c signupflow

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
```

### Step 3: Run Alembic Migrations

```bash
# Set DATABASE_URL to PostgreSQL
export DATABASE_URL="postgresql://signupflow:password@localhost:5432/signupflow"

# Run migrations
alembic upgrade head

# Verify tables created
psql -U signupflow -d signupflow -c "\dt"
```

### Step 4: Import Data

```bash
# Import organizations
python scripts/import_data.py --table organizations --file data/orgs.json

# Import people
python scripts/import_data.py --table people --file data/people.json

# Import events
python scripts/import_data.py --table events --file data/events.json
```

---

## ☁️ Deployment: Railway (Recommended)

### Why Railway?
- ✅ Automatic HTTPS
- ✅ GitHub integration (auto-deploy on push)
- ✅ Managed PostgreSQL
- ✅ Zero-config deployments
- ✅ $12/mo for small apps

### Setup Steps

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Initialize project
   railway init
   ```

3. **Add PostgreSQL Database**
   - In Railway dashboard: "+ New" → "Database" → "PostgreSQL"
   - Copy DATABASE_URL from settings

4. **Configure Environment Variables**
   ```bash
   railway variables set SECRET_KEY="your-256-bit-secret-key"
   railway variables set STRIPE_SECRET_KEY="sk_live_..."
   railway variables set SENDGRID_API_KEY="SG...."
   railway variables set APP_URL="https://signupflow.up.railway.app"
   ```

5. **Deploy**
   ```bash
   # Deploy from CLI
   railway up

   # Or connect GitHub repo for auto-deploy
   # Railway dashboard → Settings → Connect GitHub Repo
   ```

6. **Run Migrations**
   ```bash
   railway run alembic upgrade head
   ```

7. **Custom Domain**
   - Railway dashboard → Settings → Custom Domain
   - Add: app.signupflow.io
   - Update DNS: CNAME → your-app.up.railway.app

---

## ☁️ Deployment: Render

### Setup Steps

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Dashboard → "+ New" → "Web Service"
   - Connect GitHub repo: `tomqwu/SignUpFlow`

3. **Configure Service**
   ```yaml
   Name: signupflow-api
   Environment: Python 3
   Build Command: pip install poetry && poetry install --no-dev
   Start Command: alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add PostgreSQL**
   - Dashboard → "+ New" → "PostgreSQL"
   - Copy Internal Database URL

5. **Environment Variables**
   ```
   DATABASE_URL=<internal_database_url>
   SECRET_KEY=your-secret-key
   PYTHON_VERSION=3.11
   ```

6. **Deploy**
   - Click "Create Web Service"
   - Auto-deploys on git push to main

---

## ☁️ Deployment: DigitalOcean

### Setup Steps

1. **Create Droplet**
   ```bash
   # Ubuntu 22.04 LTS
   # $24/mo (2GB RAM, 50GB SSD)
   ```

2. **Initial Server Setup**
   ```bash
   # SSH into server
   ssh root@your_server_ip

   # Update system
   apt update && apt upgrade -y

   # Install dependencies
   apt install -y python3.11 python3-pip nginx postgresql redis-server

   # Create app user
   adduser signupflow
   usermod -aG sudo signupflow
   ```

3. **Setup PostgreSQL**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE signupflow;
   CREATE USER signupflow WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE signupflow TO signupflow;
   \q
   ```

4. **Deploy Application**
   ```bash
   # Clone repo
   cd /home/signupflow
   git clone https://github.com/tomqwu/SignUpFlow.git
   cd SignUpFlow

   # Install dependencies
   pip install poetry
   poetry install --no-dev

   # Run migrations
   alembic upgrade head
   ```

5. **Setup Systemd Service**
   ```ini
   # /etc/systemd/system/signupflow.service
   [Unit]
   Description=SignUpFlow API
   After=network.target postgresql.service

   [Service]
   User=signupflow
   WorkingDirectory=/home/signupflow/SignUpFlow
   ExecStart=/home/signupflow/.local/bin/poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   systemctl enable signupflow
   systemctl start signupflow
   systemctl status signupflow
   ```

6. **Setup Nginx**
   ```nginx
   # /etc/nginx/sites-available/signupflow
   server {
       listen 80;
       server_name app.signupflow.io;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   ln -s /etc/nginx/sites-available/signupflow /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

7. **Setup SSL (Let's Encrypt)**
   ```bash
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d app.signupflow.io
   ```

---

## 🔒 Security Hardening

### 1. Environment Variables

```bash
# .env.production (NEVER commit to git)
SECRET_KEY=<256-bit-random-string>
DATABASE_URL=postgresql://user:pass@host:5432/db
STRIPE_SECRET_KEY=sk_live_...
SENDGRID_API_KEY=SG....
SENTRY_DSN=https://...@sentry.io/...
```

### 2. CORS Configuration

```python
# api/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://signupflow.io",
        "https://app.signupflow.io"
    ],  # NO wildcards in production!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

```python
# api/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(...):
    ...
```

### 4. Database Connection Pooling

```python
# api/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True  # Verify connections before use
)
```

---

## 📊 Monitoring & Logging

### Sentry Setup

```python
# api/main.py
import sentry_sdk

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment="production",
    traces_sample_rate=0.1  # 10% performance monitoring
)
```

### Uptime Monitoring

- **UptimeRobot** (free): https://uptimerobot.com
- **Pingdom**: https://pingdom.com
- Check URL: https://app.signupflow.io/health

### Logs

```bash
# Railway: View in dashboard
railway logs

# Render: View in dashboard
# Logs → signupflow-api

# DigitalOcean:
journalctl -u signupflow -f
```

---

## 🚀 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          poetry install
          poetry run pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway up --service signupflow-api
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## ✅ Post-Deployment Checklist

- [ ] Health check endpoint working: `/health`
- [ ] Database migrations applied
- [ ] Environment variables set correctly
- [ ] SSL certificate active (HTTPS working)
- [ ] Domain pointing to app
- [ ] Sentry receiving errors
- [ ] Uptime monitoring configured
- [ ] Backup strategy in place
- [ ] Test signup flow end-to-end
- [ ] Test payment flow (Stripe)
- [ ] Test email delivery (SendGrid)
- [ ] Performance test (load 100 users)

---

## 📞 Support & Troubleshooting

### Common Issues

**Database connection timeout:**
```bash
# Check connection
pg_isready -h your_db_host -p 5432

# Test connection string
psql "postgresql://user:pass@host:5432/db"
```

**Migrations failed:**
```bash
# Rollback one migration
alembic downgrade -1

# Check migration status
alembic current

# Re-run migrations
alembic upgrade head
```

**App not starting:**
```bash
# Check logs
railway logs  # or journalctl -u signupflow -f

# Common fixes:
# - Missing environment variables
# - Database not accessible
# - Port already in use
```

---

## 💰 Cost Estimate

### MVP Deployment (Months 1-3)

```
Railway:              $12/mo
PostgreSQL (Railway): $15/mo (included in Railway plan)
Domain:               $12/year = $1/mo
SendGrid:             $15/mo (40k emails)
Sentry:               $0 (free tier)
UptimeRobot:          $0 (free tier)
─────────────────────────────
TOTAL:                $28/mo
```

### Production Scale (50+ customers)

```
DigitalOcean Droplet: $24/mo
Managed PostgreSQL:   $30/mo
Redis:                $15/mo
SendGrid Pro:         $90/mo
Sentry Developer:     $26/mo
CDN (CloudFlare):     $0 (free tier)
─────────────────────────────
TOTAL:                $185/mo
```

**Break-even: 7 customers @ $29/mo**

---

## 🎯 Success Criteria

- ✅ 99.9% uptime
- ✅ < 500ms API response time
- ✅ < 1% error rate
- ✅ Zero data loss
- ✅ Daily automated backups
- ✅ 24hr incident response time

---

**Ready to deploy?** Start with Railway for fastest MVP launch!
