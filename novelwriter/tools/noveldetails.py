"""
novelWriter – GUI Novel Info
============================

File History:
Created: 2024-01-18 [2.3b1] GuiNovelDetails

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

import logging
import math

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialogButtonBox, QFormLayout, QGridLayout, QHBoxLayout,
    QLabel, QSpinBox, QStackedWidget, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import formatTime, numberToRoman
from novelwriter.constants import nwUnicode
from novelwriter.extensions.configlayout import NColourLabel, NFixedPage, NScrollablePage
from novelwriter.extensions.modified import NNonBlockingDialog
from novelwriter.extensions.novelselector import NovelSelector
from novelwriter.extensions.pagedsidebar import NPagedSideBar
from novelwriter.extensions.switch import NSwitch
from novelwriter.types import QtAlignRight, QtDecoration, QtDialogClose

logger = logging.getLogger(__name__)


class GuiNovelDetails(NNonBlockingDialog):

    PAGE_OVERVIEW = 1
    PAGE_CONTENTS = 2

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiNovelDetails")
        self.setObjectName("GuiNovelDetails")
        self.setWindowTitle(self.tr("Novel Details"))

        options = SHARED.project.options
        self.setMinimumSize(CONFIG.pxInt(500), CONFIG.pxInt(400))
        self.resize(
            CONFIG.pxInt(options.getInt("GuiNovelDetails", "winWidth", CONFIG.pxInt(650))),
            CONFIG.pxInt(options.getInt("GuiNovelDetails", "winHeight", CONFIG.pxInt(500)))
        )

        # Title
        self.titleLabel = NColourLabel(
            self.tr("Novel Details"), self, color=SHARED.theme.helpText,
            scale=NColourLabel.HEADER_SCALE, indent=CONFIG.pxInt(4)
        )

        # Novel Selector
        self.novelSelector = NovelSelector(self)
        self.novelSelector.refreshNovelList()
        self.novelSelector.setHandle(
            options.getString("GuiNovelDetails", "novelRoot", self.novelSelector.firstHandle or "")
        )

        # SideBar
        self.sidebar = NPagedSideBar(self)
        self.sidebar.setLabelColor(SHARED.theme.helpText)
        self.sidebar.addButton(self.tr("Overview"), self.PAGE_OVERVIEW)
        self.sidebar.addButton(self.tr("Contents"), self.PAGE_CONTENTS)
        self.sidebar.setSelected(self.PAGE_OVERVIEW)
        self.sidebar.buttonClicked.connect(self._sidebarClicked)

        # Content
        self.overviewPage = _OverviewPage(self)
        self.contentsPage = _ContentsPage(self)

        self.mainStack = QStackedWidget(self)
        self.mainStack.addWidget(self.overviewPage)
        self.mainStack.addWidget(self.contentsPage)

        # Buttons
        self.buttonBox = QDialogButtonBox(QtDialogClose, self)
        self.buttonBox.rejected.connect(self.reject)

        # Assemble
        self.topBox = QHBoxLayout()
        self.topBox.addWidget(self.titleLabel)
        self.topBox.addStretch(1)
        self.topBox.addWidget(self.novelSelector, 1)

        self.mainBox = QHBoxLayout()
        self.mainBox.addWidget(self.sidebar)
        self.mainBox.addWidget(self.mainStack)
        self.mainBox.setContentsMargins(0, 0, 0, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.topBox)
        self.outerBox.addLayout(self.mainBox)
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(CONFIG.pxInt(8))

        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)

        # Connect Signals
        self.novelSelector.novelSelectionChanged.connect(self.overviewPage.novelValueChanged)
        self.novelSelector.novelSelectionChanged.connect(self.contentsPage.novelValueChanged)

        logger.debug("Ready: GuiNovelDetails")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiNovelDetails")
        return

    ##
    #  Methods
    ##

    def updateValues(self) -> None:
        """Load the dialogs initial values."""
        self.overviewPage.updateProjectData()
        self.overviewPage.novelValueChanged(self.novelSelector.handle)
        self.contentsPage.novelValueChanged(self.novelSelector.handle)
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window and save settings."""
        self._saveSettings()
        event.accept()
        self.softDelete()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _sidebarClicked(self, pageId: int) -> None:
        """Process a user request to switch page."""
        if pageId == self.PAGE_OVERVIEW:
            self.mainStack.setCurrentWidget(self.overviewPage)
        elif pageId == self.PAGE_CONTENTS:
            self.mainStack.setCurrentWidget(self.contentsPage)
        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self) -> None:
        """Save the user GUI settings."""
        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())
        novelRoot = self.novelSelector.handle

        logger.debug("Saving State: GuiNovelDetails")
        options = SHARED.project.options
        options.setValue("GuiNovelDetails", "winWidth", winWidth)
        options.setValue("GuiNovelDetails", "winHeight", winHeight)
        options.setValue("GuiNovelDetails", "novelRoot", novelRoot)

        self.contentsPage.saveSettings()

        return


