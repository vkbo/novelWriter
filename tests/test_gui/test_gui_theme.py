"""
novelWriter – GUI Theme and Icons Classes Tester
================================================

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

import os
import shutil
import pytest

from configparser import ConfigParser

from mock import causeOSError
from tools import writeFile

from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QMessageBox

from novelwriter.config import Config
from novelwriter.gui.theme import GuiTheme


@pytest.mark.gui
def testGuiTheme_Main(qtbot, monkeypatch, nwGUI, fncDir):
    """Test the theme class init.
    """
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)

    mainTheme: GuiTheme = nwGUI.mainTheme
    mainConf: Config = nwGUI.mainConf

    # Methods
    # =======

    mSize = mainTheme.getTextWidth("m")
    assert mSize > 0
    assert mainTheme.getTextWidth("m", mainTheme.guiFont) == mSize

    # Init Fonts
    # ==========

    # The defaults should be set
    defaultFont = mainConf.guiFont
    defaultSize = mainConf.guiFontSize

    # CHange them to nonsense values
    mainConf.guiFont = "notafont"
    mainConf.guiFontSize = 99

    # Let the theme class set them back to default
    mainTheme._setGuiFont()
    assert mainConf.guiFont == defaultFont
    assert mainConf.guiFontSize == defaultSize

    # A second call should just restore the defaults again
    mainTheme._setGuiFont()
    assert mainConf.guiFont == defaultFont
    assert mainConf.guiFontSize == defaultSize

    # Scan for Themes
    # ===============

    assert mainTheme._listConf({}, "not_a_path") is False

    themeOne = os.path.join(fncDir, "themes", "themeone.conf")
    themeTwo = os.path.join(fncDir, "themes", "themetwo.conf")
    writeFile(themeOne, "# Stuff")
    writeFile(themeTwo, "# Stuff")

    result = {}
    assert mainTheme._listConf(result, os.path.join(fncDir, "themes")) is True
    assert result["themeone"] == themeOne
    assert result["themetwo"] == themeTwo

    # Parse Colours
    # =============

    parser = ConfigParser()
    parser["Palette"] = {
        "colour1": "100, 150, 200",
        "colour2": "100, 150, 200, 250",
        "colour3": "250, 250",
        "colour4": "-10, 127, 300",
    }

    # Test the parser for several valid and invalid values
    assert mainTheme._parseColour(parser, "Palette", "colour1") == [100, 150, 200]
    assert mainTheme._parseColour(parser, "Palette", "colour2") == [100, 150, 200]
    assert mainTheme._parseColour(parser, "Palette", "colour3") == [0, 0, 0]
    assert mainTheme._parseColour(parser, "Palette", "colour4") == [0, 127, 255]
    assert mainTheme._parseColour(parser, "Palette", "colour5") == [0, 0, 0]

    # The palette should load with the parsed values
    mainTheme._setPalette(parser, "Palette", "colour1", QPalette.Window)
    assert mainTheme._guiPalette.color(QPalette.Window).getRgb() == (100, 150, 200, 255)
    mainTheme._setPalette(parser, "Palette", "colour2", QPalette.Window)
    assert mainTheme._guiPalette.color(QPalette.Window).getRgb() == (100, 150, 200, 255)
    mainTheme._setPalette(parser, "Palette", "colour3", QPalette.Window)
    assert mainTheme._guiPalette.color(QPalette.Window).getRgb() == (0, 0, 0, 255)
    mainTheme._setPalette(parser, "Palette", "colour4", QPalette.Window)
    assert mainTheme._guiPalette.color(QPalette.Window).getRgb() == (0, 127, 255, 255)
    mainTheme._setPalette(parser, "Palette", "colour5", QPalette.Window)
    assert mainTheme._guiPalette.color(QPalette.Window).getRgb() == (0, 0, 0, 255)

    # qtbot.stop()

# END Test testGuiTheme_Main


@pytest.mark.gui
def testGuiTheme_Themes(qtbot, monkeypatch, nwGUI, fncDir):
    """Test the theme class init.
    """
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)

    mainTheme: GuiTheme = nwGUI.mainTheme
    mainConf: Config = nwGUI.mainConf

    # List Themes
    # ===========

    shutil.copy(
        os.path.join(mainConf.assetPath, "themes", "default_dark.conf"),
        os.path.join(fncDir, "themes")
    )
    shutil.copy(
        os.path.join(mainConf.assetPath, "themes", "default.conf"),
        os.path.join(fncDir, "themes")
    )
    writeFile(os.path.join(fncDir, "themes", "default.qss"), "/* Stuff */")

    # Load the theme info
    themesList = mainTheme.listThemes()
    assert themesList[0] == ("default_dark", "Default Dark Theme")
    assert themesList[1] == ("default", "Default Theme")

    # A second call should returned the cached list
    assert mainTheme.listThemes() == mainTheme._themeList

    # Check handling of broken theme settings
    mainConf.guiTheme = "not_a_theme"
    assert mainTheme.loadTheme() is False

    # Check handling of unreadable file
    mainConf.guiTheme = "default"
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert mainTheme.loadTheme() is False

    # Load Default Theme
    # ==================

    # Set a mock colour for the window background
    mainTheme._guiPalette.color(QPalette.Window).setRgb(0, 0, 0, 0)

    # Load the default theme
    mainConf.guiTheme = "default"
    assert mainTheme.loadTheme() is True

    # This should load a standard palette
    wCol = QApplication.style().standardPalette().color(QPalette.Window).getRgb()
    assert mainTheme._guiPalette.color(QPalette.Window).getRgb() == wCol

    # Load Default Dark Theme
    # =======================

    mainConf.guiTheme = "default_dark"
    assert mainTheme.loadTheme() is True

    # Check a few values
    assert mainTheme._guiPalette.color(QPalette.Window).getRgb()        == (54, 54, 54, 255)
    assert mainTheme._guiPalette.color(QPalette.WindowText).getRgb()    == (174, 174, 174, 255)
    assert mainTheme._guiPalette.color(QPalette.Base).getRgb()          == (62, 62, 62, 255)
    assert mainTheme._guiPalette.color(QPalette.AlternateBase).getRgb() == (78, 78, 78, 255)

    # qtbot.stop()

# END Test testGuiTheme_Themes
