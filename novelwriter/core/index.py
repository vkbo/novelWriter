"""
novelWriter – Project Index
===========================
Data class for the project index of tags, headers and references

File History:
Created: 2019-04-22 [0.0.1] countWords
Created: 2019-05-27 [0.1.4] NWIndex

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

from nw.enum import nwItemType, nwItemClass, nwItemLayout
from nw.constants import nwFiles, nwKeyWords, nwUnicode
from nw.core.document import NWDoc
from nw.common import (
    isHandle, isTitleTag, isItemClass, isItemLayout, jsonEncode
)

logger = logging.getLogger(__name__)

H_VALID = ("H0", "H1", "H2", "H3", "H4")
H_LEVEL = {"H0": 0, "H1": 1, "H2": 2, "H3": 3, "H4": 4}


class NWIndex():

    def __init__(self, theProject):

        # Internal
        self.mainConf    = nw.CONFIG
        self.theProject  = theProject
        self.indexBroken = False

        # Indices
        self._tagIndex  = {}
        self._refIndex  = {}
        self._fileIndex = {}
        self._fileMeta  = {}

        # TimeStamps
        self._timeNovel = 0
        self._timeNotes = 0
        self._timeIndex = 0

        return

    ##
    #  Public Methods
    ##

    def clearIndex(self):
        """Clear the index dictionaries and time stamps.
        """
        self._tagIndex  = {}
        self._refIndex  = {}
        self._fileIndex = {}
        self._fileMeta  = {}
        self._timeNovel = 0
        self._timeNotes = 0
        self._timeIndex = 0
        return

    def deleteHandle(self, tHandle):
        """Delete all entries of a given document handle.
        """
        logger.debug("Removing item '%s' from the index", tHandle)

        delTags = []
        for tTag in self._tagIndex:
            if self._tagIndex[tTag][1] == tHandle:
                delTags.append(tTag)

        for tTag in delTags:
            self._tagIndex.pop(tTag, None)

        self._refIndex.pop(tHandle, None)
        self._fileIndex.pop(tHandle, None)
        self._fileMeta.pop(tHandle, None)

        return

    def reIndexHandle(self, tHandle):
        """Put a file back into the index. This is used when files are
        moved from the archive or trash folders back into the active
        project.
        """
        logger.debug("Re-indexing item '%s'", tHandle)

        tItem = self.theProject.projTree[tHandle]
        if tItem is None:
            return False
        if tItem.itemType != nwItemType.FILE:
            return False

        theDoc = NWDoc(self.theProject, tHandle)
        theText = theDoc.readDocument()
        if theText:
            self.scanText(tHandle, theText)

        return True

    def novelChangedSince(self, checkTime):
        """Check if the novel index has changed since a given time.
        """
        return self._timeNovel > checkTime

    def notesChangedSince(self, checkTime):
        """Check if the notes index has changed since a given time.
        """
        return self._timeNotes > checkTime

    def indexChangedSince(self, checkTime):
        """Check if the index has changed since a given time.
        """
        return self._timeIndex > checkTime

    ##
    #  Load and Save Index to/from File
    ##

    def loadIndex(self):
        """Load index from last session from the project meta folder.
        """
        theData = {}
        indexFile = os.path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)
        tStart = time()

        if os.path.isfile(indexFile):
            logger.debug("Loading index file")
            try:
                with open(indexFile, mode="r", encoding="utf-8") as inFile:
                    theData = json.load(inFile)

            except Exception:
                logger.error("Failed to load index file")
                nw.logException()
                self.indexBroken = True
                return False

            self._tagIndex = theData.get("tagIndex", {})
            self._refIndex = theData.get("refIndex", {})
            self._fileIndex = theData.get("fileIndex", {})
            self._fileMeta = theData.get("fileMeta", {})

            nowTime = round(time())
            self._timeNovel = nowTime
            self._timeNotes = nowTime
            self._timeIndex = nowTime

        logger.verbose("Index loaded in %.3f ms", (time() - tStart)*1000)

        self.checkIndex()

        return True

    def saveIndex(self):
        """Save the current index as a json file in the project meta
        data folder.
        """
        logger.debug("Saving index file")
        indexFile = os.path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)
        tStart = time()

        try:
            with open(indexFile, mode="w+", encoding="utf-8") as outFile:
                outFile.write("{\n")
                outFile.write(f'"tagIndex": {jsonEncode(self._tagIndex, nmax=1)},\n')
                outFile.write(f'"refIndex": {jsonEncode(self._refIndex, nmax=2)},\n')
                outFile.write(f'"fileIndex": {jsonEncode(self._fileIndex, nmax=2)},\n')
                outFile.write(f'"fileMeta": {jsonEncode(self._fileMeta, nmax=1)}\n')
                outFile.write("}\n")

        except Exception:
            logger.error("Failed to save index file")
            nw.logException()
            return False

        logger.verbose("Index saved in %.3f ms", (time() - tStart)*1000)

        return True

    def checkIndex(self):
        """Check that the entries in the index are valid and contain the
        elements it should.
        """
        logger.debug("Checking index")
        tStart = time()

        try:
            self._checkTagIndex()
            self._checkRefIndex()
            self._checkFileIndex()
            self._checkFileMeta()
            self.indexBroken = False

        except Exception:
            logger.error("Error while checking index")
            nw.logException()
            self.indexBroken = True

        logger.verbose("Index check took %.3f ms", (time() - tStart)*1000)
        logger.debug("Index check complete")

        if self.indexBroken:
            self.clearIndex()

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
            logger.info("Not indexing unknown item '%s'", tHandle)
            return False
        if theItem.itemType != nwItemType.FILE:
            logger.info("Not indexing non-file item '%s'", tHandle)
            return False
        if theItem.itemLayout == nwItemLayout.NO_LAYOUT:
            logger.info("Not indexing no-layout item '%s'", tHandle)
            return False
        if theItem.itemParent is None:
            logger.info("Not indexing orphaned item '%s'", tHandle)
            return False

        # Run word counter for the whole text
        cC, wC, pC = countWords(theText)
        self._fileMeta[tHandle] = ["H0", cC, wC, pC]

        # If the file is archived or trashed, we don't index the file itself
        if self.theProject.projTree.isTrashRoot(theItem.itemParent):
            logger.debug("Not indexing trash item '%s'", tHandle)
            return False
        if theRoot.itemClass == nwItemClass.ARCHIVE:
            logger.debug("Not indexing archived item '%s'", tHandle)
            return False

        itemClass  = theItem.itemClass
        itemLayout = theItem.itemLayout

        logger.debug("Indexing item with handle '%s'", tHandle)

        # Delete or reset old entries for the file
        self._refIndex.pop(tHandle, None)
        self._fileIndex[tHandle] = {}

        # Also clear references to file in tag index
        clearTags = []
        for aTag in self._tagIndex:
            if self._tagIndex[aTag][1] == tHandle:
                clearTags.append(aTag)
        for aTag in clearTags:
            self._tagIndex.pop(aTag)

        # Scan the text content
        nLine = 0
        nTitle = 0
        theLines = theText.splitlines()
        for aLine in theLines:
            nLine += 1
            nChar = len(aLine.strip())
            if nChar == 0:
                continue

            if aLine.startswith("#"):
                isTitle = self._indexTitle(tHandle, aLine, nLine, itemLayout)
                if isTitle and nLine > 0:
                    if nTitle > 0:
                        lastText = "\n".join(theLines[nTitle-1:nLine-1])
                        self._indexWordCounts(tHandle, lastText, nTitle)
                    nTitle = nLine

            elif aLine.startswith("@"):
                self._indexKeyword(tHandle, aLine, nLine, nTitle, itemClass)

            elif aLine.startswith("%"):
                if nTitle > 0:
                    toCheck = aLine[1:].lstrip()
                    synTag = toCheck[:9].lower()
                    tLen = len(aLine)
                    cLen = len(toCheck)
                    cOff = tLen - cLen
                    if synTag == "synopsis:":
                        self._indexSynopsis(tHandle, aLine[cOff+9:].strip(), nTitle)

        # Count words for remaining text after last heading
        if nTitle > 0:
            lastText = "\n".join(theLines[nTitle-1:])
            self._indexWordCounts(tHandle, lastText, nTitle)

        # Index page with no titles and references
        if nTitle == 0:
            self._indexPage(tHandle, itemLayout)
            self._indexWordCounts(tHandle, theText, nTitle)

        # Update timestamps for index changes
        nowTime = round(time())
        self._timeIndex = nowTime
        if itemLayout == nwItemLayout.NOTE:
            self._timeNotes = nowTime
        else:
            self._timeNovel = nowTime

        return True

    ##
    #  Internal Indexers
    ##

    def _indexTitle(self, tHandle, aLine, nLine, itemLayout):
        """Save information about the title and its location in the
        file to the index.
        """
        if aLine.startswith("# "):
            hDepth = "H1"
            hText = aLine[2:].strip()
        elif aLine.startswith("## "):
            hDepth = "H2"
            hText = aLine[3:].strip()
        elif aLine.startswith("### "):
            hDepth = "H3"
            hText = aLine[4:].strip()
        elif aLine.startswith("#### "):
            hDepth = "H4"
            hText = aLine[5:].strip()
        elif aLine.startswith("#! "):
            hDepth = "H1"
            hText = aLine[2:].strip()
        elif aLine.startswith("##! "):
            hDepth = "H2"
            hText = aLine[4:].strip()
        else:
            return False

        sTitle = "T%06d" % nLine
        self._fileIndex[tHandle][sTitle] = {
            "level": hDepth,
            "title": hText,
            "layout": itemLayout.name,
            "cCount": 0,
            "wCount": 0,
            "pCount": 0,
            "synopsis": "",
        }

        if self._fileMeta[tHandle][0] == "H0":
            self._fileMeta[tHandle][0] = hDepth

        return True

    def _indexPage(self, tHandle, itemLayout):
        """Index a page with no title.
        """
        self._fileIndex[tHandle]["T000000"] = {
            "level": "H0",
            "title": "",
            "layout": itemLayout.name,
            "cCount": 0,
            "wCount": 0,
            "pCount": 0,
            "synopsis": "",
        }

        return

    def _indexWordCounts(self, tHandle, theText, nTitle):
        """Count text stats and save the counts to the index.
        """
        cC, wC, pC = countWords(theText)
        sTitle = "T%06d" % nTitle
        if tHandle in self._fileIndex:
            if sTitle in self._fileIndex[tHandle]:
                self._fileIndex[tHandle][sTitle]["cCount"] = cC
                self._fileIndex[tHandle][sTitle]["wCount"] = wC
                self._fileIndex[tHandle][sTitle]["pCount"] = pC
        return

    def _indexSynopsis(self, tHandle, theText, nTitle):
        """Save the synopsis to the index.
        """
        sTitle = "T%06d" % nTitle
        if tHandle in self._fileIndex:
            if sTitle in self._fileIndex[tHandle]:
                self._fileIndex[tHandle][sTitle]["synopsis"] = theText
        return

    def _indexKeyword(self, tHandle, aLine, nLine, nTitle, itemClass):
        """Validate and save the information about a reference to a tag
        in another file.
        """
        isValid, theBits, _ = self.scanThis(aLine)
        if not isValid or len(theBits) < 2:
            logger.warning("Skipping keyword with %d value(s) in '%s'", len(theBits), tHandle)
            return

        if theBits[0] not in nwKeyWords.VALID_KEYS:
            logger.warning("Skipping invalid keyword '%s' in '%s'", theBits[0], tHandle)
            return

        sTitle = "T%06d" % nTitle
        if theBits[0] == nwKeyWords.TAG_KEY:
            self._tagIndex[theBits[1]] = [nLine, tHandle, itemClass.name, sTitle]

        else:
            if tHandle not in self._refIndex:
                self._refIndex[tHandle] = {}
            if sTitle not in self._refIndex[tHandle]:
                self._refIndex[tHandle][sTitle] = []
            for aVal in theBits[1:]:
                self._refIndex[tHandle][sTitle].append([nLine, theBits[0], aVal])

        return

    ##
    #  Check @ Lines
    ##

    def scanThis(self, aLine):
        """Scan a line starting with @ to check that it's valid. Then
        split it up into its elements and positions as two arrays.
        """
        theBits = []  # The elements of the string
        thePos  = []  # The absolute position of each element

        aLine = aLine.rstrip()  # Remove all trailing white spaces
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

        # For a tag, only the first value is accepted, the rest are ignored
        if theBits[0] == nwKeyWords.TAG_KEY and nBits > 1:
            if theBits[1] in self._tagIndex:
                isGood[1] = self._tagIndex[theBits[1]][1] == tItem.itemHandle
            else:
                isGood[1] = True
            return isGood

        # If we're still here, we check that the references exist
        theKey = nwKeyWords.KEY_CLASS[theBits[0]].name
        for n in range(1, nBits):
            if theBits[n] in self._tagIndex:
                isGood[n] = theKey == self._tagIndex[theBits[n]][2]

        return isGood

    ##
    #  Extract Data
    ##

    def novelStructure(self, skipExcluded=True):
        """Iterate over all titles in the novel, in the correct order as
        they appear in the tree view and in the respective document
        files, but skipping all note files.
        """
        for tHandle in self._listNovelHandles(skipExcluded):
            for sTitle in sorted(self._fileIndex[tHandle]):
                tKey = "%s:%s" % (tHandle, sTitle)
                yield tKey, tHandle, sTitle, self._fileIndex[tHandle][sTitle]

    def getNovelWordCount(self, skipExcluded=True):
        """Count the number of words in the novel project.
        """
        wCount = 0
        for tHandle in self._listNovelHandles(skipExcluded):
            for sTitle in self._fileIndex[tHandle]:
                wCount += self._fileIndex[tHandle][sTitle]["wCount"]

        return wCount

    def getNovelTitleCounts(self, skipExcluded=True):
        """Count the number of titles in the novel project.
        """
        hCount = [0, 0, 0, 0, 0]
        for tHandle in self._listNovelHandles(skipExcluded):
            for sTitle in self._fileIndex[tHandle]:
                theData = self._fileIndex[tHandle][sTitle]
                iLevel = H_LEVEL.get(theData["level"], 0)
                hCount[iLevel] += 1

        return hCount

    def getHandleWordCounts(self, tHandle):
        """Get all header word counts for a specific handle.
        """
        theCounts = []
        hRecord = self._fileIndex.get(tHandle, None)
        if hRecord is None:
            return theCounts

        for sTitle, sData in hRecord.items():
            theCounts.append(("%s:%s" % (tHandle, sTitle), sData["wCount"]))

        return theCounts

    def getHandleHeaders(self, tHandle):
        """Get all headers for a specific handle.
        """
        theHeaders = []
        hRecord = self._fileIndex.get(tHandle, None)
        if hRecord is None:
            return theHeaders

        for sTitle, sData in hRecord.items():
            theHeaders.append((sTitle, sData["level"], sData["title"]))

        return theHeaders

    def getHandleHeaderLevel(self, tHandle):
        """Get the header level of the first header of a handle.
        """
        if tHandle in self._fileMeta:
            return self._fileMeta[tHandle][0]
        return "H0"

    def getTableOfContents(self, maxDepth, skipExcluded=True):
        """Generate a table of contents up to a maxiumum depth.
        """
        tOrder = []
        tData = {}
        pKey = None
        for tHandle in self._listNovelHandles(skipExcluded):
            for sTitle in sorted(self._fileIndex[tHandle]):
                tKey = "%s:%s" % (tHandle, sTitle)
                theData = self._fileIndex[tHandle][sTitle]
                iLevel = H_LEVEL.get(theData["level"], 0)
                if iLevel > maxDepth:
                    if pKey in tData:
                        theData["wCount"]
                        tData[pKey]["words"] += theData["wCount"]
                else:
                    pKey = tKey
                    tOrder.append(tKey)
                    tData[tKey] = {
                        "level": iLevel,
                        "title": theData["title"],
                        "words": theData["wCount"],
                    }

        theToC = []
        for tKey in tOrder:
            theToC.append((
                tKey,
                tData[tKey]["level"],
                tData[tKey]["title"],
                tData[tKey]["words"],
            ))

        return theToC

    def getCounts(self, tHandle, sTitle=None):
        """Returns the counts for a file, or a section of a file
        starting at title sTitle if it is provided.
        """
        cC = 0
        wC = 0
        pC = 0

        if sTitle is None:
            if tHandle in self._fileMeta:
                cC = self._fileMeta[tHandle][1]
                wC = self._fileMeta[tHandle][2]
                pC = self._fileMeta[tHandle][3]
        else:
            if tHandle in self._fileIndex:
                if sTitle in self._fileIndex[tHandle]:
                    cC = self._fileIndex[tHandle][sTitle]["cCount"]
                    wC = self._fileIndex[tHandle][sTitle]["wCount"]
                    pC = self._fileIndex[tHandle][sTitle]["pCount"]

        return cC, wC, pC

    def getReferences(self, tHandle, sTitle=None):
        """Extract all references made in a file, and optionally title
        section. sTitle must be a string.
        """
        theRefs = {}
        for tKey in nwKeyWords.KEY_CLASS:
            theRefs[tKey] = []

        if tHandle not in self._refIndex:
            return theRefs

        for refTitle in self._refIndex[tHandle]:
            for aTag in self._refIndex[tHandle][refTitle]:
                if len(aTag) == 3 and (sTitle is None or sTitle == refTitle):
                    if aTag[1] in theRefs:
                        theRefs[aTag[1]].append(aTag[2])

        return theRefs

    def getNovelData(self, tHandle, sTitle):
        """Return the novel data of a given handle and title.
        """
        if tHandle in self._fileIndex:
            if sTitle in self._fileIndex[tHandle]:
                return self._fileIndex[tHandle][sTitle]
        return None

    def getBackReferenceList(self, tHandle):
        """Build a list of files referring back to our file, specified
        by tHandle.
        """
        theRefs = {}
        if tHandle is None:
            return theRefs

        theTags = set()
        for tTag in self._tagIndex:
            if tHandle == self._tagIndex[tTag][1]:
                theTags.add(tTag)

        if theTags:
            for tHandle in self._refIndex:
                for sTitle in self._refIndex[tHandle]:
                    for _, _, tTag in self._refIndex[tHandle][sTitle]:
                        if tTag in theTags and tHandle not in theRefs:
                            theRefs[tHandle] = sTitle

        return theRefs

    def getTagSource(self, theTag):
        """Return the source location of a given tag.
        """
        if theTag in self._tagIndex:
            theRef = self._tagIndex[theTag]
            if len(theRef) == 4:
                return theRef[1], theRef[0], theRef[3]
        return None, 0, "T000000"

    ##
    #  Internal Functions
    ##

    def _listNovelHandles(self, skipExcluded):
        """Return a list of all handles that exist in the novel index.
        """
        theHandles = []
        for tItem in self.theProject.projTree:
            if tItem is None:
                continue
            if not tItem.isExported and skipExcluded:
                continue
            if tItem.itemLayout == nwItemLayout.NOTE:
                continue
            if tItem.itemHandle in self._fileIndex:
                theHandles.append(tItem.itemHandle)

        return theHandles

    ##
    #  Index Checkers
    ##

    def _checkTagIndex(self):
        """Scan the tag index for errors.
        Warning: This function raises exceptions.
        """
        for tTag in self._tagIndex:
            if not isinstance(tTag, str):
                raise KeyError("tagIndex key is not a string")

            tEntry = self._tagIndex[tTag]
            if len(tEntry) != 4:
                raise IndexError("tagIndex[a] expected 4 values")
            if not isinstance(tEntry[0], int):
                raise ValueError("tagIndex[a][0] is not an integer")
            if not isHandle(tEntry[1]):
                raise ValueError("tagIndex[a][1] is not a handle")
            if not isItemClass(tEntry[2]):
                raise ValueError("tagIndex[a][2] is not an nwItemClass")
            if not isTitleTag(tEntry[3]):
                raise ValueError("tagIndex[a][3] is not a title tag")

        return

    def _checkRefIndex(self):
        """Scan the reference index for errors.
        Warning: This function raises exceptions.
        """
        for tHandle in self._refIndex:
            if not isHandle(tHandle):
                raise KeyError("refIndex key is not a handle")

            hEntry = self._refIndex[tHandle]
            for sTitle in hEntry:
                if not isTitleTag(sTitle):
                    raise KeyError("refIndex[a] key is not a title tag")

                sEntry = hEntry[sTitle]
                for tEntry in sEntry:
                    if len(tEntry) != 3:
                        raise IndexError("refIndex[a][b][i] expected 3 values")
                    if not isinstance(tEntry[0], int):
                        raise ValueError("refIndex[a][b][i][0] is not an integer")
                    if not tEntry[1] in nwKeyWords.VALID_KEYS:
                        raise ValueError("refIndex[a][b][i][1] is not a keyword")
                    if not isinstance(tEntry[2], str):
                        raise ValueError("refIndex[a][b][i][2] is not a string")

        return

    def _checkFileIndex(self):
        """Scan the file index for errors.
        Warning: This function raises exceptions.
        """
        for tHandle in self._fileIndex:
            if not isHandle(tHandle):
                raise KeyError("fileIndex key is not a handle")

            hEntry = self._fileIndex[tHandle]
            for sTitle in self._fileIndex[tHandle]:
                if not isTitleTag(sTitle):
                    raise KeyError("fileIndex[a] key is not a title tag")

                sEntry = hEntry[sTitle]
                if len(sEntry) != 7:
                    raise IndexError("fileIndex[a][b] expected 7 values")

                if "level" not in sEntry:
                    raise KeyError("fileIndex[a][b] has no 'level' key")
                if "title" not in sEntry:
                    raise KeyError("fileIndex[a][b] has no 'title' key")
                if "layout" not in sEntry:
                    raise KeyError("fileIndex[a][b] has no 'layout' key")
                if "cCount" not in sEntry:
                    raise KeyError("fileIndex[a][b] has no 'cCount' key")
                if "wCount" not in sEntry:
                    raise KeyError("fileIndex[a][b] has no 'wCount' key")
                if "pCount" not in sEntry:
                    raise KeyError("fileIndex[a][b] has no 'pCount' key")
                if "synopsis" not in sEntry:
                    raise KeyError("fileIndex[a][b] has no 'synopsis' key")

                if not sEntry["level"] in H_VALID:
                    raise ValueError("fileIndex[a][b][level] is not a header level")
                if not isinstance(sEntry["title"], str):
                    raise ValueError("fileIndex[a][b][title] is not a string")
                if not isItemLayout(sEntry["layout"]):
                    raise ValueError("fileIndex[a][b][layout] is not an nwItemLayout")
                if not isinstance(sEntry["cCount"], int):
                    raise ValueError("fileIndex[a][b][cCount] is not an integer")
                if not isinstance(sEntry["wCount"], int):
                    raise ValueError("fileIndex[a][b][wCount] is not an integer")
                if not isinstance(sEntry["pCount"], int):
                    raise ValueError("fileIndex[a][b][pCount] is not an integer")
                if not isinstance(sEntry["synopsis"], str):
                    raise ValueError("fileIndex[a][b][synopsis] is not a string")

        return

    def _checkFileMeta(self):
        """Scan the text counts index for errors.
        Warning: This function raises exceptions.
        """
        for tHandle in self._fileMeta:
            if not isHandle(tHandle):
                raise KeyError("fileMeta key is not a handle")

            tEntry = self._fileMeta[tHandle]
            if len(tEntry) != 4:
                raise IndexError("fileMeta[a] expected 4 values")
            if not tEntry[0] in H_VALID:
                raise ValueError("fileMeta[a][0] is not a header level")
            if not isinstance(tEntry[1], int):
                raise ValueError("fileMeta[a][1] is not an integer")
            if not isinstance(tEntry[2], int):
                raise ValueError("fileMeta[a][2] is not an integer")
            if not isinstance(tEntry[3], int):
                raise ValueError("fileMeta[a][3] is not an integer")

        return

# END Class NWIndex


# =============================================================================================== #
#  Simple Word Counter
# =============================================================================================== #

def countWords(theText):
    """Count words in a piece of text, skipping special syntax and
    comments.
    """
    charCount = 0
    wordCount = 0
    paraCount = 0
    prevEmpty = True

    if not isinstance(theText, str):
        return charCount, wordCount, paraCount

    # We need to treat dashes as word separators for counting words.
    # The check+replace apprach is much faster that direct replace for
    # large texts, and a bit slower for small texts, but in the latter
    # case it doesn't matter.
    if nwUnicode.U_ENDASH in theText:
        theText = theText.replace(nwUnicode.U_ENDASH, " ")
    if nwUnicode.U_EMDASH in theText:
        theText = theText.replace(nwUnicode.U_EMDASH, " ")

    for aLine in theText.splitlines():

        countPara = True

        if not aLine:
            prevEmpty = True
            continue
        if aLine[0] == "@" or aLine[0] == "%":
            continue

        if aLine[0] == "[":
            if aLine.startswith(("[NEWPAGE]", "[NEW PAGE]", "[VSPACE]")):
                continue
            elif aLine.startswith("[VSPACE:") and aLine.endswith("]"):
                continue

        elif aLine[0] == "#":
            if aLine[:5] == "#### ":
                aLine = aLine[5:]
                countPara = False
            elif aLine[:4] == "### ":
                aLine = aLine[4:]
                countPara = False
            elif aLine[:3] == "## ":
                aLine = aLine[3:]
                countPara = False
            elif aLine[:2] == "# ":
                aLine = aLine[2:]
                countPara = False
            elif aLine[:3] == "#! ":
                aLine = aLine[3:]
                countPara = False
            elif aLine[:4] == "##! ":
                aLine = aLine[4:]
                countPara = False

        elif aLine[0] == ">" or aLine[-1] == "<":
            if aLine[:2] == ">>":
                aLine = aLine[2:].lstrip(" ")
            elif aLine[:1] == ">":
                aLine = aLine[1:].lstrip(" ")
            if aLine[-2:] == "<<":
                aLine = aLine[:-2].rstrip(" ")
            elif aLine[-1:] == "<":
                aLine = aLine[:-1].rstrip(" ")

        wordCount += len(aLine.split())
        charCount += len(aLine)
        if countPara and prevEmpty:
            paraCount += 1

        prevEmpty = not countPara

    return charCount, wordCount, paraCount
