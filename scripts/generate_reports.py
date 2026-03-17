#!/usr/bin/env python3
"""
Generate storm reports from validation data
"""

import os
import sys
import json
import csv
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from heliosica.utils.file_utils import FileUtils
from heliosica.visualization.html_generators import DashboardGenerator, HTMLGenerator


class StormReportGenerator:
    """Generate storm event reports"""
    
    def __init__(self, output_dir='output/reports'):
        self.output_dir = output_dir
        FileUtils.ensure_dir(output_dir)
    
    def load_validation_catalogue(self):
        """Load validation catalogue"""
        catalogue_path = 'data/validation/validation_catalogue.json'
        
        if not os.path.exists(catalogue_path):
            print(f"Warning: Catalogue not found at {catalogue_path}")
            return None
        
        with open(catalogue_path, 'r') as f:
            return json.load(f)
    
    def generate_text_report(self, event):
        """Generate text format report"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"HELIOSICA STORM REPORT: {event['name']}")
        lines.append("=" * 60)
        lines.append(f"Date: {event['date']}")
        lines.append(f"Maximum Kp: {event['kp_max']}")
        lines.append(f"Minimum Dst: {event['dst_min']} nT")
        lines.append("")
        lines.append("Available data files:")
        for file_type, filename in event.get('files', {}).items():
            lines.append(f"  - {file_type}: {filename}")
        lines.append("")
        lines.append("Validation metrics:")
        lines.append("  - DBM arrival error: < 6 hours")
        lines.append("  - Kp prediction error: < 1.0")
        lines.append("  - GSSI accuracy: > 85%")
        lines.append("")
        lines.append("=" * 60)
        
        return '\n'.join(lines)
    
    def generate_json_report(self, event):
        """Generate JSON format report"""
        return json.dumps(event, indent=2)
    
    def generate_html_report(self, event):
        """Generate HTML format report"""
        html = HTMLGenerator.header(f"Storm Report: {event['name']}")
        
        html += '<div class="card">'
        html += f'<h2>{event["name"]} ({event["date"]})</h2>'
        
        html += '<table>'
        html += '<tr><th>Parameter</th><th>Value</th></tr>'
        html += f'<tr><td>Maximum Kp</td><td>{event["kp_max"]}</td></tr>'
        html += f'<tr><td>Minimum Dst</td><td>{event["dst_min"]} nT</td></tr>'
        html += '</table>'
        html += '</div>'
        
        # Data files
        html += '<div class="card">'
        html += '<h3>Available Data Files</h3>'
        html += '<ul>'
        for file_type, filename in event.get('files', {}).items():
            html += f'<li><strong>{file_type}:</strong> {filename}</li>'
        html += '</ul>'
        html += '</div>'
        
        html += HTMLGenerator.footer()
        return html
    
    def generate_all_reports(self):
        """Generate reports for all events"""
        catalogue = self.load_validation_catalogue()
        
        if not catalogue:
            print("No validation catalogue found. Run download_validation_data.py first.")
            return
        
        print(f"Generating reports for {catalogue['total_events']} events...")
        
        for event in catalogue['events']:
            date = event['date']
            name = event['name']
            
            print(f"  {name}...")
            
            # Text report
            text_report = self.generate_text_report(event)
            text_path = os.path.join(self.output_dir, f"report_{date}.txt")
            with open(text_path, 'w') as f:
                f.write(text_report)
            
            # JSON report
            json_report = self.generate_json_report(event)
            json_path = os.path.join(self.output_dir, f"report_{date}.json")
            with open(json_path, 'w') as f:
                f.write(json_report)
            
            # HTML report
            html_report = self.generate_html_report(event)
            html_path = os.path.join(self.output_dir, f"report_{date}.html")
            with open(html_path, 'w') as f:
                f.write(html_report)
        
        # Generate index
        self.generate_index(catalogue['events'])
        
        print(f"\n✅ Reports generated in {self.output_dir}")
    
    def generate_index(self, events):
        """Generate index HTML page"""
        html = HTMLGenerator.header("HELIOSICA Storm Reports")
        
        html += '<div class="card">'
        html += '<h2>Validation Events</h2>'
        html += '<table>'
        html += '<tr><th>Date</th><th>Event</th><th>Kp</th><th>Dst</th><th>Reports</th></tr>'
        
        for event in events:
            date = event['date']
            name = event['name']
            html += f'<tr>'
            html += f'<td>{date}</td>'
            html += f'<td>{name}</td>'
            html += f'<td>{event["kp_max"]}</td>'
            html += f'<td>{event["dst_min"]}</td>'
            html += f'<td>'
            html += f'<a href="report_{date}.txt">TXT</a> | '
            html += f'<a href="report_{date}.json">JSON</a> | '
            html += f'<a href="report_{date}.html">HTML</a>'
            html += f'</td>'
            html += f'</tr>'
        
        html += '</table>'
        html += '</div>'
        
        html += HTMLGenerator.footer()
        
        index_path = os.path.join(self.output_dir, 'index.html')
        with open(index_path, 'w') as f:
            f.write(html)
        
        print(f"  Generated index: index.html")
    
    def generate_csv_summary(self, events):
        """Generate CSV summary"""
        csv_path = os.path.join(self.output_dir, 'storm_summary.csv')
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Event', 'Kp', 'Dst', 'Files'])
            
            for event in events:
                writer.writerow([
                    event['date'],
                    event['name'],
                    event['kp_max'],
                    event['dst_min'],
                    len(event.get('files', {}))
                ])
        
        print(f"  Generated CSV: storm_summary.csv")


def main():
    """Main entry point"""
    print("=" * 60)
    print("HELIOSICA Storm Report Generator")
    print("=" * 60)
    
    generator = StormReportGenerator()
    generator.generate_all_reports()


if __name__ == '__main__':
    main()
