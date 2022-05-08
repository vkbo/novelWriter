"""
novelWriter – GUI Project Tree
==============================
GUI classes for the main window project tree

File History:
Created: 2018-09-29 [0.0.1] GuiProjectTree
Created: 2020-06-04 [0.7]   GuiProjectTreeMenu

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import logging
import novelwriter

from time import time

from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QAbstractItemView, QMenu, QAction
)

from novelwriter.core import NWDoc
from novelwriter.enum import nwItemType, nwItemClass, nwItemLayout, nwAlert
from novelwriter.constants import trConst, nwLabels

logger = logging.getLogger(__name__)


class GuiProjectTree(QTreeWidget):

    C_NAME   = 0
    C_COUNT  = 1
    C_EXPORT = 2
    C_STATUS = 3

    novelItemChanged = pyqtSignal()
    noteItemChanged = pyqtSignal()
    wordCountsChanged = pyqtSignal()

    def __init__(self, theParent):
        QTreeWidget.__init__(self, theParent)

        logger.debug("Initialising GuiProjectTree ...")

        self.mainConf   = novelwriter.CONFIG
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
        self.setExpandsOnDoubleClick(False)
        self.setIndentation(iPx)
        self.setColumnCount(4)
        self.setHeaderLabels([
            self.tr("Project Tree"), self.tr("Words"), "", ""
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

    def newTreeItem(self, itemType, itemClass=None):
        """Add new item to the tree, with a given itemType (and
        itemClass if Root), and attach it to the selected handle. Also make
        sure the item is added in a place it can be added, and that other
        meta data is set correctly to ensure a valid project tree.
        """
        if not self.theParent.hasProject:
            logger.error("No project open")
            return False

        nHandle = None
        tHandle = None

        if itemType == nwItemType.ROOT and isinstance(itemClass, nwItemClass):

            tHandle = self.theProject.newRoot(
                trConst(nwLabels.CLASS_NAME[itemClass]), itemClass
            )

        elif itemType in (nwItemType.FILE, nwItemType.FOLDER):

            sHandle = self.getSelectedHandle()
            if sHandle is None or sHandle not in self.theProject.projTree:
                self.theParent.makeAlert(self.tr(
                    "Did not find anywhere to add the file or folder!"
                ), nwAlert.ERROR)
                return False

            # If the selected item is a file, the new item will be a sibling
            pItem = self.theProject.projTree[sHandle]
            if pItem.itemType == nwItemType.FILE:
                nHandle = sHandle
                sHandle = pItem.itemParent
                if sHandle is None:
                    logger.error("Internal error")  # Bug
                    return False

            if self.theProject.projTree.isTrash(sHandle):
                self.theParent.makeAlert(self.tr(
                    "Cannot add new files or folders to the Trash folder."
                ), nwAlert.ERROR)
                return False

            # Add the file or folder
            if itemType == nwItemType.FILE:
                if pItem.isNovelLike():
                    tHandle = self.theProject.newFile(self.tr("New Document"), sHandle)
                else:
                    tHandle = self.theProject.newFile(self.tr("New Note"), sHandle)
            elif itemType == nwItemType.FOLDER:
                tHandle = self.theProject.newFolder(self.tr("New Folder"), sHandle)

        else:
            logger.error("Failed to add new item")
            return False

        # If there is no handle set, return here. This is a bug
        if tHandle is None:  # pragma: no cover
            return True

        # Add the new item to the tree
        self.revealNewTreeItem(tHandle, nHandle)
        self.theParent.editItem(tHandle)
        nwItem = self.theProject.projTree[tHandle]

        # If this is a folder, return here
        if nwItem.itemType != nwItemType.FILE:
            return True

        # This is a new file, so let's add some content
        newDoc = NWDoc(self.theProject, tHandle)
        if not newDoc.readDocument():
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
            self.wordCountsChanged.emit()

        return True

    def revealNewTreeItem(self, tHandle, nHandle=None):
        """Reveal a newly added project item in the project tree.
        """
        nwItem = self.theProject.projTree[tHandle]
        if nwItem is None:
            return False

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

    def toggleExpanded(self, tHandle):
        """Expand an item based on its handle.
        """
        trItem = self._getTreeItem(tHandle)
        if trItem is not None:
            trItem.setExpanded(not trItem.isExpanded())
        return

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
            self.theParent.makeAlert(self.tr(
                "There is currently no Trash folder in this project."
            ), nwAlert.INFO)
            return False

        theTrash = self.getTreeFromHandle(trashHandle)
        if trashHandle in theTrash:
            theTrash.remove(trashHandle)

        nTrash = len(theTrash)
        if nTrash == 0:
            self.theParent.makeAlert(self.tr(
                "The Trash folder is already empty."
            ), nwAlert.INFO)
            return False

        msgYes = self.theParent.askQuestion(
            self.tr("Empty Trash"),
            self.tr("Permanently delete {0} file(s) from Trash?").format(nTrash)
        )
        if not msgYes:
            return False

        logger.verbose("Deleting %d file(s) from Trash", nTrash)
        for tHandle in reversed(self.getTreeFromHandle(trashHandle)):
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
        delete the files on disk. Root folders are deleted if they're empty
        only, and the deletion is always permanent.
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

        wCount = self._getItemWordCount(tHandle)
        if nwItemS.itemType == nwItemType.ROOT:
            # Only an empty ROOT folder can be deleted
            logger.debug("User requested a root folder '%s' deleted", tHandle)
            tIndex = self.indexOfTopLevelItem(trItemS)
            if trItemS.childCount() == 0:
                self.takeTopLevelItem(tIndex)
                self._deleteTreeItem(tHandle)
                self._setTreeChanged(True)
            else:
                self.theParent.makeAlert(self.tr(
                    "Cannot delete root folder. It is not empty. "
                    "Recursive deletion is not supported. "
                    "Please delete the content first."
                ), nwAlert.ERROR)
                return False

        elif nwItemS.itemType == nwItemType.FOLDER and trItemS.childCount() == 0:
            # An empty FOLDER is just deleted without any further checks
            logger.debug("User requested an empty folder '%s' deleted", tHandle)
            trItemP = trItemS.parent()
            tIndex = trItemP.indexOfChild(trItemS)
            trItemP.takeChild(tIndex)
            self._deleteTreeItem(tHandle)
            self._setTreeChanged(True)

        else:
            # A populated FOLDER or a FILE requires confirmtation
            logger.debug("User requested a file or folder '%s' deleted", tHandle)
            trItemP = trItemS.parent()
            trItemT = self._addTrashRoot()
            if trItemP is None or trItemT is None:
                logger.error("Could not delete item")
                return False

            if self.theProject.projTree.isTrash(tHandle):
                # If the file is in the trash folder already, as the
                # user if they want to permanently delete the file.
                doPermanent = False
                if not alreadyAsked:
                    msgYes = self.theParent.askQuestion(
                        self.tr("Delete"),
                        self.tr("Permanently delete '{0}'?").format(nwItemS.itemName)
                    )
                    if msgYes:
                        doPermanent = True
                else:
                    doPermanent = True

                if doPermanent:
                    logger.debug("Permanently deleting item with handle '%s'", tHandle)

                    self.propagateCount(tHandle, 0)
                    tIndex = trItemP.indexOfChild(trItemS)
                    trItemC = trItemP.takeChild(tIndex)
                    for dHandle in reversed(self.getTreeFromHandle(tHandle)):
                        if self.theParent.docEditor.docHandle() == dHandle:
                            self.theParent.closeDocument()
                        self._deleteTreeItem(dHandle)

                    self._setTreeChanged(True)
                    self.wordCountsChanged.emit()

            else:
                # The item is not already in the trash folder, so we
                # move it there.
                msgYes = self.theParent.askQuestion(
                    self.tr("Delete"),
                    self.tr("Move '{0}' to Trash?").format(nwItemS.itemName),
                )
                if msgYes:
                    logger.debug("Moving item '%s' to trash", tHandle)

                    self.propagateCount(tHandle, 0)
                    tIndex = trItemP.indexOfChild(trItemS)
                    trItemC = trItemP.takeChild(tIndex)
                    trItemT.addChild(trItemC)
                    self._postItemMove(tHandle, wCount)
                    self._recordLastMove(trItemS, trItemP, tIndex)
                    self._setTreeChanged(True)

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

        itempStatus, statusIcon = nwItem.getImportStatus()
        hLevel = self.theIndex.getHandleHeaderLevel(tHandle)
        itemIcon = self.theTheme.getItemIcon(
            nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, hLevel
        )

        trItem.setIcon(self.C_NAME, itemIcon)
        trItem.setText(self.C_NAME, nwItem.itemName)
        trItem.setIcon(self.C_EXPORT, expIcon)
        trItem.setIcon(self.C_STATUS, statusIcon)
        trItem.setToolTip(self.C_STATUS, itempStatus)

        if self.mainConf.emphLabels and nwItem.itemLayout == nwItemLayout.DOCUMENT:
            trFont = trItem.font(self.C_NAME)
            if hLevel in ("H1", "H2"):
                trFont.setBold(True)
                trFont.setUnderline(True)
            else:
                trFont.setBold(False)
                trFont.setUnderline(False)
            trItem.setFont(self.C_NAME, trFont)

        return

    def propagateCount(self, tHandle, newCount, countChildren=False):
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

        if countChildren:
            for i in range(tItem.childCount()):
                newCount += int(tItem.child(i).data(self.C_COUNT, Qt.UserRole))

        tItem.setText(self.C_COUNT, f"{newCount:n}")
        tItem.setData(self.C_COUNT, Qt.UserRole, int(newCount))

        pItem = tItem.parent()
        if pItem is None:
            return

        pCount = 0
        pHandle = None
        for i in range(pItem.childCount()):
            pCount += int(pItem.child(i).data(self.C_COUNT, Qt.UserRole))
            pHandle = pItem.data(self.C_NAME, Qt.UserRole)

        if pHandle:
            if self.theProject.projTree.checkType(pHandle, nwItemType.FILE):
                # A file has an internal word count we need to account
                # for, but a folder always has 0 words on its own.
                pCount += self.theIndex.getCounts(pHandle)[1]

            self.propagateCount(pHandle, pCount, countChildren=False)

        return

    def buildTree(self):
        """Build the entire project tree from scratch. This depends on
        the save project item iterator in the project class which will
        always make sure items with a parent have had their parent item
        sent first.
        """
        logger.debug("Building the project tree ...")
        self.clearTree()

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
        sHandle = srcItem.data(self.C_NAME, Qt.UserRole)
        dHandle = dstItem.data(self.C_NAME, Qt.UserRole)
        logger.debug("Moving item '%s' back to '%s', index %d", sHandle, dHandle, dstIndex)

        wCount = self._getItemWordCount(sHandle)
        self.propagateCount(sHandle, 0)
        parItem = srcItem.parent()
        srcIndex = parItem.indexOfChild(srcItem)
        movItem = parItem.takeChild(srcIndex)
        dstItem.insertChild(dstIndex, movItem)

        self._postItemMove(sHandle, wCount)

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
        self.propagateCount(tHandle, wCount, countChildren=True)
        self.wordCountsChanged.emit()
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
        """Overload the drop item event to ensure relevant data has been
        updated.
        """
        sHandle = self.getSelectedHandle()
        if sHandle is None:
            logger.error("Invalid drag and drop event")
            return

        logger.debug("Drag'n'drop of item '%s' accepted", sHandle)

        sItem = self._getTreeItem(sHandle)
        isExpanded = False
        if sItem is not None:
            isExpanded = sItem.isExpanded()

        pItem = sItem.parent()
        pIndex = 0
        if pItem is not None:
            pIndex = pItem.indexOfChild(sItem)

        wCount = self._getItemWordCount(sHandle)
        self.propagateCount(sHandle, 0)

        QTreeWidget.dropEvent(self, theEvent)
        self._postItemMove(sHandle, wCount)
        self._recordLastMove(sItem, pItem, pIndex)
        sItem.setExpanded(isExpanded)

        return

    ##
    #  Internal Functions
    ##

    def _postItemMove(self, tHandle, wCount):
        """Run various maintenance tasks for a moved item.
        """
        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.projTree[tHandle]
        trItemP = trItemS.parent()
        if trItemP is None:
            logger.error("Failed to find new parent item of '%s'", tHandle)
            return False

        # Update item parent handle in the project, make sure meta data
        # is updated accordingly, and update word count
        pHandle = trItemP.data(self.C_NAME, Qt.UserRole)
        nwItemS.setParent(pHandle)
        trItemP.setExpanded(True)
        logger.debug("The parent of item '%s' has been changed to '%s'", tHandle, pHandle)

        mHandles = self.getTreeFromHandle(tHandle)
        logger.debug("A total of %d item(s) were moved", len(mHandles))
        for mHandle in mHandles:
            logger.debug("Updating item '%s'", mHandle)
            self.theProject.projTree.updateItemData(mHandle)

            # Update the index
            if nwItemS.isInactive():
                self.theIndex.deleteHandle(mHandle)
            else:
                self.theIndex.reIndexHandle(mHandle)

            self.setTreeItemValues(mHandle)

        # Trigger dependent updates
        self.propagateCount(tHandle, wCount)
        self._setTreeChanged(True)
        self._emitItemChange(tHandle)

        return True

    def _getItemWordCount(self, tHandle):
        """Retrun the word count of a given item handle.
        """
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return 0
        return int(tItem.data(self.C_COUNT, Qt.UserRole))

    def _getTreeItem(self, tHandle):
        """Return the QTreeWidgetItem of a given item handle.
        """
        return self._treeMap.get(tHandle, None)

    def _deleteTreeItem(self, tHandle):
        """Permanently delete a tree item from the project and the map.
        """
        if self.theProject.projTree.checkType(tHandle, nwItemType.FILE):
            delDoc = NWDoc(self.theProject, tHandle)
            if not delDoc.deleteDocument():
                self.theParent.makeAlert([
                    self.tr("Could not delete document file."), delDoc.getError()
                ], nwAlert.ERROR)
                return False

        self.theIndex.deleteHandle(tHandle)
        del self.theProject.projTree[tHandle]
        self._treeMap.pop(tHandle, None)

        return True

    def _scanChildren(self, theList, tItem, tIndex):
        """This is a recursive function returning all items in a tree
        starting at a given QTreeWidgetItem.
        """
        tHandle = tItem.data(self.C_NAME, Qt.UserRole)
        cCount = tItem.childCount()

        # Update tree-related meta data
        nwItem = self.theProject.projTree[tHandle]
        nwItem.setExpanded(tItem.isExpanded() and cCount > 0)
        nwItem.setOrder(tIndex)

        theList.append(tHandle)
        for i in range(cCount):
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
                newItem.setFlags(newItem.flags() ^ Qt.ItemIsDragEnabled)
                self.addTopLevelItem(newItem)
            else:
                self.theParent.makeAlert(self.tr(
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
            self.propagateCount(tHandle, nwItem.wordCount, countChildren=True)

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
        if self.theProject.projTree.checkType(tHandle, nwItemType.FILE):
            nwItem = self.theProject.projTree[tHandle]
            if nwItem.isNovelLike():
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

        inTrash = self.theTree.theProject.projTree.isTrash(theItem.itemHandle)
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
            self.theTree.newTreeItem(nwItemType.FILE)
        return

    @pyqtSlot()
    def _doMakeFolder(self):
        """Forward the new folder call to the project tree.
        """
        if self.theItem is not None:
            self.theTree.newTreeItem(nwItemType.FOLDER)
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
