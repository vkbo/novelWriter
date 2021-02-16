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

from nw.core.tools import countWords, numberToRoman

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
