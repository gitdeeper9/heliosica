"""
HELIOSICA CLI - Validate Command
Validate against historical storm events
"""

import argparse
from datetime import datetime
import sys
import json

from heliosica.physics.dbm import DBMSolver
from heliosica.physics.kp_predictor import KpPredictor
from heliosica.physics.gssi import GeomagneticStormSeverityIndex
from heliosica.data.loaders.omni import OMNILoader
from heliosica.data.loaders.soho import SOHOLoader


# Known validation events from the 312-event catalogue
VALIDATION_EVENTS = {
    '2003-10-29': {
        'name': 'Halloween 2003',
        'v0': 2459,
        'omega': 360,
        'vsw': 650,
        'np': 15,
        'bz': -12.1,
        'kp': 9.0,
        'dst': -383,
        'arrival': 19.5
    },
    '2015-03-17': {
        'name': "St. Patrick's Day 2015",
        'v0': 769,
        'omega': 120,
        'vsw': 620,
        'np': 8.5,
        'bz': -11.8,
        'kp': 8.0,
        'dst': -223,
        'arrival': 43.8
    },
    '2000-07-14': {
        'name': 'Bastille Day 2000',
        'v0': 1674,
        'omega': 360,
        'vsw': 580,
        'np': 12,
        'bz': -15.2,
        'kp': 9.0,
        'dst': -301,
        'arrival': 26.5
    },
    '2024-10-28': {
        'name': 'Halloween 2024',
        'v0': 1850,
        'omega': 300,
        'vsw': 600,
        'np': 10,
        'bz': -14.5,
        'kp': 8.0,
        'dst': -245,
        'arrival': 22.3
    }
}


def add_arguments(parser: argparse.ArgumentParser):
    """Add validate command arguments"""
    parser.add_argument(
        '--event',
        type=str,
        help='Event date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available validation events'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate against all events'
    )
    parser.add_argument(
        '--output',
        type=str,
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )


def run(args):
    """Execute validate command"""
    
    if args.list:
        list_events()
        return
    
    if args.all:
        validate_all(args)
    elif args.event:
        validate_event(args.event, args)
    else:
        print("Error: --event or --all required")
        sys.exit(1)


def list_events():
    """List available validation events"""
    print("\nHELIOSICA Validation Events")
    print("="*60)
    print(f"{'Date':<12} {'Event':<20} {'Kp':<4} {'V0':<8} {'Arrival':<8}")
    print("-"*60)
    
    for date, event in VALIDATION_EVENTS.items():
        print(f"{date:<12} {event['name']:<20} "
              f"{event['kp']:<4.0f} {event['v0']:<8.0f} "
              f"{event['arrival']:<8.1f}h")
    
    print("="*60)


