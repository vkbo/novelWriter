"""
novelWriter – ToQTextDocument Class Tester
==========================================

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

import pytest

from PyQt5.QtGui import QColor, QTextBlock, QTextCharFormat, QTextCursor

from novelwriter import CONFIG
from novelwriter.constants import nwUnicode
from novelwriter.core.project import NWProject
from novelwriter.formats.toqdoc import TextDocumentTheme, ToQTextDocument
from novelwriter.types import (
    QtAlignAbsolute, QtAlignCenter, QtAlignJustify, QtAlignLeft, QtAlignRight,
    QtPageBreakAfter, QtTransparent, QtVAlignNormal, QtVAlignSub, QtVAlignSuper
)

THEME = TextDocumentTheme()
THEME.text      = QColor(0, 0, 0)
THEME.highlight = QColor(255, 255, 166)
THEME.head      = QColor(66, 113, 174)
THEME.comment   = QColor(100, 100, 100)
THEME.note      = QColor(129, 55, 9)
THEME.code      = QColor(66, 113, 174)
THEME.modifier  = QColor(129, 55, 9)
THEME.keyword   = QColor(245, 135, 31)
THEME.tag       = QColor(66, 113, 174)
THEME.optional  = QColor(66, 113, 174)
THEME.dialog    = QColor(113, 140, 0)
THEME.altdialog = QColor(234, 183, 0)


def charFmtInBlock(block: QTextBlock, pos: int) -> QTextCharFormat:
    """Get the character format at a given place in a block."""
    cursor = QTextCursor(block)
    cursor.setPosition(block.position() + pos)
    return cursor.charFormat()


@pytest.mark.core
def testFmtToQTextDocument_ConvertHeaders(mockGUI):
    """Test header formats in the ToQTextDocument class."""
    project = NWProject()
    qdoc = ToQTextDocument(project)
    qdoc.initDocument(CONFIG.textFont, THEME)
    qdoc.saveDocument("")  # Doesn't do anything for this format

    qdoc._isNovel = True
    qdoc._isFirst = True
    qdoc._text = (
        "#! Title\n"
        "# Partition\n"
        "## Chapter\n"
        "### Scene\n"
        "#### Section\n"
    )
    qdoc.tokenizeText()
    qdoc.doConvert()
    assert qdoc.document.blockCount() == 5

    # Title
    block = qdoc.document.findBlockByNumber(0)
    assert block.text() == "Title"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mHead[qdoc.T_TITLE][0]
    assert bFmt.bottomMargin() == qdoc._mHead[qdoc.T_TITLE][1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.fontWeight() == qdoc._bold
    assert cFmt.fontPointSize() == qdoc._sHead[qdoc.T_TITLE]
    assert cFmt.foreground().color() == THEME.text

    # Partition
    block = qdoc.document.findBlockByNumber(1)
    assert block.text() == "Partition"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mHead[qdoc.T_HEAD1][0]
    assert bFmt.bottomMargin() == qdoc._mHead[qdoc.T_HEAD1][1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.fontWeight() == qdoc._bold
    assert cFmt.fontPointSize() == qdoc._sHead[qdoc.T_HEAD1]
    assert cFmt.foreground().color() == THEME.head

    # Chapter
    block = qdoc.document.findBlockByNumber(2)
    assert block.text() == "Chapter"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mHead[qdoc.T_HEAD2][0]
    assert bFmt.bottomMargin() == qdoc._mHead[qdoc.T_HEAD2][1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.fontWeight() == qdoc._bold
    assert cFmt.fontPointSize() == qdoc._sHead[qdoc.T_HEAD2]
    assert cFmt.foreground().color() == THEME.head

    # Scene
    block = qdoc.document.findBlockByNumber(3)
    assert block.text() == "Scene"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mHead[qdoc.T_HEAD3][0]
    assert bFmt.bottomMargin() == qdoc._mHead[qdoc.T_HEAD3][1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.fontWeight() == qdoc._bold
    assert cFmt.fontPointSize() == qdoc._sHead[qdoc.T_HEAD3]
    assert cFmt.foreground().color() == THEME.head

    # Section
    block = qdoc.document.findBlockByNumber(4)
    assert block.text() == "Section"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mHead[qdoc.T_HEAD4][0]
    assert bFmt.bottomMargin() == qdoc._mHead[qdoc.T_HEAD4][1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.fontWeight() == qdoc._bold
    assert cFmt.fontPointSize() == qdoc._sHead[qdoc.T_HEAD4]
    assert cFmt.foreground().color() == THEME.head


@pytest.mark.core
def testFmtToQTextDocument_SeparatorSkip(mockGUI):
    """Test separator and skip in the ToQTextDocument class."""
    project = NWProject()
    qdoc = ToQTextDocument(project)
    qdoc.initDocument(CONFIG.textFont, THEME)

    qdoc._isNovel = True
    qdoc._isFirst = True
    qdoc._text = (
        "#! Title\n"
        "## Chapter\n"
        "### Scene 1\n"
        "Text 1\n"
        "### Scene 2\n"
        "Text 2\n"
        "#### Section\n"
        "Text 3\n"
    )
    qdoc.setSceneFormat("* * *", False)
    qdoc.setSectionFormat("", False)
    qdoc.tokenizeText()
    qdoc.doConvert()
    assert qdoc.document.blockCount() == 7

    # 0: Title
    block = qdoc.document.findBlockByNumber(0)
    assert block.text() == "Title"

    # 1: Chapter
    block = qdoc.document.findBlockByNumber(1)
    assert block.text() == "Chapter"

    # Hidden: Scene 1

    # 2: Text 1
    block = qdoc.document.findBlockByNumber(2)
    assert block.text() == "Text 1"

    # 3: Scene 2
    block = qdoc.document.findBlockByNumber(3)
    assert block.text() == "* * *"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mSep[0]
    assert bFmt.bottomMargin() == qdoc._mSep[1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.foreground().color() == THEME.text

    # 4: Text 2
    block = qdoc.document.findBlockByNumber(4)
    assert block.text() == "Text 2"

    # 5: Section
    block = qdoc.document.findBlockByNumber(5)
    assert block.text() == nwUnicode.U_NBSP
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mText[0]
    assert bFmt.bottomMargin() == qdoc._mText[1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.foreground().color() == THEME.text

    # 6: Text 3
    block = qdoc.document.findBlockByNumber(6)
    assert block.text() == "Text 3"


@pytest.mark.core
def testFmtToQTextDocument_NovelMeta(mockGUI):
    """Test novel meta formats in the ToQTextDocument class."""
    project = NWProject()
    qdoc = ToQTextDocument(project)
    qdoc.initDocument(CONFIG.textFont, THEME)

    qdoc._isNovel = True
    qdoc._isFirst = True
    qdoc.setComments(True)
    qdoc.setSynopsis(True)
    qdoc.setKeywords(True)
    qdoc._text = (
        "### Scene\n\n"
        "@pov: Jane\n"
        "@char: John, Bob\n\n"
        "%Synopsis: Stuff that happened\n\n"
        "% A regular comment\n\n"
        "Text\n\n"
    )
    qdoc.tokenizeText()
    qdoc.doConvert()
    assert qdoc.document.blockCount() == 6

    # 0: Scene
    block = qdoc.document.findBlockByNumber(0)
    assert block.text() == "Scene"

    # 1: Jane
    block = qdoc.document.findBlockByNumber(1)
    assert block.text() == "Point of View: Jane"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mMeta[0]
    assert bFmt.bottomMargin() == 0.0
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.foreground().color() == THEME.keyword
    cFmt = charFmtInBlock(block, 16)
    assert cFmt.foreground().color() == THEME.tag

    # 2: John, Bob
    block = qdoc.document.findBlockByNumber(2)
    assert block.text() == "Characters: John, Bob"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == 0.0
    assert bFmt.bottomMargin() == qdoc._mMeta[1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.foreground().color() == THEME.keyword
    cFmt = charFmtInBlock(block, 13)
    assert cFmt.foreground().color() == THEME.tag

    # 3: Synopsis
    block = qdoc.document.findBlockByNumber(3)
    assert block.text() == "Synopsis: Stuff that happened"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mText[0]
    assert bFmt.bottomMargin() == qdoc._mText[1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.foreground().color() == THEME.modifier
    cFmt = charFmtInBlock(block, 11)
    assert cFmt.foreground().color() == THEME.note

    # 4: Comment
    block = qdoc.document.findBlockByNumber(4)
    assert block.text() == "Comment: A regular comment"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mText[0]
    assert bFmt.bottomMargin() == qdoc._mText[1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.foreground().color() == THEME.comment
    cFmt = charFmtInBlock(block, 10)
    assert cFmt.foreground().color() == THEME.comment

    # 5: Text
    block = qdoc.document.findBlockByNumber(5)
    assert block.text() == "Text"


@pytest.mark.core
def testFmtToQTextDocument_NoteMeta(mockGUI):
    """Test note meta formats in the ToQTextDocument class."""
    project = NWProject()
    qdoc = ToQTextDocument(project)
    qdoc.initDocument(CONFIG.textFont, THEME)

    qdoc._isNovel = False
    qdoc._isFirst = True
    qdoc.setComments(True)
    qdoc.setSynopsis(True)
    qdoc.setKeywords(True)
    qdoc._text = (
        "# Jane Smith\n\n"
        "@tag: Jane | Jane Smith\n"
        "%Short: All about Jane\n\n"
        "Text\n\n"
    )
    qdoc.tokenizeText()
    qdoc.doConvert()
    assert qdoc.document.blockCount() == 4

    # 0: Title
    block = qdoc.document.findBlockByNumber(0)
    assert block.text() == "Jane Smith"

    # 1: Tag
    block = qdoc.document.findBlockByNumber(1)
    assert block.text() == "Tag: Jane | Jane Smith"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mMeta[0]
    assert bFmt.bottomMargin() == qdoc._mMeta[1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.foreground().color() == THEME.keyword
    cFmt = charFmtInBlock(block, 6)
    assert cFmt.foreground().color() == THEME.tag
    cFmt = charFmtInBlock(block, 11)
    assert cFmt.foreground().color() == THEME.text
    cFmt = charFmtInBlock(block, 13)
    assert cFmt.foreground().color() == THEME.optional

    # 2: Short
    block = qdoc.document.findBlockByNumber(2)
    assert block.text() == "Short Description: All about Jane"
    bFmt = block.blockFormat()
    assert bFmt.topMargin() == qdoc._mText[0]
    assert bFmt.bottomMargin() == qdoc._mText[1]
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.foreground().color() == THEME.modifier
    cFmt = charFmtInBlock(block, 20)
    assert cFmt.foreground().color() == THEME.note

    # 3: Text
    block = qdoc.document.findBlockByNumber(3)
    assert block.text() == "Text"


@pytest.mark.core
def testFmtToQTextDocument_TextBlockFormats(mockGUI):
    """Test text block formats in the ToQTextDocument class."""
    project = NWProject()
    qdoc = ToQTextDocument(project)
    qdoc.setFirstLineIndent(True, 2.0, False)
    qdoc.initDocument(CONFIG.textFont, THEME)

    qdoc._isNovel = True
    qdoc._isFirst = True

    # Alignment & Indent
    # ==================
    qdoc.document.clear()

    qdoc._text = (
        "### Scene\n\n"
        "Left <<\n\n"
        ">> Center <<\n\n"
        ">> Right\n\n"
        "> Left Indent\n\n"
        "Right Indent <\n\n"
        "> Double Indent <\n\n"
        "Text Indent\n\n"
    )
    qdoc.tokenizeText()
    qdoc.doConvert()
    assert qdoc.document.blockCount() == 8

    # 0: Scene
    block = qdoc.document.findBlockByNumber(0)
    assert block.text() == "Scene"

    # 1: Left
    block = qdoc.document.findBlockByNumber(1)
    assert block.text() == "Left"
    bFmt = block.blockFormat()
    assert bFmt.alignment() == QtAlignLeft

    # 2: Center
    block = qdoc.document.findBlockByNumber(2)
    assert block.text() == "Center"
    bFmt = block.blockFormat()
    assert bFmt.alignment() == QtAlignCenter

    # 3: Right
    block = qdoc.document.findBlockByNumber(3)
    assert block.text() == "Right"
    bFmt = block.blockFormat()
    assert bFmt.alignment() == QtAlignRight

    # 4: Left Indent
    block = qdoc.document.findBlockByNumber(4)
    assert block.text() == "Left Indent"
    bFmt = block.blockFormat()
    assert bFmt.alignment() == QtAlignAbsolute
    assert bFmt.leftMargin() == qdoc._mIndent
    assert bFmt.rightMargin() == 0.0

    # 5: Right Indent
    block = qdoc.document.findBlockByNumber(5)
    assert block.text() == "Right Indent"
    bFmt = block.blockFormat()
    assert bFmt.alignment() == QtAlignAbsolute
    assert bFmt.leftMargin() == 0.0
    assert bFmt.rightMargin() == qdoc._mIndent

    # 6: Double Indent
    block = qdoc.document.findBlockByNumber(6)
    assert block.text() == "Double Indent"
    bFmt = block.blockFormat()
    assert bFmt.alignment() == QtAlignAbsolute
    assert bFmt.leftMargin() == qdoc._mIndent
    assert bFmt.rightMargin() == qdoc._mIndent

    # 7: Text Indent
    block = qdoc.document.findBlockByNumber(7)
    assert block.text() == "Text Indent"
    bFmt = block.blockFormat()
    assert bFmt.alignment() == QtAlignAbsolute
    assert bFmt.textIndent() == qdoc._tIndent
    assert bFmt.leftMargin() == 0.0
    assert bFmt.rightMargin() == 0.0

    # Unreachable
    # ===========
    # Some formatting markers are currently not reachable
    qdoc.document.clear()

    qdoc._tokens = [
        (qdoc.T_TEXT, 1, "This is justified", [], qdoc.A_JUSTIFY),
        (qdoc.T_TEXT, 1, "This has a page break", [], qdoc.A_PBA),
    ]
    qdoc.doConvert()
    assert qdoc.document.blockCount() == 2

    # 0: Justify
    block = qdoc.document.findBlockByNumber(0)
    assert block.text() == "This is justified"
    bFmt = block.blockFormat()
    assert bFmt.alignment() == QtAlignJustify

    # 1: Page Break After
    block = qdoc.document.findBlockByNumber(1)
    assert block.text() == "This has a page break"
    bFmt = block.blockFormat()
    assert bFmt.pageBreakPolicy() == QtPageBreakAfter


@pytest.mark.core
def testFmtToQTextDocument_TextCharFormats(mockGUI):
    """Test text char formats in the ToQTextDocument class."""
    CONFIG.fmtDQuoteOpen  = nwUnicode.U_LDQUO
    CONFIG.fmtDQuoteClose = nwUnicode.U_RDQUO
    CONFIG.altDialogOpen = "|<"
    CONFIG.altDialogClose = ">|"

    project = NWProject()
    qdoc = ToQTextDocument(project)

    # Convert before init
    qdoc._text = "Blabla"
    qdoc.setDialogueHighlight(True)
    qdoc.doConvert()
    qdoc.tokenizeText()
    assert qdoc.document.toPlainText() == ""

    # Init
    qdoc.initDocument(CONFIG.textFont, THEME)

    qdoc._isNovel = True
    qdoc._isFirst = True

    qdoc._text = (
        "### Scene\n\n"
        "With [b]bold[/b] text\n\n"
        "With [i]italic[/i] text\n\n"
        "With [s]deleted[/s] text\n\n"
        "With [u]underlined[/u] text\n\n"
        "With [m]highlighted[/m] text\n\n"
        "With super[sup]script[/sup] text\n\n"
        "With sub[sub]script[/sub] text\n\n"
        "With \u201cdialog\u201d text\n\n"
        "With |<alternative dialog>| text\n\n"
    )
    qdoc.tokenizeText()
    qdoc.doConvert()
    assert qdoc.document.blockCount() == 10

    # 0: Scene
    block = qdoc.document.findBlockByNumber(0)
    assert block.text() == "Scene"

    # 1: Bold
    block = qdoc.document.findBlockByNumber(1)
    assert block.text() == "With bold text"
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.fontWeight() == qdoc._normal
    cFmt = charFmtInBlock(block, 6)
    assert cFmt.fontWeight() == qdoc._bold
    cFmt = charFmtInBlock(block, 10)
    assert cFmt.fontWeight() == qdoc._normal

    # 2: Italic
    block = qdoc.document.findBlockByNumber(2)
    assert block.text() == "With italic text"
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.fontItalic() is False
    cFmt = charFmtInBlock(block, 6)
    assert cFmt.fontItalic() is True
    cFmt = charFmtInBlock(block, 12)
    assert cFmt.fontItalic() is False

    # 3: Deleted
    block = qdoc.document.findBlockByNumber(3)
    assert block.text() == "With deleted text"
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.fontStrikeOut() is False
    cFmt = charFmtInBlock(block, 6)
    assert cFmt.fontStrikeOut() is True
    cFmt = charFmtInBlock(block, 13)
    assert cFmt.fontStrikeOut() is False

    # 4: Underlined
    block = qdoc.document.findBlockByNumber(4)
    assert block.text() == "With underlined text"
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.fontUnderline() is False
    cFmt = charFmtInBlock(block, 6)
    assert cFmt.fontUnderline() is True
    cFmt = charFmtInBlock(block, 16)
    assert cFmt.fontUnderline() is False

    # 5: Highlighted
    block = qdoc.document.findBlockByNumber(5)
    assert block.text() == "With highlighted text"
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.background() == QtTransparent
    cFmt = charFmtInBlock(block, 6)
    assert cFmt.background() == THEME.highlight
    cFmt = charFmtInBlock(block, 17)
    assert cFmt.background() == QtTransparent

    # 6: Superscript
    block = qdoc.document.findBlockByNumber(6)
    assert block.text() == "With superscript text"
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.verticalAlignment() == QtVAlignNormal
    cFmt = charFmtInBlock(block, 11)
    assert cFmt.verticalAlignment() == QtVAlignSuper
    cFmt = charFmtInBlock(block, 17)
    assert cFmt.verticalAlignment() == QtVAlignNormal

    # 7: Subscript
    block = qdoc.document.findBlockByNumber(7)
    assert block.text() == "With subscript text"
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.verticalAlignment() == QtVAlignNormal
    cFmt = charFmtInBlock(block, 9)
    assert cFmt.verticalAlignment() == QtVAlignSub
    cFmt = charFmtInBlock(block, 15)
    assert cFmt.verticalAlignment() == QtVAlignNormal

    # 8: Dialogue
    block = qdoc.document.findBlockByNumber(8)
    assert block.text() == "With \u201cdialog\u201d text"
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.foreground() == THEME.text
    cFmt = charFmtInBlock(block, 6)
    assert cFmt.foreground() == THEME.dialog
    cFmt = charFmtInBlock(block, 14)
    assert cFmt.foreground() == THEME.text

    # 9: Alt. Dialogue
    block = qdoc.document.findBlockByNumber(9)
    assert block.text() == "With |<alternative dialog>| text"
    cFmt = charFmtInBlock(block, 1)
    assert cFmt.foreground() == THEME.text
    cFmt = charFmtInBlock(block, 6)
    assert cFmt.foreground() == THEME.altdialog
    cFmt = charFmtInBlock(block, 28)
    assert cFmt.foreground() == THEME.text


@pytest.mark.core
def testFmtToQTextDocument_Footnotes(mockGUI):
    """Test footnotes in the ToQTextDocument class."""
    project = NWProject()
    qdoc = ToQTextDocument(project)
    qdoc.initDocument(CONFIG.textFont, THEME)

    qdoc._isNovel = True
    qdoc._isFirst = True

    qdoc._text = (
        "### Scene\n\n"
        "Text with valid[footnote:fn1] and invalid[footnote:fn2] footnotes.\n\n"
        "%Footnote.fn1: Here's the first note.\n\n"
    )
    qdoc.tokenizeText()
    qdoc.doConvert()
    qdoc.appendFootnotes()
    assert qdoc.document.blockCount() == 4

    # 0: Scene
    block = qdoc.document.findBlockByNumber(0)
    assert block.text() == "Scene"

    # 1: Text
    block = qdoc.document.findBlockByNumber(1)
    assert block.text() == "Text with valid[1] and invalid[ERR] footnotes."

    # 2: Footnotes
    block = qdoc.document.findBlockByNumber(2)
    assert block.text() == "Footnotes"

    # 3: Footnote 1
    block = qdoc.document.findBlockByNumber(3)
    assert block.text() == "1. Here's the first note."
