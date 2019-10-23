# -*- coding: utf-8 -*-
"""novelWriter Config Class Tester
"""

import nw, pytest
from nwtools import *
from os import path
from nw.config import Config

theConf = Config()

@pytest.mark.core
def testConfigInit(nwTemp,nwRef):
    tmpConf = path.join(nwTemp,"novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert theConf.initConfig(nwTemp)
    assert theConf.setLastPath("")
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSave(nwTemp,nwRef):
    tmpConf = path.join(nwTemp,"novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert theConf.confPath == nwTemp
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetConfPath(nwTemp):
    assert theConf.setConfPath(None)
    assert not theConf.setConfPath(path.join("somewhere","over","the","rainbow"))
    assert theConf.setConfPath(path.join(nwTemp,"novelwriter.conf"))
    assert theConf.confPath == nwTemp
    assert theConf.confFile == "novelwriter.conf"
    assert not theConf.confChanged

@pytest.mark.core
def testConfigLoad():
    assert theConf.loadConfig()
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetWinSize(nwTemp,nwRef):
    tmpConf = path.join(nwTemp,"novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert theConf.setWinSize(1105, 655)
    assert not theConf.confChanged
    assert theConf.setWinSize(70,70)
    assert theConf.confChanged
    assert theConf.setWinSize(1100, 650)
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetTreeColWidths(nwTemp,nwRef):
    tmpConf = path.join(nwTemp,"novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert theConf.setTreeColWidths([0, 0, 0])
    assert theConf.confChanged
    assert theConf.setTreeColWidths([120, 30, 50])
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetMainPanePos(nwTemp,nwRef):
    tmpConf = path.join(nwTemp,"novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert theConf.setMainPanePos([0, 0])
    assert theConf.confChanged
    assert theConf.setMainPanePos([300, 800])
    assert theConf.setDocPanePos([400, 400])
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged
