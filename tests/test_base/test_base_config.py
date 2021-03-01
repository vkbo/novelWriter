# -*- coding: utf-8 -*-
"""
novelWriter – Config Class Tester
=================================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import pytest
import sys
import os
import configparser

from shutil import copyfile

from dummy import causeOSError
from tools import cmpFiles

from nw.config import Config
from nw.constants import nwConst, nwFiles

@pytest.mark.base
def testBaseConfig_Constructor(monkeypatch):
    """Test config contructor.
    """
    # Linux
    monkeypatch.setattr("sys.platform", "linux")
    tstConf = Config()
    assert tstConf.osLinux is True
    assert tstConf.osDarwin is False
    assert tstConf.osWindows is False
    assert tstConf.osUnknown is False
    monkeypatch.undo()

    # macOS
    monkeypatch.setattr("sys.platform", "darwin")
    tstConf = Config()
    assert tstConf.osLinux is False
    assert tstConf.osDarwin is True
    assert tstConf.osWindows is False
    assert tstConf.osUnknown is False
    monkeypatch.undo()

    # Windows
    monkeypatch.setattr("sys.platform", "win32")
    tstConf = Config()
    assert tstConf.osLinux is False
    assert tstConf.osDarwin is False
    assert tstConf.osWindows is True
    assert tstConf.osUnknown is False
    monkeypatch.undo()

    # Cygwin
    monkeypatch.setattr("sys.platform", "cygwin")
    tstConf = Config()
    assert tstConf.osLinux is False
    assert tstConf.osDarwin is False
    assert tstConf.osWindows is True
    assert tstConf.osUnknown is False
    monkeypatch.undo()

    # Other
    monkeypatch.setattr("sys.platform", "some_other_os")
    tstConf = Config()
    assert tstConf.osLinux is False
    assert tstConf.osDarwin is False
    assert tstConf.osWindows is False
    assert tstConf.osUnknown is True
    monkeypatch.undo()

# END Test testBaseConfig_Constructor

@pytest.mark.base
def testBaseConfig_Init(monkeypatch, tmpDir, fncDir, outDir, refDir):
    """Test config intialisation.
    """
    tstConf = Config()

    confFile = os.path.join(tmpDir, "novelwriter.conf")
    testFile = os.path.join(outDir, "baseConfig_novelwriter.conf")
    compFile = os.path.join(refDir, "baseConfig_novelwriter.conf")

    # Make sure we don't have any old conf file
    if os.path.isfile(confFile):
        os.unlink(confFile)

    # Let the config class figure out the path
    monkeypatch.setattr("PyQt5.QtCore.QStandardPaths.writableLocation", lambda *args: fncDir)
    tstConf.verQtValue = 50600
    tstConf.initConfig()
    assert tstConf.confPath == os.path.join(fncDir, tstConf.appHandle)
    assert tstConf.dataPath == os.path.join(fncDir, tstConf.appHandle)
    assert not os.path.isfile(confFile)
    tstConf.verQtValue = 50000
    tstConf.initConfig()
    assert tstConf.confPath == os.path.join(fncDir, tstConf.appHandle)
    assert tstConf.dataPath == os.path.join(fncDir, tstConf.appHandle)
    assert not os.path.isfile(confFile)
    monkeypatch.undo()

    # Fail to make folders
    monkeypatch.setattr("os.mkdir", causeOSError)

    tstConfDir = os.path.join(fncDir, "test_conf")
    tstConf.initConfig(confPath=tstConfDir, dataPath=tmpDir)
    assert tstConf.confPath is None
    assert tstConf.dataPath == tmpDir
    assert not os.path.isfile(confFile)

    tstDataDir = os.path.join(fncDir, "test_data")
    tstConf.initConfig(confPath=tmpDir, dataPath=tstDataDir)
    assert tstConf.confPath == tmpDir
    assert tstConf.dataPath is None
    assert os.path.isfile(confFile)
    os.unlink(confFile)

    monkeypatch.undo()

    # Test load/save with no path
    tstConf.confPath = None
    assert not tstConf.loadConfig()
    assert not tstConf.saveConfig()

    # Run again and set the paths directly and correctly
    # This should create a config file as well
    monkeypatch.setattr("os.path.expanduser", lambda *args: "")
    tstConf.spellTool = nwConst.SP_INTERNAL
    tstConf.initConfig(confPath=tmpDir, dataPath=tmpDir)
    assert tstConf.confPath == tmpDir
    assert tstConf.dataPath == tmpDir
    assert os.path.isfile(confFile)

    copyfile(confFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 9])
    monkeypatch.undo()

    # Load and save with OSError
    monkeypatch.setattr("builtins.open", causeOSError)

    assert not tstConf.loadConfig()
    assert tstConf.hasError is True
    assert tstConf.errData != []
    assert tstConf.getErrData().startswith("Could not")
    assert tstConf.hasError is False
    assert tstConf.errData == []

    assert not tstConf.saveConfig()
    assert tstConf.hasError is True
    assert tstConf.errData != []
    assert tstConf.getErrData().startswith("Could not")
    assert tstConf.hasError is False
    assert tstConf.errData == []

    monkeypatch.undo()

    assert tstConf.loadConfig()
    assert tstConf.saveConfig()

    # Test Correcting Quote Settings
    origDbl = tstConf.fmtDoubleQuotes
    origSng = tstConf.fmtSingleQuotes
    orDoDbl = tstConf.doReplaceDQuote
    orDoSng = tstConf.doReplaceSQuote

    tstConf.fmtDoubleQuotes = ["\"", "\""]
    tstConf.fmtSingleQuotes = ["'", "'"]
    tstConf.doReplaceDQuote = True
    tstConf.doReplaceSQuote = True
    assert tstConf.saveConfig()

    assert tstConf.loadConfig()
    assert not tstConf.doReplaceDQuote
    assert not tstConf.doReplaceSQuote

    tstConf.fmtDoubleQuotes = origDbl
    tstConf.fmtSingleQuotes = origSng
    tstConf.doReplaceDQuote = orDoDbl
    tstConf.doReplaceSQuote = orDoSng
    assert tstConf.saveConfig()

    copyfile(confFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 9])

# END Test testBaseConfig_Init

@pytest.mark.base
def testBaseConfig_RecentCache(monkeypatch, tmpConf, tmpDir, fncDir):
    """Test recent cache file.
    """
    # Check failing
    tmpConf.dataPath = None
    assert not tmpConf.loadRecentCache()
    assert not tmpConf.saveRecentCache()
    tmpConf.dataPath = tmpDir

    # Add a couple of values
    pathOne = os.path.join(fncDir, "projPathOne", nwFiles.PROJ_FILE)
    pathTwo = os.path.join(fncDir, "projPathTwo", nwFiles.PROJ_FILE)
    assert tmpConf.updateRecentCache(pathOne, "Proj One", 100, 1600002000)
    assert tmpConf.updateRecentCache(pathTwo, "Proj Two", 200, 1600005600)
    assert tmpConf.recentProj == {
        pathOne: {"time": 1600002000, "title": "Proj One", "words": 100},
        pathTwo: {"time": 1600005600, "title": "Proj Two", "words": 200},
    }

    # Fail to Save
    monkeypatch.setattr("builtins.open", causeOSError)
    assert not tmpConf.saveRecentCache()
    monkeypatch.undo()

    # Save Proper
    cacheFile = os.path.join(tmpDir, nwFiles.RECENT_FILE)
    assert tmpConf.saveRecentCache()
    assert tmpConf.saveRecentCache()
    assert os.path.isfile(cacheFile)

    # Fail to Load
    monkeypatch.setattr("builtins.open", causeOSError)
    tmpConf.recentProj = {}
    assert not tmpConf.loadRecentCache()
    assert tmpConf.recentProj == {}
    monkeypatch.undo()

    # Load Proper
    tmpConf.recentProj = {}
    assert tmpConf.loadRecentCache()
    assert tmpConf.recentProj == {
        pathOne: {"time": 1600002000, "title": "Proj One", "words": 100},
        pathTwo: {"time": 1600005600, "title": "Proj Two", "words": 200},
    }

    # Remove Non-Existent Entry
    assert not tmpConf.removeFromRecentCache("dummy")
    assert tmpConf.recentProj == {
        pathOne: {"time": 1600002000, "title": "Proj One", "words": 100},
        pathTwo: {"time": 1600005600, "title": "Proj Two", "words": 200},
    }

    # Remove Second Entry
    assert tmpConf.removeFromRecentCache(pathTwo)
    assert tmpConf.recentProj == {
        pathOne: {"time": 1600002000, "title": "Proj One", "words": 100},
    }

# END Test testBaseConfig_RecentCache

@pytest.mark.base
def testBaseConfig_SetPath(tmpConf, tmpDir):
    """Test path setters.
    """
    # Conf Path
    assert tmpConf.setConfPath(None)
    assert not tmpConf.setConfPath(os.path.join("somewhere", "over", "the", "rainbow"))
    assert tmpConf.setConfPath(os.path.join(tmpDir, "novelwriter.conf"))
    assert tmpConf.confPath == tmpDir
    assert tmpConf.confFile == "novelwriter.conf"
    assert not tmpConf.confChanged

    # Data Path
    assert tmpConf.setDataPath(None)
    assert not tmpConf.setDataPath(os.path.join("somewhere", "over", "the", "rainbow"))
    assert tmpConf.setDataPath(tmpDir)
    assert tmpConf.dataPath == tmpDir
    assert not tmpConf.confChanged

    # Last Path
    assert tmpConf.setLastPath(None)
    assert tmpConf.lastPath == ""

    assert tmpConf.setLastPath(os.path.join(tmpDir, "file.tmp"))
    assert tmpConf.lastPath == tmpDir

    assert tmpConf.setLastPath("")
    assert tmpConf.lastPath == ""

# END Test testBaseConfig_SetPath

@pytest.mark.base
def testBaseConfig_SettersGetters(tmpConf, tmpDir, outDir, refDir):
    """Set various sizes and positions
    """
    confFile = os.path.join(tmpDir, "novelwriter.conf")
    testFile = os.path.join(outDir, "baseConfig_novelwriter.conf")
    compFile = os.path.join(refDir, "baseConfig_novelwriter.conf")

    # GUI Scaling
    # ===========
    tmpConf.guiScale = 1.0
    assert tmpConf.pxInt(10) == 10
    assert tmpConf.pxInt(13) == 13
    assert tmpConf.rpxInt(10) == 10
    assert tmpConf.rpxInt(13) == 13

    tmpConf.guiScale = 2.0
    assert tmpConf.pxInt(10) == 20
    assert tmpConf.pxInt(13) == 26
    assert tmpConf.rpxInt(10) == 5
    assert tmpConf.rpxInt(13) == 6

    # Setter + Getter Combos
    # ======================

    # Window Size
    tmpConf.guiScale = 1.0
    assert tmpConf.setWinSize(1205, 655)
    assert not tmpConf.confChanged

    tmpConf.guiScale = 2.0
    assert tmpConf.setWinSize(70, 70)
    assert tmpConf.getWinSize() == [70, 70]
    assert tmpConf.winGeometry == [35, 35]

    tmpConf.guiScale = 1.0
    assert tmpConf.setWinSize(70, 70)
    assert tmpConf.getWinSize() == [70, 70]
    assert tmpConf.winGeometry == [70, 70]

    assert tmpConf.setWinSize(1200, 650)

    # Project Tree Columns
    tmpConf.guiScale = 2.0
    assert tmpConf.setTreeColWidths([10, 20, 25])
    assert tmpConf.getTreeColWidths() == [10, 20, 24]
    assert tmpConf.treeColWidth == [5, 10, 12]

    tmpConf.guiScale = 1.0
    assert tmpConf.setTreeColWidths([10, 20, 25])
    assert tmpConf.getTreeColWidths() == [10, 20, 25]
    assert tmpConf.treeColWidth == [10, 20, 25]

    assert tmpConf.setTreeColWidths([200, 50, 30])

    # Novel Tree Columns
    tmpConf.guiScale = 2.0
    assert tmpConf.setNovelColWidths([10, 20])
    assert tmpConf.getNovelColWidths() == [10, 20]
    assert tmpConf.novelColWidth == [5, 10]

    tmpConf.guiScale = 1.0
    assert tmpConf.setNovelColWidths([10, 20])
    assert tmpConf.getNovelColWidths() == [10, 20]
    assert tmpConf.novelColWidth == [10, 20]

    assert tmpConf.setNovelColWidths([200, 50])

    # Project Settings Tree Columns
    tmpConf.guiScale = 2.0
    assert tmpConf.setProjColWidths([10, 20, 30])
    assert tmpConf.getProjColWidths() == [10, 20, 30]
    assert tmpConf.projColWidth == [5, 10, 15]

    tmpConf.guiScale = 1.0
    assert tmpConf.setProjColWidths([10, 20, 30])
    assert tmpConf.getProjColWidths() == [10, 20, 30]
    assert tmpConf.projColWidth == [10, 20, 30]

    assert tmpConf.setProjColWidths([200, 60, 140])

    # Main Pane Splitter
    tmpConf.guiScale = 2.0
    assert tmpConf.setMainPanePos([200, 700])
    assert tmpConf.getMainPanePos() == [200, 700]
    assert tmpConf.mainPanePos == [100, 350]

    tmpConf.guiScale = 1.0
    assert tmpConf.setMainPanePos([200, 700])
    assert tmpConf.getMainPanePos() == [200, 700]
    assert tmpConf.mainPanePos == [200, 700]

    assert tmpConf.setMainPanePos([300, 800])

    # Doc Pane Splitter
    tmpConf.guiScale = 2.0
    assert tmpConf.setDocPanePos([300, 300])
    assert tmpConf.getDocPanePos() == [300, 300]
    assert tmpConf.docPanePos == [150, 150]

    tmpConf.guiScale = 1.0
    assert tmpConf.setDocPanePos([300, 300])
    assert tmpConf.getDocPanePos() == [300, 300]
    assert tmpConf.docPanePos == [300, 300]

    assert tmpConf.setDocPanePos([400, 400])

    # View Pane Splitter
    tmpConf.guiScale = 2.0
    assert tmpConf.setViewPanePos([400, 250])
    assert tmpConf.getViewPanePos() == [400, 250]
    assert tmpConf.viewPanePos == [200, 125]

    tmpConf.guiScale = 1.0
    assert tmpConf.setViewPanePos([400, 250])
    assert tmpConf.getViewPanePos() == [400, 250]
    assert tmpConf.viewPanePos == [400, 250]

    assert tmpConf.setViewPanePos([500, 150])

    # Outline Pane Splitter
    tmpConf.guiScale = 2.0
    assert tmpConf.setOutlinePanePos([400, 250])
    assert tmpConf.getOutlinePanePos() == [400, 250]
    assert tmpConf.outlnPanePos == [200, 125]

    tmpConf.guiScale = 1.0
    assert tmpConf.setOutlinePanePos([400, 250])
    assert tmpConf.getOutlinePanePos() == [400, 250]
    assert tmpConf.outlnPanePos == [400, 250]

    assert tmpConf.setOutlinePanePos([500, 150])

    # Getters Only
    # ============
    tmpConf.guiScale = 1.0
    assert tmpConf.getTextWidth() == 600
    assert tmpConf.getTextMargin() == 40
    assert tmpConf.getTabWidth() == 40
    assert tmpConf.getFocusWidth() == 800

    tmpConf.guiScale = 2.0
    assert tmpConf.getTextWidth() == 1200
    assert tmpConf.getTextMargin() == 80
    assert tmpConf.getTabWidth() == 80
    assert tmpConf.getFocusWidth() == 1600

    # Flag Setters
    # ============
    assert not tmpConf.setShowRefPanel(False)
    assert not tmpConf.showRefPanel
    assert tmpConf.setShowRefPanel(True)

    assert not tmpConf.setViewComments(False)
    assert not tmpConf.viewComments
    assert tmpConf.setViewComments(True)

    assert not tmpConf.setViewSynopsis(False)
    assert not tmpConf.viewSynopsis
    assert tmpConf.setViewSynopsis(True)

    # Check Final File
    # ================

    assert tmpConf.confChanged
    assert tmpConf.saveConfig()
    assert not tmpConf.confChanged

    copyfile(confFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 9])

# END Test testBaseConfig_SettersGetters

@pytest.mark.base
def testBaseConfig_Internal(monkeypatch, tmpConf):
    """Check internal functions.
    """
    # Function _packList
    assert tmpConf._packList(["A", 1, 2.0, None, False]) == "A, 1, 2.0, None, False"

    # Function _unpackList
    assert tmpConf._unpackList("1, 2, 3", [0, 0, 0], tmpConf.CNF_I_LST) == [1, 2, 3]
    assert tmpConf._unpackList("1, 2   ", [0, 0, 0], tmpConf.CNF_I_LST) == [1, 2, 0]
    assert tmpConf._unpackList("A, B, C", [0, 0, 0], tmpConf.CNF_I_LST) == [0, 0, 0]
    assert tmpConf._unpackList("1, 2, 3", ["X", "Y", "Z"], tmpConf.CNF_S_LST) == ["1", "2", "3"]
    assert tmpConf._unpackList("A, B   ", ["X", "Y", "Z"], tmpConf.CNF_S_LST) == ["A", "B", "Z"]
    assert tmpConf._unpackList("A, B, C", ["X", "Y", "Z"], tmpConf.CNF_S_LST) == ["A", "B", "C"]
    assert tmpConf._unpackList("A, B, C", ["X", "Y", "Z"], tmpConf.CNF_STR) == ["X", "Y", "Z"]

    # Function _parseLine
    cnfParse = configparser.ConfigParser()
    cnfParse.read_string(
        "[Main]\n"
        "val_string = dummy\n"
        "val_int = 123\n"
        "val_bool = True\n"
        "val_list_string = A, B, C\n"
        "val_list_int = 1, 2, 3\n"
    )

    assert tmpConf._parseLine(
        cnfParse, "Main", "val_string", tmpConf.CNF_STR, "default"
    ) == "dummy"
    assert tmpConf._parseLine(
        cnfParse, "Main", "nope", tmpConf.CNF_STR, "default"
    ) == "default"

    assert tmpConf._parseLine(
        cnfParse, "Main", "val_int", tmpConf.CNF_INT, "0"
    ) == 123
    assert tmpConf._parseLine(
        cnfParse, "Main", "nope", tmpConf.CNF_INT, 0
    ) == 0
    assert tmpConf._parseLine(
        cnfParse, "Main", "val_string", tmpConf.CNF_INT, 0
    ) == 0

    assert tmpConf._parseLine(
        cnfParse, "Main", "val_bool", tmpConf.CNF_BOOL, False
    ) is True
    assert tmpConf._parseLine(
        cnfParse, "Main", "nope", tmpConf.CNF_BOOL, False
    ) is False
    assert tmpConf._parseLine(
        cnfParse, "Main", "val_string", tmpConf.CNF_BOOL, False
    ) is False

    assert tmpConf._parseLine(
        cnfParse, "Main", "val_list_string", tmpConf.CNF_S_LST, ["W", "X", "Y", "Z"]
    ) == ["A", "B", "C", "Z"]
    assert tmpConf._parseLine(
        cnfParse, "Main", "nope", tmpConf.CNF_S_LST, ["W", "X", "Y", "Z"]
    ) == ["W", "X", "Y", "Z"]

    assert tmpConf._parseLine(
        cnfParse, "Main", "val_list_int", tmpConf.CNF_I_LST, [6, 7, 8, 9]
    ) == [1, 2, 3, 9]
    assert tmpConf._parseLine(
        cnfParse, "Main", "nope", tmpConf.CNF_S_LST, [6, 7, 8, 9]
    ) == [6, 7, 8, 9]

    # Function _checkNone
    assert tmpConf._checkNone(None) is None
    assert tmpConf._checkNone("None") is None
    assert tmpConf._checkNone("stuff") == "stuff"

    # Function _checkOptionalPackages
    # (Assumes enchant package exists ans is importable)
    tmpConf._checkOptionalPackages()
    assert tmpConf.hasEnchant is True

    monkeypatch.setitem(sys.modules, "enchant", None)
    tmpConf._checkOptionalPackages()
    assert tmpConf.hasEnchant is False
    monkeypatch.undo()

    monkeypatch.setattr("shutil.which", lambda *args: "dummy")
    tmpConf._checkOptionalPackages()
    assert tmpConf.hasAssistant is True
    monkeypatch.undo()

    monkeypatch.setattr("shutil.which", lambda *args: None)
    tmpConf._checkOptionalPackages()
    assert tmpConf.hasAssistant is False
    monkeypatch.undo()

# END Test testBaseConfig_Internal
