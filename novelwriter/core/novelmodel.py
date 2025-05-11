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

from typing import TYPE_CHECKING

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QIcon, QPixmap

from novelwriter import SHARED
from novelwriter.constants import nwKeyWords, nwLabels, nwStyles, trConst
from novelwriter.enum import nwNovelExtra
from novelwriter.types import QtAlignRight

if TYPE_CHECKING:
    from novelwriter.core.indexdata import IndexHeading, IndexNode

logger = logging.getLogger(__name__)

C_FACTOR = 0x0100

R_TEXT   = Qt.ItemDataRole.DisplayRole
R_ICON   = Qt.ItemDataRole.DecorationRole
R_ALIGN  = Qt.ItemDataRole.TextAlignmentRole
R_TIP    = Qt.ItemDataRole.ToolTipRole
R_ACCESS = Qt.ItemDataRole.AccessibleTextRole
R_HANDLE = 0xff01
R_KEY    = 0xff02

T_NodeData = str | QIcon | QPixmap | Qt.AlignmentFlag | None


class NovelModel(QAbstractTableModel):

    __slots__ = ("_columns", "_extraKey", "_extraLabel", "_more", "_rows")

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[dict[int, T_NodeData]] = []
        self._more = SHARED.theme.getIcon("more_arrow")
        self._columns = 3
        self._extraKey = ""
        self._extraLabel = ""
        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: NovelModel")
        return

    ##
    #  Properties
    ##

    @property
    def columns(self) -> int:
        """Return the number of columns."""
        return self._columns

    ##
    #  Setters
    ##

    def setExtraColumn(self, extra: nwNovelExtra) -> None:
        """Set extra data column settings."""
        match extra:
            case nwNovelExtra.HIDDEN:
                self._columns = 3
                self._extraKey = ""
                self._extraLabel = ""
            case nwNovelExtra.POV:
                self._columns = 4
                self._extraKey = nwKeyWords.POV_KEY
                self._extraLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.POV_KEY])
            case nwNovelExtra.FOCUS:
                self._columns = 4
                self._extraKey = nwKeyWords.FOCUS_KEY
                self._extraLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.FOCUS_KEY])
            case nwNovelExtra.PLOT:
                self._columns = 4
                self._extraKey = nwKeyWords.PLOT_KEY
                self._extraLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY])
        return

    ##
    #  Model Interface
    ##

    def rowCount(self, index: QModelIndex) -> int:
        """Return the number of rows."""
        return len(self._rows)

    def columnCount(self, index: QModelIndex) -> int:
        """Return the number of columns."""
        return self._columns

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> T_NodeData:
        """Return display data for a node."""
        try:
            return self._rows[index.row()].get(C_FACTOR*index.column() | role)
        except Exception:
            logger.error("Novel model index is inconsistent")
        return None

    def handle(self, index: QModelIndex) -> str | None:
        """Return item handle for the row."""
        try:
            return self._rows[index.row()].get(R_HANDLE)  # type: ignore
        except Exception:
            logger.error("Novel model index is inconsistent")
        return None

    def key(self, index: QModelIndex) -> str | None:
        """Return item handle for the row."""
        try:
            return self._rows[index.row()].get(R_KEY)  # type: ignore
        except Exception:
            logger.error("Novel model index is inconsistent")
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
                self._rows.append(self._generateEntry(handle, key, head))
        return

    def refresh(self, node: IndexNode) -> bool:
        """Refresh an index node."""
        handle = node.handle
        current = []
        for i, row in enumerate(self._rows):
            if row.get(R_HANDLE) == handle:
                current.append(i)

        if current == []:
            logger.warning("No novel model entries for '%s'", handle)
            return False

        cols = self._columns - 1
        first = current[0]
        last = current[-1]

        remains = []
        for key, head in node.items():
            if key != "T0000":
                if current:
                    j = current.pop(0)
                    self._rows[j] = self._generateEntry(handle, key, head)
                else:
                    remains.append((key, head))

        self.dataChanged.emit(self.createIndex(first, 0), self.createIndex(last, cols))

        if remains:
            # Inserting is safe for out of bounds indices
            self.beginInsertRows(QModelIndex(), last, last + len(remains) - 1)
            for k, (key, head) in enumerate(remains, last + 1):
                self._rows.insert(k, self._generateEntry(handle, key, head))
            self.endInsertRows()
        elif current:
            # Deleting ranges are safe for out of bounds indices
            self.beginRemoveRows(QModelIndex(), current[0], current[-1])
            del self._rows[current[0]:current[-1] + 1]
            self.endRemoveRows()

        return True

    ##
    #  Internal Functions
    ##

    def _generateEntry(self, handle: str, key: str, head: IndexHeading) -> dict[int, T_NodeData]:
        """Generate a cache entry."""
        iLevel = nwStyles.H_LEVEL.get(head.level, 0)
        data = {}
        data[C_FACTOR*0 | R_TIP] = head.title
        data[C_FACTOR*0 | R_TEXT] = head.title
        data[C_FACTOR*0 | R_ICON] = SHARED.theme.getHeaderDecoration(iLevel)
        data[C_FACTOR*1 | R_TEXT] = f"{head.mainCount:n}"
        data[C_FACTOR*1 | R_ALIGN] = QtAlignRight
        if self._columns == 3:
            data[C_FACTOR*2 | R_ICON] = self._more
        else:
            if self._extraKey and (refs := head.getReferencesByKeyword(self._extraKey)):
                text = ", ".join(refs)
                data[C_FACTOR*2 | R_TEXT] = text
                data[C_FACTOR*2 | R_TIP] = f"<b>{self._extraLabel}:</b> {text}"
                data[C_FACTOR*2 | R_ACCESS] = f"{self._extraLabel}: {text}"
            data[C_FACTOR*3 | R_ICON] = self._more
        data[R_HANDLE] = handle
        data[R_KEY] = key
        return data
