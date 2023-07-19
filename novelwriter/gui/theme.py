"""
novelWriter – Theme and Icons Classes
=====================================
Classes managing and caching themes and icons

File History:
Created: 2019-05-18 [0.1.3] GuiTheme
Created: 2019-11-08 [0.4]   GuiIcons

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import qApp
from PyQt5.QtGui import (
    QPalette, QColor, QIcon, QFont, QFontMetrics, QFontDatabase, QPixmap
)

from novelwriter import CONFIG
from novelwriter.enum import nwItemLayout, nwItemType
from novelwriter.error import logException
from novelwriter.common import NWConfigParser, minmax
from novelwriter.constants import nwLabels

logger = logging.getLogger(__name__)


# =============================================================================================== #
#  Gui Theme Class
#  Handles the look and feel of novelWriter
# =============================================================================================== #

class GuiTheme:

    def __init__(self):

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

        # GUI
        self.statNone    = [120, 120, 120]
        self.statUnsaved = [200, 15, 39]
        self.statSaved   = [2, 133, 37]
        self.helpText    = [0, 0, 0]

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
        self.colBack   = [255, 255, 255]
        self.colText   = [0, 0, 0]
        self.colLink   = [0, 0, 0]
        self.colHead   = [0, 0, 0]
        self.colHeadH  = [0, 0, 0]
        self.colEmph   = [0, 0, 0]
        self.colDialN  = [0, 0, 0]
        self.colDialD  = [0, 0, 0]
        self.colDialS  = [0, 0, 0]
        self.colHidden = [0, 0, 0]
        self.colKey    = [0, 0, 0]
        self.colVal    = [0, 0, 0]
        self.colSpell  = [0, 0, 0]
        self.colError  = [0, 0, 0]
        self.colRepTag = [0, 0, 0]
        self.colMod    = [0, 0, 0]

        # Class Setup
        # ===========

        # Init GUI Font
        self._setGuiFont()

        # Load Themes
        self._guiPalette  = QPalette()
        self._themeList: list[tuple[str, str]] = []
        self._syntaxList: list[tuple[str, str]] = []
        self._availThemes: dict[str, Path] = {}
        self._availSyntax: dict[str, Path] = {}

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
        self.loadDecoration = self.iconCache.loadDecoration
        self.getHeaderDecoration = self.iconCache.getHeaderDecoration

        # Extract Other Info
        self.guiDPI = qApp.primaryScreen().logicalDotsPerInchX()
        self.guiScale = qApp.primaryScreen().logicalDotsPerInchX()/96.0
        CONFIG.guiScale = self.guiScale
        logger.debug("GUI DPI: %.1f", self.guiDPI)
        logger.debug("GUI Scale: %.2f", self.guiScale)

        # Fonts
        self.guiFont = qApp.font()

        qMetric = QFontMetrics(self.guiFont)
        self.fontPointSize = self.guiFont.pointSizeF()
        self.fontPixelSize = int(round(qMetric.height()))
        self.baseIconSize = int(round(qMetric.ascent()))
        self.textNHeight = qMetric.boundingRect("N").height()
        self.textNWidth = qMetric.boundingRect("N").width()

        # Monospace Font
        self.guiFontFixed = QFont()
        self.guiFontFixed.setPointSizeF(0.95*self.fontPointSize)
        self.guiFontFixed.setFamily(QFontDatabase.systemFont(QFontDatabase.FixedFont).family())

        logger.debug("GUI Font Family: %s", self.guiFont.family())
        logger.debug("GUI Font Point Size: %.2f", self.fontPointSize)
        logger.debug("GUI Font Pixel Size: %d", self.fontPixelSize)
        logger.debug("GUI Base Icon Size: %d", self.baseIconSize)
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

    def loadTheme(self):
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
        else:
            self._guiPalette = qApp.style().standardPalette()

        # GUI
        sec = "GUI"
        if parser.has_section(sec):
            self.helpText    = self._parseColour(parser, sec, "helptext")
            self.statNone    = self._parseColour(parser, sec, "statusnone")
            self.statUnsaved = self._parseColour(parser, sec, "statusunsaved")
            self.statSaved   = self._parseColour(parser, sec, "statussaved")

        # Update Dependant Colours
        backCol = self._guiPalette.window().color()
        textCol = self._guiPalette.windowText().color()

        backLNess = backCol.lightnessF()
        textLNess = textCol.lightnessF()

        if self.helpText == [0, 0, 0]:
            if backLNess > textLNess:
                helpLCol = textLNess + 0.35*(backLNess - textLNess)
            else:
                helpLCol = backLNess + 0.65*(textLNess - backLNess)
            self.helpText = [int(255*helpLCol)]*3

        # Icons
        defaultIcons = "typicons_light" if backLNess >= 0.5 else "typicons_dark"
        self.iconCache.loadTheme(self.themeIcons or defaultIcons)

        # Apply Styles
        qApp.setPalette(self._guiPalette)

        return True

    def loadSyntax(self):
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
            self.colDialN  = self._parseColour(confParser, cnfSec, "straightquotes")
            self.colDialD  = self._parseColour(confParser, cnfSec, "doublequotes")
            self.colDialS  = self._parseColour(confParser, cnfSec, "singlequotes")
            self.colHidden = self._parseColour(confParser, cnfSec, "hidden")
            self.colKey    = self._parseColour(confParser, cnfSec, "keyword")
            self.colVal    = self._parseColour(confParser, cnfSec, "value")
            self.colSpell  = self._parseColour(confParser, cnfSec, "spellcheckline")
            self.colError  = self._parseColour(confParser, cnfSec, "errorline")
            self.colRepTag = self._parseColour(confParser, cnfSec, "replacetag")
            self.colMod    = self._parseColour(confParser, cnfSec, "modifier")

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

        self._themeList = sorted(self._themeList, key=lambda x: x[1])

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

        self._syntaxList = sorted(self._syntaxList, key=lambda x: x[1])

        return self._syntaxList

    ##
    #  Internal Functions
    ##

    def _setGuiFont(self):
        """Update the GUI's font style from settings."""
        theFont = QFont()
        fontDB = QFontDatabase()
        if CONFIG.guiFont not in fontDB.families():
            if CONFIG.osWindows and "Arial" in fontDB.families():
                # On Windows we default to Arial if possible
                theFont.setFamily("Arial")
                theFont.setPointSize(10)
            else:
                theFont = fontDB.systemFont(QFontDatabase.GeneralFont)
            CONFIG.guiFont = theFont.family()
            CONFIG.guiFontSize = theFont.pointSize()
        else:
            theFont.setFamily(CONFIG.guiFont)
            theFont.setPointSize(CONFIG.guiFontSize)

        qApp.setFont(theFont)

        return

    def _listConf(self, targetDict: dict, checkDir: Path) -> bool:
        """Scan for theme config files and populate the dictionary."""
        if not checkDir.is_dir():
            return False

        for checkFile in checkDir.iterdir():
            if checkFile.is_file() and checkFile.name.endswith(".conf"):
                targetDict[checkFile.name[:-5]] = checkFile

        return True

    def _parseColour(
        self, parser: NWConfigParser, section: str, name: str
    ) -> list[int]:
        """Parse a colour value from a config string."""
        if parser.has_option(section, name):
            values = parser.get(section, name).split(",")
            result = []
            try:
                result.append(minmax(int(values[0]), 0, 255))
                result.append(minmax(int(values[1]), 0, 255))
                result.append(minmax(int(values[2]), 0, 255))
            except Exception:
                logger.error("Could not load theme colours for '%s' from config file", name)
                result = [0, 0, 0]
        else:
            logger.warning("Could not find theme colours for '%s' in config file", name)
            result = [0, 0, 0]
        return result

    def _setPalette(
        self, parser: NWConfigParser, section: str, name: str, value: QPalette.ColorRole
    ):
        """Set a palette colour value from a config string."""
        self._guiPalette.setColor(
            value, QColor(*self._parseColour(parser, section, name))
        )
        return

