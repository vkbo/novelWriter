"""
novelWriter – Project Tree Class
================================
Data class for the project's tree of project items

File History:
Created: 2020-05-07 [0.4.5]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import random
import logging

from pathlib import Path

from novelwriter.enum import nwItemClass, nwItemLayout
from novelwriter.error import logException
from novelwriter.common import checkHandle
from novelwriter.constants import nwFiles
from novelwriter.core.item import NWItem

logger = logging.getLogger(__name__)


class NWTree:

    MAX_DEPTH = 1000  # Cap of tree traversing for loops

    def __init__(self, theProject):

        self.theProject = theProject

        self._projTree    = {}     # Holds all the items of the project
        self._treeOrder   = []     # The order of the tree items on the tree view
        self._treeRoots   = {}     # The root items of the tree
        self._trashRoot   = None   # The handle of the trash root folder
        self._archRoot    = None   # The handle of the archive root folder
        self._treeChanged = False  # True if tree structure has changed

        return

    ##
    #  Class Methods
    ##

    def clear(self):
        """Clear the item tree entirely.
        """
        self._projTree    = {}
        self._treeOrder   = []
        self._treeRoots   = {}
        self._trashRoot   = None
        self._archRoot    = None
        self._treeChanged = False
        return

    def handles(self):
        """Returns a copy of the list of all the active handles.
        """
        return self._treeOrder.copy()

    def append(self, tHandle, pHandle, nwItem):
        """Add a new item to the end of the tree.
        """
        tHandle = checkHandle(tHandle, None, True)
        pHandle = checkHandle(pHandle, None, True)
        if tHandle is None:
            tHandle = self._makeHandle()

        if tHandle in self._projTree:
            logger.warning("Duplicate handle '%s' detected, skipping", tHandle)
            return False

        logger.debug("Adding item '%s' with parent '%s'", str(tHandle), str(pHandle))

        nwItem.setHandle(tHandle)
        nwItem.setParent(pHandle)

        if nwItem.isRootType():
            logger.debug("Item '%s' is a root item", str(tHandle))
            self._treeRoots[tHandle] = nwItem
            if nwItem.itemClass == nwItemClass.ARCHIVE:
                logger.debug("Item '%s' is the archive folder", str(tHandle))
                self._archRoot = tHandle
            elif nwItem.itemClass == nwItemClass.TRASH:
                if self._trashRoot is None:
                    logger.debug("Item '%s' is the trash folder", str(tHandle))
                    self._trashRoot = tHandle
                else:
                    logger.error("Only one trash folder allowed")
                    return False

        self._projTree[tHandle] = nwItem
        self._treeOrder.append(tHandle)
        self._setTreeChanged(True)

        return True

    def pack(self):
        """Pack the content of the tree into the provided XML object. In
        the order defined by the _treeOrder list.
        """
        tree = []
        for tHandle in self._treeOrder:
            tItem = self.__getitem__(tHandle)
            if tItem:
                tree.append(tItem.pack())
        return tree

    def unpack(self, data):
        """Iterate through all items of a list and add them to the
        project tree.
        """
        self.clear()
        for item in data:
            nwItem = NWItem(self.theProject)
            if nwItem.unpack(item):
                self.append(nwItem.itemHandle, nwItem.itemParent, nwItem)
                nwItem.saveInitialCount()

        return True

    def writeToCFile(self):
        """Write the convenience table of contents file in the root of
        the project directory.
        """
        runtimePath = self.theProject.storage.runtimePath
        contentPath = self.theProject.storage.contentPath
        if not (isinstance(contentPath, Path) and isinstance(runtimePath, Path)):
            return False

        tocList = []
        tocLen = 0
        for tHandle in self._treeOrder:
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

    def sumWords(self):
        """Loop over all entries and add up the word counts.
        """
        noteWords = 0
        novelWords = 0
        for tHandle in self._treeOrder:
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

    def updateItemData(self, tHandle):
        """Update the root item handle of a given item. Returns True if
        a root was found and data updated, otherwise False.
        """
        tItem = self.__getitem__(tHandle)
        if tItem is None:
            return False

        iItem = tItem
        for _ in range(self.MAX_DEPTH):
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

    def checkType(self, tHandle, itemType):
        """Return true of item exists and is of the specified item type.
        """
        tItem = self.__getitem__(tHandle)
        if not tItem:
            return False
        return tItem.itemType == itemType

    def getItemPath(self, tHandle):
        """Iterate upwards in the tree until we find the item with
        parent None, the root item, and return the list of handles.
        We do this with a for loop with a maximum depth to make
        infinite loops impossible.
        """
        tTree = []
        tItem = self.__getitem__(tHandle)
        if tItem is not None:
            tTree.append(tHandle)
            for _ in range(self.MAX_DEPTH):
                if tItem.itemParent is None:
                    return tTree
                else:
                    tHandle = tItem.itemParent
                    tItem = self.__getitem__(tHandle)
                    if tItem is None:
                        return tTree
                    else:
                        tTree.append(tHandle)
            else:
                raise RecursionError("Critical internal error")

        return tTree

    ##
    #  Tree Root Methods
    ##

    def rootClasses(self):
        """Return a set of all root classes in use by the project.
        """
        rootClasses = set()
        for nwItem in self._treeRoots.values():
            rootClasses.add(nwItem.itemClass)
        return rootClasses

    def iterRoots(self, itemClass):
        """Iterate over all root items of a given class in order.
        """
        for tHandle in self._treeOrder:
            nwItem = self.__getitem__(tHandle)
            if isinstance(nwItem, NWItem) and nwItem.isRootType():
                if itemClass is None or nwItem.itemClass == itemClass:
                    yield tHandle, nwItem
        return

    def isRoot(self, tHandle):
        """Check if a handle is a root item.
        """
        return tHandle in self._treeRoots

    def isTrash(self, tHandle):
        """Check if an item is in or is the trash folder.
        """
        tItem = self.__getitem__(tHandle)
        if tItem is None:
            return True
        if tItem.itemClass == nwItemClass.TRASH:
            return True
        if self._trashRoot is not None:
            if tHandle == self._trashRoot:
                return True
            elif tItem.itemParent == self._trashRoot:
                return True
            elif tItem.itemRoot == self._trashRoot:
                return True
        return False

    def trashRoot(self):
        """Returns the handle of the trash folder, or None if there
        isn't one.
        """
        if self._trashRoot:
            return self._trashRoot
        return None

    def findRoot(self, theClass):
        """Find the first root item for a given class.
        """
        for aRoot in self._treeRoots:
            tItem = self.__getitem__(aRoot)
            if tItem is None:
                continue
            if theClass == tItem.itemClass:
                return tItem.itemHandle
        return None

    ##
    #  Setters
    ##

    def setOrder(self, newOrder):
        """Reorders the tree based on a list of items.
        """
        tmpOrder = [tHandle for tHandle in newOrder if tHandle in self._projTree]
        if not (len(tmpOrder) == len(newOrder) == len(self._treeOrder)):
            # Something is wrong, so let's debug it
            for tHandle in newOrder:
                if tHandle not in self._projTree:
                    logger.error("Handle '%s' in new tree order is not in old order", tHandle)
            for tHandle in self._treeOrder:
                if tHandle not in tmpOrder:
                    logger.warning("Handle '%s' in old tree order is not in new order", tHandle)

        # Save the temp list
        self._treeOrder = tmpOrder
        self._setTreeChanged(True)
        logger.debug("Project tree order updated")

        return

    def setFileItemLayout(self, tHandle, itemLayout):
        """Set the nwItemLayout for a specific file.
        """
        tItem = self.__getitem__(tHandle)
        if tItem is None:
            return False
        if not tItem.isFileType():
            logger.error("Item '%s' is not a file", tHandle)
            return False
        if not isinstance(itemLayout, nwItemLayout):
            return False

        tItem.setLayout(itemLayout)

        return True

    ##
    #  Special Methods
    ##

    def __len__(self):
        """The number of items in the project.
        """
        return len(self._treeOrder)

    def __bool__(self):
        """True if there are any items in the project.
        """
        return bool(self._treeOrder)

    def __getitem__(self, tHandle):
        """Return a project item based on its handle. Returns None if
        the handle doesn't exist in the project.
        """
        if tHandle in self._projTree:
            return self._projTree[tHandle]
        logger.error("No tree item with handle '%s'", str(tHandle))
        return None

    def __delitem__(self, tHandle):
        """Remove an item from the internal lists and dictionaries.
        """
        if tHandle in self._treeOrder and tHandle in self._projTree:
            self._treeOrder.remove(tHandle)
            del self._projTree[tHandle]
        else:
            logger.warning("Failed to delete item '%s': item not found", tHandle)
            return

        if tHandle in self._treeRoots:
            del self._treeRoots[tHandle]
        if tHandle == self._trashRoot:
            self._trashRoot = None
        if tHandle == self._archRoot:
            self._archRoot = None

        self._setTreeChanged(True)

        return

    def __contains__(self, tHandle):
        """Checks if a handle exists in the tree.
        """
        return tHandle in self._treeOrder

    def __iter__(self):
        """Iterate through project items.
        """
        for tHandle in self._treeOrder:
            tItem = self._projTree.get(tHandle)
            if isinstance(tItem, NWItem):
                yield tItem
        return

    ##
    #  Internal Functions
    ##

    def _setTreeChanged(self, theState):
        """Set the changed flag to theState, and if being set to True,
        propagate that state change to the parent NWProject class.
        """
        self._treeChanged = theState
        if theState:
            self.theProject.setProjectChanged(True)
        return

    def _makeHandle(self):
        """Generate a unique item handle. In the event that the key
        already exists, generate a new one.
        """
        logger.debug("Generating new handle")
        handle = f"{random.getrandbits(52):013x}"
        if handle in self._projTree:
            logger.warning("Duplicate handle encountered! Retrying ...")
            handle = self._makeHandle()

        return handle

# END Class NWTree
