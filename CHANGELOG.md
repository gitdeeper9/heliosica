# Changelog

All notable changes to the HELIOSICA project will be documented in this file.

**DOI:** 10.5281/zenodo.19042948  
**Repository:** github.com/gitdeeper9/heliosica  
**Web Dashboard:** heliosica.netlify.app

---

## [1.0.0] - 2026-03-14

### 🚀 Initial Release
- Publication of HELIOSICA research paper
- Release of complete 9-parameter Solar Plasma Intelligence Nonet (SPIN) framework
- 312 historical geomagnetic storm events validated (1996-2025)
- GSSI (Geomagnetic Storm Severity Index) formulation with 88.4% accuracy
- Open access data from SOHO/LASCO, DSCOVR, ACE, and OMNI datasets
- PostgreSQL database integration with live dashboard
- Netlify deployment with real-time API endpoints

### Added

#### Core Physics Engine
- **CME Launch Velocity (V₀)** : Initial ejecta speed at 21.5 R☉
  - Range: 250 - 3,000 km/s
  - Carrington Event (1859): ~2,400 km/s
  - From SOHO/LASCO coronagraph measurements

- **Southward IMF Component (Bz)** : Decisive geoeffectiveness factor
  - Range: -50 to +50 nT
  - G5 threshold: Bz < -30 nT sustained
  - From DSCOVR magnetometer (1-min cadence)

- **Solar Wind Ram Pressure (P_ram)** : Magnetospheric compression force
  - P_ram = m_p·n_p·V²_sw
  - Range: 1-50 nPa
  - Nominal: 2-3 nPa | Extreme: 30+ nPa

- **Drag Interaction Coefficient (γ)** : Heliospheric deceleration parameter
  - Units: km⁻¹
  - γ = k / (ω²·n_p) with k = 2.0×10⁻⁷
  - Inferred from CME geometry and ambient density

- **CME Angular Spread (ω)** : Ejecta geometry
  - Range: 30° - 360° (halo CME)
  - Mean: 47° from 34,000+ SOHO/LASCO CMEs
  - Determines Earth-impact probability

- **Proton Thermal Temperature (Tp)** : Plasma thermodynamic signature
  - Tp > 2× polytropic prediction → CME sheath detected
  - Range: 10⁴ - 10⁶ K
  - From DSCOVR Faraday cup

- **Reconnection Electric Field (Ey)** : Energy injection rate
  - Ey = Vsw·|Bz| for Bz < 0
  - Range: 0-50 mV/m
  - G5 threshold: Ey > 12 mV/m

- **Forbush Decrease Index (Fd)** : Cosmic ray suppression
  - Fd(%) = (J₀ - J_min)/J₀ × 100
  - Range: 1-15%
  - Fd > 3%: magnetic cloud core confirmed

- **Kp Geomagnetic Activity Index** : Planetary disturbance
  - Scale: 0-9 (3-hour)
  - G1: Kp=5 | G5: Kp=9
  - Primary validation target

#### Drag-Based Model (DBM)
- dV/dt = -γ(V - Vsw)|V - Vsw|
- Analytical solution for CME transit time
- Ensemble forecasting with 10,000 Monte Carlo members
- RMSE = 4.2 ± 0.8 hours (41% improvement over WSA-Enlil)

#### Magnetopause Standoff Distance
- R_MP = R_E · (B_E² / (2μ₀·P_ram))^(1/6)
- Nominal: 10-12 R_E
- Extreme (G5): < 5 R_E
- Satellite safety alert when R_MP < 7.0 R_E

#### Geomagnetic Storm Severity Index (GSSI)
- GSSI = 0.23·Ey + 0.19·Bz + 0.16·P_ram + 0.13·V₀ + 0.10·γ + 0.08·ω + 0.06·Tp + 0.03·Fd + 0.02·Kp
- Normalized to [0,1]
- GSSI < 0.20: G0-G1 (minor)
- GSSI 0.20-0.45: G2-G3 (moderate-strong)
- GSSI 0.45-0.70: G4 (severe - satellite alert)
- GSSI > 0.70: G5 (extreme - grid protection)

#### Kp Predictor Function
- Kp = α₁·ln(1+Ey) + α₂·ln(P_ram/P₀) + α₃·(V/V₀)^β + α₄·cos(θ_IMF) + Kp_base
- α₁=1.82, α₂=0.64, α₃=0.41, β=0.78, α₄=0.35, Kp_base=1.0
- r² = 0.91 against 312 validation events

#### Database Integration
- **PostgreSQL on Supabase**
  - Tables: alerts, api_keys, cme_events, dst_data, forbush_events, gssi_data, kp_data, magnetometer_stations, magnetopause_data, neutron_data, neutron_stations, satellites, solar_wind, storm_events
  - Row Level Security (RLS) configured for public read access
  - 312 storms with complete SPIN parameters
  - 53 stations worldwide (20 neutron, 29 magnetometer, 4 satellites)

- **API Endpoints (Netlify Functions)**
  - `/api/current` - Current solar wind and GSSI
  - `/api/gssi` - GSSI time series data
  - `/api/stations` - All stations for map
  - `/api/events` - Historical storm events
  - `/api/alerts` - Active alerts
  - `/api/stats` - Database statistics
  - `/api/forecast` - 48-hour GSSI forecast

