# -*- coding: utf-8 -*-
"""novelWriter Theme Class

 novelWriter – Theme Class
===========================
 This class reads and store the main theme

 File History:
 Created: 2019-05-18 [0.1.3]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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

import logging
import configparser
import nw

from os import path, listdir
from math import ceil

from PyQt5.QtWidgets import qApp
from PyQt5.QtGui import (
    QPalette, QColor, QIcon, QFont, QFontMetrics, QFontDatabase
)

from nw.constants import nwAlert
from nw.gui.icons import GuiIcons

logger = logging.getLogger(__name__)

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
        self.treeWCount  = [  0,  0,  0]
        self.statNone    = [120,120,120]
        self.statUnsaved = [120,120, 40]
        self.statSaved   = [ 40,120,  0]
        self.helpText    = [  0,  0,  0]

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
        self.colBack   = [255,255,255]
        self.colText   = [  0,  0,  0]
        self.colLink   = [  0,  0,  0]
        self.colHead   = [  0,  0,  0]
        self.colHeadH  = [  0,  0,  0]
        self.colEmph   = [  0,  0,  0]
        self.colDialN  = [  0,  0,  0]
        self.colDialD  = [  0,  0,  0]
        self.colDialS  = [  0,  0,  0]
        self.colComm   = [  0,  0,  0]
        self.colKey    = [  0,  0,  0]
        self.colVal    = [  0,  0,  0]
        self.colSpell  = [  0,  0,  0]
        self.colTagErr = [  0,  0,  0]
        self.colRepTag = [  0,  0,  0]
        self.colMod    = [  0,  0,  0]

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
        self.guiDPI = qApp.primaryScreen().physicalDotsPerInch()
        self.guiFont = qApp.font()

        qMetric = QFontMetrics(self.guiFont)
        self.fontPointSize = self.guiFont.pointSizeF()
        self.fontPixelSize = int(round(qMetric.height()))
        self.baseIconSize  = int(round(qMetric.ascent()))
        self.textIconSize  = int(round(qMetric.ascent() + qMetric.leading()))

        logger.verbose("GUI Font Family: %s" % self.guiFont.family())
        logger.verbose("GUI Font Point Size: %.2f" % self.fontPointSize)
        logger.verbose("GUI Font Pixel Size: %d" % self.fontPixelSize)
        logger.verbose("GUI Base Icon Size: %d" % self.baseIconSize)
        logger.verbose("GUI Text Icon Size: %d" % self.textIconSize)

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
        ttfList = []
        fontAssets = path.join(self.mainConf.assetPath, self.fontPath)
        for fontFam in listdir(fontAssets):
            fontDir = path.join(fontAssets, fontFam)
            if path.isdir(fontDir):
                if not fontFam in self.guiFontDB.families():
                    for fontFile in listdir(fontDir):
                        ttfFile = path.join(fontDir, fontFile)
                        if path.isfile(ttfFile) and fontFile.endswith(".ttf"):
                            ttfList.append(ttfFile)

        for ttfFile in ttfList:
            logger.verbose("Font asset: %s" % path.relpath(ttfFile))
            fontID = self.guiFontDB.addApplicationFont(ttfFile)
            if fontID < 0:
                logger.error("Failed to add font: %s" % path.relpath(ttfFile))

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
        self.themePath  = path.join(self.mainConf.themeRoot,self.guiPath,self.guiTheme)
        self.syntaxFile = path.join(self.themeRoot,self.syntaxPath,self.guiSyntax+".conf")
        self.confFile   = path.join(self.themePath,self.confName)
        self.cssFile    = path.join(self.themePath,self.cssName)

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

        logger.debug("Loading theme files")
        logger.debug("System icon theme is '%s'" % str(QIcon.themeName()))

        # CSS File
        cssData = ""
        try:
            if path.isfile(self.cssFile):
                with open(self.cssFile,mode="r",encoding="utf8") as inFile:
                    cssData = inFile.read()
        except Exception as e:
            logger.error("Could not load theme css file")
            return False

        # Config File
        confParser = configparser.ConfigParser()
        try:
            confParser.read_file(open(self.confFile,mode="r",encoding="utf8"))
        except Exception as e:
            logger.error("Could not load theme settings from: %s" % self.confFile)
            return False

        ## Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.themeName        = self._parseLine( confParser, cnfSec, "name", "")
            self.themeDescription = self._parseLine( confParser, cnfSec, "description", "")
            self.themeAuthor      = self._parseLine( confParser, cnfSec, "author", "")
            self.themeCredit      = self._parseLine( confParser, cnfSec, "credit", "")
            self.themeUrl         = self._parseLine( confParser, cnfSec, "url", "")
            self.themeLicense     = self._parseLine( confParser, cnfSec, "license", "")
            self.themeLicenseUrl  = self._parseLine( confParser, cnfSec, "licenseurl", "")

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
            self.treeWCount  = self._loadColour(confParser, cnfSec, "treewordcount")
            self.statNone    = self._loadColour(confParser, cnfSec, "statusnone")
            self.statUnsaved = self._loadColour(confParser, cnfSec, "statusunsaved")
            self.statSaved   = self._loadColour(confParser, cnfSec, "statussaved")

        # Apply Styles
        qApp.setStyleSheet(cssData)
        qApp.setPalette(self.guiPalette)

        logger.info("Loaded theme '%s'" % self.guiTheme)

        return True

    def loadSyntax(self):

        confParser = configparser.ConfigParser()
        try:
            confParser.read_file(open(self.syntaxFile, mode="r", encoding="utf8"))
        except Exception as e:
            logger.error("Could not load syntax colours from: %s" % self.syntaxFile)
            return False

        ## Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.syntaxName        = self._parseLine( confParser, cnfSec, "name", "")
            self.syntaxDescription = self._parseLine( confParser, cnfSec, "description", "")
            self.syntaxAuthor      = self._parseLine( confParser, cnfSec, "author", "")
            self.syntaxCredit      = self._parseLine( confParser, cnfSec, "credit", "")
            self.syntaxUrl         = self._parseLine( confParser, cnfSec, "url", "")
            self.syntaxLicense     = self._parseLine( confParser, cnfSec, "license", "")
            self.syntaxLicenseUrl  = self._parseLine( confParser, cnfSec, "licenseurl", "")

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
            self.colComm   = self._loadColour(confParser, cnfSec, "hidden")
            self.colKey    = self._loadColour(confParser, cnfSec, "keyword")
            self.colVal    = self._loadColour(confParser, cnfSec, "value")
            self.colSpell  = self._loadColour(confParser, cnfSec, "spellcheckline")
            self.colTagErr = self._loadColour(confParser, cnfSec, "tagerror")
            self.colRepTag = self._loadColour(confParser, cnfSec, "replacetag")
            self.colMod    = self._loadColour(confParser, cnfSec, "modifier")

        logger.info("Loaded syntax theme '%s'" % self.guiSyntax)

        return True

    def listThemes(self):
        """Scan the gui themes folder and list all themes.
        """
        if self.themeList:
            return self.themeList

        confParser = configparser.ConfigParser()
        for themeDir in listdir(path.join(self.mainConf.themeRoot, self.guiPath)):
            themeConf = path.join(self.mainConf.themeRoot, self.guiPath, themeDir, self.confName)
            logger.verbose("Checking theme config for '%s'" % themeDir)
            try:
                confParser.read_file(open(themeConf, mode="r", encoding="utf8"))
            except Exception as e:
                self.theParent.makeAlert(
                    ["Could not load theme config file.",str(e)], nwAlert.ERROR
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
        syntaxDir  = path.join(self.mainConf.themeRoot, self.syntaxPath)
        for syntaxFile in listdir(syntaxDir):
            syntaxPath = path.join(syntaxDir, syntaxFile)
            if not path.isfile(syntaxPath):
                continue
            logger.verbose("Checking theme syntax for '%s'" % syntaxFile)
            try:
                confParser.read_file(open(syntaxPath, mode="r", encoding="utf8"))
            except Exception as e:
                self.theParent.makeAlert(
                    ["Could not load syntax file.",str(e)], nwAlert.ERROR
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
        if confParser.has_option(cnfSec,cnfName):
            inData  = confParser.get(cnfSec,cnfName).split(",")
            outData = []
            try:
                outData.append(int(inData[0]))
                outData.append(int(inData[1]))
                outData.append(int(inData[2]))
            except:
                logger.error("Could not load theme colours for '%s' from config file" % cnfName)
                outData = [0,0,0]
        else:
            logger.warning("Could not find theme colours for '%s' in config file" % cnfName)
            outData = [0,0,0]
        return outData

    def _setPalette(self, confParser, cnfSec, cnfName, paletteVal):
        readCol = []
        if confParser.has_option(cnfSec,cnfName):
            inData  = confParser.get(cnfSec,cnfName).split(",")
            try:
                readCol.append(int(inData[0]))
                readCol.append(int(inData[1]))
                readCol.append(int(inData[2]))
            except:
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
