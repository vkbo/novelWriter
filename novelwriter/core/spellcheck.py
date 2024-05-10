"""
novelWriter – Spell Check Classes
=================================

File History:
Created: 2019-06-11 [0.1.5] NWSpellEnchant
Created: 2023-06-13 [2.1b1] UserDictionary

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt5.QtCore import QLocale

from novelwriter.constants import nwFiles
from novelwriter.error import logException

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)


class NWSpellEnchant:
    """Core: Enchant Spell Checking Wrapper

    This is a rapper class for Enchant to keep the API consistent
    between spell check tools.
    """

    def __init__(self, project: NWProject) -> None:
        self._project = project
        self._enchant = FakeEnchant()
        self._userDict = UserDictionary(project)
        self._language = None
        self._broker = None
        logger.debug("Ready: NWSpellEnchant")
        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: NWSpellEnchant")
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

    def setLanguage(self, language: str | None) -> None:
        """Load a dictionary for the language specified in the config.
        If that fails, we load a mock dictionary so that lookups don't
        crash. Note that enchant will allow loading an empty string as
        a tag, but this will fail later on. See issue #1096.
        """
        self._enchant = FakeEnchant()
        self._broker = None
        self._language = None

        try:
            import enchant

            if language and enchant.dict_exists(language):
                self._broker = enchant.Broker()
                self._enchant = self._broker.request_dict(language)
                self._language = language
                logger.debug("Enchant spell checking for language '%s' loaded", language)
            else:
                logger.warning("Enchant found no dictionary for language '%s'", language)

        except Exception:
            logger.error("Failed to load enchant spell checking for language '%s'", language)

        if self._enchant is None:
            self._enchant = FakeEnchant()
        else:
            self._userDict.load()
            for word in self._userDict:
                self._enchant.add_to_session(word)

        return

    ##
    #  Methods
    ##

    def checkWord(self, word: str) -> bool:
        """Wrapper function for pyenchant."""
        try:
            return bool(self._enchant.check(word))
        except Exception:
            return True

    def suggestWords(self, word: str) -> list[str]:
        """Wrapper function for pyenchant."""
        try:
            return self._enchant.suggest(word)
        except Exception:
            return []

    def addWord(self, word: str) -> bool:
        """Add a word to the project dictionary."""
        word = word.strip()
        if not word:
            return False
        try:
            self._enchant.add_to_session(word)
        except Exception:
            return False

        added = self._userDict.add(word)
        if added:
            self._userDict.save()

        return added

    def listDictionaries(self) -> list[tuple[str, str]]:
        """List available dictionaries."""
        lang = []
        try:
            import enchant
            tags = [x for x, _ in enchant.list_dicts()]
            lang = [(x, f"{QLocale(x).nativeLanguageName().title()} [{x}]") for x in set(tags)]
        except Exception:
            logger.error("Failed to list languages for enchant spell checking")
        return sorted(lang, key=lambda x: x[1])

    def describeDict(self) -> tuple[str, str]:
        """Describe the currently loaded dictionary."""
        try:
            tag = self._enchant.tag
            name = self._enchant.provider.name  # type: ignore
        except Exception:
            logger.error("Failed to extract information about the dictionary")
            logException()
            tag = ""
            name = ""
        return tag, name


class FakeEnchant:
    """Fallback for when Enchant is selected, but not installed."""

    def __init__(self) -> None:

        class FakeProvider:
            name = ""

        self.tag = ""
        self.provider = FakeProvider()

        return

    def check(self, word: str) -> bool:
        return True

    def suggest(self, word: str) -> list[str]:
        return []

    def add_to_session(self, word: str) -> None:
        return


class UserDictionary:

    def __init__(self, project: NWProject) -> None:
        self._project = project
        self._words = set()
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

    def load(self) -> None:
        """Load the user's dictionary."""
        self._words = set()
        wordList = self._project.storage.getMetaFile(nwFiles.DICT_FILE)
        if isinstance(wordList, Path) and wordList.is_file():
            try:
                with open(wordList, mode="r", encoding="utf-8") as fObj:
                    data = json.load(fObj)
                self._words = set(data.get("novelWriter.userDict", []))
                logger.info("Loaded: %s", nwFiles.DICT_FILE)
            except Exception:
                logger.error("Failed to load user dictionary")
                logException()
        return

    def save(self) -> None:
        """Save the user's dictionary."""
        wordList = self._project.storage.getMetaFile(nwFiles.DICT_FILE)
        if isinstance(wordList, Path):
            try:
                with open(wordList, mode="w", encoding="utf-8") as fObj:
                    data = {"novelWriter.userDict": list(self._words)}
                    json.dump(data, fObj, indent=2)
            except Exception:
                logger.error("Failed to save user dictionary")
                logException()
        return
