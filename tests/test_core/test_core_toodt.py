"""
novelWriter – ToOdt Class Tester
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

import os
import pytest
import zipfile

from lxml import etree
from shutil import copyfile

from tools import cmpFiles

from novelwriter.core import NWProject, NWIndex, ToOdt
from novelwriter.core.toodt import ODTParagraphStyle, ODTTextStyle, XMLParagraph, _mkTag

XML_NS = [
    ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"',
    ' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"',
    ' xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0"',
    ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"',
    ' xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"',
    ' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"',
]


def xmlToText(xElem):
    """Get the text content of an XML element.
    """
    rTxt = etree.tostring(xElem, encoding="utf-8", xml_declaration=False).decode()
    for nSpace in XML_NS:
        rTxt = rTxt.replace(nSpace, "")
    return rTxt


@pytest.mark.core
def testCoreToOdt_Init(mockGUI):
    """Test initialisation of the ODT document.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)

    # Flat Doc
    # ========

    theDoc = ToOdt(theProject, isFlat=True)
    theDoc.initDocument()

    # Document XML
    assert theDoc._dFlat is not None
    assert theDoc._dCont is None
    assert theDoc._dMeta is None
    assert theDoc._dStyl is None

    # Content XML
    assert theDoc._xMeta is not None
    assert theDoc._xFont is not None
    assert theDoc._xFnt2 is None
    assert theDoc._xStyl is not None
    assert theDoc._xAuto is not None
    assert theDoc._xAut2 is None
    assert theDoc._xMast is not None
    assert theDoc._xBody is not None
    assert theDoc._xText is not None

    # ODT Doc
    # =======

    theDoc = ToOdt(theProject, isFlat=False)
    theDoc.initDocument()

    # Document XML
    assert theDoc._dFlat is None
    assert theDoc._dCont is not None
    assert theDoc._dMeta is not None
    assert theDoc._dStyl is not None

    # Content XML
    assert theDoc._xMeta is not None
    assert theDoc._xFont is not None
    assert theDoc._xFnt2 is not None
    assert theDoc._xStyl is not None
    assert theDoc._xAuto is not None
    assert theDoc._xAut2 is not None
    assert theDoc._xMast is not None
    assert theDoc._xBody is not None
    assert theDoc._xText is not None

# END Test testCoreToOdt_Init


