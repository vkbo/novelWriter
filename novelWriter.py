#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

try:
    import PyQt5.QtWidgets
    import PyQt5.QtGui
    import PyQt5.QtCore
except:
    print("ERROR: Failed to load dependency python3-pyqt5")
    sys.exit(1)

if __name__ == "__main__":
    import nw
    nw.main(sys.argv[1:])
