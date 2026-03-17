"""
Magnetopause Standoff Distance Calculator
HELIOSICA - Heliospheric Event and L1 Integrated Observatory
Pure Python - no numpy
"""

import math
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class MagnetopauseResult:
    """Magnetopause calculation results"""
    r_mp_re: float          # Standoff distance (Earth radii)
    r_mp_km: float          # Standoff distance (km)
    satellite_alert: bool   # True if inside GEO orbit
    compression_ratio: float # R_MP / R_MP_nominal
    timestamp: datetime     # Calculation time


class MagnetopauseTracker:
    """
    Real-time magnetopause standoff distance tracker
    
    Monitors solar wind ram pressure and computes magnetopause location
    Issues alerts when magnetopause compresses inside geosynchronous orbit
    """
    
    # Constants - EXACT values from physics
    R_EARTH = 6371.0  # Earth radius (km)
    B_EARTH = 31000e-9  # Earth's equatorial magnetic field (T)
    MU0 = 4e-7 * math.pi  # Permeability of free space (H/m)
    
    # Reference values
    R_MP_NOMINAL = 10.5  # Nominal standoff distance (R_E)
    P_RAM_NOMINAL = 2.1  # Nominal ram pressure (nPa)
    
    # Alert thresholds
    GEO_ORBIT = 6.6  # Geosynchronous orbit (R_E)
    SAFETY_MARGIN = 0.4  # Safety margin (R_E)
    ALERT_THRESHOLD = GEO_ORBIT + SAFETY_MARGIN  # 7.0 R_E
    
    def __init__(self, history_size: int = 1440):
        """
        Initialize magnetopause tracker
        
        Parameters
        ----------
        history_size : int
            Number of historical points to keep (default: 1440 = 24 hours at 1-min)
        """
        self.history = []
        self.history_size = history_size
    
    def compute_standoff(self, P_ram: float) -> float:
        """
        Compute magnetopause standoff distance from ram pressure
        
        R_MP = R_E · (B_E² / (2μ₀·P_ram))^(1/6)
        
        Parameters
        ----------
        P_ram : float
            Solar wind ram pressure (nPa)
        
        Returns
        -------
        float
            Standoff distance in Earth radii
        """
        # Convert nPa to Pa
        P_ram_pa = P_ram * 1e-9
        
        # Pressure balance equation
        numerator = self.B_EARTH ** 2
        denominator = 2 * self.MU0 * P_ram_pa
        
        if denominator <= 0:
            return self.R_MP_NOMINAL
        
        # Standoff distance in meters
        r_mp_m = self.R_EARTH * 1000 * (numerator / denominator) ** (1/6)
        
        # Convert to Earth radii
        r_mp_re = r_mp_m / (self.R_EARTH * 1000)
        
        return r_mp_re
    
    def check_satellite_alert(self, r_mp_re: float) -> bool:
        """
        Check if magnetopause is inside safety threshold
        
        Parameters
        ----------
        r_mp_re : float
            Standoff distance in Earth radii
        
        Returns
        -------
        bool
            True if alert should be issued (R_MP < 7.0 R_E)
        """
        return r_mp_re < self.ALERT_THRESHOLD
    
    def get_compression_ratio(self, r_mp_re: float) -> float:
        """
        Compute compression ratio relative to nominal
        
        Parameters
        ----------
        r_mp_re : float
            Standoff distance in Earth radii
        
        Returns
        -------
        float
            R_MP / R_MP_nominal
        """
        return r_mp_re / self.R_MP_NOMINAL
    
    def update(self, P_ram: float, timestamp: Optional[datetime] = None) -> MagnetopauseResult:
        """
        Update magnetopause position with new ram pressure measurement
        
        Parameters
        ----------
        P_ram : float
            Solar wind ram pressure (nPa)
        timestamp : datetime, optional
            Measurement time (defaults to now)
        
        Returns
        -------
        MagnetopauseResult
            Current magnetopause status
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Compute standoff distance
        r_mp_re = self.compute_standoff(P_ram)
        r_mp_km = r_mp_re * self.R_EARTH
        
        # Check alert condition
        alert = self.check_satellite_alert(r_mp_re)
        
        # Compute compression ratio
        compression = self.get_compression_ratio(r_mp_re)
        
        # Store in history
        result = MagnetopauseResult(
            r_mp_re=r_mp_re,
            r_mp_km=r_mp_km,
            satellite_alert=alert,
            compression_ratio=compression,
            timestamp=timestamp
        )
        
        self.history.append(result)
        
        # Trim history if needed
        if len(self.history) > self.history_size:
            self.history = self.history[-self.history_size:]
        
        return result
    
    def get_forecast(self, P_ram_forecast: list, 
                     timestamps: Optional[list] = None) -> list:
        """
        Generate forecast from predicted ram pressure
        
        Parameters
        ----------
        P_ram_forecast : list
            List of predicted ram pressure values
        timestamps : list, optional
            Corresponding timestamps
        
        Returns
        -------
        list
            List of MagnetopauseResult objects for forecast
        """
        if timestamps is None:
            timestamps = [datetime.utcnow() + timedelta(minutes=5*i) 
                         for i in range(len(P_ram_forecast))]
        
        forecast = []
        for P_ram, ts in zip(P_ram_forecast, timestamps):
            result = MagnetopauseResult(
                r_mp_re=self.compute_standoff(P_ram),
                r_mp_km=self.compute_standoff(P_ram) * self.R_EARTH,
                satellite_alert=self.check_satellite_alert(self.compute_standoff(P_ram)),
                compression_ratio=self.get_compression_ratio(self.compute_standoff(P_ram)),
                timestamp=ts
            )
            forecast.append(result)
        
        return forecast
    
    def get_minimum_last_24h(self) -> Optional[float]:
        """
        Get minimum R_MP in last 24 hours
        
        Returns
        -------
        float or None
            Minimum standoff distance
        """
        if not self.history:
            return None
        
        # Filter last 24 hours (1440 minutes at 1-min cadence)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = [h for h in self.history if h.timestamp > cutoff]
        
        if not recent:
            return None
        
        return min(h.r_mp_re for h in recent)
    
    def summary(self) -> dict:
        """
        Get summary statistics
        
        Returns
        -------
        dict
            Summary of magnetopause status
        """
        if not self.history:
            return {"status": "no_data"}
        
        latest = self.history[-1]
        
        return {
            "current_r_mp": latest.r_mp_re,
            "current_alert": latest.satellite_alert,
            "min_24h": self.get_minimum_last_24h(),
            "history_size": len(self.history),
            "nominal_r_mp": self.R_MP_NOMINAL,
            "alert_threshold": self.ALERT_THRESHOLD,
            "compression_ratio": latest.compression_ratio
        }


# Example usage and validation
def validate_halloween():
    """Validate against Halloween 2003 event"""
    tracker = MagnetopauseTracker()
    
    # Halloween 2003 conditions
    P_ram = 34.8  # nPa (peak)
    
    result = tracker.update(P_ram)
    
    print("Halloween 2003 Magnetopause Validation:")
    print(f"R_MP predicted: {result.r_mp_re:.2f} R_E")
    print(f"R_MP actual: 5.1-5.5 R_E")
    print(f"Satellite alert: {result.satellite_alert}")
    print(f"Compression ratio: {result.compression_ratio:.2f}")
    
    return result


if __name__ == "__main__":
    validate_halloween()
