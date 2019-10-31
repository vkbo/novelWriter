#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

if sys.hexversion < 0x030500F0:
    print("ERROR: At least Python 3.5 is required")
    exit(1)

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

spellPack = None
try:
    import enchant
    spellPack = "enchant"
except:
    print("WARNING: No spell check library found.")
    print("Please install python3-enchant if you want to use spell checking")

if __name__ == "__main__":
    import nw
    inArgs = sys.argv[1:]
    if spellPack is not None:
        inArgs.append("--spell=%s" % spellPack)
    nw.main(inArgs)
