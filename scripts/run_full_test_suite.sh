#!/bin/bash
# Complete end-to-end automated test suite
set -e
echo "🧪 ROSTIO END-TO-END TEST SUITE"
echo "=============================="

# Kill servers
lsof -ti:8000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
sleep 2

# Fresh database  
rm -f roster.db

# Start server
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/test_server.log 2>&1 &
SERVER_PID=$!
sleep 5

# Check health
curl -s http://localhost:8000/health | grep -q "healthy" || { echo "❌ Server failed"; exit 1; }
echo "✅ Server running"

# Setup data
bash /tmp/setup_demo_data.sh > /dev/null 2>&1

# Create assignments
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
print(f"Created {len(assignments)} assignments")
conn.close()
ENDPY

echo "✅ Test data ready"

# Run tests
echo ""
echo "🧪 Testing API..."
ASSIGN_COUNT=$(curl -s "http://localhost:8000/api/solutions/?org_id=grace-church" | python3 -c "import sys, json; print(json.load(sys.stdin)['solutions'][0]['assignment_count'])")
echo "   Solutions: Assignment count = $ASSIGN_COUNT"
[[ "$ASSIGN_COUNT" == "5" ]] && echo "   ✅ PASS" || { echo "   ❌ FAIL"; exit 1; }

SARAH_COUNT=$(curl -s "http://localhost:8000/api/solutions/1/assignments" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len([a for a in d['assignments'] if 'Sarah' in a['person_name']]))")
echo "   Sarah's assignments: $SARAH_COUNT"
[[ "$SARAH_COUNT" == "3" ]] && echo "   ✅ PASS" || { echo "   ❌ FAIL"; exit 1; }

echo ""
echo "✅ ALL TESTS PASSED!"
echo "Server PID: $SERVER_PID"
echo "Test at: http://localhost:8000/"
