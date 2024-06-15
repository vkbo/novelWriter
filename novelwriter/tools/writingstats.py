"""
novelWriter – GUI Writing Statistics
====================================

File History:
Created: 2019-10-20 [0.3.0] GuiWritingStats

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

from datetime import datetime
from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QCloseEvent, QCursor, QPixmap
from PyQt5.QtWidgets import (
    QAction, QApplication, QDialogButtonBox, QFileDialog, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QMenu, QSpinBox, QTreeWidget,
    QTreeWidgetItem
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import checkInt, checkIntTuple, formatTime, minmax
from novelwriter.constants import nwConst
from novelwriter.error import formatException
from novelwriter.extensions.modified import NToolDialog
from novelwriter.extensions.switch import NSwitch
from novelwriter.types import (
    QtAlignLeftMiddle, QtAlignRight, QtAlignRightMiddle, QtDecoration,
    QtDialogClose, QtRoleAction
)

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiWritingStats(NToolDialog):
    """GUI Tools: Writing Statistics

    Displays data from the NWSessionLog object.
    """

    C_TIME   = 0
    C_LENGTH = 1
    C_IDLE   = 2
    C_COUNT  = 3
    C_BAR    = 4

    FMT_JSON = 0
    FMT_CSV  = 1

    def __init__(self, parent: GuiMain) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiWritingStats")
        self.setObjectName("GuiWritingStats")

        self.logData    = []
        self.filterData = []
        self.timeFilter = 0.0
        self.wordOffset = 0

        pOptions = SHARED.project.options

        self.setWindowTitle(self.tr("Writing Statistics"))
        self.setMinimumWidth(CONFIG.pxInt(420))
        self.setMinimumHeight(CONFIG.pxInt(400))
        self.resize(
            CONFIG.pxInt(pOptions.getInt("GuiWritingStats", "winWidth",  550)),
            CONFIG.pxInt(pOptions.getInt("GuiWritingStats", "winHeight", 500))
        )

        # List Box
        wCol0 = CONFIG.pxInt(
            pOptions.getInt("GuiWritingStats", "widthCol0", 180)
        )
        wCol1 = CONFIG.pxInt(
            pOptions.getInt("GuiWritingStats", "widthCol1", 80)
        )
        wCol2 = CONFIG.pxInt(
            pOptions.getInt("GuiWritingStats", "widthCol2", 80)
        )
        wCol3 = CONFIG.pxInt(
            pOptions.getInt("GuiWritingStats", "widthCol3", 80)
        )

        self.listBox = QTreeWidget(self)
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
        if hHeader is not None:
            hHeader.setTextAlignment(self.C_LENGTH, QtAlignRight)
            hHeader.setTextAlignment(self.C_IDLE, QtAlignRight)
            hHeader.setTextAlignment(self.C_COUNT, QtAlignRight)

        sDec = Qt.SortOrder.DescendingOrder
        sAsc = Qt.SortOrder.AscendingOrder
        sortCol = minmax(pOptions.getInt("GuiWritingStats", "sortCol", 0), 0, 2)
        sortOrder = checkIntTuple(
            pOptions.getInt("GuiWritingStats", "sortOrder", sDec), (sAsc, sDec), sDec
        )
        self.listBox.sortByColumn(sortCol, sortOrder)  # type: ignore
        self.listBox.setSortingEnabled(True)

        # Word Bar
        self.barHeight = int(round(0.5*SHARED.theme.fontPixelSize))
        self.barWidth = CONFIG.pxInt(200)
        self.barImage = QPixmap(self.barHeight, self.barHeight)
        self.barImage.fill(self.palette().highlight().color())

        # Session Info
        self.infoBox = QGroupBox(self.tr("Sum Totals"), self)
        self.infoForm = QGridLayout(self)
        self.infoBox.setLayout(self.infoForm)

        self.labelTotal = QLabel(formatTime(0), self)
        self.labelTotal.setFont(SHARED.theme.guiFontFixed)
        self.labelTotal.setAlignment(QtAlignRightMiddle)

        self.labelIdleT = QLabel(formatTime(0), self)
        self.labelIdleT.setFont(SHARED.theme.guiFontFixed)
        self.labelIdleT.setAlignment(QtAlignRightMiddle)

        self.labelFilter = QLabel(formatTime(0), self)
        self.labelFilter.setFont(SHARED.theme.guiFontFixed)
        self.labelFilter.setAlignment(QtAlignRightMiddle)

        self.novelWords = QLabel("0", self)
        self.novelWords.setFont(SHARED.theme.guiFontFixed)
        self.novelWords.setAlignment(QtAlignRightMiddle)

        self.notesWords = QLabel("0", self)
        self.notesWords.setFont(SHARED.theme.guiFontFixed)
        self.notesWords.setAlignment(QtAlignRightMiddle)

        self.totalWords = QLabel("0", self)
        self.totalWords.setFont(SHARED.theme.guiFontFixed)
        self.totalWords.setAlignment(QtAlignRightMiddle)

        lblTTime   = QLabel(self.tr("Total Time:"), self)
        lblITime   = QLabel(self.tr("Idle Time:"), self)
        lblFTime   = QLabel(self.tr("Filtered Time:"), self)
        lblNvCount = QLabel(self.tr("Novel Word Count:"), self)
        lblNtCount = QLabel(self.tr("Notes Word Count:"), self)
        lblTtCount = QLabel(self.tr("Total Word Count:"), self)

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
        iPx = SHARED.theme.baseIconHeight

        self.filterBox = QGroupBox(self.tr("Filters"), self)
        self.filterForm = QGridLayout(self)
        self.filterBox.setLayout(self.filterForm)

        self.incNovel = NSwitch(self, height=iPx)
        self.incNovel.setChecked(
            pOptions.getBool("GuiWritingStats", "incNovel", True)
        )
        self.incNovel.clicked.connect(self._updateListBox)

        self.incNotes = NSwitch(self, height=iPx)
        self.incNotes.setChecked(
            pOptions.getBool("GuiWritingStats", "incNotes", True)
        )
        self.incNotes.clicked.connect(self._updateListBox)

        self.hideZeros = NSwitch(self, height=iPx)
        self.hideZeros.setChecked(
            pOptions.getBool("GuiWritingStats", "hideZeros", True)
        )
        self.hideZeros.clicked.connect(self._updateListBox)

        self.hideNegative = NSwitch(self, height=iPx)
        self.hideNegative.setChecked(
            pOptions.getBool("GuiWritingStats", "hideNegative", False)
        )
        self.hideNegative.clicked.connect(self._updateListBox)

        self.groupByDay = NSwitch(self, height=iPx)
        self.groupByDay.setChecked(
            pOptions.getBool("GuiWritingStats", "groupByDay", False)
        )
        self.groupByDay.clicked.connect(self._updateListBox)

        self.showIdleTime = NSwitch(self, height=iPx)
        self.showIdleTime.setChecked(
            pOptions.getBool("GuiWritingStats", "showIdleTime", False)
        )
        self.showIdleTime.clicked.connect(self._updateListBox)

        self.filterForm.addWidget(QLabel(self.tr("Count novel files"), self),        0, 0)
        self.filterForm.addWidget(QLabel(self.tr("Count note files"), self),         1, 0)
        self.filterForm.addWidget(QLabel(self.tr("Hide zero word count"), self),     2, 0)
        self.filterForm.addWidget(QLabel(self.tr("Hide negative word count"), self), 3, 0)
        self.filterForm.addWidget(QLabel(self.tr("Group entries by day"), self),     4, 0)
        self.filterForm.addWidget(QLabel(self.tr("Show idle time"), self),           5, 0)
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
            pOptions.getInt("GuiWritingStats", "histMax", 2000)
        )
        self.histMax.valueChanged.connect(self._updateListBox)

        self.optsBox = QHBoxLayout()
        self.optsBox.addStretch(1)
        self.optsBox.addWidget(QLabel(self.tr("Word count cap for the histogram"), self), 0)
        self.optsBox.addWidget(self.histMax, 0)

        # Buttons
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.rejected.connect(self._doClose)

        self.btnClose = self.buttonBox.addButton(QtDialogClose)
        self.btnClose.setAutoDefault(False)

        self.btnSave = self.buttonBox.addButton(self.tr("Save As"), QtRoleAction)
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

        logger.debug("Ready: GuiWritingStats")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiWritingStats")
        return

    def populateGUI(self) -> None:
        """Populate list box with data from the log file."""
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        self._loadLogFile()
        self._updateListBox()
        QApplication.restoreOverrideCursor()
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window."""
        event.accept()
        self.softDelete()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _doClose(self) -> None:
        """Save the state of the window, clear cache, end close."""
        self.logData = []

        winWidth     = CONFIG.rpxInt(self.width())
        winHeight    = CONFIG.rpxInt(self.height())
        widthCol0    = CONFIG.rpxInt(self.listBox.columnWidth(0))
        widthCol1    = CONFIG.rpxInt(self.listBox.columnWidth(1))
        widthCol2    = CONFIG.rpxInt(self.listBox.columnWidth(2))
        widthCol3    = CONFIG.rpxInt(self.listBox.columnWidth(3))
        sortCol      = self.listBox.sortColumn()
        sortOrder    = self.listBox.header().sortIndicatorOrder()
        incNovel     = self.incNovel.isChecked()
        incNotes     = self.incNotes.isChecked()
        hideZeros    = self.hideZeros.isChecked()
        hideNegative = self.hideNegative.isChecked()
        groupByDay   = self.groupByDay.isChecked()
        showIdleTime = self.showIdleTime.isChecked()
        histMax      = self.histMax.value()

        logger.debug("Saving State: GuiWritingStats")
        pOptions = SHARED.project.options
        pOptions.setValue("GuiWritingStats", "winWidth",     winWidth)
        pOptions.setValue("GuiWritingStats", "winHeight",    winHeight)
        pOptions.setValue("GuiWritingStats", "widthCol0",    widthCol0)
        pOptions.setValue("GuiWritingStats", "widthCol1",    widthCol1)
        pOptions.setValue("GuiWritingStats", "widthCol2",    widthCol2)
        pOptions.setValue("GuiWritingStats", "widthCol3",    widthCol3)
        pOptions.setValue("GuiWritingStats", "sortCol",      sortCol)
        pOptions.setValue("GuiWritingStats", "sortOrder",    sortOrder)
        pOptions.setValue("GuiWritingStats", "incNovel",     incNovel)
        pOptions.setValue("GuiWritingStats", "incNotes",     incNotes)
        pOptions.setValue("GuiWritingStats", "hideZeros",    hideZeros)
        pOptions.setValue("GuiWritingStats", "hideNegative", hideNegative)
        pOptions.setValue("GuiWritingStats", "groupByDay",   groupByDay)
        pOptions.setValue("GuiWritingStats", "showIdleTime", showIdleTime)
        pOptions.setValue("GuiWritingStats", "histMax",      histMax)
        pOptions.saveSettings()

        self.close()

        return

    def _saveData(self, dataFmt: int) -> bool:
        """Save the content of the list box to a file."""
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
        savePath = CONFIG.lastPath("stats") / f"sessionStats.{fileExt}"
        savePath, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save Data As"), str(savePath), f"{textFmt} (*.{fileExt})"
        )
        if not savePath:
            return False

        CONFIG.setLastPath("stats", savePath)

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

        except Exception as exc:
            errMsg = formatException(exc)
            wSuccess = False

        # Report to user
        if wSuccess:
            SHARED.info(
                self.tr("{0} file successfully written to:").format(textFmt),
                info=savePath
            )
        else:
            SHARED.error(
                self.tr("Failed to write {0} file.").format(textFmt),
                info=errMsg
            )

        return wSuccess

    ##
    #  Internal Functions
    ##

    def _loadLogFile(self) -> None:
        """Load the content of the log file into a buffer."""
        logger.debug("Loading session log file")

        self.logData = []
        self.wordOffset = 0

        ttNovel = 0
        ttNotes = 0
        ttTime = 0
        ttIdle = 0

        for record in SHARED.project.session.iterRecords():
            rType = record.get("type")
            if rType == "initial":
                self.wordOffset = checkInt(record.get("offset"), 0)
                logger.debug("Initial word count when log was started is %d" % self.wordOffset)
            elif rType == "record":
                try:
                    dStart = datetime.fromisoformat(str(record.get("start")))
                    dEnd   = datetime.fromisoformat(str(record.get("end")))
                except Exception:
                    logger.error("Invalid session log record")
                    continue
                wcNovel = max(checkInt(record.get("novel"), 0), 0)
                wcNotes = max(checkInt(record.get("notes"), 0), 0)
                sIdle = max(checkInt(record.get("idle"), 0), 0)

                tDiff = dEnd - dStart
                sDiff = tDiff.total_seconds()
                ttTime += sDiff
                ttIdle += sIdle
                ttNovel = wcNovel
                ttNotes = wcNotes

                self.logData.append((dStart, sDiff, wcNovel, wcNotes, sIdle))

        ttWords = ttNovel + ttNotes
        self.labelTotal.setText(formatTime(round(ttTime)))
        self.labelIdleT.setText(formatTime(round(ttIdle)))
        self.novelWords.setText(f"{ttNovel:n}")
        self.notesWords.setText(f"{ttNotes:n}")
        self.totalWords.setText(f"{ttWords:n}")

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _updateListBox(self) -> None:
        """Load/reload the content of the list box."""
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
        mTrans = Qt.TransformationMode.FastTransformation
        mAspect = Qt.AspectRatioMode.IgnoreAspectRatio
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
                wBar = self.barImage.scaled(
                    int(200*min(nWords, histMax)/listMax),
                    self.barHeight, mAspect, mTrans
                )
                newItem.setData(self.C_BAR, QtDecoration, wBar)

            newItem.setTextAlignment(self.C_LENGTH, QtAlignRight)
            newItem.setTextAlignment(self.C_IDLE, QtAlignRight)
            newItem.setTextAlignment(self.C_COUNT, QtAlignRight)
            newItem.setTextAlignment(self.C_BAR, QtAlignLeftMiddle)

            newItem.setFont(self.C_TIME, SHARED.theme.guiFontFixed)
            newItem.setFont(self.C_LENGTH, SHARED.theme.guiFontFixed)
            newItem.setFont(self.C_COUNT, SHARED.theme.guiFontFixed)
            newItem.setFont(self.C_IDLE, SHARED.theme.guiFontFixed)

            self.listBox.addTopLevelItem(newItem)
            self.timeFilter += sDiff

        self.labelFilter.setText(formatTime(round(self.timeFilter)))

        return
