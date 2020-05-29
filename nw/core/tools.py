# -*- coding: utf-8 -*-
"""novelWriter Word Counter

 novelWriter – Word Counter
============================
 Simple word counter

 File History:
 Created: 2019-04-22 [0.0.1] countWords
 Created: 2019-10-13 [0.2.3] numberToWord, _numberToWordEN
 Merged:  2020-05-08 [0.4.5] All of the above into this file

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import nw

from os import path, unlink, rmdir

logger = logging.getLogger(__name__)

def countWords(theText):
    """Count words in a piece of text, skipping special syntax and
    comments.
    """
    charCount = 0
    wordCount = 0
    paraCount = 0
    prevEmpty = True

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

        theBuff = aLine.replace("–"," ").replace("—"," ")
        wordCount += len(theBuff.split())
        charCount += theLen
        if countPara and prevEmpty:
            paraCount += 1
        prevEmpty = countPara == False

    return charCount, wordCount, paraCount

def numberToWord(numVal, theLanguage):
    """Wrapper for converting numbers to words for chapter headings.
    """
    numWord = ""
    if theLanguage == "en":
        numWord = _numberToWordEN(numVal)
    else:
        numWord = _numberToWordEN(numVal)
    # print("%4d : %s" % (numVal, numWord))
    return numWord

def _numberToWordEN(numVal):
    """Convert numbers to English words.
    """
    numWord = ""
    oneWord = ""
    tenWord = ""
    hunWord = ""

    if numVal == 0:
        return "Zero"

    oneVal = numVal % 10
    tenVal = (numVal-oneVal) % 100
    hunVal = (numVal-tenVal-oneVal) % 1000

    if hunVal == 100: hunWord = "One Hundred"
    if hunVal == 200: hunWord = "Two Hundred"
    if hunVal == 300: hunWord = "Three Hundred"
    if hunVal == 400: hunWord = "Four Hundred"
    if hunVal == 500: hunWord = "Five Hundred"
    if hunVal == 600: hunWord = "Six Hundred"
    if hunVal == 700: hunWord = "Seven Hundred"
    if hunVal == 800: hunWord = "Eight Hundred"
    if hunVal == 900: hunWord = "Nine Hundred"

    if tenVal == 20: tenWord = "Twenty"
    if tenVal == 30: tenWord = "Thirty"
    if tenVal == 40: tenWord = "Forty"
    if tenVal == 50: tenWord = "Fifty"
    if tenVal == 60: tenWord = "Sixty"
    if tenVal == 70: tenWord = "Seventy"
    if tenVal == 80: tenWord = "Eighty"
    if tenVal == 90: tenWord = "Ninety"

    if tenVal == 10:
        if oneVal == 0: oneWord = "Ten"
        if oneVal == 1: oneWord = "Eleven"
        if oneVal == 2: oneWord = "Twelve"
        if oneVal == 3: oneWord = "Thirteen"
        if oneVal == 4: oneWord = "Fourteen"
        if oneVal == 5: oneWord = "Fifteen"
        if oneVal == 6: oneWord = "Sixteen"
        if oneVal == 7: oneWord = "Seventeen"
        if oneVal == 8: oneWord = "Eighteen"
        if oneVal == 9: oneWord = "Nineteen"
        numWord = ("%s %s" % (hunWord, oneWord)).strip()
    else:
        if oneVal == 0: oneWord = ""
        if oneVal == 1: oneWord = "One"
        if oneVal == 2: oneWord = "Two"
        if oneVal == 3: oneWord = "Three"
        if oneVal == 4: oneWord = "Four"
        if oneVal == 5: oneWord = "Five"
        if oneVal == 6: oneWord = "Six"
        if oneVal == 7: oneWord = "Seven"
        if oneVal == 8: oneWord = "Eight"
        if oneVal == 9: oneWord = "Nine"
        if tenVal == 0:
            numWord = ("%s %s" % (hunWord, oneWord)).strip()
        else:
            if oneVal == 0:
                numWord = ("%s %s" % (hunWord, tenWord)).strip()
            else:
                numWord = ("%s %s-%s" % (hunWord, tenWord, oneWord)).strip()

    return numWord
