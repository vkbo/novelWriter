"""
novelWriter – GUI Novel Tree
============================

File History:
Created: 2020-12-20 [1.1rc1] GuiNovelTree
Created: 2022-06-12 [2.0rc1] GuiNovelView
Created: 2022-06-12 [2.0rc1] GuiNovelToolBar

This file is a part of novelWriter
Copyright 2018–2020, Veronica Berglyd Olsen

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

from enum import Enum
from time import time
from typing import TYPE_CHECKING

from PyQt5.QtGui import QFocusEvent, QFont, QMouseEvent, QPalette, QResizeEvent
from PyQt5.QtCore import QModelIndex, QPoint, Qt, QSize, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView, QActionGroup, QFrame, QHBoxLayout, QHeaderView,
    QInputDialog, QMenu, QSizePolicy, QToolButton, QToolTip, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwDocMode, nwItemClass, nwOutline
from novelwriter.common import minmax
from novelwriter.constants import nwHeaders, nwKeyWords, nwLabels, trConst
from novelwriter.core.index import IndexHeading
from novelwriter.extensions.novelselector import NovelSelector

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class NovelTreeColumn(Enum):

    HIDDEN = 0
    POV    = 1
    FOCUS  = 2
    PLOT   = 3

# END Enum NovelTreeColumn


class GuiNovelView(QWidget):

    # Signals for user interaction with the novel tree
    selectedItemChanged = pyqtSignal(str)
    openDocumentRequest = pyqtSignal(str, Enum, str, bool)

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        self.mainGui = mainGui

        # Build GUI
        self.novelTree = GuiNovelTree(self)
        self.novelBar = GuiNovelToolBar(self)
        self.novelBar.setEnabled(False)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.novelBar, 0)
        self.outerBox.addWidget(self.novelTree, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        # Function Mappings
        self.getSelectedHandle = self.novelTree.getSelectedHandle
        self.setActiveHandle = self.novelTree.setActiveHandle

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.novelBar.updateTheme()
        self.novelTree.updateTheme()
        self.refreshTree()
        return

    def initSettings(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        self.novelTree.initSettings()
        return

    def clearNovelView(self) -> None:
        """Clear project-related GUI content."""
        self.novelTree.clearContent()
        self.novelBar.clearContent()
        self.novelBar.setEnabled(False)
        return

    def openProjectTasks(self) -> None:
        """Run open project tasks."""
        lastNovel = SHARED.project.data.getLastHandle("novelTree")
        if lastNovel and lastNovel not in SHARED.project.tree:
            lastNovel = SHARED.project.tree.findRoot(nwItemClass.NOVEL)

        logger.debug("Setting novel tree to root item '%s'", lastNovel)

        lastCol = SHARED.project.options.getEnum(
            "GuiNovelView", "lastCol", NovelTreeColumn, NovelTreeColumn.HIDDEN
        )
        lastColSize = SHARED.project.options.getInt(
            "GuiNovelView", "lastColSize", 25
        )

        self.clearNovelView()
        self.novelBar.buildNovelRootMenu()
        self.novelBar.setLastColType(lastCol, doRefresh=False)
        self.novelBar.setCurrentRoot(lastNovel)
        self.novelBar.setEnabled(True)

        self.novelTree.setLastColSize(lastColSize)

        return

    def closeProjectTasks(self) -> None:
        """Run closing project tasks."""
        lastColType = self.novelTree.lastColType
        lastColSize = self.novelTree.lastColSize
        pOptions = SHARED.project.options
        pOptions.setValue("GuiNovelView", "lastCol", lastColType)
        pOptions.setValue("GuiNovelView", "lastColSize", lastColSize)
        self.clearNovelView()
        return

    def setTreeFocus(self) -> None:
        """Set the focus to the tree widget."""
        self.novelTree.setFocus()
        return

    def treeHasFocus(self) -> bool:
        """Check if the novel tree has focus."""
        return self.novelTree.hasFocus()

    ##
    #  Public Slots
    ##

    @pyqtSlot()
    def refreshTree(self) -> None:
        """Refresh the current tree."""
        self.novelTree.refreshTree(rootHandle=SHARED.project.data.getLastHandle("novelTree"))
        return

    @pyqtSlot(str)
    def updateRootItem(self, tHandle: str) -> None:
        """If any root item changes, rebuild the novel root menu."""
        self.novelBar.buildNovelRootMenu()
        return

    @pyqtSlot(str)
    def updateNovelItemMeta(self, tHandle: str) -> None:
        """The meta data of a novel item has changed, and the tree item
        needs to be refreshed.
        """
        self.novelTree.refreshHandle(tHandle)
        return

# END Class GuiNovelView


class GuiNovelToolBar(QWidget):

    def __init__(self, novelView: GuiNovelView) -> None:
        super().__init__(parent=novelView)

        logger.debug("Create: GuiNovelToolBar")

        self.novelView = novelView
        self.mainGui   = novelView.mainGui

        iPx = SHARED.theme.baseIconSize
        mPx = CONFIG.pxInt(2)

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        # Novel Selector
        selFont = self.font()
        selFont.setWeight(QFont.Bold)
        self.novelPrefix = self.tr("Outline of {0}")
        self.novelValue = NovelSelector(self)
        self.novelValue.setFont(selFont)
        self.novelValue.setMinimumWidth(CONFIG.pxInt(150))
        self.novelValue.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.novelValue.novelSelectionChanged.connect(self.setCurrentRoot)

        self.tbNovel = QToolButton(self)
        self.tbNovel.setToolTip(self.tr("Novel Root"))
        self.tbNovel.setIconSize(QSize(iPx, iPx))
        self.tbNovel.clicked.connect(self._openNovelSelector)

        # Refresh Button
        self.tbRefresh = QToolButton(self)
        self.tbRefresh.setToolTip(self.tr("Refresh"))
        self.tbRefresh.setIconSize(QSize(iPx, iPx))
        self.tbRefresh.clicked.connect(self._refreshNovelTree)

        # More Options Menu
        self.mMore = QMenu(self)

        self.mLastCol = self.mMore.addMenu(self.tr("Last Column"))
        self.gLastCol = QActionGroup(self.mMore)
        self.aLastCol = {}
        self._addLastColAction(NovelTreeColumn.HIDDEN, self.tr("Hidden"))
        self._addLastColAction(NovelTreeColumn.POV,    self.tr("Point of View Character"))
        self._addLastColAction(NovelTreeColumn.FOCUS,  self.tr("Focus Character"))
        self._addLastColAction(NovelTreeColumn.PLOT,   self.tr("Novel Plot"))

        self.mLastCol.addSeparator()
        self.aLastColSize = self.mLastCol.addAction(self.tr("Column Size"))
        self.aLastColSize.triggered.connect(self._selectLastColumnSize)

        self.tbMore = QToolButton(self)
        self.tbMore.setToolTip(self.tr("More Options"))
        self.tbMore.setIconSize(QSize(iPx, iPx))
        self.tbMore.setMenu(self.mMore)
        self.tbMore.setPopupMode(QToolButton.InstantPopup)

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.novelValue)
        self.outerBox.addWidget(self.tbNovel)
        self.outerBox.addWidget(self.tbRefresh)
        self.outerBox.addWidget(self.tbMore)
        self.outerBox.setContentsMargins(mPx, mPx, 0, mPx)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        self.updateTheme()

        logger.debug("Ready: GuiNovelToolBar")

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        # Icons
        self.tbNovel.setIcon(SHARED.theme.getIcon("cls_novel"))
        self.tbRefresh.setIcon(SHARED.theme.getIcon("refresh"))
        self.tbMore.setIcon(SHARED.theme.getIcon("menu"))

        qPalette = self.palette()
        qPalette.setBrush(QPalette.Window, qPalette.base())
        self.setPalette(qPalette)

        # StyleSheets
        fadeCol = qPalette.text().color()
        buttonStyle = (
            "QToolButton {{padding: {0}px; border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({1},{2},{3},0.2);}}"
        ).format(CONFIG.pxInt(2), fadeCol.red(), fadeCol.green(), fadeCol.blue())
        buttonStyleMenu = f"{buttonStyle} QToolButton::menu-indicator {{image: none;}}"

        self.tbNovel.setStyleSheet(buttonStyle)
        self.tbRefresh.setStyleSheet(buttonStyle)
        self.tbMore.setStyleSheet(buttonStyleMenu)

        self.novelValue.setStyleSheet(
            "QComboBox {border-style: none; padding-left: 0;} "
            "QComboBox::drop-down {border-style: none}"
        )
        self.novelValue.updateList(prefix=self.novelPrefix)
        self.tbNovel.setVisible(self.novelValue.count() > 1)

        return

    def clearContent(self) -> None:
        """Run clearing project tasks."""
        self.novelValue.clear()
        self.novelValue.setToolTip("")
        return

    def buildNovelRootMenu(self) -> None:
        """Build the novel root menu."""
        self.novelValue.updateList(prefix=self.novelPrefix)
        self.tbNovel.setVisible(self.novelValue.count() > 1)
        return

    def setCurrentRoot(self, rootHandle: str | None) -> None:
        """Set the current active root handle."""
        self.novelValue.setHandle(rootHandle)
        self.novelView.novelTree.refreshTree(rootHandle=rootHandle, overRide=True)
        return

    def setLastColType(self, colType: NovelTreeColumn, doRefresh: bool = True) -> None:
        """Set the last column type."""
        self.aLastCol[colType].setChecked(True)
        self.novelView.novelTree.setLastColType(colType, doRefresh=doRefresh)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _openNovelSelector(self) -> None:
        """Trigger the dropdown list of the novel selector."""
        self.novelValue.showPopup()
        return

    @pyqtSlot()
    def _refreshNovelTree(self) -> None:
        """Rebuild the current tree."""
        rootHandle = SHARED.project.data.getLastHandle("novelTree")
        self.novelView.novelTree.refreshTree(rootHandle=rootHandle, overRide=True)
        return

    @pyqtSlot()
    def _selectLastColumnSize(self) -> None:
        """Set the maximum width for the last column."""
        oldSize = self.novelView.novelTree.lastColSize
        newSize, isOk = QInputDialog.getInt(
            self, self.tr("Column Size"), self.tr("Maximum column size in %"), oldSize, 15, 75, 5
        )
        if isOk:
            self.novelView.novelTree.setLastColSize(newSize)
            self._refreshNovelTree()
        return

    ##
    #  Internal Functions
    ##

    def _addLastColAction(self, colType, actionLabel) -> None:
        """Add a column selection entry to the last column menu."""
        aLast = self.mLastCol.addAction(actionLabel)
        aLast.setCheckable(True)
        aLast.setActionGroup(self.gLastCol)
        aLast.triggered.connect(lambda: self.setLastColType(colType))
        self.aLastCol[colType] = aLast
        return

# END Class GuiNovelToolBar


class GuiNovelTree(QTreeWidget):

    C_DATA  = 0
    C_TITLE = 0
    C_WORDS = 1
    C_EXTRA = 2
    C_MORE  = 3

    D_HANDLE = Qt.ItemDataRole.UserRole
    D_TITLE  = Qt.ItemDataRole.UserRole + 1
    D_KEY    = Qt.ItemDataRole.UserRole + 2
    D_EXTRA  = Qt.ItemDataRole.UserRole + 3

    def __init__(self, novelView: GuiNovelView) -> None:
        super().__init__(parent=novelView)

        logger.debug("Create: GuiNovelTree")

        self.novelView = novelView
        self.mainGui   = novelView.mainGui

        # Internal Variables
        self._treeMap     = {}
        self._lastBuild   = 0
        self._lastCol     = NovelTreeColumn.POV
        self._lastColSize = 0.25
        self._actHandle   = None

        # Cached Strings
        self._povLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.POV_KEY])
        self._focLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.FOCUS_KEY])
        self._pltLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY])

        # Build GUI
        # =========

        iPx = SHARED.theme.baseIconSize
        cMg = CONFIG.pxInt(6)

        self.setIconSize(QSize(iPx, iPx))
        self.setFrameStyle(QFrame.NoFrame)
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(True)
        self.setHeaderHidden(True)
        self.setIndentation(0)
        self.setColumnCount(4)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setExpandsOnDoubleClick(False)
        self.setDragEnabled(False)

        # Lock the column sizes
        treeHeader = self.header()
        treeHeader.setStretchLastSection(False)
        treeHeader.setMinimumSectionSize(iPx + cMg)
        treeHeader.setSectionResizeMode(self.C_TITLE, QHeaderView.Stretch)
        treeHeader.setSectionResizeMode(self.C_WORDS, QHeaderView.ResizeToContents)
        treeHeader.setSectionResizeMode(self.C_EXTRA, QHeaderView.ResizeToContents)
        treeHeader.setSectionResizeMode(self.C_MORE, QHeaderView.ResizeToContents)

        # Pre-Generate Tree Formatting
        fH1 = self.font()
        fH1.setBold(True)
        fH1.setUnderline(True)

        fH2 = self.font()
        fH2.setBold(True)

        self._hFonts = [self.font(), fH1, fH2, self.font(), self.font()]

        # Connect signals
        self.clicked.connect(self._treeItemClicked)
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._treeSelectionChange)

        # Set custom settings
        self.initSettings()
        self.updateTheme()

        logger.debug("Ready: GuiNovelTree")

        return

    def initSettings(self) -> None:
        """Set or update tree widget settings."""
        # Scroll bars
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        return

    def updateTheme(self) -> None:
        """Update theme elements."""
        iPx = SHARED.theme.baseIconSize
        self._pMore = SHARED.theme.loadDecoration("deco_doc_more", h=iPx)
        return

    ##
    #  Properties
    ##

    @property
    def lastColType(self) -> NovelTreeColumn:
        return self._lastCol

    @property
    def lastColSize(self) -> int:
        return int(self._lastColSize * 100)

    ##
    #  Class Methods
    ##

    def clearContent(self) -> None:
        """Clear the GUI content and the related maps."""
        self.clear()
        self._treeMap = {}
        self._lastBuild = 0
        return

    def refreshTree(self, rootHandle: str | None = None, overRide: bool = False) -> None:
        """Refresh the tree if it has been changed."""
        logger.debug("Requesting refresh of the novel tree")
        if rootHandle is None:
            rootHandle = SHARED.project.tree.findRoot(nwItemClass.NOVEL)

        treeChanged = self.mainGui.projView.changedSince(self._lastBuild)
        indexChanged = SHARED.project.index.rootChangedSince(rootHandle, self._lastBuild)
        if not (treeChanged or indexChanged or overRide):
            logger.debug("No changes have been made to the novel index")
            return

        selItem = self.selectedItems()
        titleKey = None
        if selItem:
            titleKey = selItem[0].data(self.C_DATA, self.D_KEY)

        self._populateTree(rootHandle)
        SHARED.project.data.setLastHandle(rootHandle, "novelTree")

        if titleKey is not None and titleKey in self._treeMap:
            self._treeMap[titleKey].setSelected(True)

        return

    def refreshHandle(self, tHandle: str) -> None:
        """Refresh the data for a given handle."""
        idxData = SHARED.project.index.getItemData(tHandle)
        if idxData is None:
            return

        logger.debug("Refreshing meta data for item '%s'", tHandle)
        for sTitle, tHeading in idxData.items():
            sKey = f"{tHandle}:{sTitle}"
            trItem = self._treeMap.get(sKey, None)
            if trItem is None:
                logger.debug("Heading '%s' not in novel tree", sKey)
                self.refreshTree()
                return

            self._updateTreeItemValues(trItem, tHeading, tHandle, sTitle)

        return

    def getSelectedHandle(self) -> tuple[str | None, str | None]:
        """Get the currently selected or active handle. If multiple
        items are selected, return the first.
        """
        selList = self.selectedItems()
        trItem = selList[0] if selList else self.currentItem()
        if isinstance(trItem, QTreeWidgetItem):
            tHandle = trItem.data(self.C_DATA, self.D_HANDLE)
            sTitle = trItem.data(self.C_DATA, self.D_TITLE)
            return tHandle, sTitle
        return None, None

    def setLastColType(self, colType: NovelTreeColumn, doRefresh: bool = True) -> None:
        """Change the content type of the last column and rebuild."""
        if self._lastCol != colType:
            logger.debug("Changing last column to %s", colType.name)
            self._lastCol = colType
            self.setColumnHidden(self.C_EXTRA, colType == NovelTreeColumn.HIDDEN)
            if doRefresh:
                lastNovel = SHARED.project.data.getLastHandle("novelTree")
                self.refreshTree(rootHandle=lastNovel, overRide=True)
        return

    def setLastColSize(self, colSize: int) -> None:
        """Set the column size in integer values between 15 and 75."""
        self._lastColSize = minmax(colSize, 15, 75)/100.0
        return

    def setActiveHandle(self, tHandle: str | None) -> None:
        """Highlight the rows associated with a given handle."""
        tStart = time()

        self._actHandle = tHandle
        for i in range(self.topLevelItemCount()):
            tItem = self.topLevelItem(i)
            if tItem is not None:
                if tItem.data(self.C_DATA, self.D_HANDLE) == tHandle:
                    tItem.setBackground(self.C_TITLE, self.palette().alternateBase())
                    tItem.setBackground(self.C_WORDS, self.palette().alternateBase())
                    tItem.setBackground(self.C_EXTRA, self.palette().alternateBase())
                    tItem.setBackground(self.C_MORE, self.palette().alternateBase())
                else:
                    tItem.setBackground(self.C_TITLE, self.palette().base())
                    tItem.setBackground(self.C_WORDS, self.palette().base())
                    tItem.setBackground(self.C_EXTRA, self.palette().base())
                    tItem.setBackground(self.C_MORE, self.palette().base())

        logger.debug("Highlighted Novel Tree in %.3f ms", (time() - tStart)*1000)

        return

    ##
    #  Events
    ##

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Overload mousePressEvent to clear selection if clicking the
        mouse in a blank area of the tree view, and to load a document
        for viewing if the user middle-clicked.
        """
        super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            selItem = self.indexAt(event.pos())
            if not selItem.isValid():
                self.clearSelection()

        elif event.button() == Qt.MiddleButton:
            selItem = self.itemAt(event.pos())
            if not isinstance(selItem, QTreeWidgetItem):
                return

            tHandle, sTitle = self.getSelectedHandle()
            if tHandle is None:
                return

            self.novelView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW, sTitle or "", False)

        return

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """Clear the selection when the tree no longer has focus."""
        super().focusOutEvent(event)
        self.clearSelection()
        return

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Elide labels in the extra column."""
        super().resizeEvent(event)
        newW = event.size().width()
        oldW = event.oldSize().width()
        if newW != oldW:
            eliW = int(self._lastColSize * newW)
            fMetric = self.fontMetrics()
            for i in range(self.topLevelItemCount()):
                trItem = self.topLevelItem(i)
                if isinstance(trItem, QTreeWidgetItem):
                    lastText = trItem.data(self.C_DATA, self.D_EXTRA)
                    trItem.setText(self.C_EXTRA, fMetric.elidedText(lastText, Qt.ElideRight, eliW))
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot("QModelIndex")
    def _treeItemClicked(self, index: QModelIndex) -> None:
        """The user clicked on an item in the tree."""
        if index.column() == self.C_MORE:
            tHandle = index.siblingAtColumn(self.C_DATA).data(self.D_HANDLE)
            sTitle = index.siblingAtColumn(self.C_DATA).data(self.D_TITLE)
            tipPos = self.mapToGlobal(self.visualRect(index).topRight())
            self._popMetaBox(tipPos, tHandle, sTitle)
        return

    @pyqtSlot()
    def _treeSelectionChange(self) -> None:
        """Extract the handle and line number of the currently selected
        title, and send it to the tree meta panel.
        """
        tHandle, _ = self.getSelectedHandle()
        if tHandle is not None:
            self.novelView.selectedItemChanged.emit(tHandle)
        return

    @pyqtSlot("QTreeWidgetItem*", int)
    def _treeDoubleClick(self, item: QTreeWidgetItem, column: int) -> None:
        """Extract the handle and line number of the title double-
        clicked, and send it to the main gui class for opening in the
        document editor.
        """
        tHandle, sTitle = self.getSelectedHandle()
        self.novelView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, sTitle or "", True)
        return

    ##
    #  Internal Functions
    ##

    def _populateTree(self, rootHandle: str | None) -> None:
        """Build the tree based on the project index."""
        self.clearContent()
        tStart = time()
        logger.debug("Building novel tree for root item '%s'", rootHandle)

        novStruct = SHARED.project.index.novelStructure(rootHandle=rootHandle, skipExcl=True)
        for tKey, tHandle, sTitle, novIdx in novStruct:
            if novIdx.level == "H0":
                continue

            newItem = QTreeWidgetItem()
            newItem.setData(self.C_DATA, self.D_HANDLE, tHandle)
            newItem.setData(self.C_DATA, self.D_TITLE, sTitle)
            newItem.setData(self.C_DATA, self.D_KEY, tKey)
            newItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)

            self._updateTreeItemValues(newItem, novIdx, tHandle, sTitle)
            self._treeMap[tKey] = newItem
            self.addTopLevelItem(newItem)

        self.setActiveHandle(self._actHandle)

        logger.debug("Novel Tree built in %.3f ms", (time() - tStart)*1000)
        self._lastBuild = time()

        return

    def _updateTreeItemValues(self, trItem: QTreeWidgetItem, idxItem: IndexHeading,
                              tHandle: str, sTitle: str) -> None:
        """Set the tree item values from the index entry."""
        iLevel = nwHeaders.H_LEVEL.get(idxItem.level, 0)
        hDec = SHARED.theme.getHeaderDecoration(iLevel)

        trItem.setData(self.C_TITLE, Qt.DecorationRole, hDec)
        trItem.setText(self.C_TITLE, idxItem.title)
        trItem.setFont(self.C_TITLE, self._hFonts[iLevel])
        trItem.setText(self.C_WORDS, f"{idxItem.wordCount:n}")
        trItem.setData(self.C_MORE, Qt.DecorationRole, self._pMore)

        # Custom column
        mW = int(self._lastColSize * self.viewport().width())
        lastText, toolTip = self._getLastColumnText(tHandle, sTitle)
        elideText = self.fontMetrics().elidedText(lastText, Qt.ElideRight, mW)
        trItem.setText(self.C_EXTRA, elideText)
        trItem.setData(self.C_DATA, self.D_EXTRA, lastText)
        trItem.setToolTip(self.C_EXTRA, toolTip)

        return

    def _getLastColumnText(self, tHandle: str, sTitle: str) -> tuple[str, str]:
        """Generate text for the last column based on user settings."""
        if self._lastCol == NovelTreeColumn.HIDDEN:
            return "", ""

        refData = []
        refName = ""
        theRefs = SHARED.project.index.getReferences(tHandle, sTitle)
        if self._lastCol == NovelTreeColumn.POV:
            refData = theRefs[nwKeyWords.POV_KEY]
            refName = self._povLabel

        elif self._lastCol == NovelTreeColumn.FOCUS:
            refData = theRefs[nwKeyWords.FOCUS_KEY]
            refName = self._focLabel

        elif self._lastCol == NovelTreeColumn.PLOT:
            refData = theRefs[nwKeyWords.PLOT_KEY]
            refName = self._pltLabel

        if refData:
            toolText = ", ".join(refData)
            return toolText, f"{refName}: {toolText}"

        return "", ""

    def _popMetaBox(self, qPos: QPoint, tHandle: str, sTitle: str) -> None:
        """Show the novel meta data box."""
        logger.debug("Generating meta data tooltip for '%s:%s'", tHandle, sTitle)

        pIndex = SHARED.project.index
        novIdx = pIndex.getItemHeader(tHandle, sTitle)
        refTags = pIndex.getReferences(tHandle, sTitle)
        if not novIdx:
            return

        synopText = novIdx.synopsis
        if synopText:
            synopLabel = trConst(nwLabels.OUTLINE_COLS[nwOutline.SYNOP])
            synopText = f"<p><b>{synopLabel}</b>: {synopText}</p>"

        refLines = []
        refLines = self._appendMetaTag(refTags, nwKeyWords.POV_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.FOCUS_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.CHAR_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.PLOT_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.TIME_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.WORLD_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.OBJECT_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.ENTITY_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.CUSTOM_KEY, refLines)

        refText = ""
        if refLines:
            refList = "<br>".join(refLines)
            refText = f"<p>{refList}</p>"

        ttText = refText + synopText or self.tr("No meta data")
        if ttText:
            QToolTip.showText(qPos, ttText)

        return

    @staticmethod
    def _appendMetaTag(refs: dict, key: str, lines: list[str]) -> list[str]:
        """Generate a reference list for a given reference key."""
        tags = ", ".join(refs.get(key, []))
        if tags:
            lines.append(f"<b>{trConst(nwLabels.KEY_NAME[key])}</b>: {tags}")
        return lines

# END Class GuiNovelTree
