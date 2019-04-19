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

    def __init__(self, theProject):

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.docHandle  = None
        self.theItem    = None

        return

    def openDocument(self, tHandle):

        self.docHandle = tHandle
        self.theItem   = self.theProject.getItem(tHandle)

        docDir, docFile = self._assemblePath(self.FILE_MN)
        logger.debug("Opening document %s" % path.join(docDir,docFile))
        dataDir = path.join(self.theProject.projPath, docDir)
        docPath = path.join(dataDir, docFile)

        if path.isfile(docPath):
            with open(docPath,mode="r") as inFile:
                return inFile.read()
        else:
            logger.debug("The requested document does not exist.")
            return ""

        return None

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

        with open(docPath,mode="w") as outFile:
            outFile.write(docText)

        if path.isfile(docTemp): unlink(docTemp)

        docAna = TextAnalysis(docText,"en_GB")
        wC, sC, pC = docAna.getStats()

        self.theItem.setWordCount(wC)
        self.theItem.setSentCount(sC)
        self.theItem.setParaCount(pC)

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
