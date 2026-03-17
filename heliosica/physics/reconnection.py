"""
Reconnection Electric Field Calculator
HELIOSICA - Heliospheric Event and L1 Integrated Observatory
Pure Python - no numpy
"""

import math
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class ReconnectionResult:
    """Reconnection electric field calculation results"""
    ey: float               # Electric field (mV/m)
    bz: float               # IMF Bz (nT)
    vsw: float              # Solar wind velocity (km/s)
    energy_injection: str    # Categorization: "none", "low", "moderate", "high", "severe", "extreme"
    threshold_exceeded: bool # True if Ey > G5 threshold


class ReconnectionElectricField:
    """
    Reconnection electric field calculator
    
    Ey = Vsw · |Bz| is the primary energy injection parameter
    for geomagnetic storms. Units: Vsw (km/s) * Bz (nT) = Ey (mV/m)
    """
    
    # Thresholds (mV/m)
    THRESHOLDS = {
        'G1': 2.0,    # 2.0 mV/m
        'G2': 3.5,    # 3.5 mV/m
        'G3': 5.0,    # 5.0 mV/m
        'G4': 8.0,    # 8.0 mV/m
        'G5': 12.0    # 12.0 mV/m
    }
    
    # Energy injection categories (mV/m)
    ENERGY_LEVELS = [
        (0, 2.0, "none"),
        (2.0, 3.5, "low"),
        (3.5, 5.0, "moderate"),
        (5.0, 8.0, "high"),
        (8.0, 12.0, "severe"),
        (12.0, float('inf'), "extreme")
    ]
    
    @staticmethod
    def compute_ey(Vsw: float, Bz: float) -> float:
        """
        Compute reconnection electric field
        
        Ey = Vsw · |Bz| for Bz < 0
        Ey = 0 for Bz >= 0
        
        Parameters
        ----------
        Vsw : float
            Solar wind velocity (km/s)
        Bz : float
            IMF Bz component (nT)
        
        Returns
        -------
        float
            Reconnection electric field (mV/m)
        """
        if Bz >= 0:
            return 0.0
        
        # 1 km/s * 1 nT = 1 mV/m
        return Vsw * abs(Bz)
    
    def get_energy_category(self, ey: float) -> str:
        """
        Categorize energy injection level
        
        Parameters
        ----------
        ey : float
            Electric field (mV/m)
        
        Returns
        -------
        str
            Energy category
        """
        for low, high, category in self.ENERGY_LEVELS:
            if low <= ey < high:
                return category
        return "unknown"
    
    def check_threshold(self, ey: float, threshold: str = 'G5') -> bool:
        """
        Check if Ey exceeds specified threshold
        
        Parameters
        ----------
        ey : float
            Electric field (mV/m)
        threshold : str
            Threshold level ('G1' through 'G5')
        
        Returns
        -------
        bool
            True if threshold exceeded
        """
        return ey >= self.THRESHOLDS.get(threshold, float('inf'))
    
    def evaluate(self, Vsw: float, Bz: float) -> ReconnectionResult:
        """
        Complete evaluation of reconnection conditions
        
        Parameters
        ----------
        Vsw : float
            Solar wind velocity (km/s)
        Bz : float
            IMF Bz component (nT)
        
        Returns
        -------
        ReconnectionResult
            Complete evaluation
        """
        ey = self.compute_ey(Vsw, Bz)
        category = self.get_energy_category(ey)
        threshold_exceeded = self.check_threshold(ey, 'G5')
        
        return ReconnectionResult(
            ey=ey,
            bz=Bz,
            vsw=Vsw,
            energy_injection=category,
            threshold_exceeded=threshold_exceeded
        )
    
    @staticmethod
    def storm_severity_from_ey(ey: float) -> Tuple[str, float]:
        """
        Estimate storm severity from Ey alone
        
        Parameters
        ----------
        ey : float
            Electric field (mV/m)
        
        Returns
        -------
        Tuple[str, float]
            (severity_category, probability)
        """
        if ey < 2.0:
            return "G0-G1", 0.95
        elif ey < 3.5:
            return "G1", 0.85
        elif ey < 5.0:
            return "G2", 0.80
        elif ey < 8.0:
            return "G3", 0.75
        elif ey < 12.0:
            return "G4", 0.70
        else:
            return "G5", 0.65
    
    def integrate_over_period(self, ey_timeseries: list, 
                              dt_minutes: float = 1.0) -> dict:
        """
        Integrate energy input over time period
        
        Parameters
        ----------
        ey_timeseries : list
            Ey values over time (mV/m)
        dt_minutes : float
            Time step in minutes
        
        Returns
        -------
        dict
            Integrated energy metrics
        """
        dt_hours = dt_minutes / 60.0
        
        total_energy = sum(ey_timeseries) * dt_hours
        peak_ey = max(ey_timeseries) if ey_timeseries else 0
        time_above_g5 = sum(1 for ey in ey_timeseries if ey > self.THRESHOLDS['G5']) * dt_hours
        
        mean_ey = total_energy / len(ey_timeseries) if ey_timeseries else 0
        
        return {
            'total_energy': total_energy,
            'peak_ey': peak_ey,
            'time_above_g5': time_above_g5,
            'mean_ey': mean_ey
        }


# Validation against historical events
def validate_halloween():
    """Validate against Halloween 2003 event"""
    reconnection = ReconnectionElectricField()
    
    # Halloween 2003 conditions
    Vsw = 1850  # km/s (peak)
    Bz = -12.1  # nT (southward)
    
    result = reconnection.evaluate(Vsw, Bz)
    
    print("Halloween 2003 Reconnection Validation:")
    print(f"Ey = {result.ey:.1f} mV/m")
    print(f"Energy category: {result.energy_injection}")
    print(f"G5 threshold exceeded: {result.threshold_exceeded}")
    
    return result


def validate_stpatricks():
    """Validate against St. Patrick's Day 2015"""
    reconnection = ReconnectionElectricField()
    
    # St. Patrick's Day 2015 conditions
    Vsw = 620  # km/s
    Bz = -11.8  # nT
    
    result = reconnection.evaluate(Vsw, Bz)
    
    print("\nSt. Patrick's Day 2015 Validation:")
    print(f"Ey = {result.ey:.1f} mV/m")
    print(f"Energy category: {result.energy_injection}")
    
    return result


if __name__ == "__main__":
    validate_halloween()
    validate_stpatricks()
