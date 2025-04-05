"""
novelWriter – EPUB Converter
============================

File History:
Created: 2025-04-05 [2.7b1] ToEpub

This file is a part of novelWriter
Copyright (C) 2025 Veronica Berglyd Olsen and novelWriter contributors

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

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from novelwriter.common import xmlElement, xmlSubElem
from novelwriter.core.project import NWProject
from novelwriter.formats.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

X_MIME = "application/epub+zip"

# Main XML NameSpaces
XML_NS = {
    "dc": "http://purl.org/dc/elements/1.1/",
}
for ns, uri in XML_NS.items():
    ET.register_namespace(ns, uri)


def _mkTag(ns: str, tag: str) -> str:
    """Assemble namespace and tag name."""
    if uri := XML_NS.get(ns, ""):
        return f"{{{uri}}}{tag}"
    logger.warning("Missing xml namespace '%s'", ns)
    return tag


class ToEPub(Tokenizer):

    def __init__(self, project: NWProject) -> None:
        super().__init__(project)
        return

    ##
    #  Class Methods
    ##

    def doConvert(self) -> None:
        return

    def closeDocument(self) -> None:
        return

    def saveDocument(self, path: Path) -> None:
        """Save the data to a .epub file."""

        xContainer = xmlElement("container", attrib={
            "xmlns": "urn:oasis:names:tc:opendocument:xmlns:container",
            "version": "1.0",
        })
        xRootFiles = xmlSubElem(xContainer, "rootfiles")
        xmlSubElem(xRootFiles, "rootfile", attrib={
            "full-path": "OEBPS/package.opf",
            "media-type": "application/oebps-package+xml",
        })

        def xmlToZip(name: str, root: ET.Element, zipObj: ZipFile) -> None:
            zipObj.writestr(name, ET.tostring(root, encoding="utf-8", xml_declaration=True))

        with ZipFile(path, mode="w", compression=ZIP_DEFLATED, compresslevel=3) as outZip:
            outZip.writestr("mimetype", X_MIME, compress_type=None, compresslevel=None)
            xmlToZip("META-INF/container.xml", xContainer, outZip)

        return
