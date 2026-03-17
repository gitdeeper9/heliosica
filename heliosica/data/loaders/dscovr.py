"""
DSCOVR (Deep Space Climate Observatory) Data Loader
HELIOSICA - Heliospheric Event and L1 Integrated Observatory

Real-time 1-minute cadence solar wind data from L1 point
"""

import numpy as np
import requests
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import time


@dataclass
class DSCOVRDataPoint:
    """Single DSCOVR measurement"""
    timestamp: datetime
    bx: float          # IMF Bx (nT)
    by: float          # IMF By (nT)
    bz: float          # IMF Bz (nT)
    bt: float          # Total field (nT)
    vsw: float         # Solar wind velocity (km/s)
    np: float          # Proton density (cm⁻³)
    tp: float          # Proton temperature (K)
    quality: float     # Data quality flag (0-1)


class DSCOVRLoader:
    """
    Loader for DSCOVR real-time and historical data
    
    DSCOVR provides 1-minute cadence L1 observations
    Used for Bz, Vsw, np, Tp parameters
    """
    
    # NOAA SWPC API endpoints
    BASE_URL = "https://services.swpc.noaa.gov"
    REAL_TIME_MAG = "/products/solar-wind/plasma-1-minute.json"
    REAL_TIME_PLASMA = "/products/solar-wind/mag-1-minute.json"
    
    # Backup endpoints (if primary fails)
    BACKUP_URLS = [
        "https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json",
        "https://services.swpc.noaa.gov/json/rtsw/rtsw_plasma_1m.json"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize DSCOVR loader
        
        Parameters
        ----------
        api_key : str, optional
            NOAA API key (not required for public data)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HELIOSICA/1.0 (gitdeeper@gmail.com)'
        })
        
        # Cache for recent data
        self.cache = {}
        self.last_fetch = None
        
    def fetch_realtime_mag(self) -> List[Dict]:
        """
        Fetch real-time magnetometer data
        
        Returns
        -------
        List[Dict]
            List of magnetic field measurements
        """
        try:
            url = f"{self.BASE_URL}{self.REAL_TIME_MAG}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except Exception as e:
            print(f"Error fetching real-time magnetometer: {e}")
            
            # Try backup
            try:
                response = self.session.get(self.BACKUP_URLS[0], timeout=10)
                response.raise_for_status()
                return response.json()
            except:
                return []
    
    def fetch_realtime_plasma(self) -> List[Dict]:
        """
        Fetch real-time plasma data
        
        Returns
        -------
        List[Dict]
            List of plasma measurements
        """
        try:
            url = f"{self.BASE_URL}{self.REAL_TIME_PLASMA}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except Exception as e:
            print(f"Error fetching real-time plasma: {e}")
            
            # Try backup
            try:
                response = self.session.get(self.BACKUP_URLS[1], timeout=10)
                response.raise_for_status()
                return response.json()
            except:
                return []
    
    def parse_timestamp(self, time_str: str) -> datetime:
        """
        Parse NOAA timestamp format
        
        Parameters
        ----------
        time_str : str
            Timestamp string (e.g., "2024-01-01 00:00:00")
        
        Returns
        -------
        datetime
            Parsed datetime
        """
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    
    def get_current(self) -> Optional[DSCOVRDataPoint]:
        """
        Get most recent DSCOVR measurement
        
        Returns
        -------
        DSCOVRDataPoint or None
            Latest data point
        """
        mag_data = self.fetch_realtime_mag()
        plasma_data = self.fetch_realtime_plasma()
        
        if not mag_data or not plasma_data:
            return None
        
        # Get latest from each
        latest_mag = mag_data[-1]
        latest_plasma = plasma_data[-1]
        
        # Parse timestamps
        mag_time = self.parse_timestamp(latest_mag['time_tag'])
        plasma_time = self.parse_timestamp(latest_plasma['time_tag'])
        
        # Use the most recent complete data point
        timestamp = max(mag_time, plasma_time)
        
        # Calculate total field
        bx = float(latest_mag.get('bx_gsm', 0))
        by = float(latest_mag.get('by_gsm', 0))
        bz = float(latest_mag.get('bz_gsm', 0))
        bt = np.sqrt(bx**2 + by**2 + bz**2)
        
        return DSCOVRDataPoint(
            timestamp=timestamp,
            bx=bx,
            by=by,
            bz=bz,
            bt=bt,
            vsw=float(latest_plasma.get('speed', 0)),
            np=float(latest_plasma.get('density', 0)),
            tp=float(latest_plasma.get('temperature', 0)),
            quality=1.0  # Assume good quality
        )
    
    def get_timeseries(self, minutes: int = 60) -> List[DSCOVRDataPoint]:
        """
        Get recent time series
        
        Parameters
        ----------
        minutes : int
            Number of minutes of history
        
        Returns
        -------
        List[DSCOVRDataPoint]
            Time series data
        """
        mag_data = self.fetch_realtime_mag()
        plasma_data = self.fetch_realtime_plasma()
        
        if not mag_data or not plasma_data:
            return []
        
        # Convert to dict by timestamp
        mag_dict = {}
        for item in mag_data[-minutes:]:
            ts = self.parse_timestamp(item['time_tag'])
            mag_dict[ts] = item
        
        plasma_dict = {}
        for item in plasma_data[-minutes:]:
            ts = self.parse_timestamp(item['time_tag'])
            plasma_dict[ts] = item
        
        # Combine by timestamp
        result = []
        all_times = sorted(set(mag_dict.keys()) & set(plasma_dict.keys()))
        
        for ts in all_times[-minutes:]:
            mag = mag_dict[ts]
            plasma = plasma_dict[ts]
            
            bx = float(mag.get('bx_gsm', 0))
            by = float(mag.get('by_gsm', 0))
            bz = float(mag.get('bz_gsm', 0))
            bt = np.sqrt(bx**2 + by**2 + bz**2)
            
            result.append(DSCOVRDataPoint(
                timestamp=ts,
                bx=bx,
                by=by,
                bz=bz,
                bt=bt,
                vsw=float(plasma.get('speed', 0)),
                np=float(plasma.get('density', 0)),
                tp=float(plasma.get('temperature', 0)),
                quality=1.0
            ))
        
        return result
    
    def get_bz_history(self, hours: int = 24) -> Tuple[List[datetime], List[float]]:
        """
        Get Bz history for specified period
        
        Parameters
        ----------
        hours : int
            Hours of history
        
        Returns
        -------
        Tuple[List[datetime], List[float]]
            Timestamps and Bz values
        """
        minutes = hours * 60
        data = self.get_timeseries(minutes)
        
        timestamps = [d.timestamp for d in data]
        bz_values = [d.bz for d in data]
        
        return timestamps, bz_values
    
    def check_data_quality(self, data: DSCOVRDataPoint) -> Dict[str, bool]:
        """
        Check data quality flags
        
        Parameters
        ----------
        data : DSCOVRDataPoint
            Data point to check
        
        Returns
        -------
        Dict[str, bool]
            Quality checks
        """
        return {
            'bz_valid': abs(data.bz) < 100,  # Reasonable range
            'vsw_valid': 200 < data.vsw < 2000,  # 200-2000 km/s
            'np_valid': 0.1 < data.np < 100,  # 0.1-100 cm⁻³
            'tp_valid': 1e4 < data.tp < 1e7,  # 10⁴-10⁷ K
            'timestamp_recent': (datetime.utcnow() - data.timestamp).seconds < 600  # <10 min old
        }
    
    def stream(self, interval_seconds: int = 60, callback=None):
        """
        Stream real-time data continuously
        
        Parameters
        ----------
        interval_seconds : int
            Update interval
        callback : callable, optional
            Function to call with each new data point
        """
        print(f"Starting DSCOVR data stream (interval: {interval_seconds}s)")
        
        last_timestamp = None
        
        while True:
            try:
                current = self.get_current()
                
                if current and (last_timestamp is None or 
                                current.timestamp > last_timestamp):
                    
                    quality = self.check_data_quality(current)
                    
                    if all(quality.values()):
                        if callback:
                            callback(current)
                        else:
                            # Default output
                            print(f"\r[{current.timestamp}] Bz: {current.bz:.1f} nT | "
                                  f"Vsw: {current.vsw:.0f} km/s | np: {current.np:.1f} cm⁻³", 
                                  end='')
                    
                    last_timestamp = current.timestamp
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\nStream stopped by user")
                break
            except Exception as e:
                print(f"\nError in stream: {e}")
                time.sleep(interval_seconds * 2)  # Wait longer on error


# Example usage
def test_dscovr():
    """Test DSCOVR loader"""
    loader = DSCOVRLoader()
    
    print("Testing DSCOVR loader...")
    
    # Get current data
    current = loader.get_current()
    if current:
        print(f"\nCurrent conditions:")
        print(f"Time: {current.timestamp}")
        print(f"Bz: {current.bz:.1f} nT")
        print(f"Vsw: {current.vsw:.0f} km/s")
        print(f"np: {current.np:.1f} cm⁻³")
        print(f"Tp: {current.tp:.1e} K")
        
        # Check quality
        quality = loader.check_data_quality(current)
        print(f"\nQuality checks:")
        for check, passed in quality.items():
            print(f"  {check}: {'✓' if passed else '✗'}")
    
    # Get last hour
    print(f"\nLast hour of data:")
    data = loader.get_timeseries(60)
    print(f"Retrieved {len(data)} points")
    
    if len(data) > 0:
        bz_values = [d.bz for d in data]
        print(f"Bz range: {min(bz_values):.1f} to {max(bz_values):.1f} nT")


if __name__ == "__main__":
    test_dscovr()
