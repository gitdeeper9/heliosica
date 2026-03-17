"""
HELIOSICA Command Line Interface
Main entry point for CLI commands
"""

import argparse
import sys
from typing import Optional
from datetime import datetime, timedelta

from heliosica import __version__
from heliosica.cli import (
    forecast, monitor, download, validate, serve
)


def create_parser() -> argparse.ArgumentParser:
    """Create main argument parser"""
    parser = argparse.ArgumentParser(
        description='HELIOSICA - Space Weather Forecasting Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  heliosica forecast --cme 2024-01-01 --v0 1200 --omega 60
  heliosica monitor --realtime
  heliosica download --source soho --year 2024
  heliosica validate --event 2003-10-29
  heliosica serve --port 5000
        """
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'HELIOSICA v{__version__}'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Command to execute',
        required=True
    )
    
    # forecast command
    forecast_parser = subparsers.add_parser(
        'forecast',
        help='Forecast CME transit and storm severity'
    )
    forecast.add_arguments(forecast_parser)
    
    # monitor command
    monitor_parser = subparsers.add_parser(
        'monitor',
        help='Monitor real-time space weather conditions'
    )
    monitor.add_arguments(monitor_parser)
    
    # download command
    download_parser = subparsers.add_parser(
        'download',
        help='Download data from external sources'
    )
    download.add_arguments(download_parser)
    
    # validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate against historical events'
    )
    validate.add_arguments(validate_parser)
    
    # serve command
    serve_parser = subparsers.add_parser(
        'serve',
        help='Start web dashboard server'
    )
    serve.add_arguments(serve_parser)
    
    return parser


def main(args: Optional[list] = None):
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args(args)
    
    # Dispatch to appropriate command
    if args.command == 'forecast':
        forecast.run(args)
    elif args.command == 'monitor':
        monitor.run(args)
    elif args.command == 'download':
        download.run(args)
    elif args.command == 'validate':
        validate.run(args)
    elif args.command == 'serve':
        serve.run(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
