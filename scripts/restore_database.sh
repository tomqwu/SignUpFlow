#!/bin/bash
# Database Restore Script for Rostio
# Restores database from backup

set -e

BACKUP_DIR="backups/database"
DB_FILE="roster.db"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔄 Rostio Database Restore${NC}"
echo "==============================="

# List available backups
echo -e "${BLUE}📋 Available backups:${NC}"
if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
    echo -e "${RED}❌ No backups found in $BACKUP_DIR${NC}"
    exit 1
fi

ls -lht "$BACKUP_DIR" | grep "roster_backup_" | head -n 10

# Get user selection
echo ""
echo -e "${YELLOW}⚠️  This will REPLACE your current database!${NC}"
echo -e "${BLUE}Enter backup filename (or 'latest' for most recent):${NC}"
read -r BACKUP_CHOICE

# Handle 'latest' option
if [ "$BACKUP_CHOICE" = "latest" ]; then
    BACKUP_CHOICE=$(ls -1t "$BACKUP_DIR"/roster_backup_*.db.gz | head -n 1 | xargs basename)
    echo -e "${BLUE}Using latest backup: $BACKUP_CHOICE${NC}"
fi

BACKUP_PATH="$BACKUP_DIR/$BACKUP_CHOICE"

# Verify backup exists
if [ ! -f "$BACKUP_PATH" ]; then
    echo -e "${RED}❌ Backup file not found: $BACKUP_PATH${NC}"
    exit 1
fi

# Backup current database before restoring
if [ -f "$DB_FILE" ]; then
    SAFETY_BACKUP="${DB_FILE}.before_restore_$(date +%Y%m%d_%H%M%S)"
    echo -e "${BLUE}💾 Creating safety backup of current database...${NC}"
    cp "$DB_FILE" "$SAFETY_BACKUP"
    echo -e "${GREEN}✅ Safety backup: $SAFETY_BACKUP${NC}"
fi

# Decompress and restore
echo -e "${BLUE}🗜️  Decompressing backup...${NC}"
gunzip -c "$BACKUP_PATH" > "${DB_FILE}.tmp"

# Verify integrity using Python
echo -e "${BLUE}🔍 Verifying database integrity...${NC}"
if python3 -c "import sqlite3; conn = sqlite3.connect('${DB_FILE}.tmp'); cursor = conn.execute('PRAGMA integrity_check;'); result = cursor.fetchone()[0]; conn.close(); exit(0 if result == 'ok' else 1)"; then
    echo -e "${GREEN}✅ Database integrity check passed${NC}"
else
    echo -e "${RED}❌ Database integrity check failed!${NC}"
    rm "${DB_FILE}.tmp"
    exit 1
fi

# Replace database
mv "${DB_FILE}.tmp" "$DB_FILE"

echo ""
echo -e "${GREEN}✅ Database Restored Successfully!${NC}"
echo "==============================="
echo "Restored from: $BACKUP_CHOICE"
echo "Safety backup: $SAFETY_BACKUP"
echo ""
echo -e "${BLUE}💡 Test the application to ensure everything works correctly${NC}"
