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

import pytest

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QAction, QListWidgetItem, QDialog, QMessageBox

from novelwriter.dialogs import GuiQuoteSelect, GuiUpdates

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testDlgOther_QuoteSelect(qtbot, monkeypatch, nwGUI):
    """Test the quote symbols dialog.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    nwQuot = GuiQuoteSelect(nwGUI)
    nwQuot.show()

    lastItem = ""
    for i in range(nwQuot.listBox.count()):
        anItem = nwQuot.listBox.item(i)
        assert isinstance(anItem, QListWidgetItem)
        nwQuot.listBox.clearSelection()
        nwQuot.listBox.setCurrentItem(anItem, QItemSelectionModel.Select)
        lastItem = anItem.text()[2]
        assert nwQuot.previewLabel.text() == lastItem

    nwQuot._doAccept()
    assert nwQuot.result() == QDialog.Accepted
    assert nwQuot.selectedQuote == lastItem

    # qtbot.stopForInteraction()
    nwQuot._doReject()
    nwQuot.close()

# END Test testDlgOther_QuoteSelect


@pytest.mark.gui
def testDlgOther_Updates(qtbot, monkeypatch, nwGUI):
    """Test the check for updates dialog.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    nwUpdate = GuiUpdates(nwGUI)
    nwUpdate.show()

    class mockData:
        def decode(self):
            return '{"tag_name": "v1.0", "created_at": "2021-01-01T12:00:00Z"}'

    class mockPayload:
        def read(self):
            return mockData()

    def mockUrlopenA(*a, **k):
        return None

    def mockUrlopenB(*a, **k):
        return mockPayload()

    # Faulty Return
    monkeypatch.setattr("novelwriter.dialogs.updates.urlopen", mockUrlopenA)
    nwUpdate.checkLatest()

    # Valid Return
    monkeypatch.setattr("novelwriter.dialogs.updates.urlopen", mockUrlopenB)
    nwUpdate.checkLatest()
    assert nwUpdate.latestValue.text().startswith("novelWriter v1.0")

    # Trigger from Menu
    nwGUI.mainMenu.aUpdates.activate(QAction.Trigger)

    # qtbot.stopForInteraction()
    nwUpdate._doClose()

# END Test testDlgOther_Updates
