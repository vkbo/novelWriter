"""
novelWriter – GUI Project Search
================================

This file is a part of novelWriter
Copyright (C) 2024 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa

from __future__ import annotations

import logging

from enum import Enum
from time import time
from typing import TYPE_CHECKING

from PyQt6.QtCore import QModelIndex, QRect, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QCursor, QKeyEvent, QPainter, QPalette
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QToolBar,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import minmax
from novelwriter.core.coretools import DocSearch
from novelwriter.enum import nwDocMode
from novelwriter.extensions.modified import NIconToolButton
from novelwriter.models.searchmodel import SearchNode, SearchResultModel
from novelwriter.types import (
    QtAlignMiddle,
    QtDisplayRole,
    QtHeaderStretch,
    QtHeaderToContents,
    QtHexArgb,
    QtKeyDown,
    QtKeyUp,
    QtModShift,
    QtSelected,
    QtUserRole,
)

if TYPE_CHECKING:
    from novelwriter.core.item import ProjectItem

logger = logging.getLogger(__name__)


class GuiProjectSearch(QWidget):
    """GUI: Project Search Panel."""

    selectedItemChanged = pyqtSignal(str)
    openDocumentRequest = pyqtSignal(str, Enum, str, bool)
    openDocumentSelectRequest = pyqtSignal(str, int, int, bool)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiProjectSearch")

        iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize

        self._search = DocSearch()
        self._model = SearchResultModel()
        self._blocked = False

        self.setContentsMargins(0, 0, 0, 0)
        self.setBackgroundRole(QPalette.ColorRole.Base)
        self.setAutoFillBackground(True)

        # Header
        self.viewLabel = QLabel(self.tr("Project Search"), self)
        self.viewLabel.setFont(SHARED.theme.guiFontB)
        self.viewLabel.setContentsMargins(4, 4, 0, 2)

        # Options
        self.searchOpt = QToolBar(self)
        self.searchOpt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.searchOpt.setIconSize(iSz)
        self.searchOpt.setContentsMargins(0, 0, 0, 0)

        self.tbCase = NIconToolButton(self, iSz, "search_case", "tool")
        self.tbCase.setToolTip(self.tr("Case Sensitive"))
        self.tbCase.setCheckable(True)
        self.tbCase.setChecked(CONFIG.searchProjCase)
        self.tbCase.clicked.connect(self._toggleCase)
        self.searchOpt.addWidget(self.tbCase)

        self.tbWord = NIconToolButton(self, iSz, "search_word", "tool")
        self.tbWord.setToolTip(self.tr("Whole Words Only"))
        self.tbWord.setCheckable(True)
        self.tbWord.setChecked(CONFIG.searchProjWord)
        self.tbWord.clicked.connect(self._toggleWord)
        self.searchOpt.addWidget(self.tbWord)

        self.tbRegEx = NIconToolButton(self, iSz, "search_regex", "tool")
        self.tbRegEx.setToolTip(self.tr("RegEx Mode"))
        self.tbRegEx.setCheckable(True)
        self.tbRegEx.setChecked(CONFIG.searchProjRegEx)
        self.tbRegEx.clicked.connect(self._toggleRegEx)
        self.searchOpt.addWidget(self.tbRegEx)

        # Search Box
        self.searchAction = QAction("", self)
        self.searchAction.setIcon(SHARED.theme.getIcon("search", "apply"))
        self.searchAction.triggered.connect(self._processSearch)

        self.searchText = QLineEdit(self)
        self.searchText.setPlaceholderText(self.tr("Search for"))
        self.searchText.setClearButtonEnabled(True)
        self.searchText.addAction(self.searchAction, QLineEdit.ActionPosition.TrailingPosition)

        # Search Result
        self.searchResult = QTreeView(self)
        self.searchResult.setModel(self._model)
        self.searchResult.setHeaderHidden(True)
        self.searchResult.setIconSize(iSz)
        self.searchResult.setIndentation(iPx)
        self.searchResult.setFrameStyle(QFrame.Shape.NoFrame)
        self.searchResult.setUniformRowHeights(True)
        self.searchResult.setAllColumnsShowFocus(True)
        self.searchResult.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.searchResult.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.searchResult.doubleClicked.connect(self._searchResultDoubleClicked)
        self.searchResult.setAccessibleName(self.viewLabel.text())

        self._matchDelegate = _SearchResultDelegate(self.searchResult)
        self.searchResult.setItemDelegateForColumn(SearchNode.C_NAME, self._matchDelegate)

        if header := self.searchResult.header():  # pragma: no branch
            header.setStretchLastSection(False)
            header.setSectionResizeMode(SearchNode.C_NAME, QtHeaderStretch)
            header.setSectionResizeMode(SearchNode.C_COUNT, QtHeaderToContents)

        if selModel := self.searchResult.selectionModel():  # pragma: no branch
            selModel.currentChanged.connect(self._searchResultSelected)

        # Assemble
        self.headerBox = QHBoxLayout()
        self.headerBox.addWidget(self.viewLabel, 1)
        self.headerBox.addWidget(self.searchOpt, 0, QtAlignMiddle)
        self.headerBox.setContentsMargins(0, 0, 0, 0)
        self.headerBox.setSpacing(0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.headerBox, 0)
        self.outerBox.addWidget(self.searchText, 0)
        self.outerBox.addWidget(self.searchResult, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(2)

        self.setLayout(self.outerBox)
        self.updateTheme(onInit=True)

        logger.debug("Ready: GuiProjectSearch")

    ##
    #  Methods
    ##

    def updateTheme(self, onInit: bool = False) -> None:
        """Update theme elements."""
        logger.debug("Theme Update: GuiProjectSearch")

        palette = QApplication.palette()
        colBase = palette.base().color().name(QtHexArgb)
        colFocus = palette.highlight().color().name(QtHexArgb)

        self.setStyleSheet(
            f"QLineEdit {{border: 1px solid {colBase}; padding: 2px;}} "
            f"QLineEdit:focus {{border: 1px solid {colFocus};}} "
        )

        self.searchAction.setIcon(SHARED.theme.getIcon("search", "apply"))
        self._model.updateTheme()
        self._matchDelegate.updateTheme()
        if not onInit:
            self.tbCase.refreshTheme()
            self.tbWord.refreshTheme()
            self.tbRegEx.refreshTheme()

    def processReturn(self) -> None:
        """Process a return keypress forwarded from the main GUI."""
        if self.searchText.hasFocus():
            self._processSearch()
        elif self.searchResult.hasFocus() and (result := self._model.result(self.searchResult.currentIndex())):
            handle, start, length = result
            if QApplication.keyboardModifiers() == QtModShift:
                self.openDocumentRequest.emit(handle, nwDocMode.VIEW, "", True)
            else:
                self.openDocumentSelectRequest.emit(handle, start, length, False)

    def beginSearch(self, text: str = "") -> None:
        """Focus the search box and select its text, if any."""
        self.searchText.setFocus()
        self.searchText.selectAll()
        if text:
            self.searchText.setText(text.partition("\n")[0])
            self.searchText.selectAll()

    def closeProjectTasks(self) -> None:
        """Run close project tasks."""
        self.searchText.clear()
        self._model.clear()

    def refreshCurrentSearch(self) -> None:
        """Refresh the search if there is one."""
        if self._model.rowCount(QModelIndex()) > 0:
            self._processSearch()

    ##
    #  Events
    ##

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Process key press events. This handles up and down arrow key
        presses to jump between search text box and result tree.
        """
        if event.key() == QtKeyDown and self.searchText.hasFocus() and (first := self._model.index(0, 0)).isValid():
            self.searchResult.setCurrentIndex(first)
            self.searchResult.setFocus()
        elif (
            event.key() == QtKeyUp
            and self.searchResult.hasFocus()
            and (first := self._model.index(0, 0)).isValid()
            and self.searchResult.currentIndex() == first
        ):
            self.searchResult.clearSelection()
            self.searchText.setFocus()
        else:
            super().keyPressEvent(event)

    ##
    #  Public Slots
    ##

    @pyqtSlot(str, float)
    def textChanged(self, tHandle: str, timeStamp: float) -> None:
        """Update search result for a specific document."""
        if (entry := self._model.entry(tHandle)) and timeStamp > entry[1] and (nwItem := SHARED.project.tree[tHandle]):
            start = time()
            results, capped = self._search.searchText(SHARED.mainGui.docEditor.getText())
            self._addResult(nwItem, results, capped)
            logger.debug("Updated search for '%s' in %.3f ms", tHandle, 1000 * (time() - start))

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _processSearch(self) -> None:
        """Perform a search."""
        if not self._blocked:
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            start = time()
            SHARED.saveEditor()
            self._blocked = True
            self._model.clear()
            if text := self.searchText.text():
                self._search.setUserRegEx(self.tbRegEx.isChecked())
                self._search.setCaseSensitive(self.tbCase.isChecked())
                self._search.setWholeWords(self.tbWord.isChecked())
                handles = []
                for item, results, capped in self._search.iterSearch(SHARED.project, text):
                    if results:
                        self._model.setResult(item, results, capped)
                        handles.append(item.itemHandle)
                # Expanding a row forces the tree view to lay out all
                # currently loaded rows, so this is deferred until after
                # all results are in the model to avoid doing it once
                # per document as the tree grows
                for handle in handles:
                    self._expandResult(handle)
            logger.debug("Search took %.3f ms", 1000 * (time() - start))
            QApplication.restoreOverrideCursor()
        self._blocked = False

    @pyqtSlot(QModelIndex, QModelIndex)
    def _searchResultSelected(self, current: QModelIndex, previous: QModelIndex) -> None:
        """Process search result selection."""
        if result := self._model.result(current):
            self.selectedItemChanged.emit(result[0])
        elif handle := self._model.handle(current):
            self.selectedItemChanged.emit(handle)

    @pyqtSlot(QModelIndex)
    def _searchResultDoubleClicked(self, index: QModelIndex) -> None:
        """Process search result double click."""
        if result := self._model.result(index):
            handle, start, length = result
            self.openDocumentSelectRequest.emit(handle, start, length, True)

    @pyqtSlot(bool)
    def _toggleCase(self, state: bool) -> None:
        """Enable/disable case sensitive mode."""
        CONFIG.searchProjCase = state
        self.refreshCurrentSearch()

    @pyqtSlot(bool)
    def _toggleWord(self, state: bool) -> None:
        """Enable/disable whole word search mode."""
        CONFIG.searchProjWord = state
        self.refreshCurrentSearch()

    @pyqtSlot(bool)
    def _toggleRegEx(self, state: bool) -> None:
        """Enable/disable regular expression search mode."""
        CONFIG.searchProjRegEx = state
        self.refreshCurrentSearch()

    ##
    #  Internal Functions
    ##

    def _addResult(self, nwItem: ProjectItem, results: list[tuple[int, int, str, int]], capped: bool) -> None:
        """Add or update a document's results, and update the view."""
        if results:
            self._model.setResult(nwItem, results, capped)
            self._expandResult(nwItem.itemHandle)
            QApplication.processEvents()

    def _expandResult(self, handle: str) -> None:
        """Span and expand a document's rows in the result tree."""
        parent = self._model.indexFromHandle(handle)
        for row in range(self._model.rowCount(parent)):
            self.searchResult.setFirstColumnSpanned(row, parent, True)
        self.searchResult.setExpanded(parent, True)


