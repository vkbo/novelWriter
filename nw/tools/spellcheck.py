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

from os import path

from nw.constants import isoLanguage

logger = logging.getLogger(__name__)

class NWSpellCheck():

    SP_INTERNAL = "internal"
    SP_ENCHANT  = "enchant"
    SP_SYMSPELL = "symspell"

    theDict = None
    PROJW = []

    def __init__(self):
        self.mainConf = nw.CONFIG
        self.projectDict = None
        self.spellLanguage = None
        return

    def setLanguage(self, theLang, projectDict=None):
        return

    def checkWord(self, theWord):
        return True

    def suggestWords(self, theWord):
        return []

    def addWord(self, newWord):
        if self.projectDict is not None and newWord not in self.PROJW:
            newWord = newWord.strip()
            self.PROJW.append(newWord)
            try:
                with open(self.projectDict,mode="a+",encoding="utf-8") as outFile:
                    outFile.write("%s\n" % newWord)
            except Exception as e:
                logger.error("Failed to add word to project word list %s" % str(self.projectDict))
                logger.error(str(e))
        return

    def listDictionaries(self):
        return []

    @staticmethod
    def expandLanguage(spTag):
        spBits = spTag.split("_")
        if spBits[0] in isoLanguage.ISO_639_1:
            spLang = isoLanguage.ISO_639_1[spBits[0]]
        else:
            spLang = spBits[0]
        if len(spBits) > 1:
            spLang += " (%s)" % spBits[1]
        return spLang

    ##
    #  Internal Functions
    ##

    def _readProjectDictionary(self, projectDict):
        self.PROJW = []
        if projectDict is not None:
            self.projectDict = projectDict
            if not path.isfile(projectDict):
                return
            try:
                with open(projectDict,mode="r",encoding="utf-8") as wordsFile:
                    for theLine in wordsFile:
                        theLine = theLine.strip()
                        if len(theLine) > 0 and theLine not in self.PROJW:
                            self.PROJW.append(theLine)
                logger.debug("Project word list")
                logger.debug("Project word list contains %d words" % len(self.PROJW))
            except Exception as e:
                logger.error("Failed to load project word list")
                logger.error(str(e))
        return

# END Class NWSpellCheck
