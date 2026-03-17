"""
OMNI Heliospheric Dataset Loader
HELIOSICA - Heliospheric Event and L1 Integrated Observatory

High-resolution (1-hour) merged multi-spacecraft solar wind data
"""

import numpy as np
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import h5py


@dataclass
class OMNIInterval:
    """Single OMNI data interval"""
    timestamp: datetime
    bz: float           # IMF Bz (nT)
    by: float           # IMF By (nT)
    bx: float           # IMF Bx (nT)
    vsw: float          # Solar wind velocity (km/s)
    np: float           # Proton density (cm⁻³)
    tp: float           # Proton temperature (K)
    kp: Optional[float] # Kp index
    dst: Optional[float] # Dst index (nT)


class OMNILoader:
    """
    Loader for OMNI heliospheric dataset
    
    Provides historical solar wind data for validation
    Coverage: 1963-present (1-hour and 5-minute resolution)
    """
    
    # NASA CDAWeb API
    CDAWEB_URL = "https://cdaweb.gsfc.nasa.gov/WS/cdasr/1/dataviews/spase_observatory/OMNI/data"
    
    # Local cache
    CACHE_DIR = "data/raw/omni"
    
    # OMNI variables
    VARIABLES = {
        'bz_gsm': 'bz',      # Bz GSM (nT)
        'by_gsm': 'by',      # By GSM (nT)  
        'bx_gsm': 'bx',      # Bx GSM (nT)
        'vsw': 'vsw',        # Solar wind speed (km/s)
        'np': 'np',          # Proton density (cm⁻³)
        'tp': 'tp',          # Proton temperature (K)
        'kp': 'kp',          # Kp index
        'dst': 'dst'         # Dst index (nT)
    }
    
    def __init__(self, cache_enabled: bool = True):
        """
        Initialize OMNI loader
        
        Parameters
        ----------
        cache_enabled : bool
            Whether to cache downloaded data
        """
        self.cache_enabled = cache_enabled
        self.data_cache = {}
        
        if cache_enabled:
            os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    def _get_cache_path(self, year: int) -> str:
        """Get cache file path for year"""
        return os.path.join(self.CACHE_DIR, f"omni_{year}.h5")
    
    def fetch_year(self, year: int) -> List[OMNIInterval]:
        """
        Fetch OMNI data for a specific year
        
        Parameters
        ----------
        year : int
            Year to fetch
        
        Returns
        -------
        List[OMNIInterval]
            List of hourly OMNI data
        """
        # Check cache first
        cache_path = self._get_cache_path(year)
        if self.cache_enabled and os.path.exists(cache_path):
            return self._load_from_cache(year)
        
        # Construct API request
        start_date = f"{year}-01-01T00:00:00"
        end_date = f"{year}-12-31T23:59:59"
        
        url = f"{self.CDAWEB_URL}/{start_date},{end_date}/"
        url += ",".join(self.VARIABLES.keys())
        url += "?format=json"
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            intervals = self._parse_omni_response(data)
            
            # Cache if enabled
            if self.cache_enabled:
                self._save_to_cache(year, intervals)
            
            return intervals
            
        except Exception as e:
            print(f"Error fetching OMNI data for {year}: {e}")
            return []
    
    def _parse_omni_response(self, data: Dict) -> List[OMNIInterval]:
        """Parse OMNI API response"""
        intervals = []
        
        try:
            # Extract time array
            times = data.get('Time', [])
            
            # Extract data arrays
            data_arrays = {}
            for omni_var, heliosica_var in self.VARIABLES.items():
                if omni_var in data:
                    data_arrays[heliosica_var] = data[omni_var]
            
            # Create intervals
            for i, time_str in enumerate(times):
                try:
                    timestamp = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    
                    interval = OMNIInterval(
                        timestamp=timestamp,
                        bz=float(data_arrays.get('bz', [0])[i]) if i < len(data_arrays.get('bz', [])) else 0,
                        by=float(data_arrays.get('by', [0])[i]) if i < len(data_arrays.get('by', [])) else 0,
                        bx=float(data_arrays.get('bx', [0])[i]) if i < len(data_arrays.get('bx', [])) else 0,
                        vsw=float(data_arrays.get('vsw', [0])[i]) if i < len(data_arrays.get('vsw', [])) else 0,
                        np=float(data_arrays.get('np', [0])[i]) if i < len(data_arrays.get('np', [])) else 0,
                        tp=float(data_arrays.get('tp', [0])[i]) if i < len(data_arrays.get('tp', [])) else 0,
                        kp=float(data_arrays.get('kp', [0])[i]) if i < len(data_arrays.get('kp', [])) else None,
                        dst=float(data_arrays.get('dst', [0])[i]) if i < len(data_arrays.get('dst', [])) else None
                    )
                    
                    intervals.append(interval)
                    
                except (ValueError, IndexError):
                    continue
                    
        except Exception as e:
            print(f"Error parsing OMNI response: {e}")
        
        return intervals
    
    def _save_to_cache(self, year: int, intervals: List[OMNIInterval]):
        """Save data to HDF5 cache"""
        try:
            cache_path = self._get_cache_path(year)
            
            with h5py.File(cache_path, 'w') as f:
                # Create datasets
                n_points = len(intervals)
                
                timestamps = np.array([int(i.timestamp.timestamp()) for i in intervals])
                bz = np.array([i.bz for i in intervals])
                by = np.array([i.by for i in intervals])
                bx = np.array([i.bx for i in intervals])
                vsw = np.array([i.vsw for i in intervals])
                np_arr = np.array([i.np for i in intervals])
                tp = np.array([i.tp for i in intervals])
                
                f.create_dataset('timestamps', data=timestamps)
                f.create_dataset('bz', data=bz)
                f.create_dataset('by', data=by)
                f.create_dataset('bx', data=bx)
                f.create_dataset('vsw', data=vsw)
                f.create_dataset('np', data=np_arr)
                f.create_dataset('tp', data=tp)
                
                if intervals[0].kp is not None:
                    kp = np.array([i.kp or -1 for i in intervals])
                    f.create_dataset('kp', data=kp)
                
                if intervals[0].dst is not None:
                    dst = np.array([i.dst or 0 for i in intervals])
                    f.create_dataset('dst', data=dst)
                
                f.attrs['year'] = year
                f.attrs['n_points'] = n_points
                
        except Exception as e:
            print(f"Error saving to cache: {e}")
    
    def _load_from_cache(self, year: int) -> List[OMNIInterval]:
        """Load data from HDF5 cache"""
        intervals = []
        
        try:
            cache_path = self._get_cache_path(year)
            
            with h5py.File(cache_path, 'r') as f:
                timestamps = f['timestamps'][:]
                bz = f['bz'][:]
                by = f['by'][:]
                bx = f['bx'][:]
                vsw = f['vsw'][:]
                np_arr = f['np'][:]
                tp = f['tp'][:]
                
                kp = f.get('kp')
                dst = f.get('dst')
                
                for i in range(len(timestamps)):
                    interval = OMNIInterval(
                        timestamp=datetime.fromtimestamp(timestamps[i]),
                        bz=float(bz[i]),
                        by=float(by[i]),
                        bx=float(bx[i]),
                        vsw=float(vsw[i]),
                        np=float(np_arr[i]),
                        tp=float(tp[i]),
                        kp=float(kp[i]) if kp is not None and kp[i] >= 0 else None,
                        dst=float(dst[i]) if dst is not None else None
                    )
                    intervals.append(interval)
                    
        except Exception as e:
            print(f"Error loading from cache: {e}")
        
        return intervals
    
    def get_range(self, start_date: datetime, end_date: datetime) -> List[OMNIInterval]:
        """
        Get OMNI data for a date range
        
        Parameters
        ----------
        start_date : datetime
            Start date
        end_date : datetime
            End date
        
        Returns
        -------
        List[OMNIInterval]
            OMNI data in range
        """
        all_data = []
        
        # Fetch year by year
        current_year = start_date.year
        end_year = end_date.year
        
        while current_year <= end_year:
            year_data = self.fetch_year(current_year)
            all_data.extend(year_data)
            current_year += 1
        
        # Filter by date range
        filtered = [
            d for d in all_data 
            if start_date <= d.timestamp <= end_date
        ]
        
        return filtered
    
    def get_storm_events(self, min_kp: float = 5.0, 
                         years: Optional[List[int]] = None) -> List[OMNIInterval]:
        """
        Get storm events meeting Kp threshold
        
        Parameters
        ----------
        min_kp : float
            Minimum Kp index
        years : List[int], optional
            Years to search (default: 1996-2025)
        
        Returns
        -------
        List[OMNIInterval]
            Storm events
        """
        if years is None:
            years = list(range(1996, 2026))
        
        storms = []
        
        for year in years:
            year_data = self.fetch_year(year)
            
            for interval in year_data:
                if interval.kp and interval.kp >= min_kp:
                    storms.append(interval)
        
        return storms
    
    def to_dataframe(self, intervals: List[OMNIInterval]):
        """
        Convert to pandas DataFrame
        
        Parameters
        ----------
        intervals : List[OMNIInterval]
            OMNI data
        
        Returns
        -------
        pandas.DataFrame
            DataFrame with all data
        """
        try:
            import pandas as pd
            
            df = pd.DataFrame([
                {
                    'timestamp': i.timestamp,
                    'bz': i.bz,
                    'by': i.by,
                    'bx': i.bx,
                    'vsw': i.vsw,
                    'np': i.np,
                    'tp': i.tp,
                    'kp': i.kp,
                    'dst': i.dst
                }
                for i in intervals
            ])
            
            df.set_index('timestamp', inplace=True)
            return df
            
        except ImportError:
            print("pandas not installed")
            return None
    
    def compute_statistics(self, intervals: List[OMNIInterval]) -> Dict[str, float]:
        """
        Compute statistics for data intervals
        
        Parameters
        ----------
        intervals : List[OMNIInterval]
            OMNI data
        
        Returns
        -------
        Dict[str, float]
            Statistical summary
        """
        if not intervals:
            return {}
        
        bz_values = [i.bz for i in intervals]
        vsw_values = [i.vsw for i in intervals]
        np_values = [i.np for i in intervals]
        kp_values = [i.kp for i in intervals if i.kp is not None]
        dst_values = [i.dst for i in intervals if i.dst is not None]
        
        return {
            'n_points': len(intervals),
            'mean_bz': np.mean(bz_values),
            'min_bz': np.min(bz_values),
            'max_bz': np.max(bz_values),
            'std_bz': np.std(bz_values),
            'mean_vsw': np.mean(vsw_values),
            'min_vsw': np.min(vsw_values),
            'max_vsw': np.max(vsw_values),
            'mean_np': np.mean(np_values),
            'mean_kp': np.mean(kp_values) if kp_values else 0,
            'max_kp': np.max(kp_values) if kp_values else 0,
            'mean_dst': np.mean(dst_values) if dst_values else 0,
            'min_dst': np.min(dst_values) if dst_values else 0
        }


# Example usage
def test_omni():
    """Test OMNI loader"""
    loader = OMNILoader()
    
    # Test 2003 Halloween storm
    start = datetime(2003, 10, 28)
    end = datetime(2003, 10, 31)
    
    print(f"Fetching OMNI data for Halloween 2003...")
    data = loader.get_range(start, end)
    
    print(f"Retrieved {len(data)} intervals")
    
    if data:
        stats = loader.compute_statistics(data)
        print("\nStatistics:")
        for key, value in stats.items():
            print(f"  {key}: {value:.2f}")
        
        # Find peak
        bz_values = [d.bz for d in data]
        min_bz_idx = np.argmin(bz_values)
        peak = data[min_bz_idx]
        
        print(f"\nPeak storm time:")
        print(f"  {peak.timestamp}: Bz={peak.bz:.1f} nT, Vsw={peak.vsw:.0f} km/s")
    
    # Get major storms
    print("\nFetching major storms (Kp≥8)...")
    storms = loader.get_storm_events(min_kp=8, years=[2003])
    print(f"Found {len(storms)} major storms in 2003")


if __name__ == "__main__":
    test_omni()
