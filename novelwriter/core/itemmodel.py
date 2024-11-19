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
from novelwriter.common import minmax
from novelwriter.core.item import NWItem
from novelwriter.types import QtAlignRight

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.tree import NWTree

logger = logging.getLogger(__name__)

COL_MASK = 0x0100

C_LABEL_TEXT  = 0x0000 | Qt.ItemDataRole.DisplayRole
C_LABEL_ICON  = 0x0000 | Qt.ItemDataRole.DecorationRole
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
        """Refresh data values."""
        # Label
        self._cache[C_LABEL_ICON] = SHARED.theme.getItemIcon(
            self._item.itemType, self._item.itemClass,
            self._item.itemLayout, self._item.mainHeading
        )
        self._cache[C_LABEL_TEXT] = self._item.itemName

        # Count
        self._cache[C_COUNT_ALIGN] = QtAlignRight

        # Active
        if self._item.isFileType():
            if self._item.isActive:
                self._cache[C_ACTIVE_ICON] = SHARED.theme.getIcon("checked")
            else:
                self._cache[C_ACTIVE_ICON] = SHARED.theme.getIcon("unchecked")
        else:
            self._cache[C_ACTIVE_ICON] = SHARED.theme.getIcon("noncheckable")

        # Status
        sText, sIcon = self._item.getImportStatus()
        self._cache[C_STATUS_ICON] = sIcon
        self._cache[C_STATUS_TIP] = sText

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
        """Return cached node data."""
        return self._cache.get(COL_MASK*column | role)

    def parent(self) -> ProjectNode | None:
        return self._parent

    def child(self, row: int) -> ProjectNode | None:
        if 0 <= row < len(self._children):
            return self._children[row]
        return None

    def allChildren(self) -> list[ProjectNode]:
        """Return a recursive list of all children."""
        nodes: list[ProjectNode] = []
        self._recursiveAppendChildren(nodes)
        return nodes

    ##
    #  Data Edit
    ##

    def addChild(self, child: ProjectNode, pos: int = -1) -> None:
        """Add a child item to this item."""
        child._parent = self
        self._updateRelationships(child)
        if 0 <= pos < len(self._children):
            self._children.insert(pos, child)
            self._refreshChildrenPos()
        else:
            child._row = len(self._children)
            self._children.append(child)
        self.updateCount()
        return

    def takeChild(self, pos: int) -> ProjectNode | None:
        """Remove a child item and return it."""
        if 0 <= pos < len(self._children):
            node = self._children.pop(pos)
            self._refreshChildrenPos()
            return node
        return None

    def moveChild(self, source: int, target: int) -> None:
        """Move a child internally."""
        count = len(self._children)
        if (source != target) and (0 <= source < count) and (0 <= target <= count):
            node = self._children.pop(source)
            self._children.insert(target, node)
            self._refreshChildrenPos()
        return

    ##
    #  Internal Functions
    ##

    def _recursiveAppendChildren(self, children: list[ProjectNode]) -> None:
        """Recursively add all nodes to a list."""
        for node in self._children:
            children.append(node)
            node._recursiveAppendChildren(children)
        return

    def _refreshChildrenPos(self) -> None:
        """Update the row value on all children."""
        for n, child in enumerate(self._children):
            child._row = n
        return

    def _updateRelationships(self, child: ProjectNode) -> None:
        """Update a child item's relationships."""
        if self._parent:
            child.item.setParent(self.item.itemHandle)
            child.item.setRoot(self.item.itemRoot)
        else:
            child.item.setParent(None)
            child.item.setRoot(child.item.itemHandle)
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
        if index.isValid() and (parent := index.internalPointer().parent()):
            return self.createIndex(parent.row(), 0, parent)
        return QModelIndex()

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """get the index of a child item of a parent."""
        if self.hasIndex(row, column, parent):
            node: ProjectNode = parent.internalPointer() if parent.isValid() else self._root
            if child := node.child(row):
                return self.createIndex(row, column, child)
        return QModelIndex()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> T_NodeData:
        """Return display data for a project node."""
        if index.isValid():
            return index.internalPointer().data(index.column(), role)
        return None

    ##
    #  Data Access
    ##

    def row(self, index: QModelIndex) -> int:
        """Return the row number of the  index."""
        if index.isValid():
            return index.internalPointer().row()
        return -1

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

    def rootIndex(self) -> QModelIndex:
        """Get the index representing the root."""
        return self.createIndex(0, 0, self._root)

    ##
    #  Model Edit
    ##

    def insertChild(self, child: ProjectNode, parent: QModelIndex, pos: int) -> None:
        """Insert a node into the model at a given position."""
        node: ProjectNode = parent.internalPointer() if parent.isValid() else self._root
        count = node.childCount()
        row = minmax(pos, 0, count) if pos >= 0 else count
        self.beginInsertRows(parent, row, row)
        node.addChild(child, row)
        self.endInsertRows()
        return

    def removeChild(self, parent: QModelIndex, pos: int) -> ProjectNode | None:
        """Remove a node from the model and return it."""
        node: ProjectNode = parent.internalPointer() if parent.isValid() else self._root
        if 0 <= pos < node.childCount():
            self.beginRemoveRows(parent, pos, pos)
            child = node.takeChild(pos)
            self.endRemoveRows()
            return child
        return None

    def internalMove(self, index: QModelIndex, step: int) -> None:
        """Move an item internally among its siblings."""
        if index.isValid():
            node: ProjectNode = index.internalPointer()
            if parent := node.parent():
                pos = index.row()
                new = minmax(pos + step, 0, parent.childCount() - 1)
                if new != pos:
                    end = new if new < pos else new + 1
                    self.beginMoveRows(index.parent(), pos, pos, index.parent(), end)
                    parent.moveChild(pos, new)
                    self.endMoveRows()
        return

    def multiMove(self, indices: list[QModelIndex], target: QModelIndex) -> None:
        """Move multiple items to a new location."""
        if target.isValid():
            # This is a two pass process. First we only select unique
            # non-root items for move, then we do a second pass and only
            # move those items that don't have a parent also scheduled
            # for moving or have already been moved. Child items are
            # moved with the parent.
            pruned = []
            handles = set()
            for index in indices:
                if index.isValid():
                    node: ProjectNode = index.internalPointer()
                    handle = node.item.itemHandle
                    if node.item.isRootType() is False and handle not in handles:
                        pruned.append(node)
                        handles.add(handle)
            for node in pruned:
                if node.item.itemParent not in handles:
                    index = self.indexFromNode(node)
                    if child := self.removeChild(index.parent(), index.row()):
                        self.insertChild(child, target, -1)
        return

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
