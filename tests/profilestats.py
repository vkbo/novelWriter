#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pstats

from os import path

profDir = path.abspath(path.join(path.dirname(__file__),"..","prof"))

print("")
print("Profiles directory: %s" % profDir)
print("")

profMainWindows = pstats.Stats(path.join(profDir,"testMainWindows.prof"))
profMainWindows.sort_stats("cumtime")
profMainWindows.print_stats("nw/")
