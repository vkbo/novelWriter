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

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QDialogButtonBox

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

        self.setWindowTitle("Timeline View")

        self.mainTable = QTableWidget(1,1)

        self.setLayout(self.outerBox)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)

        self.outerBox.addWidget(self.mainTable)
        self.outerBox.addWidget(self.buttonBox)

        self._buildMatrix()
        self._buildNovelList()

        self.setMinimumSize(600,400)

        self.show()

        logger.debug("TimeLineView initialisation complete")

        return

    def _buildMatrix(self):

        self.theMatrix = {
            "title"  : [], # Size numRows - 1
            "depth"  : [], # Size numRows - 1
            "handle" : [], # Size numRows - 1
            "line"   : [], # Size numRows - 1
            "tags"   : [], # Size numCols - 1
            "table"  : [], # Size numRows - 1 x numCols - 1
        }

        self.numRows = 1
        self.numCols = 1
        for tHandle in self.theProject.treeOrder:
            if tHandle not in self.theIndex.novelIndex:
                continue
            for nLine, nDepth, tTitle, tLayout in self.theIndex.novelIndex[tHandle]:
                self.theMatrix["title"].append(tTitle)
                self.theMatrix["depth"].append(nDepth)
                self.theMatrix["handle"].append(tHandle)
                self.theMatrix["line"].append(nLine)
                self.numRows += 1

        for tTag in self.theIndex.tagIndex:
            self.theMatrix["tags"].append(tTag)
            self.numCols += 1

        return

    def _buildNovelList(self):

        self.theIndex.buildNovelList()
        self.numRows = len(self.theIndex.novelList) + 1

        self.mainTable.setRowCount(self.numRows)
        self.mainTable.setColumnCount(self.numCols)

        for n in range(self.numRows-1):
            iDepth = self.theIndex.novelList[n][1]
            iTitle = self.theIndex.novelList[n][2]
            newItem = QTableWidgetItem("  "*iDepth + iTitle)
            self.mainTable.setItem(n+1, 0, newItem)

        theMap  = self.theIndex.buildTagNovelMap(self.theMatrix["tags"])
        nCol    = 1
        for theTag, theCols in theMap.items():
            newItem = QTableWidgetItem(theTag)
            self.mainTable.setItem(0, nCol, newItem)
            for n in range(self.numRows-1):
                newItem = QTableWidgetItem(str(theCols[n]))
                self.mainTable.setItem(n+1, nCol, newItem)
            nCol += 1

        return

    def _doClose(self):
        self.close()
        return

# END Class GuiItemEditor
