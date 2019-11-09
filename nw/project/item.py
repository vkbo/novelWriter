# -*- coding: utf-8 -*-
"""novelWriter Project Item

 novelWriter – Project Item
============================
 Class holding a project item

 File History:
 Created: 2018-10-27 [0.0.1]

"""

import logging
import nw

from lxml import etree
from datetime import datetime

from nw.common import checkInt
from nw.constants import nwItemType, nwItemClass, nwItemLayout

logger = logging.getLogger(__name__)

class NWItem():

    MAX_DEPTH = 8

    def __init__(self, theProject):

        self.theProject = theProject

        self.itemName   = ""
        self.itemHandle = None
        self.parHandle  = None
        self.itemOrder  = None
        self.itemType   = nwItemType.NO_TYPE
        self.itemClass  = nwItemClass.NO_CLASS
        self.itemLayout = nwItemLayout.NO_LAYOUT
        self.itemStatus = None
        self.isExpanded = False

        # Document Meta Data
        self.charCount = 0
        self.wordCount = 0
        self.paraCount = 0
        self.cursorPos = 0

        return

    ##
    #  XML Pack
    ##

    def packXML(self, xParent):
        xPack = etree.SubElement(xParent,"item",attrib={
            "handle" : str(self.itemHandle),
            "order"  : str(self.itemOrder),
            "parent" : str(self.parHandle),
        })
        xSub = self._subPack(xPack,"name",     text=str(self.itemName))
        xSub = self._subPack(xPack,"type",     text=str(self.itemType.name))
        xSub = self._subPack(xPack,"class",    text=str(self.itemClass.name))
        xSub = self._subPack(xPack,"status",   text=str(self.itemStatus))
        xSub = self._subPack(xPack,"expanded", text=str(self.isExpanded))
        if self.itemType == nwItemType.FILE:
            xSub = self._subPack(xPack,"layout",    text=str(self.itemLayout.name))
            xSub = self._subPack(xPack,"charCount", text=str(self.charCount), none=False)
            xSub = self._subPack(xPack,"wordCount", text=str(self.wordCount), none=False)
            xSub = self._subPack(xPack,"paraCount", text=str(self.paraCount), none=False)
            xSub = self._subPack(xPack,"cursorPos", text=str(self.cursorPos), none=False)
        return xPack

    def _subPack(self, xParent, name, attrib=None, text=None, none=True):
        if not none and (text == None or text == "None"):
            return None
        xSub = etree.SubElement(xParent,name,attrib=attrib)
        if text is not None:
            xSub.text = text
        return xSub

    ##
    #  Settings Wrapper
    ##

    def setFromTag(self, tagName, tagValue):
        logger.verbose("Setting tag '%s' to value '%s'" % (tagName, str(tagValue)))
        if tagName == "name":
            self.setName(tagValue)
        elif tagName == "order":
            self.setOrder(tagValue)
        elif tagName == "type":
            self.setType(tagValue)
        elif tagName == "class":
            self.setClass(tagValue)
        elif tagName == "layout":
            self.setLayout(tagValue)
        elif tagName == "status":
            self.setStatus(tagValue)
        elif tagName == "expanded":
            self.setExpanded(tagValue)
        elif tagName == "charCount":
            self.setCharCount(tagValue)
        elif tagName == "wordCount":
            self.setWordCount(tagValue)
        elif tagName == "paraCount":
            self.setParaCount(tagValue)
        elif tagName == "cursorPos":
            self.setCursorPos(tagValue)
        else:
            logger.error("Unknown tag '%s'" % tagName)
        return

    ##
    #  Set Item Values
    ##

    def setName(self, theName):
        self.itemName = theName.strip()
        return

    def setHandle(self, theHandle):
        self.itemHandle = theHandle
        return

    def setParent(self, theParent):
        self.parHandle = theParent
        return

    def setOrder(self, theOrder):
        self.itemOrder = theOrder
        return

    def setType(self, theType):
        if isinstance(theType, nwItemType):
            self.itemType = theType
            return
        else:
            for itemType in nwItemType:
                if theType == itemType.name:
                    self.itemType = itemType
                    return
        logger.error("Unrecognised item type '%s'" % theType)
        self.itemType = nwItemType.NO_TYPE
        return

    def setClass(self, theClass):
        if isinstance(theClass, nwItemClass):
            self.itemClass = theClass
            return
        else:
            for itemClass in nwItemClass:
                if theClass == itemClass.name:
                    self.itemClass = itemClass
                    return
        logger.error("Unrecognised item class '%s'" % theClass)
        self.itemClass = nwItemClass.NO_CLASS
        return

    def setLayout(self, theLayout):
        if isinstance(theLayout, nwItemLayout):
            self.itemLayout = theLayout
            return
        else:
            for itemLayout in nwItemLayout:
                if theLayout == itemLayout.name:
                    self.itemLayout = itemLayout
                    return
        logger.error("Unrecognised item layout '%s'" % theLayout)
        self.itemLayout = nwItemLayout.NO_LAYOUT
        return

    def setStatus(self, theStatus):
        if self.itemClass == nwItemClass.NOVEL:
            self.itemStatus = self.theProject.statusItems.checkEntry(theStatus)
        else:
            self.itemStatus = self.theProject.importItems.checkEntry(theStatus)
        return

    def setExpanded(self, expState):
        if isinstance(expState, str):
            self.isExpanded = expState == str(True)
        else:
            self.isExpanded = expState
        return

    ##
    #  Set Document Meta Data
    ##

    def setCharCount(self, theCount):
        theCount = checkInt(theCount,0)
        self.charCount = theCount
        return

    def setWordCount(self, theCount):
        theCount = checkInt(theCount,0)
        self.wordCount = theCount
        return

    def setParaCount(self, theCount):
        theCount = checkInt(theCount,0)
        self.paraCount = theCount
        return

    def setCursorPos(self, thePosition):
        thePosition = checkInt(thePosition,0)
        self.cursorPos = thePosition
        return

# END Class NWItem
