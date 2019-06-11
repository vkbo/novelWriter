# -*- coding: utf-8 -*-
"""novelWriter Spell Check Wrapper

 novelWriter – Spell Check Wrapper
===================================
 Wrapper class for spell checking

 File History:
 Created: 2019-06-11 [0.1.5]

"""

import logging
import nw

logger = logging.getLogger(__name__)

class NWSpellCheck():

    theDict = None

    def __init__(self):
        return

    def setLanguage(self, theLang, projectDict=None):
        return

    def checkWord(self, theWord):
        return True

    def suggestWords(self, theWord):
        return []

    def addWord(self, newWord):
        return

    def listDictionaries(self):
        return []

# END Class NWSpellCheck
