# -*- coding: utf-8 -*-
"""novelWriter Project Document

 novelWriter – Project Document
================================
 Class holding a document

 File History:
 Created: 2018-09-29 [0.0.1]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import nw

from os import path, mkdir, rename, unlink

from nw.constants import nwAlert
from nw.common import isHandle

logger = logging.getLogger(__name__)

class NWDoc():

    def __init__(self, theProject, theParent):

        self.mainConf    = nw.CONFIG
        self.theProject  = theProject
        self.theParent   = theParent
        self.theItem     = None
        self.docHandle   = None
        self.docEditable = False
        self.fileLoc     = None
        self.docMeta     = ""

        # Internal Mapping
        self.makeAlert = self.theParent.makeAlert

        return

    ##
    #  Class Methods
    ##

    def clearDocument(self):
        """Clear the document contents.
        """
        self.theItem     = None
        self.docHandle   = None
        self.docEditable = False
        self.fileLoc     = None
        self.docMeta     = ""
        return

    def openDocument(self, tHandle, showStatus=True, isOrphan=False):
        """Open a document from handle, capturing potential file system
        errors and parse meta data.
        """
        if not isHandle(tHandle):
            return None

        # Always clear first, since the object will often be reused.
        self.clearDocument()

        self.docHandle = tHandle
        if not isOrphan:
            self.theItem = self.theProject.projTree[tHandle]
        else:
            self.theItem = None

        if self.theItem is None and not isOrphan:
            self.clearDocument()
            return None

        # By default, the document is editable.
        # Except for files in the trash folder.
        self.docEditable = True
        if self.theItem is not None:
            if self.theItem.parHandle == self.theProject.projTree.trashRoot():
                self.docEditable = False

        docFile = self.docHandle+".nwd"
        logger.debug("Opening document %s" % docFile)

        docPath = path.join(self.theProject.projContent, docFile)
        self.fileLoc = docPath

        theText = ""
        self.docMeta = ""
        if path.isfile(docPath):
            try:
                with open(docPath, mode="r", encoding="utf8") as inFile:
                    fstLine = inFile.readline()
                    if fstLine.startswith("%%~ "):
                        # This is the meta line
                        self.docMeta = fstLine[4:].strip()
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

        logger.verbose("DocMeta: '%s'" % self.docMeta)

        if showStatus and not isOrphan:
            self.theParent.statusBar.setStatus("Opened Document: %s" % self.theItem.itemName)

        return theText

    def saveDocument(self, docText):
        """Save the document via temp file in case of save failure, and
        in any case keep a backup of the file.
        """
        if self.docHandle is None or not self.docEditable:
            return False

        self.theProject.ensureFolderStructure()

        docFile = self.docHandle+".nwd"
        logger.debug("Saving document %s" % docFile)

        docPath = path.join(self.theProject.projContent, docFile)
        docTemp = path.join(self.theProject.projContent, docFile+"~")

        itemPath = self.theProject.projTree.getItemPath(self.docHandle)
        docMeta  = "%%~ "+":".join(itemPath)+":"+self.theItem.itemName+"\n"

        try:
            with open(docTemp, mode="w", encoding="utf8") as outFile:
                outFile.write(docMeta)
                outFile.write(docText)
        except Exception as e:
            self.makeAlert(["Could not save document.", str(e)], nwAlert.ERROR)
            return False

        # If we're here, the file was successfully saved, so we can
        # replace the temp file with the actual file
        if path.isfile(docPath):
            unlink(docPath)
        rename(docTemp, docPath)

        self.theParent.statusBar.setStatus("Saved Document: %s" % self.theItem.itemName)

        return True

    def deleteDocument(self, tHandle):
        """Permanently delete a document source file and its backups
        from the project data folder.
        """
        if not isHandle(tHandle):
            return False

        docFile = tHandle+".nwd"

        chkList = []
        chkList.append(path.join(self.theProject.projContent, docFile))
        chkList.append(path.join(self.theProject.projContent, docFile+"~"))

        for chkFile in chkList:
            if path.isfile(chkFile):
                try:
                    unlink(chkFile)
                    logger.debug("Deleted: %s" % chkFile)
                except Exception as e:
                    self.makeAlert(["Could not delete document file.",str(e)], nwAlert.ERROR)
                    return False

        return True

    ##
    #  Getters
    ##

    def getMeta(self):
        """Parses the document meta tag and returns the path and name as
        a list and a string.
        """
        if len(self.docMeta) < 14:
            # Not enough information
            return "", []

        theMeta = self.docMeta

        # Scan for handles
        thePath = []
        for n in range(200):
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

        return theMeta, thePath

# END Class NWDoc
