"""
Forbush Decrease Monitor
HELIOSICA - Heliospheric Event and L1 Integrated Observatory
Pure Python - no numpy
"""

import math
from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ForbushEvent:
    """Detected Forbush decrease event"""
    onset_time: datetime        # Start time of decrease
    minimum_time: datetime      # Time of minimum flux
    recovery_time: datetime     # Recovery time
    fd_percent: float           # Forbush decrease amplitude (%)
    b_cloud: float              # Estimated magnetic cloud field (nT)
    magnitude: str              # 'weak', 'moderate', 'strong', 'extreme'
    cloud_confirmed: bool       # True if Fd > 3%


class ForbushMonitor:
    """
    Forbush decrease detection and magnetic cloud characterization
    
    Monitors neutron monitor count rates to detect cosmic ray suppression
    from CME magnetic clouds. Provides independent confirmation of cloud passage.
    """
    
    # Constants
    B_CLOUD_SLOPE = 0.48  # Fd to B_cloud conversion slope (%/nT)
    B_CLOUD_INTERCEPT = 1.2  # Fd to B_cloud conversion intercept (%)
    
    # Detection thresholds
    FD_WEAK = 1.0    # Weak decrease (%)
    FD_MODERATE = 3.0  # Moderate decrease (cloud confirmed)
    FD_STRONG = 5.0  # Strong decrease
    FD_EXTREME = 7.0  # Extreme decrease
    
    # CUSUM parameters
    CUSUM_THRESHOLD = 3.0  # Detection threshold (sigma)
    CUSUM_DRIFT = 0.5      # Allowed drift (sigma)
    
    def __init__(self, window_hours: int = 48, sampling_minutes: int = 1):
        """
        Initialize Forbush monitor
        
        Parameters
        ----------
        window_hours : int
            Analysis window length (hours)
        sampling_minutes : int
            Data sampling interval (minutes)
        """
        self.window_hours = window_hours
        self.sampling_minutes = sampling_minutes
        self.samples_per_window = window_hours * 60 // sampling_minutes
        
        # Background estimation
        self.background = None
        self.background_std = None
        self.background_array = None
        
        # Event history
        self.events = []
    
    def estimate_background(self, counts: list, 
                            timestamps: List[datetime]) -> Tuple[float, float]:
        """
        Estimate background count rate from quiet periods
        
        Parameters
        ----------
        counts : list
            Neutron monitor count rates
        timestamps : List[datetime]
            Corresponding timestamps
        
        Returns
        -------
        Tuple[float, float]
            (background_mean, background_std)
        """
        if len(counts) < 10:
            return (0.0, 0.0)
        
        # Calculate mean and standard deviation
        mean_val = sum(counts) / len(counts)
        
        # Calculate variance
        variance = sum((x - mean_val) ** 2 for x in counts) / (len(counts) - 1)
        std_val = math.sqrt(variance) if variance > 0 else 0
        
        # Remove outliers (values > 3 sigma from mean)
        clean_counts = []
        for x in counts:
            if abs(x - mean_val) <= 3 * std_val:
                clean_counts.append(x)
        
        if len(clean_counts) < 5:
            clean_counts = counts
        
        # Recalculate with clean data
        self.background = sum(clean_counts) / len(clean_counts)
        variance = sum((x - self.background) ** 2 for x in clean_counts) / (len(clean_counts) - 1)
        self.background_std = math.sqrt(variance) if variance > 0 else 0
        self.background_array = [self.background] * len(counts)
        
        return (self.background, self.background_std)
    
    def cusum_detection(self, counts: list) -> Tuple[list, list]:
        """
        CUSUM change point detection algorithm
        
        Parameters
        ----------
        counts : list
            Count rates
        
        Returns
        -------
        Tuple[list, list]
            (cusum_upper, cusum_lower)
        """
        if self.background is None:
            raise ValueError("Background must be estimated first")
        
        # Calculate residuals
        residuals = [x - self.background for x in counts]
        
        # Normalize by standard deviation
        if self.background_std and self.background_std > 0:
            residuals = [x / self.background_std for x in residuals]
        else:
            residuals = [0] * len(residuals)
        
        # CUSUM statistics
        n = len(residuals)
        cusum_pos = [0] * n
        cusum_neg = [0] * n
        
        for i in range(1, n):
            cusum_pos[i] = max(0, cusum_pos[i-1] + residuals[i] - self.CUSUM_DRIFT)
            cusum_neg[i] = max(0, cusum_neg[i-1] - residuals[i] - self.CUSUM_DRIFT)
        
        return cusum_pos, cusum_neg
    
    def find_forbush_events(self, counts: list, 
                            timestamps: List[datetime]) -> List[ForbushEvent]:
        """
        Detect Forbush decrease events in time series
        
        Parameters
        ----------
        counts : list
            Neutron monitor count rates
        timestamps : List[datetime]
            Corresponding timestamps
        
        Returns
        -------
        List[ForbushEvent]
            Detected Forbush events
        """
        if len(counts) < 10:
            return []
        
        # Estimate background
        self.estimate_background(counts, timestamps)
        
        # Normalize counts
        if self.background and self.background > 0:
            normalized = [x / self.background for x in counts]
        else:
            normalized = [1.0] * len(counts)
        
        # Run CUSUM detection
        cusum_pos, cusum_neg = self.cusum_detection(normalized)
        
        # Find change points
        changes = []
        for i, val in enumerate(cusum_neg):
            if val > self.CUSUM_THRESHOLD:
                changes.append(i)
        
        if len(changes) == 0:
            return []
        
        # Cluster change points
        clusters = []
        current_cluster = [changes[0]]
        
        for i in range(1, len(changes)):
            if changes[i] - changes[i-1] <= self.samples_per_window // 24:
                current_cluster.append(changes[i])
            else:
                clusters.append(current_cluster)
                current_cluster = [changes[i]]
        
        if current_cluster:
            clusters.append(current_cluster)
        
        # Analyze each cluster
        events = []
        for cluster in clusters:
            onset_idx = cluster[0]
            
            # Find minimum within 24 hours after onset
            search_end = min(onset_idx + 24 * 60 // self.sampling_minutes, len(counts))
            min_idx = onset_idx
            min_val = normalized[onset_idx]
            
            for i in range(onset_idx, search_end):
                if normalized[i] < min_val:
                    min_val = normalized[i]
                    min_idx = i
            
            # Find recovery (return to background)
            recovery_idx = min_idx
            for i in range(min_idx, len(normalized)):
                if abs(normalized[i] - 1.0) < 0.01:
                    recovery_idx = i
                    break
            
            # Compute Fd
            j0 = self.background if self.background else 1
            jmin = counts[min_idx] if min_idx < len(counts) else j0
            fd = (j0 - jmin) / j0 * 100 if j0 > 0 else 0
            
            # Estimate B_cloud
            b_cloud = (fd - self.B_CLOUD_INTERCEPT) / self.B_CLOUD_SLOPE if fd > self.FD_WEAK else 0
            
            # Determine magnitude
            if fd >= self.FD_EXTREME:
                magnitude = "extreme"
            elif fd >= self.FD_STRONG:
                magnitude = "strong"
            elif fd >= self.FD_MODERATE:
                magnitude = "moderate"
            elif fd >= self.FD_WEAK:
                magnitude = "weak"
            else:
                magnitude = "none"
            
            # Cloud confirmed?
            cloud_confirmed = fd >= self.FD_MODERATE
            
            if fd >= self.FD_WEAK:
                event = ForbushEvent(
                    onset_time=timestamps[onset_idx],
                    minimum_time=timestamps[min_idx],
                    recovery_time=timestamps[recovery_idx],
                    fd_percent=fd,
                    b_cloud=b_cloud,
                    magnitude=magnitude,
                    cloud_confirmed=cloud_confirmed
                )
                
                events.append(event)
                self.events.append(event)
        
        return events
    
    def estimate_b_cloud(self, fd: float) -> float:
        """
        Estimate magnetic cloud field strength from Fd
        
        B_cloud = (Fd - 1.2) / 0.48
        
        Parameters
        ----------
        fd : float
            Forbush decrease amplitude (%)
        
        Returns
        -------
        float
            Estimated cloud magnetic field (nT)
        """
        if fd < self.FD_WEAK:
            return 0.0
        
        return (fd - self.B_CLOUD_INTERCEPT) / self.B_CLOUD_SLOPE
    
    def get_lead_time_extension(self, event: ForbushEvent, 
                                 bz_southward_time: datetime) -> float:
        """
        Compute lead time extension from Forbush detection
        
        Parameters
        ----------
        event : ForbushEvent
            Detected Forbush event
        bz_southward_time : datetime
            Time when Bz turned southward
        
        Returns
        -------
        float
            Lead time extension (hours)
        """
        if not event.cloud_confirmed:
            return 0.0
        
        # Forbush onset is typically 2-4 hours before Bz southward
        delta = (bz_southward_time - event.onset_time).total_seconds() / 3600
        
        return max(0, delta)
    
    def summary(self) -> dict:
        """
        Get summary of detected events
        
        Returns
        -------
        dict
            Summary statistics
        """
        if not self.events:
            return {"status": "no_events"}
        
        fd_values = [e.fd_percent for e in self.events]
        b_cloud_values = [e.b_cloud for e in self.events]
        
        # Calculate mean
        mean_fd = sum(fd_values) / len(fd_values) if fd_values else 0
        mean_b_cloud = sum(b_cloud_values) / len(b_cloud_values) if b_cloud_values else 0
        
        # Count magnitudes
        magnitudes = {'weak': 0, 'moderate': 0, 'strong': 0, 'extreme': 0}
        for e in self.events:
            if e.magnitude in magnitudes:
                magnitudes[e.magnitude] += 1
        
        return {
            "total_events": len(self.events),
            "mean_fd": mean_fd,
            "max_fd": max(fd_values) if fd_values else 0,
            "mean_b_cloud": mean_b_cloud,
            "max_b_cloud": max(b_cloud_values) if b_cloud_values else 0,
            "cloud_confirmed": sum(1 for e in self.events if e.cloud_confirmed),
            "magnitudes": magnitudes
        }


# Generate sample data for testing
def generate_sample_data():
    """Generate synthetic neutron monitor data for testing"""
    import random
    
    # 7 days of 1-minute data
    n_minutes = 7 * 24 * 60
    timestamps = [datetime(2024, 1, 1) + timedelta(minutes=i) 
                  for i in range(n_minutes)]
    
    # Background with slow variation
    counts = []
    for i in range(n_minutes):
        # Base count with Poisson-like variation
        base = 5000 + 200 * math.sin(i / 1440)  # Daily variation
        noise = random.gauss(0, math.sqrt(base))
        counts.append(int(base + noise))
    
    # Add Forbush event at day 3
    event_start = 3 * 24 * 60
    event_duration = 2 * 24 * 60  # 2 days
    
    # Forbush profile
    for i in range(event_duration):
        idx = event_start + i
        if idx >= n_minutes:
            break
        
        # Exponential decrease and recovery
        if i < 12 * 60:  # First 12 hours: decrease
            factor = 1.0 - 0.15 * (i / (12*60))
        else:  # Recovery
            factor = 0.85 + 0.15 * ((i - 12*60) / (event_duration - 12*60))
        
        counts[idx] = int(counts[idx] * factor)
    
    return counts, timestamps


# Test with sample data
def test_forbush_monitor():
    """Test Forbush monitor with synthetic data"""
    monitor = ForbushMonitor()
    
    # Generate test data
    counts, timestamps = generate_sample_data()
    
    # Detect events
    events = monitor.find_forbush_events(counts, timestamps)
    
    print("Forbush Monitor Test:")
    print(f"Detected {len(events)} events")
    
    for i, event in enumerate(events):
        print(f"\nEvent {i+1}:")
        print(f"  Onset: {event.onset_time}")
        print(f"  Fd: {event.fd_percent:.2f}%")
        print(f"  B_cloud: {event.b_cloud:.1f} nT")
        print(f"  Magnitude: {event.magnitude}")
        print(f"  Cloud confirmed: {event.cloud_confirmed}")
    
    print("\nSummary:")
    print(monitor.summary())
    
    return events


if __name__ == "__main__":
    test_forbush_monitor()
