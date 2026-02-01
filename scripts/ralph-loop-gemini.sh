#!/bin/bash
#
# Ralph Loop for Gemini CLI
#
# Based on Geoffrey Huntley's Ralph Wiggum methodology.
#

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
CONSTITUTION="$PROJECT_DIR/.specify/memory/constitution.md"

# Configuration
MAX_ITERATIONS=0  # 0 = unlimited
MODE="build"
GEMINI_CMD="gemini"
YOLO_FLAG="-y"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

mkdir -p "$LOG_DIR"

# Check constitution for YOLO setting
YOLO_ENABLED=true
if [[ -f "$CONSTITUTION" ]]; then
    if grep -q "YOLO Mode.*DISABLED" "$CONSTITUTION" 2>/dev/null; then
        YOLO_ENABLED=false
    fi
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        plan)
            MODE="plan"
            MAX_ITERATIONS=1
            shift
            ;;
        [0-9]*)
            MODE="build"
            MAX_ITERATIONS="$1"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

cd "$PROJECT_DIR"

# Session log
SESSION_LOG="$LOG_DIR/ralph_gemini_${MODE}_session_$(date '+%Y%m%d_%H%M%S').log"
exec > >(tee -a "$SESSION_LOG") 2>&1

PROMPT_FILE="PROMPT_${MODE}.md"

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}              RALPH LOOP (Gemini CLI) STARTING              ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

ITERATION=0
while true; do
    if [ $MAX_ITERATIONS -gt 0 ] && [ $ITERATION -ge $MAX_ITERATIONS ]; then
        break
    fi

    ITERATION=$((ITERATION + 1))
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    echo -e "${PURPLE}════════════════════ LOOP $ITERATION ════════════════════${NC}"
    echo -e "${BLUE}[$TIMESTAMP]${NC} Iteration $ITERATION"

    LOG_FILE="$LOG_DIR/ralph_gemini_${MODE}_iter_${ITERATION}_$(date '+%Y%m%d_%H%M%S').log"
    
    # Run Gemini
    GEMINI_FLAGS=""
    if [ "$YOLO_ENABLED" = true ]; then
        GEMINI_FLAGS="--approval-mode yolo"
    fi

    # Read prompt and pass to gemini
    PROMPT_CONTENT=$(cat "$PROMPT_FILE")
    
    # Run gemini and capture output
    if OUTPUT=$( "$GEMINI_CMD" $GEMINI_FLAGS "$PROMPT_CONTENT" 2>&1 | tee "$LOG_FILE"); then
        if echo "$OUTPUT" | grep -q "<promise>DONE</promise>"; then
            echo -e "${GREEN}✓ Completion signal detected!${NC}"
            if [ "$MODE" = "plan" ]; then break; fi
        else
            echo -e "${YELLOW}⚠ No completion signal. Retrying...${NC}"
        fi
    else
        echo -e "${RED}✗ Gemini execution failed${NC}"
    fi

    sleep 2
done
