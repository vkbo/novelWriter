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

from os       import path, mkdir
from lxml     import etree
from datetime import datetime

from nw.enum  import nwItemType, nwItemClass

logger = logging.getLogger(__name__)

class NWItem():

    def __init__(self):

        self.itemName   = ""
        self.itemHandle = None
        self.parHandle  = None
        self.itemOrder  = None
        self.itemType   = nwItemType.NONE
        self.itemClass  = nwItemClass.NONE
        self.isExpanded = False

        return

    def setFromTag(self, tagName, tagValue):
        logger.verbose("Setting tag '%s' to value '%s'" % (tagName, str(tagValue)))
        if   tagName == "name":     self.setName(tagValue)
        elif tagName == "order":    self.setOrder(tagValue)
        elif tagName == "type":     self.setType(tagValue)
        elif tagName == "class":    self.setClass(tagValue)
        elif tagName == "expanded": self.setExpanded(tagValue)
        return

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
        else:
            for itemType in nwItemType:
                if theType == itemType.name:
                    self.itemType = itemType
                    return
        logger.error("Unrecognised item type '%s'" % theType)
        self.itemType = nwItemType.NONE
        return

    def setClass(self, theClass):
        if isinstance(theClass, nwItemClass):
            self.itemClass = theClass
        else:
            for itemClass in nwItemClass:
                if theClass == itemClass.name:
                    self.itemClass = itemClass
                    return
        logger.error("Unrecognised item class '%s'" % theClass)
        self.itemClass = nwItemClass.NONE
        return

    def setExpanded(self, expState):
        if isinstance(expState, str):
            self.isExpanded = expState == str(True)
        else:
            self.isExpanded = expState
        return

# END Class NWItem
