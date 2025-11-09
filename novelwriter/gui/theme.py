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
"""  # noqa
from __future__ import annotations

import logging

from configparser import ConfigParser
from dataclasses import dataclass
from math import ceil
from typing import TYPE_CHECKING, Final

from PyQt6.QtCore import QT_TRANSLATE_NOOP, QCoreApplication, QSize, Qt
from PyQt6.QtGui import (
    QColor, QFont, QFontDatabase, QFontMetrics, QGuiApplication, QIcon,
    QPainter, QPainterPath, QPalette, QPixmap
)
from PyQt6.QtWidgets import QApplication, QWidget

from novelwriter import CONFIG
from novelwriter.common import checkInt, minmax
from novelwriter.config import DEF_GUI_DARK, DEF_GUI_LIGHT, DEF_ICONS, DEF_TREECOL
from novelwriter.constants import nwLabels
from novelwriter.enum import nwItemClass, nwItemLayout, nwItemType, nwStandardButton, nwTheme
from novelwriter.error import logException
from novelwriter.extensions.modified import NPushButton
from novelwriter.types import (
    QtBlack, QtColActive, QtColDisabled, QtColInactive, QtHexArgb,
    QtPaintAntiAlias, QtTransparent
)

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

STYLES_FLAT_TABS = "flatTabWidget"
STYLES_MIN_TOOLBUTTON = "minimalToolButton"
STYLES_BIG_TOOLBUTTON = "bigToolButton"

STANDARD_BUTTONS = {
    nwStandardButton.OK:      (QT_TRANSLATE_NOOP("Button", "OK"), "btn_ok", "action"),
    nwStandardButton.CANCEL:  (QT_TRANSLATE_NOOP("Button", "Cancel"), "btn_cancel", "reject"),
    nwStandardButton.YES:     (QT_TRANSLATE_NOOP("Button", "&Yes"), "btn_yes", "accept"),
    nwStandardButton.NO:      (QT_TRANSLATE_NOOP("Button", "&No"), "btn_no", "reject"),
    nwStandardButton.OPEN:    (QT_TRANSLATE_NOOP("Button", "Open"), "btn_open", "action"),
    nwStandardButton.CLOSE:   (QT_TRANSLATE_NOOP("Button", "Close"), "btn_close", "destroy"),
    nwStandardButton.SAVE:    (QT_TRANSLATE_NOOP("Button", "Save"), "btn_save", "action"),
    nwStandardButton.BROWSE:  (QT_TRANSLATE_NOOP("Button", "Browse"), "btn_browse", "systemio"),
    nwStandardButton.LIST:    (QT_TRANSLATE_NOOP("Button", "List"), "btn_list", "action"),
    nwStandardButton.NEW:     (QT_TRANSLATE_NOOP("Button", "New"), "btn_new", "apply"),
    nwStandardButton.CREATE:  (QT_TRANSLATE_NOOP("Button", "Create"), "btn_create", "create"),
    nwStandardButton.RESET:   (QT_TRANSLATE_NOOP("Button", "Reset"), "btn_reset", "reset"),
    nwStandardButton.INSERT:  (QT_TRANSLATE_NOOP("Button", "Insert"), "btn_insert", "action"),
    nwStandardButton.APPLY:   (QT_TRANSLATE_NOOP("Button", "Apply"), "btn_apply", "apply"),
    nwStandardButton.BUILD:   (QT_TRANSLATE_NOOP("Button", "Build"), "btn_build", "action"),
    nwStandardButton.PRINT:   (QT_TRANSLATE_NOOP("Button", "Print"), "btn_print", "action"),
    nwStandardButton.PREVIEW: (QT_TRANSLATE_NOOP("Button", "Preview"), "btn_preview", "action"),
}


@dataclass
class ThemeEntry:
    """Theme data."""

    name: str
    dark: bool
    path: Path


class ThemeMeta:
    """Theme meta data."""

    name:   str = ""
    mode:   str = ""
    author: str = ""
    credit: str = ""
    url:    str = ""


class IconsMeta:
    """Icon theme meta data."""

    name:    str = ""
    author:  str = ""
    license: str = ""


class SyntaxColors:
    """Colours for the syntax highlighter."""

    back:   QColor = QColor(255, 255, 255)
    text:   QColor = QColor(0, 0, 0)
    line:   QColor = QColor(0, 0, 0)
    link:   QColor = QColor(0, 0, 0)
    head:   QColor = QColor(0, 0, 0)
    headH:  QColor = QColor(0, 0, 0)
    emph:   QColor = QColor(0, 0, 0)
    space:  QColor = QColor(0, 0, 0)
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
    """Gui Theme Class.

    Handles the look and feel of novelWriter.
    """

    __slots__ = (
        "_allThemes", "_currentTheme", "_darkThemes", "_guiPalette", "_lightThemes", "_meta",
        "_qColors", "_styleSheets", "_svgColors", "_syntaxList", "accentCol", "baseButtonHeight",
        "baseIconHeight", "baseIconSize", "errorText", "fadedText", "fontPixelSize",
        "fontPointSize", "getDecoration", "getHeaderDecoration", "getHeaderDecorationNarrow",
        "getIcon", "getItemIcon", "getPixmap", "getStandardButton", "getToggleIcon", "guiFont",
        "guiFontB", "guiFontBU", "guiFontFixed", "guiFontSmall", "helpText", "iconCache",
        "isDarkTheme", "pushButtonIconSize", "sidebarIconSize", "syntaxTheme", "textNHeight",
        "textNWidth", "toolButtonIconSize",
    )

    def __init__(self) -> None:

        # Theme Objects
        self.iconCache   = GuiIcons(self)
        self.syntaxTheme = SyntaxColors()
        self.isDarkTheme = False

        # Special Colours
        self.helpText  = QColor(0, 0, 0)
        self.fadedText = QColor(0, 0, 0)
        self.errorText = QColor(255, 0, 0)
        self.accentCol = QColor(255, 0, 255)  # Needed until we move to Qt 6.6

        # Theme Data
        self._meta = ThemeMeta()
        self._currentTheme = ""
        self._guiPalette = QPalette()
        self._allThemes: dict[str, ThemeEntry] = {}
        self._styleSheets: dict[str, str] = {}
        self._svgColors: dict[str, bytes] = {}
        self._qColors: dict[str, QColor] = {}

        # Icon Functions
        self.getIcon = self.iconCache.getIcon
        self.getPixmap = self.iconCache.getPixmap
        self.getItemIcon = self.iconCache.getItemIcon
        self.getToggleIcon = self.iconCache.getToggleIcon
        self.getDecoration = self.iconCache.getDecoration
        self.getStandardButton = self.iconCache.getStandardButton
        self.getHeaderDecoration = self.iconCache.getHeaderDecoration
        self.getHeaderDecorationNarrow = self.iconCache.getHeaderDecorationNarrow

        # Fonts
        sSmaller = 10.0/11.0
        sLarger = 12.0/11.0
        sLarge = 15.0/11.0
        sXLarge = 19.0/11.0

        self.guiFont = QApplication.font()
        self.guiFontB = QApplication.font()
        self.guiFontB.setBold(True)
        self.guiFontBU = QApplication.font()
        self.guiFontBU.setBold(True)
        self.guiFontBU.setUnderline(True)
        self.guiFontSmall = QApplication.font()
        self.guiFontSmall.setPointSizeF(sSmaller*self.guiFont.pointSizeF())

        qMetric = QFontMetrics(self.guiFont)
        fHeight = qMetric.height()
        fAscent = qMetric.ascent()

        self.fontPointSize = self.guiFont.pointSizeF()
        self.fontPixelSize = fHeight
        self.baseIconHeight = fAscent
        self.baseButtonHeight = round(sLarge*fAscent)

        self.baseIconSize = QSize(fAscent, fAscent)
        self.sidebarIconSize = QSize(round(sXLarge*fAscent), round(sXLarge*fAscent))
        self.toolButtonIconSize = QSize(round(sSmaller*fAscent), round(sSmaller*fAscent))
        self.pushButtonIconSize = QSize(round(sLarger*fAscent), round(sLarger*fAscent))

        self.textNHeight = qMetric.boundingRect("N").height()
        self.textNWidth = qMetric.boundingRect("N").width()

        # Monospace Font
        self.guiFontFixed = QFont()
        self.guiFontFixed.setPointSizeF(sSmaller*self.fontPointSize)
        self.guiFontFixed.setFamily(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()
        )

        logger.debug("GUI Font Family: %s", self.guiFont.family())
        logger.debug("GUI Font Point Size: %.2f pt", self.fontPointSize)
        logger.debug("GUI Font Pixel Size: %d px", self.fontPixelSize)
        logger.debug("GUI Base Icon Height: %d px", self.baseIconHeight)
        logger.debug("GUI Base Button Height: %d px", self.baseButtonHeight)
        logger.debug("GUI Sidebar Icon Height: %s px", self.sidebarIconSize.height())
        logger.debug("GUI ToolButton Icon Height: %s px", self.toolButtonIconSize.height())
        logger.debug("GUI PushButton Icon Height: %s px", self.pushButtonIconSize.height())
        logger.debug("Text 'N' Height: %d px", self.textNHeight)
        logger.debug("Text 'N' Width: %d px", self.textNWidth)

    ##
    #  Properties
    ##

    @property
    def colourThemes(self) -> dict[str, ThemeEntry]:
        """Return a dictionary of all themes."""
        return self._allThemes

    ##
    #  Getters
    ##

    def getTextWidth(self, text: str, font: QFont | None = None) -> int:
        """Return the width needed to contain a given piece of text in
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
        if color := self._svgColors.get(name):
            return color
        logger.warning("No colour named '%s'", name)
        return self._svgColors.get("default", b"#000000")

    ##
    #  Theme Methods
    ##

    def initThemes(self) -> None:
        """Initialise themes."""
        CONFIG.splashMessage("Scanning for colour themes ...")
        themes: list[Path] = []
        _listContent(themes, CONFIG.assetPath("themes"), ".conf")
        _listContent(themes, CONFIG.dataPath("themes"), ".conf")
        self._scanThemes(themes)

        self.iconCache.initIcons()
        self.loadTheme()

    def isDesktopDarkMode(self) -> bool:
        """Check if the desktop is in dark mode."""
        if CONFIG.verQtValue >= 0x060500 and (hint := QGuiApplication.styleHints()):
            return hint.colorScheme() == Qt.ColorScheme.Dark

        palette = QPalette()
        text = palette.windowText().color()
        window = palette.window().color()
        return text.lightnessF() > window.lightnessF()

    def loadTheme(self, force: bool = False) -> bool:
        """Load the currently specified GUI theme. The boolean return
        can be used to determine if the GUI needs refreshing.
        """
        match CONFIG.themeMode:
            case nwTheme.LIGHT:
                darkMode = False
            case nwTheme.DARK:
                darkMode = True
            case _:
                darkMode = self.isDesktopDarkMode()

        theme = CONFIG.darkTheme if darkMode else CONFIG.lightTheme
        if theme not in self._allThemes:
            logger.error("Could not find theme '%s'", theme)
            if darkMode:
                theme = DEF_GUI_DARK
                CONFIG.darkTheme = DEF_GUI_DARK
            else:
                theme = DEF_GUI_LIGHT
                CONFIG.lightTheme = DEF_GUI_LIGHT

        if theme == self._currentTheme and not force:
            logger.info("Theme '%s' is already loaded", theme)
            return False

        entry = self._allThemes.get(theme)
        if not entry:
            logger.error("Could not load GUI theme")
            return False

        CONFIG.splashMessage(f"Loading colour theme: {entry.name}")
        logger.info("Loading GUI theme '%s'", theme)
        parser = ConfigParser()
        try:
            parser.read(entry.path, encoding="utf-8")
        except Exception:
            logger.error("Could not read file: %s", entry.path)
            logException()
            return False

        # Reset Palette
        self._resetTheme()

        # Main
        sec = "Main"
        meta = ThemeMeta()
        if parser.has_section(sec):
            meta.name   = parser.get(sec, "name", fallback="")
            meta.mode   = parser.get(sec, "mode", fallback="light")
            meta.author = parser.get(sec, "author", fallback="")
            meta.credit = parser.get(sec, "credit", fallback="")
            meta.url    = parser.get(sec, "url", fallback="")

        self._meta = meta

        # Base
        sec = "Base"
        if parser.has_section(sec):
            self._setBaseColor("base",    self._readColor(parser, sec, "base"))
            self._setBaseColor("default", self._readColor(parser, sec, "default"))
            self._setBaseColor("faded",   self._readColor(parser, sec, "faded"))
            self._setBaseColor("red",     self._readColor(parser, sec, "red"))
            self._setBaseColor("orange",  self._readColor(parser, sec, "orange"))
            self._setBaseColor("yellow",  self._readColor(parser, sec, "yellow"))
            self._setBaseColor("green",   self._readColor(parser, sec, "green"))
            self._setBaseColor("cyan",    self._readColor(parser, sec, "cyan"))
            self._setBaseColor("blue",    self._readColor(parser, sec, "blue"))
            self._setBaseColor("purple",  self._readColor(parser, sec, "purple"))

        # Project
        sec = "Project"
        if parser.has_section(sec):
            self._setBaseColor("root",     self._readColor(parser, sec, "root"))
            self._setBaseColor("folder",   self._readColor(parser, sec, "folder"))
            self._setBaseColor("file",     self._readColor(parser, sec, "file"))
            self._setBaseColor("title",    self._readColor(parser, sec, "title"))
            self._setBaseColor("chapter",  self._readColor(parser, sec, "chapter"))
            self._setBaseColor("scene",    self._readColor(parser, sec, "scene"))
            self._setBaseColor("note",     self._readColor(parser, sec, "note"))
            self._setBaseColor("active",   self._readColor(parser, sec, "active"))
            self._setBaseColor("inactive", self._readColor(parser, sec, "inactive"))
            self._setBaseColor("disabled", self._readColor(parser, sec, "disabled"))

        # Icon
        sec = "Icon"
        if parser.has_section(sec):
            self._setBaseColor("tool",      self._readColor(parser, sec, "tool"))
            self._setBaseColor("sidebar",   self._readColor(parser, sec, "sidebar"))
            self._setBaseColor("accept",    self._readColor(parser, sec, "accept"))
            self._setBaseColor("reject",    self._readColor(parser, sec, "reject"))
            self._setBaseColor("action",    self._readColor(parser, sec, "action"))
            self._setBaseColor("altaction", self._readColor(parser, sec, "altaction"))
            self._setBaseColor("apply",     self._readColor(parser, sec, "apply"))
            self._setBaseColor("create",    self._readColor(parser, sec, "create"))
            self._setBaseColor("destroy",   self._readColor(parser, sec, "destroy"))
            self._setBaseColor("reset",     self._readColor(parser, sec, "reset"))
            self._setBaseColor("add",       self._readColor(parser, sec, "add"))
            self._setBaseColor("change",    self._readColor(parser, sec, "change"))
            self._setBaseColor("remove",    self._readColor(parser, sec, "remove"))
            self._setBaseColor("shortcode", self._readColor(parser, sec, "shortcode"))
            self._setBaseColor("markdown",  self._readColor(parser, sec, "markdown"))
            self._setBaseColor("systemio",  self._readColor(parser, sec, "systemio"))
            self._setBaseColor("info",      self._readColor(parser, sec, "info"))
            self._setBaseColor("warning",   self._readColor(parser, sec, "warning"))
            self._setBaseColor("error",     self._readColor(parser, sec, "error"))

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
            self.accentCol = self._readColor(parser, sec, "accent")  # Special handling 'til Qt 6.6

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
            self.syntaxTheme.line   = self._readColor(parser, sec, "line")
            self.syntaxTheme.link   = self._readColor(parser, sec, "link")
            self.syntaxTheme.head   = self._readColor(parser, sec, "headertext")
            self.syntaxTheme.headH  = self._readColor(parser, sec, "headertag")
            self.syntaxTheme.emph   = self._readColor(parser, sec, "emphasis")
            self.syntaxTheme.space  = self._readColor(parser, sec, "whitespace")
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

        grey   = QColor(120, 120, 120) if darkMode else QColor(140, 140, 140)
        dimmed = QColor(130, 130, 130) if darkMode else QColor(190, 190, 190)

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
            self._guiPalette.setBrush(QtColActive, QPalette.ColorRole.Accent, self.accentCol)
            self._guiPalette.setBrush(QtColInactive, QPalette.ColorRole.Accent, self.accentCol)
            self._guiPalette.setBrush(QtColDisabled, QPalette.ColorRole.Accent, grey)

        # Set project override colours
        if (override := CONFIG.iconColTree) != DEF_TREECOL:
            color = self._qColors.get(override, QtBlack)
            self._setBaseColor("root", color)
            self._setBaseColor("folder", color)
            if not CONFIG.iconColDocs:
                self._setBaseColor("file", color)
                self._setBaseColor("title", color)
                self._setBaseColor("chapter", color)
                self._setBaseColor("scene", color)
                self._setBaseColor("note", color)

        self.isDarkTheme = darkMode
        self._currentTheme = theme

        # Load icons after the theme is parsed
        self.iconCache.loadTheme(CONFIG.iconTheme)

        # Finalise
        QApplication.setPalette(self._guiPalette)
        self._buildStyleSheets(self._guiPalette)

        return True

    def getStyleSheet(self, name: str) -> str:
        """Load a standard style sheet."""
        return self._styleSheets.get(name, "")

    def parseColor(self, value: str, default: QColor = QtBlack) -> QColor:
        """Parse a string as a colour value."""
        if value in self._qColors:
            # Named colour
            return self._qColors[value]
        elif value.startswith("#") and len(value) == 7:
            # Assume #RRGGBB
            return QColor.fromString(value)
        elif value.startswith("#") and len(value) == 9:
            # Assume #RRGGBBAA and convert to #AARRGGBB
            return QColor.fromString(f"#{value[7:9]}{value[1:7]}")
        elif ":" in value:
            # Colour name and lighter, darker or alpha
            name, _, adjust = value.partition(":")
            color = QColor(self._qColors.get(name.strip(), default))
            if adjust.startswith("L"):
                color = color.lighter(checkInt(adjust[1:], 100))
            elif adjust.startswith("D"):
                color = color.darker(checkInt(adjust[1:], 100))
            else:
                color.setAlpha(checkInt(adjust, 255))
            return color
        elif "," in value:
            # Integer red, green, blue, alpha
            data = value.split(",")
            result = [0, 0, 0, 255]
            for i in range(min(len(data), 4)):
                result[i] = checkInt(data[i].strip(), result[i])
            return QColor(*result)
        return default

    ##
    #  Internal Functions
    ##

    def _setBaseColor(self, key: str, color: QColor) -> None:
        """Set the colour for a named colour."""
        self._qColors[key] = QColor(color)
        self._svgColors[key] = color.name(QColor.NameFormat.HexRgb).encode("utf-8")

    def _resetTheme(self) -> None:
        """Reset GUI colours to default values."""
        palette = QPalette()
        isDark = self.isDesktopDarkMode()

        # Reset GUI Palette
        base    = palette.color(QPalette.ColorRole.Base)
        default = palette.color(QPalette.ColorRole.Text)
        faded   = QColor(128, 128, 128)
        dimmed  = QColor(130, 130, 130) if isDark else QColor(190, 190, 190)
        red     = QColor(242, 119, 122) if isDark else QColor(240, 40, 41)
        orange  = QColor(249, 145,  57) if isDark else QColor(245, 135, 31)
        yellow  = QColor(255, 204, 102) if isDark else QColor(234, 183, 0)
        green   = QColor(153, 204, 153) if isDark else QColor(113, 140, 0)
        cyan    = QColor(102, 204, 204) if isDark else QColor(62, 153, 159)
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

        # Base
        self._setBaseColor("base",     base)
        self._setBaseColor("default",  default)
        self._setBaseColor("faded",    faded)
        self._setBaseColor("red",      red)
        self._setBaseColor("orange",   orange)
        self._setBaseColor("yellow",   yellow)
        self._setBaseColor("green",    green)
        self._setBaseColor("cyan",     cyan)
        self._setBaseColor("blue",     blue)
        self._setBaseColor("purple",   purple)

        # Project
        self._setBaseColor("root",     blue)
        self._setBaseColor("folder",   yellow)
        self._setBaseColor("file",     default)
        self._setBaseColor("title",    green)
        self._setBaseColor("chapter",  red)
        self._setBaseColor("scene",    blue)
        self._setBaseColor("note",     yellow)
        self._setBaseColor("active",   green)
        self._setBaseColor("inactive", red)
        self._setBaseColor("disabled", faded)

        # Icon
        self._setBaseColor("tool",      default)
        self._setBaseColor("sidebar",   default)
        self._setBaseColor("accept",    green)
        self._setBaseColor("reject",    red)
        self._setBaseColor("action",    blue)
        self._setBaseColor("altaction", orange)
        self._setBaseColor("apply",     green)
        self._setBaseColor("create",    yellow)
        self._setBaseColor("destroy",   faded)
        self._setBaseColor("reset",     green)
        self._setBaseColor("add",       green)
        self._setBaseColor("change",    green)
        self._setBaseColor("remove",    red)
        self._setBaseColor("shortcode", default)
        self._setBaseColor("markdown",  orange)
        self._setBaseColor("systemio",  yellow)
        self._setBaseColor("info",      blue)
        self._setBaseColor("warning",   orange)
        self._setBaseColor("error",     red)

    def _readColor(self, parser: ConfigParser, section: str, name: str) -> QColor:
        """Parse a colour value from a config string."""
        return self.parseColor(parser.get(section, name, fallback="default"))

    def _setPalette(
        self, parser: ConfigParser, section: str, name: str, value: QPalette.ColorRole
    ) -> None:
        """Set a palette colour value from a config string."""
        self._guiPalette.setBrush(value, self._readColor(parser, section, name))

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

    def _scanThemes(self, files: list[Path]) -> None:
        """Scan the GUI themes folder and list all themes."""
        parser = ConfigParser()
        data: dict[str, tuple[str, str, bool, Path]] = {}
        keys = []
        for file in files:
            try:
                parser.clear()
                parser.read(file, encoding="utf-8")
                name = parser.get("Main", "name", fallback="")
                mode = parser.get("Main", "mode", fallback="").lower()
                if name and mode in ("light", "dark"):
                    key = file.stem
                    prefix = "*" if key.startswith("default") else ""
                    lookup = f"{prefix}{name} {key}"
                    keys.append(lookup)
                    data[lookup] = (file.stem, name, mode == "dark", file)
            except Exception:
                logger.error("Could not read file: %s", file)
                logException()

        self._allThemes = {}
        for lookup in sorted(keys):
            key, name, dark, item = data[lookup]
            logger.debug("Checking theme config '%s'", key)
            self._allThemes[key] = ThemeEntry(name, dark, item)


