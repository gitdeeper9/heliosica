# ☀️ HELIOSICA Installation Guide v1.0.0
## Heliospheric Event and L1 Integrated Observatory for Solar Intelligence and Coronal Activity

**DOI**: 10.5281/zenodo.19042948  
**Repository**: github.com/gitdeeper9/heliosica  
**Web**: heliosica.netlify.app

---

## 📋 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+, Debian 11+, macOS 12+, Windows 10/11 (WSL2)
- **RAM**: 8 GB
- **Storage**: 50 GB free space
- **Python**: 3.9 - 3.11
- **CPU**: 4+ cores
- **Internet**: Required for real-time data

### Recommended Requirements
- **RAM**: 16+ GB
- **Storage**: 200+ GB SSD
- **CPU**: 8+ cores
- **Python**: 3.10
- **Internet**: 100 Mbps+

---

## 🚀 Quick Installation

### 1. Install via pip
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install heliosica
```

2. Quick Test

```bash
heliosica-download --sample --output ./sample_data
heliosica-process --event 2003-10-29 --input ./sample_data --output ./results
heliosica-gssi --event 2003-10-29
```

3. Start Dashboard

```bash
heliosica-serve --host 127.0.0.1 --port 5000
# Open: http://127.0.0.1:5000
```

---

📦 Installation Methods

Method A: pip Install

```bash
pip install heliosica[all]
```

Method B: From Source

```bash
git clone https://github.com/gitdeeper9/heliosica.git
cd heliosica
pip install -e .[dev]
pre-commit install
```

Method C: Docker

```bash
docker pull gitdeeper9/heliosica:latest
docker run -d -p 5000:5000 -p 8000:8000 gitdeeper9/heliosica:latest
```

---

🔧 Configuration

```bash
cp .env.example .env
nano .env  # Add your API keys
```

---

📊 Quick Examples

Real-time Monitoring

```python
import heliosica as hs
current = hs.get_current_conditions()
gssi = hs.compute_gssi(current)
print(f"Current GSSI: {gssi:.2f}")
```

CME Transit Prediction

```python
result = hs.dbm_forecast(V0=2459, omega=360, n_p=15)
print(f"Arrival: {result['arrival_50']:.1f} hours")
```

---

📞 Support

Email: gitdeeper@gmail.com
GitHub Issues: https://github.com/gitdeeper9/heliosica/issues

---

Version: 1.0.0 | 2026-03-14
