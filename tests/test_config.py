# -*- coding: utf-8 -*-
"""novelWriter Config Class Tester

 novelWriter – Config Class Tester
===================================

"""

import nw
import filecmp

from nwtools import cmpFiles

from os import path, unlink

from nw.config import Config

theConf  = Config()
testDir  = path.dirname(__file__)
testTemp = path.join(testDir,"temp")
testRef  = path.join(testDir,"reference")
tmpConf  = path.join(testTemp,"novelwriter.conf")
refConf  = path.join(testRef, "novelwriter.conf")

# Clean out old stuff
if path.isfile(tmpConf):
    unlink(tmpConf)

def testConfigInit():
    assert theConf.initConfig(testTemp)
    assert cmpFiles(tmpConf, refConf, [2])

def testConfigSave():
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
