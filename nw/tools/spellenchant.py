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

try:
    import pycountry
    hasPyCountry = True
except:
    hasPyCountry = False

from nw.tools.spellcheck import NWSpellCheck

logger = logging.getLogger(__name__)

class NWSpellEnchant(NWSpellCheck):

    def __init__(self):
        NWSpellCheck.__init__(self)
        logger.debug("Enchant spell checking activated")
        return

    def setLanguage(self, theLang, projectDict=None):
        """Load a dictionary for the language specified in the config. If that fails, we load a
        dummy dictionary so that lookups don't crash.
        """
        try:
            if projectDict is None:
                self.theDict = enchant.Dict(theLang)
            else:
                self.theDict = enchant.DictWithPWL(theLang, projectDict)
            logger.debug("Enchant spell checking for language %s loaded" % theLang)
        except:
            logger.error("Failed to load enchant spell checking for language %s" % theLang)
            self.theDict = NWSpellEnchantDummy()

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
            if hasPyCountry:
                spList  = []
                try:
                    langObj = pycountry.languages.get(alpha_2 = spTag[:2])
                    spList.append(langObj.name)
                except:
                    spList.append(spTag[:2])
                if len(spTag) > 3:
                    spList.append("(%s)" % spTag[3:])
                spList.append("[%s]" % spProvider.name)
                spName = " ".join(spList)
            else:
                spName = "%s [%s]" % (spTag, spProvider.name)
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

    def add_to_pwl(self, theWord):
        return

# END Class NWSpellEnchantDummy
