#!/bin/bash
# Database Backup Script for Rostio
# Automatically backs up SQLite database with rotation

set -e

# Configuration
DB_FILE="roster.db"
BACKUP_DIR="backups/database"
MAX_BACKUPS=30  # Keep 30 days of backups
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="roster_backup_${DATE}.db"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗄️  Rostio Database Backup${NC}"
echo "==============================="

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo -e "${RED}❌ Error: Database file '$DB_FILE' not found!${NC}"
    exit 1
fi

# Get database size
DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
echo -e "${BLUE}📊 Database size: $DB_SIZE${NC}"

# Perform backup
echo -e "${BLUE}💾 Creating backup...${NC}"
cp "$DB_FILE" "$BACKUP_DIR/$BACKUP_FILE"

# Verify backup
if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup created: $BACKUP_FILE ($BACKUP_SIZE)${NC}"
else
    echo -e "${RED}❌ Backup failed!${NC}"
    exit 1
fi

# Compress backup to save space
echo -e "${BLUE}🗜️  Compressing backup...${NC}"
gzip "$BACKUP_DIR/$BACKUP_FILE"
COMPRESSED_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_FILE}.gz" | cut -f1)
echo -e "${GREEN}✅ Compressed to: ${BACKUP_FILE}.gz ($COMPRESSED_SIZE)${NC}"

# Rotate old backups (keep only last MAX_BACKUPS)
echo -e "${BLUE}🔄 Rotating old backups...${NC}"
cd "$BACKUP_DIR"
BACKUP_COUNT=$(ls -1 roster_backup_*.db.gz 2>/dev/null | wc -l)

if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    DELETE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
    ls -1t roster_backup_*.db.gz | tail -n "$DELETE_COUNT" | xargs rm -f
    echo -e "${GREEN}✅ Deleted $DELETE_COUNT old backups${NC}"
fi

cd - > /dev/null

# Show backup summary
echo ""
echo -e "${GREEN}✅ Backup Complete!${NC}"
echo "================================"
echo "Backup location: $BACKUP_DIR/${BACKUP_FILE}.gz"
echo "Total backups: $(ls -1 $BACKUP_DIR/roster_backup_*.db.gz 2>/dev/null | wc -l)"
echo ""

# List recent backups
echo "Recent backups:"
ls -lht "$BACKUP_DIR" | head -n 6

# Optional: Upload to cloud storage (uncomment and configure)
# echo ""
# echo "📤 Uploading to cloud storage..."
# aws s3 cp "$BACKUP_DIR/${BACKUP_FILE}.gz" s3://your-bucket/rostio-backups/
# echo "✅ Cloud backup complete!"
