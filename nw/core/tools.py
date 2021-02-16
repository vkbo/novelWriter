# -*- coding: utf-8 -*-
"""
novelWriter – Various Tools
===========================
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
#  Convert an Integer to a Number String
# =============================================================================================== #

def numberToWord(numVal, theLang):
    """Wrapper for converting numbers to words for chapter headings.
    """
    if not isinstance(numVal, int):
        return "[NaN]"

    if numVal < 0:
        return "[<0]"

    if numVal > 999:
        return "[>999]"

    numWord = ""
    theCode = theLang.split("_")[0]
    if theCode == "en":
        numWord = _numberToWord_EN(numVal)
    elif theCode in ("nb", "nn"):
        numWord = _numberToWord_NO(numVal, theCode)
    else:
        # Default to return the number as a string
        numWord = str(numVal)

    return numWord

def _numberToWord_EN(numVal):
    """Convert numbers to English words.
    """
    oneWord = ""
    tenWord = ""
    hunWord = ""

    if numVal == 0:
        return "Zero"

    oneVal = numVal % 10
    tenVal = (numVal - oneVal) % 100
    hunVal = (numVal - tenVal - oneVal) % 1000

    theWords = {
        0: "", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
        6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
        11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen",
        15: "Fifteen", 16: "Sixteen", 17: "Seventeen", 18: "Eighteen",
        19: "Nineteen", 20: "Twenty", 30: "Thirty", 40: "Forty",
        50: "Fifty", 60: "Sixty", 70: "Seventy", 80: "Eighty",
        90: "Ninety", 100: "One Hundred", 200: "Two Hundred",
        300: "Three Hundred", 400: "Four Hundred", 500: "Five Hundred",
        600: "Six Hundred", 700: "Seven Hundred", 800: "Eight Hundred",
        900: "Nine Hundred",
    }

    retVal = ""
    hunWord = theWords.get(hunVal, "")
    if tenVal == 10:
        oneWord = theWords.get(oneVal+10, "")
        retVal = f"{hunWord} {oneWord}".strip()
    else:
        oneWord = theWords.get(oneVal, "")
        if tenVal == 0:
            retVal = f"{hunWord} {oneWord}".strip()
        else:
            tenWord = theWords.get(tenVal, "")
            if oneVal == 0:
                retVal = f"{hunWord} {tenWord}".strip()
            else:
                retVal = f"{hunWord} {tenWord}-{oneWord}".strip()

    return retVal

def _numberToWord_NO(numVal, theCode):
    """Convert numbers to Norwegian words.
    """
    oneWord = ""
    tenWord = ""
    hunWord = ""

    if numVal == 0:
        return "null"

    oneVal = numVal % 10
    tenVal = (numVal - oneVal) % 100
    hunVal = (numVal - tenVal - oneVal) % 1000

    theWords = {
        0: "", 1: "én", 2: "to", 3: "tre", 4: "fire", 5: "fem", 6: "seks",
        7: "sju", 8: "åtte", 9: "ni", 10: "ti", 11: "elleve", 12: "tolv",
        13: "tretten", 14: "fjorten", 15: "femten", 16: "seksten", 17: "sytten",
        18: "atten", 19: "nitten", 20: "tjue", 30: "tretti", 40: "førti",
        50: "femti", 60: "seksti", 70: "sytti", 80: "åtti", 90: "nitti",
        100: "ett hundre", 200: "to hundre", 300: "tre hundre", 400: "fire hundre",
        500: "fem hundre", 600: "seks hundre", 700: "sju hundre",
        800: "åtte hundre", 900: "ni hundre",
    }

    if theCode == "nn":
        theWords[1] = "ein"
        theWords[100] = "eitt hundre"

    retVal = ""
    hunWord = theWords.get(hunVal, "")
    if tenVal == 10:
        oneWord = theWords.get(oneVal+10, "")
        sepVal = " og " if hunWord and oneWord else " "
        retVal = f"{hunWord}{sepVal}{oneWord}"
    else:
        oneWord = theWords.get(oneVal, "")
        if tenVal == 0:
            sepVal = " og " if hunWord and oneWord else " "
            retVal = f"{hunWord}{sepVal}{oneWord}".strip()
        else:
            tenWord = theWords.get(tenVal, "")
            sepVal = " og " if hunWord and tenWord else " "
            if oneVal == 0:
                retVal = f"{hunWord}{sepVal}{tenWord}".strip()
            else:
                retVal = f"{hunWord}{sepVal}{tenWord}{oneWord}".strip()

    return retVal.strip()
