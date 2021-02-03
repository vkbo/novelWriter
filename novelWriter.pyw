#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
novelWriter – Windows Start Script
==================================
The main start script for Windows
"""

import os

os.curdir = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    import nw
    nw.main()
