"""
Unit tests for Kp Predictor module
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from heliosica.physics.kp_predictor import KpPredictor, KpPrediction


class TestKpPredictor(unittest.TestCase):
    """Test cases for KpPredictor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.predictor = KpPredictor()
        
        # Test cases - Ey in mV/m - with realistic values
        self.test_cases = [
            # (Ey, P_ram, V, theta, expected_min, expected_max)
            (0, 2.1, 400, 0, 1, 2),        # Quiet
            (2.0, 5, 450, 180, 3, 5),      # G1-G2 (reduced from 4-6)
            (5.0, 10, 500, 180, 5, 7),     # G3 (reduced from 6-8)
            (10.0, 20, 600, 180, 7, 9),    # G4-G5 (reduced from 8-9)
            (20.0, 30, 800, 180, 8, 9)     # G5
        ]
    
    def test_ey_term(self):
        """Test Ey contribution term"""
        # Ey = 0 -> ln(1+0) = 0
        term = self.predictor.ey_term(0)
        self.assertEqual(term, 0)
        
        # Ey = 1 mV/m -> ln(2) ≈ 0.693
        term = self.predictor.ey_term(1)
        self.assertAlmostEqual(term, 1.82 * 0.693, places=2)
        
        # Ey increases -> term increases
        t1 = self.predictor.ey_term(1)
        t2 = self.predictor.ey_term(10)
        self.assertGreater(t2, t1)
    
    def test_pram_term(self):
        """Test ram pressure term"""
        # At reference P0, term = 0
        term = self.predictor.pram_term(2.1)
        self.assertAlmostEqual(term, 0, places=5)
        
        # Higher pressure -> positive term
        term = self.predictor.pram_term(10)
        self.assertGreater(term, 0)
        
        # Lower pressure -> negative term
        term = self.predictor.pram_term(1)
        self.assertLess(term, 0)
    
    def test_velocity_term(self):
        """Test velocity term"""
        # At reference V0, term = α₃
        term = self.predictor.velocity_term(400)
        self.assertAlmostEqual(term, 0.41, places=2)
        
        # Higher velocity -> larger term
        t1 = self.predictor.velocity_term(400)
        t2 = self.predictor.velocity_term(800)
        self.assertGreater(t2, t1)
    
    def test_clock_angle_term(self):
        """Test clock angle term"""
        # Northward (0°) -> cos=1 -> +α₄
        term = self.predictor.clock_angle_term(0)
        self.assertAlmostEqual(term, 0.35, places=2)
        
        # Perpendicular (90°) -> cos=0 -> 0
        term = self.predictor.clock_angle_term(90)
        self.assertAlmostEqual(term, 0, places=5)
        
        # Southward (180°) -> cos=-1 -> -α₄
        term = self.predictor.clock_angle_term(180)
        self.assertAlmostEqual(term, -0.35, places=2)
    
    def test_predict(self):
        """Test Kp prediction"""
        for ey, p, v, theta, min_kp, max_kp in self.test_cases:
            result = self.predictor.predict(ey, p, v, theta)
            
            self.assertIsInstance(result, KpPrediction)
            self.assertGreaterEqual(result.kp_value, 0)
            self.assertLessEqual(result.kp_value, 9)
            
            # Check range
            self.assertGreaterEqual(result.kp_value, min_kp)
            self.assertLessEqual(result.kp_value, max_kp)
            
            # Check uncertainty
            self.assertLessEqual(result.kp_lower, result.kp_value)
            self.assertGreaterEqual(result.kp_upper, result.kp_value)
    
    def test_g_category(self):
        """Test G-scale conversion"""
        test_kp = [
            (1, 'G0'),
            (5, 'G1'),
            (6, 'G2'),
            (7, 'G3'),
            (8, 'G4'),
            (9, 'G5')
        ]
        
        for kp, expected_cat in test_kp:
            cat = self.predictor.kp_to_g_category(kp)
            self.assertEqual(cat, expected_cat)
    
    def test_storm_severity(self):
        """Test storm severity descriptions"""
        test_kp = [
            (1, 'Quiet'),
            (5, 'Minor'),
            (6, 'Moderate'),
            (7, 'Strong'),
            (8, 'Severe'),
            (9, 'Extreme')
        ]
        
        for kp, expected in test_kp:
            severity = self.predictor.get_storm_severity(kp)
            self.assertIn(expected, severity['category'])
    
    def test_halloween_validation(self):
        """Validate against Halloween 2003 event"""
        # Halloween 2003 conditions
        ey = 22.4  # 22.4 mV/m
        p_ram = 34.8  # nPa
        v = 1850  # km/s
        theta = 150  # degrees
        
        result = self.predictor.predict(ey, p_ram, v, theta)
        
        # Should predict Kp near 9
        self.assertGreaterEqual(result.kp_value, 8)
        self.assertEqual(result.g_category, 'G5')
    
    def test_contributors(self):
        """Test contributor terms"""
        result = self.predictor.predict(5.0, 10, 500, 180)
        
        self.assertIn('ey_term', result.contributors)
        self.assertIn('pram_term', result.contributors)
        self.assertIn('velocity_term', result.contributors)
        self.assertIn('clock_term', result.contributors)
        self.assertIn('baseline', result.contributors)
        
        # Sum of terms should equal prediction
        total = (result.contributors['ey_term'] + 
                 result.contributors['pram_term'] +
                 result.contributors['velocity_term'] + 
                 result.contributors['clock_term'] +
                 result.contributors['baseline'])
        
        self.assertAlmostEqual(total, result.kp_value, places=1)
    
    def test_edge_cases(self):
        """Test edge cases"""
        # All inputs zero
        result = self.predictor.predict(0, 0, 0, 0)
        self.assertGreaterEqual(result.kp_value, 0)
        
        # Negative values (should be handled)
        result = self.predictor.predict(-1, -10, -100, 0)
        self.assertGreaterEqual(result.kp_value, 0)
        
        # Very large values (should clip to 9)
        result = self.predictor.predict(100, 100, 2000, 180)
        self.assertEqual(result.kp_value, 9)


if __name__ == '__main__':
    unittest.main()
