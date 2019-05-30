# -*- coding: utf-8 -*-
"""novelWriter Project Index

 novelWriter – Project Index
=============================
 Class holding the index of tags

 File History:
 Created: 2019-05-27 [0.1.4]

Structure:

    We need to scan all files to get the novel layout. This is done by heading depth. Each heading
is recorded in a sorted list. Each such heading again can have a set of meta tags.
    In the other class root folders, each file can have a tag which the meta tags in the novel files
point to. These tags should be stored in a dictionary where the tag is the key pointing to a single
file handle. That way we can do lookups on both keys and values.
    The timeline view then consists of novel header elements in the horizontal header, possibly just
truncated to a Ch or Sc abbreviation, possibly with a number. This can be extracted from the item
layout. The vertical header column is then whatever notes we want to compare against, and the links
from the novel files are dots on the row.

"""

import logging
import json
import nw

from os                  import path

from nw.project.document import NWDoc
from nw.enum             import nwItemType, nwItemClass
from nw.constants        import nwFiles

logger = logging.getLogger(__name__)

class NWIndex():

    TAG_KEY    = "@tag"
    POV_KEY    = "@pov"
    CHAR_KEY   = "@char"
    PLOT_KEY   = "@plot"
    TIME_KEY   = "@time"
    WORLD_KEY  = "@location"
    OBJECT_KEY = "@object"
    CUSTOM_KEY = "@custom"

    NOTE_KEYS  = [TAG_KEY]
    NOVEL_KEYS = [PLOT_KEY, POV_KEY, CHAR_KEY, WORLD_KEY, TIME_KEY, OBJECT_KEY, CUSTOM_KEY]
    TAG_CLASS  = {
        POV_KEY    : nwItemClass.CHARACTER,
        CHAR_KEY   : nwItemClass.CHARACTER,
        PLOT_KEY   : nwItemClass.PLOT,
        TIME_KEY   : nwItemClass.TIMELINE,
        WORLD_KEY  : nwItemClass.WORLD,
        OBJECT_KEY : nwItemClass.OBJECT,
        CUSTOM_KEY : nwItemClass.CUSTOM,
    }

    def __init__(self, theProject, theParent):

        # Internal
        self.theProject = theProject
        self.theParent  = theParent
        self.mainConf   = self.theParent.mainConf

        # Indices
        self.tagIndex   = {}
        self.noteIndex  = {}
        self.novelIndex = {}

        return

    def clearIndex(self):
        self.tagIndex   = {}
        self.noteIndex  = {}
        self.novelIndex = {}
        return

    ##
    #  Load and Save Index to/from File
    ##

    def loadIndex(self):

        theData   = {}
        indexFile = path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)
        if path.isfile(indexFile):
            logger.debug("Loading index file")
            try:
                with open(indexFile,mode="r") as inFile:
                    theJson = inFile.read()
                theData = json.loads(theJson)
            except Exception as e:
                logger.error("Failed to load index file")
                logger.error(str(e))
                return False

            if "tagIndex" in theData.keys():
                self.tagIndex = theData["tagIndex"]
            if "noteIndex" in theData.keys():
                self.noteIndex = theData["noteIndex"]
            if "novelIndex" in theData.keys():
                self.novelIndex = theData["novelIndex"]

            return True

        return False

    def saveIndex(self):

        indexFile = path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)
        logger.debug("Saving index file")
        if self.mainConf.debugInfo:
            nIndent = 2
        else:
            nIndent = None
        try:
            with open(indexFile,mode="w+") as outFile:
                outFile.write(json.dumps({
                    "tagIndex"   : self.tagIndex,
                    "noteIndex"  : self.noteIndex,
                    "novelIndex" : self.novelIndex,
                }, indent=nIndent))
        except Exception as e:
            logger.error("Failed to save index file")
            logger.error(str(e))
            return False

        return True

    ##
    #  Index Building
    ##

    def scanText(self, tHandle, theText):

        theItem = self.theProject.getItem(tHandle)
        if theItem is None: return False
        if theItem.itemType != nwItemType.FILE: return False
        itemClass  = theItem.itemClass
        itemLayout = theItem.itemLayout

        logger.debug("Indexing item with handle %s" % tHandle)

        # Check file type, and reset its old index
        if itemClass == nwItemClass.NOVEL:
            self.novelIndex[tHandle] = []
            self.noteIndex[tHandle]  = []
            isNovel = True
        else:
            isNovel = False

        # Also clear references to file in tag index
        clearTags = []
        for aTag in self.tagIndex:
            if self.tagIndex[aTag][1] == tHandle:
                clearTags.append(aTag)
        for aTag in clearTags:
            self.tagIndex.pop(aTag)

        nLine = 0
        for aLine in theText.splitlines():
            aLine  = aLine.strip()
            nLine += 1
            nChar  = len(aLine)
            if nChar == 0: continue
            if aLine[0] == "#":
                if isNovel:
                    self.indexTitle(tHandle, aLine, nLine, itemLayout)
            elif aLine[0] == "@":
                if isNovel:
                    self.indexNoteRef(tHandle, aLine, nLine)
                else:
                    self.indexTag(tHandle, aLine, nLine, itemClass)

        return True

    def indexTitle(self, tHandle, aLine, nLine, itemLayout):

        if aLine.startswith("# "):
            hDepth = 1
            hText  = aLine[2:].strip()
        elif aLine.startswith("## "):
            hDepth = 2
            hText  = aLine[3:].strip()
        elif aLine.startswith("### "):
            hDepth = 3
            hText  = aLine[4:].strip()
        elif aLine.startswith("#### "):
            hDepth = 4
            hText  = aLine[5:].strip()
        else:
            return False

        if hText != "":
            self.novelIndex[tHandle].append([nLine, hDepth, hText, itemLayout.name])

        return True

    def indexNoteRef(self, tHandle, aLine, nLine):

        isValid, theBits, thePos = self.scanThis(aLine)
        if not isValid or len(theBits) == 0:
            return False

        theKey = theBits[0]
        if theKey in self.NOVEL_KEYS:
            for aVal in theBits[1:]:
                self.noteIndex[tHandle].append([nLine, theKey, aVal])

        return True

    def indexTag(self, tHandle, aLine, nLine, itemClass):

        isValid, theBits, thePos = self.scanThis(aLine)
        if not isValid or len(theBits) != 2:
            return False

        if theBits[0] == self.TAG_KEY:
            self.tagIndex[theBits[1]] = [nLine, tHandle, itemClass.name]

        return True

    def scanThis(self, aLine):

        theBits = []
        thePos  = []

        aLine = aLine.strip()
        nChar = len(aLine)
        if nChar < 2:
            return False, theBits, thePos
        if aLine[0] != "@":
            return False, theBits, thePos

        cPos = 0
        cKey, cSep, cVals = aLine.partition(":")
        sKey = cKey.strip()
        if sKey == "@":
            return False, theBits, thePos

        theBits.append(sKey)
        thePos.append(cPos)
        cPos += len(sKey) + 1

        if cVals == "":
            # No values, so we're done
            return True, theBits, thePos

        aVals = cVals.split(",")
        for cVal in aVals:
            sVal = cVal.strip()
            rLen = len(cVal.lstrip())
            tLen = len(cVal)
            theBits.append(sVal)
            thePos.append(cPos+tLen-rLen)
            cPos += tLen + 1

        return True, theBits, thePos

    def checkThese(self, theBits, tItem):

        nBits  = len(theBits)
        isGood = [False]*nBits
        if nBits == 0:
            return []

        # If we have a tag, the first value is always OK, rest is ignored
        if theBits[0] == self.TAG_KEY and nBits > 1:
            isGood[0] = True
            if theBits[1] in self.tagIndex.keys():
                if self.tagIndex[theBits[1]][1] == tItem.itemHandle:
                    isGood[1] = True
                else:
                    isGood[1] = False
            else:
                isGood[1] = True
            return isGood

        # If we're still here, we better check the references
        if tItem.itemClass == nwItemClass.NOVEL:
            isGood[0] = theBits[0] in self.NOVEL_KEYS
        else:
            isGood[0] = theBits[0] in self.NOTE_KEYS
        if not isGood[0] or nBits == 1:
            return isGood

        for n in range(1,nBits):
            if theBits[n] in self.tagIndex:
                isGood[n] = self.TAG_CLASS[theBits[0]].name == self.tagIndex[theBits[n]][2]

        return isGood

# END Class NWIndex
