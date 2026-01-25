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
"""  # noqa
from __future__ import annotations

import json

from configparser import ConfigParser
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPalette, QPixmap, QStyleHints

from novelwriter import CONFIG
from novelwriter.config import DEF_GUI_DARK, DEF_GUI_LIGHT, DEF_ICONS
from novelwriter.constants import nwLabels
from novelwriter.enum import nwItemClass, nwItemLayout, nwItemType, nwTheme
from novelwriter.gui.theme import (
    STYLES_BIG_TOOLBUTTON, STYLES_FLAT_TABS, STYLES_MIN_TOOLBUTTON, GuiTheme,
    ThemeMeta, _listContent
)

from tests.mocked import causeOSError


@pytest.mark.gui
def testGuiTheme_ParseColor():
    """Test the colour parsing."""
    theme = GuiTheme()

    # Pre-Populate
    theme._qColors["red"] = QColor(255, 0, 0)
    theme._qColors["green"] = QColor(0, 255, 0)
    theme._qColors["blue"] = QColor(0, 0, 255)
    theme._qColors["grey"] = QColor(127, 127, 127)

    # By Name
    assert theme.parseColor("red").getRgb() == (255, 0, 0, 255)
    assert theme.parseColor("green").getRgb() == (0, 255, 0, 255)
    assert theme.parseColor("blue").getRgb() == (0, 0, 255, 255)
    assert theme.parseColor("bob").getRgb() == (0, 0, 0, 255)

    # CSS Format
    assert theme.parseColor("#ff0000").getRgb() == (255, 0, 0, 255)
    assert theme.parseColor("#ff00007f").getRgb() == (255, 0, 0, 127)
    assert theme.parseColor("#ff00").getRgb() == (0, 0, 0, 255)  # Too short -> ignored
    assert theme.parseColor("#ff00007f15").getRgb() == (0, 0, 0, 255)  # Too long -> ignored

    # Name + Alpha
    assert theme.parseColor("red:255").getRgb() == (255, 0, 0, 255)
    assert theme.parseColor("red:127").getRgb() == (255, 0, 0, 127)
    assert theme.parseColor("red:512").getRgb() == (255, 0, 0, 255)  # Value truncated

    # Name + Lighter
    assert theme.parseColor("grey:L100").getRgb() == (127, 127, 127, 255)
    assert theme.parseColor("grey:L150").getRgb() == (190, 190, 190, 255)
    assert theme.parseColor("grey:L50").getRgb() == (63, 63, 63, 255)

    # Name + Darker
    assert theme.parseColor("grey:D100").getRgb() == (127, 127, 127, 255)
    assert theme.parseColor("grey:D150").getRgb() == (85, 85, 85, 255)
    assert theme.parseColor("grey:D50").getRgb() == (254, 254, 254, 255)

    # Values
    assert theme.parseColor("255, 0, 0").getRgb() == (255, 0, 0, 255)
    assert theme.parseColor("255, 0, 0, 255").getRgb() == (255, 0, 0, 255)
    assert theme.parseColor("255, 0, 0, 127").getRgb() == (255, 0, 0, 127)
    assert theme.parseColor("255, 0, 0, 127, 42").getRgb() == (255, 0, 0, 127)  # Truncated


@pytest.mark.gui
def testGuiTheme_ScanThemes(monkeypatch):
    """Test the themes scanning."""
    theme = GuiTheme()

    # Load built-in themes
    files = []
    _listContent(files, CONFIG.assetPath("themes"), ".conf")
    assert len(files) > 0

    # Block reading theme files
    with monkeypatch.context() as mp:
        mp.setattr(ConfigParser, "read", causeOSError)
        theme._scanThemes(files)
        assert theme.colourThemes == {}

    # Read all themes correctly
    theme._scanThemes(files)
    assert len(theme.colourThemes) > 0

    dark = theme.colourThemes[DEF_GUI_DARK]
    light = theme.colourThemes[DEF_GUI_LIGHT]

    assert dark.name == "Default Dark Theme"
    assert dark.dark is True
    assert light.name == "Default Light Theme"
    assert light.dark is False


@pytest.mark.gui
def testGuiTheme_LoadThemes(monkeypatch):
    """Test loading themes."""
    theme = GuiTheme()
    theme.iconCache = MagicMock()
    CONFIG.lightTheme = DEF_GUI_LIGHT
    CONFIG.darkTheme = DEF_GUI_DARK

    # Load built-in themes
    files = []
    _listContent(files, CONFIG.assetPath("themes"), ".conf")
    theme._scanThemes(files)
    assert DEF_GUI_LIGHT in theme._allThemes
    assert DEF_GUI_DARK in theme._allThemes
    assert theme._currentTheme == ""

    # Load light theme
    CONFIG.themeMode = nwTheme.LIGHT
    theme.loadTheme()
    assert theme._currentTheme == DEF_GUI_LIGHT

    # Load dark theme
    CONFIG.themeMode = nwTheme.DARK
    theme.loadTheme()
    assert theme._currentTheme == DEF_GUI_DARK

    # Let auto switch back to light, then dark
    with monkeypatch.context() as mp:
        mp.setattr(CONFIG, "verQtValue", 0x060500)
        mp.setattr(QStyleHints, "colorScheme", lambda *a: Qt.ColorScheme.Light)
        CONFIG.themeMode = nwTheme.AUTO
        theme.loadTheme()
        assert theme._currentTheme == DEF_GUI_LIGHT

    with monkeypatch.context() as mp:
        mp.setattr(CONFIG, "verQtValue", 0x060500)
        mp.setattr(QStyleHints, "colorScheme", lambda *a: Qt.ColorScheme.Dark)
        CONFIG.themeMode = nwTheme.AUTO
        theme.loadTheme()
        assert theme._currentTheme == DEF_GUI_DARK

    # Error Cases
    # ===========

    # Invalid light theme
    CONFIG.lightTheme = "not_a_theme"
    CONFIG.themeMode = nwTheme.LIGHT
    theme.loadTheme()
    assert theme._currentTheme == DEF_GUI_LIGHT

    # Invalid dark theme
    CONFIG.darkTheme = "not_a_theme"
    CONFIG.themeMode = nwTheme.DARK
    theme.loadTheme()
    assert theme._currentTheme == DEF_GUI_DARK

    # Clear meta and check exit early cases
    theme._meta = ThemeMeta()
    assert theme._meta.name == ""

    # Reload dark should not load anything
    CONFIG.darkTheme = DEF_GUI_DARK
    CONFIG.themeMode = nwTheme.DARK
    theme.loadTheme()
    assert theme._meta.name == ""

    # Force reload, but fail parsing
    with monkeypatch.context() as mp:
        mp.setattr(ConfigParser, "read", causeOSError)
        CONFIG.darkTheme = DEF_GUI_DARK
        CONFIG.themeMode = nwTheme.DARK
        theme.loadTheme(force=True)
        assert theme._meta.name == ""

    # Invalid theme, and defaults are missing
    del theme._allThemes[DEF_GUI_DARK]
    del theme._allThemes[DEF_GUI_LIGHT]

    CONFIG.lightTheme = "not_a_theme"
    CONFIG.themeMode = nwTheme.LIGHT
    theme.loadTheme(force=True)
    assert theme._meta.name == ""

    CONFIG.darkTheme = "not_a_theme"
    CONFIG.themeMode = nwTheme.DARK
    theme.loadTheme(force=True)
    assert theme._meta.name == ""


@pytest.mark.gui
def testGuiTheme_SpecialColors(tstPaths):
    """Test handling special cases for colours."""
    theme = GuiTheme()
    theme.iconCache = MagicMock()

    testTheme: Path = tstPaths.cnfDir / "themes" / "test.conf"
    testTheme.write_text((
        "[Main]\n"
        "name = Test\n"
        "mode = light\n"
        "\n"
        "[Base]\n"
        "default = #cccccc\n"
        "faded   = #949494\n"
        "red     = #ff0000\n"
        "orange  = #ff7f00\n"
        "yellow  = #ffff00\n"
        "green   = #00ff00\n"
        "cyan    = #00ffff\n"
        "blue    = #0000ff\n"
        "purple  = #ff00ff\n"
        "\n"
        "[Project]\n"
        "root    = blue\n"
        "folder  = yellow\n"
        "file    = default\n"
        "title   = green\n"
        "chapter = red\n"
        "scene   = blue\n"
        "note    = yellow\n"
        "\n"
        "[Palette]\n"
        "window  = #000000\n"
        "text    = #ffffff\n"
    ), encoding="utf-8")
    theme._scanThemes([testTheme])
    assert len(theme.colourThemes) == 1
    CONFIG.themeMode = nwTheme.LIGHT
    CONFIG.lightTheme = "test"

    # Load theme
    theme.loadTheme()

    # Since window is black, a lighter version should be generated
    assert theme._guiPalette.light().color().getRgb() == (57, 57, 57, 255)

    # Reload with project override to red
    CONFIG.iconColTree = "red"
    CONFIG.iconColDocs = True
    theme.loadTheme(force=True)

    assert theme.getBaseColor("root").getRgb() == (255, 0, 0, 255)
    assert theme.getBaseColor("folder").getRgb() == (255, 0, 0, 255)
    assert theme.getBaseColor("file").getRgb() == (204, 204, 204, 255)
    assert theme.getBaseColor("title").getRgb() == (0, 255, 0, 255)
    assert theme.getBaseColor("chapter").getRgb() == (255, 0, 0, 255)
    assert theme.getBaseColor("scene").getRgb() == (0, 0, 255, 255)
    assert theme.getBaseColor("note").getRgb() == (255, 255, 0, 255)

    assert theme.getRawBaseColor("root") == b"#ff0000"
    assert theme.getRawBaseColor("folder") == b"#ff0000"
    assert theme.getRawBaseColor("file") == b"#cccccc"
    assert theme.getRawBaseColor("title") == b"#00ff00"
    assert theme.getRawBaseColor("chapter") == b"#ff0000"
    assert theme.getRawBaseColor("scene") == b"#0000ff"
    assert theme.getRawBaseColor("note") == b"#ffff00"

    # Reload with project override to purple, also for docs
    CONFIG.iconColTree = "purple"
    CONFIG.iconColDocs = False
    theme.loadTheme(force=True)

    assert theme.getBaseColor("root").getRgb() == (255, 0, 255, 255)
    assert theme.getBaseColor("folder").getRgb() == (255, 0, 255, 255)
    assert theme.getBaseColor("file").getRgb() == (255, 0, 255, 255)
    assert theme.getBaseColor("title").getRgb() == (255, 0, 255, 255)
    assert theme.getBaseColor("chapter").getRgb() == (255, 0, 255, 255)
    assert theme.getBaseColor("scene").getRgb() == (255, 0, 255, 255)
    assert theme.getBaseColor("note").getRgb() == (255, 0, 255, 255)

    assert theme.getRawBaseColor("root") == b"#ff00ff"
    assert theme.getRawBaseColor("folder") == b"#ff00ff"
    assert theme.getRawBaseColor("file") == b"#ff00ff"
    assert theme.getRawBaseColor("title") == b"#ff00ff"
    assert theme.getRawBaseColor("chapter") == b"#ff00ff"
    assert theme.getRawBaseColor("scene") == b"#ff00ff"
    assert theme.getRawBaseColor("note") == b"#ff00ff"


@pytest.mark.gui
def testGuiTheme_Methods(monkeypatch):
    """Test other themes methods."""
    theme = GuiTheme()
    theme.iconCache = MagicMock()
    CONFIG.darkTheme = DEF_GUI_DARK
    CONFIG.themeMode = nwTheme.DARK

    # Init theme
    assert theme.colourThemes == {}
    theme.initThemes()
    assert theme._meta.name == "Default Dark Theme"

    # Text width
    theme.guiFont = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
    assert theme.getTextWidth("MMMMM") > theme.getTextWidth("MMM")
    font = QFont(theme.guiFont)
    font.setPointSizeF(0.5*font.pointSizeF())
    assert theme.getTextWidth("MMMMM", font) < theme.getTextWidth("MMMMM")

    # Detect desktop mode Qt 6.5+
    with monkeypatch.context() as mp:
        mp.setattr(CONFIG, "verQtValue", 0x060500)

        mp.setattr(QStyleHints, "colorScheme", lambda *a: Qt.ColorScheme.Light)
        assert theme.isDesktopDarkMode() is False

        mp.setattr(QStyleHints, "colorScheme", lambda *a: Qt.ColorScheme.Dark)
        assert theme.isDesktopDarkMode() is True

    # Detect desktop mode Qt 6.4
    mockWhite = Mock()
    mockWhite.color.return_value = QColor(255, 255, 255)

    mockBlack = Mock()
    mockBlack.color.return_value = QColor(0, 0, 0)

    with monkeypatch.context() as mp:
        mp.setattr(CONFIG, "verQtValue", 0x060400)

        mp.setattr(QPalette, "window", lambda *a: mockWhite)
        mp.setattr(QPalette, "windowText", lambda *a: mockBlack)
        assert theme.isDesktopDarkMode() is False

        mp.setattr(QPalette, "window", lambda *a: mockBlack)
        mp.setattr(QPalette, "windowText", lambda *a: mockWhite)
        assert theme.isDesktopDarkMode() is True

    # Stylesheets
    assert theme.getStyleSheet(STYLES_FLAT_TABS) != ""
    assert theme.getStyleSheet(STYLES_MIN_TOOLBUTTON) != ""
    assert theme.getStyleSheet(STYLES_BIG_TOOLBUTTON) != ""
    assert theme.getStyleSheet("stuff") == ""


@pytest.mark.gui
def testGuiTheme_ScanIcons(monkeypatch):
    """Test the icon theme scanning."""
    theme = GuiTheme()

    # Load built-in themes
    files = []
    _listContent(files, CONFIG.assetPath("icons"), ".icons")
    assert len(files) > 0

    # Block reading theme files
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        theme.iconCache._scanThemes(files)
        assert theme.iconCache.iconThemes == {}

    # Read all themes correctly
    theme.iconCache._scanThemes(files)
    assert len(theme.iconCache.iconThemes) > 0


@pytest.mark.gui
def testGuiTheme_IconThemes(monkeypatch):
    """Test loading icon theme."""
    CONFIG.lightTheme = DEF_GUI_LIGHT
    CONFIG.themeMode = nwTheme.LIGHT
    CONFIG.iconTheme = DEF_ICONS

    theme = GuiTheme()

    # Init should load default theme
    theme.initThemes()
    assert theme.iconCache._meta.name == "Material Symbols - Rounded"
    assert DEF_ICONS in theme.iconCache.iconThemes

    # Load default theme directly
    theme.iconCache._meta = ThemeMeta()
    theme.iconCache.loadTheme("DEF_ICONS")
    assert theme.iconCache._meta.name == "Material Symbols - Rounded"

    # Failed loading should load nothing
    theme.iconCache._meta = ThemeMeta()
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        theme.iconCache.loadTheme("DEF_ICONS")
        assert theme.iconCache._meta.name == ""

    # Reload with non-existent theme should reload default
    theme.iconCache._meta = ThemeMeta()
    theme.iconCache.loadTheme("not_a_theme")
    assert theme.iconCache._meta.name == "Material Symbols - Rounded"

    # If default theme is missing, load nothing
    del theme.iconCache._allThemes[DEF_ICONS]
    theme.iconCache._meta = ThemeMeta()
    theme.iconCache.loadTheme("not_a_theme")
    assert theme.iconCache._meta.name == ""


@pytest.mark.gui
def testGuiTheme_LoadIcons():
    """Test the icon cache class."""
    theme = GuiTheme()
    theme.initThemes()
    iconCache = theme.iconCache

    # Load Icons
    # ==========

    # Load an unknown icon
    qIcon = iconCache.getIcon("stuff", "tool")
    assert isinstance(qIcon, QIcon)
    assert qIcon == iconCache._noIcon

    # Load an icon, it is likely already cached
    qIcon = iconCache.getIcon("add", "tool")
    assert isinstance(qIcon, QIcon)
    assert qIcon.isNull() is False

    # Load it as a pixmap with a size
    # If this part of the test fails, you may need to set the
    # environment variable: QT_SCALE_FACTOR=1
    qPix = iconCache.getPixmap("add", (50, 50), "tool")
    assert isinstance(qPix, QPixmap)
    assert qPix.isNull() is False
    assert qPix.width() == 50, "If this fails, make sure QT_SCALE_FACTOR=1"
    assert qPix.height() == 50, "If this fails, make sure QT_SCALE_FACTOR=1"

    # Load app icon
    qIcon = iconCache.getIcon("novelwriter", "tool")
    assert isinstance(qIcon, QIcon)
    assert qIcon != iconCache._noIcon

    # Load mime icon
    qIcon = iconCache.getIcon("proj_nwx", "tool")
    assert isinstance(qIcon, QIcon)
    assert qIcon != iconCache._noIcon

    # Toggle icon
    qIcon = iconCache.getToggleIcon("bullet", (24, 24), "tool")
    assert isinstance(qIcon, QIcon)
    assert qIcon != iconCache._noIcon
    pOn = qIcon.pixmap(24, 24, QIcon.Mode.Normal, QIcon.State.On)
    pOff = qIcon.pixmap(24, 24, QIcon.Mode.Normal, QIcon.State.Off)
    assert pOn != pOff

    # Unknown toggle icon
    qIcon = iconCache.getToggleIcon("stuff", (24, 24), "tool")
    assert isinstance(qIcon, QIcon)
    assert qIcon == iconCache._noIcon

    # Load Item Icons
    # ===============

    # Root -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.ROOT, nwItemClass.NOVEL, nwItemLayout.NO_LAYOUT, hLevel="H0"
    ) == iconCache.getIcon(nwLabels.CLASS_ICON[nwItemClass.NOVEL], "root")

    # Folder -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FOLDER, nwItemClass.NOVEL, nwItemLayout.NO_LAYOUT, hLevel="H0"
    ) == iconCache.getIcon("prj_folder", "folder")

    # Document H0 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.NO_LAYOUT, hLevel="H0"
    ) == iconCache._noIcon

    # Document H1 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H1"
    ) == iconCache.getIcon("prj_title", "title")

    # Document H2 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H2"
    ) == iconCache.getIcon("prj_chapter", "chapter")

    # Document H3 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H3"
    ) == iconCache.getIcon("prj_scene", "scene")

    # Document H4 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H4"
    ) == iconCache.getIcon("prj_document", "file")

    # Document H5 -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H5"
    ) == iconCache.getIcon("prj_document", "file")

    # Note -> Not Null
    assert iconCache.getItemIcon(
        nwItemType.FILE, nwItemClass.NOVEL, nwItemLayout.NOTE, hLevel="H5"
    ) == iconCache.getIcon("prj_note", "note")

    # No Type -> Null
    assert iconCache.getItemIcon(
        nwItemType.NO_TYPE, nwItemClass.NOVEL, nwItemLayout.DOCUMENT, hLevel="H0"
    ) == iconCache._noIcon


@pytest.mark.gui
def testGuiTheme_LoadDecorations(monkeypatch):
    """Test the icon cache class."""
    theme = GuiTheme()
    theme.initThemes()
    iconCache = theme.iconCache

    # Load Decorations
    # ================

    # Invalid name should return empty pixmap
    qPix = iconCache.getDecoration("stuff")
    assert qPix.isNull() is True

    # Load an image
    qPix = iconCache.getDecoration("welcome")
    assert qPix.isNull() is False

    # Fail finding the file
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.is_file", lambda *a: False)
        qPix = iconCache.getDecoration("welcome")
        assert qPix.isNull() is True

    # Test image sizes
    qPix = iconCache.getDecoration("welcome", w=100, h=None)
    assert qPix.isNull() is False
    assert qPix.width() == 100
    assert qPix.height() > 50

    qPix = iconCache.getDecoration("welcome", w=None, h=100)
    assert qPix.isNull() is False
    assert qPix.width() > 100
    assert qPix.height() == 100

    qPix = iconCache.getDecoration("welcome", w=100, h=100)
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


THEMES = []
_listContent(THEMES, CONFIG.assetPath("themes"), ".conf")


@pytest.mark.gui
@pytest.mark.parametrize("theme", [a.stem for a in THEMES])
def testGuiTheme_CheckTheme(theme):
    """Test loading all themes."""
    themes = GuiTheme()
    themes.iconCache = MagicMock()
    themes._scanThemes(THEMES)

    assert theme in themes.colourThemes
    current = themes.colourThemes[theme]
    if current.dark:
        CONFIG.darkTheme = theme
        CONFIG.themeMode = nwTheme.DARK
    else:
        CONFIG.lightTheme = theme
        CONFIG.themeMode = nwTheme.LIGHT

    # Check loading
    themes.loadTheme()
    assert themes._meta.name == current.name
    assert themes.isDarkTheme == current.dark

    # Check completeness
    parser = ConfigParser()
    parser.read(current.path, encoding="utf-8")

    sections = ["Main", "Base", "Project", "Icon", "Palette", "GUI", "Syntax"]
    assert sorted(parser.sections()) == sorted(sections)

    structure = {
        "Main": [
            "name", "mode", "author",  # The rest are not required
        ],
        "Base": [
            "base", "default", "faded", "red", "orange", "yellow", "green",
            "cyan", "blue", "purple",
        ],
        "Project": [
            "root", "folder", "file", "title", "chapter", "scene", "note",
            "active", "inactive", "disabled",
        ],
        "Icon": [
            "tool", "sidebar", "accept", "reject", "action", "altaction",
            "apply", "create", "destroy", "reset", "add", "change", "remove",
            "shortcode", "markdown", "systemio", "info", "warning", "error",
        ],
        "Palette": [
            "window", "windowtext", "base", "alternatebase", "text",
            "tooltipbase", "tooltiptext", "button", "buttontext", "brighttext",
            "highlight", "highlightedtext", "link", "linkvisited", "accent",
        ],
        "GUI": [
            "helptext", "fadedtext", "errortext",
        ],
        "Syntax": [
            "background", "text", "line", "link", "headertext", "headertag",
            "emphasis", "whitespace", "dialog", "altdialog", "hidden", "note",
            "shortcode", "keyword", "tag", "value", "optional",
            "spellcheckline", "errorline", "replacetag", "modifier",
            "texthighlight",
        ],
    }
    optional = ["credit", "url"]
    missing = []
    for section, options in structure.items():
        missing.extend(opt for opt in options if opt not in parser[section])
    assert missing == [], "Missing options in theme file"

    # Check deprecated
    deprecated = []
    for section in sections:
        deprecated.extend(
            opt for opt in parser[section]
            if opt not in structure[section] and opt not in optional
        )
    assert deprecated == [], "Deprecated options in theme file"


@pytest.mark.parametrize("icons", [
    pytest.param(
        a.stem,
        marks=(
            (pytest.mark.gui,)
            if a.stem.startswith("material")
            else (pytest.mark.gui, pytest.mark.opt_assets)
        ),
    ) for a in CONFIG.assetPath("icons").iterdir() if a.is_dir and a.suffix == ".icons"
])
def testGuiTheme_CheckIcons(icons, tstPaths):
    """Test loading all icons."""
    keysFile: Path = tstPaths.filesDir / "all_icons.json"
    iconKeys = json.loads(keysFile.read_text(encoding="utf-8"))
    assert isinstance(iconKeys, list)

    CONFIG.lightTheme = DEF_GUI_LIGHT
    CONFIG.themeMode = nwTheme.LIGHT

    themes = GuiTheme()
    themes.initThemes()
    iconCache = themes.iconCache

    assert icons in iconCache.iconThemes
    current = iconCache.iconThemes[icons]
    CONFIG.iconTheme = icons

    # Check loading
    themes.loadTheme(force=True)
    assert iconCache._meta.name == current.name

    # Check completeness
    missing = [key for key in iconKeys if key not in iconCache._svgData]
    assert missing == [], "Missing keys in icons file"

    # Check deprecated
    deprecated = [key for key in iconCache._svgData if key not in iconKeys]
    assert deprecated == [], "Deprecated keys in icons file"
