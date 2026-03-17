"""
Unit tests for Magnetopause module
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from heliosica.physics.magnetopause import MagnetopauseTracker, MagnetopauseResult


class TestMagnetopauseTracker(unittest.TestCase):
    """Test cases for MagnetopauseTracker class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker = MagnetopauseTracker()
        
        # Test pressures (nPa)
        self.p_ram_normal = 2.1  # Typical
        self.p_ram_g4 = 20.0  # G4 threshold
        self.p_ram_g5 = 35.0  # G5 extreme
        
        # Expected results - with realistic values
        self.r_mp_normal = 10.0  # R_E (reduced from 10.5)
        self.alert_threshold = 7.0
    
    def test_compute_standoff(self):
        """Test standoff distance calculation"""
        # Normal conditions
        r_mp = self.tracker.compute_standoff(self.p_ram_normal)
        self.assertGreater(r_mp, 7)
        self.assertLess(r_mp, 12)
        
        # G4 conditions
        r_mp = self.tracker.compute_standoff(self.p_ram_g4)
        self.assertLess(r_mp, 8)
        
        # G5 conditions
        r_mp = self.tracker.compute_standoff(self.p_ram_g5)
        self.assertLess(r_mp, 7)
        
        # Higher pressure = smaller magnetosphere
        r1 = self.tracker.compute_standoff(1)
        r2 = self.tracker.compute_standoff(10)
        r3 = self.tracker.compute_standoff(100)
        
        self.assertGreater(r1, r2)
        self.assertGreater(r2, r3)
    
    def test_satellite_alert(self):
        """Test satellite alert logic"""
        # Normal - no alert
        alert = self.tracker.check_satellite_alert(10.0)
        self.assertFalse(alert)
        
        # At threshold
        alert = self.tracker.check_satellite_alert(7.0)
        self.assertFalse(alert)  # Equal to threshold, not less
        
        # Below threshold - alert
        alert = self.tracker.check_satellite_alert(6.9)
        self.assertTrue(alert)
        
        # Extreme compression - alert
        alert = self.tracker.check_satellite_alert(5.0)
        self.assertTrue(alert)
    
    def test_compression_ratio(self):
        """Test compression ratio calculation"""
        # Normal
        ratio = self.tracker.get_compression_ratio(10.0)
        self.assertAlmostEqual(ratio, 0.95, delta=0.1)
        
        # Compressed
        ratio = self.tracker.get_compression_ratio(7.0)
        self.assertAlmostEqual(ratio, 0.67, delta=0.1)
    
    def test_update(self):
        """Test update method"""
        # Normal update
        result = self.tracker.update(self.p_ram_normal)
        
        self.assertIsInstance(result, MagnetopauseResult)
        self.assertFalse(result.satellite_alert)
        self.assertIsInstance(result.timestamp, datetime)
        
        # G4 update
        result = self.tracker.update(self.p_ram_g4)
        
        # Check history
        self.assertEqual(len(self.tracker.history), 2)
    
    def test_history(self):
        """Test history tracking"""
        # Add some data points
        for p in [2, 5, 10, 15, 20]:
            self.tracker.update(p)
        
        # Check history size
        self.assertEqual(len(self.tracker.history), 5)
        
        # Test history size limit
        tracker = MagnetopauseTracker(history_size=3)
        for p in [1, 2, 3, 4, 5]:
            tracker.update(p)
        
        self.assertEqual(len(tracker.history), 3)
    
    def test_summary(self):
        """Test summary method"""
        # Empty tracker
        summary = self.tracker.summary()
        self.assertEqual(summary.get('status'), 'no_data')
        
        # Add some data
        self.tracker.update(2.0)
        self.tracker.update(10.0)
        self.tracker.update(30.0)
        
        summary = self.tracker.summary()
        self.assertIn('current_r_mp', summary)
        self.assertIn('current_alert', summary)
        self.assertIn('compression_ratio', summary)
        self.assertEqual(summary['history_size'], 3)
    
    def test_forecast(self):
        """Test forecast generation"""
        p_ram_forecast = [2.0, 5.0, 10.0, 20.0, 30.0]
        timestamps = [datetime.utcnow() + timedelta(hours=i) for i in range(5)]
        
        forecast = self.tracker.get_forecast(p_ram_forecast, timestamps)
        
        self.assertEqual(len(forecast), 5)
        
        for i, result in enumerate(forecast):
            self.assertIsInstance(result, MagnetopauseResult)
            self.assertEqual(result.timestamp, timestamps[i])
            
            # Higher pressure = smaller R_MP
            if i > 0:
                self.assertLessEqual(result.r_mp_re, forecast[i-1].r_mp_re)


if __name__ == '__main__':
    unittest.main()
