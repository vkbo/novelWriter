# -*- coding: utf-8 -*-
"""novelWriter GUI Project Outline

 novelWriter – GUI Project Outline
===================================
 Class holding the project outline view

 File History:
 Created: 2019-11-16 [0.4.1]

"""

import logging
import nw

from os import path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
)

from nw.constants import nwItemLayout

logger = logging.getLogger(__name__)

class GuiProjectOutline(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        logger.debug("Initialising ProjectOutline ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theIndex   = self.theParent.theIndex

        self.showWords    = True
        self.showSynopsis = True
        self.showFilePath = False

        self.outerBox = QVBoxLayout()
        self.mainTree = QTreeWidget()

        self.outerBox.addWidget(self.mainTree)
        self.outerBox.setContentsMargins(0,0,0,0)
        self.setLayout(self.outerBox)

        logger.debug("ProjectOutline initialisation complete")

        return

    def populateTree(self):

        self.mainTree.clear()
        self.mainTree.setHeaderLabels(["Title","Level","Document","Line"])

        currTitle   = None
        currChapter = None
        currScene   = None

        for tHandle in self.theProject.treeOrder:

            if tHandle not in self.theIndex.novelIndex:
                continue

            nwItem = self.theProject.getItem(tHandle)
            if nwItem.itemLayout == nwItemLayout.NOTE:
                continue

            for tEntry in self.theIndex.novelIndex[tHandle]:
                newItem = QTreeWidgetItem([""]*4)
                newItem.setText(0, tEntry[2])
                newItem.setText(1, str(tEntry[1]))
                newItem.setText(2, nwItem.itemName)
                newItem.setText(3, str(tEntry[0]))

                if tEntry[1] == 1:
                    currTitle = newItem
                    self.mainTree.addTopLevelItem(newItem)
                elif tEntry[1] == 2:
                    if currTitle is None:
                        self.mainTree.addTopLevelItem(newItem)
                    else:
                        currTitle.addChild(newItem)
                    currChapter = newItem
                elif tEntry[1] == 3:
                    if currChapter is None:
                        if currTitle is None:
                            self.mainTree.addTopLevelItem(newItem)
                        else:
                            currTitle.addChild(newItem)
                    else:
                        currChapter.addChild(newItem)
                    currScene = newItem
                elif tEntry[1] == 4:
                    if currScene is None:
                        if currChapter is None:
                            if currTitle is None:
                                self.mainTree.addTopLevelItem(newItem)
                            else:
                                currTitle.addChild(newItem)
                        else:
                            currChapter.addChild(newItem)
                    else:
                        currScene.addChild(newItem)

                newItem.setExpanded(True)

        return

# END Class GuiProjectOutline
