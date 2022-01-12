"""
novelWriter – Project Document
==============================
Data class for a single novelWriter document

File History:
Created: 2018-09-29 [0.0.1]

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import os
import logging

from novelwriter.enum import nwItemLayout, nwItemClass
from novelwriter.error import formatException
from novelwriter.common import isHandle, sha256sum

logger = logging.getLogger(__name__)


class NWDoc():

    def __init__(self, theProject, theHandle):

        self.theProject = theProject

        # Internal Variables
        self._theItem   = None  # The currently open item
        self._docHandle = None  # The handle of the currently open item
        self._fileLoc   = None  # The file location of the currently open item
        self._docMeta   = {}    # The meta data of the currently open item
        self._docError  = ""    # The latest encountered IO error
        self._prevHash  = None  # Previous sha256sum of the document file
        self._currHash  = None  # Latest sha256sum of the document file

        if isHandle(theHandle):
            self._docHandle = theHandle

        if self._docHandle is not None:
            self._theItem = self.theProject.projTree[theHandle]

        return

    def __repr__(self):
        return f"<NWDoc handle={self._docHandle}>"

    def __bool__(self):
        return self._docHandle is not None and bool(self._theItem)

    ##
    #  Class Methods
    ##

    def readDocument(self, isOrphan=False):
        """Read the document specified by the handle set in the
        contructor, capturing potential file system errors and parse
        meta data. If the document doesn't exist on disk, return an
        empty string. If something went wrong, return None.
        """
        self._docError = ""
        if self._docHandle is None:
            logger.error("No document handle set")
            return None

        if self._theItem is None and not isOrphan:
            logger.error("Unknown novelWriter document")
            return None

        docFile = self._docHandle+".nwd"
        logger.debug("Opening document: %s", docFile)

        docPath = os.path.join(self.theProject.projContent, docFile)
        self._fileLoc = docPath

        theText = ""
        self._docMeta = {}
        self._prevHash = sha256sum(docPath)

        if os.path.isfile(docPath):
            try:
                with open(docPath, mode="r", encoding="utf-8") as inFile:
                    # Check the first <= 10 lines for metadata
                    for i in range(10):
                        inLine = inFile.readline()
                        if inLine.startswith(r"%%~"):
                            self._parseMeta(inLine)
                        else:
                            theText = inLine
                            break

                    # Load the rest of the file
                    theText += inFile.read()

            except Exception as exc:
                self._docError = formatException(exc)
                return None

        else:
            # The document file does not exist, so we assume it's a new
            # document and initialise an empty text string.
            logger.debug("The requested document does not exist")
            return ""

        return theText

    def writeDocument(self, docText, forceWrite=False):
        """Write the document specified by the handle attribute. Handle
        any IO errors in the process  Returns True if successful, False
        if not.
        """
        self._docError = ""
        if self._docHandle is None:
            logger.error("No document handle set")
            return False

        self.theProject.ensureFolderStructure()

        docFile = self._docHandle+".nwd"
        logger.debug("Saving document: %s", docFile)

        docPath = os.path.join(self.theProject.projContent, docFile)
        docTemp = os.path.join(self.theProject.projContent, docFile+"~")

        if self._prevHash is not None and not forceWrite:
            self._currHash = sha256sum(docPath)
            if self._currHash is not None and self._currHash != self._prevHash:
                logger.error("File has been altered on disk since opened")
                return False

        # DocMeta Line
        if self._theItem is None:
            docMeta = ""
        else:
            docMeta = (
                f"%%~name: {self._theItem.itemName}\n"
                f"%%~path: {self._theItem.itemParent}/{self._theItem.itemHandle}\n"
                f"%%~kind: {self._theItem.itemClass.name}/{self._theItem.itemLayout.name}\n"
            )

        try:
            with open(docTemp, mode="w", encoding="utf-8") as outFile:
                outFile.write(docMeta)
                outFile.write(docText)
        except Exception as exc:
            self._docError = formatException(exc)
            return False

        # If we're here, the file was successfully saved, so we can
        # replace the temp file with the actual file
        try:
            os.replace(docTemp, docPath)
        except OSError as exc:
            self._docError = formatException(exc)
            return False

        self._prevHash = sha256sum(docPath)
        self._currHash = self._prevHash

        return True

    def deleteDocument(self):
        """Permanently delete a document source file and related files
        from the project data folder.
        """
        self._docError = ""
        if self._docHandle is None:
            logger.error("No document handle set")
            return False

        chkList = [
            os.path.join(self.theProject.projContent, f"{self._docHandle}.nwd"),
            os.path.join(self.theProject.projContent, f"{self._docHandle}.nwd~"),
        ]

        for chkFile in chkList:
            if os.path.isfile(chkFile):
                try:
                    os.unlink(chkFile)
                    logger.debug("Deleted: %s", chkFile)
                except Exception as exc:
                    self._docError = formatException(exc)
                    return False

        return True

    ##
    #  Getters
    ##

    def getFileLocation(self):
        """Return the file location of the current document.
        """
        return self._fileLoc

    def getCurrentItem(self):
        """Return a pointer to the currently open NWItem.
        """
        return self._theItem

    def getMeta(self):
        """Parse the document meta tag and return the name, parent,
        class and layout meta values.
        """
        theName = self._docMeta.get("name", "")
        theParent = self._docMeta.get("parent", None)
        theClass = self._docMeta.get("class", None)
        theLayout = self._docMeta.get("layout", None)

        return theName, theParent, theClass, theLayout

    def getError(self):
        """Return the last recorded exception.
        """
        return self._docError

    ##
    #  Internal Functions
    ##

    def _parseMeta(self, metaLine):
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

        else:
            logger.debug("Ignoring meta data: '%s'", metaLine.strip())

        return

# END Class NWDoc
