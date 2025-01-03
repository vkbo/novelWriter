"""
novelWriter – Text Tokenizer
============================

File History:
Created: 2019-05-05 [0.0.1] Tokenizer
Created: 2023-05-23 [2.1b1] HeadingFormatter

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

import logging
import re

from abc import ABC, abstractmethod
from pathlib import Path
from typing import NamedTuple

from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QColor, QFont

from novelwriter import CONFIG
from novelwriter.common import checkInt, fontMatcher, numberToRoman
from novelwriter.constants import (
    nwHeadFmt, nwKeyWords, nwLabels, nwShortcode, nwStats, nwStyles, nwUnicode,
    trConst
)
from novelwriter.core.index import processComment
from novelwriter.core.project import NWProject
from novelwriter.enum import nwComment, nwItemLayout
from novelwriter.formats.shared import (
    BlockFmt, BlockTyp, T_Block, T_Formats, T_Note, TextDocumentTheme, TextFmt
)
from novelwriter.text.patterns import REGEX_PATTERNS, DialogParser

logger = logging.getLogger(__name__)


class ComStyle(NamedTuple):

    label: str = ""
    labelClass: str = ""
    textClass: str = ""


COMMENT_STYLE = {
    nwComment.PLAIN:    ComStyle("Comment", "comment", "comment"),
    nwComment.IGNORE:   ComStyle(),
    nwComment.SYNOPSIS: ComStyle("Synopsis", "modifier", "synopsis"),
    nwComment.SHORT:    ComStyle("Short Description", "modifier", "synopsis"),
    nwComment.NOTE:     ComStyle("Note", "modifier", "note"),
    nwComment.FOOTNOTE: ComStyle("", "modifier", "note"),
    nwComment.COMMENT:  ComStyle(),
    nwComment.STORY:    ComStyle("", "modifier", "note"),
}
HEADINGS = [BlockTyp.TITLE, BlockTyp.HEAD1, BlockTyp.HEAD2, BlockTyp.HEAD3, BlockTyp.HEAD4]
SKIP_INDENT = [
    BlockTyp.TITLE, BlockTyp.HEAD1, BlockTyp.HEAD2, BlockTyp.HEAD2, BlockTyp.HEAD3,
    BlockTyp.HEAD4, BlockTyp.SEP, BlockTyp.SKIP,
]
B_EMPTY: T_Block = (BlockTyp.EMPTY, "", "", [], BlockFmt.NONE)


class Tokenizer(ABC):
    """Core: Text Tokenizer Abstract Base Class

    This is the base class for all document build classes. It parses the
    novelWriter markup format and generates a registry of tokens and
    text that can be further processed into other output formats by
    subclasses.
    """

    def __init__(self, project: NWProject) -> None:

        self._project = project

        # Data Variables
        self._text     = ""     # The raw text to be tokenized
        self._handle   = None   # The item handle currently being processed
        self._keepRaw  = False  # Whether to keep the raw text, used by ToRaw
        self._noTokens = False  # Disable tokenization if they're not needed

        # Blocks and Meta Data (Per Document)
        self._blocks: list[T_Block] = []
        self._footnotes: dict[str, T_Note] = {}

        # Blocks and Meta Data (Per Instance)
        self._raw: list[str] = []
        self._pages: list[str] = []
        self._counts: dict[str, int] = {}
        self._outline: dict[str, str] = {}

        # User Settings
        self._dLocale      = CONFIG.locale  # The document locale
        self._textFont     = QFont("Serif", 11)  # Output text font
        self._lineHeight   = 1.15    # Line height in units of em
        self._colorHeads   = True    # Colourise headings
        self._scaleHeads   = True    # Scale headings to larger font size
        self._boldHeads    = True    # Bold headings
        self._blockIndent  = 4.00    # Block indent in units of em
        self._firstIndent  = False   # Enable first line indent
        self._firstWidth   = 1.40    # First line indent in units of em
        self._indentFirst  = False   # Indent first paragraph
        self._doJustify    = False   # Justify text
        self._doBodyText   = True    # Include body text
        self._doSynopsis   = False   # Also process synopsis comments
        self._doComments   = False   # Also process comments
        self._doKeywords   = False   # Also process keywords like tags and references
        self._keepBreaks   = True    # Keep line breaks in paragraphs
        self._defaultAlign = "left"  # The default text alignment

        self._skipKeywords: set[str] = set()  # Keywords to ignore

        # Other Setting
        self._theme = TextDocumentTheme()
        self._classes: dict[str, QColor] = {}

        # Margins
        self._marginTitle = nwStyles.T_MARGIN["H0"]
        self._marginHead1 = nwStyles.T_MARGIN["H1"]
        self._marginHead2 = nwStyles.T_MARGIN["H2"]
        self._marginHead3 = nwStyles.T_MARGIN["H3"]
        self._marginHead4 = nwStyles.T_MARGIN["H4"]
        self._marginText  = nwStyles.T_MARGIN["TT"]
        self._marginMeta  = nwStyles.T_MARGIN["MT"]
        self._marginFoot  = nwStyles.T_MARGIN["FT"]
        self._marginSep   = nwStyles.T_MARGIN["SP"]

        # Title Formats
        self._fmtPart    = nwHeadFmt.TITLE  # Formatting for partitions
        self._fmtChapter = nwHeadFmt.TITLE  # Formatting for numbered chapters
        self._fmtUnNum   = nwHeadFmt.TITLE  # Formatting for unnumbered chapters
        self._fmtScene   = nwHeadFmt.TITLE  # Formatting for scenes
        self._fmtHScene  = nwHeadFmt.TITLE  # Formatting for hard scenes
        self._fmtSection = nwHeadFmt.TITLE  # Formatting for sections

        self._hidePart    = False  # Do not include partition headings
        self._hideChapter = False  # Do not include chapter headings
        self._hideUnNum   = False  # Do not include unnumbered headings
        self._hideScene   = False  # Do not include scene headings
        self._hideHScene  = False  # Do not include hard scene headings
        self._hideSection = False  # Do not include section headings

        self._linkHeadings = False  # Add an anchor before headings

        self._titleStyle   = BlockFmt.CENTRE | BlockFmt.PBB
        self._partStyle    = BlockFmt.CENTRE | BlockFmt.PBB
        self._chapterStyle = BlockFmt.PBB
        self._sceneStyle   = BlockFmt.NONE

        # Instance Variables
        self._hFormatter = HeadingFormatter(self._project)
        self._noSep      = True   # Flag to indicate that we don't want a scene separator
        self._noIndent   = False  # Flag to disable text indent on next paragraph
        self._breakNext  = False  # Add a page break on next token

        # This File
        self._isNovel = False  # Document is a novel document
        self._isFirst = True   # Document is the first in a set

        # Error Handling
        self._errData = []

        # Function Mapping
        self._localLookup = self._project.localLookup

        # Format RegEx
        self._rxMarkdown = [
            (REGEX_PATTERNS.markdownItalic, [0, TextFmt.I_B, 0, TextFmt.I_E]),
            (REGEX_PATTERNS.markdownBold,   [0, TextFmt.B_B, 0, TextFmt.B_E]),
            (REGEX_PATTERNS.markdownStrike, [0, TextFmt.D_B, 0, TextFmt.D_E]),
        ]

        self._shortCodeFmt = {
            nwShortcode.ITALIC_O: TextFmt.I_B,   nwShortcode.ITALIC_C: TextFmt.I_E,
            nwShortcode.BOLD_O:   TextFmt.B_B,   nwShortcode.BOLD_C:   TextFmt.B_E,
            nwShortcode.STRIKE_O: TextFmt.D_B,   nwShortcode.STRIKE_C: TextFmt.D_E,
            nwShortcode.ULINE_O:  TextFmt.U_B,   nwShortcode.ULINE_C:  TextFmt.U_E,
            nwShortcode.MARK_O:   TextFmt.M_B,   nwShortcode.MARK_C:   TextFmt.M_E,
            nwShortcode.SUP_O:    TextFmt.SUP_B, nwShortcode.SUP_C:    TextFmt.SUP_E,
            nwShortcode.SUB_O:    TextFmt.SUB_B, nwShortcode.SUB_C:    TextFmt.SUB_E,
        }
        self._shortCodeVals = {
            nwShortcode.FOOTNOTE_B: TextFmt.FNOTE,
            nwShortcode.FIELD_B:    TextFmt.FIELD,
        }

        # Dialogue
        self._hlightDialog = False
        self._rxAltDialog = REGEX_PATTERNS.altDialogStyle
        self._dialogParser = DialogParser()
        self._dialogParser.initParser()

        return

    ##
    #  Properties
    ##

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

    def setLanguage(self, language: str | None) -> None:
        """Set language for the document."""
        if language:
            self._dLocale = QLocale(language)
        return

    def setTheme(self, theme: TextDocumentTheme) -> None:
        """Set the document colour theme."""
        self._theme = theme
        return

    def setPartitionFormat(self, hFormat: str, hide: bool = False) -> None:
        """Set the partition format pattern."""
        self._fmtPart = hFormat.strip()
        self._hidePart = hide
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
        self._titleStyle = BlockFmt.CENTRE if center else BlockFmt.NONE
        self._titleStyle |= BlockFmt.PBB if pageBreak else BlockFmt.NONE
        return

    def setPartitionStyle(self, center: bool, pageBreak: bool) -> None:
        """Set the partition heading style."""
        self._partStyle = BlockFmt.CENTRE if center else BlockFmt.NONE
        self._partStyle |= BlockFmt.PBB if pageBreak else BlockFmt.NONE
        return

    def setChapterStyle(self, center: bool, pageBreak: bool) -> None:
        """Set the chapter heading style."""
        self._chapterStyle = BlockFmt.CENTRE if center else BlockFmt.NONE
        self._chapterStyle |= BlockFmt.PBB if pageBreak else BlockFmt.NONE
        return

    def setSceneStyle(self, center: bool, pageBreak: bool) -> None:
        """Set the scene heading style."""
        self._sceneStyle = BlockFmt.CENTRE if center else BlockFmt.NONE
        self._sceneStyle |= BlockFmt.PBB if pageBreak else BlockFmt.NONE
        return

    def setTextFont(self, font: QFont) -> None:
        """Set the build font."""
        self._textFont = fontMatcher(font)
        return

    def setLineHeight(self, height: float) -> None:
        """Set the line height between 0.5 and 5.0."""
        self._lineHeight = min(max(float(height), 0.5), 5.0)
        return

    def setHeadingStyles(self, color: bool, scale: bool, bold: bool) -> None:
        """Set text style for headings."""
        self._colorHeads = color
        self._scaleHeads = scale
        self._boldHeads = bold
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

    def setDialogHighlight(self, state: bool) -> None:
        """Enable or disable dialogue highlighting."""
        self._hlightDialog = state
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

    ##
    #  Class Methods
    ##

    @abstractmethod
    def doConvert(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def closeDocument(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def saveDocument(self, path: Path) -> None:
        raise NotImplementedError

    def initDocument(self) -> None:
        """Initialise data after settings."""
        self._classes["modifier"] = self._theme.modifier
        self._classes["synopsis"] = self._theme.note
        self._classes["comment"] = self._theme.comment
        self._classes["dialog"] = self._theme.dialog
        self._classes["altdialog"] = self._theme.altdialog
        self._classes["tag"] = self._theme.tag
        self._classes["keyword"] = self._theme.keyword
        self._classes["optional"] = self._theme.optional
        return

    def setBreakNext(self) -> None:
        """Set a page break for next block."""
        self._breakNext = True
        return

    def addRootHeading(self, tHandle: str) -> None:
        """Add a heading at the start of a new root folder."""
        self._text = ""
        self._handle = None

        if (item := self._project.tree[tHandle]) and item.isRootType():
            self._handle = tHandle
            style = BlockFmt.CENTRE
            if self._isFirst:
                self._isFirst = False
            else:
                style |= BlockFmt.PBB

            title = item.itemName
            if not item.isNovelLike():
                notes = self._localLookup("Notes")
                title = f"{notes}: {title}"

            self._blocks = [(
                BlockTyp.TITLE, f"{self._handle}:T0001", title, [], style
            )]
            if self._keepRaw:
                self._raw.append(f"#! {title}\n\n")

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
        """Run pre-processing jobs before the text is tokenized."""
        # Process the user's auto-replace dictionary
        if autoReplace := self._project.data.autoReplace:
            repDict = {}
            for aKey, aVal in autoReplace.items():
                repDict[f"<{aKey}>"] = aVal
            xRep = re.compile("|".join([re.escape(k) for k in repDict.keys()]), flags=re.DOTALL)
            self._text = xRep.sub(lambda x: repDict[x.group(0)], self._text)
        return

    def tokenizeText(self) -> None:
        """Scan the text for either lines starting with specific
        characters that indicate headings, comments, commands etc, or
        just contain plain text. In the case of plain text, apply the
        same RegExes that the syntax highlighter uses and save the
        locations of these formatting tags into the blocks list.

        The format of the blocs list is an entry with a five-tuple for
        each line in the file. The tuple is as follows:
          1: The type of the block, BlockType.*
          2: The heading number under which the text is placed
          3: The text content of the block, without leading tags
          4: The internal formatting map of the text, TxtFmt.*
          5: The formats of the block, BlockFmt.*
        """
        if self._keepRaw:
            self._raw.append(f"{self._text.rstrip()}\n\n")
        if self._noTokens:
            return
        if self._isNovel:
            self._hFormatter.setHandle(self._handle)

        # Cache Flags
        isNovel = self._isNovel
        doJustify = self._doJustify
        keepBreaks = self._keepBreaks
        indentFirst = self._indentFirst
        firstIndent = self._firstIndent

        # Replace all instances of [br] with a placeholder character
        text = REGEX_PATTERNS.lineBreak.sub(nwUnicode.U_NAC2, self._text)

        # Translation Maps
        transMapA = str.maketrans({
            nwUnicode.U_NAC2:  "",  # Used when [br] is ignored
            nwUnicode.U_MAPOS: nwUnicode.U_RSQUO,
            nwUnicode.U_HBAR:  nwUnicode.U_EMDASH,
        })
        transMapB = str.maketrans({
            nwUnicode.U_NAC2:  "\n",  # Used when [br] is not ignored
            nwUnicode.U_MAPOS: nwUnicode.U_RSQUO,
            nwUnicode.U_HBAR:  nwUnicode.U_EMDASH,
        })

        nHead = 0
        tHandle = self._handle or ""
        tBlocks: list[T_Block] = [B_EMPTY]
        for bLine in text.splitlines():
            aLine = bLine.translate(transMapA)
            sLine = aLine.strip().lower()

            # Check for blank lines
            if not sLine:
                tBlocks.append(B_EMPTY)
                continue

            if self._breakNext:
                tStyle = BlockFmt.PBB
                self._breakNext = False
            else:
                tStyle = BlockFmt.NONE

            # Check Line Format
            # =================

            if aLine.startswith("["):
                # Special Formats
                # ===============
                # Parse special formatting line. This must be a separate if
                # statement, as it may not reach a continue statement and must
                # therefore proceed to check other formats.

                if sLine in ("[newpage]", "[new page]"):
                    self._breakNext = True
                    continue

                elif sLine == "[vspace]":
                    tBlocks.append(
                        (BlockTyp.SKIP, "", "", [], tStyle)
                    )
                    continue

                elif sLine.startswith("[vspace:") and sLine.endswith("]"):
                    nSkip = checkInt(sLine[8:-1], 0)
                    if nSkip >= 1:
                        tBlocks.append(
                            (BlockTyp.SKIP, "", "", [], tStyle)
                        )
                    if nSkip > 1:
                        tBlocks += (nSkip - 1) * [
                            (BlockTyp.SKIP, "", "", [], BlockFmt.NONE)
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
                if cStyle in (nwComment.SYNOPSIS, nwComment.SHORT) and not self._doSynopsis:
                    continue
                if cStyle == nwComment.PLAIN and not self._doComments:
                    continue

                if doJustify and not tStyle & BlockFmt.ALIGNED:
                    tStyle |= BlockFmt.JUSTIFY

                if cStyle in (nwComment.SYNOPSIS, nwComment.SHORT, nwComment.PLAIN):
                    bStyle = COMMENT_STYLE[cStyle]
                    tLine, tFmt = self._formatComment(bStyle, cKey, cText)
                    tBlocks.append((
                        BlockTyp.COMMENT, "", tLine, tFmt, tStyle
                    ))

                elif cStyle == nwComment.FOOTNOTE:
                    tLine, tFmt = self._extractFormats(cText, skip=TextFmt.FNOTE)
                    self._footnotes[f"{tHandle}:{cKey}"] = (tLine, tFmt)

            elif aLine.startswith("@"):
                # Keywords
                # ========
                # Only valid keyword lines are parsed, and any ignored keywords
                # are automatically skipped.

                if self._doKeywords:
                    tTag, tLine, tFmt = self._formatMeta(aLine)
                    if tLine:
                        tBlocks.append((
                            BlockTyp.KEYWORD, tTag[1:], tLine, tFmt, tStyle
                        ))

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
                tType = BlockTyp.HEAD1 if isPlain else BlockTyp.TITLE
                sHide = self._hidePart if isPlain else False
                if not (isPlain or isNovel and sHide):
                    tStyle |= self._titleStyle
                if isNovel:
                    if sHide:
                        tText = ""
                        tType = BlockTyp.EMPTY
                    elif isPlain:
                        tText = self._hFormatter.apply(self._fmtPart, tText, nHead)
                        tStyle |= self._partStyle
                    if isPlain:
                        self._hFormatter.resetScene()
                    else:
                        self._hFormatter.resetAll()
                    self._noSep = True

                tBlocks.append((
                    tType, f"{tHandle}:T{nHead:04d}", tText, [], tStyle
                ))

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
                tType = BlockTyp.HEAD2
                sHide = self._hideChapter if isPlain else self._hideUnNum
                tFormat = self._fmtChapter if isPlain else self._fmtUnNum
                if isNovel:
                    if isPlain:
                        self._hFormatter.incChapter()
                    if sHide:
                        tText = ""
                        tType = BlockTyp.EMPTY
                    else:
                        tText = self._hFormatter.apply(tFormat, tText, nHead)
                        tStyle |= self._chapterStyle
                    self._hFormatter.resetScene()
                    self._noSep = True

                tBlocks.append((
                    tType, f"{tHandle}:T{nHead:04d}", tText, [], tStyle
                ))

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
                tType = BlockTyp.HEAD3
                sHide = self._hideScene if isPlain else self._hideHScene
                tFormat = self._fmtScene if isPlain else self._fmtHScene
                if isNovel:
                    self._hFormatter.incScene()
                    if sHide:
                        tText = ""
                        tType = BlockTyp.EMPTY
                    else:
                        tText = self._hFormatter.apply(tFormat, tText, nHead)
                        tStyle |= self._sceneStyle
                        if tText == "":  # Empty Format
                            tType = BlockTyp.EMPTY if self._noSep else BlockTyp.SKIP
                        elif tText == tFormat:  # Static Format
                            tText = "" if self._noSep else tText
                            tType = BlockTyp.EMPTY if self._noSep else BlockTyp.SEP
                            tStyle |= BlockFmt.NONE if self._noSep else BlockFmt.CENTRE
                    self._noSep = False

                tBlocks.append((
                    tType, f"{tHandle}:T{nHead:04d}", tText, [], tStyle
                ))

            elif aLine.startswith("#### "):
                # Section Headings
                # =================
                # Section headings in novel docs are treated as centred
                # separators if the formatting does not change the text. If the
                # format is empty, the section can be hidden or a blank
                # paragraph (skip). For notes, the heading is unchanged.

                nHead += 1
                tText = aLine[5:].strip()
                tType = BlockTyp.HEAD4
                if isNovel:
                    if self._hideSection:
                        tText = ""
                        tType = BlockTyp.EMPTY
                    else:
                        tText = self._hFormatter.apply(self._fmtSection, tText, nHead)
                        if tText == "":  # Empty Format
                            tType = BlockTyp.SKIP
                        elif tText == self._fmtSection:  # Static Format
                            tType = BlockTyp.SEP
                            tStyle |= BlockFmt.CENTRE

                tBlocks.append((
                    tType, f"{tHandle}:T{nHead:04d}", tText, [], tStyle
                ))

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
                if bLine.startswith(">>"):
                    alnRight = True
                    bLine = bLine[2:].lstrip(" ")
                elif bLine.startswith(">"):
                    indLeft = True
                    bLine = bLine[1:].lstrip(" ")

                if bLine.endswith("<<"):
                    alnLeft = True
                    bLine = bLine[:-2].rstrip(" ")
                elif bLine.endswith("<"):
                    indRight = True
                    bLine = bLine[:-1].rstrip(" ")

                if alnLeft and alnRight:
                    tStyle |= BlockFmt.CENTRE
                elif alnLeft:
                    tStyle |= BlockFmt.LEFT
                elif alnRight:
                    tStyle |= BlockFmt.RIGHT

                if indLeft:
                    tStyle |= BlockFmt.IND_L
                if indRight:
                    tStyle |= BlockFmt.IND_R

                # Process formats
                tLine, tFmt = self._extractFormats(bLine, hDialog=isNovel)
                tBlocks.append((
                    BlockTyp.TEXT, "", tLine, tFmt, tStyle
                ))

        # If we have content, turn off the first page flag
        if self._isFirst and len(tBlocks) > 1:
            self._isFirst = False  # First document has been processed

            # Make sure the blocks array doesn't start with a page break
            # on the very first block, adding a blank first page.
            for n, cBlock in enumerate(tBlocks):
                if cBlock[0] != BlockTyp.EMPTY:
                    if cBlock[4] & BlockFmt.PBB:
                        tBlocks[n] = (
                            cBlock[0], cBlock[1], cBlock[2], cBlock[3], cBlock[4] & ~BlockFmt.PBB
                        )
                    break

        # Always add an empty line at the end of the file
        tBlocks.append(B_EMPTY)

        # Second Pass
        # ===========
        # This second pass strips away consecutive blank lines, and
        # combines consecutive text lines into the same paragraph.
        # It also ensures that there isn't paragraph spacing between
        # meta data lines for formats that have spacing.

        lineSep = "\n" if keepBreaks else " "

        pLines: list[T_Block] = []
        sBlocks: list[T_Block] = []
        for n, cBlock in enumerate(tBlocks[1:-1], 1):

            pBlock = tBlocks[n-1]  # Look behind
            nBlock = tBlocks[n+1]  # Look ahead

            if cBlock[0] in SKIP_INDENT and not indentFirst:
                # Unless the indentFirst flag is set, we set up the next
                # paragraph to not be indented if we see a block of a
                # specific type
                self._noIndent = True

            if cBlock[0] == BlockTyp.EMPTY:
                # We don't need to keep the empty lines after this pass
                pass

            elif cBlock[0] == BlockTyp.KEYWORD:
                # Adjust margins for lines in a list of keyword lines
                aStyle = cBlock[4]
                if pBlock[0] == BlockTyp.KEYWORD:
                    aStyle |= BlockFmt.Z_TOP
                if nBlock[0] == BlockTyp.KEYWORD:
                    aStyle |= BlockFmt.Z_BTM
                sBlocks.append((
                    cBlock[0], cBlock[1], cBlock[2], cBlock[3], aStyle
                ))

            elif cBlock[0] == BlockTyp.TEXT:
                # Combine lines from the same paragraph
                pLines.append(cBlock)

                if nBlock[0] != BlockTyp.TEXT:
                    # Next block is not text, so we add the buffer to blocks
                    nLines = len(pLines)
                    cStyle = pLines[0][4]
                    if firstIndent and not (self._noIndent or cStyle & BlockFmt.ALIGNED):
                        # If paragraph indentation is enabled, not temporarily
                        # turned off, and the block is not aligned, we add the
                        # text indentation flag
                        cStyle |= BlockFmt.IND_T

                    if nLines == 1:
                        # The paragraph contains a single line, so we just save
                        # that directly to the blocks list. If justify is
                        # enabled, and there is no alignment, we apply it.
                        if doJustify and not cStyle & BlockFmt.ALIGNED:
                            cStyle |= BlockFmt.JUSTIFY

                        pTxt = pLines[0][2].translate(transMapB)
                        sBlocks.append((
                            BlockTyp.TEXT, pLines[0][1], pTxt, pLines[0][3], cStyle
                        ))

                    elif nLines > 1:
                        # The paragraph contains multiple lines, so we need to
                        # join them according to the line break policy, and
                        # recompute all the formatting markers
                        tTxt = ""
                        tFmt: T_Formats = []
                        for aBlock in pLines:
                            tLen = len(tTxt)
                            tTxt += f"{aBlock[2]}{lineSep}"
                            tFmt.extend((p+tLen, fmt, key) for p, fmt, key in aBlock[3])
                            cStyle |= aBlock[4]

                        pTxt = tTxt[:-1].translate(transMapB)
                        sBlocks.append((
                            BlockTyp.TEXT, pLines[0][1], pTxt, tFmt, cStyle
                        ))

                    # Reset buffer and make sure text indent is on for next pass
                    pLines = []
                    self._noIndent = False

            else:
                sBlocks.append(cBlock)

        self._blocks = sBlocks

        return

    def buildOutline(self) -> None:
        """Build an outline of the text up to level 3 headings."""
        isNovel = self._isNovel
        for tType, tKey, tText, _, _ in self._blocks:
            if tType == BlockTyp.TITLE:
                prefix = "TT"
            elif tType == BlockTyp.HEAD1:
                prefix = "PT" if isNovel else "H1"
            elif tType == BlockTyp.HEAD2:
                prefix = "CH" if isNovel else "H2"
            elif tType == BlockTyp.HEAD3:
                prefix = "SC" if isNovel else "H3"
            else:
                continue

            text = tText.replace(nwHeadFmt.BR, " ").replace("&amp;", "&")
            self._outline[tKey] = f"{prefix}|{text}"

        return

    def countStats(self) -> None:
        """Count stats on the tokenized text."""
        titleCount = self._counts.get(nwStats.TITLES, 0)
        paragraphCount = self._counts.get(nwStats.PARAGRAPHS, 0)

        allWords = self._counts.get(nwStats.WORDS_ALL, 0)
        textWords = self._counts.get(nwStats.WORDS_TEXT, 0)
        titleWords = self._counts.get(nwStats.WORDS_TITLE, 0)

        allChars = self._counts.get(nwStats.CHARS_ALL, 0)
        textChars = self._counts.get(nwStats.CHARS_TEXT, 0)
        titleChars = self._counts.get(nwStats.CHARS_TITLE, 0)

        allWordChars = self._counts.get(nwStats.WCHARS_ALL, 0)
        textWordChars = self._counts.get(nwStats.WCHARS_TEXT, 0)
        titleWordChars = self._counts.get(nwStats.WCHARS_TITLE, 0)

        for tType, _, tText, _, _ in self._blocks:
            tText = tText.replace(nwUnicode.U_ENDASH, " ")
            tText = tText.replace(nwUnicode.U_EMDASH, " ")

            tWords = tText.split()
            nWords = len(tWords)
            nChars = len(tText)
            nWChars = len("".join(tWords))

            if tType == BlockTyp.TEXT:
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

            elif tType in HEADINGS:
                titleCount += 1
                allWords += nWords
                titleWords += nWords
                allChars += nChars
                allWordChars += nWChars
                titleChars += nChars
                titleWordChars += nWChars

            elif tType == BlockTyp.SEP:
                allWords += nWords
                allChars += nChars
                allWordChars += nWChars

            elif tType in (BlockTyp.COMMENT, BlockTyp.KEYWORD):
                words = tText.split()
                allWords += len(words)
                allChars += len(tText)
                allWordChars += len("".join(words))

        self._counts[nwStats.TITLES] = titleCount
        self._counts[nwStats.PARAGRAPHS] = paragraphCount

        self._counts[nwStats.WORDS_ALL] = allWords
        self._counts[nwStats.WORDS_TEXT] = textWords
        self._counts[nwStats.WORDS_TITLE] = titleWords

        self._counts[nwStats.CHARS_ALL] = allChars
        self._counts[nwStats.CHARS_TEXT] = textChars
        self._counts[nwStats.CHARS_TITLE] = titleChars

        self._counts[nwStats.WCHARS_ALL] = allWordChars
        self._counts[nwStats.WCHARS_TEXT] = textWordChars
        self._counts[nwStats.WCHARS_TITLE] = titleWordChars

        return

    ##
    #  Internal Functions
    ##

    def _formatInt(self, value: int) -> str:
        """Return a localised integer."""
        return self._dLocale.toString(value)

    def _formatComment(self, style: ComStyle, key: str, text: str) -> tuple[str, T_Formats]:
        """Apply formatting to comments and notes."""
        tTxt, tFmt = self._extractFormats(text)
        tFmt.insert(0, (0, TextFmt.COL_B, style.textClass))
        tFmt.append((len(tTxt), TextFmt.COL_E, ""))
        if label := (self._localLookup(style.label) + (f" ({key})" if key else "")).strip():
            shift = len(label) + 2
            tTxt = f"{label}: {tTxt}"
            rFmt = [(0, TextFmt.B_B, ""), (shift - 1, TextFmt.B_E, "")]
            if style.labelClass:
                rFmt.insert(1, (0, TextFmt.COL_B, style.labelClass))
                rFmt.insert(2, (shift - 1, TextFmt.COL_E, ""))
            rFmt.extend((p + shift, f, d) for p, f, d in tFmt)
        return tTxt, rFmt

    def _formatMeta(self, text: str) -> tuple[str, str, T_Formats]:
        """Apply formatting to a meta data line."""
        tag = ""
        txt = []
        fmt = []
        valid, bits, _ = self._project.index.scanThis(text)
        if valid and bits and bits[0] in nwLabels.KEY_NAME and bits[0] not in self._skipKeywords:
            tag = bits[0]
            pos = 0
            lbl = f"{self._localLookup(nwLabels.KEY_NAME[tag])}:"
            end = len(lbl)
            fmt = [
                (pos, TextFmt.B_B, ""),
                (pos, TextFmt.COL_B, "keyword"),
                (end, TextFmt.COL_E, ""),
                (end, TextFmt.B_E, ""),
            ]
            txt = [lbl, " "]
            pos = end + 1

            if (num := len(bits)) > 1:
                if bits[0] == nwKeyWords.TAG_KEY:
                    one, two = self._project.index.parseValue(bits[1])
                    end = pos + len(one)
                    fmt.append((pos, TextFmt.COL_B, "tag"))
                    fmt.append((pos, TextFmt.ANM_B, f"tag_{one}".lower()))
                    fmt.append((end, TextFmt.ANM_E, ""))
                    fmt.append((end, TextFmt.COL_E, ""))
                    txt.append(one)
                    pos = end
                    if two:
                        txt.append(" | ")
                        pos += 3
                        end = pos + len(two)
                        fmt.append((pos, TextFmt.COL_B, "optional"))
                        fmt.append((end, TextFmt.COL_E, ""))
                        txt.append(two)
                        pos = end
                else:
                    for n, bit in enumerate(bits[1:], 2):
                        end = pos + len(bit)
                        fmt.append((pos, TextFmt.COL_B, "tag"))
                        fmt.append((pos, TextFmt.ARF_B, f"#tag_{bit}".lower()))
                        fmt.append((end, TextFmt.ARF_E, ""))
                        fmt.append((end, TextFmt.COL_E, ""))
                        txt.append(bit)
                        pos = end
                        if n < num:
                            txt.append(", ")
                            pos += 2

        return tag, "".join(txt), fmt

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
            for res in regEx.finditer(text):
                temp.extend(
                    (res.start(n), res.end(n), fmt, "")
                    for n, fmt in enumerate(fmts) if fmt > 0
                )

        # Match URLs
        for res in REGEX_PATTERNS.url.finditer(text):
            temp.append((res.start(0), 0, TextFmt.HRF_B, res.group(0)))
            temp.append((res.end(0), 0, TextFmt.HRF_E, ""))

        # Match Shortcodes
        for res in REGEX_PATTERNS.shortcodePlain.finditer(text):
            temp.append((
                res.start(1), res.end(1),
                self._shortCodeFmt.get(res.group(1).lower(), 0),
                "",
            ))

        # Match Shortcode w/Values
        tHandle = self._handle or ""
        for res in REGEX_PATTERNS.shortcodeValue.finditer(text):
            kind = self._shortCodeVals.get(res.group(1).lower(), 0)
            temp.append((
                res.start(0), res.end(0),
                TextFmt.STRIP if kind == skip else kind,
                f"{tHandle}:{res.group(2)}",
            ))

        # Match Dialogue
        if self._hlightDialog and hDialog:
            if self._dialogParser.enabled:
                for pos, end in self._dialogParser(text):
                    temp.append((pos, 0, TextFmt.COL_B, "dialog"))
                    temp.append((end, 0, TextFmt.COL_E, ""))
            if self._rxAltDialog:
                for res in self._rxAltDialog.finditer(text):
                    temp.append((res.start(0), 0, TextFmt.COL_B, "altdialog"))
                    temp.append((res.end(0), 0, TextFmt.COL_E, ""))

        # Post-process text and format
        result = text
        formats = []
        for pos, end, fmt, meta in reversed(sorted(temp, key=lambda x: x[0])):
            if fmt > 0:
                if end > pos:
                    result = result[:pos] + result[end:]
                    formats = [(p+pos-end if p > pos else p, f, m) for p, f, m in formats]
                formats.insert(0, (pos, fmt, meta))

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
        hFormat = hFormat.replace(nwHeadFmt.BR, "\n")
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
