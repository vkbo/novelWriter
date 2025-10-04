#!/usr/bin/env python3
"""
novelWriter – Start Script
==========================
"""  # noqa
import os
import sys

try:
    import PyQt6.QtCore  # noqa: F401
    import PyQt6.QtGui  # noqa: F401
    import PyQt6.QtWidgets  # noqa: F401
except Exception:
    print("ERROR: Failed to load dependency PyQt6")
    sys.exit(1)

os.curdir = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    import novelwriter
    novelwriter.main(sys.argv[1:])
