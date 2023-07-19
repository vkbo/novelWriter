"""
novelWriter – GUI Build Settings
================================

File History:
Created: 2023-02-13 [2.1b1] GuiBuildSettings

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

from PyQt5.QtGui import (
    QColor, QFont, QIcon, QSyntaxHighlighter, QTextCharFormat, QTextDocument
)
from PyQt5.QtCore import QEvent, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractButton, QAbstractItemView, QComboBox, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFontDialog, QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMenu, QPlainTextEdit, QPushButton, QSpinBox, QSplitter,
    QStackedWidget, QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget
)

from novelwriter import CONFIG
from novelwriter.constants import nwHeadFmt, nwLabels, trConst
from novelwriter.core.buildsettings import BuildSettings, FilterMode
from novelwriter.extensions.switch import NSwitch
from novelwriter.extensions.switchbox import NSwitchBox
from novelwriter.extensions.configlayout import NConfigLayout, NSimpleLayout
from novelwriter.extensions.pagedsidebar import NPagedSideBar

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain
    from novelwriter.gui.theme import GuiTheme

logger = logging.getLogger(__name__)


class GuiBuildSettings(QDialog):
    """GUI Tools: Manuscript Build Settings Dialog

    The main tool for configuring manuscript builds. It's a GUI tool for
    editing JSON build definitions, wrapped as a BuildSettings object.
    """

    OPT_FILTERS  = 1
    OPT_HEADINGS = 2
    OPT_CONTENT  = 3
    OPT_FORMAT   = 4
    OPT_OUTPUT   = 5

    newSettingsReady = pyqtSignal(BuildSettings)

    def __init__(self, parent: QWidget, mainGui: GuiMain, build: BuildSettings):
        super().__init__(parent=parent)

        logger.debug("Create: GuiBuildSettings")
        self.setObjectName("GuiBuildSettings")

        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self._build = build

        self.setWindowTitle(self.tr("Manuscript Build Settings"))
        self.setMinimumWidth(CONFIG.pxInt(700))
        self.setMinimumHeight(CONFIG.pxInt(400))

        mPx = CONFIG.pxInt(150)
        wWin = CONFIG.pxInt(750)
        hWin = CONFIG.pxInt(550)

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
        self.optSideBar.addButton(self.tr("Content"), self.OPT_CONTENT)
        self.optSideBar.addButton(self.tr("Format"), self.OPT_FORMAT)
        self.optSideBar.addButton(self.tr("Output"), self.OPT_OUTPUT)

        self.optSideBar.buttonClicked.connect(self._stackPageSelected)

        # Options Area
        # ============

        # Create Tabs
        self.optTabSelect = _FilterTab(self, self._build)
        self.optTabHeadings = _HeadingsTab(self, self._build)
        self.optTabContent = _ContentTab(self, self._build)
        self.optTabFormat = _FormatTab(self, self._build)
        self.optTabOutput = _OutputTab(self, self._build)

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

        logger.debug("Ready: GuiBuildSettings")

        return

    def __del__(self):  # pragma: no cover
        logger.debug("Delete: GuiBuildSettings")

    def loadContent(self):
        """Populate the child widgets."""
        self.editBuildName.setText(self._build.name)
        self.optTabSelect.loadContent()
        self.optTabHeadings.loadContent()
        self.optTabContent.loadContent()
        self.optTabFormat.loadContent()
        self.optTabOutput.loadContent()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _stackPageSelected(self, pageId: int):
        """Process a user request to switch page."""
        if pageId == self.OPT_FILTERS:
            self.toolStack.setCurrentWidget(self.optTabSelect)
        elif pageId == self.OPT_HEADINGS:
            self.toolStack.setCurrentWidget(self.optTabHeadings)
        elif pageId == self.OPT_CONTENT:
            self.toolStack.setCurrentWidget(self.optTabContent)
        elif pageId == self.OPT_FORMAT:
            self.toolStack.setCurrentWidget(self.optTabFormat)
        elif pageId == self.OPT_OUTPUT:
            self.toolStack.setCurrentWidget(self.optTabOutput)
        return

    @pyqtSlot("QAbstractButton*")
    def _dialogButtonClicked(self, button: QAbstractButton):
        """Handle button clicks from the dialog button box."""
        role = self.dlgButtons.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self._emitBuildData()
        elif role == QDialogButtonBox.AcceptRole:
            self._emitBuildData()
            self.close()
        elif role == QDialogButtonBox.RejectRole:
            self.close()
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QEvent):
        """Capture the user closing the window so we can save
        settings.
        """
        logger.debug("Closing: GuiBuildSettings")
        self._askToSaveBuild()
        self._saveSettings()
        event.accept()
        self.deleteLater()
        return

    ##
    #  Internal Functions
    ##

    def _askToSaveBuild(self):
        """Check if there are unsaved changes, and if there are, ask if
        it's ok to reject them.
        """
        if self._build.changed:
            doSave = self.mainGui.askQuestion(
                self.tr("Build Settings"),
                self.tr("Do you want to save your changes?")
            )
            if doSave:
                self._emitBuildData()
            self._build.resetChangedState()
        return

    def _saveSettings(self):
        """Save the various user settings."""
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

    def _emitBuildData(self):
        """Assemble the build data and emit the signal."""
        self._build.setName(self.editBuildName.text())
        self.optTabHeadings.saveContent()
        self.optTabContent.saveContent()
        self.optTabFormat.saveContent()
        self.optTabOutput.saveContent()
        self.newSettingsReady.emit(self._build)
        self._build.resetChangedState()
        return

# END Class GuiBuildSettings


class _FilterTab(QWidget):

    C_DATA   = 0
    C_NAME   = 0
    C_ACTIVE = 1
    C_STATUS = 2

    D_HANDLE = Qt.ItemDataRole.UserRole
    D_FILE   = Qt.ItemDataRole.UserRole + 1

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

        self.filteredButton = QToolButton(self)
        self.filteredButton.setToolTip(self._statusFlags[self.F_FILTERED][0])
        self.filteredButton.setIcon(self._statusFlags[self.F_FILTERED][1])
        self.filteredButton.clicked.connect(lambda: self._setSelectedMode(self.F_FILTERED))

        self.includedButton = QToolButton(self)
        self.includedButton.setToolTip(self._statusFlags[self.F_INCLUDED][0])
        self.includedButton.setIcon(self._statusFlags[self.F_INCLUDED][1])
        self.includedButton.clicked.connect(lambda: self._setSelectedMode(self.F_INCLUDED))

        self.excludedButton = QToolButton(self)
        self.excludedButton.setToolTip(self._statusFlags[self.F_EXCLUDED][0])
        self.excludedButton.setIcon(self._statusFlags[self.F_EXCLUDED][1])
        self.excludedButton.clicked.connect(lambda: self._setSelectedMode(self.F_EXCLUDED))

        self.modeBox = QHBoxLayout()
        self.modeBox.addWidget(QLabel(self.tr("Mark selection as")))
        self.modeBox.addStretch(1)
        self.modeBox.addWidget(self.filteredButton)
        self.modeBox.addWidget(self.includedButton)
        self.modeBox.addWidget(self.excludedButton)

        # Filer Options
        self.filterOpt = NSwitchBox(self, iPx)
        self.filterOpt.switchToggled.connect(self._applyFilterSwitch)
        self.filterOpt.setFrameStyle(QFrame.NoFrame)

        # Assemble GUI
        # ============

        pOptions = self.theProject.options

        self.selectionBox = QVBoxLayout()
        self.selectionBox.addWidget(self.optTree)
        self.selectionBox.addLayout(self.modeBox)
        self.selectionBox.setContentsMargins(0, 0, 0, 0)

        self.selectionWidget = QWidget()
        self.selectionWidget.setLayout(self.selectionBox)

        self.mainSplit = QSplitter()
        self.mainSplit.addWidget(self.selectionWidget)
        self.mainSplit.addWidget(self.filterOpt)
        self.mainSplit.setCollapsible(0, False)
        self.mainSplit.setCollapsible(1, False)
        self.mainSplit.setStretchFactor(0, 0)
        self.mainSplit.setStretchFactor(1, 1)
        self.mainSplit.setSizes([
            CONFIG.pxInt(pOptions.getInt("GuiBuildSettings", "treeWidth", 1)),
            CONFIG.pxInt(pOptions.getInt("GuiBuildSettings", "filterWidth", 1))
        ])

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.mainSplit)
        self.outerBox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.outerBox)

        return

    def loadContent(self):
        """Populate the widgets."""
        self._populateTree()
        self._populateFilters()
        return

    def mainSplitSizes(self) -> tuple[int, int]:
        """Extract the sizes of the main splitter."""
        sizes = self.mainSplit.sizes()
        m, n = (sizes[0], sizes[1]) if len(sizes) >= 2 else (0, 0)
        return CONFIG.rpxInt(m), CONFIG.rpxInt(n)

    ##
    #  Slots
    ##

    @pyqtSlot(str, bool)
    def _applyFilterSwitch(self, key: str, state: bool):
        """Apply filter switch and update the settings."""
        if key.startswith("doc:"):
            self._build.setValue(key[4:], state)
            self._setTreeItemMode()
        elif key.startswith("root:"):
            self._build.setAllowRoot(key[5:], state)
            self._populateTree()
        return

    ##
    #  Internal Functions
    ##

    def _populateTree(self):
        """Build the tree of project items."""
        logger.debug("Building project tree")
        self._treeMap = {}
        self.optTree.clear()
        for nwItem in self.theProject.getProjectItems():

            tHandle = nwItem.itemHandle
            pHandle = nwItem.itemParent
            rHandle = nwItem.itemRoot

            if tHandle is None or rHandle is None:
                continue

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

            if pHandle is None and nwItem.isRootType():
                self.optTree.addTopLevelItem(trItem)
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
        """Populate the filter options switches."""
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
                self.filterOpt.addItem(
                    itemIcon, nwItem.itemName, f"root:{tHandle}",
                    default=self._build.isRootAllowed(tHandle)
                )

        return

    def _setSelectedMode(self, mode: int):
        """Set the mode for the selected items."""
        for item in self.optTree.selectedItems():
            if isinstance(item, QTreeWidgetItem):
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
        """Update the filtered mode icon on all items."""
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

# END Class _FilterTab


class _HeadingsTab(QWidget):

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
        self.lblTitle = QLabel(self._build.getLabel("headings.fmtTitle"))
        self.fmtTitle = QLineEdit("")
        self.fmtTitle.setReadOnly(True)
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
        self.lblChapter = QLabel(self._build.getLabel("headings.fmtChapter"))
        self.fmtChapter = QLineEdit("")
        self.fmtChapter.setReadOnly(True)
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
        self.lblUnnumbered = QLabel(self._build.getLabel("headings.fmtUnnumbered"))
        self.fmtUnnumbered = QLineEdit("")
        self.fmtUnnumbered.setReadOnly(True)
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
        sceneHideTip = self._build.getLabel("headings.hideScene")
        self.lblScene = QLabel(self._build.getLabel("headings.fmtScene"))
        self.fmtScene = QLineEdit("")
        self.fmtScene.setReadOnly(True)
        self.btnScene = QToolButton()
        self.btnScene.setIcon(self.mainTheme.getIcon("edit"))
        self.btnScene.clicked.connect(lambda: self._editHeading(self.EDIT_SCENE))
        self.hdeScene = QLabel(self.tr("Hide"))
        self.hdeScene.setToolTip(sceneHideTip)
        self.swtScene = NSwitch(self, width=2*iPx, height=iPx)
        self.swtScene.setToolTip(sceneHideTip)

        wrapScene = QHBoxLayout()
        wrapScene.addWidget(self.fmtScene)
        wrapScene.addWidget(self.btnScene)
        wrapScene.setSpacing(bSp)

        wrapSceneHide = QHBoxLayout()
        wrapSceneHide.addWidget(self.hdeScene)
        wrapSceneHide.addWidget(self.swtScene)
        wrapSceneHide.setSpacing(bSp)

        self.formatBox.addWidget(self.lblScene, 3, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapScene,     3, 1, Qt.AlignLeft)
        self.formatBox.addLayout(wrapSceneHide, 3, 2, Qt.AlignLeft)

        # Section Heading
        sectionHideTip = self._build.getLabel("headings.hideSection")
        self.lblSection = QLabel(self._build.getLabel("headings.fmtSection"))
        self.fmtSection = QLineEdit("")
        self.fmtSection.setReadOnly(True)
        self.btnSection = QToolButton()
        self.btnSection.setIcon(self.mainTheme.getIcon("edit"))
        self.btnSection.clicked.connect(lambda: self._editHeading(self.EDIT_SECTION))
        self.hdeSection = QLabel(self.tr("Hide"))
        self.hdeSection.setToolTip(sectionHideTip)
        self.swtSection = NSwitch(self, width=2*iPx, height=iPx)
        self.swtSection.setToolTip(sectionHideTip)

        wrapSection = QHBoxLayout()
        wrapSection.addWidget(self.fmtSection)
        wrapSection.addWidget(self.btnSection)
        wrapSection.setSpacing(bSp)

        wrapSectionHide = QHBoxLayout()
        wrapSectionHide.addWidget(self.hdeSection)
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

        self.formSyntax = _HeadingSyntaxHighlighter(self.editTextBox.document(), self.mainTheme)

        self.menuInsert = QMenu()
        self.aInsTitle = self.menuInsert.addAction(self.tr("Title"))
        self.aInsChNum = self.menuInsert.addAction(self.tr("Chapter Number"))
        self.aInsChWord = self.menuInsert.addAction(self.tr("Chapter Number (Word)"))
        self.aInsChRomU = self.menuInsert.addAction(self.tr("Chapter Number (Upper Case Roman)"))
        self.aInsChRomL = self.menuInsert.addAction(self.tr("Chapter Number (Lower Case Roman)"))
        self.aInsScNum = self.menuInsert.addAction(self.tr("Scene Number (In Chapter)"))
        self.aInsScAbs = self.menuInsert.addAction(self.tr("Scene Number (Absolute)"))

        self.aInsTitle.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.TITLE))
        self.aInsChNum.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.CH_NUM))
        self.aInsChWord.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.CH_WORD))
        self.aInsChRomU.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.CH_ROMU))
        self.aInsChRomL.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.CH_ROML))
        self.aInsScNum.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.SC_NUM))
        self.aInsScAbs.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.SC_ABS))

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
        """Populate the widgets."""
        self.fmtTitle.setText(self._build.getStr("headings.fmtTitle"))
        self.fmtChapter.setText(self._build.getStr("headings.fmtChapter"))
        self.fmtUnnumbered.setText(self._build.getStr("headings.fmtUnnumbered"))
        self.fmtScene.setText(self._build.getStr("headings.fmtScene"))
        self.fmtSection.setText(self._build.getStr("headings.fmtSection"))
        self.swtScene.setChecked(self._build.getBool("headings.hideScene"))
        self.swtSection.setChecked(self._build.getBool("headings.hideSection"))
        return

    def saveContent(self):
        """Save choices back into build object."""
        self._build.setValue("headings.hideScene", self.swtScene.isChecked())
        self._build.setValue("headings.hideSection", self.swtSection.isChecked())
        return

    ##
    #  Internal Functions
    ##

    def _insertIntoForm(self, text: str):
        """Insert formatting text from the dropdown menu."""
        if self._editing > 0:
            cursor = self.editTextBox.textCursor()
            cursor.insertText(text)
            self.editTextBox.setFocus()
        return

    def _editHeading(self, heading: int):
        """Populate the form with a specific heading format."""
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
        """Save the format from the edit text box."""
        heading = self._editing
        text = self.editTextBox.toPlainText().strip().replace("\n", "//")
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

# END Class _HeadingsTab


class _HeadingSyntaxHighlighter(QSyntaxHighlighter):

    def __init__(self, document: QTextDocument, mainTheme: GuiTheme):
        super().__init__(document)
        self._fmtSymbol = QTextCharFormat()
        self._fmtSymbol.setForeground(QColor(*mainTheme.colHead))
        self._fmtFormat = QTextCharFormat()
        self._fmtFormat.setForeground(QColor(*mainTheme.colEmph))
        return

    def highlightBlock(self, text: str):
        """Add syntax highlighting to the text block."""
        for heading in nwHeadFmt.ALL:
            pos = text.find(heading)
            if pos >= 0:
                chars = len(heading)
                self.setFormat(pos, chars, self._fmtSymbol)
                self.setFormat(pos + 1, chars - 2, self._fmtFormat)
                ddots = heading.find(":")
                if ddots > 0:
                    self.setFormat(pos + ddots, 1, self._fmtSymbol)
        return

# END Class _HeadingSyntaxHighlighter


class _ContentTab(QWidget):

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings):
        super().__init__(parent=buildMain)

        self.mainGui    = buildMain.mainGui
        self.mainTheme  = buildMain.mainGui.mainTheme

        self._build = build

        iPx = self.mainTheme.baseIconSize

        # Left Form
        # =========

        self.formLeft = NSimpleLayout()
        self.formLeft.addGroupLabel(self._build.getLabel("text.grpContent"))

        self.incSynopsis = NSwitch(self, width=2*iPx, height=iPx)
        self.incComments = NSwitch(self, width=2*iPx, height=iPx)
        self.incKeywords = NSwitch(self, width=2*iPx, height=iPx)
        self.incBodyText = NSwitch(self, width=2*iPx, height=iPx)

        self.formLeft.addRow(self._build.getLabel("text.includeSynopsis"), self.incSynopsis)
        self.formLeft.addRow(self._build.getLabel("text.includeComments"), self.incComments)
        self.formLeft.addRow(self._build.getLabel("text.includeKeywords"), self.incKeywords)
        self.formLeft.addRow(self._build.getLabel("text.includeBodyText"), self.incBodyText)

        # Right Form
        # ==========

        self.formRight = NSimpleLayout()
        self.formRight.addGroupLabel(self._build.getLabel("text.grpInsert"))

        self.addNoteHead = NSwitch(self, width=2*iPx, height=iPx)

        self.formRight.addRow(self._build.getLabel("text.addNoteHeadings"), self.addNoteHead)

        # Assemble GUI
        # ============

        self.outerBox = QHBoxLayout()
        self.outerBox.addLayout(self.formLeft, 1)
        self.outerBox.addLayout(self.formRight, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(CONFIG.pxInt(16))

        self.setLayout(self.outerBox)

        return

    def loadContent(self):
        """Populate the widgets."""
        self.incSynopsis.setChecked(self._build.getBool("text.includeSynopsis"))
        self.incComments.setChecked(self._build.getBool("text.includeComments"))
        self.incKeywords.setChecked(self._build.getBool("text.includeKeywords"))
        self.incBodyText.setChecked(self._build.getBool("text.includeBodyText"))
        self.addNoteHead.setChecked(self._build.getBool("text.addNoteHeadings"))
        return

    def saveContent(self):
        """Save choices back into build object."""
        self._build.setValue("text.includeSynopsis", self.incSynopsis.isChecked())
        self._build.setValue("text.includeComments", self.incComments.isChecked())
        self._build.setValue("text.includeKeywords", self.incKeywords.isChecked())
        self._build.setValue("text.includeBodyText", self.incBodyText.isChecked())
        self._build.setValue("text.addNoteHeadings", self.addNoteHead.isChecked())
        return

# END Class _ContentTab


class _FormatTab(QWidget):

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings):
        super().__init__(parent=buildMain)

        self.mainGui    = buildMain.mainGui
        self.mainTheme  = buildMain.mainGui.mainTheme

        self._build = build
        self._unitScale = 1.0

        iPx = self.mainTheme.baseIconSize
        spW = 6*self.mainTheme.textNWidth
        dbW = 8*self.mainTheme.textNWidth

        # Text Format Form
        # ================

        self.formFormat = NConfigLayout()
        self.formFormat.addGroupLabel(self._build.getLabel("format.grpFormat"))

        # Build Language
        self.buildLang = QComboBox()
        langauges = CONFIG.listLanguages(CONFIG.LANG_PROJ)
        self.buildLang.addItem("[%s]" % self.tr("Not Set"), "None")
        for langID, langName in langauges:
            self.buildLang.addItem(langName, langID)

        self.formFormat.addRow(self._build.getLabel("format.buildLang"), self.buildLang)

        # Font Family
        self.textFont = QLineEdit()
        self.textFont.setReadOnly(True)
        self.btnTextFont = QPushButton("...")
        self.btnTextFont.setMaximumWidth(int(2.5*self.mainTheme.getTextWidth("...")))
        self.btnTextFont.clicked.connect(self._selectFont)
        self.formFormat.addRow(
            self._build.getLabel("format.textFont"), self.textFont, button=self.btnTextFont
        )

        # Font Size
        self.textSize = QSpinBox(self)
        self.textSize.setMinimum(8)
        self.textSize.setMaximum(60)
        self.textSize.setSingleStep(1)
        self.textSize.setMinimumWidth(spW)
        self.formFormat.addRow(
            self._build.getLabel("format.textSize"), self.textSize, unit="pt"
        )

        # Line Height
        self.lineHeight = QDoubleSpinBox(self)
        self.lineHeight.setFixedWidth(spW)
        self.lineHeight.setMinimum(0.75)
        self.lineHeight.setMaximum(3.0)
        self.lineHeight.setSingleStep(0.05)
        self.lineHeight.setDecimals(2)
        self.formFormat.addRow(
            self._build.getLabel("format.lineHeight"), self.lineHeight, unit="em"
        )

        # Text Options Form
        # =================

        self.formOptions = NSimpleLayout()
        self.formOptions.addGroupLabel(self._build.getLabel("format.grpOptions"))
        self.formOptions.setContentsMargins(0, 0, 0, 0)

        self.justifyText = NSwitch(self, width=2*iPx, height=iPx)
        self.stripUnicode = NSwitch(self, width=2*iPx, height=iPx)
        self.replaceTabs = NSwitch(self, width=2*iPx, height=iPx)

        self.formOptions.addRow(self._build.getLabel("format.justifyText"), self.justifyText)
        self.formOptions.addRow(self._build.getLabel("format.stripUnicode"), self.stripUnicode)
        self.formOptions.addRow(self._build.getLabel("format.replaceTabs"), self.replaceTabs)

        # Page Layout Form
        # ================

        self.formLayout = NSimpleLayout()
        self.formLayout.addGroupLabel(self._build.getLabel("format.grpPage"))
        self.formLayout.setContentsMargins(0, 0, 0, 0)

        self.pageUnit = QComboBox(self)
        for key, name in nwLabels.UNIT_NAME.items():
            self.pageUnit.addItem(trConst(name), key)

        self.pageSize = QComboBox(self)
        for key, name in nwLabels.PAPER_NAME.items():
            self.pageSize.addItem(trConst(name), key)

        self.pageWidth = QDoubleSpinBox(self)
        self.pageWidth.setFixedWidth(dbW)
        self.pageWidth.setMaximum(500.0)

        self.pageHeight = QDoubleSpinBox(self)
        self.pageHeight.setFixedWidth(dbW)
        self.pageHeight.setMaximum(500.0)

        self.topMargin = QDoubleSpinBox(self)
        self.topMargin.setFixedWidth(dbW)

        self.bottomMargin = QDoubleSpinBox(self)
        self.bottomMargin.setFixedWidth(dbW)

        self.leftMargin = QDoubleSpinBox(self)
        self.leftMargin.setFixedWidth(dbW)

        self.rightMargin = QDoubleSpinBox(self)
        self.rightMargin.setFixedWidth(dbW)

        self.formLayout.addRow(self._build.getLabel("format.pageUnit"), self.pageUnit)
        self.formLayout.addRow(self._build.getLabel("format.pageSize"), self.pageSize)
        self.formLayout.addRow(self._build.getLabel("format.pageWidth"), self.pageWidth)
        self.formLayout.addRow(self._build.getLabel("format.pageHeight"), self.pageHeight)
        self.formLayout.addRow(self._build.getLabel("format.topMargin"), self.topMargin)
        self.formLayout.addRow(self._build.getLabel("format.bottomMargin"), self.bottomMargin)
        self.formLayout.addRow(self._build.getLabel("format.leftMargin"), self.leftMargin)
        self.formLayout.addRow(self._build.getLabel("format.rightMargin"), self.rightMargin)

        # Assemble GUI
        # ============

        self.formLeft = QVBoxLayout()
        self.formLeft.addLayout(self.formFormat)
        self.formLeft.addLayout(self.formOptions)
        self.formLeft.addStretch(1)
        self.formLeft.setContentsMargins(0, 0, 0, 0)
        self.formLeft.setSpacing(CONFIG.pxInt(8))

        self.formRight = QVBoxLayout()
        self.formRight.addLayout(self.formLayout)
        self.formRight.addStretch(1)
        self.formRight.setContentsMargins(0, 0, 0, 0)
        self.formRight.setSpacing(CONFIG.pxInt(8))

        self.outerBox = QHBoxLayout()
        self.outerBox.addLayout(self.formLeft, 1)
        self.outerBox.addLayout(self.formRight, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(CONFIG.pxInt(16))

        self.setLayout(self.outerBox)

        return

    def loadContent(self):
        """Populate the widgets."""
        langIdx = self.buildLang.findData(self._build.getStr("format.buildLang"))
        if langIdx != -1:
            self.buildLang.setCurrentIndex(langIdx)

        textFont = self._build.getStr("format.textFont")
        if not textFont:
            textFont = str(CONFIG.textFont)

        self.textFont.setText(textFont)
        self.textSize.setValue(self._build.getInt("format.textSize"))
        self.lineHeight.setValue(self._build.getFloat("format.lineHeight"))

        self.justifyText.setChecked(self._build.getBool("format.justifyText"))
        self.stripUnicode.setChecked(self._build.getBool("format.stripUnicode"))
        self.replaceTabs.setChecked(self._build.getBool("format.replaceTabs"))

        pageUnit = self._build.getStr("format.pageUnit")
        index = self.pageUnit.findData(pageUnit)
        if index >= 0:
            self.pageUnit.setCurrentIndex(index)
            self._unitScale = nwLabels.UNIT_SCALE.get(pageUnit, 1.0)
            self._changeUnit(index)

        self.pageWidth.setValue(self._build.getFloat("format.pageWidth"))
        self.pageHeight.setValue(self._build.getFloat("format.pageHeight"))
        self.topMargin.setValue(self._build.getFloat("format.topMargin"))
        self.bottomMargin.setValue(self._build.getFloat("format.bottomMargin"))
        self.leftMargin.setValue(self._build.getFloat("format.leftMargin"))
        self.rightMargin.setValue(self._build.getFloat("format.rightMargin"))

        pageSize = self._build.getStr("format.pageSize")
        index = self.pageSize.findData(pageSize)
        if index >= 0:
            self.pageSize.setCurrentIndex(index)
            self._changePageSize(index)

        self.pageUnit.currentIndexChanged.connect(self._changeUnit)
        self.pageSize.currentIndexChanged.connect(self._changePageSize)

        return

    def saveContent(self):
        """Save choices back into build object."""
        self._build.setValue("format.buildLang", str(self.buildLang.currentData()))
        self._build.setValue("format.textFont", self.textFont.text())
        self._build.setValue("format.textSize", self.textSize.value())
        self._build.setValue("format.lineHeight", self.lineHeight.value())

        self._build.setValue("format.justifyText", self.justifyText.isChecked())
        self._build.setValue("format.stripUnicode", self.stripUnicode.isChecked())
        self._build.setValue("format.replaceTabs", self.replaceTabs.isChecked())

        self._build.setValue("format.pageUnit", str(self.pageUnit.currentData()))
        self._build.setValue("format.pageSize", str(self.pageSize.currentData()))
        self._build.setValue("format.pageWidth", self.pageWidth.value())
        self._build.setValue("format.pageHeight", self.pageHeight.value())
        self._build.setValue("format.topMargin", self.topMargin.value())
        self._build.setValue("format.bottomMargin", self.bottomMargin.value())
        self._build.setValue("format.leftMargin", self.leftMargin.value())
        self._build.setValue("format.rightMargin", self.rightMargin.value())
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _selectFont(self):
        """Open the QFontDialog and set a font for the font style."""
        currFont = QFont()
        currFont.setFamily(self.textFont.text())
        currFont.setPointSize(self.textSize.value())
        theFont, theStatus = QFontDialog.getFont(currFont, self)
        if theStatus:
            self.textFont.setText(theFont.family())
            self.textSize.setValue(theFont.pointSize())
        return

    @pyqtSlot(int)
    def _changeUnit(self, index: int):
        """The current unit change, so recalculate sizes."""
        newUnit = self.pageUnit.itemData(index)
        newScale = nwLabels.UNIT_SCALE.get(newUnit, 1.0)
        reScale = self._unitScale/newScale

        pageWidth = self.pageWidth.value() * reScale
        pageHeight = self.pageHeight.value() * reScale
        topMargin = self.topMargin.value() * reScale
        bottomMargin = self.bottomMargin.value() * reScale
        leftMargin = self.leftMargin.value() * reScale
        rightMargin = self.rightMargin.value() * reScale

        isMM = newUnit == "mm"
        nDec = 1 if isMM else 2
        nStep = 1.0 if isMM else 0.1
        pMax = 500.0 if isMM else 50.0
        mMax = 150.0 if isMM else 15.0

        self.pageWidth.setDecimals(nDec)
        self.pageWidth.setSingleStep(nStep)
        self.pageWidth.setMaximum(pMax)
        self.pageWidth.setValue(pageWidth)

        self.pageHeight.setDecimals(nDec)
        self.pageHeight.setSingleStep(nStep)
        self.pageHeight.setMaximum(pMax)
        self.pageHeight.setValue(pageHeight)

        self.topMargin.setDecimals(nDec)
        self.topMargin.setSingleStep(nStep)
        self.topMargin.setMaximum(mMax)
        self.topMargin.setValue(topMargin)

        self.bottomMargin.setDecimals(nDec)
        self.bottomMargin.setSingleStep(nStep)
        self.bottomMargin.setMaximum(mMax)
        self.bottomMargin.setValue(bottomMargin)

        self.leftMargin.setDecimals(nDec)
        self.leftMargin.setSingleStep(nStep)
        self.leftMargin.setMaximum(mMax)
        self.leftMargin.setValue(leftMargin)

        self.rightMargin.setDecimals(nDec)
        self.rightMargin.setSingleStep(nStep)
        self.rightMargin.setMaximum(mMax)
        self.rightMargin.setValue(rightMargin)

        self._unitScale = newScale

        return

    @pyqtSlot(int)
    def _changePageSize(self, index: int):
        """The page size has changed."""
        self.pageWidth.setEnabled(True)
        self.pageHeight.setEnabled(True)

        w, h = nwLabels.PAPER_SIZE[self.pageSize.itemData(index)] if index >= 0 else (-1.0, -1.0)
        if w > 0.0 and h > 0.0:
            self.pageWidth.setEnabled(False)
            self.pageHeight.setEnabled(False)
            self.pageWidth.setValue(w/self._unitScale)
            self.pageHeight.setValue(h/self._unitScale)

        return

# END Class _FormatTab


class _OutputTab(QWidget):

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings):
        super().__init__(parent=buildMain)

        self.mainGui    = buildMain.mainGui
        self.mainTheme  = buildMain.mainGui.mainTheme

        self._build = build

        iPx = self.mainTheme.baseIconSize

        # Left Form
        # =========

        self.formLeft = NSimpleLayout()
        self.formLeft.addGroupLabel(self._build.getLabel("odt"))

        self.odtAddColours = NSwitch(self, width=2*iPx, height=iPx)

        self.formLeft.addRow(self._build.getLabel("odt.addColours"), self.odtAddColours)

        # Right Form
        # ==========

        self.formRight = NSimpleLayout()
        self.formRight.addGroupLabel(self._build.getLabel("html"))

        self.htmlAddStyles = NSwitch(self, width=2*iPx, height=iPx)

        self.formRight.addRow(self._build.getLabel("html.addStyles"), self.htmlAddStyles)

        # Assemble GUI
        # ============

        self.outerBox = QHBoxLayout()
        self.outerBox.addLayout(self.formLeft, 1)
        self.outerBox.addLayout(self.formRight, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(CONFIG.pxInt(16))

        self.setLayout(self.outerBox)

        return

    def loadContent(self):
        """Populate the widgets."""
        self.odtAddColours.setChecked(self._build.getBool("odt.addColours"))
        self.htmlAddStyles.setChecked(self._build.getBool("html.addStyles"))
        return

    def saveContent(self):
        """Save choices back into build object."""
        self._build.setValue("odt.addColours", self.odtAddColours.isChecked())
        self._build.setValue("html.addStyles", self.htmlAddStyles.isChecked())
        return

# END Class _OutputTab
