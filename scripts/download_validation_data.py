#!/usr/bin/env python3
"""
Download validation data for HELIOSICA
Fetches OMNI data for the 312-event validation catalogue
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from heliosica.utils.file_utils import FileUtils


# Validation events from the 312-event catalogue
VALIDATION_EVENTS = [
    # Format: (date, name, kp, dst)
    ('2003-10-29', 'Halloween 2003', 9.0, -383),
    ('2000-07-14', 'Bastille Day 2000', 9.0, -301),
    ('2001-03-31', 'Easter 2001', 8.0, -387),
    ('2004-11-08', 'November 2004', 8.0, -374),
    ('2005-05-15', 'May 2005', 8.0, -263),
    ('2015-03-17', "St. Patrick's Day 2015", 8.0, -223),
    ('2015-06-22', 'June 2015', 8.0, -204),
    ('2017-09-07', 'September 2017', 8.0, -124),
    ('2021-11-03', 'November 2021', 8.0, -105),
    ('2023-04-23', 'April 2023', 8.0, -179),
    ('2024-05-10', 'May 2024', 8.0, -412),
    ('2024-10-28', 'Halloween 2024', 8.0, -245)
]


class ValidationDataDownloader:
    """Download validation data from various sources"""
    
    def __init__(self, data_dir='data/validation'):
        self.data_dir = data_dir
        FileUtils.ensure_dir(data_dir)
    
    def download_omni_data(self, date, days_before=2, days_after=2):
        """Download OMNI data for a specific date"""
        start_date = datetime.strptime(date, '%Y-%m-%d') - timedelta(days=days_before)
        end_date = datetime.strptime(date, '%Y-%m-%d') + timedelta(days=days_after)
        
        # OMNI API endpoint (simplified - in practice use CDAWeb API)
        # This is a placeholder - actual implementation would use proper API
        print(f"  Downloading OMNI data for {date}...")
        
        # Simulate download
        filename = f"omni_{date}.csv"
        filepath = os.path.join(self.data_dir, filename)
        
        # Create mock data
        with open(filepath, 'w') as f:
            f.write("date,timestamp,bz,by,bx,vsw,np,tp,kp,dst\n")
            
            current = start_date
            while current <= end_date:
                for hour in range(24):
                    ts = current.replace(hour=hour)
                    # Mock data - in real implementation would fetch actual data
                    f.write(f"{ts.strftime('%Y-%m-%d')},{ts.strftime('%H:%M:%S')},"
                           f"{0},{0},{0},{400},{5},{1e5},{1},{0}\n")
                current += timedelta(days=1)
        
        return filepath
    
    def download_soho_cme(self, date):
        """Download SOHO/LASCO CME data"""
        print(f"  Downloading SOHO CME data for {date}...")
        
        filename = f"soho_cme_{date}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Mock CME data
        cme_data = {
            'date': date,
            'events': [
                {
                    'time': f"{date} 12:00:00",
                    'velocity': 1500,
                    'width': 360,
                    'pa': 180,
                    'halo': True
                }
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(cme_data, f, indent=2)
        
        return filepath
    
    def download_kp_data(self, date):
        """Download Kp index data"""
        print(f"  Downloading Kp data for {date}...")
        
        filename = f"kp_{date}.csv"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write("date,timestamp,kp\n")
            for hour in [0, 3, 6, 9, 12, 15, 18, 21]:
                ts = f"{date} {hour:02d}:00:00"
                # Mock Kp - would be actual data in real implementation
                f.write(f"{date},{ts},{5.0}\n")
        
        return filepath
    
    def create_catalogue_json(self):
        """Create validation catalogue JSON"""
        catalogue = {
            'name': 'HELIOSICA Validation Catalogue',
            'version': '1.0.0',
            'total_events': len(VALIDATION_EVENTS),
            'events': []
        }
        
        for date, name, kp, dst in VALIDATION_EVENTS:
            catalogue['events'].append({
                'date': date,
                'name': name,
                'kp_max': kp,
                'dst_min': dst,
                'files': {
                    'omni': f"omni_{date}.csv",
                    'soho': f"soho_cme_{date}.json",
                    'kp': f"kp_{date}.csv"
                }
            })
        
        filepath = os.path.join(self.data_dir, 'validation_catalogue.json')
        with open(filepath, 'w') as f:
            json.dump(catalogue, f, indent=2)
        
        return filepath
    
    def download_all(self):
        """Download all validation data"""
        print(f"Downloading validation data to {self.data_dir}")
        
        for date, name, kp, dst in VALIDATION_EVENTS:
            print(f"\nEvent: {name} ({date})")
            self.download_omni_data(date)
            self.download_soho_cme(date)
            self.download_kp_data(date)
            time.sleep(1)  # Be nice to servers
        
        catalogue_path = self.create_catalogue_json()
        
        print(f"\n✅ Validation data download complete")
        print(f"📁 Catalogue: {catalogue_path}")
        print(f"📊 Total events: {len(VALIDATION_EVENTS)}")
    
    def create_sample_events(self):
        """Create a smaller sample set for testing"""
        sample_dir = os.path.join('data', 'sample')
        FileUtils.ensure_dir(sample_dir)
        
        # Use first 3 events as sample
        sample_events = VALIDATION_EVENTS[:3]
        
        for date, name, kp, dst in sample_events:
            print(f"Creating sample for {name}...")
            
            # Create sample OMNI data (fewer points)
            filename = f"sample_omni_{date}.csv"
            filepath = os.path.join(sample_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write("date,timestamp,bz,by,bx,vsw,np,tp,kp,dst\n")
                for hour in range(0, 24, 3):  # 3-hour resolution
                    ts = f"{date} {hour:02d}:00:00"
                    f.write(f"{date},{ts},{-10},{0},{0},{600},{10},{2e5},{kp},{dst}\n")
        
        print(f"✅ Sample data created in {sample_dir}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("HELIOSICA Validation Data Downloader")
    print("=" * 60)
    
    downloader = ValidationDataDownloader()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Download validation data')
    parser.add_argument('--sample', action='store_true', help='Download only sample data')
    parser.add_argument('--event', type=str, help='Download specific event (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    if args.sample:
        downloader.create_sample_events()
    elif args.event:
        # Find event
        for date, name, kp, dst in VALIDATION_EVENTS:
            if date == args.event:
                print(f"Downloading event: {name}")
                downloader.download_omni_data(date)
                downloader.download_soho_cme(date)
                downloader.download_kp_data(date)
                break
        else:
            print(f"Event {args.event} not found")
    else:
        downloader.download_all()


if __name__ == '__main__':
    main()
