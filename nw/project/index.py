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
        "todo","tag","pov","char","plot","time","location",
        "object","custom","scene","chapter","part"
    ]

    def __init__(self, theProject, theParent):

        # Internal
        self.theProject = theProject
        self.theParent  = theParent
        self.mainConf   = self.theParent.mainConf

        # Indices
        self.itemIndex  = {}
        self.tagIndex   = {}
        self.keyIndex   = {}
        for aKey in self.VALID_KEYS:
            self.keyIndex[aKey] = []

        return

    def saveIndex(self):

        indexFile = path.join(self.theProject.projMeta,nwFiles.INDEX_FILE)
        if self.mainConf.debugInfo:
            nIndent = 2
        else:
            nIndent = None
        try:
            with open(indexFile,mode="w+") as outFile:
                outFile.write(json.dumps({
                    "itemIndex" : self.itemIndex,
                    "tagIndex"  : self.tagIndex,
                    "keyIndex"  : self.keyIndex
                }, indent=nIndent))
        except Exception as e:
            logger.error("Failed to save index file")
            logger.error(str(e))
            return False

        return True

    def scanFile(self, tHandle):

        theDocument = NWDoc(self.theProject, self.theParent)
        theText = theDocument.openDocument(tHandle, False)
        theItem = self.theProject.getItem(tHandle)

        if theItem is None:
            return False

        if theItem.itemType != nwItemType.FILE:
            return False

        self.itemIndex[tHandle] = {}

        nLine = 0
        for aLine in theText.splitlines():
            aLine  = aLine.strip()
            nLine += 1
            nChar  = len(aLine)
            if nChar > 0 and aLine[0] == "@":
                self.indexThis(tHandle, aLine, nLine, theItem)

        # Generate reverse index
        for aKey in self.VALID_KEYS:
            if aKey in self.itemIndex[tHandle]:
                if len(self.itemIndex[tHandle][aKey]) > 0:
                    if tHandle not in self.keyIndex[aKey]:
                        self.keyIndex[aKey].append(tHandle)
                else:
                    if tHandle in self.keyIndex[aKey]:
                        self.keyIndex[aKey].remove(tHandle)

        return True

    def indexThis(self, tHandle, aLine, nLine, theItem):

        nChar = len(aLine)
        nPos  = aLine.find(":")
        if nPos < 2 or nChar < nPos+2:
            return False

        aKey = aLine[1:nPos].strip().lower()
        tVal = aLine[nPos+1:].strip()
        if aKey not in self.VALID_KEYS:
            return False

        if aKey == "todo":
            self._addItem(tHandle, aKey, nLine, tVal)
        elif aKey == "tag":
            if tVal.find(",") >- 0:
                return False
            self._addItem(tHandle, aKey, nLine, tVal)
            self.tagIndex[tVal] = [nLine, tHandle, theItem.itemClass.name]
        else:
            kVal = tVal.split(",")
            cVal = []            
            for aVal in kVal:
                cVal.append(aVal.strip().lower())
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
