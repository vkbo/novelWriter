# -*- coding: utf-8 -*-
"""novelWriter Spell Check Simple

 novelWriter – Spell Check Simple
==================================
 Simple spell checker based on difflib

 File History:
 Created: 2019-06-11 [0.1.5]

"""

import logging
import nw

from os import path, listdir
from difflib import get_close_matches

logger = logging.getLogger(__name__)

from nw.tools.spellcheck import NWSpellCheck

class NWSpellSimple(NWSpellCheck):

    WORDS = []

    def __init__(self):
        NWSpellCheck.__init__(self)
        logger.debug("Simple spell checking activated")
        return

    def setLanguage(self, theLang, projectDict=None):

        self.WORDS = []
        dictFile = path.join(self.mainConf.dictPath,theLang+".dict")
        try:
            with open(dictFile,mode="r",encoding="utf-8") as wordsFile:
                for theLine in wordsFile:
                    if len(theLine) == 0 or theLine.startswith("#"):
                        continue
                    self.WORDS.append(theLine.strip().lower())
            logger.debug("Spell check word list for language %s loaded" % theLang)
            logger.debug("Word list contains %d words" % len(self.WORDS))
            self.spellLanguage = theLang
        except Exception as e:
            logger.error("Failed to load spell check word list for language %s" % theLang)
            logger.error(str(e))
            self.spellLanguage = None

        self._readProjectDictionary(projectDict)
        for pWord in self.PROJW:
            if pWord not in self.WORDS:
                self.WORDS.append(pWord)

        return

    def checkWord(self, theWord):
        """Check if a word exists in the word list. Make sure to keep
        this function as fast as possible as it is called for every
        word by the syntax highlighter.
        """
        theWord = theWord.replace(self.mainConf.fmtApostrophe,"'").lower()
        return theWord in self.WORDS

    def suggestWords(self, theWord):
        """Get suggestions for correct word from difflib, and make sure
        the first character is upper case if that was also the case for
        the word be3ing checked. Also make sure the apostrophe is
        changed to the one in the dictionary, and then put back in the
        results.
        """
        theWord = theWord.strip()
        if len(theWord) == 0:
            return []

        firstUp = theWord[0] == theWord[0].upper()
        theWord = theWord.lower()

        theMatches = get_close_matches(theWord, self.WORDS, n=10, cutoff=0.75)
        theOptions = []
        for aWord in theMatches:
            if len(aWord) == 0:
                continue
            if firstUp:
                aWord = aWord[0].upper() + aWord[1:]
            aWord = aWord.replace("'",self.mainConf.fmtApostrophe)
            theOptions.append(aWord)

        return theOptions

    def addWord(self, newWord):
        newWord = newWord.strip().lower()
        if newWord not in self.WORDS:
            self.WORDS.append(newWord)
        NWSpellCheck.addWord(self, newWord)
        return

    def listDictionaries(self):

        retList = []
        for dictFile in listdir(self.mainConf.dictPath):

            theBits = path.splitext(dictFile)
            if len(theBits) != 2:
                continue
            if theBits[1] != ".dict":
                continue

            spName = "%s [Internal]" % self.expandLanguage(theBits[0])
            retList.append((theBits[0], spName))

        return retList

# END Class NWSpellSimple
