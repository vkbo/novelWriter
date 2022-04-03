"""
novelWriter – NWItem Class Tester
=================================

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

import pytest

from lxml import etree

from PyQt5.QtGui import QIcon

from novelwriter.core import NWProject
from novelwriter.core.item import NWItem
from novelwriter.enum import nwItemClass, nwItemType, nwItemLayout


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

    # Importance
    theItem._class = nwItemClass.CHARACTER
    theItem.setImport("Nonsense")
    assert theItem.itemImport == "New"
    theItem.setImport("New")
    assert theItem.itemImport == "New"
    theItem.setImport("Minor")
    assert theItem.itemImport == "Minor"
    theItem.setImport("Major")
    assert theItem.itemImport == "Major"
    theItem.setImport("Main")
    assert theItem.itemImport == "Main"

    # Status
    theItem._class = nwItemClass.NOVEL
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

    # Status/Importance Wrapper
    theItem._class = nwItemClass.CHARACTER
    theItem.setImportStatus("New")
    assert theItem.itemImport == "New"
    theItem.setImportStatus("Minor")
    assert theItem.itemImport == "Minor"
    theItem.setImportStatus("Note")
    assert theItem.itemImport == "New"
    theItem.setImportStatus("Draft")
    assert theItem.itemImport == "New"

    theItem._class = nwItemClass.NOVEL
    theItem.setImportStatus("New")
    assert theItem.itemStatus == "New"
    theItem.setImportStatus("Minor")
    assert theItem.itemStatus == "New"
    theItem.setImportStatus("Note")
    assert theItem.itemStatus == "Note"
    theItem.setImportStatus("Draft")
    assert theItem.itemStatus == "Draft"

    # Expanded
    theItem.setExpanded(8)
    assert theItem.isExpanded is False
    theItem.setExpanded(None)
    assert theItem.isExpanded is False
    theItem.setExpanded("None")
    assert theItem.isExpanded is False
    theItem.setExpanded("What?")
    assert theItem.isExpanded is False
    theItem.setExpanded("True")
    assert theItem.isExpanded is True
    theItem.setExpanded(True)
    assert theItem.isExpanded is True

    # Exported
    theItem.setExported(8)
    assert theItem.isExported is False
    theItem.setExported(None)
    assert theItem.isExported is False
    theItem.setExported("None")
    assert theItem.isExported is False
    theItem.setExported("What?")
    assert theItem.isExported is False
    theItem.setExported("True")
    assert theItem.isExported is True
    theItem.setExported(True)
    assert theItem.isExported is True

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
def testCoreItem_Methods(mockGUI):
    """Test the simple methods of the NWItem class.
    """
    theProject = NWProject(mockGUI)
    theItem = NWItem(theProject)

    # Describe Me
    # ===========

    assert theItem.describeMe() == "None"

    theItem.setType("ROOT")
    assert theItem.describeMe() == "Root Folder"

    theItem.setType("FOLDER")
    assert theItem.describeMe() == "Folder"

    theItem.setType("FILE")
    theItem.setLayout("DOCUMENT")
    assert theItem.describeMe() == "Novel Document"
    assert theItem.describeMe("H0") == "Novel Document"
    assert theItem.describeMe("H1") == "Novel Title Page"
    assert theItem.describeMe("H2") == "Novel Chapter"
    assert theItem.describeMe("H3") == "Novel Scene"
    assert theItem.describeMe("H4") == "Novel Document"

    theItem.setLayout("NOTE")
    assert theItem.describeMe() == "Project Note"

    # Status + Icon
    # =============
    theItem.setType("FILE")
    theItem.setStatus("Note")
    theItem.setImport("Minor")

    theItem.setClass("NOVEL")
    stT, stI = theItem.getImportStatus()
    assert stT == "Note"
    assert isinstance(stI, QIcon)

    theItem.setClass("CHARACTER")
    stT, stI = theItem.getImportStatus()
    assert stT == "Minor"
    assert isinstance(stI, QIcon)

    # Representation
    # ==============

    theItem.setName("New Item")
    theItem.setHandle("1234567890abc")
    theItem.setParent("4567890abcdef")
    assert repr(theItem) == "<NWItem handle=1234567890abc, parent=4567890abcdef, name='New Item'>"

    # Truthiness
    # ==========

    assert bool(theItem) is True
    theItem.setHandle(None)
    assert bool(theItem) is False

# END Test testCoreItem_Methods


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

    # Faulty Layouts
    theItem.setLayout(None)
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT
    theItem.setLayout("NONSENSE")
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT

    # Current Layouts
    theItem.setLayout("NO_LAYOUT")
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT
    theItem.setLayout("DOCUMENT")
    assert theItem.itemLayout == nwItemLayout.DOCUMENT
    theItem.setLayout("NOTE")
    assert theItem.itemLayout == nwItemLayout.NOTE

    # Alternatives
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
        b'<content>'
        b'<item handle="0123456789abc" parent="0123456789abc" order="1" type="FILE" class="NOVEL" '
        b'layout="NOTE"><meta charCount="7" wordCount="5" paraCount="3" cursorPos="11"/>'
        b'<name status="New" import="None" exported="False">A Name</name></item>'
        b'</content>'
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
        b'<content>'
        b'<item handle="0123456789abc" parent="0123456789abc" order="1" type="FOLDER" '
        b'class="NOVEL"><meta expanded="True"/><name status="New" import="None">A Name</name>'
        b'</item>'
        b'</content>'
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


@pytest.mark.core
def testCoreItem_ConvertFromFmt12(mockGUI):
    """Test the setter for all the nwItemLayout values for the NWItem
    class using the class names that were present in file format 1.2.
    """
    theProject = NWProject(mockGUI)
    theItem = NWItem(theProject)

    # Deprecated Layouts
    theItem.setLayout("TITLE")
    assert theItem.itemLayout == nwItemLayout.DOCUMENT
    theItem.setLayout("PAGE")
    assert theItem.itemLayout == nwItemLayout.DOCUMENT
    theItem.setLayout("BOOK")
    assert theItem.itemLayout == nwItemLayout.DOCUMENT
    theItem.setLayout("PARTITION")
    assert theItem.itemLayout == nwItemLayout.DOCUMENT
    theItem.setLayout("UNNUMBERED")
    assert theItem.itemLayout == nwItemLayout.DOCUMENT
    theItem.setLayout("CHAPTER")
    assert theItem.itemLayout == nwItemLayout.DOCUMENT
    theItem.setLayout("SCENE")
    assert theItem.itemLayout == nwItemLayout.DOCUMENT
    theItem.setLayout("MUMBOJUMBO")
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT

# END Test testCoreItem_ConvertFromFmt12


@pytest.mark.core
def testCoreItem_ConvertFromFmt13(mockGUI):
    """Test packing and unpacking XML objects for the NWItem class from
    format version 1.3
    """
    theProject = NWProject(mockGUI)

    # Make Version 1.3 XML
    nwXML = etree.Element("novelWriterXML")
    xContent = etree.SubElement(nwXML, "content")

    # Folder
    xPack = etree.SubElement(xContent, "item", attrib={
        "handle": "a000000000001",
        "order":  "1",
        "parent": "b000000000001",
    })
    NWItem._subPack(xPack, "name",     text="Folder")
    NWItem._subPack(xPack, "type",     text="FOLDER")
    NWItem._subPack(xPack, "class",    text="NOVEL")
    NWItem._subPack(xPack, "status",   text="New")
    NWItem._subPack(xPack, "expanded", text="True")

    # Unpack Folder
    theItem = NWItem(theProject)
    theItem.unpackXML(xContent[0])
    assert theItem.itemHandle == "a000000000001"
    assert theItem.itemParent == "b000000000001"
    assert theItem.itemOrder == 1
    assert theItem.isExpanded is True
    assert theItem.isExported is True
    assert theItem.charCount == 0
    assert theItem.wordCount == 0
    assert theItem.paraCount == 0
    assert theItem.cursorPos == 0
    assert theItem.itemClass == nwItemClass.NOVEL
    assert theItem.itemType == nwItemType.FOLDER
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT

    # File
    xPack = etree.SubElement(xContent, "item", attrib={
        "handle": "c000000000001",
        "order":  "2",
        "parent": "a000000000001",
    })
    NWItem._subPack(xPack, "name",      text="Scene")
    NWItem._subPack(xPack, "type",      text="FILE")
    NWItem._subPack(xPack, "class",     text="NOVEL")
    NWItem._subPack(xPack, "status",    text="New")
    NWItem._subPack(xPack, "exported",  text="True")
    NWItem._subPack(xPack, "layout",    text="DOCUMENT")
    NWItem._subPack(xPack, "charCount", text="600")
    NWItem._subPack(xPack, "wordCount", text="100")
    NWItem._subPack(xPack, "paraCount", text="6")
    NWItem._subPack(xPack, "cursorPos", text="50")

    # Unpack File
    theItem = NWItem(theProject)
    theItem.unpackXML(xContent[1])
    assert theItem.itemHandle == "c000000000001"
    assert theItem.itemParent == "a000000000001"
    assert theItem.itemOrder == 2
    assert theItem.isExpanded is False
    assert theItem.isExported is True
    assert theItem.charCount == 600
    assert theItem.wordCount == 100
    assert theItem.paraCount == 6
    assert theItem.cursorPos == 50
    assert theItem.itemClass == nwItemClass.NOVEL
    assert theItem.itemType == nwItemType.FILE
    assert theItem.itemLayout == nwItemLayout.DOCUMENT

# END Test testCoreItem_ConvertFromFmt13
