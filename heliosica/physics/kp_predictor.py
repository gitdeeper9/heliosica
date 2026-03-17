"""
Kp Index Predictor
HELIOSICA - Heliospheric Event and L1 Integrated Observatory
Pure Python - no numpy
"""

import math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class KpPrediction:
    """Kp prediction results"""
    kp_value: float          # Predicted Kp (0-9 scale)
    kp_lower: float          # Lower bound (1σ)
    kp_upper: float          # Upper bound (1σ)
    g_category: str          # G scale category (G0-G5)
    contributors: Dict[str, float]  # Individual term contributions


class KpPredictor:
    """
    Kp index predictor based on solar wind parameters
    
    Coefficients determined by non-linear least squares regression
    against 312 validation events with leave-one-year-out cross-validation
    """
    
    # Coefficients from 312-event validation - EXACT VALUES from paper
    ALPHA_1 = 1.82  # Ey term coefficient
    ALPHA_2 = 0.64  # P_ram term coefficient
    ALPHA_3 = 0.41  # V term coefficient
    BETA = 0.78     # V term exponent
    ALPHA_4 = 0.35  # Clock angle coefficient
    KP_BASE = 1.0   # Quiet-time baseline
    
    # Reference values
    P0 = 2.1  # Reference ram pressure (nPa)
    V0 = 400  # Reference velocity (km/s)
    
    # Uncertainty (1σ) from validation
    PREDICTION_SIGMA = 0.6  # Kp units
    
    def __init__(self, uncertainty: bool = True):
        """
        Initialize Kp predictor
        
        Parameters
        ----------
        uncertainty : bool
            If True, return uncertainty bounds
        """
        self.uncertainty = uncertainty
    
    def ey_term(self, Ey: float) -> float:
        """
        Reconnection electric field term
        
        α₁·ln(1+Ey)  - Ey in mV/m
        
        Parameters
        ----------
        Ey : float
            Reconnection electric field (mV/m)
        
        Returns
        -------
        float
            Ey contribution to Kp
        """
        if Ey < 0:
            Ey = 0
        return self.ALPHA_1 * math.log(1 + Ey)
    
    def pram_term(self, P_ram: float) -> float:
        """
        Ram pressure term
        
        α₂·ln(P_ram / P₀)
        
        Parameters
        ----------
        P_ram : float
            Solar wind ram pressure (nPa)
        
        Returns
        -------
        float
            P_ram contribution to Kp
        """
        if P_ram <= 0:
            return 0
        return self.ALPHA_2 * math.log(P_ram / self.P0)
    
    def velocity_term(self, V: float) -> float:
        """
        Solar wind velocity term
        
        α₃·(V / V₀)^β
        
        Parameters
        ----------
        V : float
            Solar wind velocity (km/s)
        
        Returns
        -------
        float
            Velocity contribution to Kp
        """
        if V <= 0:
            return 0
        return self.ALPHA_3 * ((V / self.V0) ** self.BETA)
    
    def clock_angle_term(self, theta_IMF: float) -> float:
        """
        IMF clock angle term
        
        α₄·cos(θ_IMF)
        
        Parameters
        ----------
        theta_IMF : float
            IMF clock angle (degrees)
            0° = fully northward, 180° = fully southward
        
        Returns
        -------
        float
            Clock angle contribution to Kp
        """
        theta_rad = theta_IMF * math.pi / 180.0
        return self.ALPHA_4 * math.cos(theta_rad)
    
    def predict(self, Ey: float, P_ram: float, V: float, 
                theta_IMF: float) -> KpPrediction:
        """
        Predict Kp index from solar wind parameters
        
        Kp = α₁·ln(1+Ey) + α₂·ln(P_ram/P₀) + α₃·(V/V₀)^β + α₄·cos(θ) + Kp_base
        
        Parameters
        ----------
        Ey : float
            Reconnection electric field (mV/m)
        P_ram : float
            Solar wind ram pressure (nPa)
        V : float
            Solar wind velocity (km/s)
        theta_IMF : float
            IMF clock angle (degrees)
        
        Returns
        -------
        KpPrediction
            Kp prediction with uncertainty
        """
        # Compute individual terms
        term1 = self.ey_term(Ey)
        term2 = self.pram_term(P_ram)
        term3 = self.velocity_term(V)
        term4 = self.clock_angle_term(theta_IMF)
        
        # Sum all contributions
        kp_raw = term1 + term2 + term3 + term4 + self.KP_BASE
        
        # Clip to valid Kp range (0-9)
        kp_value = max(0, min(9, kp_raw))
        
        # Determine G category
        g_category = self.kp_to_g_category(kp_value)
        
        # Uncertainty bounds
        if self.uncertainty:
            kp_lower = max(0, min(9, kp_value - self.PREDICTION_SIGMA))
            kp_upper = max(0, min(9, kp_value + self.PREDICTION_SIGMA))
        else:
            kp_lower = kp_upper = kp_value
        
        # Contributors for diagnostics
        contributors = {
            'ey_term': term1,
            'pram_term': term2,
            'velocity_term': term3,
            'clock_term': term4,
            'baseline': self.KP_BASE
        }
        
        return KpPrediction(
            kp_value=kp_value,
            kp_lower=kp_lower,
            kp_upper=kp_upper,
            g_category=g_category,
            contributors=contributors
        )
    
    def kp_to_g_category(self, kp: float) -> str:
        """
        Convert Kp value to G-scale category
        
        Parameters
        ----------
        kp : float
            Kp index value (0-9)
        
        Returns
        -------
        str
            G-scale category (G0-G5)
        """
        if kp < 5:
            return 'G0'
        elif kp < 6:
            return 'G1'
        elif kp < 7:
            return 'G2'
        elif kp < 8:
            return 'G3'
        elif kp < 9:
            return 'G4'
        else:
            return 'G5'
    
    def get_storm_severity(self, kp: float) -> Dict[str, str]:
        """
        Get descriptive storm severity
        
        Parameters
        ----------
        kp : float
            Kp index value
        
        Returns
        -------
        Dict
            Severity description
        """
        if kp < 5:
            return {
                'category': 'Quiet',
                'effects': 'No significant geomagnetic activity'
            }
        elif kp < 6:
            return {
                'category': 'Minor storm (G1)',
                'effects': 'Weak power grid fluctuations; minor impact on satellites'
            }
        elif kp < 7:
            return {
                'category': 'Moderate storm (G2)',
                'effects': 'High-latitude power systems affected; spacecraft orbit corrections needed'
            }
        elif kp < 8:
            return {
                'category': 'Strong storm (G3)',
                'effects': 'Voltage corrections可能 required; satellite charging possible'
            }
        elif kp < 9:
            return {
                'category': 'Severe storm (G4)',
                'effects': 'Widespread voltage control problems; satellite drag increases'
            }
        else:
            return {
                'category': 'Extreme storm (G5)',
                'effects': 'Widespread power grid collapse; satellites at risk; aurora at low latitudes'
            }


