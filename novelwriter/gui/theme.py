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

from math import ceil
from typing import TYPE_CHECKING, Final

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import (
    QColor, QFont, QFontDatabase, QFontMetrics, QIcon, QPainter, QPainterPath,
    QPalette, QPixmap
)
from PyQt6.QtWidgets import QApplication

from novelwriter import CONFIG
from novelwriter.common import NWConfigParser, minmax
from novelwriter.config import DEF_GUI, DEF_ICONS, DEF_SYNTAX
from novelwriter.constants import nwLabels
from novelwriter.enum import nwItemClass, nwItemLayout, nwItemType
from novelwriter.error import logException
from novelwriter.types import QtBlack, QtHexArgb, QtPaintAntiAlias, QtTransparent

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

STYLES_FLAT_TABS = "flatTabWidget"
STYLES_MIN_TOOLBUTTON = "minimalToolButton"
STYLES_BIG_TOOLBUTTON = "bigToolButton"


class ThemeMeta:

    name:        str = ""
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
        "_availSyntax", "_availThemes", "_guiPalette", "_styleSheets", "_syntaxList", "_themeList",
        "baseButtonHeight", "baseIconHeight", "baseIconSize", "buttonIconSize", "errorText",
        "fadedText", "fontPixelSize", "fontPointSize", "getDecoration", "getHeaderDecoration",
        "getHeaderDecorationNarrow", "getIcon", "getIconColor", "getItemIcon", "getPixmap",
        "getToggleIcon", "guiFont", "guiFontB", "guiFontBU", "guiFontFixed", "guiFontSmall",
        "helpText", "iconCache", "isDarkTheme", "syntaxMeta", "syntaxTheme", "textNHeight",
        "textNWidth", "themeMeta",
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
        self._themeList: list[tuple[str, str]] = []
        self._syntaxList: list[tuple[str, str]] = []
        self._availThemes: dict[str, Path] = {}
        self._availSyntax: dict[str, Path] = {}
        self._styleSheets: dict[str, str] = {}

        # Icon Functions
        self.getIcon = self.iconCache.getIcon
        self.getPixmap = self.iconCache.getPixmap
        self.getItemIcon = self.iconCache.getItemIcon
        self.getIconColor = self.iconCache.getIconColor
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
        _listConf(self._availSyntax, CONFIG.assetPath("syntax"), ".conf")
        _listConf(self._availThemes, CONFIG.assetPath("themes"), ".conf")
        _listConf(self._availSyntax, CONFIG.dataPath("syntax"), ".conf")
        _listConf(self._availThemes, CONFIG.dataPath("themes"), ".conf")

        self.loadTheme()
        self.loadSyntax()

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

    ##
    #  Theme Methods
    ##

    def loadTheme(self) -> bool:
        """Load the currently specified GUI theme."""
        theme = CONFIG.guiTheme
        if theme not in self._availThemes:
            logger.error("Could not find GUI theme '%s'", theme)
            theme = DEF_GUI
            CONFIG.guiTheme = theme

        if not (file := self._availThemes.get(theme)):
            logger.error("Could not load GUI theme")
            return False

        CONFIG.splashMessage("Loading GUI theme ...")
        logger.info("Loading GUI theme '%s'", theme)
        parser = NWConfigParser()
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
            meta.name        = parser.rdStr(sec, "name", "")
            meta.description = parser.rdStr(sec, "description", "N/A")
            meta.author      = parser.rdStr(sec, "author", "N/A")
            meta.credit      = parser.rdStr(sec, "credit", "N/A")
            meta.url         = parser.rdStr(sec, "url", "")
            meta.license     = parser.rdStr(sec, "license", "N/A")
            meta.licenseUrl  = parser.rdStr(sec, "licenseurl", "")

        self.themeMeta = meta

        # Icons
        sec = "Icons"
        if parser.has_section(sec):
            self.iconCache.setIconColor("default", self._parseColor(parser, sec, "default"))
            self.iconCache.setIconColor("faded",   self._parseColor(parser, sec, "faded"))
            self.iconCache.setIconColor("red",     self._parseColor(parser, sec, "red"))
            self.iconCache.setIconColor("orange",  self._parseColor(parser, sec, "orange"))
            self.iconCache.setIconColor("yellow",  self._parseColor(parser, sec, "yellow"))
            self.iconCache.setIconColor("green",   self._parseColor(parser, sec, "green"))
            self.iconCache.setIconColor("aqua",    self._parseColor(parser, sec, "aqua"))
            self.iconCache.setIconColor("blue",    self._parseColor(parser, sec, "blue"))
            self.iconCache.setIconColor("purple",  self._parseColor(parser, sec, "purple"))

        # Project
        sec = "Project"
        if parser.has_section(sec):
            self.iconCache.setIconColor("root",    self._parseColor(parser, sec, "root"))
            self.iconCache.setIconColor("folder",  self._parseColor(parser, sec, "folder"))
            self.iconCache.setIconColor("file",    self._parseColor(parser, sec, "file"))
            self.iconCache.setIconColor("title",   self._parseColor(parser, sec, "title"))
            self.iconCache.setIconColor("chapter", self._parseColor(parser, sec, "chapter"))
            self.iconCache.setIconColor("scene",   self._parseColor(parser, sec, "scene"))
            self.iconCache.setIconColor("note",    self._parseColor(parser, sec, "note"))

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
            self.helpText  = self._parseColor(parser, sec, "helptext")
            self.fadedText = self._parseColor(parser, sec, "fadedtext")
            self.errorText = self._parseColor(parser, sec, "errortext")

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

        # Load icons after the theme is parsed
        self.iconCache.loadTheme(CONFIG.iconTheme)

        # Finalise
        self.isDarkTheme = isDark
        QApplication.setPalette(self._guiPalette)
        self._buildStyleSheets(self._guiPalette)

        CONFIG.splashMessage(f"Loaded GUI theme: {meta.name}")

        return True

    def loadSyntax(self) -> bool:
        """Load the currently specified syntax highlighter theme."""
        theme = CONFIG.guiSyntax
        if theme not in self._availSyntax:
            logger.error("Could not find syntax theme '%s'", theme)
            theme = DEF_SYNTAX
            CONFIG.guiSyntax = theme

        if not (file := self._availSyntax.get(theme)):
            logger.error("Could not load syntax theme")
            return False

        CONFIG.splashMessage("Loading syntax theme ...")
        logger.info("Loading syntax theme '%s'", theme)
        parser = NWConfigParser()
        try:
            with open(file, mode="r", encoding="utf-8") as fo:
                parser.read_file(fo)
        except Exception:
            logger.error("Could not read file: %s", file)
            logException()
            return False

        # Main
        sec = "Main"
        meta = ThemeMeta()
        if parser.has_section(sec):
            meta.name        = parser.rdStr(sec, "name", "")
            meta.description = parser.rdStr(sec, "description", "N/A")
            meta.author      = parser.rdStr(sec, "author", "N/A")
            meta.credit      = parser.rdStr(sec, "credit", "N/A")
            meta.url         = parser.rdStr(sec, "url", "")
            meta.license     = parser.rdStr(sec, "license", "N/A")
            meta.licenseUrl  = parser.rdStr(sec, "licenseurl", "")

        # Syntax
        sec = "Syntax"
        syntax = SyntaxColors()
        if parser.has_section(sec):
            syntax.back   = self._parseColor(parser, sec, "background")
            syntax.text   = self._parseColor(parser, sec, "text")
            syntax.link   = self._parseColor(parser, sec, "link")
            syntax.head   = self._parseColor(parser, sec, "headertext")
            syntax.headH  = self._parseColor(parser, sec, "headertag")
            syntax.emph   = self._parseColor(parser, sec, "emphasis")
            syntax.dialN  = self._parseColor(parser, sec, "dialog")
            syntax.dialA  = self._parseColor(parser, sec, "altdialog")
            syntax.hidden = self._parseColor(parser, sec, "hidden")
            syntax.note   = self._parseColor(parser, sec, "note")
            syntax.code   = self._parseColor(parser, sec, "shortcode")
            syntax.key    = self._parseColor(parser, sec, "keyword")
            syntax.tag    = self._parseColor(parser, sec, "tag")
            syntax.val    = self._parseColor(parser, sec, "value")
            syntax.opt    = self._parseColor(parser, sec, "optional")
            syntax.spell  = self._parseColor(parser, sec, "spellcheckline")
            syntax.error  = self._parseColor(parser, sec, "errorline")
            syntax.repTag = self._parseColor(parser, sec, "replacetag")
            syntax.mod    = self._parseColor(parser, sec, "modifier")
            syntax.mark   = self._parseColor(parser, sec, "texthighlight")

        CONFIG.splashMessage(f"Loaded syntax theme: {meta.name}")

        self.syntaxMeta = meta
        self.syntaxTheme = syntax

        return True

    def listThemes(self) -> list[tuple[str, str]]:
        """Scan the GUI themes folder and list all themes."""
        if self._themeList:
            return self._themeList

        themes = []
        parser = NWConfigParser()
        for key, path in self._availThemes.items():
            logger.debug("Checking theme config '%s'", key)
            if name := _loadInternalName(parser, path):
                themes.append((key, name))

        self._themeList = sorted(themes, key=_sortTheme)

        return self._themeList

    def listSyntax(self) -> list[tuple[str, str]]:
        """Scan the syntax themes folder and list all themes."""
        if self._syntaxList:
            return self._syntaxList

        themes = []
        parser = NWConfigParser()
        for key, path in self._availSyntax.items():
            logger.debug("Checking theme syntax '%s'", key)
            if name := _loadInternalName(parser, path):
                themes.append((key, name))

        self._syntaxList = sorted(themes, key=_sortTheme)

        return self._syntaxList

    def getStyleSheet(self, name: str) -> str:
        """Load a standard style sheet."""
        return self._styleSheets.get(name, "")

    ##
    #  Internal Functions
    ##

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

        # Reset Icons
        icons = self.iconCache
        icons.clear()
        icons.setIconColor("default", text)
        icons.setIconColor("faded",   faded)
        icons.setIconColor("red",     red)
        icons.setIconColor("orange",  orange)
        icons.setIconColor("yellow",  yellow)
        icons.setIconColor("green",   green)
        icons.setIconColor("aqua",    aqua)
        icons.setIconColor("blue",    blue)
        icons.setIconColor("purple",  purple)
        icons.setIconColor("root",    blue)
        icons.setIconColor("folder",  yellow)
        icons.setIconColor("file",    text)
        icons.setIconColor("title",   green)
        icons.setIconColor("chapter", red)
        icons.setIconColor("scene",   blue)
        icons.setIconColor("note",    yellow)

        return

    def _parseColor(self, parser: NWConfigParser, section: str, name: str) -> QColor:
        """Parse a colour value from a config string."""
        return QColor(*parser.rdIntList(section, name, [0, 0, 0, 255]))

    def _setPalette(
        self, parser: NWConfigParser, section: str, name: str, value: QPalette.ColorRole
    ) -> None:
        """Set a palette colour value from a config string."""
        self._guiPalette.setBrush(value, self._parseColor(parser, section, name))
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
        "_availThemes", "_headerDec", "_headerDecNarrow", "_noIcon",
        "_qColors", "_qIcons", "_svgColors", "_svgData", "_themeList",
        "mainTheme", "themeMeta",
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

        self.mainTheme = mainTheme
        self.themeMeta = ThemeMeta()

        # Storage
        self._svgData: dict[str, bytes] = {}
        self._svgColors: dict[str, bytes] = {}
        self._qColors: dict[str, QColor] = {}
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
        self._svgColors = {}
        self._qColors = {}
        self._qIcons = {}
        self._headerDec = []
        self._headerDecNarrow = []
        self.themeMeta = ThemeMeta()
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
            self.themeMeta = meta
        except Exception:
            logger.error("Could not read file: %s", file)
            logException()
            return False

        CONFIG.splashMessage(f"Loaded icon theme: {meta.name}")
        CONFIG.splashMessage("Generating additional icons ...")

        # Set colour overrides for project item icons
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

        # Populate generated icons cache
        self.getHeaderDecoration(0)
        self.getHeaderDecorationNarrow(0)

        return True

    def setIconColor(self, key: str, color: QColor) -> None:
        """Set an icon colour for a named colour."""
        self._qColors[key] = QColor(color)
        self._svgColors[key] = color.name(QColor.NameFormat.HexRgb).encode("utf-8")
        return

    ##
    #  Access Functions
    ##

    def getIconColor(self, name: str) -> QColor:
        """Return an icon color."""
        return QColor(self._qColors.get(name) or QtBlack)

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
            idx = int(self.mainTheme.isDarkTheme)
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
            iPx = self.mainTheme.baseIconHeight
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
            iPx = self.mainTheme.baseIconHeight
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
            if fill := self._svgColors.get(color or "default"):
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
        if fill := self._svgColors.get(color or "default"):
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


def _sortTheme(data: tuple[str, str]) -> str:
    """Key function for theme sorting."""
    key, name = data
    return f"*{name}" if key.startswith("default_") else name


def _loadInternalName(parser: NWConfigParser, path: str | Path) -> str:
    """Open a conf file and read the 'name' setting."""
    try:
        with open(path, mode="r", encoding="utf-8") as inFile:
            parser.read_file(inFile)
        return parser.rdStr("Main", "name", "")
    except Exception:
        logger.error("Could not read file: %s", path)
        logException()
    return ""


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
