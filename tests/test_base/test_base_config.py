"""
novelWriter – Config Class Tester
=================================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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
from __future__ import annotations

import json
import sys

from pathlib import Path
from shutil import copyfile

import pytest

from novelwriter import CONFIG
from novelwriter.config import Config, RecentPaths, RecentProjects
from novelwriter.constants import nwFiles
from novelwriter.core.project import NWProject

from tests.mocked import MockApp, causeOSError
from tests.tools import cmpFiles, writeFile


@pytest.mark.base
def testBaseConfig_Constructor(monkeypatch):
    """Test config constructor."""
    # Linux
    with monkeypatch.context() as mp:
        mp.setattr("sys.platform", "linux")
        tstConf = Config()
        assert tstConf.osLinux is True
        assert tstConf.osDarwin is False
        assert tstConf.osWindows is False
        assert tstConf.osUnknown is False

    # MacOS
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


@pytest.mark.base
def testBaseConfig_InitLoadSave(monkeypatch, fncPath, tstPaths):
    """Test config initialisation."""
    tstConf = Config()

    confFile = fncPath / nwFiles.CONF_FILE
    testFile = tstPaths.outDir / "baseConfig_novelwriter.conf"
    compFile = tstPaths.refDir / "baseConfig_novelwriter.conf"

    # Make sure we don't have any old conf file
    if confFile.is_file():
        confFile.unlink()

    # Running init + load against a new path should write a new config file
    tstConf.initConfig(confPath=fncPath, dataPath=fncPath)
    assert tstConf._confPath == fncPath
    assert tstConf._dataPath == fncPath
    tstConf.loadConfig()
    assert confFile.exists()

    # Check that we have a default file
    copyfile(confFile, testFile)
    ignore = (
        "timestamp", "lastnotes", "localisation",
        "lastpath", "backuppath", "font", "textfont"
    )
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
    newConf.loadConfig()
    assert newConf.guiTheme == "foo"
    assert newConf.guiSyntax == "bar"

    # Test Correcting Quote Settings
    tstConf.fmtDQuoteOpen = "\""
    tstConf.fmtDQuoteClose = "\""
    tstConf.fmtSQuoteOpen = "'"
    tstConf.fmtSQuoteClose = "'"
    tstConf.doReplaceDQuote = True
    tstConf.doReplaceSQuote = True
    assert tstConf.saveConfig() is True

    assert newConf.loadConfig() is True
    assert newConf.doReplaceDQuote is False
    assert newConf.doReplaceSQuote is False


@pytest.mark.base
def testBaseConfig_Localisation(fncPath, tstPaths):
    """Test localisation."""
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
    tstConf.initLocalisation(tstApp)  # type: ignore

    # Check Lists
    languages = tstConf.listLanguages(tstConf.LANG_NW)
    assert languages == [("en_GB", "British English")]
    languages = tstConf.listLanguages(tstConf.LANG_PROJ)
    assert languages == [("en_GB", "British English")]
    languages = tstConf.listLanguages(None)  # type: ignore
    assert languages == []

    # Add Language
    copyfile(tstPaths.filesDir / "nw_en_GB.qm", i18nDir / "nw_fr.qm")
    writeFile(i18nDir / "nw_fr.ts", "")

    languages = tstConf.listLanguages(tstConf.LANG_NW)
    assert languages == [("en_GB", "British English"), ("fr", "Français")]


@pytest.mark.base
def testBaseConfig_Methods(fncPath):
    """Check class methods."""
    tstConf = Config()
    tstConf.initConfig(confPath=fncPath, dataPath=fncPath)

    # Home Path
    assert tstConf.homePath() == Path.home().absolute()

    # Data Path
    assert tstConf.dataPath() == fncPath
    assert tstConf.dataPath("stuff") == fncPath / "stuff"

    # Assets Path
    appPath = tstConf._appPath
    assert tstConf.assetPath() == appPath / "assets"
    assert tstConf.assetPath("stuff") == appPath / "assets" / "stuff"

    # Last Path
    assert tstConf.lastPath("project") == Path.home().absolute()

    tmpStuff = fncPath / "stuff"
    tmpStuff.mkdir()
    tstConf.setLastPath("project", tmpStuff)
    assert tstConf.lastPath("project") == tmpStuff

    fileStuff = tmpStuff / "more_stuff.txt"
    fileStuff.write_text("Stuff")
    tstConf.setLastPath("project", fileStuff)
    assert tstConf.lastPath("project") == tmpStuff

    fileStuff.unlink()
    tmpStuff.rmdir()
    assert tstConf.lastPath("project") == Path.home().absolute()

    # Backup Path
    assert tstConf.backupPath() == tstConf._backPath
    tstConf.setBackupPath(fncPath)
    assert tstConf.backupPath() == fncPath

    # Recent Projects
    assert isinstance(tstConf.recentProjects, RecentProjects)


@pytest.mark.base
def testBaseConfig_SettersGetters(fncPath):
    """Set various sizes and positions."""
    tstConf = Config()
    tstConf.initConfig(confPath=fncPath, dataPath=fncPath)

    # GUI Scaling
    # ===========

    tstConf.guiScale = 1.0
    assert tstConf.pxInt(10) == 10
    assert tstConf.pxInt(13) == 13
    assert tstConf.rpxInt(10) == 10
    assert tstConf.rpxInt(13) == 13

    tstConf.guiScale = 2.0
    assert tstConf.pxInt(10) == 20
    assert tstConf.pxInt(13) == 26
    assert tstConf.rpxInt(10) == 5
    assert tstConf.rpxInt(13) == 6

    # Setter + Getter Combos
    # ======================

    # Window Size
    tstConf.guiScale = 1.0
    tstConf.setMainWinSize(1205, 655)
    assert tstConf.mainWinSize == [1200, 650]

    tstConf.guiScale = 2.0
    tstConf.setMainWinSize(70, 70)
    assert tstConf.mainWinSize == [70, 70]
    assert tstConf._mainWinSize == [35, 35]

    tstConf.guiScale = 1.0
    tstConf.setMainWinSize(70, 70)
    assert tstConf.mainWinSize == [70, 70]
    assert tstConf._mainWinSize == [70, 70]

    tstConf.setMainWinSize(1200, 650)

    # Welcome Window Size
    tstConf.guiScale = 2.0
    tstConf.setWelcomeWinSize(70, 70)
    assert tstConf.welcomeWinSize == [70, 70]
    assert tstConf._welcomeSize == [35, 35]

    tstConf.guiScale = 1.0
    tstConf.setWelcomeWinSize(70, 70)
    assert tstConf.welcomeWinSize == [70, 70]
    assert tstConf._welcomeSize == [70, 70]

    tstConf.setWelcomeWinSize(800, 500)

    # Preferences Size
    tstConf.guiScale = 2.0
    tstConf.setPreferencesWinSize(70, 70)
    assert tstConf.preferencesWinSize == [70, 70]
    assert tstConf._prefsWinSize == [35, 35]

    tstConf.guiScale = 1.0
    tstConf.setPreferencesWinSize(70, 70)
    assert tstConf.preferencesWinSize == [70, 70]
    assert tstConf._prefsWinSize == [70, 70]

    tstConf.setPreferencesWinSize(700, 615)

    # Main Pane Splitter
    tstConf.guiScale = 2.0
    tstConf.setMainPanePos([200, 700])
    assert tstConf.mainPanePos == [200, 700]
    assert tstConf._mainPanePos == [100, 350]

    tstConf.guiScale = 1.0
    tstConf.setMainPanePos([200, 700])
    assert tstConf.mainPanePos == [200, 700]
    assert tstConf._mainPanePos == [200, 700]

    tstConf.setMainPanePos([300, 800])

    # View Pane Splitter
    tstConf.guiScale = 2.0
    tstConf.setViewPanePos([400, 250])
    assert tstConf.viewPanePos == [400, 250]
    assert tstConf._viewPanePos == [200, 125]

    tstConf.guiScale = 1.0
    tstConf.setViewPanePos([400, 250])
    assert tstConf.viewPanePos == [400, 250]
    assert tstConf._viewPanePos == [400, 250]

    tstConf.setViewPanePos([500, 150])

    # Outline Pane Splitter
    tstConf.guiScale = 2.0
    tstConf.setOutlinePanePos([400, 250])
    assert tstConf.outlinePanePos == [400, 250]
    assert tstConf._outlnPanePos == [200, 125]

    tstConf.guiScale = 1.0
    tstConf.setOutlinePanePos([400, 250])
    assert tstConf.outlinePanePos == [400, 250]
    assert tstConf._outlnPanePos == [400, 250]

    tstConf.setOutlinePanePos([500, 150])

    # Getters Only
    # ============

    tstConf.guiScale = 1.0
    assert tstConf.getTextWidth(False) == 700
    assert tstConf.getTextWidth(True) == 800
    assert tstConf.getTextMargin() == 40
    assert tstConf.getTabWidth() == 40

    tstConf.guiScale = 2.0
    assert tstConf.getTextWidth(False) == 1400
    assert tstConf.getTextWidth(True) == 1600
    assert tstConf.getTextMargin() == 80
    assert tstConf.getTabWidth() == 80


@pytest.mark.base
def testBaseConfig_Internal(monkeypatch, fncPath):
    """Check internal functions."""
    tstConf = Config()
    tstConf.initConfig(confPath=fncPath, dataPath=fncPath)

    # Function _packList
    assert tstConf._packList(["A", 1, 2.0, None, False]) == "A, 1, 2.0, None, False"

    # Function _checkOptionalPackages
    # (Assumes enchant package exists and is importable)
    tstConf._checkOptionalPackages()
    assert tstConf.hasEnchant is True

    with monkeypatch.context() as mp:
        mp.setitem(sys.modules, "enchant", None)
        tstConf._checkOptionalPackages()
        assert tstConf.hasEnchant is False


@pytest.mark.base
def testBaseConfig_RecentCache(monkeypatch, tstPaths, nwGUI):
    """Test recent cache file."""
    cacheFile = tstPaths.cnfDir / nwFiles.RECENT_FILE
    recent = RecentProjects(CONFIG)

    # Load when there is no file should pass, but load nothing
    assert not cacheFile.exists()
    assert recent.loadCache() is True
    assert recent.listEntries() == []

    # Add a couple of values
    pathOne = tstPaths.cnfDir / "projPathOne" / nwFiles.PROJ_FILE
    pathTwo = tstPaths.cnfDir / "projPathTwo" / nwFiles.PROJ_FILE

    prjOne = NWProject()
    prjTwo = NWProject()

    prjOne.data.setUuid(None)
    prjTwo.data.setUuid(None)
    prjOne.data.setName("Proj One")
    prjTwo.data.setName("Proj Two")
    prjOne.data.setCurrCounts(100, 0)
    prjTwo.data.setCurrCounts(200, 0)

    recent.update(pathOne, prjOne.data, 1600002000)
    recent.update(pathTwo, prjTwo.data, 1600005600)
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

    # Pass Invalid
    recent.update(None, None, 0)  # type: ignore
    recent.update(None, None, 0)  # type: ignore
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


@pytest.mark.base
def testBaseConfig_RecentPaths(monkeypatch, tstPaths):
    """Test recent paths file."""
    cacheFile = tstPaths.cnfDir / nwFiles.RECENT_PATH
    recent = RecentPaths(CONFIG)

    # Load when there is no file should pass, but load nothing
    assert not cacheFile.exists()
    assert recent.loadCache() is True
    assert recent._data == {}

    # Set valid paths
    recent.setPath("default", tstPaths.cnfDir / "default")
    recent.setPath("project", tstPaths.cnfDir / "project")
    recent.setPath("import", tstPaths.cnfDir / "import")
    recent.setPath("outline", tstPaths.cnfDir / "outline")
    recent.setPath("stats", tstPaths.cnfDir / "stats")

    # Set invalid path
    recent.setPath("foobar", tstPaths.cnfDir / "foobar")

    # Check valid paths
    assert recent.getPath("default") == str(tstPaths.cnfDir / "default")
    assert recent.getPath("project") == str(tstPaths.cnfDir / "project")
    assert recent.getPath("import")  == str(tstPaths.cnfDir / "import")
    assert recent.getPath("outline") == str(tstPaths.cnfDir / "outline")
    assert recent.getPath("stats")   == str(tstPaths.cnfDir / "stats")

    # Check invalid path
    assert recent.getPath("foobar") is None

    # Check file
    expected = {
        "default": str(tstPaths.cnfDir / "default"),
        "project": str(tstPaths.cnfDir / "project"),
        "import":  str(tstPaths.cnfDir / "import"),
        "outline": str(tstPaths.cnfDir / "outline"),
        "stats":   str(tstPaths.cnfDir / "stats"),
    }

    assert cacheFile.exists()
    assert json.loads(cacheFile.read_text()) == expected

    # Clear and reload
    recent._data = {}
    recent.loadCache()
    assert recent._data == expected

    # Check error handling
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert recent.saveCache() is False
        assert recent.loadCache() is False
