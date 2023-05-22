"""
novelWriter – GUI Build Settings
================================
GUI classes for editing Manuscript Build Settings

File History:
Created: 2023-02-13 [2.1b1]

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
from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from PyQt5.QtGui import QColor, QIcon, QSyntaxHighlighter, QTextCharFormat, QTextDocument
from PyQt5.QtCore import QEvent, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractButton, QAbstractItemView, QDialog, QDialogButtonBox, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMenu, QPlainTextEdit, QPushButton, QSplitter,
    QStackedWidget, QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget
)

from novelwriter import CONFIG
from novelwriter.constants import nwHeadingFormats
from novelwriter.core.buildsettings import BuildSettings, FilterMode
from novelwriter.extensions.switch import NSwitch
from novelwriter.extensions.switchbox import NSwitchBox
from novelwriter.extensions.pagedsidebar import NPagedSideBar

if TYPE_CHECKING:
    from novelwriter.guimain import GuiMain
    from novelwriter.gui.theme import GuiTheme

logger = logging.getLogger(__name__)


class GuiBuildSettings(QDialog):

    OPT_FILTERS  = 1
    OPT_HEADINGS = 2
    OPT_FORMAT   = 3
    OPT_CONTENT  = 4
    OPT_OUTPUT   = 5

    newSettingsReady = pyqtSignal(BuildSettings)

    def __init__(self, mainGui: GuiMain, build: BuildSettings):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiBuildSettings ...")
        self.setObjectName("GuiBuildSettings")

        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self._build = build

        self.setWindowTitle(self.tr("Manuscript Build Settings"))
        self.setMinimumWidth(CONFIG.pxInt(700))
        self.setMinimumHeight(CONFIG.pxInt(400))

        mPx = CONFIG.pxInt(150)
        wWin = CONFIG.pxInt(900)
        hWin = CONFIG.pxInt(600)

        pOptions = self.theProject.options
        self.resize(
            CONFIG.pxInt(pOptions.getInt("GuiBuildSettings", "winWidth", wWin)),
            CONFIG.pxInt(pOptions.getInt("GuiBuildSettings", "winHeight", hWin))
        )

        # Options SideBar
        # ===============

        self.optSideBar = NPagedSideBar(self)
        self.optSideBar.setMinimumWidth(mPx)
        self.optSideBar.setMaximumWidth(mPx)
        self.optSideBar.setLabelColor(self.mainTheme.helpText)

        self.optSideBar.addLabel(self.tr("Options"))
        self.optSideBar.addButton(self.tr("Filters"), self.OPT_FILTERS)
        self.optSideBar.addButton(self.tr("Headings"), self.OPT_HEADINGS)
        self.optSideBar.addButton(self.tr("Format"), self.OPT_FORMAT)
        self.optSideBar.addButton(self.tr("Content"), self.OPT_CONTENT)
        self.optSideBar.addButton(self.tr("Output"), self.OPT_OUTPUT)

        self.optSideBar.buttonClicked.connect(self._stackPageSelected)

        # Options Area
        # ============

        # Create Tabs
        self.optTabSelect = GuiBuildFilterTab(self, self._build)
        self.optTabHeadings = GuiBuildHeadingsTab(self, self._build)
        self.optTabFormat = GuiBuildFormatTab(self, self._build)
        self.optTabContent = GuiBuildContentTab(self, self._build)
        self.optTabOutput = GuiBuildOutputTab(self, self._build)

        # Add Tabs
        self.toolStack = QStackedWidget(self)
        self.toolStack.addWidget(self.optTabSelect)
        self.toolStack.addWidget(self.optTabHeadings)
        self.toolStack.addWidget(self.optTabFormat)
        self.toolStack.addWidget(self.optTabContent)
        self.toolStack.addWidget(self.optTabOutput)

        # Main Settings + Buttons
        # =======================

        self.lblBuildName = QLabel(self.tr("Name"))
        self.editBuildName = QLineEdit()
        self.dlgButtons = QDialogButtonBox(
            QDialogButtonBox.Apply | QDialogButtonBox.Save | QDialogButtonBox.Close
        )
        self.dlgButtons.clicked.connect(self._dialogButtonClicked)

        self.buttonBox = QHBoxLayout()
        self.buttonBox.addWidget(self.lblBuildName)
        self.buttonBox.addWidget(self.editBuildName)
        self.buttonBox.addWidget(self.dlgButtons)

        # Assemble GUI
        # ============

        self.mainBox = QHBoxLayout()
        self.mainBox.addWidget(self.optSideBar)
        self.mainBox.addWidget(self.toolStack)
        self.mainBox.setContentsMargins(0, 0, 0, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.mainBox)
        self.outerBox.addLayout(self.buttonBox)
        self.outerBox.setSpacing(CONFIG.pxInt(12))

        self.setLayout(self.outerBox)

        # Set Default Tab
        self.optSideBar.setSelected(self.OPT_FILTERS)

        logger.debug("GuiBuildSettings initialisation complete")

        return

    def loadContent(self):
        """Populate the child widgets.
        """
        self.editBuildName.setText(self._build.name)
        self.optTabSelect.loadContent()
        self.optTabHeadings.loadContent()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _stackPageSelected(self, pageId: int):
        """Process a user request to switch page.
        """
        if pageId == self.OPT_FILTERS:
            self.toolStack.setCurrentWidget(self.optTabSelect)
        elif pageId == self.OPT_HEADINGS:
            self.toolStack.setCurrentWidget(self.optTabHeadings)
        elif pageId == self.OPT_FORMAT:
            self.toolStack.setCurrentWidget(self.optTabFormat)
        elif pageId == self.OPT_CONTENT:
            self.toolStack.setCurrentWidget(self.optTabContent)
        elif pageId == self.OPT_OUTPUT:
            self.toolStack.setCurrentWidget(self.optTabOutput)
        return

    @pyqtSlot("QAbstractButton*")
    def _dialogButtonClicked(self, button: QAbstractButton):
        """Handle button clicks from the dialog button box.
        """
        role = self.dlgButtons.buttonRole(button)
        if role in (QDialogButtonBox.ApplyRole, QDialogButtonBox.AcceptRole):
            self._build.setName(self.editBuildName.text())
            self.newSettingsReady.emit(self._build)

        self._saveSettings()
        if role == QDialogButtonBox.AcceptRole:
            self.accept()
        elif role == QDialogButtonBox.RejectRole:
            self.reject()

        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QEvent):
        """Capture the user closing the window so we can save settings.
        """
        self._saveSettings()
        event.accept()
        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self):
        """Save the various user settings.
        """
        logger.debug("Saving GuiBuildSettings settings")

        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())

        treeWidth, filterWidth = self.optTabSelect.mainSplitSizes()

        pOptions = self.theProject.options
        pOptions.setValue("GuiBuildSettings", "winWidth", winWidth)
        pOptions.setValue("GuiBuildSettings", "winHeight", winHeight)
        pOptions.setValue("GuiBuildSettings", "treeWidth", treeWidth)
        pOptions.setValue("GuiBuildSettings", "filterWidth", filterWidth)
        pOptions.saveSettings()

        return

# END Class GuiBuildSettings


class GuiBuildFilterTab(QWidget):

    C_DATA   = 0
    C_NAME   = 0
    C_ACTIVE = 1
    C_STATUS = 2

    D_HANDLE = Qt.UserRole
    D_FILE   = Qt.UserRole + 1

    F_NONE     = 0
    F_FILTERED = 1
    F_INCLUDED = 2
    F_EXCLUDED = 3

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings):
        super().__init__(parent=buildMain)

        self.mainGui    = buildMain.mainGui
        self.mainTheme  = buildMain.mainGui.mainTheme
        self.theProject = buildMain.mainGui.theProject

        self._treeMap = {}
        self._build = build

        self._statusFlags = {
            self.F_NONE:     ("", QIcon()),
            self.F_FILTERED: (self.tr("Filtered"), self.mainTheme.getIcon("build_filtered")),
            self.F_INCLUDED: (self.tr("Included"), self.mainTheme.getIcon("build_included")),
            self.F_EXCLUDED: (self.tr("Excluded"), self.mainTheme.getIcon("build_excluded")),
        }

        # Project Tree
        # ============

        # Tree Settings
        iPx = self.mainTheme.baseIconSize
        cMg = CONFIG.pxInt(6)

        # Tree Widget
        self.optTree = QTreeWidget(self)
        self.optTree.setIconSize(QSize(iPx, iPx))
        self.optTree.setUniformRowHeights(True)
        self.optTree.setAllColumnsShowFocus(True)
        self.optTree.setHeaderHidden(True)
        self.optTree.setIndentation(iPx)
        self.optTree.setColumnCount(3)

        treeHeader = self.optTree.header()
        treeHeader.setStretchLastSection(False)
        treeHeader.setSectionResizeMode(self.C_NAME, QHeaderView.Stretch)
        treeHeader.setSectionResizeMode(self.C_ACTIVE, QHeaderView.Fixed)
        treeHeader.setSectionResizeMode(self.C_STATUS, QHeaderView.Fixed)
        treeHeader.resizeSection(self.C_ACTIVE, iPx + cMg)
        treeHeader.resizeSection(self.C_STATUS, iPx + cMg)

        self.optTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.optTree.setDragDropMode(QAbstractItemView.NoDragDrop)

        # Filters
        # =======

        self.filteredButton = QPushButton(self)
        self.filteredButton.setText(self._statusFlags[self.F_FILTERED][0])
        self.filteredButton.setIcon(self._statusFlags[self.F_FILTERED][1])
        self.filteredButton.clicked.connect(lambda: self._setSelectedMode(self.F_FILTERED))

        self.includedButton = QPushButton(self)
        self.includedButton.setText(self._statusFlags[self.F_INCLUDED][0])
        self.includedButton.setIcon(self._statusFlags[self.F_INCLUDED][1])
        self.includedButton.clicked.connect(lambda: self._setSelectedMode(self.F_INCLUDED))

        self.excludedButton = QPushButton(self)
        self.excludedButton.setText(self._statusFlags[self.F_EXCLUDED][0])
        self.excludedButton.setIcon(self._statusFlags[self.F_EXCLUDED][1])
        self.excludedButton.clicked.connect(lambda: self._setSelectedMode(self.F_EXCLUDED))

        self.modeBox = QHBoxLayout()
        self.modeBox.addWidget(self.filteredButton)
        self.modeBox.addWidget(self.includedButton)
        self.modeBox.addWidget(self.excludedButton)

        # Filer Options
        self.filterOpt = NSwitchBox(self, iPx)
        self.filterOpt.switchToggled.connect(self._applyFilterSwitch)

        # Assemble
        # ========

        pOptions = self.theProject.options
        wTree = CONFIG.pxInt(pOptions.getInt("GuiBuildSettings", "treeWidth", 0))
        fTree = CONFIG.pxInt(pOptions.getInt("GuiBuildSettings", "filterWidth", 0))

        self.selectionBox = QVBoxLayout()
        self.selectionBox.addLayout(self.modeBox)
        self.selectionBox.addWidget(self.filterOpt)
        self.selectionBox.setContentsMargins(0, 0, 0, 0)

        self.selectionWidget = QWidget()
        self.selectionWidget.setLayout(self.selectionBox)

        self.mainSplit = QSplitter()
        self.mainSplit.addWidget(self.optTree)
        self.mainSplit.addWidget(self.selectionWidget)
        if wTree > 0:
            self.mainSplit.setSizes([wTree, fTree])

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.mainSplit)
        self.outerBox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.outerBox)

        return

    def loadContent(self):
        """Populate the widgets.
        """
        self._populateTree()
        self._populateFilters()
        return

    def mainSplitSizes(self) -> tuple[int, int]:
        """Extract the sizes of the main splitter.
        """
        sizes = self.mainSplit.sizes()
        if len(sizes) < 2:
            return 0, 0
        return sizes[0], sizes[1]

    ##
    #  Slots
    ##

    @pyqtSlot(str, bool)
    def _applyFilterSwitch(self, key: str, state: bool):
        """A filter switch has been toggled, so update the settings.
        """
        if key.startswith("doc:"):
            self._build.setValue(key[4:], state)
            self._setTreeItemMode()
        elif key.startswith("root:"):
            self._build.setSkipRoot(key[5:], state)
            self._populateTree()
        return

    ##
    #  Internal Functions
    ##

    def _populateTree(self):
        """Build the tree of project items.
        """
        logger.debug("Building project tree")
        self._treeMap = {}
        self.optTree.clear()
        for nwItem in self.theProject.getProjectItems():

            tHandle = nwItem.itemHandle
            pHandle = nwItem.itemParent
            rHandle = nwItem.itemRoot
            isFile = nwItem.isFileType()
            isActive = nwItem.isActive

            if nwItem.isInactiveClass() or not self._build.isRootAllowed(rHandle):
                continue

            hLevel = nwItem.mainHeading
            itemIcon = self.mainTheme.getItemIcon(
                nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, hLevel
            )

            if isFile:
                iconName = "checked" if isActive else "unchecked"
            else:
                iconName = "noncheckable"

            trItem = QTreeWidgetItem()
            trItem.setIcon(self.C_NAME, itemIcon)
            trItem.setText(self.C_NAME, nwItem.itemName)
            trItem.setData(self.C_DATA, self.D_HANDLE, tHandle)
            trItem.setData(self.C_DATA, self.D_FILE, isFile)
            trItem.setIcon(self.C_ACTIVE, self.mainTheme.getIcon(iconName))

            trItem.setTextAlignment(self.C_NAME, Qt.AlignLeft)

            if pHandle is None:
                if nwItem.isRootType():
                    self.optTree.addTopLevelItem(trItem)
                else:
                    logger.debug("Skipping item '%s'", tHandle)
                    continue

            elif pHandle in self._treeMap:
                self._treeMap[pHandle].addChild(trItem)

            else:
                logger.debug("Skipping item '%s'", tHandle)
                continue

            self._treeMap[tHandle] = trItem
            trItem.setExpanded(True)

        self._setTreeItemMode()

        return

    def _populateFilters(self):
        """Populate the filter options switches.
        """
        self.filterOpt.clear()
        self.filterOpt.addLabel(self._build.getLabel("filter"))
        self.filterOpt.addItem(
            self.mainTheme.getIcon("proj_scene"),
            self._build.getLabel("filter.includeNovel"),
            "doc:filter.includeNovel",
            default=self._build.getBool("filter.includeNovel")
        )
        self.filterOpt.addItem(
            self.mainTheme.getIcon("proj_note"),
            self._build.getLabel("filter.includeNotes"),
            "doc:filter.includeNotes",
            default=self._build.getBool("filter.includeNotes")
        )
        self.filterOpt.addItem(
            self.mainTheme.getIcon("unchecked"),
            self._build.getLabel("filter.includeInactive"),
            "doc:filter.includeInactive",
            default=self._build.getBool("filter.includeInactive")
        )

        self.filterOpt.addSeparator()

        # Root Classes
        self.filterOpt.addLabel(self.tr("Root Folders"))
        for tHandle, nwItem in self.theProject.tree.iterRoots(None):
            if not nwItem.isInactiveClass():
                itemIcon = self.mainTheme.getItemIcon(
                    nwItem.itemType, nwItem.itemClass, nwItem.itemLayout
                )
                self.filterOpt.addItem(itemIcon, nwItem.itemName, f"root:{tHandle}", default=True)

        return

    def _setSelectedMode(self, mode: int):
        """Set the mode for the selected items.
        """
        for item in self.optTree.selectedItems():
            if not isinstance(item, QTreeWidgetItem):
                continue

            tHandle = item.data(self.C_DATA, self.D_HANDLE)
            isFile = item.data(self.C_DATA, self.D_FILE)
            if isFile:
                if mode == self.F_FILTERED:
                    self._build.setFiltered(tHandle)
                elif mode == self.F_INCLUDED:
                    self._build.setIncluded(tHandle)
                elif mode == self.F_EXCLUDED:
                    self._build.setExcluded(tHandle)

        self._setTreeItemMode()

        return

    def _setTreeItemMode(self):
        """Update the filtered mode icon on all items.
        """
        filtered = self._build.buildItemFilter(self.theProject)
        for tHandle, item in self._treeMap.items():
            allow, mode = filtered.get(tHandle, (False, FilterMode.UNKNOWN))
            if mode == FilterMode.INCLUDED:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_INCLUDED][1])
            elif mode == FilterMode.EXCLUDED:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_EXCLUDED][1])
            elif mode == FilterMode.FILTERED and allow:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_FILTERED][1])
            else:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_NONE][1])
        return

# END Class GuiBuildFilterTab


class GuiBuildHeadingsTab(QWidget):

    EDIT_TITLE   = 1
    EDIT_CHAPTER = 2
    EDIT_UNNUM   = 3
    EDIT_SCENE   = 4
    EDIT_SECTION = 5

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings):
        super().__init__(parent=buildMain)

        self.mainGui    = buildMain.mainGui
        self.mainTheme  = buildMain.mainGui.mainTheme
        self.theProject = buildMain.mainGui.theProject

        self._build = build
        self._editing = 0

        iPx = self.mainTheme.baseIconSize
        vSp = CONFIG.pxInt(12)
        bSp = CONFIG.pxInt(6)

        # Format Boxes
        # ============
        self.formatBox = QGridLayout()
        self.formatBox.setHorizontalSpacing(vSp)

        # Title Heading
        self.lblTitle = QLabel(BuildSettings.getLabel("headings.fmtTitle"))
        self.fmtTitle = QLineEdit("")
        self.fmtTitle.setEnabled(False)
        self.btnTitle = QToolButton()
        self.btnTitle.setIcon(self.mainTheme.getIcon("edit"))
        self.btnTitle.clicked.connect(lambda: self._editHeading(self.EDIT_TITLE))

        wrapTitle = QHBoxLayout()
        wrapTitle.addWidget(self.fmtTitle)
        wrapTitle.addWidget(self.btnTitle)
        wrapTitle.setSpacing(bSp)

        self.formatBox.addWidget(self.lblTitle, 0, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapTitle,     0, 1, Qt.AlignLeft)

        # Chapter Heading
        self.lblChapter = QLabel(BuildSettings.getLabel("headings.fmtChapter"))
        self.fmtChapter = QLineEdit("")
        self.fmtChapter.setEnabled(False)
        self.btnChapter = QToolButton()
        self.btnChapter.setIcon(self.mainTheme.getIcon("edit"))
        self.btnChapter.clicked.connect(lambda: self._editHeading(self.EDIT_CHAPTER))

        wrapChapter = QHBoxLayout()
        wrapChapter.addWidget(self.fmtChapter)
        wrapChapter.addWidget(self.btnChapter)
        wrapChapter.setSpacing(bSp)

        self.formatBox.addWidget(self.lblChapter, 1, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapChapter,     1, 1, Qt.AlignLeft)

        # Unnumbered Chapter Heading
        self.lblUnnumbered = QLabel(BuildSettings.getLabel("headings.fmtUnnumbered"))
        self.fmtUnnumbered = QLineEdit("")
        self.fmtUnnumbered.setEnabled(False)
        self.btnUnnumbered = QToolButton()
        self.btnUnnumbered.setIcon(self.mainTheme.getIcon("edit"))
        self.btnUnnumbered.clicked.connect(lambda: self._editHeading(self.EDIT_UNNUM))

        wrapUnnumbered = QHBoxLayout()
        wrapUnnumbered.addWidget(self.fmtUnnumbered)
        wrapUnnumbered.addWidget(self.btnUnnumbered)
        wrapUnnumbered.setSpacing(bSp)

        self.formatBox.addWidget(self.lblUnnumbered, 2, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapUnnumbered,     2, 1, Qt.AlignLeft)

        # Scene Heading
        self.lblScene = QLabel(BuildSettings.getLabel("headings.fmtScene"))
        self.fmtScene = QLineEdit("")
        self.fmtScene.setEnabled(False)
        self.btnScene = QToolButton()
        self.btnScene.setIcon(self.mainTheme.getIcon("edit"))
        self.btnScene.clicked.connect(lambda: self._editHeading(self.EDIT_SCENE))
        self.swtScene = NSwitch(width=2*iPx, height=iPx)
        self.swtScene.toggled.connect(self._hideScene)

        wrapScene = QHBoxLayout()
        wrapScene.addWidget(self.fmtScene)
        wrapScene.addWidget(self.btnScene)
        wrapScene.setSpacing(bSp)

        wrapSceneHide = QHBoxLayout()
        wrapSceneHide.addWidget(QLabel(self.tr("Hide")))
        wrapSceneHide.addWidget(self.swtScene)
        wrapSceneHide.setSpacing(bSp)

        self.formatBox.addWidget(self.lblScene, 3, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapScene,     3, 1, Qt.AlignLeft)
        self.formatBox.addLayout(wrapSceneHide, 3, 2, Qt.AlignLeft)

        # Section Heading
        self.lblSection = QLabel(BuildSettings.getLabel("headings.fmtSection"))
        self.fmtSection = QLineEdit("")
        self.fmtSection.setEnabled(False)
        self.btnSection = QToolButton()
        self.btnSection.setIcon(self.mainTheme.getIcon("edit"))
        self.btnSection.clicked.connect(lambda: self._editHeading(self.EDIT_SECTION))
        self.swtSection = NSwitch(width=2*iPx, height=iPx)
        self.swtSection.toggled.connect(self._hideSection)

        wrapSection = QHBoxLayout()
        wrapSection.addWidget(self.fmtSection)
        wrapSection.addWidget(self.btnSection)
        wrapSection.setSpacing(bSp)

        wrapSectionHide = QHBoxLayout()
        wrapSectionHide.addWidget(QLabel(self.tr("Hide")))
        wrapSectionHide.addWidget(self.swtSection)
        wrapSectionHide.setSpacing(bSp)

        self.formatBox.addWidget(self.lblSection, 4, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapSection,     4, 1, Qt.AlignLeft)
        self.formatBox.addLayout(wrapSectionHide, 4, 2, Qt.AlignLeft)

        # Edit Form
        # =========

        self.lblEditForm = QLabel(self.tr("Editing: {0}").format(self.tr("None")))

        self.editTextBox = QPlainTextEdit()
        self.editTextBox.setFixedHeight(5*iPx)
        self.editTextBox.setEnabled(False)

        self.formSyntax = GuiHeadingSyntax(self.editTextBox.document(), self.mainTheme)

        self.menuInsert = QMenu()
        self.aInsTitle = self.menuInsert.addAction(self.tr("Title"))
        self.aInsChNum = self.menuInsert.addAction(self.tr("Chapter Number"))
        self.aInsChWord = self.menuInsert.addAction(self.tr("Chapter Number (Word)"))
        self.aInsChRomU = self.menuInsert.addAction(self.tr("Chapter Number (Upper Case Roman)"))
        self.aInsChRomL = self.menuInsert.addAction(self.tr("Chapter Number (Lower Case Roman)"))
        self.aInsScNum = self.menuInsert.addAction(self.tr("Scene Number (In Chapter)"))
        self.aInsScAbs = self.menuInsert.addAction(self.tr("Scene Number (Absolute)"))

        self.aInsTitle.triggered.connect(lambda: self._insertIntoForm(nwHeadingFormats.TITLE))
        self.aInsChNum.triggered.connect(lambda: self._insertIntoForm(nwHeadingFormats.CH_NUM))
        self.aInsChWord.triggered.connect(lambda: self._insertIntoForm(nwHeadingFormats.CH_WORD))
        self.aInsChRomU.triggered.connect(lambda: self._insertIntoForm(nwHeadingFormats.CH_ROMU))
        self.aInsChRomL.triggered.connect(lambda: self._insertIntoForm(nwHeadingFormats.CH_ROML))
        self.aInsScNum.triggered.connect(lambda: self._insertIntoForm(nwHeadingFormats.SC_NUM))
        self.aInsScAbs.triggered.connect(lambda: self._insertIntoForm(nwHeadingFormats.SC_ABS))

        self.btnInsert = QPushButton(self.tr("Insert"))
        self.btnInsert.setMenu(self.menuInsert)

        self.btnApply = QPushButton(self.tr("Apply"))
        self.btnApply.clicked.connect(self._saveFormat)

        self.formButtonBox = QHBoxLayout()
        self.formButtonBox.addStretch(1)
        self.formButtonBox.addWidget(self.btnInsert)
        self.formButtonBox.addWidget(self.btnApply)

        self.editFormBox = QVBoxLayout()
        self.editFormBox.addWidget(self.lblEditForm)
        self.editFormBox.addWidget(self.editTextBox)
        self.editFormBox.addLayout(self.formButtonBox)

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.formatBox)
        self.outerBox.addSpacing(CONFIG.pxInt(16))
        self.outerBox.addLayout(self.editFormBox)
        self.outerBox.addStretch(1)

        self.setLayout(self.outerBox)

        return

    def loadContent(self):
        """Populate the widgets.
        """
        self.fmtTitle.setText(self._build.getStr("headings.fmtTitle"))
        self.fmtChapter.setText(self._build.getStr("headings.fmtChapter"))
        self.fmtUnnumbered.setText(self._build.getStr("headings.fmtUnnumbered"))
        self.fmtScene.setText(self._build.getStr("headings.fmtScene"))
        self.fmtSection.setText(self._build.getStr("headings.fmtSection"))
        self.swtScene.setChecked(self._build.getBool("headings.hideScene"))
        self.swtSection.setChecked(self._build.getBool("headings.hideSection"))
        return

    ##
    #  Internal Functions
    ##

    def _insertIntoForm(self, text: str):
        """Insert formatting text from the dropdown menu.
        """
        if self._editing > 0:
            cursor = self.editTextBox.textCursor()
            cursor.insertText(text)
            self.editTextBox.setFocus()
        return

    def _editHeading(self, heading: int):
        """Populate the form with a specific heading format.
        """
        self._editing = heading
        self.editTextBox.setEnabled(True)
        if heading == self.EDIT_TITLE:
            text = self.fmtTitle.text()
            label = self._build.getLabel("headings.fmtTitle")
        elif heading == self.EDIT_CHAPTER:
            text = self.fmtChapter.text()
            label = self._build.getLabel("headings.fmtChapter")
        elif heading == self.EDIT_UNNUM:
            text = self.fmtUnnumbered.text()
            label = self._build.getLabel("headings.fmtUnnumbered")
        elif heading == self.EDIT_SCENE:
            text = self.fmtScene.text()
            label = self._build.getLabel("headings.fmtScene")
        elif heading == self.EDIT_SECTION:
            text = self.fmtSection.text()
            label = self._build.getLabel("headings.fmtSection")
        else:
            self._editing = 0
            self.editTextBox.setEnabled(False)
            text = ""
            label = self.tr("None")

        self.editTextBox.setPlainText(text.replace("//", "\n"))
        self.lblEditForm.setText(self.tr("Editing: {0}").format(label))

        return

    ##
    #  Private Slots
    ##

    def _saveFormat(self):
        """Save the format from the edit text box.
        """
        heading = self._editing
        text = self.editTextBox.toPlainText().replace("\n", "//")
        if heading == self.EDIT_TITLE:
            self.fmtTitle.setText(text)
            self._build.setValue("headings.fmtTitle", text)
        elif heading == self.EDIT_CHAPTER:
            self.fmtChapter.setText(text)
            self._build.setValue("headings.fmtChapter", text)
        elif heading == self.EDIT_UNNUM:
            self.fmtUnnumbered.setText(text)
            self._build.setValue("headings.fmtUnnumbered", text)
        elif heading == self.EDIT_SCENE:
            self.fmtScene.setText(text)
            self._build.setValue("headings.fmtScene", text)
        elif heading == self.EDIT_SECTION:
            self.fmtSection.setText(text)
            self._build.setValue("headings.fmtSection", text)
        else:
            return

        self._editHeading(0)
        self.editTextBox.clear()

        return

    @pyqtSlot(bool)
    def _hideScene(self, status):
        """Hide scene heading
        """
        self._build.setValue("headings.hideScene", status)
        return

    @pyqtSlot(bool)
    def _hideSection(self, status):
        """Hide section heading
        """
        self._build.setValue("headings.hideSection", status)
        return

# END Class GuiBuildHeadingsTab


class GuiBuildFormatTab(QWidget):

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings):
        super().__init__(parent=buildMain)

        self._build = build

        return

# END Class GuiBuildFormatTab


class GuiBuildContentTab(QWidget):

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings):
        super().__init__(parent=buildMain)

        self._build = build

        return

# END Class GuiBuildContentTab


class GuiBuildOutputTab(QWidget):

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings):
        super().__init__(parent=buildMain)

        self._build = build

        return

# END Class GuiBuildOutputTab


class GuiHeadingSyntax(QSyntaxHighlighter):

    def __init__(self, document: QTextDocument, mainTheme: GuiTheme):
        super().__init__(document)

        self._valid = [
            nwHeadingFormats.TITLE.lower(),
            nwHeadingFormats.CH_NUM.lower(),
            nwHeadingFormats.CH_WORD.lower(),
            nwHeadingFormats.CH_ROMU.lower(),
            nwHeadingFormats.CH_ROML.lower(),
            nwHeadingFormats.SC_NUM.lower(),
            nwHeadingFormats.SC_ABS.lower(),
        ]

        self._fmtSymbol = QTextCharFormat()
        self._fmtSymbol.setForeground(QColor(*mainTheme.colHead))

        self._fmtFormat = QTextCharFormat()
        self._fmtFormat.setForeground(QColor(*mainTheme.colEmph))

        return

    def highlightBlock(self, text: str):
        """Add syntax highlighting to the text block.
        """
        check = text.lower()
        for heading in self._valid:
            pos = check.find(heading)
            if pos >= 0:
                chars = len(heading)
                self.setFormat(pos, chars, self._fmtSymbol)
                self.setFormat(pos + 1, chars - 2, self._fmtFormat)
                ddots = heading.find(":")
                if ddots > 0:
                    self.setFormat(pos + ddots, 1, self._fmtSymbol)
        return

# END Class GuiHeadingSyntax
