"""
novelWriter – GUI Novel Tree
============================

File History:
Created:   2020-12-20 [1.1rc1] GuiNovelTree
Created:   2022-06-12 [2.0rc1] GuiNovelView
Created:   2022-06-12 [2.0rc1] GuiNovelToolBar
Rewritten: 2025-02-22 [2.7b1] GuiNovelView
Rewritten: 2025-02-22 [2.7b1] GuiNovelToolBar

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
from novelwriter.enum import nwChange, nwDocMode, nwNovelExtra, nwOutline
from novelwriter.extensions.modified import NIconToolButton, NTreeView
from novelwriter.extensions.novelselector import NovelSelector
from novelwriter.gui.theme import STYLES_MIN_TOOLBUTTON
from novelwriter.types import (
    QtHeaderStretch, QtHeaderToContents, QtScrollAlwaysOff, QtScrollAsNeeded,
    QtSizeExpanding
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
        self.refreshCurrentTree = self.novelBar.forceRefreshNovelTree

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
        self.novelBar.clearContent()
        self.novelBar.setEnabled(False)
        self.novelTree.clearContent()
        return

    def openProjectTasks(self) -> None:
        """Run open project tasks."""
        lastNovel = SHARED.project.data.getLastHandle("novel")
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
        logger.debug("Saving State: GuiNovelView")

        lastColType = self.novelTree.lastColType
        lastColSize = self.novelTree.lastColSize

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
        self.novelTree.setNovelModel(rootHandle)
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
        self.tbRefresh.clicked.connect(self.forceRefreshNovelTree)

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
        self.novelValue.updateTheme()
        self.tbNovel.setVisible(self.novelValue.count() > 1)

        self.forceRefreshNovelTree()

        return

    def clearContent(self) -> None:
        """Run clearing project tasks."""
        self.novelValue.clear()
        self.novelValue.setToolTip("")
        return

    def buildNovelRootMenu(self) -> None:
        """Build the novel root menu."""
        self.novelValue.refreshNovelList()
        self.novelView.setCurrentNovel(self.novelValue.handle)
        self.tbNovel.setVisible(self.novelValue.count() > 1)
        return

    def setCurrentRoot(self, rootHandle: str | None) -> None:
        """Set the current active root handle."""
        if rootHandle is None or rootHandle not in SHARED.project.tree:
            rootHandle = self.novelValue.firstHandle
        self.novelValue.setHandle(rootHandle)
        SHARED.project.data.setLastHandle(rootHandle, "novel")
        self.novelView.setCurrentNovel(rootHandle)
        self.novelView.novelTree.setAccessibleName(self.novelValue.currentText())
        return

    def setLastColType(self, colType: nwNovelExtra, doRefresh: bool = True) -> None:
        """Set the last column type."""
        self.aLastCol[colType].setChecked(True)
        self.novelView.novelTree.setLastColType(colType)
        if doRefresh:
            self.forceRefreshNovelTree()
            self.novelView.novelTree.resizeColumns()
        return

    def setActive(self, state: bool) -> None:
        """Set the widget active state, which enables automatic tree
        refresh when content structure changes.
        """
        self._active = state
        if (
            self._active
            and (handle := self.novelValue.handle)
            and self._refresh.get(handle, False)
        ):
            self._refreshNovelTree(self.novelValue.handle)
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot()
    def forceRefreshNovelTree(self) -> None:
        """Rebuild the current tree."""
        if tHandle := self.novelValue.handle:
            self.novelView.setCurrentNovel(tHandle)
            SHARED.project.index.refreshNovelModel(tHandle)
            self._refresh[tHandle] = False
        return

    ##
    #  Private Slots
    ##

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

        # Widget Setup
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
        if (model := self._getModel()) and (index := self.currentIndex()).isValid():
            return model.handle(index), model.key(index)
        return None, None

    ##
    #  Setters
    ##

    def setNovelModel(self, tHandle: str | None) -> None:
        """Set the current novel model."""
        if tHandle and (model := SHARED.project.index.getNovelModel(tHandle)):
            if model is not self.model():
                self.setModel(model)
                self.resizeColumns()
        else:
            self.clearContent()
        return

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

    def clearContent(self) -> None:
        """Clear the tree view."""
        self.setModel(None)
        return

    def resizeColumns(self) -> None:
        """Set the correct column sizes."""
        if (header := self.header()) and (model := self._getModel()) and (vp := self.viewport()):
            header.setStretchLastSection(False)
            header.setMinimumSectionSize(SHARED.theme.baseIconHeight + 6)
            header.setSectionResizeMode(0, QtHeaderStretch)
            header.setSectionResizeMode(1, QtHeaderToContents)
            header.setSectionResizeMode(2, QtHeaderToContents)
            if model.columns == 4:
                header.setSectionResizeMode(3, QtHeaderToContents)
                header.setMaximumSectionSize(int(self._lastColSize * vp.width()))
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
        def appendTags(refs: dict, key: str, lines: list[str]) -> None:
            """Generate a reference list for a given reference key."""
            if tags := ", ".join(refs.get(key, [])):
                lines.append(f"<b>{trConst(nwLabels.KEY_NAME[key])}:</b> {tags}")
            return

        if head := SHARED.project.index.getItemHeading(tHandle, sTitle):
            logger.debug("Generating meta data tooltip for '%s:%s'", tHandle, sTitle)
            if synopsis := head.synopsis:
                label = trConst(nwLabels.OUTLINE_COLS[nwOutline.SYNOP])
                synopsis = f"<p><b>{label}:</b> {synopsis}</p>"

            lines = []
            if head := SHARED.project.index.getItemHeading(tHandle, sTitle):
                tags = head.getReferences()
                appendTags(tags, nwKeyWords.POV_KEY, lines)
                appendTags(tags, nwKeyWords.FOCUS_KEY, lines)
                appendTags(tags, nwKeyWords.CHAR_KEY, lines)
                appendTags(tags, nwKeyWords.PLOT_KEY, lines)
                appendTags(tags, nwKeyWords.TIME_KEY, lines)
                appendTags(tags, nwKeyWords.WORLD_KEY, lines)
                appendTags(tags, nwKeyWords.OBJECT_KEY, lines)
                appendTags(tags, nwKeyWords.ENTITY_KEY, lines)
                appendTags(tags, nwKeyWords.CUSTOM_KEY, lines)

            text = ""
            if lines:
                refs = "<br>".join(lines)
                text = f"<p>{refs}</p>"
            if tooltip := (text + synopsis or self.tr("No meta data")):
                QToolTip.showText(qPos, tooltip)
        return
