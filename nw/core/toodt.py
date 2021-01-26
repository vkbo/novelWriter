# -*- coding: utf-8 -*-
"""
novelWriter – ODT Text Converter
================================
Extends the Tokenizer class to generate ODT and FODT files

File History:
Created: 2021-01-26 [1.1rc1]

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
import logging
import os

from lxml import etree

from nw.core.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

XML_NS = {
    "office" : "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "style"  : "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "text"   : "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "fo"     : "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "loext"  : "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0",
}

class ToOdt(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)

        self.mainConf = nw.CONFIG

        self._xRoot = None
        self._xStyl = None
        self._xText = None

        self._dLanguage = "en"
        self._dCountry  = "GB"
        self._dFontFace = "Liberation Serif"
        self._dFontSize = 12

        return

    ##
    #  Setters
    ##

    def setLanguage(self, theLang):
        """Set language for the document.
        """
        if theLang is None:
            return False

        langBits = theLang.split("_")
        self._dLanguage = langBits[0]
        if len(langBits) > 1:
            self._dCountry = langBits[1]

        return True

    def setFont(self, fontFace, fontSize):
        """Set font and font size.
        """
        self._dFontFace = fontFace
        self._dFontSize = fontSize
        return

    ##
    #  Class Methods
    ##

    def initDocument(self):
        """Initialises a new open document XML tree.
        """
        rAttr = {
            _mkTag("office", "version")  : "1.3",
            _mkTag("office", "mimetype") : "application/vnd.oasis.opendocument.text",
        }
        self._xRoot = etree.Element(_mkTag("office", "document"), attrib=rAttr, nsmap=XML_NS)
        self._xStyl = etree.SubElement(self._xRoot, _mkTag("office", "styles"))
        self._xText = etree.SubElement(self._xRoot, _mkTag("office", "text"))

        # Add Styles
        self._styleParagraph()
        self._styleHeaders()

        return

    def doConvert(self):
        """Convert the list of text tokens into a HTML document saved
        to theResult.
        """
        self.theResult = ""

        for tType, tLine, tText, tFormat, tStyle in self.theTokens:

            # Process Text Type
            if tType == self.T_EMPTY:
                continue

            elif tType == self.T_TITLE:
                continue

        return

    def closeDocument(self):
        """Return the serialised XML document
        """
        self.theResult = etree.tostring(
            self._xRoot,
            pretty_print = True,
            encoding = "utf-8",
            xml_declaration = True
        )

        cacheFile = os.path.join(os.path.expanduser("~"), "Temp", "odtGen.fodt")
        with open(cacheFile, mode="wb") as outFile:
            outFile.write(self.theResult)

        return

    ##
    #  Style Elements
    ##

    def _styleParagraph(self):
        """Set the paragraph styles.
        """
        # Add Default Paragraph Style
        # ===========================

        theAttr = {}
        theAttr[_mkTag("style", "family")] = "paragraph"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "default-style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("style", "line-break")]        = "strict"
        theAttr[_mkTag("style", "tab-stop-distance")] = "1.251cm"
        theAttr[_mkTag("style", "writing-mode")]      = "page"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("style", "font-name")] = self._dFontFace
        theAttr[_mkTag("fo",    "font-size")] = "%dpt" % self._dFontSize
        theAttr[_mkTag("fo",    "language")]  = self._dLanguage
        theAttr[_mkTag("fo",    "country")]   = self._dCountry
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        # Add Paragraph Style
        # ===================

        theAttr = {}
        theAttr[_mkTag("style", "name")]   = "Standard"
        theAttr[_mkTag("style", "family")] = "paragraph"
        theAttr[_mkTag("style", "class")]  = "text"
        etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

        # Add Text Body Style
        # ===================

        theAttr = {}
        theAttr[_mkTag("style", "name")]              = "Text_body"
        theAttr[_mkTag("style", "display-name")]      = "Text Body"
        theAttr[_mkTag("style", "family")]            = "paragraph"
        theAttr[_mkTag("style", "parent-style-name")] = "Standard"
        theAttr[_mkTag("style", "class")]             = "text"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo",    "margin-top")]         = "0cm"
        theAttr[_mkTag("fo",    "margin-bottom")]      = "0.247cm"
        theAttr[_mkTag("style", "contextual-spacing")] = "false"
        theAttr[_mkTag("fo",    "line-height")]        = "115%"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        return

    def _styleHeaders(self):
        """Set the header styles.
        """
        # Add Default Heading Style
        # =========================

        theAttr = {}
        theAttr[_mkTag("style", "name")]              = "Heading"
        theAttr[_mkTag("style", "family")]            = "paragraph"
        theAttr[_mkTag("style", "parent-style-name")] = "Standard"
        theAttr[_mkTag("style", "next-style-name")]   = "Text_body"
        theAttr[_mkTag("style", "class")]             = "text"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo",    "margin-top")]         = "0.423cm"
        theAttr[_mkTag("fo",    "margin-bottom")]      = "0.212cm"
        theAttr[_mkTag("style", "contextual-spacing")] = "false"
        theAttr[_mkTag("fo",    "keep-with-next")]     = "always"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("style", "font-name")]   = self._dFontFace
        theAttr[_mkTag("fo",    "font-family")] = "'%s'" % self._dFontFace
        theAttr[_mkTag("style", "font-pitch")]  = "variable"
        theAttr[_mkTag("fo",    "font-size")]   = "14pt"
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        # Add Title Style
        # ===============

        theAttr = {}
        theAttr[_mkTag("style", "name")]              = "Title"
        theAttr[_mkTag("style", "family")]            = "paragraph"
        theAttr[_mkTag("style", "parent-style-name")] = "Heading"
        theAttr[_mkTag("style", "next-style-name")]   = "Text_body"
        theAttr[_mkTag("style", "class")]             = "chapter"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo", "text-align")] = "center"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo", "font-size")]   = "28pt"
        theAttr[_mkTag("fo", "font-weight")] = "bold"
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        # Add Heading 1 Style
        # ===================

        theAttr = {}
        theAttr[_mkTag("style", "name")]                  = "Heading_1"
        theAttr[_mkTag("style", "display-name")]          = "Heading 1"
        theAttr[_mkTag("style", "family")]                = "paragraph"
        theAttr[_mkTag("style", "parent-style-name")]     = "Heading"
        theAttr[_mkTag("style", "next-style-name")]       = "Text_body"
        theAttr[_mkTag("style", "default-outline-level")] = "1"
        theAttr[_mkTag("style", "class")]                 = "text"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo",    "margin-top")]         = "0.423cm"
        theAttr[_mkTag("fo",    "margin-bottom")]      = "0.212cm"
        theAttr[_mkTag("style", "contextual-spacing")] = "false"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo", "font-size")]   = "130%"
        theAttr[_mkTag("fo", "font-weight")] = "bold"
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        # Add Heading 2 Style
        # ===================

        theAttr = {}
        theAttr[_mkTag("style", "name")]                  = "Heading_2"
        theAttr[_mkTag("style", "display-name")]          = "Heading 2"
        theAttr[_mkTag("style", "family")]                = "paragraph"
        theAttr[_mkTag("style", "parent-style-name")]     = "Heading"
        theAttr[_mkTag("style", "next-style-name")]       = "Text_body"
        theAttr[_mkTag("style", "default-outline-level")] = "2"
        theAttr[_mkTag("style", "class")]                 = "text"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo",    "margin-top")]         = "0.353cm"
        theAttr[_mkTag("fo",    "margin-bottom")]      = "0.212cm"
        theAttr[_mkTag("style", "contextual-spacing")] = "false"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo", "font-size")]   = "120%"
        theAttr[_mkTag("fo", "font-weight")] = "bold"
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        # Add Heading 3 Style
        # ===================

        theAttr = {}
        theAttr[_mkTag("style", "name")]                  = "Heading_3"
        theAttr[_mkTag("style", "display-name")]          = "Heading 3"
        theAttr[_mkTag("style", "family")]                = "paragraph"
        theAttr[_mkTag("style", "parent-style-name")]     = "Heading"
        theAttr[_mkTag("style", "next-style-name")]       = "Text_body"
        theAttr[_mkTag("style", "default-outline-level")] = "3"
        theAttr[_mkTag("style", "class")]                 = "text"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo",    "margin-top")]         = "0.247cm"
        theAttr[_mkTag("fo",    "margin-bottom")]      = "0.212cm"
        theAttr[_mkTag("style", "contextual-spacing")] = "false"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo", "font-size")]   = "110%"
        theAttr[_mkTag("fo", "font-weight")] = "bold"
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        # Add Heading 4 Style
        # ===================

        theAttr = {}
        theAttr[_mkTag("style", "name")]                  = "Heading_4"
        theAttr[_mkTag("style", "display-name")]          = "Heading 4"
        theAttr[_mkTag("style", "family")]                = "paragraph"
        theAttr[_mkTag("style", "parent-style-name")]     = "Heading"
        theAttr[_mkTag("style", "next-style-name")]       = "Text_body"
        theAttr[_mkTag("style", "default-outline-level")] = "4"
        theAttr[_mkTag("style", "class")]                 = "text"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo",    "margin-top")]         = "0.247cm"
        theAttr[_mkTag("fo",    "margin-bottom")]      = "0.212cm"
        theAttr[_mkTag("style", "contextual-spacing")] = "false"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo", "font-size")]   = "100%"
        theAttr[_mkTag("fo", "font-weight")] = "bold"
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        return

# END Class ToOdt

# =========================================================================== #
#  Local Functions
# =========================================================================== #

def _mkTag(nsName, tagName):
    """Assemble namespace and tag name.
    """
    theNS = XML_NS.get(nsName, "")
    if theNS:
        return "{%s}%s" % (theNS, tagName)
    logger.warning("Missing xml namespace '%s'" % nsName)
    return tagName
