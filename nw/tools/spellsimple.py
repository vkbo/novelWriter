# -*- coding: utf-8 -*-
"""novelWriter Spell Check Simple

 novelWriter – Spell Check Simple
==================================
 Simple Python3 spell checker based on difflib

 File History:
 Created: 2019-06-11 [0.1.5]

"""

import logging
import nw

from os import path
from collections import Counter
from difflib import get_close_matches

logger = logging.getLogger(__name__)

from nw.tools.spellcheck import NWSpellCheck

class NWSpellSimple(NWSpellCheck):

    WORDS = []

    def __init__(self):
        NWSpellCheck.__init__(self)
        self.mainConf = nw.CONFIG
        logger.debug("Norvig spell checking activated")
        return

    def setLanguage(self, theLang, projectDict=None):
        dictFile = path.join(self.mainConf.dictPath,theLang+".dict")
        try:
            with open(dictFile,mode="r",encoding="utf-8") as wordsFile:
                for theLine in wordsFile:
                    if len(theLine) == 0 or theLine.startswith("#"):
                        continue
                    self.WORDS.append(theLine.strip().lower())
            logger.debug("Spell check word list for language %s loaded" % theLang)
            logger.debug("Word list contains %d words" % len(self.WORDS))
        except Exception as e:
            logger.error("Failed to load spell check word list for language %s" % theLang)
            logger.error(str(e))
        return

    def checkWord(self, theWord):
        theWord = theWord.replace(self.mainConf.fmtSingleQuotes[1],"'").lower()
        return theWord in self.WORDS

    def suggestWords(self, theWord):
        return get_close_matches(theWord.lower(), self.WORDS, n=10, cutoff=0.60)

    def addWord(self, newWord):
        return

    def listDictionaries(self):
        return ["default"]

# END Class NWSpellSimple
