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
    QFont, QFontMetrics, QTextBlockFormat, QTextCharFormat, QTextCursor,
    QTextDocument
)

from novelwriter import SHARED
from novelwriter.constants import nwHeaders, nwHeadFmt, nwKeyWords, nwLabels, nwUnicode
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import T_Formats, Tokenizer
from novelwriter.types import (
    QtAlignCenter, QtAlignJustify, QtAlignLeft, QtAlignRight, QtPageBreakAfter,
    QtPageBreakBefore, QtTransparent, QtVAlignNormal, QtVAlignSub,
    QtVAlignSuper
)

logger = logging.getLogger(__name__)

T_TextStyle = tuple[QTextBlockFormat, QTextCharFormat]


def newBlock(cursor: QTextCursor, bFmt: QTextBlockFormat) -> None:
    if cursor.position() > 0:
        cursor.insertBlock(bFmt)
    else:
        cursor.setBlockFormat(bFmt)


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

    def initDocument(self, font: QFont) -> None:
        """Initialise all computed values of the document."""
        self._textFont = font

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

        self._mIndent = mScale * 2.0

        self._defaultChar = QTextCharFormat()
        self._defaultChar.setForeground(SHARED.theme.colText)

        self._comChar = QTextCharFormat()
        self._comChar.setForeground(SHARED.theme.colHidden)

        self._noteChar = QTextCharFormat()
        self._noteChar.setForeground(SHARED.theme.colNote)

        self._codeChar = QTextCharFormat()
        self._codeChar.setForeground(SHARED.theme.colCode)

        self._modChar = QTextCharFormat()
        self._modChar.setForeground(SHARED.theme.colMod)

        self._keyChar = QTextCharFormat()
        self._keyChar.setForeground(SHARED.theme.colKey)

        self._tagChar = QTextCharFormat()
        self._tagChar.setForeground(SHARED.theme.colTag)

        self._optChar = QTextCharFormat()
        self._optChar.setForeground(SHARED.theme.colOpt)

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

    def doConvert(self) -> None:
        """Write text tokens into the document."""
        if not self._init:
            return

        self._document.blockSignals(True)
        cursor = QTextCursor(self._document)

        for tType, nHead, tText, tFormat, tStyle in self._tokens:

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
                    bFmt.setLeftMargin(self._mIndent)
                if tStyle & self.A_IND_R:
                    bFmt.setRightMargin(self._mIndent)

            if tType == self.T_TEXT:
                newBlock(cursor, bFmt)
                self._insertFragments(tText, tFormat, cursor, self._defaultChar)

            elif tType in self.L_HEADINGS:
                bFmt, cFmt = self._genHeadStyle(tType, nHead, bFmt)
                newBlock(cursor, bFmt)
                cursor.insertText(tText.replace(nwHeadFmt.BR, "\n"), cFmt)

            elif tType == self.T_SEP:
                newBlock(cursor, bFmt)
                cursor.insertText(tText, self._defaultChar)

            elif tType == self.T_SKIP:
                newBlock(cursor, bFmt)
                cursor.insertText(nwUnicode.U_NBSP, self._defaultChar)

            elif tType in self.L_SUMMARY and self._doSynopsis:
                newBlock(cursor, bFmt)
                prefix = self._localLookup(
                    "Short Description" if tType == self.T_SHORT else "Synopsis"
                )
                cursor.insertText(f"{prefix}: ", self._modChar)
                self._insertFragments(tText, tFormat, cursor, self._noteChar)

            elif tType == self.T_COMMENT and self._doComments:
                newBlock(cursor, bFmt)
                self._insertFragments(tText, tFormat, cursor, self._comChar)

            elif tType == self.T_KEYWORD and self._doKeywords:
                newBlock(cursor, bFmt)
                self._insertKeywords(tText, cursor)

        self._document.blockSignals(False)

        return

    def appendFootnotes(self) -> None:
        """Append the footnotes in the buffer."""
        if self._usedNotes:
            self._document.blockSignals(True)

            cursor = QTextCursor(self._document)
            cursor.movePosition(QTextCursor.MoveOperation.End)

            bFmt, cFmt = self._genHeadStyle(self.T_HEAD3, -1, self._defaultBlock)
            newBlock(cursor, bFmt)
            cursor.insertText(self._localLookup("Footnotes"), cFmt)

            for key, index in self._usedNotes.items():
                if content := self._footnotes.get(key):
                    cFmt = QTextCharFormat(self._codeChar)
                    cFmt.setAnchor(True)
                    cFmt.setAnchorNames([f"footnote_{index}"])
                    newBlock(cursor, self._defaultBlock)
                    cursor.insertText(f"{index}. ", cFmt)
                    self._insertFragments(*content, cursor, self._defaultChar)

            self._document.blockSignals(False)

        return

    ##
    #  Internal Functions
    ##

    def _insertFragments(
        self, text: str, tFmt: T_Formats, cursor: QTextCursor, dFmt: QTextCharFormat
    ) -> None:
        """Apply formatting tags to text."""
        cFmt = QTextCharFormat(dFmt)
        start = 0
        temp = text.replace("\n", nwUnicode.U_LSEP)
        for pos, fmt, data in tFmt:

            # Insert buffer with previous format
            cursor.insertText(temp[start:pos], cFmt)

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
                cFmt.setBackground(QtTransparent)
            elif fmt == self.FMT_SUP_B:
                cFmt.setVerticalAlignment(QtVAlignSuper)
            elif fmt == self.FMT_SUP_E:
                cFmt.setVerticalAlignment(QtVAlignNormal)
            elif fmt == self.FMT_SUB_B:
                cFmt.setVerticalAlignment(QtVAlignSub)
            elif fmt == self.FMT_SUB_E:
                cFmt.setVerticalAlignment(QtVAlignNormal)
            elif fmt == self.FMT_FNOTE:
                xFmt = QTextCharFormat(self._codeChar)
                xFmt.setVerticalAlignment(QtVAlignSuper)
                if data in self._footnotes:
                    index = len(self._usedNotes) + 1
                    self._usedNotes[data] = index
                    xFmt.setAnchor(True)
                    xFmt.setAnchorHref(f"#footnote_{index}")
                    xFmt.setFontUnderline(True)
                    cursor.insertText(f"[{index}]", xFmt)
                else:
                    cursor.insertText("[ERR]", cFmt)

            # Move pos for next pass
            start = pos

        # Insert whatever is left in the buffer
        cursor.insertText(temp[start:], cFmt)

        return

    def _insertKeywords(self, text: str, cursor: QTextCursor) -> None:
        """Apply Markdown formatting to keywords."""
        valid, bits, _ = self._project.index.scanThis("@"+text)
        if valid and bits:
            key = f"{self._localLookup(nwLabels.KEY_NAME[bits[0]])}: "
            cursor.insertText(key, self._keyChar)
            if (num := len(bits)) > 1:
                if bits[0] == nwKeyWords.TAG_KEY:
                    one, two = self._project.index.parseValue(bits[1])
                    cursor.insertText(one, self._tagChar)
                    if two:
                        cursor.insertText(" | ", self._defaultChar)
                        cursor.insertText(two, self._optChar)
                else:
                    for n, bit in enumerate(bits[1:], 2):
                        cFmt = QTextCharFormat(self._tagChar)
                        cFmt.setFontUnderline(True)
                        cFmt.setAnchor(True)
                        cFmt.setAnchorHref(f"#{bits[0][1:]}={bit}")
                        cursor.insertText(bit, cFmt)
                        if n < num:
                            cursor.insertText(", ", self._defaultChar)
        return

    def _genHeadStyle(self, level: int, nHead: int, rFmt: QTextBlockFormat) -> T_TextStyle:
        """Generate a heading style set."""
        mTop, mBottom = self._mHead.get(level, (0.0, 0.0))

        bFmt = QTextBlockFormat(rFmt)
        bFmt.setTopMargin(mTop)
        bFmt.setBottomMargin(mBottom)

        cFmt = QTextCharFormat(self._defaultChar)
        cFmt.setForeground(SHARED.theme.colHead)
        cFmt.setFontWeight(QFont.Weight.Bold)
        cFmt.setFontPointSize(self._sHead.get(level, 1.0))
        if nHead >= 0:
            cFmt.setAnchorNames([f"{self._handle}:T{nHead:04d}"])
            cFmt.setAnchor(True)

        return bFmt, cFmt
