# -*- coding: utf-8 -*-
"""novelWriter Project Document

 novelWriter – Project Document
================================
 Class holding a document

 File History:
 Created: 2018-09-29 [0.0.1]

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

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
from nw.constants import nwItemLayout, nwItemClass, nwConst

logger = logging.getLogger(__name__)

class NWDoc():

    def __init__(self, theProject, theParent):

        self.theProject = theProject
        self.theParent  = theParent

        # Internal Variables
        self._theItem   = None # The currently open item
        self._docHandle = None # The handle of the currently open item
        self._fileLoc   = None # The file location of the currently open item
        self._docMeta   = ""   # The meta string of the currently open item

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
        self._docMeta   = ""
        return

    def openDocument(self, tHandle, showStatus=True, isOrphan=False):
        """Open a document from handle, capturing potential file system
        errors and parse meta data.
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
        self._docMeta = ""
        if os.path.isfile(docPath):
            try:
                with open(docPath, mode="r", encoding="utf8") as inFile:
                    fstLine = inFile.readline()
                    if fstLine.startswith("%%~ "):
                        # This is the meta line
                        self._docMeta = fstLine[4:].strip()
                    else:
                        theText = fstLine
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

        logger.verbose("DocMeta: '%s'" % self._docMeta)

        if showStatus and not isOrphan:
            self.theParent.statusBar.setStatus("Opened Document: %s" % self._theItem.itemName)

        return theText

    def saveDocument(self, docText):
        """Save the document via temp file in case of save failure, and
        in any case keep a backup of the file.
        """
        if self._docHandle is None:
            return False

        self.theProject.ensureFolderStructure()

        docFile = self._docHandle+".nwd"
        logger.debug("Saving document %s" % docFile)

        docPath = os.path.join(self.theProject.projContent, docFile)
        docTemp = os.path.join(self.theProject.projContent, docFile+"~")

        if self._theItem is None:
            docMeta = ""
        else:
            itemPath = self.theProject.projTree.getItemPath(self._docHandle)
            docMeta = (
                "%%~ {handlepath:s}:{itemclass:s}:{itemlayout:s}:{itemname:s}\n"
            ).format(
                handlepath = ":".join(itemPath),
                itemclass  = self._theItem.itemClass.name,
                itemlayout = self._theItem.itemLayout.name,
                itemname   = self._theItem.itemName,
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

        self.theParent.statusBar.setStatus("Saved Document: %s" % self._theItem.itemName)

        return True

    def deleteDocument(self, tHandle):
        """Permanently delete a document source file and its backups
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
        if len(self._docMeta) < 14:
            # Not enough information
            return "", [], None, None

        theMeta = self._docMeta

        # Scan for handles
        thePath = []
        for n in range(nwConst.maxDepth + 5):
            if len(theMeta) < 14:
                break
            if theMeta[13] == ":":
                theHandle = theMeta[:13]
                if isHandle(theHandle):
                    thePath.append(theHandle)
                    theMeta = theMeta[14:]
                else:
                    break
            else:
                break

        theClass = nwItemClass.NO_CLASS
        for aClass in nwItemClass:
            if theMeta.startswith(aClass.name):
                theClass = aClass
                theMeta = theMeta[len(aClass.name)+1:]

        theLayout = nwItemLayout.NO_LAYOUT
        for aLayout in nwItemLayout:
            if theMeta.startswith(aLayout.name):
                theLayout = aLayout
                theMeta = theMeta[len(aLayout.name)+1:]

        return theMeta, thePath, theClass, theLayout

# END Class NWDoc
