"""
novelWriter – Spell Check Classes
=================================
Wrapper classes for spell checking tools

File History:
Created: 2019-06-11 [0.1.5]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import logging

from collections import namedtuple
from pathlib import Path

from novelwriter.error import logException

logger = logging.getLogger(__name__)


class NWSpellEnchant:

    def __init__(self):

        self._theDict = None
        self._projDict = set()
        self._projectDict = None
        self._spellLanguage = None
        self._theBroker = None

        logger.debug("Enchant spell checking activated")

        return

    ##
    #  Properties
    ##

    @property
    def spellLanguage(self):
        return self._spellLanguage

    ##
    #  Setters
    ##

    def setLanguage(self, theLang, projectDict=None):
        """Load a dictionary for the language specified in the config.
        If that fails, we load a mock dictionary so that lookups don't
        crash. Note that enchant will allow loading an empty string as
        a tag, but this will fail later on. See issue #1096.
        """
        self._theBroker = None
        self._theDict = None
        self._spellLanguage = None

        try:
            import enchant

            if theLang and enchant.dict_exists(theLang):
                self._theBroker = enchant.Broker()
                self._theDict = self._theBroker.request_dict(theLang)
                self._spellLanguage = theLang
                logger.debug("Enchant spell checking for language '%s' loaded", theLang)
            else:
                logger.warning("Enchant found no dictionary for language '%s'", theLang)

        except Exception:
            logger.error("Failed to load enchant spell checking for language '%s'", theLang)

        if self._theDict is None:
            self._theDict = FakeEnchant()
        else:
            self._readProjectDictionary(projectDict)
            for pWord in self._projDict:
                self._theDict.add_to_session(pWord)

        return

    ##
    #  Methods
    ##

    def checkWord(self, theWord):
        """Wrapper function for pyenchant.
        """
        try:
            return self._theDict.check(theWord)
        except Exception:
            return True

    def suggestWords(self, theWord):
        """Wrapper function for pyenchant.
        """
        try:
            return self._theDict.suggest(theWord)
        except Exception:
            return []

    def addWord(self, newWord):
        """Add a word to the project dictionary.
        """
        try:
            self._theDict.add_to_session(newWord)
        except Exception:
            return False

        if self._projectDict is not None and newWord not in self._projDict:
            newWord = newWord.strip()
            try:
                with open(self._projectDict, mode="a+", encoding="utf-8") as outFile:
                    outFile.write("%s\n" % newWord)
                self._projDict.add(newWord)
            except Exception:
                logger.error("Failed to add word to project word list %s", str(self._projectDict))
                logException()
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
            spTag = self._theDict.tag
            spName = self._theDict.provider.name
        except Exception:
            logger.error("Failed to extract information about the dictionary")
            logException()
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
        self._projDict = set()
        self._projectDict = projectDict

        if not isinstance(projectDict, Path):
            return False

        if not projectDict.exists():
            return False

        try:
            logger.debug("Loading project word list")
            with open(projectDict, mode="r", encoding="utf-8") as wordsFile:
                for theLine in wordsFile:
                    theLine = theLine.strip()
                    if len(theLine) > 0 and theLine not in self._projDict:
                        self._projDict.add(theLine)
            logger.debug("Project word list contains %d words", len(self._projDict))

        except Exception:
            logger.error("Failed to load project word list")
            logException()
            return False

        return True

# END Class NWSpellEnchant


class FakeEnchant:
    """Fallback for when Enchant is selected, but not installed.
    """
    def __init__(self):
        self.tag = ""
        self.provider = namedtuple("provider", "name")
        self.provider.name = ""
        return

    def check(self, theWord):
        return True

    def suggest(self, theWord):
        return []

    def add_to_session(self, theWord):
        return

# END Class FakeEnchant
