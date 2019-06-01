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
        CHAR_KEY   : [nwItemClass.CHARACTER, 1],
        POV_KEY    : [nwItemClass.CHARACTER, 2],
        PLOT_KEY   : [nwItemClass.PLOT,      1],
        TIME_KEY   : [nwItemClass.TIMELINE,  1],
        WORLD_KEY  : [nwItemClass.WORLD,     1],
        OBJECT_KEY : [nwItemClass.OBJECT,    1],
        CUSTOM_KEY : [nwItemClass.CUSTOM,    1],
    }

    def __init__(self, theProject, theParent):

        # Internal
        self.theProject = theProject
        self.theParent  = theParent
        self.mainConf   = self.theParent.mainConf

        # Indices
        self.tagIndex   = {}
        self.refIndex   = {}
        self.novelIndex = {}

        # Lists
        self.novelList  = []

        return

    def clearIndex(self):
        self.tagIndex   = {}
        self.refIndex   = {}
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
            if "refIndex" in theData.keys():
                self.refIndex = theData["refIndex"]
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
                    "refIndex"   : self.refIndex,
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
            self.refIndex[tHandle]   = []
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

        nLine  = 0
        nTitle = 0
        for aLine in theText.splitlines():
            aLine  = aLine.strip()
            nLine += 1
            nChar  = len(aLine)
            if nChar == 0: continue
            if aLine[0] == "#":
                if isNovel:
                    isTitle = self.indexTitle(tHandle, aLine, nLine, itemLayout)
                    if isTitle:
                        nTitle = nLine
            elif aLine[0] == "@":
                if isNovel:
                    self.indexNoteRef(tHandle, aLine, nLine, nTitle)
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

    def indexNoteRef(self, tHandle, aLine, nLine, nTitle):

        isValid, theBits, thePos = self.scanThis(aLine)
        if not isValid or len(theBits) == 0:
            return False

        theKey = theBits[0]
        if theKey in self.NOVEL_KEYS:
            for aVal in theBits[1:]:
                self.refIndex[tHandle].append([nLine, theKey, aVal, nTitle])

        return True

    def indexTag(self, tHandle, aLine, nLine, itemClass):

        isValid, theBits, thePos = self.scanThis(aLine)
        if not isValid or len(theBits) != 2:
            return False

        if theBits[0] == self.TAG_KEY:
            self.tagIndex[theBits[1]] = [nLine, tHandle, itemClass.name]

        return True

    ##
    #  Check @ Lines
    ##

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

        # If we have a tag, only the first value is accepted, the rest is ignored
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

        # If we're still here, we better check that the references exist
        if tItem.itemClass == nwItemClass.NOVEL:
            isGood[0] = theBits[0] in self.NOVEL_KEYS
        else:
            isGood[0] = theBits[0] in self.NOTE_KEYS
        if not isGood[0] or nBits == 1:
            return isGood

        for n in range(1,nBits):
            if theBits[n] in self.tagIndex:
                isGood[n] = self.TAG_CLASS[theBits[0]][0].name == self.tagIndex[theBits[n]][2]

        return isGood

    ##
    #  Extract Data
    ##

    def buildNovelList(self):

        self.novelList  = []
        self.novelOrder = []
        for tHandle in self.theProject.treeOrder:
            if tHandle not in self.novelIndex:
                continue
            for tEntry in self.novelIndex[tHandle]:
                self.novelList.append(tEntry)
                self.novelOrder.append("%s:%d" % (tHandle,tEntry[0]))

        return True

    def buildTagNovelMap(self, theTags):

        tagMap   = {}
        tagClass = {}

        for theTag in theTags:
            tagMap[theTag] = [0]*len(self.novelOrder)
            try:
                tagClass[theTag] = nwItemClass[self.tagIndex[theTag][2]]
            except:
                logger.error("Could not map '%s' to nwItemClass" % self.tagIndex[theTag][2])
                tagClass[theTag] = None

        for tHandle in self.refIndex:
            for nLine, tKey, tTag, nTitle in self.refIndex[tHandle]:
                if tTag in tagMap.keys() and tKey in self.TAG_CLASS:
                    try:
                        nPos = self.novelOrder.index("%s:%d" % (tHandle, nTitle))
                        if self.TAG_CLASS[tKey][0] == tagClass[tTag]:
                            tagMap[tTag][nPos] = self.TAG_CLASS[tKey][1]
                    except:
                        logger.error("Could not find '%s:%d' in novelOrder" % (tHandle, nTitle))

        return tagMap

# END Class NWIndex
