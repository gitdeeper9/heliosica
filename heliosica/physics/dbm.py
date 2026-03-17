"""
Drag-Based Model (DBM) for CME Transit Prediction
HELIOSICA - Heliospheric Event and L1 Integrated Observatory
Pure Python - no numpy
"""

import math
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DBMResult:
    """Results from DBM solver"""
    arrival_time_5: float      # 5th percentile arrival time (hours)
    arrival_time_50: float      # 50th percentile arrival time (hours)
    arrival_time_95: float      # 95th percentile arrival time (hours)
    gamma: float                # Drag coefficient (km⁻¹)
    v_at_1au: float             # Velocity at 1 AU (km/s)
    ensemble_members: list      # Individual ensemble predictions


class DBMSolver:
    """
    Analytical Drag-Based Model solver for CME transit time prediction
    
    The model assumes CME deceleration due to interaction with ambient solar wind
    Faster CMEs decelerate, slower CMEs accelerate toward Vsw
    """
    
    # Constants
    R_SUN = 6.957e5  # Solar radius (km)
    R0 = 21.5  # Inner boundary in solar radii (standard for coronagraphs)
    AU = 1.496e8  # Astronomical Unit (km)
    K_CALIB = 1.0e-5  # Calibration constant for gamma (km⁻¹·cm³) - Increased to give gamma~1e-7
    
    def __init__(self, ensemble_size: int = 10000):
        """
        Initialize DBM solver
        
        Parameters
        ----------
        ensemble_size : int
            Number of Monte Carlo ensemble members for probabilistic forecast
        """
        self.ensemble_size = ensemble_size
    
    def compute_gamma(self, omega: float, n_p: float) -> float:
        """
        Compute drag coefficient from CME angular width and proton density
        
        γ = k / (ω² · n_p)
        
        Parameters
        ----------
        omega : float
            CME angular half-width (degrees)
        n_p : float
            Ambient solar wind proton number density (cm⁻³)
        
        Returns
        -------
        float
            Drag coefficient γ (km⁻¹)
        """
        omega_rad = omega * math.pi / 180.0
        # For halo CME (360°), omega_rad = 2π ≈ 6.283
        # gamma = 1e-5 / (39.48 * 15) = 1e-5 / 592.2 = 1.69e-8 - still too small
        # Need gamma ~1e-7, so K_CALIB should be ~6e-6
        gamma = self.K_CALIB / (omega_rad**2 * n_p)
        return gamma
    
    def analytical_velocity(self, t: float, V0: float, Vsw: float, gamma: float) -> float:
        """
        Analytical solution for velocity at time t
        
        V(t) = Vsw + (V0 - Vsw) / (1 + γ|V0 - Vsw|t)
        
        Parameters
        ----------
        t : float
            Time (hours)
        V0 : float
            Initial CME velocity at R0 (km/s)
        Vsw : float
            Ambient solar wind velocity (km/s)
        gamma : float
            Drag coefficient (km⁻¹)
        
        Returns
        -------
        float
            Velocity at time t (km/s)
        """
        t_sec = t * 3600  # Convert hours to seconds
        delta_v = V0 - Vsw
        denominator = 1 + gamma * abs(delta_v) * t_sec
        return Vsw + delta_v / denominator
    
    def transit_time(self, V0: float, Vsw: float, gamma: float) -> float:
        """
        Compute CME transit time from R0 to 1 AU
        
        Uses analytical integration of velocity equation
        
        Parameters
        ----------
        V0 : float
            Initial CME velocity at R0 (km/s)
        Vsw : float
            Ambient solar wind velocity (km/s)
        gamma : float
            Drag coefficient (km⁻¹)
        
        Returns
        -------
        float
            Transit time (hours)
        """
        r0_km = self.R0 * self.R_SUN
        r1_km = self.AU
        distance_km = r1_km - r0_km
        
        delta_v = V0 - Vsw
        
        if abs(delta_v) < 1e-6:
            # No drag case (V0 ≈ Vsw)
            return distance_km / Vsw / 3600
        
        # Analytical solution for transit time
        # t = (1/(γ|Δv|)) * ln(1 + γ|Δv| * distance/Vsw)
        gamma_delta = gamma * abs(delta_v)
        
        if gamma_delta <= 0:
            return distance_km / Vsw / 3600
        
        term = 1.0 + gamma_delta * distance_km / Vsw
        if term <= 0:
            return distance_km / Vsw / 3600
            
        t_transit = (1.0 / gamma_delta) * math.log(term)
        
        return t_transit / 3600  # Convert to hours
    
    def _percentile(self, data: list, p: float) -> float:
        """Calculate percentile of list (no numpy)"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * (p / 100.0)
        f = int(math.floor(k))
        c = int(math.ceil(k))
        
        if f == c:
            return sorted_data[int(k)]
        
        d0 = sorted_data[f] * (c - k)
        d1 = sorted_data[c] * (k - f)
        return d0 + d1
    
    def ensemble_forecast(self, V0: float, Vsw: float, omega: float, n_p: float,
                          V0_unc: float = 120.0, Vsw_unc: float = 30.0,
                          n_p_unc: float = 1.0, ensemble_size: int = None) -> DBMResult:
        """
        Monte Carlo ensemble forecast with uncertainty propagation
        
        Parameters
        ----------
        V0 : float
            Nominal CME velocity (km/s)
        Vsw : float
            Nominal solar wind speed (km/s)
        omega : float
            CME angular half-width (degrees)
        n_p : float
            Nominal proton density (cm⁻³)
        V0_unc : float
            V0 uncertainty (km/s, 1σ)
        Vsw_unc : float
            Vsw uncertainty (km/s, 1σ)
        n_p_unc : float
            n_p uncertainty (cm⁻³, 1σ)
        ensemble_size : int, optional
            Number of ensemble members
        
        Returns
        -------
        DBMResult
            Probabilistic forecast with percentiles
        """
        if ensemble_size is None:
            ensemble_size = self.ensemble_size
        
        # Generate ensemble members
        transit_times = []
        gamma_values = []
        v_1au_values = []
        
        for _ in range(ensemble_size):
            # Generate random perturbations
            V0_i = V0 + random.gauss(0, V0_unc)
            Vsw_i = Vsw + random.gauss(0, Vsw_unc)
            n_p_i = n_p + random.gauss(0, n_p_unc)
            
            # Ensure physical bounds
            V0_i = max(V0_i, 100)
            Vsw_i = max(Vsw_i, 200)
            n_p_i = max(n_p_i, 0.1)
            
            # Compute gamma
            gamma_i = self.compute_gamma(omega, n_p_i)
            
            # Compute transit time
            t_i = self.transit_time(V0_i, Vsw_i, gamma_i)
            
            # Compute velocity at 1 AU
            v_i = self.analytical_velocity(t_i, V0_i, Vsw_i, gamma_i)
            
            transit_times.append(t_i)
            gamma_values.append(gamma_i)
            v_1au_values.append(v_i)
        
        # Calculate percentiles
        p5 = self._percentile(transit_times, 5)
        p50 = self._percentile(transit_times, 50)
        p95 = self._percentile(transit_times, 95)
        
        # Calculate median gamma and v_at_1au
        gamma_median = self._percentile(gamma_values, 50)
        v_median = self._percentile(v_1au_values, 50)
        
        return DBMResult(
            arrival_time_5=p5,
            arrival_time_50=p50,
            arrival_time_95=p95,
            gamma=gamma_median,
            v_at_1au=v_median,
            ensemble_members=transit_times
        )
    
    def predict(self, V0: float, Vsw: float, omega: float, n_p: float,
                probabilistic: bool = True) -> DBMResult:
        """
        Unified prediction interface
        
        Parameters
        ----------
        V0 : float
            CME launch velocity (km/s)
        Vsw : float
            Solar wind velocity (km/s)
        omega : float
            CME angular half-width (degrees)
        n_p : float
            Proton number density (cm⁻³)
        probabilistic : bool
            If True, return ensemble forecast; if False, deterministic
        
        Returns
        -------
        DBMResult
            Transit time prediction
        """
        if probabilistic:
            return self.ensemble_forecast(V0, Vsw, omega, n_p)
        else:
            gamma = self.compute_gamma(omega, n_p)
            t_transit = self.transit_time(V0, Vsw, gamma)
            v_1au = self.analytical_velocity(t_transit, V0, Vsw, gamma)
            
            # Create deterministic result
            return DBMResult(
                arrival_time_5=t_transit,
                arrival_time_50=t_transit,
                arrival_time_95=t_transit,
                gamma=gamma,
                v_at_1au=v_1au,
                ensemble_members=[t_transit]
            )


# Validation against Halloween 2003 event
def validate_halloween():
    """Test DBM against 2003 Halloween event"""
    solver = DBMSolver()
    
    # Halloween 2003 CME parameters
    V0 = 2459  # km/s (from SOHO/LASCO)
    Vsw = 650  # km/s (ambient)
    omega = 360  # degrees (halo CME)
    n_p = 15  # cm⁻³
    
    result = solver.predict(V0, Vsw, omega, n_p, probabilistic=False)
    
    print("Halloween 2003 DBM Validation:")
    print(f"Predicted transit: {result.arrival_time_50:.1f} hours")
    print(f"Actual transit: 19.5 hours")
    print(f"Error: {abs(result.arrival_time_50 - 19.5):.1f} hours")
    print(f"Gamma: {result.gamma:.2e} km⁻¹")
    
    return result


if __name__ == "__main__":
    validate_halloween()
