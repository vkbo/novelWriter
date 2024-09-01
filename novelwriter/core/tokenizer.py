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

import json
import logging
import re

from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from time import time

from PyQt5.QtCore import QCoreApplication, QRegularExpression
from PyQt5.QtGui import QFont

from novelwriter import CONFIG
from novelwriter.common import checkInt, formatTimeStamp, numberToRoman
from novelwriter.constants import nwHeadFmt, nwKeyWords, nwLabels, nwShortcode, nwUnicode, trConst
from novelwriter.core.index import processComment
from novelwriter.core.project import NWProject
from novelwriter.enum import nwComment, nwItemLayout
from novelwriter.text.patterns import REGEX_PATTERNS

logger = logging.getLogger(__name__)

ESCAPES = {r"\*": "*", r"\~": "~", r"\_": "_", r"\[": "[", r"\]": "]", r"\ ": ""}
RX_ESC = re.compile("|".join([re.escape(k) for k in ESCAPES.keys()]), flags=re.DOTALL)

T_Formats = list[tuple[int, int, str]]
T_Comment = tuple[str, T_Formats]
T_Token = tuple[int, int, str, T_Formats, int]


def stripEscape(text: str) -> str:
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
    FMT_M_B   = 9   # Begin mark
    FMT_M_E   = 10  # End mark
    FMT_SUP_B = 11  # Begin superscript
    FMT_SUP_E = 12  # End superscript
    FMT_SUB_B = 13  # Begin subscript
    FMT_SUB_E = 14  # End subscript
    FMT_DL_B  = 15  # Begin dialogue
    FMT_DL_E  = 16  # End dialogue
    FMT_ADL_B = 17  # Begin alt dialogue
    FMT_ADL_E = 18  # End alt dialogue
    FMT_FNOTE = 19  # Footnote marker
    FMT_STRIP = 20  # Strip the format code

    # Block Type
    T_EMPTY    = 1   # Empty line (new paragraph)
    T_SYNOPSIS = 2   # Synopsis comment
    T_SHORT    = 3   # Short description comment
    T_COMMENT  = 4   # Comment line
    T_KEYWORD  = 5   # Command line
    T_TITLE    = 6   # Title
    T_HEAD1    = 7   # Heading 1
    T_HEAD2    = 8   # Heading 2
    T_HEAD3    = 9   # Heading 3
    T_HEAD4    = 10  # Heading 4
    T_TEXT     = 11  # Text line
    T_SEP      = 12  # Scene separator
    T_SKIP     = 13  # Paragraph break

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
    A_IND_T    = 0x0400  # Text indentation

    # Masks
    M_ALIGNED = A_LEFT | A_RIGHT | A_CENTRE | A_JUSTIFY

    # Lookups
    L_HEADINGS = [T_TITLE, T_HEAD1, T_HEAD2, T_HEAD3, T_HEAD4]
    L_SKIP_INDENT = [T_TITLE, T_HEAD1, T_HEAD2, T_HEAD2, T_HEAD3, T_HEAD4, T_SEP, T_SKIP]
    L_SUMMARY = [T_SYNOPSIS, T_SHORT]

    def __init__(self, project: NWProject) -> None:

        self._project = project

        # Data Variables
        self._text   = ""     # The raw text to be tokenized
        self._handle = None   # The item handle currently being processed
        self._result = ""     # The result of the last document
        self._keepMD = False  # Whether to keep the markdown text

        # Tokens and Meta Data (Per Document)
        self._tokens: list[T_Token] = []
        self._footnotes: dict[str, T_Comment] = {}

        # Tokens and Meta Data (Per Instance)
        self._counts: dict[str, int] = {}
        self._outline: dict[str, str] = {}
        self._markdown: list[str] = []

        # User Settings
        self._textFont     = QFont("Serif", 11)  # Output text font
        self._lineHeight   = 1.15     # Line height in units of em
        self._blockIndent  = 4.00     # Block indent in units of em
        self._firstIndent  = False    # Enable first line indent
        self._firstWidth   = 1.40     # First line indent in units of em
        self._indentFirst  = False    # Indent first paragraph
        self._doJustify    = False    # Justify text
        self._doBodyText   = True     # Include body text
        self._doSynopsis   = False    # Also process synopsis comments
        self._doComments   = False    # Also process comments
        self._doKeywords   = False    # Also process keywords like tags and references
        self._skipKeywords = set()    # Keywords to ignore
        self._keepBreaks   = True     # Keep line breaks in paragraphs

        # Margins
        self._marginTitle = (1.417, 0.500)
        self._marginHead1 = (1.417, 0.500)
        self._marginHead2 = (1.668, 0.500)
        self._marginHead3 = (1.168, 0.500)
        self._marginHead4 = (1.168, 0.500)
        self._marginText  = (0.000, 0.584)
        self._marginMeta  = (0.000, 0.584)
        self._marginFoot  = (1.417, 0.467)
        self._marginSep   = (1.168, 1.168)

        # Title Formats
        self._fmtTitle   = nwHeadFmt.TITLE  # Formatting for titles
        self._fmtChapter = nwHeadFmt.TITLE  # Formatting for numbered chapters
        self._fmtUnNum   = nwHeadFmt.TITLE  # Formatting for unnumbered chapters
        self._fmtScene   = nwHeadFmt.TITLE  # Formatting for scenes
        self._fmtHScene  = nwHeadFmt.TITLE  # Formatting for hard scenes
        self._fmtSection = nwHeadFmt.TITLE  # Formatting for sections

        self._hideTitle   = False  # Do not include title headings
        self._hideChapter = False  # Do not include chapter headings
        self._hideUnNum   = False  # Do not include unnumbered headings
        self._hideScene   = False  # Do not include scene headings
        self._hideHScene  = False  # Do not include hard scene headings
        self._hideSection = False  # Do not include section headings

        self._linkHeadings = False  # Add an anchor before headings

        self._titleStyle   = self.A_CENTRE | self.A_PBB
        self._chapterStyle = self.A_PBB
        self._sceneStyle   = self.A_NONE

        # Instance Variables
        self._hFormatter = HeadingFormatter(self._project)
        self._noSep      = True   # Flag to indicate that we don't want a scene separator
        self._noIndent   = False  # Flag to disable text indent on next paragraph
        self._showDialog = False  # Flag for dialogue highlighting

        # This File
        self._isNovel = False  # Document is a novel document
        self._isFirst = True   # Document is the first in a set

        # Error Handling
        self._errData = []

        # Function Mapping
        self._localLookup = self._project.localLookup
        self.tr = partial(QCoreApplication.translate, "Tokenizer")

        # Format RegEx
        self._rxMarkdown = [
            (REGEX_PATTERNS.markdownItalic, [0, self.FMT_I_B, 0, self.FMT_I_E]),
            (REGEX_PATTERNS.markdownBold,   [0, self.FMT_B_B, 0, self.FMT_B_E]),
            (REGEX_PATTERNS.markdownStrike, [0, self.FMT_D_B, 0, self.FMT_D_E]),
        ]
        self._rxShortCodes = REGEX_PATTERNS.shortcodePlain
        self._rxShortCodeVals = REGEX_PATTERNS.shortcodeValue

        self._shortCodeFmt = {
            nwShortcode.ITALIC_O: self.FMT_I_B,   nwShortcode.ITALIC_C: self.FMT_I_E,
            nwShortcode.BOLD_O:   self.FMT_B_B,   nwShortcode.BOLD_C:   self.FMT_B_E,
            nwShortcode.STRIKE_O: self.FMT_D_B,   nwShortcode.STRIKE_C: self.FMT_D_E,
            nwShortcode.ULINE_O:  self.FMT_U_B,   nwShortcode.ULINE_C:  self.FMT_U_E,
            nwShortcode.MARK_O:   self.FMT_M_B,   nwShortcode.MARK_C:   self.FMT_M_E,
            nwShortcode.SUP_O:    self.FMT_SUP_B, nwShortcode.SUP_C:    self.FMT_SUP_E,
            nwShortcode.SUB_O:    self.FMT_SUB_B, nwShortcode.SUB_C:    self.FMT_SUB_E,
        }
        self._shortCodeVals = {
            nwShortcode.FOOTNOTE_B: self.FMT_FNOTE,
        }

        self._rxDialogue: list[tuple[QRegularExpression, int, int]] = []

        return

    ##
    #  Properties
    ##

    @property
    def result(self) -> str:
        """The result of the build process."""
        return self._result

    @property
    def allMarkdown(self) -> list[str]:
        """The combined novelWriter Markdown text."""
        return self._markdown

    @property
    def textStats(self) -> dict[str, int]:
        """The collected stats about the text."""
        return self._counts

    @property
    def textOutline(self) -> dict[str, str]:
        """The generated outline of the text."""
        return self._outline

    @property
    def errData(self) -> list[str]:
        """The error data."""
        return self._errData

    ##
    #  Setters
    ##

    def setTitleFormat(self, hFormat: str, hide: bool = False) -> None:
        """Set the title format pattern."""
        self._fmtTitle = hFormat.strip()
        self._hideTitle = hide
        return

    def setChapterFormat(self, hFormat: str, hide: bool = False) -> None:
        """Set the chapter format pattern."""
        self._fmtChapter = hFormat.strip()
        self._hideChapter = hide
        return

    def setUnNumberedFormat(self, hFormat: str, hide: bool = False) -> None:
        """Set the unnumbered format pattern."""
        self._fmtUnNum = hFormat.strip()
        self._hideUnNum = hide
        return

    def setSceneFormat(self, hFormat: str, hide: bool = False) -> None:
        """Set the scene format pattern and hidden status."""
        self._fmtScene = hFormat.strip()
        self._hideScene = hide
        return

    def setHardSceneFormat(self, hFormat: str, hide: bool = False) -> None:
        """Set the hard scene format pattern and hidden status."""
        self._fmtHScene = hFormat.strip()
        self._hideHScene = hide
        return

    def setSectionFormat(self, hFormat: str, hide: bool = False) -> None:
        """Set the section format pattern and hidden status."""
        self._fmtSection = hFormat.strip()
        self._hideSection = hide
        return

    def setTitleStyle(self, center: bool, pageBreak: bool) -> None:
        """Set the title heading style."""
        self._titleStyle = (
            (self.A_CENTRE if center else self.A_NONE) | (self.A_PBB if pageBreak else self.A_NONE)
        )
        return

    def setChapterStyle(self, center: bool, pageBreak: bool) -> None:
        """Set the chapter heading style."""
        self._chapterStyle = (
            (self.A_CENTRE if center else self.A_NONE) | (self.A_PBB if pageBreak else self.A_NONE)
        )
        return

    def setSceneStyle(self, center: bool, pageBreak: bool) -> None:
        """Set the scene heading style."""
        self._sceneStyle = (
            (self.A_CENTRE if center else self.A_NONE) | (self.A_PBB if pageBreak else self.A_NONE)
        )
        return

    def setFont(self, font: QFont) -> None:
        """Set the build font."""
        self._textFont = font
        return

    def setLineHeight(self, height: float) -> None:
        """Set the line height between 0.5 and 5.0."""
        self._lineHeight = min(max(float(height), 0.5), 5.0)
        return

    def setBlockIndent(self, indent: float) -> None:
        """Set the block indent between 0.0 and 10.0."""
        self._blockIndent = min(max(float(indent), 0.0), 10.0)
        return

    def setFirstLineIndent(self, state: bool, indent: float, first: bool) -> None:
        """Set first line indent and whether to also indent first
        paragraph after a heading.
        """
        self._firstIndent = state
        self._firstWidth = indent
        self._indentFirst = first
        return

    def setJustify(self, state: bool) -> None:
        """Enable or disable text justification."""
        self._doJustify = state
        return

    def setDialogueHighlight(self, state: bool) -> None:
        """Enable or disable dialogue highlighting."""
        self._rxDialogue = []
        self._showDialog = state
        if state:
            if CONFIG.dialogStyle > 0:
                self._rxDialogue.append((
                    REGEX_PATTERNS.dialogStyle, self.FMT_DL_B, self.FMT_DL_E
                ))
            if CONFIG.dialogLine:
                self._rxDialogue.append((
                    REGEX_PATTERNS.dialogLine, self.FMT_DL_B, self.FMT_DL_E
                ))
            if CONFIG.narratorBreak:
                self._rxDialogue.append((
                    REGEX_PATTERNS.narratorBreak, self.FMT_DL_E, self.FMT_DL_B
                ))
            if CONFIG.altDialogOpen and CONFIG.altDialogClose:
                self._rxDialogue.append((
                    REGEX_PATTERNS.altDialogStyle, self.FMT_ADL_B, self.FMT_ADL_E
                ))
        return

    def setTitleMargins(self, upper: float, lower: float) -> None:
        """Set the upper and lower title margin."""
        self._marginTitle = (float(upper), float(lower))
        return

    def setHead1Margins(self, upper: float, lower: float) -> None:
        """Set the upper and lower heading 1 margin."""
        self._marginHead1 = (float(upper), float(lower))
        return

    def setHead2Margins(self, upper: float, lower: float) -> None:
        """Set the upper and lower heading 2 margin."""
        self._marginHead2 = (float(upper), float(lower))
        return

    def setHead3Margins(self, upper: float, lower: float) -> None:
        """Set the upper and lower heading 3 margin."""
        self._marginHead3 = (float(upper), float(lower))
        return

    def setHead4Margins(self, upper: float, lower: float) -> None:
        """Set the upper and lower heading 4 margin."""
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

    def setSeparatorMargins(self, upper: float, lower: float) -> None:
        """Set the upper and lower meta text margin."""
        self._marginSep = (float(upper), float(lower))
        return

    def setLinkHeadings(self, state: bool) -> None:
        """Enable or disable adding an anchor before headings."""
        self._linkHeadings = state
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

    def setIgnoredKeywords(self, keywords: str) -> None:
        """Comma separated string of keywords to ignore."""
        self._skipKeywords = set(x.lower().strip() for x in keywords.split(","))
        return

    def setKeepLineBreaks(self, state: bool) -> None:
        """Keep line breaks in paragraphs."""
        self._keepBreaks = state
        return

    def setKeepMarkdown(self, state: bool) -> None:
        """Keep original markdown during build."""
        self._keepMD = state
        return

    ##
    #  Class Methods
    ##

    @abstractmethod
    def doConvert(self) -> None:
        raise NotImplementedError

    def addRootHeading(self, tHandle: str) -> None:
        """Add a heading at the start of a new root folder."""
        self._text = ""
        self._handle = None

        if (tItem := self._project.tree[tHandle]) and tItem.isRootType():
            self._handle = tHandle
            if self._isFirst:
                textAlign = self.A_CENTRE
                self._isFirst = False
            else:
                textAlign = self.A_PBB | self.A_CENTRE

            trNotes = self._localLookup("Notes")
            title = f"{trNotes}: {tItem.itemName}"
            self._tokens = []
            self._tokens.append((
                self.T_TITLE, 1, title, [], textAlign
            ))
            if self._keepMD:
                self._markdown.append(f"#! {title}\n\n")

        return

    def setText(self, tHandle: str, text: str | None = None) -> None:
        """Set the text for the tokenizer from a handle. If text is not
        set, it's is loaded from the file.
        """
        self._text = ""
        self._handle = None
        if nwItem := self._project.tree[tHandle]:
            self._text = text or self._project.storage.getDocumentText(tHandle)
            self._handle = tHandle
            self._isNovel = nwItem.itemLayout == nwItemLayout.DOCUMENT
        return

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
        trDict = {nwUnicode.U_MAPOS: nwUnicode.U_RSQUO}
        self._text = self._text.translate(str.maketrans(trDict))

        return

    def tokenizeText(self) -> None:
        """Scan the text for either lines starting with specific
        characters that indicate headings, comments, commands etc, or
        just contain plain text. In the case of plain text, apply the
        same RegExes that the syntax highlighter uses and save the
        locations of these formatting tags into the token array.

        The format of the token list is an entry with a five-tuple for
        each line in the file. The tuple is as follows:
          1: The type of the block, self.T_*
          2: The heading number under which the text is placed
          3: The text content of the block, without leading tags
          4: The internal formatting map of the text, self.FMT_*
          5: The style of the block, self.A_*
        """
        if self._isNovel:
            self._hFormatter.setHandle(self._handle)

        nHead = 0
        breakNext = False
        tmpMarkdown = []
        tHandle = self._handle or ""
        tokens: list[T_Token] = []
        for aLine in self._text.splitlines():
            sLine = aLine.strip().lower()

            # Check for blank lines
            if len(sLine) == 0:
                tokens.append((
                    self.T_EMPTY, nHead, "", [], self.A_NONE
                ))
                if self._keepMD:
                    tmpMarkdown.append("\n")

                continue

            if breakNext:
                sAlign = self.A_PBB
                breakNext = False
            else:
                sAlign = self.A_NONE

            # Check Line Format
            # =================

            if aLine.startswith("["):
                # Special Formats
                # ===============
                # Parse special formatting line. This must be a separate if
                # statement, as it may not reach a continue statement and must
                # therefore proceed to check other formats.

                if sLine in ("[newpage]", "[new page]"):
                    breakNext = True
                    continue

                elif sLine == "[vspace]":
                    tokens.append(
                        (self.T_SKIP, nHead, "", [], sAlign)
                    )
                    continue

                elif sLine.startswith("[vspace:") and sLine.endswith("]"):
                    nSkip = checkInt(sLine[8:-1], 0)
                    if nSkip >= 1:
                        tokens.append(
                            (self.T_SKIP, nHead, "", [], sAlign)
                        )
                    if nSkip > 1:
                        tokens += (nSkip - 1) * [
                            (self.T_SKIP, nHead, "", [], self.A_NONE)
                        ]
                    continue

            if aLine.startswith("%"):
                # Comments
                # ========
                # All style comments are processed and the exact type exact
                # style extracted. Ignored comments on the '%~' format are
                # skipped completely.
                if aLine.startswith("%~"):
                    continue

                cStyle, cKey, cText, _, _ = processComment(aLine)
                if cStyle == nwComment.SYNOPSIS:
                    tLine, tFmt = self._extractFormats(cText)
                    tokens.append((
                        self.T_SYNOPSIS, nHead, tLine, tFmt, sAlign
                    ))
                    if self._doSynopsis and self._keepMD:
                        tmpMarkdown.append(f"{aLine}\n")
                elif cStyle == nwComment.SHORT:
                    tLine, tFmt = self._extractFormats(cText)
                    tokens.append((
                        self.T_SHORT, nHead, tLine, tFmt, sAlign
                    ))
                    if self._doSynopsis and self._keepMD:
                        tmpMarkdown.append(f"{aLine}\n")
                elif cStyle == nwComment.FOOTNOTE:
                    tLine, tFmt = self._extractFormats(cText, skip=self.FMT_FNOTE)
                    self._footnotes[f"{tHandle}:{cKey}"] = (tLine, tFmt)
                    if self._keepMD:
                        tmpMarkdown.append(f"{aLine}\n")
                else:
                    tLine, tFmt = self._extractFormats(cText)
                    tokens.append((
                        self.T_COMMENT, nHead, tLine, tFmt, sAlign
                    ))
                    if self._doComments and self._keepMD:
                        tmpMarkdown.append(f"{aLine}\n")

            elif aLine.startswith("@"):
                # Keywords
                # ========
                # Only valid keyword lines are parsed, and any ignored keywords
                # are automatically skipped.

                valid, bits, _ = self._project.index.scanThis(aLine)
                if (
                    valid and bits and bits[0] in nwLabels.KEY_NAME
                    and bits[0] not in self._skipKeywords
                ):
                    tokens.append((
                        self.T_KEYWORD, nHead, aLine[1:].strip(), [], sAlign
                    ))
                    if self._doKeywords and self._keepMD:
                        tmpMarkdown.append(f"{aLine}\n")

            elif aLine.startswith(("# ", "#! ")):
                # Title or Partition Headings
                # ===========================
                # Main titles are allowed in any document, and they are always
                # centred and start on a new page. For novel documents, we also
                # reset all counters when such a title is encountered.
                # Partition headings are only formatted in novel documents, and
                # otherwise unchanged. Scene separators are disabled
                # immediately after partitions, and scene numbers are reset.
                isPlain = aLine.startswith("# ")

                nHead += 1
                tText = aLine[2:].strip()
                tType = self.T_HEAD1 if isPlain else self.T_TITLE
                tStyle = self.A_NONE if isPlain else (self.A_PBB | self.A_CENTRE)
                sHide = self._hideTitle if isPlain else False
                if self._isNovel:
                    if sHide:
                        tText = ""
                        tType = self.T_EMPTY
                        tStyle = self.A_NONE
                    elif isPlain:
                        tText = self._hFormatter.apply(self._fmtTitle, tText, nHead)
                        tStyle = self._titleStyle
                    if isPlain:
                        self._hFormatter.resetScene()
                    else:
                        self._hFormatter.resetAll()
                    self._noSep = True

                tokens.append((
                    tType, nHead, tText, [], tStyle
                ))
                if self._keepMD:
                    tmpMarkdown.append(f"{aLine}\n")

            elif aLine.startswith(("## ", "##! ")):
                # (Unnumbered) Chapter Headings
                # =============================
                # Chapter headings are only formatted in novel documents, and
                # otherwise unchanged. Chapter numbers are bumped before the
                # heading is formatted. Scene separators are disabled
                # immediately after chapter headings, and scene numbers are
                # reset. Unnumbered chapters are only meaningful in Novel docs,
                # so if we're in a note, we keep them as level 2 headings.
                isPlain = aLine.startswith("## ")

                nHead += 1
                tText = aLine[3:].strip()
                tType = self.T_HEAD2
                tStyle = self.A_NONE
                sHide = self._hideChapter if isPlain else self._hideUnNum
                tFormat = self._fmtChapter if isPlain else self._fmtUnNum
                if self._isNovel:
                    if isPlain:
                        self._hFormatter.incChapter()
                    if sHide:
                        tText = ""
                        tType = self.T_EMPTY
                    else:
                        tText = self._hFormatter.apply(tFormat, tText, nHead)
                        tStyle = self._chapterStyle
                    self._hFormatter.resetScene()
                    self._noSep = True

                tokens.append((
                    tType, nHead, tText, [], tStyle
                ))
                if self._keepMD:
                    tmpMarkdown.append(f"{aLine}\n")

            elif aLine.startswith(("### ", "###! ")):
                # (Alternative) Scene Headings
                # ============================
                # Scene headings in novel documents are treated as centred
                # separators if the formatting does not change the text. If the
                # format is empty, the scene can be hidden or a blank paragraph
                # (skip). When the scene title has static text or no text, it
                # is always ignored if the noSep flag is set. This prevents
                # separators immediately after other titles. Scene numbers are
                # always incremented before formatting. For notes, the heading
                # is unchanged.
                isPlain = aLine.startswith("### ")

                nHead += 1
                tText = aLine[4:].strip()
                tType = self.T_HEAD3
                tStyle = self.A_NONE
                sHide = self._hideScene if isPlain else self._hideHScene
                tFormat = self._fmtScene if isPlain else self._fmtHScene
                if self._isNovel:
                    self._hFormatter.incScene()
                    if sHide:
                        tText = ""
                        tType = self.T_EMPTY
                    else:
                        tText = self._hFormatter.apply(tFormat, tText, nHead)
                        tStyle = self._sceneStyle
                        if tText == "":  # Empty Format
                            tType = self.T_EMPTY if self._noSep else self.T_SKIP
                        elif tText == tFormat:  # Static Format
                            tText = "" if self._noSep else tText
                            tType = self.T_EMPTY if self._noSep else self.T_SEP
                            tStyle = self.A_NONE if self._noSep else self.A_CENTRE
                    self._noSep = False

                tokens.append((
                    tType, nHead, tText, [], tStyle
                ))
                if self._keepMD:
                    tmpMarkdown.append(f"{aLine}\n")

            elif aLine.startswith("#### "):
                # Section Headings
                # =================
                # Section headings in novel docs are treated as centred
                # separators if the formatting does not change the text. If the
                # format is empty, the section can be hidden or a blank
                # paragraph (skip). For notes, the heading is unchanged.

                nHead += 1
                tText = aLine[5:].strip()
                tType = self.T_HEAD4
                tStyle = self.A_NONE
                if self._isNovel:
                    if self._hideSection:
                        tText = ""
                        tType = self.T_EMPTY
                    else:
                        tText = self._hFormatter.apply(self._fmtSection, tText, nHead)
                        if tText == "":  # Empty Format
                            tType = self.T_SKIP
                        elif tText == self._fmtSection:  # Static Format
                            tType = self.T_SEP
                            tStyle = self.A_CENTRE

                tokens.append((
                    tType, nHead, tText, [], tStyle
                ))
                if self._keepMD:
                    tmpMarkdown.append(f"{aLine}\n")

            else:
                # Text Lines
                # ==========
                # Anything remaining at this point is body text. If body text
                # is not disabled, we proceed to process text formatting.
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
                tLine, tFmt = self._extractFormats(aLine, hDialog=self._isNovel)
                tokens.append((
                    self.T_TEXT, nHead, tLine, tFmt, sAlign
                ))
                if self._keepMD:
                    tmpMarkdown.append(f"{aLine}\n")

        # If we have content, turn off the first page flag
        if self._isFirst and tokens:
            self._isFirst = False  # First document has been processed

            # Make sure the token array doesn't start with a page break
            # on the very first page, adding a blank first page.
            if tokens[0][4] & self.A_PBB:
                cToken = tokens[0]
                tokens[0] = (
                    cToken[0], cToken[1], cToken[2], cToken[3], cToken[4] & ~self.A_PBB
                )

        # Always add an empty line at the end of the file
        tokens.append((
            self.T_EMPTY, nHead, "", [], self.A_NONE
        ))
        if self._keepMD:
            tmpMarkdown.append("\n")
            self._markdown.append("".join(tmpMarkdown))

        # Second Pass
        # ===========
        # This second pass strips away consecutive blank lines, and
        # combines consecutive text lines into the same paragraph.
        # It also ensures that there isn't paragraph spacing between
        # meta data lines for formats that has spacing.

        self._tokens = []
        pToken: T_Token = (self.T_EMPTY, 0, "", [], self.A_NONE)
        nToken: T_Token = (self.T_EMPTY, 0, "", [], self.A_NONE)

        lineSep = "\n" if self._keepBreaks else " "
        pLines: list[T_Token] = []

        tCount = len(tokens)
        for n, cToken in enumerate(tokens):

            if n > 0:
                pToken = tokens[n-1]  # Look behind
            if n < tCount - 1:
                nToken = tokens[n+1]  # Look ahead

            if cToken[0] in self.L_SKIP_INDENT and not self._indentFirst:
                # Unless the indentFirst flag is set, we set up the next
                # paragraph to not be indented if we see a block of a
                # specific type
                self._noIndent = True

            if cToken[0] == self.T_EMPTY:
                # We don't need to keep the empty lines after this pass
                pass

            elif cToken[0] == self.T_KEYWORD:
                # Adjust margins for lines in a list of keyword lines
                aStyle = cToken[4]
                if pToken[0] == self.T_KEYWORD:
                    aStyle |= self.A_Z_TOPMRG
                if nToken[0] == self.T_KEYWORD:
                    aStyle |= self.A_Z_BTMMRG
                self._tokens.append((
                    cToken[0], cToken[1], cToken[2], cToken[3], aStyle
                ))

            elif cToken[0] == self.T_TEXT:
                # Combine lines from the same paragraph
                pLines.append(cToken)

                if nToken[0] != self.T_TEXT:
                    # Next token is not text, so we add the buffer to tokens
                    nLines = len(pLines)
                    cStyle = pLines[0][4]
                    if self._firstIndent and not (self._noIndent or cStyle & self.M_ALIGNED):
                        # If paragraph indentation is enabled, not temporarily
                        # turned off, and the block is not aligned, we add the
                        # text indentation flag
                        cStyle |= self.A_IND_T

                    if nLines == 1:
                        # The paragraph contains a single line, so we just
                        # save that directly to the token list
                        self._tokens.append((
                            self.T_TEXT, pLines[0][1], pLines[0][2], pLines[0][3], cStyle
                        ))
                    elif nLines > 1:
                        # The paragraph contains multiple lines, so we need to
                        # join them according to the line break policy, and
                        # recompute all the formatting markers
                        tTxt = ""
                        tFmt: T_Formats = []
                        for aToken in pLines:
                            tLen = len(tTxt)
                            tTxt += f"{aToken[2]}{lineSep}"
                            tFmt.extend((p+tLen, fmt, key) for p, fmt, key in aToken[3])
                        self._tokens.append((
                            self.T_TEXT, pLines[0][1], tTxt[:-1], tFmt, cStyle
                        ))

                    # Reset buffer and make sure text indent is on for next pass
                    pLines = []
                    self._noIndent = False

            else:
                self._tokens.append(cToken)

        return

    def buildOutline(self) -> None:
        """Build an outline of the text up to level 3 headings."""
        tHandle = self._handle or ""
        isNovel = self._isNovel
        for tType, nHead, tText, _, _ in self._tokens:
            if tType == self.T_TITLE:
                prefix = "TT"
            elif tType == self.T_HEAD1:
                prefix = "PT" if isNovel else "H1"
            elif tType == self.T_HEAD2:
                prefix = "CH" if isNovel else "H2"
            elif tType == self.T_HEAD3:
                prefix = "SC" if isNovel else "H3"
            else:
                continue

            key = f"{tHandle}:T{nHead:04d}"
            text = tText.replace(nwHeadFmt.BR, " ").replace("&amp;", "&")
            self._outline[key] = f"{prefix}|{text}"

        return

    def countStats(self) -> None:
        """Count stats on the tokenized text."""
        titleCount = self._counts.get("titleCount", 0)
        paragraphCount = self._counts.get("paragraphCount", 0)

        allWords = self._counts.get("allWords", 0)
        textWords = self._counts.get("textWords", 0)
        titleWords = self._counts.get("titleWords", 0)

        allChars = self._counts.get("allChars", 0)
        textChars = self._counts.get("textChars", 0)
        titleChars = self._counts.get("titleChars", 0)

        allWordChars = self._counts.get("allWordChars", 0)
        textWordChars = self._counts.get("textWordChars", 0)
        titleWordChars = self._counts.get("titleWordChars", 0)

        for tType, _, tText, _, _ in self._tokens:
            tText = tText.replace(nwUnicode.U_ENDASH, " ")
            tText = tText.replace(nwUnicode.U_EMDASH, " ")

            tWords = tText.split()
            nWords = len(tWords)
            nChars = len(tText)
            nWChars = len("".join(tWords))

            if tType == self.T_TEXT:
                tPWords = tText.split()
                nPWords = len(tPWords)
                nPChars = len(tText)
                nPWChars = len("".join(tPWords))

                paragraphCount += 1
                allWords += nPWords
                textWords += nPWords
                allChars += nPChars
                textChars += nPChars
                allWordChars += nPWChars
                textWordChars += nPWChars

            elif tType in self.L_HEADINGS:
                titleCount += 1
                allWords += nWords
                titleWords += nWords
                allChars += nChars
                allWordChars += nWChars
                titleChars += nChars
                titleWordChars += nWChars

            elif tType == self.T_SEP:
                allWords += nWords
                allChars += nChars
                allWordChars += nWChars

            elif tType == self.T_SYNOPSIS and self._doSynopsis:
                text = "{0}: {1}".format(self._localLookup("Synopsis"), tText)
                words = text.split()
                allWords += len(words)
                allChars += len(text)
                allWordChars += len("".join(words))

            elif tType == self.T_SHORT and self._doSynopsis:
                text = "{0}: {1}".format(self._localLookup("Short Description"), tText)
                words = text.split()
                allWords += len(words)
                allChars += len(text)
                allWordChars += len("".join(words))

            elif tType == self.T_COMMENT and self._doComments:
                text = "{0}: {1}".format(self._localLookup("Comment"), tText)
                words = text.split()
                allWords += len(words)
                allChars += len(text)
                allWordChars += len("".join(words))

            elif tType == self.T_KEYWORD and self._doKeywords:
                valid, bits, _ = self._project.index.scanThis("@"+tText)
                if valid and bits:
                    key = self._localLookup(nwLabels.KEY_NAME[bits[0]])
                    text = "{0}: {1}".format(key, ", ".join(bits[1:]))
                    words = text.split()
                    allWords += len(words)
                    allChars += len(text)
                    allWordChars += len("".join(words))

        self._counts["titleCount"] = titleCount
        self._counts["paragraphCount"] = paragraphCount

        self._counts["allWords"] = allWords
        self._counts["textWords"] = textWords
        self._counts["titleWords"] = titleWords

        self._counts["allChars"] = allChars
        self._counts["textChars"] = textChars
        self._counts["titleChars"] = titleChars

        self._counts["allWordChars"] = allWordChars
        self._counts["textWordChars"] = textWordChars
        self._counts["titleWordChars"] = titleWordChars

        return

    def saveRawMarkdown(self, path: str | Path) -> None:
        """Save the raw text to a plain text file."""
        with open(path, mode="w", encoding="utf-8") as outFile:
            for nwdPage in self._markdown:
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
                "nwd": [page.rstrip("\n").split("\n") for page in self._markdown],
            }
        }
        with open(path, mode="w", encoding="utf-8") as fObj:
            json.dump(data, fObj, indent=2)
        return

    ##
    #  Internal Functions
    ##

    def _extractFormats(
        self, text: str, skip: int = 0, hDialog: bool = False
    ) -> tuple[str, T_Formats]:
        """Extract format markers from a text paragraph. In order to
        also process dialogue highlighting, the hDialog flag must be set
        to True. See issues #2011 and #2013.
        """
        temp: list[tuple[int, int, int, str]] = []

        # Match Markdown
        for regEx, fmts in self._rxMarkdown:
            rxItt = regEx.globalMatch(text, 0)
            while rxItt.hasNext():
                rxMatch = rxItt.next()
                temp.extend(
                    (rxMatch.capturedStart(n), rxMatch.capturedLength(n), fmt, "")
                    for n, fmt in enumerate(fmts) if fmt > 0
                )

        # Match Shortcodes
        rxItt = self._rxShortCodes.globalMatch(text, 0)
        while rxItt.hasNext():
            rxMatch = rxItt.next()
            temp.append((
                rxMatch.capturedStart(1),
                rxMatch.capturedLength(1),
                self._shortCodeFmt.get(rxMatch.captured(1).lower(), 0),
                "",
            ))

        # Match Shortcode w/Values
        rxItt = self._rxShortCodeVals.globalMatch(text, 0)
        tHandle = self._handle or ""
        while rxItt.hasNext():
            rxMatch = rxItt.next()
            kind = self._shortCodeVals.get(rxMatch.captured(1).lower(), 0)
            temp.append((
                rxMatch.capturedStart(0),
                rxMatch.capturedLength(0),
                self.FMT_STRIP if kind == skip else kind,
                f"{tHandle}:{rxMatch.captured(2)}",
            ))

        # Match Dialogue
        if self._rxDialogue and hDialog:
            for regEx, fmtB, fmtE in self._rxDialogue:
                rxItt = regEx.globalMatch(text, 0)
                while rxItt.hasNext():
                    rxMatch = rxItt.next()
                    temp.append((rxMatch.capturedStart(0), 0, fmtB, ""))
                    temp.append((rxMatch.capturedEnd(0), 0, fmtE, ""))

        # Post-process text and format
        result = text
        formats = []
        for pos, n, fmt, key in reversed(sorted(temp, key=lambda x: x[0])):
            if fmt > 0:
                if n > 0:
                    result = result[:pos] + result[pos+n:]
                    formats = [(p-n if p > pos else p, f, k) for p, f, k in formats]
                formats.insert(0, (pos, fmt, key))

        return result, formats


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

    def resetAll(self) -> None:
        """Reset all counters."""
        self._chCount = 0
        self._scChCount = 0
        self._scAbsCount = 0
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
