# -*- coding: utf-8 -*
"""novelWriter Project Item

 novelWriter – Project Item
============================
 Class holding a project item

 File History:
 Created: 2018-10-27 [0.1.0]

"""

import logging
import nw

from os       import path, mkdir
from lxml     import etree
from datetime import datetime

logger = logging.getLogger(__name__)

class NWItem():

    TYPE_ROOT       = 0
    TYPE_FOLDER     = 1
    TYPE_FILE       = 2

    CLASS_NONE      = 0
    CLASS_NOVEL     = 1
    CLASS_CHARACTER = 2
    CLASS_WORLD     = 3

    def __init__(self):

        self.itemName   = ""
        self.itemHandle = None
        self.parHandle  = None
        self.itemOrder  = None
        self.itemType   = None
        self.itemClass  = None
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
        if isinstance(theType, int):
            self.itemType = theType
        elif theType == "ROOT":
            self.itemType = self.TYPE_ROOT
        elif theType == "FOLDER":
            self.itemType = self.TYPE_FOLDER
        elif theType == "FILE":
            self.itemType = self.TYPE_FILE
        else:
            logger.error("Unrecognised item type '%s'" % theType)
            self.itemType = None
        return

    def setClass(self, theClass):
        if isinstance(theClass, int):
            self.itemClass = theClass
        elif theClass == "NONE":
            self.itemClass = self.CLASS_NONE
        elif theClass == "NOVEL":
            self.itemClass = self.CLASS_NOVEL
        elif theClass == "CHARACTER":
            self.itemClass = self.CLASS_CHARACTER
        elif theClass == "WORLD":
            self.itemClass = self.CLASS_WORLD
        else:
            logger.error("Unrecognised root item '%s'" % theClass)
            self.itemClass = None
        return

    def setExpanded(self, expState):
        if isinstance(expState, str):
            self.isExpanded = expState == str(True)
        else:
            self.isExpanded = expState
        return

    def getType(self):
        if self.itemType == self.TYPE_ROOT:        return "ROOT"
        if self.itemType == self.TYPE_FOLDER:      return "FOLDER"
        if self.itemType == self.TYPE_FILE:        return "FILE"
        return "NONE"

    def getClass(self):
        if self.itemClass == self.CLASS_NONE:      return "NONE"
        if self.itemClass == self.CLASS_NOVEL:     return "NOVEL"
        if self.itemClass == self.CLASS_CHARACTER: return "CHARACTER"
        if self.itemClass == self.CLASS_WORLD:     return "WORLD"
        return "NONE"

# END Class NWItem
