"""
novelWriter – NWItem Class Tester
=================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

from PyQt5.QtGui import QIcon

from tools import C, buildTestProject

from novelwriter.enum import nwItemClass, nwItemType, nwItemLayout
from novelwriter.core.item import NWItem
from novelwriter.core.project import NWProject


@pytest.mark.core
def testCoreItem_Setters(mockGUI, mockRnd, fncPath):
    """Test all the simple setters for the NWItem class.
    """
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncPath)
    theItem = NWItem(theProject)

    statusKeys = ["s000000", "s000001", "s000002", "s000003"]
    importKeys = ["i000004", "i000005", "i000006", "i000007"]

    # Name
    theItem.setName("A Name")
    assert theItem.itemName == "A Name"
    theItem.setName("\t A Name   ")
    assert theItem.itemName == "A Name"
    theItem.setName("\t A\t\u2009\u202f\u2002\u2003\u2028\u2029Name   ")
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

    # Root
    theItem.setRoot(None)
    assert theItem.itemRoot is None
    theItem.setRoot(123)
    assert theItem.itemRoot is None
    theItem.setRoot("0123456789abcdef")
    assert theItem.itemRoot is None
    theItem.setRoot("0123456789abg")
    assert theItem.itemRoot is None
    theItem.setRoot("0123456789abc")
    assert theItem.itemRoot == "0123456789abc"

    # Order
    theItem.setOrder(None)
    assert theItem.itemOrder == 0
    theItem.setOrder("1")
    assert theItem.itemOrder == 1
    theItem.setOrder(1)
    assert theItem.itemOrder == 1

    # Importance
    theItem._class = nwItemClass.CHARACTER
    theItem.setImport("Word")
    assert theItem.itemImport == importKeys[0]  # Default
    for key in importKeys:
        theItem.setImport(key)
        assert theItem.itemImport == key

    # Status
    theItem._class = nwItemClass.NOVEL
    theItem.setStatus("Word")
    assert theItem.itemStatus == statusKeys[0]  # Default
    for key in statusKeys:
        theItem.setStatus(key)
        assert theItem.itemStatus == key

    # Status/Importance Wrapper
    theItem._class = nwItemClass.CHARACTER
    for key in importKeys:
        theItem.setImport(key)
        assert theItem.itemImport == key
        assert theItem.itemStatus == statusKeys[3]  # Should not change

    theItem._class = nwItemClass.NOVEL
    for key in statusKeys:
        theItem.setStatus(key)
        assert theItem.itemImport == importKeys[3]  # Should not change
        assert theItem.itemStatus == key

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
    assert theItem.isExpanded is False
    theItem.setExpanded(True)
    assert theItem.isExpanded is True

    # Active
    theItem.setActive(8)
    assert theItem.isActive is False
    theItem.setActive(None)
    assert theItem.isActive is False
    theItem.setActive("None")
    assert theItem.isActive is False
    theItem.setActive("What?")
    assert theItem.isActive is False
    theItem.setActive("True")
    assert theItem.isActive is False
    theItem.setActive(True)
    assert theItem.isActive is True

    # CharCount
    theItem.setCharCount(None)
    assert theItem.charCount == 0
    theItem.setCharCount("1")
    assert theItem.charCount == 0
    theItem.setCharCount(1)
    assert theItem.charCount == 1

    # WordCount
    theItem.setWordCount(None)
    assert theItem.wordCount == 0
    theItem.setWordCount("1")
    assert theItem.wordCount == 0
    theItem.setWordCount(1)
    assert theItem.wordCount == 1

    # ParaCount
    theItem.setParaCount(None)
    assert theItem.paraCount == 0
    theItem.setParaCount("1")
    assert theItem.paraCount == 0
    theItem.setParaCount(1)
    assert theItem.paraCount == 1

    # CursorPos
    theItem.setCursorPos(None)
    assert theItem.cursorPos == 0
    theItem.setCursorPos("1")
    assert theItem.cursorPos == 0
    theItem.setCursorPos(1)
    assert theItem.cursorPos == 1

    # Initial Count
    theItem.setWordCount(234)
    theItem.saveInitialCount()
    assert theItem.initCount == 234

# END Test testCoreItem_Setters


@pytest.mark.core
def testCoreItem_Methods(mockGUI, mockRnd, fncPath):
    """Test the simple methods of the NWItem class.
    """
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncPath)
    theItem = NWItem(theProject)

    # Describe Me
    # ===========

    assert theItem.describeMe() == "None"

    theItem.setType("ROOT")
    assert theItem.describeMe() == "Root Folder"
    assert theItem.isRootType() is True

    theItem.setType("FOLDER")
    assert theItem.describeMe() == "Folder"
    assert theItem.isFolderType() is True

    theItem.setType("FILE")
    theItem.setLayout("DOCUMENT")
    assert theItem.isFileType() is True
    assert theItem.isDocumentLayout() is True

    theItem.setMainHeading("HH")
    assert theItem.mainHeading == "H0"
    assert theItem.describeMe() == "Novel Document"

    theItem.setMainHeading("H0")
    assert theItem.mainHeading == "H0"
    assert theItem.describeMe() == "Novel Document"

    theItem.setMainHeading("H1")
    assert theItem.mainHeading == "H1"
    assert theItem.describeMe() == "Novel Title Page"

    theItem.setMainHeading("H2")
    assert theItem.mainHeading == "H2"
    assert theItem.describeMe() == "Novel Chapter"

    theItem.setMainHeading("H3")
    assert theItem.mainHeading == "H3"
    assert theItem.describeMe() == "Novel Scene"

    theItem.setMainHeading("H4")
    assert theItem.mainHeading == "H4"
    assert theItem.describeMe() == "Novel Section"

    theItem.setMainHeading("H5")
    assert theItem.mainHeading == "H4"
    assert theItem.describeMe() == "Novel Section"

    theItem.setLayout("NOTE")
    assert theItem.isNoteLayout() is True
    assert theItem.describeMe() == "Project Note"

    # Status + Icon
    # =============

    theItem.setType("FILE")
    theItem.setStatus(C.sNote)
    theItem.setImport(C.iMinor)

    theItem.setClass("NOVEL")
    stT, stI = theItem.getImportStatus()
    assert stT == "Note"
    assert isinstance(stI, QIcon)

    theItem.setImportStatus(C.sDraft)
    stT, stI = theItem.getImportStatus()
    assert stT == "Draft"

    theItem.setClass("CHARACTER")
    stT, stI = theItem.getImportStatus()
    assert stT == "Minor"
    assert isinstance(stI, QIcon)

    theItem.setImportStatus(C.iMajor)
    stT, stI = theItem.getImportStatus()
    assert stT == "Major"

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

    # Alternative
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
    assert theItem.isNovelLike() is False
    assert theItem.documentAllowed() is False
    assert theItem.isInactiveClass() is True

    theItem.setClass("NOVEL")
    assert theItem.itemClass == nwItemClass.NOVEL
    assert theItem.isNovelLike() is True
    assert theItem.documentAllowed() is True
    assert theItem.isInactiveClass() is False

    theItem.setClass("PLOT")
    assert theItem.itemClass == nwItemClass.PLOT
    assert theItem.isNovelLike() is False
    assert theItem.documentAllowed() is False
    assert theItem.isInactiveClass() is False

    theItem.setClass("CHARACTER")
    assert theItem.itemClass == nwItemClass.CHARACTER
    assert theItem.isNovelLike() is False
    assert theItem.documentAllowed() is False
    assert theItem.isInactiveClass() is False

    theItem.setClass("WORLD")
    assert theItem.itemClass == nwItemClass.WORLD
    assert theItem.isNovelLike() is False
    assert theItem.documentAllowed() is False
    assert theItem.isInactiveClass() is False

    theItem.setClass("TIMELINE")
    assert theItem.itemClass == nwItemClass.TIMELINE
    assert theItem.isNovelLike() is False
    assert theItem.documentAllowed() is False
    assert theItem.isInactiveClass() is False

    theItem.setClass("OBJECT")
    assert theItem.itemClass == nwItemClass.OBJECT
    assert theItem.isNovelLike() is False
    assert theItem.documentAllowed() is False
    assert theItem.isInactiveClass() is False

    theItem.setClass("ENTITY")
    assert theItem.itemClass == nwItemClass.ENTITY
    assert theItem.isNovelLike() is False
    assert theItem.documentAllowed() is False
    assert theItem.isInactiveClass() is False

    theItem.setClass("CUSTOM")
    assert theItem.itemClass == nwItemClass.CUSTOM
    assert theItem.isNovelLike() is False
    assert theItem.documentAllowed() is False
    assert theItem.isInactiveClass() is False

    theItem.setClass("ARCHIVE")
    assert theItem.itemClass == nwItemClass.ARCHIVE
    assert theItem.isNovelLike() is True
    assert theItem.documentAllowed() is True
    assert theItem.isInactiveClass() is True

    theItem.setClass("TRASH")
    assert theItem.itemClass == nwItemClass.TRASH
    assert theItem.isNovelLike() is False
    assert theItem.documentAllowed() is True
    assert theItem.isInactiveClass() is True

    # Alternative
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

    # Alternative
    theItem.setLayout(nwItemLayout.NOTE)
    assert theItem.itemLayout == nwItemLayout.NOTE

# END Test testCoreItem_LayoutSetter


@pytest.mark.core
def testCoreItem_ClassDefaults(mockGUI):
    """Test the setter for the default values.
    """
    theProject = NWProject(mockGUI)
    theItem = NWItem(theProject)

    # Root items should not have their class updated
    theItem.setParent(None)
    theItem.setClass(nwItemClass.NO_CLASS)
    assert theItem.itemClass == nwItemClass.NO_CLASS

    theItem.setClassDefaults(nwItemClass.NOVEL)
    assert theItem.itemClass == nwItemClass.NO_CLASS

    # Non-root items should have their class updated
    theItem.setParent("0123456789abc")
    theItem.setClass(nwItemClass.NO_CLASS)
    assert theItem.itemClass == nwItemClass.NO_CLASS

    theItem.setClassDefaults(nwItemClass.NOVEL)
    assert theItem.itemClass == nwItemClass.NOVEL

    # Non-layout items should have their layout set based on class
    theItem.setParent("0123456789abc")
    theItem.setClass(nwItemClass.NO_CLASS)
    theItem.setLayout(nwItemLayout.NO_LAYOUT)
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT

    theItem.setClassDefaults(nwItemClass.NOVEL)
    assert theItem.itemLayout == nwItemLayout.DOCUMENT

    theItem.setParent("0123456789abc")
    theItem.setClass(nwItemClass.NO_CLASS)
    theItem.setLayout(nwItemLayout.NO_LAYOUT)
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT

    theItem.setClassDefaults(nwItemClass.PLOT)
    assert theItem.itemLayout == nwItemLayout.NOTE

    # If documents are not allowed in that class, the layout should be changed
    theItem.setParent("0123456789abc")
    theItem.setClass(nwItemClass.NO_CLASS)
    theItem.setLayout(nwItemLayout.DOCUMENT)
    assert theItem.itemLayout == nwItemLayout.DOCUMENT

    theItem.setClassDefaults(nwItemClass.PLOT)
    assert theItem.itemLayout == nwItemLayout.NOTE

    # In all cases, status and importance should no longer be None
    assert theItem.itemStatus is not None
    assert theItem.itemImport is not None

# END Test testCoreItem_ClassDefaults


@pytest.mark.core
def testCoreItem_PackUnpack(mockGUI, caplog, mockRnd):
    """Test packing and unpacking entries for the NWItem class.
    """
    theProject = NWProject(mockGUI)
    theProject.data.itemStatus.write(None, "New", (100, 100, 100))
    theProject.data.itemImport.write(None, "New", (100, 100, 100))

    # Invalid
    theItem = NWItem(theProject)
    assert theItem.unpack({}) is False

    # File
    theItem = NWItem(theProject)
    assert theItem.unpack({
        "name": "A File",
        "itemAttr": {
            "handle": "0000000000003",
            "parent": "0000000000002",
            "root": "0000000000001",
            "order": 1,
            "type": "FILE",
            "class": "NOVEL",
            "layout": "DOCUMENT",
        },
        "metaAttr": {
            "expanded": True,
            "heading": "H1",
            "charCount": 100,
            "wordCount": 20,
            "paraCount": 2,
            "cursorPos": 50,
        },
        "nameAttr": {
            "status": None,
            "import": None,
            "active": False,
        },
    }) is True

    assert theItem.itemName == "A File"
    assert theItem.itemHandle == "0000000000003"
    assert theItem.itemParent == "0000000000002"
    assert theItem.itemRoot == "0000000000001"
    assert theItem.itemOrder == 1
    assert theItem.itemType == nwItemType.FILE
    assert theItem.itemClass == nwItemClass.NOVEL
    assert theItem.itemLayout == nwItemLayout.DOCUMENT
    assert theItem.itemStatus == "s000000"
    assert theItem.itemImport == "i000001"
    assert theItem.isActive is False
    assert theItem.isExpanded is True
    assert theItem.mainHeading == "H1"
    assert theItem.charCount == 100
    assert theItem.wordCount == 20
    assert theItem.paraCount == 2
    assert theItem.cursorPos == 50

    assert theItem.pack() == {
        "name": "A File",
        "itemAttr": {
            "handle": "0000000000003",
            "parent": "0000000000002",
            "root": "0000000000001",
            "order": "1",
            "type": "FILE",
            "class": "NOVEL",
            "layout": "DOCUMENT",
        },
        "metaAttr": {
            "expanded": "yes",
            "heading": "H1",
            "charCount": "100",
            "wordCount": "20",
            "paraCount": "2",
            "cursorPos": "50",
        },
        "nameAttr": {
            "status": "s000000",
            "import": "i000001",
            "active": "no",
        }
    }

    # Folder
    theItem = NWItem(theProject)
    assert theItem.unpack({
        "name": "A Folder",
        "itemAttr": {
            "handle": "0000000000003",
            "parent": "0000000000002",
            "root": "0000000000001",
            "order": 1,
            "type": "FOLDER",
            "class": "NOVEL",
            "layout": "DOCUMENT",
        },
        "metaAttr": {
            "expanded": True,
            "heading": "H1",
            "charCount": 100,
            "wordCount": 20,
            "paraCount": 2,
            "cursorPos": 50,
        },
        "nameAttr": {
            "status": "",
            "import": "",
            "active": True,
        }
    }) is True

    assert theItem.itemName == "A Folder"
    assert theItem.itemHandle == "0000000000003"
    assert theItem.itemParent == "0000000000002"
    assert theItem.itemRoot == "0000000000001"
    assert theItem.itemOrder == 1
    assert theItem.itemType == nwItemType.FOLDER
    assert theItem.itemClass == nwItemClass.NOVEL
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT
    assert theItem.itemStatus == "s000000"
    assert theItem.itemImport == "i000001"
    assert theItem.isActive is False
    assert theItem.isExpanded is True
    assert theItem.mainHeading == "H0"
    assert theItem.charCount == 0
    assert theItem.wordCount == 0
    assert theItem.paraCount == 0
    assert theItem.cursorPos == 0

    assert theItem.pack() == {
        "name": "A Folder",
        "itemAttr": {
            "handle": "0000000000003",
            "parent": "0000000000002",
            "root": "0000000000001",
            "order": "1",
            "type": "FOLDER",
            "class": "NOVEL",
        },
        "metaAttr": {
            "expanded": "yes",
        },
        "nameAttr": {
            "status": "s000000",
            "import": "i000001",
        }
    }

    # Root
    theItem = NWItem(theProject)
    assert theItem.unpack({
        "name": "A Novel",
        "itemAttr": {
            "handle": "0000000000003",
            "parent": "0000000000002",
            "root": "0000000000001",
            "order": 1,
            "type": "ROOT",
            "class": "NOVEL",
            "layout": "DOCUMENT",
        },
        "metaAttr": {
            "expanded": True,
            "heading": "H1",
            "charCount": 100,
            "wordCount": 20,
            "paraCount": 2,
            "cursorPos": 50,
        },
        "nameAttr": {
            "status": None,
            "import": None,
            "active": True,
        },
    }) is True

    assert theItem.itemName == "A Novel"
    assert theItem.itemHandle == "0000000000003"
    assert theItem.itemParent is None
    assert theItem.itemRoot == "0000000000003"
    assert theItem.itemOrder == 1
    assert theItem.itemType == nwItemType.ROOT
    assert theItem.itemClass == nwItemClass.NOVEL
    assert theItem.itemLayout == nwItemLayout.NO_LAYOUT
    assert theItem.itemStatus == "s000000"
    assert theItem.itemImport == "i000001"
    assert theItem.isActive is False
    assert theItem.isExpanded is True
    assert theItem.mainHeading == "H0"
    assert theItem.charCount == 0
    assert theItem.wordCount == 0
    assert theItem.paraCount == 0
    assert theItem.cursorPos == 0

    assert theItem.pack() == {
        "name": "A Novel",
        "itemAttr": {
            "handle": "0000000000003",
            "parent": "None",
            "root": "0000000000003",
            "order": "1",
            "type": "ROOT",
            "class": "NOVEL",
        },
        "metaAttr": {
            "expanded": "yes",
        },
        "nameAttr": {
            "status": "s000000",
            "import": "i000001",
        }
    }

# END Test testCoreItem_PackUnpack
