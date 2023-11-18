"""
novelWriter – GUI Project Outline
=================================

File History:
Created: 2022-05-15 [2.0rc1] GuiOutlineView
Created: 2022-05-22 [2.0rc1] GuiOutlineToolBar
Created: 2019-11-16 [0.4.1]  GuiOutlineTree
Created: 2019-11-16 [0.4.1]  GuiOutlineHeaderMenu
Created: 2020-06-02 [0.7]    GuiOutlineDetails

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

from time import time
from enum import Enum

from PyQt5.QtCore import (
    Qt, pyqtSignal, pyqtSlot, QSize, QT_TRANSLATE_NOOP
)
from PyQt5.QtWidgets import (
    QAbstractItemView, QAction, QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QMenu, QScrollArea, QSizePolicy, QSplitter, QToolBar, QToolButton,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.enum import (
    nwDocMode, nwItemClass, nwItemLayout, nwItemType, nwOutline
)
from novelwriter.error import logException
from novelwriter.common import checkInt
from novelwriter.constants import nwHeaders, trConst, nwKeyWords, nwLabels
from novelwriter.extensions.novelselector import NovelSelector


logger = logging.getLogger(__name__)


class GuiOutlineView(QWidget):

    loadDocumentTagRequest = pyqtSignal(str, Enum)
    openDocumentRequest = pyqtSignal(str, Enum, str, bool)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        # Build GUI
        self.outlineTree = GuiOutlineTree(self)
        self.outlineData = GuiOutlineDetails(self)
        self.outlineBar = GuiOutlineToolBar(self)
        self.outlineBar.setEnabled(False)

        self.splitOutline = QSplitter(Qt.Vertical)
        self.splitOutline.addWidget(self.outlineTree)
        self.splitOutline.addWidget(self.outlineData)
        self.splitOutline.setOpaqueResize(False)
        self.splitOutline.setSizes(CONFIG.outlinePanePos)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setContentsMargins(0, 0, CONFIG.pxInt(4), 0)
        self.outerBox.addWidget(self.outlineBar)
        self.outerBox.addWidget(self.splitOutline)

        self.setLayout(self.outerBox)

        # Connect Signals
        self.outlineTree.hiddenStateChanged.connect(self._updateMenuColumns)
        self.outlineTree.activeItemChanged.connect(self.outlineData.showItem)
        self.outlineData.itemTagClicked.connect(self._tagClicked)
        self.outlineBar.loadNovelRootRequest.connect(self._rootItemChanged)
        self.outlineBar.viewColumnToggled.connect(self.outlineTree.menuColumnToggled)

        # Function Mappings
        self.getSelectedHandle = self.outlineTree.getSelectedHandle

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.outlineBar.updateTheme()
        self.refreshTree()
        return

    def initSettings(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        self.outlineTree.initSettings()
        self.outlineData.initSettings()
        return

    def refreshTree(self) -> None:
        """Refresh the current tree."""
        self.outlineTree.refreshTree(rootHandle=SHARED.project.data.getLastHandle("outline"))
        return

    def clearOutline(self) -> None:
        """Clear project-related GUI content."""
        self.outlineData.clearDetails()
        self.outlineBar.setEnabled(False)
        return

    def openProjectTasks(self) -> None:
        """Run open project tasks."""
        lastOutline = SHARED.project.data.getLastHandle("outline")
        if not (lastOutline is None or lastOutline in SHARED.project.tree):
            lastOutline = SHARED.project.tree.findRoot(nwItemClass.NOVEL)

        logger.debug("Setting outline tree to root item '%s'", lastOutline)

        self.clearOutline()
        self.outlineBar.populateNovelList()
        self.outlineBar.setCurrentRoot(lastOutline)
        self.outlineBar.setEnabled(True)

        return

    def closeProjectTasks(self) -> None:
        """Run closing project tasks."""
        self.outlineTree.closeProjectTasks()
        self.outlineData.updateClasses()
        self.clearOutline()
        return

    def splitSizes(self) -> list[int]:
        """Get the sizes of the splitter widget."""
        return self.splitOutline.sizes()

    def setTreeFocus(self) -> None:
        """Set the focus to the tree widget."""
        return self.outlineTree.setFocus()

    def treeHasFocus(self) -> bool:
        """Check if the outline tree has focus."""
        return self.outlineTree.hasFocus()

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def updateRootItem(self, tHandle: str) -> None:
        """Handle tasks whenever a root folders changes."""
        self.outlineBar.populateNovelList()
        self.outlineData.updateClasses()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _updateMenuColumns(self) -> None:
        """Trigger an update of the toggled state of the column menu
        checkboxes whenever a signal is received that the hidden state
        of columns has changed.
        """
        self.outlineBar.setColumnHiddenState(self.outlineTree.hiddenColumns)
        return

    @pyqtSlot(str)
    def _tagClicked(self, link: str) -> None:
        """Capture the click of a tag in the details panel."""
        if link:
            self.loadDocumentTagRequest.emit(link, nwDocMode.VIEW)
        return

    @pyqtSlot(str)
    def _rootItemChanged(self, tHandle) -> None:
        """Handle root novel changed or needs to be refreshed."""
        self.outlineTree.refreshTree(rootHandle=(tHandle or None), overRide=True)
        return

# END Class GuiOutlineView


class GuiOutlineToolBar(QToolBar):

    loadNovelRootRequest = pyqtSignal(str)
    viewColumnToggled = pyqtSignal(bool, Enum)

    def __init__(self, outlineView: GuiOutlineView) -> None:
        super().__init__(parent=outlineView)

        logger.debug("Create: GuiOutlineToolBar")

        iPx = CONFIG.pxInt(22)
        mPx = CONFIG.pxInt(12)

        self.setMovable(False)
        self.setIconSize(QSize(iPx, iPx))
        self.setContentsMargins(0, 0, 0, 0)

        stretch = QWidget(self)
        stretch.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Novel Selector
        self.novelLabel = QLabel(self.tr("Outline of"))
        self.novelLabel.setContentsMargins(0, 0, mPx, 0)

        self.novelValue = NovelSelector(self)
        self.novelValue.setMinimumWidth(CONFIG.pxInt(200))
        self.novelValue.novelSelectionChanged.connect(self._novelValueChanged)

        # Actions
        self.aRefresh = QAction(self.tr("Refresh"), self)
        self.aRefresh.triggered.connect(self._refreshRequested)

        # Column Menu
        self.mColumns = GuiOutlineHeaderMenu(self)
        self.mColumns.columnToggled.connect(
            lambda isChecked, tItem: self.viewColumnToggled.emit(isChecked, tItem)
        )

        self.tbColumns = QToolButton(self)
        self.tbColumns.setMenu(self.mColumns)
        self.tbColumns.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        # Assemble
        self.addWidget(self.novelLabel)
        self.addWidget(self.novelValue)
        self.addSeparator()
        self.addAction(self.aRefresh)
        self.addWidget(self.tbColumns)
        self.addWidget(stretch)

        self.updateTheme()

        logger.debug("Ready: GuiOutlineToolBar")

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.setStyleSheet("QToolBar {border: 0px;}")
        self.novelValue.updateList(includeAll=True)
        self.aRefresh.setIcon(SHARED.theme.getIcon("refresh"))
        self.tbColumns.setIcon(SHARED.theme.getIcon("menu"))
        self.tbColumns.setStyleSheet("QToolButton::menu-indicator {image: none;}")
        return

    def populateNovelList(self) -> None:
        """Reload the content of the novel list."""
        self.novelValue.updateList(includeAll=True)
        return

    def setCurrentRoot(self, rootHandle: str | None) -> None:
        """Set the current active root handle."""
        self.novelValue.setHandle(rootHandle)
        return

    def setColumnHiddenState(self, hiddenState: dict[nwOutline, bool]) -> None:
        """Forward the change of column hidden states to the menu."""
        self.mColumns.setHiddenState(hiddenState)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(str)
    def _novelValueChanged(self, tHandle: str) -> None:
        """Emit a signal containing the handle of the selected item."""
        self.loadNovelRootRequest.emit(tHandle)
        return

    @pyqtSlot()
    def _refreshRequested(self) -> None:
        """Emit a signal containing the handle of the selected item."""
        self.loadNovelRootRequest.emit(self.novelValue.handle)
        return

# END Class GuiOutlineToolBar


class GuiOutlineTree(QTreeWidget):

    DEF_WIDTH = {
        nwOutline.TITLE:  200,
        nwOutline.LEVEL:  40,
        nwOutline.LABEL:  150,
        nwOutline.LINE:   40,
        nwOutline.CCOUNT: 50,
        nwOutline.WCOUNT: 50,
        nwOutline.PCOUNT: 50,
        nwOutline.POV:    100,
        nwOutline.FOCUS:  100,
        nwOutline.CHAR:   100,
        nwOutline.PLOT:   100,
        nwOutline.TIME:   100,
        nwOutline.WORLD:  100,
        nwOutline.OBJECT: 100,
        nwOutline.ENTITY: 100,
        nwOutline.CUSTOM: 100,
        nwOutline.SYNOP:  200,
    }

    DEF_HIDDEN = {
        nwOutline.TITLE:  False,
        nwOutline.LEVEL:  True,
        nwOutline.LABEL:  False,
        nwOutline.LINE:   True,
        nwOutline.CCOUNT: True,
        nwOutline.WCOUNT: False,
        nwOutline.PCOUNT: False,
        nwOutline.POV:    False,
        nwOutline.FOCUS:  True,
        nwOutline.CHAR:   False,
        nwOutline.PLOT:   False,
        nwOutline.TIME:   True,
        nwOutline.WORLD:  False,
        nwOutline.OBJECT: True,
        nwOutline.ENTITY: True,
        nwOutline.CUSTOM: True,
        nwOutline.SYNOP:  False,
    }

    D_HANDLE = Qt.ItemDataRole.UserRole
    D_TITLE  = Qt.ItemDataRole.UserRole + 1

    hiddenStateChanged = pyqtSignal()
    activeItemChanged = pyqtSignal(str, str)

    def __init__(self, outlineView: GuiOutlineView) -> None:
        super().__init__(parent=outlineView)

        logger.debug("Create: GuiOutlineTree")

        self.outlineView = outlineView

        self.setUniformRowHeights(True)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setExpandsOnDoubleClick(False)
        self.setDragEnabled(False)
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._itemSelected)

        iPx = SHARED.theme.baseIconSize
        self.setIconSize(QSize(iPx, iPx))
        self.setIndentation(0)

        self.treeHead = self.header()
        self.treeHead.sectionMoved.connect(self._columnMoved)

        # Pre-Generate Tree Formatting
        fH1 = self.font()
        fH1.setBold(True)
        fH1.setUnderline(True)

        fH2 = self.font()
        fH2.setBold(True)

        iType = nwItemType.FILE
        iClass = nwItemClass.NO_CLASS
        iLayout = nwItemLayout.DOCUMENT

        self._hFonts = [self.font(), fH1, fH2, self.font(), self.font()]
        self._dIcon = {
            "H0": SHARED.theme.getItemIcon(iType, iClass, iLayout, "H0"),
            "H1": SHARED.theme.getItemIcon(iType, iClass, iLayout, "H1"),
            "H2": SHARED.theme.getItemIcon(iType, iClass, iLayout, "H2"),
            "H3": SHARED.theme.getItemIcon(iType, iClass, iLayout, "H3"),
            "H4": SHARED.theme.getItemIcon(iType, iClass, iLayout, "H4"),
        }

        # Internals
        self._treeOrder = []
        self._colWidth  = {}
        self._colHidden = {}
        self._colIdx    = {}
        self._treeNCols = 0
        self._firstView = True
        self._lastBuild = 0

        self.initSettings()
        self.clearContent()

        self.hiddenStateChanged.emit()

        logger.debug("Ready: GuiOutlineTree")

        return

    ##
    #  Properties
    ##

    @property
    def hiddenColumns(self):
        return self._colHidden

    ##
    #  Methods
    ##

    def initSettings(self) -> None:
        """Set or update outline settings."""
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        return

    def clearContent(self) -> None:
        """Clear the tree and header and set the default values for the
        columns arrays.
        """
        self.clear()
        self.setColumnCount(1)
        self.setHeaderLabel(trConst(nwLabels.OUTLINE_COLS[nwOutline.TITLE]))

        self._treeOrder: list[nwOutline] = []
        self._colWidth:  dict[nwOutline, int] = {}
        self._colHidden: dict[nwOutline, bool] = {}
        self._colIdx:    dict[nwOutline, int] = {}
        self._treeNCols = 0

        for hItem in nwOutline:
            self._treeOrder.append(hItem)
            self._colWidth[hItem] = self.DEF_WIDTH[hItem]
            self._colHidden[hItem] = self.DEF_HIDDEN[hItem]

        self._treeNCols = len(self._treeOrder)

        return

    def refreshTree(self, rootHandle: str | None = None,
                    overRide: bool = False, novelChanged: bool = False) -> None:
        """Called whenever the Outline tab is activated and controls
        what data to load, and if necessary, force a rebuild of the
        tree.
        """
        # If it's the first time, we always build
        if self._firstView or self._firstView and overRide:
            self._loadHeaderState()
            self._populateTree(rootHandle)
            self._firstView = False
            return

        # If the novel index or novel tree has changed since the tree
        # was last built, we rebuild the tree from the updated index.
        indexChanged = SHARED.project.index.rootChangedSince(rootHandle, self._lastBuild)
        if not (novelChanged or indexChanged or overRide):
            logger.debug("No changes have been made to the novel index")
            return

        self._populateTree(rootHandle)
        SHARED.project.data.setLastHandle(rootHandle or None, "outline")

        return

    def closeProjectTasks(self) -> None:
        """Called before a project is closed."""
        self._saveHeaderState()
        self.clearContent()
        self._firstView = True
        return

    def getSelectedHandle(self) -> tuple[str | None, str | None]:
        """Get the currently selected handle. If multiple items are
        selected, return the first.
        """
        selItem = self.selectedItems()
        if selItem:
            tHandle = selItem[0].data(self._colIdx[nwOutline.TITLE], self.D_HANDLE)
            sTitle = selItem[0].data(self._colIdx[nwOutline.TITLE], self.D_TITLE)
            return tHandle, sTitle
        return None, None

    ##
    #  Slots
    ##

    @pyqtSlot("QTreeWidgetItem*", int)
    def _treeDoubleClick(self, tItem: QTreeWidgetItem, tCol: int) -> None:
        """Extract the handle and line number of the title double-
        clicked, and send it to the main gui class for opening in the
        document editor.
        """
        tHandle, sTitle = self.getSelectedHandle()
        if tHandle is None:
            return
        self.outlineView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, sTitle or "", True)
        return

    @pyqtSlot()
    def _itemSelected(self) -> None:
        """Extract the handle and line number of the currently selected
        title, and send it to the details panel.
        """
        selItems = self.selectedItems()
        if selItems:
            tHandle = selItems[0].data(self._colIdx[nwOutline.TITLE], self.D_HANDLE)
            sTitle = selItems[0].data(self._colIdx[nwOutline.TITLE], self.D_TITLE)
            self.activeItemChanged.emit(tHandle, sTitle)
        return

    @pyqtSlot(int, int, int)
    def _columnMoved(self, logIdx: int, oldVisualIdx: int, newVisualIdx: int) -> None:
        """Make sure the order array is up to date with the actual order
        of the columns.
        """
        self._treeOrder.insert(newVisualIdx, self._treeOrder.pop(oldVisualIdx))
        self._saveHeaderState()
        return

    @pyqtSlot(bool, Enum)
    def menuColumnToggled(self, isChecked: bool, hItem: nwOutline) -> None:
        """Receive the changes to column visibility forwarded by the
        column selection menu.
        """
        if hItem in self._colIdx:
            self.setColumnHidden(self._colIdx[hItem], not isChecked)
            self._saveHeaderState()
        return

    ##
    #  Internal Functions
    ##

    def _loadHeaderState(self):
        """Load the state of the main tree header, that is, column order
        and column width.
        """
        # Load whatever we saved last time, regardless of whether it
        # contains the correct names or number of columns.
        colState = SHARED.project.options.getValue("GuiOutline", "columnState", {})

        tmpOrder = []
        tmpHidden = {}
        tmpWidth = {}
        try:
            for name, (hidden, width) in colState.items():
                if name not in nwOutline.__members__:
                    logger.warning("Ignored unknown outline column '%s'", str(name))
                    continue
                tmpOrder.append(nwOutline[name])
                tmpHidden[nwOutline[name]] = hidden
                tmpWidth[nwOutline[name]] = CONFIG.pxInt(width)
        except Exception:
            logger.error("Invalid column state")
            logException()

        # Add columns that was not in the file to the treeOrder array.
        for hItem in nwOutline:
            if hItem not in tmpOrder:
                tmpOrder.append(hItem)

        self._treeOrder = tmpOrder
        self._colHidden.update(tmpHidden)
        self._colWidth.update(tmpWidth)

        self.hiddenStateChanged.emit()

        return

    def _saveHeaderState(self) -> None:
        """Save the state of the main tree header, that is, column
        order, column width and column hidden state. We don't want to
        save the current width of hidden columns though. This preserves
        the last known width in case they're unhidden again.
        """
        # If we haven't built the tree, there is nothing to save.
        if self._lastBuild == 0:
            return

        colState = {}
        for iCol in range(self.columnCount()):
            hItem = self._treeOrder[iCol]
            iLog = self.treeHead.logicalIndex(iCol)
            logHidden = self.isColumnHidden(iLog)
            orgWidth = CONFIG.rpxInt(self._colWidth[hItem])
            logWidth = CONFIG.rpxInt(self.columnWidth(iLog))
            colState[hItem.name] = [
                logHidden, orgWidth if logHidden and logWidth == 0 else logWidth
            ]

        pOptions = SHARED.project.options
        pOptions.setValue("GuiOutline", "columnState", colState)
        pOptions.saveSettings()

        return

    def _populateTree(self, rootHandle: str | None) -> None:
        """Build the tree based on the project index, and the header
        based on the defined constants, default values and user selected
        width, order and hidden state. All columns are populated, even
        if they are hidden. This ensures that showing and hiding columns
        is fast and doesn't require a rebuild of the tree.
        """
        logger.debug("Rebuilding Outline tree")
        self.clear()

        if self._firstView:
            theLabels = []
            for i, hItem in enumerate(self._treeOrder):
                theLabels.append(trConst(nwLabels.OUTLINE_COLS[hItem]))
                self._colIdx[hItem] = i

            self.setHeaderLabels(theLabels)
            for hItem in self._treeOrder:
                self.setColumnWidth(self._colIdx[hItem], self._colWidth[hItem])
                self.setColumnHidden(self._colIdx[hItem], self._colHidden[hItem])

            # Make sure title column is always visible
            self.setColumnHidden(self._colIdx[nwOutline.TITLE], False)

            headItem = self.headerItem()
            if isinstance(headItem, QTreeWidgetItem):
                headItem.setTextAlignment(
                    self._colIdx[nwOutline.CCOUNT], Qt.AlignmentFlag.AlignRight)
                headItem.setTextAlignment(
                    self._colIdx[nwOutline.WCOUNT], Qt.AlignmentFlag.AlignRight)
                headItem.setTextAlignment(
                    self._colIdx[nwOutline.PCOUNT], Qt.AlignmentFlag.AlignRight)

        novStruct = SHARED.project.index.novelStructure(rootHandle=rootHandle, skipExcl=True)
        for _, tHandle, sTitle, novIdx in novStruct:

            iLevel = nwHeaders.H_LEVEL.get(novIdx.level, 0)
            nwItem = SHARED.project.tree[tHandle]
            if iLevel == 0 or nwItem is None:
                continue

            trItem = QTreeWidgetItem()
            hDec = SHARED.theme.getHeaderDecoration(iLevel)

            trItem.setData(self._colIdx[nwOutline.TITLE], Qt.ItemDataRole.DecorationRole, hDec)
            trItem.setText(self._colIdx[nwOutline.TITLE], novIdx.title)
            trItem.setData(self._colIdx[nwOutline.TITLE], self.D_HANDLE, tHandle)
            trItem.setData(self._colIdx[nwOutline.TITLE], self.D_TITLE, sTitle)
            trItem.setFont(self._colIdx[nwOutline.TITLE], self._hFonts[iLevel])
            trItem.setText(self._colIdx[nwOutline.LEVEL], novIdx.level)
            trItem.setIcon(self._colIdx[nwOutline.LABEL], self._dIcon[nwItem.mainHeading])
            trItem.setText(self._colIdx[nwOutline.LABEL], nwItem.itemName)
            trItem.setText(self._colIdx[nwOutline.LINE], f"{novIdx.line:n}")
            trItem.setText(self._colIdx[nwOutline.SYNOP], novIdx.synopsis)
            trItem.setText(self._colIdx[nwOutline.CCOUNT], f"{novIdx.charCount:n}")
            trItem.setText(self._colIdx[nwOutline.WCOUNT], f"{novIdx.wordCount:n}")
            trItem.setText(self._colIdx[nwOutline.PCOUNT], f"{novIdx.paraCount:n}")
            trItem.setTextAlignment(self._colIdx[nwOutline.CCOUNT], Qt.AlignmentFlag.AlignRight)
            trItem.setTextAlignment(self._colIdx[nwOutline.WCOUNT], Qt.AlignmentFlag.AlignRight)
            trItem.setTextAlignment(self._colIdx[nwOutline.PCOUNT], Qt.AlignmentFlag.AlignRight)

            refs = SHARED.project.index.getReferences(tHandle, sTitle)
            trItem.setText(self._colIdx[nwOutline.POV],    ", ".join(refs[nwKeyWords.POV_KEY]))
            trItem.setText(self._colIdx[nwOutline.FOCUS],  ", ".join(refs[nwKeyWords.FOCUS_KEY]))
            trItem.setText(self._colIdx[nwOutline.CHAR],   ", ".join(refs[nwKeyWords.CHAR_KEY]))
            trItem.setText(self._colIdx[nwOutline.PLOT],   ", ".join(refs[nwKeyWords.PLOT_KEY]))
            trItem.setText(self._colIdx[nwOutline.TIME],   ", ".join(refs[nwKeyWords.TIME_KEY]))
            trItem.setText(self._colIdx[nwOutline.WORLD],  ", ".join(refs[nwKeyWords.WORLD_KEY]))
            trItem.setText(self._colIdx[nwOutline.OBJECT], ", ".join(refs[nwKeyWords.OBJECT_KEY]))
            trItem.setText(self._colIdx[nwOutline.ENTITY], ", ".join(refs[nwKeyWords.ENTITY_KEY]))
            trItem.setText(self._colIdx[nwOutline.CUSTOM], ", ".join(refs[nwKeyWords.CUSTOM_KEY]))

            self.addTopLevelItem(trItem)

        self._lastBuild = time()

        return

# END Class GuiOutlineTree


class GuiOutlineHeaderMenu(QMenu):

    columnToggled = pyqtSignal(bool, Enum)

    def __init__(self, outlineToolBar: GuiOutlineToolBar) -> None:
        super().__init__(parent=outlineToolBar)

        self.acceptToggle = True

        mnuHead = QAction(self.tr("Select Columns"), self)
        self.addAction(mnuHead)
        self.addSeparator()

        self.actionMap = {}
        for hItem in nwOutline:
            if hItem == nwOutline.TITLE:
                continue
            self.actionMap[hItem] = QAction(trConst(nwLabels.OUTLINE_COLS[hItem]), self)
            self.actionMap[hItem].setCheckable(True)
            self.actionMap[hItem].toggled.connect(
                lambda isChecked, tItem=hItem: self.columnToggled.emit(isChecked, tItem)
            )
            self.addAction(self.actionMap[hItem])

        return

    def setHiddenState(self, hiddenState: dict[nwOutline, bool]) -> None:
        """Overwrite the checked state of the columns as the inverse of
        the hidden state. Skip the TITLE column as it cannot be hidden.
        """
        self.acceptToggle = False

        for hItem in nwOutline:
            if hItem == nwOutline.TITLE or hItem not in hiddenState:
                continue
            self.actionMap[hItem].setChecked(not hiddenState[hItem])

        self.acceptToggle = True

        return

# END Class GuiOutlineHeaderMenu


class GuiOutlineDetails(QScrollArea):

    LVL_MAP = {
        "H1": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Title"),
        "H2": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Chapter"),
        "H3": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Scene"),
        "H4": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Section"),
    }

    itemTagClicked = pyqtSignal(str)

    def __init__(self, outlineView: GuiOutlineView) -> None:
        super().__init__(parent=outlineView)

        logger.debug("Create: GuiOutlineDetails")

        self.outlineView = outlineView

        # Sizes
        minTitle = 30*SHARED.theme.textNWidth
        maxTitle = 40*SHARED.theme.textNWidth
        wCount = SHARED.theme.getTextWidth("999,999")
        hSpace = int(CONFIG.pxInt(10))
        vSpace = int(CONFIG.pxInt(4))

        # Details Area
        self.titleLabel = QLabel("<b>%s</b>" % self.tr("Title"))
        self.fileLabel  = QLabel("<b>%s</b>" % self.tr("Document"))
        self.itemLabel  = QLabel("<b>%s</b>" % self.tr("Status"))
        self.titleValue = QLabel("")
        self.fileValue  = QLabel("")
        self.itemValue  = QLabel("")

        self.titleValue.setMinimumWidth(minTitle)
        self.titleValue.setMaximumWidth(maxTitle)
        self.fileValue.setMinimumWidth(minTitle)
        self.fileValue.setMaximumWidth(maxTitle)
        self.itemValue.setMinimumWidth(minTitle)
        self.itemValue.setMaximumWidth(maxTitle)

        # Stats Area
        self.cCLabel = QLabel("<b>%s</b>" % self.tr("Characters"))
        self.wCLabel = QLabel("<b>%s</b>" % self.tr("Words"))
        self.pCLabel = QLabel("<b>%s</b>" % self.tr("Paragraphs"))
        self.cCValue = QLabel("")
        self.wCValue = QLabel("")
        self.pCValue = QLabel("")

        self.cCValue.setMinimumWidth(wCount)
        self.wCValue.setMinimumWidth(wCount)
        self.pCValue.setMinimumWidth(wCount)
        self.cCValue.setAlignment(Qt.AlignRight)
        self.wCValue.setAlignment(Qt.AlignRight)
        self.pCValue.setAlignment(Qt.AlignRight)

        # Synopsis
        self.synopLabel = QLabel("<b>%s</b>" % self.tr("Synopsis"))
        self.synopValue = QLabel("")
        self.synopLWrap = QHBoxLayout()
        self.synopValue.setWordWrap(True)
        self.synopValue.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.synopLWrap.addWidget(self.synopValue, 1)

        # Tags
        self.povKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.POV_KEY]))
        self.focKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.FOCUS_KEY]))
        self.chrKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.CHAR_KEY]))
        self.pltKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY]))
        self.timKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.TIME_KEY]))
        self.wldKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.WORLD_KEY]))
        self.objKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.OBJECT_KEY]))
        self.entKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.ENTITY_KEY]))
        self.cstKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.CUSTOM_KEY]))

        self.povKeyLWrap = QHBoxLayout()
        self.focKeyLWrap = QHBoxLayout()
        self.chrKeyLWrap = QHBoxLayout()
        self.pltKeyLWrap = QHBoxLayout()
        self.timKeyLWrap = QHBoxLayout()
        self.wldKeyLWrap = QHBoxLayout()
        self.objKeyLWrap = QHBoxLayout()
        self.entKeyLWrap = QHBoxLayout()
        self.cstKeyLWrap = QHBoxLayout()

        self.povKeyValue = QLabel("")
        self.focKeyValue = QLabel("")
        self.chrKeyValue = QLabel("")
        self.pltKeyValue = QLabel("")
        self.timKeyValue = QLabel("")
        self.wldKeyValue = QLabel("")
        self.objKeyValue = QLabel("")
        self.entKeyValue = QLabel("")
        self.cstKeyValue = QLabel("")

        self.povKeyValue.setWordWrap(True)
        self.focKeyValue.setWordWrap(True)
        self.chrKeyValue.setWordWrap(True)
        self.pltKeyValue.setWordWrap(True)
        self.timKeyValue.setWordWrap(True)
        self.wldKeyValue.setWordWrap(True)
        self.objKeyValue.setWordWrap(True)
        self.entKeyValue.setWordWrap(True)
        self.cstKeyValue.setWordWrap(True)

        def tagClicked(link):
            self.itemTagClicked.emit(link)

        self.povKeyValue.linkActivated.connect(tagClicked)
        self.focKeyValue.linkActivated.connect(tagClicked)
        self.chrKeyValue.linkActivated.connect(tagClicked)
        self.pltKeyValue.linkActivated.connect(tagClicked)
        self.timKeyValue.linkActivated.connect(tagClicked)
        self.wldKeyValue.linkActivated.connect(tagClicked)
        self.objKeyValue.linkActivated.connect(tagClicked)
        self.entKeyValue.linkActivated.connect(tagClicked)
        self.cstKeyValue.linkActivated.connect(tagClicked)

        self.povKeyLWrap.addWidget(self.povKeyValue, 1)
        self.focKeyLWrap.addWidget(self.focKeyValue, 1)
        self.chrKeyLWrap.addWidget(self.chrKeyValue, 1)
        self.pltKeyLWrap.addWidget(self.pltKeyValue, 1)
        self.timKeyLWrap.addWidget(self.timKeyValue, 1)
        self.wldKeyLWrap.addWidget(self.wldKeyValue, 1)
        self.objKeyLWrap.addWidget(self.objKeyValue, 1)
        self.entKeyLWrap.addWidget(self.entKeyValue, 1)
        self.cstKeyLWrap.addWidget(self.cstKeyValue, 1)

        # Selected Item Details
        self.mainGroup = QGroupBox(self.tr("Title Details"), self)
        self.mainForm = QGridLayout()
        self.mainGroup.setLayout(self.mainForm)

        topLeft = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        topRight = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight

        self.mainForm.addWidget(self.titleLabel,  0, 0, 1, 1, topLeft)
        self.mainForm.addWidget(self.titleValue,  0, 1, 1, 1, topLeft)
        self.mainForm.addWidget(self.cCLabel,     0, 2, 1, 1, topLeft)
        self.mainForm.addWidget(self.cCValue,     0, 3, 1, 1, topRight)
        self.mainForm.addWidget(self.fileLabel,   1, 0, 1, 1, topLeft)
        self.mainForm.addWidget(self.fileValue,   1, 1, 1, 1, topLeft)
        self.mainForm.addWidget(self.wCLabel,     1, 2, 1, 1, topLeft)
        self.mainForm.addWidget(self.wCValue,     1, 3, 1, 1, topRight)
        self.mainForm.addWidget(self.itemLabel,   2, 0, 1, 1, topLeft)
        self.mainForm.addWidget(self.itemValue,   2, 1, 1, 1, topLeft)
        self.mainForm.addWidget(self.pCLabel,     2, 2, 1, 1, topLeft)
        self.mainForm.addWidget(self.pCValue,     2, 3, 1, 1, topRight)
        self.mainForm.addWidget(self.synopLabel,  3, 0, 1, 4, topLeft)
        self.mainForm.addLayout(self.synopLWrap,  4, 0, 1, 4, topLeft)

        self.mainForm.setColumnStretch(1, 1)
        self.mainForm.setRowStretch(4, 1)
        self.mainForm.setHorizontalSpacing(hSpace)
        self.mainForm.setVerticalSpacing(vSpace)

        # Selected Item Tags
        self.tagsGroup = QGroupBox(self.tr("Reference Tags"), self)
        self.tagsForm = QGridLayout()
        self.tagsGroup.setLayout(self.tagsForm)

        self.tagsForm.addWidget(self.povKeyLabel, 0, 0, 1, 1, topLeft)
        self.tagsForm.addLayout(self.povKeyLWrap, 0, 1, 1, 1, topLeft)
        self.tagsForm.addWidget(self.focKeyLabel, 1, 0, 1, 1, topLeft)
        self.tagsForm.addLayout(self.focKeyLWrap, 1, 1, 1, 1, topLeft)
        self.tagsForm.addWidget(self.chrKeyLabel, 2, 0, 1, 1, topLeft)
        self.tagsForm.addLayout(self.chrKeyLWrap, 2, 1, 1, 1, topLeft)
        self.tagsForm.addWidget(self.pltKeyLabel, 3, 0, 1, 1, topLeft)
        self.tagsForm.addLayout(self.pltKeyLWrap, 3, 1, 1, 1, topLeft)
        self.tagsForm.addWidget(self.timKeyLabel, 4, 0, 1, 1, topLeft)
        self.tagsForm.addLayout(self.timKeyLWrap, 4, 1, 1, 1, topLeft)
        self.tagsForm.addWidget(self.wldKeyLabel, 5, 0, 1, 1, topLeft)
        self.tagsForm.addLayout(self.wldKeyLWrap, 5, 1, 1, 1, topLeft)
        self.tagsForm.addWidget(self.objKeyLabel, 6, 0, 1, 1, topLeft)
        self.tagsForm.addLayout(self.objKeyLWrap, 6, 1, 1, 1, topLeft)
        self.tagsForm.addWidget(self.entKeyLabel, 7, 0, 1, 1, topLeft)
        self.tagsForm.addLayout(self.entKeyLWrap, 7, 1, 1, 1, topLeft)
        self.tagsForm.addWidget(self.cstKeyLabel, 8, 0, 1, 1, topLeft)
        self.tagsForm.addLayout(self.cstKeyLWrap, 8, 1, 1, 1, topLeft)

        self.tagsForm.setColumnStretch(1, 1)
        self.tagsForm.setRowStretch(8, 1)
        self.tagsForm.setHorizontalSpacing(hSpace)
        self.tagsForm.setVerticalSpacing(vSpace)

        # Assemble
        self.outerWidget = QWidget()
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.mainGroup, 0)
        self.outerBox.addWidget(self.tagsGroup, 1)

        self.outerWidget.setLayout(self.outerBox)
        self.setWidget(self.outerWidget)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setFrameStyle(QFrame.Shape.NoFrame)

        self.initSettings()

        logger.debug("Ready: GuiOutlineDetails")

        return

    def initSettings(self) -> None:
        """Set or update outline settings."""
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.updateClasses()
        return

    def clearDetails(self) -> None:
        """Clear all the data labels."""
        self.titleLabel.setText("<b>%s</b>" % self.tr("Title"))
        self.titleValue.setText("")
        self.fileValue.setText("")
        self.itemValue.setText("")
        self.cCValue.setText("")
        self.wCValue.setText("")
        self.pCValue.setText("")
        self.synopValue.setText("")
        self.povKeyValue.setText("")
        self.focKeyValue.setText("")
        self.chrKeyValue.setText("")
        self.pltKeyValue.setText("")
        self.timKeyValue.setText("")
        self.wldKeyValue.setText("")
        self.objKeyValue.setText("")
        self.entKeyValue.setText("")
        self.cstKeyValue.setText("")
        self.updateClasses()
        return

    ##
    #  Slots
    ##

    @pyqtSlot(str, str)
    def showItem(self, tHandle: str, sTitle: str) -> bool:
        """Update the content of the tree with the given handle and line
        number pointing to a header.
        """
        pIndex = SHARED.project.index
        nwItem = SHARED.project.tree[tHandle]
        novIdx = pIndex.getItemHeader(tHandle, sTitle)
        theRefs = pIndex.getReferences(tHandle, sTitle)
        if nwItem is None or novIdx is None:
            return False

        if novIdx.level in self.LVL_MAP:
            self.titleLabel.setText("<b>%s</b>" % self.tr(self.LVL_MAP[novIdx.level]))
        else:
            self.titleLabel.setText("<b>%s</b>" % self.tr("Title"))
        self.titleValue.setText(novIdx.title)

        itemStatus, _ = nwItem.getImportStatus(incIcon=False)

        self.fileValue.setText(nwItem.itemName)
        self.itemValue.setText(itemStatus)

        cC = checkInt(novIdx.charCount, 0)
        wC = checkInt(novIdx.wordCount, 0)
        pC = checkInt(novIdx.paraCount, 0)

        self.cCValue.setText(f"{cC:n}")
        self.wCValue.setText(f"{wC:n}")
        self.pCValue.setText(f"{pC:n}")

        self.synopValue.setText(novIdx.synopsis)

        self.povKeyValue.setText(self._formatTags(theRefs, nwKeyWords.POV_KEY))
        self.focKeyValue.setText(self._formatTags(theRefs, nwKeyWords.FOCUS_KEY))
        self.chrKeyValue.setText(self._formatTags(theRefs, nwKeyWords.CHAR_KEY))
        self.pltKeyValue.setText(self._formatTags(theRefs, nwKeyWords.PLOT_KEY))
        self.timKeyValue.setText(self._formatTags(theRefs, nwKeyWords.TIME_KEY))
        self.wldKeyValue.setText(self._formatTags(theRefs, nwKeyWords.WORLD_KEY))
        self.objKeyValue.setText(self._formatTags(theRefs, nwKeyWords.OBJECT_KEY))
        self.entKeyValue.setText(self._formatTags(theRefs, nwKeyWords.ENTITY_KEY))
        self.cstKeyValue.setText(self._formatTags(theRefs, nwKeyWords.CUSTOM_KEY))

        return True

    @pyqtSlot()
    def updateClasses(self) -> None:
        """Update the visibility status of class details."""
        usedClasses = SHARED.project.tree.rootClasses()

        pltVisible = nwItemClass.PLOT in usedClasses
        timVisible = nwItemClass.TIMELINE in usedClasses
        wldVisible = nwItemClass.WORLD in usedClasses
        objVisible = nwItemClass.OBJECT in usedClasses
        entVisible = nwItemClass.ENTITY in usedClasses
        cstVisible = nwItemClass.CUSTOM in usedClasses

        self.pltKeyLabel.setVisible(pltVisible)
        self.pltKeyValue.setVisible(pltVisible)
        self.timKeyLabel.setVisible(timVisible)
        self.timKeyValue.setVisible(timVisible)
        self.wldKeyLabel.setVisible(wldVisible)
        self.wldKeyValue.setVisible(wldVisible)
        self.objKeyLabel.setVisible(objVisible)
        self.objKeyValue.setVisible(objVisible)
        self.entKeyLabel.setVisible(entVisible)
        self.entKeyValue.setVisible(entVisible)
        self.cstKeyLabel.setVisible(cstVisible)
        self.cstKeyValue.setVisible(cstVisible)

        return

    @staticmethod
    def _formatTags(refs: dict[str, list[str]], key: str) -> str:
        """Convert a list of tags into a list of clickable tag links."""
        return ", ".join(
            [f"<a href='{tag}'>{tag}</a>" for tag in refs.get(key, [])]
        )

# END Class GuiOutlineDetails
