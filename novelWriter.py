#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

try:
    import PyQt5.QtWidgets
    import PyQt5.QtGui
    import PyQt5.QtCore
except:
    print("ERROR: Failed to load dependency python3-pyqt5")
    exit(1)

try:
    import PyQt5.QtSvg
except:
    print("ERROR: Failed to load dependency python3-pyqt5.qtsvg")
    exit(1)

try:
    import lxml
except:
    print("ERROR: Failed to load dependency python3-lxml")
    exit(1)

try:
    import appdirs
except:
    print("ERROR: Failed to load dependency python3-appdirs")
    exit(1)

try:
    import enchant
except:
    print("ERROR: Failed to load dependency python3-enchant")
    exit(1)

if __name__ == "__main__":
    import nw
    nw.main(sys.argv[1:])
