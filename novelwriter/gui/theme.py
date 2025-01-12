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
from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import (
    QColor, QFont, QFontDatabase, QFontMetrics, QIcon, QPainter, QPainterPath,
    QPalette, QPixmap
)
from PyQt6.QtWidgets import QApplication

from novelwriter import CONFIG
from novelwriter.common import NWConfigParser, cssCol, minmax
from novelwriter.constants import nwLabels
from novelwriter.enum import nwItemClass, nwItemLayout, nwItemType
from novelwriter.error import logException
from novelwriter.types import QtPaintAntiAlias, QtTransparent

logger = logging.getLogger(__name__)

STYLES_FLAT_TABS = "flatTabWidget"
STYLES_MIN_TOOLBUTTON = "minimalToolButton"
STYLES_BIG_TOOLBUTTON = "bigToolButton"


class GuiTheme:
    """Gui Theme Class

    Handles the look and feel of novelWriter.
    """

    def __init__(self) -> None:

        self.iconCache = GuiIcons(self)

        # Loaded Theme Settings
        # =====================

        # Theme
        self.themeName        = ""
        self.themeDescription = ""
        self.themeAuthor      = ""
        self.themeCredit      = ""
        self.themeUrl         = ""
        self.themeLicense     = ""
        self.themeLicenseUrl  = ""
        self.isLightTheme     = True

        # GUI
        self.statNone    = QColor(0, 0, 0)
        self.statUnsaved = QColor(0, 0, 0)
        self.statSaved   = QColor(0, 0, 0)
        self.helpText    = QColor(0, 0, 0)
        self.fadedText   = QColor(0, 0, 0)
        self.errorText   = QColor(255, 0, 0)

        # Loaded Syntax Settings
        # ======================

        # Main
        self.syntaxName        = ""
        self.syntaxDescription = ""
        self.syntaxAuthor      = ""
        self.syntaxCredit      = ""
        self.syntaxUrl         = ""
        self.syntaxLicense     = ""
        self.syntaxLicenseUrl  = ""

        # Colours
        self.colBack   = QColor(255, 255, 255)
        self.colText   = QColor(0, 0, 0)
        self.colLink   = QColor(0, 0, 0)
        self.colHead   = QColor(0, 0, 0)
        self.colHeadH  = QColor(0, 0, 0)
        self.colEmph   = QColor(0, 0, 0)
        self.colDialN  = QColor(0, 0, 0)
        self.colDialA  = QColor(0, 0, 0)
        self.colHidden = QColor(0, 0, 0)
        self.colNote   = QColor(0, 0, 0)
        self.colCode   = QColor(0, 0, 0)
        self.colKey    = QColor(0, 0, 0)
        self.colTag    = QColor(0, 0, 0)
        self.colVal    = QColor(0, 0, 0)
        self.colOpt    = QColor(0, 0, 0)
        self.colSpell  = QColor(0, 0, 0)
        self.colError  = QColor(0, 0, 0)
        self.colRepTag = QColor(0, 0, 0)
        self.colMod    = QColor(0, 0, 0)
        self.colMark   = QColor(255, 255, 255, 128)

        # Class Setup
        # ===========

        # Load Themes
        self._guiPalette = QPalette()
        self._themeList: list[tuple[str, str]] = []
        self._syntaxList: list[tuple[str, str]] = []
        self._availThemes: dict[str, Path] = {}
        self._availSyntax: dict[str, Path] = {}
        self._styleSheets: dict[str, str] = {}

        self._listConf(self._availSyntax, CONFIG.assetPath("syntax"))
        self._listConf(self._availThemes, CONFIG.assetPath("themes"))
        self._listConf(self._availSyntax, CONFIG.dataPath("syntax"))
        self._listConf(self._availThemes, CONFIG.dataPath("themes"))

        self.loadTheme()
        self.loadSyntax()

        # Icon Functions
        self.getIcon = self.iconCache.getIcon
        self.getPixmap = self.iconCache.getPixmap
        self.getItemIcon = self.iconCache.getItemIcon
        self.getToggleIcon = self.iconCache.getToggleIcon
        self.loadDecoration = self.iconCache.loadDecoration
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
        self.fontPixelSize = int(round(fHeight))
        self.baseIconHeight = int(round(fAscent))
        self.baseButtonHeight = int(round(1.35*fAscent))
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
        return int(ceil(qMetrics.boundingRect(text).width()))

    ##
    #  Theme Methods
    ##

    def loadTheme(self) -> bool:
        """Load the currently specified GUI theme."""
        guiTheme = CONFIG.guiTheme
        if guiTheme not in self._availThemes:
            logger.error("Could not find GUI theme '%s'", guiTheme)
            guiTheme = "default"
            CONFIG.guiTheme = guiTheme

        themeFile = self._availThemes.get(guiTheme, None)
        if themeFile is None:
            logger.error("Could not load GUI theme")
            return False

        # Config File
        logger.info("Loading GUI theme '%s'", guiTheme)
        parser = NWConfigParser()
        try:
            with open(themeFile, mode="r", encoding="utf-8") as inFile:
                parser.read_file(inFile)
        except Exception:
            logger.error("Could not load theme settings from: %s", themeFile)
            logException()
            return False

        # Reset Palette
        self._guiPalette = QApplication.style().standardPalette()
        self._resetGuiColors()
        self.iconCache.clear()

        # Main
        sec = "Main"
        if parser.has_section(sec):
            self.themeName        = parser.rdStr(sec, "name", "")
            self.themeDescription = parser.rdStr(sec, "description", "N/A")
            self.themeAuthor      = parser.rdStr(sec, "author", "N/A")
            self.themeCredit      = parser.rdStr(sec, "credit", "N/A")
            self.themeUrl         = parser.rdStr(sec, "url", "")
            self.themeLicense     = parser.rdStr(sec, "license", "N/A")
            self.themeLicenseUrl  = parser.rdStr(sec, "licenseurl", "")

        # Icons
        sec = "Icons"
        if parser.has_section(sec):
            self.iconCache.setIconColor("default", self._parseColour(parser, sec, "default"))
            self.iconCache.setIconColor("faded",   self._parseColour(parser, sec, "faded"))
            self.iconCache.setIconColor("red",     self._parseColour(parser, sec, "red"))
            self.iconCache.setIconColor("orange",  self._parseColour(parser, sec, "orange"))
            self.iconCache.setIconColor("yellow",  self._parseColour(parser, sec, "yellow"))
            self.iconCache.setIconColor("green",   self._parseColour(parser, sec, "green"))
            self.iconCache.setIconColor("aqua",    self._parseColour(parser, sec, "aqua"))
            self.iconCache.setIconColor("blue",    self._parseColour(parser, sec, "blue"))
            self.iconCache.setIconColor("purple",  self._parseColour(parser, sec, "purple"))

        # Project
        sec = "Project"
        if parser.has_section(sec):
            self.iconCache.setIconColor("root",    self._parseColour(parser, sec, "root"))
            self.iconCache.setIconColor("folder",  self._parseColour(parser, sec, "folder"))
            self.iconCache.setIconColor("file",    self._parseColour(parser, sec, "file"))
            self.iconCache.setIconColor("title",   self._parseColour(parser, sec, "title"))
            self.iconCache.setIconColor("chapter", self._parseColour(parser, sec, "chapter"))
            self.iconCache.setIconColor("scene",   self._parseColour(parser, sec, "scene"))
            self.iconCache.setIconColor("note",    self._parseColour(parser, sec, "note"))

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
            self.helpText    = self._parseColour(parser, sec, "helptext")
            self.fadedText   = self._parseColour(parser, sec, "fadedtext")
            self.errorText   = self._parseColour(parser, sec, "errortext")
            self.statNone    = self._parseColour(parser, sec, "statusnone")
            self.statUnsaved = self._parseColour(parser, sec, "statusunsaved")
            self.statSaved   = self._parseColour(parser, sec, "statussaved")

        # Update Dependant Colours
        backCol = self._guiPalette.window().color()
        textCol = self._guiPalette.windowText().color()

        # Calculate Based on Qt Fusion
        light    = backCol.lighter(150)
        mid      = backCol.darker(130)
        midLight = mid.lighter(110)
        dark     = backCol.darker(150)
        shadow   = dark.darker(135)

        self._guiPalette.setColor(QPalette.ColorRole.Light,    light)
        self._guiPalette.setColor(QPalette.ColorRole.Mid,      mid)
        self._guiPalette.setColor(QPalette.ColorRole.Midlight, midLight)
        self._guiPalette.setColor(QPalette.ColorRole.Dark,     dark)
        self._guiPalette.setColor(QPalette.ColorRole.Shadow,   shadow)

        # Calculate Help Text
        backLNess = backCol.lightnessF()
        textLNess = textCol.lightnessF()
        self.isLightTheme = backLNess > textLNess
        if self.helpText == QColor(0, 0, 0):
            if self.isLightTheme:
                helpLCol = textLNess + 0.35*(backLNess - textLNess)
            else:
                helpLCol = backLNess + 0.65*(textLNess - backLNess)
            self.helpText = QColor.fromHsl(0, 0, int(255*helpLCol))
            logger.debug(
                "Computed help text colour: rgb(%d, %d, %d)",
                self.helpText.red(), self.helpText.green(), self.helpText.blue()
            )

        # Load icons after theme is parsed
        self.iconCache.loadTheme(CONFIG.iconTheme)

        # Apply styles
        QApplication.setPalette(self._guiPalette)

        # Reset stylesheets so that they are regenerated
        self._buildStyleSheets(self._guiPalette)

        return True

    def loadSyntax(self) -> bool:
        """Load the currently specified syntax highlighter theme."""
        guiSyntax = CONFIG.guiSyntax
        if guiSyntax not in self._availSyntax:
            logger.error("Could not find syntax theme '%s'", guiSyntax)
            guiSyntax = "default_light"
            CONFIG.guiSyntax = guiSyntax

        syntaxFile = self._availSyntax.get(guiSyntax, None)
        if syntaxFile is None:
            logger.error("Could not load syntax theme")
            return False

        logger.info("Loading syntax theme '%s'", guiSyntax)

        confParser = NWConfigParser()
        try:
            with open(syntaxFile, mode="r", encoding="utf-8") as inFile:
                confParser.read_file(inFile)
        except Exception:
            logger.error("Could not load syntax colours from: %s", syntaxFile)
            logException()
            return False

        # Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.syntaxName        = confParser.rdStr(cnfSec, "name", "")
            self.syntaxDescription = confParser.rdStr(cnfSec, "description", "N/A")
            self.syntaxAuthor      = confParser.rdStr(cnfSec, "author", "N/A")
            self.syntaxCredit      = confParser.rdStr(cnfSec, "credit", "N/A")
            self.syntaxUrl         = confParser.rdStr(cnfSec, "url", "")
            self.syntaxLicense     = confParser.rdStr(cnfSec, "license", "N/A")
            self.syntaxLicenseUrl  = confParser.rdStr(cnfSec, "licenseurl", "")

        # Syntax
        cnfSec = "Syntax"
        if confParser.has_section(cnfSec):
            self.colBack   = self._parseColour(confParser, cnfSec, "background")
            self.colText   = self._parseColour(confParser, cnfSec, "text")
            self.colLink   = self._parseColour(confParser, cnfSec, "link")
            self.colHead   = self._parseColour(confParser, cnfSec, "headertext")
            self.colHeadH  = self._parseColour(confParser, cnfSec, "headertag")
            self.colEmph   = self._parseColour(confParser, cnfSec, "emphasis")
            self.colDialN  = self._parseColour(confParser, cnfSec, "dialog")
            self.colDialA  = self._parseColour(confParser, cnfSec, "altdialog")
            self.colHidden = self._parseColour(confParser, cnfSec, "hidden")
            self.colNote   = self._parseColour(confParser, cnfSec, "note")
            self.colCode   = self._parseColour(confParser, cnfSec, "shortcode")
            self.colKey    = self._parseColour(confParser, cnfSec, "keyword")
            self.colTag    = self._parseColour(confParser, cnfSec, "tag")
            self.colVal    = self._parseColour(confParser, cnfSec, "value")
            self.colOpt    = self._parseColour(confParser, cnfSec, "optional")
            self.colSpell  = self._parseColour(confParser, cnfSec, "spellcheckline")
            self.colError  = self._parseColour(confParser, cnfSec, "errorline")
            self.colRepTag = self._parseColour(confParser, cnfSec, "replacetag")
            self.colMod    = self._parseColour(confParser, cnfSec, "modifier")
            self.colMark   = self._parseColour(confParser, cnfSec, "texthighlight")

        return True

    def listThemes(self) -> list[tuple[str, str]]:
        """Scan the GUI themes folder and list all themes."""
        if self._themeList:
            return self._themeList

        confParser = NWConfigParser()
        for themeKey, themePath in self._availThemes.items():
            logger.debug("Checking theme config for '%s'", themeKey)
            themeName = _loadInternalName(confParser, themePath)
            if themeName:
                self._themeList.append((themeKey, themeName))

        self._themeList = sorted(self._themeList, key=_sortTheme)

        return self._themeList

    def listSyntax(self) -> list[tuple[str, str]]:
        """Scan the syntax themes folder and list all themes."""
        if self._syntaxList:
            return self._syntaxList

        confParser = NWConfigParser()
        for syntaxKey, syntaxPath in self._availSyntax.items():
            logger.debug("Checking theme syntax for '%s'", syntaxKey)
            syntaxName = _loadInternalName(confParser, syntaxPath)
            if syntaxName:
                self._syntaxList.append((syntaxKey, syntaxName))

        self._syntaxList = sorted(self._syntaxList, key=_sortTheme)

        return self._syntaxList

    def getStyleSheet(self, name: str) -> str:
        """Load a standard style sheet."""
        return self._styleSheets.get(name, "")

    ##
    #  Internal Functions
    ##

    def _resetGuiColors(self) -> None:
        """Reset GUI colours to default values."""
        self.statNone    = QColor(120, 120, 120)
        self.statUnsaved = QColor(200, 15, 39)
        self.statSaved   = QColor(2, 133, 37)
        self.helpText    = QColor(0, 0, 0)
        self.fadedText   = QColor(128, 128, 128)
        self.errorText   = QColor(255, 0, 0)
        return

    def _listConf(self, targetDict: dict, checkDir: Path) -> bool:
        """Scan for theme config files and populate the dictionary."""
        if not checkDir.is_dir():
            return False

        for checkFile in checkDir.iterdir():
            if checkFile.is_file() and checkFile.name.endswith(".conf"):
                targetDict[checkFile.name[:-5]] = checkFile

        return True

    def _parseColour(self, parser: NWConfigParser, section: str, name: str) -> QColor:
        """Parse a colour value from a config string."""
        return QColor(*parser.rdIntList(section, name, [0, 0, 0, 255]))

    def _setPalette(
        self, parser: NWConfigParser, section: str, name: str, value: QPalette.ColorRole
    ) -> None:
        """Set a palette colour value from a config string."""
        self._guiPalette.setColor(value, self._parseColour(parser, section, name))
        return

    def _buildStyleSheets(self, palette: QPalette) -> None:
        """Build default style sheets."""
        self._styleSheets = {}

        aPx = CONFIG.pxInt(2)
        bPx = CONFIG.pxInt(4)
        cPx = CONFIG.pxInt(6)
        dPx = CONFIG.pxInt(8)

        tCol = palette.text().color()
        hCol = palette.highlight().color()

        # Flat Tab Widget and Tab Bar:
        self._styleSheets[STYLES_FLAT_TABS] = (
            "QTabWidget::pane {border: 0;} "
            f"QTabWidget QTabBar::tab {{border: 0; padding: {bPx}px {dPx}px;}} "
            f"QTabWidget QTabBar::tab:selected {{color: {cssCol(hCol)};}} "
        )

        # Minimal Tool Button
        self._styleSheets[STYLES_MIN_TOOLBUTTON] = (
            f"QToolButton {{padding: {aPx}px; margin: 0; border: none; background: transparent;}} "
            f"QToolButton:hover {{border: none; background: {cssCol(tCol, 48)};}} "
            "QToolButton::menu-indicator {image: none;} "
        )

        # Big Tool Button
        self._styleSheets[STYLES_BIG_TOOLBUTTON] = (
            f"QToolButton {{padding: {cPx}px; margin: 0; border: none; background: transparent;}} "
            f"QToolButton:hover {{border: none; background: {cssCol(tCol, 48)};}} "
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

    TOGGLE_ICON_KEYS: dict[str, tuple[str, str]] = {
        "bullet": ("bullet-on", "bullet-off"),
        "unfold": ("unfold-show", "unfold-hide"),
    }
    IMAGE_MAP: dict[str, tuple[str, str]] = {
        "welcome":  ("welcome-light.jpg", "welcome-dark.jpg"),
        "nw-text":  ("novelwriter-text-light.svg", "novelwriter-text-dark.svg"),
    }

    def __init__(self, mainTheme: GuiTheme) -> None:

        self.mainTheme = mainTheme

        # Storage
        self._svgData: dict[str, bytes] = {}
        self._svgColours: dict[str, bytes] = {}
        self._qIcons: dict[str, QIcon] = {}
        self._headerDec: list[QPixmap] = []
        self._headerDecNarrow: list[QPixmap] = []

        # Icon Theme Path
        self._themeList: list[tuple[str, str]] = []
        self._iconPath = CONFIG.assetPath("icons")

        # None Icon
        self._noIcon = QIcon(str(self._iconPath / "none.svg"))

        # Icon Theme Meta
        self.themeName    = ""
        self.themeAuthor  = ""
        self.themeLicense = ""

        return

    def clear(self) -> None:
        """Clear the icon cache."""
        text = QApplication.palette().windowText().color()
        default = text.name(QColor.NameFormat.HexRgb).encode("utf-8")
        faded = self.mainTheme.fadedText.name(QColor.NameFormat.HexRgb).encode("utf-8")

        self._svgData = {}
        self._svgColours = {
            "default": default,
            "faded":   faded,
            "red":     b"#ff0000",
            "orange":  b"#ff7f00",
            "yellow":  b"#ffff00",
            "green":   b"#00ff00",
            "aqua":    b"#00ffff",
            "blue":    b"#0000ff",
            "purple":  b"#ff00ff",
            "root":    b"#0000ff",
            "folder":  b"#ffff00",
            "file":    default,
            "title":   b"#00ff00",
            "chapter": b"#ff0000",
            "scene":   b"#0000ff",
            "note":    b"#ffff00",
        }
        self._qIcons = {}
        self._headerDec = []
        self._headerDecNarrow = []
        self.themeName    = ""
        self.themeAuthor  = ""
        self.themeLicense = ""
        return

    ##
    #  Actions
    ##

    def loadTheme(self, iconTheme: str) -> bool:
        """Update the theme map. This is more of an init, since many of
        the GUI icons cannot really be replaced without writing specific
        update functions for the classes where they're used.
        """
        logger.info("Loading icon theme '%s'", iconTheme)
        themePath = self._iconPath / f"{iconTheme}.icons"
        try:
            with open(themePath, mode="r", encoding="utf-8") as icons:
                for icon in icons:
                    bits = icon.partition("=")
                    key = bits[0].strip()
                    value = bits[2].strip()
                    if key and value:
                        if key.startswith("icon:"):
                            self._svgData[key[5:]] = value.encode("utf-8")
                        elif key == "meta:name":
                            self.themeName = value
                        elif key == "meta:author":
                            self.themeAuthor = value
                        elif key == "meta:license":
                            self.themeLicense = value
        except Exception:
            logger.error("Could not load icon theme from: %s", themePath)
            logException()
            return False

        # Set colour overrides for project item icons
        if (override := CONFIG.iconColTree) != "theme":
            color = self._svgColours.get(override, b"#000000")
            self._svgColours["root"] = color
            self._svgColours["folder"] = color
            if not CONFIG.iconColDocs:
                self._svgColours["file"] = color
                self._svgColours["title"] = color
                self._svgColours["chapter"] = color
                self._svgColours["scene"] = color
                self._svgColours["note"] = color

        return True

    def setIconColor(self, key: str, color: QColor) -> None:
        """Set an icon colour for a named colour."""
        self._svgColours[key] = color.name(QColor.NameFormat.HexRgb).encode("utf-8")
        return

    ##
    #  Access Functions
    ##

    def loadDecoration(self, name: str, w: int | None = None, h: int | None = None) -> QPixmap:
        """Load graphical decoration element based on the decoration
        map or the icon map. This function always returns a QPixmap.
        """
        if name in self.IMAGE_MAP:
            idx = 0 if self.mainTheme.isLightTheme else 1
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

    def getIcon(self, name: str, color: str | None = None, w: int = 24, h: int = 24) -> QIcon:
        """Return an icon from the icon buffer, or load it."""
        variant = f"{name}-{color}" if color else name
        if (key := f"{variant}-{w}x{h}") in self._qIcons:
            return self._qIcons[key]
        else:
            icon = self._loadIcon(name, color, w, h)
            self._qIcons[key] = icon
            logger.info("Icon: %s", key)
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

    def getPixmap(self, name: str, size: tuple[int, int], color: str | None = None) -> QPixmap:
        """Return an icon from the icon buffer as a QPixmap. If it
        doesn't exist, return an empty QPixmap.
        """
        w, h = size
        return self.getIcon(name, color, w, h).pixmap(w, h, QIcon.Mode.Normal)

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

        for item in self._iconPath.iterdir():
            if item.is_file() and item.suffix == ".icons":
                if name := _loadIconName(item):
                    self._themeList.append((item.stem, name))

        self._themeList = sorted(self._themeList, key=_sortTheme)

        return self._themeList

    ##
    #  Internal Functions
    ##

    def _loadIcon(self, name: str, color: str | None = None, w: int = 24, h: int = 24) -> QIcon:
        """Load an icon from the assets themes folder. Is guaranteed to
        return a QIcon.
        """
        # If we just want the app icons, return right away
        if name == "novelwriter":
            return QIcon(str(self._iconPath / "novelwriter.svg"))
        elif name == "proj_nwx":
            return QIcon(str(self._iconPath / "x-novelwriter-project.svg"))

        if svg := self._svgData.get(name, b""):
            if fill := self._svgColours.get(color or "default"):
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
        if fill := self._svgColours.get(color or "default"):
            painter.fillPath(path, QColor(fill.decode(encoding="utf-8")))
        painter.end()

        tMode = Qt.TransformationMode.SmoothTransformation
        return pixmap.scaledToHeight(height, tMode)


# Module Functions
# ================


def _sortTheme(data: tuple[str, str]) -> str:
    """Key function for theme sorting."""
    key, name = data
    return f"*{name}" if key.startswith("default_") else name


def _loadInternalName(confParser: NWConfigParser, confFile: str | Path) -> str:
    """Open a conf file and read the 'name' setting."""
    try:
        with open(confFile, mode="r", encoding="utf-8") as inFile:
            confParser.read_file(inFile)
    except Exception:
        logger.error("Could not load file: %s", confFile)
        logException()
        return ""

    return confParser.rdStr("Main", "name", "")


def _loadIconName(path: Path) -> str:
    """Open an icons file and read the name setting."""
    try:
        with open(path, mode="r", encoding="utf-8") as icons:
            for icon in icons:
                key, _, value = icon.partition("=")
                if key.strip() == "meta:name":
                    return value.strip()
    except Exception:
        logger.error("Could not load file: %s", path)
        logException()

    return ""
