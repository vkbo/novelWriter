# -*- coding: utf-8 -*-
"""novelWriter GUI Project Details

 novelWriter – GUI Project Details
===================================
 Class holding the project details dialog

 File History:
 Created: 2021-01-03 [1.0a0]

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
import math

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QWidget, QDialogButtonBox, QVBoxLayout, QTreeWidget, QTreeWidgetItem
)

from nw.gui.custom import PagedDialog

logger = logging.getLogger(__name__)

class GuiProjectDetails(PagedDialog):

    def __init__(self, theParent, theProject):
        PagedDialog.__init__(self, theParent)

        logger.debug("Initialising GuiProjectDetails ...")
        self.setObjectName("GuiProjectDetails")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.optState   = theProject.optState

        self.setWindowTitle("Project Details")

        wW = self.mainConf.pxInt(570)
        wH = self.mainConf.pxInt(375)

        self.setMinimumWidth(wW)
        self.setMinimumHeight(wH)
        self.resize(
            self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "winWidth",  wW)),
            self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "winHeight", wH))
        )

        self.tabMain     = GuiProjectDetailsMain(self.theParent, self.theProject)
        self.tabChapters = GuiProjectDetailsChapters(self.theParent, self.theProject)

        self.addTab(self.tabMain,     "Overview")
        self.addTab(self.tabChapters, "Chapters")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)
        self.addControls(self.buttonBox)

        logger.debug("GuiProjectDetails initialisation complete")

        return

    ##
    #  Slots
    ##

    def _doClose(self):
        """Save settings and close the dialog.
        """
        self._saveGuiSettings()
        self.close()
        return

    ##
    #  Internal Functions
    ##

    def _saveGuiSettings(self):
        """Save GUI settings.
        """
        winWidth  = self.mainConf.rpxInt(self.width())
        winHeight = self.mainConf.rpxInt(self.height())

        chColWidth = self.tabChapters.getColumnSizes()
        widthCol0 = self.mainConf.rpxInt(chColWidth[0])
        widthCol1 = self.mainConf.rpxInt(chColWidth[1])
        widthCol2 = self.mainConf.rpxInt(chColWidth[2])
        widthCol3 = self.mainConf.rpxInt(chColWidth[3])
        widthCol4 = self.mainConf.rpxInt(chColWidth[4])

        self.optState.setValue("GuiProjectDetails", "winWidth",  winWidth)
        self.optState.setValue("GuiProjectDetails", "winHeight", winHeight)
        self.optState.setValue("GuiProjectDetails", "widthCol0", widthCol0)
        self.optState.setValue("GuiProjectDetails", "widthCol1", widthCol1)
        self.optState.setValue("GuiProjectDetails", "widthCol2", widthCol2)
        self.optState.setValue("GuiProjectDetails", "widthCol3", widthCol3)
        self.optState.setValue("GuiProjectDetails", "widthCol4", widthCol4)

        return

# END Class GuiProjectDetails

class GuiProjectDetailsMain(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        return

# END Class GuiProjectDetailsMain

class GuiProjectDetailsChapters(QWidget):

    C_TITLE = 0
    C_WORDS = 1
    C_PAGES = 2
    C_PAGE  = 3
    C_PROG  = 4

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme
        self.theIndex   = theParent.theIndex
        self.optState   = theProject.optState

        iPx = self.theTheme.baseIconSize

        self.chTree = QTreeWidget()
        self.chTree.setIconSize(QSize(iPx, iPx))
        self.chTree.setIndentation(0)
        self.chTree.setColumnCount(6)
        self.chTree.setHeaderLabels(["Title", "Words", "Pages", "Page", "Progress", ""])

        treeHeadItem = self.chTree.headerItem()
        treeHeadItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)
        treeHeadItem.setTextAlignment(self.C_PAGES, Qt.AlignRight)
        treeHeadItem.setTextAlignment(self.C_PAGE,  Qt.AlignRight)
        treeHeadItem.setTextAlignment(self.C_PROG,  Qt.AlignRight)

        treeHeader = self.chTree.header()
        treeHeader.setStretchLastSection(True)
        treeHeader.setMinimumSectionSize(iPx + 6)

        # Get user's column width preferences
        wCol0 = self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "widthCol0", 200))
        wCol1 = self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "widthCol1", 60))
        wCol2 = self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "widthCol2", 60))
        wCol3 = self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "widthCol3", 60))
        wCol4 = self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "widthCol4", 90))
        self.chTree.setColumnWidth(0, wCol0)
        self.chTree.setColumnWidth(1, wCol1)
        self.chTree.setColumnWidth(2, wCol2)
        self.chTree.setColumnWidth(3, wCol3)
        self.chTree.setColumnWidth(4, wCol4)
        self.chTree.setColumnWidth(5, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.chTree)

        self.setLayout(self.outerBox)

        self._populateTree()

        return

    def getColumnSizes(self):
        """Return the column widths for the tree columns.
        """
        retVals = [
            self.chTree.columnWidth(0),
            self.chTree.columnWidth(1),
            self.chTree.columnWidth(2),
            self.chTree.columnWidth(3),
            self.chTree.columnWidth(4),
        ]
        return retVals

    ##
    #  Internal Functions
    ##

    def _populateTree(self):
        """Set the content of the chapter/page tree.
        """
        self.chTree.clear()

        dblPages = True
        wpPage = 100
        tPages = 1

        theToC = self.theIndex.getTableOfContents(2)
        theToC.append(("", "H0", "END", 0))

        theList = []
        pTotal = 0
        for tKey, tLevel, tTitle, wCount in theToC:
            pCount = math.ceil(wCount/wpPage)
            if dblPages:
                pCount += pCount%2
            pTotal += pCount
            theList.append((tLevel, tTitle, wCount, pCount))

        for tLevel, tTitle, wCount, pCount in theList:
            newItem = QTreeWidgetItem()

            newItem.setIcon(self.C_TITLE, self.theTheme.getIcon("doc_%s" % tLevel.lower()))
            newItem.setText(self.C_TITLE, tTitle)
            newItem.setText(self.C_WORDS, f"{wCount:n}")
            newItem.setText(self.C_PAGES, f"{pCount:n}")
            newItem.setText(self.C_PAGE,  f"{tPages:n}")
            newItem.setText(self.C_PROG,  f"{100*(tPages-1)/pTotal:.2f}%")

            newItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)
            newItem.setTextAlignment(self.C_PAGES, Qt.AlignRight)
            newItem.setTextAlignment(self.C_PAGE,  Qt.AlignRight)
            newItem.setTextAlignment(self.C_PROG,  Qt.AlignRight)

            tPages += pCount

            self.chTree.addTopLevelItem(newItem)

        return

# END Class GuiProjectDetailsChapters
