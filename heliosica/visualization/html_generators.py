"""
HELIOSICA HTML Generators
Generate HTML for web dashboard
Pure Python
"""

from datetime import datetime
import html


class HTMLGenerator:
    """Generate HTML components"""
    
    @staticmethod
    def escape(text):
        """Escape HTML special characters"""
        return html.escape(str(text))
    
    @staticmethod
    def header(title, subtitle=None):
        """Generate HTML header"""
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>{HTMLGenerator.escape(title)}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #0a0f1e; color: #e0e0e0; }}
        .container {{ max-width: 1200px; margin: auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #ffaa00; font-size: 48px; margin: 0; }}
        .header p {{ color: #8899aa; }}
        .footer {{ text-align: center; color: #8899aa; margin-top: 40px; padding: 20px; }}
        .grid {{ display: grid; grid-gap: 20px; margin: 20px 0; }}
        .card {{ background: #1a1f2e; border-radius: 10px; padding: 20px; border: 1px solid #2a2f3e; }}
        .card h2 {{ color: #ffaa00; margin-top: 0; }}
        .card h3 {{ color: #ffffff; }}
        .value {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .label {{ color: #8899aa; font-size: 14px; }}
        .alert {{ background: #ff000022; border-left: 5px solid #ff0000; padding: 15px; margin: 10px 0; }}
        .warning {{ background: #ffaa0022; border-left: 5px solid #ffaa00; padding: 15px; }}
        .good {{ color: #00ff00; }}
        .warning-color {{ color: #ffaa00; }}
        .bad {{ color: #ff0000; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ text-align: left; padding: 8px; background: #2a2f3e; color: #ffaa00; }}
        td {{ padding: 8px; border-bottom: 1px solid #2a2f3e; }}
        .button {{ background: #ffaa00; color: #0a0f1e; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .button:hover {{ background: #ffbb22; }}
        .g0 {{ color: #00ff00; }} .g1 {{ color: #aaff00; }} .g2 {{ color: #ffff00; }}
        .g3 {{ color: #ffaa00; }} .g4 {{ color: #ff5500; }} .g5 {{ color: #ff0000; }}
        @media (max-width: 600px) {{ .grid {{ grid-template-columns: 1fr !important; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>☀️ HELIOSICA</h1>
            <p>{HTMLGenerator.escape(subtitle) if subtitle else ''}</p>
        </div>
'''
        return html
    
    @staticmethod
    def footer():
        """Generate HTML footer"""
        return f'''
        <div class="footer">
            <p>HELIOSICA v1.0.0 | Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <p><a href="/" style="color: #ffaa00;">Home</a> | 
               <a href="/dashboard" style="color: #ffaa00;">Dashboard</a> | 
               <a href="/api/current" style="color: #ffaa00;">API</a></p>
        </div>
    </div>
</body>
</html>
'''
    
    @staticmethod
    def grid_start(columns=2):
        """Start grid container"""
        return f'<div class="grid" style="grid-template-columns: repeat({columns}, 1fr);">\n'
    
    @staticmethod
    def grid_end():
        """End grid container"""
        return '</div>\n'
    
    @staticmethod
    def card_start(title=None, width=None):
        """Start card container"""
        style = f' style="grid-column: span {width};"' if width else ''
        html = f'<div class="card"{style}>\n'
        if title:
            html += f'    <h2>{HTMLGenerator.escape(title)}</h2>\n'
        return html
    
    @staticmethod
    def card_end():
        """End card container"""
        return '</div>\n'
    
    @staticmethod
    def value_display(label, value, unit=',', color_class=None):
        """Display a value with label"""
        class_attr = f' class="{color_class}"' if color_class else ''
        return f'''
        <div>
            <div class="label">{HTMLGenerator.escape(label)}</div>
            <div class="value"{class_attr}>{HTMLGenerator.escape(value)} {HTMLGenerator.escape(unit)}</div>
        </div>
'''
    
    @staticmethod
    def gssi_gauge(gssi_value, category):
        """Display GSSI gauge"""
        percentage = int(gssi_value * 100)
        color_class = f'g{category.lower()}'
        
        return f'''
        <div style="text-align: center;">
            <div class="label">GSSI - {HTMLGenerator.escape(category)}</div>
            <div class="value {color_class}">{percentage}%</div>
            <div style="height: 20px; width: 100%; background: #2a2f3e; border-radius: 10px; margin: 10px 0;">
                <div style="height: 20px; width: {percentage}%; background: currentColor; border-radius: 10px;"></div>
            </div>
        </div>
'''
    
    @staticmethod
    def alert_message(message, level='warning'):
        """Display alert message"""
        alert_class = 'alert' if level == 'danger' else 'warning'
        return f'<div class="{alert_class}">{HTMLGenerator.escape(message)}</div>\n'
    
    @staticmethod
    def data_table(headers, rows):
        """Generate data table"""
        html = '<table>\n    <tr>\n'
        for h in headers:
            html += f'        <th>{HTMLGenerator.escape(h)}</th>\n'
        html += '    </tr>\n'
        
        for row in rows:
            html += '    <tr>\n'
            for cell in row:
                html += f'        <td>{HTMLGenerator.escape(str(cell))}</td>\n'
            html += '    </tr>\n'
        
        html += '</table>\n'
        return html
    
    @staticmethod
    def parameter_summary(params):
        """Generate parameter summary table"""
        headers = ['Parameter', 'Value', 'Status']
        rows = []
        
        for key, value in params.items():
            if isinstance(value, dict):
                status = value.get('status', 'normal')
                val = value.get('value', 'N/A')
            else:
                status = 'normal'
                val = value
            
            status_class = ''
            if status == 'alert':
                status_class = 'bad'
            elif status == 'warning':
                status_class = 'warning-color'
            elif status == 'good':
                status_class = 'good'
            
            status_display = status.capitalize()
            if status_class:
                status_display = f'<span class="{status_class}">{status_display}</span>'
            
            rows.append([key.upper(), val, status_display])
        
        return HTMLGenerator.data_table(headers, rows)
    
    @staticmethod
    def storm_history(events):
        """Generate storm history table"""
        headers = ['Date', 'Kp', 'GSSI', 'Category', 'Description']
        rows = []
        
        for event in events:
            rows.append([
                event.get('date', ''),
                event.get('kp', ''),
                f"{event.get('gssi', 0):.3f}",
                event.get('category', ''),
                event.get('description', '')
            ])
        
        return HTMLGenerator.data_table(headers, rows)
    
    @staticmethod
    def navigation_links(links):
        """Generate navigation links"""
        html = '<div style="margin: 20px 0;">\n'
        for text, url in links:
            html += f'    <a href="{url}" class="button" style="margin-right: 10px;">{HTMLGenerator.escape(text)}</a>\n'
        html += '</div>\n'
        return html
    
    @staticmethod
    def loading_indicator():
        """Generate loading indicator"""
        return '''
        <div style="text-align: center; padding: 40px;">
            <div style="border: 4px solid #2a2f3e; border-top: 4px solid #ffaa00; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: auto;"></div>
            <p style="color: #8899aa;">Loading...</p>
        </div>
        <style>
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
        '''
    
    @staticmethod
    def auto_refresh(seconds=60):
        """Add auto-refresh meta tag"""
        return f'<meta http-equiv="refresh" content="{seconds}">\n'


class DashboardGenerator:
    """Generate complete dashboard HTML"""
    
    @staticmethod
    def generate_index():
        """Generate index page"""
        html = HTMLGenerator.header('HELIOSICA', 'Real-time Space Weather Monitor')
        
        html += HTMLGenerator.navigation_links([
            ('Dashboard', '/dashboard'),
            ('API', '/api/current'),
            ('Documentation', '/docs')
        ])
        
        html += HTMLGenerator.grid_start(2)
        
        # Welcome card
        html += HTMLGenerator.card_start('Welcome to HELIOSICA')
        html += '''
        <p>HELIOSICA (Heliospheric Event and L1 Integrated Observatory) provides real-time 
        space weather forecasting using 9 physical parameters.</p>
        
        <h3>Features:</h3>
        <ul>
            <li>Real-time DSCOVR data monitoring</li>
            <li>GSSI (Geomagnetic Storm Severity Index)</li>
            <li>CME transit predictions (DBM model)</li>
            <li>Magnetopause tracking</li>
            <li>Forbush decrease detection</li>
        </ul>
        
        <p><a href="/dashboard" class="button">Go to Dashboard</a></p>
        '''
        html += HTMLGenerator.card_end()
        
        # Quick stats card
        html += HTMLGenerator.card_start('Current Status')
        html += '''
        <div id="quick-stats">
            <p>Loading current conditions...</p>
        </div>
        <script>
            fetch('/api/current')
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('quick-stats').innerHTML = '<p>Error loading data</p>';
                        return;
                    }
                    let html = `
                        <p><strong>Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                        <p><strong>Bz:</strong> ${data.solar_wind.bz.toFixed(1)} nT</p>
                        <p><strong>Vsw:</strong> ${data.solar_wind.vsw.toFixed(0)} km/s</p>
                        <p><strong>GSSI:</strong> ${(data.indices.gssi*100).toFixed(0)}% (${data.indices.gssi_category})</p>
                        <p><strong>Kp:</strong> ${data.indices.kp.toFixed(1)}</p>
                    `;
                    document.getElementById('quick-stats').innerHTML = html;
                });
        </script>
        '''
        html += HTMLGenerator.card_end()
        
        html += HTMLGenerator.grid_end()
        html += HTMLGenerator.footer()
        
        return html
    
    @staticmethod
    def generate_dashboard(current_data=None):
        """Generate dashboard page"""
        html = HTMLGenerator.header('HELIOSICA Dashboard', 'Real-time Monitor')
        html += HTMLGenerator.auto_refresh(60)
        
        if current_data:
            gssi = current_data.get('indices', {}).get('gssi', 0)
            category = current_data.get('indices', {}).get('gssi_category', 'G0')
            
            html += HTMLGenerator.grid_start(2)
            
            # GSSI card
            html += HTMLGenerator.card_start('Geomagnetic Storm Severity')
            html += HTMLGenerator.gssi_gauge(gssi, category)
            html += HTMLGenerator.card_end()
            
            # Solar wind card
            html += HTMLGenerator.card_start('Solar Wind (L1)')
            sw = current_data.get('solar_wind', {})
            html += HTMLGenerator.value_display('Bz', f"{sw.get('bz', 0):.1f}", 'nT')
            html += HTMLGenerator.value_display('Vsw', f"{sw.get('vsw', 0):.0f}", 'km/s')
            html += HTMLGenerator.value_display('np', f"{sw.get('np', 0):.1f}", 'cm⁻³')
            html += HTMLGenerator.value_display('Tp', f"{sw.get('tp', 0):.1e}", 'K')
            html += HTMLGenerator.card_end()
            
            # Magnetosphere card
            html += HTMLGenerator.card_start('Magnetosphere')
            mp = current_data.get('magnetosphere', {})
            r_mp = mp.get('r_mp', 10)
            alert = mp.get('satellite_alert', False)
            
            color_class = 'bad' if alert else 'good'
            html += HTMLGenerator.value_display('Standoff Distance', f"{r_mp:.2f}", 'R_E', color_class)
            
            if alert:
                html += HTMLGenerator.alert_message('⚠️ SATELLITE ALERT: R_MP < 7.0 R_E', 'danger')
            
            html += HTMLGenerator.card_end()
            
            # Indices card
            html += HTMLGenerator.card_start('Geomagnetic Indices')
            idx = current_data.get('indices', {})
            html += HTMLGenerator.value_display('Kp', f"{idx.get('kp', 0):.1f}", '', f"g{idx.get('kp_category', 'G0').lower()}")
            html += HTMLGenerator.value_display('Ey', f"{idx.get('ey', 0):.1f}", 'mV/m')
            html += HTMLGenerator.card_end()
            
            html += HTMLGenerator.grid_end()
            
        else:
            # Loading state
            html += HTMLGenerator.loading_indicator()
            html += '''
            <script>
                window.location.href = '/api/current?redirect=/dashboard';
            </script>
            '''
        
        html += HTMLGenerator.footer()
        return html
    
    @staticmethod
    def generate_storm_report(event):
        """Generate storm event report"""
        html = HTMLGenerator.header(f"Storm Report: {event.get('name', 'Unknown')}")
        
        html += HTMLGenerator.card_start('Event Details')
        html += f'''
        <p><strong>Date:</strong> {event.get('date', '')}</p>
        <p><strong>Kp:</strong> {event.get('kp', '')}</p>
        <p><strong>Dst:</strong> {event.get('dst', '')} nT</p>
        <p><strong>GSSI:</strong> {event.get('gssi', 0):.3f}</p>
        '''
        html += HTMLGenerator.card_end()
        
        html += HTMLGenerator.footer()
        return html
