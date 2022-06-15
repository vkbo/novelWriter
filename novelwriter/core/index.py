"""
novelWriter – Project Index
===========================
Data class for the project index of tags, headers and references

File History:
Created: 2019-04-22 [0.0.1]  countWords
Created: 2019-05-27 [0.1.4]  NWIndex
Created: 2022-05-28 [1.7rc1] IndexItem, IndexHeading
Created: 2022-05-29 [1.7rc1] TagsIndex, ItemIndex

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
from novelwriter.constants import nwFiles, nwKeyWords, nwUnicode, nwHeaders
from novelwriter.core.document import NWDoc
from novelwriter.common import (
    checkInt, isHandle, isItemClass, isTitleTag, jsonEncode
)

logger = logging.getLogger(__name__)


class NWIndex:
    """This class holds the entire index for a given project. The index
    contains the data that isn't stored in the project items themselves.
    The content of the index is updated every time a file item is saved.

    The primary index data is contained in the ItemIndex class, which
    contains an IndexItem representing each NWItem. Each IndexItem holds
    an IndexHeading object for each heading of the item's text.

    A reverse index of all tags is contained in the TagsIndex class.
    This is duplicate information used for quicker lookups from the tags
    and back to items where they are defined.

    The index data is cached in a JSON file between writing sessions.
    """

    def __init__(self, theProject):

        self.theProject = theProject

        # Storage and State
        self._tagsIndex = TagsIndex()
        self._itemIndex = ItemIndex(theProject)
        self._indexBroken = False

        # TimeStamps
        self._indexChange = 0
        self._rootChange = {}

        return

    def __repr__(self):
        return f"<NWIndex project='{self.theProject.projName}'>"

    ##
    #  Properties
    ##

    @property
    def indexBroken(self):
        return self._indexBroken

    ##
    #  Public Methods
    ##

    def clearIndex(self):
        """Clear the index dictionaries and time stamps.
        """
        self._tagsIndex.clear()
        self._itemIndex.clear()
        self._indexChange = 0
        self._rootChange = {}
        return

    def deleteHandle(self, tHandle):
        """Delete all entries of a given document handle.
        """
        logger.debug("Removing item '%s' from the index", tHandle)
        for tTag in self._itemIndex.allItemTags(tHandle):
            del self._tagsIndex[tTag]

        del self._itemIndex[tHandle]

        return

    def reIndexHandle(self, tHandle):
        """Put a file back into the index. This is used when files are
        moved from the archive or trash folders back into the active
        project.
        """
        if not self.theProject.tree.checkType(tHandle, nwItemType.FILE):
            return False

        logger.debug("Re-indexing item '%s'", tHandle)
        theDoc = NWDoc(self.theProject, tHandle)
        self.scanText(tHandle, theDoc.readDocument() or "")

        return True

    def indexChangedSince(self, checkTime):
        """Check if the index has changed since a given time.
        """
        return self._indexChange > checkTime

    def rootChangedSince(self, rootHandle, checkTime):
        """Check if the index has changed since a given time for a
        given root item.
        """
        return self._rootChange.get(rootHandle, self._indexChange) > checkTime

    ##
    #  Load and Save Index to/from File
    ##

    def loadIndex(self):
        """Load index from last session from the project meta folder.
        """
        theData = {}
        indexFile = os.path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)
        tStart = time()

        self._indexBroken = False
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

            try:
                self._tagsIndex.unpackData(theData["tagsIndex"])
                self._itemIndex.unpackData(theData["itemIndex"])
            except Exception:
                logger.error("The index content is invalid")
                logException()
                self._indexBroken = True
                return False

        logger.debug("Checking index")

        # Check that all files are indexed
        for fHandle in self.theProject.projFiles:
            if fHandle not in self._itemIndex:
                logger.warning("Item '%s' is not in the index", fHandle)
                self.reIndexHandle(fHandle)

        self._indexChange = round(time())

        logger.verbose("Index loaded in %.3f ms", (time() - tStart)*1000)

        return True

    def saveIndex(self):
        """Save the current index as a json file in the project meta
        data folder.
        """
        logger.debug("Saving index file")
        indexFile = os.path.join(self.theProject.projMeta, nwFiles.INDEX_FILE)
        tStart = time()

        try:
            tagsIndex = self._tagsIndex.packData()
            itemIndex = self._itemIndex.packData()
            with open(indexFile, mode="w+", encoding="utf-8") as outFile:
                outFile.write("{\n")
                outFile.write(f'  "tagsIndex": {jsonEncode(tagsIndex, n=1, nmax=2)},\n')
                outFile.write(f'  "itemIndex": {jsonEncode(itemIndex, n=1, nmax=4)}\n')
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
        files before we save them, in which case we already have the
        text.
        """
        theItem = self.theProject.tree[tHandle]
        if theItem is None:
            logger.info("Not indexing unknown item '%s'", tHandle)
            return False
        if theItem.itemType != nwItemType.FILE:
            logger.info("Not indexing non-file item '%s'", tHandle)
            return False

        # Keep a record of existing tags, and create a new item entry
        itemTags = dict.fromkeys(self._itemIndex.allItemTags(tHandle), False)
        self._itemIndex.add(tHandle, theItem)

        # Run word counter for the whole text
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

        logger.debug("Indexing item with handle '%s'", tHandle)

        # Scan the text content
        nTitle = 0
        theLines = theText.splitlines()
        for nLine, aLine in enumerate(theLines, start=1):
            if len(aLine.strip()) == 0:
                continue

            if aLine.startswith("#"):
                isTitle = self._indexTitle(tHandle, aLine, nLine)
                if isTitle and nLine > 0:
                    if nTitle > 0:
                        lastText = "\n".join(theLines[nTitle-1:nLine-1])
                        self._indexWordCounts(tHandle, lastText, nTitle)
                    nTitle = nLine

            elif aLine.startswith("@"):
                self._indexKeyword(tHandle, aLine, nTitle, theItem.itemClass, itemTags)

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

        # Also count words on a page with no titles
        if nTitle == 0:
            self._indexWordCounts(tHandle, theText, nTitle)

        # Prune no longer used tags
        for tTag, isActive in itemTags.items():
            if not isActive:
                logger.verbose("Deleting removed tag '%s'", tTag)
                del self._tagsIndex[tTag]

        # Update timestamps for index changes
        nowTime = round(time())
        self._indexChange = nowTime
        self._rootChange[theItem.itemRoot] = nowTime

        return True

    ##
    #  Internal Indexer Helpers
    ##

    def _indexTitle(self, tHandle, aLine, nTitle):
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

        sTitle = f"T{nTitle:06d}"
        self._itemIndex.addItemHeading(tHandle, sTitle, hDepth, hText)

        return True

    def _indexWordCounts(self, tHandle, theText, nTitle):
        """Count text stats and save the counts to the index.
        """
        sTitle = f"T{nTitle:06d}"
        cC, wC, pC = countWords(theText)
        self._itemIndex.setHeadingCounts(tHandle, sTitle,  cC, wC, pC)
        return

    def _indexSynopsis(self, tHandle, theText, nTitle):
        """Save the synopsis to the index.
        """
        sTitle = f"T{nTitle:06d}"
        self._itemIndex.setHeadingSynopsis(tHandle, sTitle, theText)
        return

    def _indexKeyword(self, tHandle, aLine, nTitle, itemClass, itemTags):
        """Validate and save the information about a reference to a tag
        in another file, or the setting of a tag in the file. A record
        of active tags is updated so that no longer used tags can be
        pruned later.
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
            tagName = theBits[1]
            self._tagsIndex.add(tagName, tHandle, sTitle, itemClass)
            self._itemIndex.setHeadingTag(tHandle, sTitle, tagName)
            itemTags[tagName] = True
        else:
            self._itemIndex.addHeadingReferences(tHandle, sTitle, theBits[1:], theBits[0])

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
            if theBits[1] in self._tagsIndex:
                isGood[1] = self._tagsIndex.tagHandle(theBits[1]) == tItem.itemHandle
            else:
                isGood[1] = True
            return isGood

        # If we're still here, we check that the references exist
        theKey = nwKeyWords.KEY_CLASS[theBits[0]].name
        for n in range(1, nBits):
            if theBits[n] in self._tagsIndex:
                isGood[n] = self._tagsIndex.tagClass(theBits[n]) == theKey

        return isGood

    ##
    #  Extract Data
    ##

    def novelStructure(self, rootHandle=None, skipExcl=True):
        """Iterate over all titles in the novel, in the correct order as
        they appear in the tree view and in the respective document
        files, but skipping all note files.
        """
        novStruct = self._itemIndex.iterNovelStructure(rootHandle=rootHandle, skipExcl=skipExcl)
        for tHandle, sTitle, hItem in novStruct:
            yield f"{tHandle}:{sTitle}", tHandle, sTitle, hItem
        return

    def getNovelWordCount(self, skipExcl=True):
        """Count the number of words in the novel project.
        """
        wCount = 0
        for _, _, hItem in self._itemIndex.iterNovelStructure(skipExcl=skipExcl):
            wCount += hItem.wordCount
        return wCount

    def getNovelTitleCounts(self, skipExcl=True):
        """Count the number of titles in the novel project.
        """
        hCount = [0, 0, 0, 0, 0]
        for _, _, hItem in self._itemIndex.iterNovelStructure(skipExcl=skipExcl):
            iLevel = nwHeaders.H_LEVEL.get(hItem.level, 0)
            hCount[iLevel] += 1
        return hCount

    def getHandleWordCounts(self, tHandle):
        """Get all header word counts for a specific handle.
        """
        return [
            (f"{tHandle}:{sTitle}", hItem.wordCount)
            for sTitle, hItem in self._itemIndex.iterItemHeaders(tHandle)
        ]

    def getHandleHeaders(self, tHandle):
        """Get all headers for a specific handle.
        """
        return [
            (sTitle, hItem.level, hItem.title)
            for sTitle, hItem in self._itemIndex.iterItemHeaders(tHandle)
        ]

    def getHandleHeaderLevel(self, tHandle):
        """Get the header level of the first header of a handle.
        """
        return self._itemIndex.mainItemHeader(tHandle)

    def getTableOfContents(self, maxDepth, skipExcl=True):
        """Generate a table of contents up to a maximum depth.
        """
        tOrder = []
        tData = {}
        pKey = None
        for tHandle, sTitle, hItem in self._itemIndex.iterNovelStructure(skipExcl=skipExcl):
            tKey = f"{tHandle}:{sTitle}"
            iLevel = nwHeaders.H_LEVEL.get(hItem.level, 0)
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
        tItem = self._itemIndex[tHandle]
        if tItem is None:
            return 0, 0, 0

        if sTitle is None:
            cItem = tItem.item
        else:
            cItem = tItem[sTitle]

        if cItem is not None:
            return cItem.charCount, cItem.wordCount, cItem.paraCount

        return 0, 0, 0

    def getReferences(self, tHandle, sTitle=None):
        """Extract all references made in a file, and optionally title
        section.
        """
        theRefs = {x: [] for x in nwKeyWords.KEY_CLASS}
        for rTitle, hItem in self._itemIndex.iterItemHeaders(tHandle):
            if sTitle is None or sTitle == rTitle:
                for aTag, refTypes in hItem.references.items():
                    for refType in refTypes:
                        if refType in theRefs:
                            theRefs[refType].append(aTag)

        return theRefs

    def getNovelData(self, tHandle, sTitle):
        """Return the novel data of a given handle and title.
        """
        if tHandle in self._itemIndex:
            return self._itemIndex[tHandle][sTitle]
        return None

    def getBackReferenceList(self, tHandle):
        """Build a list of files referring back to our file, specified
        by tHandle.
        """
        if tHandle is None or tHandle not in self._itemIndex:
            return {}

        theRefs = {}
        theTags = self._itemIndex.allItemTags(tHandle)
        if not theTags:
            return theRefs

        for aHandle, sTitle, hItem in self._itemIndex.iterAllHeaders():
            for aTag in hItem.references:
                if aTag in theTags and aHandle not in theRefs:
                    theRefs[aHandle] = sTitle

        return theRefs

    def getTagSource(self, theTag):
        """Return the source location of a given tag.
        """
        tHandle = self._tagsIndex.tagHandle(theTag)
        sTitle = self._tagsIndex.tagHeading(theTag)
        return tHandle, sTitle

# END Class NWIndex


# =============================================================================================== #
#  The Tags Index Object
# =============================================================================================== #

class TagsIndex:
    """A wrapper class that holds the reverse lookup tags index. This is
    just a simple wrapper around a single dictionary to keep tighter
    control of the keys.
    """

    def __init__(self):
        self._tags = {}
        return

    ##
    #  Methods
    ##

    def clear(self):
        """Clear the index.
        """
        self._tags = {}
        return

    def __contains__(self, tagKey):
        """Check if a tag exists in the index,
        """
        return tagKey in self._tags

    def __delitem__(self, tagKey):
        """Delete an entry in the index.
        """
        self._tags.pop(tagKey, None)
        return

    def __getitem__(self, tagKey):
        """Return a tag, or return None if it isn't found.
        """
        return self._tags.get(tagKey, None)

    def add(self, tagKey, tHandle, sTitle, itemClass):
        """Add a key to the index and set all values.
        """
        self._tags[tagKey] = {
            "handle": tHandle, "heading": sTitle, "class": itemClass.name
        }
        return

    def tagHandle(self, tagKey):
        """Get the handle of a given tag.
        """
        if tagKey in self._tags:
            return self._tags.get(tagKey).get("handle")
        return None

    def tagHeading(self, tagKey):
        """Get the heading of a given tag.
        """
        if tagKey in self._tags:
            return self._tags.get(tagKey).get("heading")
        return nwHeaders.TT_NONE

    def tagClass(self, tagKey):
        """Get the class of a given tag.
        """
        if tagKey in self._tags:
            return self._tags.get(tagKey).get("class")
        return None

    ##
    #  Pack/Unpack
    ##

    def packData(self):
        """Pack all the data of the tags into a single dictionary.
        """
        return self._tags

    def unpackData(self, data):
        """Iterate through the tagsIndex loaded from cache and check
        that it's valid.
        """
        self._tags = {}
        if not isinstance(data, dict):
            raise ValueError("tagsIndex is not a dict")

        for tagKey, tagData in data.items():
            if not isinstance(tagKey, str):
                raise ValueError("tagsIndex keys must be a strings")
            if "handle" not in tagData:
                raise KeyError("A tagIndex item is missing a handle entry")
            if "heading" not in tagData:
                raise KeyError("A tagIndex item is missing a heading entry")
            if "class" not in tagData:
                raise KeyError("A tagIndex item is missing a class entry")
            if not isHandle(tagData["handle"]):
                raise ValueError("tagsIndex handle must be a handle")
            if not isTitleTag(tagData["heading"]):
                raise ValueError("tagsIndex heading must be a title tag")
            if not isItemClass(tagData["class"]):
                raise ValueError("tagsIndex handle must be an nwItemClass")

        self._tags = data

        return

# END Class TagsIndex


# =============================================================================================== #
#  The Item Index Objects
# =============================================================================================== #

class ItemIndex:
    """A wrapper object holding the indexed items. This is a warapper
    class around a single storage dictionary with a set of utility
    functions for setting and accessing the index data. Each indexed
    item is stored in an IndexItem object, which again holds an
    IndexHeading object for each header of the text.
    """

    def __init__(self, theProject):
        self.theProject = theProject
        self._items = {}
        return

    ##
    #  Methods
    ##

    def clear(self):
        """Clear the index.
        """
        self._items = {}
        return

    def __contains__(self, tHandle):
        """Check if an item exists in the index,
        """
        return tHandle in self._items

    def __delitem__(self, tHandle):
        """Delete an entry in the index.
        """
        self._items.pop(tHandle, None)
        return

    def __getitem__(self, tHandle):
        """Return an item, or return None if it isn't found.
        """
        return self._items.get(tHandle, None)

    def add(self, tHandle, tItem):
        """Add a new item to the index. This will overwrite the item if
        it already exists.
        """
        self._items[tHandle] = IndexItem(tHandle, tItem)
        return

    def mainItemHeader(self, tHandle):
        """Return the primary item header for an item.
        """
        if tHandle in self._items:
            return self._items[tHandle].level
        return "H0"

    def allItemTags(self, tHandle):
        """Get all tags set for headings of an item.
        """
        if tHandle in self._items:
            return self._items[tHandle].allTags()
        return []

    def iterItemHeaders(self, tHandle):
        """Iterate over all item headers of an item.
        """
        if tHandle in self._items:
            for sTitle, hItem in self._items[tHandle].items():
                yield sTitle, hItem
        return

    def iterAllHeaders(self):
        """Iterate through all items and headings in the index.
        """
        for tHandle, tItem in self._items.items():
            for sTitle, hItem in tItem.items():
                yield tHandle, sTitle, hItem
        return

    def iterNovelStructure(self, rootHandle=None, skipExcl=False):
        """Iterate over all items and headers in the novel structure for
        a given root handle, or for all if root handle is None.
        """
        for tItem in self.theProject.tree:
            if tItem is None:
                continue
            if tItem.itemLayout == nwItemLayout.NOTE:
                continue
            if skipExcl and not tItem.isExported:
                continue

            tHandle = tItem.itemHandle
            if tHandle not in self._items:
                continue

            if rootHandle is None:
                for sTitle in self._items[tHandle].headings():
                    yield tHandle, sTitle, self._items[tHandle][sTitle]
            elif tItem.itemRoot == rootHandle:
                for sTitle in self._items[tHandle].headings():
                    yield tHandle, sTitle, self._items[tHandle][sTitle]
            else:
                continue

        return

    ##
    #  Setters
    ##

    def addItemHeading(self, tHandle, sTitle, hDepth, hText):
        """Set the main heading level of an item.
        """
        if tHandle in self._items:
            tItem = self._items[tHandle]
            tItem.updateLevel(hDepth)
            tItem.addHeading(IndexHeading(sTitle, hDepth, hText))
        return

    def setHeadingCounts(self, tHandle, sTitle, cC, wC, pC):
        """Set the character, word and paragraph counts of a heading
        on a given item.
        """
        if tHandle in self._items:
            self._items[tHandle].setHeadingCounts(sTitle, cC, wC, pC)
        return

    def setHeadingSynopsis(self, tHandle, sTitle, sText):
        """Set the synopsis text for a heading on a given item.
        """
        if tHandle in self._items:
            self._items[tHandle].setHeadingSynopsis(sTitle, sText)
        return

    def setHeadingTag(self, tHandle, sTitle, tagKey):
        """Set the main tag for a heading on a given item.
        """
        if tHandle in self._items:
            self._items[tHandle].setHeadingTag(sTitle, tagKey)
        return

    def addHeadingReferences(self, tHandle, sTitle, tagKeys, refType):
        """Set the reference tags for a heading on a given item.
        """
        if tHandle in self._items:
            self._items[tHandle].addHeadingReferences(sTitle, tagKeys, refType)
        return

    ##
    #  Pack/Unpack
    ##

    def packData(self):
        """Pack all the data of the index into a single dictionary.
        """
        return {handle: item.packData() for handle, item in self._items.items()}

    def unpackData(self, data):
        """Iterate through the itemIndex loaded from cache and check
        that it's valid. This will raise errors if there is a problem.
        """
        self._items = {}
        if not isinstance(data, dict):
            raise ValueError("itemIndex is not a dict")

        for tHandle, tData in data.items():
            if not isHandle(tHandle):
                raise ValueError("itemIndex keys must be handles")

            nwItem = self.theProject.tree[tHandle]
            if nwItem is not None:
                tItem = IndexItem(tHandle, nwItem)
                tItem.unpackData(tData)
                self._items[tHandle] = tItem

        return

# END Class ItemIndex


class IndexItem:
    """This object represents the index data of a project item (NWItem).
    It holds a record of all the headings in the text, and the meta data
    associated with each heading. It also holds a pointer to the project
    item. The main heading level of the item is also held here since it
    must be reset each time the item is re-indexed.
    """

    def __init__(self, tHandle, tItem):
        self._handle = tHandle
        self._item = tItem
        self._level = "H0"
        self._headings = {}
        self._index = 0

        # Add a placeholder heading
        self._headings[nwHeaders.TT_NONE] = IndexHeading(nwHeaders.TT_NONE)

        return

    def __repr__(self):
        return f"<IndexItem handle='{self._handle}'>"

    ##
    # Properties
    ##

    @property
    def item(self):
        return self._item

    @property
    def level(self):
        return self._level

    ##
    #  Setters
    ##

    def updateLevel(self, level):
        """Set the level only if it has not already been set.
        """
        if self._level == "H0":
            self._level = level
        return

    def addHeading(self, tHeading):
        """Add a heading to the item. Also remove the placeholder entry
        if it exists.
        """
        if nwHeaders.TT_NONE in self._headings:
            self._headings.pop(nwHeaders.TT_NONE)
        self._headings[tHeading.key] = tHeading
        return

    def setHeadingCounts(self, sTitle, charCount, wordCount, paraCount):
        """Set the character, word and paragraph count of a heading.
        """
        if sTitle in self._headings:
            self._headings[sTitle].setCounts(charCount, wordCount, paraCount)
        return

    def setHeadingSynopsis(self, sTitle, synopText):
        """Set the synopsis text of a heading.
        """
        if sTitle in self._headings:
            self._headings[sTitle].setSynopsis(synopText)
        return

    def setHeadingTag(self, sTitle, tagKey):
        """Set the tag of a heading.
        """
        if sTitle in self._headings:
            self._headings[sTitle].setTag(tagKey)
        return

    def addHeadingReferences(self, sTitle, tagKeys, refType):
        """Add a reference key and all its types to a heading.
        """
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

    def headings(self):
        return sorted(self._headings.keys())

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
            if not isTitleTag(sTitle):
                raise ValueError("The itemIndex contains an invalid title key")
            tHeading = IndexHeading(sTitle)
            tHeading.unpackData(hData)
            tHeading.unpackReferences(references.get(sTitle, {}))
            self.addHeading(tHeading)
        return

# END Class IndexItem


class IndexHeading:
    """This object represents a section of text in a project item
    associated with a single (valid) heading. It holds a separate record
    of all references made under each heading.
    """

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

    def __repr__(self):
        return f"<IndexHeading key='{self._key}'>"

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
        """Set the level of the header if it's a valid value.
        """
        if level in nwHeaders.H_VALID:
            self._level = level
        return

    def setCounts(self, charCount, wordCount, paraCount):
        """Set the character, word and paragraph count. Make sure the
        value is an integer and is not smaller than 0.
        """
        self._charCount = max(0, checkInt(charCount, 0))
        self._wordCount = max(0, checkInt(wordCount, 0))
        self._paraCount = max(0, checkInt(paraCount, 0))
        return

    def setSynopsis(self, synopText):
        """Set the synopsis text and make sure it is a string.
        """
        self._synopsis = str(synopText)
        return

    def setTag(self, tagKey):
        """Set the tag for references, and make sure it is a string.
        """
        self._tag = str(tagKey)
        return

    def addReference(self, tagKey, refType):
        """Add a record of a reference tag, and what keyword types it is
        associated with.
        """
        if refType in nwKeyWords.VALID_KEYS:
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
        Multiple types are packed into a sorted, comma separated string.
        It is sorted to prevent creating unnecessary diffs as the order
        of a set is not guaranteed.
        """
        return {key: ",".join(sorted(list(value))) for key, value in self._refs.items()}

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
            if not isinstance(tagKey, str):
                raise ValueError("itemIndex reference key must be a string")
            if not isinstance(refTypes, str):
                raise ValueError("itemIndex reference type must be a string")
            for refType in refTypes.split(","):
                if refType in nwKeyWords.VALID_KEYS:
                    self.addReference(tagKey, refType)
                else:
                    raise ValueError("The itemIndex contains an invalid reference type")
        return

# END Class IndexHeading


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
