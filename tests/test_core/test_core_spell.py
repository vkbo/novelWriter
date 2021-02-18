# -*- coding: utf-8 -*-
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

from dummy import causeOSError
from tools import readFile, writeFile

from nw.core.spellcheck import NWSpellCheck, NWSpellEnchant, NWSpellSimple

@pytest.mark.core
def testCoreSpell_Super(monkeypatch, tmpDir):
    """Test the spell checker super class
    """
    wList = os.path.join(tmpDir, "wordlist.txt")
    writeFile(wList, "a_word\nb_word\nc_word\n")

    spChk = NWSpellCheck()

    # Check that dummy functions return results that reflects that spell
    # checking is effectively disabled
    assert spChk.setLanguage("", "") is None
    assert spChk.checkWord("")
    assert spChk.suggestWords("") == []
    assert spChk.listDictionaries() == []
    assert spChk.describeDict() == ("", "")

    # Add a word to the user's dictionary
    assert spChk._readProjectDictionary("dummy") is False
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert spChk._readProjectDictionary(wList) is False
    assert spChk._readProjectDictionary(wList) is True
    assert spChk.projectDict == wList

    # Cannot write to file
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert spChk.addWord("d_word") is False
    assert readFile(wList) == "a_word\nb_word\nc_word\n"

    # First time, OK
    assert spChk.addWord("d_word") is True
    assert readFile(wList) == "a_word\nb_word\nc_word\nd_word\n"

    # But not added twice
    assert spChk.addWord("d_word") is False
    assert readFile(wList) == "a_word\nb_word\nc_word\nd_word\n"

# END Test testCoreSpell_Super

@pytest.mark.core
def testCoreSpell_Enchant(monkeypatch, tmpDir):
    """Test the pyenchant spell checker
    """
    wList = os.path.join(tmpDir, "wordlist.txt")
    writeFile(wList, "a_word\nb_word\nc_word\n")

    # Block the enchant package (and trigger the dummy class)
    with monkeypatch.context() as mp:
        mp.setitem(sys.modules, "enchant", None)
        spChk = NWSpellEnchant()

        spChk.setLanguage("en", wList)
        assert spChk.setLanguage("", "") is None
        assert spChk.checkWord("")
        assert spChk.suggestWords("") == []
        assert spChk.listDictionaries() == []
        assert spChk.describeDict() == ("", "")

    # Load the proper enchant package
    spChk = NWSpellEnchant()
    spChk.setLanguage("en", wList)

    assert spChk.checkWord("a_word")
    assert spChk.checkWord("b_word")
    assert spChk.checkWord("c_word")
    assert not spChk.checkWord("d_word")

    spChk.addWord("d_word")
    assert spChk.checkWord("d_word")

    wSuggest = spChk.suggestWords("wrod")
    assert len(wSuggest) > 0
    assert "word" in wSuggest

    dList = spChk.listDictionaries()
    assert len(dList) > 0

    aTag, aName = spChk.describeDict()
    assert aTag == "en"
    assert aName != ""

# END Test testCoreSpell_Enchant

@pytest.mark.core
def testCoreSpell_Simple(monkeypatch, tmpDir):
    """Test the fallback simple spell checker
    """
    wList = os.path.join(tmpDir, "wordlist.txt")
    wDict = os.path.join(tmpDir, "en.dict")
    writeFile(wList, "a_word\nb_word\nc_word\n")
    writeFile(wDict, "# Comment\ne_word\nf_word\ng_word\n")

    spChk = NWSpellSimple()
    spChk.mainConf.dictPath = tmpDir

    # Load dictionary, but fail
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        spChk.setLanguage("en", wList)
        assert spChk.spellLanguage is None
        assert spChk.theWords == set(spChk.projDict)

    # Load dictionary properly
    spChk.setLanguage("en", wList)
    assert spChk.projDict == ["a_word", "b_word", "c_word"]
    assert spChk.theWords == {"e_word", "f_word", "g_word", "a_word", "b_word", "c_word"}

    # Check words
    assert spChk.checkWord("a_word")
    assert spChk.checkWord("b_word")
    assert spChk.checkWord("c_word")
    assert not spChk.checkWord("d_word")
    assert spChk.checkWord("e_word")
    assert spChk.checkWord("f_word")
    assert spChk.checkWord("g_word")

    # Add word
    spChk.addWord("d_word")
    assert spChk.checkWord("d_word")

    # Check spelling
    assert spChk.suggestWords(" \t") == []

    wSuggest = spChk.suggestWords("d_wrod")
    assert len(wSuggest) > 0
    assert "d_word" in wSuggest

    # Break the matching
    with monkeypatch.context() as mp:
        mp.setattr("difflib.get_close_matches", lambda *args, **kwargs: [""])
        assert spChk.suggestWords("word") == []

    # Capitalisation
    wSuggest = spChk.suggestWords("D_wrod")
    assert len(wSuggest) > 0
    assert "D_word" in wSuggest

    # List dictionaries
    assert spChk.listDictionaries() == [("en", "difflib")]

    # Description
    aTag, aName = spChk.describeDict()
    assert aTag == "en"
    assert aName == ""

# END Test testCoreSpell_Simple
