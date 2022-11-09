"""
novelWriter – Config Class Tester
=================================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import sys
import pytest

from shutil import copyfile
from pathlib import Path

from mock import causeOSError, MockApp
from tools import cmpFiles, writeFile

from novelwriter.config import Config, RecentProjects
from novelwriter.constants import nwFiles


@pytest.mark.base
def testBaseConfig_Constructor(monkeypatch):
    """Test config contructor.
    """
    # Linux
    with monkeypatch.context() as mp:
        mp.setattr("sys.platform", "linux")
        tstConf = Config()
        assert tstConf.osLinux is True
        assert tstConf.osDarwin is False
        assert tstConf.osWindows is False
        assert tstConf.osUnknown is False

    # macOS
    with monkeypatch.context() as mp:
        mp.setattr("sys.platform", "darwin")
        tstConf = Config()
        assert tstConf.osLinux is False
        assert tstConf.osDarwin is True
        assert tstConf.osWindows is False
        assert tstConf.osUnknown is False

    # Windows
    with monkeypatch.context() as mp:
        mp.setattr("sys.platform", "win32")
        tstConf = Config()
        assert tstConf.osLinux is False
        assert tstConf.osDarwin is False
        assert tstConf.osWindows is True
        assert tstConf.osUnknown is False

    # Cygwin
    with monkeypatch.context() as mp:
        mp.setattr("sys.platform", "cygwin")
        tstConf = Config()
        assert tstConf.osLinux is False
        assert tstConf.osDarwin is False
        assert tstConf.osWindows is True
        assert tstConf.osUnknown is False

    # Other
    with monkeypatch.context() as mp:
        mp.setattr("sys.platform", "some_other_os")
        tstConf = Config()
        assert tstConf.osLinux is False
        assert tstConf.osDarwin is False
        assert tstConf.osWindows is False
        assert tstConf.osUnknown is True

    # App is single file
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.is_file", lambda *a: True)
        tstConf = Config()
        assert tstConf._appPath == tstConf._appRoot

# END Test testBaseConfig_Constructor


@pytest.mark.base
def testBaseConfig_InitLoadSave(monkeypatch, fncPath, tstPaths):
    """Test config intialisation.
    """
    tstConf = Config()

    confFile = fncPath / nwFiles.CONF_FILE
    testFile = tstPaths.outDir / "baseConfig_novelwriter.conf"
    compFile = tstPaths.refDir / "baseConfig_novelwriter.conf"

    # Make sure we don't have any old conf file
    if confFile.is_file():
        confFile.unlink()

    # Running init against a new oath should write a new config file
    tstConf.initConfig(confPath=fncPath, dataPath=fncPath)
    assert tstConf._confPath == fncPath
    assert tstConf._dataPath == fncPath
    assert confFile.exists()

    # Check that we have a default file
    copyfile(confFile, testFile)
    ignore = ("timestamp", "lastnotes", "guilang", "lastpath")
    assert cmpFiles(testFile, compFile, ignoreStart=ignore)
    tstConf.errorText()  # This clears the error cache

    # Block saving the file
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert tstConf.saveConfig() is False
        assert tstConf.hasError is True
        assert tstConf.errorText().startswith("Could not save config file")

    # Block loading the file
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert tstConf.loadConfig() is False
        assert tstConf.hasError is True
        assert tstConf.errorText().startswith("Could not load config file")

    # Change a few settings, save, reset, and reload
    tstConf.guiTheme = "foo"
    tstConf.guiSyntax = "bar"
    assert tstConf.saveConfig() is True

    newConf = Config()
    newConf.initConfig(confPath=fncPath, dataPath=fncPath)
    assert newConf.guiTheme == "foo"
    assert newConf.guiSyntax == "bar"

    # Test Correcting Quote Settings
    tstConf.fmtDoubleQuotes = ["\"", "\""]
    tstConf.fmtSingleQuotes = ["'", "'"]
    tstConf.doReplaceDQuote = True
    tstConf.doReplaceSQuote = True
    assert tstConf.saveConfig() is True

    assert newConf.loadConfig() is True
    assert newConf.doReplaceDQuote is False
    assert newConf.doReplaceSQuote is False

# END Test testBaseConfig_InitLoadSave


@pytest.mark.base
def testBaseConfig_Localisation(fncPath, tstPaths):
    """Test localisation.
    """
    tstConf = Config()
    tstConf.initConfig(confPath=fncPath, dataPath=fncPath)

    # Localisation
    # ============

    i18nDir = fncPath / "i18n"
    i18nDir.mkdir()
    tstConf._nwLangPath = i18nDir

    copyfile(tstPaths.filesDir / "nw_en_GB.qm", i18nDir / "nw_en_GB.qm")
    writeFile(i18nDir / "nw_en_GB.ts", "")
    writeFile(i18nDir / "nw_abcd.qm", "")

    tstApp = MockApp()
    tstConf.initLocalisation(tstApp)

    # Check Lists
    theList = tstConf.listLanguages(tstConf.LANG_NW)
    assert theList == [("en_GB", "British English")]
    theList = tstConf.listLanguages(tstConf.LANG_PROJ)
    assert theList == [("en_GB", "British English")]
    theList = tstConf.listLanguages(None)
    assert theList == []

    # Add Language
    copyfile(tstPaths.filesDir / "nw_en_GB.qm", i18nDir / "nw_fr.qm")
    writeFile(i18nDir / "nw_fr.ts", "")

    theList = tstConf.listLanguages(tstConf.LANG_NW)
    assert theList == [("en_GB", "British English"), ("fr", "Français")]

# END Test testBaseConfig_Localisation


@pytest.mark.base
def testBaseConfig_Methods(tmpConf, tmpPath):
    """Check class methods.
    """
    # Data Path
    assert tmpConf.dataPath() == tmpPath
    assert tmpConf.dataPath("stuff") == tmpPath / "stuff"

    # Assets Path
    appPath = tmpConf._appPath
    assert tmpConf.assetPath() == appPath / "assets"
    assert tmpConf.assetPath("stuff") == appPath / "assets" / "stuff"

    # Last Path
    assert tmpConf.lastPath() == tmpPath

    tmpStuff = tmpPath / "stuff"
    tmpStuff.mkdir()
    tmpConf.setLastPath(tmpStuff)
    assert tmpConf.lastPath() == tmpStuff

    fileStuff = tmpStuff / "more_stuff.txt"
    fileStuff.write_text("Stuff")
    tmpConf.setLastPath(fileStuff)
    assert tmpConf.lastPath() == tmpStuff

    fileStuff.unlink()
    tmpStuff.rmdir()
    assert tmpConf.lastPath() == Path.home().absolute()

    # Recent Projects
    assert isinstance(tmpConf.recentProjects, RecentProjects)

# END Test testBaseConfig_Methods


@pytest.mark.base
def testBaseConfig_SettersGetters(tmpConf):
    """Set various sizes and positions
    """
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
    tmpConf.setWinSize(1205, 655)
    assert tmpConf.confChanged is False

    tmpConf.guiScale = 2.0
    tmpConf.setWinSize(70, 70)
    assert tmpConf.getWinSize() == [70, 70]
    assert tmpConf.winGeometry == [35, 35]

    tmpConf.guiScale = 1.0
    tmpConf.setWinSize(70, 70)
    assert tmpConf.getWinSize() == [70, 70]
    assert tmpConf.winGeometry == [70, 70]

    tmpConf.setWinSize(1200, 650)

    # Preferences Size
    tmpConf.guiScale = 2.0
    tmpConf.setPreferencesSize(70, 70)
    assert tmpConf.getPreferencesSize() == [70, 70]
    assert tmpConf.prefGeometry == [35, 35]

    tmpConf.guiScale = 1.0
    tmpConf.setPreferencesSize(70, 70)
    assert tmpConf.getPreferencesSize() == [70, 70]
    assert tmpConf.prefGeometry == [70, 70]

    tmpConf.setPreferencesSize(700, 615)

    # Project Settings Tree Columns
    tmpConf.guiScale = 2.0
    tmpConf.setProjColWidths([10, 20, 30])
    assert tmpConf.getProjColWidths() == [10, 20, 30]
    assert tmpConf.projColWidth == [5, 10, 15]

    tmpConf.guiScale = 1.0
    tmpConf.setProjColWidths([10, 20, 30])
    assert tmpConf.getProjColWidths() == [10, 20, 30]
    assert tmpConf.projColWidth == [10, 20, 30]

    tmpConf.setProjColWidths([200, 60, 140])

    # Main Pane Splitter
    tmpConf.guiScale = 2.0
    tmpConf.setMainPanePos([200, 700])
    assert tmpConf.getMainPanePos() == [200, 700]
    assert tmpConf.mainPanePos == [100, 350]

    tmpConf.guiScale = 1.0
    tmpConf.setMainPanePos([200, 700])
    assert tmpConf.getMainPanePos() == [200, 700]
    assert tmpConf.mainPanePos == [200, 700]

    tmpConf.setMainPanePos([300, 800])

    # Doc Pane Splitter
    tmpConf.guiScale = 2.0
    tmpConf.setDocPanePos([300, 300])
    assert tmpConf.getDocPanePos() == [300, 300]
    assert tmpConf.docPanePos == [150, 150]

    tmpConf.guiScale = 1.0
    tmpConf.setDocPanePos([300, 300])
    assert tmpConf.getDocPanePos() == [300, 300]
    assert tmpConf.docPanePos == [300, 300]

    tmpConf.setDocPanePos([400, 400])

    # View Pane Splitter
    tmpConf.guiScale = 2.0
    tmpConf.setViewPanePos([400, 250])
    assert tmpConf.getViewPanePos() == [400, 250]
    assert tmpConf.viewPanePos == [200, 125]

    tmpConf.guiScale = 1.0
    tmpConf.setViewPanePos([400, 250])
    assert tmpConf.getViewPanePos() == [400, 250]
    assert tmpConf.viewPanePos == [400, 250]

    tmpConf.setViewPanePos([500, 150])

    # Outline Pane Splitter
    tmpConf.guiScale = 2.0
    tmpConf.setOutlinePanePos([400, 250])
    assert tmpConf.getOutlinePanePos() == [400, 250]
    assert tmpConf.outlnPanePos == [200, 125]

    tmpConf.guiScale = 1.0
    tmpConf.setOutlinePanePos([400, 250])
    assert tmpConf.getOutlinePanePos() == [400, 250]
    assert tmpConf.outlnPanePos == [400, 250]

    tmpConf.setOutlinePanePos([500, 150])

    # Getters Only
    # ============

    tmpConf.guiScale = 1.0
    assert tmpConf.getTextWidth(False) == 700
    assert tmpConf.getTextWidth(True) == 800
    assert tmpConf.getTextMargin() == 40
    assert tmpConf.getTabWidth() == 40

    tmpConf.guiScale = 2.0
    assert tmpConf.getTextWidth(False) == 1400
    assert tmpConf.getTextWidth(True) == 1600
    assert tmpConf.getTextMargin() == 80
    assert tmpConf.getTabWidth() == 80

    # Flag Setters
    # ============

    tmpConf.setShowRefPanel(False)
    assert tmpConf.showRefPanel is False
    tmpConf.setShowRefPanel(True)
    assert tmpConf.showRefPanel is True

    tmpConf.setViewComments(False)
    assert tmpConf.viewComments is False
    tmpConf.setViewComments(True)
    assert tmpConf.viewComments is True

    tmpConf.setViewSynopsis(False)
    assert tmpConf.viewSynopsis is False
    tmpConf.setViewSynopsis(True)
    assert tmpConf.viewSynopsis is True

# END Test testBaseConfig_SettersGetters


@pytest.mark.base
def testBaseConfig_Internal(monkeypatch, tmpConf):
    """Check internal functions.
    """
    # Function _packList
    assert tmpConf._packList(["A", 1, 2.0, None, False]) == "A, 1, 2.0, None, False"

    # Function _checkNone
    assert tmpConf._checkNone(None) is None
    assert tmpConf._checkNone("None") is None
    assert tmpConf._checkNone("none") is None
    assert tmpConf._checkNone("NONE") is None
    assert tmpConf._checkNone("NoNe") is None
    assert tmpConf._checkNone(123456) == 123456

    # Function _checkOptionalPackages
    # (Assumes enchant package exists and is importable)
    tmpConf._checkOptionalPackages()
    assert tmpConf.hasEnchant is True

    with monkeypatch.context() as mp:
        mp.setitem(sys.modules, "enchant", None)
        tmpConf._checkOptionalPackages()
        assert tmpConf.hasEnchant is False

# END Test testBaseConfig_Internal


@pytest.mark.base
def testBaseConfig_RecentCache(monkeypatch, fncPath):
    """Test recent cache file.
    """
    cacheFile = fncPath / nwFiles.RECENT_FILE
    recent = RecentProjects(fncPath)

    # Load when there is no file should pass, but load nothing
    assert not cacheFile.exists()
    assert recent.loadCache() is True
    assert recent.listEntries() == []

    # Add a couple of values
    pathOne = fncPath / "projPathOne" / nwFiles.PROJ_FILE
    pathTwo = fncPath / "projPathTwo" / nwFiles.PROJ_FILE

    recent.update(pathOne, "Proj One", 100, 1600002000)
    recent.update(pathTwo, "Proj Two", 200, 1600005600)
    assert recent.listEntries() == [
        (str(pathOne), "Proj One", 100, 1600002000),
        (str(pathTwo), "Proj Two", 200, 1600005600),
    ]
    assert cacheFile.exists()
    cacheFile.unlink()
    assert not cacheFile.exists()

    # Fail to Save
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert recent.saveCache() is False
        assert not cacheFile.exists()

    # Save Proper
    assert recent.saveCache() is True
    assert cacheFile.exists()

    # Fail to Load
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert recent.loadCache() is False
        assert recent.listEntries() == []

    # Load Proper
    assert recent.loadCache() is True
    assert recent.listEntries() == [
        (str(pathOne), "Proj One", 100, 1600002000),
        (str(pathTwo), "Proj Two", 200, 1600005600),
    ]

    # Remove Non-Existent Entry
    recent.remove("stuff")
    assert recent.listEntries() == [
        (str(pathOne), "Proj One", 100, 1600002000),
        (str(pathTwo), "Proj Two", 200, 1600005600),
    ]

    # Remove Second Entry
    recent.remove(pathTwo)
    assert recent.listEntries() == [
        (str(pathOne), "Proj One", 100, 1600002000),
    ]

# END Test testBaseConfig_RecentCache
