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

from PyQt5.QtCore import QEvent, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QSyntaxHighlighter, QTextCharFormat, QTextDocument
from PyQt5.QtWidgets import (
    QAbstractButton, QAbstractItemView, QDialogButtonBox, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMenu, QPlainTextEdit,
    QPushButton, QSplitter, QStackedWidget, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import describeFont, qtLambda
from novelwriter.constants import nwHeadFmt, nwKeyWords, nwLabels, nwStyles, trConst
from novelwriter.core.buildsettings import BuildSettings, FilterMode
from novelwriter.extensions.configlayout import (
    NColourLabel, NFixedPage, NScrollableForm, NScrollablePage
)
from novelwriter.extensions.modified import (
    NComboBox, NDoubleSpinBox, NIconToolButton, NSpinBox, NToolDialog
)
from novelwriter.extensions.pagedsidebar import NPagedSideBar
from novelwriter.extensions.switch import NSwitch
from novelwriter.extensions.switchbox import NSwitchBox
from novelwriter.types import (
    QtAlignCenter, QtAlignLeft, QtDialogApply, QtDialogClose, QtDialogSave,
    QtRoleAccept, QtRoleApply, QtRoleReject, QtUserRole
)

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiBuildSettings(NToolDialog):
    """GUI Tools: Manuscript Build Settings Dialog

    The main tool for configuring manuscript builds. It's a GUI tool for
    editing JSON build definitions, wrapped as a BuildSettings object.
    """

    OPT_FILTERS    = 1
    OPT_HEADINGS   = 2
    OPT_FORMATTING = 10

    newSettingsReady = pyqtSignal(BuildSettings)

    def __init__(self, parent: GuiMain, build: BuildSettings) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiBuildSettings")
        self.setObjectName("GuiBuildSettings")

        self._build = build

        self.setWindowTitle(self.tr("Manuscript Build Settings"))
        self.setMinimumSize(CONFIG.pxInt(700), CONFIG.pxInt(400))

        wWin = CONFIG.pxInt(750)
        hWin = CONFIG.pxInt(550)

        options = SHARED.project.options
        self.resize(
            CONFIG.pxInt(options.getInt("GuiBuildSettings", "winWidth", wWin)),
            CONFIG.pxInt(options.getInt("GuiBuildSettings", "winHeight", hWin))
        )

        # Title
        self.titleLabel = NColourLabel(
            self.tr("Manuscript Build Settings"), self, color=SHARED.theme.helpText,
            scale=NColourLabel.HEADER_SCALE, indent=CONFIG.pxInt(4)
        )

        # Settings Name
        self.lblBuildName = QLabel(self.tr("Name"), self)
        self.editBuildName = QLineEdit(self)

        # SideBar
        self.sidebar = NPagedSideBar(self)
        self.sidebar.setLabelColor(SHARED.theme.helpText)

        self.sidebar.addLabel(self.tr("General"))
        self.sidebar.addButton(self.tr("Selection"), self.OPT_FILTERS)
        self.sidebar.addButton(self.tr("Headings"), self.OPT_HEADINGS)
        self.sidebar.addLabel(self.tr("Formatting"))

        self.sidebar.buttonClicked.connect(self._stackPageSelected)

        # Content
        self.optTabSelect = _FilterTab(self, self._build)
        self.optTabHeadings = _HeadingsTab(self, self._build)
        self.optTabFormatting = _FormattingTab(self, self._build, self.sidebar)

        self.toolStack = QStackedWidget(self)
        self.toolStack.addWidget(self.optTabSelect)
        self.toolStack.addWidget(self.optTabHeadings)
        self.toolStack.addWidget(self.optTabFormatting)

        # Buttons
        self.buttonBox = QDialogButtonBox(QtDialogApply | QtDialogSave | QtDialogClose, self)
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
        self.optTabFormatting.loadContent()
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
        self.softDelete()
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
        elif pageId >= self.OPT_FORMATTING:
            self.toolStack.setCurrentWidget(self.optTabFormatting)
            self.optTabFormatting.scrollToSection(pageId)
        return

    @pyqtSlot("QAbstractButton*")
    def _dialogButtonClicked(self, button: QAbstractButton) -> None:
        """Handle button clicks from the dialog button box."""
        role = self.buttonBox.buttonRole(button)
        if role == QtRoleApply:
            self._emitBuildData()
        elif role == QtRoleAccept:
            self._emitBuildData()
            self.close()
        elif role == QtRoleReject:
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
        self.optTabFormatting.saveContent()
        self.newSettingsReady.emit(self._build)
        self._build.resetChangedState()
        return


class _FilterTab(NFixedPage):

    C_DATA   = 0
    C_NAME   = 0
    C_ACTIVE = 1
    C_STATUS = 2

    D_HANDLE = QtUserRole
    D_FILE   = QtUserRole + 1

    F_NONE     = 0
    F_FILTERED = 1
    F_INCLUDED = 2
    F_EXCLUDED = 3

    def __init__(self, parent: QWidget, build: BuildSettings) -> None:
        super().__init__(parent=parent)

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

        iSz = SHARED.theme.baseIconSize
        iPx = SHARED.theme.baseIconHeight
        cMg = CONFIG.pxInt(6)

        # Tree Widget
        self.optTree = QTreeWidget(self)
        self.optTree.setIconSize(iSz)
        self.optTree.setUniformRowHeights(True)
        self.optTree.setAllColumnsShowFocus(True)
        self.optTree.setHeaderHidden(True)
        self.optTree.setIndentation(iPx)
        self.optTree.setColumnCount(3)

        treeHeader = self.optTree.header()
        treeHeader.setStretchLastSection(False)
        treeHeader.setMinimumSectionSize(iPx + cMg)  # See Issue #1551
        treeHeader.setSectionResizeMode(self.C_NAME, QHeaderView.ResizeMode.Stretch)
        treeHeader.setSectionResizeMode(self.C_ACTIVE, QHeaderView.ResizeMode.Fixed)
        treeHeader.setSectionResizeMode(self.C_STATUS, QHeaderView.ResizeMode.Fixed)
        treeHeader.resizeSection(self.C_ACTIVE, iPx + cMg)
        treeHeader.resizeSection(self.C_STATUS, iPx + cMg)

        self.optTree.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.optTree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.optTree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Filters
        # =======

        self.includedButton = NIconToolButton(self, iSz)
        self.includedButton.setToolTip(self.tr("Always included"))
        self.includedButton.setIcon(self._statusFlags[self.F_INCLUDED])
        self.includedButton.clicked.connect(qtLambda(self._setSelectedMode, self.F_INCLUDED))

        self.excludedButton = NIconToolButton(self, iSz)
        self.excludedButton.setToolTip(self.tr("Always excluded"))
        self.excludedButton.setIcon(self._statusFlags[self.F_EXCLUDED])
        self.excludedButton.clicked.connect(qtLambda(self._setSelectedMode, self.F_EXCLUDED))

        self.resetButton = NIconToolButton(self, iSz, "revert")
        self.resetButton.setToolTip(self.tr("Reset to default"))
        self.resetButton.clicked.connect(qtLambda(self._setSelectedMode, self.F_FILTERED))

        self.modeBox = QHBoxLayout()
        self.modeBox.addWidget(QLabel(self.tr("Mark selection as"), self))
        self.modeBox.addStretch(1)
        self.modeBox.addWidget(self.includedButton)
        self.modeBox.addWidget(self.excludedButton)
        self.modeBox.addWidget(self.resetButton)
        self.modeBox.setSpacing(CONFIG.pxInt(4))

        # Filer Options
        self.filterOpt = NSwitchBox(self, iPx)
        self.filterOpt.switchToggled.connect(self._applyFilterSwitch)
        self.filterOpt.setFrameStyle(QFrame.Shape.NoFrame)

        # Assemble GUI
        # ============

        pOptions = SHARED.project.options

        self.selectionBox = QVBoxLayout()
        self.selectionBox.addWidget(self.optTree)
        self.selectionBox.addLayout(self.modeBox)
        self.selectionBox.setContentsMargins(0, 0, 0, 0)

        self.selectionWidget = QWidget(self)
        self.selectionWidget.setLayout(self.selectionBox)

        self.mainSplit = QSplitter(self)
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

            trItem.setTextAlignment(self.C_NAME, QtAlignLeft)

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


class _HeadingsTab(NScrollablePage):

    EDIT_TITLE   = 1
    EDIT_CHAPTER = 2
    EDIT_UNNUM   = 3
    EDIT_SCENE   = 4
    EDIT_HSCENE  = 5
    EDIT_SECTION = 6

    def __init__(self, parent: QWidget, build: BuildSettings) -> None:
        super().__init__(parent=parent)

        self._build = build
        self._editing = 0

        iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize
        sSp = CONFIG.pxInt(16)
        vSp = CONFIG.pxInt(12)
        bSp = CONFIG.pxInt(6)
        trHide = self.tr("Hide")

        # Format Boxes
        # ============
        self.formatBox = QGridLayout()
        self.formatBox.setHorizontalSpacing(bSp)

        # Title Heading
        self.lblPart = QLabel(self._build.getLabel("headings.fmtPart"), self)
        self.fmtPart = QLineEdit("", self)
        self.fmtPart.setReadOnly(True)
        self.btnPart = NIconToolButton(self, iSz, "edit")
        self.btnPart.clicked.connect(qtLambda(self._editHeading, self.EDIT_TITLE))
        self.hdePart = QLabel(trHide, self)
        self.hdePart.setIndent(bSp)
        self.swtPart = NSwitch(self, height=iPx)

        self.formatBox.addWidget(self.lblPart, 0, 0)
        self.formatBox.addWidget(self.fmtPart, 0, 1)
        self.formatBox.addWidget(self.btnPart, 0, 2)
        self.formatBox.addWidget(self.hdePart, 0, 3)
        self.formatBox.addWidget(self.swtPart, 0, 4)

        # Chapter Heading
        self.lblChapter = QLabel(self._build.getLabel("headings.fmtChapter"), self)
        self.fmtChapter = QLineEdit("", self)
        self.fmtChapter.setReadOnly(True)
        self.btnChapter = NIconToolButton(self, iSz, "edit")
        self.btnChapter.clicked.connect(qtLambda(self._editHeading, self.EDIT_CHAPTER))
        self.hdeChapter = QLabel(trHide, self)
        self.hdeChapter.setIndent(bSp)
        self.swtChapter = NSwitch(self, height=iPx)

        self.formatBox.addWidget(self.lblChapter, 1, 0)
        self.formatBox.addWidget(self.fmtChapter, 1, 1)
        self.formatBox.addWidget(self.btnChapter, 1, 2)
        self.formatBox.addWidget(self.hdeChapter, 1, 3)
        self.formatBox.addWidget(self.swtChapter, 1, 4)

        # Unnumbered Chapter Heading
        self.lblUnnumbered = QLabel(self._build.getLabel("headings.fmtUnnumbered"), self)
        self.fmtUnnumbered = QLineEdit("", self)
        self.fmtUnnumbered.setReadOnly(True)
        self.btnUnnumbered = NIconToolButton(self, iSz, "edit")
        self.btnUnnumbered.clicked.connect(qtLambda(self._editHeading, self.EDIT_UNNUM))
        self.hdeUnnumbered = QLabel(trHide, self)
        self.hdeUnnumbered.setIndent(bSp)
        self.swtUnnumbered = NSwitch(self, height=iPx)

        self.formatBox.addWidget(self.lblUnnumbered, 2, 0)
        self.formatBox.addWidget(self.fmtUnnumbered, 2, 1)
        self.formatBox.addWidget(self.btnUnnumbered, 2, 2)
        self.formatBox.addWidget(self.hdeUnnumbered, 2, 3)
        self.formatBox.addWidget(self.swtUnnumbered, 2, 4)

        # Scene Heading
        self.lblScene = QLabel(self._build.getLabel("headings.fmtScene"), self)
        self.fmtScene = QLineEdit("", self)
        self.fmtScene.setReadOnly(True)
        self.btnScene = NIconToolButton(self, iSz, "edit")
        self.btnScene.clicked.connect(qtLambda(self._editHeading, self.EDIT_SCENE))
        self.hdeScene = QLabel(trHide, self)
        self.hdeScene.setIndent(bSp)
        self.swtScene = NSwitch(self, height=iPx)

        self.formatBox.addWidget(self.lblScene, 3, 0)
        self.formatBox.addWidget(self.fmtScene, 3, 1)
        self.formatBox.addWidget(self.btnScene, 3, 2)
        self.formatBox.addWidget(self.hdeScene, 3, 3)
        self.formatBox.addWidget(self.swtScene, 3, 4)

        # Alt Scene Heading
        self.lblAScene = QLabel(self._build.getLabel("headings.fmtAltScene"), self)
        self.fmtAScene = QLineEdit("", self)
        self.fmtAScene.setReadOnly(True)
        self.btnAScene = NIconToolButton(self, iSz, "edit")
        self.btnAScene.clicked.connect(qtLambda(self._editHeading, self.EDIT_HSCENE))
        self.hdeAScene = QLabel(trHide, self)
        self.hdeAScene.setIndent(bSp)
        self.swtAScene = NSwitch(self, height=iPx)

        self.formatBox.addWidget(self.lblAScene, 4, 0)
        self.formatBox.addWidget(self.fmtAScene, 4, 1)
        self.formatBox.addWidget(self.btnAScene, 4, 2)
        self.formatBox.addWidget(self.hdeAScene, 4, 3)
        self.formatBox.addWidget(self.swtAScene, 4, 4)

        # Section Heading
        self.lblSection = QLabel(self._build.getLabel("headings.fmtSection"), self)
        self.fmtSection = QLineEdit("", self)
        self.fmtSection.setReadOnly(True)
        self.btnSection = NIconToolButton(self, iSz, "edit")
        self.btnSection.clicked.connect(qtLambda(self._editHeading, self.EDIT_SECTION))
        self.hdeSection = QLabel(trHide, self)
        self.hdeSection.setIndent(bSp)
        self.swtSection = NSwitch(self, height=iPx)

        self.formatBox.addWidget(self.lblSection, 5, 0)
        self.formatBox.addWidget(self.fmtSection, 5, 1)
        self.formatBox.addWidget(self.btnSection, 5, 2)
        self.formatBox.addWidget(self.hdeSection, 5, 3)
        self.formatBox.addWidget(self.swtSection, 5, 4)

        # Edit Form
        # =========

        self.lblEditForm = QLabel(self.tr("Editing: {0}").format(self.tr("None")), self)

        self.editTextBox = QPlainTextEdit(self)
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

        self.aInsTitle.triggered.connect(qtLambda(self._insertIntoForm, nwHeadFmt.TITLE))
        self.aInsChNum.triggered.connect(qtLambda(self._insertIntoForm, nwHeadFmt.CH_NUM))
        self.aInsChWord.triggered.connect(qtLambda(self._insertIntoForm, nwHeadFmt.CH_WORD))
        self.aInsChRomU.triggered.connect(qtLambda(self._insertIntoForm, nwHeadFmt.CH_ROMU))
        self.aInsChRomL.triggered.connect(qtLambda(self._insertIntoForm, nwHeadFmt.CH_ROML))
        self.aInsScNum.triggered.connect(qtLambda(self._insertIntoForm, nwHeadFmt.SC_NUM))
        self.aInsScAbs.triggered.connect(qtLambda(self._insertIntoForm, nwHeadFmt.SC_ABS))
        self.aInsCharPOV.triggered.connect(qtLambda(self._insertIntoForm, nwHeadFmt.CHAR_POV))
        self.aInsCharFocus.triggered.connect(qtLambda(self._insertIntoForm, nwHeadFmt.CHAR_FOCUS))

        self.btnInsert = QPushButton(self.tr("Insert"), self)
        self.btnInsert.setMenu(self.menuInsert)

        self.btnApply = QPushButton(self.tr("Apply"), self)
        self.btnApply.clicked.connect(self._saveFormat)

        self.formButtonBox = QHBoxLayout()
        self.formButtonBox.addStretch(1)
        self.formButtonBox.addWidget(self.btnInsert)
        self.formButtonBox.addWidget(self.btnApply)

        self.editFormBox = QVBoxLayout()
        self.editFormBox.addWidget(self.lblEditForm)
        self.editFormBox.addWidget(self.editTextBox)
        self.editFormBox.addLayout(self.formButtonBox)

        # Layout Matrix
        # =============
        self.layoutMatrix = QGridLayout()
        self.layoutMatrix.setVerticalSpacing(vSp)
        self.layoutMatrix.setHorizontalSpacing(vSp)

        self.layoutMatrix.addWidget(QLabel(self.tr("Centre"), self), 0, 1)
        self.layoutMatrix.addWidget(QLabel(self.tr("Page Break"), self), 0, 2)

        # Title Layout
        self.lblTitle = QLabel(self._build.getLabel("headings.styleTitle"), self)
        self.centerTitle = NSwitch(self, height=iPx)
        self.breakTitle = NSwitch(self, height=iPx)

        self.layoutMatrix.addWidget(self.lblTitle,    1, 0)
        self.layoutMatrix.addWidget(self.centerTitle, 1, 1, QtAlignCenter)
        self.layoutMatrix.addWidget(self.breakTitle,  1, 2, QtAlignCenter)

        # Partition Layout
        self.lblPart = QLabel(self._build.getLabel("headings.stylePart"), self)
        self.centerPart = NSwitch(self, height=iPx)
        self.breakPart = NSwitch(self, height=iPx)

        self.layoutMatrix.addWidget(self.lblPart,    2, 0)
        self.layoutMatrix.addWidget(self.centerPart, 2, 1, QtAlignCenter)
        self.layoutMatrix.addWidget(self.breakPart,  2, 2, QtAlignCenter)

        # Chapter Layout
        self.lblChapter = QLabel(self._build.getLabel("headings.styleChapter"), self)
        self.centerChapter = NSwitch(self, height=iPx)
        self.breakChapter = NSwitch(self, height=iPx)

        self.layoutMatrix.addWidget(self.lblChapter,    3, 0)
        self.layoutMatrix.addWidget(self.centerChapter, 3, 1, QtAlignCenter)
        self.layoutMatrix.addWidget(self.breakChapter,  3, 2, QtAlignCenter)

        # Scene Layout
        self.lblScene = QLabel(self._build.getLabel("headings.styleScene"), self)
        self.centerScene = NSwitch(self, height=iPx)
        self.breakScene = NSwitch(self, height=iPx)

        self.layoutMatrix.addWidget(self.lblScene,    4, 0)
        self.layoutMatrix.addWidget(self.centerScene, 4, 1, QtAlignCenter)
        self.layoutMatrix.addWidget(self.breakScene,  4, 2, QtAlignCenter)

        self.layoutMatrix.setColumnStretch(3, 1)

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.formatBox)
        self.outerBox.addSpacing(sSp)
        self.outerBox.addLayout(self.editFormBox)
        self.outerBox.addSpacing(sSp)
        self.outerBox.addLayout(self.layoutMatrix)
        self.outerBox.addStretch(1)

        self.setCentralLayout(self.outerBox)

        return

    def loadContent(self) -> None:
        """Populate the widgets."""
        self.fmtPart.setText(self._build.getStr("headings.fmtPart"))
        self.fmtChapter.setText(self._build.getStr("headings.fmtChapter"))
        self.fmtUnnumbered.setText(self._build.getStr("headings.fmtUnnumbered"))
        self.fmtScene.setText(self._build.getStr("headings.fmtScene"))
        self.fmtAScene.setText(self._build.getStr("headings.fmtAltScene"))
        self.fmtSection.setText(self._build.getStr("headings.fmtSection"))

        self.swtPart.setChecked(self._build.getBool("headings.hidePart"))
        self.swtChapter.setChecked(self._build.getBool("headings.hideChapter"))
        self.swtUnnumbered.setChecked(self._build.getBool("headings.hideUnnumbered"))
        self.swtScene.setChecked(self._build.getBool("headings.hideScene"))
        self.swtAScene.setChecked(self._build.getBool("headings.hideAltScene"))
        self.swtSection.setChecked(self._build.getBool("headings.hideSection"))

        self.centerTitle.setChecked(self._build.getBool("headings.centerTitle"))
        self.centerPart.setChecked(self._build.getBool("headings.centerPart"))
        self.centerChapter.setChecked(self._build.getBool("headings.centerChapter"))
        self.centerScene.setChecked(self._build.getBool("headings.centerScene"))

        self.breakTitle.setChecked(self._build.getBool("headings.breakTitle"))
        self.breakPart.setChecked(self._build.getBool("headings.breakPart"))
        self.breakChapter.setChecked(self._build.getBool("headings.breakChapter"))
        self.breakScene.setChecked(self._build.getBool("headings.breakScene"))
        return

    def saveContent(self) -> None:
        """Save choices back into build object."""
        self._build.setValue("headings.hidePart", self.swtPart.isChecked())
        self._build.setValue("headings.hideChapter", self.swtChapter.isChecked())
        self._build.setValue("headings.hideUnnumbered", self.swtUnnumbered.isChecked())
        self._build.setValue("headings.hideScene", self.swtScene.isChecked())
        self._build.setValue("headings.hideAltScene", self.swtAScene.isChecked())
        self._build.setValue("headings.hideSection", self.swtSection.isChecked())

        self._build.setValue("headings.centerTitle", self.centerTitle.isChecked())
        self._build.setValue("headings.centerPart", self.centerPart.isChecked())
        self._build.setValue("headings.centerChapter", self.centerChapter.isChecked())
        self._build.setValue("headings.centerScene", self.centerScene.isChecked())

        self._build.setValue("headings.breakTitle", self.breakTitle.isChecked())
        self._build.setValue("headings.breakPart", self.breakPart.isChecked())
        self._build.setValue("headings.breakChapter", self.breakChapter.isChecked())
        self._build.setValue("headings.breakScene", self.breakScene.isChecked())
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
            text = self.fmtPart.text()
            label = self._build.getLabel("headings.fmtPart")
        elif heading == self.EDIT_CHAPTER:
            text = self.fmtChapter.text()
            label = self._build.getLabel("headings.fmtChapter")
        elif heading == self.EDIT_UNNUM:
            text = self.fmtUnnumbered.text()
            label = self._build.getLabel("headings.fmtUnnumbered")
        elif heading == self.EDIT_SCENE:
            text = self.fmtScene.text()
            label = self._build.getLabel("headings.fmtScene")
        elif heading == self.EDIT_HSCENE:
            text = self.fmtAScene.text()
            label = self._build.getLabel("headings.fmtAltScene")
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
            self.fmtPart.setText(text)
            self._build.setValue("headings.fmtPart", text)
        elif heading == self.EDIT_CHAPTER:
            self.fmtChapter.setText(text)
            self._build.setValue("headings.fmtChapter", text)
        elif heading == self.EDIT_UNNUM:
            self.fmtUnnumbered.setText(text)
            self._build.setValue("headings.fmtUnnumbered", text)
        elif heading == self.EDIT_SCENE:
            self.fmtScene.setText(text)
            self._build.setValue("headings.fmtScene", text)
        elif heading == self.EDIT_HSCENE:
            self.fmtAScene.setText(text)
            self._build.setValue("headings.fmtAltScene", text)
        elif heading == self.EDIT_SECTION:
            self.fmtSection.setText(text)
            self._build.setValue("headings.fmtSection", text)
        else:
            return

        self._editHeading(0)
        self.editTextBox.clear()

        return


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


