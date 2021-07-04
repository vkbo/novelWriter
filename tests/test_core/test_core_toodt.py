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

import pytest

from lxml import etree

from nw.core import NWProject, NWIndex, ToOdt

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
def testCoreToOdt_Convert(mockGUI):
    """Test the converter of the ToHtml class.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)
    theDoc = ToOdt(theProject, isFlat=True)

    # Export Mode
    # ===========

    theDoc.isNovel = True

    # Header 1
    theDoc.theText = "# Title\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_1" text:outline-level="1">Title</text:h>'
        '</office:text>'
    )

    # Header 1
    theDoc.theText = "## Chapter Title\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:h text:style-name="Heading_2" text:outline-level="2">Chapter Title</text:h>'
        '</office:text>'
    )

    # Nested Text
    theDoc.theText = "Some ~~nested **bold** and _italics_ text~~ text.\nNo format\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_Body">Some '
        '<text:span text:style-name="T1">nested </text:span>'
        '<text:span text:style-name="T2">bold</text:span>'
        '<text:span text:style-name="T1"> and </text:span>'
        '<text:span text:style-name="T3">italics</text:span>'
        '<text:span text:style-name="T1"> text</text:span> text.'
        '<text:line-break/>No format</text:p>'
        '</office:text>'
    )

    # Hard Break
    theDoc.theText = "Some text.  \nNext line\n"
    theDoc.tokenizeText()
    theDoc.initDocument()
    theDoc.doConvert()
    theDoc.closeDocument()
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
    assert xmlToText(theDoc._xText) == (
        '<office:text>'
        '<text:p text:style-name="Text_Body"><text:tab/>Item 1<text:tab/>Item 2</text:p>'
        '</office:text>'
    )

# END Test testCoreToOdt_Convert
