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

from __future__ import annotations

import sys

from typing import TYPE_CHECKING

from lxml import etree

from novelwriter.enum import nwItemType, nwItemClass, nwItemLayout
from novelwriter.common import (
    checkInt, isHandle, isItemClass, isItemLayout, isItemType, simplified
)
from novelwriter.constants import nwLabels, trConst
from novelwriter.logging import getLogger, VerboseLogger

if TYPE_CHECKING:
    if sys.version_info >= (3, 10):
        from typing import Literal
    else:
        from typing_extensions import Literal

    from PyQt5.QtGui import QIcon
    from novelwriter.core.project import NWProject

logger: VerboseLogger = getLogger(__name__)


class NWItem():

    def __init__(self, theProject) -> None:

        self.theProject: NWProject = theProject

        self._name: str     = ""
        self._handle: str | None = None
        self._parent: str | None = None
        self._root:   str | None = None
        self._order: int    = 0
        self._type: nwItemType     = nwItemType.NO_TYPE
        self._class: nwItemClass   = nwItemClass.NO_CLASS
        self._layout: nwItemLayout = nwItemLayout.NO_LAYOUT
        self._status: str | None = None
        self._import: str | None = None
        self._expanded: bool = False
        self._exported: bool = True

        # Document Meta Data
        self._charCount: int = 0  # Current character count
        self._wordCount: int = 0  # Current word count
        self._paraCount: int = 0  # Current paragraph count
        self._cursorPos: int = 0  # Last cursor position
        self._initCount: int = 0  # Initial word count

        return

    def __repr__(self) -> str:
        return f"<NWItem handle={self._handle}, parent={self._parent}, name='{self._name}'>"

    def __bool__(self) -> bool:
        return self._handle is not None

    ##
    #  Properties
    ##

    @property
    def itemName(self) -> str:
        return self._name

    @property
    def itemHandle(self) -> str | None:
        return self._handle

    @property
    def itemParent(self) -> str | None:
        return self._parent

    @property
    def itemRoot(self) -> str | None:
        return self._root

    @property
    def itemOrder(self) -> int:
        return self._order

    @property
    def itemType(self) -> nwItemType:
        return self._type

    @property
    def itemClass(self) -> nwItemClass:
        return self._class

    @property
    def itemLayout(self) -> nwItemLayout:
        return self._layout

    @property
    def itemStatus(self) -> str | None:
        return self._status

    @property
    def itemImport(self) -> str | None:
        return self._import

    @property
    def isExpanded(self) -> bool:
        return self._expanded

    @property
    def isExported(self) -> bool:
        return self._exported

    @property
    def charCount(self) -> int:
        return self._charCount

    @property
    def wordCount(self) -> int:
        return self._wordCount

    @property
    def paraCount(self) -> int:
        return self._paraCount

    @property
    def initCount(self) -> int:
        return self._initCount

    @property
    def cursorPos(self) -> int:
        return self._cursorPos

    ##
    #  XML Pack/Unpack
    ##

    def packXML(self, xParent: etree._Element) -> None:
        """Pack all the data in the class instance into an XML object.
        """
        itemAttrib: dict[str, str] = {}
        itemAttrib["handle"] = str(self._handle)
        itemAttrib["parent"] = str(self._parent)
        itemAttrib["root"]   = str(self._root)
        itemAttrib["order"]  = str(self._order)
        itemAttrib["type"]   = str(self._type.name)
        itemAttrib["class"]  = str(self._class.name)
        if self._type == nwItemType.FILE:
            itemAttrib["layout"] = str(self._layout.name)

        metaAttrib: dict[str, str] = {}
        metaAttrib["expanded"] = str(self._expanded)
        if self._type == nwItemType.FILE:
            metaAttrib["charCount"] = str(self._charCount)
            metaAttrib["wordCount"] = str(self._wordCount)
            metaAttrib["paraCount"] = str(self._paraCount)
            metaAttrib["cursorPos"] = str(self._cursorPos)

        nameAttrib: dict[str, str] = {}
        nameAttrib["status"] = str(self._status)
        nameAttrib["import"] = str(self._import)
        if self._type == nwItemType.FILE:
            nameAttrib["exported"] = str(self._exported)

        xPack: etree._Element = etree.SubElement(xParent, "item", attrib=itemAttrib)
        self._subPack(xPack, "meta", attrib=metaAttrib)
        self._subPack(xPack, "name", text=str(self._name), attrib=nameAttrib)

        return

    def unpackXML(self, xItem: etree._Element) -> bool:
        """Set the values from an XML entry of type 'item'.
        """
        if xItem.tag != "item":
            logger.error("XML entry is not an NWItem")
            return False

        if "handle" in xItem.attrib:
            self.setHandle(str(xItem.attrib["handle"]))
        else:
            logger.error("XML item entry does not have a handle")
            return False

        self.setParent(xItem.attrib.get("parent", None))                    # type: ignore
        self.setRoot(xItem.attrib.get("root", None))                        # type: ignore
        self.setOrder(xItem.attrib.get("order", 0))                         # type: ignore
        self.setType(xItem.attrib.get("type", nwItemType.NO_TYPE))          # type: ignore
        self.setClass(xItem.attrib.get("class", nwItemClass.NO_CLASS))      # type: ignore
        self.setLayout(xItem.attrib.get("layout", nwItemLayout.NO_LAYOUT))  # type: ignore

        for xValue in xItem:
            if xValue.tag == "meta":
                self.setExpanded(xValue.attrib.get("expanded", False))  # type: ignore
                self.setCharCount(xValue.attrib.get("charCount", 0))    # type: ignore
                self.setWordCount(xValue.attrib.get("wordCount", 0))    # type: ignore
                self.setParaCount(xValue.attrib.get("paraCount", 0))    # type: ignore
                self.setCursorPos(xValue.attrib.get("cursorPos", 0))    # type: ignore
            elif xValue.tag == "name":
                self.setName(xValue.text)
                self.setStatus(xValue.attrib.get("status", None))      # type: ignore
                self.setImport(xValue.attrib.get("import", None))      # type: ignore
                self.setExported(xValue.attrib.get("exported", True))  # type: ignore

            # Legacy Format (1.3 and earlier)
            elif xValue.tag == "status":
                self.setImportStatus(xValue.text)
            elif xValue.tag == "type":
                self.setType(str(xValue.text))
            elif xValue.tag == "class":
                self.setClass(xValue.text or "")
            elif xValue.tag == "layout":
                self.setLayout(xValue.text or "")
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

        # Make some checks to ensure consistency
        if self._type == nwItemType.ROOT:
            self._root = self._handle  # Root items are their own ancestor
            self._parent = None        # Root items cannot have a parent

        if self._type != nwItemType.FILE:
            self._charCount = 0  # Only set for files
            self._wordCount = 0  # Only set for files
            self._paraCount = 0  # Only set for files
            self._cursorPos = 0  # Only set for files

        return True

    @staticmethod
    def _subPack(
        xParent: etree._Element, name,
        attrib: dict[str, str] | None = None,
        text: str | None = None,
        none: bool = True
    ) -> None:
        """Pack the values into an XML element.
        """
        if not none and (text is None or text == "None"):
            return None
        xAttr: dict[str, str] = {} if attrib is None else attrib
        xSub: etree._Element = etree.SubElement(xParent, name, attrib=xAttr)
        if text is not None:
            xSub.text = text

        return

    ##
    #  Lookup Methods
    ##

    def describeMe(self, hLevel: Literal["H1", "H2", "H3"] | None = None) -> str:
        """Return a string description of the item.
        """
        descKey: str = "none"
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

    def isNovelLike(self) -> bool:
        """Returns true if the item is of a novel-like class.
        """
        return self._class in (nwItemClass.NOVEL, nwItemClass.ARCHIVE)

    def documentAllowed(self) -> bool:
        """Returns true if the item is allowed to be of document layout.
        """
        return self._class in (nwItemClass.NOVEL, nwItemClass.ARCHIVE, nwItemClass.TRASH)

    def isInactive(self) -> bool:
        """Returns true if the item is in an inactive class.
        """
        return self._class in (nwItemClass.NO_CLASS, nwItemClass.ARCHIVE, nwItemClass.TRASH)

    def getImportStatus(self) -> tuple[str, QIcon]:
        """Return the relevant importance or status label and icon for
        the current item based on its class.
        """
        if self.isNovelLike() and self.theProject.statusItems is not None:
            assert self._status is not None
            stName: str = self.theProject.statusItems.name(self._status)
            stIcon: QIcon = self.theProject.statusItems.icon(self._status)
        elif self.theProject.importItems is not None:
            assert self._import is not None
            stName: str = self.theProject.importItems.name(self._import)
            stIcon: QIcon = self.theProject.importItems.icon(self._import)
        else:
            raise Exception("This is a bug!")
        return stName, stIcon

    ##
    #  Special Setters
    ##

    def setImportStatus(self, value: str | None) -> None:
        """Update the importance or status value based on class. This is
        a wrapper setter for setStatus and setImport.
        """
        if self.isNovelLike():
            self.setStatus(value)
        else:
            self.setImport(value)
        return

    def setClassDefaults(self, itemClass: str | nwItemClass) -> None:
        """Set the default values based on the item's class and the
        project settings.
        """
        if self._parent is not None:
            # Only update for child items
            self.setClass(itemClass)

        if self._layout == nwItemLayout.NO_LAYOUT:
            # If no layout is set, pick one
            if self.isNovelLike():
                self._layout = nwItemLayout.DOCUMENT
            else:
                self._layout = nwItemLayout.NOTE
        elif not self.documentAllowed():
            # Change layout to note if it is not in an allowed folder
            self._layout = nwItemLayout.NOTE

        if self._status is None:
            self.setStatus("New")  # This forces a default value lookup

        if self._import is None:
            self.setImport("New")  # This forces a default value lookup

        return

    ##
    #  Set Item Values
    ##

    def setName(self, name: str | None) -> None:
        """Set the item name.
        """
        if isinstance(name, str):
            self._name = simplified(name)
        else:
            self._name = ""
        return

    def setHandle(self, handle: str | None) -> None:
        """Set the item handle, and ensure it is valid.
        """
        if isHandle(handle):
            self._handle = handle
        else:
            self._handle = None
        return

    def setParent(self, handle: str | None) -> None:
        """Set the parent handle, and ensure it is valid.
        """
        if handle is None:
            self._parent = None
        elif isHandle(handle):
            self._parent = handle
        else:
            self._parent = None
        return

    def setRoot(self, handle:  str | None) -> None:
        """Set the root handle, and ensure it is valid.
        """
        if handle is None:
            self._root = None
        elif isHandle(handle):
            self._root = handle
        else:
            self._root = None
        return

    def setOrder(self, order: int | None) -> None:
        """Set the item order, and ensure that it is valid. This value
        is purely a meta value, and not actually used by novelWriter at
        the moment.
        """
        self._order = checkInt(order, 0)
        return

    def setType(self, value: str | nwItemType) -> None:
        """Set the item type from either a proper nwItemType, or set it
        from a string representing an nwItemType.
        """
        if isinstance(value, nwItemType):
            self._type = value
        elif isItemType(value):
            self._type = nwItemType[value]
        elif value == "TRASH":
            self._type = nwItemType.ROOT
        else:
            logger.error("Unrecognised item type '%s'", value)
            self._type = nwItemType.NO_TYPE
        return

    def setClass(self, value: str | nwItemClass) -> None:
        """Set the item class from either a proper nwItemClass, or set
        it from a string representing an nwItemClass.
        """
        if isinstance(value, nwItemClass):
            self._class = value
        elif isItemClass(value):
            self._class = nwItemClass[value]
        else:
            logger.error("Unrecognised item class '%s'", value)
            self._class = nwItemClass.NO_CLASS
        return

    def setLayout(self, value: str | nwItemLayout) -> None:
        """Set the item layout from either a proper nwItemLayout, or set
        it from a string representing an nwItemLayout.
        """
        if isinstance(value, nwItemLayout):
            self._layout = value
        elif isItemLayout(value):
            self._layout = nwItemLayout[value]
        elif value in ("TITLE", "PAGE", "BOOK", "PARTITION", "UNNUMBERED", "CHAPTER", "SCENE"):
            self._layout = nwItemLayout.DOCUMENT
        else:
            logger.error("Unrecognised item layout '%s'", value)
            self._layout = nwItemLayout.NO_LAYOUT
        return

    def setStatus(self, value: str | None) -> None:
        """Set the item status by looking it up in the valid status
        items of the current project.
        """
        assert self.theProject.statusItems is not None
        self._status = self.theProject.statusItems.check(value)
        return

    def setImport(self, value: str | None) -> None:
        """Set the item importance by looking it up in the valid import
        items of the current project.
        """
        assert self.theProject.importItems is not None
        self._import = self.theProject.importItems.check(value)
        return

    def setExpanded(self, state: str | bool | None) -> None:
        """Set the expanded status of an item in the project tree.
        """
        if isinstance(state, str):
            self._expanded = (state == str(True))
        else:
            self._expanded = (state is True)
        return

    def setExported(self, state: str | bool | None) -> None:
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

    def setCharCount(self, count: str | int | None) -> None:
        """Set the character count, and ensure that it is an integer.
        """
        self._charCount = max(0, checkInt(count, 0))
        return

    def setWordCount(self, count: str | int | None) -> None:
        """Set the word count, and ensure that it is an integer.
        """
        self._wordCount = max(0, checkInt(count, 0))
        return

    def setParaCount(self, count: str | int | None) -> None:
        """Set the paragraph count, and ensure that it is an integer.
        """
        self._paraCount = max(0, checkInt(count, 0))
        return

    def setCursorPos(self, position: str | int | None) -> None:
        """Set the cursor position, and ensure that it is an integer.
        """
        self._cursorPos = max(0, checkInt(position, 0))
        return

    def saveInitialCount(self) -> None:
        """Save the initial word count.
        """
        self._initCount = self._wordCount
        return

# END Class NWItem