@pytest.mark.core
def testCoreToOdt_TextFormatting(mockGUI):
    """Test formatting of paragraphs.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)
    theDoc = ToOdt(theProject, isFlat=True)

    theDoc.initDocument()
    assert xmlToText(theDoc._xText) == "<office:text/>"

    # Paragraph Style
    # ===============
    oStyle = ODTParagraphStyle()

    assert theDoc._paraStyle("stuff", oStyle) == "Standard"
    assert theDoc._paraStyle("Text_Body", oStyle) == "Text_Body"

    # Create new para style
    oStyle.setTextAlign("center")
    assert theDoc._paraStyle("Text_Body", oStyle) == "P1"

    # Return the same style on second call
    assert theDoc._paraStyle("Text_Body", oStyle) == "P1"

    assert list(theDoc._mainPara.keys()) == [
        "Text_Body", "Text_Meta", "Title", "Heading_1",
        "Heading_2", "Heading_3", "Heading_4", "Header"
    ]

    theKey = "a956b3abcc3d2d5daedf829b2cef56b4ba9b5b583c9c8cc8c87816dfc5a0685d"
    assert theDoc._autoPara[theKey][0] == "P1"
    assert isinstance(theDoc._autoPara[theKey][1], ODTParagraphStyle)

    # Paragraph Formatting
    # ====================
    oStyle = ODTParagraphStyle()

    # No Text
    theDoc.initDocument()
    theDoc._addTextPar("Standard", oStyle, "")
    assert xmlToText(theDoc._xText) == (
        "<office:text>"
        "<text:p text:style-name=\"Standard\"></text:p>"
        "</office:text>"
    )

    # No Format
    theDoc.initDocument()
    theDoc._addTextPar("Standard", oStyle, "Hello World")
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        "<office:text>"
        "<text:p text:style-name=\"Standard\">Hello World</text:p>"
        "</office:text>"
    )

    # Heading Level None
    theDoc.initDocument()
    theDoc._addTextPar("Standard", oStyle, "Hello World", isHead=True)
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        "<office:text>"
        "<text:h text:style-name=\"Standard\">Hello World</text:h>"
        "</office:text>"
    )

    # Heading Level 1
    theDoc.initDocument()
    theDoc._addTextPar("Standard", oStyle, "Hello World", isHead=True, oLevel="1")
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        "<office:text>"
        "<text:h text:style-name=\"Standard\" text:outline-level=\"1\">Hello World</text:h>"
        "</office:text>"
    )

    # Formatted Text
    theDoc.initDocument()
    theTxt = "A **few** _words_ from ~~our~~ sponsor"
    theFmt = "  _B   b_ I     i      _S   s_        "
    theDoc._addTextPar("Standard", oStyle, theTxt, theFmt=theFmt)
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        "<office:text>"
        "<text:p text:style-name=\"Standard\">A <text:span text:style-name=\"T1\">few</text:span> "
        "<text:span text:style-name=\"T2\">words</text:span> from <text:span text:style-name=\"T3"
        "\">our</text:span> sponsor</text:p>"
        "</office:text>"
    )

    # Incorrectly Formatted Text
    theDoc.initDocument()
    theTxt = "A **few** _wordsXXX"
    theFmt = "  _b   b_ I     XXX"
    theDoc._addTextPar("Standard", oStyle, theTxt, theFmt=theFmt)
    assert theDoc.getErrors() == ["Unknown format tag encountered"]
    assert xmlToText(theDoc._xText) == (
        "<office:text>"
        "<text:p text:style-name=\"Standard\">"
        "A few <text:span text:style-name=\"T2\">words</text:span>"
        "</text:p>"
        "</office:text>"
    )

    # Formatted Text
    theDoc.initDocument()
    theTxt = "Hello\n\tWorld"
    theFmt = "            "
    theDoc._addTextPar("Standard", oStyle, theTxt, theFmt=theFmt)
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        "<office:text>"
        "<text:p text:style-name=\"Standard\">Hello<text:line-break/><text:tab/>World</text:p>"
        "</office:text>"
    )

    # Tabs and Breaks

# END Test testCoreToOdt_TextFormatting


@pytest.mark.core
def testCoreToOdt_Convert(mockGUI):
    """Test the converter of the ToOdt class.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)
    theDoc = ToOdt(theProject, isFlat=True)

    theDoc.isNovel = True

    def getStyle(styleName):
        for aSet in theDoc._autoPara.values():
            if aSet[0] == styleName:
                return aSet[1]
        return None

    # Headers
    # =======

    # Header 1
    theDoc.theText = "# Title\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="P1" text:outline-level="1">Title</text:h>'
        '</office:text>'
    )

    # Header 2
    theDoc.theText = "## Chapter\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="P2" text:outline-level="2">Chapter</text:h>'
        '</office:text>'
    )

    # Header 3
    theDoc.theText = "### Scene\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_3" text:outline-level="3">Scene</text:h>'
        '</office:text>'
    )

    # Header 4
    theDoc.theText = "#### Section\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_4" text:outline-level="4">Section</text:h>'
        '</office:text>'
    )

    # Title
    theDoc.theText = "#! Title\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="Title">Title</text:h>'
        '</office:text>'
    )

    # Unnumbered chapter
    theDoc.theText = "##! Prologue\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="P2" text:outline-level="2">Prologue</text:h>'
        '</office:text>'
    )

    # Paragraphs
    # ==========

    # Nested Text
    theDoc.theText = "Some ~~nested **bold** and _italics_ text~~ text."
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_Body">Some '
        '<text:span text:style-name="T1">nested </text:span>'
        '<text:span text:style-name="T2">bold</text:span>'
        '<text:span text:style-name="T1"> and </text:span>'
        '<text:span text:style-name="T3">italics</text:span>'
        '<text:span text:style-name="T1"> text</text:span> text.</text:p>'
        '</office:text>'
    )

    # Hard Break
    theDoc.theText = "Some text.\nNext line\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_Body">Some text.<text:line-break/>Next line</text:p>'
        '</office:text>'
    )

    # Tab
    theDoc.theText = "\tItem 1\tItem 2\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_Body"><text:tab/>Item 1<text:tab/>Item 2</text:p>'
        '</office:text>'
    )

    # Tab in Format
    theDoc.theText = "Some **bold\ttext**"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_Body">Some <text:span text:style-name="T4">'
        'bold<text:tab/>text</text:span></text:p>'
        '</office:text>'
    )

    # Multiple Spaces
    theDoc.theText = (
        "### Scene\n\n"
        "Hello World\n\n"
        "Hello  World\n\n"
        "Hello   World\n\n"
    )
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_3" text:outline-level="3">Scene</text:h>'
        '<text:p text:style-name="Text_Body">Hello World</text:p>'
        '<text:p text:style-name="Text_Body">Hello <text:s/>World</text:p>'
        '<text:p text:style-name="Text_Body">Hello <text:s text:c="2"/>World</text:p>'
        '</office:text>'
    )

    # Synopsis, Comment, Keywords
    theDoc.theText = (
        "### Scene\n\n"
        "@pov: Jane\n\n"
        "% synopsis: So it begins\n\n"
        "% a plain comment\n\n"
    )
    theDoc.setSynopsis(True)
    theDoc.setComments(True)
    theDoc.setKeywords(True)
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_3" text:outline-level="3">Scene</text:h>'
        '<text:p text:style-name="Text_Meta"><text:span text:style-name="T4">'
        'Point of View:</text:span> Jane</text:p>'
        '<text:p text:style-name="Text_Meta"><text:span text:style-name="T4">'
        'Synopsis:</text:span> So it begins</text:p>'
        '<text:p text:style-name="Text_Meta"><text:span text:style-name="T4">'
        'Comment:</text:span> a plain comment</text:p>'
        '</office:text>'
    )

    # Scene Separator
    theDoc.theText = "### Scene One\n\nText\n\n### Scene Two\n\nText"
    theDoc.setSceneFormat("* * *", False)
    theDoc.tokenizeText()
    theDoc.doHeaders()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:p text:style-name="P3">* * *</text:p>'
        '<text:p text:style-name="Text_Body">Text</text:p>'
        '<text:p text:style-name="P3">* * *</text:p>'
        '<text:p text:style-name="Text_Body">Text</text:p>'
        '</office:text>'
    )

    # Scene Break
    theDoc.theText = "### Scene One\n\nText\n\n### Scene Two\n\nText"
    theDoc.setSceneFormat("", False)
    theDoc.tokenizeText()
    theDoc.doHeaders()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_Body"></text:p>'
        '<text:p text:style-name="Text_Body">Text</text:p>'
        '<text:p text:style-name="Text_Body"></text:p>'
        '<text:p text:style-name="Text_Body">Text</text:p>'
        '</office:text>'
    )

    # Paragraph Styles
    theDoc.theText = (
        "### Scene\n\n"
        "@pov: Jane\n"
        "@char: John\n"
        "@plot: Main\n\n"
        ">> Right align\n\n"
        "Left Align <<\n\n"
        ">> Centered <<\n\n"
        "> Left indent\n\n"
        "Right indent <\n\n"
    )
    theDoc.setKeywords(True)
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_3" text:outline-level="3">Scene</text:h>'
        '<text:p text:style-name="P4"><text:span text:style-name="T4">'
        'Point of View:</text:span> Jane</text:p>'
        '<text:p text:style-name="P5"><text:span text:style-name="T4">'
        'Characters:</text:span> John</text:p>'
        '<text:p text:style-name="Text_Meta"><text:span text:style-name="T4">'
        'Plot:</text:span> Main</text:p>'
        '<text:p text:style-name="P6">Right align</text:p>'
        '<text:p text:style-name="Text_Body">Left Align</text:p>'
        '<text:p text:style-name="P3">Centered</text:p>'
        '<text:p text:style-name="P7">Left indent</text:p>'
        '<text:p text:style-name="P8">Right indent</text:p>'
        '</office:text>'
    )
    assert getStyle("P4")._pAttr["margin-bottom"] == ["fo", "0.000cm"]
    assert getStyle("P5")._pAttr["margin-bottom"] == ["fo", "0.000cm"]
    assert getStyle("P5")._pAttr["margin-top"] == ["fo", "0.000cm"]
    assert getStyle("P6")._pAttr["text-align"] == ["fo", "right"]
    assert getStyle("P3")._pAttr["text-align"] == ["fo", "center"]
    assert getStyle("P7")._pAttr["margin-left"] == ["fo", "1.693cm"]
    assert getStyle("P8")._pAttr["margin-right"] == ["fo", "1.693cm"]

    # Justified
    theDoc.theText = (
        "### Scene\n\n"
        "Regular paragraph\n\n"
        "with\nbreak\n\n"
        "Left Align <<\n\n"
    )
    theDoc.setJustify(True)
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_3" text:outline-level="3">Scene</text:h>'
        '<text:p text:style-name="Text_Body">Regular paragraph</text:p>'
        '<text:p text:style-name="P9">with<text:line-break/>break</text:p>'
        '<text:p text:style-name="P9">Left Align</text:p>'
        '</office:text>'
    )
    assert getStyle("P9")._pAttr["text-align"] == ["fo", "left"]

    # Page Breaks
    theDoc.theText = (
        "## Chapter One\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "Text\n\n"
    )
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert theDoc.getErrors() == []
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="P2" text:outline-level="2">Chapter One</text:h>'
        '<text:p text:style-name="Text_Body">Text</text:p>'
        '<text:h text:style-name="P2" text:outline-level="2">Chapter Two</text:h>'
        '<text:p text:style-name="Text_Body">Text</text:p>'
        '</office:text>'
    )

