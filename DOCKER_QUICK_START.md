# Docker Quick Start

**Get SignUpFlow running in 2 minutes with Docker Compose**

## Prerequisites

- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop/))
- `make` command available (pre-installed on macOS/Linux)

## Quick Start

```bash
# 1. Start all services (PostgreSQL + Redis + API)
make up

# 2. Run database migrations
make migrate-docker

# 3. Open in browser
open http://localhost:8000
```

**Default login:**
- Email: `jane@test.com`
- Password: `password`

## Common Commands

```bash
make up              # Start all services
make down            # Stop all services
make logs            # View logs
make shell           # Open shell in API container
make db-shell        # Open PostgreSQL shell
make test-docker     # Run tests
make ps              # Show running services
```

## What's Included

✅ **PostgreSQL 16** - Production database (port 5433)
✅ **Redis 7** - Caching and rate limiting (port 6380)
✅ **FastAPI** - Backend API with hot-reload (port 8000)
✅ **Auto-reload** - Code changes apply instantly

## Configuration

**Optional:** Copy `.env.example` to `.env` and configure external services:

```bash
cp .env.example .env
# Edit .env to add Stripe, Mailtrap, Twilio keys
```

The app will work without `.env` - external services just won't function.

## Troubleshooting

**Port already in use:**
```bash
# Change ports in docker-compose.dev.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

**Services won't start:**
```bash
# Check Docker is running
docker ps

# View detailed logs
make logs
```

**Reset everything:**
```bash
# Stop and remove all data
make clean-docker

# Start fresh
make up
make migrate-docker
```

## Documentation

For complete documentation, see:
- [Docker Development Guide](docs/DOCKER_DEVELOPMENT.md) - Comprehensive guide
- [Quick Start Guide](docs/QUICK_START.md) - Local development
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment

## Architecture

```
┌─────────────────────────────────────┐
│  Browser (localhost:8000)           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  FastAPI (signupflow-dev-api)       │
│  - Hot-reload enabled               │
│  - Connected to PostgreSQL & Redis  │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼─────┐
│ PostgreSQL │    │   Redis    │
│ (port 5433)│    │ (port 6380)│
└────────────┘    └────────────┘
```

## Next Steps

1. **Explore the API:** http://localhost:8000/docs (Swagger UI)
2. **Make changes:** Edit files in `api/` - auto-reloads!
3. **Run tests:** `make test-docker`
4. **Read docs:** `docs/DOCKER_DEVELOPMENT.md`

## Support

- **Issues:** https://github.com/tomqwu/signupflow/issues
- **Docs:** `/docs` directory
- **Help:** `make help`
