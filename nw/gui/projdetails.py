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
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QDialogButtonBox, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QSpinBox, QGroupBox, QGridLayout, QHBoxLayout
)

from nw.gui.custom import PagedDialog, QSwitch

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
        self.tabContents = GuiProjectDetailsContents(self.theParent, self.theProject)

        self.addTab(self.tabMain,     "Overview")
        self.addTab(self.tabContents, "Contents")

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

        cColWidth = self.tabContents.getColumnSizes()
        widthCol0 = self.mainConf.rpxInt(cColWidth[0])
        widthCol1 = self.mainConf.rpxInt(cColWidth[1])
        widthCol2 = self.mainConf.rpxInt(cColWidth[2])
        widthCol3 = self.mainConf.rpxInt(cColWidth[3])
        widthCol4 = self.mainConf.rpxInt(cColWidth[4])

        wordsPerPage = self.tabContents.wpValue.value()
        clearDouble  = self.tabContents.dblValue.isChecked()

        self.optState.setValue("GuiProjectDetails", "winWidth",     winWidth)
        self.optState.setValue("GuiProjectDetails", "winHeight",    winHeight)
        self.optState.setValue("GuiProjectDetails", "widthCol0",    widthCol0)
        self.optState.setValue("GuiProjectDetails", "widthCol1",    widthCol1)
        self.optState.setValue("GuiProjectDetails", "widthCol2",    widthCol2)
        self.optState.setValue("GuiProjectDetails", "widthCol3",    widthCol3)
        self.optState.setValue("GuiProjectDetails", "widthCol4",    widthCol4)
        self.optState.setValue("GuiProjectDetails", "wordsPerPage", wordsPerPage)
        self.optState.setValue("GuiProjectDetails", "clearDouble",  clearDouble)

        return

# END Class GuiProjectDetails

class GuiProjectDetailsMain(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme
        self.theIndex   = theParent.theIndex

        fPx = self.theTheme.fontPixelSize
        vPx = self.mainConf.pxInt(4)
        hPx = self.mainConf.pxInt(12)

        # Header
        # ======

        self.bookTitle = QLabel(self.theProject.bookTitle)
        bookFont = self.bookTitle.font()
        bookFont.setPixelSize(round(2.2*fPx))
        bookFont.setWeight(QFont.Bold)
        self.bookTitle.setFont(bookFont)
        self.bookTitle.setAlignment(Qt.AlignHCenter)

        self.projName = QLabel("Working Title: %s" % self.theProject.projName)
        workFont = self.projName.font()
        workFont.setPixelSize(round(0.8*fPx))
        workFont.setItalic(True)
        self.projName.setFont(workFont)
        self.projName.setAlignment(Qt.AlignHCenter)

        self.bookAuthors = QLabel("By: %s" % ", ".join(self.theProject.bookAuthors))
        authFont = self.bookAuthors.font()
        authFont.setPixelSize(round(1.2*fPx))
        self.bookAuthors.setFont(authFont)
        self.bookAuthors.setAlignment(Qt.AlignHCenter)

        # Stats
        # =====

        hCounts = self.theIndex.getNovelCounts()

        self.wordCountLbl = QLabel("<b>Words:</b>")
        self.wordCountVal = QLabel(f"{self.theProject.currWCount:n}")

        self.chapCountLbl = QLabel("<b>Chapters:</b>")
        self.chapCountVal = QLabel(f"{hCounts[2]:n}")

        self.sceneCountLbl = QLabel("<b>Scenes:</b>")
        self.sceneCountVal = QLabel(f"{hCounts[3]:n}")

        self.statsGrid = QGridLayout()
        self.statsGrid.addWidget(self.wordCountLbl,  0, 0, 1, 1, Qt.AlignLeft)
        self.statsGrid.addWidget(self.wordCountVal,  0, 1, 1, 1, Qt.AlignRight)
        self.statsGrid.addWidget(self.chapCountLbl,  1, 0, 1, 1, Qt.AlignLeft)
        self.statsGrid.addWidget(self.chapCountVal,  1, 1, 1, 1, Qt.AlignRight)
        self.statsGrid.addWidget(self.sceneCountLbl, 2, 0, 1, 1, Qt.AlignLeft)
        self.statsGrid.addWidget(self.sceneCountVal, 2, 1, 1, 1, Qt.AlignRight)
        self.statsGrid.setHorizontalSpacing(hPx)
        self.statsGrid.setVerticalSpacing(vPx)

        self.statsBox = QHBoxLayout()
        self.statsBox.addStretch(1)
        self.statsBox.addLayout(self.statsGrid)
        self.statsBox.addStretch(1)

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.bookTitle)
        self.outerBox.addWidget(self.projName)
        self.outerBox.addWidget(self.bookAuthors)
        self.outerBox.addSpacing(round(2.5*fPx))
        self.outerBox.addLayout(self.statsBox)
        self.outerBox.addStretch(1)

        self.setLayout(self.outerBox)

        return

