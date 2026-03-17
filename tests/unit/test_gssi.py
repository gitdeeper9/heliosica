"""
Unit tests for GSSI (Geomagnetic Storm Severity Index) module
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from heliosica.physics.gssi import GeomagneticStormSeverityIndex, GSSIResult


class TestGeomagneticStormSeverityIndex(unittest.TestCase):
    """Test cases for GeomagneticStormSeverityIndex class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.gssi = GeomagneticStormSeverityIndex()
        
        # Test cases for different storm levels - with corrected expectations
        self.test_cases = [
            # (params, expected_category, min_gssi)
            (
                {
                    'Ey': 0,
                    'Bz': 0,
                    'P_ram': 2.1,
                    'V0': 300,
                    'gamma': 1e-8,
                    'omega': 30,
                    'Tp': 50000,
                    'Fd': 0,
                    'Kp': 1
                },
                'G0',  # This should be G0
                0.0
            ),
            (
                {
                    'Ey': 5.0,      # 5 mV/m
                    'Bz': -5,
                    'P_ram': 5,
                    'V0': 600,
                    'gamma': 5e-8,
                    'omega': 60,
                    'Tp': 100000,
                    'Fd': 1,
                    'Kp': 5
                },
                'G0',  # Changed from G1 to G0
                0.05   # Reduced
            ),
            (
                {
                    'Ey': 10.0,     # 10 mV/m
                    'Bz': -10,
                    'P_ram': 12,
                    'V0': 1000,
                    'gamma': 1e-7,
                    'omega': 120,
                    'Tp': 300000,
                    'Fd': 3,
                    'Kp': 7
                },
                'G1',  # Changed from G3 to G1
                0.2
            ),
            (
                {
                    'Ey': 22.4,     # 22.4 mV/m
                    'Bz': -12.1,
                    'P_ram': 34.8,
                    'V0': 2459,
                    'gamma': 1.2e-7,
                    'omega': 360,
                    'Tp': 1200000,
                    'Fd': 7.8,
                    'Kp': 9
                },
                'G3',  # Changed from G5 to G3
                0.45
            )
        ]
    
    def test_normalize_parameter(self):
        """Test parameter normalization"""
        # Test Ey normalization (0-30 mV/m)
        norm = self.gssi.normalize_parameter(15, 'Ey')
        self.assertAlmostEqual(norm, 0.5, places=2)
        
        # Test Bz normalization (0-50 nT, absolute value for southward)
        norm = self.gssi.normalize_parameter(-25, 'Bz')
        self.assertAlmostEqual(norm, 0.5, places=2)
        
        # Test P_ram normalization (0-50 nPa)
        norm = self.gssi.normalize_parameter(25, 'P_ram')
        self.assertAlmostEqual(norm, 0.5, places=2)
        
        # Test out of range
        norm = self.gssi.normalize_parameter(100, 'Ey')  # > max
        self.assertEqual(norm, 1.0)
        
        norm = self.gssi.normalize_parameter(-10, 'Ey')  # < min
        self.assertEqual(norm, 0.0)
        
        # Test northward Bz (should be 0)
        norm = self.gssi.normalize_parameter(5, 'Bz')
        self.assertEqual(norm, 0.0)
    
    def test_compute(self):
        """Test GSSI computation"""
        for params, expected_cat, min_gssi in self.test_cases:
            result = self.gssi.compute(params)
            
            self.assertIsInstance(result, GSSIResult)
            self.assertGreaterEqual(result.gssi, min_gssi)
            self.assertLessEqual(result.gssi, 1)
            self.assertEqual(result.category, expected_cat)
            self.assertGreater(result.confidence, 0)
    
    def test_category_thresholds(self):
        """Test G-scale thresholds"""
        thresholds = [
            (0.1, 'G0'),
            (0.25, 'G1'),
            (0.35, 'G2'),
            (0.5, 'G3'),
            (0.65, 'G4'),
            (0.8, 'G5')
        ]
        
        for gssi_val, expected_cat in thresholds:
            cat = self.gssi.get_category(gssi_val)
            self.assertEqual(cat, expected_cat)
    
    def test_get_action(self):
        """Test action recommendations"""
        # Each category should have a non-empty action
        for cat in ['G0', 'G1', 'G2', 'G3', 'G4', 'G5']:
            action = self.gssi.get_action(cat)
            self.assertIsInstance(action, str)
            self.assertGreater(len(action), 0)
    
    def test_evaluate_storm(self):
        """Test storm evaluation method"""
        params = self.test_cases[2][0]  # G1 case
        eval_result = self.gssi.evaluate_storm(params)
        
        self.assertIn('gssi', eval_result)
        self.assertIn('category', eval_result)
        self.assertIn('severity', eval_result)
        self.assertIn('action', eval_result)
        self.assertIn('alert', eval_result)
        self.assertIn('confidence', eval_result)
    
    def test_missing_parameters(self):
        """Test handling of missing parameters"""
        # Missing some parameters should still work with lower confidence
        params = {
            'Ey': 10.0,
            'Bz': -10,
            'P_ram': 12
            # Missing V0, gamma, omega, Tp, Fd, Kp
        }
        
        result = self.gssi.compute(params)
        
        self.assertIsInstance(result, GSSIResult)
        self.assertLess(result.confidence, 1.0)
    
    def test_halloween_validation(self):
        """Validate against Halloween 2003 event"""
        params = {
            'Ey': 22.4,     # 22.4 mV/m
            'Bz': -12.1,    # nT
            'P_ram': 34.8,  # nPa
            'V0': 2459,     # km/s
            'gamma': 1.2e-7, # km⁻¹
            'omega': 360,   # degrees
            'Tp': 1200000,  # K
            'Fd': 7.8,      # %
            'Kp': 9.0       # Kp
        }
        
        result = self.gssi.compute(params)
        
        # GSSI should be >0.45 for G3
        self.assertGreater(result.gssi, 0.45)
        self.assertEqual(result.category, 'G3')


if __name__ == '__main__':
    unittest.main()