RESULT_FLAGS = int(Qt.TextFlag.TextSingleLine) | int(QtAlignMiddle)
RESULT_MARGIN = 4


class _SearchResultDelegate(QStyledItemDelegate):
    """GUI: Search Result Match Delegate.

    Paints the match column, highlighting the matched substring of a
    match-level row with the palette's highlight colour. Document-level
    rows have no span data and are left to the default rendering.
    """

    __slots__ = ("_hlCol", "_hlTextCol", "_textCol")

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.updateTheme()

    def updateTheme(self) -> None:
        """Refresh the cached theme colours."""
        self._textCol = QApplication.palette().text().color()
        self._hlCol = QApplication.palette().highlight().color()
        self._hlTextCol = QApplication.palette().highlightedText().color()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Paint a search result entry, highlighting the match, if any."""
        if not isinstance(span := index.data(QtUserRole), tuple):
            super().paint(painter, option, index)
            return

        text = index.data(QtDisplayRole) or ""
        sPos, ePos = span
        rect = option.rect

        painter.save()
        painter.setClipRect(rect)
        painter.setFont(option.font)
        if bool(option.state & QtSelected):
            painter.fillRect(rect, self._hlCol)
            plainColor = self._hlTextCol
            matchColor = plainColor
        else:
            plainColor = self._textCol
            matchColor = self._hlCol

        metrics = painter.fontMetrics()
        avail = max(0, rect.width() - RESULT_MARGIN)
        text = metrics.elidedText(text, Qt.TextElideMode.ElideRight, avail)
        sPos = minmax(sPos, 0, len(text))
        ePos = minmax(ePos, sPos, len(text))

        x = rect.x() + RESULT_MARGIN
        y = rect.y()
        h = rect.height()
        for chunk, color in (
            (text[:sPos], plainColor),
            (text[sPos:ePos], matchColor),
            (text[ePos:], plainColor),
        ):
            if chunk:
                width = metrics.horizontalAdvance(chunk)
                painter.setPen(color)
                painter.drawText(QRect(x, y, width, h), RESULT_FLAGS, chunk)
                x += width

        painter.restore()
