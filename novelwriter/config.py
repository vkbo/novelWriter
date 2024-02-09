"""
novelWriter – Config Class
==========================

File History:
Created: 2018-09-22 [0.0.1]  Config
Created: 2022-11-09 [2.0rc2] RecentProjects

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

import sys
import json
import logging

from time import time
from pathlib import Path

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtCore import (
    PYQT_VERSION, PYQT_VERSION_STR, QT_VERSION, QT_VERSION_STR, QLibraryInfo,
    QLocale, QStandardPaths, QSysInfo, QTranslator
)
from PyQt5.QtWidgets import QApplication

from novelwriter.error import formatException, logException
from novelwriter.common import NWConfigParser, checkInt, checkPath, formatTimeStamp
from novelwriter.constants import nwFiles, nwUnicode

logger = logging.getLogger(__name__)


class Config:

    LANG_NW   = 1
    LANG_PROJ = 2

    def __init__(self) -> None:

        # Initialisation
        # ==============

        # Set Application Variables
        self.appName   = "novelWriter"
        self.appHandle = "novelwriter"

        # Set Paths
        confRoot = Path(QStandardPaths.writableLocation(QStandardPaths.ConfigLocation))
        dataRoot = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))

        self._confPath = confRoot.absolute() / self.appHandle  # The user config location
        self._dataPath = dataRoot.absolute() / self.appHandle  # The user data location
        self._homePath = Path.home().absolute()  # The user's home directory
        self._backPath = self._homePath / "Backups"

        self._appPath = Path(__file__).parent.absolute()
        self._appRoot = self._appPath.parent
        if self._appRoot.is_file():
            # novelWriter is packaged as a single file
            self._appRoot = self._appRoot.parent
            self._appPath = self._appRoot

        # Runtime Settings and Variables
        self._hasError = False  # True if the config class encountered an error
        self._errData  = []     # List of error messages

        # Localisation
        # Note that these paths must be strings
        self._nwLangPath = self._appPath / "assets" / "i18n"
        self._qtLangPath = QLibraryInfo.location(QLibraryInfo.TranslationsPath)

        wantedLocale = self._nwLangPath / f"nw_{QLocale.system().name()}.qm"
        self._qLocale = QLocale.system() if wantedLocale.exists() else QLocale("en_GB")
        self._qtTrans = {}

        # PDF Manual
        pdfDocs = self._appPath / "assets" / "manual.pdf"
        self.pdfDocs = pdfDocs if pdfDocs.is_file() else None

        # User Settings
        # =============

        self._recentObj = RecentProjects(self)

        # General GUI Settings
        self.guiLocale   = self._qLocale.name()
        self.guiTheme    = "default"        # GUI theme
        self.guiSyntax   = "default_light"  # Syntax theme
        self.guiFont     = ""               # Defaults to system default font in theme class
        self.guiFontSize = 11               # Is overridden if system default is loaded
        self.guiScale    = 1.0              # Set automatically by Theme class
        self.hideVScroll = False            # Hide vertical scroll bars on main widgets
        self.hideHScroll = False            # Hide horizontal scroll bars on main widgets
        self.lastNotes   = "0x0"            # The latest release notes that have been shown

        # Size Settings
        self._mainWinSize  = [1200, 650]     # Last size of the main GUI window
        self._welcomeSize  = [800, 550]      # Last size of the welcome window
        self._prefsWinSize = [700, 615]      # Last size of the Preferences dialog
        self._mainPanePos  = [300, 800]      # Last position of the main window splitter
        self._viewPanePos  = [500, 150]      # Last position of the document viewer splitter
        self._outlnPanePos = [500, 150]      # Last position of the outline panel splitter

        # Project Settings
        self.autoSaveProj    = 60     # Interval for auto-saving project, in seconds
        self.autoSaveDoc     = 30     # Interval for auto-saving document, in seconds
        self.emphLabels      = True   # Add emphasis to H1 and H2 item labels
        self.backupOnClose   = False  # Flag for running automatic backups
        self.askBeforeBackup = True   # Flag for asking before running automatic backup

        # Text Editor Settings
        self.textFont        = ""     # Editor font
        self.textSize        = 12     # Editor font size
        self.textWidth       = 700    # Editor text width
        self.textMargin      = 40     # Editor/viewer text margin
        self.tabWidth        = 40     # Editor tabulator width

        self.focusWidth      = 800    # Focus Mode text width
        self.hideFocusFooter = False  # Hide document footer in Focus Mode
        self.showFullPath    = True   # Show full document path in editor header
        self.autoSelect      = True   # Auto-select word when applying format with no selection

        self.doJustify       = False  # Justify text
        self.showTabsNSpaces = False  # Show tabs and spaces in editor
        self.showLineEndings = False  # Show line endings in editor
        self.showMultiSpaces = True   # Highlight multiple spaces in the text

        self.doReplace       = True   # Enable auto-replace as you type
        self.doReplaceSQuote = True   # Smart single quotes
        self.doReplaceDQuote = True   # Smart double quotes
        self.doReplaceDash   = True   # Replace multiple hyphens with dashes
        self.doReplaceDots   = True   # Replace three dots with ellipsis

        self.autoScroll      = False  # Typewriter-like scrolling
        self.autoScrollPos   = 30     # Start point for typewriter-like scrolling
        self.scrollPastEnd   = True   # Scroll past end of document, and centre cursor

        self.highlightQuotes = True   # Highlight text in quotes
        self.allowOpenSQuote = False  # Allow open-ended single quotes
        self.allowOpenDQuote = True   # Allow open-ended double quotes
        self.highlightEmph   = True   # Add colour to text emphasis

        self.stopWhenIdle    = True   # Stop the status bar clock when the user is idle
        self.userIdleTime    = 300    # Time of inactivity to consider user idle
        self.incNotesWCount  = True   # The status bar word count includes notes

        # User-Selected Symbol Settings
        self.fmtApostrophe   = nwUnicode.U_RSQUO
        self.fmtSQuoteOpen   = nwUnicode.U_LSQUO
        self.fmtSQuoteClose  = nwUnicode.U_RSQUO
        self.fmtDQuoteOpen   = nwUnicode.U_LDQUO
        self.fmtDQuoteClose  = nwUnicode.U_RDQUO
        self.fmtPadBefore    = ""
        self.fmtPadAfter     = ""
        self.fmtPadThin      = False

        # User Paths
        self._lastPath   = self._homePath  # The user's last used path
        self._backupPath = self._backPath  # Backup path to use, can be none

        # Spell Checking Settings
        self.spellLanguage = "en"

        # State
        self.showViewerPanel = True   # The panel for the viewer is visible
        self.showEditToolBar = False  # The document editor toolbar visibility
        self.useShortcodes   = False  # Use shortcodes for basic formatting
        self.viewComments    = True   # Comments are shown in the viewer
        self.viewSynopsis    = True   # Synopsis is shown in the viewer

        # Search Bar Switches
        self.searchCase     = False
        self.searchWord     = False
        self.searchRegEx    = False
        self.searchLoop     = False
        self.searchNextFile = False
        self.searchMatchCap = False

        # System and App Information
        # ==========================

        # Check Qt5 Versions
        self.verQtString   = QT_VERSION_STR
        self.verQtValue    = QT_VERSION
        self.verPyQtString = PYQT_VERSION_STR
        self.verPyQtValue  = PYQT_VERSION

        # Check Python Version
        self.verPyString = sys.version.split()[0]

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
        self.hostName  = QSysInfo.machineHostName()
        self.kernelVer = QSysInfo.kernelVersion()
        self.isDebug   = False  # True if running in debug mode
        self.memInfo   = False  # True if displaying mem info in status bar

        # Packages
        self.hasEnchant = False  # The pyenchant package

        return

    ##
    #  Properties
    ##

    @property
    def hasError(self) -> bool:
        return self._hasError

    @property
    def recentProjects(self) -> RecentProjects:
        return self._recentObj

    @property
    def mainWinSize(self) -> list[int]:
        return [int(x*self.guiScale) for x in self._mainWinSize]

    @property
    def welcomeWinSize(self) -> list[int]:
        return [int(x*self.guiScale) for x in self._welcomeSize]

    @property
    def preferencesWinSize(self) -> list[int]:
        return [int(x*self.guiScale) for x in self._prefsWinSize]

    @property
    def mainPanePos(self) -> list[int]:
        return [int(x*self.guiScale) for x in self._mainPanePos]

    @property
    def viewPanePos(self) -> list[int]:
        return [int(x*self.guiScale) for x in self._viewPanePos]

    @property
    def outlinePanePos(self) -> list[int]:
        return [int(x*self.guiScale) for x in self._outlnPanePos]

    ##
    #  Getters
    ##

    def getTextWidth(self, focusMode: bool = False) -> int:
        """Get the text with for the correct editor mode."""
        if focusMode:
            return self.pxInt(max(self.focusWidth, 200))
        else:
            return self.pxInt(max(self.textWidth, 200))

    def getTextMargin(self) -> int:
        """Get the scaled text margin."""
        return self.pxInt(max(self.textMargin, 0))

    def getTabWidth(self) -> int:
        """Get the scaled tab width."""
        return self.pxInt(max(self.tabWidth, 0))

    ##
    #  Setters
    ##

    def setMainWinSize(self, width: int, height: int) -> None:
        """Set the size of the main window, but only if the change is
        larger than 5 pixels. The OS window manager will sometimes
        adjust it a bit, and we don't want the main window to shrink or
        grow each time the app is opened.
        """
        width = int(width/self.guiScale)
        height = int(height/self.guiScale)
        if abs(self._mainWinSize[0] - width) > 5:
            self._mainWinSize[0] = width
        if abs(self._mainWinSize[1] - height) > 5:
            self._mainWinSize[1] = height
        return

    def setWelcomeWinSize(self, width: int, height: int) -> None:
        """Set the size of the Preferences dialog window."""
        self._welcomeSize[0] = int(width/self.guiScale)
        self._welcomeSize[1] = int(height/self.guiScale)
        return

    def setPreferencesWinSize(self, width: int, height: int) -> None:
        """Set the size of the Preferences dialog window."""
        self._prefsWinSize[0] = int(width/self.guiScale)
        self._prefsWinSize[1] = int(height/self.guiScale)
        return

    def setMainPanePos(self, pos: list[int]) -> None:
        """Set the position of the main GUI splitter."""
        self._mainPanePos = [int(x/self.guiScale) for x in pos]
        return

    def setViewPanePos(self, pos: list[int]) -> None:
        """Set the position of the viewer meta data splitter."""
        self._viewPanePos = [int(x/self.guiScale) for x in pos]
        return

    def setOutlinePanePos(self, pos: list[int]) -> None:
        """Set the position of the outline details splitter."""
        self._outlnPanePos = [int(x/self.guiScale) for x in pos]
        return

    def setLastPath(self, path: str | Path) -> None:
        """Set the last used path. Only the folder is saved, so if the
        path is not a folder, the parent of the path is used instead.
        """
        if isinstance(path, (str, Path)):
            path = checkPath(path, self._homePath)
            if not path.is_dir():
                path = path.parent
            if path.is_dir():
                self._lastPath = path
                logger.debug("Last path updated: %s" % self._lastPath)
        return

    def setBackupPath(self, path: Path | str) -> None:
        """Set the current backup path."""
        self._backupPath = checkPath(path, self._backPath)
        return

    def setTextFont(self, family: str | None, pointSize: int = 12) -> None:
        """Set the text font if it exists. If it doesn't, or is None,
        set to default font.
        """
        fontDB = QFontDatabase()
        fontFam = fontDB.families()
        self.textSize = pointSize
        if family is None or family not in fontFam:
            logger.warning("Unknown font '%s'", family)
            if self.osWindows and "Arial" in fontFam:
                self.textFont = "Arial"
            elif self.osDarwin and "Helvetica" in fontFam:
                self.textFont = "Helvetica"
            else:
                self.textFont = fontDB.systemFont(QFontDatabase.GeneralFont).family()
        else:
            self.textFont = family
        return

    ##
    #  Methods
    ##

    def pxInt(self, value: int) -> int:
        """Scale fixed gui sizes by the screen scale factor."""
        return int(value*self.guiScale)

    def rpxInt(self, value: int) -> int:
        """Un-scale fixed gui sizes by the screen scale factor."""
        return int(value/self.guiScale)

    def dataPath(self, target: str | None = None) -> Path:
        """Return a path in the data folder."""
        if isinstance(target, str):
            return self._dataPath / target
        return self._dataPath

    def assetPath(self, target: str | None = None) -> Path:
        """Return a path in the assets folder."""
        if isinstance(target, str):
            return self._appPath / "assets" / target
        return self._appPath / "assets"

    def lastPath(self) -> Path:
        """Return the last path used by the user, if it exists."""
        if isinstance(self._lastPath, Path):
            if self._lastPath.is_dir():
                return self._lastPath
        return self._homePath

    def backupPath(self) -> Path:
        """Return the backup path."""
        if isinstance(self._backupPath, Path) and self._backupPath.is_dir():
            return self._backupPath
        return self._backPath

    def errorText(self) -> str:
        """Compile and return error messages from the initialisation of
        the Config class, and clear the error buffer.
        """
        message = "<br>".join(self._errData)
        self._hasError = False
        self._errData = []
        return message

    def listLanguages(self, lngSet: int) -> list[tuple[str, str]]:
        """List localisation files in the i18n folder. The default GUI
        language is British English (en_GB).
        """
        if lngSet == self.LANG_NW:
            fPre = "nw_"
            fExt = ".qm"
            langList = {"en_GB": QLocale("en_GB").nativeLanguageName().title()}
        elif lngSet == self.LANG_PROJ:
            fPre = "project_"
            fExt = ".json"
            langList = {"en_GB": QLocale("en_GB").nativeLanguageName().title()}
        else:
            return []

        for qmFile in self._nwLangPath.iterdir():
            qmName = qmFile.name
            if not (qmFile.is_file() and qmName.startswith(fPre) and qmName.endswith(fExt)):
                continue

            qmLang = qmName[len(fPre):-len(fExt)]
            qmName = QLocale(qmLang).nativeLanguageName().title()
            if qmLang and qmName and qmLang != "en_GB":
                langList[qmLang] = qmName

        return sorted(langList.items(), key=lambda x: x[0])

    ##
    #  Config Actions
    ##

    def initConfig(self, confPath: str | Path | None = None,
                   dataPath: str | Path | None = None) -> None:
        """Initialise the config class. The manual setting of confPath
        and dataPath is mainly intended for the test suite.
        """
        logger.debug("Initialising Config ...")
        if isinstance(confPath, (str, Path)):
            logger.info("Setting alternative config path: %s", confPath)
            self._confPath = Path(confPath)
        if isinstance(dataPath, (str, Path)):
            logger.info("Setting alternative data path: %s", dataPath)
            self._dataPath = Path(dataPath)

        logger.debug("Config Path: %s", self._confPath)
        logger.debug("Data Path: %s", self._dataPath)
        logger.debug("App Root: %s", self._appRoot)
        logger.debug("App Path: %s", self._appPath)
        logger.debug("Last Path: %s", self._lastPath)
        logger.debug("PDF Manual: %s", self.pdfDocs)

        # If the config and data folders don't exist, create them
        # This assumes that the os config and data folders exist
        self._confPath.mkdir(exist_ok=True)
        self._dataPath.mkdir(exist_ok=True)

        # Also create the syntax, themes and icons folders if possible
        if self._dataPath.is_dir():
            (self._dataPath / "cache").mkdir(exist_ok=True)
            (self._dataPath / "icons").mkdir(exist_ok=True)
            (self._dataPath / "syntax").mkdir(exist_ok=True)
            (self._dataPath / "themes").mkdir(exist_ok=True)

        # Check if config file exists, and load it. If not, we save defaults
        if (self._confPath / nwFiles.CONF_FILE).is_file():
            self.loadConfig()
        else:
            self.saveConfig()

        self._recentObj.loadCache()
        self._checkOptionalPackages()

        logger.debug("Config instance initialised")

        return

    def initLocalisation(self, nwApp: QApplication) -> None:
        """Initialise the localisation of the GUI."""
        self._qLocale = QLocale(self.guiLocale)
        QLocale.setDefault(self._qLocale)
        self._qtTrans = {}

        langList = [
            (self._qtLangPath, "qtbase"),   # Qt 5.x
            (str(self._nwLangPath), "nw"),  # novelWriter
        ]
        for lngPath, lngBase in langList:
            for lngCode in self._qLocale.uiLanguages():
                qTrans = QTranslator()
                lngFile = "%s_%s" % (lngBase, lngCode.replace("-", "_"))
                if lngFile not in self._qtTrans:
                    if qTrans.load(lngFile, lngPath):
                        logger.debug("Loaded: %s.qm", lngFile)
                        nwApp.installTranslator(qTrans)
                        self._qtTrans[lngFile] = qTrans

        return

    def loadConfig(self) -> bool:
        """Load preferences from file and replace default settings."""
        logger.debug("Loading config file")

        conf = NWConfigParser()
        cnfPath = self._confPath / nwFiles.CONF_FILE
        try:
            with open(cnfPath, mode="r", encoding="utf-8") as inFile:
                conf.read_file(inFile)
        except Exception as exc:
            logger.error("Could not load config file")
            logException()
            self._hasError = True
            self._errData.append("Could not load config file")
            self._errData.append(formatException(exc))
            return False

        # Main
        sec = "Main"
        self.guiTheme    = conf.rdStr(sec, "theme", self.guiTheme)
        self.guiSyntax   = conf.rdStr(sec, "syntax", self.guiSyntax)
        self.guiFont     = conf.rdStr(sec, "font", self.guiFont)
        self.guiFontSize = conf.rdInt(sec, "fontsize", self.guiFontSize)
        self.guiLocale   = conf.rdStr(sec, "localisation", self.guiLocale)
        self.hideVScroll = conf.rdBool(sec, "hidevscroll", self.hideVScroll)
        self.hideHScroll = conf.rdBool(sec, "hidehscroll", self.hideHScroll)
        self.lastNotes   = conf.rdStr(sec, "lastnotes", self.lastNotes)
        self._lastPath   = conf.rdPath(sec, "lastpath", self._lastPath)

        # Sizes
        sec = "Sizes"
        self._mainWinSize  = conf.rdIntList(sec, "mainwindow", self._mainWinSize)
        self._welcomeSize  = conf.rdIntList(sec, "welcome", self._welcomeSize)
        self._prefsWinSize = conf.rdIntList(sec, "preferences", self._prefsWinSize)
        self._mainPanePos  = conf.rdIntList(sec, "mainpane", self._mainPanePos)
        self._viewPanePos  = conf.rdIntList(sec, "viewpane", self._viewPanePos)
        self._outlnPanePos = conf.rdIntList(sec, "outlinepane", self._outlnPanePos)

        # Project
        sec = "Project"
        self.autoSaveProj    = conf.rdInt(sec, "autosaveproject", self.autoSaveProj)
        self.autoSaveDoc     = conf.rdInt(sec, "autosavedoc", self.autoSaveDoc)
        self.emphLabels      = conf.rdBool(sec, "emphlabels", self.emphLabels)
        self._backupPath     = conf.rdPath(sec, "backuppath", self._backupPath)
        self.backupOnClose   = conf.rdBool(sec, "backuponclose", self.backupOnClose)
        self.askBeforeBackup = conf.rdBool(sec, "askbeforebackup", self.askBeforeBackup)

        # Editor
        sec = "Editor"
        self.textFont        = conf.rdStr(sec, "textfont", self.textFont)
        self.textSize        = conf.rdInt(sec, "textsize", self.textSize)
        self.textWidth       = conf.rdInt(sec, "width", self.textWidth)
        self.textMargin      = conf.rdInt(sec, "margin", self.textMargin)
        self.tabWidth        = conf.rdInt(sec, "tabwidth", self.tabWidth)
        self.focusWidth      = conf.rdInt(sec, "focuswidth", self.focusWidth)
        self.hideFocusFooter = conf.rdBool(sec, "hidefocusfooter", self.hideFocusFooter)
        self.doJustify       = conf.rdBool(sec, "justify", self.doJustify)
        self.autoSelect      = conf.rdBool(sec, "autoselect", self.autoSelect)
        self.doReplace       = conf.rdBool(sec, "autoreplace", self.doReplace)
        self.doReplaceSQuote = conf.rdBool(sec, "repsquotes", self.doReplaceSQuote)
        self.doReplaceDQuote = conf.rdBool(sec, "repdquotes", self.doReplaceDQuote)
        self.doReplaceDash   = conf.rdBool(sec, "repdash", self.doReplaceDash)
        self.doReplaceDots   = conf.rdBool(sec, "repdots", self.doReplaceDots)
        self.autoScroll      = conf.rdBool(sec, "autoscroll", self.autoScroll)
        self.autoScrollPos   = conf.rdInt(sec, "autoscrollpos", self.autoScrollPos)
        self.scrollPastEnd   = conf.rdBool(sec, "scrollpastend", self.scrollPastEnd)
        self.fmtSQuoteOpen   = conf.rdStr(sec, "fmtsquoteopen", self.fmtSQuoteOpen)
        self.fmtSQuoteClose  = conf.rdStr(sec, "fmtsquoteclose", self.fmtSQuoteClose)
        self.fmtDQuoteOpen   = conf.rdStr(sec, "fmtdquoteopen", self.fmtDQuoteOpen)
        self.fmtDQuoteClose  = conf.rdStr(sec, "fmtdquoteclose", self.fmtDQuoteClose)
        self.fmtPadBefore    = conf.rdStr(sec, "fmtpadbefore", self.fmtPadBefore)
        self.fmtPadAfter     = conf.rdStr(sec, "fmtpadafter", self.fmtPadAfter)
        self.fmtPadThin      = conf.rdBool(sec, "fmtpadthin", self.fmtPadThin)
        self.spellLanguage   = conf.rdStr(sec, "spellcheck", self.spellLanguage)
        self.showTabsNSpaces = conf.rdBool(sec, "showtabsnspaces", self.showTabsNSpaces)
        self.showLineEndings = conf.rdBool(sec, "showlineendings", self.showLineEndings)
        self.showMultiSpaces = conf.rdBool(sec, "showmultispaces", self.showMultiSpaces)
        self.incNotesWCount  = conf.rdBool(sec, "incnoteswcount", self.incNotesWCount)
        self.showFullPath    = conf.rdBool(sec, "showfullpath", self.showFullPath)
        self.highlightQuotes = conf.rdBool(sec, "highlightquotes", self.highlightQuotes)
        self.allowOpenSQuote = conf.rdBool(sec, "allowopensquote", self.allowOpenSQuote)
        self.allowOpenDQuote = conf.rdBool(sec, "allowopendquote", self.allowOpenDQuote)
        self.highlightEmph   = conf.rdBool(sec, "highlightemph", self.highlightEmph)
        self.stopWhenIdle    = conf.rdBool(sec, "stopwhenidle", self.stopWhenIdle)
        self.userIdleTime    = conf.rdInt(sec, "useridletime", self.userIdleTime)

        # State
        sec = "State"
        self.showViewerPanel = conf.rdBool(sec, "showviewerpanel", self.showViewerPanel)
        self.showEditToolBar = conf.rdBool(sec, "showedittoolbar", self.showEditToolBar)
        self.useShortcodes   = conf.rdBool(sec, "useshortcodes", self.useShortcodes)
        self.viewComments    = conf.rdBool(sec, "viewcomments", self.viewComments)
        self.viewSynopsis    = conf.rdBool(sec, "viewsynopsis", self.viewSynopsis)
        self.searchCase      = conf.rdBool(sec, "searchcase", self.searchCase)
        self.searchWord      = conf.rdBool(sec, "searchword", self.searchWord)
        self.searchRegEx     = conf.rdBool(sec, "searchregex", self.searchRegEx)
        self.searchLoop      = conf.rdBool(sec, "searchloop", self.searchLoop)
        self.searchNextFile  = conf.rdBool(sec, "searchnextfile", self.searchNextFile)
        self.searchMatchCap  = conf.rdBool(sec, "searchmatchcap", self.searchMatchCap)

        # Check Values
        # ============

        # If we're using straight quotes, disable auto-replace
        if self.fmtSQuoteOpen == self.fmtSQuoteClose == "'" and self.doReplaceSQuote:
            logger.info("Using straight single quotes, so disabling auto-replace")
            self.doReplaceSQuote = False

        if self.fmtDQuoteOpen == self.fmtDQuoteClose == '"' and self.doReplaceDQuote:
            logger.info("Using straight double quotes, so disabling auto-replace")
            self.doReplaceDQuote = False

        return True

    def saveConfig(self) -> bool:
        """Save the current preferences to file."""
        logger.debug("Saving config file")

        conf = NWConfigParser()

        conf["Meta"] = {
            "timestamp": formatTimeStamp(time()),
        }

        conf["Main"] = {
            "theme":        str(self.guiTheme),
            "syntax":       str(self.guiSyntax),
            "font":         str(self.guiFont),
            "fontsize":     str(self.guiFontSize),
            "localisation": str(self.guiLocale),
            "hidevscroll":  str(self.hideVScroll),
            "hidehscroll":  str(self.hideHScroll),
            "lastnotes":    str(self.lastNotes),
            "lastpath":     str(self._lastPath),
        }

        conf["Sizes"] = {
            "mainwindow":  self._packList(self._mainWinSize),
            "welcome":     self._packList(self._welcomeSize),
            "preferences": self._packList(self._prefsWinSize),
            "mainpane":    self._packList(self._mainPanePos),
            "viewpane":    self._packList(self._viewPanePos),
            "outlinepane": self._packList(self._outlnPanePos),
        }

        conf["Project"] = {
            "autosaveproject": str(self.autoSaveProj),
            "autosavedoc":     str(self.autoSaveDoc),
            "emphlabels":      str(self.emphLabels),
            "backuppath":      str(self._backupPath),
            "backuponclose":   str(self.backupOnClose),
            "askbeforebackup": str(self.askBeforeBackup),
        }

        conf["Editor"] = {
            "textfont":        str(self.textFont),
            "textsize":        str(self.textSize),
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
            "autoscroll":      str(self.autoScroll),
            "autoscrollpos":   str(self.autoScrollPos),
            "scrollpastend":   str(self.scrollPastEnd),
            "fmtsquoteopen":   str(self.fmtSQuoteOpen),
            "fmtsquoteclose":  str(self.fmtSQuoteClose),
            "fmtdquoteopen":   str(self.fmtDQuoteOpen),
            "fmtdquoteclose":  str(self.fmtDQuoteClose),
            "fmtpadbefore":    str(self.fmtPadBefore),
            "fmtpadafter":     str(self.fmtPadAfter),
            "fmtpadthin":      str(self.fmtPadThin),
            "spellcheck":      str(self.spellLanguage),
            "showtabsnspaces": str(self.showTabsNSpaces),
            "showlineendings": str(self.showLineEndings),
            "showmultispaces": str(self.showMultiSpaces),
            "incnoteswcount":  str(self.incNotesWCount),
            "showfullpath":    str(self.showFullPath),
            "highlightquotes": str(self.highlightQuotes),
            "allowopensquote": str(self.allowOpenSQuote),
            "allowopendquote": str(self.allowOpenDQuote),
            "highlightemph":   str(self.highlightEmph),
            "stopwhenidle":    str(self.stopWhenIdle),
            "useridletime":    str(self.userIdleTime),
        }

        conf["State"] = {
            "showviewerpanel": str(self.showViewerPanel),
            "showedittoolbar": str(self.showEditToolBar),
            "useshortcodes":   str(self.useShortcodes),
            "viewcomments":    str(self.viewComments),
            "viewsynopsis":    str(self.viewSynopsis),
            "searchcase":      str(self.searchCase),
            "searchword":      str(self.searchWord),
            "searchregex":     str(self.searchRegEx),
            "searchloop":      str(self.searchLoop),
            "searchnextfile":  str(self.searchNextFile),
            "searchmatchcap":  str(self.searchMatchCap),
        }

        # Write config file
        cnfPath = self._confPath / nwFiles.CONF_FILE
        try:
            with open(cnfPath, mode="w", encoding="utf-8") as outFile:
                conf.write(outFile)
        except Exception as exc:
            logger.error("Could not save config file")
            logException()
            self._hasError = True
            self._errData.append("Could not save config file")
            self._errData.append(formatException(exc))
            return False

        return True

    ##
    #  Internal Functions
    ##

    def _packList(self, data: list) -> str:
        """Pack a list of items into a comma-separated string for saving
        to the config file.
        """
        return ", ".join([str(inVal) for inVal in data])

    def _checkOptionalPackages(self) -> None:
        """Check optional packages used by some features."""
        try:
            import enchant  # noqa: F401
        except ImportError:
            self.hasEnchant = False
            logger.debug("Checking package 'pyenchant': Missing")
        else:
            self.hasEnchant = True
            logger.debug("Checking package 'pyenchant': OK")
        return

# END Class Config


class RecentProjects:

    def __init__(self, config: Config) -> None:
        self._conf = config
        self._data = {}
        return

    def loadCache(self) -> bool:
        """Load the cache file for recent projects."""
        self._data = {}

        cacheFile = self._conf.dataPath(nwFiles.RECENT_FILE)
        if cacheFile.is_file():
            try:
                with open(cacheFile, mode="r", encoding="utf-8") as inFile:
                    data = json.load(inFile)
                for path, entry in data.items():
                    self._data[path] = {
                        "title": entry.get("title", ""),
                        "words": entry.get("words", 0),
                        "time": entry.get("time", 0),
                    }
            except Exception:
                logger.error("Could not load recent project cache")
                logException()
                return False

        return True

    def saveCache(self) -> bool:
        """Save the cache dictionary of recent projects."""
        cacheFile = self._conf.dataPath(nwFiles.RECENT_FILE)
        cacheTemp = cacheFile.with_suffix(".tmp")
        try:
            with open(cacheTemp, mode="w+", encoding="utf-8") as outFile:
                json.dump(self._data, outFile, indent=2)
            cacheTemp.replace(cacheFile)
        except Exception:
            logger.error("Could not save recent project cache")
            logException()
            return False

        return True

    def listEntries(self) -> list[tuple[str, str, int, int]]:
        """List all items in the cache."""
        return [
            (str(k), str(e["title"]), checkInt(e["words"], 0), checkInt(e["time"], 0))
            for k, e in self._data.items()
        ]

    def update(self, path: str | Path, title: str, words: int, saved: float | int) -> None:
        """Add or update recent cache information on a given project."""
        self._data[str(path)] = {
            "title": title,
            "words": int(words),
            "time": int(saved),
        }
        self.saveCache()
        return

    def remove(self, path: str | Path) -> None:
        """Try to remove a path from the recent projects cache."""
        if self._data.pop(str(path), None) is not None:
            logger.debug("Removed recent: %s", path)
            self.saveCache()
        return

# END Class RecentProjects
