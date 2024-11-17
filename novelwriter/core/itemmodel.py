"""
novelWriter – Project Item Model
================================

File History:
Created: 2024-11-16 [2.7b1] ProjectNode
Created: 2024-11-16 [2.7b1] ProjectModel

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

from typing import TYPE_CHECKING, Any

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QIcon

from novelwriter import SHARED
from novelwriter.core.item import NWItem
from novelwriter.types import QtAlignRight

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.tree import NWTree

logger = logging.getLogger(__name__)

COL_MASK = 0x0100

C_LABEL_TEXT  = 0x0000 | Qt.ItemDataRole.DisplayRole
C_LABEL_ICON  = 0x0000 | Qt.ItemDataRole.DecorationRole
C_LABEL_TIP   = 0x0000 | Qt.ItemDataRole.ToolTipRole
C_COUNT_TEXT  = 0x0100 | Qt.ItemDataRole.DisplayRole
C_COUNT_ICON  = 0x0100 | Qt.ItemDataRole.DecorationRole
C_COUNT_ALIGN = 0x0100 | Qt.ItemDataRole.TextAlignmentRole
C_ACTIVE_ICON = 0x0200 | Qt.ItemDataRole.DecorationRole
C_ACTIVE_TIP  = 0x0200 | Qt.ItemDataRole.ToolTipRole
C_STATUS_ICON = 0x0300 | Qt.ItemDataRole.DecorationRole
C_STATUS_TIP  = 0x0300 | Qt.ItemDataRole.ToolTipRole


class ProjectNode:

    __slots__ = ("_item", "_children", "_parent", "_row", "_cache", "_count")

    def __init__(self, item: NWItem) -> None:
        self._item = item
        self._children = []
        self._parent: ProjectNode | None = None
        self._row = 0
        self._cache: dict[int, str | QIcon | Qt.AlignmentFlag] = {}
        self.refresh()
        return

    def refresh(self) -> None:
        cache: dict[int, str | QIcon | Qt.AlignmentFlag] = {}

        # Label
        cache[C_LABEL_ICON] = SHARED.theme.getItemIcon(
            self._item.itemType, self._item.itemClass,
            self._item.itemLayout, self._item.mainHeading
        )
        cache[C_LABEL_TEXT] = self._item.itemName
        cache[C_LABEL_TIP] = self._item.itemName

        # Count
        cache[C_COUNT_ALIGN] = QtAlignRight

        # Active
        if self._item.isFileType():
            if self._item.isActive:
                cache[C_ACTIVE_ICON] = SHARED.theme.getIcon("checked")
            else:
                cache[C_ACTIVE_ICON] = SHARED.theme.getIcon("unchecked")
        else:
            cache[C_ACTIVE_ICON] = SHARED.theme.getIcon("noncheckable")

        # Status
        sText, sIcon = self._item.getImportStatus()
        cache[C_STATUS_ICON] = sIcon
        cache[C_STATUS_TIP] = sText

        self._cache = cache
        self.updateCount()

        return

    def updateCount(self) -> None:
        self._count = self._item.wordCount + sum(c._count for c in self._children)
        self._cache[C_COUNT_TEXT] = f"{self._count:n}"
        if parent := self._parent:
            parent.updateCount()
        return

    def row(self) -> int:
        return self._row

    def childCount(self) -> int:
        return len(self._children)

    def data(self, column: int, role: Qt.ItemDataRole) -> str | QIcon | Qt.AlignmentFlag | None:
        """"""
        return self._cache.get(COL_MASK*column | role)

    def parent(self) -> ProjectNode | None:
        return self._parent

    def child(self, row: int) -> ProjectNode | None:
        if 0 <= row < len(self._children):
            return self._children[row]
        return None

    def addChild(self, child: ProjectNode) -> None:
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)
        self.refresh()
        return


class ProjectModel(QAbstractItemModel):

    def __init__(self, tree: NWTree) -> None:
        super().__init__(None)
        self._root = ProjectNode(NWItem(tree._project, ""))
        return

    def setRoot(self, root: ProjectNode) -> None:
        self._root = root
        return

    def rowCount(self, index: QModelIndex) -> int:
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def columnCount(self, index: QModelIndex) -> int:
        return 4

    def parent(self, index: QModelIndex) -> QModelIndex:
        if index.isValid():
            if parent := index.internalPointer().parent():
                return self.createIndex(parent.row(), 0, parent)
        return QModelIndex()

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent and parent.isValid():
            item = parent.internalPointer()
        else:
            item = self._root

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if child := item.child(row):
            return self.createIndex(row, column, child)

        return QModelIndex()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        if not index.isValid():
            return None
        node = index.internalPointer()
        return node.data(index.column(), role)

    def addChild(self, node: ProjectNode, parent: QModelIndex) -> None:
        if parent and parent.isValid():
            item = parent.internalPointer()
        else:
            item = self._root
        item.addChild(node)
        return
