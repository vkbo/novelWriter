"""
novelWriter – Project Index
===========================

File History:
Created: 2019-05-27 [0.1.4]  Index
Created: 2022-05-29 [2.0rc1] TagsIndex
Created: 2022-05-29 [2.0rc1] ItemIndex

This file is a part of novelWriter
Copyright (C) 2019 Veronica Berglyd Olsen and novelWriter contributors

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
import random

from pathlib import Path
from time import time
from typing import TYPE_CHECKING

from novelwriter import SHARED
from novelwriter.common import isHandle, isItemClass, isTitleTag, jsonEncode
from novelwriter.constants import nwFiles, nwKeyWords, nwStyles
from novelwriter.core.indexdata import NOTE_TYPES, TT_NONE, IndexHeading, IndexNode, T_NoteTypes
from novelwriter.core.novelmodel import NovelModel
from novelwriter.enum import nwComment, nwItemClass, nwItemLayout, nwItemType, nwNovelExtra
from novelwriter.error import logException
from novelwriter.text.comments import processComment
from novelwriter.text.counting import standardCounter

if TYPE_CHECKING:
    from collections.abc import ItemsView, Iterable

    from novelwriter.core.item import NWItem
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)

MAX_RETRY = 1000  # Key generator recursion limit
KEY_SOURCE = "0123456789bcdfghjklmnpqrstvwxz"


class Index:
    """Core: Project Index

    This class holds the entire index for a given project. The index
    contains the data that isn't stored in the project items themselves.
    The content of the index is updated every time a file item is saved.

    Some information needed by the NWItem object of a project item can
    only be known after a text file has been scanned by the indexer, so
    this data is set directly by the indexer class in the NWItem object.

    The primary index data is contained in a single instance of the
    ItemIndex class. This object contains an IndexNode representing each
    NWItem of the project. Each IndexNode holds an IndexHeading object
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
        self._itemIndex = ItemIndex(project, self._tagsIndex)
        self._indexBroken = False

        # Models
        self._novelModels: dict[str, NovelModel] = {}
        self._novelExtra = nwNovelExtra.HIDDEN

        # TimeStamps
        self._indexChange = 0.0
        self._rootChange = {}

        return

    def __repr__(self) -> str:
        return f"<Index project='{self._project.data.name}'>"

    ##
    #  Properties
    ##

    @property
    def indexBroken(self) -> bool:
        return self._indexBroken

    ##
    #  Getters
    ##

    def getNovelModel(self, tHandle: str) -> NovelModel | None:
        """Get the model for a specific novel root."""
        if tHandle not in self._novelModels:
            self._generateNovelModel(tHandle)
        return self._novelModels.get(tHandle)

    ##
    #  Setters
    ##

    def setNovelModelExtraColumn(self, extra: nwNovelExtra) -> None:
        """Set the data content type of the novel model extra column."""
        self._novelExtra = extra
        return

    ##
    #  Public Methods
    ##

    def clear(self) -> None:
        """Clear the index dictionaries and time stamps."""
        self._tagsIndex.clear()
        self._itemIndex.clear()
        self._indexChange = 0.0
        self._rootChange = {}
        SHARED.emitIndexCleared(self._project)
        return

    def rebuild(self) -> None:
        """Rebuild the entire index from scratch."""
        self.clear()
        SHARED.initMainProgress(len(self._project.tree))
        for nwItem in self._project.tree:
            if nwItem.isFileType():
                text = self._project.storage.getDocumentText(nwItem.itemHandle)
                self.scanText(nwItem.itemHandle, text, blockSignal=True)
            SHARED.incMainProgress()
        self._indexBroken = False
        SHARED.emitIndexAvailable(self._project)
        for tHandle in self._novelModels:
            self.refreshNovelModel(tHandle)
        SHARED.clearMainProgress()
        return

    def deleteHandle(self, tHandle: str) -> None:
        """Delete all entries of a given document handle."""
        logger.debug("Removing item '%s' from the index", tHandle)
        delTags = self._itemIndex.allItemTags(tHandle)
        for tTag in delTags:
            del self._tagsIndex[tTag]
        del self._itemIndex[tHandle]
        SHARED.emitIndexChangedTags(self._project, [], delTags)
        return

    def reIndexHandle(self, tHandle: str | None) -> None:
        """Put a file back into the index. This is used when files are
        moved from the archive or trash folders back into the active
        project.
        """
        if tHandle and self._project.tree.checkType(tHandle, nwItemType.FILE):
            logger.debug("Re-indexing item '%s'", tHandle)
            self.scanText(tHandle, self._project.storage.getDocumentText(tHandle))
        return

    def refreshHandle(self, tHandle: str) -> None:
        """Update the class for all tags of a handle."""
        if item := self._project.tree[tHandle]:
            logger.info("Updating class for '%s'", tHandle)
            if item.isInactiveClass():
                self.deleteHandle(tHandle)
            else:
                self._tagsIndex.updateClass(tHandle, item.itemClass.name)
        return

    def indexChangedSince(self, checkTime: int | float) -> bool:
        """Check if the index has changed since a given time."""
        return self._indexChange > float(checkTime)

    def rootChangedSince(self, rootHandle: str | None, checkTime: int | float) -> bool:
        """Check if the index has changed since a given time for a
        given root item.
        """
        if isinstance(rootHandle, str):
            return self._rootChange.get(rootHandle, self._indexChange) > float(checkTime)
        return False

    def refreshNovelModel(self, tHandle: str | None) -> None:
        """Refresh a novel model."""
        if tHandle and (model := self.getNovelModel(tHandle)):
            logger.info("Refreshing novel model '%s'", tHandle)
            model.beginResetModel()
            model.clear()
            model.setExtraColumn(self._novelExtra)
            self._appendSubTreeToModel(tHandle, model)
            model.endResetModel()
        return

    def updateNovelModelData(self, nwItem: NWItem) -> bool:
        """Refresh a novel model."""
        if (
            (rHandle := nwItem.itemRoot)
            and (model := self._novelModels.get(rHandle))
            and (node := self._itemIndex[nwItem.itemHandle])
            and node.item.isDocumentLayout()
            and node.item.isActive
        ):
            logger.info("Updating novel model data '%s'", nwItem.itemHandle)
            return model.refresh(node)
        return False

    ##
    #  Load and Save Index to/from File
    ##

    def loadIndex(self) -> bool:
        """Load index from last session from the project meta folder."""
        indexFile = self._project.storage.getMetaFile(nwFiles.INDEX_FILE)
        if not isinstance(indexFile, Path):
            return False

        tStart = time()
        self._indexBroken = False
        if indexFile.exists():
            logger.debug("Loading index file")
            try:
                with open(indexFile, mode="r", encoding="utf-8") as inFile:
                    data = json.load(inFile)
            except Exception:
                logger.error("Failed to load index file")
                logException()
                self._indexBroken = True
                return False

            try:
                self._tagsIndex.unpackData(data["novelWriter.tagsIndex"])
                self._itemIndex.unpackData(data["novelWriter.itemIndex"])
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
        SHARED.emitIndexAvailable(self._project)

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

    def scanText(self, tHandle: str, text: str, blockSignal: bool = False) -> bool:
        """Scan a piece of text associated with a handle. This will
        update the indices accordingly. This function takes the handle
        and text as separate inputs as we want to primarily scan the
        files before we save them, in which case we already have the
        text.
        """
        tItem = self._project.tree[tHandle]
        if tItem is None:
            logger.info("Not indexing unknown item '%s'", tHandle)
            return False
        if not tItem.isFileType():
            logger.info("Not indexing non-file item '%s'", tHandle)
            return False

        # Keep a record of existing tags, and create a new item entry
        itemTags = dict.fromkeys(self._itemIndex.allItemTags(tHandle), False)
        self._itemIndex.add(tHandle, tItem)

        # Run word counter for the whole text
        cC, wC, pC = standardCounter(text)
        tItem.setCharCount(cC)
        tItem.setWordCount(wC)
        tItem.setParaCount(pC)

        # If the file's meta data is missing, or the file is out of the
        # main project, we don't index the content
        if tItem.itemLayout == nwItemLayout.NO_LAYOUT:
            logger.info("Not indexing no-layout item '%s'", tHandle)
            return False
        if tItem.itemParent is None:
            logger.info("Not indexing orphaned item '%s'", tHandle)
            return False

        logger.debug("Indexing item with handle '%s'", tHandle)
        if tItem.isInactiveClass():
            self._scanInactive(tItem, text)
        else:
            self._scanActive(tHandle, tItem, text, itemTags)

        if tItem.itemClass == nwItemClass.NOVEL and not blockSignal:
            if not self.updateNovelModelData(tItem):
                self.refreshNovelModel(tItem.itemRoot)

        # Update timestamps for index changes
        nowTime = time()
        self._indexChange = nowTime
        self._rootChange[tItem.itemRoot] = nowTime
        if not blockSignal:
            tItem.notifyToRefresh()

        return True

    ##
    #  Internal Indexer Helpers
    ##

    def _scanActive(self, tHandle: str, nwItem: NWItem, text: str, tags: dict[str, bool]) -> None:
        """Scan an active document for meta data."""
        nTitle = 0         # Line Number of the previous title
        cTitle = TT_NONE   # Tag of the current title
        pTitle = TT_NONE   # Tag of the previous title
        canSetHead = True  # First heading has not yet been set

        lines = text.splitlines()
        for n, line in enumerate(lines, start=1):

            if line.strip() == "":
                continue

            if line.startswith("#"):
                hDepth, hText = self._splitHeading(line)
                if hDepth == "H0":
                    continue

                if canSetHead:
                    nwItem.setMainHeading(hDepth)
                    canSetHead = False

                cTitle = self._itemIndex.addItemHeading(tHandle, n, hDepth, hText)
                if cTitle != TT_NONE:
                    if nTitle > 0:
                        # We have a new title, so we need to count the words of the previous one
                        lastText = "\n".join(lines[nTitle-1:n-1])
                        self._indexWordCounts(tHandle, lastText, pTitle)
                    nTitle = n
                    pTitle = cTitle

            elif line.startswith("@"):
                if cTitle != TT_NONE:
                    self._indexKeyword(tHandle, line, cTitle, nwItem.itemClass, tags)

            elif line.startswith("%"):
                cStyle, cKey, cText, _, _ = processComment(line)
                if cStyle == nwComment.FOOTNOTE:
                    self._itemIndex.addNoteKey(tHandle, "footnotes", cKey)
                else:
                    self._itemIndex.setHeadingComment(tHandle, cTitle, cStyle, cKey, cText)

        # Count words for remaining text after last heading
        if pTitle != TT_NONE:
            lastText = "\n".join(lines[nTitle-1:])
            self._indexWordCounts(tHandle, lastText, pTitle)

        # Also count words on a page with no titles
        if cTitle == TT_NONE:
            self._indexWordCounts(tHandle, text, cTitle)

        # Prune no longer used tags
        for tTag, isActive in tags.items():
            updated = []
            deleted = []
            if isActive:
                logger.debug("Added/updated tag '%s'", tTag)
                updated.append(tTag)
            else:
                logger.debug("Removed tag '%s'", tTag)
                del self._tagsIndex[tTag]
                deleted.append(tTag)
            if updated or deleted:
                SHARED.emitIndexChangedTags(self._project, updated, deleted)

        return

    def _scanInactive(self, nwItem: NWItem, text: str) -> None:
        """Scan an inactive document for meta data."""
        for line in text.splitlines():
            if line.startswith("#"):
                hDepth, _ = self._splitHeading(line)
                if hDepth != "H0":
                    nwItem.setMainHeading(hDepth)
                    break
        return

    def _splitHeading(self, line: str) -> tuple[str, str]:
        """Split a heading into its heading level and text value."""
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
        elif line.startswith("###! "):
            return "H3", line[5:].strip()
        return "H0", ""

    def _indexWordCounts(self, tHandle: str, text: str, sTitle: str) -> None:
        """Count text stats and save the counts to the index."""
        cC, wC, pC = standardCounter(text)
        self._itemIndex.setHeadingCounts(tHandle, sTitle, cC, wC, pC)
        return

    def _indexKeyword(
        self, tHandle: str, line: str, sTitle: str, itemClass: nwItemClass, tags: dict[str, bool]
    ) -> None:
        """Validate and save the information about a reference to a tag
        in another file, or the setting of a tag in the file. A record
        of active tags is updated so that no longer used tags can be
        pruned later.
        """
        isValid, tBits, _ = self.scanThis(line)
        if not isValid or len(tBits) < 2:
            logger.warning("Skipping keyword with %d value(s) in '%s'", len(tBits), tHandle)
            return

        if tBits[0] not in nwKeyWords.VALID_KEYS:
            logger.warning("Skipping invalid keyword '%s' in '%s'", tBits[0], tHandle)
            return

        if tBits[0] == nwKeyWords.TAG_KEY:
            tagKey, displayName = self.parseValue(tBits[1])
            self._tagsIndex.add(tagKey, displayName, tHandle, sTitle, itemClass.name)
            self._itemIndex.setHeadingTag(tHandle, sTitle, tagKey)
            tags[tagKey.lower()] = True
        else:
            self._itemIndex.addHeadingRef(tHandle, sTitle, tBits[1:], tBits[0])

        return

    def _generateNovelModel(self, tHandle: str) -> None:
        """Generate a novel model for a specific handle."""
        if (item := self._project.tree[tHandle]) and item.isRootType() and item.isNovelLike():
            model = NovelModel()
            model.setExtraColumn(self._novelExtra)
            self._appendSubTreeToModel(tHandle, model)
            self._novelModels[tHandle] = model
        return

    def _appendSubTreeToModel(self, tHandle: str, model: NovelModel) -> None:
        """Append all active novel documents to a novel model."""
        for handle in self._project.tree.subTree(tHandle):
            if (
                (node := self._itemIndex[handle])
                and node.item.isDocumentLayout()
                and node.item.isActive
            ):
                model.append(node)
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

    def checkThese(self, tBits: list[str], tHandle: str) -> list[bool]:
        """Check tags against the index to see if they are valid."""
        nBits = len(tBits)
        isGood = [False]*nBits
        if nBits == 0:
            return []

        # Check that the keyword is valid
        kBit = tBits[0]
        isGood[0] = kBit in nwKeyWords.VALID_KEYS
        if not isGood[0] or nBits == 1:
            return isGood

        # For a tag, only the first value is accepted, the rest are ignored
        if kBit == nwKeyWords.TAG_KEY and nBits > 1:
            check, _ = self.parseValue(tBits[1])
            if check in self._tagsIndex:
                isGood[1] = self._tagsIndex.tagHandle(check) == tHandle
            else:
                isGood[1] = True
            return isGood

        if kBit == nwKeyWords.MENTION_KEY and nBits > 1:
            isGood[1:nBits] = [aBit in self._tagsIndex for aBit in tBits[1:nBits]]
            return isGood

        # If we're still here, we check that the references exist
        # Class references cannot have the | symbol in them
        if rClass := nwKeyWords.KEY_CLASS.get(kBit):
            for n in range(1, nBits):
                if (aBit := tBits[n]) in self._tagsIndex:
                    isGood[n] = self._tagsIndex.tagClass(aBit) == rClass.name and "|" not in aBit

        return isGood

    def parseValue(self, text: str) -> tuple[str, str]:
        """Parse a single value into a name and display part."""
        name, _, display = text.partition("|")
        return name.rstrip(), display.lstrip()

    def newCommentKey(self, tHandle: str, style: nwComment) -> str:
        """Generate a new key for a comment style."""
        if style == nwComment.FOOTNOTE:
            return self._itemIndex.genNewNoteKey(tHandle, "footnotes")
        elif style == nwComment.COMMENT:
            return self._itemIndex.genNewNoteKey(tHandle, "comments")
        return "err"

    ##
    #  Extract Data
    ##

    def getItemData(self, tHandle: str) -> IndexNode | None:
        """Get the index data for a given item."""
        return self._itemIndex[tHandle]

    def getItemHeading(self, tHandle: str, sTitle: str) -> IndexHeading | None:
        """Get the heading entry for a specific item and heading."""
        if tItem := self._itemIndex[tHandle]:
            return tItem[sTitle]
        return None

    def iterItemHeadings(self, tHandle: str) -> Iterable[tuple[str, IndexHeading]]:
        """Get all headings for a specific item."""
        if tItem := self._itemIndex[tHandle]:
            yield from tItem.items()
        return

    def getStoryKeys(self) -> set[str]:
        """Return all story structure keys."""
        return self._itemIndex.allStoryKeys()

    def getNoteKeys(self) -> set[str]:
        """Return all note comment keys."""
        return self._itemIndex.allNoteKeys()

    def novelStructure(
        self, rootHandle: str | None = None, activeOnly: bool = True
    ) -> Iterable[tuple[str, str, str, IndexHeading]]:
        """Iterate over all titles in the novel, in the correct order as
        they appear in the tree view and in the respective document
        files, but skipping all note files.
        """
        structure = self._itemIndex.iterNovelStructure(rHandle=rootHandle, activeOnly=activeOnly)
        for tHandle, sTitle, hItem in structure:
            yield f"{tHandle}:{sTitle}", tHandle, sTitle, hItem
        return

    def getNovelWordCount(self, rootHandle: str | None = None, activeOnly: bool = True) -> int:
        """Count the number of words in one or all novel roots."""
        return sum(hItem.wordCount for _, _, hItem in self._itemIndex.iterNovelStructure(
            rHandle=rootHandle, activeOnly=activeOnly
        ))

    def getNovelTitleCounts(
        self, rootHandle: str | None = None, activeOnly: bool = True
    ) -> list[int]:
        """Count the number of titles in one or all novel roots."""
        hCount = [0, 0, 0, 0, 0]
        for _, _, hItem in self._itemIndex.iterNovelStructure(
            rHandle=rootHandle, activeOnly=activeOnly
        ):
            iLevel = nwStyles.H_LEVEL.get(hItem.level, 0)
            hCount[iLevel] += 1
        return hCount

    def getTableOfContents(
        self, rHandle: str | None, maxDepth: int, activeOnly: bool = True
    ) -> list[tuple[str, int, str, int]]:
        """Generate a table of contents up to a maximum depth."""
        tOrder = []
        tData = {}
        pKey = None
        for tHandle, sTitle, hItem in self._itemIndex.iterNovelStructure(
            rHandle=rHandle, activeOnly=activeOnly
        ):
            tKey = f"{tHandle}:{sTitle}"
            iLevel = nwStyles.H_LEVEL.get(hItem.level, 0)
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

        result = [(
            tKey,
            tData[tKey]["level"],
            tData[tKey]["title"],
            tData[tKey]["words"]
        ) for tKey in tOrder]

        return result

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
        """Extract all tags and references made in a file, and
        optionally title section.
        """
        refs = {x: [] for x in nwKeyWords.VALID_KEYS}
        for rTitle, hItem in self._itemIndex.iterItemHeaders(tHandle):
            if sTitle is None or sTitle == rTitle:
                for aTag, refTypes in hItem.references.items():
                    for refType in refTypes:
                        if refType in refs:
                            refs[refType].append(self._tagsIndex.tagName(aTag))
                if tag := hItem.tag:
                    refs[nwKeyWords.TAG_KEY] = [self._tagsIndex.tagName(tag)]
        return refs

    def getReferenceForHeader(self, tHandle: str, nHead: int, keyClass: str) -> list[str]:
        """Get the display names for a tags class for insertion into a
        heading by one of the build classes.
        """
        if iItem := self._itemIndex[tHandle]:
            if hItem := iItem[f"T{nHead:04d}"]:
                hRefs = [k for k, v in hItem.references.items() if keyClass in v]
                return [self._tagsIndex.tagDisplay(k) for k in hRefs]
        return []

    def getBackReferenceList(self, tHandle: str) -> dict[str, tuple[str, IndexHeading]]:
        """Build a dict of files referring back to our file."""
        if tHandle is None or tHandle not in self._itemIndex:
            return {}

        tRefs = {}
        tTags = self._itemIndex.allItemTags(tHandle)
        if not tTags:
            return tRefs

        for aHandle, sTitle, hItem in self._itemIndex.iterAllHeaders():
            for aTag in hItem.references:
                if aTag in tTags and aHandle not in tRefs:
                    tRefs[aHandle] = (sTitle, hItem)

        return tRefs

    def getTagSource(self, tagKey: str) -> tuple[str | None, str]:
        """Return the source location of a given tag."""
        tHandle = self._tagsIndex.tagHandle(tagKey)
        sTitle = self._tagsIndex.tagHeading(tagKey)
        return tHandle, sTitle

    def getDocumentTags(self, tHandle: str | None) -> list[str]:
        """Return all tags used by a specific document."""
        return self._itemIndex.allItemTags(tHandle) if tHandle else []

    def getKeyWordTags(self, keyWord: str) -> list[str]:
        """Return all tags usable for a specific keyword."""
        if keyWord in nwKeyWords.CAN_LOOKUP:
            itemClass = nwKeyWords.KEY_CLASS.get(keyWord)
            return self._tagsIndex.filterTagNames(itemClass.name if itemClass else None)
        return []

    def getTagsData(
        self, activeOnly: bool = True
    ) -> Iterable[tuple[str, str, str, IndexNode | None, IndexHeading | None]]:
        """Return all known tags."""
        for tag, data in self._tagsIndex.items():
            iItem = self._itemIndex[data.get("handle")]
            hItem = None if iItem is None else iItem[data.get("heading")]
            if not activeOnly or (iItem and iItem.item.isActive):
                yield tag, data.get("name", ""), data.get("class", ""), iItem, hItem
        return

    def getSingleTag(self, tagKey: str) -> tuple[str, str, IndexNode | None, IndexHeading | None]:
        """Return tag data for a specific tag."""
        tName = self._tagsIndex.tagName(tagKey)
        tClass = self._tagsIndex.tagClass(tagKey)
        tHandle = self._tagsIndex.tagHandle(tagKey)
        tHeading = self._tagsIndex.tagHeading(tagKey)
        if tName and tClass and tHandle and tHeading:
            iItem = self._itemIndex[tHandle]
            return tName, tClass, iItem, None if iItem is None else iItem[tHeading]
        return "", "", None, None


