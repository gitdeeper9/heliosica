# ☀️ HELIOSICA Deployment Guide v1.0.0
## Heliospheric Event and L1 Integrated Observatory for Solar Intelligence and Coronal Activity

**DOI**: 10.5281/zenodo.19042948  
**Repository**: github.com/gitdeeper9/heliosica  
**Web**: heliosica.netlify.app

---

## 📋 Deployment Overview

### Deployment Architectures

| Architecture | Use Case | Resources | Update Frequency |
|-------------|----------|-----------|------------------|
| **Single Node** | Local research | 1 server (8GB RAM, 4 CPU) | On-demand |
| **Research Center** | Regional forecasting | 4-8 nodes (32GB RAM) | Real-time |
| **Cloud-Based** | Global public access | Auto-scaling | 1-min updates |
| **Edge** | Field stations | Raspberry Pi 4 | 5-min updates |

---

## 🏗️ Architecture Components

```

┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ StormForecaster│    │Magnetopause-  │    │ ForbushMonitor│
│ (Kp, GSSI)    │    │Tracker (R_MP) │    │ (Fd, B_cloud) │
└───────────────┘    └───────────────┘    └───────────────┘
│                    │                    │
└────────────────────┼────────────────────┘
▼
┌─────────────────┐
│  GSSI Composite │
│   (0-1 scale)   │
└────────┬────────┘
▼
┌────────────────────┼────────────────────┐
▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Alerts      │    │  Dashboard    │    │  API/REST     │
│ (Email/SMS)   │    │  (Netlify)    │    │  (JSON)       │
└───────────────┘    └───────────────┘    └───────────────┘

```

---

## 🔧 Local Deployment

### 1. Hardware Requirements

```yaml
Minimum:
  CPU: 4 cores
  RAM: 8 GB
  Storage: 50 GB
  Network: Internet for data

Recommended:
  CPU: 8 cores
  RAM: 16 GB
  Storage: 200 GB SSD
  Network: 100 Mbps+

Data Requirements:
  - SOHO/LASCO Catalogue: ~2 GB
  - DSCOVR Archive: ~500 GB (optional)
  - OMNI Dataset: ~100 GB
  - NMDB Data: ~50 GB
```

2. Installation

```bash
# System deps
sudo apt update && sudo apt install -y python3-pip docker.io git \
  libhdf5-dev libnetcdf-dev

# Clone
git clone https://github.com/gitdeeper9/heliosica.git
cd heliosica

# Configure
cp .env.example .env
nano .env  # Edit settings

# Install
pip install -e .[all]

# Create dirs
mkdir -p data/{raw,processed,cache} logs output

# Download sample data
heliosica-download --sample --output ./data/raw

# Test
heliosica-process --event 2003-10-29 --output ./output
```

3. Configuration File

```yaml
# config/config.yaml
project:
  name: "HELIOSICA"
  version: "1.0.0"
  data_dir: "./data"
  output_dir: "./output"

data_sources:
  soho:
    enabled: true
    source: "lasco_catalogue"
    local_path: "./data/raw/soho"
  
  dscovr:
    enabled: true
    real_time: true
    api_key: "${NOAA_API_KEY}"
  
  omni:
    enabled: true
    local_path: "./data/raw/omni"
  
  nmdb:
    enabled: true
    stations: ["oulu", "climax", "mcmurdo"]

spin_parameters:
  V0_range: [250, 3000]  # km/s
  Bz_range: [-50, 50]     # nT
  gamma_calibration: "k/(ω²·n_p)"
  ey_thresholds:
    G1: 2    # mV/m
    G3: 5
    G5: 12

dbm:
  ensemble_size: 10000
  uncertainty_bounds: [5, 95]  # percentiles
  gamma_default: 2.0e-7

gssi:
  weights:
    Ey: 0.23
    Bz: 0.19
    P_ram: 0.16
    V0: 0.13
    gamma: 0.10
    omega: 0.08
    Tp: 0.06
    Fd: 0.03
    Kp: 0.02
  
  thresholds:
    G1: 0.20
    G2: 0.30
    G3: 0.45
    G4: 0.70
    G5: 0.85

alerts:
  satellite:
    enabled: true
    threshold: 7.0  # R_E
    channels: ["email", "dashboard"]
  
  grid:
    enabled: true
    threshold: 0.70  # GSSI
    channels: ["email", "sms", "twitter"]

api:
  enabled: true
  host: "0.0.0.0"
  port: 8000
  rate_limit: 100

dashboard:
  enabled: true
  port: 5000
  update_interval: 60  # seconds
```

