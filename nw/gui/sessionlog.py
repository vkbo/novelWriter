# -*- coding: utf-8 -*-
"""novelWriter GUI Session Log Viewer

 novelWriter – GUI Session Log Viewer
======================================
 Class holding the session log view window

 File History:
 Created: 2019-10-20 [0.3]

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

from os import path
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    qApp, QDialog, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QDialogButtonBox,
    QGridLayout, QLabel, QGroupBox, QCheckBox
)

from nw.constants import nwConst, nwFiles, nwAlert

logger = logging.getLogger(__name__)

class GuiSessionLogView(QDialog):

    C_TIME   = 0
    C_LENGTH = 1
    C_COUNT  = 2

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising SessionLogView ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme
        self.optState   = theProject.optState

        self.logData    = []
        self.timeFilter = 0.0
        self.timeTotal  = 0.0

        self.setWindowTitle("Session Log")
        self.setMinimumWidth(self.mainConf.pxInt(420))
        self.setMinimumHeight(self.mainConf.pxInt(400))

        # List Box
        wCol0 = self.mainConf.pxInt(self.optState.getInt("GuiSession", "widthCol0", 180))
        wCol1 = self.mainConf.pxInt(self.optState.getInt("GuiSession", "widthCol1", 80))

        self.listBox = QTreeWidget()
        self.listBox.setHeaderLabels(["Session Start","Length","Words"])
        self.listBox.setIndentation(0)
        self.listBox.setColumnWidth(self.C_TIME, wCol0)
        self.listBox.setColumnWidth(self.C_LENGTH, wCol1)
        self.listBox.resizeColumnToContents(self.C_COUNT)

        hHeader = self.listBox.headerItem()
        hHeader.setTextAlignment(self.C_LENGTH, Qt.AlignRight)
        hHeader.setTextAlignment(self.C_COUNT, Qt.AlignRight)

        self.monoFont = QFont()
        self.monoFont.setPointSizeF(0.9*self.theTheme.fontPointSize)
        self.monoFont.setFamily(self.theTheme.guiFontFixed.family())

        sortValid = (Qt.AscendingOrder, Qt.DescendingOrder)
        sortCol = self.optState.validIntRange(
            self.optState.getInt("GuiSession", "sortCol", 0), 0, 2, 0
        )
        sortOrder = self.optState.validIntTuple(
            self.optState.getInt("GuiSession", "sortOrder", Qt.DescendingOrder),
            sortValid, Qt.DescendingOrder
        )

        self.listBox.sortByColumn(sortCol, sortOrder)
        self.listBox.setSortingEnabled(True)

        # Session Info
        self.infoBox  = QGroupBox("Sum Total Time", self)
        self.infoForm = QGridLayout(self)
        self.infoBox.setLayout(self.infoForm)

        self.labelTotal = QLabel(self._formatTime(0))
        self.labelTotal.setFont(self.monoFont)
        self.labelTotal.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.labelFilter = QLabel(self._formatTime(0))
        self.labelFilter.setFont(self.monoFont)
        self.labelFilter.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.infoForm.addWidget(QLabel("All:"),      0, 0)
        self.infoForm.addWidget(self.labelTotal,     0, 1)
        self.infoForm.addWidget(QLabel("Filtered:"), 1, 0)
        self.infoForm.addWidget(self.labelFilter,    1, 1)

        # Filter Options
        self.filterBox  = QGroupBox("Filters", self)
        self.filterForm = QGridLayout(self)
        self.filterBox.setLayout(self.filterForm)

        self.hideZeros = QCheckBox("Hide zero word count", self)
        self.hideZeros.setChecked(
            self.optState.getBool("GuiSession", "hideZeros", True)
        )
        self.hideZeros.stateChanged.connect(self._doHideZeros)

        self.hideNegative = QCheckBox("Hide negative word count", self)
        self.hideNegative.setChecked(
            self.optState.getBool("GuiSession", "hideNegative", False)
        )
        self.hideNegative.stateChanged.connect(self._doHideNegative)

        self.filterForm.addWidget(self.hideZeros,    0, 0)
        self.filterForm.addWidget(self.hideNegative, 1, 0)

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)

        # Assemble
        self.outerBox = QGridLayout()
        self.outerBox.addWidget(self.listBox,   0, 0, 1, 2)
        self.outerBox.addWidget(self.infoBox,   1, 0)
        self.outerBox.addWidget(self.filterBox, 1, 1)
        self.outerBox.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.setLayout(self.outerBox)

        logger.debug("SessionLogView initialisation complete")

        qApp.processEvents()
        self._loadLogFile()
        self._updateListBox()

        return

    ##
    #  Slots
    ##

    def _doClose(self):
        """Save the state of the window, clear cache, end close.
        """
        self.logData = []

        widthCol0    = self.mainConf.rpxInt(self.listBox.columnWidth(0))
        widthCol1    = self.mainConf.rpxInt(self.listBox.columnWidth(1))
        sortCol      = self.listBox.sortColumn()
        sortOrder    = self.listBox.header().sortIndicatorOrder()
        hideZeros    = self.hideZeros.isChecked()
        hideNegative = self.hideNegative.isChecked()

        self.optState.setValue("GuiSession", "widthCol0", widthCol0)
        self.optState.setValue("GuiSession", "widthCol1", widthCol1)
        self.optState.setValue("GuiSession", "sortCol", sortCol)
        self.optState.setValue("GuiSession", "sortOrder", sortOrder)
        self.optState.setValue("GuiSession", "hideZeros", hideZeros)
        self.optState.setValue("GuiSession", "hideNegative", hideNegative)

        self.optState.saveSettings()
        self.close()

        return

    def _doHideZeros(self, newState):
        """Reload the list box with the new filter settings in place.
        """
        self._updateListBox()
        return

    def _doHideNegative(self, newState):
        """Reload the list box with the new filter settings in place.
        """
        self._updateListBox()
        return

    ##
    #  Internal Functions
    ##

    def _loadLogFile(self):
        """Load the content of the log file into a buffer.
        """
        self.logData = []
        logger.debug("Loading session log file")

        try:
            logFile = path.join(self.theProject.projMeta, nwFiles.SESS_INFO)
            with open(logFile, mode="r", encoding="utf8") as inFile:
                for inLine in inFile:

                    inData = inLine.split()
                    if len(inData) != 8:
                        continue

                    dStart = datetime.strptime(
                        "%s %s" % (inData[1], inData[2]), nwConst.tStampFmt
                    )
                    dEnd = datetime.strptime(
                        "%s %s" % (inData[4], inData[5]), nwConst.tStampFmt
                    )

                    nWords = int(inData[7])
                    tDiff = dEnd - dStart
                    sDiff = tDiff.total_seconds()

                    self.logData.append((dStart, sDiff, nWords))

        except Exception as e:
            self.theParent.makeAlert(
                ["Failed to read session log file.",str(e)], nwAlert.ERROR
            )
            return False

        return True

    def _updateListBox(self):
        """Load/reload the content of the list box.
        """
        self.listBox.clear()
        self.timeFilter = 0.0
        self.timeTotal  = 0.0

        hideZeros    = self.hideZeros.isChecked()
        hideNegative = self.hideNegative.isChecked()

        for dStart, sDiff, nWords in self.logData:

            self.timeTotal += sDiff

            if hideZeros and nWords == 0:
                continue

            if hideNegative and nWords < 0:
                continue

            self.timeFilter += sDiff

            newItem = QTreeWidgetItem()
            newItem.setText(self.C_TIME, str(dStart))
            newItem.setText(self.C_LENGTH, self._formatTime(sDiff))
            newItem.setText(self.C_COUNT, str(nWords))

            newItem.setTextAlignment(self.C_LENGTH, Qt.AlignRight)
            newItem.setTextAlignment(self.C_COUNT, Qt.AlignRight)

            newItem.setFont(self.C_TIME, self.monoFont)
            newItem.setFont(self.C_LENGTH, self.monoFont)
            newItem.setFont(self.C_COUNT, self.monoFont)

            self.listBox.addTopLevelItem(newItem)

        self.labelFilter.setText(self._formatTime(self.timeFilter))
        self.labelTotal.setText(self._formatTime(self.timeTotal))

        return True

    def _formatTime(self, tS):
        """Format the time spent in 00:00:00 format.
        """
        tM = int(tS/60)
        tH = int(tM/60)
        tM = tM - tH*60
        tS = tS - tM*60 - tH*3600
        return "%02d:%02d:%02d" % (tH,tM,tS)

# END Class GuiSessionLogView
