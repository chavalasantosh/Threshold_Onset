#!/usr/bin/env python3
"""
Simple wrapper to start version control watching.

Usage: python watch_version.py
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from version_control import LocalVersionControl

if __name__ == "__main__":
    vc = LocalVersionControl()
    
    print("=" * 60)
    print("THRESHOLD_ONSET - Local Version Control")
    print("=" * 60)
    print()
    
    try:
        vc.watch()
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Version control stopped.")
        print("=" * 60)
