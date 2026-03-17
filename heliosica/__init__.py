"""HELIOSICA - Heliospheric Event and L1 Integrated Observatory for Solar Intelligence and Coronal Activity

A nine-parameter solar MHD framework for real-time prediction of geomagnetic storm
intensity, magnetopause standoff distance, and Kp index evolution.
"""

__version__ = "1.0.0"
__author__ = "Samir Baladi"
__email__ = "gitdeeper@gmail.com"
__doi__ = "10.5281/zenodo.19082026"

from heliosica.physics.dbm import DBMSolver
from heliosica.physics.magnetopause import MagnetopauseTracker
from heliosica.physics.reconnection import ReconnectionElectricField
from heliosica.physics.kp_predictor import KpPredictor
from heliosica.physics.forbush import ForbushMonitor
from heliosica.physics.gssi import GeomagneticStormSeverityIndex

__all__ = [
    'DBMSolver',
    'MagnetopauseTracker', 
    'ReconnectionElectricField',
    'KpPredictor',
    'ForbushMonitor',
    'GeomagneticStormSeverityIndex',
]
