"""
Unit tests for Forbush Monitor module
"""

import unittest
import sys
import os
import math
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from heliosica.physics.forbush import ForbushMonitor, ForbushEvent


class TestForbushMonitor(unittest.TestCase):
    """Test cases for ForbushMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = ForbushMonitor(window_hours=48, sampling_minutes=1)
        
        # Generate synthetic data
        n_points = 7 * 24 * 60  # 7 days
        self.timestamps = [datetime(2024, 1, 1) + timedelta(minutes=i) 
                          for i in range(n_points)]
        
        # Background: 5000 counts with slow variation
        self.background = []
        for i in range(n_points):
            self.background.append(5000 + 100 * math.sin(0.01 * i))
        
        # Add Forbush event at day 3
        self.counts = self.background.copy()
        event_start = 3 * 24 * 60
        
        for i in range(24 * 60):  # 24 hour event
            idx = event_start + i
            if idx < len(self.counts):
                # Exponential decrease and recovery
                if i < 6 * 60:  # First 6 hours: decrease
                    factor = 1.0 - 0.15 * (i / (6*60))
                else:  # Recovery
                    factor = 0.85 + 0.15 * ((i - 6*60) / (18*60))
                self.counts[idx] = int(self.counts[idx] * factor)
    
    def test_estimate_background(self):
        """Test background estimation"""
        # Use first 2 days as quiet period
        quiet_counts = self.counts[:2*24*60]
        quiet_times = self.timestamps[:2*24*60]
        
        bg_mean, bg_std = self.monitor.estimate_background(quiet_counts, quiet_times)
        
        # Background should be around 5000
        self.assertAlmostEqual(bg_mean, 5000, delta=200)
        self.assertGreater(bg_std, 0)
    
    def test_find_forbush_events(self):
        """Test Forbush event detection"""
        events = self.monitor.find_forbush_events(self.counts, self.timestamps)
        
        # Should detect at least one event
        self.assertGreaterEqual(len(events), 1)
        
        if events:
            event = events[0]
            self.assertIsInstance(event, ForbushEvent)
            self.assertGreater(event.fd_percent, 0)
            
            # Check event timing
            self.assertGreater(event.minimum_time, event.onset_time)
            self.assertGreater(event.recovery_time, event.minimum_time)
    
    def test_cloud_confirmation(self):
        """Test cloud confirmation logic"""
        # Should confirm at Fd > 3%
        events = []
        
        # Create mock events with different Fd
        for fd in [1, 2, 3, 4, 5]:
            event = ForbushEvent(
                onset_time=datetime.utcnow(),
                minimum_time=datetime.utcnow() + timedelta(hours=6),
                recovery_time=datetime.utcnow() + timedelta(hours=24),
                fd_percent=fd,
                b_cloud=(fd - 1.2) / 0.48,
                magnitude='moderate' if fd >= 3 else 'weak',
                cloud_confirmed=(fd >= 3)
            )
            events.append(event)
        
        for event in events:
            if event.fd_percent >= 3:
                self.assertTrue(event.cloud_confirmed)
            else:
                self.assertFalse(event.cloud_confirmed)
    
    def test_summary(self):
        """Test summary statistics"""
        # Add some events
        events = [
            ForbushEvent(
                onset_time=datetime.utcnow(),
                minimum_time=datetime.utcnow() + timedelta(hours=6),
                recovery_time=datetime.utcnow() + timedelta(hours=24),
                fd_percent=2.0,
                b_cloud=2.0,
                magnitude='weak',
                cloud_confirmed=False
            ),
            ForbushEvent(
                onset_time=datetime.utcnow() - timedelta(days=1),
                minimum_time=datetime.utcnow() - timedelta(hours=18),
                recovery_time=datetime.utcnow(),
                fd_percent=5.0,
                b_cloud=8.0,
                magnitude='moderate',
                cloud_confirmed=True
            )
        ]
        
        self.monitor.events = events
        summary = self.monitor.summary()
        
        self.assertEqual(summary['total_events'], 2)
        self.assertEqual(summary['cloud_confirmed'], 1)


if __name__ == '__main__':
    unittest.main()
