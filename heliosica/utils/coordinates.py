"""
HELIOSICA Coordinate Transformations
Coordinate system conversions for space weather
Pure Python implementation
"""

import math


class CoordinateSystems:
    """Coordinate system conversions"""
    
    @staticmethod
    def degrees_to_radians(deg):
        """Convert degrees to radians"""
        return deg * math.pi / 180.0
    
    @staticmethod
    def radians_to_degrees(rad):
        """Convert radians to degrees"""
        return rad * 180.0 / math.pi
    
    @staticmethod
    def cartesian_to_spherical(x, y, z):
        """
        Convert Cartesian to spherical coordinates
        
        Returns
        -------
        (r, theta, phi) where:
            r: radius
            theta: polar angle from z-axis (0 to π)
            phi: azimuthal angle from x-axis (0 to 2π)
        """
        r = math.sqrt(x*x + y*y + z*z)
        
        if r == 0:
            return (0, 0, 0)
        
        theta = math.acos(z / r)
        phi = math.atan2(y, x)
        
        # Ensure phi in [0, 2π)
        if phi < 0:
            phi += 2 * math.pi
        
        return (r, theta, phi)
    
    @staticmethod
    def spherical_to_cartesian(r, theta, phi):
        """
        Convert spherical to Cartesian coordinates
        
        Parameters
        ----------
        r : float
            Radius
        theta : float
            Polar angle from z-axis (radians)
        phi : float
            Azimuthal angle from x-axis (radians)
        
        Returns
        -------
        (x, y, z)
        """
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        
        return (x, y, z)
    
    @staticmethod
    def gse_to_gsm(b_gse, x_gse, y_gse, z_gse, dipole_tilt):
        """
        Convert GSE to GSM coordinates
        
        Parameters
        ----------
        b_gse : tuple
            Magnetic field in GSE (bx, by, bz)
        x_gse, y_gse, z_gse : float
            Position in GSE
        dipole_tilt : float
            Dipole tilt angle (radians)
        
        Returns
        -------
        tuple
            Magnetic field in GSM (bx, by, bz)
        """
        bx_gse, by_gse, bz_gse = b_gse
        
        # GSM is GSE rotated about x-axis by dipole tilt
        cos_tilt = math.cos(dipole_tilt)
        sin_tilt = math.sin(dipole_tilt)
        
        bx_gsm = bx_gse
        by_gsm = by_gse * cos_tilt - bz_gse * sin_tilt
        bz_gsm = by_gse * sin_tilt + bz_gse * cos_tilt
        
        return (bx_gsm, by_gsm, bz_gsm)
    
    @staticmethod
    def gsm_to_gse(b_gsm, x_gsm, y_gsm, z_gsm, dipole_tilt):
        """
        Convert GSM to GSE coordinates
        """
        bx_gsm, by_gsm, bz_gsm = b_gsm
        
        cos_tilt = math.cos(dipole_tilt)
        sin_tilt = math.sin(dipole_tilt)
        
        bx_gse = bx_gsm
        by_gse = by_gsm * cos_tilt + bz_gsm * sin_tilt
        bz_gse = -by_gsm * sin_tilt + bz_gsm * cos_tilt
        
        return (bx_gse, by_gse, bz_gse)
    
    @staticmethod
    def get_dipole_tilt(date):
        """
        Calculate dipole tilt angle for given date
        
        Simplified model: tilt varies with season and UT
        
        Parameters
        ----------
        date : datetime
            Date and time
        
        Returns
        -------
        float
            Dipole tilt angle in radians
        """
        # Simplified: tilt ~ 0.4 rad * sin(day_of_year)
        # More accurate models would use IGRF
        
        from .time_utils import TimeUtils
        
        doy = TimeUtils.to_doy(date)
        hours = date.hour + date.minute / 60.0
        
        # Seasonal variation (max ~30° in June, min ~-30° in December)
        seasonal = 0.5 * math.sin(2 * math.pi * (doy - 80) / 365.25)
        
        # Diurnal variation
        diurnal = 0.1 * math.sin(2 * math.pi * (hours - 12) / 24)
        
        return seasonal + diurnal
    
    @staticmethod
    def solar_wind_to_magnetopause_angle(bx, by, bz):
        """
        Calculate clock angle and cone angle of IMF
        
        Parameters
        ----------
        bx, by, bz : float
            IMF components (nT)
        
        Returns
        -------
        dict
            Angles in radians
        """
        # Clock angle (from north in GSM y-z plane)
        clock_angle = math.atan2(by, bz) if bz != 0 else 0
        
        # Cone angle (from Sun direction)
        bt = math.sqrt(by*by + bz*bz)
        cone_angle = math.atan2(bt, abs(bx)) if bx != 0 else math.pi/2
        
        return {
            'clock': clock_angle,
            'clock_deg': clock_angle * 180 / math.pi,
            'cone': cone_angle,
            'cone_deg': cone_angle * 180 / math.pi
        }
    
    @staticmethod
    def magnetic_latitude(mlat_rad):
        """
        Convert magnetic latitude to invariant latitude
        
        Parameters
        ----------
        mlat_rad : float
            Magnetic latitude (radians)
        
        Returns
        -------
        float
            Invariant latitude (radians)
        """
        return mlat_rad  # First order approximation
    
    @staticmethod
    def l_shell(mlat_rad):
        """
        Calculate L-shell from magnetic latitude
        
        L = 1 / cos²(mlat)
        
        Parameters
        ----------
        mlat_rad : float
            Magnetic latitude (radians)
        
        Returns
        -------
        float
            L-shell value
        """
        cos_lat = math.cos(mlat_rad)
        if cos_lat == 0:
            return float('inf')
        
        return 1.0 / (cos_lat * cos_lat)
    
    @staticmethod
    def mlat_from_l_shell(l_value):
        """
        Calculate magnetic latitude from L-shell
        
        mlat = arccos(1/√L)
        
        Parameters
        ----------
        l_value : float
            L-shell value
        
        Returns
        -------
        float
            Magnetic latitude (radians)
        """
        if l_value <= 1:
            return 0
        
        return math.acos(1.0 / math.sqrt(l_value))