# Validation against historical events
def validate_halloween():
    """Validate against Halloween 2003 event"""
    predictor = KpPredictor()
    
    # Halloween 2003 conditions
    Ey = 22.4  # 22.4 mV/m
    P_ram = 34.8  # nPa
    V = 1850  # km/s
    theta = 150  # degrees (mostly southward)
    
    pred = predictor.predict(Ey, P_ram, V, theta)
    
    print("Halloween 2003 Kp Validation:")
    print(f"Predicted Kp: {pred.kp_value:.1f} ({pred.g_category})")
    print(f"Uncertainty: {pred.kp_lower:.1f}-{pred.kp_upper:.1f}")
    print(f"Actual Kp: 9.0 (G5)")
    print("\nContributions:")
    for term, value in pred.contributors.items():
        print(f"  {term}: {value:.2f}")
    
    return pred


def validate_stpatricks():
    """Validate against St. Patrick's Day 2015"""
    predictor = KpPredictor()
    
    # St. Patrick's Day 2015 conditions
    Ey = 7.3  # 7.3 mV/m
    P_ram = 12.5  # nPa
    V = 620  # km/s
    theta = 140  # degrees
    
    pred = predictor.predict(Ey, P_ram, V, theta)
    
    print("\nSt. Patrick's Day 2015 Validation:")
    print(f"Predicted Kp: {pred.kp_value:.1f} ({pred.g_category})")
    print(f"Actual Kp: 8.0 (G4)")
    print(f"Within uncertainty: {pred.kp_lower <= 8.0 <= pred.kp_upper}")
    
    return pred


if __name__ == "__main__":
    validate_halloween()
    validate_stpatricks()
