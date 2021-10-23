"""
novelWriter – Spell Check Classes Tester
========================================

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
import sys
import pytest

from mock import causeOSError
from tools import readFile, writeFile

from novelwriter.core.spellcheck import NWSpellEnchant


@pytest.mark.core
def testCoreSpell_Enchant(monkeypatch, tmpDir):
    """Test the pyenchant spell checker
    """
    wList = os.path.join(tmpDir, "wordlist.txt")
    writeFile(wList, "a_word\nb_word\nc_word\n")

    # Block the enchant package (and trigger the default class)
    with monkeypatch.context() as mp:
        mp.setitem(sys.modules, "enchant", None)
        spChk = NWSpellEnchant()

        spChk.setLanguage("en", wList)
        assert spChk.setLanguage("", "") is None
        assert spChk.checkWord("") is True
        assert spChk.suggestWords("") == []
        assert spChk.listDictionaries() == []
        assert spChk.describeDict() == ("", "")

    # Load the proper enchant package (twice)
    spChk = NWSpellEnchant()
    spChk.setLanguage("en", wList)
    spChk.setLanguage("en", wList)

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
    assert aTag == "en"
    assert aName != ""

# END Test testCoreSpell_Enchant
