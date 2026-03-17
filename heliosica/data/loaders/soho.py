"""
SOHO/LASCO CME Catalogue Loader
HELIOSICA - Heliospheric Event and L1 Integrated Observatory

Load CME parameters (V₀, ω) from SOHO/LASCO coronagraph observations
"""

import numpy as np
import requests
import csv
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os


@dataclass
class CME:
    """Coronal Mass Ejection data"""
    date: datetime          # Observation date
    velocity: float         # Linear speed (km/s)
    width: float            # Angular width (degrees)
    pa: float               # Position angle (degrees)
    mass: Optional[float]   # Mass (kg)
    kinetic_energy: Optional[float]  # Kinetic energy (J)
    halo: bool              # Whether it's a halo CME


class SOHOLoader:
    """
    Loader for SOHO/LASCO CME catalogue
    
    Provides V₀ and ω parameters for CME events
    """
    
    # Catalogue URLs
    CDAW_URL = "https://cdaw.gsfc.nasa.gov/CME_list"
    LASCO_CATALOG = "/universal/text_format/univ_1996_2025.csv"
    
    # Local cache file
    CACHE_FILE = "data/raw/soho/lasco_cme_catalogue.csv"
    
    def __init__(self, use_cache: bool = True):
        """
        Initialize SOHO loader
        
        Parameters
        ----------
        use_cache : bool
            Whether to use local cache
        """
        self.use_cache = use_cache
        self.cme_list = []
        self.load_catalogue()
    
    def download_catalogue(self) -> List[Dict]:
        """
        Download CME catalogue from CDAW
        
        Returns
        -------
        List[Dict]
            List of CME events
        """
        try:
            url = f"{self.CDAW_URL}{self.LASCO_CATALOG}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV
            lines = response.text.strip().split('\n')
            reader = csv.reader(lines)
            
            cme_list = []
            for row in reader:
                if len(row) < 10:
                    continue
                
                try:
                    # Parse date
                    date_str = f"{row[0]}-{row[1]:>02}-{row[2]:>02}"
                    time_str = f"{row[3]}:{row[4]}:{row[5]}"
                    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                    
                    # Parse parameters
                    velocity = float(row[6]) if row[6] else 0
                    width = float(row[9]) if row[9] else 0
                    pa = float(row[8]) if row[8] else 0
                    
                    # Check if halo CME
                    halo = width >= 360 or (width >= 300 and row[9].strip() == "Halo")
                    
                    cme = {
                        'date': dt,
                        'velocity': velocity,
                        'width': width,
                        'pa': pa,
                        'halo': halo
                    }
                    
                    cme_list.append(cme)
                    
                except (ValueError, IndexError):
                    continue
            
            # Cache locally
            if self.use_cache:
                self._save_to_cache(cme_list)
            
            return cme_list
            
        except Exception as e:
            print(f"Error downloading catalogue: {e}")
            return []
    
    def _save_to_cache(self, cme_list: List[Dict]):
        """Save catalogue to local cache"""
        try:
            os.makedirs(os.path.dirname(self.CACHE_FILE), exist_ok=True)
            
            with open(self.CACHE_FILE, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'velocity', 'width', 'pa', 'halo'])
                
                for cme in cme_list:
                    writer.writerow([
                        cme['date'].isoformat(),
                        cme['velocity'],
                        cme['width'],
                        cme['pa'],
                        cme['halo']
                    ])
                    
        except Exception as e:
            print(f"Error saving to cache: {e}")
    
    def _load_from_cache(self) -> List[Dict]:
        """Load catalogue from local cache"""
        try:
            if not os.path.exists(self.CACHE_FILE):
                return []
            
            cme_list = []
            with open(self.CACHE_FILE, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                
                for row in reader:
                    if len(row) < 5:
                        continue
                    
                    try:
                        cme = {
                            'date': datetime.fromisoformat(row[0]),
                            'velocity': float(row[1]),
                            'width': float(row[2]),
                            'pa': float(row[3]),
                            'halo': row[4] == 'True'
                        }
                        cme_list.append(cme)
                    except (ValueError, IndexError):
                        continue
            
            return cme_list
            
        except Exception as e:
            print(f"Error loading from cache: {e}")
            return []
    
    def load_catalogue(self):
        """Load CME catalogue (from cache or download)"""
        if self.use_cache:
            self.cme_list = self._load_from_cache()
        
        if not self.cme_list:
            print("Downloading SOHO/LASCO catalogue...")
            self.cme_list = self.download_catalogue()
            print(f"Loaded {len(self.cme_list)} CME events")
    
    def get_cme(self, date: datetime) -> Optional[CME]:
        """
        Get CME parameters for specific date
        
        Parameters
        ----------
        date : datetime
            Observation date
        
        Returns
        -------
        CME or None
            CME data if found
        """
        # Find closest CME within 6 hours
        min_delta = timedelta(hours=6)
        best_cme = None
        
        for c in self.cme_list:
            delta = abs(c['date'] - date)
            if delta < min_delta:
                min_delta = delta
                best_cme = c
        
        if best_cme:
            return CME(
                date=best_cme['date'],
                velocity=best_cme['velocity'],
                width=best_cme['width'],
                pa=best_cme['pa'],
                mass=None,
                kinetic_energy=None,
                halo=best_cme['halo']
            )
        
        return None
    
    def get_cme_by_id(self, event_id: str) -> Optional[CME]:
        """
        Get CME by event ID (if available)
        
        Parameters
        ----------
        event_id : str
            CME event identifier
        
        Returns
        -------
        CME or None
            CME data if found
        """
        # Simplified - in real implementation would parse event IDs
        return None
    
    def search_cmes(self, start_date: datetime, end_date: datetime,
                    min_velocity: float = 0, min_width: float = 0) -> List[CME]:
        """
        Search for CMEs in date range
        
        Parameters
        ----------
        start_date : datetime
            Start of search period
        end_date : datetime
            End of search period
        min_velocity : float
            Minimum velocity (km/s)
        min_width : float
            Minimum angular width (degrees)
        
        Returns
        -------
        List[CME]
            Matching CME events
        """
        results = []
        
        for c in self.cme_list:
            if start_date <= c['date'] <= end_date:
                if c['velocity'] >= min_velocity and c['width'] >= min_width:
                    results.append(CME(
                        date=c['date'],
                        velocity=c['velocity'],
                        width=c['width'],
                        pa=c['pa'],
                        mass=None,
                        kinetic_energy=None,
                        halo=c['halo']
                    ))
        
        return results
    
    def get_statistics(self) -> Dict[str, float]:
        """
        Get CME catalogue statistics
        
        Returns
        -------
        Dict[str, float]
            Statistical summary
        """
        velocities = [c['velocity'] for c in self.cme_list if c['velocity'] > 0]
        widths = [c['width'] for c in self.cme_list if c['width'] > 0]
        
        return {
            'total_cmes': len(self.cme_list),
            'mean_velocity': np.mean(velocities) if velocities else 0,
            'median_velocity': np.median(velocities) if velocities else 0,
            'std_velocity': np.std(velocities) if velocities else 0,
            'max_velocity': max(velocities) if velocities else 0,
            'mean_width': np.mean(widths) if widths else 0,
            'halo_count': sum(1 for c in self.cme_list if c['halo']),
            'fast_cmes_1000': sum(1 for c in self.cme_list if c['velocity'] > 1000)
        }
    
    def get_velocity_distribution(self, bins: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get histogram of CME velocities
        
        Parameters
        ----------
        bins : int
            Number of histogram bins
        
        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Histogram counts and bin edges
        """
        velocities = [c['velocity'] for c in self.cme_list if c['velocity'] > 0]
        hist, bin_edges = np.histogram(velocities, bins=bins)
        return hist, bin_edges
    
    def get_geoeffective_cmes(self, min_velocity: float = 800,
                               min_width: float = 120) -> List[CME]:
        """
        Get potentially geoeffective CMEs
        
        Parameters
        ----------
        min_velocity : float
            Minimum velocity for geoeffectiveness (km/s)
        min_width : float
            Minimum width for geoeffectiveness (degrees)
        
        Returns
        -------
        List[CME]
            Geoeffective CMEs
        """
        results = []
        
        for c in self.cme_list:
            if c['velocity'] >= min_velocity and c['width'] >= min_width:
                results.append(CME(
                    date=c['date'],
                    velocity=c['velocity'],
                    width=c['width'],
                    pa=c['pa'],
                    mass=None,
                    kinetic_energy=None,
                    halo=c['halo']
                ))
        
        return results


# Example usage
def test_soho():
    """Test SOHO loader"""
    loader = SOHOLoader()
    
    print("SOHO/LASCO CME Catalogue Statistics:")
    stats = loader.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Search for fast CMEs in 2003
    start = datetime(2003, 1, 1)
    end = datetime(2003, 12, 31)
    
    fast_cmes = loader.search_cmes(start, end, min_velocity=1500)
    print(f"\nFast CMEs in 2003 (>1500 km/s): {len(fast_cmes)}")
    
    for cme in fast_cmes[:5]:  # Show first 5
        print(f"  {cme.date}: {cme.velocity} km/s, width={cme.width}°, halo={cme.halo}")


if __name__ == "__main__":
    test_soho()
