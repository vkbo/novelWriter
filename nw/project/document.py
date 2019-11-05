# -*- coding: utf-8 -*-
"""novelWriter Project Document

 novelWriter – Project Document
================================
 Class holding a document

 File History:
 Created: 2018-09-29 [0.0.1]

"""

import logging
import nw

from os import path, mkdir, rename, unlink

from nw.constants import nwAlert

logger = logging.getLogger(__name__)

class NWDoc():

    FILE_MN = "main.nwd"

    def __init__(self, theProject, theParent):

        self.mainConf    = nw.CONFIG
        self.theProject  = theProject
        self.theParent   = theParent
        self.theItem     = None
        self.docHandle   = None
        self.docEditable = False
        self.fileLoc     = None

        # Internal Mapping
        self.makeAlert = self.theParent.makeAlert

        return

    def clearDocument(self):
        self.theItem     = None
        self.docHandle   = None
        self.docEditable = False
        return

    def openDocument(self, tHandle, showStatus=True):

        self.docHandle = tHandle
        self.theItem   = self.theProject.getItem(tHandle)

        if self.theItem is None:
            self.clearDocument()
            return None

        # By default, the document is editable.
        # Except for files in the trash folder.
        self.docEditable = True
        if self.theItem.parHandle == self.theProject.trashRoot:
            self.docEditable = False

        docDir, docFile = self._assemblePath(self.FILE_MN)
        self.fileLoc = path.join(docDir,docFile)
        logger.debug("Opening document %s" % self.fileLoc)
        dataDir = path.join(self.theProject.projPath, docDir)
        docPath = path.join(dataDir, docFile)

        if path.isfile(docPath):
            try:
                with open(docPath,mode="r",encoding="utf8") as inFile:
                    theDoc = inFile.read()
            except Exception as e:
                self.makeAlert(["Failed to open document file.",str(e)], nwAlert.ERROR)
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

        if showStatus:
            self.theParent.statusBar.setStatus("Opened Document: %s" % self.theItem.itemName)

        return theDoc

    def saveDocument(self, docText):

        if self.docHandle is None or not self.docEditable:
            return False

        docDir, docFile = self._assemblePath(self.FILE_MN)
        logger.debug("Saving document %s" % path.join(docDir,docFile))
        dataPath = path.join(self.theProject.projPath, docDir)
        docPath  = path.join(dataPath, docFile)
        if not path.isdir(dataPath):
            mkdir(dataPath)
            logger.debug("Created folder %s" % dataPath)

        docTemp = path.join(dataPath,docFile[:-3]+"tmp")
        docBack = path.join(dataPath,docFile[:-3]+"bak")

        if path.isfile(docTemp):
            unlink(docTemp)
        if path.isfile(docBack):
            rename(docBack,docTemp)
        if path.isfile(docPath):
            rename(docPath,docBack)

        try:
            with open(docPath,mode="w",encoding="utf8") as outFile:
                outFile.write(docText)
        except Exception as e:
            self.makeAlert(["Could not save document.",str(e)], nwAlert.ERROR)
            return False

        if path.isfile(docTemp):
            unlink(docTemp)

        self.theParent.statusBar.setStatus("Saved Document: %s" % self.theItem.itemName)

        return True

    ##
    #  Internal Functions
    ##

    def _assemblePath(self, docExt):
        if self.docHandle is None:
            return None
        docDir  = "data_"+self.docHandle[0]
        docFile = self.docHandle[1:13]+"_"+docExt
        return docDir, docFile

# END Class NWDoc
