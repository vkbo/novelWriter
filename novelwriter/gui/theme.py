"""
novelWriter – Theme and Icons Classes
=====================================
Classes managing and caching themes and icons

File History:
Created: 2019-05-18 [0.1.3] GuiTheme
Created: 2019-11-08 [0.4]   GuiIcons

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
import logging
import novelwriter

from math import ceil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import qApp
from PyQt5.QtGui import (
    QPalette, QColor, QIcon, QFont, QFontMetrics, QFontDatabase, QPixmap
)

from novelwriter.enum import nwItemLayout, nwItemType
from novelwriter.error import logException
from novelwriter.common import NWConfigParser, readTextFile
from novelwriter.constants import nwLabels

logger = logging.getLogger(__name__)


# =============================================================================================== #
#  Gui Theme Class
#  Handles the look and feel of novelWriter
# =============================================================================================== #

class GuiTheme:

    def __init__(self):

        self.mainConf = novelwriter.CONFIG
        self.theIcons = GuiIcons(self)

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

        # Changeable Settings
        self.guiTheme   = None
        self.guiSyntax  = None
        self.syntaxFile = None
        self.cssFile    = None
        self.guiFontDB  = QFontDatabase()

        # Class Setup
        # ===========

        self._guiPalette  = QPalette()
        self._themeList   = []
        self._syntaxList  = []
        self._availThemes = {}
        self._availSyntax = {}

        self._listConf(self._availSyntax, os.path.join(self.mainConf.dataPath, "syntax"))
        self._listConf(self._availSyntax, os.path.join(self.mainConf.assetPath, "syntax"))
        self._listConf(self._availThemes, os.path.join(self.mainConf.dataPath, "themes"))
        self._listConf(self._availThemes, os.path.join(self.mainConf.assetPath, "themes"))

        self.updateFont()
        self.updateTheme()
        self.theIcons.updateTheme()

        # Icon Functions
        self.getIcon = self.theIcons.getIcon
        self.getPixmap = self.theIcons.getPixmap
        self.getItemIcon = self.theIcons.getItemIcon
        self.loadDecoration = self.theIcons.loadDecoration

        # Extract Other Info
        self.guiDPI = qApp.primaryScreen().logicalDotsPerInchX()
        self.guiScale = qApp.primaryScreen().logicalDotsPerInchX()/96.0
        self.mainConf.guiScale = self.guiScale
        logger.verbose("GUI DPI: %.1f", self.guiDPI)
        logger.verbose("GUI Scale: %.2f", self.guiScale)

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

        logger.verbose("GUI Font Family: %s", self.guiFont.family())
        logger.verbose("GUI Font Point Size: %.2f", self.fontPointSize)
        logger.verbose("GUI Font Pixel Size: %d", self.fontPixelSize)
        logger.verbose("GUI Base Icon Size: %d", self.baseIconSize)
        logger.verbose("Text 'N' Height: %d", self.textNHeight)
        logger.verbose("Text 'N' Width: %d", self.textNWidth)

        return

    ##
    #  Methods
    ##

    def getTextWidth(self, theText, theFont=None):
        """Returns the width needed to contain a given piece of text.
        """
        if isinstance(theFont, QFont):
            qMetrics = QFontMetrics(theFont)
        else:
            qMetrics = QFontMetrics(self.guiFont)
        return int(ceil(qMetrics.boundingRect(theText).width()))

    ##
    #  Actions
    ##

    def updateFont(self):
        """Update the GUI's font style from settings.
        """
        theFont = QFont()
        if self.mainConf.guiFont not in self.guiFontDB.families():
            if self.mainConf.osWindows and "Arial" in self.guiFontDB.families():
                # On Windows we default to Arial if possible
                theFont.setFamily("Arial")
                theFont.setPointSize(10)
            else:
                theFont = self.guiFontDB.systemFont(QFontDatabase.GeneralFont)
            self.mainConf.guiFont = theFont.family()
            self.mainConf.guiFontSize = theFont.pointSize()
        else:
            theFont.setFamily(self.mainConf.guiFont)
            theFont.setPointSize(self.mainConf.guiFontSize)

        qApp.setFont(theFont)

        return

    def updateTheme(self):
        """Update the GUI theme from theme files.
        """
        self.guiTheme  = self.mainConf.guiTheme
        self.guiSyntax = self.mainConf.guiSyntax

        self.themeFile = self._availThemes.get(self.guiTheme, None)
        if self.themeFile is None:
            logger.error("Could not find GUI theme '%s'", self.guiTheme)
        else:
            self.cssFile = self.themeFile[:-5]+".css"
            self.loadTheme()

        self.syntaxFile = self._availSyntax.get(self.guiSyntax, None)
        if self.syntaxFile is None:
            logger.error("Could not find syntax theme '%s'", self.guiSyntax)
        else:
            self.loadSyntax()

        # Update dependant colours
        backCol = qApp.palette().window().color()
        textCol = qApp.palette().windowText().color()

        backLCol = backCol.lightnessF()
        textLCol = textCol.lightnessF()

        if backLCol > textLCol:
            helpLCol = textLCol + 0.65*(backLCol - textLCol)
        else:
            helpLCol = backLCol + 0.65*(textLCol - backLCol)

        self.helpText = [int(255*helpLCol)]*3

        return True

    def loadTheme(self):
        """Load the currently specified GUI theme.
        """
        logger.info("Loading GUI theme '%s'", self.guiTheme)

        # Config File
        confParser = NWConfigParser()
        try:
            with open(self.themeFile, mode="r", encoding="utf-8") as inFile:
                confParser.read_file(inFile)
        except Exception:
            logger.error("Could not load theme settings from: %s", self.themeFile)
            logException()
            return False

        # Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.themeName        = confParser.rdStr(cnfSec, "name", "")
            self.themeDescription = confParser.rdStr(cnfSec, "description", "N/A")
            self.themeAuthor      = confParser.rdStr(cnfSec, "author", "N/A")
            self.themeCredit      = confParser.rdStr(cnfSec, "credit", "N/A")
            self.themeUrl         = confParser.rdStr(cnfSec, "url", "")
            self.themeLicense     = confParser.rdStr(cnfSec, "license", "N/A")
            self.themeLicenseUrl  = confParser.rdStr(cnfSec, "licenseurl", "")

        # Palette
        cnfSec = "Palette"
        if confParser.has_section(cnfSec):
            self._setPalette(confParser, cnfSec, "window",          QPalette.Window)
            self._setPalette(confParser, cnfSec, "windowtext",      QPalette.WindowText)
            self._setPalette(confParser, cnfSec, "base",            QPalette.Base)
            self._setPalette(confParser, cnfSec, "alternatebase",   QPalette.AlternateBase)
            self._setPalette(confParser, cnfSec, "text",            QPalette.Text)
            self._setPalette(confParser, cnfSec, "tooltipbase",     QPalette.ToolTipBase)
            self._setPalette(confParser, cnfSec, "tooltiptext",     QPalette.ToolTipText)
            self._setPalette(confParser, cnfSec, "button",          QPalette.Button)
            self._setPalette(confParser, cnfSec, "buttontext",      QPalette.ButtonText)
            self._setPalette(confParser, cnfSec, "brighttext",      QPalette.BrightText)
            self._setPalette(confParser, cnfSec, "highlight",       QPalette.Highlight)
            self._setPalette(confParser, cnfSec, "highlightedtext", QPalette.HighlightedText)
            self._setPalette(confParser, cnfSec, "link",            QPalette.Link)
            self._setPalette(confParser, cnfSec, "linkvisited",     QPalette.LinkVisited)

        # GUI
        cnfSec = "GUI"
        if confParser.has_section(cnfSec):
            self.statNone    = self._loadColour(confParser, cnfSec, "statusnone")
            self.statUnsaved = self._loadColour(confParser, cnfSec, "statusunsaved")
            self.statSaved   = self._loadColour(confParser, cnfSec, "statussaved")

        # CSS File
        cssData = readTextFile(self.cssFile)
        if cssData:
            qApp.setStyleSheet(cssData)

        # Apply Styles
        qApp.setPalette(self._guiPalette)

        return True

    def loadSyntax(self):
        """Load the currently specified syntax highlighter theme.
        """
        logger.info("Loading syntax theme '%s'", self.guiSyntax)

        confParser = NWConfigParser()
        try:
            with open(self.syntaxFile, mode="r", encoding="utf-8") as inFile:
                confParser.read_file(inFile)
        except Exception:
            logger.error("Could not load syntax colours from: %s", self.syntaxFile)
            logException()
            return False

        # Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.syntaxName        = confParser.rdStr(cnfSec, "name", "")
            self.syntaxDescription = confParser.rdStr(cnfSec, "description", "")
            self.syntaxAuthor      = confParser.rdStr(cnfSec, "author", "")
            self.syntaxCredit      = confParser.rdStr(cnfSec, "credit", "")
            self.syntaxUrl         = confParser.rdStr(cnfSec, "url", "")
            self.syntaxLicense     = confParser.rdStr(cnfSec, "license", "")
            self.syntaxLicenseUrl  = confParser.rdStr(cnfSec, "licenseurl", "")

        # Syntax
        cnfSec = "Syntax"
        if confParser.has_section(cnfSec):
            self.colBack   = self._loadColour(confParser, cnfSec, "background")
            self.colText   = self._loadColour(confParser, cnfSec, "text")
            self.colLink   = self._loadColour(confParser, cnfSec, "link")
            self.colHead   = self._loadColour(confParser, cnfSec, "headertext")
            self.colHeadH  = self._loadColour(confParser, cnfSec, "headertag")
            self.colEmph   = self._loadColour(confParser, cnfSec, "emphasis")
            self.colDialN  = self._loadColour(confParser, cnfSec, "straightquotes")
            self.colDialD  = self._loadColour(confParser, cnfSec, "doublequotes")
            self.colDialS  = self._loadColour(confParser, cnfSec, "singlequotes")
            self.colHidden = self._loadColour(confParser, cnfSec, "hidden")
            self.colKey    = self._loadColour(confParser, cnfSec, "keyword")
            self.colVal    = self._loadColour(confParser, cnfSec, "value")
            self.colSpell  = self._loadColour(confParser, cnfSec, "spellcheckline")
            self.colError  = self._loadColour(confParser, cnfSec, "errorline")
            self.colRepTag = self._loadColour(confParser, cnfSec, "replacetag")
            self.colMod    = self._loadColour(confParser, cnfSec, "modifier")

        return True

    def listThemes(self):
        """Scan the GUI themes folder and list all themes.
        """
        if self._themeList:
            return self._themeList

        confParser = NWConfigParser()
        for themeKey, themePath in self._availThemes.items():
            logger.verbose("Checking theme config for '%s'", themeKey)
            themeName = _loadInternalName(confParser, themePath)
            if themeName:
                self._themeList.append((themeKey, themeName))

        self._themeList = sorted(self._themeList, key=lambda x: x[1])

        return self._themeList

    def listSyntax(self):
        """Scan the syntax themes folder and list all themes.
        """
        if self._syntaxList:
            return self._syntaxList

        confParser = NWConfigParser()
        for syntaxKey, syntaxPath in self._availSyntax.items():
            logger.verbose("Checking theme syntax for '%s'", syntaxKey)
            syntaxName = _loadInternalName(confParser, syntaxPath)
            if syntaxName:
                self._syntaxList.append((syntaxKey, syntaxName))

        self._syntaxList = sorted(self._syntaxList, key=lambda x: x[1])

        return self._syntaxList

    ##
    #  Internal Functions
    ##

    def _listConf(self, targetDict, checkDir):
        """Scan for syntax and gui themes and populate the dictionary.
        """
        if not os.path.isdir(checkDir):
            return

        for checkFile in os.listdir(checkDir):
            confPath = os.path.join(checkDir, checkFile)
            if os.path.isfile(confPath) and confPath.endswith(".conf"):
                targetDict[checkFile[:-5]] = confPath

        return

    def _loadColour(self, confParser, cnfSec, cnfName):
        """Load a colour value from a config string.
        """
        if confParser.has_option(cnfSec, cnfName):
            inData = confParser.get(cnfSec, cnfName).split(",")
            outData = []
            try:
                outData.append(int(inData[0]))
                outData.append(int(inData[1]))
                outData.append(int(inData[2]))
            except Exception:
                logger.error("Could not load theme colours for '%s' from config file", cnfName)
                outData = [0, 0, 0]
        else:
            logger.warning("Could not find theme colours for '%s' in config file", cnfName)
            outData = [0, 0, 0]
        return outData

    def _setPalette(self, confParser, cnfSec, cnfName, paletteVal):
        """Set a palette colour value from a config string.
        """
        readCol = []
        if confParser.has_option(cnfSec, cnfName):
            inData = confParser.get(cnfSec, cnfName).split(",")
            try:
                readCol.append(int(inData[0]))
                readCol.append(int(inData[1]))
                readCol.append(int(inData[2]))
            except Exception:
                logger.error("Could not load theme colours for '%s' from config file", cnfName)
                return
        if len(readCol) == 3:
            self._guiPalette.setColor(paletteVal, QColor(*readCol))
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
        # Project and GUI icons
        "novelwriter", "proj_nwx",
        "cls_none", "cls_novel", "cls_plot", "cls_character", "cls_world",
        "cls_timeline", "cls_object", "cls_entity", "cls_custom", "cls_archive", "cls_trash",
        "proj_document", "proj_title", "proj_chapter", "proj_scene", "proj_note", "proj_folder",
        "status_lang", "status_time", "status_idle", "status_stats", "status_lines",
        "doc_h0", "doc_h1", "doc_h2", "doc_h3", "doc_h4",
        "search_case", "search_regex", "search_word", "search_loop", "search_project",
        "search_cancel", "search_preserve",

        # General Button Icons
        "delete", "close", "done", "clear", "save", "add", "remove",
        "search", "search_replace", "edit", "check", "cross", "hash",
        "maximise", "minimise", "refresh", "reference", "backward",
        "forward", "settings",

        # Switches
        "sticky-on", "sticky-off",
        "bullet-on", "bullet-off",
    }

    DECO_MAP = {
        "wiz-back": "wizard-back.jpg",
    }

    def __init__(self, theTheme):

        self.mainConf = novelwriter.CONFIG
        self.theTheme = theTheme

        # Storage
        self._qIcons    = {}
        self._themeMap  = {}
        self._themeList = []
        self._confName  = "icons.conf"

        # Icon Theme Path
        self._iconPath  = os.path.join(self.mainConf.assetPath, "icons")
        self._themePath = os.path.join(self._iconPath, "system")

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

    def updateTheme(self):
        """Update the theme map. This is more of an init, since many of
        the GUI icons cannot really be replaced without writing specific
        update functions for the classes where they're used.
        """
        self._themeMap = {}
        themePath = self._getThemePath()
        if themePath is None:
            logger.warning("No icons loaded")
            return False

        self._themePath = themePath
        themeConf = os.path.join(themePath, self._confName)
        logger.info("Loading icon theme '%s'", self.mainConf.guiIcons)

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
                    iconPath = os.path.join(self._themePath, iconFile)
                    if os.path.isfile(iconPath):
                        self._themeMap[iconName] = iconPath
                        logger.verbose("Icon slot '%s' using file '%s'", iconName, iconFile)
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

        return True

    ##
    #  Access Functions
    ##

    def loadDecoration(self, decoKey, pxW, pxH):
        """Load graphical decoration element based on the decoration
        map. This function always returns a QSwgWidget.
        """
        if decoKey not in self.DECO_MAP:
            logger.error("Decoration with name '%s' does not exist", decoKey)
            return QPixmap()

        imgPath = os.path.join(
            self.mainConf.assetPath, "images", self.DECO_MAP[decoKey]
        )
        if not os.path.isfile(imgPath):
            logger.error("Decoration file '%s' not in assets folder", self.DECO_MAP[decoKey])
            return QPixmap()

        theDeco = QPixmap(imgPath)
        if pxW is not None and pxH is not None:
            return theDeco.scaled(pxW, pxH, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        elif pxW is None and pxH is not None:
            return theDeco.scaledToHeight(pxH, Qt.SmoothTransformation)
        elif pxW is not None and pxH is None:
            return theDeco.scaledToWidth(pxW, Qt.SmoothTransformation)

        return theDeco

    def getIcon(self, iconKey, iconSize=None):
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
            elif tLayout == nwItemLayout.NOTE:
                iconName = "proj_note"
        elif tType == nwItemType.TRASH:
            iconName = nwLabels.CLASS_ICON[tClass]

        if iconName is None:
            return QIcon()

        return self.getIcon(iconName)

    def listThemes(self):
        """Scan the icons themes folder and list all themes.
        """
        if self._themeList:
            return self._themeList

        confParser = NWConfigParser()
        for themeDir in os.listdir(self._iconPath):
            themePath = os.path.join(self._iconPath, themeDir)
            if not os.path.isdir(themePath):
                continue

            logger.verbose("Checking icon theme config for '%s'", themeDir)
            themeConf = os.path.join(themePath, self._confName)
            themeName = _loadInternalName(confParser, themeConf)
            if themeName:
                self._themeList.append((themeDir, themeName))

        self._themeList = sorted(self._themeList, key=lambda x: x[1])

        return self._themeList

    ##
    #  Internal Functions
    ##

    def _getThemePath(self):
        """Get a valid theme path. Returns None if it fails.
        """
        themePath = os.path.join(self.mainConf.assetPath, "icons", self.mainConf.guiIcons)
        if not os.path.isdir(themePath):
            logger.warning(
                "Icon theme '%s' not found, resetting to default", self.mainConf.guiIcons
            )
            self.mainConf.setDefaultIconTheme()

            themePath = os.path.join(self.mainConf.assetPath, "icons", self.mainConf.guiIcons)
            if not os.path.isdir(themePath):
                logger.error("Default icon theme not found")
                return None

        return themePath

    def _loadIcon(self, iconKey):
        """Load an icon from the assets themes folder. Is guaranteed to
        return a QIcon.
        """
        if iconKey not in self.ICON_KEYS:
            logger.error("Requested unknown icon name '%s'", iconKey)
            return QIcon()

        # If we just want the app icons, return right away
        if iconKey == "novelwriter":
            return QIcon(os.path.join(self._iconPath, "novelwriter.svg"))
        elif iconKey == "proj_nwx":
            return QIcon(os.path.join(self._iconPath, "x-novelwriter-project.svg"))

        # Otherwise, we load from the theme folder
        if iconKey in self._themeMap:
            relPath = os.path.relpath(self._themeMap[iconKey], self._iconPath)
            logger.verbose("Loading: %s", relPath)
            return QIcon(self._themeMap[iconKey])

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
