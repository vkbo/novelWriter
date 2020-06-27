# -*- coding: utf-8 -*-
"""novelWriter GUI Document Tree

 novelWriter – GUI Document Tree
=================================
 Class holding the left side document tree view

 File History:
 Created: 2018-09-29 [0.0.1] GuiProjectTree
 Created: 2020-06-04 [0.7.0] GuiProjectTreeMenu

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import nw

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtWidgets import (
    qApp, QTreeWidget, QTreeWidgetItem, QAbstractItemView, QMessageBox,
    QHeaderView, QMenu, QAction
)

from nw.core import NWDoc
from nw.constants import (
    nwLabels, nwItemType, nwItemClass, nwItemLayout, nwAlert, nwUnicode
)

logger = logging.getLogger(__name__)

class GuiProjectTree(QTreeWidget):

    C_NAME   = 0
    C_COUNT  = 1
    C_EXPORT = 2
    C_FLAGS  = 3

    def __init__(self, theParent):
        QTreeWidget.__init__(self, theParent)

        logger.debug("Initialising GuiProjectTree ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theParent.theProject

        # Tree Settings
        self.theMap      = None
        self.orphRoot    = None
        self.treeChanged = False

        self.ctxMenu = GuiProjectTreeMenu(self)
        self.clearTree()

        # Build GUI
        iPx = self.theTheme.baseIconSize
        self.setIconSize(QSize(iPx, iPx))
        self.setExpandsOnDoubleClick(True)
        self.setIndentation(iPx)
        self.setColumnCount(4)
        self.setHeaderLabels(["Label", "Words", "Inc", "Flags"])
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._rightClickMenu)

        treeHeadItem = self.headerItem()
        treeHeadItem.setTextAlignment(self.C_COUNT, Qt.AlignRight)
        treeHeadItem.setToolTip(self.C_NAME, "Item label")
        treeHeadItem.setToolTip(self.C_COUNT, "Word count")
        treeHeadItem.setToolTip(self.C_EXPORT, "Include in build")
        treeHeadItem.setToolTip(self.C_FLAGS, "Status, class, and layout flags")

        # Let the last column stretch, and set the minimum size to the
        # size of the icon as the default Qt font metrics approach fails
        # for some fonts like the Ubuntu font.
        treeHeader = self.header()
        treeHeader.setStretchLastSection(True)
        treeHeader.setMinimumSectionSize(iPx+6)

        # Allow Move by Drag & Drop
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        # But don't allow drop on root level
        trRoot = self.invisibleRootItem()
        trRoot.setFlags(trRoot.flags() ^ Qt.ItemIsDropEnabled)

        # Set Multiple Selection by CTRL
        # Disabled for now, until the merge files option has been added
        # self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Get user's column width preferences for NAME and COUNT
        treeColWidth = self.mainConf.getTreeColWidths()
        if len(treeColWidth) <= 4:
            for colN, colW in enumerate(treeColWidth):
                self.setColumnWidth(colN, colW)

        # The last column should just auto-scale
        self.resizeColumnToContents(self.C_FLAGS)

        logger.debug("GuiProjectTree initialisation complete")

        # Internal Mapping
        self.makeAlert = self.theParent.makeAlert

        return

    ##
    #  Class Methods
    ##

    def clearTree(self):
        """Clear the GUI content and the related maps.
        """
        self.clear()
        self.theMap = {}
        self.orphRoot = None
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
            return False

        if itemClass is None and pHandle is not None:
            pItem = self.theProject.projTree[pHandle]
            if pItem is not None:
                itemClass = pItem.itemClass

        if itemClass is None:
            if itemType is not None:
                if itemType == nwItemType.FILE:
                    self.makeAlert(
                        "Please select a valid location in the tree to add a document.",
                        nwAlert.ERROR
                    )
                    return False
                elif itemType == nwItemType.FOLDER:
                    self.makeAlert(
                        "Please select a valid location in the tree to add a folder.",
                        nwAlert.ERROR
                    )
                    return False
            self.makeAlert("Failed to add new item.", nwAlert.BUG)
            return False

        logger.verbose("Adding new item of type %s and class %s to handle %s" % (
            itemType.name, itemClass.name, str(pHandle))
        )

        if itemType == nwItemType.ROOT:
            tHandle = self.theProject.newRoot(nwLabels.CLASS_NAME[itemClass], itemClass)

        else:
            # If no parent has been selected, make the new file under
            # the root NOVEL item.
            if pHandle is None:
                pHandle = self.theProject.projTree.findRoot(nwItemClass.NOVEL)

            # If still nothing, give up
            if pHandle is None:
                logger.error("Did not find anywhere to add the item!")
                return False

            # Now check if the selected item is a file, in which case
            # the new file will be a sibling
            pItem = self.theProject.projTree[pHandle]
            if pItem.itemType == nwItemType.FILE:
                nHandle = pHandle
                pHandle = pItem.parHandle

            # If we again has no home, give up
            if pHandle is None:
                self.makeAlert(
                    "Did not find anywhere to add the file or folder!", nwAlert.ERROR
                )
                return False

            if pHandle == self.theProject.projTree.trashRoot():
                self.makeAlert(
                    "Cannot add new files or folders to the trash folder.", nwAlert.ERROR
                )
                return False

            # If we're still here, add the file or folder
            if itemType == nwItemType.FILE:
                tHandle = self.theProject.newFile("New File", itemClass, pHandle)
            elif itemType == nwItemType.FOLDER:
                tHandle = self.theProject.newFolder("New Folder", itemClass, pHandle)
            else:
                logger.error("Failed to add new item")
                return False

        # Add the new item to the tree
        self.revealTreeItem(tHandle, nHandle)
        self.theParent.editItem()

        return True

    def revealTreeItem(self, tHandle, nHandle=None):
        """Reveal a newly added project item in the project tree.
        """
        nwItem = self.theProject.projTree[tHandle]
        trItem = self._addTreeItem(nwItem, nHandle)
        pHandle = nwItem.parHandle
        if pHandle is not None and pHandle in self.theMap:
            self.theMap[pHandle].setExpanded(True)
        self.clearSelection()
        trItem.setSelected(True)
        return True

    def moveTreeItem(self, nStep):
        """Move an item up or down in the tree, but only if the treeView
        has focus. This also applies when the menu is used.
        """
        if qApp.focusWidget() == self and self.theParent.hasProject:
            tHandle = self.getSelectedHandle()
            tItem = self._getTreeItem(tHandle)
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
            self.clearSelection()
            cItem.setSelected(True)
            self._setTreeChanged(True)
        else:
            return False
        return True

    def saveTreeOrder(self):
        """Build a list of the items in the project tree and send them
        to the project class. This syncs up the two versions of the
        project structure, and must be called before any code that
        depends on this order to be up to date.
        """
        theList = []
        for i in range(self.topLevelItemCount()):
            if self.topLevelItem(i) == self.orphRoot:
                continue
            theList = self._scanChildren(theList, self.topLevelItem(i), i)
        logger.debug("Saving project tree item order")
        self.theProject.setTreeOrder(theList)
        return True

    def flushTreeOrder(self):
        """Calls saveTreeOrder if there are unsaved changes, otherwise
        does nothing.
        """
        if self.treeChanged:
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
        trashHandle = self.theProject.projTree.trashRoot()

        logger.debug("Emptying Trash folder")
        if trashHandle is None:
            self.makeAlert("There is no Trash folder.", nwAlert.INFO)
            return False

        theTrash = self.getTreeFromHandle(trashHandle)
        if trashHandle in theTrash:
            theTrash.remove(trashHandle)

        nTrash = len(theTrash)
        if nTrash == 0:
            self.makeAlert("The Trash folder is empty.", nwAlert.INFO)
            return False

        msgBox = QMessageBox()
        msgRes = msgBox.question(
            self, "Empty Trash", "Permanently delete %d file%s from Trash?" % (
                nTrash, "s"*int(nTrash > 1)
            )
        )
        if msgRes != QMessageBox.Yes:
            return False

        logger.verbose("Deleting %d files from Trash" % nTrash)
        for tHandle in self.getTreeFromHandle(trashHandle):
            if tHandle == trashHandle:
                continue
            self.deleteItem(tHandle, True)

        if nTrash > 0:
            self._setTreeChanged(True)

        return True

    def deleteItem(self, tHandle=None, alreadyAsked=False, askForTrash=False):
        """Delete items from the tree. Note that this does not delete
        the item from the item tree in the project object. However,
        since this is only meta data, there isn't really a need to do
        that to save memory. Items not in the tree are not saved to the
        project file, so a loaded project will be clean anyway.
        """
        if tHandle is None:
            tHandle = self.getSelectedHandle()

        if tHandle is None:
            return False

        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.projTree[tHandle]

        if nwItemS is None:
            return False

        wCount = int(trItemS.text(self.C_COUNT))
        if nwItemS.itemType == nwItemType.FILE:
            logger.debug("User requested file %s moved to trash" % tHandle)
            trItemP = trItemS.parent()
            trItemT = self._addTrashRoot()
            if trItemP is None or trItemT is None:
                logger.error("Could not delete item")
                return False

            pHandle = nwItemS.parHandle
            if pHandle is not None and pHandle == self.theProject.projTree.trashRoot():
                # If the file is in the trash folder already, as the
                # user if they want to permanently delete the file.
                doPermanent = False
                if self.mainConf.showGUI and not alreadyAsked:
                    msgBox = QMessageBox()
                    msgRes = msgBox.question(
                        self, "Delete File", "Permanently delete file '%s'?" % nwItemS.itemName
                    )
                    if msgRes == QMessageBox.Yes:
                        doPermanent = True
                else:
                    doPermanent = True

                if doPermanent:
                    logger.debug("Permanently deleting file with handle %s" % tHandle)

                    self.propagateCount(tHandle, 0)
                    tIndex = trItemP.indexOfChild(trItemS)
                    trItemC = trItemP.takeChild(tIndex)

                    if self.theParent.docEditor.theHandle == tHandle:
                        self.theParent.closeDocument()

                    theDoc = NWDoc(self.theProject, self.theParent)
                    theDoc.deleteDocument(tHandle)
                    del self.theProject.projTree[tHandle]
                    self.theParent.theIndex.deleteHandle(tHandle)

            else:
                # The file is not already in the trash folder, so we
                # move it there.
                doTrash = False
                if self.mainConf.showGUI and askForTrash:
                    msgBox = QMessageBox()
                    msgRes = msgBox.question(
                        self, "Delete File", "Move file '%s' to Trash?" % nwItemS.itemName
                    )
                    if msgRes == QMessageBox.Yes:
                        doTrash = True
                else:
                    doTrash = True

                if doTrash:
                    if pHandle is None:
                        logger.warning("File has no parent item")

                    self.propagateCount(tHandle, 0)
                    tIndex  = trItemP.indexOfChild(trItemS)
                    trItemC = trItemP.takeChild(tIndex)
                    trItemT.addChild(trItemC)
                    nwItemS.setParent(self.theProject.projTree.trashRoot())
                    self.propagateCount(tHandle, wCount)

                    self._setTreeChanged(True)
                    self.theParent.theIndex.deleteHandle(tHandle)

        elif nwItemS.itemType == nwItemType.FOLDER:
            logger.debug("User requested folder %s deleted" % tHandle)
            trItemP = trItemS.parent()
            if trItemP is None:
                logger.error("Could not delete folder")
                return False
            tIndex = trItemP.indexOfChild(trItemS)
            if trItemS.childCount() == 0:
                trItemP.takeChild(tIndex)
                del self.theProject.projTree[tHandle]
            else:
                self.makeAlert("Cannot delete folder. It is not empty.", nwAlert.ERROR)
                return False

        elif nwItemS.itemType == nwItemType.ROOT:
            logger.debug("User requested root folder %s deleted" % tHandle)
            tIndex = self.indexOfTopLevelItem(trItemS)
            if trItemS.childCount() == 0:
                self.takeTopLevelItem(tIndex)
                self.theParent.mainMenu.setAvailableRoot()
                self._setTreeChanged(True)
            else:
                self.makeAlert("Cannot delete root folder. It is not empty.", nwAlert.ERROR)
                return False

        return True

    def setTreeItemValues(self, tHandle):
        """Set the name and flag values for a tree item.
        """
        trItem  = self._getTreeItem(tHandle)
        nwItem  = self.theProject.projTree[tHandle]
        tName   = nwItem.itemName
        tClass  = nwItem.itemClass
        tHandle = nwItem.itemHandle
        pHandle = nwItem.parHandle

        expIcon = QIcon()

        stClass = nwLabels.CLASS_FLAG[nwItem.itemClass]
        stLayout = ""
        if nwItem.itemType == nwItemType.FILE:
            stLayout = "."+nwLabels.LAYOUT_FLAG[nwItem.itemLayout]
            if nwItem.isExported:
                expIcon = self.theTheme.getIcon("check")
            else:
                expIcon = self.theTheme.getIcon("cross")
        tStatus = stClass+stLayout

        iStatus = nwItem.itemStatus
        if tClass == nwItemClass.NOVEL:
            iStatus = self.theProject.statusItems.checkEntry(iStatus) # Make sure it's valid
            flagIcon = self.theParent.statusIcons[iStatus]
        else:
            iStatus = self.theProject.importItems.checkEntry(iStatus) # Make sure it's valid
            flagIcon = self.theParent.importIcons[iStatus]

        trItem.setText(self.C_NAME, tName)
        trItem.setIcon(self.C_EXPORT, expIcon)
        trItem.setText(self.C_FLAGS, tStatus)
        trItem.setIcon(self.C_FLAGS, flagIcon)

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
        if tItem is not None:
            tItem.setText(self.C_COUNT, str(theCount))
            pItem = tItem.parent()
            if pItem is not None:
                pCount = 0
                for i in range(pItem.childCount()):
                    pCount += int(pItem.child(i).text(self.C_COUNT))
                    pHandle = pItem.data(self.C_NAME, Qt.UserRole)
                if not nDepth > 200 and pHandle != "":
                    self.propagateCount(pHandle, pCount, nDepth+1)
        return

    def projectWordCount(self):
        """Sum up the word counts for all root items and set the
        relevant values in the project and on the status bar. This call
        is a fast way of getting this number, and depends on the
        propagateCount function being called when it should to maintain
        the correct count. Orphan folder is not included in the total.
        """
        nWords = 0
        for n in range(self.topLevelItemCount()):
            tItem = self.topLevelItem(n)
            if tItem == self.orphRoot:
                continue
            nWords += int(tItem.text(self.C_COUNT))
        self.theProject.setProjectWordCount(nWords)
        sWords = self.theProject.getSessionWordCount()
        self.theParent.statusBar.setStats(nWords,sWords)
        return

    def buildTree(self):
        """Build the entire project tree from scratch. This depends on
        the save project item iterator in the project class which will
        always make sure items with a parent have had their parent item
        sent first.
        """
        logger.debug("Building project tree ...")
        self.clear()
        iCount = 0
        for nwItem in self.theProject.getProjectItems():
            iCount += 1
            self._addTreeItem(nwItem)
        logger.debug("%d items added to project tree" % iCount)
        return True

    def getSelectedHandle(self):
        """Get the currently selected handle. If multiple items are
        selected, return the first.
        """
        selItem = self.selectedItems()
        if len(selItem) == 0:
            return None
        if isinstance(selItem[0], QTreeWidgetItem):
            return selItem[0].data(self.C_NAME, Qt.UserRole)
        return None

    def getSelectedHandles(self):
        """Return a list of all currently selected item handles.
        """
        selItems = self.selectedItems()
        selHandles = []
        for n in range(len(selItems)):
            if isinstance(selItems[n], QTreeWidgetItem):
                selHandles.append(selItems[n].data(self.C_NAME, Qt.UserRole))
        return selHandles

    def setSelectedHandle(self, tHandle, doScroll=False):
        """Set a specific handle as the selected item.
        """
        if tHandle in self.theMap:
            self.clearSelection()
            self.theMap[tHandle].setSelected(True)
            selItems = self.selectedIndexes()
            if selItems and doScroll:
                self.scrollTo(
                    selItems[0], QAbstractItemView.PositionAtCenter
                )
            return True
        return False

    ##
    #  Slots
    ##

    def _rightClickMenu(self, clickPos):
        """The user right clicked an element in the project tree, so we
        open a context menu in-place.
        """
        selItem = self.itemAt(clickPos)
        if isinstance(selItem, QTreeWidgetItem):
            tHandle = selItem.data(self.C_NAME, Qt.UserRole)
            tItem   = self.theProject.projTree[tHandle]
            self.setSelectedHandle(tHandle) # Just to be safe
            if self.ctxMenu.filterActions(tItem):
                # Only open menu if any actions remain after filter
                self.ctxMenu.exec_(self.viewport().mapToGlobal(clickPos))
        return

    ##
    #  Events
    ##

    def mousePressEvent(self, theEvent):
        """Overload mousePressEvent to clear selection if clicking the
        mouse in a blank area of the tree view.
        """
        QTreeWidget.mousePressEvent(self, theEvent)
        selItem = self.indexAt(theEvent.pos())
        if not selItem.isValid():
            self.clearSelection()
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
            self.makeAlert("The item cannot be moved to that location.", nwAlert.ERROR)
            return

        wCount = int(sItem.text(self.C_COUNT))
        isSame = snItem.itemClass == dnItem.itemClass
        isNone = snItem.itemClass == nwItemClass.NO_CLASS
        isNote = snItem.itemLayout == nwItemLayout.NOTE
        onFile = dnItem.itemType == nwItemType.FILE
        isRoot = snItem.itemType == nwItemType.ROOT
        onRoot = dnItem.itemType == nwItemType.ROOT
        isOnTop = self.dropIndicatorPosition() == QAbstractItemView.OnItem
        if (isSame or isNone or isNote) and not (onFile and isOnTop) and not isRoot:
            logger.debug("Drag'n'drop of item %s accepted" % sHandle)
            self.propagateCount(sHandle, 0)
            QTreeWidget.dropEvent(self, theEvent)
            if isNone:
                self._moveOrphanedItem(sHandle, dHandle)
                self._cleanOrphanedRoot()
            else:
                self._updateItemParent(sHandle)
            if not isSame:
                logger.debug("Item %s class has been changed from %s to %s" % (
                    sHandle,
                    snItem.itemClass.name,
                    dnItem.itemClass.name
                ))
                snItem.setClass(dnItem.itemClass)
                self.setTreeItemValues(sHandle)
            self.propagateCount(sHandle, wCount)
        else:
            logger.debug("Drag'n'drop of item %s not accepted" % sHandle)
            self.makeAlert("The item cannot be moved to that location.", nwAlert.ERROR)

        return

    ##
    #  Internal Functions
    ##

    def _getTreeItem(self, tHandle):
        """Returns the QTreeWidgetItem of a given item handle.
        """
        if tHandle in self.theMap.keys():
            return self.theMap[tHandle]
        return None

    def _scanChildren(self, theList, theItem, theIndex):
        """This is a recursive function returning all items in a tree
        starting at a given QTreeWidgetItem.
        """
        tHandle = theItem.data(self.C_NAME, Qt.UserRole)
        nwItem = self.theProject.projTree[tHandle]
        nwItem.setExpanded(theItem.isExpanded())
        nwItem.setOrder(theIndex)
        theList.append(tHandle)
        for i in range(theItem.childCount()):
            self._scanChildren(theList, theItem.child(i), i)
        return theList

    def _addTreeItem(self, nwItem, nHandle=None):
        """Create a QTreeWidgetItem from an NWItem and add it to the
        project tree.
        """
        tHandle = nwItem.itemHandle
        pHandle = nwItem.parHandle
        tClass  = nwItem.itemClass
        newItem = QTreeWidgetItem([""]*4)

        newItem.setText(self.C_NAME,   "")
        newItem.setText(self.C_COUNT,  "0")
        newItem.setText(self.C_EXPORT, "")
        newItem.setText(self.C_FLAGS,  "")

        newItem.setTextAlignment(self.C_NAME,   Qt.AlignLeft  | Qt.AlignVCenter)
        newItem.setTextAlignment(self.C_COUNT,  Qt.AlignRight | Qt.AlignVCenter)
        newItem.setTextAlignment(self.C_EXPORT, Qt.AlignLeft  | Qt.AlignVCenter)
        newItem.setTextAlignment(self.C_FLAGS,  Qt.AlignLeft  | Qt.AlignVCenter)

        newItem.setData(self.C_NAME, Qt.UserRole, tHandle)

        self.theMap[tHandle] = newItem
        if pHandle is None:
            if nwItem.itemType == nwItemType.ROOT:
                self.addTopLevelItem(newItem)
                self.theParent.mainMenu.setAvailableRoot()
            elif nwItem.itemType == nwItemType.TRASH:
                self.addTopLevelItem(newItem)
            else:
                self._addOrphanedRoot()
                self.orphRoot.addChild(newItem)
        else:
            byIndex = -1
            if nHandle is not None and nHandle in self.theMap:
                try:
                    byIndex = self.theMap[pHandle].indexOfChild(self.theMap[nHandle])
                except:
                    logger.error("Failed to get index of item with handle %s" % nHandle)
            if byIndex >= 0: 
                self.theMap[pHandle].insertChild(byIndex+1, newItem)
            else:
                self.theMap[pHandle].addChild(newItem)
            self.propagateCount(tHandle, nwItem.wordCount)

        self.setTreeItemValues(tHandle)
        newItem.setExpanded(nwItem.isExpanded)

        if nwItem.itemType == nwItemType.ROOT:
            newItem.setIcon(self.C_NAME, self.theTheme.getIcon(nwLabels.CLASS_ICON[tClass]))
        elif nwItem.itemType == nwItemType.FOLDER:
            newItem.setIcon(self.C_NAME, self.theTheme.getIcon("proj_folder"))
        elif nwItem.itemType == nwItemType.FILE:
            newItem.setIcon(self.C_NAME, self.theTheme.getIcon("proj_document"))
        elif nwItem.itemType == nwItemType.TRASH:
            newItem.setIcon(self.C_NAME, self.theTheme.getIcon(nwLabels.CLASS_ICON[tClass]))

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
            trItem.setExpanded(True)
            self._setTreeChanged(True)
        return trItem

    def _addOrphanedRoot(self):
        """Add the special Orphaned Files root item to hold non-root
        items with no parent set.
        """
        if self.orphRoot is None:
            newItem = QTreeWidgetItem([""]*4)
            newItem.setText(self.C_NAME,   "Orphaned Files")
            newItem.setText(self.C_COUNT,  "")
            newItem.setText(self.C_EXPORT, "")
            newItem.setText(self.C_FLAGS,  "")
            self.addTopLevelItem(newItem)
            self.orphRoot = newItem
            newItem.setExpanded(True)
            newItem.setData(self.C_NAME, Qt.UserRole, "")
            newItem.setIcon(self.C_NAME, self.theTheme.getIcon("proj_orphan"))
        return

    def _cleanOrphanedRoot(self):
        """Remove the special Orphaned Files root folder if it is empty.
        """
        if self.orphRoot is not None:
            if self.orphRoot.childCount() == 0:
                self.takeTopLevelItem(self.indexOfTopLevelItem(self.orphRoot))
                self.orphRoot = None
        return

    def _updateItemParent(self, tHandle):
        """Update the parent handle of an item so that the information
        in the project is consistent with the treeView.
        """
        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.projTree[tHandle]
        trItemP = trItemS.parent()
        if trItemP is None:
            logger.error("Failed to find new parent item of %s" % tHandle)
            return False

        pHandle = trItemP.data(self.C_NAME, Qt.UserRole)
        nwItemS.setParent(pHandle)
        self.setTreeItemValues(tHandle)
        self._setTreeChanged(True)

        logger.debug("The parent of item %s has been changed to %s" % (tHandle,pHandle))

        return True

    def _moveOrphanedItem(self, tHandle, dHandle):
        """Move an Orphaned Item to a new dHandle parent item. This
        function will set all the missing meta data based on the meta
        data of the destination item.
        """
        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.projTree[tHandle]
        nwItemD = self.theProject.projTree[dHandle]
        trItemP = trItemS.parent()
        nwItemS.setClass(nwItemD.itemClass)
        if trItemP is None:
            logger.error("Failed to find new parent item of %s" % tHandle)
            return
        pHandle = trItemP.data(self.C_NAME, Qt.UserRole)
        nwItemS.setParent(pHandle)
        self.setTreeItemValues(tHandle)
        self._setTreeChanged(True)
        return

    def _setTreeChanged(self, theState):
        """Set the tree change flag, and propagate to the project.
        """
        self.treeChanged = theState
        if theState:
            self.theProject.setProjectChanged(True)
        return

# END Class GuiProjectTree

class GuiProjectTreeMenu(QMenu):

    def __init__(self, theTree):
        QMenu.__init__(self, theTree)

        self.theTree = theTree
        self.theItem = None

        self.openItem = QAction("Open Document", self)
        self.openItem.triggered.connect(self._doOpenItem)
        self.addAction(self.openItem)

        self.viewItem = QAction("View Document", self)
        self.viewItem.triggered.connect(self._doViewItem)
        self.addAction(self.viewItem)

        self.editItem = QAction("Edit Project Item", self)
        self.editItem.triggered.connect(self._doEditItem)
        self.addAction(self.editItem)

        self.toggleExp = QAction("Toggle Included Flag", self)
        self.toggleExp.triggered.connect(self._doToggleExported)
        self.addAction(self.toggleExp)

        self.newFile = QAction("New File", self)
        self.newFile.triggered.connect(self._doMakeFile)
        self.addAction(self.newFile)

        self.newFolder = QAction("New Folder", self)
        self.newFolder.triggered.connect(self._doMakeFolder)
        self.addAction(self.newFolder)

        self.deleteItem = QAction("Delete Item", self)
        self.deleteItem.triggered.connect(self._doDeleteItem)
        self.addAction(self.deleteItem)

        self.emptyTrash = QAction("Empty Trash", self)
        self.emptyTrash.triggered.connect(self._doEmptyTrash)
        self.addAction(self.emptyTrash)

        return

    def filterActions(self, theItem):
        """Update item settings from the nwItem.
        """
        self.theItem = theItem
        trashHandle = self.theTree.theProject.projTree.trashRoot()

        if theItem is None:
            return False

        inTrash = theItem.parHandle == trashHandle
        isTrash = theItem.itemHandle == trashHandle
        isFile  = theItem.itemType == nwItemType.FILE
        isOrph  = isFile and theItem.parHandle is None

        showOpen      = isFile
        showView      = isFile
        showEdit      = not isTrash and not isOrph
        showExport    = isFile and not inTrash and not isOrph
        showNewFile   = not isTrash and not inTrash and not isOrph
        showNewFolder = not isTrash and not inTrash and not isOrph
        showDelete    = not isTrash
        showEmpty     = isTrash

        self.openItem.setVisible(showOpen)
        self.viewItem.setVisible(showView)
        self.editItem.setVisible(showEdit)
        self.toggleExp.setVisible(showExport)
        self.newFile.setVisible(showNewFile)
        self.newFolder.setVisible(showNewFolder)
        self.deleteItem.setVisible(showDelete)
        self.emptyTrash.setVisible(showEmpty)

        return True

    ##
    #  Slots
    ##

    def _doOpenItem(self):
        """Forward the open document call to the main GUI window.
        """
        if self.theItem is not None:
            self.theTree.theParent.openDocument(self.theItem.itemHandle, doScroll=False)
        return

    def _doViewItem(self):
        """Forward the view document call to the main GUI window.
        """
        if self.theItem is not None:
            self.theTree.theParent.viewDocument(self.theItem.itemHandle)
        return

    def _doEditItem(self):
        """Forward the edit item call to the main GUI window.
        """
        if self.theItem is not None:
            self.theTree.theParent.editItem()
        return

    def _doMakeFile(self):
        """Forward the new file call to the project tree.
        """
        if self.theItem is not None:
            self.theTree.newTreeItem(nwItemType.FILE, None)
        return

    def _doMakeFolder(self):
        """Forward the new folder call to the project tree.
        """
        if self.theItem is not None:
            self.theTree.newTreeItem(nwItemType.FOLDER, None)
        return

    def _doToggleExported(self):
        """Flip the isExported flag of the current item.
        """
        if self.theItem is not None:
            self.theItem.setExported(not self.theItem.isExported)
            self.theTree.setTreeItemValues(self.theItem.itemHandle)
        return

    def _doDeleteItem(self):
        """Forward the delete item call to the project tree.
        """
        if self.theItem is not None:
            self.theTree.deleteItem(askForTrash=True)
        return

    def _doEmptyTrash(self):
        """Forward the delete item call to the project tree.
        """
        self.theTree.emptyTrash()
        return

# END Class GuiProjectTreeMenu
