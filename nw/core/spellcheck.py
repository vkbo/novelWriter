# -*- coding: utf-8 -*-
"""novelWriter Spell Check Wrapper

 novelWriter – Spell Check Wrapper
===================================
 Wrapper class for spell checking

 File History:
 Created: 2019-06-11 [0.1.5]

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

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

import nw
import logging
import os

from difflib import get_close_matches

from nw.constants import isoLanguage

logger = logging.getLogger(__name__)

# =============================================================================================== #
#  SpellChecking SuperClass
# =============================================================================================== #

class NWSpellCheck():

    SP_INTERNAL = "internal"
    SP_ENCHANT  = "enchant"

    theDict = None
    PROJW = []

    def __init__(self):
        self.mainConf = nw.CONFIG
        self.projectDict = None
        self.spellLanguage = None
        return

    def setLanguage(self, theLang, projectDict=None):
        """Dummy function.
        """
        return

    def checkWord(self, theWord):
        """Dummy function.
        """
        return True

    def suggestWords(self, theWord):
        """Dummy function.
        """
        return []

    def addWord(self, newWord):
        """Add a word to the project dictionary.
        """
        if self.projectDict is not None and newWord not in self.PROJW:
            newWord = newWord.strip()
            self.PROJW.append(newWord)
            try:
                with open(self.projectDict, mode="a+", encoding="utf-8") as outFile:
                    outFile.write("%s\n" % newWord)
            except Exception as e:
                logger.error("Failed to add word to project word list %s" % str(self.projectDict))
                logger.error(str(e))
        return

    def listDictionaries(self):
        """Dummy function.
        """
        return []

    def describeDict(self):
        """Dummy function.
        """
        return "", ""

    @staticmethod
    def expandLanguage(spTag):
        """Translate a language tag to something more user friendly.
        """
        spBits = spTag.split("_")
        spLang = isoLanguage.ISO_639_1.get(spBits[0], spBits[0])
        if len(spBits) > 1:
            spLang += " (%s)" % spBits[1]
        return spLang

    ##
    #  Internal Functions
    ##

    def _readProjectDictionary(self, projectDict):
        """Read the content of the project dictionary, and add it to the
        lookup lists.
        """
        self.PROJW = []
        if projectDict is not None:
            self.projectDict = projectDict
            if not os.path.isfile(projectDict):
                return
            try:
                logger.debug("Loading project word list")
                with open(projectDict, mode="r", encoding="utf-8") as wordsFile:
                    for theLine in wordsFile:
                        theLine = theLine.strip()
                        if len(theLine) > 0 and theLine not in self.PROJW:
                            self.PROJW.append(theLine)
                logger.debug("Project word list contains %d words" % len(self.PROJW))
            except Exception as e:
                logger.error("Failed to load project word list")
                logger.error(str(e))
        return

# END Class NWSpellCheck

# =============================================================================================== #
#  Enchant Based SpellChecking
# =============================================================================================== #

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
            import enchant
            self.theDict = enchant.Dict(theLang)
            self.spellLanguage = theLang
            logger.debug("Enchant spell checking for language %s loaded" % theLang)
        except Exception:
            logger.error("Failed to load enchant spell checking for language %s" % theLang)
            self.theDict = NWSpellEnchantDummy()
            self.spellLanguage = None

        self._readProjectDictionary(projectDict)
        for pWord in self.PROJW:
            self.theDict.add_to_session(pWord)

        return

    def checkWord(self, theWord):
        """Wrapper function for pyenchant.
        """
        return self.theDict.check(theWord)

    def suggestWords(self, theWord):
        """Wrapper function for pyenchant.
        """
        return self.theDict.suggest(theWord)

    def addWord(self, newWord):
        """Wrapper function for pyenchant.
        """
        self.theDict.add_to_session(newWord)
        NWSpellCheck.addWord(self, newWord)
        return

    def listDictionaries(self):
        """Wrapper function for pyenchant.
        """
        retList = []
        try:
            import enchant
            for spTag, spProvider in enchant.list_dicts():
                spName = "%s [%s]" % (self.expandLanguage(spTag), spProvider.name)
                retList.append((spTag, spName))
        except Exception:
            logger.error("Failed to list languages for enchant spell checking")
        return retList

    def describeDict(self):
        """Return the tag and provider of the currently loaded
        dictionary.
        """
        try:
            spTag = self.theDict.tag
            spName = self.theDict.provider.name
        except Exception as e:
            logger.error("Failed to extract information about the dictionary")
            logger.error(str(e))
            spTag = ""
            spName = ""

        return spTag, spName

# END Class NWSpellEnchant

class NWSpellEnchantDummy:
    """Fallback for when Enchant is selected, but not installed.
    """
    def __init__(self):
        return

    def check(self, theWord):
        return True

    def suggest(self, theWord):
        return []

    def add_to_session(self, theWord):
        return

# END Class NWSpellEnchantDummy

# =============================================================================================== #
#  Fallback SpellChecking Using difflib
# =============================================================================================== #

class NWSpellSimple(NWSpellCheck):
    """Internal spell check tool that uses standard Python packages with
    no other external dependencies. This is the fallback spell checker
    when no other is available. This method is fairly slow compared to
    other implementations.
    """

    WORDS = []

    def __init__(self):
        NWSpellCheck.__init__(self)
        self.theLang = ""
        logger.debug("Simple spell checking activated")
        return

    def setLanguage(self, theLang, projectDict=None):
        """Load a dictionary as a list from the app assets folder.
        """
        self.theLang = theLang
        self.WORDS = []
        dictFile = os.path.join(self.mainConf.dictPath, theLang+".dict")
        try:
            with open(dictFile, mode="r", encoding="utf-8") as wordsFile:
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
        theWord = theWord.replace(self.mainConf.fmtApostrophe, "'").lower()
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

        theMatches = get_close_matches(theWord.lower(), self.WORDS, n=10, cutoff=0.75)
        theOptions = []
        for aWord in theMatches:
            if len(aWord) == 0:
                continue
            if theWord[0].isupper():
                aWord = aWord[0].upper() + aWord[1:]
            aWord = aWord.replace("'", self.mainConf.fmtApostrophe)
            theOptions.append(aWord)

        return theOptions

    def addWord(self, newWord):
        """Wrapper for the internal project dictionary feature.
        """
        newWord = newWord.strip().lower()
        if newWord not in self.WORDS:
            self.WORDS.append(newWord)
        NWSpellCheck.addWord(self, newWord)
        return

    def listDictionaries(self):
        """Lists the dictionary files in the app assets folder.
        """
        retList = []
        for dictFile in os.listdir(self.mainConf.dictPath):

            theBits = os.path.splitext(dictFile)
            if len(theBits) != 2:
                continue
            if theBits[1] != ".dict":
                continue

            spName = "%s [internal]" % self.expandLanguage(theBits[0])
            retList.append((theBits[0], spName))

        return retList

    def describeDict(self):
        """Return the tag and provider of the currently loaded
        dictionary.
        """
        return self.theLang, "internal"

# END Class NWSpellSimple
