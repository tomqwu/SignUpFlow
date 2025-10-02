#!/bin/bash
# Prepare app for taking screenshots

set -e

echo "🎬 Preparing Rostio for Screenshots"
echo "===================================="

# Kill all servers
echo "1️⃣ Cleaning up..."
lsof -ti:8000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
sleep 2

# Fresh database
echo "2️⃣ Creating fresh database..."
rm -f roster.db

# Start server
echo "3️⃣ Starting server..."
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/screenshot_server.log 2>&1 &
SERVER_PID=$!
sleep 5

# Setup data
echo "4️⃣ Creating sample data..."
bash /tmp/setup_demo_data.sh > /dev/null 2>&1

# Create assignments
echo "5️⃣ Creating assignments..."
python3 << 'ENDPY'
import sqlite3
from datetime import datetime

conn = sqlite3.connect('roster.db')
c = conn.cursor()

c.execute("INSERT INTO solutions (org_id, solve_ms, hard_violations, soft_score, health_score, metrics, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
          ('grace-church', 0.05, 0, 0.0, 100.0, '{"fairness": {"stdev": 0.0, "per_person_counts": {}}}', datetime.now().isoformat()))
solution_id = c.lastrowid

c.execute("SELECT id, name FROM people ORDER BY name")
people = {name: pid for pid, name in c.fetchall()}

now = datetime.now().isoformat()
assignments = [
    (solution_id, 'sunday-service-2025-10-05', people['Sarah Johnson'], now),
    (solution_id, 'sunday-service-2025-10-05', people['Emily Davis'], now),
    (solution_id, 'sunday-service-2025-10-05', people['Mike Chen'], now),
    (solution_id, 'sunday-service-2025-10-12', people['Sarah Johnson'], now),
    (solution_id, 'sunday-service-2025-10-19', people['Sarah Johnson'], now),
]

c.executemany("INSERT INTO assignments (solution_id, event_id, person_id, assigned_at) VALUES (?, ?, ?, ?)", assignments)
conn.commit()
conn.close()
print(f"Created {len(assignments)} assignments")
ENDPY

echo ""
echo "✅ Ready for Screenshots!"
echo ""
echo "📸 Next steps:"
echo "  1. Open: http://localhost:8000/"
echo "  2. Follow guide: docs/SCREENSHOTS.md"
echo ""
echo "Login credentials:"
echo "  User:  sarah@grace.church / password123"
echo "  Admin: pastor@grace.church / password123"
echo ""
echo "Server PID: $SERVER_PID"
echo "To stop: kill $SERVER_PID"
