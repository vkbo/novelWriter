"""
novelWriter – Other Dialog Classes Tester
=========================================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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
import pytest

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QAction

from tools import writeFile, readFile, getGuiItem
from mock import causeOSError

from novelwriter.dialogs import GuiWordList
from novelwriter.constants import nwFiles

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testDlgWordList_Dialog(qtbot, monkeypatch, nwGUI, nwMinimal):
    """test the word list editor.
    """
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiWordList, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiWordList, "result", lambda *a: QDialog.Accepted)
    monkeypatch.setattr(GuiWordList, "accept", lambda *a: None)

    # Open project
    nwGUI.openProject(nwMinimal)
    qtbot.wait(stepDelay)
    dictFile = os.path.join(nwMinimal, "meta", nwFiles.PROJ_DICT)

    # Load the dialog
    nwGUI.mainMenu.aEditWordList.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiWordList") is not None, timeout=1000)

    wList = getGuiItem("GuiWordList")
    assert isinstance(wList, GuiWordList)
    wList.show()
    qtbot.wait(stepDelay)

    # List should be blank
    assert wList.listBox.count() == 0

    # Add words
    writeFile(dictFile, (
        "word_a\n"
        "word_c\n"
        "word_g\n"
        "      \n"  # Should be ignored
        "word_f\n"
        "word_b\n"
    ))
    qtbot.wait(stepDelay)
    assert wList._loadWordList()

    # Check that the content was loaded
    assert wList.listBox.item(0).text() == "word_a"
    assert wList.listBox.item(1).text() == "word_b"
    assert wList.listBox.item(2).text() == "word_c"
    assert wList.listBox.item(3).text() == "word_f"
    assert wList.listBox.item(4).text() == "word_g"

    # Add a blank word
    wList.newEntry.setText("   ")
    assert not wList._doAdd()

    # Add an existing word
    wList.newEntry.setText("word_c")
    assert not wList._doAdd()

    # Add a new word
    wList.newEntry.setText("word_d")
    assert wList._doAdd()

    # Check that the content now
    assert wList.listBox.item(0).text() == "word_a"
    assert wList.listBox.item(1).text() == "word_b"
    assert wList.listBox.item(2).text() == "word_c"
    assert wList.listBox.item(3).text() == "word_d"
    assert wList.listBox.item(4).text() == "word_f"
    assert wList.listBox.item(5).text() == "word_g"

    # Delete a word
    wList.newEntry.setText("delete_me")
    assert wList._doAdd()
    assert wList.listBox.item(0).text() == "delete_me"

    delItem = wList.listBox.findItems("delete_me", Qt.MatchExactly)[0]
    assert delItem.text() == "delete_me"
    delItem.setSelected(True)
    wList._doDelete()
    assert wList.listBox.findItems("delete_me", Qt.MatchExactly) == []
    assert wList.listBox.item(0).text() == "word_a"

    # Save files
    assert wList._doSave()
    assert readFile(dictFile) == (
        "word_a\n"
        "word_b\n"
        "word_c\n"
        "word_d\n"
        "word_f\n"
        "word_g\n"
    )

    # Save again and make it fail
    monkeypatch.setattr("builtins.open", causeOSError)
    assert not wList._doSave()

    # qtbot.stopForInteraction()
    wList._doClose()

# END Test testDlgWordList_Dialog
