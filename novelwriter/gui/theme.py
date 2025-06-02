"""
novelWriter – Theme and Icons Classes
=====================================

File History:
Created: 2019-05-18 [0.1.3] GuiTheme
Created: 2019-11-08 [0.4]   GuiIcons

This file is a part of novelWriter
Copyright (C) 2019 Veronica Berglyd Olsen and novelWriter contributors

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

import logging

from configparser import ConfigParser
from math import ceil
from typing import TYPE_CHECKING, Final

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import (
    QColor, QFont, QFontDatabase, QFontMetrics, QGuiApplication, QIcon,
    QPainter, QPainterPath, QPalette, QPixmap
)
from PyQt6.QtWidgets import QApplication

from novelwriter import CONFIG
from novelwriter.common import checkInt, minmax
from novelwriter.config import DEF_GUI_DARK, DEF_GUI_LIGHT, DEF_ICONS
from novelwriter.constants import nwLabels
from novelwriter.enum import nwItemClass, nwItemLayout, nwItemType, nwTheme
from novelwriter.error import logException
from novelwriter.types import QtBlack, QtHexArgb, QtPaintAntiAlias, QtTransparent

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

T_ThemeEntry = tuple[str, str, bool]

STYLES_FLAT_TABS = "flatTabWidget"
STYLES_MIN_TOOLBUTTON = "minimalToolButton"
STYLES_BIG_TOOLBUTTON = "bigToolButton"


class ThemeMeta:

    name:        str = ""
    mode:        str = ""
    description: str = ""
    author:      str = ""
    credit:      str = ""
    url:         str = ""
    license:     str = ""
    licenseUrl:  str = ""


class SyntaxColors:

    back:   QColor = QColor(255, 255, 255)
    text:   QColor = QColor(0, 0, 0)
    link:   QColor = QColor(0, 0, 0)
    head:   QColor = QColor(0, 0, 0)
    headH:  QColor = QColor(0, 0, 0)
    emph:   QColor = QColor(0, 0, 0)
    dialN:  QColor = QColor(0, 0, 0)
    dialA:  QColor = QColor(0, 0, 0)
    hidden: QColor = QColor(0, 0, 0)
    note:   QColor = QColor(0, 0, 0)
    code:   QColor = QColor(0, 0, 0)
    key:    QColor = QColor(0, 0, 0)
    tag:    QColor = QColor(0, 0, 0)
    val:    QColor = QColor(0, 0, 0)
    opt:    QColor = QColor(0, 0, 0)
    spell:  QColor = QColor(0, 0, 0)
    error:  QColor = QColor(0, 0, 0)
    repTag: QColor = QColor(0, 0, 0)
    mod:    QColor = QColor(0, 0, 0)
    mark:   QColor = QColor(255, 255, 255, 128)


class GuiTheme:
    """Gui Theme Class

    Handles the look and feel of novelWriter.
    """

    __slots__ = (
        "_availSyntax", "_availThemes", "_darkThemes", "_guiPalette", "_lightThemes", "_qColors",
        "_styleSheets", "_svgColors", "_syntaxList", "_themeList", "baseButtonHeight",
        "baseIconHeight", "baseIconSize", "buttonIconSize", "errorText", "fadedText",
        "fontPixelSize", "fontPointSize", "getDecoration", "getHeaderDecoration",
        "getHeaderDecorationNarrow", "getIcon", "getItemIcon", "getPixmap", "getToggleIcon",
        "guiFont", "guiFontB", "guiFontBU", "guiFontFixed", "guiFontSmall", "helpText",
        "iconCache", "isDarkTheme", "syntaxMeta", "syntaxTheme", "textNHeight", "textNWidth",
        "themeMeta",
    )

    def __init__(self) -> None:

        self.iconCache = GuiIcons(self)

        # GUI Theme
        self.themeMeta   = ThemeMeta()
        self.isDarkTheme = False

        # Special Text Colours
        self.helpText  = QColor(0, 0, 0)
        self.fadedText = QColor(0, 0, 0)
        self.errorText = QColor(255, 0, 0)

        # Syntax Theme
        self.syntaxMeta = ThemeMeta()
        self.syntaxTheme = SyntaxColors()

        # Load Themes
        self._guiPalette = QPalette()
        self._themeList: list[T_ThemeEntry] = []
        self._availThemes: dict[str, Path] = {}
        self._availSyntax: dict[str, Path] = {}
        self._styleSheets: dict[str, str] = {}
        self._svgColors: dict[str, bytes] = {}
        self._qColors: dict[str, QColor] = {}

        # Icon Functions
        self.getIcon = self.iconCache.getIcon
        self.getPixmap = self.iconCache.getPixmap
        self.getItemIcon = self.iconCache.getItemIcon
        self.getToggleIcon = self.iconCache.getToggleIcon
        self.getDecoration = self.iconCache.getDecoration
        self.getHeaderDecoration = self.iconCache.getHeaderDecoration
        self.getHeaderDecorationNarrow = self.iconCache.getHeaderDecorationNarrow

        # Fonts
        self.guiFont = QApplication.font()
        self.guiFontB = QApplication.font()
        self.guiFontB.setBold(True)
        self.guiFontBU = QApplication.font()
        self.guiFontBU.setBold(True)
        self.guiFontBU.setUnderline(True)
        self.guiFontSmall = QApplication.font()
        self.guiFontSmall.setPointSizeF(0.9*self.guiFont.pointSizeF())

        qMetric = QFontMetrics(self.guiFont)
        fHeight = qMetric.height()
        fAscent = qMetric.ascent()
        self.fontPointSize = self.guiFont.pointSizeF()
        self.fontPixelSize = round(fHeight)
        self.baseIconHeight = round(fAscent)
        self.baseButtonHeight = round(1.35*fAscent)
        self.textNHeight = qMetric.boundingRect("N").height()
        self.textNWidth = qMetric.boundingRect("N").width()

        self.baseIconSize = QSize(self.baseIconHeight, self.baseIconHeight)
        self.buttonIconSize = QSize(int(0.9*self.baseIconHeight), int(0.9*self.baseIconHeight))

        # Monospace Font
        self.guiFontFixed = QFont()
        self.guiFontFixed.setPointSizeF(0.95*self.fontPointSize)
        self.guiFontFixed.setFamily(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()
        )

        logger.debug("GUI Font Family: %s", self.guiFont.family())
        logger.debug("GUI Font Point Size: %.2f", self.fontPointSize)
        logger.debug("GUI Font Pixel Size: %d", self.fontPixelSize)
        logger.debug("GUI Base Icon Height: %d", self.baseIconHeight)
        logger.debug("GUI Base Button Height: %d", self.baseButtonHeight)
        logger.debug("Text 'N' Height: %d", self.textNHeight)
        logger.debug("Text 'N' Width: %d", self.textNWidth)

        # Process Themes
        _listConf(self._availThemes, CONFIG.assetPath("themes"), ".conf")
        _listConf(self._availThemes, CONFIG.dataPath("themes"), ".conf")

        self.loadTheme()

        return

    ##
    #  Methods
    ##

    def getTextWidth(self, text: str, font: QFont | None = None) -> int:
        """Returns the width needed to contain a given piece of text in
        pixels.
        """
        if isinstance(font, QFont):
            qMetrics = QFontMetrics(font)
        else:
            qMetrics = QFontMetrics(self.guiFont)
        return ceil(qMetrics.boundingRect(text).width())

    def getBaseColor(self, name: str) -> QColor:
        """Return a base color."""
        return QColor(self._qColors.get(name) or QtBlack)

    def getRawBaseColor(self, name: str) -> bytes:
        """Return a base color."""
        return self._svgColors.get(name, self._svgColors.get("default", b"#000000"))

    ##
    #  Theme Methods
    ##

    def isDesktopDarkMode(self) -> bool:
        """Check if the desktop is in dark mode."""
        if CONFIG.verQtValue >= 0x060500 and (hint := QGuiApplication.styleHints()):
            return hint.colorScheme() == Qt.ColorScheme.Dark

        palette = QPalette()
        text = palette.color(QPalette.ColorRole.WindowText)
        window = palette.color(QPalette.ColorRole.Window)
        return text.lightnessF() > window.lightnessF()

    def parseColor(self, value: str, default: QColor = QtBlack) -> QColor:
        """Parse a string as a colour value."""
        if value in self._qColors:
            # Named colour
            return self._qColors[value]
        elif value.startswith("#"):
            if len(value) >= 9:
                # Convert from #RRGGBBAA to #AARRGGBB
                return QColor.fromString(f"#{value[7:9]}{value[1:7]}")
            else:
                # Assume #RRGGBB
                return QColor.fromString(value[:7])
        elif "," in value:
            data = value.split(",")
            entries = len(data)
            if entries == 2:
                # Assume name, alpha
                color = self._qColors.get(data[0].strip(), default)
                color.setAlpha(checkInt(data[1], 255))
                return color
            else:
                # Assume red, green, blue, alpha
                result = [0, 0, 0, 255]
                for i in range(min(entries, 4)):
                    result[i] = checkInt(data[i].strip(), result[i])
                return QColor(*result)
        return default

    def loadTheme(self) -> bool:
        """Load the currently specified GUI theme."""
        match CONFIG.themeMode:
            case nwTheme.LIGHT:
                darkMode = False
            case nwTheme.DARK:
                darkMode = True
            case _:
                darkMode = self.isDesktopDarkMode()

        theme = CONFIG.darkTheme if darkMode else CONFIG.lightTheme
        if theme not in self._availThemes:
            logger.error("Could not find GUI theme '%s'", theme)
            if darkMode:
                theme = DEF_GUI_DARK
                CONFIG.darkTheme = DEF_GUI_DARK
            else:
                theme = DEF_GUI_LIGHT
                CONFIG.lightTheme = DEF_GUI_LIGHT

        if not (file := self._availThemes.get(theme)):
            logger.error("Could not load GUI theme")
            return False

        CONFIG.splashMessage("Loading GUI theme ...")
        logger.info("Loading GUI theme '%s'", theme)
        parser = ConfigParser()
        try:
            with open(file, mode="r", encoding="utf-8") as fo:
                parser.read_file(fo)
        except Exception:
            logger.error("Could not read file: %s", file)
            logException()
            return False

        # Reset Palette
        self._resetTheme()

        # Main
        sec = "Main"
        meta = ThemeMeta()
        if parser.has_section(sec):
            meta.name        = parser.get(sec, "name", fallback="")
            meta.mode        = parser.get(sec, "mode", fallback="light")
            meta.description = parser.get(sec, "description", fallback="N/A")
            meta.author      = parser.get(sec, "author", fallback="N/A")
            meta.credit      = parser.get(sec, "credit", fallback="N/A")
            meta.url         = parser.get(sec, "url", fallback="")
            meta.license     = parser.get(sec, "license", fallback="N/A")
            meta.licenseUrl  = parser.get(sec, "licenseurl", fallback="")

        self.themeMeta = meta

        # Icons
        sec = "Base"
        if parser.has_section(sec):
            self._setBaseColor("default", self._readColor(parser, sec, "default"))
            self._setBaseColor("faded",   self._readColor(parser, sec, "faded"))
            self._setBaseColor("red",     self._readColor(parser, sec, "red"))
            self._setBaseColor("orange",  self._readColor(parser, sec, "orange"))
            self._setBaseColor("yellow",  self._readColor(parser, sec, "yellow"))
            self._setBaseColor("green",   self._readColor(parser, sec, "green"))
            self._setBaseColor("aqua",    self._readColor(parser, sec, "aqua"))
            self._setBaseColor("blue",    self._readColor(parser, sec, "blue"))
            self._setBaseColor("purple",  self._readColor(parser, sec, "purple"))

        # Project
        sec = "Project"
        if parser.has_section(sec):
            self._setBaseColor("root",    self._readColor(parser, sec, "root"))
            self._setBaseColor("folder",  self._readColor(parser, sec, "folder"))
            self._setBaseColor("file",    self._readColor(parser, sec, "file"))
            self._setBaseColor("title",   self._readColor(parser, sec, "title"))
            self._setBaseColor("chapter", self._readColor(parser, sec, "chapter"))
            self._setBaseColor("scene",   self._readColor(parser, sec, "scene"))
            self._setBaseColor("note",    self._readColor(parser, sec, "note"))

        # Palette
        sec = "Palette"
        if parser.has_section(sec):
            self._setPalette(parser, sec, "window",          QPalette.ColorRole.Window)
            self._setPalette(parser, sec, "windowtext",      QPalette.ColorRole.WindowText)
            self._setPalette(parser, sec, "base",            QPalette.ColorRole.Base)
            self._setPalette(parser, sec, "alternatebase",   QPalette.ColorRole.AlternateBase)
            self._setPalette(parser, sec, "text",            QPalette.ColorRole.Text)
            self._setPalette(parser, sec, "tooltipbase",     QPalette.ColorRole.ToolTipBase)
            self._setPalette(parser, sec, "tooltiptext",     QPalette.ColorRole.ToolTipText)
            self._setPalette(parser, sec, "button",          QPalette.ColorRole.Button)
            self._setPalette(parser, sec, "buttontext",      QPalette.ColorRole.ButtonText)
            self._setPalette(parser, sec, "brighttext",      QPalette.ColorRole.BrightText)
            self._setPalette(parser, sec, "highlight",       QPalette.ColorRole.Highlight)
            self._setPalette(parser, sec, "highlightedtext", QPalette.ColorRole.HighlightedText)
            self._setPalette(parser, sec, "link",            QPalette.ColorRole.Link)
            self._setPalette(parser, sec, "linkvisited",     QPalette.ColorRole.LinkVisited)

        # GUI
        sec = "GUI"
        if parser.has_section(sec):
            self.helpText  = self._readColor(parser, sec, "helptext")
            self.fadedText = self._readColor(parser, sec, "fadedtext")
            self.errorText = self._readColor(parser, sec, "errortext")

        # Syntax
        sec = "Syntax"
        self.syntaxTheme = SyntaxColors()
        if parser.has_section(sec):
            self.syntaxTheme.back   = self._readColor(parser, sec, "background")
            self.syntaxTheme.text   = self._readColor(parser, sec, "text")
            self.syntaxTheme.link   = self._readColor(parser, sec, "link")
            self.syntaxTheme.head   = self._readColor(parser, sec, "headertext")
            self.syntaxTheme.headH  = self._readColor(parser, sec, "headertag")
            self.syntaxTheme.emph   = self._readColor(parser, sec, "emphasis")
            self.syntaxTheme.dialN  = self._readColor(parser, sec, "dialog")
            self.syntaxTheme.dialA  = self._readColor(parser, sec, "altdialog")
            self.syntaxTheme.hidden = self._readColor(parser, sec, "hidden")
            self.syntaxTheme.note   = self._readColor(parser, sec, "note")
            self.syntaxTheme.code   = self._readColor(parser, sec, "shortcode")
            self.syntaxTheme.key    = self._readColor(parser, sec, "keyword")
            self.syntaxTheme.tag    = self._readColor(parser, sec, "tag")
            self.syntaxTheme.val    = self._readColor(parser, sec, "value")
            self.syntaxTheme.opt    = self._readColor(parser, sec, "optional")
            self.syntaxTheme.spell  = self._readColor(parser, sec, "spellcheckline")
            self.syntaxTheme.error  = self._readColor(parser, sec, "errorline")
            self.syntaxTheme.repTag = self._readColor(parser, sec, "replacetag")
            self.syntaxTheme.mod    = self._readColor(parser, sec, "modifier")
            self.syntaxTheme.mark   = self._readColor(parser, sec, "texthighlight")

        # Update Dependant Colours
        # Based on: https://github.com/qt/qtbase/blob/dev/src/gui/kernel/qplatformtheme.cpp
        text = self._guiPalette.text().color()
        window = self._guiPalette.window().color()
        highlight = self._guiPalette.highlight().color()
        isDark = text.lightnessF() > window.lightnessF()

        QtColActive = QPalette.ColorGroup.Active
        QtColInactive = QPalette.ColorGroup.Inactive
        QtColDisabled = QPalette.ColorGroup.Disabled

        if window.lightnessF() < 0.15:
            # If window is too dark, we need a lighter ref colour for shades
            ref = QColor.fromHslF(window.hueF(), window.saturationF(), 0.15, window.alphaF())
        else:
            ref = window

        light     = ref.lighter(150)
        mid       = ref.darker(130)
        midLight  = mid.lighter(110)
        dark      = ref.darker(150)
        shadow    = dark.darker(135)
        darkOff   = dark.darker(150)
        shadowOff = ref.darker(150)

        grey   = QColor(120, 120, 120) if isDark else QColor(140, 140, 140)
        dimmed = QColor(130, 130, 130) if isDark else QColor(190, 190, 190)

        placeholder = QColor(text)
        placeholder.setAlpha(128)

        self._guiPalette.setBrush(QPalette.ColorRole.Light, light)
        self._guiPalette.setBrush(QPalette.ColorRole.Mid, mid)
        self._guiPalette.setBrush(QPalette.ColorRole.Midlight, midLight)
        self._guiPalette.setBrush(QPalette.ColorRole.Dark, dark)
        self._guiPalette.setBrush(QPalette.ColorRole.Shadow, shadow)

        self._guiPalette.setBrush(QtColDisabled, QPalette.ColorRole.Text, dimmed)
        self._guiPalette.setBrush(QtColDisabled, QPalette.ColorRole.WindowText, dimmed)
        self._guiPalette.setBrush(QtColDisabled, QPalette.ColorRole.ButtonText, dimmed)
        self._guiPalette.setBrush(QtColDisabled, QPalette.ColorRole.Base, window)
        self._guiPalette.setBrush(QtColDisabled, QPalette.ColorRole.Dark, darkOff)
        self._guiPalette.setBrush(QtColDisabled, QPalette.ColorRole.Shadow, shadowOff)

        self._guiPalette.setBrush(QPalette.ColorRole.PlaceholderText, placeholder)

        self._guiPalette.setBrush(QtColActive, QPalette.ColorRole.Highlight, highlight)
        self._guiPalette.setBrush(QtColInactive, QPalette.ColorRole.Highlight, highlight)
        self._guiPalette.setBrush(QtColDisabled, QPalette.ColorRole.Highlight, grey)

        if CONFIG.verQtValue >= 0x060600:
            self._guiPalette.setBrush(QtColActive, QPalette.ColorRole.Accent, highlight)
            self._guiPalette.setBrush(QtColInactive, QPalette.ColorRole.Accent, highlight)
            self._guiPalette.setBrush(QtColDisabled, QPalette.ColorRole.Accent, grey)

        # Set project override colours
        if (override := CONFIG.iconColTree) != "theme":
            color = self._svgColors.get(override, b"#000000")
            self._svgColors["root"] = color
            self._svgColors["folder"] = color
            if not CONFIG.iconColDocs:
                self._svgColors["file"] = color
                self._svgColors["title"] = color
                self._svgColors["chapter"] = color
                self._svgColors["scene"] = color
                self._svgColors["note"] = color

        # Load icons after the theme is parsed
        self.iconCache.loadTheme(CONFIG.iconTheme)

        # Finalise
        self.isDarkTheme = isDark
        QApplication.setPalette(self._guiPalette)
        self._buildStyleSheets(self._guiPalette)

        CONFIG.splashMessage(f"Loaded GUI theme: {meta.name}")

        return True

    def listThemes(self) -> list[T_ThemeEntry]:
        """Scan the GUI themes folder and list all themes."""
        if self._themeList:
            return self._themeList

        themes: list[T_ThemeEntry] = []
        parser = ConfigParser()
        for key, path in self._availThemes.items():
            logger.debug("Checking theme config '%s'", key)
            if meta := _loadInternalName(parser, path):
                themes.append((key, meta[0], meta[1]))

        self._themeList = sorted(themes, key=_sortTheme)

        return self._themeList

    def getStyleSheet(self, name: str) -> str:
        """Load a standard style sheet."""
        return self._styleSheets.get(name, "")

    ##
    #  Internal Functions
    ##

    def _setBaseColor(self, key: str, color: QColor) -> None:
        """Set the colour for a named colour."""
        self._qColors[key] = QColor(color)
        self._svgColors[key] = color.name(QColor.NameFormat.HexRgb).encode("utf-8")
        return

    def _resetTheme(self) -> None:
        """Reset GUI colours to default values."""
        palette = QPalette()

        text = palette.color(QPalette.ColorRole.Text)
        window = palette.color(QPalette.ColorRole.Window)
        isDark = text.lightnessF() > window.lightnessF()

        # Reset GUI Palette
        faded   = QColor(128, 128, 128)
        dimmed  = QColor(130, 130, 130) if isDark else QColor(190, 190, 190)
        red     = QColor(242, 119, 122) if isDark else QColor(240, 40, 41)
        orange  = QColor(249, 145,  57) if isDark else QColor(245, 135, 31)
        yellow  = QColor(255, 204, 102) if isDark else QColor(234, 183, 0)
        green   = QColor(153, 204, 153) if isDark else QColor(113, 140, 0)
        aqua    = QColor(102, 204, 204) if isDark else QColor(62, 153, 159)
        blue    = QColor(102, 153, 204) if isDark else QColor(66, 113, 174)
        purple  = QColor(204, 153, 204) if isDark else QColor(137, 89, 168)

        # Text Colours
        self.helpText  = dimmed
        self.fadedText = faded
        self.errorText = red

        self._guiPalette = palette

        # Reset Base Colours and Icons
        self.iconCache.clear()
        self._svgColors = {}
        self._qColors = {}
        self._setBaseColor("default", text)
        self._setBaseColor("faded",   faded)
        self._setBaseColor("red",     red)
        self._setBaseColor("orange",  orange)
        self._setBaseColor("yellow",  yellow)
        self._setBaseColor("green",   green)
        self._setBaseColor("aqua",    aqua)
        self._setBaseColor("blue",    blue)
        self._setBaseColor("purple",  purple)
        self._setBaseColor("root",    blue)
        self._setBaseColor("folder",  yellow)
        self._setBaseColor("file",    text)
        self._setBaseColor("title",   green)
        self._setBaseColor("chapter", red)
        self._setBaseColor("scene",   blue)
        self._setBaseColor("note",    yellow)

        return

    def _readColor(self, parser: ConfigParser, section: str, name: str) -> QColor:
        """Parse a colour value from a config string."""
        return self.parseColor(parser.get(section, name, fallback="default"))

    def _setPalette(
        self, parser: ConfigParser, section: str, name: str, value: QPalette.ColorRole
    ) -> None:
        """Set a palette colour value from a config string."""
        self._guiPalette.setBrush(value, self._readColor(parser, section, name))
        return

    def _buildStyleSheets(self, palette: QPalette) -> None:
        """Build default style sheets."""
        self._styleSheets = {}

        text = palette.text().color()
        text.setAlpha(48)
        tCol = text.name(QtHexArgb)
        hCol = palette.highlight().color().name(QtHexArgb)

        # Flat Tab Widget and Tab Bar:
        self._styleSheets[STYLES_FLAT_TABS] = (
            "QTabWidget::pane {border: 0;} "
            "QTabWidget QTabBar::tab {border: 0; padding: 4px 8px;} "
            f"QTabWidget QTabBar::tab:selected {{color: {hCol};}} "
        )

        # Minimal Tool Button
        self._styleSheets[STYLES_MIN_TOOLBUTTON] = (
            "QToolButton {padding: 2px; margin: 0; border: none; background: transparent;} "
            f"QToolButton:hover {{border: none; background: {tCol};}} "
            "QToolButton::menu-indicator {image: none;} "
        )

        # Big Tool Button
        self._styleSheets[STYLES_BIG_TOOLBUTTON] = (
            "QToolButton {padding: 6px; margin: 0; border: none; background: transparent;} "
            f"QToolButton:hover {{border: none; background: {tCol};}} "
            "QToolButton::menu-indicator {image: none;} "
        )

        return


class GuiIcons:
    """The icon class manages the content of the assets/icons folder,
    and provides a simple interface for requesting icons.

    Icons are generated from SVG on first request, and then cached for
    further requests. If the icon is not defined, a placeholder icon is
    returned instead.
    """

    __slots__ = (
        "_availThemes", "_headerDec", "_headerDecNarrow", "_meta", "_noIcon",
        "_qIcons", "_svgData", "_theme", "_themeList",
    )

    TOGGLE_ICON_KEYS: Final[dict[str, tuple[str, str]]] = {
        "bullet": ("bullet-on", "bullet-off"),
        "unfold": ("unfold-show", "unfold-hide"),
    }
    IMAGE_MAP: Final[dict[str, tuple[str, str]]] = {
        "welcome":  ("welcome-light.jpg", "welcome-dark.jpg"),
        "nw-text":  ("novelwriter-text-light.svg", "novelwriter-text-dark.svg"),
    }

    def __init__(self, mainTheme: GuiTheme) -> None:

        self._theme = mainTheme
        self._meta = ThemeMeta()

        # Storage
        self._svgData: dict[str, bytes] = {}
        self._qIcons: dict[str, QIcon] = {}
        self._headerDec: list[QPixmap] = []
        self._headerDecNarrow: list[QPixmap] = []

        # Icon Theme Path
        self._availThemes: dict[str, Path] = {}
        self._themeList: list[tuple[str, str]] = []

        # None Icon
        self._noIcon = QIcon(str(CONFIG.assetPath("icons") / "none.svg"))

        _listConf(self._availThemes, CONFIG.assetPath("icons"), ".icons")
        _listConf(self._availThemes, CONFIG.dataPath("icons"), ".icons")

        return

    def clear(self) -> None:
        """Clear the icon cache."""
        self._svgData = {}
        self._qIcons = {}
        self._headerDec = []
        self._headerDecNarrow = []
        self._meta = ThemeMeta()
        return

    ##
    #  Actions
    ##

    def loadTheme(self, theme: str) -> bool:
        """Update the theme map. This is more of an init, since many of
        the GUI icons cannot really be replaced without writing specific
        update functions for the classes where they're used.
        """
        if theme not in self._availThemes:
            logger.error("Could not find icon theme '%s'", theme)
            theme = DEF_ICONS
            CONFIG.iconTheme = theme

        if not (file := self._availThemes.get(theme)):
            logger.error("Could not load icon theme")
            return False

        CONFIG.splashMessage("Loading icon theme ...")
        logger.info("Loading icon theme '%s'", theme)
        try:
            meta = ThemeMeta()
            with open(file, mode="r", encoding="utf-8") as icons:
                for icon in icons:
                    bits = icon.partition("=")
                    key = bits[0].strip()
                    value = bits[2].strip()
                    if key and value:
                        if key.startswith("icon:"):
                            self._svgData[key[5:]] = value.encode("utf-8")
                        elif key == "meta:name":
                            meta.name = value
                        elif key == "meta:author":
                            meta.author = value
                        elif key == "meta:license":
                            meta.license = value
            self._meta = meta
        except Exception:
            logger.error("Could not read file: %s", file)
            logException()
            return False

        CONFIG.splashMessage(f"Loaded icon theme: {meta.name}")
        CONFIG.splashMessage("Generating additional icons ...")

        # Populate generated icons cache
        self.getHeaderDecoration(0)
        self.getHeaderDecorationNarrow(0)

        return True

    ##
    #  Access Functions
    ##

    def getIcon(self, name: str, color: str | None = None, w: int = 24, h: int = 24) -> QIcon:
        """Return an icon from the icon buffer, or load it."""
        variant = f"{name}-{color}" if color else name
        if (key := f"{variant}-{w}x{h}") in self._qIcons:
            return self._qIcons[key]
        else:
            icon = self._loadIcon(name, color, w, h)
            self._qIcons[key] = icon
            logger.debug("Icon: %s", key)
            return icon

    def getToggleIcon(self, name: str, size: tuple[int, int], color: str | None = None) -> QIcon:
        """Return a toggle icon from the icon buffer, or load it."""
        if name in self.TOGGLE_ICON_KEYS:
            pOne = self.getPixmap(self.TOGGLE_ICON_KEYS[name][0], size, color)
            pTwo = self.getPixmap(self.TOGGLE_ICON_KEYS[name][1], size, color)
            icon = QIcon()
            icon.addPixmap(pOne, QIcon.Mode.Normal, QIcon.State.On)
            icon.addPixmap(pTwo, QIcon.Mode.Normal, QIcon.State.Off)
            return icon
        return self._noIcon

    def getItemIcon(
        self, tType: nwItemType, tClass: nwItemClass, tLayout: nwItemLayout, hLevel: str = "H0"
    ) -> QIcon:
        """Get the correct icon for a project item based on type, class
        and heading level
        """
        name = None
        color = "default"
        if tType == nwItemType.ROOT:
            name = nwLabels.CLASS_ICON[tClass]
            color = "root"
        elif tType == nwItemType.FOLDER:
            name = "prj_folder"
            color = "folder"
        elif tType == nwItemType.FILE:
            if tLayout == nwItemLayout.DOCUMENT:
                if hLevel == "H1":
                    name = "prj_title"
                    color = "title"
                elif hLevel == "H2":
                    name = "prj_chapter"
                    color = "chapter"
                elif hLevel == "H3":
                    name = "prj_scene"
                    color = "scene"
                else:
                    name = "prj_document"
                    color = "file"
            elif tLayout == nwItemLayout.NOTE:
                name = "prj_note"
                color = "note"
        if name is None:
            return self._noIcon

        return self.getIcon(name, color)

    def getPixmap(self, name: str, size: tuple[int, int], color: str | None = None) -> QPixmap:
        """Return an icon from the icon buffer as a QPixmap. If it
        doesn't exist, return an empty QPixmap.
        """
        w, h = size
        return self.getIcon(name, color, w, h).pixmap(w, h, QIcon.Mode.Normal)

    def getDecoration(self, name: str, w: int | None = None, h: int | None = None) -> QPixmap:
        """Load graphical decoration element based on the decoration
        map or the icon map. This function always returns a QPixmap.
        """
        if name in self.IMAGE_MAP:
            idx = int(self._theme.isDarkTheme)
            imgPath = CONFIG.assetPath("images") / self.IMAGE_MAP[name][idx]
        else:
            logger.error("Decoration with name '%s' does not exist", name)
            return QPixmap()

        if not imgPath.is_file():
            logger.error("Asset not found: %s", imgPath)
            return QPixmap()

        pixmap = QPixmap(str(imgPath))
        tMode = Qt.TransformationMode.SmoothTransformation
        if w is not None and h is not None:
            return pixmap.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, tMode)
        elif w is None and h is not None:
            return pixmap.scaledToHeight(h, tMode)
        elif w is not None and h is None:
            return pixmap.scaledToWidth(w, tMode)

        return pixmap

    def getHeaderDecoration(self, hLevel: int) -> QPixmap:
        """Get the decoration for a specific heading level."""
        if not self._headerDec:
            iPx = self._theme.baseIconHeight
            self._headerDec = [
                self._generateDecoration("file", iPx, 0),
                self._generateDecoration("title", iPx, 0),
                self._generateDecoration("chapter", iPx, 1),
                self._generateDecoration("scene", iPx, 2),
                self._generateDecoration("file", iPx, 3),
            ]
        return self._headerDec[minmax(hLevel, 0, 4)]

    def getHeaderDecorationNarrow(self, hLevel: int) -> QPixmap:
        """Get the narrow decoration for a specific heading level."""
        if not self._headerDecNarrow:
            iPx = self._theme.baseIconHeight
            self._headerDecNarrow = [
                self._generateDecoration("file", iPx, 0),
                self._generateDecoration("title", iPx, 0),
                self._generateDecoration("chapter", iPx, 0),
                self._generateDecoration("scene", iPx, 0),
                self._generateDecoration("file", iPx, 0),
                self._generateDecoration("note", iPx, 0),
            ]
        return self._headerDecNarrow[minmax(hLevel, 0, 5)]

    def listThemes(self) -> list[tuple[str, str]]:
        """Scan the GUI icons folder and list all themes."""
        if self._themeList:
            return self._themeList

        themes = []
        for key, path in self._availThemes.items():
            logger.debug("Checking icon theme '%s'", key)
            if name := _loadIconName(path):
                themes.append((key, name))

        self._themeList = sorted(themes, key=_sortTheme)

        return self._themeList

    ##
    #  Internal Functions
    ##

    def _loadIcon(self, name: str, color: str | None = None, w: int = 24, h: int = 24) -> QIcon:
        """Load an icon from the assets themes folder. This function is
        guaranteed to return a QIcon.
        """
        # If we just want the app icons, return right away
        if name == "novelwriter":
            return QIcon(str(CONFIG.assetPath("icons") / "novelwriter.svg"))
        elif name == "proj_nwx":
            return QIcon(str(CONFIG.assetPath("icons") / "x-novelwriter-project.svg"))

        if svg := self._svgData.get(name, b""):
            if fill := self._theme.getRawBaseColor(color or "default"):
                svg = svg.replace(b"#000000", fill)
            pixmap = QPixmap(w, h)
            pixmap.fill(QtTransparent)
            pixmap.loadFromData(svg, "svg")
            return QIcon(pixmap)

        # If we didn't find one, give up and return an empty icon
        logger.warning("Did not load an icon for '%s'", name)

        return self._noIcon

    def _generateDecoration(self, color: str, height: int, indent: int = 0) -> QPixmap:
        """Generate a decoration pixmap for novel headers."""
        pixmap = QPixmap(48*indent + 12, 48)
        pixmap.fill(QtTransparent)

        path = QPainterPath()
        path.addRoundedRect(48.0*indent, 2.0, 12.0, 44.0, 4.0, 4.0)

        painter = QPainter(pixmap)
        painter.setRenderHint(QtPaintAntiAlias)
        if fill := self._theme.getRawBaseColor(color or "default"):
            painter.fillPath(path, QColor(fill.decode(encoding="utf-8")))
        painter.end()

        tMode = Qt.TransformationMode.SmoothTransformation
        return pixmap.scaledToHeight(height, tMode)


# Module Functions
# ================

def _listConf(target: dict, path: Path, extension: str) -> None:
    """Scan for theme files and populate the dictionary."""
    if path.is_dir():
        for item in path.iterdir():
            if item.is_file() and item.name.endswith(extension):
                target[item.stem] = item
    return


def _sortTheme(data: tuple) -> str:
    """Key function for theme sorting."""
    key, name = data[:2]
    return f"*{name}" if key.startswith("default_") else name


def _loadInternalName(parser: ConfigParser, path: str | Path) -> tuple[str, bool]:
    """Open a conf file and read the 'name' setting."""
    try:
        parser.clear()
        with open(path, mode="r", encoding="utf-8") as inFile:
            parser.read_file(inFile)
        name = parser.get("Main", "name", fallback="")
        dark = parser.get("Main", "mode", fallback="light").lower() == "dark"
        return name, dark
    except Exception:
        logger.error("Could not read file: %s", path)
        logException()
    return "", False


def _loadIconName(path: Path) -> str:
    """Open an icons file and read the name setting."""
    try:
        with open(path, mode="r", encoding="utf-8") as icons:
            for icon in icons:
                key, _, value = icon.partition("=")
                if key.strip() == "meta:name":
                    return value.strip()
    except Exception:
        logger.error("Could not read file: %s", path)
        logException()
    return ""
