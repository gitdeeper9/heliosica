#!/bin/bash
"""
HELIOSICA Production Deployment Script
"""

set -e  # Exit on error

echo "========================================="
echo "HELIOSICA Production Deployment"
echo "========================================="

# Configuration
APP_NAME="heliosica"
APP_DIR="/opt/heliosica"
BACKUP_DIR="/backup/heliosica"
LOG_DIR="/var/log/heliosica"
DATA_DIR="/data/heliosica"
CONFIG_DIR="/etc/heliosica"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root"
    exit 1
fi

# Create deployment directories
log_info "Creating deployment directories..."
mkdir -p $APP_DIR
mkdir -p $BACKUP_DIR
mkdir -p $LOG_DIR
mkdir -p $DATA_DIR
mkdir -p $CONFIG_DIR

# Copy application files
log_info "Copying application files..."
cp -r ../heliosica $APP_DIR/
cp ../requirements.txt $APP_DIR/
cp ../setup.py $APP_DIR/
cp ../README.md $APP_DIR/

# Create Python virtual environment
log_info "Creating Python virtual environment..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

# Install dependencies
log_info "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Install HELIOSICA
log_info "Installing HELIOSICA..."
pip install -e .

# Create systemd service
log_info "Creating systemd service..."
cat > /etc/systemd/system/heliosica.service << EOF
[Unit]
Description=HELIOSICA Space Weather Service
After=network.target

[Service]
Type=simple
User=heliosica
Group=heliosica
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="HELIOSICA_ENV=production"
ExecStart=$APP_DIR/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 heliosica.wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
