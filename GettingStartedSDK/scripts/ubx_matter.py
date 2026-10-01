#!/usr/bin/env python3
"""
Matter entry point for the u-blox Getting Started SDK.

Deliberately separate from ``ubx_sdk.py``: the Matter SDKs are several GB and
most users never need them, so the plain SDK launcher does not mention Matter
at all. Invoked through the ``ubx-matter.cmd`` / ``ubx-matter.sh`` shim:

    ubx-matter nora-w4 --doctor
    ubx-matter nora-w4 --clone --build thermometer
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ubx  # noqa: E402

if __name__ == "__main__":
    sys.exit(ubx.main(matter=True))
