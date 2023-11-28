"""
novelWriter – About Dialog Class Tester
=======================================

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

from pathlib import Path

from tools import getGuiItem

from PyQt5.QtWidgets import QAction, QMessageBox

from novelwriter.dialogs.about import GuiAbout


@pytest.mark.gui
def testDlgAbout_NWDialog(qtbot, monkeypatch, nwGUI):
    """Test the novelWriter about dialogs."""
    # NW About
    assert nwGUI.showAboutNWDialog(showNotes=True) is True

    qtbot.waitUntil(lambda: getGuiItem("GuiAbout") is not None, timeout=1000)
    msgAbout = getGuiItem("GuiAbout")
    assert isinstance(msgAbout, GuiAbout)

    assert msgAbout.pageAbout.document().characterCount() > 100
    assert msgAbout.pageNotes.document().characterCount() > 100
    assert msgAbout.pageLicense.document().characterCount() > 100

    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.config.Config.assetPath", lambda *a: Path("whatever"))
        msgAbout._fillNotesPage()
        assert msgAbout.pageNotes.toPlainText() == "Error loading release notes text ..."
        msgAbout._fillCreditsPage()
        assert msgAbout.pageCredits.toPlainText() == "Error loading credits text ..."
        msgAbout._fillLicensePage()
        assert msgAbout.pageLicense.toPlainText() == "Error loading licence text ..."

    msgAbout.showReleaseNotes()
    assert msgAbout.tabBox.currentWidget() == msgAbout.pageNotes
    msgAbout.close()

# END Test testDlgAbout_NWDialog


@pytest.mark.gui
def testDlgAbout_QtDialog(monkeypatch, nwGUI):
    """Test the Qt about dialogs."""
    monkeypatch.setattr(QMessageBox, "aboutQt", lambda *a, **k: None)

    # Open About
    # All it can do is check against a crash
    nwGUI.showAboutQtDialog()
    nwGUI.mainMenu.aAboutQt.activate(QAction.Trigger)

# END Test testDlgAbout_QtDialog