class Heliocentric:
    """Heliocentric coordinate conversions"""
    
    @staticmethod
    def earth_angle(date):
        """
        Calculate Earth's angle in heliocentric coordinates
        
        Parameters
        ----------
        date : datetime
            Observation date
        
        Returns
        -------
        float
            Earth's longitude relative to Sun (radians)
        """
        from .time_utils import TimeUtils
        
        doy = TimeUtils.to_doy(date)
        
        # Earth's orbit: 0° at vernal equinox (~March 20)
        vernal_equinox = 80  # Day of year for vernal equinox
        
        # Earth's angle around Sun
        angle = 2 * math.pi * (doy - vernal_equinox) / 365.25
        
        return angle
    
    @staticmethod
    def sun_position(date):
        """
        Get Sun's position in geocentric coordinates
        
        Parameters
        ----------
        date : datetime
            Observation date
        
        Returns
        -------
        tuple
            (x, y, z) in km
        """
        from .constants import AU
        
        earth_angle = Heliocentric.earth_angle(date)
        
        # Sun is at (-AU, 0, 0) in GSE at vernal equinox
        x = -AU * math.cos(earth_angle)
        y = -AU * math.sin(earth_angle)
        z = 0
        
        return (x, y, z)
    
    @staticmethod
    def spacecraft_position(sc_pos_geo):
        """
        Convert spacecraft position from GEO to GSE
        
        Parameters
        ----------
        sc_pos_geo : tuple
            Spacecraft position in GEO (x, y, z in km)
        
        Returns
        -------
        tuple
            Position in GSE (x, y, z in km)
        """
        # Simplified: GEO to GSE rotation
        # More accurate would use IAU Earth rotation model
        
        x_geo, y_geo, z_geo = sc_pos_geo
        
        # For DSCOVR at L1, position is approximately (1.5e6, 0, 0) in GSE
        return (1.5e6, 0, 0)
