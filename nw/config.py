# -*- coding: utf-8 -*-
"""
novelWriter – Config Class
==========================
Class holding the user preferences and handling the config file

File History:
Created: 2018-09-22 [0.0.1]

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

import logging
import configparser
import shutil
import json
import sys
import os

from time import time

from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtCore import (
    QT_VERSION_STR, QStandardPaths, QSysInfo, QLocale, QLibraryInfo,
    QTranslator
)

from nw.error import logException
from nw.common import splitVersionNumber, formatTimeStamp
from nw.constants import nwConst, nwFiles, nwUnicode

logger = logging.getLogger(__name__)

class Config:

    CNF_STR   = 0
    CNF_INT   = 1
    CNF_BOOL  = 2
    CNF_S_LST = 3
    CNF_I_LST = 4

    LANG_NW   = 1
    LANG_PROJ = 2

    def __init__(self):

        # Set Application Variables
        self.appName   = "novelWriter"
        self.appHandle = self.appName.lower()

        # Config Error Handling
        self.hasError  = False  # True if the config class encountered an error
        self.errData   = []     # List of error messages

        # Set Paths
        self.cmdOpen   = None   # Path from command line for project to be opened on launch
        self.confPath  = None   # Folder where the config is saved
        self.confFile  = None   # The config file name
        self.dataPath  = None   # Folder where app data is stored
        self.lastPath  = None   # The last user-selected folder (browse dialogs)
        self.appPath   = None   # The full path to the novelwriter package folder
        self.appRoot   = None   # The full path to the novelwriter root folder
        self.appIcon   = None   # The full path to the novelwriter icon file
        self.assetPath = None   # The full path to the nw/assets folder
        self.themeRoot = None   # The full path to the nw/assets/themes folder
        self.dictPath  = None   # The full path to the nw/assets/dict folder
        self.iconPath  = None   # The full path to the nw/assets/icons folder
        self.helpPath  = None   # The full path to the novelwriter .qhc help file

        # Runtime Settings and Variables
        self.confChanged = False # True whenever the config has chenged, false after save
        self.hasHelp     = False # True if the Qt help files are present in the assets folder

        ## General
        self.guiTheme    = "default"
        self.guiSyntax   = "default_light"
        self.guiIcons    = "typicons_colour_light"
        self.guiDark     = False # Load icons for dark backgrounds, if available
        self.guiFont     = ""    # Defaults to system default font
        self.guiFontSize = 11    # Is overridden if system default is loaded
        self.guiScale    = 1.0   # Set automatically by Theme class
        self.lastNotes   = "0x0" # The latest release notes that have been shown

        ## Localisation
        self.qLocal     = QLocale.system()
        self.guiLang    = self.qLocal.name()
        self.qtLangPath = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        self.nwLangPath = None
        self.qtTrans    = {}

        ## Sizes
        self.winGeometry   = [1200, 650]
        self.prefGeometry  = [700, 615]
        self.treeColWidth  = [200, 50, 30]
        self.novelColWidth = [200, 50]
        self.projColWidth  = [200, 60, 140]
        self.mainPanePos   = [300, 800]
        self.docPanePos    = [400, 400]
        self.viewPanePos   = [500, 150]
        self.outlnPanePos  = [500, 150]
        self.isFullScreen  = False

        ## Features
        self.hideVScroll = False # Hide vertical scroll bars on main widgets
        self.hideHScroll = False # Hide horizontal scroll bars on main widgets

        ## Project
        self.autoSaveProj = 60 # Interval for auto-saving project in seconds
        self.autoSaveDoc  = 30 # Interval for auto-saving document in seconds

        ## Text Editor
        self.textFont        = None  # Editor font
        self.textSize        = 12    # Editor font size
        self.textFixedW      = True  # Keep editor text fixed width
        self.textWidth       = 600   # Editor text width
        self.textMargin      = 40    # Editor/viewer text margin
        self.tabWidth        = 40    # Editor tabulator width

        self.focusWidth      = 800   # Focus Mode text width
        self.hideFocusFooter = False # Hide document footer in Focus Mode
        self.showFullPath    = True  # Show full document path in editor header
        self.autoSelect      = True  # Auto-select word when applying format with no selection

        self.doJustify       = False # Justify text
        self.showTabsNSpaces = False # Show tabs and spaces in edior
        self.showLineEndings = False # Show line endings in editor

        self.doReplace       = True  # Enable auto-replace as you type
        self.doReplaceSQuote = True  # Smart single quotes
        self.doReplaceDQuote = True  # Smart double quotes
        self.doReplaceDash   = True  # Replace multiple hyphens with dashes
        self.doReplaceDots   = True  # Replace three dots with ellipsis

        self.scrollPastEnd   = True  # Allow scrolling past end of document
        self.autoScroll      = False # Typewriter-like scrolling
        self.autoScrollPos   = 30    # Start point for typewriter-like scrolling

        self.wordCountTimer  = 5.0   # Interval for word count update in seconds
        self.bigDocLimit     = 800   # Size threshold for heavy editor features in kilobytes

        self.highlightQuotes = True  # Highlight text in quotes
        self.allowOpenSQuote = False # Allow open-ended single quotes
        self.allowOpenDQuote = True  # Allow open-ended double quotes
        self.highlightEmph   = True  # Add colour to text emphasis

        self.stopWhenIdle    = True  # Stop the status bar clock when the user is idle
        self.userIdleTime    = 300   # Time of inactivity to consider user idle

        ## User-Selected Symbols
        self.fmtApostrophe   = nwUnicode.U_RSQUO
        self.fmtSingleQuotes = [nwUnicode.U_LSQUO, nwUnicode.U_RSQUO]
        self.fmtDoubleQuotes = [nwUnicode.U_LDQUO, nwUnicode.U_RDQUO]
        self.fmtPadBefore    = ""
        self.fmtPadAfter     = ""
        self.fmtPadThin      = False

        ## Spell Checking
        self.spellTool     = None
        self.spellLanguage = None

        ## Search Bar Switches
        self.searchCase     = False
        self.searchWord     = False
        self.searchRegEx    = False
        self.searchLoop     = False
        self.searchNextFile = False
        self.searchMatchCap = False

        ## Backup
        self.backupPath      = ""
        self.backupOnClose   = False
        self.askBeforeBackup = True

        ## State
        self.showRefPanel = True
        self.viewComments = True
        self.viewSynopsis = True

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
        self.hostName  = "Unknown"
        self.kernelVer = "Unknown"

        # Packages
        self.hasEnchant   = False # The pyenchant package
        self.hasAssistant = False # The Qt Assistant executable

        # Recent Cache
        self.recentProj = {}

        return

    ##
    #  Methods
    ##

    def pxInt(self, theSize):
        """Used to scale fixed gui sizes by the screen scale factor.
        This function returns an int, which is always rounded down.
        """
        return int(theSize*self.guiScale)

    def rpxInt(self, theSize):
        """Used to un-scale fixed gui sizes by the screen scale factor.
        This function returns an int, which is always rounded down.
        """
        return int(theSize/self.guiScale)

    ##
    #  Config Actions
    ##

    def initConfig(self, confPath=None, dataPath=None):
        """Initialise the config class. The manual setting of confPath
        and dataPath is mainly intended for the test suite.
        """
        logger.debug("Initialising Config ...")
        if confPath is None:
            confRoot = QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)
            self.confPath = os.path.join(os.path.abspath(confRoot), self.appHandle)
        else:
            logger.info("Setting config from alternative path: %s" % confPath)
            self.confPath = confPath

        if dataPath is None:
            if self.verQtValue >= 50400:
                dataRoot = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            else:
                dataRoot = QStandardPaths.writableLocation(QStandardPaths.DataLocation)
            self.dataPath = os.path.join(os.path.abspath(dataRoot), self.appHandle)
        else:
            logger.info("Setting data path from alternative path: %s" % dataPath)
            self.dataPath = dataPath

        logger.verbose("Config path: %s" % self.confPath)
        logger.verbose("Data path: %s" % self.dataPath)

        self.confFile = self.appHandle+".conf"
        self.lastPath = os.path.expanduser("~")
        self.appPath = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
        self.appRoot = os.path.abspath(os.path.join(self.appPath, os.path.pardir))

        if os.path.isfile(self.appRoot):
            # novelWriter is packaged as a single file, so the app and
            # root paths are the same, and equal to the folder that
            # contains the single executable.
            self.appRoot = os.path.dirname(self.appRoot)
            self.appPath = self.appRoot

        # Assets
        self.assetPath = os.path.join(self.appPath, "assets")
        self.themeRoot = os.path.join(self.assetPath, "themes")
        self.dictPath  = os.path.join(self.assetPath, "dict")
        self.iconPath  = os.path.join(self.assetPath, "icons")
        self.appIcon   = os.path.join(self.iconPath, "novelwriter.svg")

        # Internationalisation
        self.nwLangPath = os.path.join(self.appRoot, "i18n")

        logger.verbose("App path: %s" % self.appPath)
        logger.verbose("Last path: %s" % self.lastPath)

        # If config folder does not exist, create it.
        # This assumes that the os config folder itself exists.
        if not os.path.isdir(self.confPath):
            try:
                os.mkdir(self.confPath)
            except Exception as e:
                logger.error("Could not create folder: %s" % self.confPath)
                logException()
                self.hasError = True
                self.errData.append("Could not create folder: %s" % self.confPath)
                self.errData.append(str(e))
                self.confPath = None

        # Check if config file exists
        if self.confPath is not None:
            if os.path.isfile(os.path.join(self.confPath, self.confFile)):
                # If it exists, load it
                self.loadConfig()
            else:
                # If it does not exist, save a copy of the default values
                self.saveConfig()

        # If data folder does not exist, make it.
        # This assumes that the os data folder itself exists.
        if self.dataPath is not None:
            if not os.path.isdir(self.dataPath):
                try:
                    os.mkdir(self.dataPath)
                except Exception as e:
                    logger.error("Could not create folder: %s" % self.dataPath)
                    logException()
                    self.hasError = True
                    self.errData.append("Could not create folder: %s" % self.dataPath)
                    self.errData.append(str(e))
                    self.dataPath = None

        # Host and Kernel
        if self.verQtValue >= 50600:
            self.hostName  = QSysInfo.machineHostName()
            self.kernelVer = QSysInfo.kernelVersion()

        # Load recent projects cache
        self.loadRecentCache()

        # Check the availability of optional packages
        self._checkOptionalPackages()

        if self.spellTool is None:
            self.spellTool = nwConst.SP_INTERNAL
        if self.spellLanguage is None:
            self.spellLanguage = "en"

        # Check if local help files exist
        self.helpPath = os.path.join(self.assetPath, "help", "novelWriter.qhc")
        self.hasHelp  = os.path.isfile(self.helpPath)
        self.hasHelp &= os.path.isfile(os.path.join(self.assetPath, "help", "novelWriter.qch"))

        logger.debug("Config initialisation complete")

        return True

    def initLocalisation(self, nwApp):
        """Initialise the localisation of the GUI.
        """
        self.qLocal = QLocale(self.guiLang)
        QLocale.setDefault(self.qLocal)
        self.qtTrans = {}

        langList = [
            (self.qtLangPath, "qtbase"), # Qt 5.x
            (self.nwLangPath, "qtbase"), # Alternative Qt 5.x
            (self.nwLangPath, "nw"),     # novelWriter
        ]
        for lngPath, lngBase in langList:
            for lngCode in self.qLocal.uiLanguages():
                qTrans = QTranslator()
                lngFile = "%s_%s" % (lngBase, lngCode.replace("-", "_"))
                if lngFile not in self.qtTrans:
                    if qTrans.load(lngFile, lngPath):
                        logger.debug("Loaded: %s" % qTrans.filePath())
                        nwApp.installTranslator(qTrans)
                        self.qtTrans[lngFile] = qTrans

        return

    def listLanguages(self, lngSet):
        """List localisation files in the i18n folder. The default GUI
        language 'en_GB' is British English.
        """
        if lngSet == self.LANG_NW:
            fPre = "nw_"
            fExt = ".qm"
            langList = {"en_GB": QLocale("en_GB").nativeLanguageName().title()}
        elif lngSet == self.LANG_PROJ:
            fPre = "project_"
            fExt = ".json"
            langList = {"en": "English"}
        else:
            return []

        for qmFile in os.listdir(self.nwLangPath):
            if not os.path.isfile(os.path.join(self.nwLangPath, qmFile)):
                continue
            if not qmFile.startswith(fPre) or not qmFile.endswith(fExt):
                continue
            qmLang = qmFile[len(fPre):-len(fExt)]
            qmName = QLocale(qmLang).nativeLanguageName().title()
            if qmLang and qmName and qmLang != "en":
                langList[qmLang] = qmName

        return sorted(langList.items(), key=lambda x: x[0])

    def loadConfig(self):
        """Load preferences from file and replace default settings.
        """
        logger.debug("Loading config file")
        if self.confPath is None:
            return False

        cnfParse = configparser.ConfigParser()
        cnfPath  = os.path.join(self.confPath, self.confFile)
        try:
            with open(cnfPath, mode="r", encoding="utf8") as inFile:
                cnfParse.read_file(inFile)
        except Exception as e:
            logger.error("Could not load config file")
            logException()
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
        self.lastNotes = self._parseLine(
            cnfParse, cnfSec, "lastnotes", self.CNF_STR, self.lastNotes
        )
        self.guiLang = self._parseLine(
            cnfParse, cnfSec, "guilang", self.CNF_STR, self.guiLang
        )

        ## Sizes
        cnfSec = "Sizes"
        self.winGeometry = self._parseLine(
            cnfParse, cnfSec, "geometry", self.CNF_I_LST, self.winGeometry
        )
        self.prefGeometry = self._parseLine(
            cnfParse, cnfSec, "preferences", self.CNF_I_LST, self.prefGeometry
        )
        self.treeColWidth = self._parseLine(
            cnfParse, cnfSec, "treecols", self.CNF_I_LST, self.treeColWidth
        )
        self.novelColWidth = self._parseLine(
            cnfParse, cnfSec, "novelcols", self.CNF_I_LST, self.novelColWidth
        )
        self.projColWidth = self._parseLine(
            cnfParse, cnfSec, "projcols", self.CNF_I_LST, self.projColWidth
        )
        self.mainPanePos = self._parseLine(
            cnfParse, cnfSec, "mainpane", self.CNF_I_LST, self.mainPanePos
        )
        self.docPanePos = self._parseLine(
            cnfParse, cnfSec, "docpane", self.CNF_I_LST, self.docPanePos
        )
        self.viewPanePos = self._parseLine(
            cnfParse, cnfSec, "viewpane", self.CNF_I_LST, self.viewPanePos
        )
        self.outlnPanePos = self._parseLine(
            cnfParse, cnfSec, "outlinepane", self.CNF_I_LST, self.outlnPanePos
        )
        self.isFullScreen = self._parseLine(
            cnfParse, cnfSec, "fullscreen", self.CNF_BOOL, self.isFullScreen
        )
        self.hideVScroll = self._parseLine(
            cnfParse, cnfSec, "hidevscroll", self.CNF_BOOL, self.hideVScroll
        )
        self.hideHScroll = self._parseLine(
            cnfParse, cnfSec, "hidehscroll", self.CNF_BOOL, self.hideHScroll
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
        self.focusWidth = self._parseLine(
            cnfParse, cnfSec, "focuswidth", self.CNF_INT, self.focusWidth
        )
        self.hideFocusFooter = self._parseLine(
            cnfParse, cnfSec, "hidefocusfooter", self.CNF_BOOL, self.hideFocusFooter
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
        self.scrollPastEnd = self._parseLine(
            cnfParse, cnfSec, "scrollpastend", self.CNF_BOOL, self.scrollPastEnd
        )
        self.autoScroll = self._parseLine(
            cnfParse, cnfSec, "autoscroll", self.CNF_BOOL, self.autoScroll
        )
        self.autoScrollPos = self._parseLine(
            cnfParse, cnfSec, "autoscrollpos", self.CNF_INT, self.autoScrollPos
        )
        self.fmtSingleQuotes = self._parseLine(
            cnfParse, cnfSec, "fmtsinglequote", self.CNF_S_LST, self.fmtSingleQuotes
        )
        self.fmtDoubleQuotes = self._parseLine(
            cnfParse, cnfSec, "fmtdoublequote", self.CNF_S_LST, self.fmtDoubleQuotes
        )
        self.fmtPadBefore = self._parseLine(
            cnfParse, cnfSec, "fmtpadbefore", self.CNF_STR, self.fmtPadBefore
        )
        self.fmtPadAfter = self._parseLine(
            cnfParse, cnfSec, "fmtpadafter", self.CNF_STR, self.fmtPadAfter
        )
        self.fmtPadThin = self._parseLine(
            cnfParse, cnfSec, "fmtpadthin", self.CNF_BOOL, self.fmtPadThin
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
        self.allowOpenSQuote = self._parseLine(
            cnfParse, cnfSec, "allowopensquote", self.CNF_BOOL, self.allowOpenSQuote
        )
        self.allowOpenDQuote = self._parseLine(
            cnfParse, cnfSec, "allowopendquote", self.CNF_BOOL, self.allowOpenDQuote
        )
        self.highlightEmph = self._parseLine(
            cnfParse, cnfSec, "highlightemph", self.CNF_BOOL, self.highlightEmph
        )
        self.stopWhenIdle = self._parseLine(
            cnfParse, cnfSec, "stopwhenidle", self.CNF_BOOL, self.stopWhenIdle
        )
        self.userIdleTime = self._parseLine(
            cnfParse, cnfSec, "useridletime", self.CNF_INT, self.userIdleTime
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
        self.viewSynopsis = self._parseLine(
            cnfParse, cnfSec, "viewsynopsis", self.CNF_BOOL, self.viewSynopsis
        )
        self.searchCase = self._parseLine(
            cnfParse, cnfSec, "searchcase", self.CNF_BOOL, self.searchCase
        )
        self.searchWord = self._parseLine(
            cnfParse, cnfSec, "searchword", self.CNF_BOOL, self.searchWord
        )
        self.searchRegEx = self._parseLine(
            cnfParse, cnfSec, "searchregex", self.CNF_BOOL, self.searchRegEx
        )
        self.searchLoop = self._parseLine(
            cnfParse, cnfSec, "searchloop", self.CNF_BOOL, self.searchLoop
        )
        self.searchNextFile = self._parseLine(
            cnfParse, cnfSec, "searchnextfile", self.CNF_BOOL, self.searchNextFile
        )
        self.searchMatchCap = self._parseLine(
            cnfParse, cnfSec, "searchmatchcap", self.CNF_BOOL, self.searchMatchCap
        )

        ## Path
        cnfSec = "Path"
        self.lastPath = self._parseLine(
            cnfParse, cnfSec, "lastpath", self.CNF_STR, self.lastPath
        )

        # Check Certain Values for None
        self.spellLanguage = self._checkNone(self.spellLanguage)

        # If we're using straight quotes, disable auto-replace
        if self.fmtSingleQuotes == ["'", "'"] and self.doReplaceSQuote:
            logger.info("Using straight single quotes, so disabling auto-replace")
            self.doReplaceSQuote = False

        if self.fmtDoubleQuotes == ["\"", "\""] and self.doReplaceDQuote:
            logger.info("Using straight double quotes, so disabling auto-replace")
            self.doReplaceDQuote = False

        return True

    def saveConfig(self):
        """Save the current preferences to file.
        """
        logger.debug("Saving config file")
        if self.confPath is None:
            return False

        cnfParse = configparser.ConfigParser()

        # Set options

        ## Main
        cnfSec = "Main"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec, "timestamp",   formatTimeStamp(time()))
        cnfParse.set(cnfSec, "theme",       str(self.guiTheme))
        cnfParse.set(cnfSec, "syntax",      str(self.guiSyntax))
        cnfParse.set(cnfSec, "icons",       str(self.guiIcons))
        cnfParse.set(cnfSec, "guidark",     str(self.guiDark))
        cnfParse.set(cnfSec, "guifont",     str(self.guiFont))
        cnfParse.set(cnfSec, "guifontsize", str(self.guiFontSize))
        cnfParse.set(cnfSec, "lastnotes",   str(self.lastNotes))
        cnfParse.set(cnfSec, "guilang",     str(self.guiLang))

        ## Sizes
        cnfSec = "Sizes"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec, "geometry",    self._packList(self.winGeometry))
        cnfParse.set(cnfSec, "preferences", self._packList(self.prefGeometry))
        cnfParse.set(cnfSec, "treecols",    self._packList(self.treeColWidth))
        cnfParse.set(cnfSec, "novelcols",   self._packList(self.novelColWidth))
        cnfParse.set(cnfSec, "projcols",    self._packList(self.projColWidth))
        cnfParse.set(cnfSec, "mainpane",    self._packList(self.mainPanePos))
        cnfParse.set(cnfSec, "docpane",     self._packList(self.docPanePos))
        cnfParse.set(cnfSec, "viewpane",    self._packList(self.viewPanePos))
        cnfParse.set(cnfSec, "outlinepane", self._packList(self.outlnPanePos))
        cnfParse.set(cnfSec, "fullscreen",  str(self.isFullScreen))
        cnfParse.set(cnfSec, "hidevscroll", str(self.hideVScroll))
        cnfParse.set(cnfSec, "hidehscroll", str(self.hideHScroll))

        ## Project
        cnfSec = "Project"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec, "autosaveproject", str(self.autoSaveProj))
        cnfParse.set(cnfSec, "autosavedoc",     str(self.autoSaveDoc))

        ## Editor
        cnfSec = "Editor"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec, "textfont",        str(self.textFont))
        cnfParse.set(cnfSec, "textsize",        str(self.textSize))
        cnfParse.set(cnfSec, "fixedwidth",      str(self.textFixedW))
        cnfParse.set(cnfSec, "width",           str(self.textWidth))
        cnfParse.set(cnfSec, "margin",          str(self.textMargin))
        cnfParse.set(cnfSec, "tabwidth",        str(self.tabWidth))
        cnfParse.set(cnfSec, "focuswidth",      str(self.focusWidth))
        cnfParse.set(cnfSec, "hidefocusfooter", str(self.hideFocusFooter))
        cnfParse.set(cnfSec, "justify",         str(self.doJustify))
        cnfParse.set(cnfSec, "autoselect",      str(self.autoSelect))
        cnfParse.set(cnfSec, "autoreplace",     str(self.doReplace))
        cnfParse.set(cnfSec, "repsquotes",      str(self.doReplaceSQuote))
        cnfParse.set(cnfSec, "repdquotes",      str(self.doReplaceDQuote))
        cnfParse.set(cnfSec, "repdash",         str(self.doReplaceDash))
        cnfParse.set(cnfSec, "repdots",         str(self.doReplaceDots))
        cnfParse.set(cnfSec, "scrollpastend",   str(self.scrollPastEnd))
        cnfParse.set(cnfSec, "autoscroll",      str(self.autoScroll))
        cnfParse.set(cnfSec, "autoscrollpos",   str(self.autoScrollPos))
        cnfParse.set(cnfSec, "fmtsinglequote",  self._packList(self.fmtSingleQuotes))
        cnfParse.set(cnfSec, "fmtdoublequote",  self._packList(self.fmtDoubleQuotes))
        cnfParse.set(cnfSec, "fmtpadbefore",    str(self.fmtPadBefore))
        cnfParse.set(cnfSec, "fmtpadafter",     str(self.fmtPadAfter))
        cnfParse.set(cnfSec, "fmtpadthin",      str(self.fmtPadThin))
        cnfParse.set(cnfSec, "spelltool",       str(self.spellTool))
        cnfParse.set(cnfSec, "spellcheck",      str(self.spellLanguage))
        cnfParse.set(cnfSec, "showtabsnspaces", str(self.showTabsNSpaces))
        cnfParse.set(cnfSec, "showlineendings", str(self.showLineEndings))
        cnfParse.set(cnfSec, "bigdoclimit",     str(self.bigDocLimit))
        cnfParse.set(cnfSec, "showfullpath",    str(self.showFullPath))
        cnfParse.set(cnfSec, "highlightquotes", str(self.highlightQuotes))
        cnfParse.set(cnfSec, "allowopensquote", str(self.allowOpenSQuote))
        cnfParse.set(cnfSec, "allowopendquote", str(self.allowOpenDQuote))
        cnfParse.set(cnfSec, "highlightemph",   str(self.highlightEmph))
        cnfParse.set(cnfSec, "stopwhenidle",    str(self.stopWhenIdle))
        cnfParse.set(cnfSec, "useridletime",    str(self.userIdleTime))

        ## Backup
        cnfSec = "Backup"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec, "backuppath",      str(self.backupPath))
        cnfParse.set(cnfSec, "backuponclose",   str(self.backupOnClose))
        cnfParse.set(cnfSec, "askbeforebackup", str(self.askBeforeBackup))

        ## State
        cnfSec = "State"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec, "showrefpanel",    str(self.showRefPanel))
        cnfParse.set(cnfSec, "viewcomments",    str(self.viewComments))
        cnfParse.set(cnfSec, "viewsynopsis",    str(self.viewSynopsis))
        cnfParse.set(cnfSec, "searchcase",      str(self.searchCase))
        cnfParse.set(cnfSec, "searchword",      str(self.searchWord))
        cnfParse.set(cnfSec, "searchregex",     str(self.searchRegEx))
        cnfParse.set(cnfSec, "searchloop",      str(self.searchLoop))
        cnfParse.set(cnfSec, "searchnextfile",  str(self.searchNextFile))
        cnfParse.set(cnfSec, "searchmatchcap",  str(self.searchMatchCap))

        ## Path
        cnfSec = "Path"
        cnfParse.add_section(cnfSec)
        cnfParse.set(cnfSec, "lastpath", str(self.lastPath))

        # Write config file
        cnfPath = os.path.join(self.confPath, self.confFile)
        try:
            with open(cnfPath, mode="w", encoding="utf8") as outFile:
                cnfParse.write(outFile)
            self.confChanged = False
        except Exception as e:
            logger.error("Could not save config file")
            logException()
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

        cacheFile = os.path.join(self.dataPath, nwFiles.RECENT_FILE)
        self.recentProj = {}

        if os.path.isfile(cacheFile):
            try:
                with open(cacheFile, mode="r", encoding="utf8") as inFile:
                    theData = json.load(inFile)

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

        cacheFile = os.path.join(self.dataPath, nwFiles.RECENT_FILE)
        cacheTemp = os.path.join(self.dataPath, nwFiles.RECENT_FILE+"~")

        try:
            with open(cacheTemp, mode="w+", encoding="utf8") as outFile:
                json.dump(self.recentProj, outFile, indent=2)
        except Exception as e:
            self.hasError = True
            self.errData.append("Could not save recent project cache")
            self.errData.append(str(e))
            return False

        if os.path.isfile(cacheFile):
            os.unlink(cacheFile)
        os.rename(cacheTemp, cacheFile)

        return True

    def updateRecentCache(self, projPath, projTitle, wordCount, saveTime):
        """Add or update recent cache information o9n a given project.
        """
        self.recentProj[os.path.abspath(projPath)] = {
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
    #  Setters
    ##

    def setConfPath(self, newPath):
        if newPath is None:
            return True
        if not os.path.isfile(newPath):
            logger.error("File not found, using default config path instead")
            return False
        self.confPath = os.path.dirname(newPath)
        self.confFile = os.path.basename(newPath)
        return True

    def setDataPath(self, newPath):
        if newPath is None:
            return True
        if not os.path.isdir(newPath):
            logger.error("Path not found, using default data path instead")
            return False
        self.dataPath = os.path.abspath(newPath)
        return True

    def setLastPath(self, lastPath):
        if lastPath is None or lastPath == "":
            self.lastPath = ""
        else:
            self.lastPath = os.path.dirname(lastPath)
        return True

    def setWinSize(self, newWidth, newHeight):
        newWidth = int(newWidth/self.guiScale)
        newHeight = int(newHeight/self.guiScale)
        if abs(self.winGeometry[0] - newWidth) > 5:
            self.winGeometry[0] = newWidth
            self.confChanged = True
        if abs(self.winGeometry[1] - newHeight) > 5:
            self.winGeometry[1] = newHeight
            self.confChanged = True
        return True

    def setPreferencesSize(self, newWidth, newHeight):
        self.prefGeometry[0] = int(newWidth/self.guiScale)
        self.prefGeometry[1] = int(newHeight/self.guiScale)
        self.confChanged = True
        return True

    def setTreeColWidths(self, colWidths):
        self.treeColWidth = [int(x/self.guiScale) for x in colWidths]
        self.confChanged = True
        return True

    def setNovelColWidths(self, colWidths):
        self.novelColWidth = [int(x/self.guiScale) for x in colWidths]
        self.confChanged = True
        return True

    def setProjColWidths(self, colWidths):
        self.projColWidth = [int(x/self.guiScale) for x in colWidths]
        self.confChanged = True
        return True

    def setMainPanePos(self, panePos):
        self.mainPanePos = [int(x/self.guiScale) for x in panePos]
        self.confChanged = True
        return True

    def setDocPanePos(self, panePos):
        self.docPanePos  = [int(x/self.guiScale) for x in panePos]
        self.confChanged = True
        return True

    def setViewPanePos(self, panePos):
        self.viewPanePos = [int(x/self.guiScale) for x in panePos]
        self.confChanged = True
        return True

    def setOutlinePanePos(self, panePos):
        self.outlnPanePos = [int(x/self.guiScale) for x in panePos]
        self.confChanged  = True
        return True

    def setShowRefPanel(self, checkState):
        self.showRefPanel = checkState
        self.confChanged  = True
        return self.showRefPanel

    def getErrData(self):
        errMessage = "<br>".join(self.errData)
        self.hasError = False
        self.errData = []
        return errMessage

    def setViewComments(self, viewState):
        self.viewComments = viewState
        self.confChanged  = True
        return self.viewComments

    def setViewSynopsis(self, viewState):
        self.viewSynopsis = viewState
        self.confChanged  = True
        return self.viewSynopsis

    ##
    #  Getters
    ##

    def getWinSize(self):
        return [int(x*self.guiScale) for x in self.winGeometry]

    def getPreferencesSize(self):
        return [int(x*self.guiScale) for x in self.prefGeometry]

    def getTreeColWidths(self):
        return [int(x*self.guiScale) for x in self.treeColWidth]

    def getNovelColWidths(self):
        return [int(x*self.guiScale) for x in self.novelColWidth]

    def getProjColWidths(self):
        return [int(x*self.guiScale) for x in self.projColWidth]

    def getMainPanePos(self):
        return [int(x*self.guiScale) for x in self.mainPanePos]

    def getDocPanePos(self):
        return [int(x*self.guiScale) for x in self.docPanePos]

    def getViewPanePos(self):
        return [int(x*self.guiScale) for x in self.viewPanePos]

    def getOutlinePanePos(self):
        return [int(x*self.guiScale) for x in self.outlnPanePos]

    def getTextWidth(self):
        return self.pxInt(self.textWidth)

    def getTextMargin(self):
        return self.pxInt(self.textMargin)

    def getTabWidth(self):
        return self.pxInt(self.tabWidth)

    def getFocusWidth(self):
        return self.pxInt(self.focusWidth)

    ##
    #  Internal Functions
    ##

    def _packList(self, inData):
        """Pack a list of items into a comma-separated string.
        """
        return ", ".join([str(inVal) for inVal in inData])

    def _unpackList(self, inStr, listDefault, cnfType):
        """Unpack a comma-separated string of items into a list.
        """
        inData = inStr.split(",")
        outData = listDefault.copy()
        for i in range(min(len(inData), len(listDefault))):
            try:
                if cnfType == self.CNF_S_LST:
                    outData[i] = inData[i].strip()
                elif cnfType == self.CNF_I_LST:
                    outData[i] = int(inData[i].strip())
                else:
                    continue
            except Exception:
                continue
        return outData

    def _parseLine(self, cnfParse, cnfSec, cnfName, cnfType, cnfDefault):
        """Parse a line and return the correct datatype.
        """
        if cnfParse.has_section(cnfSec):
            if cnfParse.has_option(cnfSec, cnfName):
                try:
                    if cnfType == self.CNF_STR:
                        return cnfParse.get(cnfSec, cnfName)
                    elif cnfType == self.CNF_INT:
                        return cnfParse.getint(cnfSec, cnfName)
                    elif cnfType == self.CNF_BOOL:
                        return cnfParse.getboolean(cnfSec, cnfName)
                    elif cnfType == self.CNF_I_LST:
                        return self._unpackList(
                            cnfParse.get(cnfSec, cnfName), cnfDefault, self.CNF_I_LST
                        )
                    elif cnfType == self.CNF_S_LST:
                        return self._unpackList(
                            cnfParse.get(cnfSec, cnfName), cnfDefault, self.CNF_S_LST
                        )
                except ValueError:
                    logger.error("Failed to load value from config file.")
                    logException()
                    return cnfDefault

        return cnfDefault

    def _checkNone(self, checkVal):
        """Return a NoneType if the value correspomds to None, otherwise
        return the value unchanged.
        """
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
            import enchant # noqa: F401
            self.hasEnchant = True
            logger.debug("Checking package 'pyenchant': OK")
        except Exception:
            self.hasEnchant = False
            logger.debug("Checking package 'pyenchant': Missing")

        assistPath = shutil.which("assistant")
        self.hasAssistant = assistPath is not None
        if self.hasAssistant:
            logger.debug("Checking executable 'assistant': OK")
        else:
            logger.debug("Checking executable 'assistant': Missing")

        return

# END Class Config
