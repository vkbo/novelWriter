# -*- coding: utf-8 -*-
"""novelWriter Various Tools

 novelWriter – Various Tools
=============================
 Various core tool functions

 File History:
 Created: 2019-04-22 [0.0.1]  countWords
 Created: 2019-10-13 [0.2.3]  numberToWord, _numberToWordEN
 Merged:  2020-05-08 [0.4.5]  All of the above into this file
 Created: 2020-07-05 [0.10.0] numberToRoman

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

import logging

from nw.constants import nwUnicode

logger = logging.getLogger(__name__)

# =============================================================================================== #
#  Simple Word Counter
# =============================================================================================== #

def countWords(theText):
    """Count words in a piece of text, skipping special syntax and
    comments.
    """
    charCount = 0
    wordCount = 0
    paraCount = 0
    prevEmpty = True

    # We need to treat dashes as word separators for counting words.
    # The check+replace apprach is much faster that direct replace for
    # large texts, and a bit slower for small texts, but in the latter
    # case it doesn't matter.
    if nwUnicode.U_ENDASH in theText:
        theText = theText.replace(nwUnicode.U_ENDASH, " ")
    if nwUnicode.U_EMDASH in theText:
        theText = theText.replace(nwUnicode.U_EMDASH, " ")

    for aLine in theText.splitlines():

        countPara = True
        theLen    = len(aLine)

        if theLen == 0:
            prevEmpty = True
            continue
        if aLine[0] == "@" or aLine[0] == "%":
            continue

        if aLine[0:5] == "#### ":
            wordCount -= 1
            charCount -= 5
            countPara = False
        elif aLine[0:4] == "### ":
            wordCount -= 1
            charCount -= 4
            countPara = False
        elif aLine[0:3] == "## ":
            wordCount -= 1
            charCount -= 3
            countPara = False
        elif aLine[0:2] == "# ":
            wordCount -= 1
            charCount -= 2
            countPara = False

        wordCount += len(aLine.split())
        charCount += theLen
        if countPara and prevEmpty:
            paraCount += 1

        prevEmpty = not countPara

    return charCount, wordCount, paraCount

# =============================================================================================== #
#  Convert an Integer to a Roman Number
# =============================================================================================== #

def numberToRoman(numVal, isLower=False):
    """Convert an integer to a roman number.
    """
    if not isinstance(numVal, int):
        return "NAN"
    if numVal < 1 or numVal > 4999:
        return "OOR"

    theValues = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
        (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]

    romNum = ""
    for theDiv, theSym in theValues:
        n = numVal//theDiv
        romNum += n*theSym
        numVal -= n*theDiv
        if numVal <= 0:
            break

    return romNum.lower() if isLower else romNum

# =============================================================================================== #
#  Convert an Integer to a Word Number
# =============================================================================================== #

def numberToWord(numVal, theLanguage):
    """Wrapper for converting numbers to words for chapter headings.
    """
    numWord = ""
    if theLanguage == "en":
        numWord = _numberToWordEN(numVal)
    else:
        numWord = _numberToWordEN(numVal)
    return numWord

def _numberToWordEN(numVal):
    """Convert numbers to English words.
    """
    oneWord = ""
    tenWord = ""
    hunWord = ""

    if not isinstance(numVal, int):
        return "[NaN]"

    if numVal < 0:
        return "[Negative]"

    if numVal > 999:
        return "[Out of Range]"

    if numVal == 0:
        return "Zero"

    oneVal = numVal % 10
    tenVal = (numVal - oneVal) % 100
    hunVal = (numVal - tenVal - oneVal) % 1000

    theHundreds = {
        100: "One Hundred",   200: "Two Hundred",   300: "Three Hundred",
        400: "Four Hundred",  500: "Five Hundred",  600: "Six Hundred",
        700: "Seven Hundred", 800: "Eight Hundred", 900: "Nine Hundred",
    }
    theTens = {
        20: "Twenty", 30: "Thirty",  40: "Forty",  50: "Fifty",
        60: "Sixty",  70: "Seventy", 80: "Eighty", 90: "Ninety",
    }
    theTeens = {
        0: "Ten",     1: "Eleven",  2: "Twelve",    3: "Thirteen", 4: "Fourteen",
        5: "Fifteen", 6: "Sixteen", 7: "Seventeen", 8: "Eighteen", 9: "Nineteen",
    }
    theOnes = {
        0: "",     1: "One", 2: "Two",   3: "Three", 4: "Four",
        5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine",
    }

    retVale = ""
    hunWord = theHundreds.get(hunVal, "")
    if tenVal == 10:
        oneWord = theTeens.get(oneVal, "")
        retVale = f"{hunWord} {oneWord}".strip()
    else:
        oneWord = theOnes.get(oneVal, "")
        if tenVal == 0:
            retVale = f"{hunWord} {oneWord}".strip()
        else:
            tenWord = theTens.get(tenVal, "")
            if oneVal == 0:
                retVale = f"{hunWord} {tenWord}".strip()
            else:
                retVale = f"{hunWord} {tenWord}-{oneWord}".strip()

    return retVale
