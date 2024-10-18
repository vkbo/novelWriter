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
from novelwriter.core.project import NWProject
from novelwriter.formats.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

# Types and Relationships
WORD_BASE = "application/vnd.openxmlformats-officedocument"
RELS_TYPE = "application/vnd.openxmlformats-package.relationships+xml"
REL_CORE = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"
REL_APP = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties"
REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"

# Main XML NameSpaces
PROPS_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
XML_NS = {
    "cp":      "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc":      "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "w":       "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "xsi":     "http://www.w3.org/2001/XMLSchema-instance",
}
for ns, uri in XML_NS.items():
    ET.register_namespace(ns, uri)


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
        self._dDoc = ET.Element("")  # document.xml

        self._xBody = ET.Element("")  # Text body

        # Internal
        self._dLanguage = "en-GB"

        return

    ##
    #  Setters
    ##

    def setLanguage(self, language: str | None) -> None:
        """Set language for the document."""
        if language:
            self._dLanguage = language.replace("_", "-")
        return

    ##
    #  Class Methods
    ##

    def initDocument(self) -> None:
        """Initialises the DocX document structure."""

        self._dDoc  = ET.Element(_mkTag("w", "document"))
        self._xBody = ET.SubElement(self._dDoc, _mkTag("w", "body"))

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
            "Id": "rId2", "Type": REL_APP, "Target": "docProps/app.xml",
        })
        _addSingle(dRels, "Relationship", attrib={
            "Id": "rId3", "Type": REL_DOC, "Target": "word/document.xml",
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
            xmlToZip("[Content_Types].xml", dCont, outZip)

        return
