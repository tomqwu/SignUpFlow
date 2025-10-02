#!/bin/bash
# Cleanup all background Rostio servers

echo "🧹 Cleaning up background servers..."

# Kill all Python processes running uvicorn
pkill -9 -f "uvicorn.*api.main" 2>/dev/null
pkill -9 -f "python.*uvicorn" 2>/dev/null

# Kill by port
lsof -ti:8000 2>/dev/null | xargs -r kill -9 2>/dev/null

# Wait a moment
sleep 2

# Check if any are still running
REMAINING=$(ps aux | grep -E "uvicorn|python.*api.main" | grep -v grep | wc -l)

if [ $REMAINING -eq 0 ]; then
    echo "✅ All servers cleaned up!"
else
    echo "⚠️  $REMAINING processes still running"
    ps aux | grep -E "uvicorn|python.*api.main" | grep -v grep
fi
