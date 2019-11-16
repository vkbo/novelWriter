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
        """Load a dictionary for the language specified in the config.
        If that fails, we load a dummy dictionary so that lookups don't
        crash.
        """
        try:
            self.theDict = enchant.Dict(theLang)
            self.spellLanguage = theLang
            logger.debug("Enchant spell checking for language %s loaded" % theLang)
        except:
            logger.error("Failed to load enchant spell checking for language %s" % theLang)
            self.theDict = NWSpellEnchantDummy()
            self.spellLanguage = None

        self._readProjectDictionary(projectDict)
        for pWord in self.PROJW:
            self.theDict.add_to_session(pWord)

        return

    def checkWord(self, theWord):
        return self.theDict.check(theWord)

    def suggestWords(self, theWord):
        return self.theDict.suggest(theWord)

    def addWord(self, newWord):
        self.theDict.add_to_session(newWord)
        NWSpellCheck.addWord(self, newWord)
        return

    def listDictionaries(self):
        retList = []
        for spTag, spProvider in enchant.list_dicts():
            spName = "%s [%s]" % (self.expandLanguage(spTag), spProvider.name)
            retList.append((spTag, spName))
        return retList

# END Class NWSpellEnchant

class NWSpellEnchantDummy:

    def __init__(self):
        return
    
    def check(self, theWord):
        return True

    def suggest(self, theWord):
        return []

    def add_to_session(self, theWord):
        return

# END Class NWSpellEnchantDummy
