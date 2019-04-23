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
from PyQt5.QtGui     import QIcon
from PyQt5.QtCore    import Qt, QSize
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView

from nw.enum         import nwItemType, nwItemClass
from nw.project.item import NWItem

logger = logging.getLogger(__name__)

class GuiDocTree(QTreeWidget):

    def __init__(self, theProject):
        QTreeWidget.__init__(self)

        logger.debug("Initialising DocTree ...")
        self.mainConf   = nw.CONFIG
        self.debugGUI   = self.mainConf.debugGUI
        self.theProject = theProject
        self.theMap     = {}

        self.setIconSize(QSize(13,13))
        self.setExpandsOnDoubleClick(True)
        self.setIndentation(13)
        self.setColumnCount(4)
        self.setHeaderLabels(["Name","S","#","Handle"])
        if not self.debugGUI:
            self.hideColumn(3)

        # Allow Move by Drag & Drop
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        for colN in range(len(self.mainConf.treeColWidth)):
            self.setColumnWidth(colN,self.mainConf.treeColWidth[colN])

        logger.debug("DocTree initialisation complete")

        return

    def newTreeItem(self, pHandle, itemType, itemClass):

        logger.verbose("Adding new item of type %s and class %s to handle %s" % (
            itemType.name,itemClass.name,str(pHandle))
        )

        # Create the new item
        if   itemType == nwItemType.FILE:
            tHandle = self.theProject.newFile("New File", itemClass, pHandle)
        elif itemType == nwItemType.FOLDER:
            tHandle = self.theProject.newFolder("New Folder", itemClass, pHandle)
        elif itemType == nwItemType.ROOT:
            tHandle = self.theProject.newRoot(NWItem.CLASS_NAME[itemClass], itemClass)
        else:
            logger.error("Failed to add new item")
            return

        # Add the new item to the tree
        nwItem = self.theProject.getItem(tHandle)
        self._addTreeItem(nwItem)

        return

    def moveTreeItem(self, tHandle, nStep):
        tItem  = self.theMap[tHandle]
        pItem  = tItem.parent()
        tIndex = pItem.indexOfChild(tItem)
        nChild = pItem.childCount()
        nIndex = tIndex + nStep
        if nIndex < 0 or nIndex >= nChild: return
        cItem  = pItem.takeChild(tIndex)
        pItem.insertChild(nIndex, cItem)
        return

    def saveTreeOrder(self):
        theList = []
        for i in range(self.topLevelItemCount()):
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
        tHandle = theItem.text(3)
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
        tName   = nwItem.itemName
        tHandle = nwItem.itemHandle
        pHandle = nwItem.parHandle
        tStatus = 0
        newItem = QTreeWidgetItem([
            tName, str(tStatus), "0", tHandle
        ])
        self.theMap[tHandle] = newItem
        if pHandle is None:
            self.addTopLevelItem(newItem)
        else:
            self.theMap[pHandle].addChild(newItem)
            self.propagateCount(tHandle, nwItem.wordCount)
        newItem.setTextAlignment(2,Qt.AlignRight)
        newItem.setExpanded(nwItem.isExpanded)
        if nwItem.itemType == nwItemType.ROOT:
            newItem.setIcon(0, QIcon.fromTheme("drive-harddisk"))
        elif nwItem.itemType == nwItemType.FOLDER:
            newItem.setIcon(0, QIcon.fromTheme("folder"))
        elif nwItem.itemType == nwItemType.FILE:
            newItem.setIcon(0, QIcon.fromTheme("x-office-document"))
        return True

    def propagateCount(self, tHandle, theCount, nDepth=0):
        tItem = self.theMap[tHandle]
        tItem.setText(2,str(theCount))
        pItem = tItem.parent()
        if pItem is not None:
            pCount = 0
            for i in range(pItem.childCount()):
                pCount += int(pItem.child(i).text(2))
                pHandle = pItem.text(3)
            if not nDepth > NWItem.MAX_DEPTH:
                self.propagateCount(pHandle, pCount, nDepth+1)
        return

    def buildTree(self):
        self.clear()
        for tHandle in self.theProject.projTree:
            nwItem = self.theProject.projTree[tHandle]
            self._addTreeItem(nwItem)
        return True

    def _getSelectedHandle(self):
        selItem = self.selectedItems()
        if len(selItem) == 0:
            return None
        if isinstance(selItem[0], QTreeWidgetItem):
            return selItem[0].text(3)
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
        sHandle = self._getSelectedHandle()
        if sHandle is None:
            return

        dIndex  = self.indexAt(theEvent.pos())
        if not dIndex.isValid():
            return

        dItem   = self.itemFromIndex(dIndex)
        dHandle = dItem.text(3)
        snItem  = self.theProject.getItem(sHandle)
        dnItem  = self.theProject.getItem(dHandle)
        isSame  = snItem.itemClass == dnItem.itemClass and dnItem.itemType
        isFile  = dnItem.itemType == nwItemType.FILE
        isRoot  = snItem.itemType == nwItemType.ROOT
        isOnTop = self.dropIndicatorPosition() == QAbstractItemView.OnItem
        if isSame and not (isFile and isOnTop) and not isRoot:
            logger.verbose("Drag'n'drop on item %s allowed" % sHandle)
            QTreeWidget.dropEvent(self, theEvent)
        else:
            logger.verbose("Drag'n'drop on item %s not allowed" % sHandle)

        return

# END Class GuiDocTree
