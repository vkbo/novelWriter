"""
novelWriter – ToOdt Class Tester
=================================

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

import pytest
import zipfile
import xml.etree.ElementTree as ET

from shutil import copyfile

from tools import ODT_IGNORE, cmpFiles

from novelwriter.common import xmlIndent
from novelwriter.constants import nwHeadFmt
from novelwriter.core.toodt import ToOdt, ODTParagraphStyle, ODTTextStyle, XMLParagraph, _mkTag
from novelwriter.core.project import NWProject

XML_NS = [
    ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"',
    ' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"',
    ' xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0"',
    ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"',
    ' xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"',
    ' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"',
    ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
]


def xmlToText(xElem):
    """Get the text content of an XML element."""
    rTxt = ET.tostring(xElem, encoding="utf-8", xml_declaration=False).decode()
    for nSpace in XML_NS:
        rTxt = rTxt.replace(nSpace, "")
    return rTxt


@pytest.mark.core
def testCoreToOdt_Init(mockGUI):
    """Test initialisation of the ODT document."""
    project = NWProject()

    # Flat Doc
    # ========

    odt = ToOdt(project, isFlat=True)
    odt.initDocument()

    # Document XML
    assert odt._dFlat.tag == _mkTag("office", "document")
    assert odt._dCont.tag == ""
    assert odt._dMeta.tag == ""
    assert odt._dStyl.tag == ""

    # Content XML
    assert odt._xMeta.tag == _mkTag("office", "meta")
    assert odt._xFont.tag == _mkTag("office", "font-face-decls")
    assert odt._xFnt2.tag == ""
    assert odt._xStyl.tag == _mkTag("office", "styles")
    assert odt._xAuto.tag == _mkTag("office", "automatic-styles")
    assert odt._xAut2.tag == ""
    assert odt._xMast.tag == _mkTag("office", "master-styles")
    assert odt._xBody.tag == _mkTag("office", "body")
    assert odt._xText.tag == _mkTag("office", "text")

    # ODT Doc
    # =======

    odt = ToOdt(project, isFlat=False)
    odt.initDocument()

    # Document XML
    assert odt._dFlat.tag == ""
    assert odt._dCont.tag == _mkTag("office", "document-content")
    assert odt._dMeta.tag == _mkTag("office", "document-meta")
    assert odt._dStyl.tag == _mkTag("office", "document-styles")

    # Content XML
    assert odt._xMeta.tag == _mkTag("office", "meta")
    assert odt._xFont.tag == _mkTag("office", "font-face-decls")
    assert odt._xFnt2.tag == _mkTag("office", "font-face-decls")
    assert odt._xStyl.tag == _mkTag("office", "styles")
    assert odt._xAuto.tag == _mkTag("office", "automatic-styles")
    assert odt._xAut2.tag == _mkTag("office", "automatic-styles")
    assert odt._xMast.tag == _mkTag("office", "master-styles")
    assert odt._xBody.tag == _mkTag("office", "body")
    assert odt._xText.tag == _mkTag("office", "text")


# END Test testCoreToOdt_Init


@pytest.mark.core
def testCoreToOdt_TextFormatting(mockGUI):
    """Test formatting of paragraphs."""
    project = NWProject()
    odt = ToOdt(project, isFlat=True)

    odt.initDocument()
    assert xmlToText(odt._xText) == "<office:text />"

    # Paragraph Style
    # ===============
    oStyle = ODTParagraphStyle()

    assert odt._paraStyle("stuff", oStyle) == "Standard"
    assert odt._paraStyle("Text_20_body", oStyle) == "Text_20_body"

    # Create new para style
    oStyle.setTextAlign("center")
    assert odt._paraStyle("Text_20_body", oStyle) == "P1"

    # Return the same style on second call
    assert odt._paraStyle("Text_20_body", oStyle) == "P1"

    assert list(odt._mainPara.keys()) == [
        "Text_20_body", "Text_20_Meta", "Title", "Separator",
        "Heading_20_1", "Heading_20_2", "Heading_20_3", "Heading_20_4", "Header",
    ]

    key = "071d6b2e4764749f8c78d3c1ab9099fa04c07d2d53fd3de61eb1bdf1cb4845c3"
    assert odt._autoPara[key][0] == "P1"
    assert isinstance(odt._autoPara[key][1], ODTParagraphStyle)

    # Paragraph Formatting
    # ====================
    oStyle = ODTParagraphStyle()

    # No Text
    odt.initDocument()
    odt._addTextPar("Standard", oStyle, "")
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Standard" />'
        '</office:text>'
    )

    # No Format
    odt.initDocument()
    odt._addTextPar("Standard", oStyle, "Hello World")
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Standard">Hello World</text:p>'
        '</office:text>'
    )

    # Heading Level None
    odt.initDocument()
    odt._addTextPar("Standard", oStyle, "Hello World", isHead=True)
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="Standard">Hello World</text:h>'
        '</office:text>'
    )

    # Heading Level 1
    odt.initDocument()
    odt._addTextPar("Standard", oStyle, "Hello World", isHead=True, oLevel="1")
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="Standard" text:outline-level="1">Hello World</text:h>'
        '</office:text>'
    )

    # Formatted Text
    odt.initDocument()
    text = "A bold word"
    fmt = [(2, odt.FMT_B_B), (6, odt.FMT_B_E)]
    odt._addTextPar("Standard", oStyle, text, tFmt=fmt)
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Standard">A <text:span text:style-name="T1">bold</text:span> '
        'word</text:p>'
        '</office:text>'
    )

    # Incorrectly Formatted Text
    odt.initDocument()
    text = "A few words"
    fmt = [(2, odt.FMT_B_B), (5, odt.FMT_B_E), (7, 99999)]
    odt._addTextPar("Standard", oStyle, text, tFmt=fmt)
    assert odt.errData == ["Unknown format tag encountered"]
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Standard">A <text:span text:style-name="T1">few</text:span> '
        'words</text:p>'
        '</office:text>'
    )

    # Unclosed format
    odt.initDocument()
    text = "A bold word"
    fmt = [(2, odt.FMT_B_B)]
    odt._addTextPar("Standard", oStyle, text, tFmt=fmt)
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Standard">A '
        '<text:span text:style-name="T1">bold word</text:span></text:p>'
        '</office:text>'
    )

    # Tabs and Breaks
    odt.initDocument()
    text = "Hello\n\tWorld"
    fmt = []
    odt._addTextPar("Standard", oStyle, text, tFmt=fmt)
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Standard">Hello<text:line-break /><text:tab />World</text:p>'
        '</office:text>'
    )

# END Test testCoreToOdt_TextFormatting


@pytest.mark.core
def testCoreToOdt_Convert(mockGUI):
    """Test the converter of the ToOdt class."""
    project = NWProject()
    odt = ToOdt(project, isFlat=True)

    odt._isNovel = True

    def getStyle(styleName):
        for aSet in odt._autoPara.values():
            if aSet[0] == styleName:
                return aSet[1]
        return None

    # Headers
    # =======

    # Header 1
    odt._text = "# Title\n"
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="P1" text:outline-level="1">Title</text:h>'
        '</office:text>'
    )

    # Header 2
    odt._text = "## Chapter\n"
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="P2" text:outline-level="2">Chapter</text:h>'
        '</office:text>'
    )

    # Header 3
    odt._text = "### Scene\n"
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_20_3" text:outline-level="3">Scene</text:h>'
        '</office:text>'
    )

    # Header 4
    odt._text = "#### Section\n"
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_20_4" text:outline-level="4">Section</text:h>'
        '</office:text>'
    )

    # Title
    odt._text = "#! Title\n"
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Title">Title</text:p>'
        '</office:text>'
    )

    # Unnumbered chapter
    odt._text = "##! Prologue\n"
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="P2" text:outline-level="2">Prologue</text:h>'
        '</office:text>'
    )

    # Paragraphs
    # ==========

    # Nested Markdown Text
    odt._text = "Some ~~nested **bold** and _italics_ text~~ text."
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_20_body">Some '
        '<text:span text:style-name="T1">nested </text:span>'
        '<text:span text:style-name="T2">bold</text:span>'
        '<text:span text:style-name="T1"> and </text:span>'
        '<text:span text:style-name="T3">italics</text:span>'
        '<text:span text:style-name="T1"> text</text:span> text.</text:p>'
        '</office:text>'
    )

    # Nested Shortcode Text, Emphasis
    odt._text = "Some [s]nested [b]bold[/b] [u]and[/u] [i]italics[/i] text[/s] text."
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_20_body">Some '
        '<text:span text:style-name="T1">nested </text:span>'
        '<text:span text:style-name="T2">bold</text:span>'
        '<text:span text:style-name="T1"> </text:span>'
        '<text:span text:style-name="T4">and</text:span>'
        '<text:span text:style-name="T1"> </text:span>'
        '<text:span text:style-name="T3">italics</text:span>'
        '<text:span text:style-name="T1"> text</text:span> text.</text:p>'
        '</office:text>'
    )

    # Nested Shortcode Text, Super/Subscript
    odt._text = "Some super[sup]script[/sup] and sub[sub]script[/sub] text."
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_20_body">Some '
        'super<text:span text:style-name="T5">script</text:span> and '
        'sub<text:span text:style-name="T6">script</text:span> text.</text:p>'
        '</office:text>'
    )

    # Hard Break
    odt._text = "Some text.\nNext line\n"
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_20_body">Some text.<text:line-break />Next line</text:p>'
        '</office:text>'
    )

    # Tab
    odt._text = "\tItem 1\tItem 2\n"
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_20_body"><text:tab />Item 1<text:tab />Item 2</text:p>'
        '</office:text>'
    )

    # Tab in Format
    odt._text = "Some **bold\ttext**"
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_20_body">Some <text:span text:style-name="T7">'
        'bold<text:tab />text</text:span></text:p>'
        '</office:text>'
    )

    # Multiple Spaces
    odt._text = (
        "### Scene\n\n"
        "Hello World\n\n"
        "Hello  World\n\n"
        "Hello   World\n\n"
    )
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_20_3" text:outline-level="3">Scene</text:h>'
        '<text:p text:style-name="Text_20_body">Hello World</text:p>'
        '<text:p text:style-name="Text_20_body">Hello <text:s />World</text:p>'
        '<text:p text:style-name="Text_20_body">Hello <text:s text:c="2" />World</text:p>'
        '</office:text>'
    )

    # Synopsis, Short, Comment, Keywords
    odt._text = (
        "### Scene\n\n"
        "@pov: Jane\n\n"
        "% synopsis: So it begins\n\n"
        "% short: Then what\n\n"
        "% A plain comment\n\n"
    )
    odt.setSynopsis(True)
    odt.setComments(True)
    odt.setKeywords(True)
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_20_3" text:outline-level="3">Scene</text:h>'
        '<text:p text:style-name="Text_20_Meta"><text:span text:style-name="T7">'
        'Point of View:</text:span> Jane</text:p>'
        '<text:p text:style-name="Text_20_Meta"><text:span text:style-name="T7">'
        'Synopsis:</text:span> So it begins</text:p>'
        '<text:p text:style-name="Text_20_Meta"><text:span text:style-name="T7">'
        'Short Description:</text:span> Then what</text:p>'
        '<text:p text:style-name="Text_20_Meta"><text:span text:style-name="T7">'
        'Comment:</text:span> A plain comment</text:p>'
        '</office:text>'
    )

    # Scene Separator
    odt._text = "### Scene One\n\nText\n\n### Scene Two\n\nText"
    odt.setSceneFormat("* * *", False)
    odt.tokenizeText()
    odt.doHeaders()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Separator">* * *</text:p>'
        '<text:p text:style-name="Text_20_body">Text</text:p>'
        '<text:p text:style-name="Separator">* * *</text:p>'
        '<text:p text:style-name="Text_20_body">Text</text:p>'
        '</office:text>'
    )

    # Scene Break
    odt._text = "### Scene One\n\nText\n\n### Scene Two\n\nText"
    odt.setSceneFormat("", False)
    odt.tokenizeText()
    odt.doHeaders()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Separator" />'
        '<text:p text:style-name="Text_20_body">Text</text:p>'
        '<text:p text:style-name="Separator" />'
        '<text:p text:style-name="Text_20_body">Text</text:p>'
        '</office:text>'
    )

    # Paragraph Styles
    odt._text = (
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
    odt.setKeywords(True)
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_20_3" text:outline-level="3">Scene</text:h>'
        '<text:p text:style-name="P3"><text:span text:style-name="T7">'
        'Point of View:</text:span> Jane</text:p>'
        '<text:p text:style-name="P4"><text:span text:style-name="T7">'
        'Characters:</text:span> John</text:p>'
        '<text:p text:style-name="Text_20_Meta"><text:span text:style-name="T7">'
        'Plot:</text:span> Main</text:p>'
        '<text:p text:style-name="P5">Right align</text:p>'
        '<text:p text:style-name="Text_20_body">Left Align</text:p>'
        '<text:p text:style-name="P6">Centered</text:p>'
        '<text:p text:style-name="P7">Left indent</text:p>'
        '<text:p text:style-name="P8">Right indent</text:p>'
        '</office:text>'
    )
    assert getStyle("P3")._pAttr["margin-bottom"] == ["fo", "0.000cm"]  # type: ignore
    assert getStyle("P4")._pAttr["margin-bottom"] == ["fo", "0.000cm"]  # type: ignore
    assert getStyle("P4")._pAttr["margin-top"] == ["fo", "0.000cm"]  # type: ignore
    assert getStyle("P5")._pAttr["text-align"] == ["fo", "right"]  # type: ignore
    assert getStyle("P6")._pAttr["text-align"] == ["fo", "center"]  # type: ignore
    assert getStyle("P7")._pAttr["margin-left"] == ["fo", "1.693cm"]  # type: ignore
    assert getStyle("P8")._pAttr["margin-right"] == ["fo", "1.693cm"]  # type: ignore

    # Justified
    odt._text = (
        "### Scene\n\n"
        "Regular paragraph\n\n"
        "with\nbreak\n\n"
        "Left Align <<\n\n"
    )
    odt.setJustify(True)
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_20_3" text:outline-level="3">Scene</text:h>'
        '<text:p text:style-name="Text_20_body">Regular paragraph</text:p>'
        '<text:p text:style-name="P9">with<text:line-break />break</text:p>'
        '<text:p text:style-name="P9">Left Align</text:p>'
        '</office:text>'
    )
    assert getStyle("P9")._pAttr["text-align"] == ["fo", "left"]  # type: ignore

    # Page Breaks
    odt._text = (
        "## Chapter One\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "Text\n\n"
    )
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:h text:style-name="P2" text:outline-level="2">Chapter One</text:h>'
        '<text:p text:style-name="Text_20_body">Text</text:p>'
        '<text:h text:style-name="P2" text:outline-level="2">Chapter Two</text:h>'
        '<text:p text:style-name="Text_20_body">Text</text:p>'
        '</office:text>'
    )

    # Test for issue #1412
    # ====================
    # See: https://github.com/vkbo/novelWriter/issues/1412

    odt._text = "Test text \\**_bold_** and more."
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()
    assert odt.errData == []
    assert xmlToText(odt._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_20_body">Test text **<text:span text:style-name="T8">'
        'bold</text:span>** and more.</text:p>'
        '</office:text>'
    )

# END Test testCoreToOdt_Convert


@pytest.mark.core
def testCoreToOdt_ConvertDirect(mockGUI):
    """Test the converter directly using the ToOdt class to reach some
    otherwise hard to reach conditions.
    """
    project = NWProject()
    doc = ToOdt(project, isFlat=True)

    doc._isNovel = True

    # Justified
    doc = ToOdt(project, isFlat=True)
    doc._tokens = [
        (doc.T_TEXT, 1, "This is a paragraph", [], doc.A_JUSTIFY),
        (doc.T_EMPTY, 1, "", None, doc.A_NONE),
    ]
    doc.initDocument()
    doc.doConvert()
    doc.closeDocument()
    assert (
        '<style:style style:name="P1" style:family="paragraph" '
        'style:parent-style-name="Text_20_body">'
        '<style:paragraph-properties fo:text-align="justify" />'
        '</style:style>'
    ) in xmlToText(doc._xAuto)
    assert xmlToText(doc._xText) == (
        '<office:text>'
        '<text:p text:style-name="P1">This is a paragraph</text:p>'
        '</office:text>'
    )

    # Page Break After
    doc = ToOdt(project, isFlat=True)
    doc._tokens = [
        (doc.T_TEXT, 1, "This is a paragraph", [], doc.A_PBA),
        (doc.T_EMPTY, 1, "", None, doc.A_NONE),
    ]
    doc.initDocument()
    doc.doConvert()
    doc.closeDocument()
    assert (
        '<style:style style:name="P1" style:family="paragraph" '
        'style:parent-style-name="Text_20_body">'
        '<style:paragraph-properties fo:break-after="page" />'
        '</style:style>'
    ) in xmlToText(doc._xAuto)
    assert xmlToText(doc._xText) == (
        '<office:text>'
        '<text:p text:style-name="P1">This is a paragraph</text:p>'
        '</office:text>'
    )

# END Test testCoreToOdt_ConvertDirect


@pytest.mark.core
def testCoreToOdt_SaveFlat(mockGUI, fncPath, tstPaths):
    """Test the document save functions."""
    project = NWProject()
    project.data.setAuthor("Jane Smith")
    project.data.setName("Test Project")
    project.data.setSaveCount(1234)
    project.data.setEditTime(3674096)

    odt = ToOdt(project, isFlat=True)
    odt._isNovel = True
    odt._dLanguage = ""
    odt.setLanguage(None)  # type: ignore
    assert odt._dLanguage == ""
    odt.setLanguage("nb_NO")
    assert odt._dLanguage == "nb"
    odt.setColourHeaders(True)
    assert odt._colourHead is True
    odt.setHeaderFormat(nwHeadFmt.ODT_AUTO, 1)
    assert odt._headerFormat == nwHeadFmt.ODT_AUTO

    odt.setPageLayout(148, 210, 20, 18, 17, 15)
    assert odt._mDocWidth  == "14.800cm"
    assert odt._mDocHeight == "21.000cm"
    assert odt._mDocTop    == "2.000cm"
    assert odt._mDocBtm    == "1.800cm"
    assert odt._mDocLeft   == "1.700cm"
    assert odt._mDocRight  == "1.500cm"

    odt._text = (
        "## Chapter One\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "Text\n\n"
    )
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()

    flatFile = fncPath / "document.fodt"
    testFile = tstPaths.outDir / "coreToOdt_SaveFlat_document.fodt"
    compFile = tstPaths.refDir / "coreToOdt_SaveFlat_document.fodt"

    odt.saveFlatXML(flatFile)
    assert flatFile.exists()

    copyfile(flatFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=ODT_IGNORE)

# END Test testCoreToOdt_SaveFlat


@pytest.mark.core
def testCoreToOdt_SaveFull(mockGUI, fncPath, tstPaths):
    """Test the document save functions."""
    project = NWProject()
    project.data.setAuthor("Jane Smith")
    project.data.setName("Test Project")
    project.data.setSaveCount(1234)
    project.data.setEditTime(3674096)

    odt = ToOdt(project, isFlat=False)
    odt._isNovel = True

    # Set a format without page number
    odt.setHeaderFormat(f"{nwHeadFmt.ODT_PROJECT} - {nwHeadFmt.ODT_AUTHOR}", 0)

    odt._text = (
        "## Chapter One\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "Text\n\n"
    )
    odt.tokenizeText()
    odt.initDocument()
    odt.doConvert()
    odt.closeDocument()

    fullFile = fncPath / "document.odt"

    odt.saveOpenDocText(fullFile)
    assert fullFile.exists()
    assert zipfile.is_zipfile(fullFile)

    maniFile = tstPaths.outDir / "coreToOdt_SaveFull_manifest.xml"
    settFile = tstPaths.outDir / "coreToOdt_SaveFull_settings.xml"
    contFile = tstPaths.outDir / "coreToOdt_SaveFull_content.xml"
    metaFile = tstPaths.outDir / "coreToOdt_SaveFull_meta.xml"
    stylFile = tstPaths.outDir / "coreToOdt_SaveFull_styles.xml"

    maniComp = tstPaths.refDir / "coreToOdt_SaveFull_manifest.xml"
    settComp = tstPaths.refDir / "coreToOdt_SaveFull_settings.xml"
    contComp = tstPaths.refDir / "coreToOdt_SaveFull_content.xml"
    metaComp = tstPaths.refDir / "coreToOdt_SaveFull_meta.xml"
    stylComp = tstPaths.refDir / "coreToOdt_SaveFull_styles.xml"

    extaxtTo = tstPaths.outDir / "coreToOdt_SaveFull"

    with zipfile.ZipFile(fullFile, mode="r") as zipObj:
        zipObj.extract("META-INF/manifest.xml", extaxtTo)
        zipObj.extract("settings.xml", extaxtTo)
        zipObj.extract("content.xml", extaxtTo)
        zipObj.extract("meta.xml", extaxtTo)
        zipObj.extract("styles.xml", extaxtTo)

    maniOut = tstPaths.outDir / "coreToOdt_SaveFull" / "META-INF" / "manifest.xml"
    settOut = tstPaths.outDir / "coreToOdt_SaveFull" / "settings.xml"
    contOut = tstPaths.outDir / "coreToOdt_SaveFull" / "content.xml"
    metaOut = tstPaths.outDir / "coreToOdt_SaveFull" / "meta.xml"
    stylOut = tstPaths.outDir / "coreToOdt_SaveFull" / "styles.xml"

    def prettifyXml(inFile, outFile):
        with open(outFile, mode="wb") as fStream:
            xml = ET.parse(inFile)
            xmlIndent(xml)
            xml.write(fStream, encoding="utf-8", xml_declaration=True)

    prettifyXml(maniOut, maniFile)
    prettifyXml(settOut, settFile)
    prettifyXml(contOut, contFile)
    prettifyXml(metaOut, metaFile)
    prettifyXml(stylOut, stylFile)

    assert cmpFiles(maniFile, maniComp)
    assert cmpFiles(settFile, settComp)
    assert cmpFiles(contFile, contComp)
    assert cmpFiles(metaFile, metaComp, ignoreStart=ODT_IGNORE)
    assert cmpFiles(stylFile, stylComp)

# END Test testCoreToOdt_SaveFull


@pytest.mark.core
def testCoreToOdt_Format(mockGUI):
    """Test the formatters for the ToOdt class."""
    project = NWProject()
    odt = ToOdt(project, isFlat=True)

    assert odt._formatSynopsis("synopsis text", True) == (
        "Synopsis: synopsis text", [(0, ToOdt.FMT_B_B), (9, ToOdt.FMT_B_E)]
    )
    assert odt._formatSynopsis("short text", False) == (
        "Short Description: short text", [(0, ToOdt.FMT_B_B), (18, ToOdt.FMT_B_E)]
    )
    assert odt._formatComments("comment text") == (
        "Comment: comment text", [(0, ToOdt.FMT_B_B), (8, ToOdt.FMT_B_E)]
    )

    assert odt._formatKeywords("") == ("", [])
    assert odt._formatKeywords("tag: Jane") == (
        "Tag: Jane", [(0, ToOdt.FMT_B_B), (4, ToOdt.FMT_B_E)]
    )
    assert odt._formatKeywords("char: Bod, Jane") == (
        "Characters: Bod, Jane", [(0, ToOdt.FMT_B_B), (11, ToOdt.FMT_B_E)]
    )

# END Test testCoreToOdt_Format


@pytest.mark.core
def testCoreToOdt_ODTParagraphStyle():
    """Test the ODTParagraphStyle class."""
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
    xStyle = ET.Element("test")
    parStyle.packXML(xStyle, "test")
    assert xmlToText(xStyle) == (
        '<test>'
        '<style:style style:name="test" style:family="paragraph" style:display-name="Name" '
        'style:parent-style-name="Name" style:next-style-name="Name">'
        '<style:paragraph-properties fo:margin-top="0.000cm" fo:margin-bottom="0.000cm" '
        'fo:margin-left="0.000cm" fo:margin-right="0.000cm" fo:line-height="1.15" />'
        '<style:text-properties style:font-name="Verdana" fo:font-family="Verdana" '
        'fo:font-size="12pt" fo:color="#000000" loext:opacity="1.00" />'
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
    """Test the ODTTextStyle class."""
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

    # Text Position
    assert txtStyle._tAttr["text-position"] == ["style", None]
    txtStyle.setTextPosition("stuff")
    assert txtStyle._tAttr["text-position"] == ["style", None]
    txtStyle.setTextPosition("super")
    assert txtStyle._tAttr["text-position"] == ["style", "super 58%"]
    txtStyle.setTextPosition("sub")
    assert txtStyle._tAttr["text-position"] == ["style", "sub 58%"]
    txtStyle.setTextPosition("stuff")
    assert txtStyle._tAttr["text-position"] == ["style", None]

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
    txtStyle.setStrikeType("none")  # Deprecated in ODF 1.3
    assert txtStyle._tAttr["text-line-through-type"]  == ["style", None]
    txtStyle.setStrikeType("single")
    assert txtStyle._tAttr["text-line-through-type"]  == ["style", "single"]
    txtStyle.setStrikeType("double")
    assert txtStyle._tAttr["text-line-through-type"]  == ["style", "double"]
    txtStyle.setStrikeType("stuff")
    assert txtStyle._tAttr["text-line-through-type"]  == ["style", None]

    # Underline Style
    assert txtStyle._tAttr["text-underline-style"] == ["style", None]
    txtStyle.setUnderlineStyle("stuff")
    assert txtStyle._tAttr["text-underline-style"] == ["style", None]
    txtStyle.setUnderlineStyle("none")
    assert txtStyle._tAttr["text-underline-style"] == ["style", "none"]
    txtStyle.setUnderlineStyle("solid")
    assert txtStyle._tAttr["text-underline-style"] == ["style", "solid"]
    txtStyle.setUnderlineStyle("stuff")
    assert txtStyle._tAttr["text-underline-style"] == ["style", None]

    # Underline Width
    assert txtStyle._tAttr["text-underline-width"] == ["style", None]
    txtStyle.setUnderlineWidth("stuff")
    assert txtStyle._tAttr["text-underline-width"] == ["style", None]
    txtStyle.setUnderlineWidth("auto")
    assert txtStyle._tAttr["text-underline-width"] == ["style", "auto"]
    txtStyle.setUnderlineWidth("stuff")
    assert txtStyle._tAttr["text-underline-width"] == ["style", None]

    # Underline Colour
    assert txtStyle._tAttr["text-underline-color"] == ["style", None]
    txtStyle.setUnderlineColour("stuff")
    assert txtStyle._tAttr["text-underline-color"] == ["style", None]
    txtStyle.setUnderlineColour("font-color")
    assert txtStyle._tAttr["text-underline-color"] == ["style", "font-color"]
    txtStyle.setUnderlineColour("stuff")
    assert txtStyle._tAttr["text-underline-color"] == ["style", None]

    # Pack XML
    # ========
    txtStyle.setFontWeight("bold")
    txtStyle.setFontStyle("italic")
    txtStyle.setTextPosition("super")
    txtStyle.setStrikeStyle("solid")
    txtStyle.setStrikeType("single")
    xStyle = ET.Element("test")
    txtStyle.packXML(xStyle, "test")
    assert xmlToText(xStyle) == (
        '<test><style:style style:name="test" style:family="text"><style:text-properties '
        'fo:font-weight="bold" fo:font-style="italic" style:text-position="super 58%" '
        'style:text-line-through-style="solid" style:text-line-through-type="single" />'
        '</style:style></test>'
    )

# END Test testCoreToOdt_ODTTextStyle


@pytest.mark.core
def testCoreToOdt_XMLParagraph():
    """Test XML encoding of paragraph."""
    # Stage 1 : Text
    # ==============

    xRoot = ET.Element("root")
    xElem = ET.SubElement(xRoot, _mkTag("text", "p"))
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

    xRoot = ET.Element("root")
    xElem = ET.SubElement(xRoot, _mkTag("text", "p"))
    xmlPar = XMLParagraph(xElem)

    # Plain Text w/Line Break
    xmlPar.appendText("Hello\nWorld\n!!")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:line-break />World<text:line-break />!!</text:p>'
        '</root>'
    )

    # Text Span w/Line Break
    xmlPar.appendSpan("spanned\ntext", "T1")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:line-break />World<text:line-break />!!'
        '<text:span text:style-name="T1">spanned<text:line-break />text</text:span></text:p>'
        '</root>'
    )

    # Tail Text w/Line Break
    xmlPar.appendText("more\ntext")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:line-break />World<text:line-break />!!'
        '<text:span text:style-name="T1">spanned<text:line-break />text</text:span>'
        'more<text:line-break />text</text:p>'
        '</root>'
    )

    assert xmlPar.checkError() == (0, "")

    # Stage 3 : Tabs
    # ==============

    xRoot = ET.Element("root")
    xElem = ET.SubElement(xRoot, _mkTag("text", "p"))
    xmlPar = XMLParagraph(xElem)

    # Plain Text w/Line Break
    xmlPar.appendText("Hello\tWorld\t!!")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:tab />World<text:tab />!!</text:p>'
        '</root>'
    )

    # Text Span w/Line Break
    xmlPar.appendSpan("spanned\ttext", "T1")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:tab />World<text:tab />!!'
        '<text:span text:style-name="T1">spanned<text:tab />text</text:span></text:p>'
        '</root>'
    )

    # Tail Text w/Line Break
    xmlPar.appendText("more\ttext")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello<text:tab />World<text:tab />!!'
        '<text:span text:style-name="T1">spanned<text:tab />text</text:span>'
        'more<text:tab />text</text:p>'
        '</root>'
    )

    assert xmlPar.checkError() == (0, "")

    # Stage 4 : Spaces
    # ================

    xRoot = ET.Element("root")
    xElem = ET.SubElement(xRoot, _mkTag("text", "p"))
    xmlPar = XMLParagraph(xElem)

    # Plain Text w/Spaces
    xmlPar.appendText("Hello  World   !!")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello <text:s />World <text:s text:c="2" />!!</text:p>'
        '</root>'
    )

    # Text Span w/Spaces
    xmlPar.appendSpan("spanned    text", "T1")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello <text:s />World <text:s text:c="2" />!!'
        '<text:span text:style-name="T1">spanned <text:s text:c="3" />text</text:span></text:p>'
        '</root>'
    )

    # Tail Text w/Spaces
    xmlPar.appendText("more     text")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p>Hello <text:s />World <text:s text:c="2" />!!'
        '<text:span text:style-name="T1">spanned <text:s text:c="3" />text</text:span>'
        'more <text:s text:c="4" />text</text:p>'
        '</root>'
    )

    assert xmlPar.checkError() == (0, "")

    # Stage 5 : Lots of Spaces
    # ========================

    xRoot = ET.Element("root")
    xElem = ET.SubElement(xRoot, _mkTag("text", "p"))
    xmlPar = XMLParagraph(xElem)

    # Plain Text w/Many Spaces
    xmlPar.appendText("  \t A \n  B ")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p><text:s text:c="2" /><text:tab /> A <text:line-break /> <text:s />B </text:p>'
        '</root>'
    )

    # Text Span w/Many Spaces
    xmlPar.appendSpan("  C  \t  D \n E ", "T1")
    assert xmlToText(xRoot) == (
        '<root>'
        '<text:p><text:s text:c="2" /><text:tab /> A <text:line-break /> <text:s />B '
        '<text:span text:style-name="T1"> <text:s />C <text:s /><text:tab /> <text:s />D '
        '<text:line-break /> E </text:span></text:p>'
        '</root>'
    )

    assert xmlPar.checkError() == (0, "")

    # Check Error
    # ===========

    xRoot = ET.Element("root")
    xElem = ET.SubElement(xRoot, _mkTag("text", "p"))
    xmlPar = XMLParagraph(xElem)

    xmlPar.appendText("A")
    xmlPar._nState = 5
    xmlPar.appendText("B")

    assert xmlPar.checkError() == (1, "1 char(s) were not written: 'AB'")

# END Test testCoreToOdt_XMLParagraph


@pytest.mark.core
def testCoreToOdt_MkTag():
    """Test the tag maker function."""
    assert _mkTag("office", "text") == "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}text"
    assert _mkTag("style", "text") == "{urn:oasis:names:tc:opendocument:xmlns:style:1.0}text"
    assert _mkTag("blabla", "text") == "text"

# END Test testCoreToOdt_MkTag
