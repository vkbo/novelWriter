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

import csv
import logging

from enum import Enum
from time import time

from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView, QAction, QFileDialog, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QMenu, QScrollArea, QSplitter, QToolBar, QToolButton,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import checkInt, formatFileFilter, makeFileNameSafe
from novelwriter.constants import nwKeyWords, nwLabels, nwStats, nwStyles, trConst
from novelwriter.enum import nwDocMode, nwItemClass, nwItemLayout, nwItemType, nwOutline
from novelwriter.error import logException
from novelwriter.extensions.configlayout import NColourLabel
from novelwriter.extensions.novelselector import NovelSelector
from novelwriter.types import (
    QtAlignLeftTop, QtAlignRight, QtAlignRightTop, QtDecoration,
    QtScrollAlwaysOff, QtScrollAsNeeded, QtSizeExpanding, QtUserRole
)

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

        self.splitOutline = QSplitter(Qt.Orientation.Vertical, self)
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
        self.outlineBar.outlineExportRequest.connect(self.outlineTree.exportOutline)

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
        if not lastOutline or lastOutline not in SHARED.project.tree:
            lastOutline = SHARED.project.tree.findRoot(nwItemClass.NOVEL)

        logger.debug("Setting outline tree to root item '%s'", lastOutline)

        self.clearOutline()
        self.outlineBar.populateNovelList()
        self.outlineBar.setCurrentRoot(lastOutline)
        self.outlineBar.setEnabled(True)
        self.outlineData.loadGuiSettings()

        return

    def closeProjectTasks(self) -> None:
        """Run closing project tasks."""
        if self.outlineTree.wasRendered:
            # If the panel hasn't been drawn yet, those values are incorrect
            self.outlineData.saveGuiSettings()
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
    def _rootItemChanged(self, tHandle: str) -> None:
        """Handle root novel changed or needs to be refreshed."""
        self.outlineTree.refreshTree(rootHandle=(tHandle or None), overRide=True)
        return


class GuiOutlineToolBar(QToolBar):

    loadNovelRootRequest = pyqtSignal(str)
    outlineExportRequest = pyqtSignal()
    viewColumnToggled = pyqtSignal(bool, Enum)

    def __init__(self, outlineView: GuiOutlineView) -> None:
        super().__init__(parent=outlineView)

        logger.debug("Create: GuiOutlineToolBar")

        self.setMovable(False)
        self.setIconSize(1.4*SHARED.theme.baseIconSize)
        self.setContentsMargins(0, 0, 0, 0)

        stretch = QWidget(self)
        stretch.setSizePolicy(QtSizeExpanding, QtSizeExpanding)

        # Novel Selector
        self.novelLabel = NColourLabel(
            self.tr("Outline of"), self, scale=NColourLabel.HEADER_SCALE, bold=True
        )
        self.novelLabel.setContentsMargins(0, 0, CONFIG.pxInt(12), 0)

        self.novelValue = NovelSelector(self)
        self.novelValue.setIncludeAll(True)
        self.novelValue.setMinimumWidth(CONFIG.pxInt(200))
        self.novelValue.novelSelectionChanged.connect(self._novelValueChanged)

        # Actions
        self.aRefresh = QAction(self.tr("Refresh"), self)
        self.aRefresh.triggered.connect(self._refreshRequested)

        self.aExport = QAction(self.tr("Export CSV"), self)
        self.aExport.triggered.connect(self._exportRequested)

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
        self.addAction(self.aExport)
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
        self.novelValue.refreshNovelList()
        self.aRefresh.setIcon(SHARED.theme.getIcon("refresh"))
        self.aExport.setIcon(SHARED.theme.getIcon("export"))
        self.tbColumns.setIcon(SHARED.theme.getIcon("menu"))
        self.tbColumns.setStyleSheet("QToolButton::menu-indicator {image: none;}")
        self.novelLabel.setTextColors(color=self.palette().windowText().color())
        return

    def populateNovelList(self) -> None:
        """Reload the content of the novel list."""
        self.novelValue.refreshNovelList()
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

    @pyqtSlot()
    def _exportRequested(self) -> None:
        """Emit a signal that an export of the outline was requested."""
        self.outlineExportRequest.emit()
        return


