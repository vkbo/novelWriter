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

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QToolBar, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import checkInt
from novelwriter.core.coretools import DocSearch
from novelwriter.core.item import NWItem

logger = logging.getLogger(__name__)


class GuiProjectSearch(QWidget):

    D_HANDLE = Qt.ItemDataRole.UserRole
    D_RESULT = Qt.ItemDataRole.UserRole + 1

    openDocumentSelectRequest = pyqtSignal(str, int, int)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiProjectSearch")

        iPx = SHARED.theme.baseIconSize
        mPx = CONFIG.pxInt(2)

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

        self.toggleWord = self.searchOpt.addAction(self.tr("Whole Words Only"))
        self.toggleWord.setCheckable(True)

        self.toggleRegEx = self.searchOpt.addAction(self.tr("RegEx Mode"))
        self.toggleRegEx.setCheckable(True)

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
        self.searchResult.setIconSize(QSize(iPx, iPx))
        self.searchResult.setIndentation(iPx)
        self.searchResult.itemPressed.connect(self._searchResultSelected)

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
        """Process a return key press forwarded from main GUI."""
        if self.searchText.hasFocus():
            self._processSearch()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _processSearch(self) -> None:
        """Perform a search."""
        self.searchResult.clear()
        if text := self.searchText.text():
            search = DocSearch(
                SHARED.project, self.toggleRegEx.isChecked(),
                self.toggleCase.isChecked(), self.toggleWord.isChecked()
            )
            for item, results in search.iterSearch(text):
                self._appendResultSet(item, results)
        return

    @pyqtSlot("QTreeWidgetItem*", int)
    def _searchResultSelected(self, item: QTreeWidgetItem, column: int) -> None:
        """Process search result selection."""
        if (data := item.data(0, self.D_RESULT)) and len(data) == 3:
            self.openDocumentSelectRequest.emit(
                str(data[0]), checkInt(data[1], -1), checkInt(data[2], -1)
            )
        return

    ##
    #  Internal Functions
    ##

    def _appendResultSet(self, nwItem: NWItem, results: list[tuple[int, int, str]]) -> None:
        """Populate the result tree."""
        if results:
            tHandle = nwItem.itemHandle
            docIcon = SHARED.theme.getItemIcon(
                nwItem.itemType, nwItem.itemClass,
                nwItem.itemLayout, nwItem.mainHeading
            )

            tItem = QTreeWidgetItem()
            tItem.setText(0, f"{nwItem.itemName} ({len(results)})")
            tItem.setIcon(0, docIcon)
            tItem.setData(0, self.D_HANDLE, tHandle)
            rItems = []
            for start, length, context in results:
                rItem = QTreeWidgetItem()
                rItem.setText(0, context)
                rItem.setData(0, self.D_RESULT, (tHandle, start, length))
                rItems.append(rItem)
            tItem.addChildren(rItems)
            tItem.setExpanded(True)
            self.searchResult.addTopLevelItem(tItem)
        return

# END Class GuiProjectSearch
