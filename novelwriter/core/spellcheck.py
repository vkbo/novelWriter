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

import os
import logging
import novelwriter

logger = logging.getLogger(__name__)


class NWSpellEnchant():

    def __init__(self):

        self.mainConf = novelwriter.CONFIG
        self.theDict = None
        self.projDict = set()
        self.projectDict = None
        self.spellLanguage = None
        self.theBroker = None

        logger.debug("Enchant spell checking activated")

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
        try:
            return self.theDict.check(theWord)
        except Exception:
            return True

    def suggestWords(self, theWord):
        """Wrapper function for pyenchant.
        """
        try:
            return self.theDict.suggest(theWord)
        except Exception:
            return []

    def addWord(self, newWord):
        """Add a word to the project dictionary.
        """
        try:
            self.theDict.add_to_session(newWord)
        except Exception:
            return False

        if self.projectDict is not None and newWord not in self.projDict:
            newWord = newWord.strip()
            try:
                with open(self.projectDict, mode="a+", encoding="utf-8") as outFile:
                    outFile.write("%s\n" % newWord)
                self.projDict.add(newWord)
            except Exception:
                logger.error("Failed to add word to project word list %s", str(self.projectDict))
                novelwriter.logException()
                return False
            return True

        return False

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
            novelwriter.logException()
            spTag = ""
            spName = ""

        return spTag, spName

    ##
    #  Internal Functions
    ##

    def _readProjectDictionary(self, projectDict):
        """Read the content of the project dictionary, and add it to the
        lookup lists.
        """
        self.projDict = set()
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
                        self.projDict.add(theLine)
            logger.debug("Project word list contains %d words", len(self.projDict))

        except Exception:
            logger.error("Failed to load project word list")
            novelwriter.logException()
            return False

        return True

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