# END Test testCoreToOdt_Convert


@pytest.mark.core
def testCoreToOdt_ConvertDirect(mockGUI):
    """Test the converter directly using the ToOdt class to reach some
    otherwise hard to reach conditions.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)
    theDoc = ToOdt(theProject, isFlat=True)

    theDoc.isNovel = True

    # Justified
    theDoc = ToOdt(theProject, isFlat=True)
    theDoc.theTokens = [
        (theDoc.T_TEXT, 1, "This is a paragraph", [], theDoc.A_JUSTIFY),
        (theDoc.T_EMPTY, 1, "", None, theDoc.A_NONE),
    ]
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert (
        '<style:style style:name="P1" style:family="paragraph" '
        'style:parent-style-name="Text_Body">'
        '<style:paragraph-properties fo:text-align="justify"/>'
        '</style:style>'
    ) in xmlToText(theDoc._xAuto)
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:p text:style-name="P1">This is a paragraph</text:p>'
        '</office:text>'
    )

    # Page Break After
    theDoc = ToOdt(theProject, isFlat=True)
    theDoc.theTokens = [
        (theDoc.T_TEXT, 1, "This is a paragraph", [], theDoc.A_PBA),
        (theDoc.T_EMPTY, 1, "", None, theDoc.A_NONE),
    ]
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert (
        '<style:style style:name="P1" style:family="paragraph" '
        'style:parent-style-name="Text_Body">'
        '<style:paragraph-properties fo:break-after="page"/>'
        '</style:style>'
    ) in xmlToText(theDoc._xAuto)
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:p text:style-name="P1">This is a paragraph</text:p>'
        '</office:text>'
    )

# END Test testCoreToOdt_ConvertDirect


@pytest.mark.core
def testCoreToOdt_SaveFlat(mockGUI, fncDir, outDir, refDir):
    """Test the document save functions.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)

    theDoc = ToOdt(theProject, isFlat=True)
    theDoc.isNovel = True
    assert theDoc.setLanguage(None) is False
    assert theDoc.setLanguage("nb_NO") is True
    theDoc.setColourHeaders(True)

    theDoc.theText = (
        "## Chapter One\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "Text\n\n"
    )
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()

    flatFile = os.path.join(fncDir, "document.fodt")
    testFile = os.path.join(outDir, "coreToOdt_SaveFlat_document.fodt")
    compFile = os.path.join(refDir, "coreToOdt_SaveFlat_document.fodt")

    theDoc.saveFlatXML(flatFile)
    assert os.path.isfile(flatFile)

    copyfile(flatFile, testFile)
    assert cmpFiles(testFile, compFile, [4, 5])

