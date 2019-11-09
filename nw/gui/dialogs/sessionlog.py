# -*- coding: utf-8 -*-
"""novelWriter GUI Session Log Viewer

 novelWriter – GUI Session Log Viewer
======================================
 Class holding the session log view window

 File History:
 Created: 2019-10-20 [0.3]

"""

import logging
import nw

from os import path
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QDialogButtonBox,
    QGridLayout, QLabel, QGroupBox, QCheckBox
)

from nw.constants import nwConst, nwFiles, nwAlert
from nw.tools import OptLastState

logger = logging.getLogger(__name__)

class GuiSessionLogView(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising SessionLogView ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.optState   = SessionLogLastState(self.theProject,nwFiles.SLOG_OPT)
        self.optState.loadSettings()

        self.timeFilter = 0.0
        self.timeTotal  = 0.0

        self.outerBox  = QGridLayout()
        self.bottomBox = QHBoxLayout()

        self.setWindowTitle("Session Log")
        self.setMinimumWidth(420)
        self.setMinimumHeight(400)

        widthCol0 = self.optState.validIntRange(
            self.optState.getSetting("widthCol0"), 30, 999, 180
        )
        widthCol1 = self.optState.validIntRange(
            self.optState.getSetting("widthCol1"), 30, 999, 80
        )
        widthCol2 = self.optState.validIntRange(
            self.optState.getSetting("widthCol2"), 30, 999, 80
        )

        self.listBox = QTreeWidget()
        self.listBox.setHeaderLabels(["Session Start","Length","Words",""])
        self.listBox.setIndentation(0)
        self.listBox.setColumnWidth(0,widthCol0)
        self.listBox.setColumnWidth(1,widthCol1)
        self.listBox.setColumnWidth(2,widthCol2)
        self.listBox.setColumnWidth(3,0)

        hHeader = self.listBox.headerItem()
        hHeader.setTextAlignment(1,Qt.AlignRight)
        hHeader.setTextAlignment(2,Qt.AlignRight)

        self.monoFont = QFont("Monospace",10)

        sortValid = (Qt.AscendingOrder, Qt.DescendingOrder)
        sortCol = self.optState.validIntRange(
            self.optState.getSetting("sortCol"), 0, 2, 0
        )
        sortOrder = self.optState.validIntTuple(
            self.optState.getSetting("sortOrder"), sortValid, Qt.DescendingOrder
        )

        self.listBox.sortByColumn(sortCol, sortOrder)
        self.listBox.setSortingEnabled(True)

        # Session Info
        self.infoBox     = QGroupBox("Sum Total Time", self)
        self.infoBoxForm = QGridLayout(self)
        self.infoBox.setLayout(self.infoBoxForm)

        self.labelTotal = QLabel(self._formatTime(0))
        self.labelTotal.setFont(self.monoFont)
        self.labelTotal.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.labelFilter = QLabel(self._formatTime(0))
        self.labelFilter.setFont(self.monoFont)
        self.labelFilter.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.infoBoxForm.addWidget(QLabel("All:"),      0, 0)
        self.infoBoxForm.addWidget(self.labelTotal,     0, 1)
        self.infoBoxForm.addWidget(QLabel("Filtered:"), 1, 0)
        self.infoBoxForm.addWidget(self.labelFilter,    1, 1)

        # Filter Options
        self.filterBox     = QGroupBox("Filters", self)
        self.filterBoxForm = QGridLayout(self)
        self.filterBox.setLayout(self.filterBoxForm)

        self.hideZeros = QCheckBox("Hide zero word count", self)
        self.hideZeros.setChecked(self.optState.getSetting("hideZeros"))
        self.hideZeros.stateChanged.connect(self._doHideZeros)

        self.hideNegative = QCheckBox("Hide negative word count", self)
        self.hideNegative.setChecked(self.optState.getSetting("hideNegative"))
        self.hideNegative.stateChanged.connect(self._doHideNegative)

        self.filterBoxForm.addWidget(self.hideZeros,    0, 0)
        self.filterBoxForm.addWidget(self.hideNegative, 1, 0)

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)

        # Assemble
        self.outerBox.addWidget(self.listBox,   0, 0, 1, 2)
        self.outerBox.addWidget(self.infoBox,   1, 0)
        self.outerBox.addWidget(self.filterBox, 1, 1)
        self.outerBox.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.setLayout(self.outerBox)

        self.show()

        logger.debug("SessionLogView initialisation complete")

        self._loadSessionLog()

        return

    def _loadSessionLog(self):

        logFile = path.join(self.theProject.projMeta, nwFiles.SESS_INFO)
        if not path.isfile(logFile):
            logger.warning("No session log file found for this project.")
            return False

        self.listBox.clear()

        self.timeFilter = 0.0
        self.timeTotal  = 0.0

        hideZeros    = self.hideZeros.isChecked()
        hideNegative = self.hideNegative.isChecked()

        logger.debug("Loading session log file")
        try:
            with open(logFile,mode="r",encoding="utf8") as inFile:
                for inLine in inFile:
                    inData = inLine.split()
                    if len(inData) != 8:
                        continue
                    dStart = datetime.strptime("%s %s" % (inData[1],inData[2]),nwConst.tStampFmt)
                    dEnd   = datetime.strptime("%s %s" % (inData[4],inData[5]),nwConst.tStampFmt)
                    nWords = int(inData[7])
                    tDiff  = dEnd - dStart
                    sDiff  = tDiff.total_seconds()

                    self.timeTotal  += sDiff
                    if abs(nWords) > 0:
                        self.timeFilter += sDiff

                    if hideZeros and nWords == 0:
                        continue

                    if hideNegative and nWords < 0:
                        continue

                    newItem = QTreeWidgetItem([str(dStart),self._formatTime(sDiff),str(nWords),""])

                    newItem.setTextAlignment(1,Qt.AlignRight)
                    newItem.setTextAlignment(2,Qt.AlignRight)

                    newItem.setFont(0,self.monoFont)
                    newItem.setFont(1,self.monoFont)
                    newItem.setFont(2,self.monoFont)

                    self.listBox.addTopLevelItem(newItem)

        except Exception as e:
            self.theParent.makeAlert(["Failed to read session log file.",str(e)], nwAlert.ERROR)
            return False

        self.labelFilter.setText(self._formatTime(self.timeFilter))
        self.labelTotal.setText(self._formatTime(self.timeTotal))

        return True

    def _doClose(self):

        widthCol0    = self.listBox.columnWidth(0)
        widthCol1    = self.listBox.columnWidth(1)
        widthCol2    = self.listBox.columnWidth(2)
        sortCol      = self.listBox.sortColumn()
        sortOrder    = self.listBox.header().sortIndicatorOrder()
        hideZeros    = self.hideZeros.isChecked()
        hideNegative = self.hideNegative.isChecked()

        self.optState.setSetting("widthCol0",   widthCol0)
        self.optState.setSetting("widthCol1",   widthCol1)
        self.optState.setSetting("widthCol2",   widthCol2)
        self.optState.setSetting("sortCol",     sortCol)
        self.optState.setSetting("sortOrder",   sortOrder)
        self.optState.setSetting("hideZeros",   hideZeros)
        self.optState.setSetting("hideNegative",hideNegative)

        self.optState.saveSettings()
        self.close()

        return

    def _doHideZeros(self, newState):
        self._loadSessionLog()
        return

    def _doHideNegative(self, newState):
        self._loadSessionLog()
        return

    def _formatTime(self, tS):
        tM = int(tS/60)
        tH = int(tM/60)
        tM = tM - tH*60
        tS = tS - tM*60 - tH*3600
        return "%02d:%02d:%02d" % (tH,tM,tS)

# END Class GuiSessionLogView

class SessionLogLastState(OptLastState):

    def __init__(self, theProject, theFile):
        OptLastState.__init__(self, theProject, theFile)
        self.theState  = {
            "widthCol0"    : 180,
            "widthCol1"    : 80,
            "widthCol2"    : 80,
            "sortCol"      : 0,
            "sortOrder"    : Qt.DescendingOrder,
            "hideZeros"    : True,
            "hideNegative" : False,
        }
        self.stringOpt = ()
        self.boolOpt   = ("hideZeros","hideNegative")
        self.intOpt    = ("widthCol0","widthCol1","widthCol2","sortCol","sortOrder")
        return

# END Class SessionLogLastState
