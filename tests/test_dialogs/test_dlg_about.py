"""
novelWriter – About Dialog Class Tester
=======================================

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

from pathlib import Path

from PyQt5.QtWidgets import QAction, QMessageBox

from novelwriter import SHARED
from novelwriter.dialogs.about import GuiAbout


@pytest.mark.gui
def testDlgAbout_NWDialog(qtbot, monkeypatch, nwGUI):
    """Test the novelWriter about dialogs."""
    # NW About
    nwGUI.showAboutNWDialog()

    qtbot.waitUntil(lambda: SHARED.findTopLevelWidget(GuiAbout) is not None, timeout=1000)
    msgAbout = SHARED.findTopLevelWidget(GuiAbout)
    assert isinstance(msgAbout, GuiAbout)

    assert msgAbout.txtCredits.document().characterCount() > 100

    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.config.Config.assetPath", lambda *a: Path("whatever"))
        msgAbout._fillCreditsPage()
        assert msgAbout.txtCredits.toPlainText() == "Error loading credits text ..."

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
