"""
novelWriter – Other Dialog Classes Tester
=========================================

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

import pytest

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QListWidgetItem, QDialog

from novelwriter.dialogs.quotes import GuiQuoteSelect
from novelwriter.dialogs.editlabel import GuiEditLabel


@pytest.mark.gui
def testDlgOther_QuoteSelect(qtbot, monkeypatch, nwGUI):
    """Test the quote symbols dialog."""
    monkeypatch.setattr(GuiQuoteSelect, "exec", lambda *a: None)

    nwQuot = GuiQuoteSelect(nwGUI)
    nwQuot.show()

    lastItem = ""
    for i in range(nwQuot.listBox.count()):
        anItem = nwQuot.listBox.item(i)
        assert isinstance(anItem, QListWidgetItem)
        nwQuot.listBox.clearSelection()
        nwQuot.listBox.setCurrentItem(anItem, QItemSelectionModel.SelectionFlag.Select)
        lastItem = anItem.text()[2]
        assert nwQuot.previewLabel.text() == lastItem

    nwQuot.accept()
    assert nwQuot.result() == QDialog.Accepted
    assert nwQuot.selectedQuote == lastItem
    nwQuot.close()

    # Test Class Method
    with monkeypatch.context() as mp:
        mp.setattr(GuiQuoteSelect, "result", lambda *a: QDialog.DialogCode.Accepted)
        assert GuiQuoteSelect.getQuote(nwGUI, current="X") == ("X", True)

    with monkeypatch.context() as mp:
        mp.setattr(GuiQuoteSelect, "result", lambda *a: QDialog.DialogCode.Rejected)
        assert GuiQuoteSelect.getQuote(nwGUI, current="X") == ("X", False)

    # qtbot.stop()

# END Test testDlgOther_QuoteSelect


@pytest.mark.gui
def testDlgOther_EditLabel(qtbot, monkeypatch):
    """Test the label editor dialog."""
    monkeypatch.setattr(GuiEditLabel, "exec", lambda *a: None)

    with monkeypatch.context() as mp:
        mp.setattr(GuiEditLabel, "result", lambda *a: QDialog.Accepted)
        newLabel, dlgOk = GuiEditLabel.getLabel(None, text="Hello World")  # type: ignore
        assert dlgOk is True
        assert newLabel == "Hello World"

    with monkeypatch.context() as mp:
        mp.setattr(GuiEditLabel, "result", lambda *a: QDialog.Rejected)
        newLabel, dlgOk = GuiEditLabel.getLabel(None, text="Hello World")  # type: ignore
        assert dlgOk is False
        assert newLabel == "Hello World"

# END Test testDlgOther_EditLabel
