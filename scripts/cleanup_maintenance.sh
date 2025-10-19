#!/bin/bash
# cleanup_maintenance.sh - Weekly maintenance script for SignUpFlow
# Add to cron: 0 0 * * 0 /path/to/cleanup_maintenance.sh

echo "🧹 SignUpFlow Weekly Maintenance"
echo "================================"

# Clean Python cache
echo "1️⃣ Cleaning Python cache..."
find . -type d -name "__pycache__" ! -path "*/node_modules/*" ! -path "*/.venv/*" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" ! -path "*/node_modules/*" ! -path "*/.venv/*" -delete 2>/dev/null
echo "   ✅ Cleaned Python cache"

# Clean old logs (>7 days)
echo "2️⃣ Cleaning old logs..."
find . -name "*.log" -type f -mtime +7 ! -path "*/node_modules/*" -delete 2>/dev/null
echo "   ✅ Deleted logs older than 7 days"

# Clean runtime database files (when server is stopped)
echo "3️⃣ Cleaning runtime database files..."
rm -f *.db-shm *.db-wal 2>/dev/null
echo "   ✅ Cleaned WAL files"

# Show git ignored files
echo "4️⃣ Checking .gitignore coverage..."
echo "   Ignored files (first 10):"
git status --ignored --short 2>/dev/null | grep "^!!" | head -10

echo ""
echo "✅ Weekly maintenance complete!"
echo "💡 Add to cron: 0 0 * * 0 $(pwd)/scripts/cleanup_maintenance.sh"