#### Dashboard Features
- **Live Data Display**: Real-time GSSI and solar wind data
- **Interactive Map**: 53 stations worldwide with color coding
- **GSSI Gauge**: Current storm severity (G0: 0.263)
- **SPIN Parameters**: Nine-parameter framework visualization
- **GSSI Trends**: 7-day historical chart
- **Storm Alerts**: G4+ notifications
- **Auto-refresh**: Updates every 60 seconds
- **Supabase Integration**: Real PostgreSQL database connection

#### Performance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| CME Arrival Time RMSE | 4.2 hrs | ≤5.0 hrs | ✅ |
| Kp Prediction r² | 0.91 | ≥0.90 | ✅ |
| GSSI Classification Accuracy | 88.4% | ≥85% | ✅ |
| Magnetopause R_MP RMSE | 0.71 R_E | ≤0.8 R_E | ✅ |
| Ey-Kp Correlation (r) | 0.871 | p < 0.001 | ✅ |
| Events in Catalogue | 312 | ≥300 | ✅ |
| Major Storms (G4+) | 47 | ≥40 | ✅ |
| Warning Lead Time | 24-48 hrs | N/A | ✅ |
| Active Stations | 53 | ≥50 | ✅ |

#### Key Events in Validation Catalogue

| Event | Date | Kp | Dst (nT) | GSSI |
|-------|------|----|----------|------|
| Halloween Superstorm | 29 Oct 2003 | 9 | -383 | 0.88 |
| Bastille Day | 14 Jul 2000 | 9 | -301 | 0.85 |
| March 1989 Storm | 13 Mar 1989 | 9 | -589 | 0.91 |
| St. Patrick's Day | 17 Mar 2015 | 8 | -223 | 0.61 |
| Halloween 2024 | 28 Oct 2024 | 8 | -245 | 0.63 |
| Carrington Event | 01 Sep 1859 | 9 | -1760 | 0.92 |

---

## [0.9.0] - 2026-02-20

### ⚠️ Pre-release Candidate

### Added
- Beta version of all core modules
- Validation against 250 storms
- Preliminary GSSI weight determination
- Basic data loaders
- Initial documentation
- PostgreSQL schema design

### Changed
- Refined DBM fitting algorithms
- Updated Ey-Kp calibration
- Improved Forbush detection

### Fixed
- DBMSolver edge cases
- Thermal anomaly detection
- Covariance matrix calculations

---

## [0.8.0] - 2026-01-25

### 🧪 Alpha Release

### Added
- Prototype physics modules
- Test deployments with OMNI data
- Basic data collection pipeline
- Preliminary GSSI formulation
- Initial storm case studies

---

## [0.5.0] - 2025-10-10

### 🏗️ Development Milestone

### Added
- DBM implementation
- Basic solar wind handling
- Kp prediction prototype
- Data ingestion from OMNI

---

## [0.1.0] - 2025-07-01

### 🎯 Project Initiation

### Added
- Project concept and framework design
- Initial 9-parameter selection
- Literature review compilation
- Research proposal development
- Data access agreements

---

## 🔮 Future Releases

### [1.1.0] - Planned Q2 2026
- Bz prediction from coronagraph observations
- Multi-CME interaction module
- Radiation belt electron forecasting
- Mobile app version

### [1.2.0] - Planned Q3 2026
- Machine learning for Bz prediction
- Real-time data from Solar Orbiter
- Additional validation (2026 data)
- Exoplanet space weather module

### [2.0.0] - Planned 2027
- Full 3D MHD simulation coupling
- AI-powered storm prediction
- Real-time global magnetometer network
- Planetary space weather (Mars, Moon)

---

## 📊 Version History

| Version | Date | Status | DOI |
|---------|------|--------|-----|
| 1.0.0 | 2026-03-14 | Stable Release | 10.5281/zenodo.19042948 |
| 1.0.1 | 2026-03-16 | Dashboard Update | 10.5281/zenodo.19042948 |
| 0.9.0 | 2026-02-20 | Release Candidate | 10.5281/zenodo.18982026 |
| 0.8.0 | 2026-01-25 | Alpha | 10.5281/zenodo.18882026 |
| 0.5.0 | 2025-10-10 | Development | - |
| 0.1.0 | 2025-07-01 | Concept | - |

---

## 📝 Latest Updates (2026-03-16)

### ✅ Dashboard Improvements
- Integrated Supabase PostgreSQL database with real data
- Added interactive map with 53 stations worldwide
- Implemented live GSSI tracking (current: 0.263)
- Created 7-day GSSI trends chart
- Added SPIN parameters visualization
- Fixed API endpoints for current, stations, and gssi data
- Configured Row Level Security (RLS) for public read access
- Deployed to Netlify with environment variables

### ✅ Database Schema
- Created 15 tables for complete space weather monitoring
- Inserted real data: 53 stations, 312 events, 57 GSSI records
- Added satellite, neutron monitor, and magnetometer stations
- Implemented storm events catalogue with historical data

### ✅ API Endpoints
- `/api/current` - Real-time space weather conditions
- `/api/stations` - 53 stations for map visualization
- `/api/gssi` - GSSI time series data for charts
- `/api/events` - Historical storm events
- `/api/alerts` - Active alerts from database
- `/api/stats` - Database statistics

---

For questions or contributions: gitdeeper@gmail.com · ORCID: 0009-0003-8903-0029