# END Test testCoreToOdt_SaveFlat


@pytest.mark.core
def testCoreToOdt_SaveFull(mockGUI, fncDir, outDir, refDir):
    """Test the document save functions.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)

    theDoc = ToOdt(theProject, isFlat=False)
    theDoc.isNovel = True

    theDoc.theText = (
        "## Chapter One\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "Text\n\n"
    )
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()

    fullFile = os.path.join(fncDir, "document.odt")

    theDoc.saveOpenDocText(fullFile)
    assert os.path.isfile(fullFile)
    assert zipfile.is_zipfile(fullFile)

    maniFile = os.path.join(outDir, "coreToOdt_SaveFull_manifest.xml")
    settFile = os.path.join(outDir, "coreToOdt_SaveFull_settings.xml")
    contFile = os.path.join(outDir, "coreToOdt_SaveFull_content.xml")
    metaFile = os.path.join(outDir, "coreToOdt_SaveFull_meta.xml")
    stylFile = os.path.join(outDir, "coreToOdt_SaveFull_styles.xml")

    maniComp = os.path.join(refDir, "coreToOdt_SaveFull_manifest.xml")
    settComp = os.path.join(refDir, "coreToOdt_SaveFull_settings.xml")
    contComp = os.path.join(refDir, "coreToOdt_SaveFull_content.xml")
    metaComp = os.path.join(refDir, "coreToOdt_SaveFull_meta.xml")
    stylComp = os.path.join(refDir, "coreToOdt_SaveFull_styles.xml")

    extaxtTo = os.path.join(outDir, "coreToOdt_SaveFull")

    with zipfile.ZipFile(fullFile, mode="r") as theZip:
        theZip.extract("META-INF/manifest.xml", extaxtTo)
        theZip.extract("settings.xml", extaxtTo)
        theZip.extract("content.xml", extaxtTo)
        theZip.extract("meta.xml", extaxtTo)
        theZip.extract("styles.xml", extaxtTo)

    maniOut = os.path.join(outDir, "coreToOdt_SaveFull", "META-INF", "manifest.xml")
    settOut = os.path.join(outDir, "coreToOdt_SaveFull", "settings.xml")
    contOut = os.path.join(outDir, "coreToOdt_SaveFull", "content.xml")
    metaOut = os.path.join(outDir, "coreToOdt_SaveFull", "meta.xml")
    stylOut = os.path.join(outDir, "coreToOdt_SaveFull", "styles.xml")

    def prettifyXml(inFile, outFile):
        with open(outFile, mode="wb") as fileStream:
            fileStream.write(
                etree.tostring(
                    etree.parse(inFile),
                    pretty_print=True,
                    encoding="utf-8",
                    xml_declaration=True
                )
            )

    prettifyXml(maniOut, maniFile)
    prettifyXml(settOut, settFile)
    prettifyXml(contOut, contFile)
    prettifyXml(metaOut, metaFile)
    prettifyXml(stylOut, stylFile)

    assert cmpFiles(maniFile, maniComp)
    assert cmpFiles(settFile, settComp)
    assert cmpFiles(contFile, contComp)
    assert cmpFiles(metaFile, metaComp, [4, 5])
    assert cmpFiles(stylFile, stylComp)

# END Test testCoreToOdt_SaveFull


@pytest.mark.core
def testCoreToOdt_Format(mockGUI):
    """Test the formatters for the ToOdt class.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)
    theDoc = ToOdt(theProject, isFlat=True)

    assert theDoc._formatSynopsis("synopsis text") == (
        "**Synopsis:** synopsis text",
        "_B         b_              "
    )
    assert theDoc._formatComments("comment text") == (
        "**Comment:** comment text",
        "_B        b_             "
    )

    assert theDoc._formatKeywords("") == ""
    assert theDoc._formatKeywords("tag: Jane") == (
        "**Tag:** Jane",
        "_B    b_     "
    )
    assert theDoc._formatKeywords("char: Bod, Jane") == (
        "**Characters:** Bod, Jane",
        "_B           b_          "
    )