# The Tags Index Object
# =====================

class TagsIndex:
    """Core: Tags Index Wrapper Class

    A wrapper class that holds the reverse lookup tags index. This is
    just a simple wrapper around a single dictionary to keep tighter
    control of the keys.
    """

    __slots__ = ("_tags",)

    def __init__(self) -> None:
        self._tags: dict[str, dict[str, str]] = {}
        return

    def __contains__(self, tagKey: str) -> bool:
        return tagKey.lower() in self._tags

    def __delitem__(self, tagKey: str) -> None:
        self._tags.pop(tagKey.lower(), None)
        return

    def __getitem__(self, tagKey: str) -> dict | None:
        return self._tags.get(tagKey.lower(), None)

    ##
    #  Methods
    ##

    def clear(self) -> None:
        """Clear the index."""
        self._tags = {}
        return

    def items(self) -> ItemsView:
        """Return a dictionary view of all tags."""
        return self._tags.items()

    def add(self, tagKey: str, displayName: str, tHandle: str,
            sTitle: str, className: str) -> None:
        """Add a key to the index and set all values."""
        self._tags[tagKey.lower()] = {
            "name": tagKey,
            "display": displayName or tagKey,
            "handle": tHandle,
            "heading": sTitle,
            "class": className,
        }
        return

    def tagName(self, tagKey: str, default: str = "") -> str:
        """Get the name of a given tag."""
        return self._tags.get(tagKey.lower(), {}).get("name", default)

    def tagDisplay(self, tagKey: str, default: str = "") -> str:
        """Get the display name of a given tag."""
        return self._tags.get(tagKey.lower(), {}).get("display", default)

    def tagHandle(self, tagKey: str) -> str | None:
        """Get the handle of a given tag."""
        return self._tags.get(tagKey.lower(), {}).get("handle", None)

    def tagHeading(self, tagKey: str) -> str:
        """Get the heading of a given tag."""
        return self._tags.get(tagKey.lower(), {}).get("heading", TT_NONE)

    def tagClass(self, tagKey: str) -> str | None:
        """Get the class of a given tag."""
        return self._tags.get(tagKey.lower(), {}).get("class", None)

    def filterTagNames(self, className: str | None) -> list[str]:
        """Get a list of tag names for a given class."""
        if className is None:
            return [
                x.get("name", "") for x in self._tags.values()
            ]
        else:
            return [
                x.get("name", "") for x in self._tags.values() if x.get("class", "") == className
            ]

    def updateClass(self, tHandle: str, className: str) -> None:
        """Update the class name of an item. This must be called when a
        document moves to another class.
        """
        for entry in self._tags.values():
            if entry.get("handle") == tHandle:
                entry["class"] = className
        return

    ##
    #  Pack/Unpack
    ##

    def packData(self) -> dict:
        """Pack all the data of the tags into a single dictionary."""
        return self._tags

    def unpackData(self, data: dict) -> None:
        """Iterate through the tagsIndex loaded from cache and check
        that it's valid.
        """
        self._tags = {}
        if not isinstance(data, dict):
            raise ValueError("tagsIndex is not a dict")

        for key, entry in data.items():
            if not isinstance(key, str):
                raise ValueError("tagsIndex key must be a string")
            if not isinstance(entry, dict):
                raise ValueError("tagsIndex entry is not a dict")

            name = entry.get("name")
            display = entry.get("display")
            handle = entry.get("handle")
            heading = entry.get("heading")
            className = entry.get("class")

            if not isinstance(name, str):
                raise ValueError("tagsIndex name is not a string")
            if not isinstance(display, str):
                raise ValueError("tagsIndex display is not a string")
            if not isHandle(handle):
                raise ValueError("tagsIndex handle must be a handle")
            if not isTitleTag(heading):
                raise ValueError("tagsIndex heading must be a title tag")
            if not isItemClass(className):
                raise ValueError("tagsIndex handle must be an nwItemClass")

            self.add(name, display, handle, heading, className)

        return


