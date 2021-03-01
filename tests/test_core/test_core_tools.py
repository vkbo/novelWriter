# -*- coding: utf-8 -*-
"""
novelWriter – Core Tools Tester
===============================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

import pytest

from nw.core.tools import countWords, numberToRoman, numberToWord

@pytest.mark.core
def testCoreTools_CountWords():
    """Test the word counter and the exclusion filers.
    """
    testText = (
        "# Heading One\n"
        "## Heading Two\n"
        "### Heading Three\n"
        "#### Heading Four\n"
        "\n"
        "@tag: value\n"
        "\n"
        "% A comment that should n ot be counted.\n"
        "\n"
        "The first paragraph.\n"
        "\n"
        "The second paragraph.\n"
        "\n"
        "\n"
        "The third paragraph.\n"
        "\n"
        "Dashes\u2013and even longer\u2014dashes."
    )
    cC, wC, pC = countWords(testText)

    assert cC == 138
    assert wC == 22
    assert pC == 4

# END Test testCoreTools_CountWords

@pytest.mark.core
def testCoreTools_RomanNumbers():
    """Test conversion of integers to Roman numbers.
    """
    assert numberToRoman(None, False) == "NAN"
    assert numberToRoman(0, False) == "OOR"
    assert numberToRoman(1, False) == "I"
    assert numberToRoman(2, False) == "II"
    assert numberToRoman(3, False) == "III"
    assert numberToRoman(4, False) == "IV"
    assert numberToRoman(5, False) == "V"
    assert numberToRoman(6, False) == "VI"
    assert numberToRoman(7, False) == "VII"
    assert numberToRoman(8, False) == "VIII"
    assert numberToRoman(9, False) == "IX"
    assert numberToRoman(10, False) == "X"
    assert numberToRoman(14, False) == "XIV"
    assert numberToRoman(42, False) == "XLII"
    assert numberToRoman(99, False) == "XCIX"
    assert numberToRoman(142, False) == "CXLII"
    assert numberToRoman(542, False) == "DXLII"
    assert numberToRoman(999, False) == "CMXCIX"
    assert numberToRoman(2010, False) == "MMX"
    assert numberToRoman(999, True) == "cmxcix"

# END Test testCoreTools_RomanNumbers

@pytest.mark.core
def testCoreTools_NumberWords():
    """Test the conversion of integer to English words.
    """
    assert numberToWord(0, "en") == "Zero"
    assert numberToWord(1, "en") == "One"
    assert numberToWord(2, "en") == "Two"
    assert numberToWord(3, "en") == "Three"
    assert numberToWord(4, "en") == "Four"
    assert numberToWord(5, "en") == "Five"
    assert numberToWord(6, "en") == "Six"
    assert numberToWord(7, "en") == "Seven"
    assert numberToWord(8, "en") == "Eight"
    assert numberToWord(9, "en") == "Nine"
    assert numberToWord(10, "en") == "Ten"
    assert numberToWord(11, "en") == "Eleven"
    assert numberToWord(12, "en") == "Twelve"
    assert numberToWord(13, "en") == "Thirteen"
    assert numberToWord(14, "en") == "Fourteen"
    assert numberToWord(15, "en") == "Fifteen"
    assert numberToWord(16, "en") == "Sixteen"
    assert numberToWord(17, "en") == "Seventeen"
    assert numberToWord(18, "en") == "Eighteen"
    assert numberToWord(19, "en") == "Nineteen"
    assert numberToWord(20, "en") == "Twenty"
    assert numberToWord(21, "en") == "Twenty-One"
    assert numberToWord(29, "en") == "Twenty-Nine"
    assert numberToWord(42, "en") == "Forty-Two"
    assert numberToWord(114, "en") == "One Hundred Fourteen"
    assert numberToWord(142, "en") == "One Hundred Forty-Two"
    assert numberToWord(999, "en") == "Nine Hundred Ninety-Nine"

    # Check a few with a nonsense language setting
    assert numberToWord(1, "foo") == "One"
    assert numberToWord(2, "foo") == "Two"
    assert numberToWord(3, "foo") == "Three"

    # Test out of range values
    assert numberToWord(12345, "en") == "[Out of Range]"
    assert numberToWord(-2345, "en") == "[Negative]"
    assert numberToWord("234", "en") == "[NaN]"

# END Test testCoreTools_NumberWords
