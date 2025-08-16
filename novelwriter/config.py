"""
novelWriter – Config Class
==========================

File History:
Created: 2018-09-22 [0.0.1]  Config
Created: 2022-11-09 [2.0rc2] RecentProjects
Created: 2024-06-16 [2.5rc1] RecentPaths

This file is a part of novelWriter
Copyright (C) 2018 Veronica Berglyd Olsen and novelWriter contributors

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

import json
import logging
import sys

from pathlib import Path
from time import time
from typing import TYPE_CHECKING, Final

from PyQt6.QtCore import (
    PYQT_VERSION, PYQT_VERSION_STR, QT_VERSION, QT_VERSION_STR, QDate,
    QDateTime, QLibraryInfo, QLocale, QStandardPaths, QSysInfo, QTranslator
)
from PyQt6.QtGui import QFont, QFontDatabase, QFontMetrics
from PyQt6.QtWidgets import QApplication

from novelwriter.common import (
    NWConfigParser, checkInt, checkPath, describeFont, fontMatcher,
    formatTimeStamp, processDialogSymbols, simplified
)
from novelwriter.constants import nwFiles, nwQuotes, nwUnicode
from novelwriter.enum import nwTheme
from novelwriter.error import formatException, logException

if TYPE_CHECKING:
    from datetime import datetime

    from novelwriter.core.projectdata import NWProjectData
    from novelwriter.splash import NSplashScreen

logger = logging.getLogger(__name__)

DEF_GUI_DARK = "default_dark"
DEF_GUI_LIGHT = "default_light"
DEF_ICONS = "material_rounded_normal"
DEF_TREECOL = "theme"


class Config:

    __slots__ = (
        "_appPath", "_appRoot", "_backPath", "_backupPath", "_confPath", "_dLocale", "_dShortDate",
        "_dShortDateTime", "_dataPath", "_errData", "_hasError", "_homePath", "_lastAuthor",
        "_manuals", "_nwLangPath", "_qLocale", "_qtLangPath", "_qtTrans", "_recentPaths",
        "_recentProjects", "_splash", "allowOpenDial", "altDialogClose", "altDialogOpen",
        "appHandle", "appName", "askBeforeBackup", "askBeforeExit", "autoSaveDoc", "autoSaveProj",
        "autoScroll", "autoScrollPos", "autoSelect", "backupOnClose", "cursorWidth", "darkTheme",
        "dialogLine", "dialogStyle", "doJustify", "doReplace", "doReplaceDQuote", "doReplaceDash",
        "doReplaceDots", "doReplaceSQuote", "emphLabels", "fmtApostrophe", "fmtDQuoteClose",
        "fmtDQuoteOpen", "fmtPadAfter", "fmtPadBefore", "fmtPadThin", "fmtSQuoteClose",
        "fmtSQuoteOpen", "focusWidth", "guiFont", "guiLocale", "hasEnchant", "hideFocusFooter",
        "hideHScroll", "hideVScroll", "highlightEmph", "hostName", "iconColDocs", "iconColTree",
        "iconTheme", "incNotesWCount", "isDebug", "kernelVer", "lastNotes", "lightTheme",
        "lineHighlight", "mainPanePos", "mainWinSize", "memInfo", "narratorBreak",
        "narratorDialog", "nativeFont", "osDarwin", "osLinux", "osType", "osUnknown", "osWindows",
        "outlinePanePos", "prefsWinSize", "scrollPastEnd", "searchCase", "searchLoop",
        "searchMatchCap", "searchNextFile", "searchProjCase", "searchProjRegEx", "searchProjWord",
        "searchRegEx", "searchWord", "showEditToolBar", "showFullPath", "showLineEndings",
        "showMultiSpaces", "showSessionTime", "showTabsNSpaces", "showViewerPanel",
        "spellLanguage", "stopWhenIdle", "tabWidth", "textFont", "textMargin", "textWidth",
        "themeMode", "useCharCount", "userIdleTime", "verPyQtString", "verPyQtValue",
        "verPyString", "verQtString", "verQtValue", "viewComments", "viewNotes", "viewPanePos",
        "viewSynopsis", "welcomeWinSize", "vimMode",
    )

    LANG_NW   = 1
    LANG_PROJ = 2

    def __init__(self) -> None:

        # Initialisation
        # ==============

        self._splash = None

        # Set Application Variables
        self.appName   = "novelWriter"
        self.appHandle = "novelwriter"

        # Set Paths
        confRoot = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.ConfigLocation)
        )
        dataRoot = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation)
        )

        self._confPath = confRoot.absolute() / self.appHandle  # The user config location
        self._dataPath = dataRoot.absolute() / self.appHandle  # The user data location
        self._homePath = Path.home().absolute()  # The user's home directory
        self._backPath = self._homePath / "Backups"

        self._appPath = Path(__file__).parent.absolute()
        self._appRoot = self._appPath.parent
        if getattr(sys, "frozen", False):  # pragma: no cover
            # novelWriter is packaged as an exe
            self._appPath = Path(__file__).parent.parent.absolute()
            self._appRoot = self._appPath

        # Runtime Settings and Variables
        self._hasError = False  # True if the config class encountered an error
        self._errData  = []     # List of error messages

        # Localisation
        # Note that these paths must be strings
        self._nwLangPath = self._appPath / "assets" / "i18n"
        self._qtLangPath = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)

        hasLocale = (self._nwLangPath / f"nw_{QLocale.system().name()}.qm").exists()
        self._qLocale = QLocale.system() if hasLocale else QLocale("en_GB")
        self._dLocale = QLocale.system()
        self._dShortDate = self._dLocale.dateFormat(QLocale.FormatType.ShortFormat)
        self._dShortDateTime = self._dLocale.dateTimeFormat(QLocale.FormatType.ShortFormat)
        self._qtTrans = {}

        # PDF Manual
        self._manuals: dict[str, Path] = {}
        if (assets := self._appPath / "assets").is_dir():
            for item in assets.iterdir():
                if item.is_file() and item.stem.startswith("manual") and item.suffix == ".pdf":
                    self._manuals[item.stem] = item

        # User Settings
        # =============

        self._recentProjects = RecentProjects(self)
        self._recentPaths = RecentPaths(self)
        self._lastAuthor = ""

        # General GUI Settings
        self.guiLocale    = self._qLocale.name()
        self.lightTheme   = DEF_GUI_LIGHT  # Light GUI theme
        self.darkTheme    = DEF_GUI_DARK   # Dark GUI theme
        self.themeMode    = nwTheme.AUTO   # Colour theme mode
        self.guiFont      = QFont()        # Main GUI font
        self.hideVScroll  = False          # Hide vertical scroll bars on main widgets
        self.hideHScroll  = False          # Hide horizontal scroll bars on main widgets
        self.lastNotes    = "0x0"          # The latest release notes that have been shown
        self.nativeFont   = True           # Use native font dialog
        self.useCharCount = False          # Use character count as primary count
        self.vimMode      = False          # Enable vim mode

        # Icons
        self.iconTheme   = DEF_ICONS    # Icons theme
        self.iconColTree = DEF_TREECOL  # Project tree icon colours
        self.iconColDocs = False        # Keep theme colours on documents

        # Size Settings
        self.mainWinSize    = [1200, 650]  # Last size of the main GUI window
        self.welcomeWinSize = [800, 550]   # Last size of the welcome window
        self.prefsWinSize   = [700, 615]   # Last size of the Preferences dialog
        self.mainPanePos    = [300, 800]   # Last position of the main window splitter
        self.viewPanePos    = [500, 150]   # Last position of the document viewer splitter
        self.outlinePanePos = [500, 150]   # Last position of the outline panel splitter

        # Project Settings
        self.autoSaveProj    = 60     # Interval for auto-saving project, in seconds
        self.autoSaveDoc     = 30     # Interval for auto-saving document, in seconds
        self.emphLabels      = False  # Add emphasis to H1 and H2 item labels
        self.backupOnClose   = True   # Flag for running automatic backups
        self.askBeforeBackup = True   # Flag for asking before running automatic backup
        self.askBeforeExit   = True   # Flag for asking before exiting the app

        # Text Editor Settings
        self.textFont        = QFont()  # Editor font
        self.textWidth       = 700      # Editor text width
        self.textMargin      = 40       # Editor/viewer text margin
        self.tabWidth        = 40       # Editor tabulator width
        self.cursorWidth     = 1        # Editor cursor width
        self.lineHighlight   = False    # Highlight current line in editor

        self.focusWidth      = 800      # Focus Mode text width
        self.hideFocusFooter = False    # Hide document footer in Focus Mode
        self.showFullPath    = True     # Show full document path in editor header
        self.autoSelect      = True     # Auto-select word when applying format with no selection

        self.doJustify       = False    # Justify text
        self.showTabsNSpaces = False    # Show tabs and spaces in editor
        self.showLineEndings = False    # Show line endings in editor
        self.showMultiSpaces = True     # Highlight multiple spaces in the text

        self.doReplace       = True     # Enable auto-replace as you type
        self.doReplaceSQuote = True     # Smart single quotes
        self.doReplaceDQuote = True     # Smart double quotes
        self.doReplaceDash   = True     # Replace multiple hyphens with dashes
        self.doReplaceDots   = True     # Replace three dots with ellipsis

        self.autoScroll      = True     # Typewriter-like scrolling
        self.autoScrollPos   = 30       # Start point for typewriter-like scrolling
        self.scrollPastEnd   = True     # Scroll past end of document, and centre cursor

        self.dialogStyle     = 2        # Quote type to use for dialogue
        self.allowOpenDial   = True     # Allow open-ended dialogue quotes
        self.dialogLine      = ""       # Symbol to use for dialogue line
        self.narratorBreak   = ""       # Symbol to use for narrator break
        self.narratorDialog  = ""       # Symbol for alternating between dialogue and narrator
        self.altDialogOpen   = ""       # Alternative dialog symbol, open
        self.altDialogClose  = ""       # Alternative dialog symbol, close
        self.highlightEmph   = True     # Add colour to text emphasis

        self.stopWhenIdle    = True     # Stop the status bar clock when the user is idle
        self.userIdleTime    = 300      # Time of inactivity to consider user idle
        self.incNotesWCount  = True     # The status bar word count includes notes

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
        self._backupPath = self._backPath  # Backup path to use, can be none

        # Spell Checking Settings
        self.spellLanguage = "en"

        # State
        self.showViewerPanel = True   # The panel for the viewer is visible
        self.showEditToolBar = False  # The document editor toolbar visibility
        self.showSessionTime = True   # Show the session time in the status bar
        self.viewComments    = True   # Comments are shown in the viewer
        self.viewSynopsis    = True   # Synopsis is shown in the viewer
        self.viewNotes       = True   # Notes are shown in the viewer

        # Search Box States
        self.searchCase      = False
        self.searchWord      = False
        self.searchRegEx     = False
        self.searchLoop      = False
        self.searchNextFile  = False
        self.searchMatchCap  = False
        self.searchProjCase  = False
        self.searchProjWord  = False
        self.searchProjRegEx = False

        # System and App Information
        # ==========================

        # Check Qt Versions
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
    def pdfDocs(self) -> Path | None:
        """Return the local manual PDF file, if any exist."""
        return self._manuals.get(f"manual_{self.locale.bcp47Name()}", self._manuals.get("manual"))

    @property
    def nwLangPath(self) -> Path:
        return self._nwLangPath

    @property
    def locale(self) -> QLocale:
        return self._dLocale

    @property
    def recentProjects(self) -> RecentProjects:
        return self._recentProjects

    @property
    def lastAuthor(self) -> str:
        """Return the last author name used."""
        return simplified(self._lastAuthor)

    ##
    #  Getters
    ##

    def getTextWidth(self, focusMode: bool = False) -> int:
        """Get the text with for the correct editor mode."""
        if focusMode:
            return max(self.focusWidth, 200)
        else:
            return max(self.textWidth, 200)

    ##
    #  Setters
    ##

    def setLastAuthor(self, value: str) -> None:
        """Set tle last used author name."""
        self._lastAuthor = simplified(value)
        return

    def setMainWinSize(self, width: int, height: int) -> None:
        """Set the size of the main window, but only if the change is
        larger than 5 pixels. The OS window manager will sometimes
        adjust it a bit, and we don't want the main window to shrink or
        grow each time the app is opened.
        """
        if abs(self.mainWinSize[0] - width) > 5:
            self.mainWinSize[0] = width
        if abs(self.mainWinSize[1] - height) > 5:
            self.mainWinSize[1] = height
        return

    def setWelcomeWinSize(self, width: int, height: int) -> None:
        """Set the size of the Preferences dialog window."""
        self.welcomeWinSize = [width, height]
        return

    def setPreferencesWinSize(self, width: int, height: int) -> None:
        """Set the size of the Preferences dialog window."""
        self.prefsWinSize = [width, height]
        return

    def setLastPath(self, key: str, path: str | Path) -> None:
        """Set the last used path. Only the folder is saved, so if the
        path is not a folder, the parent of the path is used instead.
        """
        if isinstance(path, str | Path):
            path = checkPath(path, self._homePath)
            if not path.is_dir():
                path = path.parent
            if path.is_dir():
                self._recentPaths.setPath(key, path)
        return

    def setBackupPath(self, path: Path | str) -> None:
        """Set the current backup path."""
        self._backupPath = checkPath(path, self._backPath)
        return

    def setGuiFont(self, value: QFont | str | None) -> None:
        """Update the GUI's font style from settings."""
        if isinstance(value, QFont):
            self.guiFont = fontMatcher(value)
        elif value and isinstance(value, str):
            font = QFont()
            font.fromString(value)
            self.guiFont = fontMatcher(font)
        else:
            font = QFont()
            if self.osWindows and "Arial" in QFontDatabase.families():
                # On Windows we default to Arial if possible
                font.setFamily("Arial")
                font.setPointSize(10)
            else:
                font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
            self.guiFont = fontMatcher(font)
            logger.debug("Main font set to: %s", describeFont(font))
        QApplication.setFont(self.guiFont)
        return

    def setTextFont(self, value: QFont | str | None) -> None:
        """Set the text font if it exists. If it doesn't, or is None,
        set to default font.
        """
        if isinstance(value, QFont):
            self.textFont = fontMatcher(value)
        elif value and isinstance(value, str):
            font = QFont()
            font.fromString(value)
            self.textFont = fontMatcher(font)
        else:
            fontFam = QFontDatabase.families()
            if self.osWindows and "Arial" in fontFam:
                font = QFont()
                font.setFamily("Arial")
                font.setPointSize(12)
            elif self.osDarwin and "Helvetica" in fontFam:
                font = QFont()
                font.setFamily("Helvetica")
                font.setPointSize(12)
            else:
                font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
            self.textFont = fontMatcher(font)
            logger.debug("Text font set to: %s", describeFont(self.textFont))
        return

    ##
    #  Methods
    ##

    def homePath(self) -> Path:
        """The user's home folder."""
        return self._homePath

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

    def lastPath(self, key: str) -> Path:
        """Return the last path used by the user, if it exists."""
        if path := self._recentPaths.getPath(key):
            asPath = Path(path)
            if asPath.is_dir():
                return asPath
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

    def localDate(self, value: datetime) -> str:
        """Return a localised date format."""
        # Explicitly convert the date first, see bug #2325
        return self._dLocale.toString(QDate(value.year, value.month, value.day), self._dShortDate)

    def localDateTime(self, value: datetime) -> str:
        """Return a localised datetime format."""
        # Explicitly convert the datetime first, see bug #2325
        return self._dLocale.toString(
            QDateTime(value.year, value.month, value.day, value.hour, value.minute, value.second),
            self._dShortDateTime,
        )

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

    def splashMessage(self, message: str) -> None:
        """Send a message to the splash screen."""
        if self._splash:
            self._splash.showStatus(message)
        return

    ##
    #  Config Actions
    ##

    def initConfig(
        self, confPath: str | Path | None = None, dataPath: str | Path | None = None
    ) -> None:
        """Initialise the config class. The manual setting of confPath
        and dataPath is mainly intended for the test suite.
        """
        logger.debug("Initialising Config ...")
        if isinstance(confPath, str | Path):
            logger.info("Setting alternative config path: %s", confPath)
            self._confPath = Path(confPath)
        if isinstance(dataPath, str | Path):
            logger.info("Setting alternative data path: %s", dataPath)
            self._dataPath = Path(dataPath)

        logger.debug("Config Path: %s", self._confPath)
        logger.debug("Data Path: %s", self._dataPath)
        logger.debug("App Root: %s", self._appRoot)
        logger.debug("App Path: %s", self._appPath)
        logger.debug("PDF Manual: %s", self.pdfDocs)

        # If the config and data folders don't exist, create them
        # This assumes that the os config and data folders exist
        self._confPath.mkdir(exist_ok=True)
        self._dataPath.mkdir(exist_ok=True)

        # Also create the themes and icons folders if possible
        if self._dataPath.is_dir():
            (self._dataPath / "cache").mkdir(exist_ok=True)
            (self._dataPath / "icons").mkdir(exist_ok=True)
            (self._dataPath / "themes").mkdir(exist_ok=True)

        self._recentPaths.loadCache()
        self._recentProjects.loadCache()
        self._checkOptionalPackages()

        logger.debug("Config instance initialised")

        return

    def initLocalisation(self, nwApp: QApplication) -> None:
        """Initialise the localisation of the GUI."""
        self.splashMessage("Loading localisation ...")

        self._qLocale = QLocale(self.guiLocale)
        QLocale.setDefault(self._qLocale)
        self._qtTrans = {}

        hasLocale = (self._nwLangPath / f"nw_{self._qLocale.name()}.qm").exists()
        self._dLocale = self._qLocale if hasLocale else QLocale.system()
        self._dShortDate = self._dLocale.dateFormat(QLocale.FormatType.ShortFormat)
        self._dShortDateTime = self._dLocale.dateTimeFormat(QLocale.FormatType.ShortFormat)

        langList = [
            (self._qtLangPath, "qtbase"),   # Qt
            (str(self._nwLangPath), "nw"),  # novelWriter
        ]
        for lngPath, lngBase in langList:
            for lngCode in self._qLocale.uiLanguages():
                qTrans = QTranslator()
                lngFile = "{0}_{1}".format(lngBase, lngCode.replace("-", "_"))
                if lngFile not in self._qtTrans:
                    if qTrans.load(lngFile, lngPath):
                        logger.debug("Loaded: %s.qm", lngFile)
                        nwApp.installTranslator(qTrans)
                        self._qtTrans[lngFile] = qTrans

        return

    def loadConfig(self, splash: NSplashScreen | None = None) -> bool:
        """Load preferences from file and replace default settings."""
        self._splash = splash
        self.splashMessage("Loading user configuration ...")

        logger.debug("Loading config file")

        conf = NWConfigParser()
        cnfPath = self._confPath / nwFiles.CONF_FILE

        if not cnfPath.exists():
            # Initial file, so we just create one from defaults
            self.setGuiFont(None)
            self.setTextFont(None)
            self.saveConfig()
            return True

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
        self.setGuiFont(conf.rdStr(sec, "font", ""))
        self.lightTheme   = conf.rdStr(sec, "lighttheme", self.lightTheme)
        self.darkTheme    = conf.rdStr(sec, "darktheme", self.darkTheme)
        self.themeMode    = conf.rdEnum(sec, "thememode", self.themeMode)
        self.iconTheme    = conf.rdStr(sec, "icons", self.iconTheme)
        self.iconColTree  = conf.rdStr(sec, "iconcoltree", self.iconColTree)
        self.iconColDocs  = conf.rdBool(sec, "iconcoldocs", self.iconColDocs)
        self.guiLocale    = conf.rdStr(sec, "localisation", self.guiLocale)
        self.hideVScroll  = conf.rdBool(sec, "hidevscroll", self.hideVScroll)
        self.hideHScroll  = conf.rdBool(sec, "hidehscroll", self.hideHScroll)
        self.lastNotes    = conf.rdStr(sec, "lastnotes", self.lastNotes)
        self.nativeFont   = conf.rdBool(sec, "nativefont", self.nativeFont)
        self.useCharCount = conf.rdBool(sec, "usecharcount", self.useCharCount)

        # Sizes
        sec = "Sizes"
        self.mainWinSize    = conf.rdIntList(sec, "mainwindow", self.mainWinSize)
        self.welcomeWinSize = conf.rdIntList(sec, "welcome", self.welcomeWinSize)
        self.prefsWinSize   = conf.rdIntList(sec, "preferences", self.prefsWinSize)
        self.mainPanePos    = conf.rdIntList(sec, "mainpane", self.mainPanePos)
        self.viewPanePos    = conf.rdIntList(sec, "viewpane", self.viewPanePos)
        self.outlinePanePos = conf.rdIntList(sec, "outlinepane", self.outlinePanePos)

        # Project
        sec = "Project"
        self.autoSaveProj    = conf.rdInt(sec, "autosaveproject", self.autoSaveProj)
        self.autoSaveDoc     = conf.rdInt(sec, "autosavedoc", self.autoSaveDoc)
        self.emphLabels      = conf.rdBool(sec, "emphlabels", self.emphLabels)
        self._backupPath     = conf.rdPath(sec, "backuppath", self._backupPath)
        self.backupOnClose   = conf.rdBool(sec, "backuponclose", self.backupOnClose)
        self.askBeforeBackup = conf.rdBool(sec, "askbeforebackup", self.askBeforeBackup)
        self.askBeforeExit   = conf.rdBool(sec, "askbeforeexit", self.askBeforeExit)
        self._lastAuthor     = conf.rdStr(sec, "lastauthor", self._lastAuthor)

        # Editor
        sec = "Editor"
        self.setTextFont(conf.rdStr(sec, "textfont", ""))
        self.textWidth       = conf.rdInt(sec, "width", self.textWidth)
        self.textMargin      = conf.rdInt(sec, "margin", self.textMargin)
        self.tabWidth        = conf.rdInt(sec, "tabwidth", self.tabWidth)
        self.cursorWidth     = conf.rdInt(sec, "cursorwidth", self.cursorWidth)
        self.lineHighlight   = conf.rdBool(sec, "linehighlight", self.lineHighlight)
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
        self.dialogStyle     = conf.rdInt(sec, "dialogstyle", self.dialogStyle)
        self.allowOpenDial   = conf.rdBool(sec, "allowopendial", self.allowOpenDial)
        dialogLine           = conf.rdStr(sec, "dialogline", self.dialogLine)
        narratorBreak        = conf.rdStr(sec, "narratorbreak", self.narratorBreak)
        narratorDialog       = conf.rdStr(sec, "narratordialog", self.narratorDialog)
        self.altDialogOpen   = conf.rdStr(sec, "altdialogopen", self.altDialogOpen)
        self.altDialogClose  = conf.rdStr(sec, "altdialogclose", self.altDialogClose)
        self.highlightEmph   = conf.rdBool(sec, "highlightemph", self.highlightEmph)
        self.stopWhenIdle    = conf.rdBool(sec, "stopwhenidle", self.stopWhenIdle)
        self.userIdleTime    = conf.rdInt(sec, "useridletime", self.userIdleTime)

        # State
        sec = "State"
        self.showViewerPanel = conf.rdBool(sec, "showviewerpanel", self.showViewerPanel)
        self.showEditToolBar = conf.rdBool(sec, "showedittoolbar", self.showEditToolBar)
        self.showSessionTime = conf.rdBool(sec, "showsessiontime", self.showSessionTime)
        self.viewComments    = conf.rdBool(sec, "viewcomments", self.viewComments)
        self.viewSynopsis    = conf.rdBool(sec, "viewsynopsis", self.viewSynopsis)
        self.viewNotes       = conf.rdBool(sec, "viewnotes", self.viewNotes)
        self.searchCase      = conf.rdBool(sec, "searchcase", self.searchCase)
        self.searchWord      = conf.rdBool(sec, "searchword", self.searchWord)
        self.searchRegEx     = conf.rdBool(sec, "searchregex", self.searchRegEx)
        self.searchLoop      = conf.rdBool(sec, "searchloop", self.searchLoop)
        self.searchNextFile  = conf.rdBool(sec, "searchnextfile", self.searchNextFile)
        self.searchMatchCap  = conf.rdBool(sec, "searchmatchcap", self.searchMatchCap)
        self.searchProjCase  = conf.rdBool(sec, "searchprojcase", self.searchProjCase)
        self.searchProjWord  = conf.rdBool(sec, "searchprojword", self.searchProjWord)
        self.searchProjRegEx = conf.rdBool(sec, "searchprojregex", self.searchProjRegEx)

        # Check Values
        # ============

        self._prepareFont(self.guiFont, "main")
        self._prepareFont(self.textFont, "document")

        # If we're using straight quotes, disable auto-replace
        if self.fmtSQuoteOpen == self.fmtSQuoteClose == "'" and self.doReplaceSQuote:
            logger.info("Using straight single quotes, so disabling auto-replace")
            self.doReplaceSQuote = False

        if self.fmtDQuoteOpen == self.fmtDQuoteClose == '"' and self.doReplaceDQuote:
            logger.info("Using straight double quotes, so disabling auto-replace")
            self.doReplaceDQuote = False

        self.dialogLine = processDialogSymbols(dialogLine)
        self.narratorBreak = narratorBreak if narratorBreak in nwQuotes.DASHES else ""
        self.narratorDialog = narratorDialog if narratorDialog in nwQuotes.DASHES else ""

        return True

    def saveConfig(self) -> bool:
        """Save the current preferences to file."""
        logger.debug("Saving config file")

        conf = NWConfigParser()

        conf["Meta"] = {
            "timestamp": formatTimeStamp(time()),
        }

        conf["Main"] = {
            "font":         self.guiFont.toString(),
            "lighttheme":   str(self.lightTheme),
            "darktheme":    str(self.darkTheme),
            "thememode":    self.themeMode.name,
            "icons":        str(self.iconTheme),
            "iconcoltree":  str(self.iconColTree),
            "iconcoldocs":  str(self.iconColDocs),
            "localisation": str(self.guiLocale),
            "hidevscroll":  str(self.hideVScroll),
            "hidehscroll":  str(self.hideHScroll),
            "lastnotes":    str(self.lastNotes),
            "nativefont":   str(self.nativeFont),
            "usecharcount": str(self.useCharCount),
        }

        conf["Sizes"] = {
            "mainwindow":  self._packList(self.mainWinSize),
            "welcome":     self._packList(self.welcomeWinSize),
            "preferences": self._packList(self.prefsWinSize),
            "mainpane":    self._packList(self.mainPanePos),
            "viewpane":    self._packList(self.viewPanePos),
            "outlinepane": self._packList(self.outlinePanePos),
        }

        conf["Project"] = {
            "autosaveproject": str(self.autoSaveProj),
            "autosavedoc":     str(self.autoSaveDoc),
            "emphlabels":      str(self.emphLabels),
            "backuppath":      str(self._backupPath),
            "backuponclose":   str(self.backupOnClose),
            "askbeforebackup": str(self.askBeforeBackup),
            "askbeforeexit":   str(self.askBeforeExit),
            "lastauthor":      str(self._lastAuthor),
        }

        conf["Editor"] = {
            "textfont":        self.textFont.toString(),
            "width":           str(self.textWidth),
            "margin":          str(self.textMargin),
            "tabwidth":        str(self.tabWidth),
            "cursorwidth":     str(self.cursorWidth),
            "lineHighlight":   str(self.lineHighlight),
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
            "dialogstyle":     str(self.dialogStyle),
            "allowopendial":   str(self.allowOpenDial),
            "dialogline":      str(self.dialogLine),
            "narratorbreak":   str(self.narratorBreak),
            "narratordialog":  str(self.narratorDialog),
            "altdialogopen":   str(self.altDialogOpen),
            "altdialogclose":  str(self.altDialogClose),
            "highlightemph":   str(self.highlightEmph),
            "stopwhenidle":    str(self.stopWhenIdle),
            "useridletime":    str(self.userIdleTime),
        }

        conf["State"] = {
            "showviewerpanel": str(self.showViewerPanel),
            "showedittoolbar": str(self.showEditToolBar),
            "showsessiontime": str(self.showSessionTime),
            "viewcomments":    str(self.viewComments),
            "viewsynopsis":    str(self.viewSynopsis),
            "viewnotes":       str(self.viewNotes),
            "searchcase":      str(self.searchCase),
            "searchword":      str(self.searchWord),
            "searchregex":     str(self.searchRegEx),
            "searchloop":      str(self.searchLoop),
            "searchnextfile":  str(self.searchNextFile),
            "searchmatchcap":  str(self.searchMatchCap),
            "searchprojcase":  str(self.searchProjCase),
            "searchprojword":  str(self.searchProjWord),
            "searchprojregex": str(self.searchProjRegEx),
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

    def finishStartup(self) -> None:
        """Call after startup is complete."""
        self._splash = None
        return

    ##
    #  Internal Functions
    ##

    def _packList(self, data: list) -> str:
        """Pack a list of items into a comma-separated string for saving
        to the config file.
        """
        return ", ".join(str(inVal) for inVal in data)

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

    def _prepareFont(self, font: QFont, kind: str) -> None:
        """Check Unicode availability in font. This also initialises any
        alternative character used for missing glyphs. See #2315.
        """
        self.splashMessage(f"Initialising {kind} font: {font.family()}")
        metrics = QFontMetrics(font)
        for char in nwUnicode.UI_SYMBOLS:
            if not metrics.inFont(char):  # type: ignore
                logger.warning("No glyph U+%04x in font", ord(char))  # pragma: no cover
        return


class RecentProjects:

    def __init__(self, config: Config) -> None:
        self._conf = config
        self._data: dict[str, dict[str, str | int]] = {}
        self._map: dict[str, str] = {}
        return

    def loadCache(self) -> bool:
        """Load the cache file for recent projects."""
        self._data = {}
        self._map = {}
        cacheFile = self._conf.dataPath(nwFiles.RECENT_FILE)
        if cacheFile.is_file():
            try:
                with open(cacheFile, mode="r", encoding="utf-8") as inFile:
                    data = json.load(inFile)
                for path, entry in data.items():
                    puuid = str(entry.get("uuid", ""))
                    title = str(entry.get("title", ""))
                    words = checkInt(entry.get("words", 0), 0)
                    chars = checkInt(entry.get("chars", 0), 0)
                    saved = checkInt(entry.get("time", 0), 0)
                    if path and title:
                        self._setEntry(puuid, path, title, words, chars, saved)
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

    def update(self, path: str | Path, data: NWProjectData, saved: float | int) -> None:
        """Add or update recent cache information on a given project."""
        try:
            if (remove := self._map.get(data.uuid)) and (remove != str(path)):
                self.remove(remove)
            self._setEntry(
                data.uuid,
                str(path),
                data.name,
                sum(data.currCounts[:2]),
                sum(data.currCounts[2:]),
                int(saved),
            )
            self.saveCache()
        except Exception:
            pass
        return

    def remove(self, path: str | Path) -> None:
        """Try to remove a path from the recent projects cache."""
        if self._data.pop(str(path), None) is not None:
            logger.debug("Removed recent: %s", path)
            self.saveCache()
        return

    def _setEntry(
        self, puuid: str, path: str, title: str, words: int, chars: int, saved: int
    ) -> None:
        """Set an entry in the recent projects record."""
        self._data[path] = {
            "uuid": puuid,
            "title": title,
            "words": words,
            "chars": chars,
            "time": saved,
        }
        if puuid:
            self._map[puuid] = path
        return


class RecentPaths:

    KEYS: Final[list[str]] = ["default", "project", "import", "outline", "stats"]

    def __init__(self, config: Config) -> None:
        self._conf = config
        self._data = {}
        return

    def setPath(self, key: str, path: Path | str) -> None:
        """Set a path for a given key, and save the cache."""
        if key in self.KEYS:
            self._data[key] = str(path)
        self.saveCache()
        return

    def getPath(self, key: str) -> str | None:
        """Get a path for a given key, or return None."""
        return self._data.get(key)

    def loadCache(self) -> bool:
        """Load the cache file for recent paths."""
        self._data = {}
        cacheFile = self._conf.dataPath(nwFiles.RECENT_PATH)
        if cacheFile.is_file():
            try:
                with open(cacheFile, mode="r", encoding="utf-8") as inFile:
                    data = json.load(inFile)
                if isinstance(data, dict):
                    for key, path in data.items():
                        if key in self.KEYS and isinstance(path, str):
                            self._data[key] = path
            except Exception:
                logger.error("Could not load recent paths cache")
                logException()
                return False
        return True

    def saveCache(self) -> bool:
        """Save the cache dictionary of recent paths."""
        cacheFile = self._conf.dataPath(nwFiles.RECENT_PATH)
        cacheTemp = cacheFile.with_suffix(".tmp")
        try:
            with open(cacheTemp, mode="w+", encoding="utf-8") as outFile:
                json.dump(self._data, outFile, indent=2)
            cacheTemp.replace(cacheFile)
        except Exception:
            logger.error("Could not save recent paths cache")
            logException()
            return False
        return True
