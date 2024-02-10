"""
novelWriter – GUI Build Settings
================================

File History:
Created: 2023-02-13 [2.1b1] GuiBuildSettings

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

from typing import TYPE_CHECKING

from PyQt5.QtGui import QFont, QIcon, QSyntaxHighlighter, QTextCharFormat, QTextDocument
from PyQt5.QtCore import QEvent, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractButton, QAbstractItemView, QDialog, QDialogButtonBox,
    QFontDialog, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMenu, QPlainTextEdit, QPushButton, QSplitter, QStackedWidget,
    QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.constants import nwHeadFmt, nwLabels, trConst
from novelwriter.core.buildsettings import BuildSettings, FilterMode
from novelwriter.extensions.switch import NSwitch
from novelwriter.extensions.modified import NComboBox, NDoubleSpinBox, NSpinBox
from novelwriter.extensions.switchbox import NSwitchBox
from novelwriter.extensions.configlayout import (
    NColourLabel, NFixedPage, NScrollableForm, NScrollablePage
)
from novelwriter.extensions.pagedsidebar import NPagedSideBar

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

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

    def __init__(self, mainGui: GuiMain, build: BuildSettings) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiBuildSettings")
        self.setObjectName("GuiBuildSettings")
        if CONFIG.osDarwin:
            self.setWindowFlag(Qt.WindowType.Tool)

        self._build = build

        self.setWindowTitle(self.tr("Manuscript Build Settings"))
        self.setMinimumSize(CONFIG.pxInt(700), CONFIG.pxInt(400))

        mPx = CONFIG.pxInt(150)
        wWin = CONFIG.pxInt(750)
        hWin = CONFIG.pxInt(550)

        options = SHARED.project.options
        self.resize(
            CONFIG.pxInt(options.getInt("GuiBuildSettings", "winWidth", wWin)),
            CONFIG.pxInt(options.getInt("GuiBuildSettings", "winHeight", hWin))
        )

        # Title
        self.titleLabel = NColourLabel(
            self.tr("Manuscript Build Settings"), SHARED.theme.helpText,
            parent=self, scale=NColourLabel.HEADER_SCALE, indent=CONFIG.pxInt(4)
        )

        # Settings Name
        self.lblBuildName = QLabel(self.tr("Name"))
        self.editBuildName = QLineEdit(self)

        # SideBar
        self.sidebar = NPagedSideBar(self)
        self.sidebar.setMinimumWidth(mPx)
        self.sidebar.setMaximumWidth(mPx)
        self.sidebar.setLabelColor(SHARED.theme.helpText)

        self.sidebar.addButton(self.tr("Selection"), self.OPT_FILTERS)
        self.sidebar.addButton(self.tr("Headings"), self.OPT_HEADINGS)
        self.sidebar.addButton(self.tr("Content"), self.OPT_CONTENT)
        self.sidebar.addButton(self.tr("Format"), self.OPT_FORMAT)
        self.sidebar.addButton(self.tr("Output"), self.OPT_OUTPUT)

        self.sidebar.buttonClicked.connect(self._stackPageSelected)

        # Content
        self.optTabSelect = _FilterTab(self, self._build)
        self.optTabHeadings = _HeadingsTab(self, self._build)
        self.optTabContent = _ContentTab(self, self._build)
        self.optTabFormat = _FormatTab(self, self._build)
        self.optTabOutput = _OutputTab(self, self._build)

        self.toolStack = QStackedWidget(self)
        self.toolStack.addWidget(self.optTabSelect)
        self.toolStack.addWidget(self.optTabHeadings)
        self.toolStack.addWidget(self.optTabFormat)
        self.toolStack.addWidget(self.optTabContent)
        self.toolStack.addWidget(self.optTabOutput)

        # Buttons
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply
            | QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Close
        )
        self.buttonBox.clicked.connect(self._dialogButtonClicked)

        # Assemble
        self.topBox = QHBoxLayout()
        self.topBox.addWidget(self.titleLabel)
        self.topBox.addStretch(1)
        self.topBox.addWidget(self.lblBuildName)
        self.topBox.addWidget(self.editBuildName, 1)

        self.mainBox = QHBoxLayout()
        self.mainBox.addWidget(self.sidebar)
        self.mainBox.addWidget(self.toolStack)
        self.mainBox.setContentsMargins(0, 0, 0, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.topBox)
        self.outerBox.addLayout(self.mainBox)
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(CONFIG.pxInt(12))

        self.setLayout(self.outerBox)

        # Set Default Tab
        self.sidebar.setSelected(self.OPT_FILTERS)

        logger.debug("Ready: GuiBuildSettings")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiBuildSettings")
        return

    def loadContent(self) -> None:
        """Populate the child widgets."""
        self.editBuildName.setText(self._build.name)
        self.optTabSelect.loadContent()
        self.optTabHeadings.loadContent()
        self.optTabContent.loadContent()
        self.optTabFormat.loadContent()
        self.optTabOutput.loadContent()
        return

    ##
    #  Properties
    ##

    @property
    def buildID(self) -> str:
        """The build ID of the build of the dialog."""
        return self._build.buildID

    ##
    #  Events
    ##

    def closeEvent(self, event: QEvent) -> None:
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
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _stackPageSelected(self, pageId: int) -> None:
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
    def _dialogButtonClicked(self, button: QAbstractButton) -> None:
        """Handle button clicks from the dialog button box."""
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self._emitBuildData()
        elif role == QDialogButtonBox.AcceptRole:
            self._emitBuildData()
            self.close()
        elif role == QDialogButtonBox.RejectRole:
            self.close()
        return

    ##
    #  Internal Functions
    ##

    def _askToSaveBuild(self) -> None:
        """Check if there are unsaved changes, and if there are, ask
        whether the user wants to save them.
        """
        if self._build.changed:
            response = SHARED.question(self.tr(
                "Do you want to save your changes to '{0}'?".format(self._build.name)
            ))
            if response:
                self._emitBuildData()
            self._build.resetChangedState()
        return

    def _saveSettings(self) -> None:
        """Save the various user settings."""
        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())
        treeWidth, filterWidth = self.optTabSelect.mainSplitSizes()

        logger.debug("Saving State: GuiBuildSettings")
        pOptions = SHARED.project.options
        pOptions.setValue("GuiBuildSettings", "winWidth", winWidth)
        pOptions.setValue("GuiBuildSettings", "winHeight", winHeight)
        pOptions.setValue("GuiBuildSettings", "treeWidth", treeWidth)
        pOptions.setValue("GuiBuildSettings", "filterWidth", filterWidth)
        pOptions.saveSettings()

        return

    def _emitBuildData(self) -> None:
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


class _FilterTab(NFixedPage):

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

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings) -> None:
        super().__init__(parent=buildMain)

        self._treeMap: dict[str, QTreeWidgetItem] = {}
        self._build = build

        self._statusFlags: dict[int, QIcon] = {
            self.F_NONE:     QIcon(),
            self.F_FILTERED: SHARED.theme.getIcon("build_filtered"),
            self.F_INCLUDED: SHARED.theme.getIcon("build_included"),
            self.F_EXCLUDED: SHARED.theme.getIcon("build_excluded"),
        }

        self._trIncluded = self.tr("Included in manuscript")
        self._trExcluded = self.tr("Excluded from manuscript")

        # Project Tree
        # ============

        # Tree Settings
        iPx = SHARED.theme.baseIconSize
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
        treeHeader.setMinimumSectionSize(iPx + cMg)  # See Issue #1551
        treeHeader.setSectionResizeMode(self.C_NAME, QHeaderView.Stretch)
        treeHeader.setSectionResizeMode(self.C_ACTIVE, QHeaderView.Fixed)
        treeHeader.setSectionResizeMode(self.C_STATUS, QHeaderView.Fixed)
        treeHeader.resizeSection(self.C_ACTIVE, iPx + cMg)
        treeHeader.resizeSection(self.C_STATUS, iPx + cMg)

        self.optTree.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.optTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.optTree.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Filters
        # =======

        self.includedButton = QToolButton(self)
        self.includedButton.setToolTip(self.tr("Always included"))
        self.includedButton.setIcon(self._statusFlags[self.F_INCLUDED])
        self.includedButton.clicked.connect(lambda: self._setSelectedMode(self.F_INCLUDED))

        self.excludedButton = QToolButton(self)
        self.excludedButton.setToolTip(self.tr("Always excluded"))
        self.excludedButton.setIcon(self._statusFlags[self.F_EXCLUDED])
        self.excludedButton.clicked.connect(lambda: self._setSelectedMode(self.F_EXCLUDED))

        self.resetButton = QToolButton(self)
        self.resetButton.setToolTip(self.tr("Reset to default"))
        self.resetButton.setIcon(SHARED.theme.getIcon("revert"))
        self.resetButton.clicked.connect(lambda: self._setSelectedMode(self.F_FILTERED))

        self.modeBox = QHBoxLayout()
        self.modeBox.addWidget(QLabel(self.tr("Mark selection as")))
        self.modeBox.addStretch(1)
        self.modeBox.addWidget(self.includedButton)
        self.modeBox.addWidget(self.excludedButton)
        self.modeBox.addWidget(self.resetButton)
        self.modeBox.setSpacing(CONFIG.pxInt(4))

        # Filer Options
        self.filterOpt = NSwitchBox(self, iPx)
        self.filterOpt.switchToggled.connect(self._applyFilterSwitch)
        self.filterOpt.setFrameStyle(QFrame.NoFrame)

        # Assemble GUI
        # ============

        pOptions = SHARED.project.options

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
        self.mainSplit.setStretchFactor(0, 1)
        self.mainSplit.setStretchFactor(1, 0)
        self.mainSplit.setSizes([
            CONFIG.pxInt(pOptions.getInt("GuiBuildSettings", "treeWidth", 300)),
            CONFIG.pxInt(pOptions.getInt("GuiBuildSettings", "filterWidth", 300))
        ])

        self.setCentralWidget(self.mainSplit)

        return

    def loadContent(self) -> None:
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
    def _applyFilterSwitch(self, key: str, state: bool) -> None:
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

    def _populateTree(self) -> None:
        """Build the tree of project items."""
        logger.debug("Building project tree")
        self._treeMap = {}
        self.optTree.clear()
        for nwItem in SHARED.project.iterProjectItems():

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
            itemIcon = SHARED.theme.getItemIcon(
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
            trItem.setIcon(self.C_ACTIVE, SHARED.theme.getIcon(iconName))

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

    def _populateFilters(self) -> None:
        """Populate the filter options switches."""
        self.filterOpt.clear()
        self.filterOpt.addLabel(self._build.getLabel("filter"))
        self.filterOpt.addItem(
            SHARED.theme.getIcon("proj_scene"),
            self._build.getLabel("filter.includeNovel"),
            "doc:filter.includeNovel",
            default=self._build.getBool("filter.includeNovel")
        )
        self.filterOpt.addItem(
            SHARED.theme.getIcon("proj_note"),
            self._build.getLabel("filter.includeNotes"),
            "doc:filter.includeNotes",
            default=self._build.getBool("filter.includeNotes")
        )
        self.filterOpt.addItem(
            SHARED.theme.getIcon("unchecked"),
            self._build.getLabel("filter.includeInactive"),
            "doc:filter.includeInactive",
            default=self._build.getBool("filter.includeInactive")
        )

        self.filterOpt.addSeparator()

        # Root Classes
        self.filterOpt.addLabel(self.tr("Select Root Folders"))
        for tHandle, nwItem in SHARED.project.tree.iterRoots(None):
            if not nwItem.isInactiveClass():
                itemIcon = SHARED.theme.getItemIcon(
                    nwItem.itemType, nwItem.itemClass, nwItem.itemLayout
                )
                self.filterOpt.addItem(
                    itemIcon, nwItem.itemName, f"root:{tHandle}",
                    default=self._build.isRootAllowed(tHandle)
                )

        return

    def _setSelectedMode(self, mode: int) -> None:
        """Set the mode for the selected items."""
        items = self.optTree.selectedItems()
        if len(items) == 1 and isinstance(items[0], QTreeWidgetItem):
            items = self._scanChildren(items[0], [])

        for item in items:
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

    def _setTreeItemMode(self) -> None:
        """Update the filtered mode icon on all items."""
        filtered = self._build.buildItemFilter(SHARED.project)
        for tHandle, item in self._treeMap.items():
            allow, mode = filtered.get(tHandle, (False, FilterMode.UNKNOWN))
            if mode == FilterMode.INCLUDED:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_INCLUDED])
                item.setToolTip(self.C_STATUS, self._trIncluded)
            elif mode == FilterMode.EXCLUDED:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_EXCLUDED])
                item.setToolTip(self.C_STATUS, self._trExcluded)
            elif mode == FilterMode.FILTERED and allow:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_FILTERED])
                item.setToolTip(self.C_STATUS, self._trIncluded)
            else:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_NONE])
        return

    def _scanChildren(self, item: QTreeWidgetItem | None, items: list) -> list[QTreeWidgetItem]:
        """This is a recursive function returning all items in a tree
        starting at a given QTreeWidgetItem.
        """
        if isinstance(item, QTreeWidgetItem):
            items.append(item)
            for i in range(item.childCount()):
                self._scanChildren(item.child(i), items)
        return items

# END Class _FilterTab


class _HeadingsTab(NScrollablePage):

    EDIT_TITLE   = 1
    EDIT_CHAPTER = 2
    EDIT_UNNUM   = 3
    EDIT_SCENE   = 4
    EDIT_SECTION = 5

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings) -> None:
        super().__init__(parent=buildMain)

        self._build = build
        self._editing = 0

        iPx = SHARED.theme.baseIconSize
        vSp = CONFIG.pxInt(12)
        bSp = CONFIG.pxInt(6)

        # Format Boxes
        # ============
        self.formatBox = QGridLayout()
        self.formatBox.setHorizontalSpacing(vSp)

        # Title Heading
        self.lblTitle = QLabel(self._build.getLabel("headings.fmtTitle"))
        self.fmtTitle = QLineEdit("", self)
        self.fmtTitle.setReadOnly(True)
        self.btnTitle = QToolButton(self)
        self.btnTitle.setIcon(SHARED.theme.getIcon("edit"))
        self.btnTitle.clicked.connect(lambda: self._editHeading(self.EDIT_TITLE))

        wrapTitle = QHBoxLayout()
        wrapTitle.addWidget(self.fmtTitle)
        wrapTitle.addWidget(self.btnTitle)
        wrapTitle.setSpacing(bSp)

        self.formatBox.addWidget(self.lblTitle, 0, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapTitle,     0, 1, Qt.AlignLeft)

        # Chapter Heading
        self.lblChapter = QLabel(self._build.getLabel("headings.fmtChapter"))
        self.fmtChapter = QLineEdit("", self)
        self.fmtChapter.setReadOnly(True)
        self.btnChapter = QToolButton(self)
        self.btnChapter.setIcon(SHARED.theme.getIcon("edit"))
        self.btnChapter.clicked.connect(lambda: self._editHeading(self.EDIT_CHAPTER))

        wrapChapter = QHBoxLayout()
        wrapChapter.addWidget(self.fmtChapter)
        wrapChapter.addWidget(self.btnChapter)
        wrapChapter.setSpacing(bSp)

        self.formatBox.addWidget(self.lblChapter, 1, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapChapter,     1, 1, Qt.AlignLeft)

        # Unnumbered Chapter Heading
        self.lblUnnumbered = QLabel(self._build.getLabel("headings.fmtUnnumbered"))
        self.fmtUnnumbered = QLineEdit("", self)
        self.fmtUnnumbered.setReadOnly(True)
        self.btnUnnumbered = QToolButton(self)
        self.btnUnnumbered.setIcon(SHARED.theme.getIcon("edit"))
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
        self.fmtScene = QLineEdit("", self)
        self.fmtScene.setReadOnly(True)
        self.btnScene = QToolButton(self)
        self.btnScene.setIcon(SHARED.theme.getIcon("edit"))
        self.btnScene.clicked.connect(lambda: self._editHeading(self.EDIT_SCENE))
        self.hdeScene = QLabel(self.tr("Hide"))
        self.hdeScene.setToolTip(sceneHideTip)
        self.swtScene = NSwitch(self, height=iPx)
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
        self.fmtSection = QLineEdit("", self)
        self.fmtSection.setReadOnly(True)
        self.btnSection = QToolButton(self)
        self.btnSection.setIcon(SHARED.theme.getIcon("edit"))
        self.btnSection.clicked.connect(lambda: self._editHeading(self.EDIT_SECTION))
        self.hdeSection = QLabel(self.tr("Hide"))
        self.hdeSection.setToolTip(sectionHideTip)
        self.swtSection = NSwitch(self, height=iPx)
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

        self.formSyntax = _HeadingSyntaxHighlighter(self.editTextBox.document())

        self.menuInsert = QMenu(self)
        self.aInsTitle = self.menuInsert.addAction(self.tr("Title"))
        self.aInsChNum = self.menuInsert.addAction(self.tr("Chapter Number"))
        self.aInsChWord = self.menuInsert.addAction(self.tr("Chapter Number (Word)"))
        self.aInsChRomU = self.menuInsert.addAction(self.tr("Chapter Number (Upper Case Roman)"))
        self.aInsChRomL = self.menuInsert.addAction(self.tr("Chapter Number (Lower Case Roman)"))
        self.aInsScNum = self.menuInsert.addAction(self.tr("Scene Number (In Chapter)"))
        self.aInsScAbs = self.menuInsert.addAction(self.tr("Scene Number (Absolute)"))
        self.aInsCharPOV = self.menuInsert.addAction(self.tr("Point of View Character"))
        self.aInsCharFocus = self.menuInsert.addAction(self.tr("Focus Character"))

        self.aInsTitle.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.TITLE))
        self.aInsChNum.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.CH_NUM))
        self.aInsChWord.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.CH_WORD))
        self.aInsChRomU.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.CH_ROMU))
        self.aInsChRomL.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.CH_ROML))
        self.aInsScNum.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.SC_NUM))
        self.aInsScAbs.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.SC_ABS))
        self.aInsCharPOV.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.CHAR_POV))
        self.aInsCharFocus.triggered.connect(lambda: self._insertIntoForm(nwHeadFmt.CHAR_FOCUS))

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

        self.setCentralLayout(self.outerBox)

        return

    def loadContent(self) -> None:
        """Populate the widgets."""
        self.fmtTitle.setText(self._build.getStr("headings.fmtTitle"))
        self.fmtChapter.setText(self._build.getStr("headings.fmtChapter"))
        self.fmtUnnumbered.setText(self._build.getStr("headings.fmtUnnumbered"))
        self.fmtScene.setText(self._build.getStr("headings.fmtScene"))
        self.fmtSection.setText(self._build.getStr("headings.fmtSection"))
        self.swtScene.setChecked(self._build.getBool("headings.hideScene"))
        self.swtSection.setChecked(self._build.getBool("headings.hideSection"))
        return

    def saveContent(self) -> None:
        """Save choices back into build object."""
        self._build.setValue("headings.hideScene", self.swtScene.isChecked())
        self._build.setValue("headings.hideSection", self.swtSection.isChecked())
        return

    ##
    #  Internal Functions
    ##

    def _insertIntoForm(self, text: str) -> None:
        """Insert formatting text from the dropdown menu."""
        if self._editing > 0:
            cursor = self.editTextBox.textCursor()
            cursor.insertText(text)
            self.editTextBox.setFocus()
        return

    def _editHeading(self, heading: int) -> None:
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

        self.editTextBox.setPlainText(text.replace(nwHeadFmt.BR, "\n"))
        self.lblEditForm.setText(self.tr("Editing: {0}").format(label))

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _saveFormat(self) -> None:
        """Save the format from the edit text box."""
        heading = self._editing
        text = self.editTextBox.toPlainText().strip().replace("\n", nwHeadFmt.BR)
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

    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self._fmtSymbol = QTextCharFormat()
        self._fmtSymbol.setForeground(SHARED.theme.colHead)
        self._fmtFormat = QTextCharFormat()
        self._fmtFormat.setForeground(SHARED.theme.colEmph)
        return

    def highlightBlock(self, text: str) -> None:
        """Add syntax highlighting to the text block."""
        for heading in nwHeadFmt.PAGE_HEADERS:
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


class _ContentTab(NScrollableForm):

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings) -> None:
        super().__init__(parent=buildMain)

        self._build = build

        iPx = SHARED.theme.baseIconSize

        # Text Content
        self.incSynopsis = NSwitch(self, height=iPx)
        self.incComments = NSwitch(self, height=iPx)
        self.incKeywords = NSwitch(self, height=iPx)
        self.incBodyText = NSwitch(self, height=iPx)

        self.addGroupLabel(self._build.getLabel("text.grpContent"))
        self.addRow(self._build.getLabel("text.includeSynopsis"), self.incSynopsis)
        self.addRow(self._build.getLabel("text.includeComments"), self.incComments)
        self.addRow(self._build.getLabel("text.includeKeywords"), self.incKeywords)
        self.addRow(self._build.getLabel("text.includeBodyText"), self.incBodyText)

        # Insert Content
        self.addNoteHead = NSwitch(self, height=iPx)

        self.addGroupLabel(self._build.getLabel("text.grpInsert"))
        self.addRow(self._build.getLabel("text.addNoteHeadings"), self.addNoteHead)

        # Finalise
        self.finalise()

        return

    def loadContent(self) -> None:
        """Populate the widgets."""
        self.incSynopsis.setChecked(self._build.getBool("text.includeSynopsis"))
        self.incComments.setChecked(self._build.getBool("text.includeComments"))
        self.incKeywords.setChecked(self._build.getBool("text.includeKeywords"))
        self.incBodyText.setChecked(self._build.getBool("text.includeBodyText"))
        self.addNoteHead.setChecked(self._build.getBool("text.addNoteHeadings"))
        return

    def saveContent(self) -> None:
        """Save choices back into build object."""
        self._build.setValue("text.includeSynopsis", self.incSynopsis.isChecked())
        self._build.setValue("text.includeComments", self.incComments.isChecked())
        self._build.setValue("text.includeKeywords", self.incKeywords.isChecked())
        self._build.setValue("text.includeBodyText", self.incBodyText.isChecked())
        self._build.setValue("text.addNoteHeadings", self.addNoteHead.isChecked())
        return

# END Class _ContentTab


class _FormatTab(NScrollableForm):

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings) -> None:
        super().__init__(parent=buildMain)

        self.buildMain = buildMain

        self._build = build
        self._unitScale = 1.0

        iPx = SHARED.theme.baseIconSize
        spW = 6*SHARED.theme.textNWidth
        dbW = 8*SHARED.theme.textNWidth

        # Text Format
        # ===========

        self.addGroupLabel(self._build.getLabel("format.grpFormat"))

        # Font Family
        self.textFont = QLineEdit(self)
        self.textFont.setReadOnly(True)
        self.btnTextFont = QPushButton("...")
        self.btnTextFont.setMaximumWidth(int(2.5*SHARED.theme.getTextWidth("...")))
        self.btnTextFont.clicked.connect(self._selectFont)
        self.addRow(
            self._build.getLabel("format.textFont"), self.textFont,
            button=self.btnTextFont, stretch=(3, 2)
        )

        # Font Size
        self.textSize = NSpinBox(self)
        self.textSize.setMinimum(8)
        self.textSize.setMaximum(60)
        self.textSize.setSingleStep(1)
        self.textSize.setMinimumWidth(spW)
        self.addRow(self._build.getLabel("format.textSize"), self.textSize, unit="pt")

        # Line Height
        self.lineHeight = NDoubleSpinBox(self)
        self.lineHeight.setFixedWidth(spW)
        self.lineHeight.setMinimum(0.75)
        self.lineHeight.setMaximum(3.0)
        self.lineHeight.setSingleStep(0.05)
        self.lineHeight.setDecimals(2)
        self.addRow(self._build.getLabel("format.lineHeight"), self.lineHeight, unit="em")

        # Text Options
        # ============

        self.addGroupLabel(self._build.getLabel("format.grpOptions"))

        self.justifyText = NSwitch(self, height=iPx)
        self.stripUnicode = NSwitch(self, height=iPx)
        self.replaceTabs = NSwitch(self, height=iPx)

        self.addRow(self._build.getLabel("format.justifyText"), self.justifyText)
        self.addRow(self._build.getLabel("format.stripUnicode"), self.stripUnicode)
        self.addRow(self._build.getLabel("format.replaceTabs"), self.replaceTabs)

        # Page Layout
        # ===========

        self.addGroupLabel(self._build.getLabel("format.grpPage"))

        self.pageUnit = NComboBox(self)
        for key, name in nwLabels.UNIT_NAME.items():
            self.pageUnit.addItem(trConst(name), key)

        self.pageSize = NComboBox(self)
        for key, name in nwLabels.PAPER_NAME.items():
            self.pageSize.addItem(trConst(name), key)

        self.pageWidth = NDoubleSpinBox(self)
        self.pageWidth.setFixedWidth(dbW)
        self.pageWidth.setMaximum(500.0)
        self.pageWidth.valueChanged.connect(self._pageSizeValueChanged)

        self.pageHeight = NDoubleSpinBox(self)
        self.pageHeight.setFixedWidth(dbW)
        self.pageHeight.setMaximum(500.0)
        self.pageHeight.valueChanged.connect(self._pageSizeValueChanged)

        self.topMargin = NDoubleSpinBox(self)
        self.topMargin.setFixedWidth(dbW)

        self.bottomMargin = NDoubleSpinBox(self)
        self.bottomMargin.setFixedWidth(dbW)

        self.leftMargin = NDoubleSpinBox(self)
        self.leftMargin.setFixedWidth(dbW)

        self.rightMargin = NDoubleSpinBox(self)
        self.rightMargin.setFixedWidth(dbW)

        self.addRow(self._build.getLabel("format.pageUnit"), self.pageUnit)
        self.addRow(self._build.getLabel("format.pageSize"), self.pageSize)
        self.addRow(self._build.getLabel("format.pageWidth"), self.pageWidth)
        self.addRow(self._build.getLabel("format.pageHeight"), self.pageHeight)
        self.addRow(self._build.getLabel("format.topMargin"), self.topMargin)
        self.addRow(self._build.getLabel("format.bottomMargin"), self.bottomMargin)
        self.addRow(self._build.getLabel("format.leftMargin"), self.leftMargin)
        self.addRow(self._build.getLabel("format.rightMargin"), self.rightMargin)

        # Finalise
        self.finalise()

        return

    def loadContent(self) -> None:
        """Populate the widgets."""
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

    def saveContent(self) -> None:
        """Save choices back into build object."""
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
    def _selectFont(self) -> None:
        """Open the QFontDialog and set a font for the font style."""
        currFont = QFont()
        currFont.setFamily(self.textFont.text())
        currFont.setPointSize(self.textSize.value())
        newFont, status = QFontDialog.getFont(currFont, self)
        if status:
            self.textFont.setText(newFont.family())
            self.textSize.setValue(newFont.pointSize())
        return

    @pyqtSlot(int)
    def _changeUnit(self, index: int) -> None:
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

        self.pageWidth.blockSignals(True)
        self.pageWidth.setDecimals(nDec)
        self.pageWidth.setSingleStep(nStep)
        self.pageWidth.setMaximum(pMax)
        self.pageWidth.setValue(pageWidth)
        self.pageWidth.blockSignals(False)

        self.pageHeight.blockSignals(True)
        self.pageHeight.setDecimals(nDec)
        self.pageHeight.setSingleStep(nStep)
        self.pageHeight.setMaximum(pMax)
        self.pageHeight.setValue(pageHeight)
        self.pageHeight.blockSignals(False)

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
        self._changePageSize(self.pageSize.currentIndex())

        return

    @pyqtSlot(int)
    def _changePageSize(self, index: int) -> None:
        """The page size has changed."""
        w, h = nwLabels.PAPER_SIZE[self.pageSize.itemData(index)] if index >= 0 else (-1.0, -1.0)
        if w > 0.0 and h > 0.0:
            self.pageWidth.blockSignals(True)
            self.pageWidth.setValue(w/self._unitScale)
            self.pageWidth.blockSignals(False)
            self.pageHeight.blockSignals(True)
            self.pageHeight.setValue(h/self._unitScale)
            self.pageHeight.blockSignals(False)
        return

    @pyqtSlot()
    def _pageSizeValueChanged(self):
        """The user has changed the page size spin boxes, so we flip
        the page size box to Custom.
        """
        index = self.pageSize.findData("Custom")
        if index >= 0:
            self.pageSize.setCurrentIndex(index)
        return

# END Class _FormatTab


class _OutputTab(NScrollableForm):

    def __init__(self, buildMain: GuiBuildSettings, build: BuildSettings) -> None:
        super().__init__(parent=buildMain)

        self._build = build

        iPx = SHARED.theme.baseIconSize
        spW = 6*SHARED.theme.textNWidth

        # Open Document
        self.addGroupLabel(self._build.getLabel("odt"))

        self.odtAddColours = NSwitch(self, height=iPx)
        self.addRow(self._build.getLabel("odt.addColours"), self.odtAddColours)

        self.odtPageHeader = QLineEdit(self)
        self.odtPageHeader.setMinimumWidth(CONFIG.pxInt(200))
        self.btnPageHeader = QToolButton(self)
        self.btnPageHeader.setIcon(SHARED.theme.getIcon("revert"))
        self.btnPageHeader.clicked.connect(self._resetPageHeader)
        self.addRow(
            self._build.getLabel("odt.pageHeader"), self.odtPageHeader,
            button=self.btnPageHeader, stretch=(1, 1)
        )

        self.odtPageCountOffset = NSpinBox(self)
        self.odtPageCountOffset.setMinimum(0)
        self.odtPageCountOffset.setMaximum(999)
        self.odtPageCountOffset.setSingleStep(1)
        self.odtPageCountOffset.setMinimumWidth(spW)
        self.addRow(self._build.getLabel("odt.pageCountOffset"), self.odtPageCountOffset)

        # HTML Document
        self.addGroupLabel(self._build.getLabel("html"))

        self.htmlAddStyles = NSwitch(self, height=iPx)
        self.addRow(self._build.getLabel("html.addStyles"), self.htmlAddStyles)

        # Finalise
        self.finalise()

        return

    def loadContent(self) -> None:
        """Populate the widgets."""
        self.odtAddColours.setChecked(self._build.getBool("odt.addColours"))
        self.odtPageHeader.setText(self._build.getStr("odt.pageHeader"))
        self.odtPageCountOffset.setValue(self._build.getInt("odt.pageCountOffset"))
        self.htmlAddStyles.setChecked(self._build.getBool("html.addStyles"))
        return

    def saveContent(self) -> None:
        """Save choices back into build object."""
        self._build.setValue("odt.addColours", self.odtAddColours.isChecked())
        self._build.setValue("odt.pageHeader", self.odtPageHeader.text())
        self._build.setValue("odt.pageCountOffset", self.odtPageCountOffset.value())
        self._build.setValue("html.addStyles", self.htmlAddStyles.isChecked())
        return

    ##
    #  Private Slots
    ##

    def _resetPageHeader(self) -> None:
        """Reset the ODT header format to default."""
        self.odtPageHeader.setText(nwHeadFmt.ODT_AUTO)
        return

# END Class _OutputTab
