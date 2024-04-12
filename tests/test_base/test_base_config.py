"""
novelWriter – Config Class Tester
=================================

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

import sys
import pytest

from shutil import copyfile
from pathlib import Path

from mocked import causeOSError, MockApp
from tools import cmpFiles, writeFile

from novelwriter import CONFIG
from novelwriter.config import Config, RecentProjects
from novelwriter.constants import nwFiles


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

# END Test testBaseConfig_Constructor


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

    # Running init against a new oath should write a new config file
    tstConf.initConfig(confPath=fncPath, dataPath=fncPath)
    assert tstConf._confPath == fncPath
    assert tstConf._dataPath == fncPath
    assert confFile.exists()

    # Check that we have a default file
    copyfile(confFile, testFile)
    ignore = ("timestamp", "lastnotes", "localisation", "lastpath", "backuppath")
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

# END Test testBaseConfig_InitLoadSave


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

# END Test testBaseConfig_Localisation


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
    assert tstConf.lastPath() == Path.home().absolute()

    tmpStuff = fncPath / "stuff"
    tmpStuff.mkdir()
    tstConf.setLastPath(tmpStuff)
    assert tstConf.lastPath() == tmpStuff

    fileStuff = tmpStuff / "more_stuff.txt"
    fileStuff.write_text("Stuff")
    tstConf.setLastPath(fileStuff)
    assert tstConf.lastPath() == tmpStuff

    fileStuff.unlink()
    tmpStuff.rmdir()
    assert tstConf.lastPath() == Path.home().absolute()

    # Backup Path
    assert tstConf.backupPath() == tstConf._backPath
    tstConf.setBackupPath(fncPath)
    assert tstConf.backupPath() == fncPath

    # Recent Projects
    assert isinstance(tstConf.recentProjects, RecentProjects)

# END Test testBaseConfig_Methods


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

# END Test testBaseConfig_SettersGetters


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

# END Test testBaseConfig_Internal


@pytest.mark.base
def testBaseConfig_RecentCache(monkeypatch, tstPaths):
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
