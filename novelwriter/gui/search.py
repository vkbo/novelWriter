"""
novelWriter – GUI Project Search
================================

File History:
Created: 2024-03-21 [2.4b1]  GuiProjectSearch

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

from time import time

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCursor, QKeyEvent, QPalette
from PyQt5.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QToolBar, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget, qApp
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import checkInt
from novelwriter.core.coretools import DocSearch
from novelwriter.core.item import NWItem

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 120.0  # 2 minutes


class GuiProjectSearch(QWidget):

    C_NAME   = 0
    C_RESULT = 0
    C_COUNT  = 1

    D_HANDLE = Qt.ItemDataRole.UserRole
    D_RESULT = Qt.ItemDataRole.UserRole + 1

    selectedItemChanged = pyqtSignal(str)
    openDocumentSelectRequest = pyqtSignal(str, int, int, bool)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiProjectSearch")

        iPx = SHARED.theme.baseIconSize
        mPx = CONFIG.pxInt(2)

        self._time = time()
        self._search = DocSearch()
        self._blocked = False

        # Header
        self.viewLabel = QLabel(self.tr("Project Search"))
        self.viewLabel.setFont(SHARED.theme.guiFontB)
        self.viewLabel.setContentsMargins(mPx, mPx, 0, mPx)

        # Options
        self.searchOpt = QToolBar(self)
        self.searchOpt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.searchOpt.setIconSize(QSize(iPx, iPx))
        self.searchOpt.setContentsMargins(0, 0, 0, 0)

        self.toggleCase = self.searchOpt.addAction(self.tr("Case Sensitive"))
        self.toggleCase.setCheckable(True)
        self.toggleCase.setChecked(CONFIG.searchProjCase)
        self.toggleCase.toggled.connect(self._toggleCase)

        self.toggleWord = self.searchOpt.addAction(self.tr("Whole Words Only"))
        self.toggleWord.setCheckable(True)
        self.toggleWord.setChecked(CONFIG.searchProjWord)
        self.toggleWord.toggled.connect(self._toggleWord)

        self.toggleRegEx = self.searchOpt.addAction(self.tr("RegEx Mode"))
        self.toggleRegEx.setCheckable(True)
        self.toggleRegEx.setChecked(CONFIG.searchProjRegEx)
        self.toggleRegEx.toggled.connect(self._toggleRegEx)

        # Search Box
        self.searchText = QLineEdit(self)
        self.searchText.setPlaceholderText(self.tr("Search text ..."))
        self.searchText.setClearButtonEnabled(True)

        self.searchAction = self.searchText.addAction(
            SHARED.theme.getIcon("search"), QLineEdit.ActionPosition.TrailingPosition
        )
        self.searchAction.triggered.connect(self._processSearch)

        # Search Result
        self.searchResult = QTreeWidget(self)
        self.searchResult.setHeaderHidden(True)
        self.searchResult.setColumnCount(2)
        self.searchResult.setIconSize(QSize(iPx, iPx))
        self.searchResult.setIndentation(iPx)
        self.searchResult.itemDoubleClicked.connect(self._searchResultDoubleClicked)
        self.searchResult.itemSelectionChanged.connect(self._searchResultSelected)

        treeHeader = self.searchResult.header()
        treeHeader.setStretchLastSection(False)
        treeHeader.setSectionResizeMode(self.C_NAME, QHeaderView.ResizeMode.Stretch)
        treeHeader.setSectionResizeMode(self.C_COUNT, QHeaderView.ResizeMode.ResizeToContents)

        # Assemble
        self.headerBox = QHBoxLayout()
        self.headerBox.addWidget(self.viewLabel, 1)
        self.headerBox.addWidget(self.searchOpt, 0)
        self.headerBox.setContentsMargins(0, 0, 0, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.headerBox, 0)
        self.outerBox.addWidget(self.searchText, 0)
        self.outerBox.addWidget(self.searchResult, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(mPx)

        self.setLayout(self.outerBox)
        self.updateTheme()

        logger.debug("Ready: GuiProjectSearch")

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        qPalette = self.palette()
        qPalette.setBrush(QPalette.ColorRole.Window, qPalette.base())
        self.setPalette(qPalette)

        self.searchAction.setIcon(SHARED.theme.getIcon("search"))
        self.toggleCase.setIcon(SHARED.theme.getIcon("search_case"))
        self.toggleWord.setIcon(SHARED.theme.getIcon("search_word"))
        self.toggleRegEx.setIcon(SHARED.theme.getIcon("search_regex"))

        return

    def processReturn(self) -> None:
        """Process a return keypress forwarded from the main GUI."""
        if self.searchText.hasFocus():
            self._processSearch()
        elif (
            self.searchResult.hasFocus()
            and (items := self.searchResult.selectedItems())
            and (data := items[0].data(0, self.D_RESULT))
            and len(data) == 3
        ):
            self.openDocumentSelectRequest.emit(
                str(data[0]), checkInt(data[1], -1), checkInt(data[2], -1), False
            )
        return

    def beginSearch(self) -> None:
        """Focus the search box and select its text, if any."""
        self.searchText.setFocus()
        self.searchText.selectAll()
        return

    def closeProjectTasks(self) -> None:
        """Run close project tasks."""
        self.searchText.clear()
        self.searchResult.clear()
        return

    ##
    #  Events
    ##

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Process key press events. This handles up and down arrow key
        presses to jump between search text box and result tree.
        """
        if (
            event.key() == Qt.Key.Key_Down
            and self.searchText.hasFocus()
            and (first := self.searchResult.topLevelItem(0))
        ):
            first.setSelected(True)
            self.searchResult.setFocus()
        elif (
            event.key() == Qt.Key.Key_Up
            and self.searchResult.hasFocus()
            and (first := self.searchResult.topLevelItem(0))
            and first.isSelected()
        ):
            first.setSelected(False)
            self.searchText.setFocus()
        else:
            super().keyPressEvent(event)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _processSearch(self) -> None:
        """Perform a search."""
        if not self._blocked:
            qApp.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            start = time()
            self._blocked = True
            self.searchResult.clear()
            if text := self.searchText.text():
                self._search.setUserRegEx(self.toggleRegEx.isChecked())
                self._search.setCaseSensitive(self.toggleCase.isChecked())
                self._search.setWholeWords(self.toggleWord.isChecked())
                for item, results, capped in self._search.iterSearch(SHARED.project, text):
                    self._appendResultSet(item, results, capped)
            logger.debug("Search took %.3f ms", 1000*(time() - start))
            self._time = time()
            qApp.restoreOverrideCursor()
        self._blocked = False
        return

    @pyqtSlot()
    def _searchResultSelected(self) -> None:
        """Process search result selection."""
        if items := self.searchResult.selectedItems():
            if (data := items[0].data(0, self.D_RESULT)) and len(data) == 3:
                self.selectedItemChanged.emit(str(data[0]))
            elif data := items[0].data(0, self.D_HANDLE):
                self.selectedItemChanged.emit(str(data))
        return

    @pyqtSlot("QTreeWidgetItem*", int)
    def _searchResultDoubleClicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Process search result double click."""
        if (data := item.data(0, self.D_RESULT)) and len(data) == 3:
            self.openDocumentSelectRequest.emit(
                str(data[0]), checkInt(data[1], -1), checkInt(data[2], -1), True
            )
        return

    @pyqtSlot(bool)
    def _toggleCase(self, state: bool) -> None:
        """Enable/disable case sensitive mode."""
        CONFIG.searchProjCase = state
        return

    @pyqtSlot(bool)
    def _toggleWord(self, state: bool) -> None:
        """Enable/disable whole word search mode."""
        CONFIG.searchProjWord = state
        return

    @pyqtSlot(bool)
    def _toggleRegEx(self, state: bool) -> None:
        """Enable/disable regular expression search mode."""
        CONFIG.searchProjRegEx = state
        return

    ##
    #  Internal Functions
    ##

    def _appendResultSet(
        self, nwItem: NWItem, results: list[tuple[int, int, str]], capped: bool
    ) -> None:
        """Populate the result tree."""
        if results:
            tHandle = nwItem.itemHandle
            docIcon = SHARED.theme.getItemIcon(
                nwItem.itemType, nwItem.itemClass,
                nwItem.itemLayout, nwItem.mainHeading
            )
            ext = "+" if capped else ""

            tItem = QTreeWidgetItem()
            tItem.setText(self.C_NAME, nwItem.itemName)
            tItem.setIcon(self.C_NAME, docIcon)
            tItem.setData(self.C_NAME, self.D_HANDLE, tHandle)
            tItem.setText(self.C_COUNT, f"({len(results):n}{ext})")
            tItem.setTextAlignment(self.C_COUNT, Qt.AlignmentFlag.AlignRight)
            tItem.setForeground(self.C_COUNT, self.palette().highlight())
            self.searchResult.addTopLevelItem(tItem)

            rItems = []
            for start, length, context in results:
                rItem = QTreeWidgetItem()
                rItem.setText(0, context)
                rItem.setData(0, self.D_RESULT, (tHandle, start, length))
                rItems.append(rItem)

            tItem.addChildren(rItems)
            tItem.setExpanded(True)

            parent = self.searchResult.indexFromItem(tItem)
            for i in range(tItem.childCount()):
                self.searchResult.setFirstColumnSpanned(i, parent, True)

            qApp.processEvents()

        return

# END Class GuiProjectSearch
