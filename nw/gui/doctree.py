# -*- coding: utf-8 -*
"""novelWriter GUI Document Tree

 novelWriter – GUI Document Tree
=================================
 Class holding the left side document tree view

 File History:
 Created: 2018-09-29 [0.1.0]

"""

import logging
import nw

from os              import path
from PyQt5.QtCore    import Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QAbstractItemView

logger = logging.getLogger(__name__)

class GuiDocTree(QTreeWidget):

    def __init__(self, theProject):
        QTreeWidget.__init__(self)

        logger.debug("Initialising DocTree ...")
        self.mainConf   = nw.CONFIG
        self.debugGUI   = self.mainConf.debugGUI
        self.theProject = theProject
        self.theMap     = {}

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

    def saveTreeOrder(self):

        theList = []
        for i in range(self.topLevelItemCount()):
            theList = self._scanChildren(theList, self.topLevelItem(i))

        print(theList)

        return True

    def _scanChildren(self, theList, theItem):
        theList.append(theItem.text(3))
        for i in range(theItem.childCount()):
            self._scanChildren(theList, theItem.child(i))
        return theList

    def buildTree(self):

        for tHandle in self.theProject.projTree:
            nwItem  = self.theProject.projTree[tHandle]
            tName   = nwItem.itemName
            tStatus = 0
            wCount  = 0
            pHandle = nwItem.parHandle
            newItem = QTreeWidgetItem([
                tName, str(tStatus), str(wCount), tHandle
            ])
            self.theMap[tHandle] = newItem
            if pHandle is None:
                self.addTopLevelItem(newItem)
            else:
                self.theMap[pHandle].addChild(newItem)

        return True

    def getColumnSizes(self):
        retVals = [
            self.columnWidth(0),
            self.columnWidth(1),
            self.columnWidth(2),
        ]
        return retVals

# END Class GuiDocTree
