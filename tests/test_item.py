# -*- coding: utf-8 -*-
"""novelWriter NWItem Class Tester
"""

import nw
import pytest

from lxml import etree
from nwdummy import DummyMain

from nw.config import Config
from nw.project.project import NWProject, NWItem
from nw.constants import nwItemClass, nwItemType, nwItemLayout

theConf = Config()
theMain = DummyMain()
theMain.mainConf = theConf

theProject = NWProject(theMain)
theItem = NWItem(theProject)
nwXML = etree.Element("novelWriterXML")

@pytest.mark.project
def testItemSettersSimple():

    # Name
    theItem.setName("A Name")
    assert theItem.itemName == "A Name"
    theItem.setName("\t A Name   ")
    assert theItem.itemName == "A Name"

    # Handle
    theItem.setHandle(123)
    assert theItem.itemHandle is None
    theItem.setHandle("0123456789abcdef")
    assert theItem.itemHandle is None
    theItem.setHandle("0123456789abc")
    assert theItem.itemHandle == "0123456789abc"

    # Parent
    theItem.setParent(None)
    assert theItem.parHandle is None
    theItem.setParent(123)
    assert theItem.parHandle is None
    theItem.setParent("0123456789abcdef")
    assert theItem.parHandle is None
    theItem.setParent("0123456789abc")
    assert theItem.parHandle == "0123456789abc"

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

@pytest.mark.project
def testItemClassSetter():

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
    theItem.setClass("TRASH")
    assert theItem.itemClass == nwItemClass.TRASH

@pytest.mark.project
def testItemTypeSetter():

    # Class
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

@pytest.mark.project
def testItemLayoutSetter():

    # Class
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

@pytest.mark.project
def testItemXMLPackUnpack():

    # Pack
    xContent = etree.SubElement(nwXML, "content")
    theItem.packXML(xContent)
    assert etree.tostring(xContent, pretty_print=False, encoding="utf-8") == (
        b"<content>"
        b"<item handle=\"0123456789abc\" order=\"1\" parent=\"0123456789abc\">"
        b"<name>A Name</name><type>TRASH</type><class>TRASH</class><status>Main</status><expanded>True</expanded>"
        b"</item>"
        b"</content>"
    )

    # Unpack
    assert theItem.unpackXML(xContent[0])
    assert theItem.itemHandle == "0123456789abc"
    assert theItem.parHandle == "0123456789abc"
    assert theItem.itemOrder == 1
    assert theItem.isExpanded
    assert theItem.charCount == 1
    assert theItem.wordCount == 1
    assert theItem.paraCount == 1
    assert theItem.cursorPos == 1
    assert theItem.itemClass == nwItemClass.TRASH
    assert theItem.itemType == nwItemType.TRASH
    assert theItem.itemLayout == nwItemLayout.NOTE
