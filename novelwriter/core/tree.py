"""
novelWriter – Project Tree Class
================================

File History:
Created: 2020-05-07 [0.4.5] NWTree

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
import random

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt5.QtCore import QModelIndex

from novelwriter import SHARED
from novelwriter.constants import nwFiles, nwLabels, trConst
from novelwriter.core.item import NWItem
from novelwriter.core.itemmodel import ProjectModel, ProjectNode
from novelwriter.enum import nwItemClass, nwItemLayout, nwItemType
from novelwriter.error import logException

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)

MAX_DEPTH = 1000  # Cap of tree traversing for loops (recursion limit)


class NWTree:
    """Core: Project Tree Data Class

    Only one instance of this class should exist in the project class.
    This class holds all the project items of the project as instances
    of NWItem.

    For historical reasons, the order of the items is saved in a
    separate list from the items themselves, which are stored in a
    dictionary. This is somewhat redundant with the newer versions of
    Python, but is still practical as it's easier to update the item
    order as a list.

    Each item has a handle, which is a random hex string of length 13.
    The handle is the name of the item everywhere in novelWriter, and is
    also used for file names.
    """

    __slots__ = (
        "_project", "_tree", "_order", "_roots",
        "_model", "_items", "_nodes", "_trash", "_changed",
    )

    def __init__(self, project: NWProject) -> None:
        self._project = project
        self._model = ProjectModel(self)
        self._items: dict[str, NWItem] = {}
        self._nodes: dict[str, ProjectNode] = {}
        self._trash = None
        logger.debug("Ready: NWTree")
        return

    def __del__(self) -> None:
        logger.debug("Delete: NWTree")
        return

    ##
    #  Properties
    ##

    # @property
    # def trashRoot(self) -> str | None:
    #     """Return the handle of the trash folder, or None."""
    #     return self._trash

    @property
    def model(self) -> ProjectModel:
        return self._model

    @property
    def nodes(self) -> dict[str, ProjectNode]:
        return self._nodes

    ##
    #  Class Methods
    ##

    def clear(self) -> None:
        """Clear the item tree entirely."""
        oldModel = self._model
        self._model = ProjectModel(self)
        self._items = {}
        self._nodes = {}
        self._trash = None
        oldModel.deleteLater()
        del oldModel
        return

    def handles(self) -> list[str]:
        """Returns a copy of the list of all the active handles."""
        return list(self._items.keys())

    def add(self, item: NWItem, pos: int = -1) -> bool:
        """Add a project item into the project tree."""
        if pHandle := item.itemParent:
            if parent := self._nodes.get(pHandle):
                node = ProjectNode(item)
                index = self._model.indexFromNode(parent)
                self._model.insertChild(node, index, pos)
                self._nodes[item.itemHandle] = node
                self._items[item.itemHandle] = item
            else:
                logger.error("Could not locate parent of '%s'", item.itemHandle)
                return False
        elif item.isRootType():
            node = ProjectNode(item)
            self._model.insertChild(node, QModelIndex(), pos)
            self._nodes[item.itemHandle] = node
            self._items[item.itemHandle] = item
        else:
            logger.error("Invalid project item '%s'", item.itemHandle)
            return False
        return True

    def create(
        self, label: str, parent: str | None, itemType: nwItemType,
        itemClass: nwItemClass = nwItemClass.NO_CLASS, pos: int = -1,
    ) -> str | None:
        """Create a new item in the project tree, and return its handle.
        If the item cannot be added to the project because of an invalid
        parent, None is returned. For root elements, this cannot occur.
        """
        parent = None if itemType == nwItemType.ROOT else parent
        if parent is None or parent in self._nodes:
            tHandle = self._makeHandle()
            nwItem = NWItem(self._project, tHandle)
            nwItem.setName(label)
            nwItem.setParent(parent)
            nwItem.setType(itemType)
            nwItem.setClass(itemClass)
            if self.add(nwItem, pos):
                self.updateItemData(tHandle)
                self._project.setProjectChanged(True)
                return tHandle
        return None

    def duplicate(self, sHandle: str) -> NWItem | None:
        """Duplicate an item and set a new handle."""
        # sItem = self.__getitem__(sHandle)
        # if isinstance(sItem, NWItem):
        #     nItem = NWItem.duplicate(sItem, self._makeHandle())
        #     if self.append(nItem):
        #         logger.info("Duplicated item '%s' -> '%s'", sHandle, nItem.itemHandle)
        #         return nItem
        return None

    def pack(self) -> list[dict]:
        """Pack the content of the tree into a list of dictionaries of
        items. In the order defined by the _treeOrder list.
        """
        nodes = self._model.root.allChildren()
        if len(nodes) != len(self._nodes):
            logger.warning(
                "Model tree is inconsitent with nodes map, %d != %d",
                len(nodes), len(self._nodes)
            )
        return [node.item.pack() for node in nodes]

    def unpack(self, data: list[dict]) -> None:
        """Iterate through all items of a list and add them to the
        project tree.
        """
        self.clear()
        items: dict[str, NWItem] = self._items.copy()
        for item in data:
            nwItem = NWItem(self._project, "")
            if nwItem.unpack(item):
                items[nwItem.itemHandle] = nwItem

        later = items
        self._model.beginInsertRows(self._model.index(0, 0), 0, 0)
        for _ in range(999):
            later = self._addItems(later)
            if len(later) == 0:
                break
        else:
            logger.error("Not all items could be added to project tree")

        self._trash = self._getTrashNode()
        self._model.endInsertRows()
        self._model.layoutChanged.emit()

        return

    def refreshItems(self, items: list[str], isRange: bool = False) -> None:
        """Refresh these items on the GUI. If they are an ordered range,
        also set the isRange flag to True.
        """
        indices = []
        for tHandle in items:
            if node := self._nodes.get(tHandle):
                node.refresh()
                SHARED.projectSignalProxy({"event": "projectItem", "handle": tHandle})
                indices.append(self._model.indexFromNode(node))
        if isRange and len(indices) >= 2:
            self._model.dataChanged.emit(indices[0], indices[-1])
        else:
            for index in indices:
                self._model.dataChanged.emit(index, index)
        self._project.setProjectChanged(len(indices) > 0)
        return

    def checkConsistency(self, prefix: str) -> tuple[int, int]:
        """Check the project tree consistency. Also check the content
        folder and add back files that were discovered but were not
        included in the tree. This function should only be called after
        the project file has been processed, but before the loading of
        the project returns. The functions requires a prefix string to
        mark recovered files.
        """
        storage = self._project.storage
        files = set(storage.scanContent())
        for tHandle in self._nodes:
            if self.updateItemData(tHandle):
                logger.debug("Checking item '%s' ... OK", tHandle)
                files.discard(tHandle)  # Remove it from the record
            else:
                logger.error("Checking item '%s' ... ERROR", tHandle)
                self.__delitem__(tHandle)  # The file will be re-added as orphaned

        orphans = len(files)
        if orphans == 0:
            logger.info("Checked project files: OK")
            return 0, 0

        logger.warning("Found %d file(s) not tracked in project", orphans)
        recovered = 0
        for cHandle in files:
            aDoc = storage.getDocument(cHandle)
            aDoc.readDocument(isOrphan=True)
            oName, oParent, oClass, oLayout = aDoc.getMeta()

            oName = oName or cHandle
            oParent = oParent if oParent in self._nodes else None
            oClass = oClass or nwItemClass.NOVEL
            oLayout = oLayout or nwItemLayout.NOTE

            # If the parent doesn't exists, find a new home
            if oParent is None:  # Add it to the first available class root
                oParent = self.findRoot(oClass)
            if oParent is None:  # Otherwise, add to the Novel root
                oParent = self.findRoot(nwItemClass.NOVEL)
            if oParent is None:  # If not, create a new novel folder
                oParent = self.create(prefix, None, nwItemType.ROOT, nwItemClass.NOVEL)

            assert oParent is not None  # Otherwise there's an issue with self.create()

            # Create a new item
            newItem = NWItem(self._project, cHandle)
            newItem.setName(f"[{prefix}] {oName}")
            newItem.setParent(oParent)
            newItem.setType(nwItemType.FILE)
            newItem.setClass(oClass)
            newItem.setLayout(oLayout)
            if self.add(newItem):
                self.updateItemData(cHandle)
                recovered += 1

        return orphans, recovered

    def writeToCFile(self) -> bool:
        """Write the convenience table of contents file in the root of
        the project directory.
        """
        runtimePath = self._project.storage.runtimePath
        contentPath = self._project.storage.contentPath
        if not (isinstance(contentPath, Path) and isinstance(runtimePath, Path)):
            return False

        entries = []
        maxLen = 0
        for node in self._model.root.allChildren():
            item = node.item
            file = f"{item.itemHandle}.nwd"
            if (contentPath / file).is_file():
                tocLine = "{0:<25s}  {1:<9s}  {2:<8s}  {3:s}".format(
                    str(Path("content") / file),
                    item.itemClass.name,
                    item.itemLayout.name,
                    item.itemName,
                )
                entries.append(tocLine)
                maxLen = max(maxLen, len(tocLine))

        try:
            with open(runtimePath / nwFiles.TOC_TXT, mode="w", encoding="utf-8") as toc:
                toc.write("\n")
                toc.write("Table of Contents\n")
                toc.write("=================\n")
                toc.write("\n")
                toc.write("{0:<25s}  {1:<9s}  {2:<8s}  {3:s}\n".format(
                    "File Name", "Class", "Layout", "Document Label"
                ))
                toc.write("-"*max(maxLen, 62) + "\n")
                toc.write("\n".join(entries))
                toc.write("\n")

        except Exception:
            logger.error("Could not write ToC file")
            logException()
            return False

        return True

    def sumWords(self) -> tuple[int, int]:
        """Loop over all entries and add up the word counts."""
        noteWords = 0
        novelWords = 0
        for item in self._items.values():
            if item.itemLayout == nwItemLayout.NOTE:
                noteWords += item.wordCount
            elif item.itemLayout == nwItemLayout.DOCUMENT:
                novelWords += item.wordCount
        return novelWords, noteWords

    ##
    #  Tree Item Methods
    ##

    def updateItemData(self, tHandle: str) -> bool:
        """Update the root item handle of a given item. Returns True if
        a root was found and data updated, otherwise False.
        """
        if tItem := self._items.get(tHandle):
            iItem = tItem
            for _ in range(MAX_DEPTH):
                if iItem.itemParent is None:
                    tItem.setRoot(iItem.itemHandle)
                    tItem.setClassDefaults(iItem.itemClass)
                    return True
                else:
                    iItem = self.__getitem__(iItem.itemParent)
                    if iItem is None:
                        return False
            else:
                raise RecursionError("Critical internal error")
        return False

    def checkType(self, tHandle: str, itemType: nwItemType) -> bool:
        """Check if item exists and is of the specified item type."""
        tItem = self.__getitem__(tHandle)
        if not tItem:
            return False
        return tItem.itemType == itemType

    def getItemPath(self, tHandle: str, asName: bool = False) -> list[str]:
        """Iterate upwards in the tree until we find the item with
        parent None, the root item, and return the list of handles, or
        alternatively item names. We do this with a for loop with a
        maximum depth to make infinite loops impossible.
        """
        tTree = []
        tItem = self.__getitem__(tHandle)
        if tItem is not None:
            tTree.append(tItem.itemName if asName else tHandle)
            for _ in range(MAX_DEPTH):
                if tItem.itemParent is None:
                    return tTree
                else:
                    tHandle = tItem.itemParent
                    tItem = self.__getitem__(tHandle)
                    if tItem is None:
                        return tTree
                    else:
                        tTree.append(tItem.itemName if asName else tHandle)
            else:
                raise RecursionError("Critical internal error")

        return tTree

    ##
    #  Tree Root Methods
    ##

    def rootClasses(self) -> set[nwItemClass]:
        """Return a set of all root classes in use by the project."""
        rootClasses = set()
        for node in self._model.root.children:
            rootClasses.add(node.item.itemClass)
        return rootClasses

    def iterRoots(self, itemClass: nwItemClass | None) -> Iterable[tuple[str, NWItem]]:
        """Iterate over all root items of a given class in order."""
        for node in self._model.root.children:
            if node.item.isRootType():
                if itemClass is None or node.item.itemClass == itemClass:
                    yield node.item.itemHandle, node.item
        return

    def isTrash(self, tHandle: str) -> bool:
        """Check if an item is in or is the trash folder."""
        # tItem = self.__getitem__(tHandle)
        # if tItem is None:
        #     return True
        # if tItem.itemClass == nwItemClass.TRASH:
        #     return True
        # if self._trash is not None:
        #     if tHandle == self._trash:
        #         return True
        #     elif tItem.itemParent == self._trash:
        #         return True
        #     elif tItem.itemRoot == self._trash:
        #         return True
        return False

    def findRoot(self, itemClass: nwItemClass | None) -> str | None:
        """Find the first root item for a given class."""
        for node in self._model.root.children:
            if node.item.itemClass == itemClass:
                return node.item.itemHandle
        return None

    ##
    #  Special Methods
    ##

    def __len__(self) -> int:
        """The number of items in the project."""
        return len(self._items)

    def __bool__(self) -> bool:
        """True if there are any items in the project."""
        return bool(self._items)

    def __getitem__(self, tHandle: str | None) -> NWItem | None:
        """Return a project item based on its handle. Returns None if
        the handle doesn't exist in the project.
        """
        if tHandle and tHandle in self._items:
            return self._items[tHandle]
        logger.error("No tree item with handle '%s'", str(tHandle))
        return None

    def __delitem__(self, tHandle: str) -> None:
        """Remove an item from the internal lists and dictionaries."""
        # if tHandle in self._order and tHandle in self._tree:
        #     self._order.remove(tHandle)
        #     del self._tree[tHandle]
        # else:
        #     logger.warning("Failed to delete item '%s': item not found", tHandle)
        #     return

        # if tHandle in self._roots:
        #     del self._roots[tHandle]
        # if tHandle == self._trash:
        #     self._trash = None

        return

    def __contains__(self, tHandle: str) -> bool:
        """Checks if a handle exists in the tree."""
        return tHandle in self._items

    def __iter__(self) -> Iterator[NWItem]:
        """Iterate through project items."""
        for node in self._model.root.allChildren():
            yield node.item
        return

    ##
    #  Internal Functions
    ##

    def _getTrashNode(self) -> ProjectNode | None:
        """Get the trash node. If it doesn't exist, create it."""
        for node in self._model.root.children:
            if node.item.itemClass == nwItemClass.TRASH:
                return node
        label = trConst(nwLabels.CLASS_NAME[nwItemClass.TRASH])
        if handle := self.create(label, None, nwItemType.ROOT, nwItemClass.TRASH):
            return self._nodes.get(handle)
        return None

    def _addItems(self, items: dict[str, NWItem]) -> dict[str, NWItem]:
        """Add a dictionary of items to the project tree. Returns a new
        dictionary of items that could not be added yet, but can be.
        """
        remains: dict[str, NWItem] = {}
        for handle, item in items.items():
            if pHandle := item.itemParent:
                if parent := self._nodes.get(pHandle):
                    node = ProjectNode(item)
                    parent.addChild(node)
                    self._items[handle] = item
                    self._nodes[handle] = node
                elif pHandle in items:
                    remains[handle] = item
                    logger.warning("Item '%s' found before its parent", handle)
                else:
                    logger.error("Item '%s' has no parent in current tree", handle)
            elif item.isRootType():
                node = ProjectNode(item)
                self._model.root.addChild(node)
                self._items[handle] = item
                self._nodes[handle] = node
        return remains

    def _makeHandle(self) -> str:
        """Generate a unique item handle. In the event that the key
        already exists, generate a new one.
        """
        logger.debug("Generating new handle")
        handle = f"{random.getrandbits(52):013x}"
        if handle in self._items:
            logger.warning("Duplicate handle encountered! Retrying ...")
            handle = self._makeHandle()

        return handle
