# -*- coding: utf-8 -*-
"""novelWriter GUI Document Word Counter

 novelWriter – GUI Document Word Counter
===================================
 A thread for counting words and characters in a document

 File History:
 Created: 2019-04-22 [0.0.1]

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

from PyQt5.QtCore import QThread

from nw.core.tools import countWords

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
        """Overloaded run function for the word counter, forwarding the
        call to the function that does the actual counting.
        """
        theText = self.theParent.getText()
        cC, wC, pC = countWords(theText)

        self.charCount = cC
        self.wordCount = wC
        self.paraCount = pC

        return

## END Class WordCounter
