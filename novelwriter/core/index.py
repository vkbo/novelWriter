"""
novelWriter – Project Index
===========================

File History:
Created: 2019-04-22 [0.0.1]  countWords
Created: 2019-05-27 [0.1.4]  NWIndex
Created: 2022-05-28 [2.0rc1] IndexItem
Created: 2022-05-28 [2.0rc1] IndexHeading
Created: 2022-05-29 [2.0rc1] TagsIndex
Created: 2022-05-29 [2.0rc1] ItemIndex

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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
from __future__ import annotations

import json
import logging

from time import time
from typing import TYPE_CHECKING, ItemsView, Iterable, Iterator
from pathlib import Path

from novelwriter.enum import nwItemClass, nwItemType, nwItemLayout
from novelwriter.error import logException
from novelwriter.common import checkInt, isHandle, isItemClass, isTitleTag, jsonEncode
from novelwriter.constants import nwFiles, nwKeyWords, nwUnicode, nwHeaders

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.item import NWItem
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)

TT_NONE = "T0000"


class NWIndex:
    """Core: Project Index

    This class holds the entire index for a given project. The index
    contains the data that isn't stored in the project items themselves.
    The content of the index is updated every time a file item is saved.

    Some information needed by the NWItem object of a project item can
    only be known after a text file has been scanned by the indexer, so
    this data is set directly by the indexer class in the NWItem object.

    The primary index data is contained in a single instance of the
    ItemIndex class. This object contains an IndexItem representing each
    NWItem of the project. Each IndexItem holds an IndexHeading object
    for each heading of the item's text.

    A reverse index of all tags is contained in a single instance of the
    TagsIndex class. This is duplicate information used for quicker
    lookups from the tags and back to items where they are defined.

    The index data is cached in a JSON file between writing sessions in
    order to save startup time. The cached index is validated on input,
    and a broken flag set if it is not valid. If it is invalid, the
    loaded data is cleared and it is up to the calling code to initiate
    a rebuild of the index data.
    """

    def __init__(self, project: NWProject) -> None:

        self._project = project

        # Storage and State
        self._tagsIndex = TagsIndex()
        self._itemIndex = ItemIndex(project)
        self._indexBroken = False

        # TimeStamps
        self._indexChange = 0.0
        self._rootChange = {}

        return

    def __repr__(self) -> str:
        return f"<NWIndex project='{self._project.data.name}'>"

    ##
    #  Properties
    ##

    @property
    def indexBroken(self) -> bool:
        return self._indexBroken

    ##
    #  Public Methods
    ##

    def clearIndex(self) -> None:
        """Clear the index dictionaries and time stamps."""
        self._tagsIndex.clear()
        self._itemIndex.clear()
        self._indexChange = 0.0
        self._rootChange = {}
        return

    def rebuildIndex(self) -> None:
        """Rebuild the entire index from scratch."""
        self.clearIndex()
        for nwItem in self._project.tree:
            if nwItem.isFileType():
                tHandle = nwItem.itemHandle
                theDoc = self._project.storage.getDocument(tHandle)
                self.scanText(tHandle, theDoc.readDocument() or "")
        self._indexBroken = False
        return

    def deleteHandle(self, tHandle: str) -> None:
        """Delete all entries of a given document handle."""
        logger.debug("Removing item '%s' from the index", tHandle)
        for tTag in self._itemIndex.allItemTags(tHandle):
            del self._tagsIndex[tTag]
        del self._itemIndex[tHandle]
        return

    def reIndexHandle(self, tHandle: str | None) -> bool:
        """Put a file back into the index. This is used when files are
        moved from the archive or trash folders back into the active
        project.
        """
        if tHandle is None or not self._project.tree.checkType(tHandle, nwItemType.FILE):
            return False

        logger.debug("Re-indexing item '%s'", tHandle)
        theDoc = self._project.storage.getDocument(tHandle)
        self.scanText(tHandle, theDoc.readDocument() or "")

        return True

    def indexChangedSince(self, checkTime: int | float) -> bool:
        """Check if the index has changed since a given time."""
        return self._indexChange > float(checkTime)

    def rootChangedSince(self, rootHandle: str, checkTime: int | float) -> bool:
        """Check if the index has changed since a given time for a
        given root item.
        """
        return self._rootChange.get(rootHandle, self._indexChange) > float(checkTime)

    ##
    #  Load and Save Index to/from File
    ##

    def loadIndex(self) -> bool:
        """Load index from last session from the project meta folder."""
        indexFile = self._project.storage.getMetaFile(nwFiles.INDEX_FILE)
        if not isinstance(indexFile, Path):
            return False

        theData = {}
        tStart = time()

        self._indexBroken = False
        if indexFile.exists():
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
                self._tagsIndex.unpackData(theData["novelWriter.tagsIndex"])
                self._itemIndex.unpackData(theData["novelWriter.itemIndex"])
            except Exception:
                logger.error("The index content is invalid")
                logException()
                self._indexBroken = True
                return False

        logger.debug("Checking index")

        # Check that all files are indexed
        for fHandle in self._project.storage.scanContent():
            if fHandle not in self._itemIndex:
                logger.warning("Item '%s' is not in the index", fHandle)
                self.reIndexHandle(fHandle)

        self._indexChange = time()

        logger.debug("Index loaded in %.3f ms", (time() - tStart)*1000)

        return True

    def saveIndex(self) -> bool:
        """Save the current index as a json file in the project meta
        data folder.
        """
        indexFile = self._project.storage.getMetaFile(nwFiles.INDEX_FILE)
        if not isinstance(indexFile, Path):
            return False

        logger.debug("Saving index file")
        tStart = time()

        try:
            tagsIndex = jsonEncode(self._tagsIndex.packData(), n=1, nmax=2)
            itemIndex = jsonEncode(self._itemIndex.packData(), n=1, nmax=4)
            with open(indexFile, mode="w+", encoding="utf-8") as outFile:
                outFile.write("{\n")
                outFile.write(f'  "novelWriter.tagsIndex": {tagsIndex},\n')
                outFile.write(f'  "novelWriter.itemIndex": {itemIndex}\n')
                outFile.write("}\n")

        except Exception:
            logger.error("Failed to save index file")
            logException()
            return False

        logger.debug("Index saved in %.3f ms", (time() - tStart)*1000)

        return True

    ##
    #  Index Building
    ##

    def scanText(self, tHandle: str, theText: str) -> bool:
        """Scan a piece of text associated with a handle. This will
        update the indices accordingly. This function takes the handle
        and text as separate inputs as we want to primarily scan the
        files before we save them, in which case we already have the
        text.
        """
        theItem = self._project.tree[tHandle]
        if theItem is None:
            logger.info("Not indexing unknown item '%s'", tHandle)
            return False
        if not theItem.isFileType():
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

        logger.debug("Indexing item with handle '%s'", tHandle)
        if theItem.isInactiveClass():
            self._scanInactive(theItem, theText)
        else:
            self._scanActive(tHandle, theItem, theText, itemTags)

        # Update timestamps for index changes
        nowTime = time()
        self._indexChange = nowTime
        self._rootChange[theItem.itemRoot] = nowTime

        return True

    ##
    #  Internal Indexer Helpers
    ##

    def _scanActive(self, tHandle: str, nwItem: NWItem, text: str, tags: dict) -> None:
        """Scan an active document for meta data."""
        nTitle = 0           # Line Number of the previous title
        cTitle = TT_NONE     # Tag of the current title
        pTitle = TT_NONE     # Tag of the previous title
        canSetHeader = True  # First header has not yet been set

        theLines = text.splitlines()
        for nLine, aLine in enumerate(theLines, start=1):

            if aLine.strip() == "":
                continue

            if aLine.startswith("#"):
                hDepth, hText = self._splitHeading(aLine)
                if hDepth == "H0":
                    continue

                if canSetHeader:
                    nwItem.setMainHeading(hDepth)
                    canSetHeader = False

                cTitle = self._itemIndex.addItemHeading(tHandle, nLine, hDepth, hText)
                if cTitle != TT_NONE:
                    if nTitle > 0:
                        # We have a new title, so we need to count the words of the previous one
                        lastText = "\n".join(theLines[nTitle-1:nLine-1])
                        self._indexWordCounts(tHandle, lastText, pTitle)
                    nTitle = nLine
                    pTitle = cTitle

            elif aLine.startswith("@"):
                if cTitle != TT_NONE:
                    self._indexKeyword(tHandle, aLine, cTitle, nwItem.itemClass, tags)

            elif aLine.startswith("%"):
                if cTitle != TT_NONE:
                    toCheck = aLine[1:].lstrip()
                    synTag = toCheck[:9].lower()
                    tLen = len(aLine)
                    cLen = len(toCheck)
                    cOff = tLen - cLen
                    if synTag == "synopsis:":
                        sText = aLine[cOff+9:].strip()
                        self._itemIndex.setHeadingSynopsis(tHandle, cTitle, sText)

        # Count words for remaining text after last heading
        if pTitle != TT_NONE:
            lastText = "\n".join(theLines[nTitle-1:])
            self._indexWordCounts(tHandle, lastText, pTitle)

        # Also count words on a page with no titles
        if cTitle == TT_NONE:
            self._indexWordCounts(tHandle, text, cTitle)

        # Prune no longer used tags
        for tTag, isActive in tags.items():
            if not isActive:
                logger.debug("Deleting removed tag '%s'", tTag)
                del self._tagsIndex[tTag]

        return

    def _scanInactive(self, nwItem: NWItem, text: str) -> None:
        """Scan an inactive document for meta data."""
        for aLine in text.splitlines():
            if aLine.startswith("#"):
                hDepth, _ = self._splitHeading(aLine)
                if hDepth != "H0":
                    nwItem.setMainHeading(hDepth)
                    break
        return

    def _splitHeading(self, line: str) -> tuple[str, str]:
        """Split a heading into its header level and text value."""
        if line.startswith("# "):
            return "H1", line[2:].strip()
        elif line.startswith("## "):
            return "H2", line[3:].strip()
        elif line.startswith("### "):
            return "H3", line[4:].strip()
        elif line.startswith("#### "):
            return "H4", line[5:].strip()
        elif line.startswith("#! "):
            return "H1", line[3:].strip()
        elif line.startswith("##! "):
            return "H2", line[4:].strip()
        return "H0", ""

    def _indexWordCounts(self, tHandle: str, text: str, sTitle: str):
        """Count text stats and save the counts to the index."""
        cC, wC, pC = countWords(text)
        self._itemIndex.setHeadingCounts(tHandle, sTitle, cC, wC, pC)
        return

    def _indexKeyword(self, tHandle: str, line: str, sTitle: str,
                      itemClass: nwItemClass, tags: dict) -> None:
        """Validate and save the information about a reference to a tag
        in another file, or the setting of a tag in the file. A record
        of active tags is updated so that no longer used tags can be
        pruned later.
        """
        isValid, theBits, _ = self.scanThis(line)
        if not isValid or len(theBits) < 2:
            logger.warning("Skipping keyword with %d value(s) in '%s'", len(theBits), tHandle)
            return

        if theBits[0] not in nwKeyWords.VALID_KEYS:
            logger.warning("Skipping invalid keyword '%s' in '%s'", theBits[0], tHandle)
            return

        if theBits[0] == nwKeyWords.TAG_KEY:
            tagName = theBits[1]
            self._tagsIndex.add(tagName, tHandle, sTitle, itemClass)
            self._itemIndex.setHeadingTag(tHandle, sTitle, tagName)
            tags[tagName] = True
        else:
            self._itemIndex.addHeadingReferences(tHandle, sTitle, theBits[1:], theBits[0])

        return

    ##
    #  Check @ Lines
    ##

    def scanThis(self, line: str) -> tuple[bool, list[str], list[int]]:
        """Scan a line starting with @ to check that it's valid. Then
        split it up into its elements and positions as two arrays.
        """
        tBits = []  # The elements of the string
        tPos  = []  # The absolute position of each element

        line = line.rstrip()  # Remove all trailing white spaces
        nChar = len(line)
        if nChar < 2:
            return False, tBits, tPos
        if line[0] != "@":
            return False, tBits, tPos

        cKey, _, cVals = line.partition(":")
        sKey = cKey.strip()
        if sKey == "@":
            return False, tBits, tPos

        cPos = 0
        tBits.append(sKey)
        tPos.append(cPos)
        cPos += len(cKey) + 1

        if not cVals:
            # No values, so we're done
            return True, tBits, tPos

        for cVal in cVals.split(","):
            sVal = cVal.strip()
            rLen = len(cVal.lstrip())
            tLen = len(cVal)
            tBits.append(sVal)
            tPos.append(cPos + tLen - rLen)
            cPos += tLen + 1

        return True, tBits, tPos

    def checkThese(self, tBits: list[str], nwItem: NWItem) -> list[bool]:
        """Check the tags against the index to see if they are valid
        tags. This is needed for syntax highlighting.
        """
        nBits = len(tBits)
        isGood = [False]*nBits
        if nBits == 0:
            return []

        # Check that the key is valid
        isGood[0] = tBits[0] in nwKeyWords.VALID_KEYS
        if not isGood[0] or nBits == 1:
            return isGood

        # For a tag, only the first value is accepted, the rest are ignored
        if tBits[0] == nwKeyWords.TAG_KEY and nBits > 1:
            if tBits[1] in self._tagsIndex:
                isGood[1] = self._tagsIndex.tagHandle(tBits[1]) == nwItem.itemHandle
            else:
                isGood[1] = True
            return isGood

        # If we're still here, we check that the references exist
        theKey = nwKeyWords.KEY_CLASS[tBits[0]].name
        for n in range(1, nBits):
            if tBits[n] in self._tagsIndex:
                isGood[n] = self._tagsIndex.tagClass(tBits[n]) == theKey

        return isGood

    ##
    #  Extract Data
    ##

    def getItemData(self, tHandle: str) -> IndexItem | None:
        """Get the index data for a given item."""
        return self._itemIndex[tHandle]

    def getItemHeader(self, tHandle: str, sTitle: str) -> IndexHeading | None:
        """Get the header entry for a specific item and heading."""
        tItem = self._itemIndex[tHandle]
        if isinstance(tItem, IndexItem):
            return tItem[sTitle]
        return None

    def novelStructure(
        self, rootHandle: str | None = None, skipExcl: bool = True
    ) -> Iterator[tuple[str, str, str, IndexHeading]]:
        """Iterate over all titles in the novel, in the correct order as
        they appear in the tree view and in the respective document
        files, but skipping all note files.
        """
        novStruct = self._itemIndex.iterNovelStructure(rHandle=rootHandle, skipExcl=skipExcl)
        for tHandle, sTitle, hItem in novStruct:
            yield f"{tHandle}:{sTitle}", tHandle, sTitle, hItem
        return

    def getNovelWordCount(self, skipExcl: bool = True) -> int:
        """Count the number of words in the novel project."""
        wCount = 0
        for _, _, hItem in self._itemIndex.iterNovelStructure(skipExcl=skipExcl):
            wCount += hItem.wordCount
        return wCount

    def getNovelTitleCounts(self, skipExcl: bool = True) -> list[int]:
        """Count the number of titles in the novel project."""
        hCount = [0, 0, 0, 0, 0]
        for _, _, hItem in self._itemIndex.iterNovelStructure(skipExcl=skipExcl):
            iLevel = nwHeaders.H_LEVEL.get(hItem.level, 0)
            hCount[iLevel] += 1
        return hCount

    def getHandleHeaderCount(self, tHandle: str) -> int:
        """Get the number of headers in an item."""
        tItem = self._itemIndex[tHandle]
        if isinstance(tItem, IndexItem):
            return len(tItem)
        return 0

    def getTableOfContents(
        self, rHandle: str, maxDepth: int, skipExcl: bool = True
    ) -> list[tuple[str, str, str, int]]:
        """Generate a table of contents up to a maximum depth."""
        tOrder = []
        tData = {}
        pKey = None
        for tHandle, sTitle, hItem in self._itemIndex.iterNovelStructure(
            rHandle=rHandle, skipExcl=skipExcl
        ):
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

    def getCounts(self, tHandle: str, sTitle: str | None = None) -> tuple[int, int, int]:
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

    def getReferences(self, tHandle: str, sTitle: str | None = None) -> dict[str, list[str]]:
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

    def getBackReferenceList(self, tHandle: str) -> dict[str, str]:
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

    def getTagSource(self, tagKey: str) -> tuple[str, str]:
        """Return the source location of a given tag."""
        tHandle = self._tagsIndex.tagHandle(tagKey)
        sTitle = self._tagsIndex.tagHeading(tagKey)
        return tHandle, sTitle

# END Class NWIndex


# =============================================================================================== #
#  The Tags Index Object
# =============================================================================================== #

class TagsIndex:
    """Core: Tags Index Wrapper Class

    A wrapper class that holds the reverse lookup tags index. This is
    just a simple wrapper around a single dictionary to keep tighter
    control of the keys.
    """

    __slots__ = ("_tags")

    def __init__(self):
        self._tags: dict[str, dict] = {}
        return

    def __contains__(self, tagKey):
        return tagKey in self._tags

    def __delitem__(self, tagKey):
        self._tags.pop(tagKey, None)
        return

    def __getitem__(self, tagKey):
        return self._tags.get(tagKey, None)

    ##
    #  Methods
    ##

    def clear(self):
        """Clear the index."""
        self._tags = {}
        return

    def add(self, tagKey: str, tHandle: str, sTitle: str, itemClass: nwItemClass):
        """Add a key to the index and set all values."""
        self._tags[tagKey] = {
            "handle": tHandle, "heading": sTitle, "class": itemClass.name
        }
        return

    def tagHandle(self, tagKey: str) -> str:
        """Get the handle of a given tag."""
        return self._tags.get(tagKey, {}).get("handle", None)

    def tagHeading(self, tagKey: str) -> str:
        """Get the heading of a given tag."""
        return self._tags.get(tagKey, {}).get("heading", TT_NONE)

    def tagClass(self, tagKey: str) -> str | None:
        """Get the class of a given tag."""
        return self._tags.get(tagKey, {}).get("class", None)

    ##
    #  Pack/Unpack
    ##

    def packData(self) -> dict:
        """Pack all the data of the tags into a single dictionary."""
        return self._tags

    def unpackData(self, data: dict):
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
    """Core: Item Index Wrapper Class

    A wrapper object holding the indexed items. This is a wrapper
    class around a single storage dictionary with a set of utility
    functions for setting and accessing the index data. Each indexed
    item is stored in an IndexItem object, which again holds an
    IndexHeading object for each header of the text.
    """

    __slots__ = ("_project", "_items")

    def __init__(self, project: NWProject):
        self._project = project
        self._items: dict[str, IndexItem] = {}
        return

    def __contains__(self, tHandle: str) -> bool:
        return tHandle in self._items

    def __delitem__(self, tHandle: str):
        self._items.pop(tHandle, None)
        return

    def __getitem__(self, tHandle: str) -> IndexItem | None:
        return self._items.get(tHandle, None)

    ##
    #  Methods
    ##

    def clear(self):
        """Clear the index."""
        self._items = {}
        return

    def add(self, tHandle: str, nwItem: NWItem):
        """Add a new item to the index. This will overwrite the item if
        it already exists.
        """
        self._items[tHandle] = IndexItem(tHandle, nwItem)
        return

    def allItemTags(self, tHandle: str) -> list[str]:
        """Get all tags set for headings of an item."""
        if tHandle in self._items:
            return self._items[tHandle].allTags()
        return []

    def iterItemHeaders(self, tHandle: str) -> Iterable[tuple[str, IndexHeading]]:
        """Iterate over all item headers of an item."""
        if tHandle in self._items:
            yield from self._items[tHandle].items()
        return

    def iterAllHeaders(self) -> Iterable[tuple[str, str, IndexHeading]]:
        """Iterate through all items and headings in the index."""
        for tHandle, tItem in self._items.items():
            for sTitle, hItem in tItem.items():
                yield tHandle, sTitle, hItem
        return

    def iterNovelStructure(
        self, rHandle: str | None = None, skipExcl: bool = False
    ) -> Iterable[tuple[str, str, IndexHeading]]:
        """Iterate over all items and headers in the novel structure for
        a given root handle, or for all if root handle is None.
        """
        for tItem in self._project.tree:
            if tItem.isNoteLayout():
                continue
            if skipExcl and not tItem.isActive:
                continue

            tHandle = tItem.itemHandle
            if tHandle is None or tHandle not in self._items:
                continue

            if rHandle is None:
                for sTitle in self._items[tHandle].headings():
                    hItem = self._items[tHandle][sTitle]
                    if hItem:
                        yield tHandle, sTitle, hItem
            elif tItem.itemRoot == rHandle:
                for sTitle in self._items[tHandle].headings():
                    hItem = self._items[tHandle][sTitle]
                    if hItem:
                        yield tHandle, sTitle, hItem

        return

    ##
    #  Setters
    ##

    def addItemHeading(self, tHandle: str, lineNo: int, level: str, text: str) -> str:
        """Add a heading to an item."""
        if tHandle in self._items:
            tItem = self._items[tHandle]
            sTitle = tItem.nextHeading()
            tItem.addHeading(IndexHeading(sTitle, lineNo, level, text))
            return sTitle
        return TT_NONE

    def setHeadingCounts(self, tHandle: str, sTitle: str, cC: int, wC: int, pC: int):
        """Set the character, word and paragraph counts of a heading
        on a given item.
        """
        if tHandle in self._items:
            self._items[tHandle].setHeadingCounts(sTitle, cC, wC, pC)
        return

    def setHeadingSynopsis(self, tHandle: str, sTitle: str, text: str):
        """Set the synopsis text for a heading on a given item."""
        if tHandle in self._items:
            self._items[tHandle].setHeadingSynopsis(sTitle, text)
        return

    def setHeadingTag(self, tHandle: str, sTitle: str, tagKey: str):
        """Set the main tag for a heading on a given item."""
        if tHandle in self._items:
            self._items[tHandle].setHeadingTag(sTitle, tagKey)
        return

    def addHeadingReferences(self, tHandle: str, sTitle: str, tagKeys: list[str], refType: str):
        """Set the reference tags for a heading on a given item."""
        if tHandle in self._items:
            self._items[tHandle].addHeadingReferences(sTitle, tagKeys, refType)
        return

    ##
    #  Pack/Unpack
    ##

    def packData(self) -> dict:
        """Pack all the data of the index into a single dictionary."""
        return {handle: item.packData() for handle, item in self._items.items()}

    def unpackData(self, data: dict):
        """Iterate through the itemIndex loaded from cache and check
        that it's valid. This will raise errors if there is a problem.
        """
        self._items = {}
        if not isinstance(data, dict):
            raise ValueError("itemIndex is not a dict")

        for tHandle, tData in data.items():
            if not isHandle(tHandle):
                raise ValueError("itemIndex keys must be handles")

            nwItem = self._project.tree[tHandle]
            if nwItem is not None:
                tItem = IndexItem(tHandle, nwItem)
                tItem.unpackData(tData)
                self._items[tHandle] = tItem

        return

# END Class ItemIndex


class IndexItem:
    """Core: Single Index Item Class

    This object represents the index data of a project item (NWItem).
    It holds a record of all the headings in the text, and the meta data
    associated with each heading. It also holds a pointer to the project
    item. The main heading level of the item is also held here since it
    must be reset each time the item is re-indexed.
    """

    __slots__ = ("_handle", "_item", "_headings", "_headings", "_count")

    def __init__(self, tHandle: str, nwItem: NWItem):
        self._handle = tHandle
        self._item = nwItem
        self._headings: dict[str, IndexHeading] = {}
        self._count = 0

        # Add a placeholder heading
        self._headings[TT_NONE] = IndexHeading(TT_NONE)

        return

    def __repr__(self) -> str:
        return f"<IndexItem handle='{self._handle}'>"

    def __len__(self) -> int:
        return len(self._headings)

    def __getitem__(self, sTitle: str) -> IndexHeading | None:
        return self._headings.get(sTitle, None)

    def __contains__(self, sTitle: str) -> bool:
        return sTitle in self._headings

    ##
    # Properties
    ##

    @property
    def item(self) -> NWItem:
        return self._item

    ##
    #  Setters
    ##

    def addHeading(self, tHeading: IndexHeading):
        """Add a heading to the item. Also remove the placeholder entry
        if it exists.
        """
        if TT_NONE in self._headings:
            self._headings.pop(TT_NONE)
        self._headings[tHeading.key] = tHeading
        return

    def setHeadingCounts(self, sTitle: str, cCount: int, wCount: int, pCount: int):
        """Set the character, word and paragraph count of a heading."""
        if sTitle in self._headings:
            self._headings[sTitle].setCounts(cCount, wCount, pCount)
        return

    def setHeadingSynopsis(self, sTitle: str, text: str):
        """Set the synopsis text of a heading."""
        if sTitle in self._headings:
            self._headings[sTitle].setSynopsis(text)
        return

    def setHeadingTag(self, sTitle: str, tagKey: str):
        """Set the tag of a heading."""
        if sTitle in self._headings:
            self._headings[sTitle].setTag(tagKey)
        return

    def addHeadingReferences(self, sTitle: str, tagKeys: list[str], refType: str):
        """Add a reference key and all its types to a heading."""
        if sTitle in self._headings:
            for tagKey in tagKeys:
                self._headings[sTitle].addReference(tagKey, refType)
        return

    ##
    #  Data Methods
    ##

    def items(self) -> ItemsView[str, IndexHeading]:
        return self._headings.items()

    def headings(self) -> list[str]:
        return sorted(self._headings.keys())

    def allTags(self) -> list[str]:
        """Return a list of all tags in the current item."""
        return [h.tag for h in self._headings.values() if h.tag]

    def nextHeading(self) -> str:
        """Return the next heading key to be used."""
        self._count += 1
        return f"T{self._count:04d}"

    ##
    #  Pack/Unpack
    ##

    def packData(self) -> dict:
        """Pack the indexed item's data into a dictionary."""
        heads = {}
        refs = {}
        for sTitle, hItem in self._headings.items():
            heads[sTitle] = hItem.packData()
            hRefs = hItem.packReferences()
            if hRefs:
                refs[sTitle] = hRefs

        data = {}
        data["headings"] = heads
        if refs:
            data["references"] = refs

        return data

    def unpackData(self, data: dict):
        """Unpack an item entry from the data."""
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
    """Core: Single Index Heading Class

    This object represents a section of text in a project item
    associated with a single (valid) heading. It holds a separate record
    of all references made under the heading.
    """

    __slots__ = (
        "_key", "_line", "_level", "_title", "_charCount", "_wordCount",
        "_paraCount", "_synopsis", "_tag", "_refs",
    )

    def __init__(self, key: str, line: int = 0, level: str = "H0", title: str = ""):
        self._key = key
        self._line = line
        self._level = level
        self._title = title

        self._charCount = 0
        self._wordCount = 0
        self._paraCount = 0
        self._synopsis = ""

        self._tag = ""
        self._refs: dict[str, set[str]] = {}

        return

    def __repr__(self) -> str:
        return f"<IndexHeading key='{self._key}'>"

    ##
    #  Properties
    ##

    @property
    def key(self) -> str:
        return self._key

    @property
    def line(self) -> int:
        return self._line

    @property
    def level(self) -> str:
        return self._level

    @property
    def title(self) -> str:
        return self._title

    @property
    def charCount(self) -> int:
        return self._charCount

    @property
    def wordCount(self) -> int:
        return self._wordCount

    @property
    def paraCount(self) -> int:
        return self._paraCount

    @property
    def synopsis(self) -> str:
        return self._synopsis

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def references(self) -> dict:
        return self._refs

    ##
    #  Setters
    ##

    def setLevel(self, level: str):
        """Set the level of the header if it's a valid value."""
        if level in nwHeaders.H_VALID:
            self._level = level
        return

    def setLine(self, line: int):
        """Set the line number of a heading."""
        self._line = max(0, checkInt(line, 0))
        return

    def setCounts(self, charCount: int, wordCount: int, paraCount: int):
        """Set the character, word and paragraph count. Make sure the
        value is an integer and is not smaller than 0.
        """
        self._charCount = max(0, checkInt(charCount, 0))
        self._wordCount = max(0, checkInt(wordCount, 0))
        self._paraCount = max(0, checkInt(paraCount, 0))
        return

    def setSynopsis(self, text: str):
        """Set the synopsis text and make sure it is a string."""
        self._synopsis = str(text)
        return

    def setTag(self, tagKey: str):
        """Set the tag for references, and make sure it is a string."""
        self._tag = str(tagKey)
        return

    def addReference(self, tagKey: str, refType: str):
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

    def packData(self) -> dict:
        """Pack the values into a dictionary for saving to cache."""
        return {
            "level": self._level,
            "title": self._title,
            "line": self._line,
            "tag": self._tag,
            "cCount": self._charCount,
            "wCount": self._wordCount,
            "pCount": self._paraCount,
            "synopsis": self._synopsis,
        }

    def packReferences(self) -> dict[str, str]:
        """Pack references into a dictionary for saving to cache.
        Multiple types are packed into a sorted, comma separated string.
        It is sorted to prevent creating unnecessary diffs as the order
        of a set is not guaranteed.
        """
        return {key: ",".join(sorted(list(value))) for key, value in self._refs.items()}

    def unpackData(self, data: dict):
        """Unpack a heading entry from a dictionary."""
        self.setLevel(data.get("level", "H0"))
        self._title = str(data.get("title", ""))
        self._tag = str(data.get("tag", ""))
        self.setLine(data.get("line", 0))
        self.setCounts(
            data.get("cCount", 0),
            data.get("wCount", 0),
            data.get("pCount", 0),
        )
        self._synopsis = str(data.get("synopsis", ""))
        return

    def unpackReferences(self, data: dict):
        """Unpack a set of references from a dictionary."""
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

def countWords(text: str) -> tuple[int, int, int]:
    """Count words in a piece of text, skipping special syntax and
    comments.
    """
    charCount = 0
    wordCount = 0
    paraCount = 0
    prevEmpty = True

    if not isinstance(text, str):
        return charCount, wordCount, paraCount

    # We need to treat dashes as word separators for counting words.
    # The check+replace approach is much faster than direct replace for
    # large texts, and a bit slower for small texts, but in the latter
    # case it doesn't really matter.
    if nwUnicode.U_ENDASH in text:
        text = text.replace(nwUnicode.U_ENDASH, " ")
    if nwUnicode.U_EMDASH in text:
        text = text.replace(nwUnicode.U_EMDASH, " ")

    for aLine in text.splitlines():

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
