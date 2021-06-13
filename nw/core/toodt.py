# -*- coding: utf-8 -*-
"""
novelWriter – ODT Text Converter
================================
Extends the Tokenizer class to generate ODT and FODT files

File History:
Created: 2021-01-26 [1.2a0]

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

from lxml import etree
from hashlib import sha256
from zipfile import ZipFile
from datetime import datetime

from nw.constants import nwKeyWords, nwLabels
from nw.core.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

# Main XML NameSpaces
XML_NS = {
    "office" : "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "style"  : "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "loext"  : "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0",
    "text"   : "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "meta"   : "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    "fo"     : "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
}

# Mimetype and Version
X_MIME = "application/vnd.oasis.opendocument.text"
X_VERS = "1.2"

# Text Formatting Tags
TAG_BR   = "{%s}line-break" % XML_NS["text"]
TAG_TAB  = "{%s}tab" % XML_NS["text"]
TAG_SPAN = "{%s}span" % XML_NS["text"]
TAG_STNM = "{%s}style-name" % XML_NS["text"]

class ToOdt(Tokenizer):

    X_BLD = 0x01 # Bold format
    X_ITA = 0x02 # Italic format
    X_DEL = 0x04 # Strikethrough format
    X_BRK = 0x08 # Line break
    X_TAB = 0x10 # Tab

    def __init__(self, theProject, isFlat):
        Tokenizer.__init__(self, theProject)

        self.mainConf = nw.CONFIG

        self._isFlat = isFlat # Flat: .fodt, otherwise .odt

        self._dFlat = None # FODT file XML root
        self._dCont = None # ODT content.xml root
        self._dMeta = None # ODT meta.xml root
        self._dStyl = None # ODT styles.xml root

        self._xMeta = None # Office meta root
        self._xStyl = None # Office styles root
        self._xAuto = None # Office auto-styles root
        self._xMast = None # Office master-styles root
        self._xBody = None # Office body root
        self._xText = None # Office text root

        self._xAut2 = None # Page layout auto-styles for ODT file

        self._mainPara = {} # User-accessible paragraph styles
        self._autoPara = {} # Auto-generated paragraph styles
        self._autoText = {} # Auto-generated text styles

        # Properties
        self.textFont   = "Liberation Serif"
        self.textSize   = 12
        self.textFixed  = False
        self.colourHead = False
        self.addHeader  = True
        self.headerText = ""

        # Internal
        self._fontFamily  = "&apos;Liberation Sans&apos;"
        self._fontPitch   = "variable"
        self._fSizeTitle  = "30pt"
        self._fSizeHead1  = "24pt"
        self._fSizeHead2  = "20pt"
        self._fSizeHead3  = "16pt"
        self._fSizeHead4  = "14pt"
        self._fSizeHead   = "14pt"
        self._fSizeText   = "12pt"
        self._lineHeight  = "115%"
        self._blockIndent = "1.693cm"
        self._textAlign   = "left"
        self._dLanguage   = "en"
        self._dCountry    = "GB"

        ## Text Margings in Units of em
        self._mTopTitle = "0.423cm"
        self._mTopHead1 = "0.423cm"
        self._mTopHead2 = "0.353cm"
        self._mTopHead3 = "0.247cm"
        self._mTopHead4 = "0.247cm"
        self._mTopHead  = "0.423cm"
        self._mTopText  = "0.000cm"
        self._mTopMeta  = "0.000cm"

        self._mBotTitle = "0.212cm"
        self._mBotHead1 = "0.212cm"
        self._mBotHead2 = "0.212cm"
        self._mBotHead3 = "0.212cm"
        self._mBotHead4 = "0.212cm"
        self._mBotHead  = "0.212cm"
        self._mBotText  = "0.247cm"
        self._mBotMeta  = "0.106cm"

        ## Document Margins
        self._mDocTop   = "2.000cm"
        self._mDocBtm   = "2.000cm"
        self._mDocLeft  = "2.000cm"
        self._mDocRight = "2.000cm"

        ## Colour
        self._colHead12 = None
        self._opaHead12 = None
        self._colHead34 = None
        self._opaHead34 = None
        self._colMetaTx = None
        self._opaMetaTx = None

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

    def setColourHeaders(self, doColour):
        """Enable/disable coloured headings and comments.
        """
        self.colourHead = doColour
        return

    ##
    #  Class Methods
    ##

    def initDocument(self):
        """Initialises a new open document XML tree.
        """
        # Initialise Variables
        # ====================

        self._fontFamily = self.textFont
        if len(self.textFont.split()) > 1:
            self._fontFamily = f"'{self.textFont}'"
        self._fontPitch = "fixed" if self.textFixed else "variable"

        self._fSizeTitle = f"{round(2.50 * self.textSize):d}pt"
        self._fSizeHead1 = f"{round(2.00 * self.textSize):d}pt"
        self._fSizeHead2 = f"{round(1.60 * self.textSize):d}pt"
        self._fSizeHead3 = f"{round(1.30 * self.textSize):d}pt"
        self._fSizeHead4 = f"{round(1.15 * self.textSize):d}pt"
        self._fSizeHead  = f"{round(1.15 * self.textSize):d}pt"
        self._fSizeText  = f"{self.textSize:d}pt"

        mScale = self.lineHeight/1.15

        self._mTopTitle = self._emToCm(mScale * self.marginTitle[0])
        self._mTopHead1 = self._emToCm(mScale * self.marginHead1[0])
        self._mTopHead2 = self._emToCm(mScale * self.marginHead2[0])
        self._mTopHead3 = self._emToCm(mScale * self.marginHead3[0])
        self._mTopHead4 = self._emToCm(mScale * self.marginHead4[0])
        self._mTopHead  = self._emToCm(mScale * self.marginHead4[0])
        self._mTopText  = self._emToCm(mScale * self.marginText[0])
        self._mTopMeta  = self._emToCm(mScale * self.marginMeta[0])

        self._mBotTitle = self._emToCm(mScale * self.marginTitle[1])
        self._mBotHead1 = self._emToCm(mScale * self.marginHead1[1])
        self._mBotHead2 = self._emToCm(mScale * self.marginHead2[1])
        self._mBotHead3 = self._emToCm(mScale * self.marginHead3[1])
        self._mBotHead4 = self._emToCm(mScale * self.marginHead4[1])
        self._mBotHead  = self._emToCm(mScale * self.marginHead4[1])
        self._mBotText  = self._emToCm(mScale * self.marginText[1])
        self._mBotMeta  = self._emToCm(mScale * self.marginMeta[1])

        if self.colourHead:
            self._colHead12 = "#2a6099"
            self._opaHead12 = "100%"
            self._colHead34 = "#444444"
            self._opaHead34 = "100%"
            self._colMetaTx = "#813709"
            self._opaMetaTx = "100%"

        self._lineHeight  = f"{round(100 * self.lineHeight):d}%"
        self._blockIndent = self._emToCm(self.blockIndent)
        self._textAlign   = "justify" if self.doJustify else "left"

        # Document Header
        # ===============

        if self.headerText == "":
            theTitle = self.theProject.bookTitle
            theAuth  = self.theProject.getAuthors()
            self.headerText = f"{theTitle} / {theAuth} /"

        # Create Roots
        # ============

        tAttr = {}
        tAttr[_mkTag("office", "version")] = X_VERS

        fAttr = {}
        fAttr[_mkTag("style", "name")] = self.textFont
        fAttr[_mkTag("style", "font-pitch")] = self._fontPitch

        if self._isFlat:

            # FODT File
            # =========

            tAttr[_mkTag("office", "mimetype")] = X_MIME

            tFlat = _mkTag("office", "document")
            self._dFlat = etree.Element(tFlat, attrib=tAttr, nsmap=XML_NS)

            self._xMeta = etree.SubElement(self._dFlat, _mkTag("office", "meta"))
            self._xFont = etree.SubElement(self._dFlat, _mkTag("office", "font-face-decls"))
            self._xStyl = etree.SubElement(self._dFlat, _mkTag("office", "styles"))
            self._xAuto = etree.SubElement(self._dFlat, _mkTag("office", "automatic-styles"))
            self._xMast = etree.SubElement(self._dFlat, _mkTag("office", "master-styles"))
            self._xBody = etree.SubElement(self._dFlat, _mkTag("office", "body"))

            etree.SubElement(self._xFont, _mkTag("style", "font-face"), attrib=fAttr)

        else:

            # ODT File
            # ========

            tCont = _mkTag("office", "document-content")
            tMeta = _mkTag("office", "document-meta")
            tStyl = _mkTag("office", "document-styles")

            # content.xml
            self._dCont = etree.Element(tCont, attrib=tAttr, nsmap=XML_NS)
            self._xFnt1 = etree.SubElement(self._dCont, _mkTag("office", "font-face-decls"))
            self._xAuto = etree.SubElement(self._dCont, _mkTag("office", "automatic-styles"))
            self._xBody = etree.SubElement(self._dCont, _mkTag("office", "body"))

            # meta.xml
            self._dMeta = etree.Element(tMeta, attrib=tAttr, nsmap=XML_NS)
            self._xMeta = etree.SubElement(self._dMeta, _mkTag("office", "meta"))

            # styles.xml
            self._dStyl = etree.Element(tStyl, attrib=tAttr, nsmap=XML_NS)
            self._xFnt2 = etree.SubElement(self._dStyl, _mkTag("office", "font-face-decls"))
            self._xStyl = etree.SubElement(self._dStyl, _mkTag("office", "styles"))
            self._xAut2 = etree.SubElement(self._dStyl, _mkTag("office", "automatic-styles"))
            self._xMast = etree.SubElement(self._dStyl, _mkTag("office", "master-styles"))

            etree.SubElement(self._xFnt1, _mkTag("style", "font-face"), attrib=fAttr)
            etree.SubElement(self._xFnt2, _mkTag("style", "font-face"), attrib=fAttr)

        # Finalise
        # ========

        self._xText = etree.SubElement(self._xBody, _mkTag("office", "text"))

        # Meta Data
        xMeta = etree.SubElement(self._xMeta, _mkTag("meta", "creation-date"))
        xMeta.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        xMeta = etree.SubElement(self._xMeta, _mkTag("meta", "generator"))
        xMeta.text = f"novelWriter/{nw.__version__}"

        self._pageStyles()
        self._defaultStyles()
        self._useableStyles()
        self._writeHeader()

        return

    def doConvert(self):
        """Convert the list of text tokens into XML elements.
        """
        self.theResult = "" # Not used, but cleared just in case

        odtTags = {
            self.FMT_B_B : "_B", # Bold open format
            self.FMT_B_E : "b_", # Bold close format
            self.FMT_I_B : "I",  # Italic open format
            self.FMT_I_E : "i",  # Italic close format
            self.FMT_D_B : "_S", # Strikethrough open format
            self.FMT_D_E : "s_", # Strikethrough close format
        }

        thisPar = []
        thisFmt = []
        parStyle = None
        for tType, _, tText, tFormat, tStyle in self.theTokens:

            # Styles
            oStyle = ODTParagraphStyle()
            if tStyle is not None:
                if tStyle & self.A_LEFT:
                    oStyle.setTextAlign("left")
                elif tStyle & self.A_RIGHT:
                    oStyle.setTextAlign("right")
                elif tStyle & self.A_CENTRE:
                    oStyle.setTextAlign("center")
                elif tStyle & self.A_JUSTIFY:
                    oStyle.setTextAlign("justify")

                if tStyle & self.A_PBB:
                    oStyle.setBreakBefore("page")
                elif tStyle & self.A_PBB_AUT:
                    oStyle.setBreakBefore("auto")

                if tStyle & self.A_PBA:
                    oStyle.setBreakAfter("page")
                elif tStyle & self.A_PBA_AUT:
                    oStyle.setBreakAfter("auto")

                if tStyle & self.A_Z_BTMMRG:
                    oStyle.setMarginBottom("0.000cm")
                if tStyle & self.A_Z_TOPMRG:
                    oStyle.setMarginTop("0.000cm")

                if tStyle & self.A_IND_L:
                    oStyle.setMarginLeft(self._blockIndent)
                if tStyle & self.A_IND_R:
                    oStyle.setMarginRight(self._blockIndent)

            # Process Text Types
            if tType == self.T_EMPTY:
                if len(thisPar) > 1 and parStyle is not None:
                    if self.doJustify:
                        parStyle.setTextAlign("left")

                if len(thisPar) > 0:
                    tTemp = "\n".join(thisPar)
                    fTemp = " ".join(thisFmt)
                    tTxt = tTemp.rstrip()
                    tFmt = fTemp[:len(tTxt)]
                    self._addTextPar("Text_Body", parStyle, tTxt, theFmt=tFmt)

                thisPar = []
                thisFmt = []
                parStyle = None

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
                if parStyle is None:
                    parStyle = oStyle

                tFmt = " "*len(tText)
                for xPos, xLen, xFmt in tFormat:
                    tFmt = tFmt[:xPos] + odtTags[xFmt] + tFmt[xPos+xLen:]

                tTxt = tText.rstrip()
                tFmt = tFmt[:len(tTxt)]
                thisPar.append(tTxt)
                thisFmt.append(tFmt)

            elif tType == self.T_SYNOPSIS and self.doSynopsis:
                tTemp, fTemp = self._formatSynopsis(tText)
                self._addTextPar("Text_Meta", oStyle, tTemp, theFmt=fTemp)

            elif tType == self.T_COMMENT and self.doComments:
                tTemp, fTemp = self._formatComments(tText)
                self._addTextPar("Text_Meta", oStyle, tTemp, theFmt=fTemp)

            elif tType == self.T_KEYWORD and self.doKeywords:
                tTemp, fTemp = self._formatKeywords(tText)
                self._addTextPar("Text_Meta", oStyle, tTemp, theFmt=fTemp)

        return

    def closeDocument(self):
        """Return the serialised XML document
        """
        # Build the auto-generated styles
        for styleName, styleObj in self._autoPara.values():
            styleObj.packXML(self._xAuto, styleName)
        for styleName, styleObj in self._autoText.values():
            styleObj.packXML(self._xAuto, styleName)

        return

    def saveFlatXML(self, savePath):
        """Save the data to an .fodt file.
        """
        with open(savePath, mode="wb") as outFile:
            outFile.write(etree.tostring(
                self._dFlat,
                pretty_print = True,
                encoding = "utf-8",
                xml_declaration = True
            ))
        return

    def saveOpenDocText(self, savePath):
        """Save the data to an .odt file.
        """
        mMap = {"manifest" : "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"}
        mMani = "{%s}manifest" % mMap["manifest"]
        mVers = "{%s}version" % mMap["manifest"]
        mPath = "{%s}full-path" % mMap["manifest"]
        mType = "{%s}media-type" % mMap["manifest"]
        mFile = "{%s}file-entry" % mMap["manifest"]

        xMani = etree.Element(mMani, attrib={mVers: X_VERS}, nsmap=mMap)
        etree.SubElement(xMani, mFile, attrib={mPath: "/", mVers: X_VERS, mType: X_MIME})
        etree.SubElement(xMani, mFile, attrib={mPath: "settings.xml", mType: "text/xml"})
        etree.SubElement(xMani, mFile, attrib={mPath: "content.xml", mType: "text/xml"})
        etree.SubElement(xMani, mFile, attrib={mPath: "meta.xml", mType: "text/xml"})
        etree.SubElement(xMani, mFile, attrib={mPath: "styles.xml", mType: "text/xml"})

        sMap = {"office" : "urn:oasis:names:tc:opendocument:xmlns:office:1.0"}
        oRoot = "{%s}document-settings" % sMap["office"]
        oSett = "{%s}settings" % sMap["office"]
        xSett = etree.Element(oRoot, nsmap=sMap)
        etree.SubElement(xSett, oSett)

        with ZipFile(savePath, mode="w") as outFile:
            outFile.writestr("mimetype", X_MIME)
            outFile.writestr("META-INF/manifest.xml", etree.tostring(
                xMani, pretty_print=False, encoding="utf-8", xml_declaration=True
            ))
            outFile.writestr("settings.xml", etree.tostring(
                xSett, pretty_print=False, encoding="utf-8", xml_declaration=True
            ))
            outFile.writestr("content.xml", etree.tostring(
                self._dCont, pretty_print=False, encoding="utf-8", xml_declaration=True
            ))
            outFile.writestr("meta.xml", etree.tostring(
                self._dMeta, pretty_print=False, encoding="utf-8", xml_declaration=True
            ))
            outFile.writestr("styles.xml", etree.tostring(
                self._dStyl, pretty_print=False, encoding="utf-8", xml_declaration=True
            ))

        return

    ##
    #  Internal Functions
    ##

    def _formatSynopsis(self, tText):
        """Apply formatting to synopsis lines.
        """
        sSynop = self._localLookup("Synopsis")
        rTxt = "**%s:** %s" % (sSynop, tText)
        rFmt = "_B%s b_ %s" % (" "*len(sSynop), " "*len(tText))
        return rTxt, rFmt

    def _formatComments(self, tText):
        """Apply formatting to comments.
        """
        sComm = self._localLookup("Comment")
        rTxt = "**%s:** %s" % (sComm, tText)
        rFmt = "_B%s b_ %s" % (" "*len(sComm), " "*len(tText))
        return rTxt, rFmt

    def _formatKeywords(self, tText):
        """Apply formatting to keywords.
        """
        isValid, theBits, _ = self.theParent.theIndex.scanThis("@"+tText)
        if not isValid or not theBits:
            return ""

        rTxt = ""
        rFmt = ""
        if theBits[0] in nwLabels.KEY_NAME:
            tText = nwLabels.KEY_NAME[theBits[0]]
            rTxt += "**%s:** " % tText
            rFmt += "_B%s b_ " % (" "*len(tText))
            if len(theBits) > 1:
                if theBits[0] == nwKeyWords.TAG_KEY:
                    rTxt += "%s" % theBits[1]
                    rFmt += "%s" % (" "*len(theBits[1]))
                else:
                    tTags = ", ".join(theBits[1:])
                    rTxt += tTags
                    rFmt += (" "*len(tTags))

        return rTxt, rFmt

    def _addTextPar(self, styleName, oStyle, theText, theFmt="", isHead=False, oLevel=None):
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

        ##
        #  Process Formatting
        ##

        if len(theText) != len(theFmt):
            # Generate an empty format if there isn't any or it doesn't match
            theFmt = " "*len(theText)

        # XML functions
        xTail = None

        def appendText(tText):
            nonlocal xElem, xTail
            if tText:
                if xTail is None:
                    xElem.text = tText
                else:
                    xTail.tail = tText

        def appendSpan(tText, tFmt):
            nonlocal xElem, xTail
            if tText:
                xTail = etree.SubElement(xElem, TAG_SPAN, attrib={
                    TAG_STNM: self._textStyle(tFmt)
                })
                xTail.text = tText

        # The formatting loop
        tTemp = ""
        xFmt = 0x00
        pFmt = 0x00

        for i, c in enumerate(theText):

            if theFmt[i] == "_":
                continue
            elif theFmt[i] == "B":
                xFmt |= self.X_BLD
            elif theFmt[i] == "b":
                xFmt ^= self.X_BLD
            elif theFmt[i] == "I":
                xFmt |= self.X_ITA
            elif theFmt[i] == "i":
                xFmt ^= self.X_ITA
            elif theFmt[i] == "S":
                xFmt |= self.X_DEL
            elif theFmt[i] == "s":
                xFmt ^= self.X_DEL

            if c == "\n":
                xFmt |= self.X_BRK
                c = ""
            elif c == "\t":
                xFmt |= self.X_TAB
                c = ""

            if theFmt[i] == " ":
                tTemp += c

            if xFmt != pFmt:
                if pFmt == 0x00:
                    appendText(tTemp)
                    tTemp = ""
                else:
                    appendSpan(tTemp, pFmt)
                    tTemp = ""

                if xFmt & self.X_BRK:
                    xTail = etree.SubElement(xElem, TAG_BR)
                    xFmt ^= self.X_BRK

                if xFmt & self.X_TAB:
                    xTail = etree.SubElement(xElem, TAG_TAB)
                    xFmt ^= self.X_TAB

            pFmt = xFmt

        # Save what remains in the buffer
        appendText(tTemp)

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

    def _textStyle(self, styleCode):
        """Return a text style for a given style code.
        """
        if styleCode in self._autoText:
            return self._autoText[styleCode][0]

        newName = "T%d" % (len(self._autoText) + 1)
        newStyle = ODTTextStyle()
        if styleCode & self.X_BLD:
            newStyle.setFontWeight("bold")
        if styleCode & self.X_ITA:
            newStyle.setFontStyle("italic")
        if styleCode & self.X_DEL:
            newStyle.setStrikeStyle("solid")
            newStyle.setStrikeType("single")

        self._autoText[styleCode] = (newName, newStyle)

        return newName

    def _emToCm(self, emVal):
        """Converts an em value to centimetres.
        """
        return f"{emVal*2.54/72*self.textSize:.3f}cm"

    ##
    #  Style Elements
    ##

    def _pageStyles(self):
        """Set the default page style.
        """
        theAttr = {}
        theAttr[_mkTag("style", "name")] = "PM1"
        if self._isFlat:
            xPage = etree.SubElement(self._xAuto, _mkTag("style", "page-layout"), attrib=theAttr)
        else:
            xPage = etree.SubElement(self._xAut2, _mkTag("style", "page-layout"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("fo", "margin-top")]    = self._mDocTop
        theAttr[_mkTag("fo", "margin-bottom")] = self._mDocBtm
        theAttr[_mkTag("fo", "margin-left")]   = self._mDocLeft
        theAttr[_mkTag("fo", "margin-right")]  = self._mDocRight
        etree.SubElement(xPage, _mkTag("style", "page-layout-properties"), attrib=theAttr)

        xHead = etree.SubElement(xPage, _mkTag("style", "header-style"))

        theAttr = {}
        theAttr[_mkTag("fo", "min-height")]    = "0.600cm"
        theAttr[_mkTag("fo", "margin-left")]   = "0.000cm"
        theAttr[_mkTag("fo", "margin-right")]  = "0.000cm"
        theAttr[_mkTag("fo", "margin-bottom")] = "0.500cm"
        etree.SubElement(xHead, _mkTag("style", "header-footer-properties"), attrib=theAttr)

        return

    def _defaultStyles(self):
        """Set the default styles.
        """
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
        theAttr[_mkTag("fo", "margin-top")]     = self._mTopHead
        theAttr[_mkTag("fo", "margin-bottom")]  = self._mBotHead
        theAttr[_mkTag("fo", "keep-with-next")] = "always"
        etree.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib=theAttr)

        theAttr = {}
        theAttr[_mkTag("style", "font-name")]   = self.textFont
        theAttr[_mkTag("fo",    "font-family")] = self._fontFamily
        theAttr[_mkTag("fo",    "font-size")]   = self._fSizeHead
        etree.SubElement(xStyl, _mkTag("style", "text-properties"), attrib=theAttr)

        # Add Header and Footer Styles
        # ============================
        if not self.addHeader:
            return

        theAttr = {}
        theAttr[_mkTag("style", "name")]              = "Header_and_Footer"
        theAttr[_mkTag("style", "display-name")]      = "Header and Footer"
        theAttr[_mkTag("style", "family")]            = "paragraph"
        theAttr[_mkTag("style", "parent-style-name")] = "Standard"
        theAttr[_mkTag("style", "class")]             = "extra"
        etree.SubElement(self._xStyl, _mkTag("style", "style"), attrib=theAttr)

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
        oStyle.setMarginTop(self._mTopText)
        oStyle.setMarginBottom(self._mBotText)
        oStyle.setLineHeight(self._lineHeight)
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeText)
        oStyle.setTextAlign(self._textAlign)
        oStyle.packXML(self._xStyl, "Text_Body")

        self._mainPara["Text_Body"] = oStyle

        # Add Text Meta Style
        # ===================

        oStyle = ODTParagraphStyle()
        oStyle.setDisplayName("Text Meta")
        oStyle.setParentStyleName("Standard")
        oStyle.setClass("text")
        oStyle.setMarginTop(self._mTopMeta)
        oStyle.setMarginBottom(self._mBotMeta)
        oStyle.setLineHeight(self._lineHeight)
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeText)
        oStyle.setColor(self._colMetaTx)
        oStyle.setOpacity(self._opaMetaTx)
        oStyle.packXML(self._xStyl, "Text_Meta")

        self._mainPara["Text_Meta"] = oStyle

        # Add Title Style
        # ===============

        oStyle = ODTParagraphStyle()
        oStyle.setDisplayName("Title")
        oStyle.setParentStyleName("Heading")
        oStyle.setNextStyleName("Text_Body")
        oStyle.setClass("chapter")
        oStyle.setTextAlign("center")
        oStyle.setMarginTop(self._mTopTitle)
        oStyle.setMarginBottom(self._mBotTitle)
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
        oStyle.setMarginTop(self._mTopHead1)
        oStyle.setMarginBottom(self._mBotHead1)
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeHead1)
        oStyle.setColor(self._colHead12)
        oStyle.setOpacity(self._opaHead12)
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
        oStyle.setMarginTop(self._mTopHead2)
        oStyle.setMarginBottom(self._mBotHead2)
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeHead2)
        oStyle.setColor(self._colHead12)
        oStyle.setOpacity(self._opaHead12)
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
        oStyle.setMarginTop(self._mTopHead3)
        oStyle.setMarginBottom(self._mBotHead3)
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeHead3)
        oStyle.setColor(self._colHead34)
        oStyle.setOpacity(self._opaHead34)
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
        oStyle.setMarginTop(self._mTopHead4)
        oStyle.setMarginBottom(self._mBotHead4)
        oStyle.setFontName(self.textFont)
        oStyle.setFontFamily(self._fontFamily)
        oStyle.setFontSize(self._fSizeHead4)
        oStyle.setColor(self._colHead34)
        oStyle.setOpacity(self._opaHead34)
        oStyle.setFontWeight("bold")
        oStyle.packXML(self._xStyl, "Heading_4")

        self._mainPara["Heading_4"] = oStyle

        # Add Header Style
        # ================
        if not self.addHeader:
            return

        oStyle = ODTParagraphStyle()
        oStyle.setDisplayName("Header")
        oStyle.setParentStyleName("Header_and_Footer")
        oStyle.setTextAlign("right")
        oStyle.packXML(self._xStyl, "Header")

        self._mainPara["Header"] = oStyle

        return

    def _writeHeader(self):
        """Write the header elements.
        """
        if not self.addHeader:
            return

        theAttr = {}
        theAttr[_mkTag("style", "name")]             = "Standard"
        theAttr[_mkTag("style", "page-layout-name")] = "PM1"
        xPage = etree.SubElement(self._xMast, _mkTag("style", "master-page"), attrib=theAttr)

        # Standard Page Header
        xHead = etree.SubElement(xPage, _mkTag("style", "header"))
        xPar = etree.SubElement(xHead, _mkTag("text", "p"), attrib={
            _mkTag("text", "style-name"): "Header"
        })
        xPar.text = self.headerText.strip() + " "

        xTail = etree.SubElement(xPar, _mkTag("text", "page-number"), attrib={
            _mkTag("text", "select-page"): "current"
        })
        xTail.text = "2"

        # First Page Header
        xHead = etree.SubElement(xPage, _mkTag("style", "header-first"))
        xPar = etree.SubElement(xHead, _mkTag("text", "p"), attrib={
            _mkTag("text", "style-name"): "Header"
        })

        return

# END Class ToOdt

# =============================================================================================== #
#  Auto-Style Classes
# =============================================================================================== #

class ODTParagraphStyle():
    """Wrapper class for the paragraph style setting used by the
    exporter. Only the used settings are exposed here to keep the class
    minimal and fast.
    """
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
            "margin-left":   ["fo", None],
            "margin-right":  ["fo", None],
            "line-height":   ["fo", None],
            "text-align":    ["fo", None],
            "break-before":  ["fo", None],
            "break-after":   ["fo", None],
        }

        # Text Attributes
        self._tAttr = {
            "font-name":   ["style", None],
            "font-family": ["fo",    None],
            "font-size":   ["fo",    None],
            "font-weight": ["fo",    None],
            "color":       ["fo",    None],
            "opacity":     ["loext", None],
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

    def setMarginLeft(self, theValue):
        self._pAttr["margin-left"][1] = str(theValue)
        return

    def setMarginRight(self, theValue):
        self._pAttr["margin-right"][1] = str(theValue)
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

    def setColor(self, theValue):
        self._tAttr["color"][1] = str(theValue)
        return

    def setOpacity(self, theValue):
        self._tAttr["opacity"][1] = str(theValue)
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
        for aName, (_, aVal) in refStyle._mAttr.items():
            if aVal is not None and aVal != self._mAttr[aName][1]:
                return True
        for aName, (_, aVal) in refStyle._pAttr.items():
            if aVal is not None and aVal != self._pAttr[aName][1]:
                return True
        for aName, (_, aVal) in refStyle._tAttr.items():
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

class ODTTextStyle():
    """Wrapper class for the text style setting used by the exporter.
    Only the used settings are exposed here to keep the class minimal
    and fast.
    """
    VALID_WEIGHT = ["normal", "inherit", "bold"]
    VALID_STYLE  = ["normal", "inherit", "italic"]
    VALID_LSTYLE = ["none", "solid"]
    VALID_LTYPE  = ["none", "single", "double"]

    def __init__(self):

        # Text Attributes
        self._tAttr = {
            "font-weight":             ["fo",    None],
            "font-style":              ["fo",    None],
            "text-line-through-style": ["style", None],
            "text-line-through-type":  ["style", None],
        }

        return

    ##
    #  Setters
    ##

    def setFontWeight(self, theValue):
        if theValue in self.VALID_WEIGHT:
            self._tAttr["font-weight"][1] = str(theValue)
        return

    def setFontStyle(self, theValue):
        if theValue in self.VALID_STYLE:
            self._tAttr["font-style"][1] = str(theValue)
        return

    def setStrikeStyle(self, theValue):
        if theValue in self.VALID_LSTYLE:
            self._tAttr["text-line-through-style"][1] = str(theValue)
        return

    def setStrikeType(self, theValue):
        if theValue in self.VALID_LTYPE:
            self._tAttr["text-line-through-type"][1] = str(theValue)
        return

    ##
    #  Methods
    ##

    def packXML(self, xParent, xName):
        """Pack the content into an xml element.
        """
        theAttr = {}
        theAttr[_mkTag("style", "name")] = xName
        theAttr[_mkTag("style", "family")] = "text"
        xEntry = etree.SubElement(xParent, _mkTag("style", "style"), attrib=theAttr)

        theAttr = {}
        for aName, (aNm, aVal) in self._tAttr.items():
            if aVal is not None:
                theAttr[_mkTag(aNm, aName)] = aVal

        if theAttr:
            etree.SubElement(xEntry, _mkTag("style", "text-properties"), attrib=theAttr)

        return

# END Class ODTTextStyle

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
