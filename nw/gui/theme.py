# -*- coding: utf-8 -*-
"""novelWriter Theme and Icons Classes

 novelWriter – Theme and Icons Classs
======================================
 Class managing and caching themes and icons

 File History:
 Created: 2019-05-18 [0.1.3] GuiTheme
 Created: 2019-11-08 [0.4.0] GuiIcons

 This file is a part of novelWriter
 Copyright 2018–2021, Veronica Berglyd Olsen

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

import nw
import logging
import configparser
import os

from math import ceil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyle, qApp
from PyQt5.QtGui import (
    QPalette, QColor, QIcon, QFont, QFontMetrics, QFontDatabase, QPixmap
)

from nw.constants import nwAlert

logger = logging.getLogger(__name__)

# =============================================================================================== #
#  Gui Theme Class
#  Handles the look and feel of novelWriter
# =============================================================================================== #

class GuiTheme:

    def __init__(self, theParent):

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theIcons   = GuiIcons(self.theParent)
        self.guiPalette = QPalette()
        self.guiPath    = "gui"
        self.fontPath   = "fonts"
        self.syntaxPath = "syntax"
        self.cssName    = "style.qss"
        self.confName   = "theme.conf"
        self.themeList  = []
        self.syntaxList = []

        # Loaded Theme Settings

        ## Theme
        self.themeName        = ""
        self.themeDescription = ""
        self.themeAuthor      = ""
        self.themeCredit      = ""
        self.themeUrl         = ""
        self.themeLicense     = ""
        self.themeLicenseUrl  = ""

        ## GUI
        self.statNone    = [120, 120, 120]
        self.statUnsaved = [200, 15, 39]
        self.statSaved   = [2, 133, 37]
        self.helpText    = [0, 0, 0]

        # Loaded Syntax Settings

        ## Main
        self.syntaxName        = ""
        self.syntaxDescription = ""
        self.syntaxAuthor      = ""
        self.syntaxCredit      = ""
        self.syntaxUrl         = ""
        self.syntaxLicense     = ""
        self.syntaxLicenseUrl  = ""

        ## Colours
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
        self.colTagErr = [0, 0, 0]
        self.colRepTag = [0, 0, 0]
        self.colMod    = [0, 0, 0]

        # Changeable Settings
        self.guiTheme   = None
        self.guiSyntax  = None
        self.themeRoot  = None
        self.themePath  = None
        self.syntaxFile = None
        self.confFile   = None
        self.cssFile    = None
        self.guiFontDB  = QFontDatabase()

        self.loadFonts()
        self.updateFont()
        self.updateTheme()
        self.theIcons.updateTheme()

        self.getIcon = self.theIcons.getIcon
        self.getPixmap = self.theIcons.getPixmap
        self.loadDecoration = self.theIcons.loadDecoration

        # Extract Other Info
        self.guiDPI = qApp.primaryScreen().logicalDotsPerInchX()
        self.guiScale = qApp.primaryScreen().logicalDotsPerInchX()/96.0
        self.mainConf.guiScale = self.guiScale
        logger.verbose("GUI DPI: %.1f" % self.guiDPI)
        logger.verbose("GUI Scale: %.2f" % self.guiScale)

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

        logger.verbose("GUI Font Family: %s" % self.guiFont.family())
        logger.verbose("GUI Font Point Size: %.2f" % self.fontPointSize)
        logger.verbose("GUI Font Pixel Size: %d" % self.fontPixelSize)
        logger.verbose("GUI Base Icon Size: %d" % self.baseIconSize)
        logger.verbose("Text 'N' Height: %d" % self.textNHeight)
        logger.verbose("Text 'N' Width: %d" % self.textNWidth)

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

    def loadFonts(self):
        """Add the fonts in the assets fonts folder to the app.
        """
        logger.debug("Loading additional fonts")

        ttfList = []
        fontAssets = os.path.join(self.mainConf.assetPath, self.fontPath)
        for fontFam in os.listdir(fontAssets):
            fontDir = os.path.join(fontAssets, fontFam)
            if os.path.isdir(fontDir):
                logger.verbose("Found font: %s" % fontFam)
                if fontFam not in self.guiFontDB.families():
                    for fontFile in os.listdir(fontDir):
                        ttfFile = os.path.join(fontDir, fontFile)
                        if os.path.isfile(ttfFile) and fontFile.endswith(".ttf"):
                            ttfList.append(ttfFile)

        for ttfFile in ttfList:
            relPath = os.path.relpath(ttfFile, fontAssets)
            logger.verbose("Adding font: %s" % relPath)
            fontID = self.guiFontDB.addApplicationFont(ttfFile)
            if fontID < 0:
                logger.error("Failed to add font: %s" % relPath)

        return

    def updateFont(self):
        """Updated the GUI's font style from settings,
        """
        theFont = QFont()
        if self.mainConf.guiFont not in self.guiFontDB.families():
            if self.mainConf.osWindows:
                # On Windows, default to Cantarell provided by novelWriter
                theFont.setFamily("Cantarell")
                theFont.setPointSize(11)
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
        self.guiTheme   = self.mainConf.guiTheme
        self.guiSyntax  = self.mainConf.guiSyntax
        self.themeRoot  = self.mainConf.themeRoot
        self.themePath  = os.path.join(self.mainConf.themeRoot, self.guiPath, self.guiTheme)
        self.syntaxFile = os.path.join(self.themeRoot, self.syntaxPath, self.guiSyntax+".conf")
        self.confFile   = os.path.join(self.themePath, self.confName)
        self.cssFile    = os.path.join(self.themePath, self.cssName)

        self.loadTheme()
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
        logger.debug("Loading theme files")
        logger.debug("System icon theme is '%s'" % str(QIcon.themeName()))

        # CSS File
        cssData = ""
        try:
            if os.path.isfile(self.cssFile):
                with open(self.cssFile, mode="r", encoding="utf8") as inFile:
                    cssData = inFile.read()
        except Exception as e:
            logger.error("Could not load theme css file")
            logger.error(str(e))
            return False

        # Config File
        confParser = configparser.ConfigParser()
        try:
            with open(self.confFile, mode="r", encoding="utf8") as inFile:
                confParser.read_file(inFile)
        except Exception as e:
            logger.error("Could not load theme settings from: %s" % self.confFile)
            logger.error(str(e))
            return False

        ## Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.themeName        = self._parseLine(confParser, cnfSec, "name", "")
            self.themeDescription = self._parseLine(confParser, cnfSec, "description", "N/A")
            self.themeAuthor      = self._parseLine(confParser, cnfSec, "author", "N/A")
            self.themeCredit      = self._parseLine(confParser, cnfSec, "credit", "N/A")
            self.themeUrl         = self._parseLine(confParser, cnfSec, "url", "")
            self.themeLicense     = self._parseLine(confParser, cnfSec, "license", "N/A")
            self.themeLicenseUrl  = self._parseLine(confParser, cnfSec, "licenseurl", "")

        ## Palette
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

        ## GUI
        cnfSec = "GUI"
        if confParser.has_section(cnfSec):
            self.statNone    = self._loadColour(confParser, cnfSec, "statusnone")
            self.statUnsaved = self._loadColour(confParser, cnfSec, "statusunsaved")
            self.statSaved   = self._loadColour(confParser, cnfSec, "statussaved")

        # Apply Styles
        qApp.setStyleSheet(cssData)
        qApp.setPalette(self.guiPalette)

        logger.info("Loaded theme '%s'" % self.guiTheme)

        return True

    def loadSyntax(self):
        """Load the currently specified syntax highlighter theme.
        """
        logger.debug("Loading syntax theme files")

        confParser = configparser.ConfigParser()
        try:
            with open(self.syntaxFile, mode="r", encoding="utf8") as inFile:
                confParser.read_file(inFile)
        except Exception as e:
            logger.error("Could not load syntax colours from: %s" % self.syntaxFile)
            logger.error(str(e))
            return False

        ## Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.syntaxName        = self._parseLine(confParser, cnfSec, "name", "")
            self.syntaxDescription = self._parseLine(confParser, cnfSec, "description", "")
            self.syntaxAuthor      = self._parseLine(confParser, cnfSec, "author", "")
            self.syntaxCredit      = self._parseLine(confParser, cnfSec, "credit", "")
            self.syntaxUrl         = self._parseLine(confParser, cnfSec, "url", "")
            self.syntaxLicense     = self._parseLine(confParser, cnfSec, "license", "")
            self.syntaxLicenseUrl  = self._parseLine(confParser, cnfSec, "licenseurl", "")

        ## Syntax
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
            self.colTagErr = self._loadColour(confParser, cnfSec, "tagerror")
            self.colRepTag = self._loadColour(confParser, cnfSec, "replacetag")
            self.colMod    = self._loadColour(confParser, cnfSec, "modifier")

        logger.info("Loaded syntax theme '%s'" % self.guiSyntax)

        return True

    def listThemes(self):
        """Scan the GUI themes folder and list all themes.
        """
        if self.themeList:
            return self.themeList

        confParser = configparser.ConfigParser()
        for themeDir in os.listdir(os.path.join(self.mainConf.themeRoot, self.guiPath)):
            themeConf = os.path.join(
                self.mainConf.themeRoot, self.guiPath, themeDir, self.confName
            )
            logger.verbose("Checking theme config for '%s'" % themeDir)
            try:
                with open(themeConf, mode="r", encoding="utf8") as inFile:
                    confParser.read_file(inFile)
            except Exception as e:
                self.theParent.makeAlert(
                    ["Could not load theme config file.", str(e)], nwAlert.ERROR
                )
                continue
            themeName = ""
            if confParser.has_section("Main"):
                if confParser.has_option("Main", "name"):
                    themeName = confParser.get("Main", "name")
                    logger.verbose("Theme name is '%s'" % themeName)
            if themeName != "":
                self.themeList.append((themeDir, themeName))

        self.themeList = sorted(self.themeList, key=lambda x: x[1])

        return self.themeList

    def listSyntax(self):
        """Scan the syntax themes folder and list all themes.
        """
        if self.syntaxList:
            return self.syntaxList

        confParser = configparser.ConfigParser()
        syntaxDir  = os.path.join(self.mainConf.themeRoot, self.syntaxPath)
        for syntaxFile in os.listdir(syntaxDir):
            syntaxPath = os.path.join(syntaxDir, syntaxFile)
            if not os.path.isfile(syntaxPath):
                continue
            logger.verbose("Checking theme syntax for '%s'" % syntaxFile)
            try:
                with open(syntaxPath, mode="r", encoding="utf8") as inFile:
                    confParser.read_file(inFile)
            except Exception as e:
                self.theParent.makeAlert(
                    ["Could not load syntax file.", str(e)], nwAlert.ERROR
                )
                return []
            syntaxName = ""
            if confParser.has_section("Main"):
                if confParser.has_option("Main", "name"):
                    syntaxName = confParser.get("Main", "name")
            if len(syntaxFile) > 5 and syntaxName != "":
                self.syntaxList.append((syntaxFile[:-5], syntaxName))
                logger.verbose("Syntax name is '%s'" % syntaxName)

        self.syntaxList = sorted(self.syntaxList, key=lambda x: x[1])

        return self.syntaxList

    ##
    #  Internal Functions
    ##

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
                logger.error("Could not load theme colours for '%s' from config file" % cnfName)
                outData = [0, 0, 0]
        else:
            logger.warning("Could not find theme colours for '%s' in config file" % cnfName)
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
                logger.error("Could not load theme colours for '%s' from config file" % cnfName)
                return
        if len(readCol) == 3:
            self.guiPalette.setColor(paletteVal, QColor(*readCol))
        return

    def _parseLine(self, confParser, cnfSec, cnfName, cnfDefault):
        if confParser.has_section(cnfSec):
            if confParser.has_option(cnfSec, cnfName):
                return confParser.get(cnfSec, cnfName)
        return cnfDefault

# End Class GuiTheme

# =============================================================================================== #
#  Icons Class
# =============================================================================================== #

class GuiIcons:
    """The icon class manages the content of the assets/icons folder,
    and provides a simple interface for requesting icons. Only icons
    listed in the ICON_MAP are handled.

    Icons are loaded on first request, and then cached for further
    requests. Each icon key in the ICON_MAP has a series of fallbacks:
      * The first lookup is in the key-to-file map for the selected icon
        theme. The map is specified in the icons.conf file in the theme
        folder. The map makes it possible to preserve the original file
        name from the icon theme were the icons were extracted.
      * Second, if the icon does not exist in the theme map, the
        GuiIcons class will check if there is a QStyle icon specified in
        the ICON_MAP data tuple[0]. This will let Qt pull the closest
        system icon.
      * Third action is to look up the freedesktop icon theme name using
        the fromTheme Qt call. This generally produces the same results
        as the step above, but has more icons available in other cases.
      * Fourth, and finally, the icon is looked up in the fallback
        folder. Files in this folder must have the same file name as the
        novelWriter internal icon key, with '-dark' appended to it for
        the dark background version of the icon.
    """

    ICON_MAP = {
        # Project and GUI icons
        "novelwriter"     : (None, None),
        "cls_none"        : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "cls_novel"       : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "cls_plot"        : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "cls_character"   : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "cls_world"       : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "cls_timeline"    : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "cls_object"      : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "cls_entity"      : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "cls_custom"      : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "cls_archive"     : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "cls_trash"       : (QStyle.SP_DriveHDIcon, "drive-harddisk"),
        "proj_document"   : (QStyle.SP_FileIcon,    "x-office-document"),
        "proj_folder"     : (QStyle.SP_DirIcon,     "folder"),
        "proj_nwx"        : (None, None),
        "status_lang"     : (None, None),
        "status_time"     : (None, None),
        "status_stats"    : (None, None),
        "status_lines"    : (None, None),
        "doc_h1"          : (QStyle.SP_FileIcon, "x-office-document"),
        "doc_h2"          : (QStyle.SP_FileIcon, "x-office-document"),
        "doc_h3"          : (QStyle.SP_FileIcon, "x-office-document"),
        "doc_h4"          : (QStyle.SP_FileIcon, "x-office-document"),
        "search_case"     : (None, None),
        "search_regex"    : (None, None),
        "search_word"     : (None, None),
        "search_loop"     : (None, None),
        "search_project"  : (None, None),
        "search_cancel"   : (None, None),
        "search_preserve" : (None, None),

        ## General Button Icons
        "folder-open"    : (QStyle.SP_DirOpenIcon,         "folder-open"),
        "delete"         : (QStyle.SP_DialogDiscardButton, "edit-delete"),
        "close"          : (QStyle.SP_DialogCloseButton,   "window-close"),
        "done"           : (QStyle.SP_DialogApplyButton,    None),
        "clear"          : (QStyle.SP_LineEditClearButton, "clear_left"),
        "save"           : (QStyle.SP_DialogSaveButton,    "document-save"),
        "add"            : (None, "list-add"),
        "remove"         : (None, "list-remove"),
        "search"         : (None, "edit-find"),
        "search-replace" : (None, "edit-find-replace"),
        "edit"           : (None, None),
        "check"          : (None, None),
        "cross"          : (None, None),
        "hash"           : (None, None),
        "maximise"       : (None, None),
        "minimise"       : (None, None),
        "refresh"        : (None, None),
        "reference"      : (None, None),
        "backward"       : (None, None),
        "forward"        : (None, None),

        ## Switches
        "sticky-on"  : (None, None),
        "sticky-off" : (None, None),
        "bullet-on"  : (None, None),
        "bullet-off" : (None, None),
    }

    DECO_MAP = {
        "wiz-back" : "wizard-back.jpg",
    }

    def __init__(self, theParent):

        self.mainConf  = nw.CONFIG
        self.theParent = theParent

        # Storage
        self.qIcons    = {}
        self.themeMap  = {}
        self.themeList = []
        self.fbackName = "fallback"
        self.confName  = "icons.conf"

        # Icon Theme Path
        self.iconPath = None
        self.confFile = None

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

        logger.debug("Loading icon theme files")

        self.themeMap = {}
        checkPath = os.path.join(self.mainConf.iconPath, self.mainConf.guiIcons)
        if os.path.isdir(checkPath):
            logger.debug("Loading icon theme '%s'" % self.mainConf.guiIcons)
            self.iconPath = checkPath
            self.confFile = os.path.join(checkPath, self.confName)
        else:
            return False

        # Config File
        confParser = configparser.ConfigParser()
        try:
            with open(self.confFile, mode="r", encoding="utf8") as inFile:
                confParser.read_file(inFile)
        except Exception as e:
            logger.error("Could not load icon theme settings from: %s" % self.confFile)
            logger.error(str(e))
            return False

        ## Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.themeName        = self._parseLine(confParser, cnfSec, "name", "")
            self.themeDescription = self._parseLine(confParser, cnfSec, "description", "")
            self.themeAuthor      = self._parseLine(confParser, cnfSec, "author", "N/A")
            self.themeCredit      = self._parseLine(confParser, cnfSec, "credit", "N/A")
            self.themeUrl         = self._parseLine(confParser, cnfSec, "url", "")
            self.themeLicense     = self._parseLine(confParser, cnfSec, "license", "N/A")
            self.themeLicenseUrl  = self._parseLine(confParser, cnfSec, "licenseurl", "")

        ## Palette
        cnfSec = "Map"
        if confParser.has_section(cnfSec):
            for iconName, iconFile in confParser.items(cnfSec):
                if iconName not in self.ICON_MAP:
                    logger.error("Unknown icon name '%s' in config file" % iconName)
                else:
                    iconPath = os.path.join(self.iconPath, iconFile)
                    if os.path.isfile(iconPath):
                        self.themeMap[iconName] = iconPath
                        logger.verbose("Icon slot '%s' using file '%s'" % (iconName, iconFile))
                    else:
                        logger.error("Icon file '%s' not in theme folder" % iconFile)

        logger.info("Loaded icon theme '%s'" % self.mainConf.guiIcons)

        return True

    ##
    #  Access Functions
    ##

    def loadDecoration(self, decoKey, pxW, pxH):
        """Load graphical decoration element based on the decoration
        map. This function always returns a QSwgWidget.
        """
        if decoKey not in self.DECO_MAP:
            logger.error("Decoration with name '%s' does not exist" % decoKey)
            return QPixmap()

        imgPath = os.path.join(
            self.mainConf.assetPath, "images", self.DECO_MAP[decoKey]
        )
        if not os.path.isfile(imgPath):
            logger.error("Decoration file '%s' not in assets folder" % self.DECO_MAP[decoKey])
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
        if iconKey in self.qIcons:
            return self.qIcons[iconKey]
        else:
            qIcon = self._loadIcon(iconKey)
            self.qIcons[iconKey] = qIcon
            return qIcon

    def getPixmap(self, iconKey, iconSize):
        """Return an icon from the icon buffer as a QPixmap. If it
        doesn't exist, return an empty QPixmap.
        """
        qIcon = self.getIcon(iconKey)
        return qIcon.pixmap(iconSize[0], iconSize[1], QIcon.Normal)

    def listThemes(self):
        """Scan the icons themes folder and list all themes.
        """
        if self.themeList:
            return self.themeList

        confParser = configparser.ConfigParser()
        for themeDir in os.listdir(self.mainConf.iconPath):
            themePath = os.path.join(self.mainConf.iconPath, themeDir)
            if not os.path.isdir(themePath) or themeDir == self.fbackName:
                continue
            themeConf = os.path.join(themePath, self.confName)
            logger.verbose("Checking icon theme config for '%s'" % themeDir)
            try:
                with open(themeConf, mode="r", encoding="utf8") as inFile:
                    confParser.read_file(inFile)
            except Exception as e:
                self.theParent.makeAlert(
                    ["Could not load theme config file.", str(e)], nwAlert.ERROR
                )
                continue
            themeName = ""
            if confParser.has_section("Main"):
                if confParser.has_option("Main", "name"):
                    themeName = confParser.get("Main", "name")
                    logger.verbose("Theme name is '%s'" % themeName)
            if themeName != "":
                self.themeList.append((themeDir, themeName))

        self.themeList = sorted(self.themeList, key=lambda x: x[1])

        return self.themeList

    ##
    #  Internal Functions
    ##

    def _loadIcon(self, iconKey):
        """Load an icon from the assets or theme folder, with a
        preference for dark/light icons depending on theme type, if such
        an icon exists. Prefer svg files over png files. Always returns
        a QIcon.
        """
        if iconKey not in self.ICON_MAP:
            logger.error("Requested unknown icon name '%s'" % iconKey)
            return QIcon()

        # If we just want the app icon, return it right away
        if iconKey == "novelwriter":
            return QIcon(os.path.join(self.mainConf.iconPath, "novelwriter.svg"))

        # Otherwise, we start looking for it
        # First in the theme folder
        if iconKey in self.themeMap:
            relPath = os.path.relpath(self.themeMap[iconKey], self.mainConf.iconPath)
            logger.verbose("Loading: %s" % relPath)
            return QIcon(self.themeMap[iconKey])

        # Next, we try to load the Qt style icons
        if self.ICON_MAP[iconKey][0] is not None:
            logger.verbose("Loading icon '%s' from Qt QStyle.standardIcon" % iconKey)
            return qApp.style().standardIcon(self.ICON_MAP[iconKey][0])

        # If we're still here, try to set from system theme
        if self.ICON_MAP[iconKey][1] is not None:
            logger.verbose("Loading icon '%s' from system theme" % iconKey)
            if QIcon().hasThemeIcon(self.ICON_MAP[iconKey][1]):
                return QIcon().fromTheme(self.ICON_MAP[iconKey][1])

        # Finally. we check if we have a fallback icon
        if self.mainConf.guiDark:
            fbackIcon = os.path.join(
                self.mainConf.iconPath, self.fbackName, "%s-dark.svg" % iconKey
            )
            if os.path.isfile(fbackIcon):
                logger.verbose("Loading icon '%s' from fallback theme (dark mode)" % iconKey)
                return QIcon(fbackIcon)
        fbackIcon = os.path.join(self.mainConf.iconPath, self.fbackName, "%s.svg" % iconKey)
        if os.path.isfile(fbackIcon):
            logger.verbose("Loading icon '%s' from fallback theme (light mode)" % iconKey)
            return QIcon(fbackIcon)

        # Give up and return an empty icon
        logger.warning("Did not load an icon for '%s'" % iconKey)

        return QIcon()

    def _parseLine(self, confParser, cnfSec, cnfName, cnfDefault):
        """Simple wrapper for the config parser check for entry existing
        before arrempting to load.
        """
        if confParser.has_section(cnfSec):
            if confParser.has_option(cnfSec, cnfName):
                return confParser.get(cnfSec, cnfName)
        return cnfDefault

# END Class GuiIcons
