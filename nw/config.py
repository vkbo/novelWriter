# -*- coding: utf-8 -*-
"""novelWriter Config Class

 novelWriter – Config Class
============================
 This class reads and store the main preferences of the application

 File History:
 Created: 2018-09-22 [0.0.1]

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
import json
import sys
import nw

from os import path, mkdir, unlink, rename
from time import time

from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtCore import QT_VERSION_STR, QStandardPaths, QSysInfo

from nw.constants import nwFiles, nwUnicode
from nw.common import splitVersionNumber, formatTimeStamp

logger = logging.getLogger(__name__)

class Config:

    CNF_STR  = 0
    CNF_INT  = 1
    CNF_BOOL = 2
    CNF_LIST = 3

    def __init__(self):

        # Set Application Variables
        self.appName   = nw.__package__
        self.appHandle = nw.__package__.lower()
        self.showGUI   = True
        self.debugInfo = False
        self.cmdOpen   = None

        # Config Error Handling
        self.hasError  = False
        self.errData   = []

        # Set Paths
        self.confPath  = None
        self.confFile  = None
        self.dataPath  = None
        self.homePath  = None
        self.lastPath  = None
        self.appPath   = None
        self.appRoot   = None
        self.appIcon   = None
        self.assetPath = None
        self.themeRoot = None
        self.graphPath = None
        self.dictPath  = None
        self.iconPath  = None

        # Set default values
        self.confChanged = False

        ## General
        self.guiTheme    = "default"
        self.guiSyntax   = "default_light"
        self.guiIcons    = "typicons_grey_light"
        self.guiDark     = False
        self.guiLang     = "en" # Hardcoded for now
        self.guiFont     = ""
        self.guiFontSize = 11

        ## Sizes
        self.winGeometry  = [1100, 650]
        self.treeColWidth = [120, 30, 50]
        self.projColWidth = [140, 55, 140]
        self.mainPanePos  = [300, 800]
        self.docPanePos   = [400, 400]
        self.isFullScreen = False

        ## Project
        self.autoSaveProj = 60
        self.autoSaveDoc  = 30

        ## Text Editor
        self.textFont        = None
        self.textSize        = 12
        self.textFixedW      = True
        self.textWidth       = 600
        self.textMargin      = 40
        self.tabWidth        = 40
        self.zenWidth        = 800
        self.doJustify       = False
        self.autoSelect      = True
        self.doReplace       = True
        self.doReplaceSQuote = True
        self.doReplaceDQuote = True
        self.doReplaceDash   = True
        self.doReplaceDots   = True
        self.wordCountTimer  = 5.0
        self.showTabsNSpaces = False
        self.showLineEndings = False
        self.bigDocLimit     = 800
        self.showFullPath    = True
        self.highlightQuotes = True

        self.fmtApostrophe   = nwUnicode.U_RSQUO
        self.fmtSingleQuotes = [nwUnicode.U_LSQUO,nwUnicode.U_RSQUO]
        self.fmtDoubleQuotes = [nwUnicode.U_LDQUO,nwUnicode.U_RDQUO]

        self.spellTool     = None
        self.spellLanguage = None

        ## Backup
        self.backupPath      = ""
        self.backupOnClose   = False
        self.askBeforeBackup = True

        ## State
        self.showRefPanel = True
        self.viewComments = True

        # Check Qt5 Versions
        verQt = splitVersionNumber(QT_VERSION_STR)
        self.verQtString = QT_VERSION_STR
        self.verQtMajor  = verQt[0]
        self.verQtMinor  = verQt[1]
        self.verQtPatch  = verQt[2]
        self.verQtValue  = verQt[3]

        verQt = splitVersionNumber(PYQT_VERSION_STR)
        self.verPyQtString = PYQT_VERSION_STR
        self.verPyQtMajor  = verQt[0]
        self.verPyQtMinor  = verQt[1]
        self.verPyQtPatch  = verQt[2]
        self.verPyQtValue  = verQt[3]

        # Check Python Version
        self.verPyString = sys.version.split()[0]
        self.verPyMajor  = sys.version_info[0]
        self.verPyMinor  = sys.version_info[1]
        self.verPyPatch  = sys.version_info[2]
        self.verPyHexVal = sys.hexversion

        # Check OS Type
        self.osType    = sys.platform
        self.osLinux   = False
        self.osWindows = False
        self.osDarwin  = False
        self.osUnknown = False
        if self.osType.startswith("linux"):
            self.osLinux = True
        elif self.osType.startswith("darwin"):
            self.osDarwin = True
        elif self.osType.startswith("win32"):
            self.osWindows = True
        elif self.osType.startswith("cygwin"):
            self.osWindows = True
        else:
            self.osUnknown = True

        # Other System Info
        if self.verQtValue >= 50600:
            self.hostName  = QSysInfo.machineHostName()
            self.kernelVer = QSysInfo.kernelVersion()
        else:
            self.hostName  = "Unknown"
            self.kernelVer = "Unknown"

        # Packages
        self.hasEnchant  = False
        self.hasSymSpell = False

        # Recent Cache
        self.recentProj = {}

        return

    ##
    #  Actions
    ##

    def initConfig(self, confPath=None, dataPath=None):
        """Initialise the config class. The manual setting of confPath
        and dataPath is mainly intended for the test suite.
        """
        if confPath is None:
            confRoot = QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)
            self.confPath = path.join(path.abspath(confRoot), self.appHandle)
        else:
            logger.info("Setting config from alternative path: %s" % confPath)
            self.confPath = confPath

        if dataPath is None:
            if self.verQtValue >= 50400:
                dataRoot = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            else:
                dataRoot = QStandardPaths.writableLocation(QStandardPaths.DataLocation)
            self.dataPath = path.join(path.abspath(dataRoot), self.appHandle)
        else:
            logger.info("Setting data path from alternative path: %s" % dataPath)
            self.dataPath = dataPath

        logger.verbose("Config path: %s" % self.confPath)
        logger.verbose("Data path: %s" % self.dataPath)

        self.confFile  = self.appHandle+".conf"
        self.homePath  = path.expanduser("~")
        self.lastPath  = self.homePath
        self.appPath   = getattr(sys, "_MEIPASS", path.abspath(path.dirname(__file__)))
        self.appRoot   = path.join(self.appPath,path.pardir)
        self.assetPath = path.join(self.appPath,"assets")
        self.themeRoot = path.join(self.assetPath,"themes")
        self.graphPath = path.join(self.assetPath,"graphics")
        self.dictPath  = path.join(self.assetPath,"dict")
        self.iconPath  = path.join(self.assetPath,"icons")
        self.appIcon   = path.join(self.iconPath, "novelwriter.svg")

        logger.verbose("App path: %s" % self.appPath)
        logger.verbose("Home path: %s" % self.homePath)

        # If config folder does not exist, make it.
        # This assumes that the os config folder itself exists.
        if not path.isdir(self.confPath):
            try:
                mkdir(self.confPath)
            except Exception as e:
                logger.error("Could not create folder: %s" % self.confPath)
                logger.error(str(e))
                self.hasError = True
                self.errData.append("Could not create folder: %s" % self.confPath)
                self.errData.append(str(e))
                self.confPath = None

        # Check if config file exists
        if self.confPath is not None:
            if path.isfile(path.join(self.confPath,self.confFile)):
                # If it exists, load it
                self.loadConfig()
            else:
                # If it does not exist, save a copy of the default values
                self.saveConfig()

        # If data folder does not exist, make it.
        # This assumes that the os data folder itself exists.
        if self.dataPath is not None:
            if not path.isdir(self.dataPath):
                try:
                    mkdir(self.dataPath)
                except Exception as e:
                    logger.error("Could not create folder: %s" % self.dataPath)
                    logger.error(str(e))
                    self.hasError = True
                    self.errData.append("Could not create folder: %s" % self.dataPath)
                    self.errData.append(str(e))
                    self.dataPath = None

        # Load recent projects cache
        self.loadRecentCache()

        # Check the availability of optional packages
        self._checkOptionalPackages()

        if self.spellTool is None:
            self.spellTool = "internal"
        if self.spellLanguage is None:
            self.spellLanguage = "en"

        return True

    def loadConfig(self):
        """Load preferences from file and replace default settings.
        """
        logger.debug("Loading config file")
        cnfParse = configparser.ConfigParser()
        try:
            cnfParse.read_file(
                open(path.join(self.confPath,self.confFile),mode="r",encoding="utf8")
            )
        except Exception as e:
            logger.error("Could not load config file")
            logger.error(str(e))
            self.hasError = True
            self.errData.append("Could not load config file")
            self.errData.append(str(e))
            return False

        ## Main
        cnfSec = "Main"
        self.guiTheme = self._parseLine(
            cnfParse, cnfSec, "theme", self.CNF_STR, self.guiTheme
        )
        self.guiSyntax = self._parseLine(
            cnfParse, cnfSec, "syntax", self.CNF_STR, self.guiSyntax
        )
        self.guiIcons = self._parseLine(
            cnfParse, cnfSec, "icons", self.CNF_STR, self.guiIcons
        )
        self.guiDark = self._parseLine(
            cnfParse, cnfSec, "guidark", self.CNF_BOOL, self.guiDark
        )
        self.guiFont = self._parseLine(
            cnfParse, cnfSec, "guifont", self.CNF_STR, self.guiFont
        )
        self.guiFontSize = self._parseLine(
            cnfParse, cnfSec, "guifontsize", self.CNF_INT, self.guiFontSize
        )

        ## Sizes
        cnfSec = "Sizes"
        self.winGeometry = self._parseLine(
            cnfParse, cnfSec, "geometry", self.CNF_LIST, self.winGeometry
        )
        self.treeColWidth = self._parseLine(
            cnfParse, cnfSec, "treecols", self.CNF_LIST, self.treeColWidth
        )
        self.projColWidth = self._parseLine(
            cnfParse, cnfSec, "projcols", self.CNF_LIST, self.projColWidth
        )
        self.mainPanePos = self._parseLine(
            cnfParse, cnfSec, "mainpane", self.CNF_LIST, self.mainPanePos
        )
        self.docPanePos = self._parseLine(
            cnfParse, cnfSec, "docpane", self.CNF_LIST, self.docPanePos
        )
        self.isFullScreen = self._parseLine(
            cnfParse, cnfSec, "fullscreen", self.CNF_BOOL, self.isFullScreen
        )

        ## Project
        cnfSec = "Project"
        self.autoSaveProj = self._parseLine(
            cnfParse, cnfSec, "autosaveproject", self.CNF_INT, self.autoSaveProj
        )
        self.autoSaveDoc = self._parseLine(
            cnfParse, cnfSec, "autosavedoc", self.CNF_INT, self.autoSaveDoc
        )

        ## Editor
        cnfSec = "Editor"
        self.textFont = self._parseLine(
            cnfParse, cnfSec, "textfont", self.CNF_STR, self.textFont
        )
        self.textSize = self._parseLine(
            cnfParse, cnfSec, "textsize", self.CNF_INT, self.textSize
        )
        self.textFixedW = self._parseLine(
            cnfParse, cnfSec, "fixedwidth", self.CNF_BOOL, self.textFixedW
        )
        self.textWidth = self._parseLine(
            cnfParse, cnfSec, "width", self.CNF_INT, self.textWidth
        )
        self.textMargin = self._parseLine(
            cnfParse, cnfSec, "margin", self.CNF_INT, self.textMargin
        )
        self.tabWidth = self._parseLine(
            cnfParse, cnfSec, "tabwidth", self.CNF_INT, self.tabWidth
        )
        self.zenWidth = self._parseLine(
            cnfParse, cnfSec, "zenwidth", self.CNF_INT, self.zenWidth
        )
        self.doJustify = self._parseLine(
            cnfParse, cnfSec, "justify", self.CNF_BOOL, self.doJustify
        )
        self.autoSelect = self._parseLine(
            cnfParse, cnfSec, "autoselect", self.CNF_BOOL, self.autoSelect
        )
        self.doReplace = self._parseLine(
            cnfParse, cnfSec, "autoreplace", self.CNF_BOOL, self.doReplace
        )
        self.doReplaceSQuote = self._parseLine(
            cnfParse, cnfSec, "repsquotes", self.CNF_BOOL, self.doReplaceSQuote
        )
        self.doReplaceDQuote = self._parseLine(
            cnfParse, cnfSec, "repdquotes", self.CNF_BOOL, self.doReplaceDQuote
        )
        self.doReplaceDash = self._parseLine(
            cnfParse, cnfSec, "repdash", self.CNF_BOOL, self.doReplaceDash
        )
        self.doReplaceDots = self._parseLine(
            cnfParse, cnfSec, "repdots", self.CNF_BOOL, self.doReplaceDots
        )
        self.fmtSingleQuotes = self._parseLine(
            cnfParse, cnfSec, "fmtsinglequote", self.CNF_LIST, self.fmtSingleQuotes
        )
        self.fmtDoubleQuotes = self._parseLine(
            cnfParse, cnfSec, "fmtdoublequote", self.CNF_LIST, self.fmtDoubleQuotes
        )
        self.spellTool = self._parseLine(
            cnfParse, cnfSec, "spelltool", self.CNF_STR, self.spellTool
        )
        self.spellLanguage = self._parseLine(
            cnfParse, cnfSec, "spellcheck", self.CNF_STR, self.spellLanguage
        )
        self.showTabsNSpaces = self._parseLine(
            cnfParse, cnfSec, "showtabsnspaces", self.CNF_BOOL, self.showTabsNSpaces
        )
        self.showLineEndings = self._parseLine(
            cnfParse, cnfSec, "showlineendings", self.CNF_BOOL, self.showLineEndings
        )
        self.bigDocLimit = self._parseLine(
            cnfParse, cnfSec, "bigdoclimit", self.CNF_INT, self.bigDocLimit
        )
        self.showFullPath = self._parseLine(
            cnfParse, cnfSec, "showfullpath", self.CNF_BOOL, self.showFullPath
        )
        self.highlightQuotes = self._parseLine(
            cnfParse, cnfSec, "highlightquotes", self.CNF_BOOL, self.highlightQuotes
        )

        ## Backup
        cnfSec = "Backup"
        self.backupPath = self._parseLine(
            cnfParse, cnfSec, "backuppath", self.CNF_STR, self.backupPath
        )
        self.backupOnClose = self._parseLine(
            cnfParse, cnfSec, "backuponclose", self.CNF_BOOL, self.backupOnClose
        )
        self.askBeforeBackup = self._parseLine(
            cnfParse, cnfSec, "askbeforebackup", self.CNF_BOOL, self.askBeforeBackup
        )

        ## State
        cnfSec = "State"
        self.showRefPanel = self._parseLine(
            cnfParse, cnfSec, "showrefpanel", self.CNF_BOOL, self.showRefPanel
        )
        self.viewComments = self._parseLine(
            cnfParse, cnfSec, "viewcomments", self.CNF_BOOL, self.viewComments
        )

        ## Path
        cnfSec = "Path"
        self.lastPath = self._parseLine(
            cnfParse, cnfSec, "lastpath", self.CNF_STR, self.lastPath
        )

        # Check Certain Values for None
        self.spellLanguage = self._checkNone(self.spellLanguage)

        return True

    def saveConfig(self):
        """Save the current preferences to file.
        """
        logger.debug("Saving config file")
        cnfParse = configparser.ConfigParser()

        # Set options

        ## Main
        cnfSec = "Main"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec,"timestamp",   formatTimeStamp(time()))
        cnfParse.set(cnfSec,"theme",       str(self.guiTheme))
        cnfParse.set(cnfSec,"syntax",      str(self.guiSyntax))
        cnfParse.set(cnfSec,"icons",       str(self.guiIcons))
        cnfParse.set(cnfSec,"guidark",     str(self.guiDark))
        cnfParse.set(cnfSec,"guifont",     str(self.guiFont))
        cnfParse.set(cnfSec,"guifontsize", str(self.guiFontSize))

        ## Sizes
        cnfSec = "Sizes"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec,"geometry",   self._packList(self.winGeometry))
        cnfParse.set(cnfSec,"treecols",   self._packList(self.treeColWidth))
        cnfParse.set(cnfSec,"projcols",   self._packList(self.projColWidth))
        cnfParse.set(cnfSec,"mainpane",   self._packList(self.mainPanePos))
        cnfParse.set(cnfSec,"docpane",    self._packList(self.docPanePos))
        cnfParse.set(cnfSec,"fullscreen", str(self.isFullScreen))

        ## Project
        cnfSec = "Project"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec,"autosaveproject", str(self.autoSaveProj))
        cnfParse.set(cnfSec,"autosavedoc",     str(self.autoSaveDoc))

        ## Editor
        cnfSec = "Editor"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec,"textfont",        str(self.textFont))
        cnfParse.set(cnfSec,"textsize",        str(self.textSize))
        cnfParse.set(cnfSec,"fixedwidth",      str(self.textFixedW))
        cnfParse.set(cnfSec,"width",           str(self.textWidth))
        cnfParse.set(cnfSec,"margin",          str(self.textMargin))
        cnfParse.set(cnfSec,"tabwidth",        str(self.tabWidth))
        cnfParse.set(cnfSec,"zenwidth",        str(self.zenWidth))
        cnfParse.set(cnfSec,"justify",         str(self.doJustify))
        cnfParse.set(cnfSec,"autoselect",      str(self.autoSelect))
        cnfParse.set(cnfSec,"autoreplace",     str(self.doReplace))
        cnfParse.set(cnfSec,"repsquotes",      str(self.doReplaceSQuote))
        cnfParse.set(cnfSec,"repdquotes",      str(self.doReplaceDQuote))
        cnfParse.set(cnfSec,"repdash",         str(self.doReplaceDash))
        cnfParse.set(cnfSec,"repdots",         str(self.doReplaceDots))
        cnfParse.set(cnfSec,"fmtsinglequote",  self._packList(self.fmtSingleQuotes))
        cnfParse.set(cnfSec,"fmtdoublequote",  self._packList(self.fmtDoubleQuotes))
        cnfParse.set(cnfSec,"spelltool",       str(self.spellTool))
        cnfParse.set(cnfSec,"spellcheck",      str(self.spellLanguage))
        cnfParse.set(cnfSec,"showtabsnspaces", str(self.showTabsNSpaces))
        cnfParse.set(cnfSec,"showlineendings", str(self.showLineEndings))
        cnfParse.set(cnfSec,"bigdoclimit",     str(self.bigDocLimit))
        cnfParse.set(cnfSec,"showfullpath",    str(self.showFullPath))
        cnfParse.set(cnfSec,"highlightquotes", str(self.highlightQuotes))

        ## Backup
        cnfSec = "Backup"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec,"backuppath",     str(self.backupPath))
        cnfParse.set(cnfSec,"backuponclose",  str(self.backupOnClose))
        cnfParse.set(cnfSec,"askbeforebackup",str(self.askBeforeBackup))

        ## State
        cnfSec = "State"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec,"showrefpanel",str(self.showRefPanel))
        cnfParse.set(cnfSec,"viewcomments",str(self.viewComments))

        ## Path
        cnfSec = "Path"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec,"lastpath", str(self.lastPath))

        # Write config file
        try:
            cnfParse.write(
                open(path.join(self.confPath, self.confFile), mode="w", encoding="utf8")
            )
            self.confChanged = False
        except Exception as e:
            logger.error("Could not save config file")
            logger.error(str(e))
            self.hasError = True
            self.errData.append("Could not save config file")
            self.errData.append(str(e))
            return False

        return True

    def loadRecentCache(self):
        """Load the cache file for recent projects.
        """
        if self.dataPath is None:
            return False

        cacheFile = path.join(self.dataPath, nwFiles.RECENT_FILE)
        self.recentProj = {}

        if path.isfile(cacheFile):
            try:
                with open(cacheFile, mode="r", encoding="utf8") as inFile:
                    theJson = inFile.read()
                theData = json.loads(theJson)

                for projPath in theData.keys():
                    theEntry  = theData[projPath]
                    theTitle  = ""
                    lastTime  = 0
                    wordCount = 0
                    if "title" in theEntry.keys():
                        theTitle = theEntry["title"]
                    if "time" in theEntry.keys():
                        lastTime = int(theEntry["time"])
                    if "words" in theEntry.keys():
                        wordCount = int(theEntry["words"])
                    self.recentProj[projPath] = {
                        "title" : theTitle,
                        "time"  : lastTime,
                        "words" : wordCount,
                    }

            except Exception as e:
                self.hasError = True
                self.errData.append("Could not load recent project cache")
                self.errData.append(str(e))
                return False

        return True

    def saveRecentCache(self):
        """Save the cache dictionary of recent projects.
        """
        if self.dataPath is None:
            return False

        cacheFile = path.join(self.dataPath, nwFiles.RECENT_FILE)
        cacheTemp = path.join(self.dataPath, nwFiles.RECENT_FILE+"~")

        try:
            with open(cacheTemp, mode="w+", encoding="utf8") as outFile:
                outFile.write(json.dumps(self.recentProj, indent=2))
        except Exception as e:
            self.hasError = True
            self.errData.append("Could not save recent project cache")
            self.errData.append(str(e))
            return False

        if path.isfile(cacheFile):
            unlink(cacheFile)
        rename(cacheTemp, cacheFile)

        return True

    def updateRecentCache(self, projPath, projTitle, wordCount, saveTime):
        """Add or update recent cache information o9n a given project.
        """
        self.recentProj[path.abspath(projPath)] = {
            "title" : projTitle,
            "time"  : int(saveTime),
            "words" : int(wordCount),
        }
        return True

    def removeFromRecentCache(self, thePath):
        """Trying to remove a path from the recent projects cache.
        """
        if thePath in self.recentProj:
            del self.recentProj[thePath]
            logger.verbose("Removed recent: %s" % thePath)
            self.saveRecentCache()
        else:
            logger.error("Unknown recent: %s" % thePath)
            return False
        return True

    ##
    #  Setters and Getters
    ##

    def setConfPath(self, newPath):
        if newPath is None:
            return True
        if not path.isfile(newPath):
            logger.error("File not found, using default config path instead")
            return False
        self.confPath = path.dirname(newPath)
        self.confFile = path.basename(newPath)
        return True

    def setDataPath(self, newPath):
        if newPath is None:
            return True
        if not path.isdir(newPath):
            logger.error("Path not found, using default data path instead")
            return False
        self.dataPath = path.abspath(newPath)
        return True

    def setLastPath(self, lastPath):
        if lastPath is None or lastPath == "":
            self.lastPath = ""
        else:
            self.lastPath = path.dirname(lastPath)
        return True

    def setWinSize(self, newWidth, newHeight):
        if abs(self.winGeometry[0] - newWidth) > 5:
            self.winGeometry[0] = newWidth
            self.confChanged = True
        if abs(self.winGeometry[1] - newHeight) > 5:
            self.winGeometry[1] = newHeight
            self.confChanged = True
        return True

    def setTreeColWidths(self, colWidths):
        self.treeColWidth = colWidths
        self.confChanged = True
        return True

    def setProjColWidths(self, colWidths):
        self.projColWidth = colWidths
        self.confChanged = True
        return True

    def setMainPanePos(self, panePos):
        self.mainPanePos = panePos
        self.confChanged = True
        return True

    def setDocPanePos(self, panePos):
        self.docPanePos  = panePos
        self.confChanged = True
        return True

    def setShowRefPanel(self, checkState):
        self.showRefPanel = checkState
        self.confChanged  = True
        return self.showRefPanel

    def setViewComments(self, checkState):
        self.viewComments = checkState
        self.confChanged  = True
        return self.viewComments

    def getErrData(self):
        errMessage = "<br>".join(self.errData)
        self.hasError = False
        self.errData = []
        return errMessage

    ##
    #  Internal Functions
    ##

    def _unpackList(self, inStr, listLen, listDefault, castTo=int):
        inData  = inStr.split(",")
        outData = []
        for i in range(listLen):
            try:
                outData.append(castTo(inData[i]))
            except:
                outData.append(listDefault[i])
        return outData

    def _packList(self, inData):
        return ", ".join(str(inVal) for inVal in inData)

    def _parseLine(self, cnfParse, cnfSec, cnfName, cnfType, cnfDefault):
        if cnfParse.has_section(cnfSec):
            if cnfParse.has_option(cnfSec, cnfName):
                if cnfType == self.CNF_STR:
                    return cnfParse.get(cnfSec, cnfName)
                elif cnfType == self.CNF_INT:
                    return cnfParse.getint(cnfSec, cnfName)
                elif cnfType == self.CNF_BOOL:
                    return cnfParse.getboolean(cnfSec, cnfName)
                elif cnfType == self.CNF_LIST:
                    return self._unpackList(
                        cnfParse.get(cnfSec, cnfName), len(cnfDefault), cnfDefault
                    )
        return cnfDefault

    def _checkNone(self, checkVal):
        if checkVal is None:
            return None
        if isinstance(checkVal, str):
            if checkVal.lower() == "none":
                return None
        return checkVal

    def _checkOptionalPackages(self):
        """Cheks if we have the optional packages used by some features.
        """
        try:
            import enchant
            self.hasEnchant = True
            logger.debug("Checking package pyenchant: Ok")
        except:
            self.hasEnchant = False
            logger.debug("Checking package pyenchant: Missing")

        return

# End Class Config
