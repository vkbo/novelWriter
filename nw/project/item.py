# -*- coding: utf-8 -*-
"""novelWriter Project Item

 novelWriter – Project Item
============================
 Class holding a project item

 File History:
 Created: 2018-10-27 [0.0.1]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import nw

from lxml import etree

from nw.common import checkInt
from nw.constants import nwItemType, nwItemClass, nwItemLayout

logger = logging.getLogger(__name__)

class NWItem():

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
        """Packs all the data in the class instance into an XML object.
        """
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
        return

    def unpackXML(self, xItem):
        """Sets the values from an XML entry of type 'item'.
        """

        if xItem.tag != "item":
            logger.error("XML entry is not an NWItem")
            return False

        if "handle" in xItem.attrib:
            self.itemHandle = xItem.attrib["handle"]
        else:
            logger.error("XML item entry does not have a handle")
            return False

        if "parent" in xItem.attrib:
            self.parHandle = xItem.attrib["parent"]

        setMap = {
            "name"      : self.setName,
            "order"     : self.setOrder,
            "type"      : self.setType,
            "class"     : self.setClass,
            "layout"    : self.setLayout,
            "status"    : self.setStatus,
            "expanded"  : self.setExpanded,
            "charCount" : self.setCharCount,
            "wordCount" : self.setWordCount,
            "paraCount" : self.setParaCount,
            "cursorPos" : self.setCursorPos,
        }
        for xValue in xItem:
            if xValue.tag in setMap:
                setMap[xValue.tag](xValue.text)
            else:
                logger.error("Unknown tag '%s'" % xValue.tag)

        return True

    @staticmethod
    def _subPack(xParent, name, attrib=None, text=None, none=True):
        if not none and (text == None or text == "None"):
            return None
        xSub = etree.SubElement(xParent,name,attrib=attrib)
        if text is not None:
            xSub.text = text
        return xSub

    ##
    #  Set Item Values
    ##

    def setName(self, theName):
        self.itemName = theName.strip()
        return

    def setHandle(self, theHandle):
        if isinstance(theHandle, str):
            if len(theHandle) == 13:
                self.itemHandle = theHandle
            else:
                self.itemHandle = None
        else:
            self.itemHandle = None
        return

    def setParent(self, theParent):
        if theParent is None:
            self.parHandle = None
        elif isinstance(theParent, str):
            if len(theParent) == 13:
                self.parHandle = theParent
            else:
                self.parHandle = None
        else:
            self.parHandle = None
        return

    def setOrder(self, theOrder):
        self.itemOrder = checkInt(theOrder, 0)
        return

    def setType(self, theType):
        if isinstance(theType, nwItemType):
            self.itemType = theType
        elif theType in nwItemType.__members__:
            self.itemType = nwItemType[theType]
        else:
            logger.error("Unrecognised item type '%s'" % theType)
            self.itemType = nwItemType.NO_TYPE
        return

    def setClass(self, theClass):
        if isinstance(theClass, nwItemClass):
            self.itemClass = theClass
        elif theClass in nwItemClass.__members__:
            self.itemClass = nwItemClass[theClass]
        else:
            logger.error("Unrecognised item class '%s'" % theClass)
            self.itemClass = nwItemClass.NO_CLASS
        return

    def setLayout(self, theLayout):
        if isinstance(theLayout, nwItemLayout):
            self.itemLayout = theLayout
        elif theLayout in nwItemLayout.__members__:
            self.itemLayout = nwItemLayout[theLayout]
        else:
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
            self.isExpanded = expState == True
        return

    ##
    #  Set Document Meta Data
    ##

    def setCharCount(self, theCount):
        self.charCount = checkInt(theCount,0)
        return

    def setWordCount(self, theCount):
        self.wordCount = checkInt(theCount,0)
        return

    def setParaCount(self, theCount):
        self.paraCount = checkInt(theCount,0)
        return

    def setCursorPos(self, thePosition):
        self.cursorPos = checkInt(thePosition,0)
        return

# END Class NWItem
