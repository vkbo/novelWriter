#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pstats
import os

profDir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "prof"))

print("")
print("Profiles directory: %s" % profDir)
print("")

profMainWindows = pstats.Stats(os.path.join(profDir, "testMainWindows.prof"))
profMainWindows.sort_stats("cumtime")
profMainWindows.print_stats("nw/")
