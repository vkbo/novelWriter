# -*- coding: utf-8 -*-
"""novelWriter GUI Document Word Counter

 novelWriter – GUI Document Word Counter
===================================
 A thread for counting words and characters in a document

 File History:
 Created: 2019-04-22 [0.0.1]

"""

import logging
import nw

from time import time

from PyQt5.QtCore import QThread

logger = logging.getLogger(__name__)

class WordCounter(QThread):

    def __init__(self, theParent):
        QThread.__init__(self, theParent)
        self.theParent = theParent
        self.charCount = 0
        self.wordCount = 0
        self.paraCount = 0
        return

    def run(self):

        self.charCount = 0
        self.wordCount = 0
        self.paraCount = 0

        prevEmpty = True

        for n in range(self.theParent.theDoc.blockCount()):

            theBlock = self.theParent.theDoc.findBlockByNumber(n)
            if not theBlock.isValid():
                continue

            countPara = True
            theText   = theBlock.text()
            theLen    = len(theText)

            if theLen == 0:
                prevEmpty = True
                continue
            if theText[0] == "@" or theText[0] == "%":
                prevEmpty = True
                continue

            if   theText[0:5] == "#### ":
                self.wordCount -= 1
                self.charCount -= 5
                countPara = False
            elif theText[0:4] == "### ":
                self.wordCount -= 1
                self.charCount -= 4
                countPara = False
            elif theText[0:3] == "## ":
                self.wordCount -= 1
                self.charCount -= 3
                countPara = False
            elif theText[0:2] == "# ":
                self.wordCount -= 1
                self.charCount -= 2
                countPara = False

            theBuff = theText.replace("–"," ").replace("—"," ")
            self.wordCount += len(theBuff.split())
            self.charCount += theLen
            if countPara and prevEmpty:
                self.paraCount += 1
            prevEmpty = countPara == False

        return

## END Class WordCounter
