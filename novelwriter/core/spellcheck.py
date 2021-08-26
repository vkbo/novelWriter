"""
novelWriter – Spell Check Classes
=================================
Wrapper classes for spell checking tools

File History:
Created: 2019-06-11 [0.1.5]

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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
import difflib

logger = logging.getLogger(__name__)


# =============================================================================================== #
#  SpellChecking SuperClass
# =============================================================================================== #

class NWSpellCheck():

    theDict = None
    projDict = []

    def __init__(self):
        self.mainConf = nw.CONFIG
        self.projectDict = None
        self.spellLanguage = None
        return

    def setLanguage(self, theLang, projectDict=None):
        """Default function.
        """
        return

    def checkWord(self, theWord):
        """Default function.
        """
        return True

    def suggestWords(self, theWord):
        """Default function.
        """
        return []

    def addWord(self, newWord):
        """Add a word to the project dictionary.
        """
        if self.projectDict is not None and newWord not in self.projDict:
            newWord = newWord.strip()
            try:
                with open(self.projectDict, mode="a+", encoding="utf-8") as outFile:
                    outFile.write("%s\n" % newWord)
                self.projDict.append(newWord)
            except Exception:
                logger.error("Failed to add word to project word list %s", str(self.projectDict))
                nw.logException()
                return False
            return True
        return False

    def listDictionaries(self):
        """Default function.
        """
        return []

    def describeDict(self):
        """Default function.
        """
        return "", ""

    ##
    #  Internal Functions
    ##

    def _readProjectDictionary(self, projectDict):
        """Read the content of the project dictionary, and add it to the
        lookup lists.
        """
        self.projDict = []
        self.projectDict = projectDict

        if projectDict is None:
            return False

        if not os.path.isfile(projectDict):
            return False

        try:
            logger.debug("Loading project word list")
            with open(projectDict, mode="r", encoding="utf-8") as wordsFile:
                for theLine in wordsFile:
                    theLine = theLine.strip()
                    if len(theLine) > 0 and theLine not in self.projDict:
                        self.projDict.append(theLine)
            logger.debug("Project word list contains %d words", len(self.projDict))

        except Exception:
            logger.error("Failed to load project word list")
            nw.logException()
            return False

        return True

# END Class NWSpellCheck


# =============================================================================================== #
#  Enchant Based SpellChecking
# =============================================================================================== #

class NWSpellEnchant(NWSpellCheck):

    def __init__(self):
        NWSpellCheck.__init__(self)
        logger.debug("Enchant spell checking activated")
        self.theBroker = None
        return

    def setLanguage(self, theLang, projectDict=None):
        """Load a dictionary for the language specified in the config.
        If that fails, we load a mock dictionary so that lookups don't
        crash.
        """
        try:
            import enchant
            if self.theBroker is not None:
                logger.debug("Deleting old pyenchant broker")
                del self.theBroker

            self.theBroker = enchant.Broker()
            self.theDict = self.theBroker.request_dict(theLang)
            self.spellLanguage = theLang
            logger.debug("Enchant spell checking for language '%s' loaded", theLang)

        except Exception:
            logger.error("Failed to load enchant spell checking for language '%s'", theLang)
            self.theDict = FakeEnchant()
            self.spellLanguage = None

        self._readProjectDictionary(projectDict)
        for pWord in self.projDict:
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
                retList.append((spTag, spProvider.name))
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
        except Exception:
            logger.error("Failed to extract information about the dictionary")
            nw.logException()
            spTag = ""
            spName = ""

        return spTag, spName

# END Class NWSpellEnchant


class FakeEnchant:
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

# END Class FakeEnchant


# =============================================================================================== #
#  Fallback SpellChecking Using difflib
# =============================================================================================== #

class NWSpellSimple(NWSpellCheck):
    """Internal spell check tool that uses standard Python packages with
    no other external dependencies. This is the fallback spell checker
    when no other is available. This method is slower than enchant.
    """
    theWords = set()

    def __init__(self):
        NWSpellCheck.__init__(self)
        self.theLang = ""
        logger.debug("Simple spell checking activated")
        return

    def setLanguage(self, theLang, projectDict=None):
        """Load a dictionary as a list from the app assets folder.
        """
        self.theLang = theLang
        self.theWords = set()
        dictFile = os.path.join(self.mainConf.dictPath, theLang+".dict")
        try:
            with open(dictFile, mode="r", encoding="utf-8") as wordsFile:
                for theLine in wordsFile:
                    if len(theLine) == 0 or theLine.startswith("#"):
                        continue
                    self.theWords.add(theLine.strip().lower())

            logger.debug("Spell check dictionary for language '%s' loaded", theLang)
            logger.debug("Dictionary contains %d words", len(self.theWords))
            self.spellLanguage = theLang

        except Exception:
            logger.error("Failed to load spell check word list for language '%s'", theLang)
            nw.logException()
            self.spellLanguage = None

        self._readProjectDictionary(projectDict)
        for pWord in self.projDict:
            self.theWords.add(pWord)

        return

    def checkWord(self, theWord):
        """Check if a word exists in the word list. Make sure to keep
        this function as fast as possible as it is called for every
        word by the syntax highlighter.
        """
        theWord = theWord.replace(self.mainConf.fmtApostrophe, "'").lower()
        return theWord in self.theWords

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

        theMatches = difflib.get_close_matches(theWord.lower(), self.theWords, n=10, cutoff=0.75)
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
        if newWord not in self.theWords:
            self.theWords.add(newWord)
        NWSpellCheck.addWord(self, newWord)
        return

    def listDictionaries(self):
        """Lists the dictionary files in the app assets folder.
        """
        retList = []
        for dictFile in os.listdir(self.mainConf.dictPath):

            fRoot, fExt = os.path.splitext(dictFile)
            if fExt != ".dict":
                continue

            retList.append((fRoot, "difflib"))

        return retList

    def describeDict(self):
        """Return the tag and provider of the currently loaded
        dictionary.
        """
        return self.theLang, ""

# END Class NWSpellSimple