# End Class GuiTheme


# =============================================================================================== #
#  Icons Class
# =============================================================================================== #

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

    ICON_KEYS = {
        # Project and GUI Icons
        "novelwriter", "build_excluded", "build_filtered", "build_included", "cls_archive",
        "cls_character", "cls_custom", "cls_entity", "cls_none", "cls_novel", "cls_object",
        "cls_plot", "cls_timeline", "cls_trash", "cls_world", "proj_chapter", "proj_details",
        "proj_document", "proj_folder", "proj_note", "proj_nwx", "proj_section", "proj_scene",
        "proj_stats", "proj_title", "search_cancel", "search_case", "search_loop",
        "search_preserve", "search_project", "search_regex", "search_word", "status_idle",
        "status_lang", "status_lines", "status_stats", "status_time", "view_build", "view_editor",
        "view_novel", "view_outline",

        # General Button Icons
        "add", "backward", "bookmark", "browse", "checked", "close", "cross", "down", "edit",
        "export", "forward", "maximise", "menu", "minimise", "noncheckable", "reference",
        "refresh", "remove", "revert", "search_replace", "search", "settings", "unchecked", "up",

        # Switches
        "sticky-on", "sticky-off",
        "bullet-on", "bullet-off",

        # Decorations
        "deco_doc_h0", "deco_doc_h1", "deco_doc_h2", "deco_doc_h3", "deco_doc_h4", "deco_doc_more",
    }

    IMAGE_MAP = {
        "wiz-back": "wizard-back.jpg",
    }

    def __init__(self, mainTheme):

        self.mainTheme = mainTheme

        # Storage
        self._qIcons    = {}
        self._themeMap  = {}
        self._headerDec = []
        self._confName  = "icons.conf"

        # Icon Theme Path
        self._iconPath = CONFIG.assetPath("icons")

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

    def loadTheme(self, iconTheme):
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

        return True

    ##
    #  Access Functions
    ##

    def loadDecoration(self, decoKey, pxW=None, pxH=None):
        """Load graphical decoration element based on the decoration
        map or the icon map. This function always returns a QPixmap.
        """
        if decoKey in self._themeMap:
            imgPath = self._themeMap[decoKey]
        elif decoKey in self.IMAGE_MAP:
            imgPath = CONFIG.assetPath("images") / self.IMAGE_MAP[decoKey]
        else:
            logger.error("Decoration with name '%s' does not exist", decoKey)
            return QPixmap()

        if not imgPath.is_file():
            logger.error("Asset not found: %s", imgPath)
            return QPixmap()

        theDeco = QPixmap(str(imgPath))
        if pxW is not None and pxH is not None:
            return theDeco.scaled(pxW, pxH, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        elif pxW is None and pxH is not None:
            return theDeco.scaledToHeight(pxH, Qt.SmoothTransformation)
        elif pxW is not None and pxH is None:
            return theDeco.scaledToWidth(pxW, Qt.SmoothTransformation)

        return theDeco

    def getIcon(self, iconKey):
        """Return an icon from the icon buffer. If it doesn't exist,
        return, load it, and if it still doesn't exist, return an empty
        icon.
        """
        if iconKey in self._qIcons:
            return self._qIcons[iconKey]
        else:
            qIcon = self._loadIcon(iconKey)
            self._qIcons[iconKey] = qIcon
            return qIcon

    def getPixmap(self, iconKey, iconSize):
        """Return an icon from the icon buffer as a QPixmap. If it
        doesn't exist, return an empty QPixmap.
        """
        qIcon = self.getIcon(iconKey)
        return qIcon.pixmap(iconSize[0], iconSize[1], QIcon.Normal)

    def getItemIcon(self, tType, tClass, tLayout, hLevel="H0"):
        """Get the correct icon for a project item based on type, class
        and header level
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
            return QIcon()

        return self.getIcon(iconName)

    def getHeaderDecoration(self, hLevel):
        """Get the decoration for a specific header level.
        """
        if not self._headerDec:
            iPx = self.mainTheme.baseIconSize
            self._headerDec = [
                self.loadDecoration("deco_doc_h0", pxH=iPx),
                self.loadDecoration("deco_doc_h1", pxH=iPx),
                self.loadDecoration("deco_doc_h2", pxH=iPx),
                self.loadDecoration("deco_doc_h3", pxH=iPx),
                self.loadDecoration("deco_doc_h4", pxH=iPx),
            ]
        return self._headerDec[minmax(hLevel, 0, 4)]

    ##
    #  Internal Functions
    ##

    def _loadIcon(self, iconKey):
        """Load an icon from the assets themes folder. Is guaranteed to
        return a QIcon.
        """
        if iconKey not in self.ICON_KEYS:
            logger.error("Requested unknown icon name '%s'", iconKey)
            return QIcon()

        # If we just want the app icons, return right away
        if iconKey == "novelwriter":
            return QIcon(str(self._iconPath / "novelwriter.svg"))
        elif iconKey == "proj_nwx":
            return QIcon(str(self._iconPath / "x-novelwriter-project.svg"))

        # Otherwise, we load from the theme folder
        if iconKey in self._themeMap:
            logger.debug("Loading: %s", self._themeMap[iconKey].name)
            return QIcon(str(self._themeMap[iconKey]))

        # If we didn't find one, give up and return an empty icon
        logger.warning("Did not load an icon for '%s'", iconKey)

        return QIcon()

# END Class GuiIcons


# =============================================================================================== #
#  Module Functions
# =============================================================================================== #

def _loadInternalName(confParser, confFile):
    """Open a conf file and read the 'name' setting.
    """
    try:
        with open(confFile, mode="r", encoding="utf-8") as inFile:
            confParser.read_file(inFile)
    except Exception:
        logger.error("Could not load file: %s", confFile)
        logException()
        return ""

    return confParser.rdStr("Main", "name", "")