# END Test testCoreToOdt_Format


@pytest.mark.core
def testCoreToOdt_ODTParagraphStyle():
    """Test the ODTParagraphStyle class.
    """
    parStyle = ODTParagraphStyle()

    # Set Attributes
    # ==============

    # Display, Parent, Next Style
    assert parStyle._mAttr["display-name"]      == ["style", None]
    assert parStyle._mAttr["parent-style-name"] == ["style", None]
    assert parStyle._mAttr["next-style-name"]   == ["style", None]

    parStyle.setDisplayName("Name")
    parStyle.setParentStyleName("Name")
    parStyle.setNextStyleName("Name")

    assert parStyle._mAttr["display-name"]      == ["style", "Name"]
    assert parStyle._mAttr["parent-style-name"] == ["style", "Name"]
    assert parStyle._mAttr["next-style-name"]   == ["style", "Name"]

    # Outline Level
    assert parStyle._mAttr["default-outline-level"] == ["style", None]
    parStyle.setOutlineLevel("0")
    assert parStyle._mAttr["default-outline-level"] == ["style", None]
    parStyle.setOutlineLevel("1")
    assert parStyle._mAttr["default-outline-level"] == ["style", "1"]
    parStyle.setOutlineLevel("2")
    assert parStyle._mAttr["default-outline-level"] == ["style", "2"]
    parStyle.setOutlineLevel("3")
    assert parStyle._mAttr["default-outline-level"] == ["style", "3"]
    parStyle.setOutlineLevel("4")
    assert parStyle._mAttr["default-outline-level"] == ["style", "4"]
    parStyle.setOutlineLevel("5")
    assert parStyle._mAttr["default-outline-level"] == ["style", None]

    # Class
    assert parStyle._mAttr["class"] == ["style", None]
    parStyle.setClass("stuff")
    assert parStyle._mAttr["class"] == ["style", None]
    parStyle.setClass("text")
    assert parStyle._mAttr["class"] == ["style", "text"]
    parStyle.setClass("chapter")
    assert parStyle._mAttr["class"] == ["style", "chapter"]
    parStyle.setClass("stuff")
    assert parStyle._mAttr["class"] == ["style", None]

    # Set Paragraph Style
    # ===================

    # Margins & Line Height
    assert parStyle._pAttr["margin-top"]    == ["fo", None]
    assert parStyle._pAttr["margin-bottom"] == ["fo", None]
    assert parStyle._pAttr["margin-left"]   == ["fo", None]
    assert parStyle._pAttr["margin-right"]  == ["fo", None]
    assert parStyle._pAttr["line-height"]   == ["fo", None]

    parStyle.setMarginTop("0.000cm")
    parStyle.setMarginBottom("0.000cm")
    parStyle.setMarginLeft("0.000cm")
    parStyle.setMarginRight("0.000cm")
    parStyle.setLineHeight("1.15")

    assert parStyle._pAttr["margin-top"]    == ["fo", "0.000cm"]
    assert parStyle._pAttr["margin-bottom"] == ["fo", "0.000cm"]
    assert parStyle._pAttr["margin-left"]   == ["fo", "0.000cm"]
    assert parStyle._pAttr["margin-right"]  == ["fo", "0.000cm"]
    assert parStyle._pAttr["line-height"]   == ["fo", "1.15"]

    # Text Alignment
    assert parStyle._pAttr["text-align"] == ["fo", None]
    parStyle.setTextAlign("stuff")
    assert parStyle._pAttr["text-align"] == ["fo", None]
    parStyle.setTextAlign("start")
    assert parStyle._pAttr["text-align"] == ["fo", "start"]
    parStyle.setTextAlign("center")
    assert parStyle._pAttr["text-align"] == ["fo", "center"]
    parStyle.setTextAlign("end")
    assert parStyle._pAttr["text-align"] == ["fo", "end"]
    parStyle.setTextAlign("justify")
    assert parStyle._pAttr["text-align"] == ["fo", "justify"]
    parStyle.setTextAlign("inside")
    assert parStyle._pAttr["text-align"] == ["fo", "inside"]
    parStyle.setTextAlign("outside")
    assert parStyle._pAttr["text-align"] == ["fo", "outside"]
    parStyle.setTextAlign("left")
    assert parStyle._pAttr["text-align"] == ["fo", "left"]
    parStyle.setTextAlign("right")
    assert parStyle._pAttr["text-align"] == ["fo", "right"]
    parStyle.setTextAlign("stuff")
    assert parStyle._pAttr["text-align"] == ["fo", None]

    # Break Before
    assert parStyle._pAttr["break-before"] == ["fo", None]
    parStyle.setBreakBefore("stuff")
    assert parStyle._pAttr["break-before"] == ["fo", None]
    parStyle.setBreakBefore("auto")
    assert parStyle._pAttr["break-before"] == ["fo", "auto"]
    parStyle.setBreakBefore("column")
    assert parStyle._pAttr["break-before"] == ["fo", "column"]
    parStyle.setBreakBefore("page")
    assert parStyle._pAttr["break-before"] == ["fo", "page"]
    parStyle.setBreakBefore("even-page")
    assert parStyle._pAttr["break-before"] == ["fo", "even-page"]
    parStyle.setBreakBefore("odd-page")
    assert parStyle._pAttr["break-before"] == ["fo", "odd-page"]
    parStyle.setBreakBefore("inherit")
    assert parStyle._pAttr["break-before"] == ["fo", "inherit"]
    parStyle.setBreakBefore("stuff")
    assert parStyle._pAttr["break-before"] == ["fo", None]

    # Break After
    assert parStyle._pAttr["break-after"]  == ["fo", None]
    parStyle.setBreakAfter("stuff")
    assert parStyle._pAttr["break-after"]  == ["fo", None]
    parStyle.setBreakAfter("auto")
    assert parStyle._pAttr["break-after"] == ["fo", "auto"]
    parStyle.setBreakAfter("column")
    assert parStyle._pAttr["break-after"] == ["fo", "column"]
    parStyle.setBreakAfter("page")
    assert parStyle._pAttr["break-after"] == ["fo", "page"]
    parStyle.setBreakAfter("even-page")
    assert parStyle._pAttr["break-after"] == ["fo", "even-page"]
    parStyle.setBreakAfter("odd-page")
    assert parStyle._pAttr["break-after"] == ["fo", "odd-page"]
    parStyle.setBreakAfter("inherit")
    assert parStyle._pAttr["break-after"] == ["fo", "inherit"]
    parStyle.setBreakAfter("stuff")
    assert parStyle._pAttr["break-after"] == ["fo", None]

    # Text Attributes
    # ===============

    # Font Name, Family and Size
    assert parStyle._tAttr["font-name"]   == ["style", None]
    assert parStyle._tAttr["font-family"] == ["fo", None]
    assert parStyle._tAttr["font-size"]   == ["fo", None]

    parStyle.setFontName("Verdana")
    parStyle.setFontFamily("Verdana")
    parStyle.setFontSize("12pt")

    assert parStyle._tAttr["font-name"]   == ["style", "Verdana"]
    assert parStyle._tAttr["font-family"] == ["fo", "Verdana"]
    assert parStyle._tAttr["font-size"]   == ["fo", "12pt"]

    # Font Weight
    assert parStyle._tAttr["font-weight"] == ["fo", None]
    parStyle.setFontWeight("stuff")
    assert parStyle._tAttr["font-weight"] == ["fo", None]
    parStyle.setFontWeight("normal")
    assert parStyle._tAttr["font-weight"] == ["fo", "normal"]
    parStyle.setFontWeight("inherit")
    assert parStyle._tAttr["font-weight"] == ["fo", "inherit"]
    parStyle.setFontWeight("bold")
    assert parStyle._tAttr["font-weight"] == ["fo", "bold"]
    parStyle.setFontWeight("stuff")
    assert parStyle._tAttr["font-weight"] == ["fo", None]

    # Colour & Opacity
    assert parStyle._tAttr["color"]   == ["fo", None]
    assert parStyle._tAttr["opacity"] == ["loext", None]

    parStyle.setColor("#000000")
    parStyle.setOpacity("1.00")

    assert parStyle._tAttr["color"]   == ["fo", "#000000"]
    assert parStyle._tAttr["opacity"] == ["loext", "1.00"]

    # Pack XML
    # ========
    xStyle = etree.Element("test", nsmap={
        "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
        "loext": "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0",
        "fo":    "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    })
    parStyle.packXML(xStyle, "test")
    assert xmlToText(xStyle) == (
        '<test>'
        '<style:style style:name="test" style:family="paragraph" style:display-name="Name" '
        'style:parent-style-name="Name" style:next-style-name="Name">'
        '<style:paragraph-properties fo:margin-top="0.000cm" fo:margin-bottom="0.000cm" '
        'fo:margin-left="0.000cm" fo:margin-right="0.000cm" fo:line-height="1.15"/>'
        '<style:text-properties style:font-name="Verdana" fo:font-family="Verdana" '
        'fo:font-size="12pt" fo:color="#000000" loext:opacity="1.00"/>'
        '</style:style>'
        '</test>'
    )

    # Changes
    # =======

    aStyle = ODTParagraphStyle()
    oStyle = ODTParagraphStyle()
    assert aStyle.checkNew(oStyle) is False
    assert aStyle.getID() == oStyle.getID()

    aStyle.setDisplayName("Name1")
    oStyle.setDisplayName("Name2")
    assert aStyle.checkNew(oStyle) is True
    assert aStyle.getID() != oStyle.getID()

    aStyle = ODTParagraphStyle()
    oStyle = ODTParagraphStyle()
    aStyle.setMarginTop("0.000cm")
    oStyle.setMarginTop("1.000cm")
    assert aStyle.checkNew(oStyle) is True
    assert aStyle.getID() != oStyle.getID()

    aStyle = ODTParagraphStyle()
    oStyle = ODTParagraphStyle()
    aStyle.setColor("#000000")
    oStyle.setColor("#111111")
    assert aStyle.checkNew(oStyle) is True
    assert aStyle.getID() != oStyle.getID()

# END Test testCoreToOdt_ODTParagraphStyle


@pytest.mark.core
def testCoreToOdt_ODTTextStyle():
    """Test the ODTTextStyle class.
    """
    txtStyle = ODTTextStyle()

    # Font Weight
    assert txtStyle._tAttr["font-weight"] == ["fo", None]
    txtStyle.setFontWeight("stuff")
    assert txtStyle._tAttr["font-weight"] == ["fo", None]
    txtStyle.setFontWeight("normal")
    assert txtStyle._tAttr["font-weight"] == ["fo", "normal"]
    txtStyle.setFontWeight("inherit")
    assert txtStyle._tAttr["font-weight"] == ["fo", "inherit"]
    txtStyle.setFontWeight("bold")
    assert txtStyle._tAttr["font-weight"] == ["fo", "bold"]
    txtStyle.setFontWeight("stuff")
    assert txtStyle._tAttr["font-weight"] == ["fo", None]

    # Font Style
    assert txtStyle._tAttr["font-style"] == ["fo", None]
    txtStyle.setFontStyle("stuff")
    assert txtStyle._tAttr["font-style"] == ["fo", None]
    txtStyle.setFontStyle("normal")
    assert txtStyle._tAttr["font-style"] == ["fo", "normal"]
    txtStyle.setFontStyle("inherit")
    assert txtStyle._tAttr["font-style"] == ["fo", "inherit"]
    txtStyle.setFontStyle("italic")
    assert txtStyle._tAttr["font-style"] == ["fo", "italic"]
    txtStyle.setFontStyle("stuff")
    assert txtStyle._tAttr["font-style"] == ["fo", None]

    # Line Through Style
    assert txtStyle._tAttr["text-line-through-style"] == ["style", None]
    txtStyle.setStrikeStyle("stuff")
    assert txtStyle._tAttr["text-line-through-style"] == ["style", None]
    txtStyle.setStrikeStyle("none")
    assert txtStyle._tAttr["text-line-through-style"] == ["style", "none"]
    txtStyle.setStrikeStyle("solid")
    assert txtStyle._tAttr["text-line-through-style"] == ["style", "solid"]
    txtStyle.setStrikeStyle("stuff")
    assert txtStyle._tAttr["text-line-through-style"] == ["style", None]

    # Line Through Type
    assert txtStyle._tAttr["text-line-through-type"]  == ["style", None]
    txtStyle.setStrikeType("stuff")
    assert txtStyle._tAttr["text-line-through-type"]  == ["style", None]
    txtStyle.setStrikeType("none")
    assert txtStyle._tAttr["text-line-through-type"]  == ["style", "none"]
    txtStyle.setStrikeType("single")
    assert txtStyle._tAttr["text-line-through-type"]  == ["style", "single"]
    txtStyle.setStrikeType("double")
    assert txtStyle._tAttr["text-line-through-type"]  == ["style", "double"]
    txtStyle.setStrikeType("stuff")
    assert txtStyle._tAttr["text-line-through-type"]  == ["style", None]

    # Pack XML
    # ========
    txtStyle.setFontWeight("bold")
    txtStyle.setFontStyle("italic")
    txtStyle.setStrikeStyle("solid")
    txtStyle.setStrikeType("single")
    xStyle = etree.Element("test", nsmap={
        "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
        "fo":    "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    })
    txtStyle.packXML(xStyle, "test")
    assert xmlToText(xStyle) == (
        '<test><style:style style:name="test" style:family="text"><style:text-properties '
        'fo:font-weight="bold" fo:font-style="italic" style:text-line-through-style="solid" '
        'style:text-line-through-type="single"/></style:style></test>'
    )

# END Test testCoreToOdt_ODTTextStyle


@pytest.mark.core
def testCoreToOdt_XMLParagraph():
    """Test XML encoding of paragraph.
    """
    nsMap = {
        "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        "style":  "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
        "loext":  "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0",
        "text":   "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        "meta":   "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
        "fo":     "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    }

    # Stage 1 : Text
    # ==============

    xRoot = etree.Element("root", nsmap=nsMap)
    xElem = etree.SubElement(xRoot, "{%s}p" % nsMap["text"])
    xmlPar = XMLParagraph(xElem)

    # Plain Text
    xmlPar.appendText("Hello World")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello World</text:p>'
        '</root>'
    )

    # Text Span
    xmlPar.appendSpan("spanned text", "T1")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello World'
        '<text:span text:style-name="T1">spanned text</text:span>'
        '</text:p>'
        '</root>'
    )

    # Tail Text
    xmlPar.appendText("more text")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello World'
        '<text:span text:style-name="T1">spanned text</text:span>'
        'more text</text:p>'
        '</root>'
    )

    assert xmlPar.checkError() == (0, "")

    # Stage 2 : Line Breaks
    # =====================

    xRoot = etree.Element("root", nsmap=nsMap)
    xElem = etree.SubElement(xRoot, "{%s}p" % nsMap["text"])
    xmlPar = XMLParagraph(xElem)

    # Plain Text w/Line Break
    xmlPar.appendText("Hello\nWorld\n!!")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:line-break/>World<text:line-break/>!!</text:p>'
        '</root>'
    )

    # Text Span w/Line Break
    xmlPar.appendSpan("spanned\ntext", "T1")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:line-break/>World<text:line-break/>!!'
        '<text:span text:style-name="T1">spanned<text:line-break/>text</text:span></text:p>'
        '</root>'
    )

    # Tail Text w/Line Break
    xmlPar.appendText("more\ntext")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:line-break/>World<text:line-break/>!!'
        '<text:span text:style-name="T1">spanned<text:line-break/>text</text:span>'
        'more<text:line-break/>text</text:p>'
        '</root>'
    )

    assert xmlPar.checkError() == (0, "")

    # Stage 3 : Tabs
    # ==============

    xRoot = etree.Element("root", nsmap=nsMap)
    xElem = etree.SubElement(xRoot, "{%s}p" % nsMap["text"])
    xmlPar = XMLParagraph(xElem)

    # Plain Text w/Line Break
    xmlPar.appendText("Hello\tWorld\t!!")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:tab/>World<text:tab/>!!</text:p>'
        '</root>'
    )

    # Text Span w/Line Break
    xmlPar.appendSpan("spanned\ttext", "T1")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:tab/>World<text:tab/>!!'
        '<text:span text:style-name="T1">spanned<text:tab/>text</text:span></text:p>'
        '</root>'
    )

    # Tail Text w/Line Break
    xmlPar.appendText("more\ttext")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:tab/>World<text:tab/>!!'
        '<text:span text:style-name="T1">spanned<text:tab/>text</text:span>'
        'more<text:tab/>text</text:p>'
        '</root>'
    )

    assert xmlPar.checkError() == (0, "")

    # Stage 4 : Spaces
    # ================

    xRoot = etree.Element("root", nsmap=nsMap)
    xElem = etree.SubElement(xRoot, "{%s}p" % nsMap["text"])
    xmlPar = XMLParagraph(xElem)

    # Plain Text w/Spaces
    xmlPar.appendText("Hello  World   !!")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello <text:s/>World <text:s text:c="2"/>!!</text:p>'
        '</root>'
    )

    # Text Span w/Spaces
    xmlPar.appendSpan("spanned    text", "T1")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello <text:s/>World <text:s text:c="2"/>!!'
        '<text:span text:style-name="T1">spanned <text:s text:c="3"/>text</text:span></text:p>'
        '</root>'
    )

    # Tail Text w/Spaces
    xmlPar.appendText("more     text")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello <text:s/>World <text:s text:c="2"/>!!'
        '<text:span text:style-name="T1">spanned <text:s text:c="3"/>text</text:span>'
        'more <text:s text:c="4"/>text</text:p>'
        '</root>'
    )

    assert xmlPar.checkError() == (0, "")

    # Stage 5 : Lots of Spaces
    # ========================

    xRoot = etree.Element("root", nsmap=nsMap)
    xElem = etree.SubElement(xRoot, "{%s}p" % nsMap["text"])
    xmlPar = XMLParagraph(xElem)

    # Plain Text w/Many Spaces
    xmlPar.appendText("  \t A \n  B ")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p><text:s text:c="2"/><text:tab/> A <text:line-break/> <text:s/>B </text:p>'
        '</root>'
    )

    # Text Span w/Many Spaces
    xmlPar.appendSpan("  C  \t  D \n E ", "T1")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p><text:s text:c="2"/><text:tab/> A <text:line-break/> <text:s/>B '
        '<text:span text:style-name="T1"> <text:s/>C <text:s/><text:tab/> <text:s/>D '
        '<text:line-break/> E </text:span></text:p>'
        '</root>'
    )

    assert xmlPar.checkError() == (0, "")

    # Check Error
    # ===========

    xRoot = etree.Element("root", nsmap=nsMap)
    xElem = etree.SubElement(xRoot, "{%s}p" % nsMap["text"])
    xmlPar = XMLParagraph(xElem)

    xmlPar.appendText("A")
    xmlPar._nState = 5
    xmlPar.appendText("B")

    assert xmlPar.checkError() == (1, "1 char(s) were not written: 'AB'")

# END Test testCoreToOdt_XMLParagraph


@pytest.mark.core
def testCoreToOdt_MkTag():
    """Test the tag maker function.
    """
    assert _mkTag("office", "text") == "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}text"
    assert _mkTag("style", "text") == "{urn:oasis:names:tc:opendocument:xmlns:style:1.0}text"
    assert _mkTag("blabla", "text") == "text"

# END Test testCoreToOdt_MkTag
