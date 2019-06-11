# -*- coding: utf-8 -*-
"""novelWriter Spell Check Wrapper : pyEnchant

 novelWriter – Spell Check Wrapper : pyEnchant
===============================================
 Wrapper class for spell checking with pyEnchant

 File History:
 Created: 2019-06-11 [0.1.5]

"""

import logging
import enchant
import nw

from nw.tools.spellcheck import NWSpellCheck

logger = logging.getLogger(__name__)

class NWSpellEnchant(NWSpellCheck):

    def __init__(self):
        NWSpellCheck.__init__(self)
        logger.debug("Enchant spell checking activated")
        return

    def setLanguage(self, theLang, projectDict=None):
        if projectDict is None:
            self.theDict = enchant.Dict(theLang)
        else:
            self.theDict = enchant.DictWithPWL(theLang, projectDict)
        logger.debug("Enchant spell checking for %s loaded" % theLang)
        return

    def checkWord(self, theWord):
        return self.theDict.check(theWord)

    def suggestWords(self, theWord):
        return self.theDict.suggest(theWord)

    def addWord(self, newWord):
        self.theDict.add_to_pwl(newWord)
        return

    def listDictionaries(self):
        retList = []
        for spTag, spProvider in enchant.list_dicts():
            retList.append((spTag, "%s [%s]" % (spTag, spProvider.name)))
        return retList

# END Class NWSpellEnchant
