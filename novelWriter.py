#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
novelWriter – Linux Start Script
================================
The main start script for Linux
"""

import sys

try:
    import PyQt5.QtWidgets # noqa: F401
    import PyQt5.QtGui # noqa: F401
    import PyQt5.QtCore # noqa: F401
except Exception:
    print("ERROR: Failed to load dependency python3-pyqt5")
    sys.exit(1)

if __name__ == "__main__":
    import nw
    nw.main(sys.argv[1:])
