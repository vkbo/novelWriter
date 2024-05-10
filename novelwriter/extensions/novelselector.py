"""
novelWriter – Custom Widget: Novel Selector
===========================================

File History:
Created: 2022-11-17 [2.0] NovelSelector

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

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QComboBox, QWidget

from novelwriter import SHARED
from novelwriter.constants import nwLabels
from novelwriter.enum import nwItemClass

logger = logging.getLogger(__name__)


class NovelSelector(QComboBox):

    novelSelectionChanged = pyqtSignal(str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._blockSignal = False
        self._firstHandle = None
        self._includeAll = False
        self._listFormat = None
        self.currentIndexChanged.connect(self._indexChanged)
        return

    ##
    #  Properties
    ##

    @property
    def handle(self) -> str:
        return self.currentData()

    @property
    def firstHandle(self) -> str | None:
        return self._firstHandle

    ##
    #  Methods
    ##

    def setHandle(self, tHandle: str | None, blockSignal: bool = True) -> None:
        """Set the currently selected handle."""
        if (index := self.findData(tHandle) if tHandle else (self.count() - 1)) >= 0:
            self._blockSignal = blockSignal
            self.setCurrentIndex(index)
            self._blockSignal = False
        return

    def setIncludeAll(self, value: bool) -> None:
        """Set flag to add an "All Novel Folders" option."""
        self._includeAll = value
        return

    def setListFormat(self, value: str | None) -> None:
        """Set a format string for the list entries."""
        if value is None or "{0}" in value:
            self._listFormat = value
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot()
    def refreshNovelList(self) -> None:
        """Rebuild the list of novel items."""
        self._blockSignal = True
        self._firstHandle = None
        self.clear()

        icon = SHARED.theme.getIcon(nwLabels.CLASS_ICON[nwItemClass.NOVEL])
        handle = self.currentData()
        for tHandle, nwItem in SHARED.project.tree.iterRoots(nwItemClass.NOVEL):
            if self._listFormat:
                name = self._listFormat.format(nwItem.itemName)
                self.addItem(name, tHandle)
            else:
                name = nwItem.itemName
                self.addItem(icon, nwItem.itemName, tHandle)
            if self._firstHandle is None:
                self._firstHandle = tHandle

        if self._includeAll:
            self.insertSeparator(self.count())
            self.addItem(icon, self.tr("All Novel Folders"), "")

        self.setHandle(handle)
        self.setEnabled(self.count() > 1)
        self._blockSignal = False

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _indexChanged(self, index: int) -> None:
        """Re-emit the change of selection signal, unless blocked."""
        if not self._blockSignal:
            self.novelSelectionChanged.emit(self.currentData())
        return
