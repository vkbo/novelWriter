# -*- coding: utf-8 -*-
"""novelWriter Config Class Tester
"""

import nw, pytest
from nwtools import *
from os import path, unlink
from nw.config import Config

theConf  = Config()
testDir  = path.dirname(__file__)
testTemp = path.join(testDir,"temp")
testRef  = path.join(testDir,"reference")
tmpConf  = path.join(testTemp,"novelwriter.conf")
refConf  = path.join(testRef, "novelwriter.conf")

ensureDir(testTemp)

# Clean out old stuff
if path.isfile(tmpConf):
    unlink(tmpConf)

@pytest.mark.core
def testConfigInit():
    assert theConf.initConfig(testTemp)
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSave():
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetConfPath():
    assert theConf.setConfPath(None)
    assert not theConf.setConfPath(path.join("somewhere","over","the","rainbow"))
    assert theConf.setConfPath(path.join(testTemp,"novelwriter.conf"))
    assert theConf.confPath == testTemp
    assert theConf.confFile == "novelwriter.conf"
    assert not theConf.confChanged

@pytest.mark.core
def testConfigLoad():
    assert theConf.loadConfig()
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetWinSize():
    assert theConf.setWinSize(1105, 655)
    assert not theConf.confChanged
    assert theConf.setWinSize(70,70)
    assert theConf.confChanged
    assert theConf.setWinSize(1100, 650)
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetTreeColWidths():
    assert theConf.setTreeColWidths([0, 0, 0])
    assert theConf.confChanged
    assert theConf.setTreeColWidths([120, 30, 50])
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetMainPanePos():
    assert theConf.setMainPanePos([0, 0])
    assert theConf.confChanged
    assert theConf.setMainPanePos([300, 800])
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged
