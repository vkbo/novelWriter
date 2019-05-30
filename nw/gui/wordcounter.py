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

from PyQt5.QtCore import QThread

from nw.tools.wordcount import countWords

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

        theText = self.theParent.getText()
        cC, wC, pC = countWords(theText)

        self.charCount = cC
        self.wordCount = wC
        self.paraCount = pC

        return

## END Class WordCounter
