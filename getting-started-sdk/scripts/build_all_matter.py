#!/usr/bin/env python3
"""
Build the default vendor Matter example of every target through
ubx-matter.cmd (Windows) or ubx-matter.sh. Developer check, not a user tool;
see build_all.py. The Matter SDKs are several GB each; --setup fetches them.

    python scripts/build_all_matter.py                  clean build of every target
    python scripts/build_all_matter.py --incremental    no clean, faster rerun
    python scripts/build_all_matter.py nora-w40 nora-b20-b21-b22
    python scripts/build_all_matter.py --setup          --clone/--install first
    python scripts/build_all_matter.py --dry-run        show the launcher commands only
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_all  # noqa: E402

if __name__ == "__main__":
    sys.exit(build_all.main(matter=True))
