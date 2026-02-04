#!/usr/bin/env python3
"""
LOBSTER HFT Engine - Terminal User Interface

A professional TUI for the LOBSTER C++ Order Matching Engine.
Connects to the TCP server and provides real-time visualization
of algorithmic trading activity.

Usage:
    python lobster_tui.py [--host HOST] [--port PORT]
    
Requirements:
    pip install textual rich
"""

import argparse
import sys


def check_dependencies():
    missing = []
    try:
        import textual
    except ImportError:
        missing.append("textual")
    try:
        import rich
    except ImportError:
        missing.append("rich")
    
    if missing:
        print("Missing required dependencies:", ", ".join(missing))
        print("Install with: pip install textual rich")
        sys.exit(1)


def main():
    check_dependencies()
    
    parser = argparse.ArgumentParser(
        description="LOBSTER HFT Engine TUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Controls:
  Q           Quit the application
  1           Switch to Market Making strategy
  2           Switch to Momentum strategy  
  3           Switch to Arbitrage strategy
  +/-         Increase/Decrease order rate
  SPACE       Pause/Resume order generation
  R           Reset session statistics

Examples:
  python lobster_tui.py                    # Default (localhost:54321)
  python lobster_tui.py --port 12345       # Custom port
  python lobster_tui.py --host 192.168.1.5 # Remote server
        """
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Server host address (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=54321,
        help="Server port (default: 54321)"
    )
    
    args = parser.parse_args()
    
    from tui import run_app
    run_app(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
