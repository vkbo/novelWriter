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
from typing import TYPE_CHECKING, Literal, overload

from novelwriter.common import isHandle
from novelwriter.constants import nwFiles
from novelwriter.core.item import NWItem
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

    __slots__ = ("_project", "_tree", "_order", "_roots", "_trash", "_changed")

    def __init__(self, project: NWProject) -> None:

        self._project = project

        self._tree: dict[str, NWItem] = {}   # Holds all the items of the project
        self._order: list[str] = []          # The order of the tree items in the tree view
        self._roots: dict[str, NWItem] = {}  # The root items of the tree

        self._trash = None     # The handle of the trash root folder
        self._changed = False  # True if tree structure has changed

        return

    ##
    #  Properties
    ##

    @property
    def trashRoot(self) -> str | None:
        """Return the handle of the trash folder, or None."""
        return self._trash

    ##
    #  Class Methods
    ##

    def clear(self) -> None:
        """Clear the item tree entirely."""
        self._tree    = {}
        self._order   = []
        self._roots   = {}
        self._trash   = None
        self._changed = False
        return

    def handles(self) -> list[str]:
        """Returns a copy of the list of all the active handles."""
        return self._order.copy()

    @overload  # pragma: no cover
    def create(self, label: str, parent: None, itemType: Literal[nwItemType.ROOT],
               itemClass: nwItemClass) -> str:
        pass

    @overload  # pragma: no cover
    def create(self, label: str, parent: str | None, itemType: nwItemType,
               itemClass: nwItemClass = nwItemClass.NO_CLASS) -> str | None:
        pass

    def create(self, label, parent, itemType, itemClass=nwItemClass.NO_CLASS):
        """Create a new item in the project tree, and return its handle.
        If the item cannot be added to the project because of an invalid
        parent, None is returned. For root elements, this cannot occur.
        """
        parent = None if itemType == nwItemType.ROOT else parent
        if parent is None or parent in self._order:
            tHandle = self._makeHandle()
            newItem = NWItem(self._project, tHandle)
            newItem.setName(label)
            newItem.setParent(parent)
            newItem.setType(itemType)
            newItem.setClass(itemClass)
            self.append(newItem)
            self.updateItemData(tHandle)
            return tHandle
        return None

    def append(self, nwItem: NWItem) -> bool:
        """Add a new item to the end of the tree."""
        tHandle = nwItem.itemHandle
        pHandle = nwItem.itemParent

        if not isHandle(tHandle):
            logger.warning("Invalid item handle '%s' detected, skipping", tHandle)
            return False

        if tHandle in self._tree:
            logger.warning("Duplicate handle '%s' detected, skipping", tHandle)
            return False

        logger.debug("Adding item '%s' with parent '%s'", str(tHandle), str(pHandle))

        if nwItem.isRootType():
            logger.debug("Item '%s' is a root item", str(tHandle))
            self._roots[tHandle] = nwItem
            if nwItem.itemClass == nwItemClass.TRASH:
                if self._trash is None:
                    logger.debug("Item '%s' is the trash folder", str(tHandle))
                    self._trash = tHandle
                else:
                    logger.error("Only one trash folder allowed")
                    return False

        self._tree[tHandle] = nwItem
        self._order.append(tHandle)
        self._setTreeChanged(True)

        return True

    def duplicate(self, sHandle: str) -> NWItem | None:
        """Duplicate an item and set a new handle."""
        sItem = self.__getitem__(sHandle)
        if isinstance(sItem, NWItem):
            nItem = NWItem.duplicate(sItem, self._makeHandle())
            if self.append(nItem):
                logger.info("Duplicated item '%s' -> '%s'", sHandle, nItem.itemHandle)
                return nItem
        return None

    def pack(self) -> list[dict]:
        """Pack the content of the tree into a list of dictionaries of
        items. In the order defined by the _treeOrder list.
        """
        tree = []
        for tHandle in self._order:
            tItem = self.__getitem__(tHandle)
            if tItem:
                tree.append(tItem.pack())
        return tree

    def unpack(self, data: list[dict]) -> None:
        """Iterate through all items of a list and add them to the
        project tree.
        """
        self.clear()
        for item in data:
            nwItem = NWItem(self._project, "")  # Handle is set by unpack()
            if nwItem.unpack(item):
                self.append(nwItem)
                nwItem.saveInitialCount()
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
        for tHandle in self._order:
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
            oParent = oParent if oParent in self._order else None
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
            if self.append(newItem):
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

        tocList = []
        tocLen = 0
        for tHandle in self._order:
            tItem = self.__getitem__(tHandle)
            if tItem is None:
                continue

            tFile = tHandle+".nwd"
            if (contentPath / tFile).is_file():
                tocLine = "{0:<25s}  {1:<9s}  {2:<8s}  {3:s}".format(
                    str(Path("content") / tFile),
                    tItem.itemClass.name,
                    tItem.itemLayout.name,
                    tItem.itemName,
                )
                tocList.append(tocLine)
                tocLen = max(tocLen, len(tocLine))

        try:
            # Dump the text
            tocText = runtimePath / nwFiles.TOC_TXT
            with open(tocText, mode="w", encoding="utf-8") as outFile:
                outFile.write("\n")
                outFile.write("Table of Contents\n")
                outFile.write("=================\n")
                outFile.write("\n")
                outFile.write("{0:<25s}  {1:<9s}  {2:<8s}  {3:s}\n".format(
                    "File Name", "Class", "Layout", "Document Label"
                ))
                outFile.write("-"*max(tocLen, 62) + "\n")
                outFile.write("\n".join(tocList))
                outFile.write("\n")

        except Exception:
            logger.error("Could not write ToC file")
            logException()
            return False

        return True

    def sumWords(self) -> tuple[int, int]:
        """Loop over all entries and add up the word counts."""
        noteWords = 0
        novelWords = 0
        for tHandle in self._order:
            tItem = self.__getitem__(tHandle)
            if tItem is None:
                continue
            if tItem.itemLayout == nwItemLayout.NO_LAYOUT:
                pass
            elif tItem.itemLayout == nwItemLayout.NOTE:
                noteWords += tItem.wordCount
            else:
                novelWords += tItem.wordCount
        return novelWords, noteWords

    ##
    #  Tree Item Methods
    ##

    def updateItemData(self, tHandle: str) -> bool:
        """Update the root item handle of a given item. Returns True if
        a root was found and data updated, otherwise False.
        """
        tItem = self.__getitem__(tHandle)
        if tItem is None:
            return False

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
        for nwItem in self._roots.values():
            rootClasses.add(nwItem.itemClass)
        return rootClasses

    def iterRoots(self, itemClass: nwItemClass | None) -> Iterable[tuple[str, NWItem]]:
        """Iterate over all root items of a given class in order."""
        for tHandle in self._order:
            nwItem = self.__getitem__(tHandle)
            if isinstance(nwItem, NWItem) and nwItem.isRootType():
                if itemClass is None or nwItem.itemClass == itemClass:
                    yield tHandle, nwItem
        return

    def isTrash(self, tHandle: str) -> bool:
        """Check if an item is in or is the trash folder."""
        tItem = self.__getitem__(tHandle)
        if tItem is None:
            return True
        if tItem.itemClass == nwItemClass.TRASH:
            return True
        if self._trash is not None:
            if tHandle == self._trash:
                return True
            elif tItem.itemParent == self._trash:
                return True
            elif tItem.itemRoot == self._trash:
                return True
        return False

    def findRoot(self, itemClass: nwItemClass | None) -> str | None:
        """Find the first root item for a given class."""
        for aRoot in self._roots:
            tItem = self.__getitem__(aRoot)
            if tItem is None:
                continue
            if itemClass == tItem.itemClass:
                return tItem.itemHandle
        return None

    ##
    #  Setters
    ##

    def setOrder(self, newOrder: list[str]) -> None:
        """Reorders the tree based on a list of items."""
        tmpOrder = [tHandle for tHandle in newOrder if tHandle in self._tree]
        if not (len(tmpOrder) == len(newOrder) == len(self._order)):
            # Something is wrong, so let's debug it
            for tHandle in newOrder:
                if tHandle not in self._tree:
                    logger.error("Handle '%s' in new tree order is not in old order", tHandle)
            for tHandle in self._order:
                if tHandle not in tmpOrder:
                    logger.warning("Handle '%s' in old tree order is not in new order", tHandle)

        # Save the temp list
        self._order = tmpOrder
        self._setTreeChanged(True)
        logger.debug("Project tree order updated")

        return

    ##
    #  Special Methods
    ##

    def __len__(self) -> int:
        """The number of items in the project."""
        return len(self._order)

    def __bool__(self) -> bool:
        """True if there are any items in the project."""
        return bool(self._order)

    def __getitem__(self, tHandle: str | None) -> NWItem | None:
        """Return a project item based on its handle. Returns None if
        the handle doesn't exist in the project.
        """
        if tHandle and tHandle in self._tree:
            return self._tree[tHandle]
        logger.error("No tree item with handle '%s'", str(tHandle))
        return None

    def __delitem__(self, tHandle: str) -> None:
        """Remove an item from the internal lists and dictionaries."""
        if tHandle in self._order and tHandle in self._tree:
            self._order.remove(tHandle)
            del self._tree[tHandle]
        else:
            logger.warning("Failed to delete item '%s': item not found", tHandle)
            return

        if tHandle in self._roots:
            del self._roots[tHandle]
        if tHandle == self._trash:
            self._trash = None

        self._setTreeChanged(True)

        return

    def __contains__(self, tHandle: str) -> bool:
        """Checks if a handle exists in the tree."""
        return tHandle in self._order

    def __iter__(self) -> Iterator[NWItem]:
        """Iterate through project items."""
        for tHandle in self._order:
            tItem = self._tree.get(tHandle)
            if isinstance(tItem, NWItem):
                yield tItem
        return

    ##
    #  Internal Functions
    ##

    def _setTreeChanged(self, state: bool) -> None:
        """Set the changed flag to state, and if being set to True,
        propagate that state change to the parent NWProject class.
        """
        self._changed = state
        if state:
            self._project.setProjectChanged(True)
        return

    def _makeHandle(self) -> str:
        """Generate a unique item handle. In the event that the key
        already exists, generate a new one.
        """
        logger.debug("Generating new handle")
        handle = f"{random.getrandbits(52):013x}"
        if handle in self._tree:
            logger.warning("Duplicate handle encountered! Retrying ...")
            handle = self._makeHandle()

        return handle
