"""
novelWriter – GUI Project Tree
==============================
GUI classes for the main window project tree

File History:
Created: 2018-09-29 [0.0.1] GuiProjectTree
Created: 2020-06-04 [0.7.0] GuiProjectTreeMenu

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

from time import time

from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QAbstractItemView, QMenu, QAction
)

from nw.core import NWDoc
from nw.enum import nwItemType, nwItemClass, nwItemLayout, nwAlert
from nw.constants import nwConst, trConst, nwLists, nwLabels

logger = logging.getLogger(__name__)


class GuiProjectTree(QTreeWidget):

    C_NAME   = 0
    C_COUNT  = 1
    C_EXPORT = 2
    C_STATUS = 3

    novelItemChanged = pyqtSignal()
    noteItemChanged = pyqtSignal()
    projectWordCountChanged = pyqtSignal(int, int)

    def __init__(self, theParent):
        QTreeWidget.__init__(self, theParent)

        logger.debug("Initialising GuiProjectTree ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theParent.theProject
        self.theIndex   = theParent.theIndex

        # Internal Variables
        self._treeMap     = {}
        self._treeChanged = False
        self._timeChanged = 0
        self._lastMove    = {}

        ##
        #  Build GUI
        ##

        # Context Menu
        self.ctxMenu = GuiProjectTreeMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._rightClickMenu)

        # Tree Settings
        iPx = self.theTheme.baseIconSize
        self.setIconSize(QSize(iPx, iPx))
        self.setExpandsOnDoubleClick(True)
        self.setIndentation(iPx)
        self.setColumnCount(4)
        self.setHeaderLabels([
            self.tr("Project Tree"), self.tr("Words"), "",
            self.tr("Status") if self.mainConf.fullStatus else ""
        ])

        treeHeadItem = self.headerItem()
        treeHeadItem.setTextAlignment(self.C_COUNT, Qt.AlignRight)
        treeHeadItem.setToolTip(self.C_NAME, self.tr("Item label"))
        treeHeadItem.setToolTip(self.C_COUNT, self.tr("Word count"))
        treeHeadItem.setToolTip(self.C_EXPORT, self.tr("Include in build"))
        treeHeadItem.setToolTip(self.C_STATUS, self.tr("Item status"))

        # Let the last column stretch, and set the minimum size to the
        # size of the icon as the default Qt font metrics approach fails
        # for some fonts like the Ubuntu font.
        treeHeader = self.header()
        treeHeader.setStretchLastSection(True)
        treeHeader.setMinimumSectionSize(iPx + 6)

        # Allow Move by Drag & Drop
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        # But don't allow drop on root level
        trRoot = self.invisibleRootItem()
        trRoot.setFlags(trRoot.flags() ^ Qt.ItemIsDropEnabled)

        # Set Multiple Selection by CTRL
        # Disabled for now, until the merge files option has been added
        # self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Get user's column width preferences for NAME and COUNT
        treeColWidth = self.mainConf.getTreeColWidths()
        if len(treeColWidth) <= 4:
            for colN, colW in enumerate(treeColWidth):
                self.setColumnWidth(colN, colW)

        # The last column should just auto-scale
        self.resizeColumnToContents(self.C_STATUS)

        # Set custom settings
        self.initTree()

        # Internal Function Mapping
        self.makeAlert = self.theParent.makeAlert
        self.askQuestion = self.theParent.askQuestion

        logger.debug("GuiProjectTree initialisation complete")

        return

    def initTree(self):
        """Set or update tree widget settings.
        """
        # Scroll bars
        if self.mainConf.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if self.mainConf.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        return

    ##
    #  Class Methods
    ##

    def clearTree(self):
        """Clear the GUI content and the related map.
        """
        self.clear()
        self._treeMap = {}
        self._treeChanged = False
        self._timeChanged = 0
        return

    def newTreeItem(self, itemType, itemClass):
        """Add new item to the tree, with a given itemType and
        itemClass, and attach it to the selected handle. Also make sure
        the item is added in a place it can be added, and that other
        meta data is set correctly to ensure a valid project tree.
        """
        pHandle = self.getSelectedHandle()
        nHandle = None

        if not self.theParent.hasProject:
            logger.error("No project open")
            return False

        if not isinstance(itemType, nwItemType):
            # This would indicate an internal bug
            logger.error("No itemType provided")
            return False

        # The item needs to be assigned an item class, so one must be
        # provided, or it must be possible to extract it from the parent
        # item of the new item.
        if itemClass is None and pHandle is not None:
            pItem = self.theProject.projTree[pHandle]
            if pItem is not None:
                itemClass = pItem.itemClass

        # If class is still not set, alert the user and exit
        if itemClass is None:
            if itemType == nwItemType.FILE:
                self.makeAlert(self.tr(
                    "Please select a valid location in the tree to add the document."
                ), nwAlert.ERROR)
            else:
                self.makeAlert(self.tr(
                    "Please select a valid location in the tree to add the folder."
                ), nwAlert.ERROR)
            return False

        # Everything is fine, we have what we need, so we proceed
        logger.verbose(
            "Adding new item of type '%s' and class '%s' to handle '%s'",
            itemType.name, itemClass.name, str(pHandle)
        )

        if itemType == nwItemType.ROOT:
            tHandle = self.theProject.newRoot(trConst(nwLabels.CLASS_NAME[itemClass]), itemClass)
            if tHandle is None:
                logger.error("No root item added")
                return False

        else:
            # If no parent has been selected, make the new file under
            # the root NOVEL item.
            if pHandle is None:
                pHandle = self.theProject.projTree.findRoot(nwItemClass.NOVEL)

            # If still nothing, give up
            if pHandle is None:
                self.makeAlert(self.tr(
                    "Did not find anywhere to add the file or folder!"
                ), nwAlert.ERROR)
                return False

            # Now check if the selected item is a file, in which case
            # the new file will be a sibling
            pItem = self.theProject.projTree[pHandle]
            if pItem.itemType == nwItemType.FILE:
                nHandle = pHandle
                pHandle = pItem.itemParent

            # If we again have no home, give up
            if pHandle is None:
                self.makeAlert(self.tr(
                    "Did not find anywhere to add the file or folder!"
                ), nwAlert.ERROR)
                return False

            if self.theProject.projTree.isTrashRoot(pHandle):
                self.makeAlert(self.tr(
                    "Cannot add new files or folders to the Trash folder."
                ), nwAlert.ERROR)
                return False

            parTree = self.theProject.projTree.getItemPath(pHandle)

            # If we're still here, add the file or folder
            if itemType == nwItemType.FILE:
                tHandle = self.theProject.newFile(self.tr("New File"), itemClass, pHandle)

            elif itemType == nwItemType.FOLDER:
                if len(parTree) >= nwConst.MAX_DEPTH - 1:
                    # Folders cannot be deeper than MAX_DEPTH - 1, leaving room
                    # for one more level of files.
                    self.makeAlert(self.tr(
                        "Cannot add new folder to this item. "
                        "Maximum folder depth has been reached."
                    ), nwAlert.ERROR)
                    return False
                tHandle = self.theProject.newFolder(self.tr("New Folder"), itemClass, pHandle)

            else:
                logger.error("Failed to add new item")
                return False

        # If there is no handle set, return here
        if tHandle is None:
            return True

        # Add the new item to the tree
        self.revealNewTreeItem(tHandle, nHandle)
        self.theParent.editItem(tHandle)
        nwItem = self.theProject.projTree[tHandle]

        # If this is a folder, return here
        if nwItem.itemType != nwItemType.FILE:
            return True

        # This is a new files, so let's add some content
        newDoc = NWDoc(self.theProject, tHandle)
        curTxt = newDoc.readDocument()
        if curTxt is None:
            curTxt = ""

        if curTxt == "":
            if nwItem.itemLayout == nwItemLayout.DOCUMENT:
                newText = f"### {nwItem.itemName}\n\n"
            else:
                newText = f"# {nwItem.itemName}\n\n"

            # Save the text and index it
            newDoc.writeDocument(newText)
            self.theIndex.scanText(tHandle, newText)

            # Get Word Counts
            cC, wC, pC = self.theIndex.getCounts(tHandle)
            nwItem.setCharCount(cC)
            nwItem.setWordCount(wC)
            nwItem.setParaCount(pC)
            self.propagateCount(tHandle, wC)
            self.projectWordCount()

        return True

    def revealNewTreeItem(self, tHandle, nHandle=None):
        """Reveal a newly added project item in the project tree.
        """
        nwItem = self.theProject.projTree[tHandle]
        trItem = self._addTreeItem(nwItem, nHandle)
        if trItem is None:
            return False

        pHandle = nwItem.itemParent
        if pHandle is not None and pHandle in self._treeMap:
            self._treeMap[pHandle].setExpanded(True)

        self._emitItemChange(tHandle)
        self.clearSelection()
        trItem.setSelected(True)

        return True

    def moveTreeItem(self, nStep):
        """Move an item up or down in the tree, but only if the treeView
        has focus. This also applies when the menu is used.
        """
        if not self.theParent.hasProject:
            logger.error("No project open")
            return False

        if not self.hasFocus():
            return False

        tHandle = self.getSelectedHandle()
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return False

        pItem = tItem.parent()
        if pItem is None:
            tIndex = self.indexOfTopLevelItem(tItem)
            nChild = self.topLevelItemCount()
            nIndex = tIndex + nStep
            if nIndex < 0 or nIndex >= nChild:
                return False
            cItem = self.takeTopLevelItem(tIndex)
            self.insertTopLevelItem(nIndex, cItem)

        else:
            tIndex = pItem.indexOfChild(tItem)
            nChild = pItem.childCount()
            nIndex = tIndex + nStep
            if nIndex < 0 or nIndex >= nChild:
                return False
            cItem = pItem.takeChild(tIndex)
            pItem.insertChild(nIndex, cItem)
            self._recordLastMove(cItem, pItem, tIndex)

        self.clearSelection()
        cItem.setSelected(True)
        self._setTreeChanged(True)
        self._emitItemChange(tHandle)

        return True

    def saveTreeOrder(self):
        """Build a list of the items in the project tree and send them
        to the project class. This syncs up the two versions of the
        project structure, and must be called before any code that
        depends on this order to be up to date.
        """
        theList = []
        for i in range(self.topLevelItemCount()):
            theList = self._scanChildren(theList, self.topLevelItem(i), i)
        logger.debug("Saving project tree item order")
        self.theProject.setTreeOrder(theList)
        return True

    def flushTreeOrder(self):
        """Calls saveTreeOrder if there are unsaved changes, otherwise
        does nothing.
        """
        if self._treeChanged:
            logger.verbose("Flushing project tree to project class")
            self.saveTreeOrder()
            self._setTreeChanged(False)
        return

    def getTreeFromHandle(self, tHandle):
        """Recursively return all the children items starting from a
        given item handle.
        """
        theList = []
        theItem = self._getTreeItem(tHandle)
        if theItem is not None:
            theList = self._scanChildren(theList, theItem, 0)
        return theList

    def getColumnSizes(self):
        """Return the column widths for the tree columns.
        """
        retVals = [
            self.columnWidth(0),
            self.columnWidth(1),
            self.columnWidth(2),
        ]
        return retVals

    def emptyTrash(self):
        """Permanently delete all documents in the Trash folder. This
        function only asks for confirmation once, and calls the regular
        deleteItem function for each document in the Trash folder.
        """
        if not self.theParent.hasProject:
            logger.error("No project open")
            return False

        trashHandle = self.theProject.projTree.trashRoot()

        logger.debug("Emptying Trash folder")
        if trashHandle is None:
            self.makeAlert(self.tr(
                "There is currently no Trash folder in this project."
            ), nwAlert.INFO)
            return False

        theTrash = self.getTreeFromHandle(trashHandle)
        if trashHandle in theTrash:
            theTrash.remove(trashHandle)

        nTrash = len(theTrash)
        if nTrash == 0:
            self.makeAlert(self.tr(
                "The Trash folder is already empty."
            ), nwAlert.INFO)
            return False

        msgYes = self.askQuestion(
            self.tr("Empty Trash"),
            self.tr("Permanently delete {0} file(s) from Trash?").format(nTrash)
        )
        if not msgYes:
            return False

        logger.verbose("Deleting %d file(s) from Trash", nTrash)
        for tHandle in self.getTreeFromHandle(trashHandle):
            if tHandle == trashHandle:
                continue
            self.deleteItem(tHandle, alreadyAsked=True, bulkAction=True)

        if nTrash > 0:
            self._setTreeChanged(True)

        return True

    def deleteItem(self, tHandle=None, alreadyAsked=False, bulkAction=False):
        """Delete an item from the project tree. As a first step, files are
        moved to the Trash folder. Permanent deletion is a second step. This
        second step also deletes the item from the project object as well as
        delete the files on disk. Folders are deleted if they're empty only,
        and the deletion is always permanent.
        """
        if not self.theParent.hasProject:
            logger.error("No project open")
            return False

        if not self.hasFocus() and not bulkAction:
            logger.info("Delete action blocked due to no widget focus")
            return False

        if tHandle is None:
            tHandle = self.getSelectedHandle()

        if tHandle is None:
            logger.error("There is no item to delete")
            return False

        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.projTree[tHandle]

        if trItemS is None or nwItemS is None:
            logger.error("Could not find tree item for deletion")
            return False

        wCount = int(trItemS.data(self.C_COUNT, Qt.UserRole))
        if nwItemS.itemType == nwItemType.FILE:
            logger.debug("User requested file '%s' deleted", tHandle)
            trItemP = trItemS.parent()
            trItemT = self._addTrashRoot()
            if trItemP is None or trItemT is None:
                logger.error("Could not delete item")
                return False

            pHandle = nwItemS.itemParent
            if self.theProject.projTree.isTrashRoot(pHandle):
                # If the file is in the trash folder already, as the
                # user if they want to permanently delete the file.
                doPermanent = False
                if not alreadyAsked:
                    msgYes = self.askQuestion(
                        self.tr("Delete File"),
                        self.tr("Permanently delete file '{0}'?").format(nwItemS.itemName)
                    )
                    if msgYes:
                        doPermanent = True
                else:
                    doPermanent = True

                if doPermanent:
                    logger.debug("Permanently deleting file with handle '%s'", tHandle)

                    self.propagateCount(tHandle, 0)
                    tIndex = trItemP.indexOfChild(trItemS)
                    trItemC = trItemP.takeChild(tIndex)

                    if self.theParent.docEditor.docHandle() == tHandle:
                        self.theParent.closeDocument()

                    delDoc = NWDoc(self.theProject, tHandle)
                    if not delDoc.deleteDocument():
                        self.makeAlert([
                            self.tr("Could not delete document file."), delDoc.getError()
                        ], nwAlert.ERROR)
                        return False

                    self.theIndex.deleteHandle(tHandle)
                    self._deleteTreeItem(tHandle)
                    self._setTreeChanged(True)
                    self.projectWordCount()

            else:
                # The file is not already in the trash folder, so we
                # move it there.
                msgYes = self.askQuestion(
                    self.tr("Delete File"),
                    self.tr("Move file '{0}' to Trash?").format(nwItemS.itemName),
                )
                if msgYes:
                    if pHandle is None:
                        logger.warning("File has no parent item")

                    logger.debug("Moving file '%s' to trash", tHandle)

                    self.propagateCount(tHandle, 0)
                    tIndex  = trItemP.indexOfChild(trItemS)
                    trItemC = trItemP.takeChild(tIndex)
                    trItemT.addChild(trItemC)
                    self._updateItemParent(tHandle)
                    self.propagateCount(tHandle, wCount)

                    self.theIndex.deleteHandle(tHandle)
                    self._recordLastMove(trItemS, trItemP, tIndex)
                    self._setTreeChanged(True)

        elif nwItemS.itemType == nwItemType.FOLDER:
            logger.debug("User requested folder '%s' deleted", tHandle)
            trItemP = trItemS.parent()
            if trItemP is None:
                logger.error("Could not delete folder")
                return False
            tIndex = trItemP.indexOfChild(trItemS)
            if trItemS.childCount() == 0:
                trItemP.takeChild(tIndex)
                self._deleteTreeItem(tHandle)
                self._setTreeChanged(True)
            else:
                self.makeAlert(self.tr(
                    "Cannot delete folder. It is not empty. "
                    "Recursive deletion is not supported. "
                    "Please delete the content first."
                ), nwAlert.ERROR)
                return False

        elif nwItemS.itemType == nwItemType.ROOT:
            logger.debug("User requested root folder '%s' deleted", tHandle)
            tIndex = self.indexOfTopLevelItem(trItemS)
            if trItemS.childCount() == 0:
                self.takeTopLevelItem(tIndex)
                self._deleteTreeItem(tHandle)
                self.theParent.mainMenu.setAvailableRoot()
                self._setTreeChanged(True)
            else:
                self.makeAlert(self.tr(
                    "Cannot delete root folder. It is not empty. "
                    "Recursive deletion is not supported. "
                    "Please delete the content first."
                ), nwAlert.ERROR)
                return False

        return True

    def setTreeItemValues(self, tHandle):
        """Set the name and flag values for a tree item from a handle in
        the project tree. Does not trigger a tree change as the data is
        already coming from the project tree.
        """
        trItem = self._getTreeItem(tHandle)
        nwItem = self.theProject.projTree[tHandle]
        if trItem is None or nwItem is None:
            return

        expIcon = QIcon()
        if nwItem.itemType == nwItemType.FILE:
            if nwItem.isExported:
                expIcon = self.theTheme.getIcon("check")
            else:
                expIcon = self.theTheme.getIcon("cross")

        iStatus = nwItem.itemStatus
        if nwItem.itemClass == nwItemClass.NOVEL:
            iStatus = self.theProject.statusItems.checkEntry(iStatus)  # Make sure it's valid
            statIcon = self.theParent.statusIcons[iStatus]
        else:
            iStatus = self.theProject.importItems.checkEntry(iStatus)  # Make sure it's valid
            statIcon = self.theParent.importIcons[iStatus]

        hLevel = self.theIndex.getHandleHeaderLevel(tHandle)
        itemIcon = self.theTheme.getItemIcon(
            nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, hLevel
        )

        trItem.setIcon(self.C_NAME, itemIcon)
        trItem.setText(self.C_NAME, nwItem.itemName)
        trItem.setIcon(self.C_EXPORT, expIcon)
        trItem.setIcon(self.C_STATUS, statIcon)

        if self.mainConf.fullStatus:
            trItem.setText(self.C_STATUS, nwItem.itemStatus)
        else:
            trItem.setToolTip(self.C_STATUS, nwItem.itemStatus)

        if self.mainConf.emphLabels and nwItem.itemLayout == nwItemLayout.DOCUMENT:
            if hLevel in ("H1", "H2"):
                trFont = trItem.font(self.C_NAME)
                trFont.setBold(True)
                trFont.setUnderline(True)
                trItem.setFont(self.C_NAME, trFont)

        return

    def propagateCount(self, tHandle, theCount, nDepth=0):
        """Recursive function setting the word count for a given item,
        and propagating that count upwards in the tree until reaching a
        root item. This function is more efficient than recalculating
        everything each time the word count is updated, but is also
        prone to diverging from the true values if the counts are not
        properly reported to the function.
        """
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return

        tItem.setText(self.C_COUNT, f"{theCount:n}")
        tItem.setData(self.C_COUNT, Qt.UserRole, int(theCount))

        pItem = tItem.parent()
        if pItem is None:
            return

        pCount = 0
        for i in range(pItem.childCount()):
            pCount += int(pItem.child(i).data(self.C_COUNT, Qt.UserRole))
            pHandle = pItem.data(self.C_NAME, Qt.UserRole)

        if not nDepth > nwConst.MAX_DEPTH + 1 and pHandle != "":
            self.propagateCount(pHandle, pCount, nDepth+1)

        return

    def projectWordCount(self):
        """Sum up the word counts for all root items and set the
        relevant values in the project and on the status bar. This call
        is a fast way of getting this number, and depends on the
        propagateCount function being called when it should to maintain
        the correct count.
        """
        nWords = 0
        for n in range(self.topLevelItemCount()):
            tItem = self.topLevelItem(n)
            nWords += int(tItem.data(self.C_COUNT, Qt.UserRole))

        self.theProject.setProjectWordCount(nWords)
        sWords = self.theProject.getSessionWordCount()

        self.projectWordCountChanged.emit(nWords, sWords)

        return

    def buildTree(self):
        """Build the entire project tree from scratch. This depends on
        the save project item iterator in the project class which will
        always make sure items with a parent have had their parent item
        sent first.
        """
        logger.debug("Building the project tree ...")
        self.clearTree()

        self.setHeaderLabels([
            self.tr("Project Tree"), self.tr("Words"), "",
            self.tr("Status") if self.mainConf.fullStatus else ""
        ])

        iCount = 0
        for nwItem in self.theProject.getProjectItems():
            iCount += 1
            self._addTreeItem(nwItem)

        logger.debug("%d item(s) added to the project tree", iCount)
        return True

    def undoLastMove(self):
        """Attempt to undo the last action.
        """
        srcItem = self._lastMove.get("item", None)
        dstItem = self._lastMove.get("parent", None)
        dstIndex = self._lastMove.get("index", None)

        if not self.hasFocus():
            return False

        if srcItem is None or dstItem is None or dstIndex is None:
            logger.verbose("No tree move to undo")
            return False

        if srcItem not in self._treeMap.values():
            logger.warning("Source item no longer exists")
            return False

        if dstItem not in self._treeMap.values():
            logger.warning("Previous parent item no longer exists")
            return False

        dstIndex = min(max(0, dstIndex), dstItem.childCount())
        wCount = int(srcItem.data(self.C_COUNT, Qt.UserRole))
        sHandle = srcItem.data(self.C_NAME, Qt.UserRole)
        dHandle = dstItem.data(self.C_NAME, Qt.UserRole)
        logger.debug("Moving item '%s' back to '%s', index %d", sHandle, dHandle, dstIndex)

        self.propagateCount(sHandle, 0)
        parItem = srcItem.parent()
        srcIndex = parItem.indexOfChild(srcItem)
        movItem = parItem.takeChild(srcIndex)
        dstItem.insertChild(dstIndex, movItem)

        snItem = self.theProject.projTree[sHandle]
        dnItem = self.theProject.projTree[dHandle]
        self._postItemMove(sHandle, snItem, dnItem, wCount)

        self.clearSelection()
        movItem.setSelected(True)
        self._lastMove = {}

        return True

    def getSelectedHandle(self):
        """Get the currently selected handle. If multiple items are
        selected, return the first.
        """
        selItem = self.selectedItems()
        if selItem:
            return selItem[0].data(self.C_NAME, Qt.UserRole)

        return None

    def setSelectedHandle(self, tHandle, doScroll=False):
        """Set a specific handle as the selected item.
        """
        if tHandle not in self._treeMap:
            return False

        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return False

        self.clearSelection()
        self._treeMap[tHandle].setSelected(True)

        selItems = self.selectedIndexes()
        if selItems and doScroll:
            self.scrollTo(selItems[0], QAbstractItemView.PositionAtCenter)

        return True

    def changedSince(self, checkTime):
        """Check if the tree has changed since a given time.
        """
        return self._timeChanged > checkTime

    ##
    #  Slots
    ##

    @pyqtSlot("QPoint")
    def _rightClickMenu(self, clickPos):
        """The user right clicked an element in the project tree, so we
        open a context menu in-place.
        """
        selItem = self.itemAt(clickPos)
        if isinstance(selItem, QTreeWidgetItem):
            tHandle = selItem.data(self.C_NAME, Qt.UserRole)
            self.setSelectedHandle(tHandle)  # Just to be safe
            tItem = self.theProject.projTree[tHandle]
            if tItem is not None:
                if self.ctxMenu.filterActions(tItem):
                    # Only open menu if any actions remain after filter
                    self.ctxMenu.exec_(self.viewport().mapToGlobal(clickPos))

        return

    @pyqtSlot(str, int, int, int)
    def doUpdateCounts(self, tHandle, cCount, wCount, pCount):
        """Slot for updating the word count of a specific item.
        """
        self.propagateCount(tHandle, wCount)
        self.projectWordCount()
        return

    ##
    #  Events
    ##

    def mousePressEvent(self, theEvent):
        """Overload mousePressEvent to clear selection if clicking the
        mouse in a blank area of the tree view, and to load a document
        for viewing if the user middle-clicked.
        """
        QTreeWidget.mousePressEvent(self, theEvent)

        if theEvent.button() == Qt.LeftButton:
            selItem = self.indexAt(theEvent.pos())
            if not selItem.isValid():
                self.clearSelection()

        elif theEvent.button() == Qt.MiddleButton:
            selItem = self.itemAt(theEvent.pos())
            if not isinstance(selItem, QTreeWidgetItem):
                return

            tHandle = selItem.data(self.C_NAME, Qt.UserRole)
            tItem = self.theProject.projTree[tHandle]
            if tItem is None:
                return

            if tItem.itemType == nwItemType.FILE:
                self.theParent.viewDocument(tHandle)

        return

    def dropEvent(self, theEvent):
        """Overload the drop of dragged item event to check whether the
        drop is allowed or not. Disallowed drops are cancelled.
        """
        sHandle = self.getSelectedHandle()
        if sHandle is None:
            logger.error("No handle selected")
            return

        dIndex = self.indexAt(theEvent.pos())
        if not dIndex.isValid():
            logger.error("Invalid drop index")
            return

        sItem = self._getTreeItem(sHandle)
        dItem = self.itemFromIndex(dIndex)
        dHandle = dItem.data(self.C_NAME, Qt.UserRole)
        snItem = self.theProject.projTree[sHandle]
        dnItem = self.theProject.projTree[dHandle]
        if dnItem is None:
            self.makeAlert(self.tr(
                "The item cannot be moved to that location."
            ), nwAlert.ERROR)
            return

        pItem = sItem.parent()
        pIndex = 0
        if pItem is not None:
            pIndex = pItem.indexOfChild(sItem)

        wCount = int(sItem.data(self.C_COUNT, Qt.UserRole))
        isFile = snItem.itemType == nwItemType.FILE
        isRoot = snItem.itemType == nwItemType.ROOT
        onFile = dnItem.itemType == nwItemType.FILE

        isSame = snItem.itemClass == dnItem.itemClass
        isNone = snItem.itemClass == nwItemClass.NO_CLASS
        isNote = snItem.itemLayout == nwItemLayout.NOTE
        onFree = dnItem.itemClass in nwLists.FREE_CLASS and isFile

        allowDrop  = isSame or isNone or isNote or onFree
        allowDrop &= not (self.dropIndicatorPosition() == QAbstractItemView.OnItem and onFile)

        if allowDrop and not isRoot:
            logger.debug("Drag'n'drop of item '%s' accepted", sHandle)
            self.propagateCount(sHandle, 0)
            QTreeWidget.dropEvent(self, theEvent)
            self._postItemMove(sHandle, snItem, dnItem, wCount)
            self._recordLastMove(sItem, pItem, pIndex)

        else:
            theEvent.ignore()
            logger.debug("Drag'n'drop of item '%s' not accepted", sHandle)
            self.makeAlert(self.tr(
                "The item cannot be moved to that location."
            ), nwAlert.ERROR)

        return

    ##
    #  Internal Functions
    ##

    def _postItemMove(self, sHandle, snItem, dnItem, wCount):
        """Run various maintenance tasks for a moved item.
        """
        isFile = snItem.itemType == nwItemType.FILE
        isSame = snItem.itemClass == dnItem.itemClass
        onFree = dnItem.itemClass in nwLists.FREE_CLASS and isFile

        self._updateItemParent(sHandle)

        # If the item does not have the same class as the target,
        # and the target is not a free root folder, update its class
        if not (isSame or onFree):
            logger.debug(
                "Item '%s' class has been changed from '%s' to '%s'",
                sHandle, snItem.itemClass.name, dnItem.itemClass.name
            )
            snItem.setClass(dnItem.itemClass)
            self.setTreeItemValues(sHandle)

        self.propagateCount(sHandle, wCount)

        # The items dropped into archive or trash should be removed
        # from the project index, for all other items, we rescan the
        # file to ensure the index is up to date.
        if onFree:
            self.theIndex.deleteHandle(sHandle)
        else:
            self.theIndex.reIndexHandle(sHandle)

        # Trigger dependent updates
        self._setTreeChanged(True)
        self._emitItemChange(sHandle)

        return

    def _getTreeItem(self, tHandle):
        """Returns the QTreeWidgetItem of a given item handle.
        """
        return self._treeMap.get(tHandle, None)

    def _deleteTreeItem(self, tHandle):
        """Delete a tree item from the project and the map.
        """
        del self.theProject.projTree[tHandle]
        self._treeMap.pop(tHandle, None)
        return

    def _scanChildren(self, theList, tItem, tIndex):
        """This is a recursive function returning all items in a tree
        starting at a given QTreeWidgetItem.
        """
        tHandle = tItem.data(self.C_NAME, Qt.UserRole)
        nwItem = self.theProject.projTree[tHandle]
        nwItem.setExpanded(tItem.isExpanded())
        nwItem.setOrder(tIndex)
        theList.append(tHandle)
        for i in range(tItem.childCount()):
            self._scanChildren(theList, tItem.child(i), i)
        return theList

    def _addTreeItem(self, nwItem, nHandle=None):
        """Create a QTreeWidgetItem from an NWItem and add it to the
        project tree.
        """
        tHandle = nwItem.itemHandle
        pHandle = nwItem.itemParent
        newItem = QTreeWidgetItem([""]*4)

        newItem.setText(self.C_NAME, "")
        newItem.setText(self.C_COUNT, "0")
        newItem.setText(self.C_EXPORT, "")
        newItem.setText(self.C_STATUS, "")

        newItem.setTextAlignment(self.C_NAME, Qt.AlignLeft)
        newItem.setTextAlignment(self.C_COUNT, Qt.AlignRight)
        newItem.setTextAlignment(self.C_EXPORT, Qt.AlignLeft)
        newItem.setTextAlignment(self.C_STATUS, Qt.AlignLeft)

        newItem.setData(self.C_NAME, Qt.UserRole, tHandle)
        newItem.setData(self.C_COUNT, Qt.UserRole, 0)

        self._treeMap[tHandle] = newItem
        if pHandle is None:
            if nwItem.itemType == nwItemType.ROOT:
                self.addTopLevelItem(newItem)
                self.theParent.mainMenu.setAvailableRoot()
            elif nwItem.itemType == nwItemType.TRASH:
                self.addTopLevelItem(newItem)
            else:
                self.makeAlert(self.tr(
                    "There is nowhere to add item with name '{0}'."
                ).format(nwItem.itemName), nwAlert.ERROR)
                del self._treeMap[tHandle]
                return None

        else:
            byIndex = -1
            if nHandle is not None and nHandle in self._treeMap:
                try:
                    byIndex = self._treeMap[pHandle].indexOfChild(self._treeMap[nHandle])
                except Exception:
                    logger.error("Failed to get index of item with handle '%s'", nHandle)
            if byIndex >= 0:
                self._treeMap[pHandle].insertChild(byIndex+1, newItem)
            else:
                self._treeMap[pHandle].addChild(newItem)
            self.propagateCount(tHandle, nwItem.wordCount)

        self.setTreeItemValues(tHandle)
        newItem.setExpanded(nwItem.isExpanded)

        self._setTreeChanged(True)

        return newItem

    def _addTrashRoot(self):
        """Adds the trash root folder if it doesn't already exist in the
        project tree.
        """
        trashHandle = self.theProject.trashFolder()
        if trashHandle is None:
            return None

        trItem = self._getTreeItem(trashHandle)
        if trItem is None:
            trItem = self._addTreeItem(
                self.theProject.projTree[trashHandle]
            )
            if trItem is not None:
                trItem.setExpanded(True)
                self._setTreeChanged(True)

        return trItem

    def _updateItemParent(self, tHandle):
        """Update the parent handle of an item so that the information
        in the project is consistent with the treeView.
        """
        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.projTree[tHandle]
        trItemP = trItemS.parent()
        if trItemP is None:
            logger.error("Failed to find new parent item of '%s'", tHandle)
            return False

        pHandle = trItemP.data(self.C_NAME, Qt.UserRole)
        nwItemS.setParent(pHandle)
        self.setTreeItemValues(tHandle)

        logger.debug("The parent of item '%s' has been changed to '%s'", tHandle, pHandle)

        return True

    def _setTreeChanged(self, theState):
        """Set the tree change flag, and propagate to the project.
        """
        self._treeChanged = theState
        if theState:
            self._timeChanged = time()
            self.theProject.setProjectChanged(True)
        return

    def _emitItemChange(self, tHandle):
        """Emit an item change signal for a given handle.
        """
        nwItem = self.theProject.projTree[tHandle]
        if nwItem is None:
            return

        if nwItem.itemType == nwItemType.FILE:
            if nwItem.itemClass == nwItemClass.NOVEL:
                self.novelItemChanged.emit()
            else:
                self.noteItemChanged.emit()

        return

    def _recordLastMove(self, srcItem, parItem, parIndex):
        """Record the last action so that it can be undone.
        """
        prevItem = self._lastMove.get("item", None)
        if prevItem is None or srcItem != prevItem:
            self._lastMove = {
                "item": srcItem,
                "parent": parItem,
                "index": parIndex,
            }

        return

# END Class GuiProjectTree


class GuiProjectTreeMenu(QMenu):

    def __init__(self, theTree):
        QMenu.__init__(self, theTree)

        self.theTree = theTree
        self.theItem = None

        self.editItem = QAction(self.tr("Edit Project Item"), self)
        self.editItem.triggered.connect(self._doEditItem)
        self.addAction(self.editItem)

        self.openItem = QAction(self.tr("Open Document"), self)
        self.openItem.triggered.connect(self._doOpenItem)
        self.addAction(self.openItem)

        self.viewItem = QAction(self.tr("View Document"), self)
        self.viewItem.triggered.connect(self._doViewItem)
        self.addAction(self.viewItem)

        self.toggleExp = QAction(self.tr("Toggle Included Flag"), self)
        self.toggleExp.triggered.connect(self._doToggleExported)
        self.addAction(self.toggleExp)

        self.newFile = QAction(self.tr("New File"), self)
        self.newFile.triggered.connect(self._doMakeFile)
        self.addAction(self.newFile)

        self.newFolder = QAction(self.tr("New Folder"), self)
        self.newFolder.triggered.connect(self._doMakeFolder)
        self.addAction(self.newFolder)

        self.deleteItem = QAction(self.tr("Delete Item"), self)
        self.deleteItem.triggered.connect(self._doDeleteItem)
        self.addAction(self.deleteItem)

        self.emptyTrash = QAction(self.tr("Empty Trash"), self)
        self.emptyTrash.triggered.connect(self._doEmptyTrash)
        self.addAction(self.emptyTrash)

        self.moveUp = QAction(self.tr("Move Item Up"), self)
        self.moveUp.triggered.connect(self._doMoveUp)
        self.addAction(self.moveUp)

        self.moveDown = QAction(self.tr("Move Item Down"), self)
        self.moveDown.triggered.connect(self._doMoveDown)
        self.addAction(self.moveDown)

        return

    def filterActions(self, theItem):
        """Filter the menu entries available based on the properties of
        the item the menu was activated on.
        """
        self.theItem = theItem

        if theItem is None:
            logger.error("Failed to extract information to build tree context menu")
            return False

        trashHandle = self.theTree.theProject.projTree.trashRoot()

        inTrash = theItem.itemParent == trashHandle and trashHandle is not None
        isTrash = theItem.itemHandle == trashHandle and trashHandle is not None
        isFile = theItem.itemType == nwItemType.FILE

        allowNew = not (isTrash or inTrash)

        self.editItem.setVisible(not isTrash)
        self.openItem.setVisible(isFile)
        self.viewItem.setVisible(isFile)
        self.toggleExp.setVisible(isFile)
        self.newFile.setVisible(allowNew)
        self.newFolder.setVisible(allowNew)
        self.deleteItem.setVisible(not isTrash)
        self.emptyTrash.setVisible(isTrash)

        return True

    ##
    #  Slots
    ##

    @pyqtSlot()
    def _doOpenItem(self):
        """Forward the open document call to the main GUI window.
        """
        if self.theItem is not None:
            self.theTree.theParent.openDocument(self.theItem.itemHandle, doScroll=False)
        return

    @pyqtSlot()
    def _doViewItem(self):
        """Forward the view document call to the main GUI window.
        """
        if self.theItem is not None:
            self.theTree.theParent.viewDocument(self.theItem.itemHandle)
        return

    @pyqtSlot()
    def _doEditItem(self):
        """Forward the edit item call to the main GUI window.
        """
        if self.theItem is not None:
            self.theTree.theParent.editItem()
        return

    @pyqtSlot()
    def _doMakeFile(self):
        """Forward the new file call to the project tree.
        """
        if self.theItem is not None:
            self.theTree.newTreeItem(nwItemType.FILE, None)
        return

    @pyqtSlot()
    def _doMakeFolder(self):
        """Forward the new folder call to the project tree.
        """
        if self.theItem is not None:
            self.theTree.newTreeItem(nwItemType.FOLDER, None)
        return

    @pyqtSlot()
    def _doToggleExported(self):
        """Flip the isExported flag of the current item.
        """
        if self.theItem is not None:
            self.theItem.setExported(not self.theItem.isExported)
            self.theTree.setTreeItemValues(self.theItem.itemHandle)
        return

    @pyqtSlot()
    def _doDeleteItem(self):
        """Forward the delete item call to the project tree.
        """
        if self.theItem is not None:
            self.theTree.deleteItem()
        return

    @pyqtSlot()
    def _doEmptyTrash(self):
        """Forward the empty trash call to the project tree.
        """
        self.theTree.emptyTrash()
        return

    @pyqtSlot()
    def _doMoveUp(self):
        """Forward the move item call to the project tree.
        """
        self.theTree.moveTreeItem(-1)
        return

    @pyqtSlot()
    def _doMoveDown(self):
        """Forward the move item call to the project tree.
        """
        self.theTree.moveTreeItem(1)
        return

# END Class GuiProjectTreeMenu
