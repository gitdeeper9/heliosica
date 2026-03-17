"""
HELIOSICA CLI - Monitor Command
Real-time monitoring of space weather conditions
"""

import argparse
import time
from datetime import datetime
import sys

from heliosica.data.loaders.dscovr import DSCOVRLoader
from heliosica.physics.reconnection import ReconnectionElectricField
from heliosica.physics.kp_predictor import KpPredictor
from heliosica.physics.gssi import GeomagneticStormSeverityIndex
from heliosica.physics.magnetopause import MagnetopauseTracker


def add_arguments(parser: argparse.ArgumentParser):
    """Add monitor command arguments"""
    parser.add_argument(
        '--realtime',
        action='store_true',
        help='Monitor real-time DSCOVR data'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Update interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--alerts',
        action='store_true',
        help='Show alerts when thresholds exceeded'
    )


def run(args):
    """Execute monitor command"""
    
    if not args.realtime:
        print("Error: --realtime required")
        sys.exit(1)
    
    # Initialize components
    dscovr = DSCOVRLoader()
    reconnection = ReconnectionElectricField()
    kp_pred = KpPredictor()
    gssi = GeomagneticStormSeverityIndex()
    mp_tracker = MagnetopauseTracker()
    
    print("\n" + "="*70)
    print("HELIOSICA REAL-TIME MONITOR")
    print("="*70)
    print(f"Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Update interval: {args.interval} seconds")
    print("-"*70)
    
    def display_conditions(data):
        """Display current conditions"""
        # Clear screen (simple approach)
        print("\033c", end='')
        
        # Reconnection
        ey_result = reconnection.evaluate(data.vsw, data.bz)
        
        # Kp prediction
        mp = 1.67e-27
        p_ram = mp * data.np * 1e6 * (data.vsw * 1000)**2 * 1e9
        theta = 180 if data.bz < 0 else 0
        kp_result = kp_pred.predict(ey_result.ey, p_ram, data.vsw, theta)
        
        # GSSI
        params = {
            'Ey': ey_result.ey,
            'Bz': data.bz,
            'P_ram': p_ram,
            'V0': 0,  # Not applicable
            'gamma': 0,
            'omega': 0,
            'Tp': data.tp,
            'Fd': 0,
            'Kp': kp_result.kp_value
        }
        gssi_result = gssi.compute(params)
        
        # Magnetopause
        mp_result = mp_tracker.update(p_ram)
        
        # Display
        print("\n" + "="*70)
        print(f"HELIOSICA REAL-TIME MONITOR - {data.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("="*70)
        
        # Solar wind
        print(f"\n📡 Solar Wind at L1:")
        print(f"   Bz: {data.bz:>6.1f} nT")
        print(f"   Vsw: {data.vsw:>6.0f} km/s")
        print(f"   np: {data.np:>6.1f} cm⁻³")
        print(f"   Tp: {data.tp:>6.1e} K")
        
        # Reconnection
        print(f"\n⚡ Reconnection:")
        print(f"   Ey: {ey_result.ey:>6.1f} mV/m ({ey_result.energy_injection})")
        
        # Storm indices
        print(f"\n🌪️ Storm Indices:")
        print(f"   Kp: {kp_result.kp_value:>6.1f} ({kp_result.g_category})")
        print(f"   GSSI: {gssi_result.gssi:>6.3f} ({gssi_result.category})")
        
        # Magnetosphere
        print(f"\n🛡️ Magnetosphere:")
        print(f"   R_MP: {mp_result.r_mp_re:>6.2f} R_E")
        if mp_result.satellite_alert:
            print(f"   ⚠️ SATELLITE ALERT: R_MP < 7.0 R_E")
        
        # Alerts
        if args.alerts:
            print(f"\n🚨 Alerts:")
            
            if ey_result.threshold_exceeded:
                print(f"   🔴 G5 Ey threshold exceeded!")
            
            if gssi_result.category in ['G4', 'G5']:
                print(f"   🟠 {gssi_result.category} storm in progress")
            
            if mp_result.satellite_alert:
                print(f"   🟡 Satellites at risk!")
        
        print("\n" + "-"*70)
        print(f"Press Ctrl+C to stop")
    
    # Start streaming
    try:
        dscovr.stream(
            interval_seconds=args.interval,
            callback=display_conditions
        )
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped")
        sys.exit(0)
