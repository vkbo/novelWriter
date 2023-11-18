"""
novelWriter – Shared Data Class
===============================

File History:
Created: 2023-08-10 [2.1rc1]

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

from time import time
from typing import TYPE_CHECKING
from pathlib import Path

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QWidget

from novelwriter.core.spellcheck import NWSpellEnchant

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain
    from novelwriter.gui.theme import GuiTheme
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)


class SharedData(QObject):

    __slots__ = (
        "_gui", "_theme", "_project", "_spelling", "_lockedBy", "_alert",
        "_idleTime", "_idleRefTime",
    )

    projectStatusChanged = pyqtSignal(bool)
    projectStatusMessage = pyqtSignal(str)
    spellLanguageChanged = pyqtSignal(str, str)
    indexScannedText = pyqtSignal(str)
    indexChangedTags = pyqtSignal(list, list)
    indexCleared = pyqtSignal()
    indexAvailable = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        # Objects
        self._gui = None
        self._theme = None
        self._project = None
        self._spelling = None

        # Settings
        self._lockedBy = None
        self._alert = None
        self._idleTime = 0.0
        self._idleRefTime = time()

        return

    ##
    #  Properties
    ##

    @property
    def mainGui(self) -> GuiMain:
        """Return the Main GUI instance."""
        if self._gui is None:
            raise Exception("SharedData class not fully initialised")
        return self._gui

    @property
    def theme(self) -> GuiTheme:
        """Return the GUI Theme instance."""
        if self._theme is None:
            raise Exception("SharedData class not fully initialised")
        return self._theme

    @property
    def project(self) -> NWProject:
        """Return the active NWProject instance."""
        if self._project is None:
            raise Exception("SharedData class not fully initialised")
        return self._project

    @property
    def spelling(self) -> NWSpellEnchant:
        """Return the active NWProject instance."""
        if self._spelling is None:
            raise Exception("SharedData class not fully initialised")
        return self._spelling

    @property
    def hasProject(self) -> bool:
        """Return True if the project instance is populated."""
        return self.project.isValid

    @property
    def projectLock(self) -> list | None:
        """Return cached lock information for the last project."""
        return self._lockedBy

    @property
    def projectIdleTime(self) -> float:
        """Return the session idle time."""
        return self._idleTime

    @property
    def alert(self) -> _GuiAlert | None:
        """Return a pointer to the last alert box."""
        return self._alert

    ##
    #  Methods
    ##

    def initSharedData(self, gui: GuiMain, theme: GuiTheme) -> None:
        """Initialise the SharedData instance. This must be called as
        soon as the Main GUI is created to ensure the SHARED singleton
        has the properties needed for operation.
        """
        self._gui = gui
        self._theme = theme
        self._resetProject()
        logger.debug("Ready: SharedData")
        logger.debug("Thread Pool Max Count: %d", QThreadPool.globalInstance().maxThreadCount())
        return

    def openProject(self, path: str | Path, clearLock: bool = False) -> bool:
        """Open a project."""
        if self.project.isValid:
            logger.error("A project is already open")
            return False

        self._lockedBy = None
        status = self.project.openProject(path, clearLock=clearLock)
        if status is False:
            # We must cache the lock status before resetting the project
            self._lockedBy = self.project.lockStatus
            self._resetProject()

        self.updateSpellCheckLanguage(reload=True)
        self._resetIdleTimer()

        return status

    def saveProject(self, autoSave: bool = False) -> bool:
        """Save the current project."""
        if not self.project.isValid:
            logger.error("There is no project open")
            return False
        return self.project.saveProject(autoSave=autoSave)

    def saveAndCloseProject(self) -> bool:
        """Save and close the current project."""
        if not self.project.isValid:
            logger.error("There is no project open")
            return False
        self.project.saveProjectMeta(self._idleTime)
        saveOk = self.project.saveProject()
        self.project.closeProject()
        self._resetProject()
        self._resetIdleTimer()
        return saveOk

    def updateSpellCheckLanguage(self, reload: bool = False) -> None:
        """Update the active spell check language from settings."""
        from novelwriter import CONFIG
        language = self.project.data.spellLang or CONFIG.spellLanguage
        if language != self.spelling.spellLanguage or reload:
            self.spelling.setLanguage(language)
            _, provider = self.spelling.describeDict()
            self.spellLanguageChanged.emit(language, provider)
        return

    def updateIdleTime(self, currTime: float, userIdle: bool) -> None:
        """Update the idle time record. If the userIdle flag is True,
        the user idle counter is updated with the time difference since
        the last time this function was called. Otherwise, only the
        reference time is updated.
        """
        if userIdle:
            self._idleTime += currTime - self._idleRefTime
        self._idleRefTime = currTime
        return

    def newStatusMessage(self, message: str) -> None:
        """Request a new status message. This is a callable function for
        core classes that cannot emit signals on their own.
        """
        self.projectStatusMessage.emit(message)
        return

    def setGlobalProjectState(self, state: bool) -> None:
        """Change the global project status. This is a callable function
        for core classes that cannot emit signals on their own.
        """
        self.projectStatusChanged.emit(state)
        return

    def runInThreadPool(self, runnable: QRunnable, priority: int = 0) -> None:
        """Queue a runnable in the application thread pool."""
        QThreadPool.globalInstance().start(runnable, priority=priority)
        return

    ##
    #  Signal Proxy
    ##

    def indexSignalProxy(self, data: dict) -> None:
        """Emit signals on behalf of the index."""
        event = data.get("event")
        logger.debug("Received '%s' event from the index", event)
        if event == "updateTags":
            self.indexChangedTags.emit(data.get("updated", []), data.get("deleted", []))
        elif event == "scanText":
            self.indexScannedText.emit(data.get("handle", ""))
        elif event == "clearIndex":
            self.indexCleared.emit()
        elif event == "buildIndex":
            self.indexAvailable.emit()
        return

    ##
    #  Alert Boxes
    ##

    def info(self, text: str, info: str = "", details: str = "", log: bool = True) -> None:
        """Open an information alert box."""
        self._alert = _GuiAlert(self.mainGui, self.theme)
        self._alert.setMessage(text, info, details)
        self._alert.setAlertType(_GuiAlert.INFO, False)
        if log:
            logger.info(self._alert.logMessage, stacklevel=2)
        self._alert.exec_()
        return

    def warn(self, text: str, info: str = "", details: str = "", log: bool = True) -> None:
        """Open a warning alert box."""
        self._alert = _GuiAlert(self.mainGui, self.theme)
        self._alert.setMessage(text, info, details)
        self._alert.setAlertType(_GuiAlert.WARN, False)
        if log:
            logger.warning(self._alert.logMessage, stacklevel=2)
        self._alert.exec_()
        return

    def error(self, text: str, info: str = "", details: str = "", log: bool = True,
              exc: Exception | None = None) -> None:
        """Open an error alert box."""
        self._alert = _GuiAlert(self.mainGui, self.theme)
        self._alert.setMessage(text, info, details)
        self._alert.setAlertType(_GuiAlert.ERROR, False)
        if exc:
            self._alert.setException(exc)
        if log:
            logger.error(self._alert.logMessage, stacklevel=2)
        self._alert.exec_()
        return

    def question(self, text: str, info: str = "", details: str = "", warn: bool = False) -> bool:
        """Open a question box."""
        self._alert = _GuiAlert(self.mainGui, self.theme)
        self._alert.setMessage(text, info, details)
        self._alert.setAlertType(_GuiAlert.WARN if warn else _GuiAlert.ASK, True)
        self._alert.exec_()
        return self._alert.result() == QMessageBox.Yes

    ##
    #  Internal Functions
    ##

    def _resetProject(self) -> None:
        """Create a new project and spell checking instance."""
        from novelwriter.core.project import NWProject
        if isinstance(self._project, NWProject):
            del self._project
            del self._spelling
        self._project = NWProject()
        self._spelling = NWSpellEnchant(self._project)
        self.updateSpellCheckLanguage()
        return

    def _resetIdleTimer(self) -> None:
        """Reset the timer data for the idle timer."""
        self._idleRefTime = time()
        self._idleTime = 0.0
        return

# END Class SharedData


class _GuiAlert(QMessageBox):

    INFO = 0
    WARN = 1
    ERROR = 2
    ASK = 3

    def __init__(self, parent: QWidget, theme: GuiTheme) -> None:
        super().__init__(parent=parent)
        self._theme = theme
        self._message = ""
        return

    @property
    def logMessage(self) -> str:
        return self._message

    def setMessage(self, text: str, info: str, details: str) -> None:
        """Set the alert box message."""
        self._message = " ".join(filter(None, [text, info, details]))
        self.setText(text)
        self.setInformativeText(info)
        self.setDetailedText(details)
        return

    def setException(self, exception: Exception) -> None:
        """Add exception details."""
        info = self.informativeText()
        text = f"<b>{type(exception).__name__}</b>: {str(exception)}"
        self.setInformativeText(f"{info}<br>{text}" if info else text)
        return

    def setAlertType(self, level: int, isYesNo: bool) -> None:
        """Set the type of alert and whether the dialog should have
        Yes/No buttons or just an Ok button.
        """
        if isYesNo:
            self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        else:
            self.setStandardButtons(QMessageBox.Ok)
        pSz = 2*self._theme.baseIconSize
        if level == self.INFO:
            self.setIconPixmap(self._theme.getPixmap("alert_info", (pSz, pSz)))
            self.setWindowTitle(self.tr("Information"))
        elif level == self.WARN:
            self.setIconPixmap(self._theme.getPixmap("alert_warn", (pSz, pSz)))
            self.setWindowTitle(self.tr("Warning"))
        elif level == self.ERROR:
            self.setIconPixmap(self._theme.getPixmap("alert_error", (pSz, pSz)))
            self.setWindowTitle(self.tr("Error"))
        elif level == self.ASK:
            self.setIconPixmap(self._theme.getPixmap("alert_question", (pSz, pSz)))
            self.setWindowTitle(self.tr("Question"))
        return

# END Class _GuiAlert
