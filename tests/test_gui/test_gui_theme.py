"""
novelWriter – GUI Theme and Icons Classes Tester
================================================

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

import sys

from pathlib import Path

import pytest

from PyQt5.QtGui import QColor, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import QApplication

from novelwriter import CONFIG, SHARED
from novelwriter.common import NWConfigParser
from novelwriter.constants import nwLabels
from novelwriter.enum import nwItemClass, nwItemLayout, nwItemType

from tests.mocked import causeOSError
from tests.tools import writeFile


@pytest.mark.gui
def testGuiTheme_Main(qtbot, nwGUI, tstPaths):
    """Test the theme class init."""
    mainTheme = SHARED.theme

    # Methods
    # =======

    mSize = mainTheme.getTextWidth("m")
    assert mSize > 0
    assert mainTheme.getTextWidth("m", mainTheme.guiFont) == mSize

    # Scan for Themes
    # ===============

    assert mainTheme._listConf({}, Path("not_a_path")) is False

    themeOne = tstPaths.cnfDir / "themes" / "themeone.conf"
    themeTwo = tstPaths.cnfDir / "themes" / "themetwo.conf"
    writeFile(themeOne, "# Stuff")
    writeFile(themeTwo, "# Stuff")

    result = {}
    assert mainTheme._listConf(result, tstPaths.cnfDir / "themes") is True
    assert result["themeone"] == themeOne
    assert result["themetwo"] == themeTwo

    # Parse Colours
    # =============

    parser = NWConfigParser()
    parser["Palette"] = {
        "colour1": "100, 150, 200",            # Valid
        "colour2": "100, 150, 200, 250",       # With alpha
        "colour3": "100, 150, 200, 250, 300",  # Too many values
        "colour4": "250, 250",                 # Missing blue
        "colour5": "-10, 127, 300",            # Invalid red and blue
        "colour6": "bob, 127, 255",            # Invalid red
    }

    # Test the parser for several valid and invalid values
    assert mainTheme._parseColour(parser, "Palette", "colour1").getRgb() == (100, 150, 200, 255)
    assert mainTheme._parseColour(parser, "Palette", "colour2").getRgb() == (100, 150, 200, 250)
    assert mainTheme._parseColour(parser, "Palette", "colour3").getRgb() == (100, 150, 200, 250)
    assert mainTheme._parseColour(parser, "Palette", "colour4").getRgb() == (250, 250, 0, 255)
    assert mainTheme._parseColour(parser, "Palette", "colour5").getRgb() == (0, 0, 0, 0)
    assert mainTheme._parseColour(parser, "Palette", "colour6").getRgb() == (0, 127, 255, 255)

    # The palette should load with the parsed values
    mainTheme._setPalette(parser, "Palette", "colour1", QPalette.ColorRole.Window)
    assert mainTheme._guiPalette.color(QPalette.ColorRole.Window).getRgb() == (100, 150, 200, 255)
    mainTheme._setPalette(parser, "Palette", "colour2", QPalette.ColorRole.Window)
    assert mainTheme._guiPalette.color(QPalette.ColorRole.Window).getRgb() == (100, 150, 200, 250)
    mainTheme._setPalette(parser, "Palette", "colour3", QPalette.ColorRole.Window)
    assert mainTheme._guiPalette.color(QPalette.ColorRole.Window).getRgb() == (100, 150, 200, 250)
    mainTheme._setPalette(parser, "Palette", "colour4", QPalette.ColorRole.Window)
    assert mainTheme._guiPalette.color(QPalette.ColorRole.Window).getRgb() == (250, 250, 0, 255)
    mainTheme._setPalette(parser, "Palette", "colour5", QPalette.ColorRole.Window)
    assert mainTheme._guiPalette.color(QPalette.ColorRole.Window).getRgb() == (0, 0, 0, 0)
    mainTheme._setPalette(parser, "Palette", "colour6", QPalette.ColorRole.Window)
    assert mainTheme._guiPalette.color(QPalette.ColorRole.Window).getRgb() == (0, 127, 255, 255)

    # Non-existing value should return default colour
    mainTheme._setPalette(parser, "Palette", "stuff", QPalette.ColorRole.Window)
    assert mainTheme._guiPalette.color(QPalette.ColorRole.Window).getRgb() == (0, 0, 0, 255)

    # qtbot.stop()


@pytest.mark.gui
def testGuiTheme_Theme(qtbot, monkeypatch, nwGUI, tstPaths):
    """Test the theme part of the class."""
    mainTheme = SHARED.theme

    # List Themes
    # ===========

    # Block the reading of the files
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert mainTheme.listThemes() == []

    # Load the theme info, default themes first
    themesList = mainTheme.listThemes()
    assert themesList[0] == ("default_dark", "Default Dark Theme")
    assert themesList[1] == ("default_light", "Default Light Theme")
    assert themesList[2] == ("cyberpunk_night", "Cyberpunk Night")
    assert themesList[3] == ("dracula", "Dracula")

    # A second call should returned the cached list
    assert mainTheme.listThemes() == mainTheme._themeList

    # Check handling of broken theme settings
    CONFIG.guiTheme = "not_a_theme"
    availThemes = mainTheme._availThemes
    mainTheme._availThemes = {}
    assert mainTheme.loadTheme() is False
    mainTheme._availThemes = availThemes

    # Check handling of unreadable file
    CONFIG.guiTheme = "default"
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert mainTheme.loadTheme() is False

    # Load Default Theme
    # ==================

    if sys.platform != "win32":
        # Set a mock colour for the window background
        mainTheme._guiPalette.color(QPalette.ColorRole.Window).setRgb(0, 0, 0, 0)

        # Load the default theme
        CONFIG.guiTheme = "default"
        assert mainTheme.loadTheme() is True

        # This should load a standard palette
        wCol = QApplication.style().standardPalette().color(QPalette.ColorRole.Window).getRgb()
        assert mainTheme._guiPalette.color(QPalette.ColorRole.Window).getRgb() == wCol

    # Mock Dark Theme
    # ===============

    mockTheme: Path = tstPaths.cnfDir / "themes" / "test.conf"
    mockTheme.write_text(
        "[Main]\n"
        "name = Test\n"
        "\n"
        "[Palette]\n"
        "window = 0, 0, 0\n"
        "windowtext = 255, 255, 255\n"
        "\n"
        "[GUI]\n"
        "helptext = 0, 0, 0\n"
    )
    mainTheme._availThemes["test"] = mockTheme

    CONFIG.guiTheme = "test"
    assert mainTheme.loadTheme() is True
    assert mainTheme.isLightTheme is False
    assert mainTheme.helpText.getRgb() == (165, 165, 165, 255)

    # Load Default Light Theme
    # ========================

    CONFIG.guiTheme = "default_light"
    assert mainTheme.loadTheme() is True

    # Check a few values
    assert mainTheme._guiPalette.color(
        QPalette.ColorRole.Window).getRgb() == (239, 239, 239, 255)
    assert mainTheme._guiPalette.color(
        QPalette.ColorRole.WindowText).getRgb() == (0, 0, 0, 255)
    assert mainTheme._guiPalette.color(
        QPalette.ColorRole.Base).getRgb() == (255, 255, 255, 255)
    assert mainTheme._guiPalette.color(
        QPalette.ColorRole.AlternateBase).getRgb() == (239, 239, 239, 255)

    # Load Default Dark Theme
    # =======================

    CONFIG.guiTheme = "default_dark"
    assert mainTheme.loadTheme() is True

    # Check a few values
    assert mainTheme._guiPalette.color(
        QPalette.ColorRole.Window).getRgb()        == (54, 54, 54, 255)
    assert mainTheme._guiPalette.color(
        QPalette.ColorRole.WindowText).getRgb()    == (204, 204, 204, 255)
    assert mainTheme._guiPalette.color(
        QPalette.ColorRole.Base).getRgb()          == (62, 62, 62, 255)
    assert mainTheme._guiPalette.color(
        QPalette.ColorRole.AlternateBase).getRgb() == (78, 78, 78, 255)

    # qtbot.stop()


@pytest.mark.gui
def testGuiTheme_Syntax(qtbot, monkeypatch, nwGUI):
    """Test the syntax part of the class."""
    mainTheme = SHARED.theme

    # List Themes
    # ===========

    # Block the reading of the files
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert mainTheme.listThemes() == []

    # Load the syntax info
    syntaxList = mainTheme.listSyntax()
    assert syntaxList[0] == ("default_dark", "Default Dark")
    assert syntaxList[1] == ("default_light", "Default Light")

    # A second call should returned the cached list
    assert mainTheme.listSyntax() == mainTheme._syntaxList

    # Check handling of broken theme settings
    availSyntax = mainTheme._availSyntax
    mainTheme._availSyntax = {}
    CONFIG.guiSyntax = "not_a_syntax"
    assert mainTheme.loadSyntax() is False
    mainTheme._availSyntax = availSyntax

    # Check handling of unreadable file
    CONFIG.guiSyntax = "default_light"
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert mainTheme.loadSyntax() is False

    # Load Default Light Syntax
    # =========================

    # Load the default syntax
    CONFIG.guiSyntax = "default_light"
    assert mainTheme.loadSyntax() is True

    # Check some values
    assert mainTheme.syntaxName == "Default Light"
    assert mainTheme.colBack == QColor(255, 255, 255)
    assert mainTheme.colText == QColor(0, 0, 0)
    assert mainTheme.colLink == QColor(0, 0, 200)

    # Load Default Dark Theme
    # =======================

    # Load the default syntax
    CONFIG.guiSyntax = "default_dark"
    assert mainTheme.loadSyntax() is True

    # Check some values
    assert mainTheme.syntaxName == "Default Dark"
    assert mainTheme.colBack == QColor(42, 42, 42)
    assert mainTheme.colText == QColor(204, 204, 204)
    assert mainTheme.colLink == QColor(102, 153, 204)

    # qtbot.stop()


@pytest.mark.gui
def testGuiTheme_IconThemes(qtbot, caplog, monkeypatch, tstPaths):
    """Test the icon cache class."""
    iconCache = SHARED.theme.iconCache

    # Load Theme
    # ==========

    # Invalid theme name
    assert iconCache.loadTheme("not_a_theme") is False

    # Check handling of unreadable file
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert iconCache.loadTheme("typicons_dark") is False

    # Load a broken theme file
    iconsDir = tstPaths.cnfDir / "icons"
    testIcons = iconsDir / "testicons"
    testIcons.mkdir()
    writeFile(testIcons / "icons.conf", (
        "[Main]\n"
        "name = Test Icons\n"
        "\n"
        "[Map]\n"
        "add = add.svg\n"
        "stuff = stuff.svg\n"
    ))

    iconPath = iconCache._iconPath
    iconCache._iconPath = tstPaths.cnfDir / "icons"

    caplog.clear()
    assert iconCache.loadTheme("testicons") is True
    assert "Unknown icon name 'stuff' in config file" in caplog.text
    assert "Icon file 'add.svg' not in theme folder" in caplog.text

    iconCache._iconPath = iconPath

    # Load working theme file
    assert iconCache.loadTheme("typicons_dark") is True
    assert "add" in iconCache._themeMap

    # qtbot.stop()


@pytest.mark.gui
def testGuiTheme_LoadIcons(qtbot):
    """Test the icon cache class."""
    iconCache = SHARED.theme.iconCache
    assert iconCache.loadTheme("typicons_dark") is True

    # Load Icons
    # ==========

    # Load an unknown icon
    qIcon = iconCache.getIcon("stuff")
    assert isinstance(qIcon, QIcon)
    assert qIcon == iconCache._noIcon

    # Load an icon, it is likely already cached
    qIcon = iconCache.getIcon("add")
    assert isinstance(qIcon, QIcon)
    assert qIcon.isNull() is False

    # Load it as a pixmap with a size
    qPix = iconCache.getPixmap("add", (50, 50))
    assert isinstance(qPix, QPixmap)
    assert qPix.isNull() is False
    assert qPix.width() == 50
    assert qPix.height() == 50

    # Load app icon
    qIcon = iconCache.getIcon("novelwriter")
    assert isinstance(qIcon, QIcon)
    assert qIcon != iconCache._noIcon

    # Load mime icon
    qIcon = iconCache.getIcon("proj_nwx")
    assert isinstance(qIcon, QIcon)
    assert qIcon != iconCache._noIcon

    # Toggle icon
    qIcon = iconCache.getToggleIcon("bullet", (24, 24))
    assert isinstance(qIcon, QIcon)
    assert qIcon != iconCache._noIcon
    pOn = qIcon.pixmap(24, 24, QIcon.Mode.Normal, QIcon.State.On)
    pOff = qIcon.pixmap(24, 24, QIcon.Mode.Normal, QIcon.State.Off)
    assert pOn != pOff

    # Unknown toggle icon
    qIcon = iconCache.getToggleIcon("stuff", (24, 24))
    assert isinstance(qIcon, QIcon)
    assert qIcon == iconCache._noIcon

    # Load Item Icons
    # ===============

    # Root -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.ROOT, nwItemClass.NOVEL, nwItemLayout.NO_LAYOUT, hLevel="H0"
    ) == iconCache.getIcon(nwLabels.CLASS_ICON[nwItemClass.NOVEL])

    # Folder -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FOLDER, nwItemClass.NOVEL, nwItemLayout.NO_LAYOUT, hLevel="H0"
    ) == iconCache.getIcon("proj_folder")

    # Document H0 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.NO_LAYOUT, hLevel="H0"
    ) == iconCache.getIcon("proj_document")

    # Document H1 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H1"
    ) == iconCache.getIcon("proj_title")

    # Document H2 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H2"
    ) == iconCache.getIcon("proj_chapter")

    # Document H3 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H3"
    ) == iconCache.getIcon("proj_scene")

    # Document H4 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H4"
    ) == iconCache.getIcon("proj_section")

    # Document H5 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.NO_LAYOUT, hLevel="H4"
    ) == iconCache.getIcon("proj_document")

    # Note -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.NOTE, hLevel="H5"
    ) == iconCache.getIcon("proj_note")

    # No Type -> Null
    assert iconCache.getItemIcon(
        nwItemType.NO_TYPE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H0"
    ) == iconCache._noIcon

    # qtbot.stop()


@pytest.mark.gui
def testGuiTheme_LoadDecorations(qtbot, monkeypatch):
    """Test the icon cache class."""
    iconCache = SHARED.theme.iconCache
    assert iconCache.loadTheme("typicons_dark") is True

    # Load Decorations
    # ================

    # Invalid name should return empty pixmap
    qPix = iconCache.loadDecoration("stuff")
    assert qPix.isNull() is True

    # Load an image
    qPix = iconCache.loadDecoration("welcome")
    assert qPix.isNull() is False

    # Fail finding the file
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.is_file", lambda *a: False)
        qPix = iconCache.loadDecoration("welcome")
        assert qPix.isNull() is True

    # Test image sizes
    qPix = iconCache.loadDecoration("welcome", w=100, h=None)
    assert qPix.isNull() is False
    assert qPix.width() == 100
    assert qPix.height() > 50

    qPix = iconCache.loadDecoration("welcome", w=None, h=100)
    assert qPix.isNull() is False
    assert qPix.width() > 100
    assert qPix.height() == 100

    qPix = iconCache.loadDecoration("welcome", w=100, h=100)
    assert qPix.isNull() is False
    assert qPix.width() == 100
    assert qPix.height() == 100

    # Header Decorations
    # ==================

    assert iconCache.getHeaderDecoration(-1) == iconCache._headerDec[0]
    assert iconCache.getHeaderDecoration(0)  == iconCache._headerDec[0]
    assert iconCache.getHeaderDecoration(1)  == iconCache._headerDec[1]
    assert iconCache.getHeaderDecoration(2)  == iconCache._headerDec[2]
    assert iconCache.getHeaderDecoration(3)  == iconCache._headerDec[3]
    assert iconCache.getHeaderDecoration(4)  == iconCache._headerDec[4]
    assert iconCache.getHeaderDecoration(5)  == iconCache._headerDec[4]

    # Narrow Header Decorations
    # =========================

    assert iconCache.getHeaderDecorationNarrow(-1) == iconCache._headerDecNarrow[0]
    assert iconCache.getHeaderDecorationNarrow(0)  == iconCache._headerDecNarrow[0]
    assert iconCache.getHeaderDecorationNarrow(1)  == iconCache._headerDecNarrow[1]
    assert iconCache.getHeaderDecorationNarrow(2)  == iconCache._headerDecNarrow[2]
    assert iconCache.getHeaderDecorationNarrow(3)  == iconCache._headerDecNarrow[3]
    assert iconCache.getHeaderDecorationNarrow(4)  == iconCache._headerDecNarrow[4]
    assert iconCache.getHeaderDecorationNarrow(5)  == iconCache._headerDecNarrow[5]
    assert iconCache.getHeaderDecorationNarrow(6)  == iconCache._headerDecNarrow[5]

    # qtbot.stop()
