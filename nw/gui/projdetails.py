"""
novelWriter – GUI Project Details
=================================
Class holding the project details dialog

File History:
Created: 2021-01-03 [1.1a0]

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
import math
import logging

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QDialogButtonBox, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QSpinBox, QGridLayout, QHBoxLayout, QLineEdit, QAbstractItemView
)

from nw.common import numberToRoman
from nw.constants import nwUnicode
from nw.gui.custom import PagedDialog, QSwitch

logger = logging.getLogger(__name__)


class GuiProjectDetails(PagedDialog):

    def __init__(self, theParent):
        PagedDialog.__init__(self, theParent)

        logger.debug("Initialising GuiProjectDetails ...")
        self.setObjectName("GuiProjectDetails")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.optState   = theParent.theProject.optState

        self.setWindowTitle(self.tr("Project Details"))

        wW = self.mainConf.pxInt(600)
        wH = self.mainConf.pxInt(400)

        self.setMinimumWidth(wW)
        self.setMinimumHeight(wH)
        self.resize(
            self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "winWidth",  wW)),
            self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "winHeight", wH))
        )

        self.tabMain = GuiProjectDetailsMain(self.theParent, self.theProject)
        self.tabContents = GuiProjectDetailsContents(self.theParent, self.theProject)

        self.addTab(self.tabMain, self.tr("Overview"))
        self.addTab(self.tabContents, self.tr("Contents"))

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.button(QDialogButtonBox.Close).setText(self.tr("Close"))
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
        countFrom    = self.tabContents.poValue.value()
        clearDouble  = self.tabContents.dblValue.isChecked()

        self.optState.setValue("GuiProjectDetails", "winWidth",     winWidth)
        self.optState.setValue("GuiProjectDetails", "winHeight",    winHeight)
        self.optState.setValue("GuiProjectDetails", "widthCol0",    widthCol0)
        self.optState.setValue("GuiProjectDetails", "widthCol1",    widthCol1)
        self.optState.setValue("GuiProjectDetails", "widthCol2",    widthCol2)
        self.optState.setValue("GuiProjectDetails", "widthCol3",    widthCol3)
        self.optState.setValue("GuiProjectDetails", "widthCol4",    widthCol4)
        self.optState.setValue("GuiProjectDetails", "wordsPerPage", wordsPerPage)
        self.optState.setValue("GuiProjectDetails", "countFrom",    countFrom)
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
        fPt = self.theTheme.fontPointSize
        vPx = self.mainConf.pxInt(4)
        hPx = self.mainConf.pxInt(12)

        # Header
        # ======

        self.bookTitle = QLabel(self.theProject.bookTitle)
        bookFont = self.bookTitle.font()
        bookFont.setPointSizeF(2.2*fPt)
        bookFont.setWeight(QFont.Bold)
        self.bookTitle.setFont(bookFont)
        self.bookTitle.setAlignment(Qt.AlignHCenter)
        self.bookTitle.setWordWrap(True)

        self.projName = QLabel(
            self.tr("Working Title: {0}").format(self.theProject.projName)
        )
        workFont = self.projName.font()
        workFont.setPointSizeF(0.8*fPt)
        workFont.setItalic(True)
        self.projName.setFont(workFont)
        self.projName.setAlignment(Qt.AlignHCenter)
        self.projName.setWordWrap(True)

        self.bookAuthors = QLabel(self.tr("By {0}").format(self.theProject.getAuthors()))
        authFont = self.bookAuthors.font()
        authFont.setPointSizeF(1.2*fPt)
        self.bookAuthors.setFont(authFont)
        self.bookAuthors.setAlignment(Qt.AlignHCenter)
        self.bookAuthors.setWordWrap(True)

        # Stats
        # =====

        hCounts = self.theIndex.getNovelTitleCounts()
        nwCount = self.theIndex.getNovelWordCount()

        self.wordCountLbl = QLabel("<b>%s:</b>" % self.tr("Words"))
        self.wordCountVal = QLabel(f"{nwCount:n}")

        self.chapCountLbl = QLabel("<b>%s:</b>" % self.tr("Chapters"))
        self.chapCountVal = QLabel(f"{hCounts[2]:n}")

        self.sceneCountLbl = QLabel("<b>%s:</b>" % self.tr("Scenes"))
        self.sceneCountVal = QLabel(f"{hCounts[3]:n}")

        self.revCountLbl = QLabel("<b>%s:</b>" % self.tr("Revisions"))
        self.revCountVal = QLabel(f"{self.theProject.saveCount:n}")

        edTime = self.theProject.getCurrentEditTime()
        self.editTimeLbl = QLabel("<b>%s:</b>" % self.tr("Editing Time"))
        self.editTimeVal = QLabel(f"{edTime//3600:02d}:{edTime%3600//60:02d}")

        self.statsGrid = QGridLayout()
        self.statsGrid.addWidget(self.wordCountLbl,  0, 0, 1, 1, Qt.AlignRight)
        self.statsGrid.addWidget(self.wordCountVal,  0, 1, 1, 1, Qt.AlignLeft)
        self.statsGrid.addWidget(self.chapCountLbl,  1, 0, 1, 1, Qt.AlignRight)
        self.statsGrid.addWidget(self.chapCountVal,  1, 1, 1, 1, Qt.AlignLeft)
        self.statsGrid.addWidget(self.sceneCountLbl, 2, 0, 1, 1, Qt.AlignRight)
        self.statsGrid.addWidget(self.sceneCountVal, 2, 1, 1, 1, Qt.AlignLeft)
        self.statsGrid.addWidget(self.revCountLbl,   3, 0, 1, 1, Qt.AlignRight)
        self.statsGrid.addWidget(self.revCountVal,   3, 1, 1, 1, Qt.AlignLeft)
        self.statsGrid.addWidget(self.editTimeLbl,   4, 0, 1, 1, Qt.AlignRight)
        self.statsGrid.addWidget(self.editTimeVal,   4, 1, 1, 1, Qt.AlignLeft)
        self.statsGrid.setHorizontalSpacing(hPx)
        self.statsGrid.setVerticalSpacing(vPx)

        # Meta
        # ====

        self.projPathLbl = QLabel("<b>%s:</b>" % self.tr("Path"))
        self.projPathVal = QLineEdit()
        self.projPathVal.setText(self.theProject.projPath)
        self.projPathVal.setReadOnly(True)

        self.projPathBox = QHBoxLayout()
        self.projPathBox.addWidget(self.projPathLbl)
        self.projPathBox.addWidget(self.projPathVal)
        self.projPathBox.setSpacing(hPx)

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addSpacing(fPx)
        self.outerBox.addWidget(self.bookTitle)
        self.outerBox.addWidget(self.projName)
        self.outerBox.addWidget(self.bookAuthors)
        self.outerBox.addSpacing(2*fPx)
        self.outerBox.addLayout(self.statsGrid)
        self.outerBox.addSpacing(fPx)
        self.outerBox.addStretch(1)
        self.outerBox.addLayout(self.projPathBox)

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
        hPx = self.mainConf.pxInt(12)
        vPx = self.mainConf.pxInt(4)

        # Contents Tree
        # =============

        self.tocTree = QTreeWidget()
        self.tocTree.setIconSize(QSize(iPx, iPx))
        self.tocTree.setIndentation(0)
        self.tocTree.setColumnCount(6)
        self.tocTree.setSelectionMode(QAbstractItemView.NoSelection)
        self.tocTree.setHeaderLabels([
            self.tr("Title"),
            self.tr("Words"),
            self.tr("Pages"),
            self.tr("Page"),
            self.tr("Progress"),
            ""
        ])

        treeHeadItem = self.tocTree.headerItem()
        treeHeadItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)
        treeHeadItem.setTextAlignment(self.C_PAGES, Qt.AlignRight)
        treeHeadItem.setTextAlignment(self.C_PAGE,  Qt.AlignRight)
        treeHeadItem.setTextAlignment(self.C_PROG,  Qt.AlignRight)

        treeHeader = self.tocTree.header()
        treeHeader.setStretchLastSection(True)
        treeHeader.setMinimumSectionSize(hPx)

        wCol0 = self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "widthCol0", 200))
        wCol1 = self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "widthCol1", 60))
        wCol2 = self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "widthCol2", 60))
        wCol3 = self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "widthCol3", 60))
        wCol4 = self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "widthCol4", 90))

        self.tocTree.setColumnWidth(0, wCol0)
        self.tocTree.setColumnWidth(1, wCol1)
        self.tocTree.setColumnWidth(2, wCol2)
        self.tocTree.setColumnWidth(3, wCol3)
        self.tocTree.setColumnWidth(4, wCol4)
        self.tocTree.setColumnWidth(5, hPx)

        # Options
        # =======

        wordsPerPage = self.optState.getInt("GuiProjectDetails", "wordsPerPage", 350)
        countFrom    = self.optState.getInt("GuiProjectDetails", "countFrom", 1)
        clearDouble  = self.optState.getInt("GuiProjectDetails", "clearDouble", True)

        wordsHelp = (
            self.tr("Typical word count for a 5 by 8 inch book page with 11 pt font is 350.")
        )
        offsetHelp = (
            self.tr("Start counting page numbers from this page.")
        )
        dblHelp = (
            self.tr("Assume a new chapter or partition always start on an odd numbered page.")
        )

        self.wpLabel = QLabel(self.tr("Words per page"))
        self.wpLabel.setToolTip(wordsHelp)

        self.wpValue = QSpinBox()
        self.wpValue.setMinimum(10)
        self.wpValue.setMaximum(1000)
        self.wpValue.setSingleStep(10)
        self.wpValue.setValue(wordsPerPage)
        self.wpValue.setToolTip(wordsHelp)
        self.wpValue.valueChanged.connect(self._populateTree)

        self.poLabel = QLabel(self.tr("Count pages from"))
        self.poLabel.setToolTip(offsetHelp)

        self.poValue = QSpinBox()
        self.poValue.setMinimum(1)
        self.poValue.setMaximum(9999)
        self.poValue.setSingleStep(1)
        self.poValue.setValue(countFrom)
        self.poValue.setToolTip(offsetHelp)
        self.poValue.valueChanged.connect(self._populateTree)

        self.dblLabel = QLabel(self.tr("Clear double pages"))
        self.dblLabel.setToolTip(dblHelp)

        self.dblValue = QSwitch(self, 2*iPx, iPx)
        self.dblValue.setChecked(clearDouble)
        self.dblValue.setToolTip(dblHelp)
        self.dblValue.clicked.connect(self._populateTree)

        self.optionsBox = QGridLayout()
        self.optionsBox.addWidget(self.wpLabel,  0, 0)
        self.optionsBox.addWidget(self.wpValue,  0, 1)
        self.optionsBox.addWidget(self.dblLabel, 0, 3)
        self.optionsBox.addWidget(self.dblValue, 0, 4)
        self.optionsBox.addWidget(self.poLabel,  1, 0)
        self.optionsBox.addWidget(self.poValue,  1, 1)
        self.optionsBox.setHorizontalSpacing(hPx)
        self.optionsBox.setVerticalSpacing(vPx)
        self.optionsBox.setColumnStretch(2, 1)

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(QLabel("<b>%s</b>" % self.tr("Table of Contents")))
        self.outerBox.addWidget(self.tocTree)
        self.outerBox.addLayout(self.optionsBox)

        self.setLayout(self.outerBox)

        self._prepareData()
        self._populateTree()

        return

    def getColumnSizes(self):
        """Return the column widths for the tree columns.
        """
        retVals = [
            self.tocTree.columnWidth(0),
            self.tocTree.columnWidth(1),
            self.tocTree.columnWidth(2),
            self.tocTree.columnWidth(3),
            self.tocTree.columnWidth(4),
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
        self._theToC.append(("", 0, self.tr("END"), 0))
        return

    ##
    #  Slots
    ##

    def _populateTree(self):
        """Set the content of the chapter/page tree.
        """
        dblPages = self.dblValue.isChecked()
        wpPage = self.wpValue.value()
        fstPage = self.poValue.value() - 1

        pTotal = 0
        tPages = 1

        theList = []
        for _, tLevel, tTitle, wCount in self._theToC:
            pCount = math.ceil(wCount/wpPage)
            if dblPages:
                pCount += pCount%2

            pTotal += pCount
            theList.append((tLevel, tTitle, wCount, pCount))

        pMax = pTotal - fstPage

        self.tocTree.clear()
        for tLevel, tTitle, wCount, pCount in theList:
            newItem = QTreeWidgetItem()

            if tPages <= fstPage:
                progPage = numberToRoman(tPages, True)
                progText = ""
            else:
                cPage = tPages - fstPage
                pgProg = 100.0*(cPage - 1)/pMax if pMax > 0 else 0.0
                progPage = f"{cPage:n}"
                progText = f"{pgProg:.1f}{nwUnicode.U_THSP}%"

            newItem.setIcon(self.C_TITLE, self.theTheme.getIcon("doc_h%d" % tLevel))
            newItem.setText(self.C_TITLE, tTitle)
            newItem.setText(self.C_WORDS, f"{wCount:n}")
            newItem.setText(self.C_PAGES, f"{pCount:n}")
            newItem.setText(self.C_PAGE,  progPage)
            newItem.setText(self.C_PROG,  progText)

            newItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)
            newItem.setTextAlignment(self.C_PAGES, Qt.AlignRight)
            newItem.setTextAlignment(self.C_PAGE,  Qt.AlignRight)
            newItem.setTextAlignment(self.C_PROG,  Qt.AlignRight)

            # Make pages and titles/partitions stand out
            if tLevel < 2:
                bFont = newItem.font(self.C_TITLE)
                if tLevel == 0:
                    bFont.setItalic(True)
                else:
                    bFont.setBold(True)
                    bFont.setUnderline(True)
                newItem.setFont(self.C_TITLE, bFont)

            tPages += pCount

            self.tocTree.addTopLevelItem(newItem)

        return

# END Class GuiProjectDetailsContents
