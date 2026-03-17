#!/bin/bash
"""
HELIOSICA Backup Script
"""

set -e

echo "========================================="
echo "HELIOSICA Backup"
echo "========================================="

# Configuration
BACKUP_DIR="/backup/heliosica"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="heliosica_backup_$DATE"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
log_info "Creating backup directory..."
mkdir -p $BACKUP_DIR/$BACKUP_NAME

# Backup database
if [ -f "heliosica.db" ]; then
    log_info "Backing up SQLite database..."
    cp heliosica.db $BACKUP_DIR/$BACKUP_NAME/
    sqlite3 heliosica.db ".dump" > $BACKUP_DIR/$BACKUP_NAME/heliosica_dump.sql
else
    log_warn "No SQLite database found"
fi

# Backup PostgreSQL (if configured)
if command -v pg_dump &> /dev/null; then
    if [ -f ".env" ] && grep -q "DB_PASSWORD" .env; then
        log_info "Backing up PostgreSQL database..."
        source .env
        PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > $BACKUP_DIR/$BACKUP_NAME/postgres_dump.sql
    fi
fi

# Backup configuration
log_info "Backing up configuration files..."
cp -r config/* $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || log_warn "No config files found"
cp .env $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || log_warn "No .env file found"

# Backup data
log_info "Backing up data..."
if [ -d "data" ]; then
    # Exclude large raw data
    tar -czf $BACKUP_DIR/$BACKUP_NAME/data.tar.gz \
        --exclude="data/raw/*" \
        --exclude="data/cache/*" \
        data/
else
    log_warn "No data directory found"
fi

# Backup logs
log_info "Backing up logs..."
if [ -d "logs" ]; then
    tar -czf $BACKUP_DIR/$BACKUP_NAME/logs.tar.gz logs/
else
    log_warn "No logs directory found"
fi

# Create backup info file
log_info "Creating backup info..."
cat > $BACKUP_DIR/$BACKUP_NAME/backup_info.txt << EOF
HELIOSICA Backup
Date: $(date)
Version: $(python -c "import heliosica; print(heliosica.__version__)" 2>/dev/null || echo "unknown")
Backup ID: $BACKUP_NAME
Contents:
  - Database
  - Configuration
  - Data (excluding raw)
  - Logs
