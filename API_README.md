# Roster API - Microservice Documentation

A FastAPI-based microservice for constraint-based roster scheduling. Supports cricket leagues, church volunteers, on-call rotations, and custom scheduling scenarios.

## 🚀 Quick Start

### Start the API Server

```bash
# Install dependencies
poetry install

# Start the server
poetry run roster-api

# Or use uvicorn directly
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Core Resources

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/organizations` | GET, POST, PUT, DELETE | Manage organizations/leagues |
| `/people` | GET, POST, PUT, DELETE | Manage people/players/volunteers |
| `/teams` | GET, POST, PUT, DELETE | Manage teams |
| `/events` | GET, POST, PUT, DELETE | Manage events/matches/shifts |
| `/constraints` | GET, POST, PUT, DELETE | Manage scheduling constraints |

### Solver

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solver/solve` | POST | Generate a schedule solution |

### Solutions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solutions` | GET | List all solutions |
| `/solutions/{id}` | GET | Get solution details |
| `/solutions/{id}/assignments` | GET | Get all assignments |
| `/solutions/{id}/export` | POST | Export solution (CSV/JSON/ICS) |

## 💡 Example Usage

### 1. Create an Organization

```bash
curl -X POST http://localhost:8000/organizations/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my_league",
    "name": "My Cricket League",
    "region": "AU-NSW",
    "config": {
      "change_min_weight": 100,
      "fairness_weight": 50,
      "cooldown_days": 7
    }
  }'
```

### 2. Add People

```bash
curl -X POST http://localhost:8000/people/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "player_01",
    "org_id": "my_league",
    "name": "Alice Smith",
    "email": "alice@example.com",
    "roles": ["batsman", "captain"]
  }'
```

### 3. Create Teams

```bash
curl -X POST http://localhost:8000/teams/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "team_a",
    "org_id": "my_league",
    "name": "Team A",
    "member_ids": ["player_01", "player_02", "player_03"]
  }'
```

### 4. Schedule Events

```bash
curl -X POST http://localhost:8000/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "match_01",
    "org_id": "my_league",
    "type": "cricket_match",
    "start_time": "2025-10-07T14:00:00",
    "end_time": "2025-10-07T18:00:00",
    "team_ids": ["team_a", "team_b"]
  }'
```

### 5. Solve the Schedule

```bash
curl -X POST http://localhost:8000/solver/solve \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "my_league",
    "from_date": "2025-10-01",
    "to_date": "2025-10-31",
    "mode": "strict",
    "change_min": false
  }'
```

**Response:**
```json
{
  "solution_id": 1,
  "metrics": {
    "hard_violations": 0,
    "soft_score": 0.0,
    "health_score": 100.0,
    "solve_ms": 45.2,
    "fairness": {
      "stdev": 0.5,
      "per_person_counts": {
        "player_01": 3,
        "player_02": 3
      }
    }
  },
  "assignment_count": 12,
  "violations": [],
  "message": "Solution generated with 12 assignments"
}
```

### 6. Export Solution

```bash
# Export as CSV
curl -X POST http://localhost:8000/solutions/1/export \
  -H "Content-Type: application/json" \
  -d '{
    "format": "csv",
    "scope": "org"
  }' > schedule.csv

# Export as ICS calendar
curl -X POST http://localhost:8000/solutions/1/export \
  -H "Content-Type: application/json" \
  -d '{
    "format": "ics",
    "scope": "person:player_01"
  }' > calendar.ics
```

## 🐍 Python Client Example

See [examples/api_client_example.py](examples/api_client_example.py) for a complete working example.

