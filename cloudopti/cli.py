"""Command-line interface for CloudOpti"""

import sys
import argparse
from cloudopti.aws_cost_monitor import AWSCostMonitor


def main():
    """Main entry point for the opti command"""
    parser = argparse.ArgumentParser(
        description="CloudOpti - AWS Cost Monitoring Tool",
        prog="opti"
    )
    
    subparsers = parser.add_subparsers(dest="service", help="Service to monitor")
    
    # AWS subcommand
    aws_parser = subparsers.add_parser("aws", help="Monitor AWS costs")
    
    args = parser.parse_args()
    
    if args.service == "aws":
        monitor = AWSCostMonitor()
        try:
            monitor.run()
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

