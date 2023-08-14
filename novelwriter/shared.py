"""
novelWriter – Shared Data Class
===============================

File History:
Created: 2023-08-10 [2.1b2]

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

from typing import TYPE_CHECKING
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMessageBox, QWidget

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain
    from novelwriter.gui.theme import GuiTheme
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)


class SharedData(QObject):

    projectStatusChanged = pyqtSignal(bool)
    projectStatusMessage = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._gui = None
        self._theme = None
        self._project = None
        self._lockedBy = None
        self._alert = None
        return

    @property
    def mainGui(self) -> GuiMain:
        """Return the Main GUI instance."""
        if self._gui is None:
            raise Exception("UserData class not properly initialised")
        return self._gui

    @property
    def theme(self) -> GuiTheme:
        """Return the GUI Theme instance."""
        if self._theme is None:
            raise Exception("UserData class not properly initialised")
        return self._theme

    @property
    def project(self) -> NWProject:
        """Return the active NWProject instance."""
        if self._project is None:
            raise Exception("UserData class not properly initialised")
        return self._project

    @property
    def hasProject(self) -> bool:
        """Return True of the project instance is populated."""
        return self.project.isValid

    @property
    def projectLock(self) -> list | None:
        """Return cached lock information for the last project."""
        return self._lockedBy

    @property
    def alert(self) -> _GuiAlert | None:
        """Return a pointer to the last alert box."""
        return self._alert

    ##
    #  Methods
    ##

    def initSharedData(self, gui: GuiMain, theme: GuiTheme) -> None:
        """Initialise the UserData instance. This must be called as soon
        as the Main GUI is created to ensure the SHARED singleton has the
        properties needed for operation.
        """
        self._gui = gui
        self._theme = theme
        self._resetProject()
        logger.debug("SharedData instance initialised")
        return

    def openProject(self, path: str | Path) -> bool:
        """Open a project."""
        if self.project.isValid:
            logger.error("A project is already open")
            return False

        self._lockedBy = None
        status = self.project.openProject(path)
        if status is False:
            # We must cache the lock status before resetting the project
            self._lockedBy = self.project.lockStatus
            self._resetProject()

        return status

    def saveProject(self, autoSave: bool = False) -> bool:
        """Save the current project."""
        if not self.project.isValid:
            logger.error("There is no project open")
            return False
        return self.project.saveProject(autoSave=autoSave)

    def closeProject(self, idleTime: float) -> None:
        """Close the current project."""
        self.project.closeProject(idleTime)
        self._resetProject()
        return

    def unlockProject(self) -> bool:
        """Remove the project lock."""
        return self.project.storage.clearLockFile()

    ##
    #  Alert Boxes
    ##

    def info(self, text: str, info: str = "", details: str = "") -> None:
        """Open an information alert box."""
        self._alert = _GuiAlert(self.mainGui, self.theme)
        self._alert.setMessage(text, info, details)
        self._alert.setAlertType(_GuiAlert.INFO, False)
        logger.info(self._alert.logMessage, stacklevel=2)
        self._alert.exec_()
        return

    def warn(self, text: str, info: str = "", details: str = "") -> None:
        """Open a warning alert box."""
        self._alert = _GuiAlert(self.mainGui, self.theme)
        self._alert.setMessage(text, info, details)
        self._alert.setAlertType(_GuiAlert.WARN, False)
        logger.warning(self._alert.logMessage, stacklevel=2)
        self._alert.exec_()
        return

    def error(self, text: str, info: str = "", details: str = "",
              exc: Exception | None = None) -> None:
        """Open an error alert box."""
        self._alert = _GuiAlert(self.mainGui, self.theme)
        self._alert.setMessage(text, info, details)
        self._alert.setAlertType(_GuiAlert.ERROR, False)
        if exc:
            self._alert.setException(exc)
        logger.error(self._alert.logMessage, stacklevel=2)
        self._alert.exec_()
        return

    def question(self, text: str, info: str = "", details: str = "", warn: bool = False) -> bool:
        """Open an error alert box."""
        self._alert = _GuiAlert(self.mainGui, self.theme)
        self._alert.setMessage(text, info, details)
        self._alert.setAlertType(_GuiAlert.ERROR, True)
        self._alert.exec_()
        return self._alert.result() == QMessageBox.Yes

    ##
    #  Internal Slots
    ##

    @pyqtSlot(bool)
    def _emitProjectStatusChange(self, state: bool) -> None:
        """Forward the project status slot."""
        self.projectStatusChanged.emit(state)
        return

    @pyqtSlot(str)
    def _emitProjectStatusMeesage(self, message: str) -> None:
        """Forward the project message slot."""
        self.projectStatusMessage.emit(message)
        return

    ##
    #  Internal Functions
    ##

    def _resetProject(self) -> None:
        """Create a new project instance."""
        from novelwriter.core.project import NWProject
        if isinstance(self._project, NWProject):
            self._project.statusChanged.disconnect()
            self._project.statusMessage.disconnect()
            self._project.deleteLater()
        self._project = NWProject(self)
        self._project.statusChanged.connect(self._emitProjectStatusChange)
        self._project.statusMessage.connect(self._emitProjectStatusMeesage)
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
