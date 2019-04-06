# -*- coding: utf-8 -*
"""novelWriter Project Document

 novelWriter – Project Document
================================
 Class holding a document

 File History:
 Created: 2018-09-29 [0.0.1]

"""

import logging
import nw

from os import path, mkdir
from lxml import etree, html

logger = logging.getLogger(__name__)

class NWDoc():

    FILE_MN = "main.md"

    def __init__(self, theProject):

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.docHandle  = None

        return

    def openDocument(self, tHandle):
        self.docHandle = tHandle
        docDir, docFile = self._assemblePath(self.FILE_MN)
        logger.debug("Opening document %s" % path.join(docDir,docFile))
        dataDir = path.join(self.theProject.projPath, docDir)
        docPath = path.join(dataDir, docFile)
        if path.isfile(docPath):
            with open(docPath,mode="r") as inFile:
                return inFile.read()
        else:
            logger.debug("Document does not exist.")
            return ""
        return None

    def saveDocument(self, docHtml):
        if self.docHandle is None: return False
        docDir, docFile = self._assemblePath(self.FILE_MN)
        logger.debug("Saving document %s" % path.join(docDir,docFile))
        dataDir = path.join(self.theProject.projPath, docDir)
        docPath = path.join(dataDir, docFile)
        if not path.isdir(dataDir):
            mkdir(dataDir)
            logger.debug("Created folder %s" % dataDir)
        with open(docPath,mode="w") as outFile:
            outFile.write(docHtml)
            # docData = html.fromstring(docHtml)
            # outFile.write(html.tostring(
            #     docData,
            #     pretty_print = True,
            #     encoding     = "utf-8",
            #     method       = "html",
            # ))
        return True

    def _assemblePath(self, docExt):
        if self.docHandle is None: return None
        docDir  = "data_"+self.docHandle[0]
        docFile = self.docHandle[1:13]+"_"+docExt
        return docDir, docFile

# END Class NWDoc
