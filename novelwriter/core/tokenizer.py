"""
novelWriter – Text Tokenizer
============================

File History:
Created: 2019-05-05 [0.0.1] Tokenizer
Created: 2023-05-23 [2.1b1] HeadingFormatter

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

import re
import json
import logging

from abc import ABC, abstractmethod
from time import time
from pathlib import Path
from functools import partial

from PyQt5.QtCore import QCoreApplication, QRegularExpression

from novelwriter.enum import nwComment, nwItemLayout
from novelwriter.common import formatTimeStamp, numberToRoman, checkInt
from novelwriter.constants import (
    nwHeadFmt, nwKeyWords, nwLabels, nwRegEx, nwShortcode, nwUnicode, trConst
)
from novelwriter.core.index import processComment
from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)

ESCAPES = {r"\*": "*", r"\~": "~", r"\_": "_", r"\[": "[", r"\]": "]", r"\ ": ""}
RX_ESC = re.compile("|".join([re.escape(k) for k in ESCAPES.keys()]), flags=re.DOTALL)


def stripEscape(text) -> str:
    """Strip escaped Markdown characters from paragraph text."""
    if "\\" in text:
        return RX_ESC.sub(lambda x: ESCAPES[x.group(0)], text)
    return text


class Tokenizer(ABC):
    """Core: Text Tokenizer Abstract Base Class

    This is the base class for all document build classes. It parses the
    novelWriter markup format and generates a registry of tokens and
    text that can be further processed into other output formats by
    subclasses.
    """

    # In-Text Format
    FMT_B_B   = 1   # Begin bold
    FMT_B_E   = 2   # End bold
    FMT_I_B   = 3   # Begin italics
    FMT_I_E   = 4   # End italics
    FMT_D_B   = 5   # Begin strikeout
    FMT_D_E   = 6   # End strikeout
    FMT_U_B   = 7   # Begin underline
    FMT_U_E   = 8   # End underline
    FMT_SUP_B = 9   # Begin superscript
    FMT_SUP_E = 10  # End superscript
    FMT_SUB_B = 11  # Begin subscript
    FMT_SUB_E = 12  # End subscript

    # Block Type
    T_EMPTY    = 1   # Empty line (new paragraph)
    T_SYNOPSIS = 2   # Synopsis comment
    T_SHORT    = 3   # Short description comment
    T_COMMENT  = 4   # Comment line
    T_KEYWORD  = 5   # Command line
    T_TITLE    = 6   # Title
    T_UNNUM    = 7   # Unnumbered
    T_HEAD1    = 8   # Header 1
    T_HEAD2    = 9   # Header 2
    T_HEAD3    = 10   # Header 3
    T_HEAD4    = 11  # Header 4
    T_TEXT     = 12  # Text line
    T_SEP      = 13  # Scene separator
    T_SKIP     = 14  # Paragraph break

    # Block Style
    A_NONE     = 0x0000  # No special style
    A_LEFT     = 0x0001  # Left aligned
    A_RIGHT    = 0x0002  # Right aligned
    A_CENTRE   = 0x0004  # Centred
    A_JUSTIFY  = 0x0008  # Justified
    A_PBB      = 0x0010  # Page break before
    A_PBA      = 0x0020  # Page break after
    A_Z_TOPMRG = 0x0040  # Zero top margin
    A_Z_BTMMRG = 0x0080  # Zero bottom margin
    A_IND_L    = 0x0100  # Left indentation
    A_IND_R    = 0x0200  # Right indentation

    def __init__(self, project: NWProject) -> None:

        self._project = project

        # Data Variables
        self._text   = ""    # The raw text to be tokenized
        self._nwItem = None  # The NWItem currently being processed
        self._result = ""    # The result of the last document

        self._keepMarkdown = False  # Whether to keep the markdown text
        self._allMarkdown  = []     # The result novelWriter markdown of all documents

        # Processed Tokens
        self._tokens: list[tuple[int, int, str, list[tuple[int, int]], int]] = []

        # User Settings
        self._textFont    = "Serif"  # Output text font
        self._textSize    = 11       # Output text size
        self._textFixed   = False    # Fixed width text
        self._lineHeight  = 1.15     # Line height in units of em
        self._blockIndent = 4.00     # Block indent in units of em
        self._doJustify   = False    # Justify text
        self._doBodyText  = True     # Include body text
        self._doSynopsis  = False    # Also process synopsis comments
        self._doComments  = False    # Also process comments
        self._doKeywords  = False    # Also process keywords like tags and references

        # Margins
        self._marginTitle = (1.000, 0.500)
        self._marginHead1 = (1.000, 0.500)
        self._marginHead2 = (0.834, 0.500)
        self._marginHead3 = (0.584, 0.500)
        self._marginHead4 = (0.584, 0.500)
        self._marginText  = (0.000, 0.584)
        self._marginMeta  = (0.000, 0.584)

        # Title Formats
        self._fmtTitle   = nwHeadFmt.TITLE  # Formatting for titles
        self._fmtChapter = nwHeadFmt.TITLE  # Formatting for numbered chapters
        self._fmtUnNum   = nwHeadFmt.TITLE  # Formatting for unnumbered chapters
        self._fmtScene   = nwHeadFmt.TITLE  # Formatting for scenes
        self._fmtSection = nwHeadFmt.TITLE  # Formatting for sections

        self._hideScene   = False  # Do not include scene headers
        self._hideSection = False  # Do not include section headers

        self._linkHeaders = False  # Add an anchor before headers

        # Instance Variables
        self._hFormatter = HeadingFormatter(self._project)
        self._firstScene = False  # Flag to indicate that the first scene of the chapter

        # This File
        self._isNone  = False  # Document has unknown layout
        self._isNovel = False  # Document is a novel document
        self._isNote  = False  # Document is a project note
        self._isFirst = True   # Document is the first in a set

        # Error Handling
        self._errData = []

        # Function Mapping
        self._localLookup = self._project.localLookup
        self.tr = partial(QCoreApplication.translate, "Tokenizer")

        # Format RegEx
        self._rxMarkdown = [
            (QRegularExpression(nwRegEx.FMT_EI), [0, self.FMT_I_B, 0, self.FMT_I_E]),
            (QRegularExpression(nwRegEx.FMT_EB), [0, self.FMT_B_B, 0, self.FMT_B_E]),
            (QRegularExpression(nwRegEx.FMT_ST), [0, self.FMT_D_B, 0, self.FMT_D_E]),
        ]
        self._rxShortCodes = QRegularExpression(nwRegEx.FMT_SC)
        self._rxShortCodeVals = QRegularExpression(nwRegEx.FMT_SV)

        self._shortCodeFmt = {
            nwShortcode.ITALIC_O: self.FMT_I_B,   nwShortcode.ITALIC_C: self.FMT_I_E,
            nwShortcode.BOLD_O:   self.FMT_B_B,   nwShortcode.BOLD_C:   self.FMT_B_E,
            nwShortcode.STRIKE_O: self.FMT_D_B,   nwShortcode.STRIKE_C: self.FMT_D_E,
            nwShortcode.ULINE_O:  self.FMT_U_B,   nwShortcode.ULINE_C:  self.FMT_U_E,
            nwShortcode.SUP_O:    self.FMT_SUP_B, nwShortcode.SUP_C:    self.FMT_SUP_E,
            nwShortcode.SUB_O:    self.FMT_SUB_B, nwShortcode.SUB_C:    self.FMT_SUB_E,
        }

        return

    ##
    #  Properties
    ##

    @property
    def result(self) -> str:
        """The result of the build process."""
        return self._result

    @property
    def allMarkdown(self) -> list:
        """The combined novelWriter Markdown text."""
        return self._allMarkdown

    @property
    def errData(self) -> list:
        """The error data."""
        return self._errData

    ##
    #  Setters
    ##

    def setTitleFormat(self, hFormat: str) -> None:
        """Set the title format pattern."""
        self._fmtTitle = hFormat.strip()
        return

    def setChapterFormat(self, hFormat: str) -> None:
        """Set the chapter format pattern."""
        self._fmtChapter = hFormat.strip()
        return

    def setUnNumberedFormat(self, hFormat: str) -> None:
        """Set the unnumbered format pattern."""
        self._fmtUnNum = hFormat.strip()
        return

    def setSceneFormat(self, hFormat: str, hide: bool) -> None:
        """Set the scene format pattern and hidden status."""
        self._fmtScene = hFormat.strip()
        self._hideScene = hide
        return

    def setSectionFormat(self, hFormat: str, hide: bool) -> None:
        """Set the section format pattern and hidden status."""
        self._fmtSection = hFormat.strip()
        self._hideSection = hide
        return

    def setFont(self, family: str, size: int, isFixed: bool = False) -> None:
        """Set the build font."""
        self._textFont = family
        self._textSize = round(int(size))
        self._textFixed = isFixed
        return

    def setLineHeight(self, height: float) -> None:
        """Set the line height between 0.5 and 5.0."""
        self._lineHeight = min(max(float(height), 0.5), 5.0)
        return

    def setBlockIndent(self, indent: float) -> None:
        """Set the block indent between 0.0 and 10.0."""
        self._blockIndent = min(max(float(indent), 0.0), 10.0)
        return

    def setJustify(self, state: bool) -> None:
        """Enable or disable text justification."""
        self._doJustify = state
        return

    def setTitleMargins(self, upper: float, lower: float) -> None:
        """Set the upper and lower title margin."""
        self._marginTitle = (float(upper), float(lower))
        return

    def setHead1Margins(self, upper: float, lower: float) -> None:
        """Set the upper and lower header 1 margin."""
        self._marginHead1 = (float(upper), float(lower))
        return

    def setHead2Margins(self, upper: float, lower: float) -> None:
        """Set the upper and lower header 2 margin."""
        self._marginHead2 = (float(upper), float(lower))
        return

    def setHead3Margins(self, upper: float, lower: float) -> None:
        """Set the upper and lower header 3 margin."""
        self._marginHead3 = (float(upper), float(lower))
        return

    def setHead4Margins(self, upper: float, lower: float) -> None:
        """Set the upper and lower header 4 margin."""
        self._marginHead4 = (float(upper), float(lower))
        return

    def setTextMargins(self, upper: float, lower: float) -> None:
        """Set the upper and lower text margin."""
        self._marginText = (float(upper), float(lower))
        return

    def setMetaMargins(self, upper: float, lower: float) -> None:
        """Set the upper and lower meta text margin."""
        self._marginMeta = (float(upper), float(lower))
        return

    def setLinkHeaders(self, state: bool) -> None:
        """Enable or disable adding an anchor before headers."""
        self._linkHeaders = state
        return

    def setBodyText(self, state: bool) -> None:
        """Include body text in build."""
        self._doBodyText = state
        return

    def setSynopsis(self, state: bool) -> None:
        """Include synopsis comments in build."""
        self._doSynopsis = state
        return

    def setComments(self, state: bool) -> None:
        """Include comments in build."""
        self._doComments = state
        return

    def setKeywords(self, state: bool) -> None:
        """Include keywords in build."""
        self._doKeywords = state
        return

    def setKeepMarkdown(self, state: bool) -> None:
        """Keep original markdown during build."""
        self._keepMarkdown = state
        return

    ##
    #  Class Methods
    ##

    @abstractmethod
    def doConvert(self) -> None:
        raise NotImplementedError

    def addRootHeading(self, tHandle: str) -> bool:
        """Add a heading at the start of a new root folder."""
        tItem = self._project.tree[tHandle]
        if not tItem or not tItem.isRootType():
            return False

        if self._isFirst:
            textAlign = self.A_CENTRE
            self._isFirst = False
        else:
            textAlign = self.A_PBB | self.A_CENTRE

        trNotes = self._localLookup("Notes")
        title = f"{trNotes}: {tItem.itemName}"
        self._tokens = []
        self._tokens.append((
            self.T_TITLE, 0, title, [], textAlign
        ))
        if self._keepMarkdown:
            self._allMarkdown.append(f"# {title}\n\n")

        return True

    def setText(self, tHandle: str, text: str | None = None) -> bool:
        """Set the text for the tokenizer from a handle. If text is not
        set, load it from the file.
        """
        self._nwItem = self._project.tree[tHandle]
        if self._nwItem is None:
            return False

        if text is None:
            text = self._project.storage.getDocument(tHandle).readDocument() or ""

        self._text = text

        self._isNone  = self._nwItem.itemLayout == nwItemLayout.NO_LAYOUT
        self._isNovel = self._nwItem.itemLayout == nwItemLayout.DOCUMENT
        self._isNote  = self._nwItem.itemLayout == nwItemLayout.NOTE

        return True

    def doPreProcessing(self) -> None:
        """Run trough the various replace dictionaries."""
        # Process the user's auto-replace dictionary
        autoReplace = self._project.data.autoReplace
        if len(autoReplace) > 0:
            repDict = {}
            for aKey, aVal in autoReplace.items():
                repDict[f"<{aKey}>"] = aVal
            xRep = re.compile("|".join([re.escape(k) for k in repDict.keys()]), flags=re.DOTALL)
            self._text = xRep.sub(lambda x: repDict[x.group(0)], self._text)

        # Process the character translation map
        trDict = {nwUnicode.U_MAPOSS: nwUnicode.U_RSQUO}
        self._text = self._text.translate(str.maketrans(trDict))

        return

    def tokenizeText(self) -> None:
        """Scan the text for either lines starting with specific
        characters that indicate headers, comments, commands etc, or
        just contain plain text. In the case of plain text, apply the
        same RegExes that the syntax highlighter uses and save the
        locations of these formatting tags into the token array.

        The format of the token list is an entry with a five-tuple for
        each line in the file. The tuple is as follows:
          1: The type of the block, self.T_*
          2: The header number under which the text is placed
          3: The text content of the block, without leading tags
          4: The internal formatting map of the text, self.FMT_*
          5: The style of the block, self.A_*
        """
        self._tokens = []
        tmpMarkdown = []
        nHead = 0
        breakNext = False
        for aLine in self._text.splitlines():
            sLine = aLine.strip().lower()

            # Check for blank lines
            if len(sLine) == 0:
                self._tokens.append((
                    self.T_EMPTY, nHead, "", [], self.A_NONE
                ))
                if self._keepMarkdown:
                    tmpMarkdown.append("\n")

                continue

            if breakNext:
                sAlign = self.A_PBB
                breakNext = False
            else:
                sAlign = self.A_NONE

            # Check Line Format
            # =================

            if aLine[0] == "[":
                # Parse special formatting line
                # This must be a separate if statement, as it may not
                # reach a continue statement and must therefore proceed
                # to check other formats.

                if sLine in ("[newpage]", "[new page]"):
                    breakNext = True
                    continue

                elif sLine == "[vspace]":
                    self._tokens.append(
                        (self.T_SKIP, nHead, "", [], sAlign)
                    )
                    continue

                elif sLine.startswith("[vspace:") and sLine.endswith("]"):
                    nSkip = checkInt(sLine[8:-1], 0)
                    if nSkip >= 1:
                        self._tokens.append(
                            (self.T_SKIP, nHead, "", [], sAlign)
                        )
                    if nSkip > 1:
                        self._tokens += (nSkip - 1) * [
                            (self.T_SKIP, nHead, "", [], self.A_NONE)
                        ]
                    continue

            if aLine[0] == "%":
                if aLine[1] == "~":
                    # Completely ignore the paragraph
                    continue

                cStyle, cText, _ = processComment(aLine)
                if cStyle == nwComment.SYNOPSIS:
                    self._tokens.append((
                        self.T_SYNOPSIS, nHead, cText, [], sAlign
                    ))
                    if self._doSynopsis and self._keepMarkdown:
                        tmpMarkdown.append("%s\n" % aLine)
                elif cStyle == nwComment.SHORT:
                    self._tokens.append((
                        self.T_SHORT, nHead, cText, [], sAlign
                    ))
                    if self._doSynopsis and self._keepMarkdown:
                        tmpMarkdown.append("%s\n" % aLine)
                else:
                    self._tokens.append((
                        self.T_COMMENT, nHead, cText, [], sAlign
                    ))
                    if self._doComments and self._keepMarkdown:
                        tmpMarkdown.append("%s\n" % aLine)

            elif aLine[0] == "@":
                self._tokens.append((
                    self.T_KEYWORD, nHead, aLine[1:].strip(), [], sAlign
                ))
                if self._doKeywords and self._keepMarkdown:
                    tmpMarkdown.append("%s\n" % aLine)

            elif aLine[:2] == "# ":
                if self._isNovel:
                    sAlign |= self.A_CENTRE
                    sAlign |= self.A_PBB

                nHead += 1
                self._tokens.append((
                    self.T_HEAD1, nHead, aLine[2:].strip(), [], sAlign
                ))
                if self._keepMarkdown:
                    tmpMarkdown.append("%s\n" % aLine)

            elif aLine[:3] == "## ":
                if self._isNovel:
                    sAlign |= self.A_PBB

                nHead += 1
                self._tokens.append((
                    self.T_HEAD2, nHead, aLine[3:].strip(), [], sAlign
                ))
                if self._keepMarkdown:
                    tmpMarkdown.append("%s\n" % aLine)

            elif aLine[:4] == "### ":
                nHead += 1
                self._tokens.append((
                    self.T_HEAD3, nHead, aLine[4:].strip(), [], sAlign
                ))
                if self._keepMarkdown:
                    tmpMarkdown.append("%s\n" % aLine)

            elif aLine[:5] == "#### ":
                nHead += 1
                self._tokens.append((
                    self.T_HEAD4, nHead, aLine[5:].strip(), [], sAlign
                ))
                if self._keepMarkdown:
                    tmpMarkdown.append("%s\n" % aLine)

            elif aLine[:3] == "#! ":
                nHead += 1
                if self._isNovel:
                    tStyle = self.T_TITLE
                else:
                    tStyle = self.T_HEAD1

                self._tokens.append((
                    tStyle, nHead, aLine[3:].strip(), [], sAlign | self.A_CENTRE
                ))
                if self._keepMarkdown:
                    tmpMarkdown.append("%s\n" % aLine)

            elif aLine[:4] == "##! ":
                nHead += 1
                if self._isNovel:
                    tStyle = self.T_UNNUM
                    sAlign |= self.A_PBB
                else:
                    tStyle = self.T_HEAD2

                self._tokens.append((
                    tStyle, nHead, aLine[4:].strip(), [], sAlign
                ))
                if self._keepMarkdown:
                    tmpMarkdown.append("%s\n" % aLine)

            else:
                if not self._doBodyText:
                    # Skip all body text
                    continue

                # Check Alignment and Indentation
                alnLeft = False
                alnRight = False
                indLeft = False
                indRight = False
                if aLine.startswith(">>"):
                    alnRight = True
                    aLine = aLine[2:].lstrip(" ")
                elif aLine.startswith(">"):
                    indLeft = True
                    aLine = aLine[1:].lstrip(" ")

                if aLine.endswith("<<"):
                    alnLeft = True
                    aLine = aLine[:-2].rstrip(" ")
                elif aLine.endswith("<"):
                    indRight = True
                    aLine = aLine[:-1].rstrip(" ")

                if alnLeft and alnRight:
                    sAlign |= self.A_CENTRE
                elif alnLeft:
                    sAlign |= self.A_LEFT
                elif alnRight:
                    sAlign |= self.A_RIGHT

                if indLeft:
                    sAlign |= self.A_IND_L
                if indRight:
                    sAlign |= self.A_IND_R

                # Process formats
                tLine, fmtPos = self._extractFormats(aLine)
                self._tokens.append((
                    self.T_TEXT, nHead, tLine, fmtPos, sAlign
                ))
                if self._keepMarkdown:
                    tmpMarkdown.append("%s\n" % aLine)

        # If we have content, turn off the first page flag
        if self._isFirst and self._tokens:
            self._isFirst = False

            # Make sure the token array doesn't start with a page break
            # on the very first page, adding a blank first page.
            if self._tokens[0][4] & self.A_PBB:
                tToken = self._tokens[0]
                self._tokens[0] = (
                    tToken[0], tToken[1], tToken[2], tToken[3], tToken[4] & ~self.A_PBB
                )

        # Always add an empty line at the end of the file
        self._tokens.append((
            self.T_EMPTY, nHead, "", [], self.A_NONE
        ))
        if self._keepMarkdown:
            tmpMarkdown.append("\n")

        if self._keepMarkdown:
            self._allMarkdown.append("".join(tmpMarkdown))

        # Second Pass
        # ===========
        # Some items need a second pass

        pToken = (self.T_EMPTY, 0, "", [], self.A_NONE)
        nToken = (self.T_EMPTY, 0, "", [], self.A_NONE)
        tCount = len(self._tokens)
        for n, tToken in enumerate(self._tokens):

            if n > 0:
                pToken = self._tokens[n-1]
            if n < tCount - 1:
                nToken = self._tokens[n+1]

            if tToken[0] == self.T_KEYWORD:
                aStyle = tToken[4]
                if pToken[0] == self.T_KEYWORD:
                    aStyle |= self.A_Z_TOPMRG
                if nToken[0] == self.T_KEYWORD:
                    aStyle |= self.A_Z_BTMMRG
                self._tokens[n] = (
                    tToken[0], tToken[1], tToken[2], tToken[3], aStyle
                )

        return

    def doHeaders(self) -> bool:
        """Apply formatting to the text headers for novel files. This
        also applies chapter and scene numbering.
        """
        if not self._isNovel:
            return False

        self._hFormatter.setHandle(self._nwItem.itemHandle if self._nwItem else None)

        for n, tToken in enumerate(self._tokens):

            # In case we see text before a scene, we reset the flag
            if tToken[0] == self.T_TEXT:
                self._firstScene = False

            elif tToken[0] == self.T_HEAD1:
                # Partition

                tTemp = self._hFormatter.apply(self._fmtTitle, tToken[2], tToken[1])
                self._tokens[n] = (
                    tToken[0], tToken[1], tTemp, [], tToken[4]
                )

            elif tToken[0] in (self.T_HEAD2, self.T_UNNUM):
                # Chapter

                # Numbered or Unnumbered
                if tToken[0] == self.T_UNNUM:
                    tTemp = self._hFormatter.apply(self._fmtUnNum, tToken[2], tToken[1])
                else:
                    self._hFormatter.incChapter()
                    tTemp = self._hFormatter.apply(self._fmtChapter, tToken[2], tToken[1])

                # Format the chapter header
                self._tokens[n] = (
                    tToken[0], tToken[1], tTemp, [], tToken[4]
                )

                # Set scene variables
                self._firstScene = True
                self._hFormatter.resetScene()

            elif tToken[0] == self.T_HEAD3:
                # Scene

                self._hFormatter.incScene()

                tTemp = self._hFormatter.apply(self._fmtScene, tToken[2], tToken[1])
                if tTemp == "" and self._hideScene:
                    self._tokens[n] = (
                        self.T_EMPTY, tToken[1], "", [], self.A_NONE
                    )
                elif tTemp == "" and not self._hideScene:
                    if self._firstScene:
                        self._tokens[n] = (
                            self.T_EMPTY, tToken[1], "", [], self.A_NONE
                        )
                    else:
                        self._tokens[n] = (
                            self.T_SKIP, tToken[1], "", [], tToken[4]
                        )
                elif tTemp == self._fmtScene:
                    if self._firstScene:
                        self._tokens[n] = (
                            self.T_EMPTY, tToken[1], "", [], self.A_NONE
                        )
                    else:
                        self._tokens[n] = (
                            self.T_SEP, tToken[1], tTemp, [], tToken[4] | self.A_CENTRE
                        )
                else:
                    self._tokens[n] = (
                        tToken[0], tToken[1], tTemp, [], tToken[4]
                    )

                self._firstScene = False

            elif tToken[0] == self.T_HEAD4:
                # Section

                tTemp = self._hFormatter.apply(self._fmtSection, tToken[2], tToken[1])
                if tTemp == "" and self._hideSection:
                    self._tokens[n] = (
                        self.T_EMPTY, tToken[1], "", [], self.A_NONE
                    )
                elif tTemp == "" and not self._hideSection:
                    self._tokens[n] = (
                        self.T_SKIP, tToken[1], "", [], tToken[4]
                    )
                elif tTemp == self._fmtSection:
                    self._tokens[n] = (
                        self.T_SEP, tToken[1], tTemp, [], tToken[4] | self.A_CENTRE
                    )
                else:
                    self._tokens[n] = (
                        tToken[0], tToken[1], tTemp, [], tToken[4]
                    )

        return True

    def saveRawMarkdown(self, path: str | Path) -> None:
        """Save the raw text to a plain text file."""
        with open(path, mode="w", encoding="utf-8") as outFile:
            for nwdPage in self._allMarkdown:
                outFile.write(nwdPage)
        return

    def saveRawMarkdownJSON(self, path: str | Path) -> None:
        """Save the raw text to a JSON file."""
        timeStamp = time()
        data = {
            "meta": {
                "projectName": self._project.data.name,
                "novelAuthor": self._project.data.author,
                "buildTime": int(timeStamp),
                "buildTimeStr": formatTimeStamp(timeStamp),
            },
            "text": {
                "nwd": [page.rstrip("\n").split("\n") for page in self._allMarkdown],
            }
        }
        with open(path, mode="w", encoding="utf-8") as fObj:
            json.dump(data, fObj, indent=2)
        return

    ##
    #  Internal Functions
    ##

    def _extractFormats(self, text: str) -> tuple[str, list[tuple[int, int]]]:
        """Extract format markers from a text paragraph."""
        temp = []

        # Match Markdown
        for regEx, fmts in self._rxMarkdown:
            rxItt = regEx.globalMatch(text, 0)
            while rxItt.hasNext():
                rxMatch = rxItt.next()
                temp.extend(
                    [rxMatch.capturedStart(n), rxMatch.capturedLength(n), fmt]
                    for n, fmt in enumerate(fmts) if fmt > 0
                )

        # Match Shortcodes
        rxItt = self._rxShortCodes.globalMatch(text, 0)
        while rxItt.hasNext():
            rxMatch = rxItt.next()
            temp.append([
                rxMatch.capturedStart(1),
                rxMatch.capturedLength(1),
                self._shortCodeFmt.get(rxMatch.captured(1).lower(), 0)
            ])

        # Post-process text and format markers
        result = text
        formats = []
        for pos, n, fmt in reversed(sorted(temp, key=lambda x: x[0])):
            if fmt > 0:
                result = result[:pos] + result[pos+n:]
                formats = [(p-n, f) for p, f in formats]
                formats.insert(0, (pos, fmt))

        return result, formats

# END Class Tokenizer


class HeadingFormatter:

    def __init__(self, project: NWProject) -> None:
        self._project = project
        self._handle = None
        self._chCount = 0
        self._scChCount = 0
        self._scAbsCount = 0
        return

    def setHandle(self, tHandle: str | None) -> None:
        """Set the handle currently being processed."""
        self._handle = tHandle
        return

    def incChapter(self) -> None:
        """Increment the chapter counter."""
        self._chCount += 1
        return

    def incScene(self) -> None:
        """Increment the scene counters."""
        self._scChCount += 1
        self._scAbsCount += 1
        return

    def resetScene(self) -> None:
        """Reset the chapter scene counter."""
        self._scChCount = 0
        return

    def apply(self, hFormat: str, text: str, nHead: int) -> str:
        """Apply formatting to a specific heading."""
        hFormat = hFormat.replace(nwHeadFmt.TITLE, text)
        hFormat = hFormat.replace(nwHeadFmt.CH_NUM, str(self._chCount))
        hFormat = hFormat.replace(nwHeadFmt.SC_NUM, str(self._scChCount))
        hFormat = hFormat.replace(nwHeadFmt.SC_ABS, str(self._scAbsCount))
        if nwHeadFmt.CH_WORD in hFormat:
            chWord = self._project.localLookup(self._chCount)
            hFormat = hFormat.replace(nwHeadFmt.CH_WORD, chWord)
        if nwHeadFmt.CH_ROML in hFormat:
            chRom = numberToRoman(self._chCount, toLower=True)
            hFormat = hFormat.replace(nwHeadFmt.CH_ROML, chRom)
        if nwHeadFmt.CH_ROMU in hFormat:
            chRom = numberToRoman(self._chCount, toLower=False)
            hFormat = hFormat.replace(nwHeadFmt.CH_ROMU, chRom)

        if nwHeadFmt.CHAR_POV in hFormat or nwHeadFmt.CHAR_FOCUS in hFormat:
            if self._handle and nHead > 0:
                index = self._project.index
                pList = index.getReferenceForHeader(self._handle, nHead, nwKeyWords.POV_KEY)
                fList = index.getReferenceForHeader(self._handle, nHead, nwKeyWords.FOCUS_KEY)
                pText = pList[0] if pList else nwUnicode.U_ENDASH
                fText = fList[0] if fList else nwUnicode.U_ENDASH
            else:
                pText = trConst(nwLabels.KEY_NAME[nwKeyWords.POV_KEY])
                fText = trConst(nwLabels.KEY_NAME[nwKeyWords.FOCUS_KEY])
            hFormat = hFormat.replace(nwHeadFmt.CHAR_POV, pText)
            hFormat = hFormat.replace(nwHeadFmt.CHAR_FOCUS, fText)

        return hFormat

# END Class HeadingFormatter