class _OverviewPage(NScrollablePage):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        mPx = CONFIG.pxInt(8)
        sPx = CONFIG.pxInt(16)
        hPx = CONFIG.pxInt(24)
        vPx = CONFIG.pxInt(4)

        # Project Info
        self.projLabel = NColourLabel(
            self.tr("Project"), self, color=SHARED.theme.helpText,
            scale=NColourLabel.HEADER_SCALE
        )

        self.projName = QLabel("", self)
        self.projWords = QLabel("", self)
        self.projNovels = QLabel("", self)
        self.projNotes = QLabel("", self)
        self.projRevisions = QLabel("", self)
        self.projEditTime = QLabel("", self)

        self.projForm = QFormLayout()
        self.projForm.addRow("<b>{0}</b>".format(self.tr("Name")), self.projName)
        self.projForm.addRow("<b>{0}</b>".format(self.tr("Revisions")), self.projRevisions)
        self.projForm.addRow("<b>{0}</b>".format(self.tr("Editing Time")), self.projEditTime)
        self.projForm.addRow("<b>{0}</b>".format(self.tr("Word Count")), self.projWords)
        self.projForm.addRow("<b>\u2026 {0}</b>".format(self.tr("In Novels")), self.projNovels)
        self.projForm.addRow("<b>\u2026 {0}</b>".format(self.tr("In Notes")), self.projNotes)
        self.projForm.setContentsMargins(mPx, 0, 0, 0)
        self.projForm.setHorizontalSpacing(hPx)
        self.projForm.setVerticalSpacing(vPx)

        # Novel Info
        self.novelLabel = NColourLabel(
            self.tr("Selected Novel"), self, color=SHARED.theme.helpText,
            scale=NColourLabel.HEADER_SCALE
        )

        self.novelName = QLabel("", self)
        self.novelWords = QLabel("", self)
        self.novelChapters = QLabel("", self)
        self.novelScenes = QLabel("", self)

        self.novelForm = QFormLayout()
        self.novelForm.addRow("<b>{0}</b>".format(self.tr("Name")), self.novelName)
        self.novelForm.addRow("<b>{0}</b>".format(self.tr("Word Count")), self.novelWords)
        self.novelForm.addRow("<b>{0}</b>".format(self.tr("Chapters")), self.novelChapters)
        self.novelForm.addRow("<b>{0}</b>".format(self.tr("Scenes")), self.novelScenes)
        self.novelForm.setContentsMargins(mPx, 0, 0, 0)
        self.novelForm.setHorizontalSpacing(hPx)
        self.novelForm.setVerticalSpacing(vPx)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.projLabel)
        self.outerBox.addLayout(self.projForm)
        self.outerBox.addWidget(self.novelLabel)
        self.outerBox.addLayout(self.novelForm)
        self.outerBox.setSpacing(sPx)
        self.outerBox.addStretch(1)

        self.setCentralLayout(self.outerBox)

        return

    ##
    #  Methods
    ##

    def updateProjectData(self) -> None:
        """Load information about the project."""
        project = SHARED.project
        project.updateWordCounts()
        wcNovel, wcNotes = project.data.currCounts

        self.projName.setText(project.data.name)
        self.projRevisions.setText(f"{project.data.saveCount:n}")
        self.projEditTime.setText(formatTime(project.currentEditTime))
        self.projWords.setText(f"{wcNovel + wcNotes:n}")
        self.projNovels.setText(f"{wcNovel:n}")
        self.projNotes.setText(f"{wcNotes:n}")
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def novelValueChanged(self, tHandle: str) -> None:
        """Refresh the data for the selected novel."""
        project = SHARED.project
        if nwItem := project.tree[tHandle]:
            self.novelName.setText(nwItem.itemName)

        nwCount = project.index.getNovelWordCount(rootHandle=tHandle)
        self.novelWords.setText(f"{nwCount:n}")

        hCounts = project.index.getNovelTitleCounts(rootHandle=tHandle)
        self.novelChapters.setText(f"{hCounts[2]:n}")
        self.novelScenes.setText(f"{hCounts[3]:n}")

        return


