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
from time import time

from nw.constants import (
    nwFiles, nwKeyWords, nwItemType, nwItemClass, nwItemLayout, nwAlert
)
from nw.tools import countWords

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
        nwKeyWords.CHAR_KEY   : nwItemClass.CHARACTER,
        nwKeyWords.POV_KEY    : nwItemClass.CHARACTER,
        nwKeyWords.PLOT_KEY   : nwItemClass.PLOT,
        nwKeyWords.TIME_KEY   : nwItemClass.TIMELINE,
        nwKeyWords.WORLD_KEY  : nwItemClass.WORLD,
        nwKeyWords.OBJECT_KEY : nwItemClass.OBJECT,
        nwKeyWords.ENTITY_KEY : nwItemClass.ENTITY,
        nwKeyWords.CUSTOM_KEY : nwItemClass.CUSTOM,
    }

    def __init__(self, theProject, theParent):

        # Internal
        self.theProject  = theProject
        self.theParent   = theParent
        self.mainConf    = self.theParent.mainConf
        self.indexBroken = False

        # Indices
        self.tagIndex   = None
        self.refIndex   = None
        self.novelIndex = None
        self.noteIndex  = None
        self.textCounts = None

        self.clearIndex()

        return

    ##
    #  Public Methods
    ##

    def clearIndex(self):
        self.tagIndex   = {}
        self.refIndex   = {}
        self.novelIndex = {}
        self.noteIndex  = {}
        self.textCounts = {}
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
        self.textCounts.pop(tHandle, None)

        return

    ##
    #  Load and Save Index to/from File
    ##

    def loadIndex(self):
        """Load index from last session from the project meta folder.
        """

        theData   = {}
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
            if "textCounts" in theData.keys():
                self.textCounts = theData["textCounts"]

        self.checkIndex()

        return True

    def saveIndex(self):
        """Save the current index as a json file in the project meta
        data folder.
        """

        indexFile = path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)

        logger.debug("Saving index and meta files")
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
                    "textCounts" : self.textCounts,
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

        try:
            for tTag in self.tagIndex:
                if len(self.tagIndex[tTag]) != 3:
                    self.indexBroken = True

            for tHandle in self.refIndex:
                for sTitle in self.refIndex[tHandle]:
                    for tEntry in self.refIndex[tHandle][sTitle]["tags"]:
                        if len(tEntry) != 3:
                            self.indexBroken = True

            for tHandle in self.novelIndex:
                for sLine in self.novelIndex[tHandle]:
                    if len(self.novelIndex[tHandle][sLine].keys()) != 8:
                        self.indexBroken = True

            for tHandle in self.noteIndex:
                for sLine in self.noteIndex[tHandle]:
                    if len(self.noteIndex[tHandle][sLine].keys()) != 8:
                        self.indexBroken = True

            for tHandle in self.textCounts:
                if len(self.textCounts[tHandle]) != 3:
                    self.indexBroken = True

        except:
            self.indexBroken = True

        if self.indexBroken:
            self.clearIndex()
            self.theParent.makeAlert(
                "The index loaded from project cache contains errors. Rebuilding index.",
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
        if theItem is None:
            return False
        if theItem.itemType != nwItemType.FILE:
            return False
        if theItem.parHandle == self.theProject.trashRoot:
            return False
        if theItem.itemLayout == nwItemLayout.NO_LAYOUT:
            return False

        itemClass  = theItem.itemClass
        itemLayout = theItem.itemLayout

        logger.debug("Indexing item with handle %s" % tHandle)

        # Check file type, and reset its old index
        self.refIndex[tHandle] = {}
        if itemLayout == nwItemLayout.NOTE:
            self.noteIndex[tHandle] = {}
            isNovel = False
        else:
            self.novelIndex[tHandle] = {}
            isNovel = True

        # Also clear references to file in tag index
        clearTags = []
        for aTag in self.tagIndex:
            if self.tagIndex[aTag][1] == tHandle:
                clearTags.append(aTag)
        for aTag in clearTags:
            self.tagIndex.pop(aTag)

        nLine  = 0
        nTitle = 0
        sTitle = None
        theLines = theText.splitlines()
        for aLine in theLines:
            aLine  = aLine
            nLine += 1
            nChar  = len(aLine.strip())
            if nChar == 0:
                continue

            if aLine.startswith(r"#"):
                isTitle = self.indexTitle(tHandle, isNovel, aLine, nLine, itemLayout)
                if isTitle and nLine > 0:
                    if nTitle > 0:
                        lastText = "\n".join(theLines[nTitle-1:nLine-1])
                        self.indexWordCounts(tHandle, isNovel, lastText, nTitle)
                    nTitle = nLine

            elif aLine.startswith(r"@"):
                self.indexNoteRef(tHandle, aLine, nLine, nTitle)
                self.indexTag(tHandle, aLine, nLine, itemClass)

            elif aLine.startswith(r"%synopsis:"):
                if nTitle > 0:
                    self.indexSynopsis(tHandle, isNovel, aLine[10:].strip(), nTitle)

        # Count words for remaining text after last heading
        if nTitle > 0:
            lastText = "\n".join(theLines[nTitle-1:nLine-1])
            self.indexWordCounts(tHandle, isNovel, lastText, nTitle)

        # Run word counter for whole text
        cC, wC, pC = countWords(theText)
        self.textCounts[tHandle] = [cC, wC, pC]

        return True

    def indexTitle(self, tHandle, isNovel, aLine, nLine, itemLayout):
        """Save information about the title and its location in the
        file.
        """

        if aLine.startswith("# "):
            hDepth = "H1"
            hText  = aLine[2:].strip()
        elif aLine.startswith("## "):
            hDepth = "H2"
            hText  = aLine[3:].strip()
        elif aLine.startswith("### "):
            hDepth = "H3"
            hText  = aLine[4:].strip()
        elif aLine.startswith("#### "):
            hDepth = "H4"
            hText  = aLine[5:].strip()
        else:
            return False

        sTitle = "T%d" % nLine
        self.refIndex[tHandle][sTitle] = {
            "tags"    : [],
            "updated" : time(),
        }
        theData = {
            "level"    : hDepth,
            "title"    : hText,
            "layout"   : itemLayout.name,
            "synopsis" : "",
            "cCount"   : 0,
            "wCount"   : 0,
            "pCount"   : 0,
            "updated"  : time(),
        }

        if hText != "":
            if isNovel:
                if tHandle in self.novelIndex:
                    self.novelIndex[tHandle][sTitle] = theData
            else:
                if tHandle in self.noteIndex:
                    self.noteIndex[tHandle][sTitle] = theData

        return True

    def indexWordCounts(self, tHandle, isNovel, theText, nTitle):
        cC, wC, pC = countWords(theText)
        sTitle = "T%d" % nTitle
        if isNovel:
            if tHandle in self.novelIndex:
                if sTitle in self.novelIndex[tHandle]:
                    self.novelIndex[tHandle][sTitle]["cCount"] = cC
                    self.novelIndex[tHandle][sTitle]["wCount"] = wC
                    self.novelIndex[tHandle][sTitle]["pCount"] = pC
                    self.novelIndex[tHandle][sTitle]["updated"] = time()
        else:
            if tHandle in self.noteIndex:
                if sTitle in self.noteIndex[tHandle]:
                    self.noteIndex[tHandle][sTitle]["cCount"] = cC
                    self.noteIndex[tHandle][sTitle]["wCount"] = wC
                    self.noteIndex[tHandle][sTitle]["pCount"] = pC
                    self.noteIndex[tHandle][sTitle]["updated"] = time()
        return

    def indexSynopsis(self, tHandle, isNovel, theText, nTitle):
        sTitle = "T%d" % nTitle
        if isNovel:
            if tHandle in self.novelIndex:
                if sTitle in self.novelIndex[tHandle]:
                    self.novelIndex[tHandle][sTitle]["synopsis"] = theText
                    self.novelIndex[tHandle][sTitle]["updated"] = time()
        else:
            if tHandle in self.noteIndex:
                if sTitle in self.noteIndex[tHandle]:
                    self.noteIndex[tHandle][sTitle]["synopsis"] = theText
                    self.noteIndex[tHandle][sTitle]["updated"] = time()
        return

    def indexNoteRef(self, tHandle, aLine, nLine, nTitle):
        """Validate and save the information about a reference to a tag
        in another file.
        """

        isValid, theBits, thePos = self.scanThis(aLine)
        if not isValid or len(theBits) == 0:
            return False

        sTitle = "T%d" % nTitle

        if theBits[0] != nwKeyWords.TAG_KEY:
            for aVal in theBits[1:]:
                self.refIndex[tHandle][sTitle]["tags"].append([nLine, theBits[0], aVal])

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
                isGood[n] = self.TAG_CLASS[theBits[0]].name == self.tagIndex[theBits[n]][2]

        return isGood

    ##
    #  Extract Data
    ##

    def getNovelStructure(self):
        """Builds a list of all titles in the novel, in the correct
        order as they appear in the tree view and in the respective
        document files, but skipping all note files.
        """

        theStructure = []
        for tHandle in self.theProject.treeOrder:
            if tHandle not in self.novelIndex:
                continue
            for sTitle in sorted(self.novelIndex[tHandle].keys()):
                theStructure.append("%s:%s" % (tHandle, sTitle))

        return theStructure

    def getCounts(self, tHandle, nTitle=None):
        """Returns the counts for a file, or a section of a file
        starting at title nTitle.
        """

        cC = 0
        wC = 0
        pC = 0

        if nTitle is None:
            if tHandle in self.textCounts:
                cC = self.textCounts[tHandle][0]
                wC = self.textCounts[tHandle][1]
                pC = self.textCounts[tHandle][2]
        else:
            if tHandle in self.novelIndex:
                if nTitle in self.novelIndex[tHandle]:
                    cC = self.novelIndex[tHandle][nTitle]["cCount"]
                    wC = self.novelIndex[tHandle][nTitle]["wCount"]
                    pC = self.novelIndex[tHandle][nTitle]["pCount"]
            elif tHandle in self.noteIndex:
                if nTitle in self.noteIndex[tHandle]:
                    cC = self.noteIndex[tHandle][nTitle]["cCount"]
                    wC = self.noteIndex[tHandle][nTitle]["wCount"]
                    pC = self.noteIndex[tHandle][nTitle]["pCount"]

        return cC, wC, pC

    def getReferences(self, tHandle, tTitle=None):
        """Extract all references made in a file, and optionally title
        section. tTitle must be a string.
        """

        theRefs = {}
        for tKey in self.TAG_CLASS:
            theRefs[tKey] = []

        if tHandle not in self.refIndex:
            return theRefs

        try:
            for sTitle in self.refIndex[tHandle]:
                for nLine, tKey, tTag in self.refIndex[tHandle][sTitle]["tags"]:
                    if tTitle is None or tTitle == sTitle:
                        theRefs[tKey].append(tTag)
        except Exception as e:
            logger.error("Failed to generate reference list")
            logger.error(str(e))

        return theRefs

    def getBackReferenceList(self, tHandle):
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
                for sTitle in self.refIndex[tHandle]:
                    for nLine, tKey, tTag in self.refIndex[tHandle][sTitle]["tags"]:
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

# END Class NWIndex
