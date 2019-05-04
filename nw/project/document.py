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

from nw.tools.analyse import TextAnalysis

logger = logging.getLogger(__name__)

class NWDoc():

    FILE_MN = "main.nwd"

    def __init__(self, theProject, theParent):

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.theItem    = None
        self.docHandle  = None

        return

    def openDocument(self, tHandle):

        self.docHandle = tHandle
        self.theItem   = self.theProject.getItem(tHandle)
        self.theParent.statusBar.setDocHandleCount(tHandle)

        docDir, docFile = self._assemblePath(self.FILE_MN)
        logger.debug("Opening document %s" % path.join(docDir,docFile))
        dataDir = path.join(self.theProject.projPath, docDir)
        docPath = path.join(dataDir, docFile)

        if path.isfile(docPath):
            try:
                with open(docPath,mode="r") as inFile:
                    theDoc = inFile.read()
            except Exception as e:
                self.theParent.makeAlert(["Failed to open document file.",str(e)],2)
                return ""
        else:
            logger.debug("The requested document does not exist.")
            return ""

        self.theParent.statusBar.setStatus("Opened Document: %s" % self.theItem.itemName)

        return theDoc

    def saveDocument(self, docText):

        if self.docHandle is None:
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

        if path.isfile(docTemp): unlink(docTemp)
        if path.isfile(docBack): rename(docBack,docTemp)
        if path.isfile(docPath): rename(docPath,docBack)

        try:
            with open(docPath,mode="w") as outFile:
                outFile.write(docText)
        except Exception as e:
            self.theParent.makeAlert(["Could not save document.",str(e)],2)
            return False

        if path.isfile(docTemp): unlink(docTemp)

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
