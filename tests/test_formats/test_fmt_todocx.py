"""
novelWriter – ToDocX Class Tester
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

import xml.etree.ElementTree as ET
import zipfile

import pytest

from novelwriter.common import xmlIndent
from novelwriter.constants import nwHeadFmt
from novelwriter.core.buildsettings import BuildSettings
from novelwriter.core.docbuild import NWBuildDocument
from novelwriter.core.project import NWProject
from novelwriter.enum import nwBuildFmt
from novelwriter.formats.shared import BlockFmt, BlockTyp
from novelwriter.formats.todocx import (
    S_FNOTE, S_HEAD1, S_HEAD2, S_HEAD3, S_HEAD4, S_META, S_NORM, S_SEP,
    S_TITLE, ToDocX, _mkTag, _wTag
)

from tests.tools import DOCX_IGNORE, cmpFiles

OOXML_SCM = "http://schemas.openxmlformats.org"
XML_NS = [
    f' xmlns:r="{OOXML_SCM}/officeDocument/2006/relationships"',
    f' xmlns:w="{OOXML_SCM}/wordprocessingml/2006/main"',
    f' xmlns:cp="{OOXML_SCM}/package/2006/metadata/core-properties"',
    ' xmlns:dc="http://purl.org/dc/elements/1.1/"',
    ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
    ' xmlns:xml="http://www.w3.org/XML/1998/namespace"',
    ' xmlns:dcterms="http://purl.org/dc/terms/"',
]


def xmlToText(xElem):
    """Get the text content of an XML element."""
    rTxt = ET.tostring(xElem, encoding="utf-8", xml_declaration=False).decode()
    for ns in XML_NS:
        rTxt = rTxt.replace(ns, "")
    return rTxt


@pytest.mark.core
def testFmtToDocX_ParagraphStyles(mockGUI):
    """Test formatting of paragraphs."""
    project = NWProject()
    doc = ToDocX(project)
    doc.setSynopsis(True)
    doc.setComments(True)
    doc.setKeywords(True)
    doc.initDocument()

    # Normal Text
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TEXT, 0, "Hello World", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr><w:r><w:rPr />'
        '<w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Title
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TITLE, 0, "Hello World", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_TITLE}" /></w:pPr><w:r><w:rPr />'
        '<w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Heading Level 1
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.HEAD1, 0, "Hello World", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_HEAD1}" /></w:pPr><w:r><w:rPr />'
        '<w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Heading Level 2
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.HEAD2, 0, "Hello World", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_HEAD2}" /></w:pPr><w:r><w:rPr />'
        '<w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Heading Level 3
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.HEAD3, 0, "Hello World", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_HEAD3}" /></w:pPr><w:r><w:rPr />'
        '<w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Heading Level 4
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.HEAD4, 0, "Hello World", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_HEAD4}" /></w:pPr><w:r><w:rPr />'
        '<w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Separator
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.SEP, 0, "* * *", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_SEP}" /></w:pPr><w:r><w:rPr />'
        '<w:t>* * *</w:t></w:r></w:p></w:body>'
    )

    # Empty Paragraph
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.SKIP, 0, "* * *", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr></w:p></w:body>'
    )

    # Synopsis
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.SYNOPSIS, 0, "Hello World", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_META}" /></w:pPr>'
        '<w:r><w:rPr><w:b /></w:rPr><w:t>Synopsis:</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve"> Hello World</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Short
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.SHORT, 0, "Hello World", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_META}" /></w:pPr>'
        '<w:r><w:rPr><w:b /></w:rPr><w:t>Short Description:</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve"> Hello World</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Comment
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.COMMENT, 0, "Hello World", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_META}" /></w:pPr>'
        '<w:r><w:rPr><w:b /></w:rPr><w:t>Comment:</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve"> Hello World</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Tags and References (Single)
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.KEYWORD, 0, "tag: Stuff", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_META}" /></w:pPr>'
        '<w:r><w:rPr><w:b /></w:rPr><w:t>Tag:</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve"> Stuff</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Tags and References (Multiple)
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.KEYWORD, 0, "char: Jane, John", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_META}" /></w:pPr>'
        '<w:r><w:rPr><w:b /></w:rPr><w:t>Characters:</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve"> Jane, John</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Tags and References (Invalid)
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.KEYWORD, 0, "stuff: Stuff", [], BlockFmt.NONE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_META}" /></w:pPr></w:p></w:body>'
    )


@pytest.mark.core
def testFmtToDocX_ParagraphFormatting(mockGUI):
    """Test formatting of paragraphs."""
    project = NWProject()
    doc = ToDocX(project)
    doc.setSynopsis(True)
    doc.setComments(True)
    doc.setKeywords(True)
    doc.initDocument()

    # Left Align
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TEXT, 0, "Hello World", [], BlockFmt.LEFT)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /><w:jc w:val="left" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Right Align
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TEXT, 0, "Hello World", [], BlockFmt.RIGHT)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /><w:jc w:val="right" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Center Align
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TEXT, 0, "Hello World", [], BlockFmt.CENTRE)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /><w:jc w:val="center" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Justify
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TEXT, 0, "Hello World", [], BlockFmt.JUSTIFY)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /><w:jc w:val="both" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Page Break Before
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TEXT, 0, "Hello World", [], BlockFmt.PBB)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr>'
        '<w:r><w:br w:type="page" /></w:r>'
        '<w:r><w:rPr /><w:t>Hello World</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Page Break After
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TEXT, 0, "Hello World", [], BlockFmt.PBA)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Hello World</w:t></w:r>'
        '<w:r><w:br w:type="page" /></w:r>'
        '</w:p></w:body>'
    )

    # Zero Margins
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TEXT, 0, "Hello World", [], BlockFmt.Z_TOPMRG | BlockFmt.Z_BTMMRG)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" />'
        '<w:spacing w:before="0" w:after="0" w:line="252" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # Indent
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TEXT, 0, "Hello World", [], BlockFmt.IND_L | BlockFmt.IND_R)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" />'
        '<w:ind w:left="880" w:right="880" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Hello World</w:t></w:r></w:p></w:body>'
    )

    # First Line Indent
    xTest = ET.Element(_wTag("body"))
    doc._blocks = [(BlockTyp.TEXT, 0, "Hello World", [], BlockFmt.IND_T)]
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" />'
        '<w:ind w:firstLine="308" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Hello World</w:t></w:r></w:p></w:body>'
    )


@pytest.mark.core
def testFmtToDocX_TextFormatting(mockGUI):
    """Test formatting of text."""
    project = NWProject()
    doc = ToDocX(project)
    doc.initDocument()

    # Markdown
    xTest = ET.Element(_wTag("body"))
    doc._text = "Text **bold**, _italic_, ~~strike~~."
    doc.tokenizeText()
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr>'
        '<w:r><w:rPr /><w:t xml:space="preserve">Text </w:t></w:r>'
        '<w:r><w:rPr><w:b /></w:rPr><w:t>bold</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve">, </w:t></w:r>'
        '<w:r><w:rPr><w:i /></w:rPr><w:t>italic</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve">, </w:t></w:r>'
        '<w:r><w:rPr><w:strike /></w:rPr><w:t>strike</w:t></w:r>'
        '<w:r><w:rPr /><w:t>.</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Nested Shortcode Text, Emphasis
    xTest = ET.Element(_wTag("body"))
    doc._text = "Some [s]nested [b]bold[/b] [u]and[/u] [i]italics[/i] text[/s] text."
    doc.tokenizeText()
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr>'
        '<w:r><w:rPr /><w:t xml:space="preserve">Some </w:t></w:r>'
        '<w:r><w:rPr><w:strike /></w:rPr><w:t xml:space="preserve">nested </w:t></w:r>'
        '<w:r><w:rPr><w:b /><w:strike /></w:rPr><w:t>bold</w:t></w:r>'
        '<w:r><w:rPr><w:strike /></w:rPr><w:t xml:space="preserve"> </w:t></w:r>'
        '<w:r><w:rPr><w:u w:val="single" /><w:strike /></w:rPr><w:t>and</w:t></w:r>'
        '<w:r><w:rPr><w:strike /></w:rPr><w:t xml:space="preserve"> </w:t></w:r>'
        '<w:r><w:rPr><w:i /><w:strike /></w:rPr><w:t>italics</w:t></w:r>'
        '<w:r><w:rPr><w:strike /></w:rPr><w:t xml:space="preserve"> text</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve"> text.</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Shortcode Text, Super/Subscript
    xTest = ET.Element(_wTag("body"))
    doc._text = "Some super[sup]script[/sup] and sub[sub]script[/sub] text."
    doc.tokenizeText()
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Some super</w:t></w:r>'
        '<w:r><w:rPr><w:vertAlign w:val="superscript" /></w:rPr><w:t>script</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve"> and sub</w:t></w:r>'
        '<w:r><w:rPr><w:vertAlign w:val="subscript" /></w:rPr><w:t>script</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve"> text.</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Shortcode Text, Underline/Highlight
    xTest = ET.Element(_wTag("body"))
    doc._text = "Some [u]underlined and [m]highlighted[/m][/u] text."
    doc.tokenizeText()
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr>'
        '<w:r><w:rPr /><w:t xml:space="preserve">Some </w:t></w:r>'
        '<w:r><w:rPr><w:u w:val="single" /></w:rPr>'
        '<w:t xml:space="preserve">underlined and </w:t></w:r>'
        '<w:r><w:rPr><w:u w:val="single" /><w:shd w:fill="ffffa6" w:val="clear" /></w:rPr>'
        '<w:t>highlighted</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve"> text.</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Hard Break
    xTest = ET.Element(_wTag("body"))
    doc._text = "Some text.\nNext line\n"
    doc.tokenizeText()
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Some text.</w:t><w:br /><w:t>Next line</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Tab
    xTest = ET.Element(_wTag("body"))
    doc._text = "\tItem 1\tItem 2\n"
    doc.tokenizeText()
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr>'
        '<w:r><w:rPr /><w:tab /><w:t>Item 1</w:t><w:tab /><w:t>Item 2</w:t></w:r>'
        '</w:p></w:body>'
    )

    # Tab in Format
    xTest = ET.Element(_wTag("body"))
    doc._text = "Some **bold\ttext**"
    doc.tokenizeText()
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr>'
        '<w:r><w:rPr /><w:t xml:space="preserve">Some </w:t></w:r>'
        '<w:r><w:rPr><w:b /></w:rPr><w:t>bold</w:t><w:tab /><w:t>text</w:t></w:r>'
        '</w:p></w:body>'
    )


@pytest.mark.core
def testFmtToDocX_Footnotes(mockGUI):
    """Test formatting of footnotes."""
    project = NWProject()
    doc = ToDocX(project)
    doc.initDocument()

    # Text
    xTest = ET.Element(_wTag("body"))
    doc._text = (
        "Text with one[footnote:fa], **two**[footnote:fd], "
        "or three[footnote:fb] footnotes.[footnote:fe]\n\n"
        "%footnote.fa: Footnote text A.[footnote:fc]\n\n"
        "%footnote.fc: This footnote is skipped.\n\n"
        "%footnote.fd: Another footnote.\n\n"
        "%footnote.fe: Again?\n\n"
    )
    doc.tokenizeText()
    doc.doConvert()
    doc._pars[-1].toXml(xTest)
    assert xmlToText(xTest) == (
        f'<w:body><w:p><w:pPr><w:pStyle w:val="{S_NORM}" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Text with one</w:t></w:r>'
        '<w:r><w:rPr><w:vertAlign w:val="superscript" /></w:rPr>'
        '<w:footnoteReference w:id="1" /></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve">, </w:t></w:r>'
        '<w:r><w:rPr><w:b /></w:rPr><w:t>two</w:t></w:r>'
        '<w:r><w:rPr><w:vertAlign w:val="superscript" /></w:rPr>'
        '<w:footnoteReference w:id="2" /></w:r>'
        '<w:r><w:rPr /><w:t>, or three</w:t></w:r>'
        '<w:r><w:rPr /><w:t xml:space="preserve"> footnotes.</w:t></w:r>'
        '<w:r><w:rPr><w:vertAlign w:val="superscript" /></w:rPr>'
        '<w:footnoteReference w:id="3" /></w:r>'
        '</w:p></w:body>'
    )

    # Footnotes
    doc._footnotesXml()
    assert xmlToText(doc._files["footnotes.xml"].xml) == (
        '<w:footnotes>'
        f'<w:footnote w:id="1"><w:p><w:pPr><w:pStyle w:val="{S_FNOTE}" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Footnote text A.</w:t></w:r></w:p></w:footnote>'
        f'<w:footnote w:id="2"><w:p><w:pPr><w:pStyle w:val="{S_FNOTE}" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Another footnote.</w:t></w:r></w:p></w:footnote>'
        f'<w:footnote w:id="3"><w:p><w:pPr><w:pStyle w:val="{S_FNOTE}" /></w:pPr>'
        '<w:r><w:rPr /><w:t>Again?</w:t></w:r></w:p></w:footnote>'
        '</w:footnotes>'
    )


@pytest.mark.core
def testFmtToDocX_SaveDocument(mockGUI, prjLipsum, fncPath, tstPaths):
    """Test document output."""
    project = NWProject()
    project.openProject(prjLipsum)

    pageHeader = f"Page {nwHeadFmt.DOC_PAGE} - {nwHeadFmt.DOC_PROJECT} ({nwHeadFmt.DOC_AUTHOR})"

    build = BuildSettings()
    build.setValue("filter.includeNovel", True)
    build.setValue("filter.includeNotes", True)
    build.setValue("filter.includeInactive", False)
    build.setValue("text.includeSynopsis", True)
    build.setValue("text.includeComments", True)
    build.setValue("text.includeKeywords", True)
    build.setValue("format.textFont", "Source Sans Pro,12")
    build.setValue("format.firstLineIndent", True)
    build.setValue("doc.pageHeader", pageHeader)

    docBuild = NWBuildDocument(project, build)
    docBuild.queueAll()

    docPath = fncPath / "document.docx"
    assert list(docBuild.iterBuildDocument(docPath, nwBuildFmt.DOCX)) == [
        (0, True), (1, True), (2, True), (3, True), (4, True), (5, False),
        (6, True), (7, True), (8, True), (9, False), (10, False), (11, True),
        (12, True), (13, True), (14, True), (15, True), (16, True), (17, True),
        (18, True), (19, True), (20, True),
    ]

    assert docPath.exists()
    assert zipfile.is_zipfile(docPath)

    with zipfile.ZipFile(docPath, mode="r") as zipObj:
        zipObj.extractall(fncPath / "extract")

    def prettifyXml(inFile, outFile):
        with open(outFile, mode="wb") as fStream:
            xml = ET.parse(inFile)
            xmlIndent(xml)
            xml.write(fStream, encoding="utf-8", xml_declaration=True)

    expected = [
        fncPath / "extract" / "[Content_Types].xml",
        fncPath / "extract" / "_rels" / ".rels",
        fncPath / "extract" / "docProps" / "app.xml",
        fncPath / "extract" / "docProps" / "core.xml",
        fncPath / "extract" / "word" / "_rels" / "document.xml.rels",
        fncPath / "extract" / "word" / "document.xml",
        fncPath / "extract" / "word" / "footnotes.xml",
        fncPath / "extract" / "word" / "header1.xml",
        fncPath / "extract" / "word" / "header2.xml",
        fncPath / "extract" / "word" / "settings.xml",
        fncPath / "extract" / "word" / "styles.xml",
    ]

    outDir = tstPaths.outDir / "fmtToDocX_SaveDocument"
    outDir.mkdir()
    for file in expected:
        assert file.is_file()
        name = file.name.replace("[", "").replace("]", "").lstrip(".")
        outFile = outDir / name
        refFile = tstPaths.refDir / f"fmtToDocX_SaveDocument_{name}"
        prettifyXml(file, outFile)
        assert cmpFiles(outFile, refFile, ignoreStart=DOCX_IGNORE)


@pytest.mark.core
def testFmtToDocX_MkTag():
    """Test the tag maker function."""
    assert _mkTag("r", "id") == f"{{{OOXML_SCM}/officeDocument/2006/relationships}}id"
    assert _mkTag("w", "t") == f"{{{OOXML_SCM}/wordprocessingml/2006/main}}t"
    assert _mkTag("q", "t") == "t"
