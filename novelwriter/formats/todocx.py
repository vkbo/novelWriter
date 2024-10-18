"""
novelWriter – DOCX Text Converter
=================================

File History:
Created: 2024-10-15 [2.6b1] ToRaw

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

from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from novelwriter import __version__
from novelwriter.common import xmlIndent
from novelwriter.constants import nwStyles
from novelwriter.core.project import NWProject
from novelwriter.formats.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

# Types and Relationships
WORD_BASE = "application/vnd.openxmlformats-officedocument"
RELS_TYPE = "application/vnd.openxmlformats-package.relationships+xml"
REL_CORE = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"
REL_BASE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

# Main XML NameSpaces
PROPS_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = {
    "w":       W_NS,
    "cp":      "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc":      "http://purl.org/dc/elements/1.1/",
    "xsi":     "http://www.w3.org/2001/XMLSchema-instance",
    "dcterms": "http://purl.org/dc/terms/",
}
for ns, uri in XML_NS.items():
    ET.register_namespace(ns, uri)


def _wTag(tag: str) -> str:
    """Assemble namespace and tag name for standard w namespace."""
    return f"{{{W_NS}}}{tag}"


def _mkTag(ns: str, tag: str) -> str:
    """Assemble namespace and tag name."""
    if uri := XML_NS.get(ns, ""):
        return f"{{{uri}}}{tag}"
    logger.warning("Missing xml namespace '%s'", ns)
    return tag


def _addSingle(
    parent: ET.Element,
    tag: str,
    text: str | int | None = None,
    attrib: dict | None = None
) -> None:
    """Add a single value to a parent element."""
    xSub = ET.SubElement(parent, tag, attrib=attrib or {})
    if text is not None:
        xSub.text = str(text)
    return


class ToDocX(Tokenizer):
    """Core: DocX Document Writer

    Extend the Tokenizer class to writer DocX Document files.
    """

    def __init__(self, project: NWProject) -> None:
        super().__init__(project)

        # XML
        self._dDoc  = ET.Element("")  # document.xml
        self._dStyl = ET.Element("")  # styles.xml

        self._xBody = ET.Element("")  # Text body

        # Properties
        self._headerFormat = ""
        self._pageOffset   = 0

        # Internal
        self._fontFamily = "Liberation Serif"
        self._fontSize   = 12.0
        self._dLanguage  = "en-GB"

        return

    ##
    #  Setters
    ##

    def setLanguage(self, language: str | None) -> None:
        """Set language for the document."""
        if language:
            self._dLanguage = language
        return

    def setPageLayout(
        self, width: float, height: float, top: float, bottom: float, left: float, right: float
    ) -> None:
        """Set the document page size and margins in millimetres."""
        return

    def setHeaderFormat(self, format: str, offset: int) -> None:
        """Set the document header format."""
        self._headerFormat = format.strip()
        self._pageOffset = offset
        return

    ##
    #  Class Methods
    ##

    def _emToSz(self, scale: float) -> int:
        return int()

    def initDocument(self) -> None:
        """Initialises the DocX document structure."""

        self._fontFamily = self._textFont.family()
        self._fontSize = self._textFont.pointSizeF()

        self._dDoc  = ET.Element(_wTag("document"))
        self._dStyl = ET.Element(_wTag("styles"))

        self._xBody = ET.SubElement(self._dDoc, _wTag("body"))

        self._defaultStyles()
        self._useableStyles()

        return

    def doConvert(self) -> None:
        """Convert the list of text tokens into XML elements."""
        self._result = ""  # Not used, but cleared just in case
        return

    def saveDocument(self, path: Path) -> None:
        """Save the data to a .docx file."""
        timeStamp = datetime.now().isoformat(sep="T", timespec="seconds")

        # .rels
        dRels = ET.Element("Relationships", attrib={"xmlns": RELS_NS})
        _addSingle(dRels, "Relationship", attrib={
            "Id": "rId1", "Type": REL_CORE, "Target": "docProps/core.xml",
        })
        _addSingle(dRels, "Relationship", attrib={
            "Id": "rId2", "Type": f"{REL_BASE}/extended-properties", "Target": "docProps/app.xml",
        })
        _addSingle(dRels, "Relationship", attrib={
            "Id": "rId3", "Type": f"{REL_BASE}/officeDocument", "Target": "word/document.xml",
        })

        # core.xml
        dCore = ET.Element("coreProperties")
        tsAttr = {_mkTag("xsi", "type"): "dcterms:W3CDTF"}
        _addSingle(dCore, _mkTag("dcterms", "created"), timeStamp, attrib=tsAttr)
        _addSingle(dCore, _mkTag("dcterms", "modified"), timeStamp, attrib=tsAttr)
        _addSingle(dCore, _mkTag("dc", "creator"), self._project.data.author)
        _addSingle(dCore, _mkTag("dc", "title"), self._project.data.name)
        _addSingle(dCore, _mkTag("dc", "creator"), self._project.data.author)
        _addSingle(dCore, _mkTag("dc", "language"), self._dLanguage)
        _addSingle(dCore, _mkTag("cp", "revision"), str(self._project.data.saveCount))
        _addSingle(dCore, _mkTag("cp", "lastModifiedBy"), self._project.data.author)

        # app.xml
        dApp = ET.Element("Properties", attrib={"xmlns": PROPS_NS})
        _addSingle(dApp, "TotalTime", self._project.data.editTime // 60)
        _addSingle(dApp, "Application", f"novelWriter/{__version__}")
        if count := self._counts.get("allWords"):
            _addSingle(dApp, "Words", count)
        if count := self._counts.get("textWordChars"):
            _addSingle(dApp, "Characters", count)
        if count := self._counts.get("textChars"):
            _addSingle(dApp, "CharactersWithSpaces", count)
        if count := self._counts.get("paragraphCount"):
            _addSingle(dApp, "Paragraphs", count)

        # document.xml.rels
        dDRels = ET.Element("Relationships", attrib={"xmlns": RELS_NS})
        _addSingle(dDRels, "Relationship", attrib={
            "Id": "rId1", "Type": f"{REL_BASE}/styles", "Target": "styles.xml",
        })

        # [Content_Types].xml
        dCont = ET.Element("Types", attrib={"xmlns": TYPES_NS})
        _addSingle(dCont, "Default", attrib={
            "Extension": "xml", "ContentType": "application/xml",
        })
        _addSingle(dCont, "Default", attrib={
            "Extension": "rels", "ContentType": RELS_TYPE,
        })
        _addSingle(dCont, "Override", attrib={
            "PartName": "/_rels/.rels",
            "ContentType": RELS_TYPE,
        })
        _addSingle(dCont, "Override", attrib={
            "PartName": "/docProps/core.xml",
            "ContentType": f"{WORD_BASE}.extended-properties+xml",
        })
        _addSingle(dCont, "Override", attrib={
            "PartName": "/docProps/app.xml",
            "ContentType": "application/vnd.openxmlformats-package.core-properties+xml",
        })
        _addSingle(dCont, "Override", attrib={
            "PartName": "/word/_rels/document.xml.rels",
            "ContentType": RELS_TYPE,
        })
        _addSingle(dCont, "Override", attrib={
            "PartName": "/word/document.xml",
            "ContentType": f"{WORD_BASE}.wordprocessingml.document.main+xml",
        })
        _addSingle(dCont, "Override", attrib={
            "PartName": "/word/styles.xml",
            "ContentType": f"{WORD_BASE}.wordprocessingml.styles+xml",
        })

        def xmlToZip(name: str, xObj: ET.Element, zipObj: ZipFile) -> None:
            with zipObj.open(name, mode="w") as fObj:
                xml = ET.ElementTree(xObj)
                xmlIndent(xml)
                xml.write(fObj, encoding="utf-8", xml_declaration=True)

        with ZipFile(path, mode="w") as outZip:
            xmlToZip("_rels/.rels", dRels, outZip)
            xmlToZip("docProps/core.xml", dCore, outZip)
            xmlToZip("docProps/app.xml", dApp, outZip)
            xmlToZip("word/_rels/document.xml.rels", dDRels, outZip)
            xmlToZip("word/document.xml", self._dDoc, outZip)
            xmlToZip("word/styles.xml", self._dStyl, outZip)
            xmlToZip("[Content_Types].xml", dCont, outZip)

        return

    ##
    #  Internal Functions
    ##

    def _defaultStyles(self) -> None:
        """Set the default styles."""
        xStyl = ET.SubElement(self._dStyl, _wTag("docDefaults"))
        xRDef = ET.SubElement(xStyl, _wTag("rPrDefault"))
        xPDef = ET.SubElement(xStyl, _wTag("pPrDefault"))
        xRPr = ET.SubElement(xRDef, _wTag("rPr"))
        xPPr = ET.SubElement(xPDef, _wTag("pPr"))

        size = str(int(2.0 * self._fontSize))
        line = str(int(2.0 * self._lineHeight * self._fontSize))

        ET.SubElement(xRPr, _wTag("rFonts"), attrib={
            _wTag("ascii"): self._fontFamily,
            _wTag("hAnsi"): self._fontFamily,
            _wTag("cs"): self._fontFamily,
        })
        ET.SubElement(xRPr, _wTag("sz"), attrib={_wTag("val"): size})
        ET.SubElement(xRPr, _wTag("szCs"), attrib={_wTag("val"): size})
        ET.SubElement(xRPr, _wTag("lang"), attrib={_wTag("val"): self._dLanguage})
        ET.SubElement(xPPr, _wTag("spacing"), attrib={_wTag("line"): line})

        return

    def _useableStyles(self) -> None:
        """Set the usable styles."""
        # Add Normal Style
        self._addParStyle(
            name="Normal",
            styleId="Normal",
            size=1.0,
            default=True,
            margins=self._marginText,
        )

        # Add Heading 1
        hScale = self._scaleHeads
        self._addParStyle(
            name="Heading 1",
            styleId="Heading1",
            size=nwStyles.H_SIZES[1] if hScale else 1.0,
            basedOn="Normal",
            nextStyle="Normal",
            margins=self._marginHead1,
            level=0,
        )

        # Add Heading 2
        hScale = self._scaleHeads
        self._addParStyle(
            name="Heading 2",
            styleId="Heading2",
            size=nwStyles.H_SIZES[2] if hScale else 1.0,
            basedOn="Normal",
            nextStyle="Normal",
            margins=self._marginHead2,
            level=1,
        )

        # Add Heading 3
        hScale = self._scaleHeads
        self._addParStyle(
            name="Heading 3",
            styleId="Heading3",
            size=nwStyles.H_SIZES[3] if hScale else 1.0,
            basedOn="Normal",
            nextStyle="Normal",
            margins=self._marginHead3,
            level=1,
        )

        # Add Heading 4
        hScale = self._scaleHeads
        self._addParStyle(
            name="Heading 4",
            styleId="Heading4",
            size=nwStyles.H_SIZES[4] if hScale else 1.0,
            basedOn="Normal",
            nextStyle="Normal",
            margins=self._marginHead4,
            level=1,
        )

        return

    def _addParStyle(
        self, *,
        name: str,
        styleId: str,
        size: float,
        basedOn: str | None = None,
        nextStyle: str | None = None,
        margins: tuple[float, float] | None = None,
        default: bool = False,
        level: int | None = None,
    ) -> None:
        """Add a paragraph style."""
        sAttr = {}
        sAttr[_wTag("type")] = "paragraph"
        sAttr[_wTag("styleId")] = styleId
        if default:
            sAttr[_wTag("default")] = "1"

        sz = str(int(2.0 * size * self._fontSize))

        xStyl = ET.SubElement(self._dStyl, _wTag("style"), attrib=sAttr)
        ET.SubElement(xStyl, _wTag("name"), attrib={_wTag("val"): name})
        if basedOn:
            ET.SubElement(xStyl, _wTag("basedOn"), attrib={_wTag("val"): basedOn})
        if nextStyle:
            ET.SubElement(xStyl, _wTag("next"), attrib={_wTag("val"): nextStyle})
        if level is not None:
            ET.SubElement(xStyl, _wTag("outlineLvl"), attrib={_wTag("val"): str(level)})

        xPPr = ET.SubElement(xStyl, _wTag("pPr"))
        if margins:
            ET.SubElement(xPPr, _wTag("spacing"), attrib={
                _wTag("before"): str(int(20.0 * margins[0])),
                _wTag("after"): str(int(20.0 * margins[1])),
            })

        xRPr = ET.SubElement(xStyl, _wTag("rPr"))
        ET.SubElement(xRPr, _wTag("sz"), attrib={_wTag("val"): sz})
        ET.SubElement(xRPr, _wTag("szCs"), attrib={_wTag("val"): sz})

        return
