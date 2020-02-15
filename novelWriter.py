#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

if sys.hexversion < 0x030600F0:
    print("ERROR: At least Python 3.6 is required")
    sys.exit(1)

try:
    import PySide2.QtCore
except:
    print("ERROR: Failed to load dependency python3-pyside2.qtcore")
    sys.exit(1)

try:
    import PySide2.QtGui
except:
    print("ERROR: Failed to load dependency python3-pyside2.qtgui")
    sys.exit(1)

try:
    import PySide2.QtWidgets
except:
    print("ERROR: Failed to load dependency python3-pyside2.qtwidgets")
    sys.exit(1)

try:
    import PySide2.QtSvg
except:
    print("ERROR: Failed to load dependency python3-pyside2.qtsvg")
    sys.exit(1)

try:
    import lxml
except:
    print("ERROR: Failed to load dependency python3-lxml")
    sys.exit(1)

try:
    import appdirs
except:
    print("ERROR: Failed to load dependency python3-appdirs")
    sys.exit(1)

if __name__ == "__main__":
    import nw
    nw.main(sys.argv[1:])