class IndexCache:
    """Core: Item Index Lookup Data Class

    A small data class passed between all objects of the Item Index
    which provides lookup capabilities and caching for shared data.
    """

    __slots__ = ("note", "story", "tags")

    def __init__(self, tagsIndex: TagsIndex) -> None:
        self.tags: TagsIndex = tagsIndex
        self.story: set[str] = set()
        self.note: set[str] = set()
        return


# The Item Index Objects
# ======================

class ItemIndex:
    """Core: Item Index Wrapper Class

    A wrapper object holding the indexed items. This is a wrapper
    class around a single storage dictionary with a set of utility
    functions for setting and accessing the index data. Each indexed
    item is stored in an IndexNode object, which again holds an
    IndexHeading object for each heading of the text.
    """

    __slots__ = ("_cache", "_items", "_project")

    def __init__(self, project: NWProject, tagsIndex: TagsIndex) -> None:
        self._project = project
        self._cache = IndexCache(tagsIndex)
        self._items: dict[str, IndexNode] = {}
        return

    def __contains__(self, tHandle: str) -> bool:
        return tHandle in self._items

    def __delitem__(self, tHandle: str) -> None:
        self._items.pop(tHandle, None)
        return

    def __getitem__(self, tHandle: str) -> IndexNode | None:
        return self._items.get(tHandle, None)

    ##
    #  Methods
    ##

    def clear(self) -> None:
        """Clear the index."""
        self._items = {}
        return

    def add(self, tHandle: str, nwItem: NWItem) -> None:
        """Add a new item to the index. This will overwrite the item if
        it already exists.
        """
        self._items[tHandle] = IndexNode(self._cache, tHandle, nwItem)
        return

    def allStoryKeys(self) -> set[str]:
        """Return all story structure keys."""
        return self._cache.story.copy()

    def allNoteKeys(self) -> set[str]:
        """Return all note comment keys."""
        return self._cache.note.copy()

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
        self, rHandle: str | None = None, activeOnly: bool = False
    ) -> Iterable[tuple[str, str, IndexHeading]]:
        """Iterate over all items and headers in the novel structure for
        a given root handle, or for all if root handle is None.
        """
        for tItem in self._project.tree:
            if tItem.isNoteLayout():
                continue
            if activeOnly and not tItem.isActive:
                continue

            tHandle = tItem.itemHandle
            if tHandle is None or tHandle not in self._items:
                continue

            if rHandle is None:
                for sTitle in self._items[tHandle].headings():
                    if hItem := self._items[tHandle][sTitle]:
                        yield tHandle, sTitle, hItem
            elif tItem.itemRoot == rHandle:
                for sTitle in self._items[tHandle].headings():
                    if hItem := self._items[tHandle][sTitle]:
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
            tItem.addHeading(IndexHeading(self._cache, sTitle, lineNo, level, text))
            return sTitle
        return TT_NONE

    def setHeadingCounts(self, tHandle: str, sTitle: str, cC: int, wC: int, pC: int) -> None:
        """Set the character, word and paragraph counts of a heading
        on a given item.
        """
        if tHandle in self._items:
            self._items[tHandle].setHeadingCounts(sTitle, cC, wC, pC)
        return

    def setHeadingComment(
        self, tHandle: str, sTitle: str,
        comment: nwComment, key: str, text: str,
    ) -> None:
        """Set a story comment for a heading on a given item."""
        if tHandle in self._items:
            self._items[tHandle].setHeadingComment(sTitle, comment, key, text)
        return

    def setHeadingTag(self, tHandle: str, sTitle: str, tagKey: str) -> None:
        """Set the main tag for a heading on a given item."""
        if tHandle in self._items:
            self._items[tHandle].setHeadingTag(sTitle, tagKey)
        return

    def addHeadingRef(self, tHandle: str, sTitle: str, tagKeys: list[str], refType: str) -> None:
        """Set the reference tags for a heading on a given item."""
        if tHandle in self._items:
            self._items[tHandle].addHeadingRef(sTitle, tagKeys, refType)
        return

    def addNoteKey(self, tHandle: str, style: T_NoteTypes, key: str) -> None:
        """Set notes key for a given item."""
        if tHandle in self._items:
            self._items[tHandle].addNoteKey(style, key)
        return

    def genNewNoteKey(self, tHandle: str, style: T_NoteTypes) -> str:
        """Set notes key for a given item."""
        if style in NOTE_TYPES and (item := self._items.get(tHandle)):
            keys = set()
            for entry in self._items.values():
                keys.update(entry.noteKeys(style))
            for _ in range(MAX_RETRY):
                key = style[:1] + "".join(random.choices(KEY_SOURCE, k=4))
                if key not in keys:
                    item.addNoteKey(style, key)
                    return key
        return "err"

    ##
    #  Pack/Unpack
    ##

    def packData(self) -> dict:
        """Pack all the data of the index into a single dictionary."""
        return {handle: item.packData() for handle, item in self._items.items()}

    def unpackData(self, data: dict) -> None:
        """Iterate through the itemIndex loaded from cache and check
        that it's valid. This will raise errors if there are problems.
        """
        self._items = {}
        if not isinstance(data, dict):
            raise ValueError("itemIndex is not a dict")

        for tHandle, tData in data.items():
            if not isHandle(tHandle):
                raise ValueError("itemIndex keys must be handles")

            nwItem = self._project.tree[tHandle]
            if nwItem is not None:
                tItem = IndexNode(self._cache, tHandle, nwItem)
                tItem.unpackData(tData)
                self._items[tHandle] = tItem

        return
