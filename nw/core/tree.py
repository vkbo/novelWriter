# -*- coding: utf-8 -*-
"""
novelWriter – Project Tree Class
================================
Data class for the project's tree of project items

File History:
Created: 2020-05-07 [0.4.5]

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

import nw
import logging
import os

from lxml import etree
from hashlib import sha256
from time import time

from nw.core.item import NWItem
from nw.common import checkHandle
from nw.constants import (
    nwFiles, nwItemType, nwItemClass, nwItemLayout, nwConst, nwLists
)

logger = logging.getLogger(__name__)

# Layout Translation Map
LAYOUT_MAP = {
    nwItemLayout.SCENE: {
        "H1": nwItemLayout.BOOK,
        "H2": nwItemLayout.CHAPTER,
    },
    nwItemLayout.CHAPTER: {
        "H1": nwItemLayout.BOOK,
        "H3": nwItemLayout.SCENE,
        "H4": nwItemLayout.SCENE,
    },
    nwItemLayout.UNNUMBERED: {
        "H1": nwItemLayout.BOOK,
        "H3": nwItemLayout.SCENE,
        "H4": nwItemLayout.SCENE,
    },
    nwItemLayout.PARTITION: {
        "H2": nwItemLayout.CHAPTER,
        "H3": nwItemLayout.SCENE,
        "H4": nwItemLayout.SCENE,
    },
}

class NWTree():

    def __init__(self, theProject):

        self.theProject = theProject

        self._projTree    = {}    # Holds all the items of the project
        self._treeOrder   = []    # The order of the tree items on the tree view
        self._treeRoots   = []    # The root items of the tree
        self._trashRoot   = None  # The handle of the trash root folder
        self._archRoot    = None  # The handle of the archive root folder
        self._theIndex    = 0     # The current iterator index
        self._treeChanged = False # True if tree structure has changed

        self._handleSeed  = None  # Used for generating handles for testing

        return

    ##
    #  Class Methods
    ##

    def clear(self):
        """Clear the item tree entirely.
        """
        self._projTree  = {}
        self._treeOrder = []
        self._treeRoots = []
        self._trashRoot = None
        self._archRoot  = None
        self._theIndex  = 0
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
            logger.warning("Duplicate handle %s detected, skipping" % tHandle)
            return False

        logger.verbose("Adding item %s with parent %s" % (str(tHandle), str(pHandle)))

        nwItem.setHandle(tHandle)
        nwItem.setParent(pHandle)

        if nwItem.itemType == nwItemType.ROOT:
            logger.verbose("Item %s is a root item" % str(tHandle))
            self._treeRoots.append(tHandle)
            if nwItem.itemClass == nwItemClass.ARCHIVE:
                logger.verbose("Item %s is the archive folder" % str(tHandle))
                self._archRoot = tHandle

        if nwItem.itemType == nwItemType.TRASH:
            if self._trashRoot is None:
                logger.verbose("Item %s is the trash folder" % str(tHandle))
                self._trashRoot = tHandle
            else:
                logger.error("Only one trash folder allowed")
                return False

        self._projTree[tHandle] = nwItem
        self._treeOrder.append(tHandle)
        self._setTreeChanged(True)

        return True

    def packXML(self, xParent):
        """Pack the content of the tree into the provided XML object. In
        the order defined by the _treeOrder list.
        """
        xContent = etree.SubElement(xParent, "content", attrib={
            "count": str(len(self._treeOrder))}
        )
        for tHandle in self._treeOrder:
            tItem = self.__getitem__(tHandle)
            tItem.packXML(xContent)
        return

    def unpackXML(self, xContent):
        """Iterate through all items of a content XML object and add
        them to the project tree.
        """
        if xContent.tag != "content":
            logger.error("XML entry is not a NWTree")
            return False

        self.clear()
        for xItem in xContent:
            nwItem = NWItem(self.theProject)
            if nwItem.unpackXML(xItem):
                self.append(nwItem.itemHandle, nwItem.itemParent, nwItem)
                nwItem.saveInitialCount()

        return True

    def writeToCFile(self):
        """Write the convenience table of contents file in the root of
        the project directory.
        """
        tocList = []
        tocLen = 0
        for tHandle in self._treeOrder:
            tItem = self.__getitem__(tHandle)
            if tItem is None:
                continue
            tFile = tHandle+".nwd"
            if os.path.isfile(os.path.join(self.theProject.projContent, tFile)):
                tocLine = "%-25s  %-9s  %-10s  %s" % (
                    os.path.join("content", tFile),
                    tItem.itemClass.name,
                    tItem.itemLayout.name,
                    tItem.itemName,
                )
                tocList.append(tocLine)
                tocLen = max(tocLen, len(tocLine))

        try:
            # Dump the text
            tocText = os.path.join(self.theProject.projPath, nwFiles.TOC_TXT)
            with open(tocText, mode="w", encoding="utf8") as outFile:
                outFile.write("\n")
                outFile.write("Table of Contents\n")
                outFile.write("=================\n")
                outFile.write("\n")
                outFile.write("%-25s  %-9s  %-10s  %s\n" % (
                    "File Name", "Class", "Layout", "Document Label"
                ))
                outFile.write("-"*tocLen + "\n")
                outFile.write("\n".join(tocList))
                outFile.write("\n")

        except Exception:
            logger.error("Could not write ToC file")
            nw.logException()
            return False

        return True

    def sumWords(self):
        """Loops over all entries and adds up the word counts.
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

    def updateItemLayout(self, tHandle, hLevel):
        """Check if the item layout needs updating based on the header
        given level.
        """
        tItem = self.__getitem__(tHandle)
        if tItem is None:
            return False
        if tItem.itemClass not in nwLists.CLS_NOVEL:
            return False
        if hLevel not in ("H1", "H2", "H3", "H4"):
            return False

        iLayout = tItem.itemLayout
        if iLayout in LAYOUT_MAP:
            if hLevel in LAYOUT_MAP[iLayout]:
                tItem.itemLayout = LAYOUT_MAP[iLayout][hLevel]
                logger.debug("Changed layout for %s from %s to %s" % (
                    tHandle, iLayout.name, tItem.itemLayout.name
                ))
                return True

        return False

    ##
    #  Tree Structure Methods
    ##

    def trashRoot(self):
        """Returns the handle of the trash folder, or None if there
        isn't one.
        """
        if self._trashRoot:
            return self._trashRoot
        return None

    def isTrashRoot(self, tHandle):
        """Check if a handle is the trash folder.
        """
        if self._trashRoot is None:
            return False
        return tHandle == self._trashRoot

    def archiveRoot(self):
        """Returns the handle of the archive folder, or None if there
        isn't one.
        """
        if self._archRoot:
            return self._archRoot
        return None

    def findRoot(self, theClass):
        """Find the root item for a given class.
        Note: This returns the first item for class CUSTOM.
        """
        for aRoot in self._treeRoots:
            tItem = self.__getitem__(aRoot)
            if tItem is None:
                continue
            if theClass == tItem.itemClass:
                return tItem.itemHandle
        return None

    def checkRootUnique(self, theClass):
        """Checks if there already is a root entry of class 'theClass'
        in the root of the project tree. CUSTOM class is skipped as it
        is not required to be unique.
        """
        if theClass == nwItemClass.CUSTOM:
            return True
        for aRoot in self._treeRoots:
            tItem = self.__getitem__(aRoot)
            if tItem is None:
                continue
            if theClass == tItem.itemClass:
                return False
        return True

    def getRootItem(self, tHandle):
        """Iterate upwards in the tree until we find the item with
        parent None, the root item. We do this with a for loop with a
        maximum depth to make infinite loops impossible.
        """
        tItem = self.__getitem__(tHandle)
        if tItem is not None:
            for i in range(nwConst.MAX_DEPTH + 1):
                if tItem.itemParent is None:
                    return tItem
                else:
                    tHandle = tItem.itemParent
                    tItem = self.__getitem__(tHandle)
        return None

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
            for i in range(nwConst.MAX_DEPTH + 1):
                if tItem.itemParent is None:
                    return tTree
                else:
                    tHandle = tItem.itemParent
                    tItem   = self.__getitem__(tHandle)
                    if tItem is None:
                        return tTree
                    else:
                        tTree.append(tHandle)
        return tTree

    ##
    #  Setters
    ##

    def setOrder(self, newOrder):
        """Reorders the tree based on a list of items.
        """
        tmpOrder = []

        # Add all known elements to a new temp list
        for tHandle in newOrder:
            if tHandle in self._projTree:
                tmpOrder.append(tHandle)
            else:
                logger.error("Handle %s in new tree order is not in project tree" % tHandle)

        # Do a reverse lookup to check for items that will be lost
        # This is mainly for debugging purposes
        for tHandle in self._treeOrder:
            if tHandle not in tmpOrder:
                logger.warning("Handle %s in old tree order is not in new tree order" % tHandle)

        # Save the temp list
        self._treeOrder = tmpOrder
        self._setTreeChanged(True)
        logger.verbose("Project tree order updated")

        return

    def setSeed(self, theSeed):
        """Used for debugging!
        Sets a seed for generating handles so that they always come out
        in a predictable order.
        """
        self._handleSeed = theSeed
        return

    def setFileItemLayout(self, tHandle, itemLayout):
        """Set the nwItemLayout for a specific file.
        """
        tItem = self.__getitem__(tHandle)
        if tItem is None:
            return False
        if tItem.itemType != nwItemType.FILE:
            logger.error("Item %s is not a file" % tHandle)
            return False
        if not isinstance(itemLayout, nwItemLayout):
            return False

        tItem.setLayout(itemLayout)

        return True

    ##
    #  Getters
    ##

    def countTypes(self):
        """Count the number of files, folders and roots in the project.
        """
        nRoot = 0
        nFolder = 0
        nFile = 0

        for tHandle in self._treeOrder:
            tItem = self.__getitem__(tHandle)
            if tItem is None:
                continue
            elif tItem.itemType == nwItemType.ROOT:
                nRoot += 1
            elif tItem.itemType == nwItemType.FOLDER:
                nFolder += 1
            elif tItem.itemType == nwItemType.FILE:
                nFile += 1

        return nRoot, nFolder, nFile

    ##
    #  Meta Methods
    ##

    def __len__(self):
        """Return the length counter. Does not check that it is correct!
        """
        return len(self._treeOrder)

    def __bool__(self):
        """Returns True if the tree has any entries.
        """
        return len(self._treeOrder) > 0

    ##
    #  Item Access Methods
    ##

    def __getitem__(self, tHandle):
        """Return a project item based on its handle. Returns None if
        the handle doesn't exist in the project.
        """
        if tHandle in self._projTree:
            return self._projTree[tHandle]
        logger.error("No tree item with handle %s" % str(tHandle))
        return None

    def __delitem__(self, tHandle):
        """Remove an item from the internal lists and dictionaries.
        """
        if tHandle in self._treeOrder and tHandle in self._projTree:
            self._treeOrder.remove(tHandle)
            del self._projTree[tHandle]
        else:
            logger.warning("Failed to delete item %s: item not found" % tHandle)
            return

        if tHandle in self._treeRoots:
            self._treeRoots.remove(tHandle)
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

    ##
    #  Iterator Methods
    ##

    def __iter__(self):
        """Initiates the iterator.
        """
        self._theIndex = 0
        return self

    def __next__(self):
        """Returns the item from the next entry in the _treeOrder list.
        """
        if self._theIndex < len(self._treeOrder):
            theItem = self.__getitem__(self._treeOrder[self._theIndex])
            self._theIndex += 1
            return theItem
        else:
            raise StopIteration

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

    def _makeHandle(self, addSeed=""):
        """Generate a unique item handle. In the event that the key
        already exists, salt the seed and generate a new handle.
        A key collision is very unlikely to be caused by the truncation
        of the sha256 hash to 13 characters. Assuming it is near-random,
        it will on average happen every 4.5^15 times. However, the clock
        seed is likely to occasionally generate a collision if the
        handle requests come faster than the clock resolution.
        """
        if self._handleSeed is None:
            newSeed = str(time()) + addSeed
        else:
            # This is used for debugging
            newSeed = str(self._handleSeed)
            self._handleSeed += 1

        logger.verbose("Generating handle with seed '%s'" % newSeed)
        itemHandle = sha256(newSeed.encode()).hexdigest()[0:13]
        if itemHandle in self._projTree:
            logger.warning("Duplicate handle encountered! Retrying ...")
            itemHandle = self._makeHandle(addSeed+"!")

        return itemHandle

# END Class NWTree
