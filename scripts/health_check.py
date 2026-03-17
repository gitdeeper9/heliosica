#!/usr/bin/env python3
"""
HELIOSICA Health Check Script
Monitors system health and sends alerts
"""

import os
import sys
import json
import socket
import subprocess
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from heliosica.utils.file_utils import FileUtils


class HealthChecker:
    """Check system health"""
    
    def __init__(self, config_file='.env'):
        self.config = self.load_config(config_file)
        self.status = {
            'timestamp': datetime.utcnow().isoformat(),
            'hostname': socket.gethostname(),
            'checks': {}
        }
    
    def load_config(self, config_file):
        """Load configuration from .env file"""
        config = {}
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"\'')
        
        return config
    
    def check_disk_usage(self):
        """Check disk usage"""
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        
        if len(lines) >= 2:
            parts = lines[1].split()
            usage = parts[4].replace('%', '')
            
            self.status['checks']['disk_usage'] = {
                'status': 'ok' if int(usage) < 80 else 'warning',
                'value': f"{usage}%",
                'threshold': '80%'
            }
    
    def check_memory_usage(self):
        """Check memory usage"""
        result = subprocess.run(['free', '-m'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        
        if len(lines) >= 2:
            parts = lines[1].split()
            total = int(parts[1])
            used = int(parts[2])
            usage = (used / total) * 100
            
            self.status['checks']['memory_usage'] = {
                'status': 'ok' if usage < 80 else 'warning',
                'value': f"{usage:.1f}%",
                'threshold': '80%'
            }
    
    def check_cpu_load(self):
        """Check CPU load"""
        result = subprocess.run(['uptime'], capture_output=True, text=True)
        line = result.stdout.strip()
        
        # Extract load average
        parts = line.split('load average:')
        if len(parts) > 1:
            load = float(parts[1].split(',')[0].strip())
            
            self.status['checks']['cpu_load'] = {
                'status': 'ok' if load < 4 else 'warning',
                'value': f"{load:.2f}",
                'threshold': '4.0'
            }
    
    def check_service_status(self):
        """Check if HELIOSICA service is running"""
        if os.path.exists('/etc/systemd/system/heliosica.service'):
            result = subrun(['systemctl', 'is-active', 'heliosica'], capture_output=True, text=True)
            status = result.stdout.strip()
            
            self.status['checks']['service'] = {
                'status': 'ok' if status == 'active' else 'error',
                'value': status
            }
        else:
            # Check if process is running
            result = subprocess.run(['pgrep', '-f', 'heliosica'], capture_output=True)
            self.status['checks']['service'] = {
                'status': 'ok' if result.returncode == 0 else 'error',
                'value': 'running' if result.returncode == 0 else 'stopped'
            }
    
    def check_database(self):
        """Check database connectivity"""
        db_path = 'heliosica.db'
        
        if os.path.exists(db_path):
            # Check if we can read it
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master")
                count = cursor.fetchone()[0]
                conn.close()
                
                self.status['checks']['database'] = {
                    'status': 'ok',
                    'value': f"accessible ({count} tables)"
                }
            except Exception as e:
                self.status['checks']['database'] = {
                    'status': 'error',
                    'value': str(e)
                }
        else:
            self.status['checks']['database'] = {
                'status': 'warning',
                'value': 'not found'
            }
    
    def check_data_dirs(self):
        """Check data directories"""
        dirs = ['data/raw', 'data/validation', 'logs', 'output']
        missing = []
        
        for d in dirs:
            if not os.path.exists(d):
                missing.append(d)
        
        self.status['checks']['directories'] = {
            'status': 'ok' if not missing else 'warning',
            'value': f"{len(dirs) - len(missing)}/{len(dirs)} exist",
            'missing': missing
        }
    
    def check_recent_data(self):
        """Check if recent data is available"""
        # Check last modified time of data files
        import glob
        
        data_files = glob.glob('data/raw/*/*')
        if data_files:
            latest = max(data_files, key=os.path.getmtime)
            mtime = os.path.getmtime(latest)
            age = (datetime.now().timestamp() - mtime) / 3600  # hours
            
            self.status['checks']['recent_data'] = {
                'status': 'ok' if age < 24 else 'warning',
                'value': f"latest: {os.path.basename(latest)} ({age:.1f} hours old)"
            }
        else:
            self.status['checks']['recent_data'] = {
                'status': 'warning',
                'value': 'no data files found'
            }
    
    def run_all_checks(self):
        """Run all health checks"""
        self.check_disk_usage()
        self.check_memory_usage()
        self.check_cpu_load()
        self.check_service_status()
        self.check_database()
        self.check_data_dirs()
        self.check_recent_data()
        
        return self.status
    
    def send_alert(self, message):
        """Send alert email"""
        if not all(k in self.config for k in ['SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD', 'ALERT_EMAIL']):
            print("Email configuration not found, skipping alert")
            return
        
        msg = MIMEMultipart()
        msg['From'] = self.config['SMTP_USER']
        msg['To'] = self.config['ALERT_EMAIL']
        msg['Subject'] = f"HELIOSICA Health Alert: {self.status['hostname']}"
        
        body = f"""
HELIOSICA Health Check Alert
Time: {self.status['timestamp']}
Host: {self.status['hostname']}

Issues detected:
{message}

Full status:
{json.dumps(self.status, indent=2)}
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.config['SMTP_HOST'], int(self.config.get('SMTP_PORT', 587)))
            server.starttls()
            server.login(self.config['SMTP_USER'], self.config['SMTP_PASSWORD'])
            server.send_message(msg)
            server.quit()
            print("Alert email sent")
        except Exception as e:
            print(f"Failed to send alert: {e}")
    
    def print_report(self):
        """Print health report"""
        print("\n" + "=" * 60)
        print(f"HELIOSICA Health Check - {self.status['timestamp']}")
        print(f"Host: {self.status['hostname']}")
        print("=" * 60)
        
        all_ok = True
        
        for check, result in self.status['checks'].items():
            status_symbol = '✅' if result['status'] == 'ok' else '⚠️' if result['status'] == 'warning' else '❌'
            print(f"\n{status_symbol} {check.upper()}:")
            print(f"   Status: {result['status']}")
            print(f"   Value: {result['value']}")
            
            if result['status'] != 'ok':
                all_ok = False
        
        print("\n" + "=" * 60)
        if all_ok:
            print("✅ All systems OK")
        else:
            print("⚠️ Some issues detected")
        
        print("=" * 60)
    
    def save_report(self, output_dir='logs'):
        """Save health report to file"""
        FileUtils.ensure_dir(output_dir)
        
        filename = f"health_check_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.status, f, indent=2)
        
        print(f"Report saved to {filepath}")
        return filepath


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HELIOSICA Health Check')
    parser.add_argument('--alert', action='store_true', help='Send alert if issues found')
    parser.add_argument('--save', action='store_true', help='Save report to file')
    
    args = parser.parse_args()
    
    checker = HealthChecker()
    checker.run_all_checks()
    checker.print_report()
    
    if args.save:
        checker.save_report()
    
    # Check if any warnings or errors
    if args.alert:
        issues = []
        for check, result in checker.status['checks'].items():
            if result['status'] != 'ok':
                issues.append(f"{check}: {result['status']} - {result['value']}")
        
        if issues:
            checker.send_alert('\n'.join(issues))
    
    # Exit with appropriate code
    for check, result in checker.status['checks'].items():
        if result['status'] == 'error':
            sys.exit(2)
        elif result['status'] == 'warning':
            sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
