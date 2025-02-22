"""
novelWriter – Novel Model
=========================

File History:
Created: 2025-02-22 [2.7b1] NovelModel

This file is a part of novelWriter
Copyright (C) 2025 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QIcon, QPixmap

from novelwriter import SHARED
from novelwriter.constants import nwStyles
from novelwriter.core.indexdata import IndexNode
from novelwriter.core.item import NWItem
from novelwriter.types import QtAlignRight

logger = logging.getLogger(__name__)

C_FACTOR = 0x0100

C_TITLE_TEXT  = 0x0000 | Qt.ItemDataRole.DisplayRole
C_TITLE_ICON  = 0x0000 | Qt.ItemDataRole.DecorationRole
C_COUNT_TEXT  = 0x0100 | Qt.ItemDataRole.DisplayRole
C_COUNT_ALIGN = 0x0100 | Qt.ItemDataRole.TextAlignmentRole
C_EXTRA_TEXT  = 0x0200 | Qt.ItemDataRole.DisplayRole
C_EXTRA_TIP   = 0x0200 | Qt.ItemDataRole.ToolTipRole
C_MORE_ICON   = 0x0300 | Qt.ItemDataRole.DecorationRole

T_NodeData = str | QIcon | QPixmap | Qt.AlignmentFlag | None


class NovelModel(QAbstractTableModel):

    def __init__(self, rootItem: NWItem) -> None:
        super().__init__()
        self._root = rootItem
        self._rows: list[tuple[str, str, dict]] = []
        self._more = SHARED.theme.getIcon("more_arrow")
        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: NovelModel")
        return

    ##
    #  Model Interface
    ##

    def rowCount(self, index: QModelIndex) -> int:
        """Return the number of rows for an entry."""
        return len(self._rows)

    def columnCount(self, index: QModelIndex) -> int:
        """Return the number of columns for an entry."""
        return 4

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> T_NodeData:
        """Return display data for a node."""
        if index.isValid() and (row := index.row()) < len(self._rows):
            return self._rows[row][2].get(C_FACTOR*index.column() | role)
        return None

    ##
    #  Data Methods
    ##

    def append(self, node: IndexNode) -> None:
        """Append a node to the model."""
        handle = node.handle
        for key, head in node.items():
            if key != "T0000":
                iLevel = nwStyles.H_LEVEL.get(head.level, 0)
                data = {}
                data[C_TITLE_TEXT]  = head.title
                data[C_TITLE_ICON]  = SHARED.theme.getHeaderDecoration(iLevel)
                data[C_COUNT_TEXT]  = f"{head.mainCount:n}"
                data[C_COUNT_ALIGN] = QtAlignRight
                data[C_MORE_ICON]   = self._more
                self._rows.append((handle, key, data))
        return
