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
from PyQt5.QtGui import QColor, QPixmap, QFont
from PyQt5.QtWidgets import QStatusBar, QLabel

from nw.core import NWSpellCheck

logger = logging.getLogger(__name__)

class GuiMainStatus(QStatusBar):

    def __init__(self, theParent):
        QStatusBar.__init__(self, theParent)

        logger.debug("Initialising MainStatus ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.refTime   = None

        self.iconGrey   = QPixmap(16,16)
        self.iconYellow = QPixmap(16,16)
        self.iconGreen  = QPixmap(16,16)

        self.monoFont = QFont("Monospace",10)

        self.iconGrey.fill(QColor(*self.theParent.theTheme.statNone))
        self.iconYellow.fill(QColor(*self.theParent.theTheme.statUnsaved))
        self.iconGreen.fill(QColor(*self.theParent.theTheme.statSaved))

        self.boxStats = QLabel()
        self.boxStats.setToolTip("Project Word Count | Session Word Count")

        self.timeBox = QLabel("")
        self.timeBox.setToolTip("Session Time")
        self.timeBox.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.timeBox.setFont(self.monoFont)

        self.timeIcon = QLabel()
        self.timeIcon.setPixmap(self.theParent.theTheme.getPixmap("status_time",(14,14)))

        self.boxCounts = QLabel()
        self.boxCounts.setToolTip("Document Character | Word | Paragraph Count")

        self.projChanged = QLabel("")
        self.projChanged.setFixedHeight(14)
        self.projChanged.setFixedWidth(14)
        self.projChanged.setToolTip("Project Changes Saved")

        self.docChanged = QLabel("")
        self.docChanged.setFixedHeight(14)
        self.docChanged.setFixedWidth(14)
        self.docChanged.setToolTip("Document Changes Saved")

        self.langBox = QLabel("None")
        self.langIcon = QLabel("")
        self.langIcon.setPixmap(self.theParent.theTheme.getPixmap("status_lang",(14,14)))

        # Add Them
        self.addPermanentWidget(self.langIcon)
        self.addPermanentWidget(self.langBox)
        self.addPermanentWidget(QLabel("  "))
        self.addPermanentWidget(self.docChanged)
        self.addPermanentWidget(self.boxCounts)
        self.addPermanentWidget(QLabel("  "))
        self.addPermanentWidget(self.projChanged)
        self.addPermanentWidget(self.boxStats)
        self.addPermanentWidget(QLabel("  "))
        self.addPermanentWidget(self.timeIcon)
        self.addPermanentWidget(self.timeBox)

        self.setSizeGripEnabled(True)

        self.sessionTimer = QTimer()
        self.sessionTimer.setInterval(1000)
        self.sessionTimer.timeout.connect(self._updateTime)
        self.sessionTimer.start()

        logger.debug("MainStatus initialisation complete")

        self.clearStatus()

        return

    def clearStatus(self):
        self.setRefTime(None)
        self.setStats(0,0)
        self.setCounts(0,0,0)
        self.setProjectStatus(None)
        self.setDocumentStatus(None)
        self._updateTime()
        return True

    def setRefTime(self, theTime):
        self.refTime = theTime
        return

    def setStatus(self, theMessage, timeOut=10.0):
        self.showMessage(theMessage, int(timeOut*1000))
        return

    def setLanguage(self, theLanguage):
        if theLanguage is None:
            self.langBox.setText("None")
        else:
            self.langBox.setText(NWSpellCheck.expandLanguage(theLanguage))
        return

    def setProjectStatus(self, isChanged):
        if isChanged is None:
            self.projChanged.setPixmap(self.iconGrey)
        elif isChanged == True:
            self.projChanged.setPixmap(self.iconYellow)
        elif isChanged == False:
            self.projChanged.setPixmap(self.iconGreen)
        else:
            self.projChanged.setPixmap(self.iconGrey)
        return

    def setDocumentStatus(self, isChanged):
        if isChanged is None:
            self.docChanged.setPixmap(self.iconGrey)
        elif isChanged == True:
            self.docChanged.setPixmap(self.iconYellow)
        elif isChanged == False:
            self.docChanged.setPixmap(self.iconGreen)
        else:
            self.docChanged.setPixmap(self.iconGrey)
        return

    def setStats(self, pWC, sWC):
        self.boxStats.setText("<b>Project:</b> {:d} : {:d}".format(pWC,sWC))
        return

    def setCounts(self, cC, wC, pC):
        self.boxCounts.setText("<b>Document:</b> {:d} : {:d} : {:d}".format(cC,wC,pC))
        return

    ##
    #  Internal Functions
    ##

    def _updateTime(self):
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
        self.timeBox.setText(theTime)
        return

# END Class GuiMainStatus
