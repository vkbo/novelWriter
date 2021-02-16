# -*- coding: utf-8 -*-
"""
novelWriter – GUI Main Window Status Bar
========================================
GUI class for the main window status bar

File History:
Created: 2019-04-20 [0.0.1]

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

from time import time

from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import qApp, QStatusBar, QLabel, QAbstractButton

from nw.common import formatTime

logger = logging.getLogger(__name__)

class GuiMainStatus(QStatusBar):

    def __init__(self, theParent):
        QStatusBar.__init__(self, theParent)

        logger.debug("Initialising GuiMainStatus ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme
        self.refTime   = None
        self.userIdle  = False

        colNone  = QColor(*self.theTheme.statNone)
        colTrue  = QColor(*self.theTheme.statUnsaved)
        colFalse = QColor(*self.theTheme.statSaved)

        iPx = self.theTheme.baseIconSize

        # Permanent Widgets
        # =================

        xM = self.mainConf.pxInt(8)

        ## The Spell Checker Language
        self.langIcon = QLabel("")
        self.langText = QLabel(self.tr("None"))
        self.langIcon.setPixmap(self.theTheme.getPixmap("status_lang", (iPx, iPx)))
        self.langIcon.setContentsMargins(0, 0, 0, 0)
        self.langText.setContentsMargins(0, 0, xM, 0)
        self.addPermanentWidget(self.langIcon)
        self.addPermanentWidget(self.langText)

        ## The Editor Status
        self.docIcon = StatusLED(colNone, colTrue, colFalse, iPx, iPx, self)
        self.docText = QLabel(self.tr("Editor"))
        self.docIcon.setContentsMargins(0, 0, 0, 0)
        self.docText.setContentsMargins(0, 0, xM, 0)
        self.addPermanentWidget(self.docIcon)
        self.addPermanentWidget(self.docText)

        ## The Project Status
        self.projIcon = StatusLED(colNone, colTrue, colFalse, iPx, iPx, self)
        self.projText = QLabel(self.tr("Project"))
        self.projIcon.setContentsMargins(0, 0, 0, 0)
        self.projText.setContentsMargins(0, 0, xM, 0)
        self.addPermanentWidget(self.projIcon)
        self.addPermanentWidget(self.projText)

        ## The Project and Session Stats
        self.statsIcon = QLabel()
        self.statsText = QLabel("")
        self.statsIcon.setPixmap(self.theTheme.getPixmap("status_stats", (iPx, iPx)))
        self.statsIcon.setContentsMargins(0, 0, 0, 0)
        self.statsText.setContentsMargins(0, 0, xM, 0)
        self.addPermanentWidget(self.statsIcon)
        self.addPermanentWidget(self.statsText)

        ## The Session Clock
        ### Set the mimimum width so the label doesn't rescale every second
        self.timePixmap = self.theTheme.getPixmap("status_time", (iPx, iPx))
        self.idlePixmap = self.theTheme.getPixmap("status_idle", (iPx, iPx))

        self.timeIcon = QLabel()
        self.timeText = QLabel("")
        self.timeIcon.setPixmap(self.timePixmap)
        self.timeText.setToolTip(self.tr("Session Time"))
        self.timeText.setMinimumWidth(self.theTheme.getTextWidth("00:00:00:"))
        self.timeIcon.setContentsMargins(0, 0, 0, 0)
        self.timeText.setContentsMargins(0, 0, 0, 0)
        self.addPermanentWidget(self.timeIcon)
        self.addPermanentWidget(self.timeText)

        # Other Settings
        self.setSizeGripEnabled(True)

        logger.debug("GuiMainStatus initialisation complete")

        self.clearStatus()

        return

    def clearStatus(self):
        """Reset all widgets on the status bar to default values.
        """
        self.setRefTime(None)
        self.setLanguage(None)
        self.setStats(0, 0)
        self.setProjectStatus(None)
        self.setDocumentStatus(None)
        self.updateTime()
        return True

    ##
    #  Setters
    ##

    def setRefTime(self, theTime):
        """Set the reference time for the status bar clock.
        """
        self.refTime = theTime
        return

    def setStatus(self, theMessage, timeOut=20.0):
        """Set the status bar message to display for 'timeOut' seconds.
        """
        self.showMessage(theMessage, int(timeOut*1000))
        qApp.processEvents()
        return

    def setLanguage(self, theLanguage, theProvider=""):
        """Set the language code for the spell checker.
        """
        if theLanguage is None:
            self.langText.setText(self.tr("None"))
            self.langText.setToolTip("")
        else:
            qLocal = QLocale(theLanguage)
            spLang = qLocal.nativeLanguageName().title()
            self.langText.setText(spLang)
            if theProvider:
                self.langText.setToolTip("%s (%s)" % (theLanguage, theProvider))
            else:
                self.langText.setToolTip(theLanguage)

        return

    def setProjectStatus(self, isChanged):
        """Set the project status colour icon.
        """
        self.projIcon.setState(isChanged)
        return

    def setDocumentStatus(self, isChanged):
        """Set the document status colour icon.
        """
        self.docIcon.setState(isChanged)
        return

    def setStats(self, pWC, sWC):
        """Set the current project statistics.
        """
        self.statsText.setText(self.tr("Words: {0} ({1})").format(f"{pWC:n}", f"{sWC:+n}"))
        self.statsText.setToolTip(self.tr("Project word count (session change)"))
        return

    def setUserIdle(self, userIdle):
        """Change the idle status icon.
        """
        if not self.mainConf.stopWhenIdle:
            userIdle = False

        if self.userIdle != userIdle:
            if userIdle:
                self.timeIcon.setPixmap(self.idlePixmap)
            else:
                self.timeIcon.setPixmap(self.timePixmap)

            self.userIdle = userIdle

        return

    def updateTime(self, idleTime=0.0):
        """Update the session clock.
        """
        if self.refTime is None:
            self.timeText.setText("00:00:00")
        else:
            if self.mainConf.stopWhenIdle:
                sessTime = round(time() - self.refTime - idleTime)
            else:
                sessTime = round(time() - self.refTime)
            self.timeText.setText(formatTime(sessTime))
        return

# END Class GuiMainStatus

class StatusLED(QAbstractButton):

    def __init__(self, colNone, colTrue, colFalse, sW, sH, parent=None):
        super().__init__(parent=parent)

        self.colNone  = colNone
        self.colTrue  = colTrue
        self.colFalse = colFalse
        self._theCol  = colNone

        self.setFixedWidth(sW)
        self.setFixedHeight(sH)

        return

    ##
    #  Setters
    ##

    def setState(self, theState):
        """Set the colour state.
        """
        self._theCol = self.colNone
        if theState is True:
            self._theCol = self.colTrue
        elif theState is False:
            self._theCol = self.colFalse

        self.update()

        return

    ##
    #  Events
    ##

    def paintEvent(self, event):
        """Drawing the LED.
        """
        qPalette = self.palette()
        qPaint = QPainter(self)
        qPaint.setRenderHint(QPainter.Antialiasing, True)
        qPaint.setPen(qPalette.dark().color())
        qPaint.setBrush(self._theCol)
        qPaint.setOpacity(1.0)
        qPaint.drawEllipse(1, 1, self.width() - 2, self.height() - 2)
        return

# END Class StatusLED
