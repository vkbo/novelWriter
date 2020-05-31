# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window StatusBar

 novelWriter – GUI Main Window StatusBar
=========================================
 Class holding the main window status bar

 File History:
 Created: 2019-04-20 [0.0.1]

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
import nw

from time import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPixmap, QFont, QPainter
from PyQt5.QtWidgets import qApp, QStatusBar, QLabel, QAbstractButton

from nw.core import NWSpellCheck
from nw.common import formatInt

logger = logging.getLogger(__name__)

class GuiMainStatus(QStatusBar):

    def __init__(self, theParent):
        QStatusBar.__init__(self, theParent)

        logger.debug("Initialising MainStatus ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme
        self.refTime   = None

        self.charCount = 0
        self.wordCount = 0
        self.paraCount = 0
        self.projWords = 0
        self.sessWords = 0

        colNone  = QColor(*self.theTheme.statNone)
        colTrue  = QColor(*self.theTheme.statUnsaved)
        colFalse = QColor(*self.theTheme.statSaved)

        iPx = self.theTheme.textIconSize

        # Permanent Widgets
        # =================

        ## The Spell Checker Language
        self.langIcon = QLabel("")
        self.langText = QLabel("None")
        self.langIcon.setPixmap(self.theTheme.getPixmap("status_lang", (iPx, iPx)))
        self.langIcon.setContentsMargins(0, 0, 0, 0)
        self.langText.setContentsMargins(0, 0, 8, 0)
        self.addPermanentWidget(self.langIcon)
        self.addPermanentWidget(self.langText)

        ## The Editor Status
        self.docIcon = StatusLED(colNone, colTrue, colFalse, iPx, iPx, self)
        self.docText = QLabel("Editor")
        self.docIcon.setContentsMargins(0, 0, 0, 0)
        self.docText.setContentsMargins(0, 0, 8, 0)
        self.addPermanentWidget(self.docIcon)
        self.addPermanentWidget(self.docText)

        ## The Project Status
        self.projIcon = StatusLED(colNone, colTrue, colFalse, iPx, iPx, self)
        self.projText = QLabel("Project")
        self.projIcon.setContentsMargins(0, 0, 0, 0)
        self.projText.setContentsMargins(0, 0, 8, 0)
        self.addPermanentWidget(self.projIcon)
        self.addPermanentWidget(self.projText)

        ## The Project and Session Stats
        self.statsIcon = QLabel()
        self.statsText = QLabel("")
        self.statsIcon.setPixmap(self.theTheme.getPixmap("status_stats", (iPx, iPx)))
        self.statsIcon.setContentsMargins(0, 0, 0, 0)
        self.statsText.setContentsMargins(0, 0, 8, 0)
        self.addPermanentWidget(self.statsIcon)
        self.addPermanentWidget(self.statsText)

        ## The Session Clock
        ### Set the mimimum width so the label doesn't rescale every second
        self.timeIcon = QLabel()
        self.timeText = QLabel("")
        self.timeIcon.setPixmap(self.theTheme.getPixmap("status_time", (iPx, iPx)))
        self.timeText.setToolTip("Session Time")
        self.timeText.setMinimumWidth(self.theTheme.getTextWidth("00:00:00:"))
        self.timeIcon.setContentsMargins(0, 0, 0, 0)
        self.timeText.setContentsMargins(0, 0, 0, 0)
        self.addPermanentWidget(self.timeIcon)
        self.addPermanentWidget(self.timeText)

        # Other Settings
        self.setSizeGripEnabled(True)

        # Start the Clock
        self.sessionTimer = QTimer()
        self.sessionTimer.setInterval(1000)
        self.sessionTimer.timeout.connect(self._updateTime)
        self.sessionTimer.start()

        logger.debug("MainStatus initialisation complete")

        self.clearStatus()

        return

    def clearStatus(self):
        """Reset all widgets on the status bar to default values.
        """
        self.setRefTime(None)
        self.setStats(0, 0)
        self.setCounts(0, 0, 0)
        self.setProjectStatus(None)
        self.setDocumentStatus(None)
        self._updateTime()
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

    def setLanguage(self, theLanguage):
        """Set the language code for the spell checker.
        """
        if theLanguage is None:
            self.langText.setText("None")
        else:
            self.langText.setText(NWSpellCheck.expandLanguage(theLanguage))
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
        self.projWords = pWC
        self.sessWords = sWC
        self._updateStats()
        return

    def setCounts(self, cC, wC, pC):
        """Set the current document statistics.
        """
        self.charCount = cC
        self.wordCount = wC
        self.paraCount = pC
        self._updateStats()
        return

    ##
    #  Internal Functions
    ##

    def _updateStats(self):
        """Update statistics.
        """
        self.statsText.setToolTip(
            "D: Document word count<br>P: Project word count (session change)"
        )
        self.statsText.setText((
            "D:{wC:n}  P:{pWC:n} ({sWC:+n})"
        ).format(
            wC  = self.wordCount,
            pWC = self.projWords,
            sWC = self.sessWords,
        ))
        return

    def _updateTime(self):
        """Update the session clock.
        """
        if self.refTime is None:
            theTime = "00:00:00"
        else:
            # This is much faster than using datetime format
            tS = int(time() - self.refTime)
            tM = int(tS/60)
            tH = int(tM/60)
            tM = tM - tH*60
            tS = tS - tM*60 - tH*3600
            theTime = "%02d:%02d:%02d" % (tH,tM,tS)
        self.timeText.setText(theTime)
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
    #  Getters and Setters
    ##

    def setState(self, theState):
        """Set the colour state.
        """
        if theState is None:
            self._theCol = self.colNone
        elif theState == True:
            self._theCol = self.colTrue
        elif theState == False:
            self._theCol = self.colFalse
        else:
            self._theCol = self.colNone
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
        qPaint.drawEllipse(1, 1, self.width()-2, self.height()-2)
        return

# END Class StatusLED
