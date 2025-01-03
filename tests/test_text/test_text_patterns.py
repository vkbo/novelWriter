"""
novelWriter – Patterns Module Tester
====================================

This file is a part of novelWriter
Copyright (C) 2024 Veronica Berglyd Olsen and novelWriter contributors

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

import pytest

from novelwriter import CONFIG
from novelwriter.constants import nwUnicode
from novelwriter.text.patterns import REGEX_PATTERNS, DialogParser


def allMatches(regEx: re.Pattern, text: str) -> list[list[str]]:
    """Get all matches for a regex."""
    result = []
    for res in regEx.finditer(text):
        result.append([
            (res.group(n), res.start(n), res.end(n))
            for n in range((res.lastindex or 0) + 1)
        ])
    return result


@pytest.mark.core
def testTextPatterns_Urls():
    """Test the URL regex."""
    regEx = REGEX_PATTERNS.url

    valid = [
        "http://example.com",
        "http://example.com/",
        "http://example.com/path+to+page",
        "http://example.com/path-to-page",
        "http://example.com/path_to_page",
        "http://example.com/path~to~page",
        "http://example.com/path/to/page",
        "http://example.com/path/to/page.html",
        "http://example.com/path/to/page.html#title",
        "http://example.com/path/to/page.html#title%20here",
        "http://example.com/path/to/page.html#title%20here",
        "http://example.com/path/to/page?foo=bar&bar=baz",
        "http://example.com/path/to/page.html?foo=bar&bar=baz",
        "http://example.com/path/to/page.html#title?foo=bar&bar=baz",
        "http://user:password@example.com/",
        "http://www.example.com/",
        "http://www.www.example.com/",
        "http://www.www.www.example.com/",
        "https://example.com",
        "https://www.example.com/",
    ]
    invalid = [
        "hppt://example.com/",
        "sftp://example.com/",
        "http:/example.com/",
        "http://www example com/",
        "http://www\texample\tcom/",
    ]

    for test in valid:
        assert allMatches(regEx, f"Text {test} more text") == [[(test, 5, 5 + len(test))]]

    for test in invalid:
        assert allMatches(regEx, f"Text {test} more text") == []


@pytest.mark.core
def testTextPatterns_Words():
    """Test the word split regex."""
    regEx = REGEX_PATTERNS.wordSplit

    # Spaces
    assert allMatches(regEx, "one two three") == [
        [("one", 0, 3)], [("two", 4, 7)], [("three", 8, 13)]
    ]

    # Hyphens
    assert allMatches(regEx, "one-two-three") == [
        [("one", 0, 3)], [("two", 4, 7)], [("three", 8, 13)]
    ]

    # Em Dashes
    assert allMatches(regEx, "one\u2014two\u2014three") == [
        [("one", 0, 3)], [("two", 4, 7)], [("three", 8, 13)]
    ]

    # Em Dashes
    assert allMatches(regEx, "one\u2014two\u2014three") == [
        [("one", 0, 3)], [("two", 4, 7)], [("three", 8, 13)]
    ]

    # Plus
    assert allMatches(regEx, "one+two+three") == [
        [("one", 0, 3)], [("two", 4, 7)], [("three", 8, 13)]
    ]

    # Slash
    assert allMatches(regEx, "one/two/three") == [
        [("one", 0, 3)], [("two", 4, 7)], [("three", 8, 13)]
    ]

    # Brackets
    assert allMatches(regEx, "one[two]three") == [
        [("one", 0, 3)], [("two", 4, 7)], [("three", 8, 13)]
    ]

    # Colon
    assert allMatches(regEx, "one:two:three") == [
        [("one", 0, 3)], [("two", 4, 7)], [("three", 8, 13)]
    ]


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
def testTextPatterns_LineBreakReplace():
    """Test replacing forced line breaks."""
    regEx = REGEX_PATTERNS.lineBreak

    assert regEx.sub("\n", "one[br]two") == "one\ntwo"
    assert regEx.sub("\n", "one[br]\ntwo") == "one\ntwo"
    assert regEx.sub("\n", "one[br]\n\ntwo") == "one\n\ntwo"
    assert regEx.sub("\n", "one[BR]two") == "one\ntwo"
    assert regEx.sub("\n", "one[BR]\ntwo") == "one\ntwo"
    assert regEx.sub("\n", "one[BR]\n\ntwo") == "one\n\ntwo"


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
    # Before set, the regex is None
    CONFIG.dialogStyle = 0
    assert REGEX_PATTERNS.dialogStyle is None

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
    assert regEx is not None

    # Defined single quotes are recognised
    assert allMatches(regEx, "one \u2018two\u2019 three") == [
        [("\u2018two\u2019", 4, 9)]
    ]

    # Defined double quotes are recognised
    assert allMatches(regEx, "one \u201ctwo\u201d three") == [
        [("\u201ctwo\u201d", 4, 9)]
    ]

    # Both single and double quotes are recognised
    assert allMatches(regEx, "one \u2018two\u2019 three \u201cfour\u201d five") == [
        [("\u2018two\u2019", 4, 9)], [("\u201cfour\u201d", 16, 22)]
    ]

    # But not mixed
    assert allMatches(regEx, "one \u2018two\u201d three \u201cfour\u2019 five") == [
        [("\u2018two\u201d three \u201cfour\u2019", 4, 22)]
    ]

    # Straight single quotes are ignored
    assert allMatches(regEx, "one 'two' three") == []

    # Straight double quotes are ignored
    assert allMatches(regEx, "one \"two\" three") == []

    # Check with no whitespace, single quote
    assert allMatches(regEx, "one\u2018two\u2019three") == [
        [("\u2018two\u2019", 3, 8)]
    ]
    assert allMatches(regEx, "one\u2018two\u2019 three") == [
        [("\u2018two\u2019", 3, 8)]
    ]

    # Check with no whitespace, double quote
    assert allMatches(regEx, "one\u201ctwo\u201dthree") == [
        [("\u201ctwo\u201d", 3, 8)]
    ]
    assert allMatches(regEx, "one\u201ctwo\u201d three") == [
        [("\u201ctwo\u201d", 3, 8)]
    ]

    # Check with apostrophe
    assert allMatches(regEx, "one \u2018two\u2019s three\u2019, \u2018four\u2019 five") == [
        [("\u2018two\u2019s three\u2019", 4, 17)],
        [("\u2018four\u2019", 19, 25)],
    ]

    # Open
    # ====

    CONFIG.allowOpenDial = True
    regEx = REGEX_PATTERNS.dialogStyle
    assert regEx is not None

    # Defined single quotes are recognised also when open
    assert allMatches(regEx, "one \u2018two three") == [
        [("\u2018two three", 4, 14)]
    ]

    # Defined double quotes are recognised also when open
    assert allMatches(regEx, "one \u201ctwo three") == [
        [("\u201ctwo three", 4, 14)]
    ]


@pytest.mark.core
def testTextPatterns_DialoguePlain():
    """Test the dialogue style pattern regexes for plain quotes."""
    # Set the config
    CONFIG.fmtSQuoteOpen  = "'"
    CONFIG.fmtSQuoteClose = "'"
    CONFIG.fmtDQuoteOpen  = '"'
    CONFIG.fmtDQuoteClose = '"'

    CONFIG.dialogStyle = 3
    CONFIG.allowOpenDial = False
    regEx = REGEX_PATTERNS.dialogStyle
    assert regEx is not None

    # Double
    # ======

    # One double quoted string
    assert allMatches(regEx, "one \"two\" three") == [
        [("\"two\"", 4, 9)]
    ]

    # Two double quoted strings
    assert allMatches(regEx, "one \"two\" three \"four\" five") == [
        [("\"two\"", 4, 9)], [("\"four\"", 16, 22)],
    ]

    # No space
    assert allMatches(regEx, "one\"two\" three") == []
    assert allMatches(regEx, "one \"two\"three") == []
    assert allMatches(regEx, "one\"two\"three") == []

    # Single
    # ======

    # One single quoted string
    assert allMatches(regEx, "one 'two' three") == [
        [("'two'", 4, 9)]
    ]

    # Two single quoted strings
    assert allMatches(regEx, "one 'two' three 'four' five") == [
        [("'two'", 4, 9)], [("'four'", 16, 22)],
    ]

    # No space
    assert allMatches(regEx, "one'two' three") == []
    assert allMatches(regEx, "one 'two'three") == []
    assert allMatches(regEx, "one'two'three") == []

    # Check with apostrophe
    assert allMatches(regEx, "one 'two's three', 'four' five") == [
        [("'two's three'", 4, 17)],
        [("'four'", 19, 25)],
    ]


@pytest.mark.core
def testTextPatterns_DialogueSpecial():
    """Test the special dialogue style pattern regexes."""
    # Before set, the regex is None
    CONFIG.altDialogOpen = ""
    CONFIG.altDialogClose = ""
    assert REGEX_PATTERNS.altDialogStyle is None

    # Set the config
    CONFIG.altDialogOpen = "::"
    CONFIG.altDialogClose = "::"

    # Alternative Dialogue
    # ====================
    regEx = REGEX_PATTERNS.altDialogStyle
    assert regEx is not None

    # With no padding
    assert allMatches(regEx, "one ::two:: three") == [
        [("::two::", 4, 11)]
    ]

    # With padding
    assert allMatches(regEx, "one :: two :: three") == [
        [(":: two ::", 4, 13)]
    ]


@pytest.mark.core
def testTextPatterns_DialogParserEnglish():
    """Test the dialog parser with English settings."""
    # Set the config
    CONFIG.dialogStyle = 3
    CONFIG.fmtSQuoteOpen  = nwUnicode.U_LSQUO
    CONFIG.fmtSQuoteClose = nwUnicode.U_RSQUO
    CONFIG.fmtDQuoteOpen  = nwUnicode.U_LDQUO
    CONFIG.fmtDQuoteClose = nwUnicode.U_RDQUO

    parser = DialogParser()
    parser.initParser()
    assert parser.enabled is True

    # Positions:   0                 18
    assert parser("“Simple dialogue.”") == [
        (0, 18),
    ]

    # Positions:   0                 18
    assert parser("“Simple dialogue,” argued John.") == [
        (0, 18),
    ]

    # Positions:   0                 18            32                      56
    assert parser("“Simple dialogue,” argued John, “is not always so easy.”") == [
        (0, 18), (32, 56),
    ]

    # With Narrator breaks
    CONFIG.dialogLine = ""
    CONFIG.narratorBreak = nwUnicode.U_EMDASH
    parser.initParser()

    # Positions:   0                 18              34                      58
    assert parser("“Simple dialogue, — argued John, — is not always so easy.”") == [
        (0, 18), (34, 58),
    ]

    # Positions:   0                 18            32                      56
    assert parser("“Simple dialogue, —argued John—, is not always so easy.”") == [
        (0, 18), (32, 56),
    ]

    # Positions:   0                              31
    assert parser("“Simple dialogue, —argued John”") == [
        (0, 31),
    ]


@pytest.mark.core
def testTextPatterns_DialogParserSpanish():
    """Test the dialog parser with Spanish settings."""
    # Set the config
    CONFIG.dialogStyle = 3
    CONFIG.fmtSQuoteOpen  = nwUnicode.U_LSAQUO
    CONFIG.fmtSQuoteClose = nwUnicode.U_RSAQUO
    CONFIG.fmtDQuoteOpen  = nwUnicode.U_LAQUO
    CONFIG.fmtDQuoteClose = nwUnicode.U_RAQUO
    CONFIG.dialogLine = nwUnicode.U_EMDASH + nwUnicode.U_RAQUO
    CONFIG.narratorBreak = nwUnicode.U_EMDASH

    parser = DialogParser()
    parser.initParser()

    # Positions:   0                 18                                  54              70
    assert parser("—No te preocupes. —Cerró la puerta y salió corriendo—. Volveré pronto.") == [
        (0, 18), (54, 70),
    ]

    # Positions:   0             14
    assert parser("«Tengo hambre», pensó Pedro.") == [
        (0, 14),
    ]

    # Positions:   0               16
    assert parser("—Puedes hacerlo —le dije y pensé «pero te costará mucho trabajo».") == [
        (0, 16),
    ]


@pytest.mark.core
def testTextPatterns_DialogParserPortuguese():
    """Test the dialog parser with Portuguese settings."""
    # Set the config
    CONFIG.dialogStyle = 0
    CONFIG.fmtSQuoteOpen  = nwUnicode.U_LSAQUO
    CONFIG.fmtSQuoteClose = nwUnicode.U_RSAQUO
    CONFIG.fmtDQuoteOpen  = nwUnicode.U_LAQUO
    CONFIG.fmtDQuoteClose = nwUnicode.U_RAQUO
    CONFIG.dialogLine = nwUnicode.U_EMDASH
    CONFIG.narratorBreak = nwUnicode.U_EMDASH

    parser = DialogParser()
    parser.initParser()

    # Positions:   0                    21
    assert parser("— Está ficando tarde.") == [
        (0, 21),
    ]

    # Positions:   0           12
    assert parser("— Ainda não — ela responde.") == [
        (0, 12),
    ]

    # Positions:   0           12               29                  49
    assert parser("— Tudo bem? — ele pergunta. — Você falou com ele?") == [
        (0, 12), (29, 49),
    ]

    # Positions:   0           12               29                  49
    assert parser("— Tudo bem? — ele pergunta —. Você falou com ele?") == [
        (0, 12), (29, 49),
    ]


@pytest.mark.core
def testTextPatterns_DialogParserPolish():
    """Test the dialog parser with alternating Polish settings."""
    # Set the config
    CONFIG.dialogStyle = 0
    CONFIG.fmtSQuoteOpen  = "'"
    CONFIG.fmtSQuoteClose = "'"
    CONFIG.fmtDQuoteOpen  = '"'
    CONFIG.fmtDQuoteClose = '"'
    CONFIG.dialogLine = ""
    CONFIG.narratorBreak = ""
    CONFIG.narratorDialog = nwUnicode.U_ENDASH

    parser = DialogParser()
    parser.initParser()

    # This is what an example dialogue might look like using Polish punctuation rules
    # See discussion #1976

    assert parser(
        "– Example statement – someone said. And he added: – Another example statement."
    ) == [
        (0, 20), (50, 78),
    ]

    assert parser(
        "– Oh my! – It would be nice if only the statements were highlighted, without "
        "any narration. In a paragraph where there is only a short statement and then "
        "a lot happens, this would be especially justified."
    ) == [
        (0, 9),
    ]

    assert parser(
        "There are also sometimes paragraphs that start with a narrative, and only then "
        "someone shouts out the words: – Oooh! Look!"
    ) == [
        (109, 122),
    ]

    assert parser(
        "And so on and so forth. However, \"text in quotation marks\" should not be "
        "highlighted at all, and if so, it should be highlighted differently."
    ) == []
