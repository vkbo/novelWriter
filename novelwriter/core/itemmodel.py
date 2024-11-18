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

from typing import TYPE_CHECKING

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

T_NodeData = str | QIcon | Qt.AlignmentFlag | None


class ProjectNode:

    __slots__ = ("_item", "_children", "_parent", "_row", "_cache", "_count")

    def __init__(self, item: NWItem) -> None:
        self._item = item
        self._children: list[ProjectNode] = []
        self._parent: ProjectNode | None = None
        self._row = 0
        self._cache: dict[int, str | QIcon | Qt.AlignmentFlag] = {}
        self.refresh()
        return

    def __repr__(self) -> str:
        return (
            f"<ProjectNode handle={self._item.itemHandle} "
            f"parent={self._parent.item.itemHandle if self._parent else None} "
            f"row={self._row} "
            f"children={len(self._children)}>"
        )

    ##
    #  Properties
    ##

    @property
    def item(self) -> NWItem:
        return self._item

    @property
    def children(self) -> list[ProjectNode]:
        return self._children

    ##
    #  Data Maintenance
    ##

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

    ##
    #  Data Access
    ##

    def row(self) -> int:
        return self._row

    def childCount(self) -> int:
        return len(self._children)

    def data(self, column: int, role: Qt.ItemDataRole) -> T_NodeData:
        """"""
        return self._cache.get(COL_MASK*column | role)

    def parent(self) -> ProjectNode | None:
        return self._parent

    def child(self, row: int) -> ProjectNode | None:
        if 0 <= row < len(self._children):
            return self._children[row]
        return None

    def allChildren(self) -> list[ProjectNode]:
        nodes: list[ProjectNode] = []
        self._recursiveAppendChildren(nodes)
        return nodes

    ##
    #  Data Edit
    ##

    def addChild(self, child: ProjectNode) -> None:
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)
        self.refresh()
        return

    def moveChild(self, source: int, step: int) -> int:
        """Move a child internally."""
        count = len(self._children)
        if 0 <= source < count:
            target = max(min(source + step, count - 1), 0)
            if source != target:
                node = self._children.pop(source)
                self._children.insert(target, node)
                for n, child in enumerate(self._children):
                    child._row = n
                return target + 1 if target > source else target
        return -1

    ##
    #  Internal Functions
    ##

    def _recursiveAppendChildren(self, children: list[ProjectNode]) -> None:
        for node in self._children:
            children.append(node)
            node._recursiveAppendChildren(children)
        return


class ProjectModel(QAbstractItemModel):

    __slots__ = ("_tree", "_root")

    def __init__(self, tree: NWTree) -> None:
        super().__init__()
        self._tree = tree
        self._root = ProjectNode(NWItem(tree._project, "invisibleRoot"))
        logger.debug("Ready: ProjectModel")
        return

    def __del__(self) -> None:
        logger.debug("Delete: ProjectModel")
        return

    @property
    def root(self) -> ProjectNode:
        """Return the model root item."""
        return self._root

    ##
    #  Model Interface
    ##

    def rowCount(self, index: QModelIndex) -> int:
        """Return the number of rows for an entry."""
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def columnCount(self, index: QModelIndex) -> int:
        """Return the number of columns for an entry."""
        return 4

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Get the parent model index of another index."""
        if index.isValid():
            if parent := index.internalPointer().parent():
                return self.createIndex(parent.row(), 0, parent)
        return QModelIndex()

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """get the index of a child item of a parent."""
        if parent.isValid():
            item: ProjectNode = parent.internalPointer()
        else:
            item = self._root

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if child := item.child(row):
            return self.createIndex(row, column, child)

        return QModelIndex()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> T_NodeData:
        """Return display data for a project node."""
        if not index.isValid():
            return None
        node: ProjectNode = index.internalPointer()
        return node.data(index.column(), role)

    # def addChild(self, node: ProjectNode, parent: QModelIndex) -> None:
    #     if parent.isValid():
    #         item = parent.internalPointer()
    #     else:
    #         item = self._root
    #     item.addChild(node)
    #     return

    ##
    #  Data Access
    ##

    def node(self, index: QModelIndex) -> ProjectNode | None:
        """Return the node for a given model index."""
        if index.isValid():
            return index.internalPointer()
        return None

    def indexFromHandle(self, handle: str | None) -> QModelIndex:
        """Get the index representing a node in the model."""
        if handle and (node := self._tree.nodes.get(handle)):
            return self.createIndex(node.row(), 0, node)
        return QModelIndex()

    def indexFromNode(self, node: ProjectNode) -> QModelIndex:
        """Get the index representing a node in the model."""
        return self.createIndex(node.row(), 0, node)

    ##
    #  Model Edit
    ##

    def internalMove(self, index: QModelIndex, step: int) -> None:
        """Move an item internally among its siblings."""
        if index.isValid():
            node: ProjectNode = index.internalPointer()
            if parent := node.parent():
                pos = index.row()
                if (new := parent.moveChild(index.row(), step)) > -1:
                    self.beginMoveRows(index.parent(), pos, pos, index.parent(), new)
                    self.endMoveRows()
        return

    def moveRows(self, indices: list[QModelIndex], destination: QModelIndex, row: int) -> bool:
        """Move indices to destination."""
        return False

    ##
    #  Other Methods
    ##

    def allExpanded(self) -> list[QModelIndex]:
        """Return a list of all expanded items."""
        expanded = []
        for node in self._root.allChildren():
            if node._item.isExpanded:
                expanded.append(self.createIndex(node.row(), 0, node))
        return expanded
