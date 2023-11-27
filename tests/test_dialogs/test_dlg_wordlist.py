"""
novelWriter – Other Dialog Classes Tester
=========================================

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

import pytest

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QAction

from tools import buildTestProject, getGuiItem

from novelwriter import SHARED
from novelwriter.core.spellcheck import UserDictionary
from novelwriter.dialogs.wordlist import GuiWordList


@pytest.mark.gui
def testDlgWordList_Dialog(qtbot, monkeypatch, nwGUI, projPath):
    """test the word list editor.
    """
    buildTestProject(nwGUI, projPath)

    monkeypatch.setattr(GuiWordList, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiWordList, "result", lambda *a: QDialog.Accepted)
    monkeypatch.setattr(GuiWordList, "accept", lambda *a: None)

    # Open project
    nwGUI.openProject(projPath)

    # Load the dialog
    nwGUI.mainMenu.aEditWordList.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiWordList") is not None, timeout=1000)

    wList = getGuiItem("GuiWordList")
    assert isinstance(wList, GuiWordList)
    wList.show()

    # List should be blank
    assert wList.listBox.count() == 0

    # Add words
    userDict = UserDictionary(SHARED.project)
    userDict.add("word_a")
    userDict.add("word_c")
    userDict.add("word_g")
    userDict.add("word_f")
    userDict.add("word_b")
    userDict.save()

    wList._loadWordList()

    # Check that the content was loaded
    assert wList.listBox.item(0).text() == "word_a"
    assert wList.listBox.item(1).text() == "word_b"
    assert wList.listBox.item(2).text() == "word_c"
    assert wList.listBox.item(3).text() == "word_f"
    assert wList.listBox.item(4).text() == "word_g"
    assert wList.listBox.count() == 5

    # Add a blank word, which is ignored
    wList.newEntry.setText("   ")
    wList._doAdd()
    assert wList.listBox.count() == 5

    # Add an existing word, which is ignored
    wList.newEntry.setText("word_c")
    wList._doAdd()
    assert wList.listBox.count() == 5

    # Add a new word
    wList.newEntry.setText("word_d")
    wList._doAdd()
    assert wList.listBox.count() == 6

    # Check that the content now
    assert wList.listBox.item(0).text() == "word_a"
    assert wList.listBox.item(1).text() == "word_b"
    assert wList.listBox.item(2).text() == "word_c"
    assert wList.listBox.item(3).text() == "word_d"
    assert wList.listBox.item(4).text() == "word_f"
    assert wList.listBox.item(5).text() == "word_g"

    # Delete a word
    wList.newEntry.setText("delete_me")
    wList._doAdd()
    assert wList.listBox.item(0).text() == "delete_me"

    delItem = wList.listBox.findItems("delete_me", Qt.MatchExactly)[0]
    assert delItem.text() == "delete_me"
    delItem.setSelected(True)
    wList._doDelete()
    assert wList.listBox.findItems("delete_me", Qt.MatchExactly) == []
    assert wList.listBox.item(0).text() == "word_a"

    # Save files
    wList._doSave()
    userDict.load()
    assert len(list(userDict)) == 6
    assert "word_a" in userDict
    assert "word_b" in userDict
    assert "word_c" in userDict
    assert "word_d" in userDict
    assert "word_f" in userDict
    assert "word_g" in userDict

    # qtbot.stop()
    wList._doClose()

# END Test testDlgWordList_Dialog
