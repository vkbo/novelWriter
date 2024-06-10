"""
novelWriter – ODT Text Converter
================================

File History:
Created: 2021-01-26 [1.2b1] ToOdt
Created: 2021-01-27 [1.2b1] ODTParagraphStyle
Created: 2021-01-27 [1.2b1] ODTTextStyle
Created: 2021-08-14 [1.5b1] XMLParagraph

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

import logging
import xml.etree.ElementTree as ET

from collections.abc import Sequence
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

from PyQt5.QtGui import QFont

from novelwriter import __version__
from novelwriter.common import xmlIndent
from novelwriter.constants import nwHeadFmt, nwKeyWords, nwLabels
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import T_Formats, Tokenizer, stripEscape
from novelwriter.types import FONT_STYLE, FONT_WEIGHTS

logger = logging.getLogger(__name__)

# Main XML NameSpaces
XML_NS = {
    "manifest": "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0",
    "office":   "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "style":    "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "loext":    "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0",
    "text":     "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "meta":     "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    "fo":       "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "dc":       "http://purl.org/dc/elements/1.1/",
}
for ns, uri in XML_NS.items():
    ET.register_namespace(ns, uri)


def _mkTag(ns: str, tag: str) -> str:
    """Assemble namespace and tag name."""
    if uri := XML_NS.get(ns, ""):
        return f"{{{uri}}}{tag}"
    logger.warning("Missing xml namespace '%s'", ns)
    return tag


# Mimetype and Version
X_MIME = "application/vnd.oasis.opendocument.text"
X_VERS = "1.3"

# Text Formatting Tags
TAG_BR   = _mkTag("text", "line-break")
TAG_SPC  = _mkTag("text", "s")
TAG_NSPC = _mkTag("text", "c")
TAG_TAB  = _mkTag("text", "tab")
TAG_SPAN = _mkTag("text", "span")
TAG_STNM = _mkTag("text", "style-name")

# Formatting Codes
X_BLD = 0x001  # Bold format
X_ITA = 0x002  # Italic format
X_DEL = 0x004  # Strikethrough format
X_UND = 0x008  # Underline format
X_MRK = 0x010  # Marked format
X_SUP = 0x020  # Superscript
X_SUB = 0x040  # Subscript
X_DLG = 0x080  # Dialogue
X_DLA = 0x100  # Alt. Dialogue

# Formatting Masks
M_BLD = ~X_BLD
M_ITA = ~X_ITA
M_DEL = ~X_DEL
M_UND = ~X_UND
M_MRK = ~X_MRK
M_SUP = ~X_SUP
M_SUB = ~X_SUB
M_DLG = ~X_DLG
M_DLA = ~X_DLA

# ODT Styles
S_TITLE = "Title"
S_HEAD1 = "Heading_20_1"
S_HEAD2 = "Heading_20_2"
S_HEAD3 = "Heading_20_3"
S_HEAD4 = "Heading_20_4"
S_SEP   = "Separator"
S_FIND  = "First_20_line_20_indent"
S_TEXT  = "Text_20_body"
S_META  = "Text_20_Meta"
S_HNF   = "Header_20_and_20_Footer"

# Font Data
FONT_WEIGHT_NUM = ["100", "200", "300", "400", "500", "600", "700", "800", "900"]
FONT_WEIGHT_MAP = {"400": "normal", "700": "bold"}


class ToOdt(Tokenizer):
    """Core: Open Document Writer

    Extend the Tokenizer class to writer Open Document files. The output
    should conform to the 1.3 Extended standard.

    Test with: https://odfvalidator.org/
    """

    def __init__(self, project: NWProject, isFlat: bool) -> None:
        super().__init__(project)

        self._isFlat = isFlat  # Flat: .fodt, otherwise .odt

        self._dFlat = ET.Element("")  # FODT file XML root
        self._dCont = ET.Element("")  # ODT content.xml root
        self._dMeta = ET.Element("")  # ODT meta.xml root
        self._dStyl = ET.Element("")  # ODT styles.xml root

        self._xMeta = ET.Element("")  # Office meta root
        self._xFont = ET.Element("")  # Office font face declaration
        self._xFnt2 = ET.Element("")  # Office font face declaration, secondary
        self._xStyl = ET.Element("")  # Office styles root
        self._xAuto = ET.Element("")  # Office auto-styles root
        self._xAut2 = ET.Element("")  # Office auto-styles root, secondary
        self._xMast = ET.Element("")  # Office master-styles root
        self._xBody = ET.Element("")  # Office body root
        self._xText = ET.Element("")  # Office text root

        self._mainPara: dict[str, ODTParagraphStyle] = {}  # User-accessible paragraph styles
        self._autoPara: dict[str, ODTParagraphStyle] = {}  # Auto-generated paragraph styles
        self._autoText: dict[int, ODTTextStyle] = {}       # Auto-generated text styles

        # Footnotes
        self._nNote = 0
        self._etNotes: dict[str, ET.Element] = {}  # Generated note elements

        self._errData = []  # List of errors encountered

        # Properties
        self._textFont     = QFont("Liberation Serif", 12)
        self._colourHead   = False
        self._headerFormat = ""
        self._pageOffset   = 0

        # Internal
        self._fontFamily   = "Liberation Serif"
        self._fontSize     = 12
        self._fontWeight   = "normal"
        self._fontStyle    = "normal"
        self._fontPitch    = "variable"
        self._fontBold     = "bold"
        self._fSizeTitle   = "30pt"
        self._fSizeHead1   = "24pt"
        self._fSizeHead2   = "20pt"
        self._fSizeHead3   = "16pt"
        self._fSizeHead4   = "14pt"
        self._fSizeHead    = "14pt"
        self._fSizeText    = "12pt"
        self._fSizeFoot    = "10pt"
        self._fLineHeight  = "115%"
        self._fBlockIndent = "1.693cm"
        self._fTextIndent  = "0.499cm"
        self._textAlign    = "left"
        self._dLanguage    = "en"
        self._dCountry     = "GB"

        # Text Margins
        self._mTopTitle = "0.423cm"
        self._mTopHead1 = "0.423cm"
        self._mTopHead2 = "0.353cm"
        self._mTopHead3 = "0.247cm"
        self._mTopHead4 = "0.247cm"
        self._mTopHead  = "0.423cm"
        self._mTopText  = "0.000cm"
        self._mTopMeta  = "0.000cm"
        self._mTopSep   = "0.247cm"

        self._mBotTitle = "0.212cm"
        self._mBotHead1 = "0.212cm"
        self._mBotHead2 = "0.212cm"
        self._mBotHead3 = "0.212cm"
        self._mBotHead4 = "0.212cm"
        self._mBotHead  = "0.212cm"
        self._mBotText  = "0.247cm"
        self._mBotMeta  = "0.106cm"
        self._mBotSep   = "0.247cm"

        self._mBotFoot  = "0.106cm"
        self._mLeftFoot = "0.600cm"

        # Document Size and Margins
        self._mDocWidth  = "21.0cm"
        self._mDocHeight = "29.7cm"
        self._mDocTop    = "2.000cm"
        self._mDocBtm    = "2.000cm"
        self._mDocLeft   = "2.000cm"
        self._mDocRight  = "2.000cm"

        # Colour
        self._colHead12  = None
        self._opaHead12  = None
        self._colHead34  = None
        self._opaHead34  = None
        self._colMetaTx  = None
        self._opaMetaTx  = None
        self._colDialogM = None
        self._colDialogA = None
        self._markText   = "#ffffa6"

        return

    ##
    #  Setters
    ##

    def setLanguage(self, language: str | None) -> None:
        """Set language for the document."""
        if language:
            lang, _, country = language.partition("_")
            self._dLanguage = lang or self._dLanguage
            self._dCountry = country or self._dCountry
        return

    def setColourHeaders(self, state: bool) -> None:
        """Enable/disable coloured headings and comments."""
        self._colourHead = state
        return

    def setPageLayout(
        self, width: int | float, height: int | float,
        top: int | float, bottom: int | float, left: int | float, right: int | float
    ) -> None:
        """Set the document page size and margins in millimetres."""
        self._mDocWidth  = f"{width/10.0:.3f}cm"
        self._mDocHeight = f"{height/10.0:.3f}cm"
        self._mDocTop    = f"{top/10.0:.3f}cm"
        self._mDocBtm    = f"{bottom/10.0:.3f}cm"
        self._mDocLeft   = f"{left/10.0:.3f}cm"
        self._mDocRight  = f"{right/10.0:.3f}cm"
        return

    def setHeaderFormat(self, format: str, offset: int) -> None:
        """Set the document header format."""
        self._headerFormat = format.strip()
        self._pageOffset = offset
        return

    ##
    #  Class Methods
    ##

    def initDocument(self) -> None:
        """Initialises a new open document XML tree."""
        # Initialise Variables
        # ====================

        intWeight = FONT_WEIGHTS.get(self._textFont.weight(), 400)
        fontWeight = str(intWeight)
        fontBold = str(min(intWeight + 300, 900))

        self._fontFamily = self._textFont.family()
        self._fontSize   = self._textFont.pointSize()
        self._fontWeight = FONT_WEIGHT_MAP.get(fontWeight, fontWeight)
        self._fontStyle  = FONT_STYLE.get(self._textFont.style(), "normal")
        self._fontPitch  = "fixed" if self._textFont.fixedPitch() else "variable"
        self._fontBold   = FONT_WEIGHT_MAP.get(fontBold, fontBold)

        self._fSizeTitle = f"{round(2.50 * self._fontSize):d}pt"
        self._fSizeHead1 = f"{round(2.00 * self._fontSize):d}pt"
        self._fSizeHead2 = f"{round(1.60 * self._fontSize):d}pt"
        self._fSizeHead3 = f"{round(1.30 * self._fontSize):d}pt"
        self._fSizeHead4 = f"{round(1.15 * self._fontSize):d}pt"
        self._fSizeHead  = f"{round(1.15 * self._fontSize):d}pt"
        self._fSizeText  = f"{self._fontSize:d}pt"
        self._fSizeFoot  = f"{round(0.8*self._fontSize):d}pt"

        mScale = self._lineHeight/1.15

        self._mTopTitle = self._emToCm(mScale * self._marginTitle[0])
        self._mTopHead1 = self._emToCm(mScale * self._marginHead1[0])
        self._mTopHead2 = self._emToCm(mScale * self._marginHead2[0])
        self._mTopHead3 = self._emToCm(mScale * self._marginHead3[0])
        self._mTopHead4 = self._emToCm(mScale * self._marginHead4[0])
        self._mTopHead  = self._emToCm(mScale * self._marginHead4[0])
        self._mTopText  = self._emToCm(mScale * self._marginText[0])
        self._mTopMeta  = self._emToCm(mScale * self._marginMeta[0])
        self._mTopSep   = self._emToCm(mScale * self._marginSep[0])

        self._mBotTitle = self._emToCm(mScale * self._marginTitle[1])
        self._mBotHead1 = self._emToCm(mScale * self._marginHead1[1])
        self._mBotHead2 = self._emToCm(mScale * self._marginHead2[1])
        self._mBotHead3 = self._emToCm(mScale * self._marginHead3[1])
        self._mBotHead4 = self._emToCm(mScale * self._marginHead4[1])
        self._mBotHead  = self._emToCm(mScale * self._marginHead4[1])
        self._mBotText  = self._emToCm(mScale * self._marginText[1])
        self._mBotMeta  = self._emToCm(mScale * self._marginMeta[1])
        self._mBotSep   = self._emToCm(mScale * self._marginSep[1])

        self._mLeftFoot = self._emToCm(self._marginFoot[0])
        self._mBotFoot  = self._emToCm(self._marginFoot[1])

        if self._colourHead:
            self._colHead12 = "#2a6099"
            self._opaHead12 = "100%"
            self._colHead34 = "#444444"
            self._opaHead34 = "100%"
            self._colMetaTx = "#813709"
            self._opaMetaTx = "100%"

        if self._showDialog:
            self._colDialogM = "#2a6099"
            self._colDialogA = "#813709"

        self._fLineHeight  = f"{round(100 * self._lineHeight):d}%"
        self._fBlockIndent = self._emToCm(self._blockIndent)
        self._fTextIndent  = self._emToCm(self._firstWidth)
        self._textAlign    = "justify" if self._doJustify else "left"

        # Clear Errors
        self._errData = []

        # Create Roots
        # ============

        tAttr = {}
        tAttr[_mkTag("office", "version")] = X_VERS

        fAttr = {}
        fAttr[_mkTag("style", "name")] = self._fontFamily
        fAttr[_mkTag("style", "font-pitch")] = self._fontPitch

        if self._isFlat:

            # FODT File
            # =========

            tAttr[_mkTag("office", "mimetype")] = X_MIME

            tFlat = _mkTag("office", "document")
            self._dFlat = ET.Element(tFlat, attrib=tAttr)

            self._xMeta = ET.SubElement(self._dFlat, _mkTag("office", "meta"))
            self._xFont = ET.SubElement(self._dFlat, _mkTag("office", "font-face-decls"))
            self._xStyl = ET.SubElement(self._dFlat, _mkTag("office", "styles"))
            self._xAuto = ET.SubElement(self._dFlat, _mkTag("office", "automatic-styles"))
            self._xMast = ET.SubElement(self._dFlat, _mkTag("office", "master-styles"))
            self._xBody = ET.SubElement(self._dFlat, _mkTag("office", "body"))

            ET.SubElement(self._xFont, _mkTag("style", "font-face"), attrib=fAttr)

        else:

            # ODT File
            # ========

            tCont = _mkTag("office", "document-content")
            tMeta = _mkTag("office", "document-meta")
            tStyl = _mkTag("office", "document-styles")

            # content.xml
            self._dCont = ET.Element(tCont, attrib=tAttr)
            self._xFont = ET.SubElement(self._dCont, _mkTag("office", "font-face-decls"))
            self._xAuto = ET.SubElement(self._dCont, _mkTag("office", "automatic-styles"))
            self._xBody = ET.SubElement(self._dCont, _mkTag("office", "body"))

            # meta.xml
            self._dMeta = ET.Element(tMeta, attrib=tAttr)
            self._xMeta = ET.SubElement(self._dMeta, _mkTag("office", "meta"))

            # styles.xml
            self._dStyl = ET.Element(tStyl, attrib=tAttr)
            self._xFnt2 = ET.SubElement(self._dStyl, _mkTag("office", "font-face-decls"))
            self._xStyl = ET.SubElement(self._dStyl, _mkTag("office", "styles"))
            self._xAut2 = ET.SubElement(self._dStyl, _mkTag("office", "automatic-styles"))
            self._xMast = ET.SubElement(self._dStyl, _mkTag("office", "master-styles"))

            ET.SubElement(self._xFont, _mkTag("style", "font-face"), attrib=fAttr)
            ET.SubElement(self._xFnt2, _mkTag("style", "font-face"), attrib=fAttr)

        # Finalise
        # ========

        self._xText = ET.SubElement(self._xBody, _mkTag("office", "text"))

        timeStamp = datetime.now().isoformat(sep="T", timespec="seconds")

        # Office Meta Data
        xMeta = ET.SubElement(self._xMeta, _mkTag("meta", "creation-date"))
        xMeta.text = timeStamp

        xMeta = ET.SubElement(self._xMeta, _mkTag("meta", "generator"))
        xMeta.text = f"novelWriter/{__version__}"

        xMeta = ET.SubElement(self._xMeta, _mkTag("meta", "initial-creator"))
        xMeta.text = self._project.data.author

        xMeta = ET.SubElement(self._xMeta, _mkTag("meta", "editing-cycles"))
        xMeta.text = str(self._project.data.saveCount)

        # Format is: PnYnMnDTnHnMnS
        # https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#duration
        eT = self._project.data.editTime
        xMeta = ET.SubElement(self._xMeta, _mkTag("meta", "editing-duration"))
        xMeta.text = f"P{eT//86400:d}DT{eT%86400//3600:d}H{eT%3600//60:d}M{eT%60:d}S"

        # Dublin Core Meta Data
        xMeta = ET.SubElement(self._xMeta, _mkTag("dc", "title"))
        xMeta.text = self._project.data.name

        xMeta = ET.SubElement(self._xMeta, _mkTag("dc", "date"))
        xMeta.text = timeStamp

        xMeta = ET.SubElement(self._xMeta, _mkTag("dc", "creator"))
        xMeta.text = self._project.data.author

        self._pageStyles()
        self._defaultStyles()
        self._useableStyles()
        self._writeHeader()

        return

    def doConvert(self) -> None:
        """Convert the list of text tokens into XML elements."""
        self._result = ""  # Not used, but cleared just in case

        xText = self._xText
        for tType, _, tText, tFormat, tStyle in self._tokens:

            # Styles
            oStyle = ODTParagraphStyle("New")
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
                if tStyle & self.A_PBA:
                    oStyle.setBreakAfter("page")

                if tStyle & self.A_Z_BTMMRG:
                    oStyle.setMarginBottom("0.000cm")
                if tStyle & self.A_Z_TOPMRG:
                    oStyle.setMarginTop("0.000cm")

                if tStyle & self.A_IND_L:
                    oStyle.setMarginLeft(self._fBlockIndent)
                if tStyle & self.A_IND_R:
                    oStyle.setMarginRight(self._fBlockIndent)

            # Process Text Types
            if tType == self.T_TEXT:
                # Text indentation is processed here because there is a
                # dedicated pre-defined style for it
                if tStyle & self.A_IND_T:
                    self._addTextPar(xText, S_FIND, oStyle, tText, tFmt=tFormat)
                else:
                    self._addTextPar(xText, S_TEXT, oStyle, tText, tFmt=tFormat)

            elif tType == self.T_TITLE:
                # Title must be text:p
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                self._addTextPar(xText, S_TITLE, oStyle, tHead, isHead=False)

            elif tType == self.T_HEAD1:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                self._addTextPar(xText, S_HEAD1, oStyle, tHead, isHead=True, oLevel="1")

            elif tType == self.T_HEAD2:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                self._addTextPar(xText, S_HEAD2, oStyle, tHead, isHead=True, oLevel="2")

            elif tType == self.T_HEAD3:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                self._addTextPar(xText, S_HEAD3, oStyle, tHead, isHead=True, oLevel="3")

            elif tType == self.T_HEAD4:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                self._addTextPar(xText, S_HEAD4, oStyle, tHead, isHead=True, oLevel="4")

            elif tType == self.T_SEP:
                self._addTextPar(xText, S_SEP, oStyle, tText)

            elif tType == self.T_SKIP:
                self._addTextPar(xText, S_TEXT, oStyle, "")

            elif tType == self.T_SYNOPSIS and self._doSynopsis:
                tTemp, tFmt = self._formatSynopsis(tText, tFormat, True)
                self._addTextPar(xText, S_META, oStyle, tTemp, tFmt=tFmt)

            elif tType == self.T_SHORT and self._doSynopsis:
                tTemp, tFmt = self._formatSynopsis(tText, tFormat, False)
                self._addTextPar(xText, S_META, oStyle, tTemp, tFmt=tFmt)

            elif tType == self.T_COMMENT and self._doComments:
                tTemp, tFmt = self._formatComments(tText, tFormat)
                self._addTextPar(xText, S_META, oStyle, tTemp, tFmt=tFmt)

            elif tType == self.T_KEYWORD and self._doKeywords:
                tTemp, tFmt = self._formatKeywords(tText)
                self._addTextPar(xText, S_META, oStyle, tTemp, tFmt=tFmt)

        return

    def closeDocument(self) -> None:
        """Pack the automatic styles of the XML document."""
        for style in self._autoPara.values():
            style.packXML(self._xAuto)
        for style in self._autoText.values():
            style.packXML(self._xAuto)
        return

    def saveFlatXML(self, path: str | Path) -> None:
        """Save the data to an .fodt file."""
        with open(path, mode="wb") as fObj:
            xml = ET.ElementTree(self._dFlat)
            xmlIndent(xml)
            xml.write(fObj, encoding="utf-8", xml_declaration=True)
        logger.info("Wrote file: %s", path)
        return

    def saveOpenDocText(self, path: str | Path) -> None:
        """Save the data to an .odt file."""
        mMani = _mkTag("manifest", "manifest")
        mVers = _mkTag("manifest", "version")
        mPath = _mkTag("manifest", "full-path")
        mType = _mkTag("manifest", "media-type")
        mFile = _mkTag("manifest", "file-entry")

        xMani = ET.Element(mMani, attrib={mVers: X_VERS})
        ET.SubElement(xMani, mFile, attrib={mPath: "/", mVers: X_VERS, mType: X_MIME})
        ET.SubElement(xMani, mFile, attrib={mPath: "settings.xml", mType: "text/xml"})
        ET.SubElement(xMani, mFile, attrib={mPath: "content.xml", mType: "text/xml"})
        ET.SubElement(xMani, mFile, attrib={mPath: "meta.xml", mType: "text/xml"})
        ET.SubElement(xMani, mFile, attrib={mPath: "styles.xml", mType: "text/xml"})

        oRoot = _mkTag("office", "document-settings")
        oVers = _mkTag("office", "version")
        xSett = ET.Element(oRoot, attrib={oVers: X_VERS})

        def putInZip(name: str, xObj: ET.Element, zipObj: ZipFile) -> None:
            with zipObj.open(name, mode="w") as fObj:
                xml = ET.ElementTree(xObj)
                xml.write(fObj, encoding="utf-8", xml_declaration=True)

        with ZipFile(path, mode="w") as outZip:
            outZip.writestr("mimetype", X_MIME)
            putInZip("META-INF/manifest.xml", xMani, outZip)
            putInZip("settings.xml", xSett, outZip)
            putInZip("content.xml", self._dCont, outZip)
            putInZip("meta.xml", self._dMeta, outZip)
            putInZip("styles.xml", self._dStyl, outZip)

        logger.info("Wrote file: %s", path)

        return

    ##
    #  Internal Functions
    ##

    def _formatSynopsis(self, text: str, fmt: T_Formats, synopsis: bool) -> tuple[str, T_Formats]:
        """Apply formatting to synopsis lines."""
        name = self._localLookup("Synopsis" if synopsis else "Short Description")
        shift = len(name) + 2
        rTxt = f"{name}: {text}"
        rFmt: T_Formats = [(0, self.FMT_B_B, ""), (len(name) + 1, self.FMT_B_E, "")]
        rFmt.extend((p + shift, f, d) for p, f, d in fmt)
        return rTxt, rFmt

    def _formatComments(self, text: str, fmt: T_Formats) -> tuple[str, T_Formats]:
        """Apply formatting to comments."""
        name = self._localLookup("Comment")
        shift = len(name) + 2
        rTxt = f"{name}: {text}"
        rFmt: T_Formats = [(0, self.FMT_B_B, ""), (len(name) + 1, self.FMT_B_E, "")]
        rFmt.extend((p + shift, f, d) for p, f, d in fmt)
        return rTxt, rFmt

    def _formatKeywords(self, text: str) -> tuple[str, T_Formats]:
        """Apply formatting to keywords."""
        valid, bits, _ = self._project.index.scanThis("@"+text)
        if not valid or not bits or bits[0] not in nwLabels.KEY_NAME:
            return "", []

        rTxt = f"{self._localLookup(nwLabels.KEY_NAME[bits[0]])}: "
        rFmt: T_Formats = [(0, self.FMT_B_B, ""), (len(rTxt) - 1, self.FMT_B_E, "")]
        if len(bits) > 1:
            if bits[0] == nwKeyWords.TAG_KEY:
                rTxt += bits[1]
            else:
                rTxt += ", ".join(bits[1:])

        return rTxt, rFmt

    def _addTextPar(
        self, xParent: ET.Element, styleName: str, oStyle: ODTParagraphStyle, tText: str,
        tFmt: Sequence[tuple[int, int, str]] = [], isHead: bool = False, oLevel: str | None = None
    ) -> None:
        """Add a text paragraph to the text XML element."""
        tAttr = {_mkTag("text", "style-name"): self._paraStyle(styleName, oStyle)}
        if oLevel is not None:
            tAttr[_mkTag("text", "outline-level")] = oLevel

        pTag = "h" if isHead else "p"
        xElem = ET.SubElement(xParent, _mkTag("text", pTag), attrib=tAttr)

        # It's important to set the initial text field to empty, otherwise
        # xmlIndent will add a line break if the first subelement is a span.
        xElem.text = ""

        if not tText:
            return

        # Loop Over Fragments
        # ===================

        parProc = XMLParagraph(xElem)

        pErr = 0
        xFmt = 0x00
        tFrag = ""
        fLast = 0
        xNode = None
        for fPos, fFmt, fData in tFmt:

            # Add any extra nodes
            if xNode is not None:
                parProc.appendNode(xNode)
                xNode = None

            # Add the text up to the current fragment
            if tFrag := tText[fLast:fPos]:
                if xFmt == 0x00:
                    parProc.appendText(tFrag)
                else:
                    parProc.appendSpan(tFrag, self._textStyle(xFmt))

            # Calculate the change of format
            if fFmt == self.FMT_B_B:
                xFmt |= X_BLD
            elif fFmt == self.FMT_B_E:
                xFmt &= M_BLD
            elif fFmt == self.FMT_I_B:
                xFmt |= X_ITA
            elif fFmt == self.FMT_I_E:
                xFmt &= M_ITA
            elif fFmt == self.FMT_D_B:
                xFmt |= X_DEL
            elif fFmt == self.FMT_D_E:
                xFmt &= M_DEL
            elif fFmt == self.FMT_U_B:
                xFmt |= X_UND
            elif fFmt == self.FMT_U_E:
                xFmt &= M_UND
            elif fFmt == self.FMT_M_B:
                xFmt |= X_MRK
            elif fFmt == self.FMT_M_E:
                xFmt &= M_MRK
            elif fFmt == self.FMT_SUP_B:
                xFmt |= X_SUP
            elif fFmt == self.FMT_SUP_E:
                xFmt &= M_SUP
            elif fFmt == self.FMT_SUB_B:
                xFmt |= X_SUB
            elif fFmt == self.FMT_SUB_E:
                xFmt &= M_SUB
            elif fFmt == self.FMT_DL_B:
                xFmt |= X_DLG
            elif fFmt == self.FMT_DL_E:
                xFmt &= M_DLG
            elif fFmt == self.FMT_ADL_B:
                xFmt |= X_DLA
            elif fFmt == self.FMT_ADL_E:
                xFmt &= M_DLA
            elif fFmt == self.FMT_FNOTE:
                xNode = self._generateFootnote(fData)
            elif fFmt == self.FMT_STRIP:
                pass
            else:
                pErr += 1

            fLast = fPos

        if xNode is not None:
            parProc.appendNode(xNode)

        if tFrag := tText[fLast:]:
            if xFmt == 0x00:
                parProc.appendText(tFrag)
            else:
                parProc.appendSpan(tFrag, self._textStyle(xFmt))

        if pErr > 0:
            self._errData.append("Unknown format tag encountered")

        nErr, errMsg = parProc.checkError()
        if nErr > 0:  # pragma: no cover
            # This one should only capture bugs
            self._errData.append(errMsg)

        return

    def _paraStyle(self, mainName: str, modStyle: ODTParagraphStyle) -> str:
        """Return a name for a style object."""
        if not (refStyle := self._mainPara.get(mainName)):
            logger.error("Unknown main paragraph style '%s'", mainName)
            return "Standard"

        if not refStyle.checkNew(modStyle):
            # The style is unmodified, so we return the main style
            return mainName

        # The style is modified, so we check if there already is an
        # identical style with the same parent we can use instead
        modStyle.setParentStyleName(mainName)
        if (pID := modStyle.getID()) in self._autoPara:
            return self._autoPara[pID].name

        # If neither of the above hold, we store it as a new style
        modStyle.setName(f"P{len(self._autoPara)+1:d}")
        self._autoPara[pID] = modStyle

        return modStyle.name

    def _textStyle(self, hFmt: int) -> str:
        """Return a text style for a given style code."""
        if hFmt in self._autoText:
            return self._autoText[hFmt].name

        style = ODTTextStyle(f"T{len(self._autoText)+1:d}")
        if hFmt & X_BLD:
            style.setFontWeight(self._fontBold)
        if hFmt & X_ITA:
            style.setFontStyle("italic")
        if hFmt & X_DEL:
            style.setStrikeStyle("solid")
            style.setStrikeType("single")
        if hFmt & X_UND:
            style.setUnderlineStyle("solid")
            style.setUnderlineWidth("auto")
            style.setUnderlineColour("font-color")
        if hFmt & X_MRK:
            style.setBackgroundColour(self._markText)
        if hFmt & X_SUP:
            style.setTextPosition("super")
        if hFmt & X_SUB:
            style.setTextPosition("sub")
        if hFmt & X_DLG:
            style.setColour(self._colDialogM)
        if hFmt & X_DLA:
            style.setColour(self._colDialogA)
        self._autoText[hFmt] = style

        return style.name

    def _generateFootnote(self, key: str) -> ET.Element | None:
        """Generate a footnote XML object."""
        if content := self._footnotes.get(key):
            self._nNote += 1
            nStyle = ODTParagraphStyle("New")
            xNote = ET.Element(_mkTag("text", "note"), attrib={
                _mkTag("text", "id"): f"ftn{self._nNote}",
                _mkTag("text", "note-class"): "footnote",
            })
            xCite = ET.SubElement(xNote, _mkTag("text", "note-citation"))
            xCite.text = str(self._nNote)
            xBody = ET.SubElement(xNote, _mkTag("text", "note-body"))
            self._addTextPar(xBody, "Footnote", nStyle, content[0], tFmt=content[1])
            return xNote
        return None

    def _emToCm(self, value: float) -> str:
        """Converts an em value to centimetres."""
        return f"{value*2.54/72*self._fontSize:.3f}cm"

    ##
    #  Style Elements
    ##

    def _pageStyles(self) -> None:
        """Set the default page style."""
        xPage = ET.SubElement(
            self._xAuto if self._isFlat else self._xAut2,
            _mkTag("style", "page-layout"),
            attrib={_mkTag("style", "name"): "PM1"}
        )
        ET.SubElement(xPage, _mkTag("style", "page-layout-properties"), attrib={
            _mkTag("fo", "page-width"): self._mDocWidth,
            _mkTag("fo", "page-height"): self._mDocHeight,
            _mkTag("fo", "margin-top"): self._mDocTop,
            _mkTag("fo", "margin-bottom"): self._mDocBtm,
            _mkTag("fo", "margin-left"): self._mDocLeft,
            _mkTag("fo", "margin-right"): self._mDocRight,
        })

        xHead = ET.SubElement(xPage, _mkTag("style", "header-style"))
        ET.SubElement(xHead, _mkTag("style", "header-footer-properties"), attrib={
            _mkTag("fo", "min-height"): "0.600cm",
            _mkTag("fo", "margin-left"): "0.000cm",
            _mkTag("fo", "margin-right"): "0.000cm",
            _mkTag("fo", "margin-bottom"): "0.500cm",
        })

        return

    def _defaultStyles(self) -> None:
        """Set the default styles."""
        # Add Paragraph Family Style
        xStyl = ET.SubElement(self._xStyl, _mkTag("style", "default-style"), attrib={
            _mkTag("style", "family"): "paragraph",
        })
        ET.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib={
            _mkTag("style", "line-break"): "strict",
            _mkTag("style", "tab-stop-distance"): "1.251cm",
            _mkTag("style", "writing-mode"): "page",
        })
        ET.SubElement(xStyl, _mkTag("style", "text-properties"), attrib={
            _mkTag("style", "font-name"): self._fontFamily,
            _mkTag("fo", "font-family"): self._fontFamily,
            _mkTag("fo", "font-weight"): self._fontWeight,
            _mkTag("fo", "font-style"): self._fontStyle,
            _mkTag("fo", "font-size"): self._fSizeText,
            _mkTag("fo", "language"): self._dLanguage,
            _mkTag("fo", "country"): self._dCountry,
        })

        # Add Standard Paragraph Style
        xStyl = ET.SubElement(self._xStyl, _mkTag("style", "style"), attrib={
            _mkTag("style", "name"): "Standard",
            _mkTag("style", "family"): "paragraph",
            _mkTag("style", "class"): "text",
        })
        ET.SubElement(xStyl, _mkTag("style", "text-properties"), attrib={
            _mkTag("style", "font-name"): self._fontFamily,
            _mkTag("fo", "font-family"): self._fontFamily,
            _mkTag("fo", "font-weight"): self._fontWeight,
            _mkTag("fo", "font-style"): self._fontStyle,
            _mkTag("fo", "font-size"): self._fSizeText,
        })

        # Add Default Heading Style
        xStyl = ET.SubElement(self._xStyl, _mkTag("style", "style"), attrib={
            _mkTag("style", "name"): "Heading",
            _mkTag("style", "family"): "paragraph",
            _mkTag("style", "parent-style-name"): "Standard",
            _mkTag("style", "next-style-name"): S_TEXT,
            _mkTag("style", "class"): "text",
        })
        ET.SubElement(xStyl, _mkTag("style", "paragraph-properties"), attrib={
            _mkTag("fo", "margin-top"): self._mTopHead,
            _mkTag("fo", "margin-bottom"): self._mBotHead,
            _mkTag("fo", "keep-with-next"): "always",
        })
        ET.SubElement(xStyl, _mkTag("style", "text-properties"), attrib={
            _mkTag("style", "font-name"): self._fontFamily,
            _mkTag("fo", "font-family"): self._fontFamily,
            _mkTag("fo", "font-weight"): self._fontWeight,
            _mkTag("fo", "font-style"): self._fontStyle,
            _mkTag("fo", "font-size"): self._fSizeHead,
        })

        # Add Header and Footer Styles
        ET.SubElement(self._xStyl, _mkTag("style", "style"), attrib={
            _mkTag("style", "name"): S_HNF,
            _mkTag("style", "display-name"): "Header and Footer",
            _mkTag("style", "family"): "paragraph",
            _mkTag("style", "parent-style-name"): "Standard",
            _mkTag("style", "class"): "extra",
        })

        return

    def _useableStyles(self) -> None:
        """Set the usable styles."""
        # Add Text Body Style
        style = ODTParagraphStyle(S_TEXT)
        style.setDisplayName("Text body")
        style.setParentStyleName("Standard")
        style.setClass("text")
        style.setMarginTop(self._mTopText)
        style.setMarginBottom(self._mBotText)
        style.setLineHeight(self._fLineHeight)
        style.setTextAlign(self._textAlign)
        style.setFontName(self._fontFamily)
        style.setFontFamily(self._fontFamily)
        style.setFontSize(self._fSizeText)
        style.setFontWeight(self._fontWeight)
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        # Add First Line Indent Style
        style = ODTParagraphStyle(S_FIND)
        style.setDisplayName("First line indent")
        style.setParentStyleName(S_TEXT)
        style.setClass("text")
        style.setTextIndent(self._fTextIndent)
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        # Add Text Meta Style
        style = ODTParagraphStyle(S_META)
        style.setDisplayName("Text Meta")
        style.setParentStyleName("Standard")
        style.setClass("text")
        style.setMarginTop(self._mTopMeta)
        style.setMarginBottom(self._mBotMeta)
        style.setLineHeight(self._fLineHeight)
        style.setFontName(self._fontFamily)
        style.setFontFamily(self._fontFamily)
        style.setFontSize(self._fSizeText)
        style.setFontWeight(self._fontWeight)
        style.setColour(self._colMetaTx)
        style.setOpacity(self._opaMetaTx)
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        # Add Title Style
        style = ODTParagraphStyle(S_TITLE)
        style.setDisplayName("Title")
        style.setParentStyleName("Heading")
        style.setNextStyleName(S_TEXT)
        style.setClass("chapter")
        style.setMarginTop(self._mTopTitle)
        style.setMarginBottom(self._mBotTitle)
        style.setTextAlign("center")
        style.setFontName(self._fontFamily)
        style.setFontFamily(self._fontFamily)
        style.setFontSize(self._fSizeTitle)
        style.setFontWeight(self._fontBold)
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        # Add Separator Style
        style = ODTParagraphStyle(S_SEP)
        style.setDisplayName("Separator")
        style.setParentStyleName("Standard")
        style.setNextStyleName(S_TEXT)
        style.setClass("text")
        style.setMarginTop(self._mTopSep)
        style.setMarginBottom(self._mBotSep)
        style.setLineHeight(self._fLineHeight)
        style.setTextAlign("center")
        style.setFontName(self._fontFamily)
        style.setFontFamily(self._fontFamily)
        style.setFontSize(self._fSizeText)
        style.setFontWeight(self._fontWeight)
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        # Add Heading 1 Style
        style = ODTParagraphStyle(S_HEAD1)
        style.setDisplayName("Heading 1")
        style.setParentStyleName("Heading")
        style.setNextStyleName(S_TEXT)
        style.setOutlineLevel("1")
        style.setClass("text")
        style.setMarginTop(self._mTopHead1)
        style.setMarginBottom(self._mBotHead1)
        style.setFontName(self._fontFamily)
        style.setFontFamily(self._fontFamily)
        style.setFontSize(self._fSizeHead1)
        style.setFontWeight(self._fontBold)
        style.setColour(self._colHead12)
        style.setOpacity(self._opaHead12)
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        # Add Heading 2 Style
        style = ODTParagraphStyle(S_HEAD2)
        style.setDisplayName("Heading 2")
        style.setParentStyleName("Heading")
        style.setNextStyleName(S_TEXT)
        style.setOutlineLevel("2")
        style.setClass("text")
        style.setMarginTop(self._mTopHead2)
        style.setMarginBottom(self._mBotHead2)
        style.setFontName(self._fontFamily)
        style.setFontFamily(self._fontFamily)
        style.setFontSize(self._fSizeHead2)
        style.setFontWeight(self._fontBold)
        style.setColour(self._colHead12)
        style.setOpacity(self._opaHead12)
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        # Add Heading 3 Style
        style = ODTParagraphStyle(S_HEAD3)
        style.setDisplayName("Heading 3")
        style.setParentStyleName("Heading")
        style.setNextStyleName(S_TEXT)
        style.setOutlineLevel("3")
        style.setClass("text")
        style.setMarginTop(self._mTopHead3)
        style.setMarginBottom(self._mBotHead3)
        style.setFontName(self._fontFamily)
        style.setFontFamily(self._fontFamily)
        style.setFontSize(self._fSizeHead3)
        style.setFontWeight(self._fontBold)
        style.setColour(self._colHead34)
        style.setOpacity(self._opaHead34)
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        # Add Heading 4 Style
        style = ODTParagraphStyle(S_HEAD4)
        style.setDisplayName("Heading 4")
        style.setParentStyleName("Heading")
        style.setNextStyleName(S_TEXT)
        style.setOutlineLevel("4")
        style.setClass("text")
        style.setMarginTop(self._mTopHead4)
        style.setMarginBottom(self._mBotHead4)
        style.setFontName(self._fontFamily)
        style.setFontFamily(self._fontFamily)
        style.setFontSize(self._fSizeHead4)
        style.setFontWeight(self._fontBold)
        style.setColour(self._colHead34)
        style.setOpacity(self._opaHead34)
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        # Add Header Style
        style = ODTParagraphStyle("Header")
        style.setDisplayName("Header")
        style.setParentStyleName(S_HNF)
        style.setTextAlign("right")
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        # Add Footnote Style
        style = ODTParagraphStyle("Footnote")
        style.setDisplayName("Footnote")
        style.setParentStyleName("Standard")
        style.setClass("extra")
        style.setMarginLeft(self._mLeftFoot)
        style.setMarginBottom(self._mBotFoot)
        style.setTextIndent("-"+self._mLeftFoot)
        style.setFontSize(self._fSizeFoot)
        style.packXML(self._xStyl)
        self._mainPara[style.name] = style

        return

    def _writeHeader(self) -> None:
        """Write the header elements."""
        xPage = ET.SubElement(self._xMast, _mkTag("style", "master-page"), attrib={
            _mkTag("style", "name"): "Standard",
            _mkTag("style", "page-layout-name"): "PM1",
        })

        # Standard Page Header
        if self._headerFormat:
            pre, page, post = self._headerFormat.partition(nwHeadFmt.ODT_PAGE)

            pre = pre.replace(nwHeadFmt.ODT_PROJECT, self._project.data.name)
            pre = pre.replace(nwHeadFmt.ODT_AUTHOR, self._project.data.author)
            post = post.replace(nwHeadFmt.ODT_PROJECT, self._project.data.name)
            post = post.replace(nwHeadFmt.ODT_AUTHOR, self._project.data.author)

            xHead = ET.SubElement(xPage, _mkTag("style", "header"))
            xPar = ET.SubElement(xHead, _mkTag("text", "p"), attrib={
                _mkTag("text", "style-name"): "Header"
            })
            xPar.text = pre
            if page:
                attr = {_mkTag("text", "select-page"): "current"}
                if self._pageOffset > 0:
                    attr = {_mkTag("text", "page-adjust"): str(0 - self._pageOffset)}
                xTail = ET.SubElement(xPar, _mkTag("text", "page-number"), attrib=attr)
                xTail.text = "2"
                xTail.tail = post
            else:
                xPar.text += post

        # First Page Header
        xHead = ET.SubElement(xPage, _mkTag("style", "header-first"))
        xPar = ET.SubElement(xHead, _mkTag("text", "p"), attrib={
            _mkTag("text", "style-name"): "Header"
        })

        return


# Auto-Style Classes
# ==================

class ODTParagraphStyle:
    """Wrapper class for the paragraph style setting used by the
    exporter. Only the used settings are exposed here to keep the class
    minimal and fast.
    """
    VALID_ALIGN  = ["start", "center", "end", "justify", "inside", "outside", "left", "right"]
    VALID_BREAK  = ["auto", "column", "page", "even-page", "odd-page", "inherit"]
    VALID_LEVEL  = ["1", "2", "3", "4"]
    VALID_CLASS  = ["text", "chapter", "extra"]
    VALID_WEIGHT = ["normal", "bold"] + FONT_WEIGHT_NUM

    def __init__(self, name: str) -> None:

        self._name = name

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
            "text-indent":   ["fo", None],
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

    @property
    def name(self) -> str:
        return self._name

    ##
    #  Checkers
    ##

    def isUnaligned(self) -> bool:
        """Check if paragraph has any sort of alignment or margins."""
        return all(
            self._pAttr[n][1] is None for n in ["text-align", "margin-left", "margin-right"]
        )

    ##
    #  Setters
    ##

    def setName(self, name: str) -> None:
        """Set the paragraph style name."""
        self._name = name
        return

    ##
    #  Attribute Setters
    ##

    def setDisplayName(self, value: str | None) -> None:
        """Set style display name."""
        self._mAttr["display-name"][1] = value
        return

    def setParentStyleName(self, value: str | None) -> None:
        """Set parent style name."""
        self._mAttr["parent-style-name"][1] = value
        return

    def setNextStyleName(self, value: str | None) -> None:
        """Set next style name."""
        self._mAttr["next-style-name"][1] = value
        return

    def setOutlineLevel(self, value: str | None) -> None:
        """Set paragraph outline level."""
        if value in self.VALID_LEVEL:
            self._mAttr["default-outline-level"][1] = value
        else:
            self._mAttr["default-outline-level"][1] = None
        return

    def setClass(self, value: str | None) -> None:
        """Set paragraph class."""
        if value in self.VALID_CLASS:
            self._mAttr["class"][1] = value
        else:
            self._mAttr["class"][1] = None
        return

    ##
    #  Paragraph Setters
    ##

    def setMarginTop(self, value: str | None) -> None:
        """Set paragraph top margin."""
        self._pAttr["margin-top"][1] = value
        return

    def setMarginBottom(self, value: str | None) -> None:
        """Set paragraph bottom margin."""
        self._pAttr["margin-bottom"][1] = value
        return

    def setMarginLeft(self, value: str | None) -> None:
        """Set paragraph left margin."""
        self._pAttr["margin-left"][1] = value
        return

    def setMarginRight(self, value: str | None) -> None:
        """Set paragraph right margin."""
        self._pAttr["margin-right"][1] = value
        return

    def setTextIndent(self, value: str | None) -> None:
        """Set text indentation."""
        self._pAttr["text-indent"][1] = value
        return

    def setLineHeight(self, value: str | None) -> None:
        """Set line height."""
        self._pAttr["line-height"][1] = value
        return

    def setTextAlign(self, value: str | None) -> None:
        """Set paragraph text alignment."""
        if value in self.VALID_ALIGN:
            self._pAttr["text-align"][1] = value
        else:
            self._pAttr["text-align"][1] = None
        return

    def setBreakBefore(self, value: str | None) -> None:
        """Set page break before policy."""
        if value in self.VALID_BREAK:
            self._pAttr["break-before"][1] = value
        else:
            self._pAttr["break-before"][1] = None
        return

    def setBreakAfter(self, value: str | None) -> None:
        """Set page break after policy."""
        if value in self.VALID_BREAK:
            self._pAttr["break-after"][1] = value
        else:
            self._pAttr["break-after"][1] = None
        return

    ##
    #  Text Setters
    ##

    def setFontName(self, value: str | None) -> None:
        """Set font name."""
        self._tAttr["font-name"][1] = value
        return

    def setFontFamily(self, value: str | None) -> None:
        """Set font family."""
        self._tAttr["font-family"][1] = value
        return

    def setFontSize(self, value: str | None) -> None:
        """Set font size."""
        self._tAttr["font-size"][1] = value
        return

    def setFontWeight(self, value: str | None) -> None:
        """Set font weight."""
        if value in self.VALID_WEIGHT:
            self._tAttr["font-weight"][1] = value
        else:
            self._tAttr["font-weight"][1] = None
        return

    def setColour(self, value: str | None) -> None:
        """Set text colour."""
        self._tAttr["color"][1] = value
        return

    def setOpacity(self, value: str | None) -> None:
        """Set text opacity."""
        self._tAttr["opacity"][1] = value
        return

    ##
    #  Methods
    ##

    def checkNew(self, style: ODTParagraphStyle) -> bool:
        """Check if there are new settings in style that differ from
        those in this object. Unset styles are ignored as they can be
        inherited from the parent style.
        """
        if any(v and v != self._mAttr[m][1] for m, (_, v) in style._mAttr.items()):
            return True
        if any(v and v != self._pAttr[m][1] for m, (_, v) in style._pAttr.items()):
            return True
        if any(v and v != self._tAttr[m][1] for m, (_, v) in style._tAttr.items()):
            return True
        return False

    def getID(self) -> str:
        """Generate a unique ID from the settings."""
        return sha256((
            f"Paragraph:Main:{str(self._mAttr)}:"
            f"Paragraph:Para:{str(self._pAttr)}:"
            f"Paragraph:Text:{str(self._tAttr)}:"
        ).encode()).hexdigest()

    def packXML(self, xParent: ET.Element) -> None:
        """Pack the content into an xml element."""
        attr = {
            _mkTag("style", "name"): self._name,
            _mkTag("style", "family"): "paragraph",
        }
        attr.update(
            {_mkTag(n, m): v for m, (n, v) in self._mAttr.items() if v}
        )
        xEntry = ET.SubElement(xParent, _mkTag("style", "style"), attrib=attr)

        if attr := {_mkTag(n, m): v for m, (n, v) in self._pAttr.items() if v}:
            ET.SubElement(xEntry, _mkTag("style", "paragraph-properties"), attrib=attr)

        if attr := {_mkTag(n, m): v for m, (n, v) in self._tAttr.items() if v}:
            ET.SubElement(xEntry, _mkTag("style", "text-properties"), attrib=attr)

        return


class ODTTextStyle:
    """Wrapper class for the text style setting used by the exporter.
    Only the used settings are exposed here to keep the class minimal
    and fast.
    """
    VALID_WEIGHT = ["normal", "bold"] + FONT_WEIGHT_NUM
    VALID_STYLE  = ["normal", "italic", "oblique"]
    VALID_POS    = ["super", "sub"]
    VALID_LSTYLE = ["none", "solid"]
    VALID_LTYPE  = ["single", "double"]
    VALID_LWIDTH = ["auto"]
    VALID_LCOL   = ["font-color"]

    def __init__(self, name: str) -> None:
        self._name = name
        self._tAttr = {
            "font-weight":             ["fo",    None],
            "font-style":              ["fo",    None],
            "color":                   ["fo",    None],
            "background-color":        ["fo",    None],
            "text-position":           ["style", None],
            "text-line-through-style": ["style", None],
            "text-line-through-type":  ["style", None],
            "text-underline-style":    ["style", None],
            "text-underline-width":    ["style", None],
            "text-underline-color":    ["style", None],
        }
        return

    @property
    def name(self) -> str:
        return self._name

    ##
    #  Setters
    ##

    def setFontWeight(self, value: str | None) -> None:
        """Set text font weight."""
        if value in self.VALID_WEIGHT:
            self._tAttr["font-weight"][1] = value
        else:
            self._tAttr["font-weight"][1] = None
        return

    def setFontStyle(self, value: str | None) -> None:
        """Set text font style."""
        if value in self.VALID_STYLE:
            self._tAttr["font-style"][1] = value
        else:
            self._tAttr["font-style"][1] = None
        return

    def setColour(self, value: str | None) -> None:
        """Set text colour."""
        if value and len(value) == 7 and value[0] == "#":
            self._tAttr["color"][1] = value
        else:
            self._tAttr["color"][1] = None
        return

    def setBackgroundColour(self, value: str | None) -> None:
        """Set text background colour."""
        if value and len(value) == 7 and value[0] == "#":
            self._tAttr["background-color"][1] = value
        else:
            self._tAttr["background-color"][1] = None
        return

    def setTextPosition(self, value: str | None) -> None:
        """Set text vertical position."""
        if value in self.VALID_POS:
            self._tAttr["text-position"][1] = f"{value} 58%"
        else:
            self._tAttr["text-position"][1] = None
        return

    def setStrikeStyle(self, value: str | None) -> None:
        """Set text line-trough style."""
        if value in self.VALID_LSTYLE:
            self._tAttr["text-line-through-style"][1] = value
        else:
            self._tAttr["text-line-through-style"][1] = None
        return

    def setStrikeType(self, value: str | None) -> None:
        """Set text line-through type."""
        if value in self.VALID_LTYPE:
            self._tAttr["text-line-through-type"][1] = value
        else:
            self._tAttr["text-line-through-type"][1] = None
        return

    def setUnderlineStyle(self, value: str | None) -> None:
        """Set text underline style."""
        if value in self.VALID_LSTYLE:
            self._tAttr["text-underline-style"][1] = value
        else:
            self._tAttr["text-underline-style"][1] = None
        return

    def setUnderlineWidth(self, value: str | None) -> None:
        """Set text underline width."""
        if value in self.VALID_LWIDTH:
            self._tAttr["text-underline-width"][1] = value
        else:
            self._tAttr["text-underline-width"][1] = None
        return

    def setUnderlineColour(self, value: str | None) -> None:
        """Set text underline colour."""
        if value in self.VALID_LCOL:
            self._tAttr["text-underline-color"][1] = value
        else:
            self._tAttr["text-underline-color"][1] = None
        return

    ##
    #  Methods
    ##

    def packXML(self, xParent: ET.Element) -> None:
        """Pack the content into an xml element."""
        xEntry = ET.SubElement(xParent, _mkTag("style", "style"), attrib={
            _mkTag("style", "name"): self._name,
            _mkTag("style", "family"): "text",
        })
        if attr := {_mkTag(n, m): v for m, (n, v) in self._tAttr.items() if v}:
            ET.SubElement(xEntry, _mkTag("style", "text-properties"), attrib=attr)
        return


# XML Complex Element Helper Class
# ================================

X_ROOT_TEXT = 0
X_ROOT_TAIL = 1
X_SPAN_TEXT = 2
X_SPAN_SING = 3


class XMLParagraph:
    """This is a helper class to manage the text content of a single
    XML element using mixed content tags.

    Rules:
     * The root tag can only have text set, never tail.
     * Any span must be under root, and the text in the span is set in
       one pass. The span then becomes the new base element using tail
       for further added text, permanently replacing root.
     * Any single special tags like tabs, line breaks or multi-spaces,
       should never have text set. After insertion, they become the next
       tail tag if on root level, or if in a span, only exists within
       the lifetime of the span. In this case, the span becomes the new
       tail.

    The four constants associated with this class represent the only
    allowed states the class can exist in, which dictates which XML
    object and attribute is written to,
    """

    def __init__(self, xRoot: ET.Element) -> None:

        self._xRoot = xRoot
        self._xTail = ET.Element("")
        self._xSing = ET.Element("")

        self._nState = X_ROOT_TEXT
        self._chrPos = 0
        self._rawTxt = ""
        self._xRoot.text = ""

        return

    def appendText(self, text: str) -> None:
        """Append text to the XML element. We do this one character at
        the time in order to be able to process line breaks, tabs and
        spaces separately. Multiple spaces are concatenated into a
        single tag, and must therefore be processed separately.
        """
        text = stripEscape(text)
        nSpaces = 0
        self._rawTxt += text

        for c in text:
            if c == " ":
                nSpaces += 1
                continue
            elif nSpaces > 0:
                self._processSpaces(nSpaces)
                nSpaces = 0

            if c == "\n":
                if self._nState in (X_ROOT_TEXT, X_ROOT_TAIL):
                    self._xTail = ET.SubElement(self._xRoot, TAG_BR)
                    self._xTail.tail = ""
                    self._nState = X_ROOT_TAIL
                    self._chrPos += 1
                elif self._nState in (X_SPAN_TEXT, X_SPAN_SING):
                    self._xSing = ET.SubElement(self._xTail, TAG_BR)
                    self._xSing.tail = ""
                    self._nState = X_SPAN_SING
                    self._chrPos += 1
            elif c == "\t":
                if self._nState in (X_ROOT_TEXT, X_ROOT_TAIL):
                    self._xTail = ET.SubElement(self._xRoot, TAG_TAB)
                    self._xTail.tail = ""
                    self._nState = X_ROOT_TAIL
                    self._chrPos += 1
                elif self._nState in (X_SPAN_TEXT, X_SPAN_SING):
                    self._xSing = ET.SubElement(self._xTail, TAG_TAB)
                    self._xSing.tail = ""
                    self._chrPos += 1
                    self._nState = X_SPAN_SING
            else:
                if self._nState == X_ROOT_TEXT:
                    self._xRoot.text = (self._xRoot.text or "") + c
                    self._chrPos += 1
                elif self._nState == X_ROOT_TAIL:
                    self._xTail.tail = (self._xTail.tail or "") + c
                    self._chrPos += 1
                elif self._nState == X_SPAN_TEXT:
                    self._xTail.text = (self._xTail.text or "") + c
                    self._chrPos += 1
                elif self._nState == X_SPAN_SING:
                    self._xSing.tail = (self._xSing.tail or "") + c
                    self._chrPos += 1

        if nSpaces > 0:
            # Handle trailing spaces
            self._processSpaces(nSpaces)

        return

    def appendSpan(self, text: str, fmt: str) -> None:
        """Append a text span to the XML element. The span is always
        closed since we do not allow nested spans (like Libre Office).
        Therefore we return to the root element level when we're done
        processing the text of the span.
        """
        self._xTail = ET.SubElement(self._xRoot, TAG_SPAN, attrib={TAG_STNM: fmt})
        self._xTail.text = ""  # Defaults to None
        self._xTail.tail = ""  # Defaults to None
        self._nState = X_SPAN_TEXT
        self.appendText(text)
        self._nState = X_ROOT_TAIL
        return

    def appendNode(self, xNode: ET.Element | None) -> None:
        """Append an XML node to the paragraph. We only check for the
        X_ROOT_TEXT and X_ROOT_TAIL states. X_SPAN_TEXT is not possible
        at all, and X_SPAN_SING only happens internally in an appendSpan
        call, returning us to an X_ROOT_TAIL state.
        """
        if xNode is not None and self._nState in (X_ROOT_TEXT, X_ROOT_TAIL):
            self._xRoot.append(xNode)
            self._xTail = xNode
            self._xTail.tail = ""
            self._nState = X_ROOT_TAIL
        return

    def checkError(self) -> tuple[int, str]:
        """Check that the number of characters written matches the
        number of characters received.
        """
        errMsg = ""
        nMissed = len(self._rawTxt) - self._chrPos
        if nMissed != 0:
            errMsg = "%d char(s) were not written: '%s'" % (nMissed, self._rawTxt)
        return nMissed, errMsg

    ##
    #  Internal Functions
    ##

    def _processSpaces(self, nSpaces: int) -> None:
        """Add spaces to paragraph. The first space is always written
        as-is (unless it's the first character of the paragraph). The
        second space uses the dedicated tag for spaces, and from the
        third space and on, a counter is added to the tag.

        See: http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html
        Sections: 6.1.2, 6.1.3, and 19.763
        """
        if nSpaces > 0:
            if self._chrPos > 0:
                if self._nState == X_ROOT_TEXT:
                    self._xRoot.text = (self._xRoot.text or "") + " "
                    self._chrPos += 1
                elif self._nState == X_ROOT_TAIL:
                    self._xTail.tail = (self._xTail.tail or "") + " "
                    self._chrPos += 1
                elif self._nState == X_SPAN_TEXT:
                    self._xTail.text = (self._xTail.text or "") + " "
                    self._chrPos += 1
                elif self._nState == X_SPAN_SING:
                    self._xSing.tail = (self._xSing.tail or "") + " "
                    self._chrPos += 1
            else:
                nSpaces += 1

        if nSpaces == 2:
            if self._nState in (X_ROOT_TEXT, X_ROOT_TAIL):
                self._xTail = ET.SubElement(self._xRoot, TAG_SPC)
                self._xTail.tail = ""
                self._nState = X_ROOT_TAIL
                self._chrPos += nSpaces - 1

            elif self._nState in (X_SPAN_TEXT, X_SPAN_SING):
                self._xSing = ET.SubElement(self._xTail, TAG_SPC)
                self._xSing.tail = ""
                self._nState = X_SPAN_SING
                self._chrPos += nSpaces - 1

        elif nSpaces > 2:
            if self._nState in (X_ROOT_TEXT, X_ROOT_TAIL):
                self._xTail = ET.SubElement(self._xRoot, TAG_SPC, attrib={
                    TAG_NSPC: str(nSpaces - 1)
                })
                self._xTail.tail = ""
                self._nState = X_ROOT_TAIL
                self._chrPos += nSpaces - 1

            elif self._nState in (X_SPAN_TEXT, X_SPAN_SING):
                self._xSing = ET.SubElement(self._xTail, TAG_SPC, attrib={
                    TAG_NSPC: str(nSpaces - 1)
                })
                self._xSing.tail = ""
                self._nState = X_SPAN_SING
                self._chrPos += nSpaces - 1

        return