---

🌐 Cloud Deployment (AWS)

```bash
# 1. Launch EC2 (t2.large or better)
# 2. SSH and install
ssh -i key.pem ubuntu@ec2-ip

sudo apt update
sudo apt install -y python3-pip docker.io git
sudo systemctl start docker

git clone https://github.com/gitdeeper9/heliosica.git
cd heliosica
pip install -e .[all]

# 3. Set up environment
cp .env.example .env
nano .env  # Add API keys

# 4. Run with Docker
docker-compose up -d

# 5. Configure security group
# - HTTP (80) from 0.0.0.0/0
# - HTTPS (443) from 0.0.0.0/0
# - SSH from your IP only
```

Netlify Dashboard

```bash
cd dashboard
npm install
npm run build
netlify deploy --prod --dir=build --site=heliosica
```

---

🐳 Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  heliosica:
    image: gitdeeper9/heliosica:latest
    ports:
      - "5000:5000"  # Dashboard
      - "8000:8000"  # API
    volumes:
      - ./data:/data
      - ./config:/app/config
    environment:
      - HELIOSICA_ENV=production
      - DB_HOST=timescaledb
      - NOAA_API_KEY=${NOAA_API_KEY}
    depends_on:
      - timescaledb
      - redis

  timescaledb:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_DB=heliosica
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - timescaledb-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 1gb

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf

volumes:
  timescaledb-data:
```

---

📊 Monitoring

Prometheus Metrics

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'heliosica'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
```

Health Checks

```bash
curl http://localhost:5000/health
# {"status": "healthy", "version": "1.0.0"}

heliosica-db status
heliosica-validate --all
```

---

🚨 Alerts Configuration

Email Alerts (G4+)

```python
# config/alerts.py
ALERT_RULES = {
    'G4': {
        'threshold': 0.45,
        'channels': ['email', 'dashboard'],
        'emails': ['operator@center.edu']
    },
    'G5': {
        'threshold': 0.70,
        'channels': ['email', 'sms', 'twitter'],
        'emails': ['all-hands@center.edu']
    },
    'R_MP': {
        'threshold': 7.0,  # R_E
        'message': '⚠️ Satellites at risk! R_MP < 7.0'
    }
}
```

SMS via Twilio

```bash
export TWILIO_SID=your_sid
export TWILIO_TOKEN=your_token
export TWILIO_FROM=+1234567890
export ALERT_PHONES=+1987654321
```

---

📈 Scaling

Users RAM CPU Instances
1-10 8GB 2 1
10-50 16GB 4 1-2
50-200 32GB 8 2-4
200-1000 64GB 16 4-8

---

🔄 Backup

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/heliosica"

# Database
pg_dump -U heliosica_user heliosica > $BACKUP_DIR/db_$DATE.sql

# Data
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /data/heliosica

# Configs
cp /config/* $BACKUP_DIR/config/

# Keep 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

---

✅ Checklist

· System requirements met
· Dependencies installed
· .env configured
· Data downloaded
· Test calculations passed
· Alerts configured
· SSL certificates installed
· Backup strategy ready
· Monitoring set up

---

Contact: gitdeeper@gmail.com | v1.0.0 | 2026-03-14
