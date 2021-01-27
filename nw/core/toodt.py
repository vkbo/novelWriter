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
from hashlib import sha256

from nw.core.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

XML_NS = {
    "office" : "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "style"  : "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "text"   : "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "fo"     : "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
}

X_BR  = "{%s}line-break" % XML_NS["text"]
X_TAB = "{%s}tab" % XML_NS["text"]

class ToOdt(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)

        self.mainConf = nw.CONFIG

        self._xRoot = None
        self._xStyl = None
        self._xBody = None
        self._xText = None
        self._xAuto = None

        self._mainPara = {}
        self._autoPara = {}
        self._autoText = {}

        # Properties
        self.textFont  = "Liberation Serif"
        self.textSize  = 12
        self.textFixed = False

        # Internal
        self._fontFamily = None
        self._fontPitch  = "variable"
        self._fSizeTitle = "30pt"
        self._fSizeHead1 = "24pt"
        self._fSizeHead2 = "20pt"
        self._fSizeHead3 = "16pt"
        self._fSizeHead4 = "14pt"
        self._fSizeHead  = "14pt"
        self._fSizeText  = "12pt"
        self._lineHeight = "115%"
        self._textAlign  = "left"
        self._dLanguage  = "en"
        self._dCountry   = "GB"

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
        self._xFont = etree.SubElement(self._xRoot, _mkTag("office", "font-face-decls"))
        self._xStyl = etree.SubElement(self._xRoot, _mkTag("office", "styles"))
        self._xAuto = etree.SubElement(self._xRoot, _mkTag("office", "automatic-styles"))
        self._xBody = etree.SubElement(self._xRoot, _mkTag("office", "body"))
        self._xText = etree.SubElement(self._xBody, _mkTag("office", "text"))

        # Re-Init Variables
        self._fontFamily = self.textFont
        if len(self.textFont.split()) > 1:
            self._fontFamily = f"&apos;{self.textFont}&apos;"
        self._fontPitch = "fixed" if self.textFixed else "variable"

        self._fSizeTitle = f"{round(2.50 * self.textSize):d}pt"
        self._fSizeHead1 = f"{round(2.00 * self.textSize):d}pt"
        self._fSizeHead2 = f"{round(1.60 * self.textSize):d}pt"
        self._fSizeHead3 = f"{round(1.30 * self.textSize):d}pt"
        self._fSizeHead4 = f"{round(1.15 * self.textSize):d}pt"
        self._fSizeHead  = f"{round(1.15 * self.textSize):d}pt"
        self._fSizeText  = f"{self.textSize:d}pt"

        self._lineHeight = f"{round(100 * self.lineHeight):d}%"
        self._textAlign  = "justify" if self.doJustify else "left"

        # Add Styles
        self._defaultStyles()
        self._useableStyles()

        return

    def doConvert(self):
        """Convert the list of text tokens into a HTML document saved
        to theResult.
        """
        self.theResult = ""

        thisPar = []
        parStyle = None
        hasHardBreak = False
        for tType, tLine, tText, tFormat, tStyle in self.theTokens:

            # Styles
            oStyle = ODTParagraphStyle()
            if tStyle is not None:
                if tStyle & self.A_LEFT:
                    oStyle.setTextAlign("left")
                if tStyle & self.A_RIGHT:
                    oStyle.setTextAlign("right")
                if tStyle & self.A_CENTRE:
                    oStyle.setTextAlign("center")
                if tStyle & self.A_JUSTIFY:
                    oStyle.setTextAlign("justify")
                if tStyle & self.A_PBB:
                    oStyle.setBreakBefore("page")
                if tStyle & self.A_PBA:
                    oStyle.setBreakAfter("page")

            # Process Text Type
            if tType == self.T_EMPTY:
                if hasHardBreak and parStyle is not None:
                    if self.doJustify:
                        parStyle.setTextAlign("left")
                if len(thisPar) > 0:
                    tTemp = "".join(thisPar)
                    self._addTextPar("Text_Body", parStyle, tTemp.rstrip())
                thisPar = []
                parStyle = None
                hasHardBreak = False

            elif tType == self.T_TITLE:
                tHead = tText.replace(r"\\", "\n")
                self._addTextPar("Title", oStyle, tHead, isHead=True)

            elif tType == self.T_HEAD1:
                tHead = tText.replace(r"\\", "\n")
                self._addTextPar("Heading_1", oStyle, tHead, isHead=True, oLevel="1")

            elif tType == self.T_HEAD2:
                tHead = tText.replace(r"\\", "\n")
                self._addTextPar("Heading_2", oStyle, tHead, isHead=True, oLevel="2")

            elif tType == self.T_HEAD3:
                tHead = tText.replace(r"\\", "\n")
                self._addTextPar("Heading_3", oStyle, tHead, isHead=True, oLevel="3")

            elif tType == self.T_HEAD4:
                tHead = tText.replace(r"\\", "\n")
                self._addTextPar("Heading_4", oStyle, tHead, isHead=True, oLevel="4")

            elif tType == self.T_SEP:
                self._addTextPar("Text_Body", oStyle, tText)

            elif tType == self.T_SKIP:
                self._addTextPar("Text_Body", oStyle, "")

            elif tType == self.T_TEXT:
                tTemp = tText
                if parStyle is None:
                    parStyle = oStyle
                # for xPos, xLen, xFmt in reversed(tFormat):
                #     tTemp = tTemp[:xPos]+htmlTags[xFmt]+tTemp[xPos+xLen:]
                if tText.endswith("  "):
                    thisPar.append(tTemp.rstrip()+"\n")
                    hasHardBreak = True
                else:
                    thisPar.append(tTemp.rstrip()+" ")

        return

    def closeDocument(self):
        """Return the serialised XML document
        """
        for styleName, styleObj in self._autoPara.values():
            styleObj.packXML(self._xAuto, styleName)

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
    #  Internal Functions
    ##

    def _addTextPar(self, styleName, oStyle, theText, isHead=False, oLevel=None):
        """Add a text paragraph to the text XML element.
        """
        tAttr = {}
        tAttr[_mkTag("text", "style-name")] = self._paraStyle(styleName, oStyle)
        if oLevel is not None:
            tAttr[_mkTag("text", "outline-level")] = oLevel

        pTag = "h" if isHead else "p"
        xElem = etree.SubElement(self._xText, _mkTag("text", pTag), attrib=tAttr)

        if not theText:
            return

        if "\t" not in theText and "\n" not in theText:
            xElem.text = theText
            return

        # Process tabs and line breaks
        tTemp = ""
        xTail = None
        for c in theText:
            if c == "\t":
                if xTail is None:
                    xElem.text = tTemp
                else:
                    xTail.tail = tTemp
                tTemp = ""
                xTail = etree.SubElement(xElem, X_TAB)
            elif c == "\n":
                if xTail is None:
                    xElem.text = tTemp
                else:
                    xTail.tail = tTemp
                tTemp = ""
                xTail = etree.SubElement(xElem, X_BR)
            else:
                tTemp += c

        if tTemp != "":
            if xTail is None:
                xElem.text = tTemp
            else:
                xTail.tail = tTemp

        return

    def _paraStyle(self, parName, oStyle):
        """Return a name for a style object.
        """
        refStyle = self._mainPara.get(parName, None)
        if refStyle is None:
            logger.error("Unknown paragraph style '%s'" % parName)
            return "Standard"

        if not refStyle.checkNew(oStyle):
            return parName

        oStyle.setParentStyleName(parName)
        theID = oStyle.getID()
        if theID in self._autoPara:
            return self._autoPara[theID][0]

        newName = "P%d" % (len(self._autoPara) + 1)
        self._autoPara[theID] = (newName, oStyle)

        return newName

    ##
    #  Style Elements
    ##

    def _defaultStyles(self):
        """Set the default styles.
        """
        # Add Font
        # ========

        theAttr = {}
        theAttr[_mkTag("style", "name")] = self.textFont
        theAttr[_mkTag("style", "font-pitch")] = self._fontPitch
        xStyl = etree.SubElement(self._xFont, _mkTag("style", "font-face"), attrib=theAttr)

        # Add Paragraph Family Style
        # ==========================

        theAttr = {}
        theAttr[_mkTag("style", "family")] = "paragraph"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "default-style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("style", "line-break")]        = "strict"
        theAttr[_mkTag("style", "tab-stop-distance")] = "1.251cm"
        theAttr[_mkTag("style", "writing-mode")]      = "page"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("style", "font-name")]   = self.textFont
        theAttr[_mkTag("fo",    "font-family")] = self._fontFamily
        theAttr[_mkTag("fo",    "font-size")]   = self._fSizeText
        theAttr[_mkTag("fo",    "language")]    = self._dLanguage
        theAttr[_mkTag("fo",    "country")]     = self._dCountry
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        # Add Standard Paragraph Style
        # ============================

        theAttr = {}
        theAttr[_mkTag("style", "name")]   = "Standard"
        theAttr[_mkTag("style", "family")] = "paragraph"
        theAttr[_mkTag("style", "class")]  = "text"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("style", "font-name")]   = self.textFont
        theAttr[_mkTag("fo",    "font-family")] = self._fontFamily
        theAttr[_mkTag("fo",    "font-size")]   = self._fSizeText
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        # Add Default Heading Style
        # =========================

        theAttr = {}
        theAttr[_mkTag("style", "name")]              = "Heading"
        theAttr[_mkTag("style", "family")]            = "paragraph"
        theAttr[_mkTag("style", "parent-style-name")] = "Standard"
        theAttr[_mkTag("style", "next-style-name")]   = "Text_Body"
        theAttr[_mkTag("style", "class")]             = "text"
        xStyl = etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo", "margin-top")]     = "0.423cm"
        theAttr[_mkTag("fo", "margin-bottom")]  = "0.212cm"
        theAttr[_mkTag("fo", "keep-with-next")] = "always"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("style", "font-name")]   = self.textFont
        theAttr[_mkTag("fo",    "font-family")] = self._fontFamily
        theAttr[_mkTag("fo",    "font-size")]   = self._fSizeHead
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        return

    def _useableStyles(self):
        """Set the usable styles.
        """
        # Add Text Body Style
        # ===================

        oStyle = ODTParagraphStyle()
        oStyle.setDisplayName("Text Body")
        oStyle.setParentStyleName("Standard")
        oStyle.setClass("text")
        oStyle.setMarginTop("0cm")
        oStyle.setMarginBottom("0.247cm")
        oStyle.setLineHeight(self._lineHeight)
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeText)
        oStyle.setTextAlign(self._textAlign)
        oStyle.packXML(self._xStyl, "Text_Body")

        self._mainPara["Text_Body"] = oStyle

        # Add Title Style
        # ===============

        oStyle = ODTParagraphStyle()
        oStyle.setDisplayName("Title")
        oStyle.setParentStyleName("Heading")
        oStyle.setNextStyleName("Text_Body")
        oStyle.setClass("chapter")
        oStyle.setTextAlign("center")
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeTitle)
        oStyle.setFontWeight("bold")
        oStyle.packXML(self._xStyl, "Title")

        self._mainPara["Title"] = oStyle

        # Add Heading 1 Style
        # ===================

        oStyle = ODTParagraphStyle()
        oStyle.setDisplayName("Heading 1")
        oStyle.setParentStyleName("Heading")
        oStyle.setNextStyleName("Text_Body")
        oStyle.setOutlineLevel("1")
        oStyle.setClass("text")
        oStyle.setMarginTop("0.423cm")
        oStyle.setMarginBottom("0.212cm")
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeHead1)
        oStyle.setFontWeight("bold")
        oStyle.packXML(self._xStyl, "Heading_1")

        self._mainPara["Heading_1"] = oStyle

        # Add Heading 2 Style
        # ===================

        oStyle = ODTParagraphStyle()
        oStyle.setDisplayName("Heading 2")
        oStyle.setParentStyleName("Heading")
        oStyle.setNextStyleName("Text_Body")
        oStyle.setOutlineLevel("2")
        oStyle.setClass("text")
        oStyle.setMarginTop("0.353cm")
        oStyle.setMarginBottom("0.212cm")
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeHead2)
        oStyle.setFontWeight("bold")
        oStyle.packXML(self._xStyl, "Heading_2")

        self._mainPara["Heading_2"] = oStyle

        # Add Heading 3 Style
        # ===================

        oStyle = ODTParagraphStyle()
        oStyle.setDisplayName("Heading 3")
        oStyle.setParentStyleName("Heading")
        oStyle.setNextStyleName("Text_Body")
        oStyle.setOutlineLevel("3")
        oStyle.setClass("text")
        oStyle.setMarginTop("0.247cm")
        oStyle.setMarginBottom("0.212cm")
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeHead3)
        oStyle.setFontWeight("bold")
        oStyle.packXML(self._xStyl, "Heading_3")

        self._mainPara["Heading_3"] = oStyle

        # Add Heading 4 Style
        # ===================

        oStyle = ODTParagraphStyle()
        oStyle.setDisplayName("Heading 4")
        oStyle.setParentStyleName("Heading")
        oStyle.setNextStyleName("Text_Body")
        oStyle.setOutlineLevel("4")
        oStyle.setClass("text")
        oStyle.setMarginTop("0.247cm")
        oStyle.setMarginBottom("0.212cm")
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeHead4)
        oStyle.setFontWeight("bold")
        oStyle.packXML(self._xStyl, "Heading_4")

        self._mainPara["Heading_4"] = oStyle

        return