# END Class GuiProjectDetailsMain

class GuiProjectDetailsContents(QWidget):

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

        # Internal
        self._theToC = []

        iPx = self.theTheme.baseIconSize

        # Contents Tree
        # =============

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

        # Options
        # =======

        wordsPerPage = self.optState.getInt("GuiProjectDetails", "wordsPerPage", 300)
        clearDouble  = self.optState.getInt("GuiProjectDetails", "clearDouble", True)

        self.optionsBox  = QGroupBox("Options", self)
        self.optionsForm = QGridLayout(self)
        self.optionsBox.setLayout(self.optionsForm)

        self.wpLabel = QLabel("Words per page")
        self.wpValue = QSpinBox()
        self.wpValue.setMinimum(10)
        self.wpValue.setMaximum(1000)
        self.wpValue.setSingleStep(10)
        self.wpValue.setValue(wordsPerPage)
        self.wpValue.valueChanged.connect(self._populateTree)

        self.dblLabel = QLabel("Clear double pages")
        self.dblValue = QSwitch(self, 2*iPx, iPx)
        self.dblValue.setChecked(clearDouble)
        self.dblValue.clicked.connect(self._populateTree)

        self.optionsForm.addWidget(self.wpLabel,  0, 0, 1, 1, Qt.AlignLeft)
        self.optionsForm.addWidget(self.wpValue,  0, 1, 1, 1, Qt.AlignRight)
        self.optionsForm.addWidget(self.dblLabel, 1, 0, 1, 1, Qt.AlignLeft)
        self.optionsForm.addWidget(self.dblValue, 1, 1, 1, 1, Qt.AlignRight)
        self.optionsForm.setColumnStretch(2, 1)

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.chTree)
        self.outerBox.addWidget(self.optionsBox)

        self.setLayout(self.outerBox)

        self._prepareData()
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

    def _prepareData(self):
        """Extract the data for the tree.
        """
        self._theToC = []
        self._theToC = self.theIndex.getTableOfContents(2)
        self._theToC.append(("", "H0", "END", 0))
        return

    ##
    #  Slots
    ##

    def _populateTree(self):
        """Set the content of the chapter/page tree.
        """
        dblPages = self.dblValue.isChecked()
        wpPage   = self.wpValue.value()

        tPages = 1
        pTotal = 0

        theList = []
        for tKey, tLevel, tTitle, wCount in self._theToC:
            pCount = math.ceil(wCount/wpPage)
            if dblPages:
                pCount += pCount%2
            pTotal += pCount
            theList.append((tLevel, tTitle, wCount, pCount))

        self.chTree.clear()
        for tLevel, tTitle, wCount, pCount in theList:
            newItem = QTreeWidgetItem()

            newItem.setIcon(self.C_TITLE, self.theTheme.getIcon("doc_%s" % tLevel.lower()))
            newItem.setText(self.C_TITLE, tTitle)
            newItem.setText(self.C_WORDS, f"{wCount:n}")
            newItem.setText(self.C_PAGES, f"{pCount:n}")
            newItem.setText(self.C_PAGE,  f"{tPages:n}")
            newItem.setText(self.C_PROG,  f"{100*(tPages-1)/pTotal:.1f}\u202f%")

            newItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)
            newItem.setTextAlignment(self.C_PAGES, Qt.AlignRight)
            newItem.setTextAlignment(self.C_PAGE,  Qt.AlignRight)
            newItem.setTextAlignment(self.C_PROG,  Qt.AlignRight)

            tPages += pCount

            self.chTree.addTopLevelItem(newItem)

        return

# END Class GuiProjectDetailsContents
