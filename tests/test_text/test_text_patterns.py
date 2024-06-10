"""
novelWriter – Patterns Module Tester
====================================

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

from PyQt5.QtCore import QRegularExpression

from novelwriter import CONFIG
from novelwriter.constants import nwUnicode
from novelwriter.text.patterns import REGEX_PATTERNS


def allMatches(regEx: QRegularExpression, text: str) -> list[list[str]]:
    """Get all matches for a regex."""
    result = []
    itt = regEx.globalMatch(text, 0)
    while itt.hasNext():
        match = itt.next()
        result.append([
            (match.captured(n), match.capturedStart(n), match.capturedEnd(n))
            for n in range(match.lastCapturedIndex() + 1)
        ])
    return result


@pytest.mark.core
def testTextPatterns_Markdown():
    """Test the markdown pattern regexes."""
    # Bold
    regEx = REGEX_PATTERNS.markdownBold
    assert allMatches(regEx, "one **two** three") == [
        [("**two**", 4, 11), ("**", 4, 6), ("two", 6, 9), ("**", 9, 11)]
    ]
    assert allMatches(regEx, "one **two* three") == []
    assert allMatches(regEx, "one *two** three") == []
    assert allMatches(regEx, "one**two**three") == []

    # Italic
    regEx = REGEX_PATTERNS.markdownItalic
    assert allMatches(regEx, "one _two_ three") == [
        [("_two_", 4, 9), ("_", 4, 5), ("two", 5, 8), ("_", 8, 9)]
    ]
    assert allMatches(regEx, "one __two_ three") == []
    assert allMatches(regEx, "one _two__ three") == [
        [("_two__", 4, 10), ("_", 4, 5), ("two_", 5, 9), ("_", 9, 10)]
    ]
    assert allMatches(regEx, "one_two_three") == []

    # Strike
    regEx = REGEX_PATTERNS.markdownStrike
    assert allMatches(regEx, "one ~~two~~ three") == [
        [("~~two~~", 4, 11), ("~~", 4, 6), ("two", 6, 9), ("~~", 9, 11)]
    ]
    assert allMatches(regEx, "one ~~two~ three") == []
    assert allMatches(regEx, "one ~two~~ three") == []
    assert allMatches(regEx, "one~~two~~three") == []


@pytest.mark.core
def testTextPatterns_ShortcodesPlain():
    """Test the shortcode pattern regexes."""
    regEx = REGEX_PATTERNS.shortcodePlain

    # Test Usage
    # ==========

    # General, normal usage
    assert allMatches(regEx, "one [b]two[/b] three") == [
        [("[b]", 4, 7), ("[b]", 4, 7)],
        [("[/b]", 10, 14), ("[/b]", 10, 14)],
    ]

    # General, no spaces
    assert allMatches(regEx, "one[b]two[/b]three") == [
        [("[b]", 3, 6), ("[b]", 3, 6)],
        [("[/b]", 9, 13), ("[/b]", 9, 13)],
    ]

    # General, with padding
    assert allMatches(regEx, "one [b] two [/b] three") == [
        [("[b]", 4, 7), ("[b]", 4, 7)],
        [("[/b]", 12, 16), ("[/b]", 12, 16)],
    ]

    # General, with escapes
    assert allMatches(regEx, "one \\[b]two[/b\\] three") == []

    # Test Formats
    # ============

    # Bold
    assert allMatches(regEx, "one [b]two[/b] three") == [
        [("[b]", 4, 7), ("[b]", 4, 7)],
        [("[/b]", 10, 14), ("[/b]", 10, 14)],
    ]

    # Italic
    assert allMatches(regEx, "one [i]two[/i] three") == [
        [("[i]", 4, 7), ("[i]", 4, 7)],
        [("[/i]", 10, 14), ("[/i]", 10, 14)],
    ]

    # Strike
    assert allMatches(regEx, "one [s]two[/s] three") == [
        [("[s]", 4, 7), ("[s]", 4, 7)],
        [("[/s]", 10, 14), ("[/s]", 10, 14)],
    ]

    # Underline
    assert allMatches(regEx, "one [u]two[/u] three") == [
        [("[u]", 4, 7), ("[u]", 4, 7)],
        [("[/u]", 10, 14), ("[/u]", 10, 14)],
    ]

    # Mark
    assert allMatches(regEx, "one [m]two[/m] three") == [
        [("[m]", 4, 7), ("[m]", 4, 7)],
        [("[/m]", 10, 14), ("[/m]", 10, 14)],
    ]

    # Superscript
    assert allMatches(regEx, "one [sup]two[/sup] three") == [
        [("[sup]", 4, 9), ("[sup]", 4, 9)],
        [("[/sup]", 12, 18), ("[/sup]", 12, 18)],
    ]

    # Subscript
    assert allMatches(regEx, "one [sub]two[/sub] three") == [
        [("[sub]", 4, 9), ("[sub]", 4, 9)],
        [("[/sub]", 12, 18), ("[/sub]", 12, 18)],
    ]

    # Test Invalid
    # ============

    assert allMatches(regEx, "one [x]two[/x] three") == []


@pytest.mark.core
def testTextPatterns_ShortcodesValue():
    """Test the shortcode with value pattern regexes."""
    regEx = REGEX_PATTERNS.shortcodeValue

    assert allMatches(regEx, "one [footnote:two] three") == [
        [("[footnote:two]", 4, 18), ("[footnote:", 4, 14), ("two", 14, 17), ("]", 17, 18)]
    ]


@pytest.mark.core
def testTextPatterns_DialogueStyle():
    """Test the dialogue style pattern regexes."""
    # Set the config
    CONFIG.fmtSQuoteOpen  = nwUnicode.U_LSQUO
    CONFIG.fmtSQuoteClose = nwUnicode.U_RSQUO
    CONFIG.fmtDQuoteOpen  = nwUnicode.U_LDQUO
    CONFIG.fmtDQuoteClose = nwUnicode.U_RDQUO

    CONFIG.dialogStyle = 3

    # Closed
    # ======

    CONFIG.allowOpenDial = False
    regEx = REGEX_PATTERNS.dialogStyle

    # Defined single quotes are recognised
    assert allMatches(regEx, "one \u2018two\u2019 three") == [
        [("\u2018two\u2019", 4, 9)]
    ]

    # Defined double quotes are recognised
    assert allMatches(regEx, "one \u201ctwo\u201d three") == [
        [("\u201ctwo\u201d", 4, 9)]
    ]

    # Straight single quotes are ignored
    assert allMatches(regEx, "one 'two' three") == []

    # Straight double quotes are ignored
    assert allMatches(regEx, "one \"two\" three") == []

    # Skipping whitespace is not allowed
    assert allMatches(regEx, "one\u2018two\u2019three") == []

    # Open
    # ====

    CONFIG.allowOpenDial = True
    regEx = REGEX_PATTERNS.dialogStyle

    # Defined single quotes are recognised also when open
    assert allMatches(regEx, "one \u2018two three") == [
        [("\u2018two three", 4, 14)]
    ]

    # Defined double quotes are recognised also when open
    assert allMatches(regEx, "one \u201ctwo three") == [
        [("\u201ctwo three", 4, 14)]
    ]


@pytest.mark.core
def testTextPatterns_DialogueSpecial():
    """Test the special dialogue style pattern regexes."""
    # Set the config
    CONFIG.fmtSQuoteOpen  = nwUnicode.U_LSQUO
    CONFIG.fmtSQuoteClose = nwUnicode.U_RSQUO
    CONFIG.fmtDQuoteOpen  = nwUnicode.U_LDQUO
    CONFIG.fmtDQuoteClose = nwUnicode.U_RDQUO

    CONFIG.dialogStyle = 3
    CONFIG.dialogLine = nwUnicode.U_ENDASH
    CONFIG.narratorBreak = nwUnicode.U_ENDASH
    CONFIG.altDialogOpen = "::"
    CONFIG.altDialogClose = "::"

    # Dialogue Line
    # =============
    regEx = REGEX_PATTERNS.dialogLine

    # Check dialogue line in first position
    assert allMatches(regEx, "\u2013 one two three") == [
        [("\u2013 one two three", 0, 15)]
    ]

    # Check dialogue line in second position
    assert allMatches(regEx, " \u2013 one two three") == []

    # Narrator Break
    # ==============
    regEx = REGEX_PATTERNS.narratorBreak

    # Narrator break with no padding
    assert allMatches(regEx, "one \u2013two\u2013 three") == [
        [("\u2013two\u2013", 4, 9)]
    ]

    # Narrator break with padding
    assert allMatches(regEx, "one \u2013 two \u2013 three") == []

    # Alternative Dialogue
    # ====================
    regEx = REGEX_PATTERNS.altDialogStyle

    # With no padding
    assert allMatches(regEx, "one ::two:: three") == [
        [("::two::", 4, 11)]
    ]

    # With padding
    assert allMatches(regEx, "one :: two :: three") == [
        [(":: two ::", 4, 13)]
    ]
