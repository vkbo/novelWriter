# -*- coding: utf-8 -*-
"""novelWriter Config Class Tester
"""

import pytest
from nwtools import cmpFiles
from os import path
from nw.config import Config

theConf = Config()

@pytest.mark.core
def testConfigInit(nwTemp, nwRef):
    tmpConf = path.join(nwTemp, "novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert theConf.initConfig(nwTemp, nwTemp)
    assert theConf.setLastPath("")
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSave(nwTemp, nwRef):
    tmpConf = path.join(nwTemp, "novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert theConf.confPath == nwTemp
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetConfPath(nwTemp):
    assert theConf.setConfPath(None)
    assert not theConf.setConfPath(path.join("somewhere", "over", "the", "rainbow"))
    assert theConf.setConfPath(path.join(nwTemp, "novelwriter.conf"))
    assert theConf.confPath == nwTemp
    assert theConf.confFile == "novelwriter.conf"
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetDataPath(nwTemp):
    assert theConf.setDataPath(None)
    assert not theConf.setDataPath(path.join("somewhere", "over", "the", "rainbow"))
    assert theConf.setDataPath(nwTemp)
    assert theConf.dataPath == nwTemp
    assert not theConf.confChanged

@pytest.mark.core
def testConfigLoad():
    assert theConf.loadConfig()
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetWinSize(nwTemp, nwRef):
    tmpConf = path.join(nwTemp, "novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert theConf.setWinSize(1105, 655)
    assert not theConf.confChanged
    assert theConf.setWinSize(70, 70)
    assert theConf.confChanged
    assert theConf.setWinSize(1100, 650)
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetTreeColWidths(nwTemp, nwRef):
    tmpConf = path.join(nwTemp, "novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert theConf.setTreeColWidths([0, 0, 0])
    assert theConf.confChanged
    assert theConf.setTreeColWidths([120, 30, 50])
    assert theConf.setProjColWidths([140, 55, 140])
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigSetPanePos(nwTemp, nwRef):
    tmpConf = path.join(nwTemp, "novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert theConf.setMainPanePos([0, 0])
    assert theConf.confChanged
    assert theConf.setMainPanePos([300, 800])
    assert theConf.setDocPanePos([400, 400])
    assert theConf.setViewPanePos([500, 150])
    assert theConf.setOutlinePanePos([500, 150])
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigFlags(nwTemp, nwRef):
    tmpConf = path.join(nwTemp, "novelwriter.conf")
    refConf = path.join(nwRef, "novelwriter.conf")
    assert not theConf.setShowRefPanel(False)
    assert theConf.setShowRefPanel(True)
    assert theConf.confChanged
    assert theConf.saveConfig()
    assert cmpFiles(tmpConf, refConf, [2])
    assert not theConf.confChanged

@pytest.mark.core
def testConfigErrors(nwTemp):
    nonPath = path.join("somewhere", "over", "the", "rainbow")
    assert theConf.initConfig(nonPath, nonPath)
    assert theConf.hasError
    assert not theConf.loadConfig()
    assert not theConf.saveConfig()
    assert not theConf.loadRecentCache()
    assert len(theConf.getErrData()) > 0

@pytest.mark.core
def testConfigInternals():
    assert theConf._checkNone(None) is None
    assert theConf._checkNone("None") is None
