"""
novelWriter – GUI Writing Statistics
====================================
GUI class for the session statistics dialog

File History:
Created: 2019-10-20 [0.3]

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
import os
import json
import logging

from datetime import datetime

from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    qApp, QDialog, QTreeWidget, QTreeWidgetItem, QDialogButtonBox, QGridLayout,
    QLabel, QGroupBox, QMenu, QAction, QFileDialog, QSpinBox, QHBoxLayout
)

from nw.enum import nwAlert
from nw.common import formatTime, checkInt
from nw.constants import nwConst, nwFiles
from nw.gui.custom import QSwitch

logger = logging.getLogger(__name__)


class GuiWritingStats(QDialog):

    C_TIME   = 0
    C_LENGTH = 1
    C_IDLE   = 2
    C_COUNT  = 3
    C_BAR    = 4

    FMT_JSON = 0
    FMT_CSV  = 1

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiWritingStats ...")
        self.setObjectName("GuiWritingStats")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theParent.theProject
        self.optState   = theParent.theProject.optState

        self.logData    = []
        self.filterData = []
        self.timeFilter = 0.0
        self.wordOffset = 0

        self.setWindowTitle(self.tr("Writing Statistics"))
        self.setMinimumWidth(self.mainConf.pxInt(420))
        self.setMinimumHeight(self.mainConf.pxInt(400))
        self.resize(
            self.mainConf.pxInt(self.optState.getInt("GuiWritingStats", "winWidth",  550)),
            self.mainConf.pxInt(self.optState.getInt("GuiWritingStats", "winHeight", 500))
        )

        # List Box
        wCol0 = self.mainConf.pxInt(
            self.optState.getInt("GuiWritingStats", "widthCol0", 180)
        )
        wCol1 = self.mainConf.pxInt(
            self.optState.getInt("GuiWritingStats", "widthCol1", 80)
        )
        wCol2 = self.mainConf.pxInt(
            self.optState.getInt("GuiWritingStats", "widthCol2", 80)
        )
        wCol3 = self.mainConf.pxInt(
            self.optState.getInt("GuiWritingStats", "widthCol3", 80)
        )

        self.listBox = QTreeWidget()
        self.listBox.setHeaderLabels([
            self.tr("Session Start"),
            self.tr("Length"),
            self.tr("Idle"),
            self.tr("Words"),
            self.tr("Histogram"),
        ])
        self.listBox.setIndentation(0)
        self.listBox.setColumnWidth(self.C_TIME, wCol0)
        self.listBox.setColumnWidth(self.C_LENGTH, wCol1)
        self.listBox.setColumnWidth(self.C_IDLE, wCol2)
        self.listBox.setColumnWidth(self.C_COUNT, wCol3)

        hHeader = self.listBox.headerItem()
        hHeader.setTextAlignment(self.C_LENGTH, Qt.AlignRight)
        hHeader.setTextAlignment(self.C_IDLE, Qt.AlignRight)
        hHeader.setTextAlignment(self.C_COUNT, Qt.AlignRight)

        sortValid = (Qt.AscendingOrder, Qt.DescendingOrder)
        sortCol = self.optState.validIntRange(
            self.optState.getInt("GuiWritingStats", "sortCol", 0), 0, 2, 0
        )
        sortOrder = self.optState.validIntTuple(
            self.optState.getInt("GuiWritingStats", "sortOrder", Qt.DescendingOrder),
            sortValid, Qt.DescendingOrder
        )
        self.listBox.sortByColumn(sortCol, sortOrder)
        self.listBox.setSortingEnabled(True)

        # Word Bar
        self.barHeight = int(round(0.5*self.theTheme.fontPixelSize))
        self.barWidth = self.mainConf.pxInt(200)
        self.barImage = QPixmap(self.barHeight, self.barHeight)
        self.barImage.fill(self.palette().highlight().color())

        # Session Info
        self.infoBox = QGroupBox(self.tr("Sum Totals"), self)
        self.infoForm = QGridLayout(self)
        self.infoBox.setLayout(self.infoForm)

        self.labelTotal = QLabel(formatTime(0))
        self.labelTotal.setFont(self.theTheme.guiFontFixed)
        self.labelTotal.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.labelIdleT = QLabel(formatTime(0))
        self.labelIdleT.setFont(self.theTheme.guiFontFixed)
        self.labelIdleT.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.labelFilter = QLabel(formatTime(0))
        self.labelFilter.setFont(self.theTheme.guiFontFixed)
        self.labelFilter.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.novelWords = QLabel("0")
        self.novelWords.setFont(self.theTheme.guiFontFixed)
        self.novelWords.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.notesWords = QLabel("0")
        self.notesWords.setFont(self.theTheme.guiFontFixed)
        self.notesWords.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.totalWords = QLabel("0")
        self.totalWords.setFont(self.theTheme.guiFontFixed)
        self.totalWords.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        lblTTime   = QLabel(self.tr("Total Time:"))
        lblITime   = QLabel(self.tr("Idle Time:"))
        lblFTime   = QLabel(self.tr("Filtered Time:"))
        lblNvCount = QLabel(self.tr("Novel Word Count:"))
        lblNtCount = QLabel(self.tr("Notes Word Count:"))
        lblTtCount = QLabel(self.tr("Total Word Count:"))

        self.infoForm.addWidget(lblTTime,   0, 0)
        self.infoForm.addWidget(lblITime,   1, 0)
        self.infoForm.addWidget(lblFTime,   2, 0)
        self.infoForm.addWidget(lblNvCount, 3, 0)
        self.infoForm.addWidget(lblNtCount, 4, 0)
        self.infoForm.addWidget(lblTtCount, 5, 0)

        self.infoForm.addWidget(self.labelTotal,  0, 1)
        self.infoForm.addWidget(self.labelIdleT,  1, 1)
        self.infoForm.addWidget(self.labelFilter, 2, 1)
        self.infoForm.addWidget(self.novelWords,  3, 1)
        self.infoForm.addWidget(self.notesWords,  4, 1)
        self.infoForm.addWidget(self.totalWords,  5, 1)

        self.infoForm.setRowStretch(6, 1)

        # Filter Options
        sPx = self.theTheme.baseIconSize

        self.filterBox = QGroupBox(self.tr("Filters"), self)
        self.filterForm = QGridLayout(self)
        self.filterBox.setLayout(self.filterForm)

        self.incNovel = QSwitch(width=2*sPx, height=sPx)
        self.incNovel.setChecked(
            self.optState.getBool("GuiWritingStats", "incNovel", True)
        )
        self.incNovel.clicked.connect(self._updateListBox)

        self.incNotes = QSwitch(width=2*sPx, height=sPx)
        self.incNotes.setChecked(
            self.optState.getBool("GuiWritingStats", "incNotes", True)
        )
        self.incNotes.clicked.connect(self._updateListBox)

        self.hideZeros = QSwitch(width=2*sPx, height=sPx)
        self.hideZeros.setChecked(
            self.optState.getBool("GuiWritingStats", "hideZeros", True)
        )
        self.hideZeros.clicked.connect(self._updateListBox)

        self.hideNegative = QSwitch(width=2*sPx, height=sPx)
        self.hideNegative.setChecked(
            self.optState.getBool("GuiWritingStats", "hideNegative", False)
        )
        self.hideNegative.clicked.connect(self._updateListBox)

        self.groupByDay = QSwitch(width=2*sPx, height=sPx)
        self.groupByDay.setChecked(
            self.optState.getBool("GuiWritingStats", "groupByDay", False)
        )
        self.groupByDay.clicked.connect(self._updateListBox)

        self.showIdleTime = QSwitch(width=2*sPx, height=sPx)
        self.showIdleTime.setChecked(
            self.optState.getBool("GuiWritingStats", "showIdleTime", False)
        )
        self.showIdleTime.clicked.connect(self._updateListBox)

        self.filterForm.addWidget(QLabel(self.tr("Count novel files")),        0, 0)
        self.filterForm.addWidget(QLabel(self.tr("Count note files")),         1, 0)
        self.filterForm.addWidget(QLabel(self.tr("Hide zero word count")),     2, 0)
        self.filterForm.addWidget(QLabel(self.tr("Hide negative word count")), 3, 0)
        self.filterForm.addWidget(QLabel(self.tr("Group entries by day")),     4, 0)
        self.filterForm.addWidget(QLabel(self.tr("Show idle time")),           5, 0)
        self.filterForm.addWidget(self.incNovel,     0, 1)
        self.filterForm.addWidget(self.incNotes,     1, 1)
        self.filterForm.addWidget(self.hideZeros,    2, 1)
        self.filterForm.addWidget(self.hideNegative, 3, 1)
        self.filterForm.addWidget(self.groupByDay,   4, 1)
        self.filterForm.addWidget(self.showIdleTime, 5, 1)
        self.filterForm.setRowStretch(6, 1)

        # Settings
        self.histMax = QSpinBox(self)
        self.histMax.setMinimum(100)
        self.histMax.setMaximum(100000)
        self.histMax.setSingleStep(100)
        self.histMax.setValue(
            self.optState.getInt("GuiWritingStats", "histMax", 2000)
        )
        self.histMax.valueChanged.connect(self._updateListBox)

        self.optsBox = QHBoxLayout()
        self.optsBox.addStretch(1)
        self.optsBox.addWidget(QLabel(self.tr("Word count cap for the histogram")), 0)
        self.optsBox.addWidget(self.histMax, 0)

        # Buttons
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.rejected.connect(self._doClose)

        self.btnClose = self.buttonBox.addButton(QDialogButtonBox.Close)
        self.btnClose.setAutoDefault(False)

        self.btnSave = self.buttonBox.addButton(self.tr("Save As"), QDialogButtonBox.ActionRole)
        self.btnSave.setAutoDefault(False)

        self.saveMenu = QMenu(self)
        self.btnSave.setMenu(self.saveMenu)

        self.saveJSON = QAction(self.tr("JSON Data File (.json)"), self)
        self.saveJSON.triggered.connect(lambda: self._saveData(self.FMT_JSON))
        self.saveMenu.addAction(self.saveJSON)

        self.saveCSV = QAction(self.tr("CSV Data File (.csv)"), self)
        self.saveCSV.triggered.connect(lambda: self._saveData(self.FMT_CSV))
        self.saveMenu.addAction(self.saveCSV)

        # Assemble
        self.outerBox = QGridLayout()
        self.outerBox.addWidget(self.listBox,   0, 0, 1, 2)
        self.outerBox.addLayout(self.optsBox,   1, 0, 1, 2)
        self.outerBox.addWidget(self.infoBox,   2, 0)
        self.outerBox.addWidget(self.filterBox, 2, 1)
        self.outerBox.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.outerBox.setRowStretch(0, 1)

        self.setLayout(self.outerBox)

        logger.debug("GuiWritingStats initialisation complete")

        return

    def populateGUI(self):
        """Populate list box with data from the log file.
        """
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        self._loadLogFile()
        self._updateListBox()
        qApp.restoreOverrideCursor()
        return

    ##
    #  Slots
    ##

    def _doClose(self):
        """Save the state of the window, clear cache, end close.
        """
        self.logData = []

        winWidth     = self.mainConf.rpxInt(self.width())
        winHeight    = self.mainConf.rpxInt(self.height())
        widthCol0    = self.mainConf.rpxInt(self.listBox.columnWidth(0))
        widthCol1    = self.mainConf.rpxInt(self.listBox.columnWidth(1))
        widthCol2    = self.mainConf.rpxInt(self.listBox.columnWidth(2))
        widthCol3    = self.mainConf.rpxInt(self.listBox.columnWidth(3))
        sortCol      = self.listBox.sortColumn()
        sortOrder    = self.listBox.header().sortIndicatorOrder()
        incNovel     = self.incNovel.isChecked()
        incNotes     = self.incNotes.isChecked()
        hideZeros    = self.hideZeros.isChecked()
        hideNegative = self.hideNegative.isChecked()
        groupByDay   = self.groupByDay.isChecked()
        showIdleTime = self.showIdleTime.isChecked()
        histMax      = self.histMax.value()

        self.optState.setValue("GuiWritingStats", "winWidth",     winWidth)
        self.optState.setValue("GuiWritingStats", "winHeight",    winHeight)
        self.optState.setValue("GuiWritingStats", "widthCol0",    widthCol0)
        self.optState.setValue("GuiWritingStats", "widthCol1",    widthCol1)
        self.optState.setValue("GuiWritingStats", "widthCol2",    widthCol2)
        self.optState.setValue("GuiWritingStats", "widthCol3",    widthCol3)
        self.optState.setValue("GuiWritingStats", "sortCol",      sortCol)
        self.optState.setValue("GuiWritingStats", "sortOrder",    sortOrder)
        self.optState.setValue("GuiWritingStats", "incNovel",     incNovel)
        self.optState.setValue("GuiWritingStats", "incNotes",     incNotes)
        self.optState.setValue("GuiWritingStats", "hideZeros",    hideZeros)
        self.optState.setValue("GuiWritingStats", "hideNegative", hideNegative)
        self.optState.setValue("GuiWritingStats", "groupByDay",   groupByDay)
        self.optState.setValue("GuiWritingStats", "showIdleTime", showIdleTime)
        self.optState.setValue("GuiWritingStats", "histMax",      histMax)

        self.optState.saveSettings()
        self.close()

        return

    def _saveData(self, dataFmt):
        """Save the content of the list box to a file.
        """
        fileExt = ""
        textFmt = ""

        if dataFmt == self.FMT_JSON:
            fileExt = "json"
            textFmt = self.tr("JSON Data File")
        elif dataFmt == self.FMT_CSV:
            fileExt = "csv"
            textFmt = self.tr("CSV Data File")
        else:
            return False

        # Generate the file name
        saveDir = self.mainConf.lastPath
        if not os.path.isdir(saveDir):
            saveDir = os.path.expanduser("~")

        fileName = "sessionStats.%s" % fileExt
        savePath = os.path.join(saveDir, fileName)

        savePath, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save Data As"), savePath, "%s (*.%s)" % (textFmt, fileExt)
        )
        if not savePath:
            return False

        self.mainConf.setLastPath(savePath)

        # Do the actual writing
        wSuccess = False
        errMsg = ""

        try:
            with open(savePath, mode="w", encoding="utf-8") as outFile:
                if dataFmt == self.FMT_JSON:
                    jsonData = []
                    for _, sD, tT, wD, wA, wB, tI in self.filterData:
                        jsonData.append({
                            "date": sD,
                            "length": tT,
                            "newWords": wD,
                            "novelWords": wA,
                            "noteWords": wB,
                            "idleTime": tI,
                        })
                    json.dump(jsonData, outFile, indent=2)
                    wSuccess = True

                if dataFmt == self.FMT_CSV:
                    outFile.write(
                        '"Date","Length (sec)","Words Changed",'
                        '"Novel Words","Note Words","Idle Time (sec)"\n'
                    )
                    for _, sD, tT, wD, wA, wB, tI in self.filterData:
                        outFile.write(f'"{sD}",{tT:.0f},{wD},{wA},{wB},{tI}\n')
                    wSuccess = True

        except Exception as e:
            errMsg = str(e)
            wSuccess = False

        # Report to user
        if wSuccess:
            self.theParent.makeAlert([
                self.tr("{0} file successfully written to:").format(textFmt), savePath
            ], nwAlert.INFO)
        else:
            self.theParent.makeAlert([
                self.tr("Failed to write {0} file.").format(textFmt), errMsg
            ], nwAlert.ERROR)

        return wSuccess

    ##
    #  Internal Functions
    ##

    def _loadLogFile(self):
        """Load the content of the log file into a buffer.
        """
        logger.debug("Loading session log file")

        self.logData = []
        self.wordOffset = 0

        ttNovel = 0
        ttNotes = 0
        ttTime = 0
        ttIdle = 0

        logFile = os.path.join(self.theProject.projMeta, nwFiles.SESS_STATS)
        if not os.path.isfile(logFile):
            logger.info("This project has no writing stats logfile")
            return False

        try:
            with open(logFile, mode="r", encoding="utf-8") as inFile:
                for inLine in inFile:
                    if inLine.startswith("#"):
                        if inLine.startswith("# Offset"):
                            self.wordOffset = checkInt(inLine[9:].strip(), 0)
                            logger.verbose(
                                "Initial word count when log was started is %d" % self.wordOffset
                            )
                        continue

                    inData = inLine.split()
                    if len(inData) < 6:
                        continue

                    dStart = datetime.strptime(
                        "%s %s" % (inData[0], inData[1]), nwConst.FMT_TSTAMP
                    )
                    dEnd = datetime.strptime(
                        "%s %s" % (inData[2], inData[3]), nwConst.FMT_TSTAMP
                    )

                    sIdle = 0
                    if len(inData) > 6:
                        sIdle = checkInt(inData[6], 0)

                    tDiff = dEnd - dStart
                    sDiff = tDiff.total_seconds()
                    ttTime += sDiff
                    ttIdle += sIdle

                    wcNovel = int(inData[4])
                    wcNotes = int(inData[5])
                    ttNovel = wcNovel
                    ttNotes = wcNotes

                    self.logData.append((dStart, sDiff, wcNovel, wcNotes, sIdle))

        except Exception as e:
            self.theParent.makeAlert([
                self.tr("Failed to read session log file."), str(e)
            ], nwAlert.ERROR)
            return False

        ttWords = ttNovel + ttNotes
        self.labelTotal.setText(formatTime(round(ttTime)))
        self.labelIdleT.setText(formatTime(round(ttIdle)))
        self.novelWords.setText(f"{ttNovel:n}")
        self.notesWords.setText(f"{ttNotes:n}")
        self.totalWords.setText(f"{ttWords:n}")

        return True

    ##
    #  Slots
    ##

    def _updateListBox(self):
        """Load/reload the content of the list box. The dummyVar
        variable captures the variable sent from the widgets connecting
        to it and discards it.
        """
        self.listBox.clear()
        self.timeFilter = 0.0

        incNovel     = self.incNovel.isChecked()
        incNotes     = self.incNotes.isChecked()
        hideZeros    = self.hideZeros.isChecked()
        hideNegative = self.hideNegative.isChecked()
        groupByDay   = self.groupByDay.isChecked()
        histMax      = self.histMax.value()

        # Group the data
        if groupByDay:
            tempData = []
            sessDate = None
            sessTime = 0
            sessIdle = 0
            lstNovel = 0
            lstNotes = 0

            for n, (dStart, sDiff, wcNovel, wcNotes, sIdle) in enumerate(self.logData):
                if n == 0:
                    sessDate = dStart.date()
                if sessDate != dStart.date():
                    tempData.append((sessDate, sessTime, lstNovel, lstNotes, sessIdle))
                    sessDate = dStart.date()
                    sessTime = sDiff
                    sessIdle = sIdle
                    lstNovel = wcNovel
                    lstNotes = wcNotes
                else:
                    sessTime += sDiff
                    sessIdle += sIdle
                    lstNovel = wcNovel
                    lstNotes = wcNotes

            if sessDate is not None:
                tempData.append((sessDate, sessTime, lstNovel, lstNotes, sessIdle))

        else:
            tempData = self.logData

        # Calculate Word Diff
        self.filterData = []
        pcTotal = 0
        listMax = 0
        isFirst = True
        for dStart, sDiff, wcNovel, wcNotes, sIdle in tempData:

            wcTotal = 0
            if incNovel:
                wcTotal += wcNovel
            if incNotes:
                wcTotal += wcNotes

            dwTotal = wcTotal - pcTotal
            if hideZeros and dwTotal == 0:
                continue
            if hideNegative and dwTotal < 0:
                pcTotal = wcTotal
                continue

            if isFirst:
                # Subtract the offset from the first list entry
                dwTotal -= self.wordOffset
                dwTotal = max(dwTotal, 1)  # Don't go zero or negative
                isFirst = False

            if groupByDay:
                sStart = dStart.strftime(nwConst.FMT_DSTAMP)
            else:
                sStart = dStart.strftime(nwConst.FMT_TSTAMP)

            self.filterData.append((dStart, sStart, sDiff, dwTotal, wcNovel, wcNotes, sIdle))
            listMax = min(max(listMax, dwTotal), histMax)
            pcTotal = wcTotal

        # Populate the list
        showIdleTime = self.showIdleTime.isChecked()
        for _, sStart, sDiff, nWords, _, _, sIdle in self.filterData:

            if showIdleTime:
                idleEntry = formatTime(sIdle)
            else:
                sRatio = sIdle/sDiff if sDiff > 0.0 else 0.0
                idleEntry = "%d %%" % round(100.0 * sRatio)

            newItem = QTreeWidgetItem()
            newItem.setText(self.C_TIME, sStart)
            newItem.setText(self.C_LENGTH, formatTime(round(sDiff)))
            newItem.setText(self.C_IDLE, idleEntry)
            newItem.setText(self.C_COUNT, f"{nWords:n}")

            if nWords > 0 and listMax > 0:
                theBar = self.barImage.scaled(
                    int(200*min(nWords, histMax)/listMax),
                    self.barHeight,
                    Qt.IgnoreAspectRatio,
                    Qt.FastTransformation
                )
                newItem.setData(self.C_BAR, Qt.DecorationRole, theBar)

            newItem.setTextAlignment(self.C_LENGTH, Qt.AlignRight)
            newItem.setTextAlignment(self.C_IDLE, Qt.AlignRight)
            newItem.setTextAlignment(self.C_COUNT, Qt.AlignRight)
            newItem.setTextAlignment(self.C_BAR, Qt.AlignLeft | Qt.AlignVCenter)

            newItem.setFont(self.C_TIME, self.theTheme.guiFontFixed)
            newItem.setFont(self.C_LENGTH, self.theTheme.guiFontFixed)
            newItem.setFont(self.C_COUNT, self.theTheme.guiFontFixed)
            if showIdleTime:
                newItem.setFont(self.C_IDLE, self.theTheme.guiFontFixed)
            else:
                newItem.setFont(self.C_IDLE, self.theTheme.guiFont)

            self.listBox.addTopLevelItem(newItem)
            self.timeFilter += sDiff

        self.labelFilter.setText(formatTime(round(self.timeFilter)))

        return True

# END Class GuiWritingStats
