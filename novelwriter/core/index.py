"""
novelWriter – Project Index
===========================
Data class for the project index of tags, headers and references

File History:
Created: 2019-04-22 [0.0.1] countWords
Created: 2019-05-27 [0.1.4] NWIndex

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import os
import json
import logging

from time import time

from novelwriter.enum import nwItemType, nwItemLayout
from novelwriter.error import logException
from novelwriter.constants import nwFiles, nwKeyWords, nwUnicode
from novelwriter.core.document import NWDoc
from novelwriter.common import checkInt, jsonEncode

logger = logging.getLogger(__name__)

H_VALID = ("H0", "H1", "H2", "H3", "H4")
H_LEVEL = {"H0": 0, "H1": 1, "H2": 2, "H3": 3, "H4": 4}
H_NONE = "T000000"


class NWIndex():

    def __init__(self, theProject):

        self.theProject = theProject

        # Internal
        self._indexBroken = False

        # Indices
        self._tags = {}
        self._items = {}

        # TimeStamps
        self._timeNovel = 0
        self._timeNotes = 0
        self._timeIndex = 0

        return

    @property
    def indexBroken(self):
        return self._indexBroken

    ##
    #  Public Methods
    ##

    def clearIndex(self):
        """Clear the index dictionaries and time stamps.
        """
        self._timeNovel = 0
        self._timeNotes = 0
        self._timeIndex = 0

        self._tags = {}
        self._items = {}

        return

    def deleteHandle(self, tHandle):
        """Delete all entries of a given document handle.
        """
        if tHandle not in self._items:
            return

        logger.debug("Removing item '%s' from the index", tHandle)

        for tTag in self._items[tHandle].allTags():
            self._tags.pop(tTag, None)

        self._items.pop(tHandle, None)

        return

    def reIndexHandle(self, tHandle):
        """Put a file back into the index. This is used when files are
        moved from the archive or trash folders back into the active
        project.
        """
        logger.debug("Re-indexing item '%s'", tHandle)
        if not self.theProject.tree.checkType(tHandle, nwItemType.FILE):
            return False

        theDoc = NWDoc(self.theProject, tHandle)
        theText = theDoc.readDocument()
        self.scanText(tHandle, theText if theText is not None else "")

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
                logException()
                self._indexBroken = True
                return False

            self._tags = theData.get("tagsIndex", {})
            for tHandle, tData in theData.get("itemIndex", {}).items():
                nwItem = self.theProject.tree[tHandle]
                if nwItem is not None:
                    tItem = IndexItem(tHandle, nwItem)
                    tItem.unpackData(tData)
                    self._items[tHandle] = tItem

            nowTime = round(time())
            self._timeNovel = nowTime
            self._timeNotes = nowTime
            self._timeIndex = nowTime

        logger.verbose("Index loaded in %.3f ms", (time() - tStart)*1000)

        self._checkIndex()

        return True

    def saveIndex(self):
        """Save the current index as a json file in the project meta
        data folder.
        """
        logger.debug("Saving index file")
        indexFile = os.path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)
        tStart = time()

        try:
            itemsIndex = {handle: item.packData() for handle, item in self._items.items()}
            with open(indexFile, mode="w+", encoding="utf-8") as outFile:
                outFile.write("{\n")
                outFile.write(f'  "tagsIndex": {jsonEncode(self._tags, n=1, nmax=2)},\n')
                outFile.write(f'  "itemIndex": {jsonEncode(itemsIndex, n=1, nmax=4)}\n')
                outFile.write("}\n")

        except Exception:
            logger.error("Failed to save index file")
            logException()
            return False

        logger.verbose("Index saved in %.3f ms", (time() - tStart)*1000)

        return True

    ##
    #  Index Building
    ##

    def scanText(self, tHandle, theText):
        """Scan a piece of text associated with a handle. This will
        update the indices accordingly. This function takes the handle
        and text as separate inputs as we want to primarily scan the
        files before we save them in which case we already have the
        text.
        """
        theItem = self.theProject.tree[tHandle]
        if theItem is None:
            logger.info("Not indexing unknown item '%s'", tHandle)
            return False
        if theItem.itemType != nwItemType.FILE:
            logger.info("Not indexing non-file item '%s'", tHandle)
            return False

        self.deleteHandle(tHandle)

        # Run word counter for the whole text
        self._items[tHandle] = IndexItem(tHandle, theItem)

        cC, wC, pC = countWords(theText)
        theItem.setCharCount(cC)
        theItem.setWordCount(wC)
        theItem.setParaCount(pC)

        # If the file's meta data is missing, or the file is out of the
        # main project, we don't index the content
        if theItem.itemLayout == nwItemLayout.NO_LAYOUT:
            logger.info("Not indexing no-layout item '%s'", tHandle)
            return False
        if theItem.itemParent is None:
            logger.info("Not indexing orphaned item '%s'", tHandle)
            return False
        if theItem.isInactive():
            logger.debug("Not indexing inactive item '%s'", tHandle)
            return False

        itemClass  = theItem.itemClass
        itemLayout = theItem.itemLayout

        logger.debug("Indexing item with handle '%s'", tHandle)

        # Scan the text content
        nTitle = 0
        theLines = theText.splitlines()
        for nLine, aLine in enumerate(theLines, start=1):
            if len(aLine.strip()) == 0:
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
            hText = aLine[3:].strip()
        elif aLine.startswith("##! "):
            hDepth = "H2"
            hText = aLine[4:].strip()
        else:
            return False

        sTitle = f"T{nLine:06d}"
        tItem = self._items[tHandle]
        tItem.updateLevel(hDepth)
        tItem.addHeading(IndexHeading(sTitle, hDepth, hText))

        return True

    def _indexWordCounts(self, tHandle, theText, nTitle):
        """Count text stats and save the counts to the index.
        """
        cC, wC, pC = countWords(theText)
        sTitle = f"T{nTitle:06d}"
        if tHandle in self._items:
            self._items[tHandle].setHeadingCounts(sTitle, cC, wC, pC)
        return

    def _indexSynopsis(self, tHandle, theText, nTitle):
        """Save the synopsis to the index.
        """
        sTitle = f"T{nTitle:06d}"
        if tHandle in self._items:
            self._items[tHandle].setHeadingSynopsis(sTitle, theText)
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

        sTitle = f"T{nTitle:06d}"
        if theBits[0] == nwKeyWords.TAG_KEY:
            self._tags[theBits[1]] = {
                "handle": tHandle,
                "heading": sTitle,
                "class": itemClass.name,
            }
            if tHandle in self._items:
                self._items[tHandle].setHeadingTag(sTitle, theBits[1])
        else:
            if tHandle in self._items:
                self._items[tHandle].addHeadingReferences(sTitle, theBits[1:], theBits[0])

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
            if theBits[1] in self._tags:
                isGood[1] = self._tags[theBits[1]].get("handle") == tItem.itemHandle
            else:
                isGood[1] = True
            return isGood

        # If we're still here, we check that the references exist
        theKey = nwKeyWords.KEY_CLASS[theBits[0]].name
        for n in range(1, nBits):
            if theBits[n] in self._tags:
                isGood[n] = theKey == self._tags[theBits[n]].get("class")

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
            for sTitle in self._items[tHandle].headings:
                tKey = f"{tHandle}:{sTitle}"
                yield tKey, tHandle, sTitle, self._items[tHandle][sTitle]

    def getNovelWordCount(self, skipExcluded=True):
        """Count the number of words in the novel project.
        """
        wCount = 0
        for tHandle in self._listNovelHandles(skipExcluded):
            for hItem in self._items[tHandle].entries:
                wCount += hItem.wordCount

        return wCount

    def getNovelTitleCounts(self, skipExcluded=True):
        """Count the number of titles in the novel project.
        """
        hCount = [0, 0, 0, 0, 0]
        for tHandle in self._listNovelHandles(skipExcluded):
            for hItem in self._items[tHandle].entries:
                iLevel = H_LEVEL.get(hItem.level, 0)
                hCount[iLevel] += 1

        return hCount

    def getHandleWordCounts(self, tHandle):
        """Get all header word counts for a specific handle.
        """
        return [
            (f"{tHandle}:{sTitle}", hItem.wordCount)
            for sTitle, hItem in self._items.get(tHandle, {}).items()
        ]

    def getHandleHeaders(self, tHandle):
        """Get all headers for a specific handle.
        """
        return [
            (sTitle, hItem.level, hItem.title)
            for sTitle, hItem in self._items.get(tHandle, {}).items()
        ]

    def getHandleHeaderLevel(self, tHandle):
        """Get the header level of the first header of a handle.
        """
        if tHandle in self._items:
            return self._items[tHandle].level
        else:
            return "H0"

    def getTableOfContents(self, maxDepth, skipExcluded=True):
        """Generate a table of contents up to a maximum depth.
        """
        tOrder = []
        tData = {}
        pKey = None
        for tHandle in self._listNovelHandles(skipExcluded):
            for sTitle in self._items[tHandle].headings:
                tKey = f"{tHandle}:{sTitle}"
                hItem = self._items[tHandle][sTitle]
                iLevel = H_LEVEL.get(hItem.level, 0)
                if iLevel > maxDepth:
                    if pKey in tData:
                        tData[pKey]["words"] += hItem.wordCount
                else:
                    pKey = tKey
                    tOrder.append(tKey)
                    tData[tKey] = {
                        "level": iLevel,
                        "title": hItem.title,
                        "words": hItem.wordCount,
                    }

        theToC = [(
            tKey,
            tData[tKey]["level"],
            tData[tKey]["title"],
            tData[tKey]["words"]
        ) for tKey in tOrder]

        return theToC

    def getCounts(self, tHandle, sTitle=None):
        """Return the counts for a file, or a section of a file,
        starting at title sTitle if it is provided.
        """
        cC = 0
        wC = 0
        pC = 0

        if sTitle is None:
            if tHandle in self._items:
                tItem = self._items[tHandle].item
                cC = tItem.charCount
                wC = tItem.wordCount
                pC = tItem.paraCount
        else:
            if tHandle in self._items:
                if sTitle in self._items[tHandle]:
                    hItem = self._items[tHandle][sTitle]
                    cC = hItem.charCount
                    wC = hItem.wordCount
                    pC = hItem.paraCount

        return cC, wC, pC

    def getReferences(self, tHandle, sTitle=None):
        """Extract all references made in a file, and optionally title
        section.
        """
        theRefs = {x: [] for x in nwKeyWords.KEY_CLASS}
        if tHandle not in self._items:
            return theRefs

        for rTitle, hItem in self._items[tHandle].items():
            if sTitle is None or sTitle == rTitle:
                for aTag, refTypes in hItem.references.items():
                    for refType in refTypes:
                        if refType in theRefs:
                            theRefs[refType].append(aTag)

        return theRefs

    def getNovelData(self, tHandle, sTitle):
        """Return the novel data of a given handle and title.
        """
        if tHandle in self._items:
            if sTitle in self._items[tHandle]:
                return self._items[tHandle][sTitle]
        return None

    def getBackReferenceList(self, tHandle):
        """Build a list of files referring back to our file, specified
        by tHandle.
        """
        if tHandle is None or tHandle not in self._items:
            return {}

        theRefs = {}
        theTags = self._items[tHandle].allTags()
        if not theTags:
            return theRefs

        for aHandle, tItem in self._items.items():
            for sTitle, hItem in tItem.items():
                for aTag in hItem.references:
                    if aTag in theTags and aHandle not in theRefs:
                        theRefs[aHandle] = sTitle

        return theRefs

    def getTagSource(self, theTag):
        """Return the source location of a given tag.
        """
        ref = self._tags.get(theTag, {})
        return ref.get("handle"), ref.get("heading", H_NONE)

    ##
    #  Internal Functions
    ##

    def _listNovelHandles(self, skipExcluded):
        """Return a list of all handles that exist in the novel index.
        """
        theHandles = []
        for tItem in self.theProject.tree:
            if tItem is None:
                continue
            if not tItem.isExported and skipExcluded:
                continue
            if tItem.itemLayout == nwItemLayout.NOTE:
                continue
            if tItem.itemHandle in self._items:
                theHandles.append(tItem.itemHandle)

        return theHandles

    ##
    #  Index Checkers
    ##

    def _checkIndex(self):
        """Check that the entries in the index are valid and contain the
        elements it should. Also check that each file present in the
        contents folder when the project was loaded are also present in
        the fileMeta index.
        """
        logger.debug("Checking index")
        tStart = time()

        # If the index was ok, we check that project files are indexed
        for fHandle in self.theProject.projFiles:
            if fHandle not in self._items:
                logger.warning("Item '%s' is not in the index", fHandle)
                self.reIndexHandle(fHandle)

        logger.verbose("Index check completed in %.3f ms", (time() - tStart)*1000)

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
    # The check+replace approach is much faster than direct replace for
    # large texts, and a bit slower for small texts, but in the latter
    # case it doesn't really matter.
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


class IndexItem:

    def __init__(self, tHandle, tItem):
        self._handle = tHandle
        self._item = tItem

        self._level = "H0"
        self._headings = {}
        self._index = 0

        # Add a placeholder heading
        self._headings[H_NONE] = IndexHeading(H_NONE)

        return

    ##
    # Properties
    ##

    @property
    def item(self):
        return self._item

    @property
    def level(self):
        return self._level

    @property
    def headings(self):
        return sorted(self._headings.keys())

    @property
    def entries(self):
        return self._headings.values()

    ##
    #  Setters
    ##

    def setLevel(self, level):
        if level in H_VALID:
            self._level = level
        else:
            self._level = "H0"
        return

    def updateLevel(self, level):
        """Set the level only if it is H0.
        """
        if level in H_VALID and self._level == "H0":
            self._level = level
        else:
            self._level = "H0"
        return

    def addHeading(self, tHeading):
        if H_NONE in self._headings:
            self._headings.pop(H_NONE)
        self._headings[tHeading.key] = tHeading
        return

    def setHeadingCounts(self, sTitle, charCount, wordCount, paraCount):
        if sTitle in self._headings:
            self._headings[sTitle].setCounts(charCount, wordCount, paraCount)
        return

    def setHeadingSynopsis(self, sTitle, synopText):
        if sTitle in self._headings:
            self._headings[sTitle].setSynopsis(synopText)
        return

    def setHeadingTag(self, sTitle, tagKey):
        if sTitle in self._headings:
            self._headings[sTitle].setTag(tagKey)
        return

    def addHeadingReferences(self, sTitle, tagKeys, refType):
        if sTitle in self._headings:
            for tagKey in tagKeys:
                self._headings[sTitle].addReference(tagKey, refType)
        return

    ##
    #  Data Methods
    ##

    def __getitem__(self, sTitle):
        return self._headings.get(sTitle, None)

    def __contains__(self, sTitle):
        return sTitle in self._headings

    def items(self):
        return self._headings.items()

    def allTags(self):
        """Return a list of all tags in the current item.
        """
        tags = []
        for hItem in self._headings.values():
            tag = hItem.tag
            if tag:
                tags.append(tag)
        return tags

    ##
    #  Pack/Unpack
    ##

    def packData(self):
        """Pack the indexed item's data into a dictionary.
        """
        heads = {}
        refs = {}
        for sTitle, hItem in self._headings.items():
            heads[sTitle] = hItem.packData()
            hRefs = hItem.packReferences()
            if hRefs:
                refs[sTitle] = hRefs

        data = {"level": self._level}
        data["headings"] = heads
        if refs:
            data["references"] = refs

        return data

    def unpackData(self, data):
        """Unpack an item entry from the data.
        """
        self._level = data.get("level", "H0")
        references = data.get("references", {})
        for sTitle, hData in data.get("headings", {}).items():
            tHeading = IndexHeading(sTitle)
            tHeading.unpackData(hData)
            tHeading.unpackReferences(references.get(sTitle, {}))
            self.addHeading(tHeading)
        return

# END Class IndexItem


class IndexHeading:

    def __init__(self, key, level="H0", title=""):
        self._key = key
        self._level = level
        self._title = title

        self._charCount = 0
        self._wordCount = 0
        self._paraCount = 0
        self._synopsis = ""

        self._tag = ""
        self._refs = {}

        return

    ##
    #  Properties
    ##

    @property
    def key(self):
        return self._key

    @property
    def level(self):
        return self._level

    @property
    def title(self):
        return self._title

    @property
    def charCount(self):
        return self._charCount

    @property
    def wordCount(self):
        return self._wordCount

    @property
    def paraCount(self):
        return self._paraCount

    @property
    def synopsis(self):
        return self._synopsis

    @property
    def tag(self):
        return self._tag

    @property
    def references(self):
        return self._refs

    ##
    #  Setters
    ##

    def setLevel(self, level):
        if level in H_VALID:
            self._level = level
        else:
            self._level = "H0"
        return

    def setCounts(self, charCount, wordCount, paraCount):
        self._charCount = max(0, checkInt(charCount, 0))
        self._wordCount = max(0, checkInt(wordCount, 0))
        self._paraCount = max(0, checkInt(paraCount, 0))
        return

    def setSynopsis(self, synopText):
        self._synopsis = str(synopText)
        return

    def setTag(self, tagKey):
        self._tag = str(tagKey)
        return

    def addReference(self, tagKey, refType):
        """Add a record of a reference tag, and what keyword types it is
        associated with.
        """
        if tagKey not in self._refs:
            self._refs[tagKey] = set()
        self._refs[tagKey].add(refType)
        return

    ##
    #  Data Methods
    ##

    def packData(self):
        """Pack the values into a dictionary for saving to cache.
        """
        return {
            "level": self._level,
            "title": self._title,
            "tag": self._tag,
            "cCount": self._charCount,
            "wCount": self._wordCount,
            "pCount": self._paraCount,
            "synopsis": self._synopsis,
        }

    def packReferences(self):
        """Pack references into a dictionary for saving to cache.
        """
        return {key: list(value) for key, value in self._refs.items()}

    def unpackData(self, data):
        """Unpack a heading entry from a dictionary.
        """
        self.setLevel(data.get("level", "H0"))
        self._title = str(data.get("title", ""))
        self._tag = str(data.get("tag", ""))
        self.setCounts(
            data.get("cCount", 0),
            data.get("wCount", 0),
            data.get("pCount", 0),
        )
        self._synopsis = str(data.get("synopsis", ""))
        return

    def unpackReferences(self, data):
        """Unpack a set of references from a dictionary.
        """
        for tagKey, refTypes in data.items():
            self._refs[tagKey] = set(refTypes)
        return

# END Class IndexHeading
