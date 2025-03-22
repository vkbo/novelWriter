"""
novelWriter – GUI Novel Tree
============================

File History:
Created: 2020-12-20 [1.1rc1] GuiNovelTree
Created: 2022-06-12 [2.0rc1] GuiNovelView
Created: 2022-06-12 [2.0rc1] GuiNovelToolBar

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt6.QtCore import QModelIndex, QPoint, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QActionGroup, QFont, QPainter, QPalette, QResizeEvent
from PyQt6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QInputDialog, QMenu,
    QStyleOptionViewItem, QToolTip, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import minmax, qtAddAction, qtAddMenu, qtLambda
from novelwriter.constants import nwKeyWords, nwLabels, trConst
from novelwriter.core.novelmodel import NovelModel
from novelwriter.enum import nwChange, nwDocMode, nwItemClass, nwNovelExtra, nwOutline
from novelwriter.extensions.modified import NIconToolButton, NTreeView
from novelwriter.extensions.novelselector import NovelSelector
from novelwriter.gui.theme import STYLES_MIN_TOOLBUTTON
from novelwriter.types import (
    QtHeaderFixed, QtHeaderStretch, QtHeaderToContents, QtScrollAlwaysOff,
    QtScrollAsNeeded, QtSizeExpanding
)

logger = logging.getLogger(__name__)


class GuiNovelView(QWidget):

    # Signals for user interaction with the novel tree
    selectedItemChanged = pyqtSignal(str)
    openDocumentRequest = pyqtSignal(str, Enum, str, bool)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

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
        self.setActive = self.novelBar.setActive
        self.getSelectedHandle = self.novelTree.getSelectedHandle

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.novelBar.updateTheme()
        return

    def initSettings(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        self.novelTree.initSettings()
        return

    def clearNovelView(self) -> None:
        """Clear project-related GUI content."""
        # self.novelTree.clearContent()
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
            "GuiNovelView", "lastCol", nwNovelExtra, nwNovelExtra.HIDDEN
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
        logger.debug("Saving State: GuiNovelView")
        options = SHARED.project.options
        options.setValue("GuiNovelView", "lastCol", lastColType)
        options.setValue("GuiNovelView", "lastColSize", lastColSize)
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

    @pyqtSlot(str)
    def setCurrentNovel(self, rootHandle: str | None) -> None:
        """Set the current novel to display."""
        if rootHandle and (model := SHARED.project.index.getNovelModel(rootHandle)):
            self.novelTree.setModel(model)
            self.novelTree.resizeColumns()
        return

    @pyqtSlot(str)
    def setActiveHandle(self, tHandle: str) -> None:
        """Highlight the rows associated with a given handle."""
        self.novelTree.setActiveHandle(tHandle)
        return

    @pyqtSlot(str, Enum)
    def updateRootItem(self, tHandle: str, change: nwChange) -> None:
        """If any root item changes, rebuild the novel root menu."""
        self.novelBar.buildNovelRootMenu()
        return

    @pyqtSlot(str)
    def updateNovelItemMeta(self, tHandle: str) -> None:
        """The meta data of a novel item has changed, and the tree item
        needs to be refreshed.
        """
        # self.novelTree.refreshHandle(tHandle)
        return


class GuiNovelToolBar(QWidget):

    def __init__(self, novelView: GuiNovelView) -> None:
        super().__init__(parent=novelView)

        logger.debug("Create: GuiNovelToolBar")

        self.novelView = novelView

        self._active = False
        self._refresh: dict[str, bool] = {}

        iSz = SHARED.theme.baseIconSize

        self.setContentsMargins(0, 0, 0, 0)
        self.setBackgroundRole(QPalette.ColorRole.Base)
        self.setAutoFillBackground(True)

        # Novel Selector
        selFont = self.font()
        selFont.setWeight(QFont.Weight.Bold)

        self.novelValue = NovelSelector(self)
        self.novelValue.setFont(selFont)
        self.novelValue.setListFormat(self.tr("Outline of {0}"))
        self.novelValue.setMinimumWidth(150)
        self.novelValue.setSizePolicy(QtSizeExpanding, QtSizeExpanding)
        self.novelValue.novelSelectionChanged.connect(self.setCurrentRoot)

        self.tbNovel = NIconToolButton(self, iSz)
        self.tbNovel.setToolTip(self.tr("Novel Root"))
        self.tbNovel.clicked.connect(self.novelValue.showPopup)

        # Refresh Button
        self.tbRefresh = NIconToolButton(self, iSz)
        self.tbRefresh.setToolTip(self.tr("Refresh"))
        self.tbRefresh.clicked.connect(self._forceRefreshNovelTree)

        # More Options Menu
        self.mMore = QMenu(self)

        self.mLastCol = qtAddMenu(self.mMore, self.tr("Last Column"))
        self.gLastCol = QActionGroup(self.mMore)
        self.aLastCol = {}
        self._addLastColAction(nwNovelExtra.HIDDEN, self.tr("Hidden"))
        self._addLastColAction(nwNovelExtra.POV,    self.tr("Point of View Character"))
        self._addLastColAction(nwNovelExtra.FOCUS,  self.tr("Focus Character"))
        self._addLastColAction(nwNovelExtra.PLOT,   self.tr("Novel Plot"))

        self.mLastCol.addSeparator()
        self.aLastColSize = qtAddAction(self.mLastCol, self.tr("Column Size"))
        self.aLastColSize.triggered.connect(self._selectLastColumnSize)

        self.tbMore = NIconToolButton(self, iSz)
        self.tbMore.setToolTip(self.tr("More Options"))
        self.tbMore.setMenu(self.mMore)

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.novelValue)
        self.outerBox.addWidget(self.tbNovel)
        self.outerBox.addWidget(self.tbRefresh)
        self.outerBox.addWidget(self.tbMore)
        self.outerBox.setContentsMargins(4, 2, 0, 2)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        self.updateTheme()

        # Connect Signals
        SHARED.novelStructureChanged.connect(self._refreshNovelTree)

        logger.debug("Ready: GuiNovelToolBar")

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        # Icons
        self.tbNovel.setThemeIcon("cls_novel", "red")
        self.tbRefresh.setThemeIcon("refresh", "green")
        self.tbMore.setThemeIcon("more_vertical")

        # StyleSheets
        buttonStyle = SHARED.theme.getStyleSheet(STYLES_MIN_TOOLBUTTON)
        self.tbNovel.setStyleSheet(buttonStyle)
        self.tbRefresh.setStyleSheet(buttonStyle)
        self.tbMore.setStyleSheet(buttonStyle)

        self.novelValue.setStyleSheet(
            "QComboBox {border-style: none; padding-left: 0;} "
            "QComboBox::drop-down {border-style: none}"
        )
        self.novelValue.refreshNovelList()
        self.tbNovel.setVisible(self.novelValue.count() > 1)

        self._forceRefreshNovelTree()

        return

    def clearContent(self) -> None:
        """Run clearing project tasks."""
        self.novelValue.clear()
        self.novelValue.setToolTip("")
        return

    def buildNovelRootMenu(self) -> None:
        """Build the novel root menu."""
        self.novelValue.refreshNovelList()
        self.tbNovel.setVisible(self.novelValue.count() > 1)
        return

    def setCurrentRoot(self, rootHandle: str | None) -> None:
        """Set the current active root handle."""
        self.novelValue.setHandle(rootHandle)
        SHARED.project.data.setLastHandle(rootHandle, "novelTree")
        self.novelView.setCurrentNovel(rootHandle)
        return

    def setLastColType(self, colType: nwNovelExtra, doRefresh: bool = True) -> None:
        """Set the last column type."""
        self.aLastCol[colType].setChecked(True)
        self.novelView.novelTree.setLastColType(colType)
        if doRefresh:
            self._forceRefreshNovelTree()
            self.novelView.novelTree.resizeColumns()
        return

    def setActive(self, state: bool) -> None:
        """Set the widget active state, which enables automatic tree
        refresh when content structure changes.
        """
        self._active = state
        if self._active and self._refresh.get(self.novelValue.handle, False):
            self._refreshNovelTree(self.novelValue.handle)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _forceRefreshNovelTree(self) -> None:
        """Rebuild the current tree."""
        if tHandle := self.novelValue.handle:
            SHARED.project.index.refreshNovelModel(tHandle)
            self._refresh[tHandle] = False
        return

    @pyqtSlot(str)
    def _refreshNovelTree(self, tHandle: str) -> None:
        """Refresh or schedule refresh of a novel tree."""
        if self._active:
            SHARED.project.index.refreshNovelModel(tHandle)
            self._refresh[tHandle] = False
        else:
            self._refresh[tHandle] = True
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
            self.novelView.novelTree.resizeColumns()
        return

    ##
    #  Internal Functions
    ##

    def _addLastColAction(self, colType: nwNovelExtra, actionLabel: str) -> None:
        """Add a column selection entry to the last column menu."""
        aLast = qtAddAction(self.mLastCol, actionLabel)
        aLast.setCheckable(True)
        aLast.setActionGroup(self.gLastCol)
        aLast.triggered.connect(qtLambda(self.setLastColType, colType))
        self.aLastCol[colType] = aLast
        return


class GuiNovelTree(NTreeView):

    def __init__(self, novelView: GuiNovelView) -> None:
        super().__init__(parent=novelView)

        logger.debug("Create: GuiNovelTree")

        self.novelView = novelView

        # Internal Variables
        self._actHandle   = None
        self._lastColType = nwNovelExtra.POV
        self._lastColSize = 0.25
        # self._lastBuild   = 0
        # self._treeMap: dict[str, QTreeWidgetItem] = {}

        # Cached Strings
        # self._povLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.POV_KEY])
        # self._focLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.FOCUS_KEY])
        # self._pltLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY])

        self.setIconSize(SHARED.theme.baseIconSize)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(True)
        self.setHeaderHidden(True)
        self.setIndentation(2)
        self.setDragEnabled(False)

        # Set selection options
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Connect signals
        self.clicked.connect(self._onSingleClick)
        self.doubleClicked.connect(self._onDoubleClick)
        self.middleClicked.connect(self._onMiddleClick)

        # Set custom settings
        self.initSettings()

        logger.debug("Ready: GuiNovelTree")

        return

    def initSettings(self) -> None:
        """Set or update tree widget settings."""
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(QtScrollAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(QtScrollAsNeeded)
        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(QtScrollAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(QtScrollAsNeeded)
        return

    ##
    #  Properties
    ##

    @property
    def lastColType(self) -> nwNovelExtra:
        """The data type of the extra column."""
        return self._lastColType

    @property
    def lastColSize(self) -> int:
        """Return the size of the extra column."""
        return int(self._lastColSize * 100)

    ##
    #  Getters
    ##

    def getSelectedHandle(self) -> tuple[str | None, str | None]:
        """Get the currently selected or active handle. If multiple
        items are selected, return the first.
        """
        if model := self._getModel():
            index = self.currentIndex()
            return model.handle(index), model.key(index)
        return None, None

    ##
    #  Setters
    ##

    def setActiveHandle(self, tHandle: str | None) -> None:
        """Set the handle to be highlighted."""
        self._actHandle = tHandle
        if viewport := self.viewport():
            viewport.repaint()
        return

    def setLastColType(self, colType: nwNovelExtra) -> None:
        """Set the extra column type."""
        self._lastColType = colType
        SHARED.project.index.setNovelModelExtraColumn(colType)
        return

    def setLastColSize(self, colSize: int) -> None:
        """Set the extra column size between 15% and 75%."""
        self._lastColSize = minmax(colSize, 15, 75)/100.0
        return

    ##
    #  Class Methods
    ##

    def resizeColumns(self) -> None:
        """Set the correct column sizes."""
        if (header := self.header()) and (model := self._getModel()) and (vp := self.viewport()):
            header.setStretchLastSection(False)
            header.setMinimumSectionSize(SHARED.theme.baseIconHeight + 6)
            header.setSectionResizeMode(0, QtHeaderStretch)
            header.setSectionResizeMode(1, QtHeaderToContents)
            if model.columns == 3:
                header.setSectionResizeMode(2, QtHeaderToContents)
            elif model.columns == 4:
                header.setSectionResizeMode(2, QtHeaderFixed)
                header.setSectionResizeMode(3, QtHeaderToContents)
                header.resizeSection(2, int(self._lastColSize * vp.width()))
        return

    ##
    #  Overloads
    ##

    def drawRow(self, painter: QPainter, opt: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Draw a box on the active row."""
        if (model := self._getModel()) and model.handle(index) == self._actHandle:
            painter.fillRect(opt.rect, self.palette().alternateBase())
        super().drawRow(painter, opt, index)
        return

    ##
    #  Events
    ##

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Process size changed."""
        super().resizeEvent(event)
        self.resizeColumns()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(QModelIndex)
    def _onSingleClick(self, index: QModelIndex) -> None:
        """The user single-clicked an index."""
        if index.isValid() and (model := self._getModel()):
            if (tHandle := model.handle(index)) and (sTitle := model.key(index)):
                self.novelView.selectedItemChanged.emit(tHandle)
                if index.column() == model.columnCount(index) - 1:
                    pos = self.mapToGlobal(self.visualRect(index).topRight())
                    self._popMetaBox(pos, tHandle, sTitle)
        return

    @pyqtSlot(QModelIndex)
    def _onDoubleClick(self, index: QModelIndex) -> None:
        """The user double-clicked an index."""
        if (
            (model := self._getModel())
            and (tHandle := model.handle(index))
            and (sTitle := model.key(index))
        ):
            self.novelView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, sTitle, False)
        return

    @pyqtSlot(QModelIndex)
    def _onMiddleClick(self, index: QModelIndex) -> None:
        """The user middle-clicked an index."""
        if (
            (model := self._getModel())
            and (tHandle := model.handle(index))
            and (sTitle := model.key(index))
        ):
            self.novelView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW, sTitle, False)
        return

    ##
    #  Internal Functions
    ##

    def _getModel(self) -> NovelModel | None:
        """Return the model, if it exists."""
        if isinstance(model := self.model(), NovelModel):
            return model
        return None

    def _popMetaBox(self, qPos: QPoint, tHandle: str, sTitle: str) -> None:
        """Show the novel meta data box."""
        if head := SHARED.project.index.getItemHeading(tHandle, sTitle):
            logger.debug("Generating meta data tooltip for '%s:%s'", tHandle, sTitle)
            if synopsis := head.synopsis:
                label = trConst(nwLabels.OUTLINE_COLS[nwOutline.SYNOP])
                synopsis = f"<p><b>{label}</b>: {synopsis}</p>"

            def appendTags(refs: dict, key: str, lines: list[str]) -> list[str]:
                """Generate a reference list for a given reference key."""
                if tags := ", ".join(refs.get(key, [])):
                    lines.append(f"<b>{trConst(nwLabels.KEY_NAME[key])}</b>: {tags}")
                return lines

            tags = SHARED.project.index.getReferences(tHandle, sTitle)
            lines = []
            lines = appendTags(tags, nwKeyWords.POV_KEY, lines)
            lines = appendTags(tags, nwKeyWords.FOCUS_KEY, lines)
            lines = appendTags(tags, nwKeyWords.CHAR_KEY, lines)
            lines = appendTags(tags, nwKeyWords.PLOT_KEY, lines)
            lines = appendTags(tags, nwKeyWords.TIME_KEY, lines)
            lines = appendTags(tags, nwKeyWords.WORLD_KEY, lines)
            lines = appendTags(tags, nwKeyWords.OBJECT_KEY, lines)
            lines = appendTags(tags, nwKeyWords.ENTITY_KEY, lines)
            lines = appendTags(tags, nwKeyWords.CUSTOM_KEY, lines)

            text = ""
            if lines:
                refs = "<br>".join(lines)
                text = f"<p>{refs}</p>"
            if tooltip := (text + synopsis or self.tr("No meta data")):
                QToolTip.showText(qPos, tooltip)
        return

    ##
    #  Old Code
    ##

    ##
    #  Class Methods
    ##

    # def clearContent(self) -> None:
    #     """Clear the GUI content and the related maps."""
    #     self.clear()
    #     self._treeMap = {}
    #      self._lastBuild = 0
    #     return

    # def refreshTree(self, rootHandle: str | None = None, overRide: bool = False) -> None:
    #     """Refresh the tree if it has been changed."""
    #     logger.debug("Requesting refresh of the novel tree")
    #     if rootHandle is None:
    #         rootHandle = SHARED.project.tree.findRoot(nwItemClass.NOVEL)

    #     titleKey = None
    #     if selItems := self.selectedItems():
    #         titleKey = selItems[0].data(self.C_DATA, self.D_KEY)

    #     self._populateTree(rootHandle)
    #     SHARED.project.data.setLastHandle(rootHandle, "novelTree")

    #     if titleKey is not None and titleKey in self._treeMap:
    #         self._treeMap[titleKey].setSelected(True)

    #     return

    # def refreshHandle(self, tHandle: str) -> None:
    #     """Refresh the data for a given handle."""
    #     if idxData := SHARED.project.index.getItemData(tHandle):
    #         logger.debug("Refreshing meta data for item '%s'", tHandle)
    #         for sTitle, tHeading in idxData.items():
    #             sKey = f"{tHandle}:{sTitle}"
    #             if trItem := self._treeMap.get(sKey, None):
    #                 self._updateTreeItemValues(trItem, tHeading, tHandle, sTitle)
    #             else:
    #                 logger.debug("Heading '%s' not in novel tree", sKey)
    #                 self.refreshTree()
    #                 return
    #     return

    # def setLastColType(self, colType: NovelTreeColumn, doRefresh: bool = True) -> None:
    #     """Change the content type of the last column and rebuild."""
    #     if self._lastCol != colType:
    #         logger.debug("Changing last column to %s", colType.name)
    #         self._lastCol = colType
    #         self.setColumnHidden(self.C_EXTRA, colType == NovelTreeColumn.HIDDEN)
    #         if doRefresh:
    #             lastNovel = SHARED.project.data.getLastHandle("novelTree")
    #             self.refreshTree(rootHandle=lastNovel, overRide=True)
    #     return

    # def setActiveHandle(self, tHandle: str | None) -> None:
    #     """Highlight the rows associated with a given handle."""
    #     didScroll = False
    #     brushOn = self.palette().alternateBase()
    #     brushOff = self.palette().base()
    #     if pHandle := self._actHandle:
    #         for key, item in self._treeMap.items():
    #             if key.startswith(pHandle):
    #                 for i in range(self.columnCount()):
    #                     item.setBackground(i, brushOff)
    #     if tHandle:
    #         for key, item in self._treeMap.items():
    #             if key.startswith(tHandle):
    #                 for i in range(self.columnCount()):
    #                     item.setBackground(i, brushOn)
    #                 if not didScroll:
    #                     self.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)
    #                     didScroll = True
    #     self._actHandle = tHandle or None
    #     return

    ##
    #  Events
    ##

    # def mousePressEvent(self, event: QMouseEvent) -> None:
    #     """Overload mousePressEvent to clear selection if clicking the
    #     mouse in a blank area of the tree view, and to load a document
    #     for viewing if the user middle-clicked.
    #     """
    #     super().mousePressEvent(event)

    #     if event.button() == QtMouseLeft:
    #         selItem = self.indexAt(event.pos())
    #         if not selItem.isValid():
    #             self.clearSelection()

    #     elif event.button() == QtMouseMiddle:
    #         selItem = self.itemAt(event.pos())
    #         if not isinstance(selItem, QTreeWidgetItem):
    #             return

    #         tHandle, sTitle = self.getSelectedHandle()
    #         if tHandle is None:
    #             return

    #         self.novelView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW, sTitle or "", False)

    #     return

    # def focusOutEvent(self, event: QFocusEvent) -> None:
    #     """Clear the selection when the tree no longer has focus."""
    #     super().focusOutEvent(event)
    #     self.clearSelection()
    #     return

    ##
    #  Private Slots
    ##

    # @pyqtSlot("QModelIndex")
    # def _treeItemClicked(self, index: QModelIndex) -> None:
    #     """The user clicked on an item in the tree."""
    #     if index.column() == self.C_MORE:
    #         tHandle = index.siblingAtColumn(self.C_DATA).data(self.D_HANDLE)
    #         sTitle = index.siblingAtColumn(self.C_DATA).data(self.D_TITLE)
    #         tipPos = self.mapToGlobal(self.visualRect(index).topRight())
    #         self._popMetaBox(tipPos, tHandle, sTitle)
    #     return

    # @pyqtSlot()
    # def _treeSelectionChange(self) -> None:
    #     """Extract the handle and line number of the currently selected
    #     title, and send it to the tree meta panel.
    #     """
    #     tHandle, _ = self.getSelectedHandle()
    #     if tHandle is not None:
    #         self.novelView.selectedItemChanged.emit(tHandle)
    #     return

    # @pyqtSlot("QTreeWidgetItem*", int)
    # def _treeDoubleClick(self, item: QTreeWidgetItem, column: int) -> None:
    #     """Extract the handle and line number of the title double-
    #     clicked, and send it to the main gui class for opening in the
    #     document editor.
    #     """
    #     tHandle, sTitle = self.getSelectedHandle()
    #     self.novelView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, sTitle or "", True)
    #     return

    ##
    #  Internal Functions
    ##

    # def _populateTree(self, rootHandle: str | None) -> None:
    #     """Build the tree based on the project index."""
    #     self.clearContent()
    #     tStart = time()
    #     logger.debug("Building novel tree for root item '%s'", rootHandle)

    #     novStruct = SHARED.project.index.novelStructure(rootHandle=rootHandle, activeOnly=True)
    #     for tKey, tHandle, sTitle, novIdx in novStruct:
    #         if novIdx.level == "H0":
    #             continue

    #         newItem = QTreeWidgetItem()
    #         newItem.setData(self.C_DATA, self.D_HANDLE, tHandle)
    #         newItem.setData(self.C_DATA, self.D_TITLE, sTitle)
    #         newItem.setData(self.C_DATA, self.D_KEY, tKey)
    #         newItem.setTextAlignment(self.C_WORDS, QtAlignRight)

    #         self._updateTreeItemValues(newItem, novIdx, tHandle, sTitle)
    #         self._treeMap[tKey] = newItem
    #         self.addTopLevelItem(newItem)

    #     self.setActiveHandle(self._actHandle)

    #     logger.debug("Novel Tree built in %.3f ms", (time() - tStart)*1000)
    #     self._lastBuild = time()

    #     return

    # def _updateTreeItemValues(
    #     self, trItem: QTreeWidgetItem, idxItem: IndexHeading, tHandle: str, sTitle: str
    # ) -> None:
    #     """Set the tree item values from the index entry."""
    #     iLevel = nwStyles.H_LEVEL.get(idxItem.level, 0)
    #     hDec = SHARED.theme.getHeaderDecoration(iLevel)

    #     trItem.setData(self.C_TITLE, QtDecoration, hDec)
    #     trItem.setText(self.C_TITLE, idxItem.title)
    #     trItem.setFont(self.C_TITLE, self._hFonts[iLevel])
    #     trItem.setText(self.C_WORDS, f"{idxItem.wordCount:n}")
    #     trItem.setData(self.C_MORE, QtDecoration, self._pMore)

    #     # Custom column
    #     viewport = self.viewport()
    #     mW = int(self._lastColSize * (viewport.width() if viewport else 100))
    #     lastText, toolTip = self._getLastColumnText(tHandle, sTitle)
    #     elideText = self.fontMetrics().elidedText(lastText, Qt.TextElideMode.ElideRight, mW)
    #     trItem.setText(self.C_EXTRA, elideText)
    #     trItem.setData(self.C_DATA, self.D_EXTRA, lastText)
    #     trItem.setToolTip(self.C_EXTRA, toolTip)

    #     return

    # def _getLastColumnText(self, tHandle: str, sTitle: str) -> tuple[str, str]:
    #     """Generate text for the last column based on user settings."""
    #     if self._lastCol == NovelTreeColumn.HIDDEN:
    #         return "", ""

    #     refData = []
    #     refName = ""
    #     refs = SHARED.project.index.getReferences(tHandle, sTitle)
    #     if self._lastCol == NovelTreeColumn.POV:
    #         refData = refs[nwKeyWords.POV_KEY]
    #         refName = self._povLabel

    #     elif self._lastCol == NovelTreeColumn.FOCUS:
    #         refData = refs[nwKeyWords.FOCUS_KEY]
    #         refName = self._focLabel

    #     elif self._lastCol == NovelTreeColumn.PLOT:
    #         refData = refs[nwKeyWords.PLOT_KEY]
    #         refName = self._pltLabel

    #     if refData:
    #         toolText = ", ".join(refData)
    #         return toolText, f"{refName}: {toolText}"

    #     return "", ""
