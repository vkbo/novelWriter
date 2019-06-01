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

from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QIcon, QColor, QBrush, QPixmap
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QDialogButtonBox, QLabel, QPushButton
)

logger = logging.getLogger(__name__)

class GuiTimeLineView(QDialog):

    def __init__(self, theParent, theProject, theIndex):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising TimeLineView ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.theIndex   = theIndex
        self.theMatrix  = {}
        self.numRows    = 0
        self.numCols    = 0

        self.outerBox   = QVBoxLayout()
        self.bottomBox  = QHBoxLayout()

        self.setWindowTitle("Timeline View")
        self.setMinimumSize(*self.mainConf.dlgTimeLine)

        self.mainTable = QTableWidget()
        self.mainTable.setGridStyle(Qt.NoPen)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)

        self.btnRebuild = QPushButton("Rebuild Index")
        self.btnRebuild.clicked.connect(self.theParent.rebuildIndex)

        self.btnRefresh = QPushButton("Refresh Table")
        self.btnRefresh.clicked.connect(self._buildNovelList)

        self.setLayout(self.outerBox)
        self.outerBox.addWidget(self.mainTable)
        self.outerBox.addLayout(self.bottomBox)
        self.bottomBox.addWidget(self.btnRebuild)
        self.bottomBox.addWidget(self.btnRefresh)
        self.bottomBox.addStretch()
        self.bottomBox.addWidget(self.buttonBox)

        self._buildNovelList()
        self.buttonBox.setFocus()

        self.show()

        logger.debug("TimeLineView initialisation complete")

        return

    def _buildNovelList(self):

        self.theIndex.buildNovelList()
        self.numRows = len(self.theIndex.novelList)
        self.numCols = len(self.theIndex.tagIndex.keys())

        self.mainTable.clear()
        self.mainTable.setRowCount(self.numRows)
        self.mainTable.setColumnCount(self.numCols)

        for n in range(len(self.theIndex.novelList)):
            iDepth = self.theIndex.novelList[n][1]
            iTitle = self.theIndex.novelList[n][2]
            newItem = QTableWidgetItem("  "*iDepth + iTitle)
            self.mainTable.setVerticalHeaderItem(n, newItem)
            self.mainTable.setRowHeight(n, 16)

        theMap = self.theIndex.buildTagNovelMap(self.theIndex.tagIndex.keys())
        nCol   = 0
        for theTag, theCols in theMap.items():
            newItem = QTableWidgetItem(theTag)
            self.mainTable.setHorizontalHeaderItem(nCol, newItem)
            self.mainTable.setColumnWidth(nCol,50)
            for n in range(len(theCols)):
                if theCols[n] == 1:
                    pxNew  = QPixmap(10,10)
                    pxNew.fill(QColor(0,120,0))
                    lblNew = QLabel()
                    lblNew.setPixmap(pxNew)
                    lblNew.setAlignment(Qt.AlignCenter)
                    self.mainTable.setCellWidget(n, nCol, lblNew)
                elif theCols[n] == 2:
                    pxNew  = QPixmap(10,10)
                    pxNew.fill(QColor(120,0,0))
                    lblNew = QLabel()
                    lblNew.setPixmap(pxNew)
                    lblNew.setAlignment(Qt.AlignCenter)
                    self.mainTable.setCellWidget(n, nCol, lblNew)
            nCol += 1

        return

    def _doClose(self):
        self.mainConf.setTLineSize(self.width(), self.height())
        self.close()
        return

# END Class GuiItemEditor
