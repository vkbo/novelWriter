"""
novelWriter – Project Item Model
================================

File History:
Created: 2024-11-16 [2.6b2] ProjectNode
Created: 2024-11-16 [2.6b2] ProjectModel

This file is a part of novelWriter
Copyright (C) 2024 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt6.QtCore import QAbstractItemModel, QMimeData, QModelIndex, Qt
from PyQt6.QtGui import QFont, QIcon

from novelwriter.common import decodeMimeHandles, encodeMimeHandles, minmax
from novelwriter.constants import nwConst
from novelwriter.core.item import NWItem
from novelwriter.enum import nwItemClass
from novelwriter.types import QtAlignRight

if TYPE_CHECKING:
    from novelwriter.core.tree import NWTree

logger = logging.getLogger(__name__)

INV_ROOT = "invisibleRoot"
C_FACTOR = 0x0100

C_LABEL_TEXT    = 0x0000 | Qt.ItemDataRole.DisplayRole
C_LABEL_ICON    = 0x0000 | Qt.ItemDataRole.DecorationRole
C_LABEL_FONT    = 0x0000 | Qt.ItemDataRole.FontRole
C_COUNT_TEXT    = 0x0100 | Qt.ItemDataRole.DisplayRole
C_COUNT_ICON    = 0x0100 | Qt.ItemDataRole.DecorationRole
C_COUNT_ALIGN   = 0x0100 | Qt.ItemDataRole.TextAlignmentRole
C_ACTIVE_ICON   = 0x0200 | Qt.ItemDataRole.DecorationRole
C_ACTIVE_TIP    = 0x0200 | Qt.ItemDataRole.ToolTipRole
C_ACTIVE_ACCESS = 0x0200 | Qt.ItemDataRole.AccessibleTextRole
C_STATUS_ICON   = 0x0300 | Qt.ItemDataRole.DecorationRole
C_STATUS_TIP    = 0x0300 | Qt.ItemDataRole.ToolTipRole
C_STATUS_ACCESS = 0x0300 | Qt.ItemDataRole.AccessibleTextRole

NODE_FLAGS = Qt.ItemFlag.ItemIsEnabled
NODE_FLAGS |= Qt.ItemFlag.ItemIsSelectable
NODE_FLAGS |= Qt.ItemFlag.ItemIsDropEnabled

T_NodeData = str | QIcon | QFont | Qt.AlignmentFlag | None


class ProjectNode:
    """Core: Project Model Node Class

    The project tree structure is saved as nodes in a tree, starting
    from a root node. This class makes up these nodes.

    Each node is a wrapper around an NWItem object. The NWItem is the
    object representing a single item in the project, and it only
    contains a reference to its parent as well as it top level root, but
    is itself not structured in a hierarchy in memory.

    This class provides the necessary hierarchical structure, as well as
    the data entries needed for populating the GUI project tree. It also
    handles pushing and pulling information from its NWItem when
    necessary.

    The data to be displayed could in principle be pulled from the
    NWItem whenever it is needed, but for performance reason it is
    cached, as the GUI will pull this information often.
    """

    C_NAME   = 0
    C_COUNT  = 1
    C_ACTIVE = 2
    C_STATUS = 3

    __slots__ = ("_cache", "_children", "_count", "_flags", "_item", "_parent", "_row")

    def __init__(self, item: NWItem) -> None:
        self._item = item
        self._children: list[ProjectNode] = []
        self._parent: ProjectNode | None = None
        self._row = 0
        self._cache: dict[int, T_NodeData] = {}
        self._flags = NODE_FLAGS
        self._count = 0
        self.refresh()
        self.updateCount()
        return

    def __repr__(self) -> str:
        return (
            f"<ProjectNode handle={self._item.itemHandle} "
            f"parent={self._parent.item.itemHandle if self._parent else None} "
            f"row={self._row} "
            f"children={len(self._children)}>"
        )

    def __bool__(self) -> bool:
        """A node should always evaluate to True."""
        return True

    ##
    #  Properties
    ##

    @property
    def item(self) -> NWItem:
        """The project item of the node."""
        return self._item

    @property
    def children(self) -> list[ProjectNode]:
        """All children of the node."""
        return self._children

    @property
    def count(self) -> int:
        """The count of the node."""
        return self._count

    ##
    #  Data Maintenance
    ##

    def refresh(self) -> None:
        """Refresh data values."""
        # Label
        self._cache[C_LABEL_ICON] = self._item.getMainIcon()
        self._cache[C_LABEL_TEXT] = self._item.itemName
        self._cache[C_LABEL_FONT] = self._item.getMainFont()

        # Count
        self._cache[C_COUNT_ALIGN] = QtAlignRight

        # Active
        aText, aIcon = self._item.getActiveStatus()
        self._cache[C_ACTIVE_ICON] = aIcon
        self._cache[C_ACTIVE_TIP] = aText
        self._cache[C_ACTIVE_ACCESS] = aText

        # Status
        sText, sIcon = self._item.getImportStatus()
        self._cache[C_STATUS_ICON] = sIcon
        self._cache[C_STATUS_TIP] = sText
        self._cache[C_STATUS_ACCESS] = sText

        return

    def updateCount(self, propagate: bool = True) -> None:
        """Update counts, and propagate upwards in the tree."""
        self._count = self._item.mainCount + sum(c._count for c in self._children)  # noqa: SLF001
        self._cache[C_COUNT_TEXT] = f"{self._count:n}"
        if propagate and (parent := self._parent):
            parent.updateCount()
        return

    ##
    #  Data Access
    ##

    def row(self) -> int:
        """Return the node's row number."""
        return self._row

    def childCount(self) -> int:
        """Return the number of children of the node."""
        return len(self._children)

    def data(self, column: int, role: Qt.ItemDataRole) -> T_NodeData:
        """Return cached node data."""
        return self._cache.get(C_FACTOR*column | role)

    def flags(self) -> Qt.ItemFlag:
        """Return cached node flags."""
        return self._flags

    def parent(self) -> ProjectNode | None:
        """Return the parent of the node."""
        return self._parent

    def child(self, row: int) -> ProjectNode | None:
        """Return a child of the node."""
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
        else:
            child._row = len(self._children)
            self._children.append(child)
        self._refreshChildrenPos()
        self._item.notifyNovelStructureChange()
        return

    def takeChild(self, pos: int) -> ProjectNode | None:
        """Remove a child item and return it."""
        if 0 <= pos < len(self._children):
            node = self._children.pop(pos)
            self._refreshChildrenPos()
            self.updateCount()
            self._item.notifyNovelStructureChange()
            return node
        return None

    def moveChild(self, source: int, target: int) -> None:
        """Move a child internally."""
        count = len(self._children)
        if (source != target) and (0 <= source < count) and (0 <= target <= count):
            node = self._children.pop(source)
            self._children.insert(target, node)
            self._refreshChildrenPos()
            self._item.notifyNovelStructureChange()
        return

    def setExpanded(self, state: bool) -> None:
        """Set the node's expanded state."""
        if state and self._children:
            self._item.setExpanded(True)
        else:
            self._item.setExpanded(False)
        return

    ##
    #  Internal Functions
    ##

    def _recursiveAppendChildren(self, children: list[ProjectNode]) -> None:
        """Recursively add all nodes to a list."""
        for node in self._children:
            children.append(node)
            node._recursiveAppendChildren(children)  # noqa: SLF001
        return

    def _refreshChildrenPos(self) -> None:
        """Update the row value on all children."""
        for n, child in enumerate(self._children):
            child._row = n  # noqa: SLF001
            child.item.setOrder(n)
        return

    def _updateRelationships(self, child: ProjectNode) -> None:
        """Update a child item's relationships."""
        if self._parent:
            child.item.setParent(self._item.itemHandle)
            child.item.setRoot(self._item.itemRoot)
            child.item.setClassDefaults(self._item.itemClass)
            child._flags = NODE_FLAGS | Qt.ItemFlag.ItemIsDragEnabled
        else:
            child.item.setParent(None)
            child.item.setRoot(child.item.itemHandle)
            child.item.setClassDefaults(child.item.itemClass)
        return


