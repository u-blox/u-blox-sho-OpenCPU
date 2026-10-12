#!/usr/bin/env python3
"""
Plain SDK entry point for the u-blox Getting Started SDK.

Invoked through the ``ubx-sdk.cmd`` / ``ubx-sdk.sh`` shim:

    ubx-sdk nora-w40 --clone --install --build hello_world
    ubx-sdk iris-w10 --doctor

The shared logic lives in ``ubx.py``; Matter uses the same core through
``ubx_matter.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ubx  # noqa: E402

if __name__ == "__main__":
    sys.exit(ubx.main())