```python
import httpx

API_URL = "http://localhost:8000"

with httpx.Client(base_url=API_URL) as client:
    # Create organization
    response = client.post("/organizations/", json={
        "id": "demo_league",
        "name": "Demo League",
        "region": "US-CA"
    })

    # Add people
    response = client.post("/people/", json={
        "id": "player_01",
        "org_id": "demo_league",
        "name": "Alice",
        "roles": ["captain"]
    })

    # Solve
    response = client.post("/solver/solve", json={
        "org_id": "demo_league",
        "from_date": "2025-10-01",
        "to_date": "2025-10-31",
        "mode": "strict"
    })

    solution = response.json()
    print(f"Solution ID: {solution['solution_id']}")
    print(f"Health Score: {solution['metrics']['health_score']}")
```

## 🗄️ Database

The API uses SQLite by default with SQLAlchemy ORM:
- **Location**: `./roster.db` (created automatically)
- **Schema**: See [roster_cli/db/models.py](roster_cli/db/models.py)
- **Migrations**: Auto-created on startup

### Database Schema

- **organizations** - League/church/company info
- **people** - Players/volunteers
- **teams** - Team definitions
- **team_members** - Team membership
- **resources** - Venues/grounds/rooms
- **events** - Matches/shifts/meetings
- **event_teams** - Event-team links
- **holidays** - Organization-wide holidays
- **constraints** - Scheduling constraints
- **solutions** - Generated schedules
- **assignments** - Person-to-event assignments

## 📊 API Response Models

### Solution Metrics

```json
{
  "hard_violations": 0,
  "soft_score": 12.5,
  "health_score": 95.0,
  "solve_ms": 123.4,
  "fairness": {
    "stdev": 0.8,
    "per_person_counts": {
      "person_01": 4,
      "person_02": 3
    }
  }
}
```

- **hard_violations**: Count of hard constraint violations (0 = feasible)
- **soft_score**: Penalty score from soft constraints (lower is better)
- **health_score**: Overall solution quality (0-100, higher is better)
- **solve_ms**: Time taken to solve in milliseconds
- **fairness.stdev**: Standard deviation of assignment counts

## 🔧 Configuration

### Environment Variables

```bash
# Database URL (default: sqlite:///./roster.db)
DATABASE_URL=sqlite:///./roster.db

# API Host and Port
API_HOST=0.0.0.0
API_PORT=8000
```

### CORS

CORS is enabled for all origins by default. For production, configure in [api/main.py](api/main.py):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 Testing

```bash
# Run the example client
poetry run python examples/api_client_example.py

# Manual testing with curl
curl http://localhost:8000/health
curl http://localhost:8000/organizations/
```

## 📖 Architecture

```
api/
├── main.py                  # FastAPI app entry point
├── database.py              # Database connection & session
├── routers/                 # API endpoints
│   ├── organizations.py     # Organization CRUD
│   ├── people.py            # People CRUD
│   ├── teams.py             # Teams CRUD
│   ├── events.py            # Events CRUD
│   ├── constraints.py       # Constraints CRUD
│   ├── solver.py            # Solve endpoint
│   └── solutions.py         # Solutions & export
└── schemas/                 # Pydantic models
    ├── organization.py
    ├── person.py
    ├── team.py
    ├── event.py
    ├── constraint.py
    └── solver.py

roster_cli/                  # Core business logic (reused)
├── core/                    # Domain models & solver
│   ├── models.py
│   ├── solver/
│   │   ├── heuristics.py    # Greedy solver
│   │   └── adapter.py       # Solver interface
│   ├── constraints/         # Constraint DSL
│   └── *_writer.py          # Export formatters
└── db/                      # Database layer
    └── models.py            # SQLAlchemy models
```

## 🚀 Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install poetry && poetry install --no-dev

CMD ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  roster-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/roster
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: roster
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
```

## 📝 Notes

- **Constraints**: The API currently accepts constraint definitions but passes an empty list to the solver. Full constraint integration requires converting DB constraint format to `ConstraintBinding` objects with proper DSL parsing.
- **Authentication**: No auth is implemented. Add JWT/OAuth for production.
- **Rate Limiting**: Not implemented. Consider adding for production.
- **Async**: Solver runs synchronously. For heavy loads, consider background tasks with Celery/RQ.

## 📄 License

MIT License
