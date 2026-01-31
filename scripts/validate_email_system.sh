#!/bin/bash
# validate_email_system.sh - Email Notification System Validation Script
# Purpose: Automated prerequisite checks and validation setup
# Usage: ./scripts/validate_email_system.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emojis
CHECK="✅"
CROSS="❌"
WARN="⚠️"
INFO="ℹ️"
ROCKET="🚀"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   📧 Email Notification System - Validation Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Track validation status
ALL_PASSED=true

# Function to check prerequisites
check_prerequisite() {
    local name=$1
    local command=$2
    local error_msg=$3

    echo -n "${INFO} Checking ${name}... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}${CHECK} OK${NC}"
        return 0
    else
        echo -e "${RED}${CROSS} FAILED${NC}"
        echo -e "   ${YELLOW}${error_msg}${NC}"
        ALL_PASSED=false
        return 1
    fi
}

# Check Python version
echo -e "${BLUE}━━━ Step 1: System Requirements ━━━${NC}"
check_prerequisite \
    "Python 3.10+" \
    "python3 --version | grep -E 'Python 3\.(10|11|12|13|14)'" \
    "Install Python 3.10+: sudo apt-get install python3"

# Check Poetry
check_prerequisite \
    "Poetry" \
    "poetry --version" \
    "Install Poetry: curl -sSL https://install.python-poetry.org | python3 -"

# Check Redis
echo ""
echo -e "${BLUE}━━━ Step 2: Redis (REQUIRED for Celery) ━━━${NC}"
if ! command -v redis-cli &> /dev/null; then
    echo -e "${RED}${CROSS} Redis CLI not found${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${YELLOW}Installing Redis via brew...${NC}"
        brew install redis
        brew services start redis
    else
        echo -e "${YELLOW}Installing Redis...${NC}"
        sudo apt-get update -qq
        sudo apt-get install -y redis-server
        sudo systemctl start redis-server
        sudo systemctl enable redis-server
    fi

    echo -e "${GREEN}${CHECK} Redis installed and started${NC}"
fi

# Check if Redis is running
if redis-cli ping | grep -q "PONG"; then
    echo -e "${GREEN}${CHECK} Redis is running${NC}"
else
    echo -e "${YELLOW}${WARN} Redis not running, attempting to start...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start redis
    else
        sudo systemctl start redis-server
    fi

    if redis-cli ping | grep -q "PONG"; then
        echo -e "${GREEN}${CHECK} Redis started successfully${NC}"
    else
        echo -e "${RED}${CROSS} Failed to start Redis${NC}"
        echo -e "${YELLOW}Manual fix: brew services start redis (macOS) or sudo systemctl start redis-server (Linux)${NC}"
        ALL_PASSED=false
    fi
fi

# Check dependencies
echo ""
echo -e "${BLUE}━━━ Step 3: Python Dependencies ━━━${NC}"
# Use current directory instead of hardcoded path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."

if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}${WARN} Virtual environment not found, installing dependencies...${NC}"
    poetry install
    echo -e "${GREEN}${CHECK} Dependencies installed${NC}"
else
    echo -e "${GREEN}${CHECK} Dependencies already installed${NC}"
fi

# Verify critical dependencies
check_prerequisite \
    "Celery" \
    "poetry run celery --version" \
    "Run: poetry install"

check_prerequisite \
    "FastAPI" \
    "poetry run python -c 'import fastapi'" \
    "Run: poetry install"

check_prerequisite \
    "SQLAlchemy" \
    "poetry run python -c 'import sqlalchemy'" \
    "Run: poetry install"