class _ContentsPage(NFixedPage):

    C_TITLE = 0
    C_WORDS = 1
    C_PAGES = 2
    C_PAGE  = 3
    C_PROG  = 4

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self._data = []
        self._currentRoot = None

        iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize
        hPx = CONFIG.pxInt(12)
        vPx = CONFIG.pxInt(4)
        options = SHARED.project.options

        # Title
        self.contentLabel = NColourLabel(
            self.tr("Table of Contents"), self, color=SHARED.theme.helpText,
            scale=NColourLabel.HEADER_SCALE
        )

        # Contents Tree
        self.tocTree = QTreeWidget(self)
        self.tocTree.setIconSize(iSz)
        self.tocTree.setIndentation(0)
        self.tocTree.setColumnCount(6)
        self.tocTree.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tocTree.setHeaderLabels([
            self.tr("Title"),
            self.tr("Words"),
            self.tr("Pages"),
            self.tr("Page"),
            self.tr("Progress"),
            "",
        ])

        treeHeadItem = self.tocTree.headerItem()
        if treeHeadItem:
            treeHeadItem.setTextAlignment(self.C_WORDS, QtAlignRight)
            treeHeadItem.setTextAlignment(self.C_PAGES, QtAlignRight)
            treeHeadItem.setTextAlignment(self.C_PAGE,  QtAlignRight)
            treeHeadItem.setTextAlignment(self.C_PROG,  QtAlignRight)

        treeHeader = self.tocTree.header()
        treeHeader.setStretchLastSection(True)
        treeHeader.setMinimumSectionSize(hPx)

        wCol0 = CONFIG.pxInt(options.getInt("GuiNovelDetails", "widthCol0", 200))
        wCol1 = CONFIG.pxInt(options.getInt("GuiNovelDetails", "widthCol1", 60))
        wCol2 = CONFIG.pxInt(options.getInt("GuiNovelDetails", "widthCol2", 60))
        wCol3 = CONFIG.pxInt(options.getInt("GuiNovelDetails", "widthCol3", 60))
        wCol4 = CONFIG.pxInt(options.getInt("GuiNovelDetails", "widthCol4", 90))

        self.tocTree.setColumnWidth(0, wCol0)
        self.tocTree.setColumnWidth(1, wCol1)
        self.tocTree.setColumnWidth(2, wCol2)
        self.tocTree.setColumnWidth(3, wCol3)
        self.tocTree.setColumnWidth(4, wCol4)
        self.tocTree.setColumnWidth(5, hPx)

        # Options
        wordsPerPage = options.getInt("GuiNovelDetails", "wordsPerPage", 350)
        countFrom    = options.getInt("GuiNovelDetails", "countFrom", 1)
        clearDouble  = options.getBool("GuiNovelDetails", "clearDouble", True)

        self.wpLabel = QLabel(self.tr("Words per page"), self)

        self.wpValue = QSpinBox(self)
        self.wpValue.setMinimum(10)
        self.wpValue.setMaximum(1000)
        self.wpValue.setSingleStep(10)
        self.wpValue.setValue(wordsPerPage)
        self.wpValue.valueChanged.connect(self._populateTree)

        self.poLabel = QLabel(self.tr("First page offset"), self)

        self.poValue = QSpinBox(self)
        self.poValue.setMinimum(1)
        self.poValue.setMaximum(9999)
        self.poValue.setSingleStep(1)
        self.poValue.setValue(countFrom)
        self.poValue.valueChanged.connect(self._populateTree)

        self.dblLabel = QLabel(self.tr("Chapters on odd pages"), self)

        self.dblValue = NSwitch(self, height=iPx)
        self.dblValue.setChecked(clearDouble)
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
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.contentLabel)
        self.outerBox.addWidget(self.tocTree)
        self.outerBox.addLayout(self.optionsBox)

        self.setCentralLayout(self.outerBox)

        return

    def saveSettings(self) -> None:
        """Save the user GUI settings."""
        widthCol0 = CONFIG.rpxInt(self.tocTree.columnWidth(0))
        widthCol1 = CONFIG.rpxInt(self.tocTree.columnWidth(1))
        widthCol2 = CONFIG.rpxInt(self.tocTree.columnWidth(2))
        widthCol3 = CONFIG.rpxInt(self.tocTree.columnWidth(3))
        widthCol4 = CONFIG.rpxInt(self.tocTree.columnWidth(4))

        options = SHARED.project.options
        options.setValue("GuiNovelDetails", "widthCol0",    widthCol0)
        options.setValue("GuiNovelDetails", "widthCol1",    widthCol1)
        options.setValue("GuiNovelDetails", "widthCol2",    widthCol2)
        options.setValue("GuiNovelDetails", "widthCol3",    widthCol3)
        options.setValue("GuiNovelDetails", "widthCol4",    widthCol4)
        options.setValue("GuiNovelDetails", "wordsPerPage", self.wpValue.value())
        options.setValue("GuiNovelDetails", "countFrom",    self.poValue.value())
        options.setValue("GuiNovelDetails", "clearDouble",  self.dblValue.isChecked())
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def novelValueChanged(self, tHandle: str) -> None:
        """Refresh the tree with another root item."""
        if tHandle != self._currentRoot:
            self._prepareData(tHandle)
            self._populateTree()
            self._currentRoot = tHandle
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _populateTree(self) -> None:
        """Set the content of the chapter/page tree."""
        dblPages = self.dblValue.isChecked()
        wpPage = self.wpValue.value()
        fstPage = self.poValue.value() - 1

        pTotal = 0
        tPages = 1

        entries = []
        for _, tLevel, tTitle, wCount in self._data:
            pCount = math.ceil(wCount/wpPage)
            if dblPages:
                pCount += pCount%2

            pTotal += pCount
            entries.append((tLevel, tTitle, wCount, pCount))

        pMax = pTotal - fstPage

        self.tocTree.clear()
        for tLevel, tTitle, wCount, pCount in entries:
            newItem = QTreeWidgetItem()

            if tPages <= fstPage:
                progPage = numberToRoman(tPages, True)
                progText = ""
            else:
                cPage = tPages - fstPage
                pgProg = 100.0*(cPage - 1)/pMax if pMax > 0 else 0.0
                progPage = f"{cPage:n}"
                progText = f"{pgProg:.1f}{nwUnicode.U_THSP}%"

            hDec = SHARED.theme.getHeaderDecoration(tLevel)
            if tTitle.strip() == "":
                tTitle = self.tr("Untitled")

            newItem.setData(self.C_TITLE, QtDecoration, hDec)
            newItem.setText(self.C_TITLE, tTitle)
            newItem.setText(self.C_WORDS, f"{wCount:n}")
            newItem.setText(self.C_PAGES, f"{pCount:n}")
            newItem.setText(self.C_PAGE,  progPage)
            newItem.setText(self.C_PROG,  progText)

            newItem.setTextAlignment(self.C_WORDS, QtAlignRight)
            newItem.setTextAlignment(self.C_PAGES, QtAlignRight)
            newItem.setTextAlignment(self.C_PAGE,  QtAlignRight)
            newItem.setTextAlignment(self.C_PROG,  QtAlignRight)

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

    ##
    #  Internal Functions
    ##

    def _prepareData(self, rootHandle: str | None) -> None:
        """Extract the information from the project index."""
        logger.debug("Populating ToC from handle '%s'", rootHandle)
        self._data = SHARED.project.index.getTableOfContents(rootHandle, 2)
        self._data.append(("", 0, self.tr("END"), 0))
        return
