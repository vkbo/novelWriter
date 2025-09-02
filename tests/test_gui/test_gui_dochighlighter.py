"""
novelWriter – GUI Syntax Highlighter Tester
===========================================

This file is a part of novelWriter
Copyright (C) 2025 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa
from __future__ import annotations

import pytest

from PyQt6.QtGui import QTextCharFormat, QTextCursor, QTextDocument

from novelwriter import CONFIG, SHARED
from novelwriter.core.item import NWItem
from novelwriter.enum import nwItemClass, nwItemLayout, nwItemType, nwTheme
from novelwriter.gui.dochighlight import BLOCK_META, BLOCK_TITLE, GuiDocHighlighter, TextBlockData
from novelwriter.types import QtKeepAnchor

R_HANDLE = "3456789abcdef"
T_HANDLE = "0123456789abc"


@pytest.fixture()
def syntax(nwGUI):
    """Create a syntax object for use with testing."""
    CONFIG.lightTheme = "default_light"
    CONFIG.themeMode = nwTheme.LIGHT

    CONFIG.dialogStyle = 3
    CONFIG.fmtDQuoteOpen = "\u201c"
    CONFIG.fmtDQuoteClose = "\u201d"
    CONFIG.altDialogOpen = "::"
    CONFIG.altDialogClose = "::"
    CONFIG.showMultiSpaces = True

    theme = SHARED.theme
    theme.loadTheme(force=True)
    assert theme._guiPalette.base().color().getRgb() == (0xfc, 0xfc, 0xfc, 0xff)
    assert theme.syntaxTheme.text.getRgb() == (0x30, 0x30, 0x30, 0xff)

    doc = QTextDocument()
    syntax = GuiDocHighlighter(doc)

    # Add a Mock Item
    tRoot = NWItem(SHARED.project, R_HANDLE)
    tRoot.setClass(nwItemClass.NOVEL)
    tRoot.setType(nwItemType.ROOT)

    tItem = NWItem(SHARED.project, T_HANDLE)
    tItem.setParent(R_HANDLE)
    tItem.setLayout(nwItemLayout.NOTE)
    tItem.setClass(nwItemClass.NOVEL)
    tItem.setType(nwItemType.FILE)

    SHARED.project.tree.add(tRoot)
    SHARED.project.tree.add(tItem)

    yield syntax


def getFragments(
    syntax: GuiDocHighlighter
) -> tuple[list[tuple[int, str]], list[QTextCharFormat]]:
    """Extract all syntax highlighter fragments from a document."""
    pieces = []
    formats = []
    doc = syntax.document()
    cursor = QTextCursor(doc)
    assert doc is not None
    for b in range(doc.blockCount()):
        block = doc.findBlockByNumber(b)
        first = block.position()
        syntax.rehighlightBlock(block)
        if layout := block.layout():
            for fmt in layout.formats():
                cursor.setPosition(first + fmt.start)
                cursor.setPosition(first + fmt.start + fmt.length, QtKeepAnchor)
                pieces.append((b, fmt.start, fmt.length, cursor.selectedText()))
                formats.append(fmt.format)
    return pieces, formats


def maxOrd(text: str) -> int:
    """Get the max character value of a string."""
    return max(ord(c) for c in text)


@pytest.mark.gui
def testGuiDocHighlighter_Basic(syntax):
    """Test the basic functionality of the syntax highlighter."""
    # Alternate Spell Check
    assert syntax._spellCheck is False
    syntax.setSpellCheck(True)
    assert syntax._spellCheck is True

    # Check Handle
    assert syntax._tHandle is None
    syntax.setHandle(T_HANDLE)
    assert syntax._tHandle == T_HANDLE
    assert syntax._isNovel is False
    assert syntax._isInactive is False

    tItem = SHARED.project.tree[T_HANDLE]
    assert tItem is not None
    tItem.setLayout(nwItemLayout.DOCUMENT)
    tItem.setClass(nwItemClass.ARCHIVE)
    syntax.setHandle(T_HANDLE)
    assert syntax._tHandle == T_HANDLE
    assert syntax._isNovel is True
    assert syntax._isInactive is True


@pytest.mark.gui
def testGuiDocHighlighter_Keywords(syntax):
    """Test highlighting of keywords."""
    theme = SHARED.theme
    doc = syntax.document()
    assert doc is not None

    # Settings
    syntax._tHandle = T_HANDLE

    colKey = theme.syntaxTheme.key.getRgb()
    colTag = theme.syntaxTheme.tag.getRgb()
    colOpt = theme.syntaxTheme.opt.getRgb()
    colErr = theme.syntaxTheme.error.getRgb()

    # Ascii
    doc.setPlainText(
        "@tag: Bob | Robert\n"
        "@char: Someone\n"
    )
    syntax.rehighlightByType(BLOCK_META)
    assert maxOrd(doc.toPlainText()) <= 0x7f

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 4, "@tag"), (0, 6, 3, "Bob"), (0, 12, 6, "Robert"),
        (1, 0, 5, "@char"), (1, 7, 7, "Someone"),
    ]
    assert formats[0].foreground().color().getRgb() == colKey
    assert formats[1].foreground().color().getRgb() == colTag
    assert formats[2].foreground().color().getRgb() == colOpt
    assert formats[3].foreground().color().getRgb() == colKey
    assert formats[4].underlineColor().getRgb() == colErr

    # # Unicode <= 0xFFFF
    doc.setPlainText(
        "@tag: Zoë | Zoë Smith\n"
        "@char: Олексій\n"
    )
    syntax.rehighlightByType(BLOCK_META)
    assert 0x7f < maxOrd(doc.toPlainText()) <= 0xffff

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 4, "@tag"), (0, 6, 3, "Zoë"), (0, 12, 9, "Zoë Smith"),
        (1, 0, 5, "@char"), (1, 7, 7, "Олексій"),
    ]
    assert formats[0].foreground().color().getRgb() == colKey
    assert formats[1].foreground().color().getRgb() == colTag
    assert formats[2].foreground().color().getRgb() == colOpt
    assert formats[3].foreground().color().getRgb() == colKey
    assert formats[4].underlineColor().getRgb() == colErr

    # # Unicode > 0xFFFF
    doc.setPlainText(
        "@tag: 😄 | Smiley 😄\n"
        "@char: 😎😎😎\n"
    )
    syntax.rehighlightByType(BLOCK_META)
    assert 0xffff < maxOrd(doc.toPlainText()) <= 0xffffffff

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 4, "@tag"), (0, 6, 2, "😄"), (0, 11, 9, "Smiley 😄"),
        (1, 0, 5, "@char"), (1, 7, 6, "😎😎😎"),
    ]
    assert formats[0].foreground().color().getRgb() == colKey
    assert formats[1].foreground().color().getRgb() == colTag
    assert formats[2].foreground().color().getRgb() == colOpt
    assert formats[3].foreground().color().getRgb() == colKey
    assert formats[4].underlineColor().getRgb() == colErr


@pytest.mark.gui
def testGuiDocHighlighter_Titles(syntax):
    """Test highlighting of titles."""
    theme = SHARED.theme
    doc = syntax.document()
    assert doc is not None

    # Settings
    syntax._tHandle = T_HANDLE

    colHeadMark = theme.syntaxTheme.headH.getRgb()
    colHeadText = theme.syntaxTheme.head.getRgb()

    # Ascii
    doc.setPlainText(
        "# Heading 1\n\n"
        "## Heading 2\n\n"
        "### Heading 3\n\n"
        "#### Heading 4\n\n"
        "#! Heading A1\n\n"
        "##! Heading A2\n\n"
        "###! Heading A3\n\n"
    )
    syntax.rehighlightByType(BLOCK_TITLE)
    assert maxOrd(doc.toPlainText()) <= 0x7f

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 1, "#"), (0, 1, 10, " Heading 1"),
        (2, 0, 2, "##"), (2, 2, 10, " Heading 2"),
        (4, 0, 3, "###"), (4, 3, 10, " Heading 3"),
        (6, 0, 4, "####"), (6, 4, 10, " Heading 4"),
        (8, 0, 2, "#!"), (8, 2, 11, " Heading A1"),
        (10, 0, 3, "##!"), (10, 3, 11, " Heading A2"),
        (12, 0, 4, "###!"), (12, 4, 11, " Heading A3"),
    ]
    for i in range(0, len(formats), 2):
        assert formats[i].foreground().color().getRgb() == colHeadMark
        assert formats[i+1].foreground().color().getRgb() == colHeadText

    # Unicode <= 0xFFFF
    doc.setPlainText(
        "# Ȟǣđ 1\n\n"
        "## Ȟǣđ 2\n\n"
        "### Ȟǣđ 3\n\n"
        "#### Ȟǣđ 4\n\n"
        "#! Ȟǣđ A1\n\n"
        "##! Ȟǣđ A2\n\n"
        "###! Ȟǣđ A3\n\n"
    )
    syntax.rehighlightByType(BLOCK_TITLE)
    assert 0x7f < maxOrd(doc.toPlainText()) <= 0xffff

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 1, "#"), (0, 1, 6, " Ȟǣđ 1"),
        (2, 0, 2, "##"), (2, 2, 6, " Ȟǣđ 2"),
        (4, 0, 3, "###"), (4, 3, 6, " Ȟǣđ 3"),
        (6, 0, 4, "####"), (6, 4, 6, " Ȟǣđ 4"),
        (8, 0, 2, "#!"), (8, 2, 7, " Ȟǣđ A1"),
        (10, 0, 3, "##!"), (10, 3, 7, " Ȟǣđ A2"),
        (12, 0, 4, "###!"), (12, 4, 7, " Ȟǣđ A3"),
    ]
    for i in range(0, len(formats), 2):
        assert formats[i].foreground().color().getRgb() == colHeadMark
        assert formats[i+1].foreground().color().getRgb() == colHeadText

    # Unicode > 0xFFFF
    doc.setPlainText(
        "# 😇😎 1\n\n"
        "## 😇😎 2\n\n"
        "### 😇😎 3\n\n"
        "#### 😇😎 4\n\n"
        "#! 😇😎 A1\n\n"
        "##! 😇😎 A2\n\n"
        "###! 😇😎 A3\n\n"
    )
    syntax.rehighlightByType(BLOCK_TITLE)
    assert 0xffff < maxOrd(doc.toPlainText()) <= 0xffffffff

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 1, "#"), (0, 1, 7, " 😇😎 1"),
        (2, 0, 2, "##"), (2, 2, 7, " 😇😎 2"),
        (4, 0, 3, "###"), (4, 3, 7, " 😇😎 3"),
        (6, 0, 4, "####"), (6, 4, 7, " 😇😎 4"),
        (8, 0, 2, "#!"), (8, 2, 8, " 😇😎 A1"),
        (10, 0, 3, "##!"), (10, 3, 8, " 😇😎 A2"),
        (12, 0, 4, "###!"), (12, 4, 8, " 😇😎 A3"),
    ]
    for i in range(0, len(formats), 2):
        assert formats[i].foreground().color().getRgb() == colHeadMark
        assert formats[i+1].foreground().color().getRgb() == colHeadText


@pytest.mark.gui
def testGuiDocHighlighter_Comments(syntax):
    """Test highlighting of comments."""
    theme = SHARED.theme
    doc = syntax.document()
    assert doc is not None

    # Settings
    syntax._tHandle = T_HANDLE

    colHidden = theme.syntaxTheme.hidden.getRgb()
    colMod = theme.syntaxTheme.mod.getRgb()
    colValue = theme.syntaxTheme.val.getRgb()
    colNote = theme.syntaxTheme.note.getRgb()

    # Ascii
    doc.setPlainText(
        "% Plain\n"
        "%~ Ignored\n"
        "%Synopsis: Synopsis\n"
        "%Note.Stuff: Note\n"
    )
    syntax.rehighlight()
    assert maxOrd(doc.toPlainText()) <= 0x7f

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 7, "% Plain"),
        (1, 0, 10, "%~ Ignored"),
        (2, 0, 10, "%Synopsis:"), (2, 10, 9, " Synopsis"),
        (3, 0, 6, "%Note."), (3, 6, 6, "Stuff:"), (3, 12, 5, " Note"),
    ]
    assert formats[0].foreground().color().getRgb() == colHidden
    assert formats[1].foreground().color().getRgb() == colHidden
    assert formats[1].fontStrikeOut() is True
    assert formats[2].foreground().color().getRgb() == colMod
    assert formats[3].foreground().color().getRgb() == colNote
    assert formats[4].foreground().color().getRgb() == colMod
    assert formats[5].foreground().color().getRgb() == colValue
    assert formats[6].foreground().color().getRgb() == colNote

    # Unicode <= 0xFFFF
    doc.setPlainText(
        "% Рівнина\n"
        "%~ Ігноровано\n"
        "%Synopsis: Синопсис\n"
        "%Note.Stuff: Примітка\n"
    )
    syntax.rehighlight()
    assert 0x7f < maxOrd(doc.toPlainText()) <= 0xffff

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 9, "% Рівнина"),
        (1, 0, 13, "%~ Ігноровано"),
        (2, 0, 10, "%Synopsis:"), (2, 10, 9, " Синопсис"),
        (3, 0, 6, "%Note."), (3, 6, 6, "Stuff:"), (3, 12, 9, " Примітка"),
    ]
    assert formats[0].foreground().color().getRgb() == colHidden
    assert formats[1].foreground().color().getRgb() == colHidden
    assert formats[1].fontStrikeOut() is True
    assert formats[2].foreground().color().getRgb() == colMod
    assert formats[3].foreground().color().getRgb() == colNote
    assert formats[4].foreground().color().getRgb() == colMod
    assert formats[5].foreground().color().getRgb() == colValue
    assert formats[6].foreground().color().getRgb() == colNote

    # Unicode > 0xFFFF
    doc.setPlainText(
        "% 😎😎\n"
        "%~ 🙈🙈🙈\n"
        "%Synopsis: 😍😍😍😍\n"
        "%Note.Stuff: 😡😡😡😡😡\n"
    )
    syntax.rehighlight()
    assert 0xffff < maxOrd(doc.toPlainText()) <= 0xffffffff

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 6, "% 😎😎"),
        (1, 0, 9, "%~ 🙈🙈🙈"),
        (2, 0, 10, "%Synopsis:"), (2, 10, 9, " 😍😍😍😍"),
        (3, 0, 6, "%Note."), (3, 6, 6, "Stuff:"), (3, 12, 11, " 😡😡😡😡😡"),
    ]
    assert formats[0].foreground().color().getRgb() == colHidden
    assert formats[1].foreground().color().getRgb() == colHidden
    assert formats[1].fontStrikeOut() is True
    assert formats[2].foreground().color().getRgb() == colMod
    assert formats[3].foreground().color().getRgb() == colNote
    assert formats[4].foreground().color().getRgb() == colMod
    assert formats[5].foreground().color().getRgb() == colValue
    assert formats[6].foreground().color().getRgb() == colNote


@pytest.mark.gui
def testGuiDocHighlighter_Special(syntax):
    """Test highlighting of special commands."""
    theme = SHARED.theme
    doc = syntax.document()
    assert doc is not None

    # Settings
    syntax._tHandle = T_HANDLE

    colErr = theme.syntaxTheme.error.getRgb()
    colCode = theme.syntaxTheme.code.getRgb()
    colValue = theme.syntaxTheme.val.getRgb()

    # Ascii
    doc.setPlainText(
        "[NewPage]\n"
        "[New Page]\n"
        "[VSpace]\n"
        "[VSpace:123]\n"
        "[VSpace:Meh]\n"
    )
    syntax.rehighlight()
    assert maxOrd(doc.toPlainText()) <= 0x7f

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 9, "[NewPage]"),
        (1, 0, 10, "[New Page]"),
        (2, 0, 8, "[VSpace]"),
        (3, 0, 8, "[VSpace:"), (3, 8, 3, "123"), (3, 11, 1, "]"),
        (4, 0, 8, "[VSpace:"), (4, 8, 3, "Meh"), (4, 11, 1, "]"),
    ]
    assert formats[0].foreground().color().getRgb() == colCode
    assert formats[1].foreground().color().getRgb() == colCode
    assert formats[2].foreground().color().getRgb() == colCode
    assert formats[3].foreground().color().getRgb() == colCode
    assert formats[4].foreground().color().getRgb() == colValue
    assert formats[5].foreground().color().getRgb() == colCode
    assert formats[6].foreground().color().getRgb() == colCode
    assert formats[7].underlineColor().getRgb() == colErr
    assert formats[8].foreground().color().getRgb() == colCode

    # Unicode <= 0xFFFF
    doc.setPlainText(
        "[NewPage]\n"
        "[New Page]\n"
        "[VSpace]\n"
        "[VSpace:123]\n"
        "[VSpace:⅘]\n"
    )
    syntax.rehighlight()
    assert 0x7f < maxOrd(doc.toPlainText()) <= 0xffff

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 9, "[NewPage]"),
        (1, 0, 10, "[New Page]"),
        (2, 0, 8, "[VSpace]"),
        (3, 0, 8, "[VSpace:"), (3, 8, 3, "123"), (3, 11, 1, "]"),
        (4, 0, 8, "[VSpace:"), (4, 8, 1, "⅘"), (4, 9, 1, "]"),
    ]
    assert formats[0].foreground().color().getRgb() == colCode
    assert formats[1].foreground().color().getRgb() == colCode
    assert formats[2].foreground().color().getRgb() == colCode
    assert formats[3].foreground().color().getRgb() == colCode
    assert formats[4].foreground().color().getRgb() == colValue
    assert formats[5].foreground().color().getRgb() == colCode
    assert formats[6].foreground().color().getRgb() == colCode
    assert formats[7].underlineColor().getRgb() == colErr
    assert formats[8].foreground().color().getRgb() == colCode

    # Unicode > 0xFFFF
    doc.setPlainText(
        "[NewPage]\n"
        "[New Page]\n"
        "[VSpace]\n"
        "[VSpace:123]\n"
        "[VSpace:🙈🙈]\n"
    )
    syntax.rehighlight()
    assert 0xffff < maxOrd(doc.toPlainText()) <= 0xffffffff

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 9, "[NewPage]"),
        (1, 0, 10, "[New Page]"),
        (2, 0, 8, "[VSpace]"),
        (3, 0, 8, "[VSpace:"), (3, 8, 3, "123"), (3, 11, 1, "]"),
        (4, 0, 8, "[VSpace:"), (4, 8, 4, "🙈🙈"), (4, 12, 1, "]"),
    ]
    assert formats[0].foreground().color().getRgb() == colCode
    assert formats[1].foreground().color().getRgb() == colCode
    assert formats[2].foreground().color().getRgb() == colCode
    assert formats[3].foreground().color().getRgb() == colCode
    assert formats[4].foreground().color().getRgb() == colValue
    assert formats[5].foreground().color().getRgb() == colCode
    assert formats[6].foreground().color().getRgb() == colCode
    assert formats[7].underlineColor().getRgb() == colErr
    assert formats[8].foreground().color().getRgb() == colCode


@pytest.mark.gui
def testGuiDocHighlighter_Text(monkeypatch, syntax):
    """Test highlighting of text."""
    theme = SHARED.theme
    doc = syntax.document()
    assert doc is not None

    # Settings
    syntax._tHandle = T_HANDLE
    syntax._isNovel = True
    syntax.setSpellCheck(True)
    monkeypatch.setattr(SHARED.spelling, "checkWord", lambda *a: False)

    colHidden = theme.syntaxTheme.hidden.getRgb()
    colEmph = theme.syntaxTheme.emph.getRgb()
    colLink = theme.syntaxTheme.link.getRgb()
    colSpell = theme.syntaxTheme.spell.getRgb()
    colCode = theme.syntaxTheme.code.getRgb()
    colDialogue = theme.syntaxTheme.dialN.getRgb()
    colAltDialogue = theme.syntaxTheme.dialA.getRgb()

    # Ascii
    doc.setPlainText(
        "Text **bold** text _italic_ text ~~strike~~ text [b]bold[/b], http://example.com\n\n"
    )
    syntax.rehighlight()
    assert maxOrd(doc.toPlainText()) <= 0x7f

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 4, "Text"),
        (0, 5, 2, "**"), (0, 7, 4, "bold"), (0, 11, 2, "**"),
        (0, 14, 4, "text"),
        (0, 19, 1, "_"), (0, 20, 6, "italic"), (0, 26, 1, "_"),
        (0, 28, 4, "text"),
        (0, 33, 2, "~~"), (0, 35, 6, "strike"), (0, 41, 2, "~~"),
        (0, 44, 4, "text"),
        (0, 49, 3, "[b]"), (0, 52, 4, "bold"), (0, 56, 4, "[/b]"),
        (0, 62, 18, "http://example.com"),
    ]
    assert formats[0].underlineColor().getRgb() == colSpell  # Text
    assert formats[1].foreground().color().getRgb() == colHidden  # **
    assert formats[2].foreground().color().getRgb() == colEmph  # bold
    assert formats[2].underlineColor().getRgb() == colSpell
    assert formats[3].foreground().color().getRgb() == colHidden  # **
    assert formats[4].underlineColor().getRgb() == colSpell  # text
    assert formats[5].foreground().color().getRgb() == colHidden  # _
    assert formats[6].foreground().color().getRgb() == colEmph  # italic
    assert formats[6].underlineColor().getRgb() == colSpell
    assert formats[7].foreground().color().getRgb() == colHidden  # _
    assert formats[8].underlineColor().getRgb() == colSpell  # text
    assert formats[9].foreground().color().getRgb() == colHidden  # ~~
    assert formats[10].foreground().color().getRgb() == colHidden  # strike
    assert formats[10].fontStrikeOut() is True
    assert formats[10].underlineColor().getRgb() == colSpell
    assert formats[11].foreground().color().getRgb() == colHidden  # ~~
    assert formats[12].underlineColor().getRgb() == colSpell  # text
    assert formats[13].foreground().color().getRgb() == colCode  # [b]
    assert formats[14].underlineColor().getRgb() == colSpell  # bold
    assert formats[15].foreground().color().getRgb() == colCode  # [/b]
    assert formats[16].foreground().color().getRgb() == colLink  # http://example.com

    # Spell Check
    data = doc.findBlockByNumber(0).userData()
    assert isinstance(data, TextBlockData)
    assert data.metaData == [(62, 80, "http://example.com", "url")]
    assert data.spellErrors == [
        (0, 4, "Text"), (7, 11, "bold"),
        (14, 18, "text"), (20, 26, "italic"),
        (28, 32, "text"), (35, 41, "strike"),
        (44, 48, "text"), (52, 56, "bold"),
    ]

    # Unicode <= 0xFFFF
    doc.setPlainText(
        "\u201cDialogue,\u201d and then ::dialogue::, http://example.com\n\n"
    )
    syntax.rehighlight()
    assert 0x7f < maxOrd(doc.toPlainText()) <= 0xffff

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 1, "\u201c"), (0, 1, 8, "Dialogue"), (0, 9, 2, ",\u201d"),
        (0, 12, 3, "and"), (0, 16, 4, "then"),
        (0, 21, 2, "::"), (0, 23, 8, "dialogue"), (0, 31, 2, "::"),
        (0, 35, 18, "http://example.com"),
    ]
    assert formats[0].foreground().color().getRgb() == colDialogue  # Quote
    assert formats[1].foreground().color().getRgb() == colDialogue  # Dialogue
    assert formats[1].underlineColor().getRgb() == colSpell
    assert formats[2].foreground().color().getRgb() == colDialogue  # Quote
    assert formats[3].underlineColor().getRgb() == colSpell  # and
    assert formats[4].underlineColor().getRgb() == colSpell  # then
    assert formats[5].foreground().color().getRgb() == colAltDialogue  # ::
    assert formats[6].foreground().color().getRgb() == colAltDialogue  # dialogue
    assert formats[6].underlineColor().getRgb() == colSpell
    assert formats[7].foreground().color().getRgb() == colAltDialogue  # ::
    assert formats[8].foreground().color().getRgb() == colLink  # http://example.com

    # Spell Check
    data = doc.findBlockByNumber(0).userData()
    assert isinstance(data, TextBlockData)
    assert data.metaData == [(35, 53, "http://example.com", "url")]
    assert data.spellErrors == [
        (1, 9, "Dialogue"), (12, 15, "and"),
        (16, 20, "then"), (23, 31, "dialogue"),
    ]

    # Unicode > 0xFFFF
    doc.setPlainText(
        "\u201c😁 Grinning 😁,\u201d and then ::🙊 shush 🙊::, http://example.com\n\n"
    )
    syntax.rehighlight()
    assert 0xffff < maxOrd(doc.toPlainText()) <= 0xffffffff

    pieces, formats = getFragments(syntax)
    assert pieces == [
        (0, 0, 4, "\u201c😁 "), (0, 4, 8, "Grinning"), (0, 12, 5, " 😁,\u201d"),
        (0, 18, 3, "and"), (0, 22, 4, "then"),
        (0, 27, 5, "::🙊 "), (0, 32, 5, "shush"), (0, 37, 5, " 🙊::"),
        (0, 44, 18, "http://example.com"),
    ]
    assert formats[0].foreground().color().getRgb() == colDialogue  # Quote😁
    assert formats[1].foreground().color().getRgb() == colDialogue  # Grinning
    assert formats[1].underlineColor().getRgb() == colSpell
    assert formats[2].foreground().color().getRgb() == colDialogue  # 😁Quote
    assert formats[3].underlineColor().getRgb() == colSpell  # and
    assert formats[4].underlineColor().getRgb() == colSpell  # then
    assert formats[5].foreground().color().getRgb() == colAltDialogue  # ::🙊
    assert formats[6].foreground().color().getRgb() == colAltDialogue  # shush
    assert formats[6].underlineColor().getRgb() == colSpell
    assert formats[7].foreground().color().getRgb() == colAltDialogue  # 🙊::
    assert formats[8].foreground().color().getRgb() == colLink  # http://example.com

    # Spell Check
    data = doc.findBlockByNumber(0).userData()
    assert isinstance(data, TextBlockData)
    assert data.metaData == [(40, 58, "http://example.com", "url")]
    assert data.spellErrors == [
        (4, 12, "Grinning"), (18, 21, "and"),
        (22, 26, "then"), (32, 37, "shush"),
    ]
