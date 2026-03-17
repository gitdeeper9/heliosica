"""
NMDB (Neutron Monitor Database) Loader
HELIOSICA - Heliospheric Event and L1 Integrated Observatory

Real-time and historical neutron monitor data for Forbush decrease detection
"""

import numpy as np
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import time


@dataclass
class NeutronData:
    """Single neutron monitor measurement"""
    timestamp: datetime
    counts: float           # Count rate (counts/minute)
    station: str            # Station code
    latitude: float         # Station latitude
    longitude: float        # Station longitude
    altitude: float         # Station altitude (m)
    cutoff: float           # Geomagnetic cutoff rigidity (GV)


class NMDBLoader:
    """
    Loader for Neutron Monitor Database
    
    Provides real-time and historical cosmic ray data
    Used for Forbush decrease detection (Fd parameter)
    """
    
    # NMDB API endpoints
    BASE_URL = "http://www.nmdb.eu/nest/data"
    
    # Major neutron monitor stations
    STATIONS = {
        'oulu': {
            'name': 'Oulu',
            'country': 'Finland',
            'latitude': 65.05,
            'longitude': 25.47,
            'altitude': 15,
            'cutoff': 0.8,
            'active': True
        },
        'climax': {
            'name': 'Climax',
            'country': 'USA',
            'latitude': 39.37,
            'longitude': -106.18,
            'altitude': 3400,
            'cutoff': 3.0,
            'active': True
        },
        'mcmurdo': {
            'name': 'McMurdo',
            'country': 'Antarctica',
            'latitude': -77.85,
            'longitude': 166.72,
            'altitude': 48,
            'cutoff': 0.01,
            'active': True
        },
        'newark': {
            'name': 'Newark',
            'country': 'USA',
            'latitude': 39.68,
            'longitude': -75.75,
            'altitude': 50,
            'cutoff': 2.4,
            'active': True
        },
        'junge': {
            'name': 'Jungfraujoch',
            'country': 'Switzerland',
            'latitude': 46.55,
            'longitude': 7.98,
            'altitude': 3570,
            'cutoff': 4.5,
            'active': True
        }
    }
    
    def __init__(self, station: str = 'oulu'):
        """
        Initialize NMDB loader
        
        Parameters
        ----------
        station : str
            Station code (oulu, climax, mcmurdo, etc.)
        """
        self.station = station
        self.station_info = self.STATIONS.get(station, self.STATIONS['oulu'])
        
        # Data cache
        self.cache = {}
        self.last_fetch = None
    
    def fetch_realtime(self, minutes: int = 60) -> List[NeutronData]:
        """
        Fetch real-time neutron monitor data
        
        Parameters
        ----------
        minutes : int
            Minutes of history to fetch
        
        Returns
        -------
        List[NeutronData]
            Neutron monitor measurements
        """
        try:
            # Construct API request
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=minutes)
            
            url = f"{self.BASE_URL}/{self.station}/"
            url += f"{start_time.strftime('%Y%m%d%H%M')}/"
            url += f"{end_time.strftime('%Y%m%d%H%M')}/"
            url += "json"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_response(data)
            
        except Exception as e:
            print(f"Error fetching real-time NMDB data: {e}")
            return []
    
    def fetch_historical(self, start_date: datetime, 
                         end_date: datetime) -> List[NeutronData]:
        """
        Fetch historical neutron monitor data
        
        Parameters
        ----------
        start_date : datetime
            Start date
        end_date : datetime
            End date
        
        Returns
        -------
        List[NeutronData]
            Historical measurements
        """
        try:
            url = f"{self.BASE_URL}/{self.station}/"
            url += f"{start_date.strftime('%Y%m%d%H%M')}/"
            url += f"{end_date.strftime('%Y%m%d%H%M')}/"
            url += "json"
            
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_response(data)
            
        except Exception as e:
            print(f"Error fetching historical NMDB data: {e}")
            return []
    
    def _parse_response(self, data: Dict) -> List[NeutronData]:
        """Parse NMDB API response"""
        measurements = []
        
        try:
            # NMDB returns time and count arrays
            times = data.get('time', [])
            counts = data.get('counts', [])
            
            for t_str, count in zip(times, counts):
                try:
                    timestamp = datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
                    
                    measurements.append(NeutronData(
                        timestamp=timestamp,
                        counts=float(count),
                        station=self.station,
                        latitude=self.station_info['latitude'],
                        longitude=self.station_info['longitude'],
                        altitude=self.station_info['altitude'],
                        cutoff=self.station_info['cutoff']
                    ))
                    
                except (ValueError, TypeError):
                    continue
                    
        except Exception as e:
            print(f"Error parsing NMDB response: {e}")
        
        return measurements
    
    def get_current(self) -> Optional[NeutronData]:
        """
        Get most recent measurement
        
        Returns
        -------
        NeutronData or None
            Latest data point
        """
        data = self.fetch_realtime(minutes=5)
        
        if data:
            return data[-1]
        
        return None
    
    def get_daily_average(self, date: datetime) -> Optional[float]:
        """
        Get daily average count rate
        
        Parameters
        ----------
        date : datetime
            Date to get average for
        
        Returns
        -------
        float or None
            Daily average count rate
        """
        start = datetime(date.year, date.month, date.day, 0, 0)
        end = start + timedelta(days=1)
        
        data = self.fetch_historical(start, end)
        
        if data:
            counts = [d.counts for d in data]
            return np.mean(counts)
        
        return None
    
    def get_baseline(self, days: int = 30) -> Tuple[float, float]:
        """
        Get baseline count rate from quiet period
        
        Parameters
        ----------
        days : int
            Number of days to use for baseline
        
        Returns
        -------
        Tuple[float, float]
            (baseline_mean, baseline_std)
        """
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        
        data = self.fetch_historical(start, end)
        
        if len(data) < 10:
            return (0.0, 0.0)
        
        # Remove outliers (likely Forbush events)
        counts = np.array([d.counts for d in data])
        
        # Use median and MAD for robust statistics
        baseline = np.median(counts)
        mad = np.median(np.abs(counts - baseline))
        
        # Keep only points within 3 MAD
        mask = np.abs(counts - baseline) < 3 * mad
        clean_counts = counts[mask]
        
        return (float(np.mean(clean_counts)), float(np.std(clean_counts)))
    
    def detect_forbush_candidate(self, data: List[NeutronData], 
                                  threshold_sigma: float = 3.0) -> List[NeutronData]:
        """
        Detect potential Forbush decrease events
        
        Parameters
        ----------
        data : List[NeutronData]
            Time series data
        threshold_sigma : float
            Detection threshold in sigma
        
        Returns
        -------
        List[NeutronData]
            Points with significant decrease
        """
        if len(data) < 10:
            return []
        
        counts = np.array([d.counts for d in data])
        
        # Calculate running baseline (24-hour window)
        window = 24 * 60  # 24 hours in minutes
        baseline = np.zeros_like(counts)
        
        for i in range(len(counts)):
            start = max(0, i - window)
            end = i
            baseline[i] = np.median(counts[start:end])
        
        # Detect significant decreases
        deviation = (baseline - counts) / baseline
        
        # Find points where deviation > threshold
        candidates = []
        threshold = threshold_sigma * np.std(deviation)
        
        for i, dev in enumerate(deviation):
            if dev > threshold:
                candidates.append(data[i])
        
        return candidates
    
    def get_stations_list(self) -> List[Dict]:
        """
        Get list of available stations
        
        Returns
        -------
        List[Dict]
            Station information
        """
        return [
            {
                'code': code,
                'name': info['name'],
                'country': info['country'],
                'latitude': info['latitude'],
                'longitude': info['longitude'],
                'cutoff': info['cutoff']
            }
            for code, info in self.STATIONS.items()
            if info['active']
        ]
    
    def stream(self, interval_minutes: int = 5, callback=None):
        """
        Stream real-time neutron monitor data
        
        Parameters
        ----------
        interval_minutes : int
            Update interval in minutes
        callback : callable, optional
            Function to call with new data
        """
        print(f"Starting NMDB stream for {self.station.upper()} "
              f"(interval: {interval_minutes} minutes)")
        
        last_count = None
        
        while True:
            try:
                current = self.get_current()
                
                if current and (last_count is None or 
                                abs(current.counts - last_count) > 0.1):
                    
                    if callback:
                        callback(current)
                    else:
                        print(f"\r[{current.timestamp}] {self.station}: "
                              f"{current.counts:.0f} counts/min", end='')
                    
                    last_count = current.counts
                
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\nStream stopped by user")
                break
            except Exception as e:
                print(f"\nError in stream: {e}")
                time.sleep(interval_minutes * 120)