# END Class ToOdt

# =============================================================================================== #
#  Auto-Style Classes
# =============================================================================================== #

class ODTParagraphStyle():

    VALID_ALIGN  = ["start", "center", "end", "justify", "inside", "outside", "left", "right"]
    VALID_BREAK  = ["auto", "column", "page", "even-page", "odd-page", "inherit"]
    VALID_LEVEL  = ["1", "2", "3", "4"]
    VALID_CLASS  = ["text", "chapter"]
    VALID_WEIGHT = ["normal", "inherit", "bold"]

    def __init__(self):

        # Attributes
        self._mAttr = {
            "display-name":          ["style", None],
            "parent-style-name":     ["style", None],
            "next-style-name":       ["style", None],
            "default-outline-level": ["style", None],
            "class":                 ["style", None],
        }

        # Paragraph Attributes
        self._pAttr = {
            "margin-top":    ["fo", None],
            "margin-bottom": ["fo", None],
            "line-height":   ["fo", None],
            "text-align":    ["fo", None],
            "break-before":  ["fo", None],
            "break-after":   ["fo", None],
        }

        # text Attributes
        self._tAttr = {
            "font-name":   ["style", None],
            "font-family": ["fo",    None],
            "font-size":   ["fo",    None],
            "font-weight": ["fo",    None],
        }

        return

    ##
    #  Attribute Setters
    ##

    def setDisplayName(self, theValue):
        self._mAttr["display-name"][1] = str(theValue)
        return

    def setParentStyleName(self, theValue):
        self._mAttr["parent-style-name"][1] = str(theValue)
        return

    def setNextStyleName(self, theValue):
        self._mAttr["next-style-name"][1] = str(theValue)
        return

    def setOutlineLevel(self, theValue):
        if theValue in self.VALID_LEVEL:
            self._mAttr["default-outline-level"][1] = str(theValue)
        return

    def setClass(self, theValue):
        if theValue in self.VALID_CLASS:
            self._mAttr["class"][1] = str(theValue)
        return

    ##
    #  Paragraph Setters
    ##

    def setMarginTop(self, theValue):
        self._pAttr["margin-top"][1] = str(theValue)
        return

    def setMarginBottom(self, theValue):
        self._pAttr["margin-bottom"][1] = str(theValue)
        return

    def setLineHeight(self, theValue):
        self._pAttr["line-height"][1] = str(theValue)
        return

    def setTextAlign(self, theValue):
        if theValue in self.VALID_ALIGN:
            self._pAttr["text-align"][1] = str(theValue)
        return

    def setBreakBefore(self, theValue):
        if theValue in self.VALID_BREAK:
            self._pAttr["break-before"][1] = str(theValue)
        return

    def setBreakAfter(self, theValue):
        if theValue in self.VALID_BREAK:
            self._pAttr["break-after"][1] = str(theValue)
        return

    ##
    #  Text Setters
    ##

    def setFontName(self, theValue):
        self._tAttr["font-name"][1] = str(theValue)
        return

    def setFontFamily(self, theValue):
        self._tAttr["font-family"][1] = str(theValue)
        return

    def setFontSize(self, theValue):
        self._tAttr["font-size"][1] = str(theValue)
        return

    def setFontWeight(self, theValue):
        if theValue in self.VALID_WEIGHT:
            self._tAttr["font-weight"][1] = str(theValue)
        return

    ##
    #  Getters
    ##

    def getAttr(self, attrName):
        """Look through the dictionaries for the value, and return it if
        we can find it, If not, return None.
        """
        retVal = self._mAttr.get(attrName, None)
        if retVal is not None:
            return retVal

        retVal = self._pAttr.get(attrName, None)
        if retVal is not None:
            return retVal

        retVal = self._tAttr.get(attrName, None)
        if retVal is not None:
            return retVal

        return None

    ##
    #  Methods
    ##

    def checkNew(self, refStyle):
        """Check if there are new settings in refStyle that differ from
        those in the current object.
        """
        for aName, (aNm, aVal) in refStyle._mAttr.items():
            if aVal is not None and aVal != self._mAttr[aName][1]:
                return True
        for aName, (aNm, aVal) in refStyle._pAttr.items():
            if aVal is not None and aVal != self._pAttr[aName][1]:
                return True
        for aName, (aNm, aVal) in refStyle._tAttr.items():
            if aVal is not None and aVal != self._tAttr[aName][1]:
                return True
        return False

    def getID(self):
        """Generate a unique ID from the settings.
        """
        theString = (
            f"Paragraph:Main:{str(self._mAttr)}:"
            f"Paragraph:Para:{str(self._pAttr)}:"
            f"Paragraph:Text:{str(self._tAttr)}:"
        )
        return sha256(theString.encode()).hexdigest()

    def packXML(self, xParent, xName):
        """Pack the content into an xml element.
        """
        theAttr = {}
        theAttr[_mkTag("style", "name")] = xName
        theAttr[_mkTag("style", "family")] = "paragraph"
        for aName, (aNm, aVal) in self._mAttr.items():
            if aVal is not None:
                theAttr[_mkTag(aNm, aName)] = aVal

        xEntry = etree.SubElement(xParent, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        for aName, (aNm, aVal) in self._pAttr.items():
            if aVal is not None:
                theAttr[_mkTag(aNm, aName)] = aVal

        if theAttr:
            etree.SubElement(xEntry, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        for aName, (aNm, aVal) in self._tAttr.items():
            if aVal is not None:
                theAttr[_mkTag(aNm, aName)] = aVal

        if theAttr:
            etree.SubElement(xEntry, _mkTag("style", "text-properties"), attrib=theAttr)

        return

# END Class ODTParagraphStyle

# =============================================================================================== #
#  Local Functions
# =============================================================================================== #

def _mkTag(nsName, tagName):
    """Assemble namespace and tag name.
    """
    theNS = XML_NS.get(nsName, "")
    if theNS:
        return "{%s}%s" % (theNS, tagName)
    logger.warning("Missing xml namespace '%s'" % nsName)
    return tagName
