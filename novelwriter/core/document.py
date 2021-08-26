"""
novelWriter – Project Document
==============================
Data class for a single novelWriter document

File History:
Created: 2018-09-29 [0.0.1]

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

import logging
import os

from nw.enum import nwItemLayout, nwItemClass
from nw.common import isHandle

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

        if isHandle(theHandle):
            self._docHandle = theHandle

        if self._docHandle is not None:
            self._theItem = self.theProject.projTree[theHandle]

        return

    ##
    #  Class Methods
    ##

    def readDocument(self, isOrphan=False):
        """Read a document from set handle, capturing potential file
        system errors and parse meta data. If the document doesn't exist
        on disk, return an empty string. If something went wrong, return
        None.
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

            except Exception as e:
                self._docError = str(e)
                return None

        else:
            # The document file does not exist, so we assume it's a new
            # document and initialise an empty text string.
            logger.debug("The requested document does not exist.")
            return ""

        return theText

    def writeDocument(self, docText):
        """Write the document. The file is saved via a temp file in case
        of save failure. Returns True if successful, False if not.
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

        # DocMeta line
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
        except Exception as e:
            self._docError = str(e)
            return False

        # If we're here, the file was successfully saved, so we can
        # replace the temp file with the actual file
        if os.path.isfile(docPath):
            os.unlink(docPath)
        os.rename(docTemp, docPath)

        return True

    def deleteDocument(self):
        """Permanently delete a document source file and related files
        from the project data folder.
        """
        self._docError = ""
        if self._docHandle is None:
            logger.error("No document handle set")
            return False

        docFile = self._docHandle+".nwd"

        chkList = []
        chkList.append(os.path.join(self.theProject.projContent, docFile))
        chkList.append(os.path.join(self.theProject.projContent, docFile+"~"))

        for chkFile in chkList:
            if os.path.isfile(chkFile):
                try:
                    os.unlink(chkFile)
                    logger.debug("Deleted: %s", chkFile)
                except Exception as e:
                    self._docError = str(e)
                    return False

        return True

    ##
    #  Getters
    ##

    def getFileLocation(self):
        """Return the file location of the current file.
        """
        return self._fileLoc

    def getCurrentItem(self):
        """Return a pointer to the currently open item.
        """
        return self._theItem

    def getMeta(self):
        """Parses the document meta tag and returns the path and name as
        a list and a string.
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
        """Parse a line from the document statting with the characters
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