# Example usage
def test_nmdb():
    """Test NMDB loader"""
    # Test Oulu station
    loader = NMDBLoader('oulu')
    
    print(f"Testing NMDB loader for {loader.station.upper()}...")
    
    # Get current data
    current = loader.get_current()
    if current:
        print(f"\nCurrent:")
        print(f"  Time: {current.timestamp}")
        print(f"  Counts: {current.counts:.0f} counts/min")
        print(f"  Cutoff rigidity: {current.cutoff:.1f} GV")
    
    # Get baseline
    baseline_mean, baseline_std = loader.get_baseline(days=7)
    print(f"\nBaseline (7 days):")
    print(f"  Mean: {baseline_mean:.0f} counts/min")
    print(f"  Std: {baseline_std:.0f} counts/min")
    
    # Get last hour
    print(f"\nLast hour of data:")
    data = loader.fetch_realtime(60)
    print(f"  Retrieved {len(data)} measurements")
    
    if len(data) > 5:
        counts = [d.counts for d in data[-5:]]
        print(f"  Last 5: {[int(c) for c in counts]}")
    
    # List available stations
    print(f"\nAvailable stations:")
    stations = loader.get_stations_list()
    for s in stations[:3]:  # Show first 3
        print(f"  {s['code']}: {s['name']}, {s['country']}")


if __name__ == "__main__":
    test_nmdb()
