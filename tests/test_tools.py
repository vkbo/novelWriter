# -*- coding: utf-8 -*-
"""novelWriter Tools Tester
"""

import pytest

from nw.core.tools import countWords, numberToRoman, numberToWord

@pytest.mark.core
def testCountWords():
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
    )
    cC, wC, pC = countWords(testText)

    assert cC == 108
    assert wC == 17
    assert pC == 3

@pytest.mark.core
def testNumberWords():
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
    assert numberToWord(142, "en") == "One Hundred Forty-Two"
    assert numberToWord(999, "en") == "Nine Hundred Ninety-Nine"

@pytest.mark.core
def testRomanNumbers():
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
