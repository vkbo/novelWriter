# -*- coding: utf-8 -*-
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

import nw
import pytest

from lxml import etree

from nw.core import NWProject, NWIndex, ToOdt

XML_NS = [
    ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"',
    ' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"',
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
def testCoreToOdt_Convert(tmpConf, dummyGUI):
    """Test the converter of the ToHtml class.
    """
    nw.CONFIG = tmpConf

    theProject = NWProject(dummyGUI)
    dummyGUI.theIndex = NWIndex(theProject, dummyGUI)
    theDoc = ToOdt(theProject, dummyGUI)

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

# END Test testCoreToOdt_Convert
