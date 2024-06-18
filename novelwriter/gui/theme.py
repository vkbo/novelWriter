"""
novelWriter – Theme and Icons Classes
=====================================

File History:
Created: 2019-05-18 [0.1.3] GuiTheme
Created: 2019-11-08 [0.4]   GuiIcons

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

import logging

from math import ceil
from pathlib import Path

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QFontMetrics, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import QApplication

from novelwriter import CONFIG
from novelwriter.common import NWConfigParser, cssCol, minmax
from novelwriter.constants import nwLabels
from novelwriter.enum import nwItemClass, nwItemLayout, nwItemType
from novelwriter.error import logException

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
        self.themeIcons       = ""
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

        # Extract Other Info
        self.guiDPI = QApplication.primaryScreen().logicalDotsPerInchX()
        self.guiScale = QApplication.primaryScreen().logicalDotsPerInchX()/96.0
        CONFIG.guiScale = self.guiScale
        logger.debug("GUI DPI: %.1f", self.guiDPI)
        logger.debug("GUI Scale: %.2f", self.guiScale)

        # Fonts
        self.guiFont = QApplication.font()
        self.guiFontB = QApplication.font()
        self.guiFontB.setBold(True)
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
            self.themeIcons       = parser.rdStr(sec, "icontheme", "")

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

        # Icons
        defaultIcons = "typicons_light" if backLNess >= 0.5 else "typicons_dark"
        self.iconCache.loadTheme(self.themeIcons or defaultIcons)

        # Apply Styles
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

    def _setPalette(self, parser: NWConfigParser, section: str,
                    name: str, value: QPalette.ColorRole) -> None:
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
    and provides a simple interface for requesting icons. Only icons
    listed in the ICON_KEYS are handled.

    Icons are loaded on first request, and then cached for further
    requests. Each icon key in the ICON_KEYS set has standard icon set
    in the icon theme conf file. The existence of the file, and the
    definition of all keys are checked when the theme is loaded.

    When an icon is requested, the icon is loaded and cached. If it is
    missing, a blank icon is returned and a warning issued.
    """

    ICON_KEYS: set[str] = {
        # Project and GUI Icons
        "novelwriter", "alert_error", "alert_info", "alert_question", "alert_warn",
        "build_excluded", "build_filtered", "build_included", "proj_chapter", "proj_details",
        "proj_document", "proj_folder", "proj_note", "proj_nwx", "proj_section", "proj_scene",
        "proj_stats", "proj_title", "status_idle", "status_lang", "status_lines", "status_stats",
        "status_time", "view_build", "view_editor", "view_novel", "view_outline", "view_search",

        # Class Icons
        "cls_archive", "cls_character", "cls_custom", "cls_entity", "cls_none", "cls_novel",
        "cls_object", "cls_plot", "cls_template", "cls_timeline", "cls_trash", "cls_world",

        # Search Icons
        "search_cancel", "search_case", "search_loop", "search_preserve", "search_project",
        "search_regex", "search_word",

        # Format Icons
        "fmt_bold", "fmt_bold-md", "fmt_italic", "fmt_italic-md", "fmt_mark", "fmt_strike",
        "fmt_strike-md", "fmt_subscript", "fmt_superscript", "fmt_underline",

        # General Button Icons
        "add", "add_document", "backward", "bookmark", "browse", "checked", "close", "cross",
        "document", "down", "edit", "export", "font", "forward", "import", "list", "maximise",
        "menu", "minimise", "more", "noncheckable", "open", "panel", "quote", "refresh", "remove",
        "revert", "search_replace", "search", "settings", "star", "unchecked", "up", "view",

        # Switches
        "sticky-on", "sticky-off",
        "bullet-on", "bullet-off",
        "unfold-show", "unfold-hide",

        # Decorations
        "deco_doc_h0", "deco_doc_h1", "deco_doc_h2", "deco_doc_h3", "deco_doc_h4", "deco_doc_more",
        "deco_doc_h0_n", "deco_doc_h1_n", "deco_doc_h2_n", "deco_doc_h3_n", "deco_doc_h4_n",
        "deco_doc_nt_n",
    }

    TOGGLE_ICON_KEYS: dict[str, tuple[str, str]] = {
        "sticky": ("sticky-on", "sticky-off"),
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
        self._qIcons: dict[str, QIcon] = {}
        self._themeMap: dict[str, Path] = {}
        self._headerDec: list[QPixmap] = []
        self._headerDecNarrow: list[QPixmap] = []

        # Icon Theme Path
        self._confName = "icons.conf"
        self._iconPath = CONFIG.assetPath("icons")

        # None Icon
        self._noIcon = QIcon(str(self._iconPath / "none.svg"))

        # Icon Theme Meta
        self.themeName        = ""
        self.themeDescription = ""
        self.themeAuthor      = ""
        self.themeCredit      = ""
        self.themeUrl         = ""
        self.themeLicense     = ""
        self.themeLicenseUrl  = ""

        return

    ##
    #  Actions
    ##

    def loadTheme(self, iconTheme: str) -> bool:
        """Update the theme map. This is more of an init, since many of
        the GUI icons cannot really be replaced without writing specific
        update functions for the classes where they're used.
        """
        self._themeMap = {}
        themePath = self._iconPath / iconTheme
        if not themePath.is_dir():
            themePath = CONFIG.dataPath("icons") / iconTheme
            if not themePath.is_dir():
                logger.warning("No icons loaded for '%s'", iconTheme)
                return False

        themeConf = themePath / self._confName
        logger.info("Loading icon theme '%s'", iconTheme)

        # Config File
        confParser = NWConfigParser()
        try:
            with open(themeConf, mode="r", encoding="utf-8") as inFile:
                confParser.read_file(inFile)
        except Exception:
            logger.error("Could not load icon theme settings from: %s", themeConf)
            logException()
            return False

        # Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.themeName        = confParser.rdStr(cnfSec, "name", "")
            self.themeDescription = confParser.rdStr(cnfSec, "description", "")
            self.themeAuthor      = confParser.rdStr(cnfSec, "author", "N/A")
            self.themeCredit      = confParser.rdStr(cnfSec, "credit", "N/A")
            self.themeUrl         = confParser.rdStr(cnfSec, "url", "")
            self.themeLicense     = confParser.rdStr(cnfSec, "license", "N/A")
            self.themeLicenseUrl  = confParser.rdStr(cnfSec, "licenseurl", "")

        # Populate Icon Map
        cnfSec = "Map"
        if confParser.has_section(cnfSec):
            for iconName, iconFile in confParser.items(cnfSec):
                if iconName not in self.ICON_KEYS:
                    logger.error("Unknown icon name '%s' in config file", iconName)
                else:
                    iconPath = themePath / iconFile
                    if iconPath.is_file():
                        self._themeMap[iconName] = iconPath
                        logger.debug("Icon slot '%s' using file '%s'", iconName, iconFile)
                    else:
                        logger.error("Icon file '%s' not in theme folder", iconFile)

        # Check that icons have been defined
        logger.debug("Scanning theme icons")
        for iconKey in self.ICON_KEYS:
            if iconKey in ("novelwriter", "proj_nwx"):
                # These are not part of the theme itself
                continue
            if iconKey not in self._themeMap:
                logger.error("No icon file specified for '%s'", iconKey)

        # Refresh icons
        for iconKey in self._qIcons:
            logger.debug("Reloading icon: '%s'", iconKey)
            qIcon = self._loadIcon(iconKey)
            self._qIcons[iconKey] = qIcon

        self._headerDec = []
        self._headerDecNarrow = []

        return True

    ##
    #  Access Functions
    ##

    def loadDecoration(self, name: str, w: int | None = None, h: int | None = None) -> QPixmap:
        """Load graphical decoration element based on the decoration
        map or the icon map. This function always returns a QPixmap.
        """
        if name in self._themeMap:
            imgPath = self._themeMap[name]
        elif name in self.IMAGE_MAP:
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

    def getIcon(self, name: str) -> QIcon:
        """Return an icon from the icon buffer, or load it."""
        if name in self._qIcons:
            return self._qIcons[name]
        else:
            icon = self._loadIcon(name)
            self._qIcons[name] = icon
            return icon

    def getToggleIcon(self, name: str, size: tuple[int, int]) -> QIcon:
        """Return a toggle icon from the icon buffer. or load it."""
        if name in self.TOGGLE_ICON_KEYS:
            pOne = self.getPixmap(self.TOGGLE_ICON_KEYS[name][0], size)
            pTwo = self.getPixmap(self.TOGGLE_ICON_KEYS[name][1], size)
            icon = QIcon()
            icon.addPixmap(pOne, QIcon.Mode.Normal, QIcon.State.On)
            icon.addPixmap(pTwo, QIcon.Mode.Normal, QIcon.State.Off)
            return icon
        return self._noIcon

    def getPixmap(self, name: str, size: tuple[int, int]) -> QPixmap:
        """Return an icon from the icon buffer as a QPixmap. If it
        doesn't exist, return an empty QPixmap.
        """
        return self.getIcon(name).pixmap(size[0], size[1], QIcon.Mode.Normal)

    def getItemIcon(self, tType: nwItemType, tClass: nwItemClass,
                    tLayout: nwItemLayout, hLevel: str = "H0") -> QIcon:
        """Get the correct icon for a project item based on type, class
        and heading level
        """
        iconName = None
        if tType == nwItemType.ROOT:
            iconName = nwLabels.CLASS_ICON[tClass]
        elif tType == nwItemType.FOLDER:
            iconName = "proj_folder"
        elif tType == nwItemType.FILE:
            iconName = "proj_document"
            if tLayout == nwItemLayout.DOCUMENT:
                if hLevel == "H1":
                    iconName = "proj_title"
                elif hLevel == "H2":
                    iconName = "proj_chapter"
                elif hLevel == "H3":
                    iconName = "proj_scene"
                elif hLevel == "H4":
                    iconName = "proj_section"
            elif tLayout == nwItemLayout.NOTE:
                iconName = "proj_note"
        if iconName is None:
            return self._noIcon

        return self.getIcon(iconName)

    def getHeaderDecoration(self, hLevel: int) -> QPixmap:
        """Get the decoration for a specific heading level."""
        if not self._headerDec:
            iPx = self.mainTheme.baseIconHeight
            self._headerDec = [
                self.loadDecoration("deco_doc_h0", h=iPx),
                self.loadDecoration("deco_doc_h1", h=iPx),
                self.loadDecoration("deco_doc_h2", h=iPx),
                self.loadDecoration("deco_doc_h3", h=iPx),
                self.loadDecoration("deco_doc_h4", h=iPx),
            ]
        return self._headerDec[minmax(hLevel, 0, 4)]

    def getHeaderDecorationNarrow(self, hLevel: int) -> QPixmap:
        """Get the narrow decoration for a specific heading level."""
        if not self._headerDecNarrow:
            iPx = self.mainTheme.baseIconHeight
            self._headerDecNarrow = [
                self.loadDecoration("deco_doc_h0_n", h=iPx),
                self.loadDecoration("deco_doc_h1_n", h=iPx),
                self.loadDecoration("deco_doc_h2_n", h=iPx),
                self.loadDecoration("deco_doc_h3_n", h=iPx),
                self.loadDecoration("deco_doc_h4_n", h=iPx),
                self.loadDecoration("deco_doc_nt_n", h=iPx),
            ]
        return self._headerDecNarrow[minmax(hLevel, 0, 5)]

    ##
    #  Internal Functions
    ##

    def _loadIcon(self, name: str) -> QIcon:
        """Load an icon from the assets themes folder. Is guaranteed to
        return a QIcon.
        """
        if name not in self.ICON_KEYS:
            logger.error("Requested unknown icon name '%s'", name)
            return self._noIcon

        # If we just want the app icons, return right away
        if name == "novelwriter":
            return QIcon(str(self._iconPath / "novelwriter.svg"))
        elif name == "proj_nwx":
            return QIcon(str(self._iconPath / "x-novelwriter-project.svg"))

        # Otherwise, we load from the theme folder
        if name in self._themeMap:
            logger.debug("Loading: %s", self._themeMap[name].name)
            return QIcon(str(self._themeMap[name]))

        # If we didn't find one, give up and return an empty icon
        logger.warning("Did not load an icon for '%s'", name)

        return self._noIcon


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
