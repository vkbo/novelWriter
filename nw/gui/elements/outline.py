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

from nw.constants import nwItemLayout, nwKeyWords, nwLabels

logger = logging.getLogger(__name__)

class GuiProjectOutline(QWidget):

    I_TITLE  = 0
    I_LEVEL  = 1
    I_LABEL  = 2
    I_LINE   = 3
    I_WCOUNT = 4
    I_CCOUNT = 5
    I_PCOUNT = 6
    I_SYNOP  = 7
    I_POV    = 8
    I_CHAR   = 9
    I_PLOT   = 10
    I_TIME   = 11
    I_WORLD  = 12
    I_OBJECT = 13
    I_ENTITY = 14
    I_CUSTOM = 15

    COL_ORDER = [
        I_TITLE,  I_LEVEL,  I_LABEL,  I_LINE,
        I_WCOUNT, I_CCOUNT, I_PCOUNT, I_SYNOP,
        I_POV,    I_CHAR,   I_PLOT,   I_TIME,
        I_WORLD,  I_OBJECT, I_ENTITY, I_CUSTOM,
    ]

    COL_LABELS = {
        I_TITLE  : "Title",
        I_LEVEL  : "Level",
        I_LABEL  : "Document",
        I_LINE   : "Line",
        I_WCOUNT : "Words",
        I_CCOUNT : "Chars",
        I_PCOUNT : "Pars",
        I_SYNOP  : "Synopsis",
        I_POV    : nwLabels.KEY_NAME[nwKeyWords.POV_KEY],
        I_CHAR   : nwLabels.KEY_NAME[nwKeyWords.CHAR_KEY],
        I_PLOT   : nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY],
        I_TIME   : nwLabels.KEY_NAME[nwKeyWords.TIME_KEY],
        I_WORLD  : nwLabels.KEY_NAME[nwKeyWords.WORLD_KEY],
        I_OBJECT : nwLabels.KEY_NAME[nwKeyWords.OBJECT_KEY],
        I_ENTITY : nwLabels.KEY_NAME[nwKeyWords.ENTITY_KEY],
        I_CUSTOM : nwLabels.KEY_NAME[nwKeyWords.CUSTOM_KEY],
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
        treeHead.setTextAlignment(self.I_CCOUNT,Qt.AlignRight)
        treeHead.setTextAlignment(self.I_WCOUNT,Qt.AlignRight)
        treeHead.setTextAlignment(self.I_PCOUNT,Qt.AlignRight)

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

                nTitle = str(tEntry[0])
                tTitle = tEntry[2]
                tLevel = str(tEntry[1])
                tLabel = nwItem.itemName
                tItem  = self._createTreeItem(tHandle, nTitle, tTitle, tLevel, tLabel)

                if tEntry[1] == 1:
                    currTitle = tItem
                    self.mainTree.addTopLevelItem(tItem)
                elif tEntry[1] == 2:
                    if currTitle is None:
                        self.mainTree.addTopLevelItem(tItem)
                    else:
                        currTitle.addChild(tItem)
                    currChapter = tItem
                elif tEntry[1] == 3:
                    if currChapter is None:
                        if currTitle is None:
                            self.mainTree.addTopLevelItem(tItem)
                        else:
                            currTitle.addChild(tItem)
                    else:
                        currChapter.addChild(tItem)
                    currScene = tItem
                elif tEntry[1] == 4:
                    if currScene is None:
                        if currChapter is None:
                            if currTitle is None:
                                self.mainTree.addTopLevelItem(tItem)
                            else:
                                currTitle.addChild(tItem)
                        else:
                            currChapter.addChild(tItem)
                    else:
                        currScene.addChild(tItem)

                tItem.setExpanded(True)

        return

    ##
    #  Internal Functions
    ##

    def _createTreeItem(self, tHandle, nTitle, tTitle, tLevel, tLabel):

        newItem = QTreeWidgetItem()
        newItem.setText(self.I_TITLE, tTitle)
        newItem.setText(self.I_LEVEL, tLevel)
        newItem.setText(self.I_LABEL, tLabel)
        newItem.setText(self.I_LINE,  nTitle)

        cC, wC, pC = self.theIndex.getCounts(tHandle, nTitle)
        newItem.setText(self.I_CCOUNT, str(cC))
        newItem.setText(self.I_WCOUNT, str(wC))
        newItem.setText(self.I_PCOUNT, str(pC))
        newItem.setTextAlignment(self.I_CCOUNT,Qt.AlignRight)
        newItem.setTextAlignment(self.I_WCOUNT,Qt.AlignRight)
        newItem.setTextAlignment(self.I_PCOUNT,Qt.AlignRight)

        povList    = []
        charList   = []
        plotList   = []
        timeList   = []
        worldList  = []
        objectList = []
        entityList = []
        customList = []
        for tKey, tTag in self.theIndex.getReferences(tHandle, nTitle):
            if tKey == nwKeyWords.POV_KEY:
                povList.append(tTag)
            elif tKey == nwKeyWords.CHAR_KEY:
                charList.append(tTag)
            elif tKey == nwKeyWords.PLOT_KEY:
                plotList.append(tTag)
            elif tKey == nwKeyWords.TIME_KEY:
                timeList.append(tTag)
            elif tKey == nwKeyWords.WORLD_KEY:
                worldList.append(tTag)
            elif tKey == nwKeyWords.OBJECT_KEY:
                objectList.append(tTag)
            elif tKey == nwKeyWords.ENTITY_KEY:
                entityList.append(tTag)
            elif tKey == nwKeyWords.CUSTOM_KEY:
                customList.append(tTag)

        newItem.setText(self.I_POV,    ", ".join(povList))
        newItem.setText(self.I_CHAR,   ", ".join(charList))
        newItem.setText(self.I_PLOT,   ", ".join(plotList))
        newItem.setText(self.I_TIME,   ", ".join(timeList))
        newItem.setText(self.I_WORLD,  ", ".join(worldList))
        newItem.setText(self.I_OBJECT, ", ".join(objectList))
        newItem.setText(self.I_ENTITY, ", ".join(entityList))
        newItem.setText(self.I_CUSTOM, ", ".join(customList))

        return newItem


# END Class GuiProjectOutline
