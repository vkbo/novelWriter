# -*- coding: utf-8 -*-
"""novelWriter Project Index

 novelWriter – Project Index
=============================
 Class holding the project index of tags, headers and references

 File History:
 Created: 2019-05-27 [0.1.4]

 This file is a part of novelWriter
 Copyright 2018–2021, Veronica Berglyd Olsen

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import nw
import logging
import json
import os

from time import time

from nw.constants import (
    nwFiles, nwKeyWords, nwItemType, nwItemClass, nwItemLayout, nwAlert
)
from nw.core.document import NWDoc
from nw.core.tools import countWords

logger = logging.getLogger(__name__)

class NWIndex():

    def __init__(self, theProject, theParent):

        # Internal
        self.mainConf    = nw.CONFIG
        self.theProject  = theProject
        self.theParent   = theParent
        self.indexBroken = False

        # Indices
        self.tagIndex   = None
        self.refIndex   = None
        self.novelIndex = None
        self.noteIndex  = None
        self.textCounts = None

        # TimeStamps
        self.timeNovel = 0
        self.timeNote  = 0
        self.timeIndex = 0

        self.clearIndex()

        return

    ##
    #  Public Methods
    ##

    def clearIndex(self):
        """Clear the index dictionaries and time stamps.
        """
        self.tagIndex   = {}
        self.refIndex   = {}
        self.novelIndex = {}
        self.noteIndex  = {}
        self.textCounts = {}
        self.timeNovel  = 0
        self.timeNote   = 0
        self.timeIndex  = 0
        return

    def deleteHandle(self, tHandle):
        """Delete all entries of a given document handle.
        """
        logger.debug("Removing item %s from the index" % tHandle)

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

    def reIndexHandle(self, tHandle):
        """Put a file back into the index. This is used when files are
        moved from the archive or trash folders back into the active
        project.
        """
        logger.debug("Re-indexing item %s" % tHandle)

        tItem = self.theProject.projTree[tHandle]
        if tItem is None:
            return False
        if tItem.itemType != nwItemType.FILE:
            return False

        theDoc = NWDoc(self.theProject, self.theParent)
        theText = theDoc.openDocument(tHandle, showStatus=False)
        if theText:
            self.scanText(tHandle, theText)

        return True

    ##
    #  Load and Save Index to/from File
    ##

    def loadIndex(self):
        """Load index from last session from the project meta folder.
        """
        theData   = {}
        indexFile = os.path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)

        if os.path.isfile(indexFile):
            logger.debug("Loading index file")
            try:
                with open(indexFile, mode="r", encoding="utf8") as inFile:
                    theData = json.load(inFile)
            except Exception as e:
                logger.error("Failed to load index file")
                logger.error(str(e))
                return False

            self.tagIndex   = theData.get("tagIndex", {})
            self.refIndex   = theData.get("refIndex", {})
            self.novelIndex = theData.get("novelIndex", {})
            self.noteIndex  = theData.get("noteIndex", {})
            self.textCounts = theData.get("textCounts", {})

            nowTime = round(time())
            self.timeNovel = nowTime
            self.timeNote  = nowTime
            self.timeIndex = nowTime

        self.checkIndex()

        return True

    def saveIndex(self):
        """Save the current index as a json file in the project meta
        data folder.
        """
        logger.debug("Saving index file")
        indexFile = os.path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)

        try:
            with open(indexFile, mode="w+", encoding="utf8") as outFile:
                json.dump({
                    "tagIndex"   : self.tagIndex,
                    "refIndex"   : self.refIndex,
                    "novelIndex" : self.novelIndex,
                    "noteIndex"  : self.noteIndex,
                    "textCounts" : self.textCounts,
                }, outFile, indent=2)
        except Exception as e:
            logger.error("Failed to save index file")
            logger.error(str(e))
            return False

        return True

    def checkIndex(self):
        """Check that the entries in the index are valid and contain the
        elements it should.
        """
        logger.debug("Checking index")
        self.indexBroken = False

        try:
            for tTag in self.tagIndex:
                if len(self.tagIndex[tTag]) != 4:
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

        except Exception:
            self.indexBroken = True

        logger.debug("Index check complete")
        if self.indexBroken:
            self.clearIndex()
            self.theParent.makeAlert(
                "The project index is outdated or broken. Rebuilding index.",
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
        theItem = self.theProject.projTree[tHandle]
        theRoot = self.theProject.projTree.getRootItem(tHandle)

        if theItem is None:
            logger.info("Not indexing unknown item %s" % tHandle)
            return False
        if theItem.itemType != nwItemType.FILE:
            logger.info("Not indexing non-file item %s" % tHandle)
            return False
        if theItem.itemLayout == nwItemLayout.NO_LAYOUT:
            logger.info("Not indexing no-layout item %s" % tHandle)
            return False
        if theItem.itemParent is None:
            logger.info("Not indexing orphaned item %s" % tHandle)
            return False

        # Run word counter for the whole text
        cC, wC, pC = countWords(theText)
        self.textCounts[tHandle] = [cC, wC, pC]

        # If the file is archived or trashed, we don't index the file itself
        if self.theProject.projTree.isTrashRoot(theItem.itemParent):
            logger.info("Not indexing trash item %s" % tHandle)
            return False
        if theRoot.itemClass == nwItemClass.ARCHIVE:
            logger.info("Not indexing archived item %s" % tHandle)
            return False

        itemClass  = theItem.itemClass
        itemLayout = theItem.itemLayout

        logger.debug("Indexing item with handle %s" % tHandle)

        # Check file type, and reset its old index
        # Also add a dummy entry T000000 in case the file has no title
        self.refIndex[tHandle] = {}
        self.refIndex[tHandle]["T000000"] = {
            "tags"    : [],
            "updated" : round(time()),
        }
        if itemLayout == nwItemLayout.NOTE:
            self.novelIndex.pop(tHandle, None)
            self.noteIndex[tHandle] = {}
            isNovel = False
        else:
            self.novelIndex[tHandle] = {}
            self.noteIndex.pop(tHandle, None)
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
        theLines = theText.splitlines()
        for aLine in theLines:
            aLine  = aLine
            nLine += 1
            nChar  = len(aLine.strip())
            if nChar == 0:
                continue

            if aLine.startswith(r"#"):
                isTitle = self._indexTitle(tHandle, isNovel, aLine, nLine, itemLayout)
                if isTitle and nLine > 0:
                    if nTitle > 0:
                        lastText = "\n".join(theLines[nTitle-1:nLine-1])
                        self._indexWordCounts(tHandle, isNovel, lastText, nTitle)
                    nTitle = nLine

            elif aLine.startswith(r"@"):
                self._indexNoteRef(tHandle, aLine, nLine, nTitle)
                self._indexTag(tHandle, aLine, nLine, nTitle, itemClass)

            elif aLine.startswith(r"%"):
                if nTitle > 0:
                    toCheck = aLine[1:].lstrip()
                    synTag = toCheck[:9].lower()
                    tLen = len(aLine)
                    cLen = len(toCheck)
                    cOff = tLen - cLen
                    if synTag == "synopsis:":
                        self._indexSynopsis(tHandle, isNovel, aLine[cOff+9:].strip(), nTitle)

        # Count words for remaining text after last heading
        if nTitle > 0:
            lastText = "\n".join(theLines[nTitle-1:])
            self._indexWordCounts(tHandle, isNovel, lastText, nTitle)

        # Update timestamps for index changes
        nowTime = round(time())
        self.timeIndex = nowTime
        if isNovel:
            self.timeNovel = nowTime
        else:
            self.timeNote = nowTime

        return True

    ##
    #  Internal Indexers
    ##

    def _indexTitle(self, tHandle, isNovel, aLine, nLine, itemLayout):
        """Save information about the title and its location in the
        file to the index.
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

        sTitle = "T%06d" % nLine
        self.refIndex[tHandle][sTitle] = {
            "tags"    : [],
            "updated" : round(time()),
        }
        theData = {
            "level"    : hDepth,
            "title"    : hText,
            "layout"   : itemLayout.name,
            "synopsis" : "",
            "cCount"   : 0,
            "wCount"   : 0,
            "pCount"   : 0,
            "updated"  : round(time()),
        }

        if hText != "":
            if isNovel:
                if tHandle in self.novelIndex:
                    self.novelIndex[tHandle][sTitle] = theData
            else:
                if tHandle in self.noteIndex:
                    self.noteIndex[tHandle][sTitle] = theData

        return True

    def _indexWordCounts(self, tHandle, isNovel, theText, nTitle):
        """Count text stats and save the counts to the index.
        """
        cC, wC, pC = countWords(theText)
        sTitle = "T%06d" % nTitle
        if isNovel:
            if tHandle in self.novelIndex:
                if sTitle in self.novelIndex[tHandle]:
                    self.novelIndex[tHandle][sTitle]["cCount"] = cC
                    self.novelIndex[tHandle][sTitle]["wCount"] = wC
                    self.novelIndex[tHandle][sTitle]["pCount"] = pC
                    self.novelIndex[tHandle][sTitle]["updated"] = round(time())
        else:
            if tHandle in self.noteIndex:
                if sTitle in self.noteIndex[tHandle]:
                    self.noteIndex[tHandle][sTitle]["cCount"] = cC
                    self.noteIndex[tHandle][sTitle]["wCount"] = wC
                    self.noteIndex[tHandle][sTitle]["pCount"] = pC
                    self.noteIndex[tHandle][sTitle]["updated"] = round(time())
        return

    def _indexSynopsis(self, tHandle, isNovel, theText, nTitle):
        """Save the synopsis to the index.
        """
        sTitle = "T%06d" % nTitle
        if isNovel:
            if tHandle in self.novelIndex:
                if sTitle in self.novelIndex[tHandle]:
                    self.novelIndex[tHandle][sTitle]["synopsis"] = theText
                    self.novelIndex[tHandle][sTitle]["updated"] = round(time())
        else:
            if tHandle in self.noteIndex:
                if sTitle in self.noteIndex[tHandle]:
                    self.noteIndex[tHandle][sTitle]["synopsis"] = theText
                    self.noteIndex[tHandle][sTitle]["updated"] = round(time())
        return

    def _indexNoteRef(self, tHandle, aLine, nLine, nTitle):
        """Validate and save the information about a reference to a tag
        in another file.
        """
        isValid, theBits, _ = self.scanThis(aLine)
        if not isValid or len(theBits) == 0:
            return False

        sTitle = "T%06d" % nTitle
        if sTitle in self.refIndex[tHandle] and theBits[0] != nwKeyWords.TAG_KEY:
            for aVal in theBits[1:]:
                self.refIndex[tHandle][sTitle]["tags"].append([nLine, theBits[0], aVal])

        return True

    def _indexTag(self, tHandle, aLine, nLine, nTitle, itemClass):
        """Validate and save the information from a tag.
        """
        isValid, theBits, thePos = self.scanThis(aLine)
        if not isValid or len(theBits) != 2:
            return False

        if theBits[0] == nwKeyWords.TAG_KEY:
            sTitle = "T%06d" % nTitle
            self.tagIndex[theBits[1]] = [nLine, tHandle, itemClass.name, sTitle]

        return True

    ##
    #  Check @ Lines
    ##

    def scanThis(self, aLine):
        """Scan a line starting with @ to check that it's valid. Then
        split it up into its elements and positions as two arrays.
        """
        theBits = [] # The elements of the string
        thePos  = [] # The absolute position of each element

        aLine = aLine.rstrip() # Remove all trailing white spaces
        nChar = len(aLine)
        if nChar < 2:
            return False, theBits, thePos
        if aLine[0] != "@":
            return False, theBits, thePos

        cKey, _, cVals = aLine.partition(":")
        sKey = cKey.strip()
        if sKey == "@":
            return False, theBits, thePos

        cPos = 0
        theBits.append(sKey)
        thePos.append(cPos)
        cPos += len(cKey) + 1

        if not cVals:
            # No values, so we're done
            return True, theBits, thePos

        for cVal in cVals.split(","):
            sVal = cVal.strip()
            rLen = len(cVal.lstrip())
            tLen = len(cVal)
            theBits.append(sVal)
            thePos.append(cPos + tLen - rLen)
            cPos += tLen + 1

        return True, theBits, thePos

    def checkThese(self, theBits, tItem):
        """Check the tags against the index to see if they are valid
        tags. This is needed for syntax highlighting.
        """
        nBits = len(theBits)
        isGood = [False]*nBits
        if nBits == 0:
            return []

        # Check that the key is valid
        isGood[0] = theBits[0] in nwKeyWords.VALID_KEYS
        if not isGood[0] or nBits == 1:
            return isGood

        # If we have a tag, only the first value is accepted, the rest
        # is ignored
        if theBits[0] == nwKeyWords.TAG_KEY and nBits > 1:
            isGood[0] = True
            if theBits[1] in self.tagIndex:
                if self.tagIndex[theBits[1]][1] == tItem.itemHandle:
                    isGood[1] = True
                else:
                    isGood[1] = False
            else:
                isGood[1] = True
            return isGood

        # If we're still here, we better check that the references exist
        for n in range(1, nBits):
            if theBits[n] in self.tagIndex:
                isGood[n] = nwKeyWords.KEY_CLASS[theBits[0]].name == self.tagIndex[theBits[n]][2]

        return isGood

    ##
    #  Extract Data
    ##

    def getNovelStructure(self, skipExcluded=True):
        """Builds a list of all titles in the novel, in the correct
        order as they appear in the tree view and in the respective
        document files, but skipping all note files.
        """
        theStructure = []
        for tItem in self.theProject.projTree:
            if tItem is not None:
                if not tItem.isExported and skipExcluded:
                    continue
                tHandle = tItem.itemHandle
                if tHandle not in self.novelIndex:
                    continue
                for sTitle in sorted(self.novelIndex[tHandle].keys()):
                    theStructure.append("%s:%s" % (tHandle, sTitle))

        return theStructure

    def getCounts(self, tHandle, sTitle=None):
        """Returns the counts for a file, or a section of a file
        starting at title sTitle if it is provided.
        """
        cC = 0
        wC = 0
        pC = 0

        if sTitle is None:
            if tHandle in self.textCounts:
                cC = self.textCounts[tHandle][0]
                wC = self.textCounts[tHandle][1]
                pC = self.textCounts[tHandle][2]
        else:
            if tHandle in self.novelIndex:
                if sTitle in self.novelIndex[tHandle]:
                    cC = self.novelIndex[tHandle][sTitle]["cCount"]
                    wC = self.novelIndex[tHandle][sTitle]["wCount"]
                    pC = self.novelIndex[tHandle][sTitle]["pCount"]
            elif tHandle in self.noteIndex:
                if sTitle in self.noteIndex[tHandle]:
                    cC = self.noteIndex[tHandle][sTitle]["cCount"]
                    wC = self.noteIndex[tHandle][sTitle]["wCount"]
                    pC = self.noteIndex[tHandle][sTitle]["pCount"]

        return cC, wC, pC

    def getReferences(self, tHandle, sTitle=None):
        """Extract all references made in a file, and optionally title
        section. sTitle must be a string.
        """
        theRefs = {}
        for tKey in nwKeyWords.KEY_CLASS:
            theRefs[tKey] = []

        if tHandle not in self.refIndex:
            return theRefs

        for refTitle in self.refIndex[tHandle]:
            for aTag in self.refIndex[tHandle][refTitle].get("tags", []):
                if len(aTag) == 3 and (sTitle is None or sTitle == refTitle):
                    theRefs[aTag[1]].append(aTag[2])

        return theRefs

    def getBackReferenceList(self, tHandle):
        """Build a list of files referring back to our file, specified
        by tHandle.
        """
        theRefs = {}
        if tHandle is None:
            return theRefs

        theTags = set()
        for tTag in self.tagIndex:
            if tHandle == self.tagIndex[tTag][1]:
                theTags.add(tTag)

        if theTags:
            for tHandle in self.refIndex:
                for sTitle in self.refIndex[tHandle]:
                    for _, _, tTag in self.refIndex[tHandle][sTitle]["tags"]:
                        if tTag in theTags and tHandle not in theRefs:
                            theRefs[tHandle] = sTitle

        return theRefs

    def getTagSource(self, theTag):
        """Return the source location of a given tag.
        """
        if theTag in self.tagIndex:
            theRef = self.tagIndex[theTag]
            if len(theRef) == 4:
                return theRef[1], theRef[0], theRef[3]
        return None, 0, "T000000"

# END Class NWIndex
