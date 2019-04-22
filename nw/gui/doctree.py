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
from PyQt5.QtCore    import QSize
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView

from nw.enum         import nwItemType, nwItemClass

logger = logging.getLogger(__name__)

class GuiDocTree(QTreeWidget):

    def __init__(self, theProject):
        QTreeWidget.__init__(self)

        logger.debug("Initialising DocTree ...")
        self.mainConf   = nw.CONFIG
        self.debugGUI   = self.mainConf.debugGUI
        self.theProject = theProject
        self.theMap     = {}

        self.setStyleSheet("QTreeWidget {font-size: 13px;}")
        self.setIconSize(QSize(13,13))
        self.setExpandsOnDoubleClick(True)
        self.setIndentation(13)
        self.setColumnCount(4)
        self.setHeaderLabels(["Name","","","Handle"])
        if not self.debugGUI:
            self.hideColumn(3)

        # Allow Move by Drag & Drop
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        for colN in range(len(self.mainConf.treeColWidth)):
            self.setColumnWidth(colN,self.mainConf.treeColWidth[colN])

        logger.debug("DocTree initialisation complete")

        return

    def newTreeItem(self, itemType):

        rHandle = self._getSelectedHandle()
        logger.verbose("Adding item relative to handle %s" % rHandle)

        # Figure out where to put the new item
        if rHandle is None:
            nwType  = nwItemType.ROOT
            pHandle = None
        else:
            rItem = self.theProject.projTree[rHandle]
            if rItem.itemType == nwItemType.FILE:
                pHandle = rItem.parHandle
            else:
                pHandle = rHandle

        # Create the new item
        if itemType == nwItemType.FILE:
            tHandle = self.theProject.newFile("New File", nwItemClass.NONE, pHandle)
        elif itemType == nwItemType.FOLDER:
            if pHandle is None:
                logger.error("Failed to add new item")
                return
            pItem = self.theProject.projTree[rHandle]
            if pItem.itemClass == nwItemClass.NOVEL:
                tHandle = self.theProject.newFolder("New Chapter", nwItemClass.CHAPTER, pHandle)
            elif pItem.itemClass == nwItemClass.CHAPTER:
                tHandle = self.theProject.newFolder("New Chapter", nwItemClass.CHAPTER, pItem.parHandle)
            else:
                tHandle = self.theProject.newFolder("New Folder", nwItemClass.NONE, pHandle)
        elif itemType == nwItemType.ROOT:
            tHandle = self.theProject.newRoot("Root Folder", nwItemClass.NONE)
        else:
            logger.error("Failed to add new item")
            return

        # Add the new item to the tree
        nwItem = self.theProject.projTree[tHandle]
        self._addTreeItem(nwItem)

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
        wCount  = 0
        newItem = QTreeWidgetItem([
            tName, str(tStatus), str(wCount), tHandle
        ])
        self.theMap[tHandle] = newItem
        if pHandle is None:
            self.addTopLevelItem(newItem)
        else:
            self.theMap[pHandle].addChild(newItem)
        newItem.setExpanded(nwItem.isExpanded)
        if nwItem.itemType == nwItemType.ROOT:
            newItem.setIcon(0, QIcon.fromTheme("drive-harddisk"))
        elif nwItem.itemType == nwItemType.FOLDER:
            newItem.setIcon(0, QIcon.fromTheme("folder"))
        elif nwItem.itemType == nwItemType.FILE:
            newItem.setIcon(0, QIcon.fromTheme("x-office-document"))
        return True

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
