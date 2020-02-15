#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

if sys.hexversion < 0x030600F0:
    print("ERROR: At least Python 3.6 is required")
    sys.exit(1)

try:
    import PyQt5.QtWidgets
    import PyQt5.QtGui
    import PyQt5.QtCore
except:
    print("ERROR: Failed to load dependency python3-pyqt5")
    sys.exit(1)

try:
    import PyQt5.QtSvg
except:
    print("ERROR: Failed to load dependency python3-pyqt5.qtsvg")
    sys.exit(1)

try:
    import lxml
except:
    print("ERROR: Failed to load dependency python3-lxml")
    sys.exit(1)

if __name__ == "__main__":
    import nw
    nw.main(sys.argv[1:])
