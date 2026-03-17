"""
HELIOSICA CLI - Serve Command
Start web dashboard server
"""

import argparse
import sys
import os


def add_arguments(parser: argparse.ArgumentParser):
    """Add serve command arguments"""
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )


def run(args):
    """Execute serve command"""
    
    # Check if dashboard directory exists
    dashboard_dir = os.path.join(os.path.dirname(__file__), '../../dashboard')
    
    if not os.path.exists(dashboard_dir):
        print("Warning: Dashboard directory not found")
        print(f"Expected: {dashboard_dir}")
        
        # Create simple HTML if missing
        create_simple_dashboard(dashboard_dir)
    
    # Try to import flask
    try:
        from flask import Flask, jsonify, send_from_directory
    except ImportError:
        print("Error: Flask not installed")
        print("Install with: pip install flask")
        sys.exit(1)
    
    # Create Flask app
    app = Flask(__name__, static_folder=dashboard_dir)
    
    @app.route('/')
    def index():
        return send_from_directory(dashboard_dir, 'index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return send_from_directory(dashboard_dir, 'dashboard.html')
    
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'service': 'HELIOSICA'
        })
    
    @app.route('/api/current')
    def current():
        """Get current space weather conditions"""
        try:
            from heliosica.data.loaders.dscovr import DSCOVRLoader
            from heliosica.physics.gssi import GeomagneticStormSeverityIndex
            from heliosica.physics.kp_predictor import KpPredictor
            from heliosica.physics.magnetopause import MagnetopauseTracker
            
            dscovr = DSCOVRLoader()
            data = dscovr.get_current()
            
            if not data:
                return jsonify({'error': 'No data available'}), 503
            
            # Compute derived parameters
            mp = 1.67e-27
            p_ram = mp * data.np * 1e6 * (data.vsw * 1000)**2 * 1e9
            ey = data.vsw * abs(data.bz) if data.bz < 0 else 0
            theta = 180 if data.bz < 0 else 0
            
            kp_pred = KpPredictor()
            kp_result = kp_pred.predict(ey, p_ram, data.vsw, theta)
            
            gssi = GeomagneticStormSeverityIndex()
            params = {
                'Ey': ey, 'Bz': data.bz, 'P_ram': p_ram,
                'V0': 0, 'gamma': 0, 'omega': 0,
                'Tp': data.tp, 'Fd': 0, 'Kp': kp_result.kp_value
            }
            gssi_result = gssi.compute(params)
            
            mp_tracker = MagnetopauseTracker()
            mp_result = mp_tracker.update(p_ram)
            
            return jsonify({
                'timestamp': data.timestamp.isoformat(),
                'solar_wind': {
                    'bz': data.bz,
                    'vsw': data.vsw,
                    'np': data.np,
                    'tp': data.tp
                },
                'indices': {
                    'ey': ey,
                    'kp': kp_result.kp_value,
                    'kp_category': kp_result.g_category,
                    'gssi': gssi_result.gssi,
                    'gssi_category': gssi_result.category
                },
                'magnetosphere': {
                    'r_mp': mp_result.r_mp_re,
                    'satellite_alert': mp_result.satellite_alert
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/forecast')
    def forecast():
        """Get forecast"""
        return jsonify({
            'forecast': 'Coming soon',
            'lead_time': '24-48 hours'
        })
    
    # Start server
    print(f"\n🚀 Starting HELIOSICA web dashboard")
    print(f"📡 URL: http://{args.host}:{args.port}")
    print(f"📊 Dashboard: http://{args.host}:{args.port}/dashboard")
    print(f"🔧 API: http://{args.host}:{args.port}/api/current")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


def create_simple_dashboard(dashboard_dir):
    """Create simple HTML dashboard if missing"""
    os.makedirs(dashboard_dir, exist_ok=True)
    
    # Create index.html
    with open(os.path.join(dashboard_dir, 'index.html'), 'w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>HELIOSICA Dashboard</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body { font-family: Arial; margin: 40px; background: #0a0f1e; color: #e0e0e0; }
        .container { max-width: 1200px; margin: auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { color: #ffaa00; font-size: 48px; margin: 0; }
        .header p { color: #8899aa; }
        .panel { background: #1a1f2e; border-radius: 10px; padding: 20px; margin: 20px 0; border: 1px solid #2a2f3e; }
        .gssi-gauge { font-size: 72px; text-align: center; padding: 20px; }
        .g0 { color: #00ff00; } .g1 { color: #aaff00; } .g2 { color: #ffff00; }
        .g3 { color: #ffaa00; } .g4 { color: #ff5500; } .g5 { color: #ff0000; }
        .alert { background: #ff000022; border-left: 5px solid #ff0000; padding: 10px; margin: 10px 0; }
        .footer { text-align: center; color: #8899aa; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>☀️ HELIOSICA</h1>
            <p>Real-time Space Weather Monitor</p>
        </div>
        
        <div class="panel" id="current">
            <h2>Loading current conditions...</h2>
        </div>
        
        <div class="footer">
            <p>HELIOSICA v1.0.0 | Data from NOAA DSCOVR | Updates every 60s</p>
        </div>
    </div>
    
    <script>
        function fetchData() {
            fetch('/api/current')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('current').innerHTML = 
                            `<h2>Error: ${data.error}</h2>`;
                        return;
                    }
                    
                    const gssi = data.indices.gssi;
                    const gssiClass = `g${data.indices.gssi_category.toLowerCase()}`;
                    
                    let html = `
                        <h2>Current Conditions</h2>
                        <p>Time: ${new Date(data.timestamp).toLocaleString()}</p>
                        
                        <h3>Solar Wind at L1</h3>
                        <p>Bz: ${data.solar_wind.bz.toFixed(1)} nT</p>
                        <p>Vsw: ${data.solar_wind.vsw.toFixed(0)} km/s</p>
                        <p>np: ${data.solar_wind.np.toFixed(1)} cm⁻³</p>
                        
                        <h3>Geomagnetic Indices</h3>
                        <div class="gssi-gauge ${gssiClass}">
                            GSSI: ${(gssi*100).toFixed(0)}%
                        </div>
                        <p>Category: ${data.indices.gssi_category}</p>
                        <p>Kp: ${data.indices.kp.toFixed(1)} (${data.indices.kp_category})</p>
                        
                        <h3>Magnetosphere</h3>
                        <p>R_MP: ${data.magnetosphere.r_mp.toFixed(2)} R_E</p>
                    `;
                    
                    if (data.magnetosphere.satellite_alert) {
                        html += `<div class="alert">⚠️ SATELLITE ALERT: R_MP < 7.0 R_E</div>`;
                    }
                    
                    document.getElementById('current').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('current').innerHTML = 
                        `<h2>Error fetching data: ${error}</h2>`;
                });
        }
        
        fetchData();
        setInterval(fetchData, 60000);
    </script>
</body>
</html>""")
    
    # Create dashboard.html
    with open(os.path.join(dashboard_dir, 'dashboard.html'), 'w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>HELIOSICA - Dashboard</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body { font-family: Arial; margin: 0; padding: 20px; background: #0a0f1e; color: #e0e0e0; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .card { background: #1a1f2e; border-radius: 10px; padding: 20px; border: 1px solid #2a2f3e; }
        .full-width { grid-column: span 2; }
        .value { font-size: 32px; font-weight: bold; margin: 10px 0; }
        .label { color: #8899aa; font-size: 14px; }
        .g0 { color: #00ff00; } .g1 { color: #aaff00; } .g2 { color: #ffff00; }
        .g3 { color: #ffaa00; } .g4 { color: #ff5500; } .g5 { color: #ff0000; }
        .alert { background: #ff000022; border-left: 5px solid #ff0000; padding: 15px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>☀️ HELIOSICA Real-time Dashboard</h1>
    <div class="grid" id="dashboard">
        <div class="card full-width">Loading data...</div>
    </div>
    
    <script>
        function updateDashboard() {
            fetch('/api/current')
                .then(r => r.json())
                .then(data => {
                    if (data.error) return;
                    
                    const gssiClass = `g${data.indices.gssi_category.toLowerCase()}`;
                    
                    let html = `
                        <div class="card">
                            <div class="label">Time (UTC)</div>
                            <div class="value">${new Date(data.timestamp).toLocaleTimeString()}</div>
                        </div>
                        <div class="card">
                            <div class="label">GSSI</div>
                            <div class="value ${gssiClass}">${(data.indices.gssi*100).toFixed(0)}%</div>
                            <div>${data.indices.gssi_category}</div>
                        </div>
                        <div class="card">
                            <div class="label">Kp Index</div>
                            <div class="value">${data.indices.kp.toFixed(1)}</div>
                            <div>${data.indices.kp_category}</div>
                        </div>
                        <div class="card">
                            <div class="label">Bz</div>
                            <div class="value">${data.solar_wind.bz.toFixed(1)} nT</div>
                        </div>
                        <div class="card">
                            <div class="label">Solar Wind Speed</div>
                            <div class="value">${data.solar_wind.vsw.toFixed(0)} km/s</div>
                        </div>
                        <div class="card">
                            <div class="label">Density</div>
                            <div class="value">${data.solar_wind.np.toFixed(1)} cm⁻³</div>
                        </div>
                        <div class="card">
                            <div class="label">Magnetopause</div>
                            <div class="value">${data.magnetosphere.r_mp.toFixed(2)} R_E</div>
                        </div>
                        <div class="card">
                            <div class="label">Status</div>
                            <div class="value">${data.magnetosphere.satellite_alert ? '⚠️ ALERT' : 'Normal'}</div>
                        </div>
                    `;
                    
                    if (data.magnetosphere.satellite_alert) {
                        html += `<div class="card full-width alert">⚠️ SATELLITE ALERT: Magnetopause inside geosynchronous orbit</div>`;
                    }
                    
                    document.getElementById('dashboard').innerHTML = html;
                });
        }
        
        updateDashboard();
        setInterval(updateDashboard, 60000);
    </script>
</body>
</html>""")
    
    print(f"Created simple dashboard in {dashboard_dir}")
