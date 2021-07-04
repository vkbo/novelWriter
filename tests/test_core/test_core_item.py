"""
novelWriter – NWItem Class Tester
=================================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

import pytest

from lxml import etree

from nw.core import NWProject
from nw.core.item import NWItem
from nw.enum import nwItemClass, nwItemType, nwItemLayout


@pytest.mark.core
def testCoreItem_Setters(mockGUI):
    """Test all the simple setters for the NWItem class.
    """
    theProject = NWProject(mockGUI)
    theItem = NWItem(theProject)

    # Name
    theItem.setName("A Name")
    assert theItem.itemName == "A Name"
    theItem.setName("\t A Name   ")
    assert theItem.itemName == "A Name"
    theItem.setName(123)
    assert theItem.itemName == ""

    # Handle
    theItem.setHandle(123)
    assert theItem.itemHandle is None
    theItem.setHandle("0123456789abcdef")
    assert theItem.itemHandle is None
    theItem.setHandle("0123456789abg")
    assert theItem.itemHandle is None
    theItem.setHandle("0123456789abc")
    assert theItem.itemHandle == "0123456789abc"

    # Parent
    theItem.setParent(None)
    assert theItem.itemParent is None
    theItem.setParent(123)
    assert theItem.itemParent is None
    theItem.setParent("0123456789abcdef")
    assert theItem.itemParent is None
    theItem.setParent("0123456789abg")
    assert theItem.itemParent is None
    theItem.setParent("0123456789abc")
    assert theItem.itemParent == "0123456789abc"

    # Order
    theItem.setOrder(None)
    assert theItem.itemOrder == 0
    theItem.setOrder("1")
    assert theItem.itemOrder == 1
    theItem.setOrder(1)
    assert theItem.itemOrder == 1

    # Status
    theItem.setStatus("Nonsense")
    assert theItem.itemStatus == "New"
    theItem.setStatus("New")
    assert theItem.itemStatus == "New"
    theItem.setStatus("Minor")
    assert theItem.itemStatus == "Minor"
    theItem.setStatus("Major")
    assert theItem.itemStatus == "Major"
    theItem.setStatus("Main")
    assert theItem.itemStatus == "Main"

    # Importance
    theItem.itemClass = nwItemClass.NOVEL
    theItem.setStatus("Nonsense")
    assert theItem.itemStatus == "New"
    theItem.setStatus("New")
    assert theItem.itemStatus == "New"
    theItem.setStatus("Note")
    assert theItem.itemStatus == "Note"
    theItem.setStatus("Draft")
    assert theItem.itemStatus == "Draft"
    theItem.setStatus("Finished")
    assert theItem.itemStatus == "Finished"

    # Expanded
    theItem.setExpanded(8)
    assert not theItem.isExpanded
    theItem.setExpanded(None)
    assert not theItem.isExpanded
    theItem.setExpanded("None")
    assert not theItem.isExpanded
    theItem.setExpanded("What?")
    assert not theItem.isExpanded
    theItem.setExpanded("True")
    assert theItem.isExpanded
    theItem.setExpanded(True)
    assert theItem.isExpanded

    # Exported
    theItem.setExported(8)
    assert not theItem.isExported
    theItem.setExported(None)
    assert not theItem.isExported
    theItem.setExported("None")
    assert not theItem.isExported
    theItem.setExported("What?")
    assert not theItem.isExported
    theItem.setExported("True")
    assert theItem.isExported
    theItem.setExported(True)
    assert theItem.isExported

    # CharCount
    theItem.setCharCount(None)
    assert theItem.charCount == 0
    theItem.setCharCount("1")
    assert theItem.charCount == 1
    theItem.setCharCount(1)
    assert theItem.charCount == 1

    # WordCount
    theItem.setWordCount(None)
    assert theItem.wordCount == 0
    theItem.setWordCount("1")
    assert theItem.wordCount == 1
    theItem.setWordCount(1)
    assert theItem.wordCount == 1

    # ParaCount
    theItem.setParaCount(None)
    assert theItem.paraCount == 0
    theItem.setParaCount("1")
    assert theItem.paraCount == 1
    theItem.setParaCount(1)
    assert theItem.paraCount == 1

    # CursorPos
    theItem.setCursorPos(None)
    assert theItem.cursorPos == 0
    theItem.setCursorPos("1")
    assert theItem.cursorPos == 1
    theItem.setCursorPos(1)
    assert theItem.cursorPos == 1

    # Initial Count
    theItem.setWordCount(234)
    theItem.saveInitialCount()
    assert theItem.initCount == 234

# END Test testCoreItem_Setters


@pytest.mark.core
def testCoreItem_TypeSetter(mockGUI):
    """Test the setter for all the nwItemType values for the NWItem
    class.
    """
    theProject = NWProject(mockGUI)
    theItem = NWItem(theProject)

    # Type
    theItem.setType(None)
    assert theItem.itemType == nwItemType.NO_TYPE
    theItem.setType("NONSENSE")
    assert theItem.itemType == nwItemType.NO_TYPE
    theItem.setType("NO_TYPE")
    assert theItem.itemType == nwItemType.NO_TYPE
    theItem.setType("ROOT")
    assert theItem.itemType == nwItemType.ROOT
    theItem.setType("FOLDER")
    assert theItem.itemType == nwItemType.FOLDER
    theItem.setType("FILE")
    assert theItem.itemType == nwItemType.FILE
    theItem.setType("TRASH")
    assert theItem.itemType == nwItemType.TRASH
    theItem.setType(nwItemType.ROOT)
    assert theItem.itemType == nwItemType.ROOT

# END Test testCoreItem_TypeSetter


@pytest.mark.core
def testCoreItem_ClassSetter(mockGUI):
    """Test the setter for all the nwItemClass values for the NWItem
    class.
    """
    theProject = NWProject(mockGUI)
    theItem = NWItem(theProject)

    # Class
    theItem.setClass(None)
    assert theItem.itemClass == nwItemClass.NO_CLASS
    theItem.setClass("NONSENSE")
    assert theItem.itemClass == nwItemClass.NO_CLASS
    theItem.setClass("NO_CLASS")
    assert theItem.itemClass == nwItemClass.NO_CLASS
    theItem.setClass("NOVEL")
    assert theItem.itemClass == nwItemClass.NOVEL
    theItem.setClass("PLOT")
    assert theItem.itemClass == nwItemClass.PLOT
    theItem.setClass("CHARACTER")
    assert theItem.itemClass == nwItemClass.CHARACTER
    theItem.setClass("WORLD")
    assert theItem.itemClass == nwItemClass.WORLD
    theItem.setClass("TIMELINE")
    assert theItem.itemClass == nwItemClass.TIMELINE
    theItem.setClass("OBJECT")
    assert theItem.itemClass == nwItemClass.OBJECT
    theItem.setClass("ENTITY")
    assert theItem.itemClass == nwItemClass.ENTITY
    theItem.setClass("CUSTOM")
    assert theItem.itemClass == nwItemClass.CUSTOM
    theItem.setClass("ARCHIVE")
    assert theItem.itemClass == nwItemClass.ARCHIVE
    theItem.setClass("TRASH")
    assert theItem.itemClass == nwItemClass.TRASH
    theItem.setClass(nwItemClass.NOVEL)
    assert theItem.itemClass == nwItemClass.NOVEL

# END Test testCoreItem_ClassSetter


@pytest.mark.core
def testCoreItem_LayoutSetter(mockGUI):
    """Test the setter for all the nwItemLayout values for the NWItem
    class.
    """
    theProject = NWProject(mockGUI)
    theItem = NWItem(theProject)

    # Layout
    theItem.setLayout(None)
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT
    theItem.setLayout("NONSENSE")
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT
    theItem.setLayout("NO_LAYOUT")
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT
    theItem.setLayout("TITLE")
    assert theItem.itemLayout == nwItemLayout.TITLE
    theItem.setLayout("BOOK")
    assert theItem.itemLayout == nwItemLayout.BOOK
    theItem.setLayout("PAGE")
    assert theItem.itemLayout == nwItemLayout.PAGE
    theItem.setLayout("PARTITION")
    assert theItem.itemLayout == nwItemLayout.PARTITION
    theItem.setLayout("UNNUMBERED")
    assert theItem.itemLayout == nwItemLayout.UNNUMBERED
    theItem.setLayout("CHAPTER")
    assert theItem.itemLayout == nwItemLayout.CHAPTER
    theItem.setLayout("SCENE")
    assert theItem.itemLayout == nwItemLayout.SCENE
    theItem.setLayout("NOTE")
    assert theItem.itemLayout == nwItemLayout.NOTE
    theItem.setLayout(nwItemLayout.NOTE)
    assert theItem.itemLayout == nwItemLayout.NOTE

# END Test testCoreItem_LayoutSetter


@pytest.mark.core
def testCoreItem_XMLPackUnpack(mockGUI, caplog):
    """Test packing and unpacking XML objects for the NWItem class.
    """
    theProject = NWProject(mockGUI)
    nwXML = etree.Element("novelWriterXML")

    # File
    # ====

    theItem = NWItem(theProject)
    theItem.setHandle("0123456789abc")
    theItem.setParent("0123456789abc")
    theItem.setOrder(1)
    theItem.setName("A Name")
    theItem.setClass("NOVEL")
    theItem.setType("FILE")
    theItem.setStatus("Main")
    theItem.setLayout("NOTE")
    theItem.setExported(False)
    theItem.setParaCount(3)
    theItem.setWordCount(5)
    theItem.setCharCount(7)
    theItem.setCursorPos(11)

    # Pack
    xContent = etree.SubElement(nwXML, "content")
    theItem.packXML(xContent)
    assert etree.tostring(xContent, pretty_print=False, encoding="utf-8") == (
        b"<content>"
        b"<item handle=\"0123456789abc\" order=\"1\" parent=\"0123456789abc\">"
        b"<name>A Name</name><type>FILE</type><class>NOVEL</class><status>New</status>"
        b"<exported>False</exported><layout>NOTE</layout><charCount>7</charCount>"
        b"<wordCount>5</wordCount><paraCount>3</paraCount><cursorPos>11</cursorPos></item>"
        b"</content>"
    )

    # Unpack
    theItem = NWItem(theProject)
    assert theItem.unpackXML(xContent[0])
    assert theItem.itemHandle == "0123456789abc"
    assert theItem.itemParent == "0123456789abc"
    assert theItem.itemOrder == 1
    assert theItem.isExported is False
    assert theItem.paraCount == 3
    assert theItem.wordCount == 5
    assert theItem.charCount == 7
    assert theItem.cursorPos == 11
    assert theItem.itemClass == nwItemClass.NOVEL
    assert theItem.itemType == nwItemType.FILE
    assert theItem.itemLayout == nwItemLayout.NOTE

    # Folder
    # ======

    theItem = NWItem(theProject)
    theItem.setHandle("0123456789abc")
    theItem.setParent("0123456789abc")
    theItem.setOrder(1)
    theItem.setName("A Name")
    theItem.setClass("NOVEL")
    theItem.setType("FOLDER")
    theItem.setStatus("Main")
    theItem.setLayout("NOTE")
    theItem.setExpanded(True)
    theItem.setExported(False)
    theItem.setParaCount(3)
    theItem.setWordCount(5)
    theItem.setCharCount(7)
    theItem.setCursorPos(11)

    # Pack
    xContent = etree.SubElement(nwXML, "content")
    theItem.packXML(xContent)
    assert etree.tostring(xContent, pretty_print=False, encoding="utf-8") == (
        b"<content>"
        b"<item handle=\"0123456789abc\" order=\"1\" parent=\"0123456789abc\">"
        b"<name>A Name</name><type>FOLDER</type><class>NOVEL</class><status>New</status>"
        b"<expanded>True</expanded></item>"
        b"</content>"
    )

    # Unpack
    theItem = NWItem(theProject)
    assert theItem.unpackXML(xContent[0])
    assert theItem.itemHandle == "0123456789abc"
    assert theItem.itemParent == "0123456789abc"
    assert theItem.itemOrder == 1
    assert theItem.isExpanded is True
    assert theItem.isExported is True
    assert theItem.paraCount == 0
    assert theItem.wordCount == 0
    assert theItem.charCount == 0
    assert theItem.cursorPos == 0
    assert theItem.itemClass == nwItemClass.NOVEL
    assert theItem.itemType == nwItemType.FOLDER
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT

    # Errors
    # ======

    # Not an Item
    mockXml = etree.SubElement(nwXML, "stuff")
    assert theItem.unpackXML(mockXml) is False

    # Item without Handle
    mockXml = etree.SubElement(nwXML, "item", attrib={"stuff": "nah"})
    assert theItem.unpackXML(mockXml) is False

    # Item with Invalid SubElement is Accepted w/Error
    mockXml = etree.SubElement(nwXML, "item", attrib={"handle": "0123456789abc"})
    xParam = etree.SubElement(mockXml, "invalid")
    xParam.text = "stuff"
    caplog.clear()
    assert theItem.unpackXML(mockXml) is True
    assert "Unknown tag 'invalid'" in caplog.text

    # Pack Valid Item
    mockXml = etree.SubElement(nwXML, "group")
    theItem._subPack(mockXml, "subGroup", {"one": "two"}, "value", False)
    assert etree.tostring(mockXml, pretty_print=False, encoding="utf-8") == (
        b"<group><subGroup one=\"two\">value</subGroup></group>"
    )

    # Pack Not Allowed None
    mockXml = etree.SubElement(nwXML, "group")
    assert theItem._subPack(mockXml, "subGroup", {}, None, False) is None
    assert theItem._subPack(mockXml, "subGroup", {}, "None", False) is None
    assert etree.tostring(mockXml, pretty_print=False, encoding="utf-8") == (
        b"<group/>"
    )

# END Test testCoreItem_XMLPackUnpack