# Check .env file
echo ""
echo -e "${BLUE}━━━ Step 4: Configuration Files ━━━${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}${CHECK} .env file exists${NC}"

    # Check critical env vars
    if grep -q "CELERY_BROKER_URL" .env && grep -q "CELERY_RESULT_BACKEND" .env; then
        echo -e "${GREEN}${CHECK} Celery configuration found${NC}"
    else
        echo -e "${YELLOW}${WARN} Missing Celery configuration in .env${NC}"
        echo -e "   Add: CELERY_BROKER_URL=redis://localhost:6379/0"
        echo -e "   Add: CELERY_RESULT_BACKEND=redis://localhost:6379/0"
        ALL_PASSED=false
    fi

    # Check email configuration
    if grep -q "MAILTRAP_SMTP_USER" .env || grep -q "SENDGRID_API_KEY" .env; then
        echo -e "${GREEN}${CHECK} Email service configured${NC}"
    else
        echo -e "${YELLOW}${WARN} No email service configured${NC}"
        echo -e "   Configure Mailtrap OR SendGrid in .env"
        echo -e "   See: docs/MANUAL_VALIDATION_GUIDE.md"
        ALL_PASSED=false
    fi
else
    echo -e "${RED}${CROSS} .env file not found${NC}"
    echo -e "${YELLOW}Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}${CHECK} .env created${NC}"
    echo -e "${YELLOW}${WARN} You must configure email credentials in .env${NC}"
    ALL_PASSED=false
fi

# Check database
echo ""
echo -e "${BLUE}━━━ Step 5: Database ━━━${NC}"
if [ -f "roster.db" ]; then
    echo -e "${GREEN}${CHECK} Database file exists${NC}"
else
    echo -e "${YELLOW}${WARN} Database not initialized${NC}"
    echo -e "${YELLOW}Initializing database...${NC}"
    poetry run python -c "from api.database import init_db; init_db()"
    echo -e "${GREEN}${CHECK} Database initialized${NC}"
fi

# Verify database models
if poetry run python -c "from api.models import Notification, EmailPreference, DeliveryLog" 2>/dev/null; then
    echo -e "${GREEN}${CHECK} Notification models verified${NC}"
else
    echo -e "${RED}${CROSS} Failed to import notification models${NC}"
    ALL_PASSED=false
fi

# Test email service import
echo ""
echo -e "${BLUE}━━━ Step 6: Notification System Components ━━━${NC}"
check_prerequisite \
    "Email Service" \
    "poetry run python -c 'from api.services.email_service import EmailService'" \
    "Check api/services/email_service.py"

check_prerequisite \
    "Notification Service" \
    "poetry run python -c 'from api.services.notification_service import create_assignment_notifications'" \
    "Check api/services/notification_service.py"

check_prerequisite \
    "Celery Tasks" \
    "poetry run python -c 'from api.tasks.notifications import send_email_task'" \
    "Check api/tasks/notifications.py"

check_prerequisite \
    "Notifications Router" \
    "poetry run python -c 'from api.routers.notifications import router'" \
    "Check api/routers/notifications.py"

check_prerequisite \
    "Notification Schemas" \
    "poetry run python -c 'from api.schemas.notifications import NotificationResponse'" \
    "Check api/schemas/notifications.py"

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}${CHECK} ALL PREREQUISITES PASSED${NC}"
    echo ""
    echo -e "${GREEN}${ROCKET} Ready for manual validation!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. Configure email credentials in .env"
    echo -e "  2. Open 3 terminals"
    echo -e "  3. Follow: ${YELLOW}docs/MANUAL_VALIDATION_GUIDE.md${NC}"
    echo ""
    echo -e "${BLUE}Quick start:${NC}"
    echo -e "  ${YELLOW}Terminal 1:${NC} poetry run uvicorn api.main:app --reload"
    echo -e "  ${YELLOW}Terminal 2:${NC} poetry run celery -A api.celery_app worker --loglevel=info"
    echo -e "  ${YELLOW}Terminal 3:${NC} # Testing commands"
else
    echo -e "${RED}${CROSS} SOME PREREQUISITES FAILED${NC}"
    echo ""
    echo -e "${YELLOW}Fix the issues above and run this script again.${NC}"
    echo -e "${YELLOW}For detailed troubleshooting: docs/MANUAL_VALIDATION_GUIDE.md${NC}"
    exit 1
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