class ProjectModel(QAbstractItemModel):
    """Core: Project Model Class

    This class provides the interface for the tree widget used on the
    GUI. It implements the QModelIndex based interface required, adds
    support for drag and drop, and a few other novelWriter-specific
    methods needed primarily by the project tree GUI component.
    """

    __slots__ = ("_root", "_tree")

    def __init__(self, tree: NWTree) -> None:
        super().__init__()
        self._tree = tree
        self._root = ProjectNode(NWItem(tree.project, INV_ROOT))
        self._root.item.setName("Invisible Root")
        logger.debug("Ready: ProjectModel")
        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: ProjectModel")
        return

    ##
    #  Properties
    ##

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
        if index.isValid() and (node := index.internalPointer()) and (parent := node.parent()):
            return self.createIndex(parent.row(), 0, parent)
        return QModelIndex()

    def index(self, row: int, column: int, parent: QModelIndex | None = None) -> QModelIndex:
        """Get the index of a child item of a parent."""
        parent = parent or QModelIndex()
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

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Return flags for a project node."""
        if index.isValid():
            return index.internalPointer().flags()
        return Qt.ItemFlag.NoItemFlags

    ##
    #  Drag and Drop
    ##

    def supportedDropActions(self) -> Qt.DropAction:
        """Return supported drop actions"""
        return Qt.DropAction.MoveAction

    def mimeTypes(self) -> list[str]:
        """Return the supported mime types of the model."""
        return [nwConst.MIME_HANDLE]

    def mimeData(self, indices: list[QModelIndex]) -> QMimeData:
        """Encode mime data about a selection."""
        handles = [
            i.internalPointer().item.itemHandle
            for i in indices if i.isValid() and i.column() == 0
        ]
        mime = QMimeData()
        encodeMimeHandles(mime, handles)
        return mime

    def canDropMimeData(
        self, data: QMimeData, action: Qt.DropAction,
        row: int, column: int, parent: QModelIndex
    ) -> bool:
        """Check if mime data can be dropped on the current location."""
        if parent.isValid() and parent.internalPointer() is not self._root:
            return data.hasFormat(nwConst.MIME_HANDLE) and action == Qt.DropAction.MoveAction
        return False

    def dropMimeData(
        self, data: QMimeData, action: Qt.DropAction,
        row: int, column: int, parent: QModelIndex
    ) -> bool:
        """Process mime data drop."""
        if self.canDropMimeData(data, action, row, column, parent):
            items = [
                index for handle in decodeMimeHandles(data)
                if (index := self.indexFromHandle(handle)).isValid()
            ]
            self.multiMove(items, parent, row)
            return True
        return False

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

    def nodes(self, indices: list[QModelIndex]) -> list[ProjectNode]:
        """Return the nodes for a list of model indices."""
        return [i.internalPointer() for i in indices if i.isValid() and i.column() == 0]

    def indexFromHandle(self, handle: str | None) -> QModelIndex:
        """Get the index representing a node in the model."""
        if handle and (node := self._tree.nodes.get(handle)):
            return self.createIndex(node.row(), 0, node)
        return QModelIndex()

    def indexFromNode(self, node: ProjectNode, column: int = 0) -> QModelIndex:
        """Get the index representing a node in the model."""
        return self.createIndex(node.row(), column, node)

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

    def multiMove(self, indices: list[QModelIndex], target: QModelIndex, pos: int = -1) -> None:
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
            for node in (reversed(pruned) if pos >= 0 else pruned):
                if node.item.itemParent not in handles:
                    index = self.indexFromNode(node)
                    if temp := self.removeChild(index.parent(), index.row()):
                        self.insertChild(temp, target, pos)
                        for child in reversed(node.allChildren()):
                            node._updateRelationships(child)  # noqa: SLF001
                            child.item.notifyToRefresh()
                        node.item.notifyToRefresh()
        return

    ##
    #  Other Methods
    ##

    def clear(self) -> None:
        """Clear the project model."""
        self._root.children.clear()
        return

    def allExpanded(self) -> list[QModelIndex]:
        """Return a list of all expanded items."""
        return [
            self.createIndex(node.row(), 0, node) for node in self._root.allChildren()
            if node.item.isExpanded
        ]

    def trashSelection(self, indices: list[QModelIndex]) -> bool:
        """Check if a selection of indices are all in trash or not."""
        for index in indices:
            if index.isValid():
                node: ProjectNode = index.internalPointer()
                if node.item.itemClass != nwItemClass.TRASH:
                    return False
        return True
