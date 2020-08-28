# -*- coding: utf-8 -*-
"""novelWriter Config Class Tester
"""

import pytest
from nwtools import cmpFiles
from os import path

@pytest.mark.core
def testConfigCore(tmpConf, nwTemp, nwRef):
    refConf = path.join(nwRef, "novelwriter.conf")
    testConf = path.join(tmpConf.confPath, "novelwriter.conf")

    assert tmpConf.confPath == nwTemp
    assert tmpConf.saveConfig()
    assert cmpFiles(testConf, refConf, [2])
    assert not tmpConf.confChanged

    assert tmpConf.loadConfig()
    assert not tmpConf.confChanged

@pytest.mark.core
def testConfigSetConfPath(tmpConf, nwTemp):
    assert tmpConf.setConfPath(None)
    assert not tmpConf.setConfPath(path.join("somewhere", "over", "the", "rainbow"))
    assert tmpConf.setConfPath(path.join(nwTemp, "novelwriter.conf"))
    assert tmpConf.confPath == nwTemp
    assert tmpConf.confFile == "novelwriter.conf"
    assert not tmpConf.confChanged

@pytest.mark.core
def testConfigSetDataPath(tmpConf, nwTemp):
    assert tmpConf.setDataPath(None)
    assert not tmpConf.setDataPath(path.join("somewhere", "over", "the", "rainbow"))
    assert tmpConf.setDataPath(nwTemp)
    assert tmpConf.dataPath == nwTemp
    assert not tmpConf.confChanged

@pytest.mark.core
def testConfigSetWinSize(tmpConf, nwTemp, nwRef):
    refConf = path.join(nwRef, "novelwriter.conf")
    testConf = path.join(tmpConf.confPath, "novelwriter.conf")

    assert tmpConf.confPath == nwTemp
    assert tmpConf.setWinSize(1105, 655)
    assert not tmpConf.confChanged
    assert tmpConf.setWinSize(70, 70)
    assert tmpConf.confChanged
    assert tmpConf.setWinSize(1100, 650)
    assert tmpConf.saveConfig()

    assert cmpFiles(testConf, refConf, [2])
    assert not tmpConf.confChanged

@pytest.mark.core
def testConfigSetTreeColWidths(tmpConf, nwTemp, nwRef):
    refConf = path.join(nwRef, "novelwriter.conf")
    testConf = path.join(tmpConf.confPath, "novelwriter.conf")

    assert tmpConf.confPath == nwTemp
    assert tmpConf.setTreeColWidths([0, 0, 0])
    assert tmpConf.confChanged
    assert tmpConf.setTreeColWidths([120, 30, 50])
    assert tmpConf.setProjColWidths([140, 55, 140])
    assert tmpConf.saveConfig()

    assert cmpFiles(testConf, refConf, [2])
    assert not tmpConf.confChanged

@pytest.mark.core
def testConfigSetPanePos(tmpConf, nwTemp, nwRef):
    refConf = path.join(nwRef, "novelwriter.conf")
    testConf = path.join(tmpConf.confPath, "novelwriter.conf")

    assert tmpConf.confPath == nwTemp
    assert tmpConf.setMainPanePos([0, 0])
    assert tmpConf.confChanged
    assert tmpConf.setMainPanePos([300, 800])
    assert tmpConf.setDocPanePos([400, 400])
    assert tmpConf.setViewPanePos([500, 150])
    assert tmpConf.setOutlinePanePos([500, 150])
    assert tmpConf.saveConfig()

    assert cmpFiles(testConf, refConf, [2])
    assert not tmpConf.confChanged

@pytest.mark.core
def testConfigFlags(tmpConf, nwTemp, nwRef):
    refConf = path.join(nwRef, "novelwriter.conf")
    testConf = path.join(tmpConf.confPath, "novelwriter.conf")

    assert tmpConf.confPath == nwTemp
    assert not tmpConf.setShowRefPanel(False)
    assert tmpConf.setShowRefPanel(True)
    assert tmpConf.confChanged
    assert tmpConf.saveConfig()

    assert cmpFiles(testConf, refConf, [2])
    assert not tmpConf.confChanged

@pytest.mark.core
def testConfigErrors(tmpConf):
    nonPath = path.join("somewhere", "over", "the", "rainbow")
    assert tmpConf.initConfig(nonPath, nonPath)
    assert tmpConf.hasError
    assert not tmpConf.loadConfig()
    assert not tmpConf.saveConfig()
    assert not tmpConf.loadRecentCache()
    assert len(tmpConf.getErrData()) > 0

@pytest.mark.core
def testConfigInternals(tmpConf):
    assert tmpConf._checkNone(None) is None
    assert tmpConf._checkNone("None") is None
