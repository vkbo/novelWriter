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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
)

from nw.constants import nwItemLayout

logger = logging.getLogger(__name__)

class GuiProjectOutline(QWidget):

    I_TITLE = 0
    I_LEVEL = 1
    I_LABEL = 2
    I_LINE  = 3
    I_WORDS = 4
    I_CHARS = 5
    I_PARAS = 6
    I_SYNOP = 7

    COL_ORDER = [
        I_TITLE, I_LEVEL, I_LABEL, I_LINE,
        I_WORDS, I_CHARS, I_PARAS, I_SYNOP,
    ]

    COL_LABELS = {
        I_TITLE : "Title",
        I_LEVEL : "Level",
        I_LABEL : "Document",
        I_LINE  : "Line",
        I_WORDS : "Words",
        I_CHARS : "Chars",
        I_PARAS : "Pars",
        I_SYNOP : "Synopsis",
    }

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

        self.outerBox  = QVBoxLayout()
        self.mainTree  = QTreeWidget()
        self.treeOrder = self.COL_ORDER

        self.outerBox.addWidget(self.mainTree)
        self.outerBox.setContentsMargins(0,0,0,0)
        self.setLayout(self.outerBox)

        logger.debug("ProjectOutline initialisation complete")

        return

    def populateTree(self):

        theLabels = []
        for n in self.treeOrder:
            theLabels.append(self.COL_LABELS[n])
 
        self.mainTree.clear()
        self.mainTree.setHeaderLabels(theLabels)
 
        treeHead = self.mainTree.headerItem()
        treeHead.setTextAlignment(self.I_CHARS,Qt.AlignRight)
        treeHead.setTextAlignment(self.I_WORDS,Qt.AlignRight)
        treeHead.setTextAlignment(self.I_PARAS,Qt.AlignRight)

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

                theLine = str(tEntry[0])

                newItem = QTreeWidgetItem([""]*4)
                newItem.setText(self.I_TITLE, tEntry[2])
                newItem.setText(self.I_LEVEL, str(tEntry[1]))
                newItem.setText(self.I_LABEL, nwItem.itemName)
                newItem.setText(self.I_LINE,  theLine)

                cC, wC, pC = self.theIndex.getCounts(tHandle, theLine)
                newItem.setText(self.I_CHARS, str(cC))
                newItem.setText(self.I_WORDS, str(wC))
                newItem.setText(self.I_PARAS, str(pC))
                newItem.setTextAlignment(self.I_CHARS,Qt.AlignRight)
                newItem.setTextAlignment(self.I_WORDS,Qt.AlignRight)
                newItem.setTextAlignment(self.I_PARAS,Qt.AlignRight)

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
