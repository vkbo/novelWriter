"""
novelWriter – Markdown Text Converter
=====================================

File History:
Created: 2021-02-06 [1.2b1] ToMarkdown

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

import logging

from PyQt5.QtGui import (
    QColor, QFont, QFontMetrics, QTextBlockFormat, QTextCharFormat,
    QTextCursor, QTextDocument
)

from novelwriter import SHARED
from novelwriter.constants import nwHeaders
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import T_Formats, Tokenizer
from novelwriter.types import (
    QtAlignCenter, QtAlignJustify, QtAlignLeft, QtAlignRight, QtPageBreakAfter,
    QtPageBreakBefore, QtTransparent, QtVAlignNormal, QtVAlignSub,
    QtVAlignSuper
)

logger = logging.getLogger(__name__)

T_TextStyle = tuple[QTextBlockFormat, QTextCharFormat]


class ToQTextDocument(Tokenizer):
    """Core: QTextDocument Writer

    Extend the Tokenizer class to generate a QTextDocument output. This
    is intended for usage in the document viewer and build tool preview.
    """

    def __init__(self, project: NWProject) -> None:
        super().__init__(project)
        self._document = QTextDocument()
        self._document.setUndoRedoEnabled(False)

        self._styles: dict[int, T_TextStyle] = {}
        self._usedNotes: dict[str, int] = {}

        self._init = False
        self._bold = QFont.Weight.Bold
        self._normal = QFont.Weight.Normal

        return

    def initDocument(self) -> None:
        """Initialise all computed values of the document."""
        self._document.setUndoRedoEnabled(False)
        self._document.blockSignals(True)
        self._document.clear()
        self._document.setDefaultFont(self._textFont)

        qMetric = QFontMetrics(self._textFont)
        mScale = qMetric.height()
        fPt = self._textFont.pointSizeF()

        self._mHead = {
            self.T_TITLE: (mScale * self._marginTitle[0], mScale * self._marginTitle[1]),
            self.T_HEAD1: (mScale * self._marginHead1[0], mScale * self._marginHead1[1]),
            self.T_HEAD2: (mScale * self._marginHead2[0], mScale * self._marginHead2[1]),
            self.T_HEAD3: (mScale * self._marginHead3[0], mScale * self._marginHead3[1]),
            self.T_HEAD4: (mScale * self._marginHead4[0], mScale * self._marginHead4[1]),
        }

        self._sHead = {
            self.T_TITLE: nwHeaders.H_SIZES.get(1, 1.0) * fPt,
            self.T_HEAD1: nwHeaders.H_SIZES.get(1, 1.0) * fPt,
            self.T_HEAD2: nwHeaders.H_SIZES.get(2, 1.0) * fPt,
            self.T_HEAD3: nwHeaders.H_SIZES.get(3, 1.0) * fPt,
            self.T_HEAD4: nwHeaders.H_SIZES.get(4, 1.0) * fPt,
        }

        self._mText = (mScale * self._marginText[0], mScale * self._marginText[1])
        self._mMeta = (mScale * self._marginMeta[0], mScale * self._marginMeta[1])

        self._defaultChar = QTextCharFormat()
        self._defaultChar.setForeground(SHARED.theme.colText)

        self._defaultBlock = QTextBlockFormat()
        self._defaultBlock.setTopMargin(self._mText[0])
        self._defaultBlock.setBottomMargin(self._mText[1])

        self._init = True

        return

    ##
    #  Properties
    ##

    @property
    def document(self) -> QTextDocument:
        """Return the document."""
        return self._document

    ##
    #  Class Methods
    ##

    def clearDocument(self) -> None:
        """Clear the document so the class can be reused."""
        self._document.clear()
        return

    def doConvert(self) -> None:
        """Write text tokens into the document."""
        if not self._init:
            return

        self._document.blockSignals(True)
        cursor = QTextCursor(self._document)

        def newBlock(bFmt: QTextBlockFormat) -> None:
            if cursor.position() > 0:
                cursor.insertBlock(bFmt)
            else:
                cursor.setBlockFormat(bFmt)

        for tType, _, tText, tFormat, tStyle in self._tokens:

            # Styles
            bFmt = QTextBlockFormat(self._defaultBlock)
            if tStyle is not None:
                if tStyle & self.A_LEFT:
                    bFmt.setAlignment(QtAlignLeft)
                elif tStyle & self.A_RIGHT:
                    bFmt.setAlignment(QtAlignRight)
                elif tStyle & self.A_CENTRE:
                    bFmt.setAlignment(QtAlignCenter)
                elif tStyle & self.A_JUSTIFY:
                    bFmt.setAlignment(QtAlignJustify)

                if tStyle & self.A_PBB:
                    bFmt.setPageBreakPolicy(QtPageBreakBefore)
                if tStyle & self.A_PBA:
                    bFmt.setPageBreakPolicy(QtPageBreakAfter)

                if tStyle & self.A_Z_BTMMRG:
                    bFmt.setBottomMargin(0.0)
                if tStyle & self.A_Z_TOPMRG:
                    bFmt.setTopMargin(0.0)

                if tStyle & self.A_IND_L:
                    bFmt.setLeftMargin(self._blockIndent)
                if tStyle & self.A_IND_R:
                    bFmt.setRightMargin(self._blockIndent)

            if tType == self.T_TEXT:
                newBlock(bFmt)
                self._insertFragments(tText, tFormat, cursor, self._defaultChar)

            elif tType in self.L_HEADINGS:
                bFmt, cFmt = self._genHeadStyle(tType, bFmt)
                newBlock(bFmt)
                cursor.insertText(tText, cFmt)

            elif tType == self.T_SEP:
                newBlock(bFmt)
                cursor.insertText(tText, self._defaultChar)

            elif tType == self.T_SKIP:
                newBlock(bFmt)

            elif tType == self.T_SYNOPSIS and self._doSynopsis:
                pass

            elif tType == self.T_SHORT and self._doSynopsis:
                pass

            elif tType == self.T_COMMENT and self._doComments:
                pass

            elif tType == self.T_KEYWORD and self._doKeywords:
                pass

        self._document.blockSignals(False)

        return

    def appendFootnotes(self) -> None:
        """Append the footnotes in the buffer."""
        # if self._usedNotes:
        #     tags = STD_MD if self._genMode == self.M_STD else EXT_MD
        #     footnotes = self._localLookup("Footnotes")

        #     lines = []
        #     lines.append(f"### {footnotes}\n\n")
        #     for key, index in self._usedNotes.items():
        #         if content := self._footnotes.get(key):
        #             marker = f"{index}. "
        #             text = self._formatText(*content, tags)
        #             lines.append(f"{marker}{text}\n")
        #     lines.append("\n")

        #     result = "".join(lines)
        #     self._result += result
        #     self._fullMD.append(result)

        return

    ##
    #  Internal Functions
    ##

    def _insertFragments(
        self, text: str, tFmt: T_Formats, cursor: QTextCursor,
        dFmt: QTextCharFormat, bgCol: QColor = QtTransparent
    ) -> None:
        """Apply formatting tags to text."""
        cFmt = QTextCharFormat(dFmt)
        start = 0
        for pos, fmt, data in tFmt:

            # Insert buffer with previous format
            cursor.insertText(text[start:pos], cFmt)

            # Construct next format
            if fmt == self.FMT_B_B:
                cFmt.setFontWeight(self._bold)
            elif fmt == self.FMT_B_E:
                cFmt.setFontWeight(self._normal)
            elif fmt == self.FMT_I_B:
                cFmt.setFontItalic(True)
            elif fmt == self.FMT_I_E:
                cFmt.setFontItalic(False)
            elif fmt == self.FMT_D_B:
                cFmt.setFontStrikeOut(True)
            elif fmt == self.FMT_D_E:
                cFmt.setFontStrikeOut(False)
            elif fmt == self.FMT_U_B:
                cFmt.setFontUnderline(True)
            elif fmt == self.FMT_U_E:
                cFmt.setFontUnderline(False)
            elif fmt == self.FMT_M_B:
                cFmt.setBackground(SHARED.theme.colMark)
            elif fmt == self.FMT_M_E:
                cFmt.setBackground(bgCol)
            elif fmt == self.FMT_SUP_B:
                cFmt.setVerticalAlignment(QtVAlignSuper)
            elif fmt == self.FMT_SUP_E:
                cFmt.setVerticalAlignment(QtVAlignNormal)
            elif fmt == self.FMT_SUB_B:
                cFmt.setVerticalAlignment(QtVAlignSub)
            elif fmt == self.FMT_SUB_E:
                cFmt.setVerticalAlignment(QtVAlignNormal)
            elif fmt == self.FMT_FNOTE:
                cFmt.setVerticalAlignment(QtVAlignSuper)
                if data in self._footnotes:
                    index = len(self._usedNotes) + 1
                    self._usedNotes[data] = index
                    cursor.insertText(f"[{index}]", cFmt)
                else:
                    cursor.insertText("[ERR]", cFmt)
                cFmt.setVerticalAlignment(QtVAlignNormal)

            # Move pos for next pass
            start = pos

        # Insert whatever is left in the buffer
        cursor.insertText(text[start:], cFmt)

        return

    def _formatKeywords(self, text: str, style: int) -> str:
        """Apply Markdown formatting to keywords."""
        # valid, bits, _ = self._project.index.scanThis("@"+text)
        # if not valid or not bits:
        #     return ""

        result = ""
        # if bits[0] in nwLabels.KEY_NAME:
        #     result += f"**{self._localLookup(nwLabels.KEY_NAME[bits[0]])}:** "
        #     if len(bits) > 1:
        #         result += ", ".join(bits[1:])

        # result += "  \n" if style & self.A_Z_BTMMRG else "\n\n"

        return result

    def _genHeadStyle(self, level: int, rFmt: QTextBlockFormat) -> T_TextStyle:
        """Generate a heading style set."""
        mTop, mBottom = self._mHead.get(level, (0.0, 0.0))

        bFmt = QTextBlockFormat(rFmt)
        bFmt.setTopMargin(mTop)
        bFmt.setBottomMargin(mBottom)

        cFmt = QTextCharFormat(self._defaultChar)
        cFmt.setForeground(SHARED.theme.colHead)
        cFmt.setFontWeight(QFont.Weight.Bold)
        cFmt.setFontPointSize(self._sHead.get(level, 1.0))

        return bFmt, cFmt