def validate_event(date_str, args):
    """Validate against a single event"""
    
    if date_str not in VALIDATION_EVENTS:
        print(f"Error: Event {date_str} not found")
        print("Use --list to see available events")
        sys.exit(1)
    
    event = VALIDATION_EVENTS[date_str]
    
    print(f"\nValidating: {event['name']} ({date_str})")
    print("="*60)
    
    # Initialize solvers
    dbm = DBMSolver()
    kp_pred = KpPredictor()
    gssi = GeomagneticStormSeverityIndex()
    
    # DBM prediction
    dbm_result = dbm.predict(
        event['v0'],
        event['vsw'],
        event['omega'],
        event['np'],
        probabilistic=False
    )
    
    # Storm prediction
    ey = event['vsw'] * abs(event['bz'])
    mp = 1.67e-27
    p_ram = mp * event['np'] * 1e6 * (event['vsw'] * 1000)**2 * 1e9
    theta = 180 if event['bz'] < 0 else 0
    
    kp_result = kp_pred.predict(ey, p_ram, event['vsw'], theta)
    
    params = {
        'Ey': ey,
        'Bz': event['bz'],
        'P_ram': p_ram,
        'V0': event['v0'],
        'gamma': dbm_result.gamma,
        'omega': event['omega'],
        'Tp': 1e5,
        'Fd': 0,
        'Kp': kp_result.kp_value
    }
    gssi_result = gssi.compute(params)
    
    # Calculate errors
    arrival_error = abs(dbm_result.arrival_time_50 - event['arrival'])
    kp_error = abs(kp_result.kp_value - event['kp'])
    
    # Display results
    print(f"\nCME Transit:")
    print(f"  Predicted: {dbm_result.arrival_time_50:.1f} hours")
    print(f"  Actual:    {event['arrival']:.1f} hours")
    print(f"  Error:     {arrival_error:.1f} hours")
    print(f"  Gamma:     {dbm_result.gamma:.2e} km⁻¹")
    
    print(f"\nKp Index:")
    print(f"  Predicted: {kp_result.kp_value:.1f} ({kp_result.g_category})")
    print(f"  Actual:    {event['kp']:.0f}")
    print(f"  Error:     {kp_error:.1f}")
    
    print(f"\nGSSI:")
    print(f"  Value:     {gssi_result.gssi:.3f}")
    print(f"  Category:  {gssi_result.category}")
    
    # Success criteria
    print(f"\nValidation Results:")
    arrival_success = arrival_error <= 6.0
    kp_success = kp_error <= 1.0
    
    print(f"  Arrival (≤6h): {'✅ PASS' if arrival_success else '❌ FAIL'}")
    print(f"  Kp (≤1.0):     {'✅ PASS' if kp_success else '❌ FAIL'}")
    
    if args.output == 'json':
        output = {
            'event': event['name'],
            'date': date_str,
            'dbm': {
                'predicted': dbm_result.arrival_time_50,
                'actual': event['arrival'],
                'error': arrival_error,
                'gamma': dbm_result.gamma,
                'success': arrival_success
            },
            'kp': {
                'predicted': kp_result.kp_value,
                'actual': event['kp'],
                'error': kp_error,
                'success': kp_success
            },
            'gssi': {
                'value': gssi_result.gssi,
                'category': gssi_result.category
            }
        }
        print(json.dumps(output, indent=2))


def validate_all(args):
    """Validate against all events"""
    
    print("\nHELIOSICA Validation Summary")
    print("="*70)
    print(f"{'Event':<20} {'Arrival Error':<15} {'Kp Error':<10} {'Result':<10}")
    print("-"*70)
    
    results = []
    
    for date_str, event in VALIDATION_EVENTS.items():
        # Quick validation without detailed output
        dbm = DBMSolver()
        dbm_result = dbm.predict(
            event['v0'], event['vsw'], event['omega'], event['np'],
            probabilistic=False
        )
        
        arrival_error = abs(dbm_result.arrival_time_50 - event['arrival'])
        
        ey = event['vsw'] * abs(event['bz'])
        mp = 1.67e-27
        p_ram = mp * event['np'] * 1e6 * (event['vsw'] * 1000)**2 * 1e9
        
        kp_pred = KpPredictor()
        kp_result = kp_pred.predict(ey, p_ram, event['vsw'], 180)
        kp_error = abs(kp_result.kp_value - event['kp'])
        
        arrival_success = arrival_error <= 6.0
        kp_success = kp_error <= 1.0
        overall = '✅' if (arrival_success and kp_success) else '❌'
        
        print(f"{event['name']:<20} {arrival_error:>6.1f}h ({'✅' if arrival_success else '❌'})   "
              f"{kp_error:>4.1f} ({'✅' if kp_success else '❌'})     {overall}")
        
        results.append({
            'arrival_success': arrival_success,
            'kp_success': kp_success
        })
    
    # Summary statistics
    n_events = len(results)
    arrival_passed = sum(1 for r in results if r['arrival_success'])
    kp_passed = sum(1 for r in results if r['kp_success'])
    both_passed = sum(1 for r in results if r['arrival_success'] and r['kp_success'])
    
    print("\n" + "="*70)
    print(f"Summary:")
    print(f"  Arrival prediction (≤6h): {arrival_passed}/{n_events} ({arrival_passed/n_events*100:.1f}%)")
    print(f"  Kp prediction (≤1.0):     {kp_passed}/{n_events} ({kp_passed/n_events*100:.1f}%)")
    print(f"  Overall success:          {both_passed}/{n_events} ({both_passed/n_events*100:.1f}%)")
    print(f"  Target (H1/H2):           ≥80% / ≥90%")
