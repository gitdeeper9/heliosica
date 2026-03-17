"""
HELIOSICA CLI - Download Command
Download data from external sources
"""

import argparse
from datetime import datetime
import sys
import os

from heliosica.data.loaders.soho import SOHOLoader
from heliosica.data.loaders.omni import OMNILoader
from heliosica.data.loaders.nmdb import NMDBLoader


def add_arguments(parser: argparse.ArgumentParser):
    """Add download command arguments"""
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        choices=['soho', 'omni', 'nmdb', 'sample'],
        help='Data source to download'
    )
    parser.add_argument(
        '--year',
        type=int,
        help='Year to download (for OMNI)'
    )
    parser.add_argument(
        '--station',
        type=str,
        default='oulu',
        help='Neutron monitor station (for NMDB)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./data/raw',
        help='Output directory (default: ./data/raw)'
    )


def run(args):
    """Execute download command"""
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    if args.source == 'soho':
        download_soho(args)
    elif args.source == 'omni':
        download_omni(args)
    elif args.source == 'nmdb':
        download_nmdb(args)
    elif args.source == 'sample':
        download_sample(args)


def download_soho(args):
    """Download SOHO/LASCO CME catalogue"""
    print(f"Downloading SOHO/LASCO CME catalogue...")
    
    loader = SOHOLoader(use_cache=True)
    
    stats = loader.get_statistics()
    print(f"\nDownload complete:")
    print(f"  Total CMEs: {stats['total_cmes']}")
    print(f"  Mean velocity: {stats['mean_velocity']:.0f} km/s")
    print(f"  Max velocity: {stats['max_velocity']:.0f} km/s")
    print(f"  Halo CMEs: {stats['halo_count']}")
    
    # Save to output directory
    print(f"\nSaved to: {args.output}/soho/")


def download_omni(args):
    """Download OMNI data"""
    if not args.year:
        print("Error: --year required for OMNI download")
        sys.exit(1)
    
    print(f"Downloading OMNI data for {args.year}...")
    
    loader = OMNILoader(cache_enabled=True)
    data = loader.fetch_year(args.year)
    
    print(f"\nDownload complete:")
    print(f"  Retrieved {len(data)} intervals")
    
    if data:
        stats = loader.compute_statistics(data)
        print(f"  Mean Bz: {stats['mean_bz']:.2f} nT")
        print(f"  Mean Vsw: {stats['mean_vsw']:.0f} km/s")


def download_nmdb(args):
    """Download NMDB neutron monitor data"""
    print(f"Downloading NMDB data for station {args.station}...")
    
    loader = NMDBLoader(station=args.station)
    
    # Get recent data
    data = loader.fetch_realtime(1440)  # Last 24 hours
    
    print(f"\nDownload complete:")
    print(f"  Retrieved {len(data)} measurements")
    
    if data:
        baseline_mean, baseline_std = loader.get_baseline(days=7)
        print(f"  Baseline: {baseline_mean:.0f} ± {baseline_std:.0f} counts/min")


def download_sample(args):
    """Download sample data"""
    print("Downloading sample data...")
    
    # Create sample directories
    sample_dir = os.path.join(args.output, 'sample')
    os.makedirs(sample_dir, exist_ok=True)
    
    # Download small sample from each source
    print("\n1. SOHO sample (Halloween 2003 CMEs)...")
    soho = SOHOLoader()
    start = datetime(2003, 10, 28)
    end = datetime(2003, 10, 31)
    cmes = soho.search_cmes(start, end)
    print(f"   Found {len(cmes)} CMEs")
    
    print("\n2. OMNI sample (Halloween 2003 storm)...")
    omni = OMNILoader()
    omni_data = omni.get_range(start, end)
    print(f"   Found {len(omni_data)} intervals")
    
    print("\n3. NMDB sample (Oulu station)...")
    nmdb = NMDBLoader('oulu')
    nmdb_data = nmdb.fetch_realtime(60)
    print(f"   Found {len(nmdb_data)} recent measurements")
    
    print(f"\n✅ Sample data saved to {sample_dir}")
    print("\nTo use sample data:")
    print("  heliosica forecast --cme 2003-10-29")
