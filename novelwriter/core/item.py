"""
novelWriter – Project Item Class
================================
Data class for a project tree item

File History:
Created: 2018-10-27 [0.0.1]

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

from lxml import etree

from novelwriter.enum import nwItemType, nwItemClass, nwItemLayout
from novelwriter.common import (
    checkInt, isHandle, isItemClass, isItemLayout, isItemType
)
from novelwriter.constants import nwLabels, nwLists, trConst

logger = logging.getLogger(__name__)


class NWItem():

    def __init__(self, theProject):

        self.theProject = theProject

        self._name     = ""
        self._handle   = None
        self._parent   = None
        self._order    = 0
        self._type     = nwItemType.NO_TYPE
        self._class    = nwItemClass.NO_CLASS
        self._layout   = nwItemLayout.NO_LAYOUT
        self._status   = None
        self._expanded = False
        self._exported = True

        # Document Meta Data
        self._charCount = 0  # Current character count
        self._wordCount = 0  # Current word count
        self._paraCount = 0  # Current paragraph count
        self._cursorPos = 0  # Last cursor position
        self._initCount = 0  # Initial word count

        return

    def __repr__(self):
        return f"<NWItem handle={self._handle}, parent={self._parent}, name='{self._name}'>"

    def __bool__(self):
        return self._handle is not None

    ##
    #  Properties
    ##

    @property
    def itemName(self):
        return self._name

    @property
    def itemHandle(self):
        return self._handle

    @property
    def itemParent(self):
        return self._parent

    @property
    def itemOrder(self):
        return self._order

    @property
    def itemType(self):
        return self._type

    @property
    def itemClass(self):
        return self._class

    @property
    def itemLayout(self):
        return self._layout

    @property
    def itemStatus(self):
        return self._status

    @property
    def isExpanded(self):
        return self._expanded

    @property
    def isExported(self):
        return self._exported

    @property
    def charCount(self):
        return self._charCount

    @property
    def wordCount(self):
        return self._wordCount

    @property
    def paraCount(self):
        return self._paraCount

    @property
    def initCount(self):
        return self._initCount

    @property
    def cursorPos(self):
        return self._cursorPos

    ##
    #  XML Pack/Unpack
    ##

    def packXML(self, xParent):
        """Pack all the data in the class instance into an XML object.
        """
        xPack = etree.SubElement(xParent, "item", attrib={
            "handle": str(self._handle),
            "order":  str(self._order),
            "parent": str(self._parent),
        })
        self._subPack(xPack, "name",   text=str(self._name))
        self._subPack(xPack, "type",   text=str(self._type.name))
        self._subPack(xPack, "class",  text=str(self._class.name))
        self._subPack(xPack, "status", text=str(self._status))
        if self._type == nwItemType.FILE:
            self._subPack(xPack, "exported",  text=str(self._exported))
            self._subPack(xPack, "layout",    text=str(self._layout.name))
            self._subPack(xPack, "charCount", text=str(self._charCount), none=False)
            self._subPack(xPack, "wordCount", text=str(self._wordCount), none=False)
            self._subPack(xPack, "paraCount", text=str(self._paraCount), none=False)
            self._subPack(xPack, "cursorPos", text=str(self._cursorPos), none=False)
        else:
            self._subPack(xPack, "expanded", text=str(self._expanded))

        return

    def unpackXML(self, xItem):
        """Set the values from an XML entry of type 'item'.
        """
        if xItem.tag != "item":
            logger.error("XML entry is not an NWItem")
            return False

        if "handle" in xItem.attrib:
            self.setHandle(xItem.attrib["handle"])
        else:
            logger.error("XML item entry does not have a handle")
            return False

        self.setParent(xItem.attrib.get("parent", None))
        self.setOrder(xItem.attrib.get("order", 0))

        tmpStatus = ""
        for xValue in xItem:
            if xValue.tag == "name":
                self.setName(xValue.text)
            elif xValue.tag == "type":
                self.setType(xValue.text)
            elif xValue.tag == "class":
                self.setClass(xValue.text)
            elif xValue.tag == "layout":
                self.setLayout(xValue.text)
            elif xValue.tag == "status":
                tmpStatus = xValue.text
            elif xValue.tag == "expanded":
                self.setExpanded(xValue.text)
            elif xValue.tag == "exported":
                self.setExported(xValue.text)
            elif xValue.tag == "charCount":
                self.setCharCount(xValue.text)
            elif xValue.tag == "wordCount":
                self.setWordCount(xValue.text)
            elif xValue.tag == "paraCount":
                self.setParaCount(xValue.text)
            elif xValue.tag == "cursorPos":
                self.setCursorPos(xValue.text)
            else:
                # Sliently skip as we may otherwise cause orphaned
                # items if an otherwise valid file is opened by a
                # version of novelWriter that doesn't know the tag
                logger.error("Unknown tag '%s'", xValue.tag)

        # Guarantees that <status> is parsed after <class>
        self.setStatus(tmpStatus)

        return True

    @staticmethod
    def _subPack(xParent, name, attrib=None, text=None, none=True):
        """Pack the values into an XML element.
        """
        if not none and (text is None or text == "None"):
            return None
        xAttr = {} if attrib is None else attrib
        xSub = etree.SubElement(xParent, name, attrib=xAttr)
        if text is not None:
            xSub.text = text

        return

    ##
    #  Methods
    ##

    def describeMe(self, hLevel=None):
        """Return a string description of the item.
        """
        descKey = "none"
        if self._type == nwItemType.ROOT:
            descKey = "root"
        elif self._type == nwItemType.FOLDER:
            descKey = "folder"
        elif self._type == nwItemType.FILE:
            if self._layout == nwItemLayout.DOCUMENT:
                if hLevel == "H1":
                    descKey = "doc_h1"
                elif hLevel == "H2":
                    descKey = "doc_h2"
                elif hLevel == "H3":
                    descKey = "doc_h3"
                else:
                    descKey = "document"
            elif self._layout == nwItemLayout.NOTE:
                descKey = "note"

        return trConst(nwLabels.ITEM_DESCRIPTION.get(descKey, ""))

    ##
    #  Set Item Values
    ##

    def setName(self, theName):
        """Set the item name.
        """
        if isinstance(theName, str):
            self._name = theName.strip()
        else:
            self._name = ""
        return

    def setHandle(self, theHandle):
        """Set the item handle, and ensure it is valid.
        """
        if isHandle(theHandle):
            self._handle = theHandle
        else:
            self._handle = None
        return

    def setParent(self, theParent):
        """Set the parent handle, and ensure it is valid.
        """
        if theParent is None:
            self._parent = None
        elif isHandle(theParent):
            self._parent = theParent
        else:
            self._parent = None
        return

    def setOrder(self, theOrder):
        """Set the item order, and ensure that it is valid. This value
        is purely a meta value, and not actually used by novelWriter at
        the moment.
        """
        self._order = checkInt(theOrder, 0)
        return

    def setType(self, theType):
        """Set the item type from either a proper nwItemType, or set it
        from a string representing an nwItemType.
        """
        if isinstance(theType, nwItemType):
            self._type = theType
        elif isItemType(theType):
            self._type = nwItemType[theType]
        else:
            logger.error("Unrecognised item type '%s'", theType)
            self._type = nwItemType.NO_TYPE
        return

    def setClass(self, theClass):
        """Set the item class from either a proper nwItemClass, or set
        it from a string representing an nwItemClass.
        """
        if isinstance(theClass, nwItemClass):
            self._class = theClass
        elif isItemClass(theClass):
            self._class = nwItemClass[theClass]
        else:
            logger.error("Unrecognised item class '%s'", theClass)
            self._class = nwItemClass.NO_CLASS
        return

    def setLayout(self, theLayout):
        """Set the item layout from either a proper nwItemLayout, or set
        it from a string representing an nwItemLayout.
        """
        if isinstance(theLayout, nwItemLayout):
            self._layout = theLayout
        elif isItemLayout(theLayout):
            self._layout = nwItemLayout[theLayout]
        elif theLayout in nwLists.DEP_LAYOUT:
            self._layout = nwItemLayout.DOCUMENT
        else:
            logger.error("Unrecognised item layout '%s'", theLayout)
            self._layout = nwItemLayout.NO_LAYOUT
        return

    def setStatus(self, theStatus):
        """Set the item status by looking it up in the valid status
        items of the current project.
        """
        if self._class in nwLists.CLS_NOVEL:
            self._status = self.theProject.statusItems.checkEntry(theStatus)
        else:
            self._status = self.theProject.importItems.checkEntry(theStatus)
        return

    def setExpanded(self, expState):
        """Set the expanded status of an item in the project tree.
        """
        if isinstance(expState, str):
            self._expanded = (expState == str(True))
        else:
            self._expanded = (expState is True)
        return

    def setExported(self, expState):
        """Set the export flag.
        """
        if isinstance(expState, str):
            self._exported = (expState == str(True))
        else:
            self._exported = (expState is True)
        return

    ##
    #  Set Document Meta Data
    ##

    def setCharCount(self, theCount):
        """Set the character count, and ensure that it is an integer.
        """
        self._charCount = max(0, checkInt(theCount, 0))
        return

    def setWordCount(self, theCount):
        """Set the word count, and ensure that it is an integer.
        """
        self._wordCount = max(0, checkInt(theCount, 0))
        return

    def setParaCount(self, theCount):
        """Set the paragraph count, and ensure that it is an integer.
        """
        self._paraCount = max(0, checkInt(theCount, 0))
        return

    def setCursorPos(self, thePosition):
        """Set the cursor position, and ensure that it is an integer.
        """
        self._cursorPos = max(0, checkInt(thePosition, 0))
        return

    def saveInitialCount(self):
        """Save the initial word count.
        """
        self._initCount = self._wordCount
        return

# END Class NWItem
