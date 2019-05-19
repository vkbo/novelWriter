# -*- coding: utf-8 -*-
"""novelWriter GUI Document Tree

 novelWriter – GUI Document Tree
=================================
 Class holding the left side document tree view

 File History:
 Created: 2018-09-29 [0.0.1]

"""

import logging
import nw

from os              import path
from PyQt5.QtCore    import Qt, QSize
from PyQt5.QtGui     import QIcon, QFont, QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView, QInputDialog, QLineEdit, QApplication

from nw.project.item import NWItem
from nw.enum         import nwItemType, nwItemClass, nwAlert
from nw.constants    import nwLabels

logger = logging.getLogger(__name__)

class GuiDocTree(QTreeWidget):

    C_NAME   = 0
    C_COUNT  = 1
    C_FLAGS  = 2
    C_HANDLE = 3

    def __init__(self, theParent, theProject):
        QTreeWidget.__init__(self, theParent)

        logger.debug("Initialising DocTree ...")
        self.mainConf   = nw.CONFIG
        self.debugGUI   = self.mainConf.debugGUI
        self.theParent  = theParent
        self.theProject = theProject

        # Tree Settings
        self.theMap     = None
        self.orphRoot   = None

        self.clearTree()

        # Build GUI
        self.setIconSize(QSize(13,13))
        self.setExpandsOnDoubleClick(True)
        self.setIndentation(13)
        self.setColumnCount(4)
        self.setHeaderLabels(["Name","Count","Flags","Handle"])
        if not self.debugGUI:
            self.hideColumn(self.C_HANDLE)

        treeHead = self.headerItem()
        treeHead.setTextAlignment(self.C_COUNT,Qt.AlignRight)

        # Allow Move by Drag & Drop
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        # Set Multiple Selection by CTRL
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        for colN in range(len(self.mainConf.treeColWidth)):
            self.setColumnWidth(colN,self.mainConf.treeColWidth[colN])

        self.fontFlags = QFont("Monospace",10)
        self.fontCount = QFont("Monospace",10)

        logger.debug("DocTree initialisation complete")

        # Internal Mapping
        self.makeAlert = self.theParent.makeAlert

        return

    ##
    #  Class Methods
    ##

    def clearTree(self):
        self.clear()
        self.theMap   = {}
        self.orphRoot = None
        return

    def newTreeItem(self, itemType, itemClass):

        pHandle = self.getSelectedHandle()

        if itemClass is None and pHandle is not None:
            itemClass = self.theProject.getItem(pHandle).itemClass
        if itemClass is None:
            self.makeAlert("Failed to find an appropriate item class for item %s" % pHandle, nwAlert.BUG)
            return False

        logger.verbose("Adding new item of type %s and class %s to handle %s" % (
            itemType.name, itemClass.name, str(pHandle))
        )

        if itemType == nwItemType.ROOT:
            tHandle = self.theProject.newRoot(nwLabels.CLASS_NAME[itemClass], itemClass)

        else:
            # If no parent has been selected, make the new file under the root NOVEL item.
            if pHandle is None:
                pHandle = self.theProject.findRootItem(nwItemClass.NOVEL)

            # If still nothing, give up
            if pHandle is None:
                logger.error("Did not find anywhere to add the item!")
                return False

            # Now check if the selected item is a file, in which case the new file will be a sibling
            pItem = self.theProject.getItem(pHandle)
            if pItem.itemType == nwItemType.FILE:
                pHandle = pItem.parHandle

            # If we again has no home, give up
            if pHandle is None:
                logger.error("Did not find anywhere to add the item!")
                return False

            # If we're still here, add the file
            if itemType == nwItemType.FILE:
                tHandle = self.theProject.newFile("New File", itemClass, pHandle)
            elif itemType == nwItemType.FOLDER:
                tHandle = self.theProject.newFolder("New Folder", itemClass, pHandle)
            else:
                logger.error("Failed to add new item")
                return False

        # Add the new item to the tree
        nwItem = self.theProject.getItem(tHandle)
        trItem = self._addTreeItem(nwItem)
        if pHandle is not None and pHandle in self.theMap.keys():
            self.theMap[pHandle].setExpanded(True)
        self.clearSelection()
        trItem.setSelected(True)
        self.theParent.editItem()

        return True

    def moveTreeItem(self, nStep):
        """Move an item up or down in the tree, but only if the treeView has focus. This also
        applies when the menu is used.
        """
        if QApplication.focusWidget() == self:
            tHandle = self.getSelectedHandle()
            tItem   = self._getTreeItem(tHandle)
            pItem   = tItem.parent()
            if pItem is None:
                tIndex = self.indexOfTopLevelItem(tItem)
                nChild = self.topLevelItemCount()
                nIndex = tIndex + nStep
                if nIndex < 0 or nIndex >= nChild: return
                cItem  = self.takeTopLevelItem(tIndex)
                self.insertTopLevelItem(nIndex, cItem)
            else:
                tIndex = pItem.indexOfChild(tItem)
                nChild = pItem.childCount()
                nIndex = tIndex + nStep
                if nIndex < 0 or nIndex >= nChild: return
                cItem   = pItem.takeChild(tIndex)
                pItem.insertChild(nIndex, cItem)
            self.clearSelection()
            cItem.setSelected(True)
            self.theProject.setProjectChanged(True)
        return

    def saveTreeOrder(self):
        theList = []
        for i in range(self.topLevelItemCount()):
            if self.topLevelItem(i) == self.orphRoot:
                continue
            theList = self._scanChildren(theList, self.topLevelItem(i), i)
        self.theProject.setTreeOrder(theList)
        return True

    def getColumnSizes(self):
        retVals = [
            self.columnWidth(0),
            self.columnWidth(1),
            self.columnWidth(2),
        ]
        return retVals

    def deleteItem(self, tHandle=None):
        """Delete items from the tree. Note that this does not delete the item from the item tree in
        the project object. However, since this is only meta data, there isn't really a need to do
        that to save memory. As items not in the tree are not saved to the project file, a loaded
        project will be clean anyway.
        """

        if tHandle is None:
            tHandle = self.getSelectedHandle()

        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.getItem(tHandle)

        if nwItemS.itemType == nwItemType.FILE:
            logger.debug("User requested file %s moved to trash" % tHandle)
            trItemP = trItemS.parent()
            trItemT = self._addTrashRoot()
            if trItemP is None or trItemT is None:
                logger.error("Could not move item to trash")
                return
            tIndex  = trItemP.indexOfChild(trItemS)
            trItemC = trItemP.takeChild(tIndex)
            trItemT.addChild(trItemC)
            nwItemS.setParent(self.theProject.trashRoot)
            self.clearSelection()
            trItemP.setSelected(True)
            self.theProject.setProjectChanged(True)

        elif nwItemS.itemType == nwItemType.FOLDER:
            logger.debug("User requested folder %s deleted" % tHandle)
            trItemP = trItemS.parent()
            if trItemP is None:
                logger.error("Could not delete folder")
                return
            tIndex = trItemP.indexOfChild(trItemS)
            if trItemS.childCount() == 0:
                trItemP.takeChild(tIndex)
                self.clearSelection()
                trItemP.setSelected(True)
                self.theProject.setProjectChanged(True)
            else:
                self.makeAlert(["Cannot delete folder.","It is not empty."], nwAlert.ERROR)
                return

        elif nwItemS.itemType == nwItemType.ROOT:
            logger.debug("User requested root folder %s deleted" % tHandle)
            tIndex = self.indexOfTopLevelItem(trItemS)
            if trItemS.childCount() == 0:
                self.takeTopLevelItem(tIndex)
                self.theParent.mainMenu.setAvailableRoot()
                self.theProject.setProjectChanged(True)
            else:
                self.makeAlert(["Cannot delete root folder.","It is not empty."], nwAlert.ERROR)
                return

        return

    def setTreeItemValues(self, tHandle):

        trItem  = self._getTreeItem(tHandle)
        nwItem  = self.theProject.getItem(tHandle)
        tName   = nwItem.itemName
        tClass  = nwItem.itemClass
        tHandle = nwItem.itemHandle
        pHandle = nwItem.parHandle

        tStatus = nwLabels.CLASS_FLAG[nwItem.itemClass]
        if nwItem.itemType == nwItemType.FILE:
            tStatus += "."+nwLabels.LAYOUT_FLAG[nwItem.itemLayout]
        iStatus = nwItem.itemStatus
        if tClass == nwItemClass.NOVEL:
            if iStatus is None:
                iStatus = self.theProject.statusItems.checkEntry(iStatus)
            flagIcon = self.theParent.statusIcons[iStatus]
        else:
            if iStatus is None:
                iStatus = self.theProject.importItems.checkEntry(iStatus)
            flagIcon = self.theParent.importIcons[iStatus]

        trItem.setText(self.C_NAME, tName)
        trItem.setText(self.C_FLAGS,tStatus)
        trItem.setIcon(self.C_FLAGS,flagIcon)

        return

    def propagateCount(self, tHandle, theCount, nDepth=0):
        tItem = self._getTreeItem(tHandle)
        if tItem is not None:
            tItem.setText(self.C_COUNT,str(theCount))
            pItem = tItem.parent()
            if pItem is not None:
                pCount = 0
                for i in range(pItem.childCount()):
                    pCount += int(pItem.child(i).text(self.C_COUNT))
                    pHandle = pItem.text(self.C_HANDLE)
                if not nDepth > 200 and pHandle != "":
                    self.propagateCount(pHandle, pCount, nDepth+1)
        return

    def buildTree(self):
        self.clear()
        for nwItem in self.theProject.getProjectItems():
            self._addTreeItem(nwItem)
        return True

    def getSelectedHandle(self):
        selItem = self.selectedItems()
        if len(selItem) == 0:
            return None
        if isinstance(selItem[0], QTreeWidgetItem):
            return selItem[0].text(self.C_HANDLE)
        return None

    def getSelectedHandles(self):
        selItems   = self.selectedItems()
        selHandles = []
        for n in range(len(selItems)):
            if isinstance(selItems[n], QTreeWidgetItem):
                selHandles.append(selItems[n].text(self.C_HANDLE))
        return selHandles

    ##
    #  Internal Functions
    ##

    def _getTreeItem(self, tHandle):
        if tHandle in self.theMap.keys():
            return self.theMap[tHandle]
        return None

    def _scanChildren(self, theList, theItem, theIndex):
        tHandle = theItem.text(self.C_HANDLE)
        nwItem  = self.theProject.projTree[tHandle]
        nwItem.setExpanded(theItem.isExpanded())
        nwItem.setOrder(theIndex)
        theList.append(tHandle)
        for i in range(theItem.childCount()):
            self._scanChildren(theList, theItem.child(i), i)
        return theList

    def _addTreeItem(self, nwItem):

        tHandle = nwItem.itemHandle
        pHandle = nwItem.parHandle
        newItem = QTreeWidgetItem([""]*4)

        newItem.setText(self.C_NAME,   "")
        newItem.setText(self.C_COUNT,  "0")
        newItem.setText(self.C_FLAGS,  "")
        newItem.setText(self.C_HANDLE, tHandle)

        newItem.setForeground(self.C_COUNT,QColor(0,105,135))
        newItem.setTextAlignment(self.C_COUNT,Qt.AlignRight)
        newItem.setFont(self.C_FLAGS,self.fontFlags)

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
            self.theMap[pHandle].addChild(newItem)
            self.propagateCount(tHandle, nwItem.wordCount)

        self.setTreeItemValues(tHandle)
        newItem.setExpanded(nwItem.isExpanded)

        if nwItem.itemType == nwItemType.ROOT:
            newItem.setIcon(self.C_NAME, QIcon.fromTheme("drive-harddisk"))
        elif nwItem.itemType == nwItemType.FOLDER:
            newItem.setIcon(self.C_NAME, QIcon.fromTheme("folder"))
        elif nwItem.itemType == nwItemType.FILE:
            newItem.setIcon(self.C_NAME, QIcon.fromTheme("x-office-document"))
        elif nwItem.itemType == nwItemType.TRASH:
            newItem.setIcon(self.C_NAME, QIcon.fromTheme("user-trash"))

        return newItem

    def _addTrashRoot(self):
        if self.theProject.trashRoot is None:
            self.theProject.addTrash()
            trItem = self._addTreeItem(
                self.theProject.getItem(self.theProject.trashRoot)
            )
            trItem.setExpanded(True)
        else:
            trItem = self._getTreeItem(self.theProject.trashRoot)
        return trItem

    def _addOrphanedRoot(self):
        if self.orphRoot is None:
            newItem = QTreeWidgetItem([""]*4)
            newItem.setText(self.C_NAME,   "Orphaned Files")
            newItem.setText(self.C_COUNT,  "")
            newItem.setText(self.C_FLAGS,  "")
            newItem.setText(self.C_HANDLE, "")
            self.addTopLevelItem(newItem)
            self.orphRoot = newItem
            newItem.setExpanded(True)
            newItem.setIcon(self.C_NAME, QIcon.fromTheme("dialog-warning"))
        return

    def _cleanOrphanedRoot(self):
        if self.orphRoot.childCount() == 0:
            self.takeTopLevelItem(self.indexOfTopLevelItem(self.orphRoot))
            self.orphRoot = None
        return

    def _updateItemParent(self, tHandle):
        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.getItem(tHandle)
        trItemP = trItemS.parent()
        if trItemP is None:
            logger.error("Failed to find new parent item of %s" % tHandle)
            return
        pHandle = trItemP.text(self.C_HANDLE)
        nwItemS.setParent(pHandle)
        self.setTreeItemValues(tHandle)
        self.theProject.setProjectChanged(True)
        return

    def _moveOrphanedItem(self, tHandle, dHandle):
        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.getItem(tHandle)
        nwItemD = self.theProject.getItem(dHandle)
        trItemP = trItemS.parent()
        nwItemS.setClass(nwItemD.itemClass)
        if trItemP is None:
            logger.error("Failed to find new parent item of %s" % tHandle)
            return
        pHandle = trItemP.text(self.C_HANDLE)
        nwItemS.setParent(pHandle)
        self.setTreeItemValues(tHandle)
        self.theProject.setProjectChanged(True)
        return

    ##
    #  Event Overloading
    ##

    def mousePressEvent(self, theEvent):
        """Overload mousePressEvent to clear selection if clicking the mouse in a blank
        area of the tree view.
        """
        QTreeWidget.mousePressEvent(self, theEvent)
        selItem = self.indexAt(theEvent.pos())
        if not selItem.isValid():
            self.clearSelection()
        return

    def dropEvent(self, theEvent):
        """Overload the drop of dragged item event to check whether the drop is allowed
        or not. Disallowed drops are cancelled.
        """
        sHandle = self.getSelectedHandle()
        if sHandle is None:
            return

        dIndex  = self.indexAt(theEvent.pos())
        if not dIndex.isValid():
            return

        dItem   = self.itemFromIndex(dIndex)
        dHandle = dItem.text(self.C_HANDLE)
        snItem  = self.theProject.getItem(sHandle)
        dnItem  = self.theProject.getItem(dHandle)
        isSame  = snItem.itemClass == dnItem.itemClass
        isNone  = snItem.itemClass == nwItemClass.NO_CLASS
        onFile  = dnItem.itemType == nwItemType.FILE
        isRoot  = snItem.itemType == nwItemType.ROOT
        onRoot  = dnItem.itemType == nwItemType.ROOT
        isOnTop = self.dropIndicatorPosition() == QAbstractItemView.OnItem
        isAbove = self.dropIndicatorPosition() == QAbstractItemView.AboveItem
        isBelow = self.dropIndicatorPosition() == QAbstractItemView.BelowItem
        if (isSame or isNone) and not (onFile and isOnTop) and not isRoot:
            logger.verbose("Drag'n'drop of item %s accepted" % sHandle)
            QTreeWidget.dropEvent(self, theEvent)
            if isNone:
                self._moveOrphanedItem(sHandle, dHandle)
                self._cleanOrphanedRoot()
            else:
                self._updateItemParent(sHandle)
        elif isRoot and (isAbove or isBelow) and onRoot:
            logger.verbose("Drag'n'drop of item %s accepted" % sHandle)
            QTreeWidget.dropEvent(self, theEvent)
        else:
            logger.verbose("Drag'n'drop of item %s not accepted" % sHandle)

        return

# END Class GuiDocTree
