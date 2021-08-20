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

import os
import sys
import json
import logging

from time import time

from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtCore import (
    QT_VERSION_STR, QStandardPaths, QSysInfo, QLocale, QLibraryInfo,
    QTranslator
)

from nw.error import logException
from nw.common import splitVersionNumber, formatTimeStamp, NWConfigParser
from nw.constants import nwConst, nwFiles, nwUnicode

logger = logging.getLogger(__name__)


class Config:

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
        self.pdfDocs   = None   # The location of the PDF manual, if it exists

        # Runtime Settings and Variables
        self.confChanged = False  # True whenever the config has chenged, false after save

        # General
        self.guiTheme    = "default"
        self.guiSyntax   = "default_light"
        self.guiIcons    = "typicons_colour_light"
        self.guiDark     = False  # Load icons for dark backgrounds, if available
        self.guiFont     = ""     # Defaults to system default font
        self.guiFontSize = 11     # Is overridden if system default is loaded
        self.guiScale    = 1.0    # Set automatically by Theme class
        self.lastNotes   = "0x0"  # The latest release notes that have been shown

        # Localisation
        self.qLocal     = QLocale.system()
        self.guiLang    = self.qLocal.name()
        self.qtLangPath = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        self.nwLangPath = None
        self.qtTrans    = {}

        # Sizes
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

        # Features
        self.hideVScroll = False  # Hide vertical scroll bars on main widgets
        self.hideHScroll = False  # Hide horizontal scroll bars on main widgets
        self.fullStatus  = True   # Show the full status text in the project tree
        self.emphLabels  = True   # Add emphasis to H1 and H2 item labels

        # Project
        self.autoSaveProj = 60  # Interval for auto-saving project in seconds
        self.autoSaveDoc  = 30  # Interval for auto-saving document in seconds

        # Text Editor
        self.textFont        = None   # Editor font
        self.textSize        = 12     # Editor font size
        self.textFixedW      = True   # Keep editor text fixed width
        self.textWidth       = 600    # Editor text width
        self.textMargin      = 40     # Editor/viewer text margin
        self.tabWidth        = 40     # Editor tabulator width

        self.focusWidth      = 800    # Focus Mode text width
        self.hideFocusFooter = False  # Hide document footer in Focus Mode
        self.showFullPath    = True   # Show full document path in editor header
        self.autoSelect      = True   # Auto-select word when applying format with no selection

        self.doJustify       = False  # Justify text
        self.showTabsNSpaces = False  # Show tabs and spaces in edior
        self.showLineEndings = False  # Show line endings in editor
        self.showMultiSpaces = True   # Highlight multiple spaces in the text

        self.doReplace       = True   # Enable auto-replace as you type
        self.doReplaceSQuote = True   # Smart single quotes
        self.doReplaceDQuote = True   # Smart double quotes
        self.doReplaceDash   = True   # Replace multiple hyphens with dashes
        self.doReplaceDots   = True   # Replace three dots with ellipsis

        self.scrollPastEnd   = True   # Allow scrolling past end of document
        self.autoScroll      = False  # Typewriter-like scrolling
        self.autoScrollPos   = 30     # Start point for typewriter-like scrolling

        self.wordCountTimer  = 5.0    # Interval for word count update in seconds
        self.bigDocLimit     = 800    # Size threshold for heavy editor features in kilobytes

        self.highlightQuotes = True   # Highlight text in quotes
        self.allowOpenSQuote = False  # Allow open-ended single quotes
        self.allowOpenDQuote = True   # Allow open-ended double quotes
        self.highlightEmph   = True   # Add colour to text emphasis

        self.stopWhenIdle    = True   # Stop the status bar clock when the user is idle
        self.userIdleTime    = 300    # Time of inactivity to consider user idle

        # User-Selected Symbols
        self.fmtApostrophe   = nwUnicode.U_RSQUO
        self.fmtSingleQuotes = [nwUnicode.U_LSQUO, nwUnicode.U_RSQUO]
        self.fmtDoubleQuotes = [nwUnicode.U_LDQUO, nwUnicode.U_RDQUO]
        self.fmtPadBefore    = ""
        self.fmtPadAfter     = ""
        self.fmtPadThin      = False

        # Spell Checking
        self.spellTool     = None
        self.spellLanguage = None

        # Search Bar Switches
        self.searchCase     = False
        self.searchWord     = False
        self.searchRegEx    = False
        self.searchLoop     = False
        self.searchNextFile = False
        self.searchMatchCap = False

        # Backup
        self.backupPath      = ""
        self.backupOnClose   = False
        self.askBeforeBackup = True

        # State
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
        self.hasEnchant = False  # The pyenchant package

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
            logger.info("Setting config from alternative path: %s", confPath)
            self.confPath = confPath

        if dataPath is None:
            if self.verQtValue >= 50400:
                dataRoot = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            else:
                dataRoot = QStandardPaths.writableLocation(QStandardPaths.DataLocation)
            self.dataPath = os.path.join(os.path.abspath(dataRoot), self.appHandle)
        else:
            logger.info("Setting data path from alternative path: %s", dataPath)
            self.dataPath = dataPath

        logger.verbose("Config path: %s", self.confPath)
        logger.verbose("Data path: %s", self.dataPath)

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
        self.nwLangPath = os.path.join(self.assetPath, "i18n")

        logger.verbose("App path: %s", self.appPath)
        logger.verbose("Last path: %s", self.lastPath)

        # If config folder does not exist, create it.
        # This assumes that the os config folder itself exists.
        if not os.path.isdir(self.confPath):
            try:
                os.mkdir(self.confPath)
            except Exception as e:
                logger.error("Could not create folder: %s", self.confPath)
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
                    logger.error("Could not create folder: %s", self.dataPath)
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

        # Look for a PDF version of the manual
        lookIn = [
            os.path.join(self.assetPath, "help", "manual.pdf"),
            os.path.join(self.appRoot, "UserManual.pdf"),
        ]
        for pdfDocs in lookIn:
            if os.path.isfile(pdfDocs):
                self.pdfDocs = pdfDocs
                break

        logger.debug("Config initialisation complete")

        return True

    def initLocalisation(self, nwApp):
        """Initialise the localisation of the GUI.
        """
        self.qLocal = QLocale(self.guiLang)
        QLocale.setDefault(self.qLocal)
        self.qtTrans = {}

        langList = [
            (self.qtLangPath, "qtbase"),  # Qt 5.x
            (self.nwLangPath, "qtbase"),  # Alternative Qt 5.x
            (self.nwLangPath, "nw"),      # novelWriter
        ]
        for lngPath, lngBase in langList:
            for lngCode in self.qLocal.uiLanguages():
                qTrans = QTranslator()
                lngFile = "%s_%s" % (lngBase, lngCode.replace("-", "_"))
                if lngFile not in self.qtTrans:
                    if qTrans.load(lngFile, lngPath):
                        logger.debug("Loaded: %s", os.path.join(lngPath, lngFile))
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

        theConf = NWConfigParser()
        cnfPath = os.path.join(self.confPath, self.confFile)
        try:
            with open(cnfPath, mode="r", encoding="utf-8") as inFile:
                theConf.read_file(inFile)
        except Exception as e:
            logger.error("Could not load config file")
            logException()
            self.hasError = True
            self.errData.append("Could not load config file")
            self.errData.append(str(e))
            return False

        # Main
        cnfSec = "Main"
        self.guiTheme    = theConf.rdStr(cnfSec, "theme", self.guiTheme)
        self.guiSyntax   = theConf.rdStr(cnfSec, "syntax", self.guiSyntax)
        self.guiIcons    = theConf.rdStr(cnfSec, "icons", self.guiIcons)
        self.guiDark     = theConf.rdBool(cnfSec, "guidark", self.guiDark)
        self.guiFont     = theConf.rdStr(cnfSec, "guifont", self.guiFont)
        self.guiFontSize = theConf.rdInt(cnfSec, "guifontsize", self.guiFontSize)
        self.lastNotes   = theConf.rdStr(cnfSec, "lastnotes", self.lastNotes)
        self.guiLang     = theConf.rdStr(cnfSec, "guilang", self.guiLang)
        self.hideVScroll = theConf.rdBool(cnfSec, "hidevscroll", self.hideVScroll)
        self.hideHScroll = theConf.rdBool(cnfSec, "hidehscroll", self.hideHScroll)

        # Sizes
        cnfSec = "Sizes"
        self.winGeometry   = theConf.rdIntList(cnfSec, "geometry", self.winGeometry)
        self.prefGeometry  = theConf.rdIntList(cnfSec, "preferences", self.prefGeometry)
        self.treeColWidth  = theConf.rdIntList(cnfSec, "treecols", self.treeColWidth)
        self.novelColWidth = theConf.rdIntList(cnfSec, "novelcols", self.novelColWidth)
        self.projColWidth  = theConf.rdIntList(cnfSec, "projcols", self.projColWidth)
        self.mainPanePos   = theConf.rdIntList(cnfSec, "mainpane", self.mainPanePos)
        self.docPanePos    = theConf.rdIntList(cnfSec, "docpane", self.docPanePos)
        self.viewPanePos   = theConf.rdIntList(cnfSec, "viewpane", self.viewPanePos)
        self.outlnPanePos  = theConf.rdIntList(cnfSec, "outlinepane", self.outlnPanePos)
        self.isFullScreen  = theConf.rdBool(cnfSec, "fullscreen", self.isFullScreen)

        # Project
        cnfSec = "Project"
        self.autoSaveProj = theConf.rdInt(cnfSec, "autosaveproject", self.autoSaveProj)
        self.autoSaveDoc  = theConf.rdInt(cnfSec, "autosavedoc", self.autoSaveDoc)
        self.fullStatus   = theConf.rdBool(cnfSec, "fullstatus", self.fullStatus)
        self.emphLabels   = theConf.rdBool(cnfSec, "emphlabels", self.emphLabels)

        # Editor
        cnfSec = "Editor"
        self.textFont        = theConf.rdStr(cnfSec, "textfont", self.textFont)
        self.textSize        = theConf.rdInt(cnfSec, "textsize", self.textSize)
        self.textFixedW      = theConf.rdBool(cnfSec, "fixedwidth", self.textFixedW)
        self.textWidth       = theConf.rdInt(cnfSec, "width", self.textWidth)
        self.textMargin      = theConf.rdInt(cnfSec, "margin", self.textMargin)
        self.tabWidth        = theConf.rdInt(cnfSec, "tabwidth", self.tabWidth)
        self.focusWidth      = theConf.rdInt(cnfSec, "focuswidth", self.focusWidth)
        self.hideFocusFooter = theConf.rdBool(cnfSec, "hidefocusfooter", self.hideFocusFooter)
        self.doJustify       = theConf.rdBool(cnfSec, "justify", self.doJustify)
        self.autoSelect      = theConf.rdBool(cnfSec, "autoselect", self.autoSelect)
        self.doReplace       = theConf.rdBool(cnfSec, "autoreplace", self.doReplace)
        self.doReplaceSQuote = theConf.rdBool(cnfSec, "repsquotes", self.doReplaceSQuote)
        self.doReplaceDQuote = theConf.rdBool(cnfSec, "repdquotes", self.doReplaceDQuote)
        self.doReplaceDash   = theConf.rdBool(cnfSec, "repdash", self.doReplaceDash)
        self.doReplaceDots   = theConf.rdBool(cnfSec, "repdots", self.doReplaceDots)
        self.scrollPastEnd   = theConf.rdBool(cnfSec, "scrollpastend", self.scrollPastEnd)
        self.autoScroll      = theConf.rdBool(cnfSec, "autoscroll", self.autoScroll)
        self.autoScrollPos   = theConf.rdInt(cnfSec, "autoscrollpos", self.autoScrollPos)
        self.fmtSingleQuotes = theConf.rdStrList(cnfSec, "fmtsinglequote", self.fmtSingleQuotes)
        self.fmtDoubleQuotes = theConf.rdStrList(cnfSec, "fmtdoublequote", self.fmtDoubleQuotes)
        self.fmtPadBefore    = theConf.rdStr(cnfSec, "fmtpadbefore", self.fmtPadBefore)
        self.fmtPadAfter     = theConf.rdStr(cnfSec, "fmtpadafter", self.fmtPadAfter)
        self.fmtPadThin      = theConf.rdBool(cnfSec, "fmtpadthin", self.fmtPadThin)
        self.spellTool       = theConf.rdStr(cnfSec, "spelltool", self.spellTool)
        self.spellLanguage   = theConf.rdStr(cnfSec, "spellcheck", self.spellLanguage)
        self.showTabsNSpaces = theConf.rdBool(cnfSec, "showtabsnspaces", self.showTabsNSpaces)
        self.showLineEndings = theConf.rdBool(cnfSec, "showlineendings", self.showLineEndings)
        self.showMultiSpaces = theConf.rdBool(cnfSec, "showmultispaces", self.showMultiSpaces)
        self.bigDocLimit     = theConf.rdInt(cnfSec, "bigdoclimit", self.bigDocLimit)
        self.showFullPath    = theConf.rdBool(cnfSec, "showfullpath", self.showFullPath)
        self.highlightQuotes = theConf.rdBool(cnfSec, "highlightquotes", self.highlightQuotes)
        self.allowOpenSQuote = theConf.rdBool(cnfSec, "allowopensquote", self.allowOpenSQuote)
        self.allowOpenDQuote = theConf.rdBool(cnfSec, "allowopendquote", self.allowOpenDQuote)
        self.highlightEmph   = theConf.rdBool(cnfSec, "highlightemph", self.highlightEmph)
        self.stopWhenIdle    = theConf.rdBool(cnfSec, "stopwhenidle", self.stopWhenIdle)
        self.userIdleTime    = theConf.rdInt(cnfSec, "useridletime", self.userIdleTime)

        # Backup
        cnfSec = "Backup"
        self.backupPath      = theConf.rdStr(cnfSec, "backuppath", self.backupPath)
        self.backupOnClose   = theConf.rdBool(cnfSec, "backuponclose", self.backupOnClose)
        self.askBeforeBackup = theConf.rdBool(cnfSec, "askbeforebackup", self.askBeforeBackup)

        # State
        cnfSec = "State"
        self.showRefPanel   = theConf.rdBool(cnfSec, "showrefpanel", self.showRefPanel)
        self.viewComments   = theConf.rdBool(cnfSec, "viewcomments", self.viewComments)
        self.viewSynopsis   = theConf.rdBool(cnfSec, "viewsynopsis", self.viewSynopsis)
        self.searchCase     = theConf.rdBool(cnfSec, "searchcase", self.searchCase)
        self.searchWord     = theConf.rdBool(cnfSec, "searchword", self.searchWord)
        self.searchRegEx    = theConf.rdBool(cnfSec, "searchregex", self.searchRegEx)
        self.searchLoop     = theConf.rdBool(cnfSec, "searchloop", self.searchLoop)
        self.searchNextFile = theConf.rdBool(cnfSec, "searchnextfile", self.searchNextFile)
        self.searchMatchCap = theConf.rdBool(cnfSec, "searchmatchcap", self.searchMatchCap)

        # Path
        cnfSec = "Path"
        self.lastPath = theConf.rdStr(cnfSec, "lastpath", self.lastPath)

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

        theConf = NWConfigParser()

        theConf["Main"] = {
            "timestamp":   formatTimeStamp(time()),
            "theme":       str(self.guiTheme),
            "syntax":      str(self.guiSyntax),
            "icons":       str(self.guiIcons),
            "guidark":     str(self.guiDark),
            "guifont":     str(self.guiFont),
            "guifontsize": str(self.guiFontSize),
            "lastnotes":   str(self.lastNotes),
            "guilang":     str(self.guiLang),
            "hidevscroll": str(self.hideVScroll),
            "hidehscroll": str(self.hideHScroll),
        }

        theConf["Sizes"] = {
            "geometry":    self._packList(self.winGeometry),
            "preferences": self._packList(self.prefGeometry),
            "treecols":    self._packList(self.treeColWidth),
            "novelcols":   self._packList(self.novelColWidth),
            "projcols":    self._packList(self.projColWidth),
            "mainpane":    self._packList(self.mainPanePos),
            "docpane":     self._packList(self.docPanePos),
            "viewpane":    self._packList(self.viewPanePos),
            "outlinepane": self._packList(self.outlnPanePos),
            "fullscreen":  str(self.isFullScreen),
        }

        theConf["Project"] = {
            "autosaveproject": str(self.autoSaveProj),
            "autosavedoc":     str(self.autoSaveDoc),
            "fullstatus":      str(self.fullStatus),
            "emphlabels":      str(self.emphLabels),
        }

        theConf["Editor"] = {
            "textfont":        str(self.textFont),
            "textsize":        str(self.textSize),
            "fixedwidth":      str(self.textFixedW),
            "width":           str(self.textWidth),
            "margin":          str(self.textMargin),
            "tabwidth":        str(self.tabWidth),
            "focuswidth":      str(self.focusWidth),
            "hidefocusfooter": str(self.hideFocusFooter),
            "justify":         str(self.doJustify),
            "autoselect":      str(self.autoSelect),
            "autoreplace":     str(self.doReplace),
            "repsquotes":      str(self.doReplaceSQuote),
            "repdquotes":      str(self.doReplaceDQuote),
            "repdash":         str(self.doReplaceDash),
            "repdots":         str(self.doReplaceDots),
            "scrollpastend":   str(self.scrollPastEnd),
            "autoscroll":      str(self.autoScroll),
            "autoscrollpos":   str(self.autoScrollPos),
            "fmtsinglequote":  self._packList(self.fmtSingleQuotes),
            "fmtdoublequote":  self._packList(self.fmtDoubleQuotes),
            "fmtpadbefore":    str(self.fmtPadBefore),
            "fmtpadafter":     str(self.fmtPadAfter),
            "fmtpadthin":      str(self.fmtPadThin),
            "spelltool":       str(self.spellTool),
            "spellcheck":      str(self.spellLanguage),
            "showtabsnspaces": str(self.showTabsNSpaces),
            "showlineendings": str(self.showLineEndings),
            "showmultispaces": str(self.showMultiSpaces),
            "bigdoclimit":     str(self.bigDocLimit),
            "showfullpath":    str(self.showFullPath),
            "highlightquotes": str(self.highlightQuotes),
            "allowopensquote": str(self.allowOpenSQuote),
            "allowopendquote": str(self.allowOpenDQuote),
            "highlightemph":   str(self.highlightEmph),
            "stopwhenidle":    str(self.stopWhenIdle),
            "useridletime":    str(self.userIdleTime),
        }

        theConf["Backup"] = {
            "backuppath":      str(self.backupPath),
            "backuponclose":   str(self.backupOnClose),
            "askbeforebackup": str(self.askBeforeBackup),
        }

        theConf["State"] = {
            "showrefpanel":    str(self.showRefPanel),
            "viewcomments":    str(self.viewComments),
            "viewsynopsis":    str(self.viewSynopsis),
            "searchcase":      str(self.searchCase),
            "searchword":      str(self.searchWord),
            "searchregex":     str(self.searchRegEx),
            "searchloop":      str(self.searchLoop),
            "searchnextfile":  str(self.searchNextFile),
            "searchmatchcap":  str(self.searchMatchCap),
        }

        theConf["Path"] = {
            "lastpath": str(self.lastPath),
        }

        # Write config file
        cnfPath = os.path.join(self.confPath, self.confFile)
        try:
            with open(cnfPath, mode="w", encoding="utf-8") as outFile:
                theConf.write(outFile)
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
                with open(cacheFile, mode="r", encoding="utf-8") as inFile:
                    theData = json.load(inFile)

                for projPath in theData.keys():
                    theEntry = theData[projPath]
                    theTitle = ""
                    lastTime = 0
                    wordCount = 0
                    if "title" in theEntry.keys():
                        theTitle = theEntry["title"]
                    if "time" in theEntry.keys():
                        lastTime = int(theEntry["time"])
                    if "words" in theEntry.keys():
                        wordCount = int(theEntry["words"])
                    self.recentProj[projPath] = {
                        "title": theTitle,
                        "time": lastTime,
                        "words": wordCount,
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
            with open(cacheTemp, mode="w+", encoding="utf-8") as outFile:
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
        """Add or update recent cache information on a given project.
        """
        self.recentProj[os.path.abspath(projPath)] = {
            "title": projTitle,
            "time": int(saveTime),
            "words": int(wordCount),
        }
        return True

    def removeFromRecentCache(self, thePath):
        """Trying to remove a path from the recent projects cache.
        """
        if thePath in self.recentProj:
            del self.recentProj[thePath]
            logger.verbose("Removed recent: %s", thePath)
            self.saveRecentCache()
        else:
            logger.error("Unknown recent: %s", thePath)
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

    def getErrData(self):
        errMessage = "<br>".join(self.errData)
        self.hasError = False
        self.errData = []
        return errMessage

    ##
    #  Internal Functions
    ##

    def _packList(self, inData):
        """Pack a list of items into a comma-separated string.
        """
        return ", ".join([str(inVal) for inVal in inData])

    def _checkNone(self, checkVal):
        """Return a NoneType if the value corresponds to None, otherwise
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
            import enchant  # noqa: F401
            self.hasEnchant = True
            logger.debug("Checking package 'pyenchant': OK")
        except Exception:
            self.hasEnchant = False
            logger.debug("Checking package 'pyenchant': Missing")

        return

# END Class Config
