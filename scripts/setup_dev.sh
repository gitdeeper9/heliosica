#!/bin/bash
"""
HELIOSICA Development Environment Setup Script
"""

echo "========================================="
echo "HELIOSICA Development Environment Setup"
echo "========================================="

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode
echo "📦 Installing HELIOSICA in development mode..."
pip install -e .

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/raw/soho
mkdir -p data/raw/dscovr
mkdir -p data/raw/omni
mkdir -p data/raw/nmdb
mkdir -p data/validation
mkdir -p data/thresholds
mkdir -p data/calibration
mkdir -p data/sample
mkdir -p logs
mkdir -p output/reports
mkdir -p output/figures
mkdir -p cache

# Initialize database
echo "🗄️ Initializing database..."
python scripts/init_db.py

# Download sample data
echo "📥 Downloading sample data..."
python scripts/download_validation_data.py --sample

echo ""
echo "========================================="
echo "✅ Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Run tests: python scripts/run_tests.py"
echo "  3. Start dashboard: heliosica serve"
echo ""
