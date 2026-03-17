"""
HELIOSICA CLI - Forecast Command
CME transit and storm severity forecasting
"""

import argparse
import sys
from datetime import datetime
import json

from heliosica.physics.dbm import DBMSolver
from heliosica.physics.kp_predictor import KpPredictor
from heliosica.physics.gssi import GeomagneticStormSeverityIndex
from heliosica.physics.magnetopause import MagnetopauseTracker
from heliosica.data.loaders.soho import SOHOLoader


def add_arguments(parser: argparse.ArgumentParser):
    """Add forecast command arguments"""
    parser.add_argument(
        '--cme',
        type=str,
        help='CME date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--v0',
        type=float,
        help='CME launch velocity (km/s)'
    )
    parser.add_argument(
        '--omega',
        type=float,
        help='CME angular width (degrees)'
    )
    parser.add_argument(
        '--vsw',
        type=float,
        default=450,
        help='Solar wind velocity (km/s, default: 450)'
    )
    parser.add_argument(
        '--np',
        type=float,
        default=5,
        help='Proton density (cm⁻³, default: 5)'
    )
    parser.add_argument(
        '--bz',
        type=float,
        help='IMF Bz (nT)'
    )
    parser.add_argument(
        '--probabilistic',
        action='store_true',
        help='Run probabilistic forecast with ensembles'
    )
    parser.add_argument(
        '--output',
        type=str,
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )


def run(args):
    """Execute forecast command"""
    
    # Get CME parameters
    v0 = args.v0
    omega = args.omega
    
    # If date provided, try to get from SOHO catalogue
    if args.cme and not (v0 and omega):
        try:
            date = datetime.strptime(args.cme, '%Y-%m-%d')
            soho = SOHOLoader()
            cme = soho.get_cme(date)
            
            if cme:
                v0 = cme.velocity
                omega = cme.width
                print(f"Found CME on {date.date()}: V0={v0:.0f} km/s, ω={omega:.0f}°")
            else:
                print(f"No CME found for {args.cme}")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error loading CME data: {e}")
            sys.exit(1)
    
    # Validate required parameters
    if not v0 or not omega:
        print("Error: V0 and omega required")
        print("Provide with --v0 and --omega or use --cme to lookup")
        sys.exit(1)
    
    # Initialize solvers
    dbm = DBMSolver()
    kp_pred = KpPredictor()
    gssi = GeomagneticStormSeverityIndex()
    mp_tracker = MagnetopauseTracker()
    
    # DBM forecast
    if args.probabilistic:
        result = dbm.ensemble_forecast(v0, args.vsw, omega, args.np)
    else:
        result = dbm.predict(v0, args.vsw, omega, args.np, probabilistic=False)
    
    # If Bz provided, compute Kp and GSSI
    if args.bz:
        # Compute Ey
        ey = args.vsw * abs(args.bz) if args.bz < 0 else 0
        
        # Ram pressure
        mp = 1.67e-27  # proton mass (kg)
        p_ram = mp * args.np * 1e6 * (args.vsw * 1000)**2 * 1e9  # nPa
        
        # Kp prediction
        kp_result = kp_pred.predict(ey, p_ram, args.vsw, 180 if args.bz < 0 else 0)
        
        # GSSI
        params = {
            'Ey': ey,
            'Bz': args.bz,
            'P_ram': p_ram,
            'V0': v0,
            'gamma': result.gamma,
            'omega': omega,
            'Tp': 1e5,  # Default
            'Fd': 0,    # No Forbush
            'Kp': kp_result.kp_value
        }
        gssi_result = gssi.compute(params)
        
        # Magnetopause
        mp_result = mp_tracker.update(p_ram)
    
    # Output
    if args.output == 'json':
        output_json(args, result, locals())
    else:
        output_text(args, result, locals())


def output_text(args, dbm_result, namespace):
    """Text output format"""
    print("\n" + "="*60)
    print("HELIOSICA FORECAST")
    print("="*60)
    
    # CME parameters
    print(f"\nCME Parameters:")
    print(f"  V0: {args.v0:.0f} km/s")
    print(f"  ω: {args.omega:.0f}°")
    print(f"  Vsw: {args.vsw:.0f} km/s")
    print(f"  np: {args.np:.1f} cm⁻³")
    
    # DBM results
    print(f"\nDBM Transit Forecast:")
    print(f"  Gamma: {dbm_result.gamma:.2e} km⁻¹")
    print(f"  Arrival time: {dbm_result.arrival_time_50:.1f} hours")
    
    if args.probabilistic:
        print(f"  Uncertainty (90%): {dbm_result.arrival_time_5:.1f}-{dbm_result.arrival_time_95:.1f} hours")
    
    print(f"  V at 1 AU: {dbm_result.v_at_1au:.0f} km/s")
    
    # Storm forecast
    if args.bz:
        kp_result = namespace.get('kp_result')
        gssi_result = namespace.get('gssi_result')
        mp_result = namespace.get('mp_result')
        
        print(f"\nStorm Forecast:")
        print(f"  Bz: {args.bz:.1f} nT")
        print(f"  Ey: {args.vsw * abs(args.bz):.1f} mV/m")
        print(f"  Kp: {kp_result.kp_value:.1f} ({kp_result.g_category})")
        print(f"  GSSI: {gssi_result.gssi:.3f} ({gssi_result.category})")
        print(f"  R_MP: {mp_result.r_mp_re:.1f} R_E")
        
        if mp_result.satellite_alert:
            print(f"  ⚠️ SATELLITE ALERT: R_MP < 7.0 R_E")
        
        print(f"\nSeverity: {gssi_result.severity}")
        print(f"Confidence: {gssi_result.confidence:.1%}")
    
    print("\n" + "="*60)


def output_json(args, dbm_result, namespace):
    """JSON output format"""
    output = {
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'input': {
            'v0': args.v0,
            'omega': args.omega,
            'vsw': args.vsw,
            'np': args.np
        },
        'dbm': {
            'gamma': dbm_result.gamma,
            'arrival_time_50': dbm_result.arrival_time_50,
            'v_at_1au': dbm_result.v_at_1au
        }
    }
    
    if args.probabilistic:
        output['dbm']['arrival_time_5'] = dbm_result.arrival_time_5
        output['dbm']['arrival_time_95'] = dbm_result.arrival_time_95
    
    if args.bz:
        kp_result = namespace.get('kp_result')
        gssi_result = namespace.get('gssi_result')
        mp_result = namespace.get('mp_result')
        
        ey = args.vsw * abs(args.bz) if args.bz < 0 else 0
        
        output['storm'] = {
            'bz': args.bz,
            'ey': ey,
            'kp': kp_result.kp_value,
            'kp_category': kp_result.g_category,
            'gssi': gssi_result.gssi,
            'gssi_category': gssi_result.category,
            'r_mp': mp_result.r_mp_re,
            'satellite_alert': mp_result.satellite_alert,
            'severity': gssi_result.severity,
            'confidence': gssi_result.confidence
        }
    
    print(json.dumps(output, indent=2))
