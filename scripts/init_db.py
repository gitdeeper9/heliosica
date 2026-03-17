#!/usr/bin/env python3
"""
Initialize HELIOSICA database
Create tables and load reference data
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from heliosica.utils.file_utils import FileUtils
from heliosica.utils.constants import *


def create_sqlite_db(db_path='heliosica.db'):
    """Create SQLite database"""
    print(f"Creating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript('''
        -- CME events table
        CREATE TABLE IF NOT EXISTS cmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            velocity REAL,
            width REAL,
            pa REAL,
            halo BOOLEAN,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Solar wind measurements
        CREATE TABLE IF NOT EXISTS solar_wind (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            bx REAL,
            by REAL,
            bz REAL,
            bt REAL,
            vsw REAL,
            np REAL,
            tp REAL,
            source TEXT,
            quality REAL
        );
        
        -- Kp index
        CREATE TABLE IF NOT EXISTS kp_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            kp_value REAL,
            kp_category TEXT,
            source TEXT
        );
        
        -- Dst index
        CREATE TABLE IF NOT EXISTS dst_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            dst_value REAL,
            source TEXT
        );
        
        -- Forbush events
        CREATE TABLE IF NOT EXISTS forbush_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            onset_time TEXT NOT NULL,
            minimum_time TEXT,
            recovery_time TEXT,
            fd_percent REAL,
            b_cloud REAL,
            magnitude TEXT,
            cloud_confirmed BOOLEAN,
            station TEXT
        );
        
        -- GSSI predictions
        CREATE TABLE IF NOT EXISTS gssi_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            gssi_value REAL,
            category TEXT,
            ey REAL,
            bz REAL,
            p_ram REAL,
            v0 REAL,
            gamma REAL,
            omega REAL,
            tp REAL,
            fd REAL,
            kp REAL,
            confidence REAL
        );
        
        -- Storm events catalogue
        CREATE TABLE IF NOT EXISTS storm_catalogue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date TEXT NOT NULL,
            event_name TEXT,
            kp_max REAL,
            dst_min REAL,
            gssi_max REAL,
            v0 REAL,
            omega REAL,
            vsw REAL,
            np REAL,
            bz_min REAL,
            description TEXT
        );
        
        -- Stations
        CREATE TABLE IF NOT EXISTS stations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            type TEXT,
            country TEXT,
            active BOOLEAN
        );
    ''')
    
    # Insert reference data
    
    # Insert neutron monitor stations
    stations = [
        ('oulu', 'Oulu', 65.05, 25.47, 15, 'neutron', 'Finland', 1),
        ('climax', 'Climax', 39.37, -106.18, 3400, 'neutron', 'USA', 1),
        ('mcmurdo', 'McMurdo', -77.85, 166.72, 48, 'neutron', 'Antarctica', 1),
        ('newark', 'Newark', 39.68, -75.75, 50, 'neutron', 'USA', 1),
        ('junge', 'Jungfraujoch', 46.55, 7.98, 3570, 'neutron', 'Switzerland', 1),
        ('thule', 'Thule', 76.5, -68.8, 10, 'magnetometer', 'Greenland', 1),
        ('yellowknife', 'Yellowknife', 62.5, -114.5, 200, 'magnetometer', 'Canada', 1),
        ('leirvogur', 'Leirvogur', 64.2, -21.7, 50, 'magnetometer', 'Iceland', 1)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO stations (code, name, latitude, longitude, altitude, type, country, active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', stations)
    
    # Insert validation events
    events = [
        ('2003-10-29', 'Halloween 2003', 9.0, -383, 0.88, 2459, 360, 650, 15, -12.1,
         'Extreme storm during Solar Cycle 23, caused satellite damage and power outages'),
        ('2000-07-14', 'Bastille Day 2000', 9.0, -301, 0.85, 1674, 360, 580, 12, -15.2,
         'Major storm with aurora visible at mid-latitudes'),
        ('2015-03-17', "St. Patrick's Day 2015", 8.0, -223, 0.61, 769, 120, 620, 8.5, -11.8,
         'Strongest storm of Solar Cycle 24'),
        ('2024-10-28', 'Halloween 2024', 8.0, -245, 0.63, 1850, 300, 600, 10, -14.5,
         'Recent G4 storm'),
        ('1989-03-13', 'March 1989', 9.0, -589, 0.91, 2100, 360, 700, 20, -18.0,
         'Quebec blackout event')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO storm_catalogue 
        (event_date, event_name, kp_max, dst_min, gssi_max, v0, omega, vsw, np, bz_min, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', events)
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully")
    return db_path


def create_postgresql_schema():
    """Generate PostgreSQL schema SQL"""
    schema = '''
-- HELIOSICA PostgreSQL Schema
-- Run this on your PostgreSQL server

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- CME events table
CREATE TABLE IF NOT EXISTS cmes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date TIMESTAMPTZ NOT NULL,
    velocity REAL,
    width REAL,
    pa REAL,
    halo BOOLEAN,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on date
CREATE INDEX IF NOT EXISTS idx_cmes_date ON cmes(date);

-- Solar wind measurements (use TimescaleDB hypertable)
CREATE TABLE IF NOT EXISTS solar_wind (
    time TIMESTAMPTZ NOT NULL,
    bx REAL,
    by REAL,
    bz REAL,
    bt REAL,
    vsw REAL,
    np REAL,
    tp REAL,
    source TEXT,
    quality REAL
);

-- Convert to hypertable for time-series
SELECT create_hypertable('solar_wind', 'time', if_not_exists => TRUE);

-- Kp index
CREATE TABLE IF NOT EXISTS kp_index (
    time TIMESTAMPTZ NOT NULL,
    kp_value REAL,
    kp_category TEXT,
    source TEXT
);

SELECT create_hypertable('kp_index', 'time', if_not_exists => TRUE);

-- Dst index
CREATE TABLE IF NOT EXISTS dst_index (
    time TIMESTAMPTZ NOT NULL,
    dst_value REAL,
    source TEXT
);

SELECT create_hypertable('dst_index', 'time', if_not_exists => TRUE);

-- Forbush events
CREATE TABLE IF NOT EXISTS forbush_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    onset_time TIMESTAMPTZ NOT NULL,
    minimum_time TIMESTAMPTZ,
    recovery_time TIMESTAMPTZ,
    fd_percent REAL,
    b_cloud REAL,
    magnitude TEXT,
    cloud_confirmed BOOLEAN,
    station TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- GSSI predictions
CREATE TABLE IF NOT EXISTS gssi_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    time TIMESTAMPTZ NOT NULL,
    gssi_value REAL,
    category TEXT,
    ey REAL,
    bz REAL,
    p_ram REAL,
    v0 REAL,
    gamma REAL,
    omega REAL,
    tp REAL,
    fd REAL,
    kp REAL,
    confidence REAL
);

SELECT create_hypertable('gssi_predictions', 'time', if_not_exists => TRUE);

-- Storm catalogue
CREATE TABLE IF NOT EXISTS storm_catalogue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_date DATE NOT NULL,
    event_name TEXT,
    kp_max REAL,
    dst_min REAL,
    gssi_max REAL,
    v0 REAL,
    omega REAL,
    vsw REAL,
    np REAL,
    bz_min REAL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stations
CREATE TABLE IF NOT EXISTS stations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE,
    name TEXT,
    latitude REAL,
    longitude REAL,
    altitude REAL,
    type TEXT,
    country TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_solar_wind_bz ON solar_wind (time DESC, bz);
CREATE INDEX IF NOT EXISTS idx_gssi_category ON gssi_predictions (time DESC, category);
CREATE INDEX IF NOT EXISTS idx_forbush_detected ON forbush_events (onset_time DESC, cloud_confirmed);

-- Insert reference data
INSERT INTO stations (code, name, latitude, longitude, altitude, type, country, active) VALUES
    ('oulu', 'Oulu', 65.05, 25.47, 15, 'neutron', 'Finland', true),
    ('climax', 'Climax', 39.37, -106.18, 3400, 'neutron', 'USA', true),
    ('mcmurdo', 'McMurdo', -77.85, 166.72, 48, 'neutron', 'Antarctica', true),
    ('thule', 'Thule', 76.5, -68.8, 10, 'magnetometer', 'Greenland', true)
ON CONFLICT (code) DO NOTHING;

-- Insert validation events
INSERT INTO storm_catalogue (event_date, event_name, kp_max, dst_min, gssi_max, v0, omega, vsw, np, bz_min, description) VALUES
    ('2003-10-29', 'Halloween 2003', 9.0, -383, 0.88, 2459, 360, 650, 15, -12.1,
     'Extreme storm during Solar Cycle 23, caused satellite damage and power outages'),
    ('2015-03-17', 'St. Patrick''s Day 2015', 8.0, -223, 0.61, 769, 120, 620, 8.5, -11.8,
     'Strongest storm of Solar Cycle 24')
ON CONFLICT DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW current_conditions AS
SELECT 
    time,
    bz,
    vsw,
    np,
    tp
FROM solar_wind
ORDER BY time DESC
LIMIT 1;

CREATE OR REPLACE VIEW recent_storms AS
SELECT 
    event_date,
    event_name,
    kp_max,
    dst_min,
    gssi_max
FROM storm_catalogue
WHERE event_date > NOW() - INTERVAL '1 year'
ORDER BY event_date DESC;

-- Create function to get GSSI statistics
CREATE OR REPLACE FUNCTION get_gssi_stats(
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ
)
RETURNS TABLE (
    avg_gssi REAL,
    max_gssi REAL,
    min_gssi REAL,
    stddev_gssi REAL,
    count_g4 BIGINT,
    count_g5 BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        AVG(gssi_value)::REAL,
        MAX(gssi_value)::REAL,
        MIN(gssi_value)::REAL,
        STDDEV(gssi_value)::REAL,
        COUNT(*) FILTER (WHERE category = 'G4')::BIGINT,
        COUNT(*) FILTER (WHERE category = 'G5')::BIGINT
    FROM gssi_predictions
    WHERE time BETWEEN start_time AND end_time;
END;
$$ LANGUAGE plpgsql;
'''
    
    # Write to file
    with open('scripts/postgresql_schema.sql', 'w') as f:
        f.write(schema)
    
    print("✅ PostgreSQL schema generated: scripts/postgresql_schema.sql")
    return schema


def main():
    """Main entry point"""
    print("=" * 60)
    print("HELIOSICA Database Initialization")
    print("=" * 60)
    
    # Create SQLite database
    db_path = create_sqlite_db('heliosica.db')
    
    # Generate PostgreSQL schema
    create_postgresql_schema()
    
    print("\n✅ Database initialization complete")
    print(f"📁 SQLite database: {db_path}")
    print("📁 PostgreSQL schema: scripts/postgresql_schema.sql")
    
    print("\nNext steps:")
    print("  1. For SQLite: sqlite3 heliosica.db")
    print("  2. For PostgreSQL: psql -f scripts/postgresql_schema.sql")


if __name__ == '__main__':
    main()
