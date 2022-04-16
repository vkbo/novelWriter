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
    checkInt, isHandle, isItemClass, isItemLayout, isItemType, simplified
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
        self._import   = None
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
    def itemImport(self):
        return self._import

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
        itemAttrib = {}
        itemAttrib["handle"] = str(self._handle)
        itemAttrib["parent"] = str(self._parent)
        itemAttrib["order"]  = str(self._order)
        itemAttrib["type"]   = str(self._type.name)
        itemAttrib["class"]  = str(self._class.name)
        if self._type == nwItemType.FILE:
            itemAttrib["layout"] = str(self._layout.name)

        metaAttrib = {}
        if self._type == nwItemType.FILE:
            metaAttrib["charCount"] = str(self._charCount)
            metaAttrib["wordCount"] = str(self._wordCount)
            metaAttrib["paraCount"] = str(self._paraCount)
            metaAttrib["cursorPos"] = str(self._cursorPos)
        else:
            metaAttrib["expanded"]  = str(self._expanded)

        nameAttrib = {}
        nameAttrib["status"] = str(self._status)
        nameAttrib["import"] = str(self._import)
        if self._type == nwItemType.FILE:
            nameAttrib["exported"]  = str(self._exported)

        xPack = etree.SubElement(xParent, "item", attrib=itemAttrib)
        self._subPack(xPack, "meta", attrib=metaAttrib)
        self._subPack(xPack, "name", text=str(self._name), attrib=nameAttrib)

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
        self.setType(xItem.attrib.get("type", nwItemType.NO_TYPE))
        self.setClass(xItem.attrib.get("class", nwItemClass.NO_CLASS))
        self.setLayout(xItem.attrib.get("layout", nwItemLayout.NO_LAYOUT))

        for xValue in xItem:
            if xValue.tag == "meta":
                self.setExpanded(xValue.attrib.get("expanded", False))
                self.setCharCount(xValue.attrib.get("charCount", 0))
                self.setWordCount(xValue.attrib.get("wordCount", 0))
                self.setParaCount(xValue.attrib.get("paraCount", 0))
                self.setCursorPos(xValue.attrib.get("cursorPos", 0))
            elif xValue.tag == "name":
                self.setName(xValue.text)
                self.setStatus(xValue.attrib.get("status", None))
                self.setImport(xValue.attrib.get("import", None))
                self.setExported(xValue.attrib.get("exported", True))

            # Legacy Format (1.3 and earlier)
            elif xValue.tag == "status":
                self.setImportStatus(xValue.text)
            elif xValue.tag == "type":
                self.setType(xValue.text)
            elif xValue.tag == "class":
                self.setClass(xValue.text)
            elif xValue.tag == "layout":
                self.setLayout(xValue.text)
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

    def getImportStatus(self):
        """Return the relevant importance or status label and icon for
        the current item based on its class.
        """
        if self._class in nwLists.CLS_NOVEL:
            stName = self.theProject.statusItems.name(self._status)
            stIcon = self.theProject.statusItems.icon(self._status)
        else:
            stName = self.theProject.importItems.name(self._import)
            stIcon = self.theProject.importItems.icon(self._import)
        return stName, stIcon

    def setImportStatus(self, theLabel):
        """Update the importance or status value based on class. This is
        a wrapper setter for setStatus and setImport.
        """
        if self._class in nwLists.CLS_NOVEL:
            self.setStatus(theLabel)
        else:
            self.setImport(theLabel)
        return

    ##
    #  Set Item Values
    ##

    def setName(self, name):
        """Set the item name.
        """
        if isinstance(name, str):
            self._name = simplified(name)
        else:
            self._name = ""
        return

    def setHandle(self, tHandle):
        """Set the item handle, and ensure it is valid.
        """
        if isHandle(tHandle):
            self._handle = tHandle
        else:
            self._handle = None
        return

    def setParent(self, pHandle):
        """Set the parent handle, and ensure it is valid.
        """
        if pHandle is None:
            self._parent = None
        elif isHandle(pHandle):
            self._parent = pHandle
        else:
            self._parent = None
        return

    def setOrder(self, order):
        """Set the item order, and ensure that it is valid. This value
        is purely a meta value, and not actually used by novelWriter at
        the moment.
        """
        self._order = checkInt(order, 0)
        return

    def setType(self, itemType):
        """Set the item type from either a proper nwItemType, or set it
        from a string representing an nwItemType.
        """
        if isinstance(itemType, nwItemType):
            self._type = itemType
        elif isItemType(itemType):
            self._type = nwItemType[itemType]
        else:
            logger.error("Unrecognised item type '%s'", itemType)
            self._type = nwItemType.NO_TYPE
        return

    def setClass(self, itemClass):
        """Set the item class from either a proper nwItemClass, or set
        it from a string representing an nwItemClass.
        """
        if isinstance(itemClass, nwItemClass):
            self._class = itemClass
        elif isItemClass(itemClass):
            self._class = nwItemClass[itemClass]
        else:
            logger.error("Unrecognised item class '%s'", itemClass)
            self._class = nwItemClass.NO_CLASS
        return

    def setLayout(self, itemLayout):
        """Set the item layout from either a proper nwItemLayout, or set
        it from a string representing an nwItemLayout.
        """
        if isinstance(itemLayout, nwItemLayout):
            self._layout = itemLayout
        elif isItemLayout(itemLayout):
            self._layout = nwItemLayout[itemLayout]
        elif itemLayout in nwLists.DEP_LAYOUT:
            self._layout = nwItemLayout.DOCUMENT
        else:
            logger.error("Unrecognised item layout '%s'", itemLayout)
            self._layout = nwItemLayout.NO_LAYOUT
        return

    def setStatus(self, itemStatus):
        """Set the item status by looking it up in the valid status
        items of the current project.
        """
        self._status = self.theProject.statusItems.check(itemStatus)
        return

    def setImport(self, itemImport):
        """Set the item importance by looking it up in the valid import
        items of the current project.
        """
        self._import = self.theProject.importItems.check(itemImport)
        return

    def setExpanded(self, state):
        """Set the expanded status of an item in the project tree.
        """
        if isinstance(state, str):
            self._expanded = (state == str(True))
        else:
            self._expanded = (state is True)
        return

    def setExported(self, state):
        """Set the export flag.
        """
        if isinstance(state, str):
            self._exported = (state == str(True))
        else:
            self._exported = (state is True)
        return

    ##
    #  Set Document Meta Data
    ##

    def setCharCount(self, count):
        """Set the character count, and ensure that it is an integer.
        """
        self._charCount = max(0, checkInt(count, 0))
        return

    def setWordCount(self, count):
        """Set the word count, and ensure that it is an integer.
        """
        self._wordCount = max(0, checkInt(count, 0))
        return

    def setParaCount(self, count):
        """Set the paragraph count, and ensure that it is an integer.
        """
        self._paraCount = max(0, checkInt(count, 0))
        return

    def setCursorPos(self, position):
        """Set the cursor position, and ensure that it is an integer.
        """
        self._cursorPos = max(0, checkInt(position, 0))
        return

    def saveInitialCount(self):
        """Save the initial word count.
        """
        self._initCount = self._wordCount
        return

# END Class NWItem
