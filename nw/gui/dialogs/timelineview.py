# -*- coding: utf-8 -*-
"""novelWriter GUI Timeline View

 novelWriter – GUI Timeline View
=================================
 Class holding the timeline view window

 File History:
 Created: 2019-05-30 [0.1.4]

"""

import logging
import nw

from os import path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel,
    QDialogButtonBox, QPushButton, QHeaderView, QGridLayout, QGroupBox,
    QCheckBox
)

from nw.constants import nwFiles, nwItemClass
from nw.tools import OptLastState

logger = logging.getLogger(__name__)

class GuiTimeLineView(QDialog):

    def __init__(self, theParent, theProject, theIndex):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising TimeLineView ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.theIndex   = theIndex
        self.optState   = TimeLineLastState(self.theProject,nwFiles.TLINE_OPT)
        self.optState.loadSettings()

        self.theMatrix = {}
        self.numRows   = 0
        self.numCols   = 0

        self.outerBox  = QVBoxLayout()
        self.filterBox = QVBoxLayout()
        self.centreBox = QHBoxLayout()
        self.bottomBox = QHBoxLayout()

        self.setWindowTitle("Timeline View")
        self.setMinimumWidth(700)
        self.setMinimumHeight(400)

        winWidth = self.optState.validIntRange(
            self.optState.getSetting("winWidth"),  700, 10000, 700
        )
        winHeight = self.optState.validIntRange(
            self.optState.getSetting("winHeight"), 400, 10000, 400
        )
        self.resize(winWidth,winHeight)

        # TimeLine Table
        self.mainTable = QTableWidget()
        self.mainTable.setGridStyle(Qt.NoPen)

        self.hHeader = self.mainTable.horizontalHeader()
        self.hHeader.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.mainTable.setHorizontalHeader(self.hHeader)

        self.vHeader = self.mainTable.verticalHeader()
        self.vHeader.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.mainTable.setVerticalHeader(self.vHeader)

        # Option Box
        self.optFilter = QGroupBox("Include Tags", self)
        self.optFilterGrid = QGridLayout(self)
        self.optFilter.setLayout(self.optFilterGrid)

        self.filterPlot = QCheckBox("Plot tags", self)
        self.filterPlot.setChecked(self.optState.getSetting("fPlot"))
        self.filterPlot.stateChanged.connect(self._filterChange)

        self.filterChar = QCheckBox("Character tags", self)
        self.filterChar.setChecked(self.optState.getSetting("fChar"))
        self.filterChar.stateChanged.connect(self._filterChange)

        self.filterWorld = QCheckBox("Location tags", self)
        self.filterWorld.setChecked(self.optState.getSetting("fWorld"))
        self.filterWorld.stateChanged.connect(self._filterChange)

        self.filterTime = QCheckBox("Timeline tags", self)
        self.filterTime.setChecked(self.optState.getSetting("fTime"))
        self.filterTime.stateChanged.connect(self._filterChange)

        self.filterObject = QCheckBox("Object tags", self)
        self.filterObject.setChecked(self.optState.getSetting("fObject"))
        self.filterObject.stateChanged.connect(self._filterChange)

        self.filterCustom = QCheckBox("Custom tags", self)
        self.filterCustom.setChecked(self.optState.getSetting("fCustom"))
        self.filterCustom.stateChanged.connect(self._filterChange)

        self.optFilterGrid.addWidget(self.filterPlot,   0, 1)
        self.optFilterGrid.addWidget(self.filterChar,   1, 1)
        self.optFilterGrid.addWidget(self.filterWorld,  2, 1)
        self.optFilterGrid.addWidget(self.filterTime,   3, 1)
        self.optFilterGrid.addWidget(self.filterObject, 4, 1)
        self.optFilterGrid.addWidget(self.filterCustom, 5, 1)

        self.optHide = QGroupBox("Filters", self)
        self.optHideGrid = QGridLayout(self)
        self.optHide.setLayout(self.optHideGrid)

        self.hideUnused = QCheckBox("Hide unused", self)
        self.hideUnused.setChecked(self.optState.getSetting("hUnused"))
        self.hideUnused.stateChanged.connect(self._filterChange)

        self.optHideGrid.addWidget(self.hideUnused, 0, 1)

        # Button Box
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)

        self.btnRebuild = QPushButton("Rebuild Index")
        self.btnRebuild.clicked.connect(self.theParent.rebuildIndex)

        self.btnRefresh = QPushButton("Refresh Table")
        self.btnRefresh.clicked.connect(self._buildNovelList)

        self.bottomBox.addWidget(self.btnRebuild)
        self.bottomBox.addWidget(self.btnRefresh)
        self.bottomBox.addStretch()
        self.bottomBox.addWidget(self.buttonBox)

        # Assemble
        self.filterBox.addWidget(self.optFilter)
        self.filterBox.addWidget(self.optHide)
        self.filterBox.addStretch()
        self.centreBox.addWidget(self.mainTable)
        self.centreBox.addLayout(self.filterBox)
        self.outerBox.addLayout(self.centreBox)
        self.outerBox.addLayout(self.bottomBox)
        self.setLayout(self.outerBox)

        self._buildNovelList()
        self.buttonBox.setFocus()

        self.show()

        logger.debug("TimeLineView initialisation complete")

        return

    def _buildNovelList(self):

        self.mainTable.clear()
        self.theIndex.buildNovelList()

        self.numRows = len(self.theIndex.novelList)
        self.mainTable.setRowCount(self.numRows)

        theFilters = {}
        theFilters["exClass"] = []
        theFilters["hUnused"] = self.hideUnused.isChecked()

        if not self.filterPlot.isChecked():
            theFilters["exClass"].append(nwItemClass.PLOT)
        if not self.filterChar.isChecked():
            theFilters["exClass"].append(nwItemClass.CHARACTER)
        if not self.filterWorld.isChecked():
            theFilters["exClass"].append(nwItemClass.WORLD)
        if not self.filterTime.isChecked():
            theFilters["exClass"].append(nwItemClass.TIMELINE)
        if not self.filterObject.isChecked():
            theFilters["exClass"].append(nwItemClass.OBJECT)
        if not self.filterCustom.isChecked():
            theFilters["exClass"].append(nwItemClass.CUSTOM)

        for n in range(len(self.theIndex.novelList)):
            iDepth = self.theIndex.novelList[n][1]
            iTitle = self.theIndex.novelList[n][2]
            newItem = QTableWidgetItem("%s%s  " % ("  "*iDepth,iTitle))
            self.mainTable.setVerticalHeaderItem(n, newItem)

        theMap = self.theIndex.buildTagNovelMap(self.theIndex.tagIndex.keys(), theFilters)
        self.numCols = len(theMap.keys())
        self.mainTable.setColumnCount(self.numCols)

        nCol = 0
        for theTag, theCols in theMap.items():
            newItem = QTableWidgetItem(" %s " % theTag)
            self.mainTable.setHorizontalHeaderItem(nCol, newItem)
            for n in range(len(theCols)):
                if theCols[n] == 1:
                    pxNew = QPixmap(10,10)
                    pxNew.fill(QColor(0,120,0))
                    lblNew = QLabel()
                    lblNew.setPixmap(pxNew)
                    lblNew.setAlignment(Qt.AlignCenter)
                    lblNew.setAttribute(Qt.WA_TranslucentBackground)
                    self.mainTable.setCellWidget(n, nCol, lblNew)
                elif theCols[n] == 2:
                    pxNew = QPixmap(10,10)
                    pxNew.fill(QColor(0,0,120))
                    lblNew = QLabel()
                    lblNew.setPixmap(pxNew)
                    lblNew.setAlignment(Qt.AlignCenter)
                    lblNew.setAttribute(Qt.WA_TranslucentBackground)
                    self.mainTable.setCellWidget(n, nCol, lblNew)
            nCol += 1

        return

    def _doClose(self):

        logger.verbose("GuiTimeLineView close button clicked")

        winWidth  = self.width()
        winHeight = self.height()
        fPlot     = self.filterPlot.isChecked()
        fChar     = self.filterChar.isChecked()
        fWorld    = self.filterWorld.isChecked()
        fTime     = self.filterTime.isChecked()
        fObject   = self.filterObject.isChecked()
        fCustom   = self.filterCustom.isChecked()
        hUnused   = self.hideUnused.isChecked()

        self.optState.setSetting("winWidth", winWidth)
        self.optState.setSetting("winHeight",winHeight)
        self.optState.setSetting("fPlot",    fPlot)
        self.optState.setSetting("fChar",    fChar)
        self.optState.setSetting("fWorld",   fWorld)
        self.optState.setSetting("fTime",    fTime)
        self.optState.setSetting("fObject",  fObject)
        self.optState.setSetting("fCustom",  fCustom)
        self.optState.setSetting("hUnused",  hUnused)

        self.optState.saveSettings()
        self.close()

        return

    def _filterChange(self, checkState):
        self._buildNovelList()
        return

# END Class GuiTimeLineView

class TimeLineLastState(OptLastState):

    def __init__(self, theProject, theFile):
        OptLastState.__init__(self, theProject, theFile)
        self.theState  = {
            "winWidth"  : 700,
            "winHeight" : 400,
            "fPlot"     : True,
            "fChar"     : True,
            "fWorld"    : True,
            "fTime"     : True,
            "fObject"   : True,
            "fCustom"   : True,
            "hUnused"   : True,
        }
        self.stringOpt = ()
        self.boolOpt   = ("fPlot","fChar","fWorld","fTime","fObject","fCustom","hUnused")
        self.intOpt    = ("winWidth","winHeight")
        return

# END Class TimeLineLastState