class GuiOutlineTree(QTreeWidget):

    DEF_WIDTH = {
        nwOutline.TITLE:   200,
        nwOutline.LEVEL:   40,
        nwOutline.LABEL:   150,
        nwOutline.LINE:    40,
        nwOutline.STATUS:  100,
        nwOutline.CCOUNT:  50,
        nwOutline.WCOUNT:  50,
        nwOutline.PCOUNT:  50,
        nwOutline.POV:     100,
        nwOutline.FOCUS:   100,
        nwOutline.CHAR:    100,
        nwOutline.PLOT:    100,
        nwOutline.TIME:    100,
        nwOutline.WORLD:   100,
        nwOutline.OBJECT:  100,
        nwOutline.ENTITY:  100,
        nwOutline.CUSTOM:  100,
        nwOutline.STORY:   100,
        nwOutline.MENTION: 100,
        nwOutline.SYNOP:   200,
    }

    DEF_HIDDEN = {
        nwOutline.TITLE:   False,
        nwOutline.LEVEL:   True,
        nwOutline.LABEL:   False,
        nwOutline.LINE:    True,
        nwOutline.STATUS:  True,
        nwOutline.CCOUNT:  True,
        nwOutline.WCOUNT:  False,
        nwOutline.PCOUNT:  False,
        nwOutline.POV:     False,
        nwOutline.FOCUS:   True,
        nwOutline.CHAR:    False,
        nwOutline.PLOT:    False,
        nwOutline.TIME:    True,
        nwOutline.WORLD:   False,
        nwOutline.OBJECT:  True,
        nwOutline.ENTITY:  True,
        nwOutline.CUSTOM:  True,
        nwOutline.STORY:   True,
        nwOutline.MENTION: True,
        nwOutline.SYNOP:   False,
    }

    D_HANDLE = QtUserRole
    D_TITLE  = QtUserRole + 1

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

        self.setIconSize(SHARED.theme.baseIconSize)
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
    def hiddenColumns(self) -> dict[nwOutline, bool]:
        return self._colHidden

    @property
    def wasRendered(self) -> bool:
        """Returns True after the Outline has been rendered once."""
        return not self._firstView

    ##
    #  Methods
    ##

    def initSettings(self) -> None:
        """Set or update outline settings."""
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(QtScrollAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(QtScrollAsNeeded)
        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(QtScrollAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(QtScrollAsNeeded)
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

    def refreshTree(
        self, rootHandle: str | None = None,
        overRide: bool = False, novelChanged: bool = False
    ) -> None:
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
        if item := self.selectedItems():
            tHandle = item[0].data(self._colIdx[nwOutline.TITLE], self.D_HANDLE)
            sTitle = item[0].data(self._colIdx[nwOutline.TITLE], self.D_TITLE)
            return tHandle, sTitle
        return None, None

    ##
    #  Public Slots
    ##

    @pyqtSlot(bool, Enum)
    def menuColumnToggled(self, isChecked: bool, hItem: nwOutline) -> None:
        """Receive the changes to column visibility forwarded by the
        column selection menu.
        """
        if hItem in self._colIdx:
            self.setColumnHidden(self._colIdx[hItem], not isChecked)
            self._saveHeaderState()
        return

    @pyqtSlot()
    def exportOutline(self) -> None:
        """Export the outline as a CSV file."""
        path = CONFIG.lastPath("outline") / f"{makeFileNameSafe(SHARED.project.data.name)}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save Outline As"), str(path), formatFileFilter(["*.csv", "*"])
        )
        if path:
            CONFIG.setLastPath("outline", path)
            logger.info("Writing CSV file: %s", path)
            cols = [col for col in self._treeOrder if not self._colHidden[col]]
            order = [self._colIdx[col] for col in cols]
            with open(path, mode="w", newline="") as csvFile:
                writer = csv.writer(csvFile, dialect="excel", quoting=csv.QUOTE_ALL)
                writer.writerow([trConst(nwLabels.OUTLINE_COLS[col]) for col in cols])
                for i in range(self.topLevelItemCount()):
                    if item := self.topLevelItem(i):
                        writer.writerow(item.text(i) for i in order)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot("QTreeWidgetItem*", int)
    def _treeDoubleClick(self, tItem: QTreeWidgetItem, tCol: int) -> None:
        """Extract the handle and line number of the title double-
        clicked, and send it to the main gui class for opening in the
        document editor.
        """
        tHandle, sTitle = self.getSelectedHandle()
        if tHandle:
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

    ##
    #  Internal Functions
    ##

    def _loadHeaderState(self) -> None:
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

        logger.debug("Saving State: GuiOutline")
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
        tStart = time()
        self.clear()

        if self._firstView:
            labels = []
            for i, hItem in enumerate(self._treeOrder):
                labels.append(trConst(nwLabels.OUTLINE_COLS[hItem]))
                self._colIdx[hItem] = i

            self.setHeaderLabels(labels)
            for hItem in self._treeOrder:
                self.setColumnWidth(self._colIdx[hItem], self._colWidth[hItem])
                self.setColumnHidden(self._colIdx[hItem], self._colHidden[hItem])

            # Make sure title column is always visible
            self.setColumnHidden(self._colIdx[nwOutline.TITLE], False)

            headItem = self.headerItem()
            if isinstance(headItem, QTreeWidgetItem):
                headItem.setTextAlignment(
                    self._colIdx[nwOutline.CCOUNT], QtAlignRight)
                headItem.setTextAlignment(
                    self._colIdx[nwOutline.WCOUNT], QtAlignRight)
                headItem.setTextAlignment(
                    self._colIdx[nwOutline.PCOUNT], QtAlignRight)

        novStruct = SHARED.project.index.novelStructure(rootHandle=rootHandle, activeOnly=True)
        for _, tHandle, sTitle, novIdx in novStruct:

            iLevel = nwStyles.H_LEVEL.get(novIdx.level, 0)
            nwItem = SHARED.project.tree[tHandle]
            if iLevel == 0 or nwItem is None:
                continue
            sLabel, sIcon = nwItem.getImportStatus()

            item = QTreeWidgetItem()
            hDec = SHARED.theme.getHeaderDecoration(iLevel)

            item.setData(self._colIdx[nwOutline.TITLE], QtDecoration, hDec)
            item.setText(self._colIdx[nwOutline.TITLE], novIdx.title)
            item.setData(self._colIdx[nwOutline.TITLE], self.D_HANDLE, tHandle)
            item.setData(self._colIdx[nwOutline.TITLE], self.D_TITLE, sTitle)
            item.setFont(self._colIdx[nwOutline.TITLE], self._hFonts[iLevel])
            item.setText(self._colIdx[nwOutline.LEVEL], novIdx.level)
            item.setIcon(self._colIdx[nwOutline.LABEL], self._dIcon[nwItem.mainHeading])
            item.setText(self._colIdx[nwOutline.LABEL], nwItem.itemName)
            item.setText(self._colIdx[nwOutline.LINE], f"{novIdx.line:n}")
            item.setText(self._colIdx[nwOutline.STATUS], sLabel)
            item.setIcon(self._colIdx[nwOutline.STATUS], sIcon)
            item.setText(self._colIdx[nwOutline.SYNOP], novIdx.synopsis)
            item.setText(self._colIdx[nwOutline.CCOUNT], f"{novIdx.charCount:n}")
            item.setText(self._colIdx[nwOutline.WCOUNT], f"{novIdx.wordCount:n}")
            item.setText(self._colIdx[nwOutline.PCOUNT], f"{novIdx.paraCount:n}")
            item.setTextAlignment(self._colIdx[nwOutline.CCOUNT], QtAlignRight)
            item.setTextAlignment(self._colIdx[nwOutline.WCOUNT], QtAlignRight)
            item.setTextAlignment(self._colIdx[nwOutline.PCOUNT], QtAlignRight)

            refs = SHARED.project.index.getReferences(tHandle, sTitle)
            item.setText(self._colIdx[nwOutline.POV],     ", ".join(refs[nwKeyWords.POV_KEY]))
            item.setText(self._colIdx[nwOutline.FOCUS],   ", ".join(refs[nwKeyWords.FOCUS_KEY]))
            item.setText(self._colIdx[nwOutline.CHAR],    ", ".join(refs[nwKeyWords.CHAR_KEY]))
            item.setText(self._colIdx[nwOutline.PLOT],    ", ".join(refs[nwKeyWords.PLOT_KEY]))
            item.setText(self._colIdx[nwOutline.TIME],    ", ".join(refs[nwKeyWords.TIME_KEY]))
            item.setText(self._colIdx[nwOutline.WORLD],   ", ".join(refs[nwKeyWords.WORLD_KEY]))
            item.setText(self._colIdx[nwOutline.OBJECT],  ", ".join(refs[nwKeyWords.OBJECT_KEY]))
            item.setText(self._colIdx[nwOutline.ENTITY],  ", ".join(refs[nwKeyWords.ENTITY_KEY]))
            item.setText(self._colIdx[nwOutline.CUSTOM],  ", ".join(refs[nwKeyWords.CUSTOM_KEY]))
            item.setText(self._colIdx[nwOutline.STORY],   ", ".join(refs[nwKeyWords.STORY_KEY]))
            item.setText(self._colIdx[nwOutline.MENTION], ", ".join(refs[nwKeyWords.MENTION_KEY]))

            self.addTopLevelItem(item)

        self._lastBuild = time()
        logger.debug("Project outline built in %.3f ms", 1000.0*(time() - tStart))

        return


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

        bFont = SHARED.theme.guiFontB

        trStats1 = trConst(nwLabels.STATS_NAME[nwStats.CHARS_ALL])
        trStats2 = trConst(nwLabels.STATS_NAME[nwStats.WORDS_ALL])
        trStats3 = trConst(nwLabels.STATS_NAME[nwStats.PARAGRAPHS])

        # Details Area
        self.titleLabel = QLabel(self.tr("Title"), self)
        self.fileLabel  = QLabel(self.tr("Document"), self)
        self.itemLabel  = QLabel(self.tr("Status"), self)
        self.titleValue = QLabel("", self)
        self.fileValue  = QLabel("", self)
        self.itemValue  = QLabel("", self)

        self.titleLabel.setFont(bFont)
        self.fileLabel.setFont(bFont)
        self.itemLabel.setFont(bFont)

        self.titleValue.setMinimumWidth(minTitle)
        self.titleValue.setMaximumWidth(maxTitle)
        self.fileValue.setMinimumWidth(minTitle)
        self.fileValue.setMaximumWidth(maxTitle)
        self.itemValue.setMinimumWidth(minTitle)
        self.itemValue.setMaximumWidth(maxTitle)

        # Stats Area
        self.cCLabel = QLabel(trStats1, self)
        self.wCLabel = QLabel(trStats2, self)
        self.pCLabel = QLabel(trStats3, self)
        self.cCValue = QLabel("", self)
        self.wCValue = QLabel("", self)
        self.pCValue = QLabel("", self)

        self.cCLabel.setFont(bFont)
        self.wCLabel.setFont(bFont)
        self.pCLabel.setFont(bFont)

        self.cCValue.setMinimumWidth(wCount)
        self.wCValue.setMinimumWidth(wCount)
        self.pCValue.setMinimumWidth(wCount)
        self.cCValue.setAlignment(QtAlignRight)
        self.wCValue.setAlignment(QtAlignRight)
        self.pCValue.setAlignment(QtAlignRight)

        # Synopsis
        self.synopLabel = QLabel(self.tr("Synopsis"), self)
        self.synopLabel.setFont(bFont)

        self.synopValue = QLabel("", self)
        self.synopValue.setWordWrap(True)
        self.synopValue.setAlignment(QtAlignLeftTop)

        self.synopLWrap = QHBoxLayout()
        self.synopLWrap.addWidget(self.synopValue, 1)

        # Selected Item Details
        self.mainForm = QGridLayout()
        self.mainGroup = QGroupBox(self.tr("Title Details"), self)
        self.mainGroup.setLayout(self.mainForm)

        self.mainForm.addWidget(self.titleLabel, 0, 0, 1, 1, QtAlignLeftTop)
        self.mainForm.addWidget(self.titleValue, 0, 1, 1, 1, QtAlignLeftTop)
        self.mainForm.addWidget(self.cCLabel,    0, 2, 1, 1, QtAlignLeftTop)
        self.mainForm.addWidget(self.cCValue,    0, 3, 1, 1, QtAlignRightTop)
        self.mainForm.addWidget(self.fileLabel,  1, 0, 1, 1, QtAlignLeftTop)
        self.mainForm.addWidget(self.fileValue,  1, 1, 1, 1, QtAlignLeftTop)
        self.mainForm.addWidget(self.wCLabel,    1, 2, 1, 1, QtAlignLeftTop)
        self.mainForm.addWidget(self.wCValue,    1, 3, 1, 1, QtAlignRightTop)
        self.mainForm.addWidget(self.itemLabel,  2, 0, 1, 1, QtAlignLeftTop)
        self.mainForm.addWidget(self.itemValue,  2, 1, 1, 1, QtAlignLeftTop)
        self.mainForm.addWidget(self.pCLabel,    2, 2, 1, 1, QtAlignLeftTop)
        self.mainForm.addWidget(self.pCValue,    2, 3, 1, 1, QtAlignRightTop)
        self.mainForm.addWidget(self.synopLabel, 3, 0, 1, 4, QtAlignLeftTop)
        self.mainForm.addLayout(self.synopLWrap, 4, 0, 1, 4, QtAlignLeftTop)

        self.mainForm.setColumnStretch(1, 1)
        self.mainForm.setRowStretch(4, 1)
        self.mainForm.setHorizontalSpacing(hSpace)
        self.mainForm.setVerticalSpacing(vSpace)

        # Selected Item Tags
        self.tagsForm = QGridLayout()
        self.tagsGroup = QGroupBox(self.tr("Reference Tags"), self)
        self.tagsGroup.setLayout(self.tagsForm)

        self.tagValues: dict[str, tuple[QLabel, QLabel]] = {}
        for key in nwKeyWords.ALL_KEYS:
            label = QLabel(trConst(nwLabels.KEY_NAME[key]), self)
            label.setFont(bFont)
            value = QLabel("", self)
            value.setWordWrap(True)
            value.linkActivated.connect(lambda x: self.itemTagClicked.emit(x))
            layout = QHBoxLayout()
            layout.addWidget(value, 1)
            n = len(self.tagValues)
            self.tagsForm.addWidget(label, n, 0, QtAlignLeftTop)
            self.tagsForm.addLayout(layout, n, 1, QtAlignLeftTop)
            self.tagValues[key] = (label, value)

        self.tagsForm.setColumnStretch(1, 1)
        self.tagsForm.setRowStretch(len(self.tagValues), 1)
        self.tagsForm.setHorizontalSpacing(hSpace)
        self.tagsForm.setVerticalSpacing(vSpace)

        # Assemble
        self.mainSplit = QSplitter(Qt.Orientation.Horizontal)
        self.mainSplit.addWidget(self.mainGroup)
        self.mainSplit.addWidget(self.tagsGroup)
        self.mainSplit.setCollapsible(0, False)
        self.mainSplit.setCollapsible(1, False)

        self.setWidget(self.mainSplit)

        self.setHorizontalScrollBarPolicy(QtScrollAsNeeded)
        self.setVerticalScrollBarPolicy(QtScrollAsNeeded)
        self.setWidgetResizable(True)
        self.setFrameStyle(QFrame.Shape.NoFrame)

        self.initSettings()

        logger.debug("Ready: GuiOutlineDetails")

        return

    def initSettings(self) -> None:
        """Set or update outline settings."""
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(QtScrollAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(QtScrollAsNeeded)
        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(QtScrollAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(QtScrollAsNeeded)
        self.updateClasses()
        return

    def loadGuiSettings(self) -> None:
        """Run open project tasks."""
        parent = self.outlineView.parent()  # This widget is rendered already
        width = parent.width() if isinstance(parent, QWidget) else 1000
        pOptions = SHARED.project.options
        self.mainSplit.setSizes([
            CONFIG.pxInt(pOptions.getInt("GuiOutlineDetails", "detailsWidth", width//3)),
            CONFIG.pxInt(pOptions.getInt("GuiOutlineDetails", "tagsWidth", 2*width//3))
        ])
        return

    def saveGuiSettings(self) -> None:
        """Run close project tasks."""
        mainSplit = self.mainSplit.sizes()
        detailsWidth = CONFIG.rpxInt(mainSplit[0])
        tagsWidth = CONFIG.rpxInt(mainSplit[1])

        logger.debug("Saving State: GuiOutlineDetails")
        pOptions = SHARED.project.options
        pOptions.setValue("GuiOutlineDetails", "detailsWidth", detailsWidth)
        pOptions.setValue("GuiOutlineDetails", "tagsWidth", tagsWidth)
        return

    def clearDetails(self) -> None:
        """Clear all the data labels."""
        self.titleLabel.setText(self.tr("Title"))
        self.titleValue.clear()
        self.fileValue.clear()
        self.itemValue.clear()
        self.cCValue.clear()
        self.wCValue.clear()
        self.pCValue.clear()
        self.synopValue.clear()

        for _, value in self.tagValues.values():
            value.clear()

        self.updateClasses()
        return

    ##
    #  Slots
    ##

    @pyqtSlot(str, str)
    def showItem(self, tHandle: str, sTitle: str) -> None:
        """Update the content of the tree with the given handle and line
        number pointing to a header.
        """
        pIndex = SHARED.project.index
        nwItem = SHARED.project.tree[tHandle]
        novIdx = pIndex.getItemHeading(tHandle, sTitle)
        novRefs = pIndex.getReferences(tHandle, sTitle)
        if nwItem and novIdx:
            self.titleLabel.setText(self.tr(self.LVL_MAP.get(novIdx.level, "H1")))
            self.titleValue.setText(novIdx.title)

            itemStatus, _ = nwItem.getImportStatus()

            self.fileValue.setText(nwItem.itemName)
            self.itemValue.setText(itemStatus)

            self.cCValue.setText(f"{checkInt(novIdx.charCount, 0):n}")
            self.wCValue.setText(f"{checkInt(novIdx.wordCount, 0):n}")
            self.pCValue.setText(f"{checkInt(novIdx.paraCount, 0):n}")

            self.synopValue.setText(novIdx.synopsis)

            for key, (_, value) in self.tagValues.items():
                value.setText(self._formatTags(novRefs, key))

        return

    @pyqtSlot()
    def updateClasses(self) -> None:
        """Update the visibility status of class details."""
        usedClasses = SHARED.project.tree.rootClasses()
        for key, itemClass in nwKeyWords.KEY_CLASS.items():
            visible = itemClass in usedClasses
            if key in self.tagValues:
                label, value = self.tagValues[key]
                label.setVisible(visible)
                value.setVisible(visible)
        return

    @staticmethod
    def _formatTags(refs: dict[str, list[str]], key: str) -> str:
        """Convert a list of tags into a list of clickable tag links."""
        return ", ".join(
            [f"<a href='{tag}'>{tag}</a>" for tag in refs.get(key, [])]
        )
