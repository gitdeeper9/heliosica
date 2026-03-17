# 🤝 Contributing to HELIOSICA

## Heliospheric Event and L1 Integrated Observatory for Solar Intelligence and Coronal Activity

**DOI**: 10.5281/zenodo.19042948  
**Repository**: github.com/gitdeeper9/heliosica  
**Web**: heliosica.netlify.app

---

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Contributing to Physics Modules](#contributing-to-physics-modules)
- [Contributing to Data Processing](#contributing-to-data-processing)
- [Contributing to Documentation](#contributing-to-documentation)
- [Testing Guidelines](#testing-guidelines)
- [Data Contributions](#data-contributions)
- [Pull Request Process](#pull-request-process)

---

## 📜 Code of Conduct

### Our Pledge
We as members, contributors, and leaders pledge to make participation in the HELIOSICA community a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
Examples of behavior that contributes to a positive environment:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members
- Acknowledging the importance of space weather research
- Promoting open science and reproducible research

### Enforcement
Instances of abuse: gitdeeper@gmail.com

---

## 🚀 Getting Started

### Prerequisites
```bash
python --version  # 3.9-3.11
git --version     # 2.30+
docker --version  # 20.10+ (optional)
```

Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/heliosica.git
cd heliosica
git remote add upstream https://github.com/gitdeeper9/heliosica.git
```

Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .[dev]
pre-commit install
```

---

🔄 Development Workflow

Branch Naming

· feature/ - New features (e.g., feature/bz-prediction)
· bugfix/ - Bug fixes (e.g., bugfix/dbm-convergence)
· docs/ - Documentation (e.g., docs/api-refactor)
· physics/ - Physics updates (e.g., physics/gamma-calibration)
· data/ - Data contributions (e.g., data/new-storm-2026)

Process

```bash
git checkout main
git pull upstream main
git checkout -b feature/your-feature
# make changes
pytest tests/ -v
git commit -m "feat: add your feature"
git push origin feature/your-feature
# create Pull Request
```

Commit Messages

```
feat: add Bz prediction from coronagraph
fix: correct magnetopause calculation
docs: update GSSI thresholds
physics: refine Ey-Kp coupling function
data: add 2026 Halloween storm data
```

---

🔬 Physics Modules

1. Drag-Based Model (DBM)

```python
# heliosica/physics/dbm.py
def dbm_solver(V0, Vsw, gamma, t):
    """
    dV/dt = -γ(V - Vsw)|V - Vsw|
    
    Parameters
    ----------
    V0 : float
        Initial CME velocity (km/s)
    Vsw : float
        Solar wind speed (km/s)
    gamma : float
        Drag parameter (km⁻¹)
    t : float
        Time (hours)
    
    Returns
    -------
    float : Velocity at time t
    """
    # Implementation
    pass
```

2. Magnetopause Standoff

```python
# heliosica/physics/magnetopause.py
def magnetopause_distance(P_ram):
    """
    R_MP = R_E · (B_E² / (2μ₀·P_ram))^(1/6)
    
    Parameters
    ----------
    P_ram : float
        Ram pressure (nPa)
    
    Returns
    -------
    float : Standoff distance (R_E)
    """
    R_E = 6371
    B_E = 31000e-9
    mu0 = 4e-7 * np.pi
    return R_E * (B_E**2 / (2 * mu0 * P_ram * 1e-9))**(1/6) / R_E
```

3. Reconnection Electric Field

```python
# heliosica/physics/reconnection.py
def ey_field(Vsw, Bz):
    """
    Ey = Vsw · |Bz|  (Bz < 0 only)
    
    Parameters
    ----------
    Vsw : float
        Solar wind velocity (km/s)
    Bz : float
        IMF Bz component (nT)
    
    Returns
    -------
    float : Ey in mV/m
    """
    return 0.0 if Bz >= 0 else Vsw * abs(Bz)
```

4. Kp Predictor

```python
# heliosica/physics/kp_predictor.py
def predict_kp(Ey, P_ram, V, theta_IMF):
    """
    Kp = α₁·ln(1+Ey) + α₂·ln(P_ram/2.1) + α₃·(V/400)^0.78 + α₄·cos(θ) + 1.0
    α₁=1.82, α₂=0.64, α₃=0.41, α₄=0.35
    """
    term1 = 1.82 * np.log(1 + Ey)
    term2 = 0.64 * np.log(P_ram / 2.1)
    term3 = 0.41 * (V / 400)**0.78
    term4 = 0.35 * np.cos(np.radians(theta_IMF))
    return np.clip(term1 + term2 + term3 + term4 + 1.0, 0, 9)
```

5. Forbush Decrease

```python
# heliosica/physics/forbush.py
def fd_index(J0, Jmin):
    """
    Fd(%) = (J₀ - J_min)/J₀ × 100
    """
    return (J0 - Jmin) / J0 * 100
```

6. GSSI Composite

```python
# heliosica/physics/gssi.py
def compute_gssi(params):
    """
    GSSI = 0.23·Ey + 0.19·Bz + 0.16·P_ram + 0.13·V₀ +
           0.10·γ + 0.08·ω + 0.06·Tp + 0.03·Fd + 0.02·Kp
    
    Returns
    -------
    float : 0-1
        <0.20: G0-G1 | 0.20-0.45: G2-G3
        0.45-0.70: G4 | >0.70: G5
    """
    weights = {'Ey':0.23, 'Bz':0.19, 'P_ram':0.16, 'V0':0.13,
               'gamma':0.10, 'omega':0.08, 'Tp':0.06, 'Fd':0.03, 'Kp':0.02}
    return sum(weights[k] * _normalize(params[k]) for k in params)
```

---

📊 Data Loaders

DSCOVR Real-time

```python
# heliosica/data/loaders/dscovr.py
class DSCOVRLoader:
    """1-minute cadence L1 data"""
    def get_current(self):
        """Bx, By, Bz, Vsw, np, Tp"""
        pass
```

SOHO/LASCO CME Catalogue

```python
# heliosica/data/loaders/soho.py
class SOHOLoader:
    """CME parameters: V0, ω"""
    def get_cme(self, date):
        pass
```

OMNI Dataset

```python
# heliosica/data/loaders/omni.py
class OMNILoader:
    """Historical solar wind data"""
    def get_hourly(self, start, end):
        pass
```

NMDB Neutron Monitors

```python
# heliosica/data/loaders/nmdb.py
class NMDBLoader:
    """Forbush decrease detection"""
    def get_counts(self, station='oulu'):
        pass
```

---

🧪 Testing

Directory Structure

```
tests/
├── unit/
│   ├── physics/
│   │   ├── test_dbm.py
│   │   ├── test_magnetopause.py
│   │   ├── test_reconnection.py
│   │   ├── test_kp_predictor.py
│   │   ├── test_forbush.py
│   │   └── test_gssi.py
│   └── data/
│       └── test_loaders.py
├── integration/
│   ├── test_full_pipeline.py
│   └── test_312_events.py
└── validation/
    ├── test_halloween_2003.py
    └── test_patricks_day_2015.py
```

Example Test

```python
# tests/unit/physics/test_dbm.py
def test_dbm_halloween():
    """Test DBM on 2003 Halloween event"""
    V0 = 2459  # km/s
    Vsw = 650  # km/s
    gamma = 1.2e-7
    t_pred = dbm_solver(V0, Vsw, gamma, arrival=True)
    t_obs = 19.5  # hours
    assert abs(t_pred - t_obs) < 1.0
```

Run Tests

```bash
pytest tests/ -v
pytest tests/ --cov=heliosica
pytest tests/unit/physics/test_dbm.py -v
```

---

📝 Pull Request Checklist

· Code follows style guide (black, isort)
· Tests added/updated and passing
· Documentation updated
· CHANGELOG.md updated
· CI checks passing
· Physics changes validated (RMSE targets)
· New parameters documented

---

📄 License

By contributing, you agree to the MIT License.

---

Contact: gitdeeper@gmail.com · ORCID: 0009-0003-8903-0029
