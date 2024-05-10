"""
novelWriter – Project Document
==============================

File History:
Created: 2018-09-29 [0.0.1]

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

import hashlib
import logging

from pathlib import Path
from time import time
from typing import TYPE_CHECKING

from novelwriter.common import formatTimeStamp, isHandle
from novelwriter.core.item import NWItem
from novelwriter.enum import nwItemClass, nwItemLayout
from novelwriter.error import formatException, logException

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)


class NWDocument:
    """Core: Document Class

    A Class wrapping a single novelWriter document file. It represents
    a project item of nwItemType FILE. The file is not guaranteed to
    exist, even if the item does. In the case it doesn't exist, reading
    it returns a None rather than an empty or non-empty string.
    """

    def __init__(self, project: NWProject, tHandle: str | None) -> None:

        self._project = project

        self._item      = None   # The currently open item
        self._handle    = None   # The handle of the currently open item
        self._fileLoc   = None   # The file location of the currently open item
        self._docMeta   = {}     # The meta data of the currently open item
        self._docError  = ""     # The latest encountered IO error
        self._lastHash  = ""     # The last known SHA hash
        self._hashError = False  # Hash mismatch on last write attempt

        if isHandle(tHandle):
            self._handle = tHandle

        if self._handle is not None:
            self._item = self._project.tree[tHandle]

        return

    def __repr__(self) -> str:
        return f"<NWDocument handle={self._handle}>"

    def __bool__(self) -> bool:
        return self._handle is not None and self._item is not None

    ##
    #  Properties
    ##

    @property
    def hashError(self) -> bool:
        """Check if the file hash has changed outside of novelWriter."""
        return self._hashError

    @property
    def fileLocation(self) -> str:
        """Return the file location of the current document."""
        return str(self._fileLoc)

    @property
    def createdDate(self) -> str:
        """Return the document creation date."""
        return self._docMeta.get("created", "Unknown")

    @property
    def updatedDate(self) -> str:
        """Return the document creation date."""
        return self._docMeta.get("updated", "Unknown")

    @property
    def nwItem(self) -> NWItem | None:
        """Return a pointer to the currently open NWItem."""
        return self._item

    ##
    #  Static Methods
    ##

    @staticmethod
    def quickReadText(content: Path, tHandle: str) -> str:
        """Return the text of a document in a fast and efficient way."""
        if (path := content / f"{tHandle}.nwd").is_file():
            try:
                with open(path, mode="r", encoding="utf-8") as inFile:
                    line = ""
                    for _ in range(10):
                        if not (line := inFile.readline()).startswith(r"%%~"):
                            break
                    return line + inFile.read()
            except Exception:
                logger.error("Cannot read document with handle '%s'", tHandle)
                logException()
                return ""
        return ""

    ##
    #  Methods
    ##

    def fileExists(self) -> bool:
        """Check if the document file exists."""
        if self._handle is None:
            return False

        contentPath = self._project.storage.contentPath
        if not isinstance(contentPath, Path):
            logger.error("No content path set")
            return False

        return (contentPath / f"{self._handle}.nwd").is_file()

    def readDocument(self, isOrphan: bool = False) -> str | None:
        """Read the document specified by the handle set in the
        constructor, capturing potential file system errors and parse
        meta data. If the document doesn't exist on disk, return an
        empty string. If something went wrong, return None.
        """
        self._docError = ""
        if not isinstance(self._handle, str):
            logger.error("No document handle set")
            return None

        if self._item is None and not isOrphan:
            logger.error("Unknown novelWriter document")
            return None

        contentPath = self._project.storage.contentPath
        if not isinstance(contentPath, Path):
            logger.error("No content path set")
            return None

        docFile = f"{self._handle}.nwd"
        logger.debug("Opening document: %s", docFile)

        docPath = contentPath / docFile
        self._fileLoc = docPath

        text = ""
        self._docMeta = {}
        self._lastHash = ""

        if docPath.exists():
            try:
                with open(docPath, mode="r", encoding="utf-8") as inFile:
                    # Check the first <= 10 lines for metadata
                    for _ in range(10):
                        line = inFile.readline()
                        if line.startswith(r"%%~"):
                            self._parseMeta(line)
                        else:
                            text = line
                            break

                    # Load the rest of the file
                    text += inFile.read()

            except Exception as exc:
                self._docError = formatException(exc)
                return None

        else:
            # The document file does not exist, so we assume it's a new
            # document and return an empty text string.
            logger.debug("The requested document does not exist")

        self._lastHash = hashlib.sha1(text.encode()).hexdigest()

        return text

    def writeDocument(self, text: str, forceWrite: bool = False) -> bool:
        """Write the document specified by the handle attribute. Handle
        any IO errors in the process  Returns True if successful, False
        if not.
        """
        self._docError = ""
        if not isinstance(self._handle, str):
            logger.error("No document handle set")
            return False

        contentPath = self._project.storage.contentPath
        if not isinstance(contentPath, Path):
            logger.error("No content path set")
            return False

        docFile = f"{self._handle}.nwd"
        logger.debug("Saving document: %s", docFile)

        docPath = contentPath / docFile
        docTemp = docPath.with_suffix(".tmp")

        # Re-read the document on disk to check if it has changed
        prevHash = self._lastHash
        self.readDocument()
        if prevHash and self._lastHash != prevHash and not forceWrite:
            logger.error("File has been altered on disk since opened")
            self._hashError = True
            return False

        currTime = formatTimeStamp(time())
        writeHash = hashlib.sha1(text.encode()).hexdigest()
        createdDate = self._docMeta.get("created", "Unknown")
        updatedDate = self._docMeta.get("updated", "Unknown")
        if writeHash != self._lastHash:
            updatedDate = currTime
        if not docPath.is_file():
            createdDate = currTime
            updatedDate = currTime

        # DocMeta Line
        docMeta = ""
        if self._item:
            docMeta = (
                f"%%~name: {self._item.itemName}\n"
                f"%%~path: {self._item.itemParent}/{self._item.itemHandle}\n"
                f"%%~kind: {self._item.itemClass.name}/{self._item.itemLayout.name}\n"
                f"%%~hash: {writeHash}\n"
                f"%%~date: {createdDate}/{updatedDate}\n"
            )

        try:
            with open(docTemp, mode="w", encoding="utf-8") as outFile:
                outFile.write(docMeta)
                outFile.write(text)
        except Exception as exc:
            self._docError = formatException(exc)
            return False

        # If we're here, the file was successfully saved, so we can
        # replace the temp file with the actual file
        try:
            docTemp.replace(docPath)
        except OSError as exc:
            self._docError = formatException(exc)
            return False

        self._lastHash = writeHash
        self._hashError = False

        return True

    def deleteDocument(self) -> bool:
        """Permanently delete a document source file and related files
        from the project data folder.
        """
        self._docError = ""
        if not isinstance(self._handle, str):
            logger.error("No document handle set")
            return False

        contentPath = self._project.storage.contentPath
        if not isinstance(contentPath, Path):
            logger.error("No content path set")
            return False

        docPath = contentPath / f"{self._handle}.nwd"
        docTemp = docPath.with_suffix(".tmp")

        try:
            docPath.unlink(missing_ok=True)
            docTemp.unlink(missing_ok=True)
        except Exception as exc:
            self._docError = formatException(exc)
            return False

        return True

    ##
    #  Getters
    ##

    def getMeta(self) -> tuple[str, str | None, nwItemClass | None, nwItemLayout | None]:
        """Parse the document meta tag and return the name, parent,
        class and layout meta values.
        """
        name = self._docMeta.get("name", "")
        parent = self._docMeta.get("parent", None)
        itemClass = self._docMeta.get("class", None)
        itemLayout = self._docMeta.get("layout", None)

        return name, parent, itemClass, itemLayout

    def getError(self) -> str:
        """Return the last recorded exception."""
        return self._docError

    ##
    #  Internal Functions
    ##

    def _parseMeta(self, metaLine: str) -> None:
        """Parse a line from the document starting with the characters
        %%~ that may contain meta data.
        """
        if metaLine.startswith("%%~name:"):
            self._docMeta["name"] = metaLine[8:].strip()

        elif metaLine.startswith("%%~path:"):
            metaVal = metaLine[8:].strip()
            metaBits = metaVal.split("/")
            if len(metaBits) == 2:
                if isHandle(metaBits[0]):
                    self._docMeta["parent"] = metaBits[0]
                if isHandle(metaBits[1]):
                    self._docMeta["handle"] = metaBits[1]

        elif metaLine.startswith("%%~kind:"):
            metaVal = metaLine[8:].strip()
            metaBits = metaVal.split("/")
            if len(metaBits) == 2:
                if metaBits[0] in nwItemClass.__members__:
                    self._docMeta["class"] = nwItemClass[metaBits[0]]
                if metaBits[1] in nwItemLayout.__members__:
                    self._docMeta["layout"] = nwItemLayout[metaBits[1]]

        elif metaLine.startswith("%%~hash:"):
            self._docMeta["hash"] = metaLine[8:].strip()

        elif metaLine.startswith("%%~date:"):
            metaVal = metaLine[8:].strip()
            metaBits = metaVal.split("/")
            if len(metaBits) == 2:
                self._docMeta["created"] = metaBits[0].strip()
                self._docMeta["updated"] = metaBits[1].strip()

        else:
            logger.debug("Unknown meta data: '%s'", metaLine.strip())

        return
