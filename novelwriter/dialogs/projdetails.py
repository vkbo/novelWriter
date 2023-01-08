"""
novelWriter – GUI Project Details
=================================
Class holding the project details dialog

File History:
Created: 2021-01-03 [1.1rc1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import math
import logging
import novelwriter

from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from novelwriter.common import numberToRoman
from novelwriter.custom import PagedDialog, QSwitch
from novelwriter.constants import nwUnicode
from novelwriter.gui.components import NovelSelector

logger = logging.getLogger(__name__)


class GuiProjectDetails(PagedDialog):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiProjectDetails ...")
        self.setObjectName("GuiProjectDetails")

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.theProject = mainGui.theProject

        self.setWindowTitle(self.tr("Project Details"))

        wW = self.mainConf.pxInt(600)
        wH = self.mainConf.pxInt(400)
        pOptions = self.theProject.options

        self.setMinimumWidth(wW)
        self.setMinimumHeight(wH)
        self.resize(
            self.mainConf.pxInt(pOptions.getInt("GuiProjectDetails", "winWidth",  wW)),
            self.mainConf.pxInt(pOptions.getInt("GuiProjectDetails", "winHeight", wH))
        )

        self.tabMain = GuiProjectDetailsMain(self.mainGui, self.theProject)
        self.tabContents = GuiProjectDetailsContents(self.mainGui, self.theProject)

        self.addTab(self.tabMain, self.tr("Overview"))
        self.addTab(self.tabContents, self.tr("Contents"))

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.button(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)
        self.addControls(self.buttonBox)

        logger.debug("GuiProjectDetails initialisation complete")

        return

    def updateValues(self):
        """Set all the values of the pages.
        """
        self.tabMain.updateValues()
        self.tabContents.updateValues()
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

        pOptions = self.theProject.options
        pOptions.setValue("GuiProjectDetails", "winWidth",     winWidth)
        pOptions.setValue("GuiProjectDetails", "winHeight",    winHeight)
        pOptions.setValue("GuiProjectDetails", "widthCol0",    widthCol0)
        pOptions.setValue("GuiProjectDetails", "widthCol1",    widthCol1)
        pOptions.setValue("GuiProjectDetails", "widthCol2",    widthCol2)
        pOptions.setValue("GuiProjectDetails", "widthCol3",    widthCol3)
        pOptions.setValue("GuiProjectDetails", "widthCol4",    widthCol4)
        pOptions.setValue("GuiProjectDetails", "wordsPerPage", wordsPerPage)
        pOptions.setValue("GuiProjectDetails", "countFrom",    countFrom)
        pOptions.setValue("GuiProjectDetails", "clearDouble",  clearDouble)

        return

# END Class GuiProjectDetails


class GuiProjectDetailsMain(QWidget):

    def __init__(self, mainGui, theProject):
        super().__init__(parent=mainGui)

        self.mainConf   = novelwriter.CONFIG
        self.theProject = theProject
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme

        fPx = self.mainTheme.fontPixelSize
        fPt = self.mainTheme.fontPointSize
        vPx = self.mainConf.pxInt(4)
        hPx = self.mainConf.pxInt(12)

        # Header
        # ======

        self.bookTitle = QLabel(self.theProject.data.title)
        bookFont = self.bookTitle.font()
        bookFont.setPointSizeF(2.2*fPt)
        bookFont.setWeight(QFont.Bold)
        self.bookTitle.setFont(bookFont)
        self.bookTitle.setAlignment(Qt.AlignHCenter)
        self.bookTitle.setWordWrap(True)

        self.projName = QLabel(
            self.tr("Working Title: {0}").format(self.theProject.data.name)
        )
        workFont = self.projName.font()
        workFont.setPointSizeF(0.8*fPt)
        workFont.setItalic(True)
        self.projName.setFont(workFont)
        self.projName.setAlignment(Qt.AlignHCenter)
        self.projName.setWordWrap(True)

        self.bookAuthors = QLabel(self.tr("By {0}").format(self.theProject.data.author))
        authFont = self.bookAuthors.font()
        authFont.setPointSizeF(1.2*fPt)
        self.bookAuthors.setFont(authFont)
        self.bookAuthors.setAlignment(Qt.AlignHCenter)
        self.bookAuthors.setWordWrap(True)

        # Stats
        # =====

        self.wordCountLbl = QLabel("<b>%s:</b>" % self.tr("Words"))
        self.wordCountVal = QLabel("")

        self.chapCountLbl = QLabel("<b>%s:</b>" % self.tr("Chapters"))
        self.chapCountVal = QLabel("")

        self.sceneCountLbl = QLabel("<b>%s:</b>" % self.tr("Scenes"))
        self.sceneCountVal = QLabel("")

        self.revCountLbl = QLabel("<b>%s:</b>" % self.tr("Revisions"))
        self.revCountVal = QLabel("")

        self.editTimeLbl = QLabel("<b>%s:</b>" % self.tr("Editing Time"))
        self.editTimeVal = QLabel("")

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

    def updateValues(self):
        """Set all the values.
        """
        pIndex = self.theProject.index
        hCounts = pIndex.getNovelTitleCounts()
        nwCount = pIndex.getNovelWordCount()
        edTime = self.theProject.getCurrentEditTime()

        self.wordCountVal.setText(f"{nwCount:n}")
        self.chapCountVal.setText(f"{hCounts[2]:n}")
        self.sceneCountVal.setText(f"{hCounts[3]:n}")
        self.revCountVal.setText(f"{self.theProject.data.saveCount:n}")
        self.editTimeVal.setText(f"{edTime//3600:02d}:{edTime%3600//60:02d}")

        self.projPathVal.setText(str(self.theProject.storage.storagePath))

        return

# END Class GuiProjectDetailsMain


class GuiProjectDetailsContents(QWidget):

    C_TITLE = 0
    C_WORDS = 1
    C_PAGES = 2
    C_PAGE  = 3
    C_PROG  = 4

    def __init__(self, mainGui, theProject):
        super().__init__(parent=mainGui)

        self.mainConf   = novelwriter.CONFIG
        self.theProject = theProject
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme

        # Internal
        self._theToC = []
        self._currentRoot = None

        iPx = self.mainTheme.baseIconSize
        hPx = self.mainConf.pxInt(12)
        vPx = self.mainConf.pxInt(4)
        pOptions = self.theProject.options

        # Header
        # ======

        self.tocLabel = QLabel("<b>%s</b>" % self.tr("Table of Contents"))

        self.novelValue = NovelSelector(self, self.theProject, self.mainGui)
        self.novelValue.setMinimumWidth(self.mainConf.pxInt(200))
        self.novelValue.novelSelectionChanged.connect(self._novelValueChanged)

        self.headBox = QHBoxLayout()
        self.headBox.addWidget(self.tocLabel)
        self.headBox.addWidget(self.novelValue)

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

        wCol0 = self.mainConf.pxInt(pOptions.getInt("GuiProjectDetails", "widthCol0", 200))
        wCol1 = self.mainConf.pxInt(pOptions.getInt("GuiProjectDetails", "widthCol1", 60))
        wCol2 = self.mainConf.pxInt(pOptions.getInt("GuiProjectDetails", "widthCol2", 60))
        wCol3 = self.mainConf.pxInt(pOptions.getInt("GuiProjectDetails", "widthCol3", 60))
        wCol4 = self.mainConf.pxInt(pOptions.getInt("GuiProjectDetails", "widthCol4", 90))

        self.tocTree.setColumnWidth(0, wCol0)
        self.tocTree.setColumnWidth(1, wCol1)
        self.tocTree.setColumnWidth(2, wCol2)
        self.tocTree.setColumnWidth(3, wCol3)
        self.tocTree.setColumnWidth(4, wCol4)
        self.tocTree.setColumnWidth(5, hPx)

        # Options
        # =======

        wordsPerPage = pOptions.getInt("GuiProjectDetails", "wordsPerPage", 350)
        countFrom    = pOptions.getInt("GuiProjectDetails", "countFrom", 1)
        clearDouble  = pOptions.getInt("GuiProjectDetails", "clearDouble", True)

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
        self.outerBox.addLayout(self.headBox)
        self.outerBox.addWidget(self.tocTree)
        self.outerBox.addLayout(self.optionsBox)

        self.setLayout(self.outerBox)

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

    def updateValues(self):
        """Populate the tree.
        """
        self._currentRoot = None
        self.novelValue.updateList()
        self.novelValue.setHandle(self.novelValue.firstHandle)
        self._prepareData(self.novelValue.firstHandle)
        self._populateTree()

        return

    ##
    #  Internal Functions
    ##

    def _prepareData(self, rootHandle):
        """Extract the information from the project index.
        """
        logger.debug("Populating ToC from handle '%s'", rootHandle)
        self._theToC = self.theProject.index.getTableOfContents(rootHandle, 2)
        self._theToC.append(("", 0, self.tr("END"), 0))
        return

    ##
    #  Slots
    ##

    @pyqtSlot(str)
    def _novelValueChanged(self, tHandle):
        """Refresh the tree with another root item.
        """
        if tHandle != self._currentRoot:
            self._prepareData(tHandle)
            self._populateTree()
            self._currentRoot = self.novelValue.handle
        return

    @pyqtSlot()
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

            hDec = self.mainTheme.getHeaderDecoration(tLevel)
            if tTitle.strip() == "":
                tTitle = self.tr("Untitled")

            newItem.setData(self.C_TITLE, Qt.DecorationRole, hDec)
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
