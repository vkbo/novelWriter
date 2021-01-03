# -*- coding: utf-8 -*-
"""novelWriter Project Document

 novelWriter – Project Document
================================
 Class holding a single novelWriter document

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

from nw.constants import nwAlert
from nw.common import isHandle
from nw.constants import nwItemLayout, nwItemClass

logger = logging.getLogger(__name__)

class NWDoc():

    def __init__(self, theProject, theParent):

        self.theProject = theProject
        self.theParent  = theParent

        # Internal Variables
        self._theItem   = None # The currently open item
        self._docHandle = None # The handle of the currently open item
        self._fileLoc   = None # The file location of the currently open item
        self._docMeta   = {}   # The meta data of the currently open item

        # Internal Mapping
        self.makeAlert = self.theParent.makeAlert

        return

    ##
    #  Class Methods
    ##

    def clearDocument(self):
        """Clear the document contents.
        """
        self._theItem   = None
        self._docHandle = None
        self._fileLoc   = None
        self._docMeta   = {}
        return

    def openDocument(self, tHandle, showStatus=True, isOrphan=False):
        """Open a document from handle, capturing potential file system
        errors and parse meta data. If the document doesn't exist on
        disk, return an empty string. If something went wrong, return
        None.
        """
        if not isHandle(tHandle):
            return None

        # Always clear first, since the object will often be reused.
        self.clearDocument()

        self._docHandle = tHandle
        if not isOrphan:
            self._theItem = self.theProject.projTree[tHandle]
        else:
            self._theItem = None

        if self._theItem is None and not isOrphan:
            self.clearDocument()
            return None

        docFile = self._docHandle+".nwd"
        logger.debug("Opening document %s" % docFile)

        docPath = os.path.join(self.theProject.projContent, docFile)
        self._fileLoc = docPath

        theText = ""
        self._docMeta = {}
        if os.path.isfile(docPath):
            try:
                with open(docPath, mode="r", encoding="utf8") as inFile:

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
                self.makeAlert(["Failed to open document file.", str(e)], nwAlert.ERROR)
                # Note: Document must be cleared in case of an io error,
                # or else the auto-save or save will try to overwrite it
                # with an empty file. Return None to alert the caller.
                self.clearDocument()
                return None
        else:
            # The document file does not exist, so we assume it's a new
            # document and initialise an empty text string.
            logger.debug("The requested document does not exist.")
            return ""

        if showStatus and not isOrphan:
            self.theParent.setStatus("Opened Document: %s" % self._theItem.itemName)

        return theText

    def saveDocument(self, docText):
        """Save the document. The file is saved via a temp file in case
        of save failure. Returns True if successful, False if not.
        """
        if self._docHandle is None:
            return False

        self.theProject.ensureFolderStructure()

        docFile = self._docHandle+".nwd"
        logger.debug("Saving document %s" % docFile)

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
            with open(docTemp, mode="w", encoding="utf8") as outFile:
                outFile.write(docMeta)
                outFile.write(docText)
        except Exception as e:
            self.makeAlert(["Could not save document.", str(e)], nwAlert.ERROR)
            return False

        # If we're here, the file was successfully saved, so we can
        # replace the temp file with the actual file
        if os.path.isfile(docPath):
            os.unlink(docPath)
        os.rename(docTemp, docPath)

        if self._theItem is not None:
            self.theParent.setStatus("Saved Document: %s" % self._theItem.itemName)

        return True

    def deleteDocument(self, tHandle):
        """Permanently delete a document source file and related files
        from the project data folder.
        """
        if not isHandle(tHandle):
            return False

        docFile = tHandle+".nwd"

        chkList = []
        chkList.append(os.path.join(self.theProject.projContent, docFile))
        chkList.append(os.path.join(self.theProject.projContent, docFile+"~"))

        for chkFile in chkList:
            if os.path.isfile(chkFile):
                try:
                    os.unlink(chkFile)
                    logger.debug("Deleted: %s" % chkFile)
                except Exception as e:
                    self.makeAlert(["Could not delete document file.", str(e)], nwAlert.ERROR)
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
            logger.debug("Ignoring meta data: '%s'" % metaLine.strip())

        return

# END Class NWDoc
