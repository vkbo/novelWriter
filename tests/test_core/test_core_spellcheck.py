"""
novelWriter – Spell Check Classes Tester
========================================

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

import sys
import pytest

from mocked import causeOSError
from tools import readFile, writeFile

from novelwriter.core.spellcheck import FakeEnchant, NWSpellEnchant


@pytest.mark.core
def testCoreSpell_FakeEnchant(monkeypatch):
    """Test the FakeEnchant spell checker fallback.
    """
    # Make package import fail
    with monkeypatch.context() as mp:
        mp.setitem(sys.modules, "enchant", None)
        spChk = NWSpellEnchant()
        spChk.setLanguage("en_US", "")
        assert isinstance(spChk._theDict, FakeEnchant)

    # Request a non-existent dictionary
    spChk = NWSpellEnchant()
    spChk.setLanguage("whatchamajig", "")
    assert isinstance(spChk._theDict, FakeEnchant)

    # Request an emety language string
    # See issue https://github.com/vkbo/novelWriter/issues/1096
    spChk = NWSpellEnchant()
    spChk.setLanguage("", "")
    assert isinstance(spChk._theDict, FakeEnchant)

    # FakeEnchant should handle requests
    fkChk = FakeEnchant()
    assert fkChk.tag == ""
    assert fkChk.provider.name == ""
    assert fkChk.check("whatchamajig") is True
    assert fkChk.suggest("whatchamajig") == []
    assert fkChk.add_to_session("whatchamajig") is None

# END Test testCoreSpell_FakeEnchant


@pytest.mark.core
def testCoreSpell_Enchant(monkeypatch, fncPath):
    """Test the pyenchant spell checker.
    """
    wList = fncPath / "wordlist.txt"
    writeFile(wList, "a_word\nb_word\nc_word\n")

    # Break the enchant package, and check error handling
    with monkeypatch.context() as mp:
        mp.setitem(sys.modules, "enchant", None)
        spChk = NWSpellEnchant()
        assert spChk.listDictionaries() == []
        assert spChk.describeDict() == ("", "")

    # Set the dict to None, and check dictionary call error handling
    spChk = NWSpellEnchant()
    spChk.theDict = None
    assert spChk.checkWord("word") is True
    assert spChk.suggestWords("word") == []
    assert spChk.addWord("word") is False

    # Load the proper enchant package (twice)
    spChk = NWSpellEnchant()
    spChk.setLanguage("en_US", wList)
    spChk.setLanguage("en_US", wList)
    assert spChk.spellLanguage == "en_US"

    # Add a word to the user's dictionary
    assert spChk._readProjectDictionary("stuff") is False
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert spChk._readProjectDictionary(wList) is False

    assert spChk._readProjectDictionary(None) is False
    assert spChk._readProjectDictionary(wList) is True
    assert spChk._projectDict == wList

    # Cannot write to file
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert spChk.addWord("d_word") is False

    assert readFile(wList) == "a_word\nb_word\nc_word\n"
    assert spChk.addWord("d_word") is True
    assert readFile(wList) == "a_word\nb_word\nc_word\nd_word\n"
    assert spChk.addWord("d_word") is False

    # Check words
    assert spChk.checkWord("a_word") is True
    assert spChk.checkWord("b_word") is True
    assert spChk.checkWord("c_word") is True
    assert spChk.checkWord("d_word") is True
    assert spChk.checkWord("e_word") is False

    spChk.addWord("d_word")
    assert spChk.checkWord("d_word") is True

    wSuggest = spChk.suggestWords("wrod")
    assert len(wSuggest) > 0
    assert "word" in wSuggest

    dList = spChk.listDictionaries()
    assert len(dList) > 0

    aTag, aName = spChk.describeDict()
    assert aTag == "en_US"
    assert aName != ""

# END Test testCoreSpell_Enchant


@pytest.mark.core
def testCoreSpell_SessionWords(fncPath):
    """Test the handling of the custom word list in the spell checker.
    New project sessions should not inherit the project word list from
    other sessions, so this test checks that they don't bleed through.
    """
    wList1 = fncPath / "wordlist1.txt"
    wList2 = fncPath / "wordlist2.txt"
    writeFile(wList1, "a_word\nb_word\nc_word\n")
    writeFile(wList2, "d_word\ne_word\nf_word\n")

    spChk = NWSpellEnchant()

    spChk.setLanguage("en_US", wList1)
    assert spChk.checkWord("a_word") is True
    assert spChk.checkWord("b_word") is True
    assert spChk.checkWord("c_word") is True
    assert spChk.checkWord("d_word") is False
    assert spChk.checkWord("e_word") is False
    assert spChk.checkWord("f_word") is False

    spChk.setLanguage("en_US", wList2)
    assert spChk.checkWord("a_word") is False
    assert spChk.checkWord("b_word") is False
    assert spChk.checkWord("c_word") is False
    assert spChk.checkWord("d_word") is True
    assert spChk.checkWord("e_word") is True
    assert spChk.checkWord("f_word") is True

# END Test testCoreSpell_SessionWords
