# -*- coding: utf-8 -*-
"""novelWriter Word Counter

 novelWriter – Word Counter
============================
 Simple word counter

 File History:
 Created: 2019-04-22 [0.0.1]
 Moved:   2019-05-30 [0.1.4]

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
 along with this program. If not, see https://www.gnu.org/licenses/.
"""

import logging
import nw

logger = logging.getLogger(__name__)

def countWords(theText):

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
