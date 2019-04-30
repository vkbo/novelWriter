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
from nw.enum         import nwItemType, nwItemClass
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
        self.theMap     = {}
        self.orphRoot   = None

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

        for colN in range(len(self.mainConf.treeColWidth)):
            self.setColumnWidth(colN,self.mainConf.treeColWidth[colN])

        self.fontFlags = QFont("Monospace",10)
        self.fontCount = QFont("Monospace",10)

        logger.debug("DocTree initialisation complete")

        return

    def newTreeItem(self, itemType, itemClass):

        pHandle = self.getSelectedHandle()
        if itemClass is None and pHandle is not None:
            itemClass = self.theProject.getItem(pHandle).itemClass

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
        if pHandle is not None:
            self.theMap[pHandle].setExpanded(True)
        self.clearSelection()
        trItem.setSelected(True)
        self.theParent.editItem()

        return

    def moveTreeItem(self, nStep):
        """Move an item up or down in the tree, but only if the treeView has focus. This also
        applies when the menu is used.
        """
        if QApplication.focusWidget() == self:
            tHandle = self.getSelectedHandle()
            tItem   = self.theMap[tHandle]
            pItem   = tItem.parent()
            tIndex  = pItem.indexOfChild(tItem)
            nChild  = pItem.childCount()
            nIndex  = tIndex + nStep
            if nIndex < 0 or nIndex >= nChild: return
            cItem   = pItem.takeChild(tIndex)
            pItem.insertChild(nIndex, cItem)
            self.clearSelection()
            cItem.setSelected(True)
        return

    def renameTreeItem(self, tHandle):
        tItem   = self.theMap[tHandle]
        oldName = tItem.text(self.C_NAME)
        newName, isOk = QInputDialog.getText(self, "Rename Item", "New Name", QLineEdit.Normal,oldName)
        if isOk:
            newName = newName.strip()
            if newName == "":
                newName = oldName
            tItem.setText(self.C_NAME,newName)
            self.theProject.setItemName(tHandle, newName)
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

    ##
    #  Internal Functions
    ##

    def _scanChildren(self, theList, theItem, theIndex):
        tHandle = theItem.text(self.C_HANDLE)
        nwItem  = self.theProject.projTree[tHandle]
        nwItem.setExpanded(theItem.isExpanded())
        nwItem.setOrder(theIndex)
        theList.append(tHandle)
        for i in range(theItem.childCount()):
            self._scanChildren(theList, theItem.child(i), i)
        return theList

    def _scanParents(self, theItem, theCount=0):
        if theItem.parent() is not None:
            theItem, theCount = self._scanParents(theItem.parent(), theCount)
        return theItem, theCount+1

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

        return newItem

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
        return
    
    def _cleanOrphanedRoot(self):
        if self.orphRoot.childCount() == 0:
            self.takeTopLevelItem(self.indexOfTopLevelItem(self.orphRoot))
            self.orphRoot = None
        return

    def setTreeItemValues(self, tHandle):

        trItem  = self.theMap[tHandle]
        nwItem  = self.theProject.getItem(tHandle)
        tName   = nwItem.itemName
        tHandle = nwItem.itemHandle
        pHandle = nwItem.parHandle

        tStatus = nwLabels.CLASS_FLAG[nwItem.itemClass]
        if nwItem.itemType == nwItemType.FILE:
            tStatus += "."+nwLabels.LAYOUT_FLAG[nwItem.itemLayout]
        nStatus = nwItem.itemStatus
        if nStatus < 0 or nStatus >= len(self.theProject.statusIcons):
            nStatus = 0

        trItem.setText(self.C_NAME,tName)
        trItem.setText(self.C_FLAGS,tStatus)
        trItem.setIcon(self.C_FLAGS,self.theProject.statusIcons[nStatus])

        return

    def propagateCount(self, tHandle, theCount, nDepth=0):
        tItem = self.theMap[tHandle]
        tItem.setText(self.C_COUNT,str(theCount))
        pItem = tItem.parent()
        if pItem is not None:
            pCount = 0
            for i in range(pItem.childCount()):
                pCount += int(pItem.child(i).text(self.C_COUNT))
                pHandle = pItem.text(self.C_HANDLE)
            if not nDepth > NWItem.MAX_DEPTH and pHandle != "":
                self.propagateCount(pHandle, pCount, nDepth+1)
        return

    def buildTree(self):
        self.clear()
        for tHandle in self.theProject.projTree:
            nwItem = self.theProject.projTree[tHandle]
            self._addTreeItem(nwItem)
        return True

    def getSelectedHandle(self):
        selItem = self.selectedItems()
        if len(selItem) == 0:
            return None
        if isinstance(selItem[0], QTreeWidgetItem):
            return selItem[0].text(self.C_HANDLE)
        return None

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
        isFile  = dnItem.itemType == nwItemType.FILE
        isRoot  = snItem.itemType == nwItemType.ROOT
        isOnTop = self.dropIndicatorPosition() == QAbstractItemView.OnItem
        if (isSame or isNone) and not (isFile and isOnTop) and not isRoot:
            logger.verbose("Drag'n'drop of item %s accepted" % sHandle)
            QTreeWidget.dropEvent(self, theEvent)
            if isNone:
                snItem.setClass(dnItem.itemClass)
                self.setTreeItemValues(sHandle)
                self._cleanOrphanedRoot()
        else:
            logger.verbose("Drag'n'drop of item %s not accepted" % sHandle)

        return

# END Class GuiDocTree