class _FormattingTab(NScrollableForm):

    def __init__(self, parent: QWidget, build: BuildSettings, sidebar: NPagedSideBar) -> None:
        super().__init__(parent=parent)

        self._build = build
        self._sidebar = sidebar

        self.setHelpTextStyle(SHARED.theme.helpText)
        self.buildForm()

        return

    def buildForm(self) -> None:
        """Build the formatting form."""
        section = 10

        iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize
        spW = 6*SHARED.theme.textNWidth
        dbW = 8*SHARED.theme.textNWidth

        # Common Translations

        trW = self.tr("W:")  # Width
        trH = self.tr("H:")  # Height
        trT = self.tr("T:")  # Top
        trB = self.tr("B:")  # Bottom
        trL = self.tr("L:")  # Left
        trR = self.tr("R:")  # Right

        # Text Content
        # ============

        title = self._build.getLabel("text.grpContent")
        section += 1
        self._sidebar.addButton(title, section)
        self.addGroupLabel(title, section)

        # Text Inclusion
        self.incBodyText = NSwitch(self, height=iPx)
        self.incSynopsis = NSwitch(self, height=iPx)
        self.incComments = NSwitch(self, height=iPx)
        self.incKeywords = NSwitch(self, height=iPx)

        self.addRow(self._build.getLabel("text.includeBodyText"), self.incBodyText)
        self.addRow(self._build.getLabel("text.includeSynopsis"), self.incSynopsis)
        self.addRow(self._build.getLabel("text.includeComments"), self.incComments)
        self.addRow(self._build.getLabel("text.includeKeywords"), self.incKeywords)

        # Ignored Keywords
        self.ignoredKeywords = QLineEdit(self)

        self.mnKeywords = QMenu(self)
        for keyword in nwKeyWords.VALID_KEYS:
            self.mnKeywords.addAction(
                trConst(nwLabels.KEY_NAME[keyword]),
                lambda keyword=keyword: self._updateIgnoredKeywords(keyword)
            )

        self.ignoredKeywordsButton = NIconToolButton(self, iSz, "add")
        self.ignoredKeywordsButton.setMenu(self.mnKeywords)
        self.addRow(
            self._build.getLabel("text.ignoredKeywords"), self.ignoredKeywords,
            button=self.ignoredKeywordsButton, stretch=(1, 1)
        )

        # Note Headings
        self.addNoteHead = NSwitch(self, height=iPx)

        self.addRow(self._build.getLabel("text.addNoteHeadings"), self.addNoteHead)

        # Text Format
        # ===========

        title = self._build.getLabel("format.grpFormat")
        section += 1
        self._sidebar.addButton(title, section)
        self.addGroupLabel(title, section)

        # Text Font
        self.textFont = QLineEdit(self)
        self.textFont.setReadOnly(True)
        self.btnTextFont = NIconToolButton(self, iSz, "font")
        self.btnTextFont.clicked.connect(self._selectFont)
        self.addRow(
            self._build.getLabel("format.textFont"), self.textFont,
            button=self.btnTextFont, stretch=(1, 1)
        )

        # Line Height
        self.lineHeight = NDoubleSpinBox(self)
        self.lineHeight.setFixedWidth(spW)
        self.lineHeight.setMinimum(0.75)
        self.lineHeight.setMaximum(3.0)
        self.lineHeight.setSingleStep(0.05)
        self.lineHeight.setDecimals(2)
        self.addRow(self._build.getLabel("format.lineHeight"), self.lineHeight, unit="em")

        # Text Options
        self.justifyText = NSwitch(self, height=iPx)
        self.stripUnicode = NSwitch(self, height=iPx)
        self.replaceTabs = NSwitch(self, height=iPx)
        self.keepBreaks = NSwitch(self, height=iPx)
        self.showDialogue = NSwitch(self, height=iPx)

        self.addRow(self._build.getLabel("format.justifyText"), self.justifyText)
        self.addRow(self._build.getLabel("format.stripUnicode"), self.stripUnicode)
        self.addRow(self._build.getLabel("format.replaceTabs"), self.replaceTabs)
        self.addRow(self._build.getLabel("format.keepBreaks"), self.keepBreaks)
        self.addRow(self._build.getLabel("format.showDialogue"), self.showDialogue)

        # First Line Indent
        # =================

        title = self._build.getLabel("format.grpParIndent")
        section += 1
        self._sidebar.addButton(title, section)
        self.addGroupLabel(title, section)

        self.firstIndent = NSwitch(self, height=iPx)
        self.indentFirstPar = NSwitch(self, height=iPx)

        self.indentWidth = NDoubleSpinBox(self)
        self.indentWidth.setFixedWidth(spW)
        self.indentWidth.setMinimum(0.1)
        self.indentWidth.setMaximum(9.9)
        self.indentWidth.setSingleStep(0.1)
        self.indentWidth.setDecimals(1)

        self.addRow(self._build.getLabel("format.firstLineIndent"), self.firstIndent)
        self.addRow(self._build.getLabel("format.firstIndentWidth"), self.indentWidth, unit="em")
        self.addRow(self._build.getLabel("format.indentFirstPar"), self.indentFirstPar)

        # Text Margins
        # ============

        title = self._build.getLabel("format.grpMargins")
        section += 1
        self._sidebar.addButton(title, section)
        self.addGroupLabel(title, section)

        # Title
        self.titleMarginT = NDoubleSpinBox(self)
        self.titleMarginT.setFixedWidth(dbW)

        self.titleMarginB = NDoubleSpinBox(self)
        self.titleMarginB.setFixedWidth(dbW)

        self.addRow(
            trConst(nwStyles.T_LABEL["H0"]),
            [trT, self.titleMarginT, 6, trB, self.titleMarginB],
        )

        # Heading 1
        self.h1MarginT = NDoubleSpinBox(self)
        self.h1MarginT.setFixedWidth(dbW)

        self.h1MarginB = NDoubleSpinBox(self)
        self.h1MarginB.setFixedWidth(dbW)

        self.addRow(
            trConst(nwStyles.T_LABEL["H1"]),
            [trT, self.h1MarginT, 6, trB, self.h1MarginB],
        )

        # Heading 2
        self.h2MarginT = NDoubleSpinBox(self)
        self.h2MarginT.setFixedWidth(dbW)

        self.h2MarginB = NDoubleSpinBox(self)
        self.h2MarginB.setFixedWidth(dbW)

        self.addRow(
            trConst(nwStyles.T_LABEL["H2"]),
            [trT, self.h2MarginT, 6, trB, self.h2MarginB],
        )

        # Heading 3
        self.h3MarginT = NDoubleSpinBox(self)
        self.h3MarginT.setFixedWidth(dbW)

        self.h3MarginB = NDoubleSpinBox(self)
        self.h3MarginB.setFixedWidth(dbW)

        self.addRow(
            trConst(nwStyles.T_LABEL["H3"]),
            [trT, self.h3MarginT, 6, trB, self.h3MarginB],
        )

        # Heading 4
        self.h4MarginT = NDoubleSpinBox(self)
        self.h4MarginT.setFixedWidth(dbW)

        self.h4MarginB = NDoubleSpinBox(self)
        self.h4MarginB.setFixedWidth(dbW)

        self.addRow(
            trConst(nwStyles.T_LABEL["H4"]),
            [trT, self.h4MarginT, 6, trB, self.h4MarginB],
        )

        # Text
        self.textMarginT = NDoubleSpinBox(self)
        self.textMarginT.setFixedWidth(dbW)

        self.textMarginB = NDoubleSpinBox(self)
        self.textMarginB.setFixedWidth(dbW)

        self.addRow(
            trConst(nwStyles.T_LABEL["TT"]),
            [trT, self.textMarginT, 6, trB, self.textMarginB],
        )

        # Separator
        self.sepMarginT = NDoubleSpinBox(self)
        self.sepMarginT.setFixedWidth(dbW)

        self.sepMarginB = NDoubleSpinBox(self)
        self.sepMarginB.setFixedWidth(dbW)

        self.addRow(
            trConst(nwStyles.T_LABEL["SP"]),
            [trT, self.sepMarginT, 6, trB, self.sepMarginB],
        )

        # Page Layout
        # ===========

        title = self._build.getLabel("format.grpPage")
        section += 1
        self._sidebar.addButton(title, section)
        self.addGroupLabel(title, section)

        # Unit
        self.pageUnit = NComboBox(self)
        for key, name in nwLabels.UNIT_NAME.items():
            self.pageUnit.addItem(trConst(name), key)

        self.addRow(self._build.getLabel("format.pageUnit"), self.pageUnit)

        # Page Size
        self.pageSize = NComboBox(self)
        for key, name in nwLabels.PAPER_NAME.items():
            self.pageSize.addItem(trConst(name), key)

        self.pageWidth = NDoubleSpinBox(self, max=500.0)
        self.pageWidth.setFixedWidth(dbW)
        self.pageWidth.valueChanged.connect(self._pageSizeValueChanged)

        self.pageHeight = NDoubleSpinBox(self, max=500.0)
        self.pageHeight.setFixedWidth(dbW)
        self.pageHeight.valueChanged.connect(self._pageSizeValueChanged)

        self.addRow(
            self._build.getLabel("format.pageSize"),
            [self.pageSize, 6, trW, self.pageWidth, 6, trH, self.pageHeight],
        )

        # Page Margins
        self.topMargin = NDoubleSpinBox(self)
        self.topMargin.setFixedWidth(dbW)

        self.bottomMargin = NDoubleSpinBox(self)
        self.bottomMargin.setFixedWidth(dbW)

        self.leftMargin = NDoubleSpinBox(self)
        self.leftMargin.setFixedWidth(dbW)

        self.rightMargin = NDoubleSpinBox(self)
        self.rightMargin.setFixedWidth(dbW)

        self.addRow(
            self._build.getLabel("format.pageMargins"),
            [trT, self.topMargin, 6, trB, self.bottomMargin],
        )
        self.addRow(
            "",
            [trL, self.leftMargin, 6, trR, self.rightMargin],
        )

        # Open Document
        # =============

        title = self._build.getLabel("doc")
        section += 1
        self._sidebar.addButton(title, section)
        self.addGroupLabel(title, section)

        # Header
        self.odtPageHeader = QLineEdit(self)
        self.odtPageHeader.setMinimumWidth(CONFIG.pxInt(200))
        self.btnPageHeader = NIconToolButton(self, iSz, "revert")
        self.btnPageHeader.clicked.connect(self._resetPageHeader)
        self.addRow(
            self._build.getLabel("doc.pageHeader"), self.odtPageHeader,
            button=self.btnPageHeader, stretch=(1, 1)
        )

        self.odtPageCountOffset = NSpinBox(self)
        self.odtPageCountOffset.setMinimum(0)
        self.odtPageCountOffset.setMaximum(999)
        self.odtPageCountOffset.setSingleStep(1)
        self.odtPageCountOffset.setMinimumWidth(spW)
        self.addRow(self._build.getLabel("doc.pageCountOffset"), self.odtPageCountOffset)

        # Headings
        self.colorHeadings = NSwitch(self, height=iPx)
        self.scaleHeadings = NSwitch(self, height=iPx)
        self.boldHeadings = NSwitch(self, height=iPx)

        self.addRow(self._build.getLabel("doc.colorHeadings"), self.colorHeadings)
        self.addRow(self._build.getLabel("doc.scaleHeadings"), self.scaleHeadings)
        self.addRow(self._build.getLabel("doc.boldHeadings"), self.boldHeadings)

        # HTML Document
        # =============

        title = self._build.getLabel("html")
        section += 1
        self._sidebar.addButton(title, section)
        self.addGroupLabel(title, section)

        self.htmlAddStyles = NSwitch(self, height=iPx)
        self.addRow(self._build.getLabel("html.addStyles"), self.htmlAddStyles)

        self.htmlPreserveTabs = NSwitch(self, height=iPx)
        self.addRow(self._build.getLabel("html.preserveTabs"), self.htmlPreserveTabs)

        # Finalise
        self.finalise()

        return

    def loadContent(self) -> None:
        """Populate the widgets."""
        # Text Content
        # ============

        self.incBodyText.setChecked(self._build.getBool("text.includeBodyText"))
        self.incSynopsis.setChecked(self._build.getBool("text.includeSynopsis"))
        self.incComments.setChecked(self._build.getBool("text.includeComments"))
        self.incKeywords.setChecked(self._build.getBool("text.includeKeywords"))
        self.ignoredKeywords.setText(self._build.getStr("text.ignoredKeywords"))
        self.addNoteHead.setChecked(self._build.getBool("text.addNoteHeadings"))
        self._updateIgnoredKeywords()

        # Text Format
        # ===========

        self._textFont = QFont()
        self._textFont.fromString(self._build.getStr("format.textFont"))

        self.textFont.setText(describeFont(self._textFont))
        self.textFont.setCursorPosition(0)

        self.lineHeight.setValue(self._build.getFloat("format.lineHeight"))
        self.justifyText.setChecked(self._build.getBool("format.justifyText"))
        self.stripUnicode.setChecked(self._build.getBool("format.stripUnicode"))
        self.replaceTabs.setChecked(self._build.getBool("format.replaceTabs"))
        self.keepBreaks.setChecked(self._build.getBool("format.keepBreaks"))
        self.showDialogue.setChecked(self._build.getBool("format.showDialogue"))

        # First Line Indent
        # =================

        self.firstIndent.setChecked(self._build.getBool("format.firstLineIndent"))
        self.indentWidth.setValue(self._build.getFloat("format.firstIndentWidth"))
        self.indentFirstPar.setChecked(self._build.getBool("format.indentFirstPar"))

        # Text Margins
        # ============

        self.titleMarginT.setValue(self._build.getFloat("format.titleMarginT"))
        self.titleMarginB.setValue(self._build.getFloat("format.titleMarginB"))
        self.h1MarginT.setValue(self._build.getFloat("format.h1MarginT"))
        self.h1MarginB.setValue(self._build.getFloat("format.h1MarginB"))
        self.h2MarginT.setValue(self._build.getFloat("format.h2MarginT"))
        self.h2MarginB.setValue(self._build.getFloat("format.h2MarginB"))
        self.h3MarginT.setValue(self._build.getFloat("format.h3MarginT"))
        self.h3MarginB.setValue(self._build.getFloat("format.h3MarginB"))
        self.h4MarginT.setValue(self._build.getFloat("format.h4MarginT"))
        self.h4MarginB.setValue(self._build.getFloat("format.h4MarginB"))
        self.textMarginT.setValue(self._build.getFloat("format.textMarginT"))
        self.textMarginB.setValue(self._build.getFloat("format.textMarginB"))
        self.sepMarginT.setValue(self._build.getFloat("format.sepMarginT"))
        self.sepMarginB.setValue(self._build.getFloat("format.sepMarginB"))

        # Page Layout
        # ===========

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

        # Document
        # ========

        self.colorHeadings.setChecked(self._build.getBool("doc.colorHeadings"))
        self.scaleHeadings.setChecked(self._build.getBool("doc.scaleHeadings"))
        self.boldHeadings.setChecked(self._build.getBool("doc.boldHeadings"))
        self.odtPageHeader.setText(self._build.getStr("doc.pageHeader"))
        self.odtPageCountOffset.setValue(self._build.getInt("doc.pageCountOffset"))
        self.odtPageHeader.setCursorPosition(0)

        # HTML Document
        # =============

        self.htmlAddStyles.setChecked(self._build.getBool("html.addStyles"))
        self.htmlPreserveTabs.setChecked(self._build.getBool("html.preserveTabs"))

        return

    def saveContent(self) -> None:
        """Save choices back into build object."""
        # Text Content
        self._updateIgnoredKeywords()
        self._build.setValue("text.includeBodyText", self.incBodyText.isChecked())
        self._build.setValue("text.includeSynopsis", self.incSynopsis.isChecked())
        self._build.setValue("text.includeComments", self.incComments.isChecked())
        self._build.setValue("text.includeKeywords", self.incKeywords.isChecked())
        self._build.setValue("text.ignoredKeywords", self.ignoredKeywords.text())
        self._build.setValue("text.addNoteHeadings", self.addNoteHead.isChecked())

        # Text Format
        self._build.setValue("format.textFont", self._textFont.toString())
        self._build.setValue("format.lineHeight", self.lineHeight.value())

        self._build.setValue("format.justifyText", self.justifyText.isChecked())
        self._build.setValue("format.stripUnicode", self.stripUnicode.isChecked())
        self._build.setValue("format.replaceTabs", self.replaceTabs.isChecked())
        self._build.setValue("format.keepBreaks", self.keepBreaks.isChecked())
        self._build.setValue("format.showDialogue", self.showDialogue.isChecked())

        # First Line Indent
        self._build.setValue("format.firstLineIndent", self.firstIndent.isChecked())
        self._build.setValue("format.firstIndentWidth", self.indentWidth.value())
        self._build.setValue("format.indentFirstPar", self.indentFirstPar.isChecked())

        # Text Margins
        self._build.setValue("format.titleMarginT", self.titleMarginT.value())
        self._build.setValue("format.titleMarginB", self.titleMarginB.value())
        self._build.setValue("format.h1MarginT", self.h1MarginT.value())
        self._build.setValue("format.h1MarginB", self.h1MarginB.value())
        self._build.setValue("format.h2MarginT", self.h2MarginT.value())
        self._build.setValue("format.h2MarginB", self.h2MarginB.value())
        self._build.setValue("format.h3MarginT", self.h3MarginT.value())
        self._build.setValue("format.h3MarginB", self.h3MarginB.value())
        self._build.setValue("format.h4MarginT", self.h4MarginT.value())
        self._build.setValue("format.h4MarginB", self.h4MarginB.value())
        self._build.setValue("format.textMarginT", self.textMarginT.value())
        self._build.setValue("format.textMarginB", self.textMarginB.value())
        self._build.setValue("format.sepMarginT", self.sepMarginT.value())
        self._build.setValue("format.sepMarginB", self.sepMarginB.value())

        # Page Layout
        self._build.setValue("format.pageUnit", str(self.pageUnit.currentData()))
        self._build.setValue("format.pageSize", str(self.pageSize.currentData()))
        self._build.setValue("format.pageWidth", self.pageWidth.value())
        self._build.setValue("format.pageHeight", self.pageHeight.value())
        self._build.setValue("format.topMargin", self.topMargin.value())
        self._build.setValue("format.bottomMargin", self.bottomMargin.value())
        self._build.setValue("format.leftMargin", self.leftMargin.value())
        self._build.setValue("format.rightMargin", self.rightMargin.value())

        # Documents
        self._build.setValue("doc.colorHeadings", self.colorHeadings.isChecked())
        self._build.setValue("doc.scaleHeadings", self.scaleHeadings.isChecked())
        self._build.setValue("doc.boldHeadings", self.boldHeadings.isChecked())
        self._build.setValue("doc.pageHeader", self.odtPageHeader.text())
        self._build.setValue("doc.pageCountOffset", self.odtPageCountOffset.value())

        # HTML Document
        self._build.setValue("html.addStyles", self.htmlAddStyles.isChecked())
        self._build.setValue("html.preserveTabs", self.htmlPreserveTabs.isChecked())

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _selectFont(self) -> None:
        """Open the QFontDialog and set a font for the font style."""
        font, status = SHARED.getFont(self._textFont, CONFIG.nativeFont)
        if status:
            self.textFont.setText(describeFont(font))
            self.textFont.setCursorPosition(0)
            self._textFont = font
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
    def _pageSizeValueChanged(self) -> None:
        """The user has changed the page size spin boxes, so we flip
        the page size box to Custom.
        """
        index = self.pageSize.findData("Custom")
        if index >= 0:
            self.pageSize.setCurrentIndex(index)
        return

    def _resetPageHeader(self) -> None:
        """Reset the ODT header format to default."""
        self.odtPageHeader.setText(nwHeadFmt.DOC_AUTO)
        self.odtPageHeader.setCursorPosition(0)
        return

    ##
    #  Internal Functions
    ##

    def _updateIgnoredKeywords(self, keyword: str | None = None) -> None:
        """Update the ignored keywords list."""
        current = [x.lower().strip() for x in self.ignoredKeywords.text().split(",")]
        if keyword:
            current.append(keyword)
        verified = set(x for x in current if x in nwKeyWords.VALID_KEYS)
        self.ignoredKeywords.setText(", ".join(verified))
        return
