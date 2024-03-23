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

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.core.coretools import DocSearch
from novelwriter.core.item import NWItem
from novelwriter.extensions.modified import NIconToolButton
from novelwriter.gui.theme import STYLES_MIN_TOOLBUTTON

logger = logging.getLogger(__name__)


class GuiProjectSearch(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiProjectSearch")

        iPx = SHARED.theme.baseIconSize
        mPx = CONFIG.pxInt(2)

        # Header
        self.viewLabel = QLabel(self.tr("Project Search"))
        self.viewLabel.setFont(SHARED.theme.guiFontB)
        self.viewLabel.setContentsMargins(mPx, mPx, 0, mPx)

        # Controls
        self.searchText = QLineEdit(self)
        self.searchText.setPlaceholderText(self.tr("Search text ..."))

        self.searchButton = NIconToolButton(self, iPx)
        self.searchButton.clicked.connect(self._processSearch)

        self.searchBar = QHBoxLayout()
        self.searchBar.addWidget(self.searchText)
        self.searchBar.addWidget(self.searchButton)

        # Search Result
        self.searchResult = QTreeWidget(self)
        self.searchResult.setHeaderHidden(True)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.viewLabel, 0)
        self.outerBox.addLayout(self.searchBar, 0)
        self.outerBox.addWidget(self.searchResult, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(0)

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

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_MIN_TOOLBUTTON)
        self.searchButton.setStyleSheet(buttonStyle)

        self.searchButton.setIcon(SHARED.theme.getIcon("search"))

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _processSearch(self) -> None:
        """Perform a search."""
        self.searchResult.clear()
        if text := self.searchText.text():
            search = DocSearch(SHARED.project)
            for item, results in search.iterSearch(text):
                self._appendResultSet(item, results)
        return

    ##
    #  Internal Functions
    ##

    def _appendResultSet(self, item: NWItem, results: list[tuple[int, int, str]]) -> None:
        """Populate the result tree."""
        if results:
            tItem = QTreeWidgetItem()
            tItem.setText(0, f"{item.itemName} ({len(results)})")
            rItems = []
            for start, end, context in results:
                rItem = QTreeWidgetItem()
                rItem.setText(0, context)
                rItems.append(rItem)
            tItem.addChildren(rItems)
            self.searchResult.addTopLevelItem(tItem)
        return

# END Class GuiProjectSearch
