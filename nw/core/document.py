# -*- coding: utf-8 -*-
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

import nw
import logging
import shutil
import time
import os

from nw.enum import nwItemLayout, nwItemClass
from nw.common import (
    isHandle, safeMakeDir, safeUnlink, formatTimeStamp, parseTimeStamp
)

logger = logging.getLogger(__name__)

class NWDoc():

    def __init__(self, theProject, theHandle):

        self.theProject = theProject

        # Internal Variables
        self._theItem   = None # The currently open item
        self._docHandle = None # The handle of the currently open item
        self._fileLoc   = None # The file location of the currently open item
        self._docMeta   = {}   # The meta data of the currently open item
        self._docError  = ""   # The latest encountered IO error

        if isHandle(theHandle):
            self._docHandle = theHandle

        if self._docHandle is not None:
            self._theItem = self.theProject.projTree[theHandle]

        return

    ##
    #  Class Methods
    ##

    def readDocument(self, isOrphan=False, sessCopy=False, versionSuffix=None):
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

        if versionSuffix is None:
            docFile = "%s.nwd" % self._docHandle
            docBase = self.theProject.projContent
        else:
            docFile = "%s_%s.nwd" % (self._docHandle, versionSuffix)
            docBase = os.path.join(self.theProject.projVers, self._docHandle)
            safeMakeDir(docBase)

        docPath = os.path.join(docBase, docFile)
        self._fileLoc = docPath

        logger.debug("Opening document: %s" % docFile)

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
                self._docError = str(e)
                return None

        else:
            # The document file does not exist, so we assume it's a new
            # document and initialise an empty text string.
            logger.debug("The requested document does not exist.")
            return ""

        # If requested, also make a copy of the document, for the
        # current session only. This will only be done once per session.
        if sessCopy and not isOrphan and versionSuffix is None:
            if not self._theItem.sessionBak:
                bakFile = "%s.bak" % self._docHandle
                bakPath = os.path.join(docBase, bakFile)
                safeUnlink(bakPath)
                shutil.copy2(docPath, bakPath)
                logger.debug("Created session backup: %s" % bakFile)
                self._theItem.setSessionBackup(True)

        return theText

    def writeDocument(self, docText, versionSuffix=None, metaTime=0, metaNote=""):
        """Write the document. The file is saved via a temp file in case
        of save failure. Returns True if successful, False if not.
        """
        self._docError = ""
        if self._docHandle is None:
            logger.error("No document handle set")
            return False

        self.theProject.ensureFolderStructure()

        if versionSuffix is None:
            docFile = "%s.nwd" % self._docHandle
            docBase = self.theProject.projContent
        else:
            docFile = "%s_%s.nwd" % (self._docHandle, versionSuffix)
            docBase = os.path.join(self.theProject.projVers, self._docHandle)
            safeMakeDir(docBase)

        docPath = os.path.join(docBase, docFile)
        docTemp = os.path.join(docBase, docFile+"~")

        logger.debug("Saving document: %s" % docFile)

        # DocMeta line
        if self._theItem is None:
            docMeta = ""
        else:
            docMeta = (
                f"%%~name: {self._theItem.itemName}\n"
                f"%%~path: {self._theItem.itemParent}/{self._theItem.itemHandle}\n"
                f"%%~kind: {self._theItem.itemClass.name}/{self._theItem.itemLayout.name}\n"
            )
            if versionSuffix is not None:
                docMeta += (
                    f"%%~sess: {self.theProject.sessionID}/{formatTimeStamp(int(metaTime))}\n"
                    f"%%~note: {str(metaNote)}\n"
                )

        try:
            with open(docTemp, mode="w", encoding="utf8") as outFile:
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
                    logger.debug("Deleted: %s" % chkFile)
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
        """Returns the standard document meta tags.
        """
        theName = self._docMeta.get("name", "")
        theParent = self._docMeta.get("parent", None)
        theClass = self._docMeta.get("class", None)
        theLayout = self._docMeta.get("layout", None)

        return theName, theParent, theClass, theLayout

    def getVersionMeta(self):
        """Returns the versioned document meta tags.
        """
        sessID = self._docMeta.get("sessionID", "")
        versTime = self._docMeta.get("versionTime", 0.0)
        versNote = self._docMeta.get("versionNote", "")
        return sessID, versTime, versNote

    def getError(self):
        """Return the last recorded exception.
        """
        return self._docError

    ##
    #  Versioning
    ##

    def listVersions(self):
        """List all versions of the document in the versions folder.
        """
        theList = []

        # Assemble the version folder for the document
        versionPath = os.path.join(self.theProject.projVers, self._docHandle)
        if not os.path.isdir(versionPath):
            return theList

        dataFile = os.path.join(versionPath, "versions.dat")
        if not os.path.isfile(dataFile):
            return theList

        try:
            with open(dataFile, mode="r", encoding="utf-8") as inFIle:
                for aLine in inFIle.readlines():
                    aLine = aLine.strip()
                    if len(aLine) < 32:
                        continue
                    versName = aLine[0:11]
                    versDate = parseTimeStamp(aLine[13:32], 0.0)
                    versNote = aLine[34:]
                    theList.append((versName, versDate, versNote))

        except Exception:
            logger.error("Failed to parse versions file")
            nw.logException()
            self.rebuildVersions()
            return theList

        logger.debug("Found %d version(s) of document %s" % (len(theList), self._docHandle))

        return theList

    def rebuildVersions(self):
        """Rebuild the versins file.
        """
        versionPath = os.path.join(self.theProject.projVers, self._docHandle)
        dataFile = os.path.join(versionPath, "versions.dat")
        if os.path.isfile(dataFile):
            safeUnlink(dataFile)

        versData = ""
        versCount = 0
        for aFile in os.listdir(versionPath):
            docPath = os.path.join(versionPath, aFile)

            # Check the entries, and reject anything that seems wrong
            if not os.path.isfile(docPath):
                continue
            if not aFile.startswith(self._docHandle+"_"):
                continue
            if not len(aFile) == 29:
                continue
            versSuffix = aFile[14:25]
            if len(versSuffix) != 11:
                continue
            if versSuffix[8] != "_":
                continue

            docText = self.readDocument(versionSuffix=versSuffix)
            if docText is None:
                continue

            _, vT, vN = self.getVersionMeta()
            versData += "%11s  %19s  %s\n" % (
                versSuffix, formatTimeStamp(vT), str(vN)
            )
            versCount += 1

        with open(dataFile, mode="w", encoding="utf8") as outFile:
            outFile.write(versData)

        logger.debug("Recreated %d records in %s/versions.dat" % (versCount, self._docHandle))

        return True

    def savePermanentVersion(self, theMessage):
        """Save a permament version file with a message.
        """
        self.theProject.ensureFolderStructure()

        # Assemble the version folder for the document
        versionPath = os.path.join(self.theProject.projVers, self._docHandle)
        if not safeMakeDir(versionPath):
            return False

        sessID   = self.theProject.sessionID
        dataFile = os.path.join(versionPath, "versions.dat")
        metaTime = time.time()

        versFile = None
        versNum  = 0
        for nItt in range(100):
            versFile = os.path.join(versionPath, "%13s_%8s_%02d.nwd" % (
                self._docHandle, sessID, nItt
            ))
            if not os.path.isfile(versFile):
                versNum = nItt
                break

        if versFile is None:
            logger.error("Failed to generate unique version file name")
            return False

        versionSuffix = "%8s_%02d" % (sessID, versNum)
        docText = self.readDocument()
        if docText:
            wrStatus = self.writeDocument(
                docText,
                versionSuffix=versionSuffix,
                metaTime=metaTime,
                metaNote=str(theMessage)
            )
            if wrStatus:
                try:
                    with open(dataFile, mode="a+", encoding="utf8") as outFile:
                        outFile.write("%11s  %19s  %s\n" % (
                            versionSuffix, formatTimeStamp(metaTime), str(theMessage)
                        ))
                    logger.debug("Saved version file for %s" % self._docHandle)

                except Exception:
                    logger.error("Failed to save version file: %s" % versFile)
                    nw.logException()
                    return False

        return True

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

        elif metaLine.startswith("%%~sess:"):
            metaVal = metaLine[8:].strip()
            metaBits = metaVal.split("/")
            if len(metaBits) == 2:
                if isHandle(metaBits[0]):
                    self._docMeta["sessionID"] = metaBits[0]
                self._docMeta["versionTime"] = parseTimeStamp(metaBits[1], 0.0)

        elif metaLine.startswith("%%~note:"):
            self._docMeta["versionNote"] = metaLine[8:].strip()

        else:
            logger.debug("Ignoring meta data: '%s'" % metaLine.strip())

        return

# END Class NWDoc
