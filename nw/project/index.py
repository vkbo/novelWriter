# -*- coding: utf-8 -*-
"""novelWriter Project Index

 novelWriter – Project Index
=============================
 Class holding the index of tags

 File History:
 Created: 2019-05-27 [0.1.4]

"""

import logging
import json
import nw

from os                  import path

from nw.project.document import NWDoc
from nw.enum             import nwItemType
from nw.constants        import nwFiles

logger = logging.getLogger(__name__)

class NWIndex():

    VALID_KEYS = [
        "todo","tag","pov","chars","plot","time","location",
        "object","custom","scene","chapter","part"
    ]

    def __init__(self, theProject, theParent):

        # Internal
        self.theProject = theProject
        self.theParent  = theParent
        self.mainConf   = self.theParent.mainConf

        # Indices
        self.itemIndex  = {}

        return

    def clearIndex(self):
        self.itemIndex  = {}
        return

    def loadIndex(self):

        indexFile = path.join(self.theProject.projMeta,nwFiles.INDEX_FILE)
        if path.isfile(indexFile):
            logger.debug("Loading index file")
            try:
                with open(indexFile,mode="r") as inFile:
                    theJson = inFile.read()
                self.itemIndex = json.loads(theJson)
            except Exception as e:
                logger.error("Failed to load index file")
                logger.error(str(e))
                return False

            return True

        return False

    def saveIndex(self):

        indexFile = path.join(self.theProject.projMeta,nwFiles.INDEX_FILE)
        logger.debug("Saving index file")
        if self.mainConf.debugInfo:
            nIndent = 2
        else:
            nIndent = None
        try:
            with open(indexFile,mode="w+") as outFile:
                outFile.write(json.dumps(self.itemIndex, indent=nIndent))
        except Exception as e:
            logger.error("Failed to save index file")
            logger.error(str(e))
            return False

        return True

    def scanFile(self, tHandle):

        theItem = self.theProject.getItem(tHandle)
        if theItem is None:
            return False
        if theItem.itemType != nwItemType.FILE:
            return False

        theDocument = NWDoc(self.theProject, self.theParent)
        theText = theDocument.openDocument(tHandle, False)

        self.scanText(tHandle, theText)

        return

    def scanText(self, tHandle, theText):

        theItem = self.theProject.getItem(tHandle)
        if theItem is None:
            return False
        if theItem.itemType != nwItemType.FILE:
            return False

        logger.debug("Indexing item with handle %s" % tHandle)

        self.itemIndex[tHandle] = {}

        nLine = 0
        for aLine in theText.splitlines():
            aLine  = aLine.strip()
            nLine += 1
            nChar  = len(aLine)
            if nChar > 0 and aLine[0] == "@":
                self.indexThis(tHandle, aLine, nLine, theItem)

        return True

    def indexThis(self, tHandle, aLine, nLine, theItem):

        nChar = len(aLine)
        nPos  = aLine.find(":")
        if nPos < 2 or nChar < nPos+2:
            return False

        aKey = aLine[1:nPos].strip().lower()
        tVal = aLine[nPos+1:].strip().lower()
        if aKey not in self.VALID_KEYS:
            logger.verbose("Not a valid key '%s'" % aKey)
            return False

        logger.verbose("Found valid key '%s'" % aKey)
        if aKey == "todo":
            self._addItem(tHandle, aKey, nLine, tVal)
        elif aKey == "tag":
            if tVal.find(",") >- 0:
                return False
            self._addItem(tHandle, aKey, nLine, tVal)
        else:
            kVal = tVal.split(",")
            cVal = [aVal.strip() for aVal in kVal]
            if len(cVal) > 0:
                self._addItem(tHandle, aKey, nLine, cVal)
            else:
                return False

        return True

    ##
    #  Internal Functions
    ##

    def _addItem(self, tHandle, tKey, tLine, tVal):
        if tKey not in self.itemIndex[tHandle].keys():
            self.itemIndex[tHandle][tKey] = []
        self.itemIndex[tHandle][tKey].append([tLine, tVal])
        return

# END Class NWIndex
