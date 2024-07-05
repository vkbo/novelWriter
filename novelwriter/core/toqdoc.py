"""
novelWriter – QTextDocument Converter
=====================================

File History:
Created: 2024-05-21 [2.5b1] ToQTextDocument

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
    QColor, QFont, QFontMetricsF, QTextBlockFormat, QTextCharFormat,
    QTextCursor, QTextDocument
)

from novelwriter.constants import nwHeaders, nwHeadFmt, nwKeyWords, nwLabels, nwUnicode
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import T_Formats, Tokenizer
from novelwriter.types import (
    QtAlignAbsolute, QtAlignCenter, QtAlignJustify, QtAlignLeft, QtAlignRight,
    QtBlack, QtPageBreakAfter, QtPageBreakBefore, QtTransparent,
    QtVAlignNormal, QtVAlignSub, QtVAlignSuper
)

logger = logging.getLogger(__name__)

T_TextStyle = tuple[QTextBlockFormat, QTextCharFormat]


class TextDocumentTheme:
    text:      QColor = QtBlack
    highlight: QColor = QtTransparent
    head:      QColor = QtBlack
    comment:   QColor = QtBlack
    note:      QColor = QtBlack
    code:      QColor = QtBlack
    modifier:  QColor = QtBlack
    keyword:   QColor = QtBlack
    tag:       QColor = QtBlack
    optional:  QColor = QtBlack
    dialog:    QColor = QtBlack
    altdialog: QColor = QtBlack


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
        self._document.setDocumentMargin(0)

        self._theme = TextDocumentTheme()
        self._styles: dict[int, T_TextStyle] = {}
        self._usedNotes: dict[str, int] = {}

        self._init = False
        self._bold = QFont.Weight.Bold
        self._normal = QFont.Weight.Normal

        return

    def initDocument(self, font: QFont, theme: TextDocumentTheme) -> None:
        """Initialise all computed values of the document."""
        self._textFont = font
        self._theme = theme

        self._document.setUndoRedoEnabled(False)
        self._document.blockSignals(True)
        self._document.clear()
        self._document.setDefaultFont(self._textFont)

        qMetric = QFontMetricsF(self._textFont)
        mPx = qMetric.ascent()  # 1 em in pixels
        fPt = self._textFont.pointSizeF()

        # Scaled Sizes
        # ============

        self._mHead = {
            self.T_TITLE: (mPx * self._marginTitle[0], mPx * self._marginTitle[1]),
            self.T_HEAD1: (mPx * self._marginHead1[0], mPx * self._marginHead1[1]),
            self.T_HEAD2: (mPx * self._marginHead2[0], mPx * self._marginHead2[1]),
            self.T_HEAD3: (mPx * self._marginHead3[0], mPx * self._marginHead3[1]),
            self.T_HEAD4: (mPx * self._marginHead4[0], mPx * self._marginHead4[1]),
        }

        self._sHead = {
            self.T_TITLE: nwHeaders.H_SIZES.get(0, 1.0) * fPt,
            self.T_HEAD1: nwHeaders.H_SIZES.get(1, 1.0) * fPt,
            self.T_HEAD2: nwHeaders.H_SIZES.get(2, 1.0) * fPt,
            self.T_HEAD3: nwHeaders.H_SIZES.get(3, 1.0) * fPt,
            self.T_HEAD4: nwHeaders.H_SIZES.get(4, 1.0) * fPt,
        }

        self._mText = (mPx * self._marginText[0], mPx * self._marginText[1])
        self._mMeta = (mPx * self._marginMeta[0], mPx * self._marginMeta[1])
        self._mSep  = (mPx * self._marginSep[0], mPx * self._marginSep[1])

        self._mIndent = mPx * 2.0
        self._tIndent = mPx * self._firstWidth

        # Block Format
        # ============

        self._blockFmt = QTextBlockFormat()
        self._blockFmt.setTopMargin(self._mText[0])
        self._blockFmt.setBottomMargin(self._mText[1])
        self._blockFmt.setAlignment(QtAlignJustify if self._doJustify else QtAlignAbsolute)
        self._blockFmt.setLineHeight(
            100*self._lineHeight, QTextBlockFormat.LineHeightTypes.ProportionalHeight
        )

        # Character Formats
        # =================

        self._cText = QTextCharFormat()
        self._cText.setBackground(QtTransparent)
        self._cText.setForeground(self._theme.text)

        self._cHead = QTextCharFormat(self._cText)
        self._cHead.setForeground(self._theme.head)

        self._cComment = QTextCharFormat(self._cText)
        self._cComment.setForeground(self._theme.comment)

        self._cCommentMod = QTextCharFormat(self._cText)
        self._cCommentMod.setForeground(self._theme.comment)
        self._cCommentMod.setFontWeight(self._bold)

        self._cNote = QTextCharFormat(self._cText)
        self._cNote.setForeground(self._theme.note)

        self._cCode = QTextCharFormat(self._cText)
        self._cCode.setForeground(self._theme.code)

        self._cModifier = QTextCharFormat(self._cText)
        self._cModifier.setForeground(self._theme.modifier)
        self._cModifier.setFontWeight(self._bold)

        self._cKeyword = QTextCharFormat(self._cText)
        self._cKeyword.setForeground(self._theme.keyword)

        self._cTag = QTextCharFormat(self._cText)
        self._cTag.setForeground(self._theme.tag)

        self._cOptional = QTextCharFormat(self._cText)
        self._cOptional.setForeground(self._theme.optional)

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
        cursor.movePosition(QTextCursor.MoveOperation.End)

        for tType, nHead, tText, tFormat, tStyle in self._tokens:

            # Styles
            bFmt = QTextBlockFormat(self._blockFmt)
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
                if tStyle & self.A_IND_T:
                    bFmt.setTextIndent(self._tIndent)

            if tType == self.T_TEXT:
                newBlock(cursor, bFmt)
                self._insertFragments(tText, tFormat, cursor, self._cText)

            elif tType in self.L_HEADINGS:
                bFmt, cFmt = self._genHeadStyle(tType, nHead, bFmt)
                newBlock(cursor, bFmt)
                cursor.insertText(tText.replace(nwHeadFmt.BR, "\n"), cFmt)

            elif tType == self.T_SEP:
                sFmt = QTextBlockFormat(bFmt)
                sFmt.setTopMargin(self._mSep[0])
                sFmt.setBottomMargin(self._mSep[1])
                newBlock(cursor, sFmt)
                cursor.insertText(tText, self._cText)

            elif tType == self.T_SKIP:
                newBlock(cursor, bFmt)
                cursor.insertText(nwUnicode.U_NBSP, self._cText)

            elif tType in self.L_SUMMARY and self._doSynopsis:
                newBlock(cursor, bFmt)
                modifier = self._localLookup(
                    "Short Description" if tType == self.T_SHORT else "Synopsis"
                )
                cursor.insertText(f"{modifier}: ", self._cModifier)
                self._insertFragments(tText, tFormat, cursor, self._cNote)

            elif tType == self.T_COMMENT and self._doComments:
                newBlock(cursor, bFmt)
                modifier = self._localLookup("Comment")
                cursor.insertText(f"{modifier}: ", self._cCommentMod)
                self._insertFragments(tText, tFormat, cursor, self._cComment)

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

            bFmt, cFmt = self._genHeadStyle(self.T_HEAD4, -1, self._blockFmt)
            newBlock(cursor, bFmt)
            cursor.insertText(self._localLookup("Footnotes"), cFmt)

            for key, index in self._usedNotes.items():
                if content := self._footnotes.get(key):
                    cFmt = QTextCharFormat(self._cCode)
                    cFmt.setAnchor(True)
                    cFmt.setAnchorNames([f"footnote_{index}"])
                    newBlock(cursor, self._blockFmt)
                    cursor.insertText(f"{index}. ", cFmt)
                    self._insertFragments(*content, cursor, self._cText)

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
                cFmt.setBackground(self._theme.highlight)
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
            elif fmt == self.FMT_DL_B:
                cFmt.setForeground(self._theme.dialog)
            elif fmt == self.FMT_DL_E:
                cFmt.setForeground(self._theme.text)
            elif fmt == self.FMT_ADL_B:
                cFmt.setForeground(self._theme.altdialog)
            elif fmt == self.FMT_ADL_E:
                cFmt.setForeground(self._theme.text)
            elif fmt == self.FMT_FNOTE:
                xFmt = QTextCharFormat(self._cCode)
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
            cursor.insertText(key, self._cKeyword)
            if (num := len(bits)) > 1:
                if bits[0] == nwKeyWords.TAG_KEY:
                    one, two = self._project.index.parseValue(bits[1])
                    cFmt = QTextCharFormat(self._cTag)
                    cFmt.setAnchor(True)
                    cFmt.setAnchorNames([f"tag_{one}".lower()])
                    cursor.insertText(one, cFmt)
                    if two:
                        cursor.insertText(" | ", self._cText)
                        cursor.insertText(two, self._cOptional)
                else:
                    for n, bit in enumerate(bits[1:], 2):
                        cFmt = QTextCharFormat(self._cTag)
                        cFmt.setFontUnderline(True)
                        cFmt.setAnchor(True)
                        cFmt.setAnchorHref(f"#tag_{bit}".lower())
                        cursor.insertText(bit, cFmt)
                        if n < num:
                            cursor.insertText(", ", self._cText)
        return

    def _genHeadStyle(self, hType: int, nHead: int, rFmt: QTextBlockFormat) -> T_TextStyle:
        """Generate a heading style set."""
        mTop, mBottom = self._mHead.get(hType, (0.0, 0.0))

        bFmt = QTextBlockFormat(rFmt)
        bFmt.setTopMargin(mTop)
        bFmt.setBottomMargin(mBottom)

        cFmt = QTextCharFormat(self._cText if hType == self.T_TITLE else self._cHead)
        cFmt.setFontWeight(self._bold)
        cFmt.setFontPointSize(self._sHead.get(hType, 1.0))
        if nHead >= 0:
            cFmt.setAnchorNames([f"{self._handle}:T{nHead:04d}"])
            cFmt.setAnchor(True)

        return bFmt, cFmt