class GuiIcons:
    """The icon class manages the content of the assets/icons folder,
    and provides a simple interface for requesting icons.

    Icons are generated from SVG on first request, and then cached for
    further requests. If the icon is not defined, a placeholder icon is
    returned instead.
    """

    __slots__ = (
        "_allThemes", "_headerDec", "_headerDecNarrow", "_meta",
        "_noIcon", "_qIcons", "_svgData", "_theme",
    )

    TOGGLE_ICON_KEYS: Final[dict[str, tuple[str, str]]] = {
        "bullet": ("bullet-on", "bullet-off"),
        "unfold": ("unfold-show", "unfold-hide"),
    }
    IMAGE_MAP: Final[dict[str, tuple[str, str]]] = {
        "welcome":  ("welcome.webp", "welcome.webp"),
        "nw-text":  ("novelwriter-text-light.svg", "novelwriter-text-dark.svg"),
    }

    def __init__(self, mainTheme: GuiTheme) -> None:

        self._theme = mainTheme
        self._meta = IconsMeta()

        # Storage
        self._allThemes: dict[str, ThemeEntry] = {}
        self._svgData: dict[str, bytes] = {}
        self._qIcons: dict[str, QIcon] = {}
        self._headerDec: list[QPixmap] = []
        self._headerDecNarrow: list[QPixmap] = []

        # None Icon
        self._noIcon = QIcon(str(CONFIG.assetPath("icons") / "none.svg"))

    def clear(self) -> None:
        """Clear the icon cache."""
        self._svgData = {}
        self._qIcons = {}
        self._headerDec = []
        self._headerDecNarrow = []
        self._meta = ThemeMeta()

    ##
    #  Properties
    ##

    @property
    def iconThemes(self) -> dict[str, ThemeEntry]:
        """Return a dictionary of all icon themes."""
        return self._allThemes

    ##
    #  Actions
    ##

    def initIcons(self) -> None:
        """Initialise icons."""
        CONFIG.splashMessage("Scanning for icon themes ...")
        icons: list[Path] = []
        _listContent(icons, CONFIG.assetPath("icons"), ".icons")
        _listContent(icons, CONFIG.dataPath("icons"), ".icons")
        self._scanThemes(icons)

    def loadTheme(self, theme: str) -> None:
        """Update the theme map. This is more of an init, since many of
        the GUI icons cannot really be replaced without writing specific
        update functions for the classes where they're used.
        """
        if theme not in self._allThemes:
            logger.error("Could not find icon theme '%s'", theme)
            theme = DEF_ICONS
            CONFIG.iconTheme = theme

        entry = self._allThemes.get(theme)
        if not entry:
            logger.error("Could not load icon theme")
            return

        CONFIG.splashMessage(f"Loading icon theme: {entry.name}")
        logger.info("Loading icon theme '%s'", theme)
        try:
            meta = IconsMeta()
            with open(entry.path, mode="r", encoding="utf-8") as icons:
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
            logger.error("Could not read file: %s", entry.path)
            logException()
            return

        # Populate generated icons cache
        CONFIG.splashMessage("Generating additional icons ...")
        self.getHeaderDecoration(0)
        self.getHeaderDecorationNarrow(0)

        return

    ##
    #  Access Functions
    ##

    def getIcon(self, name: str, color: str, w: int = 24, h: int = 24) -> QIcon:
        """Return an icon from the icon buffer, or load it."""
        variant = f"{name}-{color}" if color else name
        if (key := f"{variant}-{w}x{h}") in self._qIcons:
            return self._qIcons[key]
        else:
            icon = self._loadIcon(name, color, w, h)
            self._qIcons[key] = icon
            logger.debug("Icon: %s", key)
            return icon

    def getToggleIcon(self, name: str, size: tuple[int, int], color: str) -> QIcon:
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
        and heading level.
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
        return self.getIcon(name, color or "default", w, h).pixmap(w, h, QIcon.Mode.Normal)

    def getStandardButton(self, button: nwStandardButton, parent: QWidget) -> NPushButton:
        """Return a standard button with icon and text."""
        text, icon, color = STANDARD_BUTTONS.get(button, ("", "", ""))
        return NPushButton(
            parent, QCoreApplication.translate("Button", text),
            self._theme.pushButtonIconSize, icon, color
        )

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

    def _scanThemes(self, entries: list[Path]) -> None:
        """Scan the GUI themes folder and list all themes."""
        data: dict[str, tuple[str, str, Path]] = {}
        keys = []
        for entry in entries:
            try:
                with open(entry, mode="r", encoding="utf-8") as fo:
                    for line in fo:
                        key, _, value = line.partition("=")
                        if key.strip() == "meta:name":
                            if name := value.strip():
                                lookup = entry.stem
                                keys.append(lookup)
                                data[lookup] = (lookup, name, entry)
                            break
            except Exception:
                logger.error("Could not read file: %s", entry)
                logException()

        self._allThemes = {}
        for lookup in sorted(keys):
            key, name, item = data[lookup]
            logger.debug("Checking icon theme '%s'", key)
            self._allThemes[key] = ThemeEntry(name, False, item)


# Module Functions
# ================

def _listContent(data: list[Path], path: Path, extension: str) -> None:
    """List files of a specific type and extend the list."""
    if path.is_dir():
        data.extend(n for n in path.iterdir() if n.is_file() and n.suffix == extension)
