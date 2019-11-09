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

from os import path

from nw.constants import (
    nwFiles, nwKeyWords, nwItemType, nwItemClass, nwAlert
)

logger = logging.getLogger(__name__)

class NWIndex():

    VALID_KEYS = [
        nwKeyWords.TAG_KEY,
        nwKeyWords.PLOT_KEY,
        nwKeyWords.POV_KEY,
        nwKeyWords.CHAR_KEY,
        nwKeyWords.WORLD_KEY,
        nwKeyWords.TIME_KEY,
        nwKeyWords.OBJECT_KEY,
        nwKeyWords.ENTITY_KEY,
        nwKeyWords.CUSTOM_KEY
    ]
    TAG_CLASS  = {
        nwKeyWords.CHAR_KEY   : [nwItemClass.CHARACTER, 1],
        nwKeyWords.POV_KEY    : [nwItemClass.CHARACTER, 2],
        nwKeyWords.PLOT_KEY   : [nwItemClass.PLOT,      1],
        nwKeyWords.TIME_KEY   : [nwItemClass.TIMELINE,  1],
        nwKeyWords.WORLD_KEY  : [nwItemClass.WORLD,     1],
        nwKeyWords.OBJECT_KEY : [nwItemClass.OBJECT,    1],
        nwKeyWords.ENTITY_KEY : [nwItemClass.ENTITY,    1],
        nwKeyWords.CUSTOM_KEY : [nwItemClass.CUSTOM,    1],
    }

    def __init__(self, theProject, theParent):

        # Internal
        self.theProject  = theProject
        self.theParent   = theParent
        self.mainConf    = self.theParent.mainConf
        self.indexBroken = False

        # Indices
        self.tagIndex   = {}
        self.refIndex   = {}
        self.novelIndex = {}
        self.noteIndex  = {}

        # Lists
        self.novelList = []

        return

    ##
    #  Public Methods
    ##

    def clearIndex(self):
        self.tagIndex   = {}
        self.refIndex   = {}
        self.novelIndex = {}
        self.noteIndex  = {}
        return

    def deleteHandle(self, tHandle):

        delTags = []
        for tTag in self.tagIndex:
            if self.tagIndex[tTag][1] == tHandle:
                delTags.append(tTag)

        for tTag in delTags:
            self.tagIndex.pop(tTag, None)

        self.refIndex.pop(tHandle, None)
        self.novelIndex.pop(tHandle, None)
        self.noteIndex.pop(tHandle, None)

        return

    ##
    #  Load and Save Index to/from File
    ##

    def loadIndex(self):
        """Load index from last session from the project meta folder.
        """

        theData = {}
        indexFile = path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)
        if path.isfile(indexFile):
            logger.debug("Loading index file")
            try:
                with open(indexFile,mode="r",encoding="utf8") as inFile:
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
            if "noteIndex" in theData.keys():
                self.noteIndex = theData["noteIndex"]

            self.checkIndex()

            return True

        return False

    def saveIndex(self):
        """Save the current index as a json file in the project meta
        folder.
        """

        indexFile = path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)
        logger.debug("Saving index file")
        if self.mainConf.debugInfo:
            nIndent = 2
        else:
            nIndent = None
        try:
            with open(indexFile,mode="w+",encoding="utf8") as outFile:
                outFile.write(json.dumps({
                    "tagIndex"   : self.tagIndex,
                    "refIndex"   : self.refIndex,
                    "novelIndex" : self.novelIndex,
                    "noteIndex"  : self.noteIndex,
                }, indent=nIndent))
        except Exception as e:
            logger.error("Failed to save index file")
            logger.error(str(e))
            return False

        return True

    def checkIndex(self):
        """Check that the entries in the index are valid and contain the
        elements it should.
        """

        self.indexBroken = False

        for tTag in self.tagIndex:
            if len(self.tagIndex[tTag]) != 3:
                self.indexBroken = True

        for tHandle in self.refIndex:
            for tEntry in self.refIndex[tHandle]:
                if len(tEntry) != 4:
                    self.indexBroken = True

        for tHandle in self.novelIndex:
            for tEntry in self.novelIndex[tHandle]:
                if len(tEntry) != 4:
                    self.indexBroken = True

        for tHandle in self.noteIndex:
            for tEntry in self.noteIndex[tHandle]:
                if len(tEntry) != 4:
                    self.indexBroken = True

        if self.indexBroken:
            self.clearIndex()
            self.theParent.makeAlert(
                "The project index loaded from cache contains errors. Triggering Rebuild Index.",
                nwAlert.WARN
            )

        return

    ##
    #  Index Building
    ##

    def scanText(self, tHandle, theText):
        """Scan a piece of text associated with a handle. This will
        update the indices accordingly. This function takes the handle
        and text as separate inputs as we want to primarily scan the
        files before we save them, unless we're rebuilding the index.
        """

        theItem = self.theProject.getItem(tHandle)
        if theItem is None: return False
        if theItem.itemType != nwItemType.FILE: return False
        if theItem.parHandle == self.theProject.trashRoot: return False
        itemClass  = theItem.itemClass
        itemLayout = theItem.itemLayout

        logger.debug("Indexing item with handle %s" % tHandle)

        # Check file type, and reset its old index
        if itemClass == nwItemClass.NOVEL:
            self.novelIndex[tHandle] = []
            self.refIndex[tHandle] = []
            isNovel = True
        else:
            self.noteIndex[tHandle] = []
            self.refIndex[tHandle] = []
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
                isTitle = self.indexTitle(tHandle, isNovel, aLine, nLine, itemLayout)
                if isTitle:
                    nTitle = nLine
            elif aLine[0] == "@":
                self.indexNoteRef(tHandle, aLine, nLine, nTitle)
                self.indexTag(tHandle, aLine, nLine, itemClass)

        return True

    def indexTitle(self, tHandle, isNovel, aLine, nLine, itemLayout):
        """Save information about the title and its location in the
        file.
        """

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
            if isNovel:
                if tHandle in self.novelIndex:
                    self.novelIndex[tHandle].append([nLine, hDepth, hText, itemLayout.name])
            else:
                if tHandle in self.noteIndex:
                    self.noteIndex[tHandle].append([nLine, hDepth, hText, itemLayout.name])

        return True

    def indexNoteRef(self, tHandle, aLine, nLine, nTitle):
        """Validate and save the information about a reference to a tag
        in another file.
        """

        isValid, theBits, thePos = self.scanThis(aLine)
        if not isValid or len(theBits) == 0:
            return False

        if theBits[0] != nwKeyWords.TAG_KEY:
            for aVal in theBits[1:]:
                self.refIndex[tHandle].append([nLine, theBits[0], aVal, nTitle])

        return True

    def indexTag(self, tHandle, aLine, nLine, itemClass):
        """Validate and save the information from a tag.
        """

        isValid, theBits, thePos = self.scanThis(aLine)
        if not isValid or len(theBits) != 2:
            return False

        if theBits[0] == nwKeyWords.TAG_KEY:
            self.tagIndex[theBits[1]] = [nLine, tHandle, itemClass.name]

        return True

    ##
    #  Check @ Lines
    ##

    def scanThis(self, aLine):
        """Scan a line starting with @ to check that it's valid and to
        split up its elements into an array and an array of positions.
        The latter is needed for the syntax highlighter.
        """

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
        """Check the tags against the index to see if they are valid
        tags. This is needed for syntax highlighting.
        """

        nBits  = len(theBits)
        isGood = [False]*nBits
        if nBits == 0:
            return []

        # Check that the key is valid
        isGood[0] = theBits[0] in self.VALID_KEYS
        if not isGood[0] or nBits == 1:
            return isGood

        # If we have a tag, only the first value is accepted, the rest
        # is ignored
        if theBits[0] == nwKeyWords.TAG_KEY and nBits > 1:
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
        for n in range(1,nBits):
            if theBits[n] in self.tagIndex:
                isGood[n] = self.TAG_CLASS[theBits[0]][0].name == self.tagIndex[theBits[n]][2]

        return isGood

    ##
    #  Extract Data
    ##

    def buildNovelList(self):
        """Build a list of the content of the novel.
        """
        self.novelList  = []
        self.novelOrder = []
        for tHandle in self.theProject.treeOrder:
            if tHandle not in self.novelIndex:
                continue
            for tEntry in self.novelIndex[tHandle]:
                self.novelList.append(tEntry)
                self.novelOrder.append("%s:%d" % (tHandle,tEntry[0]))
        return True

    def buildReferenceList(self, tHandle):
        """Build a list of files referring back to our file, specified
        by tHandle.
        """

        theRefs = {}

        tItem = self.theProject.getItem(tHandle)
        if tHandle is None:
            return theRefs

        theTag = None
        for tTag in self.tagIndex:
            if tHandle == self.tagIndex[tTag][1]:
                theTag = tTag
                break

        if theTag is not None:
            for tHandle in self.refIndex:
                for nLine, tKey, tTag, nTitle in self.refIndex[tHandle]:
                    if tTag == theTag:
                        theRefs[tHandle] = nLine

        return theRefs

    def getTagSource(self, theTag):
        """Return the source location of a given tag.
        """
        if theTag in self.tagIndex:
            theRef = self.tagIndex[theTag]
            if len(theRef) == 3:
                return theRef[1], theRef[0]
        return None, 0

    def buildTagNovelMap(self, theTags, theFilters=None):
        """Build a two-dimensional map of all titles of the novel and
        which tags they link to from the various meta tags. This map is
        used to display the timeline view.
        """

        tagMap   = {}
        tagClass = {}
        exClass  = []

        if theFilters is not None:
            if "exClass" in theFilters.keys():
                exClass = theFilters["exClass"]

        for theTag in theTags:
            try:
                tagClass[theTag] = nwItemClass[self.tagIndex[theTag][2]]
            except:
                logger.error("Could not map '%s' to nwItemClass" % self.tagIndex[theTag][2])
                tagClass[theTag] = None
            if tagClass[theTag] not in exClass:
                tagMap[theTag] = [0]*len(self.novelOrder)

        for tHandle in self.refIndex:
            for nLine, tKey, tTag, nTitle in self.refIndex[tHandle]:
                if tTag in tagMap.keys() and tKey in self.TAG_CLASS:
                    try:
                        nPos = self.novelOrder.index("%s:%d" % (tHandle, nTitle))
                        if self.TAG_CLASS[tKey][0] == tagClass[tTag]:
                            tagMap[tTag][nPos] = self.TAG_CLASS[tKey][1]
                    except:
                        logger.error("Could not find '%s:%d' in novelOrder" % (tHandle, nTitle))

        if theFilters["hUnused"]:
            tagMapFiltered = {}
            for theTag in tagMap.keys():
                if sum(tagMap[theTag]) > 0:
                    tagMapFiltered[theTag] = tagMap[theTag]
            return tagMapFiltered

        return tagMap

# END Class NWIndex
