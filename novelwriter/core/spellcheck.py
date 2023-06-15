"""
novelWriter – Spell Check Classes
=================================

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
from __future__ import annotations

import json
import logging

from typing import TYPE_CHECKING, Iterator
from pathlib import Path

from novelwriter.error import logException
from novelwriter.constants import nwFiles

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)


class NWSpellEnchant:
    """Core: Enchant Spell Checking Wrapper

    This is a rapper class for Enchant to keep the API consistent
    between spell check tools.
    """

    def __init__(self, project: NWProject):
        self._project = project
        self._dictObj = FakeEnchant()
        self._userDict = UserDictionary(project)
        self._language = None
        self._broker = None
        logger.debug("Enchant spell checking activated")
        return

    ##
    #  Properties
    ##

    @property
    def spellLanguage(self) -> str | None:
        return self._language

    ##
    #  Setters
    ##

    def setLanguage(self, language: str | None):
        """Load a dictionary for the language specified in the config.
        If that fails, we load a mock dictionary so that lookups don't
        crash. Note that enchant will allow loading an empty string as
        a tag, but this will fail later on. See issue #1096.
        """
        self._dictObj = FakeEnchant()
        self._broker = None
        self._language = None

        try:
            import enchant

            if language and enchant.dict_exists(language):
                self._broker = enchant.Broker()
                self._dictObj = self._broker.request_dict(language)
                self._language = language
                logger.debug("Enchant spell checking for language '%s' loaded", language)
            else:
                logger.warning("Enchant found no dictionary for language '%s'", language)

        except Exception:
            logger.error("Failed to load enchant spell checking for language '%s'", language)

        if self._dictObj is None:
            self._dictObj = FakeEnchant()
        else:
            self._userDict.load()
            for pWord in self._userDict:
                self._dictObj.add_to_session(pWord)

        return

    ##
    #  Methods
    ##

    def checkWord(self, word: str) -> bool:
        """Wrapper function for pyenchant."""
        try:
            return bool(self._dictObj.check(word))
        except Exception:
            return True

    def suggestWords(self, word: str) -> list[str]:
        """Wrapper function for pyenchant."""
        try:
            return self._dictObj.suggest(word)
        except Exception:
            return []

    def addWord(self, word: str) -> bool:
        """Add a word to the project dictionary."""
        word = word.strip()
        if not word:
            return False
        try:
            self._dictObj.add_to_session(word)
        except Exception:
            return False

        added = self._userDict.add(word)
        if added:
            self._userDict.save()

        return added

    def listDictionaries(self) -> list[tuple[str, str]]:
        """Wrapper function for pyenchant."""
        retList = []
        try:
            import enchant
            for spTag, spProvider in enchant.list_dicts():
                retList.append((spTag, spProvider.name))
        except Exception:
            logger.error("Failed to list languages for enchant spell checking")

        return retList

    def describeDict(self) -> tuple[str, str]:
        """Return the tag and provider of the currently loaded
        dictionary.
        """
        try:
            tag = self._dictObj.tag
            name = self._dictObj.provider.name  # type: ignore
        except Exception:
            logger.error("Failed to extract information about the dictionary")
            logException()
            tag = ""
            name = ""

        return tag, name

# END Class NWSpellEnchant


class FakeEnchant:
    """Fallback for when Enchant is selected, but not installed."""
    def __init__(self):

        class FakeProvider:
            name = ""

        self.tag = ""
        self.provider = FakeProvider()

        return

    def check(self, word: str) -> bool:
        return True

    def suggest(self, word) -> list[str]:
        return []

    def add_to_session(self, word: str):
        return

# END Class FakeEnchant


class UserDictionary:

    def __init__(self, project: NWProject):
        self._project = project
        self._words = set()
        self._path = None
        return

    def __contains__(self, word: str) -> bool:
        return word in self._words

    def __iter__(self) -> Iterator[str]:
        return iter(self._words)

    def add(self, word: str) -> bool:
        """Add a word to the dictionary, and return True if it was
        added, or False if it already existed.
        """
        if word in self._words:
            return False
        self._words.add(word)
        return True

    def load(self):
        """Load the user's dictionary."""
        self._path = self._project.storage.getMetaFile(nwFiles.DICT_FILE)
        if not isinstance(self._path, Path):
            return
        try:
            with open(self._path, mode="r", encoding="utf-8") as fObj:
                data = json.load(fObj)
            self._words = set(data.get("novelWriter.userDict", []))
        except Exception:
            logger.error("Failed to load user dictionary")
            logException()
        return

    def save(self):
        """Save the user's dictionary."""
        if self._path is None:
            self._path = self._project.storage.getMetaFile(nwFiles.DICT_FILE)
        if not isinstance(self._path, Path):
            return
        try:
            with open(self._path, mode="w", encoding="utf-8") as fObj:
                data = {"novelWriter.userDict": list(self._words)}
                json.dump(data, fObj, indent=2)
        except Exception:
            logger.error("Failed to save user dictionary")
            logException()
        return

# END Class UserDictionary
