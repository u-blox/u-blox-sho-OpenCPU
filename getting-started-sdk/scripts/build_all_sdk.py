#!/usr/bin/env python3
"""
Build every target through ubx-sdk.cmd (Windows) or ubx-sdk.sh. Developer
check, not a user tool; see build_all.py.

    python scripts/build_all_sdk.py                  clean build of every target
    python scripts/build_all_sdk.py --incremental    no clean, faster rerun
    python scripts/build_all_sdk.py nora-w40 iris-w10
    python scripts/build_all_sdk.py --setup          --clone/--install/--build-sdk first
    python scripts/build_all_sdk.py --dry-run        show the launcher commands only
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_all  # noqa: E402

if __name__ == "__main__":
    sys.exit(build_all.main())
