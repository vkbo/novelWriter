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
from novelwriter.types import QtAlignRight

logger = logging.getLogger(__name__)

C_FACTOR = 0x0100

R_TEXT   = Qt.ItemDataRole.DisplayRole
R_ICON   = Qt.ItemDataRole.DecorationRole
R_ALIGN  = Qt.ItemDataRole.TextAlignmentRole
R_TIP    = Qt.ItemDataRole.ToolTipRole
R_HANDLE = 0xff01
R_KEY    = 0xff02

T_NodeData = str | tuple[str, str] | QIcon | QPixmap | Qt.AlignmentFlag | None


class NovelModel(QAbstractTableModel):

    __slots__ = ("_rows", "_more", "_columns")

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[dict[int, T_NodeData]] = []
        self._more = SHARED.theme.getIcon("more_arrow")
        self._columns = 3
        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: NovelModel")
        return

    ##
    #  Setters
    ##

    def setExtraColumn(self, state: bool) -> None:
        """Set extra data column settings."""
        self._columns = 4 if state else 3
        return

    ##
    #  Model Interface
    ##

    def rowCount(self, index: QModelIndex) -> int:
        """Return the number of rows for an entry."""
        return len(self._rows)

    def columnCount(self, index: QModelIndex) -> int:
        """Return the number of columns for an entry."""
        return self._columns

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> T_NodeData:
        """Return display data for a node."""
        try:
            return self._rows[index.row()].get(C_FACTOR*index.column() | role)
        except Exception:
            print("NovelModel Debug: Oops!")
        return None

    def handle(self, index: QModelIndex) -> str | None:
        """Return item handle for the row."""
        try:
            return self._rows[index.row()].get(R_HANDLE)  # type: ignore
        except Exception:
            print("NovelModel Debug: Oops!")
        return None

    def key(self, index: QModelIndex) -> str | None:
        """Return item handle for the row."""
        try:
            return self._rows[index.row()].get(R_KEY)  # type: ignore
        except Exception:
            print("NovelModel Debug: Oops!")
        return None

    ##
    #  Data Methods
    ##

    def clear(self) -> None:
        """Clear the model."""
        self._rows.clear()
        return

    def append(self, node: IndexNode) -> None:
        """Append a node to the model."""
        handle = node.handle
        for key, head in node.items():
            if key != "T0000":
                iLevel = nwStyles.H_LEVEL.get(head.level, 0)
                more = self._columns - 1
                data = {}
                data[C_FACTOR*0 | R_TEXT] = head.title
                data[C_FACTOR*0 | R_ICON] = SHARED.theme.getHeaderDecoration(iLevel)
                data[C_FACTOR*1 | R_TEXT] = f"{head.mainCount:n}"
                data[C_FACTOR*1 | R_ALIGN] = QtAlignRight
                data[C_FACTOR*more | R_ICON] = self._more
                data[R_HANDLE] = handle
                data[R_KEY] = key
                self._rows.append(data)
        return
