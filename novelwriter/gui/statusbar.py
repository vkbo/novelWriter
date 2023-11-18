"""
novelWriter – GUI Main Window Status Bar
========================================

File History:
Created: 2019-04-20 [0.0.1]

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
from typing import TYPE_CHECKING, Literal

from PyQt5.QtCore import pyqtSlot, QLocale
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import qApp, QStatusBar, QLabel

from novelwriter import CONFIG, SHARED
from novelwriter.common import formatTime
from novelwriter.constants import nwConst
from novelwriter.extensions.statusled import StatusLED

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiMainStatus(QStatusBar):

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiMainStatus")

        self._refTime  = -1.0
        self._userIdle = False

        colNone = QColor(*SHARED.theme.statNone)
        colSaved = QColor(*SHARED.theme.statSaved)
        colUnsaved = QColor(*SHARED.theme.statUnsaved)

        iPx = SHARED.theme.baseIconSize

        # Permanent Widgets
        # =================

        xM = CONFIG.pxInt(8)

        # The Spell Checker Language
        self.langIcon = QLabel("")
        self.langText = QLabel(self.tr("None"))
        self.langIcon.setContentsMargins(0, 0, 0, 0)
        self.langText.setContentsMargins(0, 0, xM, 0)
        self.addPermanentWidget(self.langIcon)
        self.addPermanentWidget(self.langText)

        # The Editor Status
        self.docIcon = StatusLED(colNone, colSaved, colUnsaved, iPx, iPx, self)
        self.docText = QLabel(self.tr("Editor"))
        self.docIcon.setContentsMargins(0, 0, 0, 0)
        self.docText.setContentsMargins(0, 0, xM, 0)
        self.addPermanentWidget(self.docIcon)
        self.addPermanentWidget(self.docText)

        # The Project Status
        self.projIcon = StatusLED(colNone, colSaved, colUnsaved, iPx, iPx, self)
        self.projText = QLabel(self.tr("Project"))
        self.projIcon.setContentsMargins(0, 0, 0, 0)
        self.projText.setContentsMargins(0, 0, xM, 0)
        self.addPermanentWidget(self.projIcon)
        self.addPermanentWidget(self.projText)

        # The Project and Session Stats
        self.statsIcon = QLabel()
        self.statsText = QLabel("")
        self.statsIcon.setContentsMargins(0, 0, 0, 0)
        self.statsText.setContentsMargins(0, 0, xM, 0)
        self.addPermanentWidget(self.statsIcon)
        self.addPermanentWidget(self.statsText)

        # The Session Clock
        # Set the minimum width so the label doesn't rescale every second
        self.timeIcon = QLabel()
        self.timeText = QLabel("")
        self.timeText.setToolTip(self.tr("Session Time"))
        self.timeText.setMinimumWidth(SHARED.theme.getTextWidth("00:00:00:"))
        self.timeIcon.setContentsMargins(0, 0, 0, 0)
        self.timeText.setContentsMargins(0, 0, 0, 0)
        self.addPermanentWidget(self.timeIcon)
        self.addPermanentWidget(self.timeText)

        # Other Settings
        self.setSizeGripEnabled(True)

        logger.debug("Ready: GuiMainStatus")

        self.updateTheme()
        self.clearStatus()

        return

    def clearStatus(self) -> None:
        """Reset all widgets on the status bar to default values."""
        self.setRefTime(-1.0)
        self.setLanguage(*SHARED.spelling.describeDict())
        self.setProjectStats(0, 0)
        self.setProjectStatus(StatusLED.S_NONE)
        self.setDocumentStatus(StatusLED.S_NONE)
        self.updateTime()
        return

    def updateTheme(self) -> None:
        """Update theme elements."""
        iPx = SHARED.theme.baseIconSize
        self.langIcon.setPixmap(SHARED.theme.getPixmap("status_lang", (iPx, iPx)))
        self.statsIcon.setPixmap(SHARED.theme.getPixmap("status_stats", (iPx, iPx)))
        self.timePixmap = SHARED.theme.getPixmap("status_time", (iPx, iPx))
        self.idlePixmap = SHARED.theme.getPixmap("status_idle", (iPx, iPx))
        self.timeIcon.setPixmap(self.timePixmap)
        return

    ##
    #  Setters
    ##

    def setRefTime(self, refTime: float) -> None:
        """Set the reference time for the status bar clock."""
        self._refTime = refTime
        return

    def setProjectStatus(self, state: Literal[0, 1, 2]) -> None:
        """Set the project status colour icon."""
        self.projIcon.setState(state)
        return

    def setDocumentStatus(self, state: Literal[0, 1, 2]) -> None:
        """Set the document status colour icon."""
        self.docIcon.setState(state)
        return

    def setUserIdle(self, idle: bool) -> None:
        """Change the idle status icon."""
        if not CONFIG.stopWhenIdle:
            idle = False
        if self._userIdle != idle:
            if idle:
                self.timeIcon.setPixmap(self.idlePixmap)
            else:
                self.timeIcon.setPixmap(self.timePixmap)
            self._userIdle = idle
        return

    def setProjectStats(self, pWC: int, sWC: int) -> None:
        """Update the current project statistics."""
        self.statsText.setText(self.tr("Words: {0} ({1})").format(f"{pWC:n}", f"{sWC:+n}"))
        if CONFIG.incNotesWCount:
            self.statsText.setToolTip(self.tr("Project word count (session change)"))
        else:
            self.statsText.setToolTip(self.tr("Novel word count (session change)"))
        return

    def updateTime(self, idleTime: float = 0.0) -> None:
        """Update the session clock."""
        if self._refTime < 0.0:
            self.timeText.setText("00:00:00")
        else:
            if CONFIG.stopWhenIdle:
                sessTime = round(time() - self._refTime - idleTime)
            else:
                sessTime = round(time() - self._refTime)
            self.timeText.setText(formatTime(sessTime))
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def setStatusMessage(self, message: str) -> None:
        """Set the status bar message to display."""
        self.showMessage(message, nwConst.STATUS_MSG_TIMEOUT)
        qApp.processEvents()
        return

    @pyqtSlot(str, str)
    def setLanguage(self, language: str, provider: str) -> None:
        """Set the language code for the spell checker."""
        if language == "None":
            self.langText.setText(self.tr("None"))
            self.langText.setToolTip("")
        else:
            self.langText.setText(QLocale(language).nativeLanguageName().title())
            self.langText.setToolTip(f"{language} ({provider})" if provider else language)
        return

    @pyqtSlot(bool)
    def updateProjectStatus(self, status: bool) -> None:
        """Update the project status."""
        self.setProjectStatus(StatusLED.S_BAD if status else StatusLED.S_GOOD)
        return

    @pyqtSlot(bool)
    def updateDocumentStatus(self, status: bool) -> None:
        """Update the document status."""
        self.setDocumentStatus(StatusLED.S_BAD if status else StatusLED.S_GOOD)
        return

# END Class GuiMainStatus
