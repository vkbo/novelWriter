"""
novelWriter – About Dialog Class Tester
=======================================

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

import pytest

from tools import getGuiItem

from PyQt5.QtWidgets import QAction, QMessageBox

from novelwriter.dialogs import GuiAbout


@pytest.mark.gui
def testDlgAbout_NWDialog(qtbot, monkeypatch, nwGUI):
    """Test the novelWriter about dialogs.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    # NW About
    nwGUI.theTheme.themeName = "A Theme"
    nwGUI.theTheme.themeAuthor = "An Author"
    assert nwGUI.showAboutNWDialog(showNotes=True) is True

    qtbot.waitUntil(lambda: getGuiItem("GuiAbout") is not None, timeout=1000)
    msgAbout = getGuiItem("GuiAbout")
    assert isinstance(msgAbout, GuiAbout)

    assert msgAbout.pageAbout.document().characterCount() > 100
    assert msgAbout.pageNotes.document().characterCount() > 100
    assert msgAbout.pageLicense.document().characterCount() > 100

    msgAbout.mainConf.assetPath = "whatever"

    msgAbout._fillNotesPage()
    assert msgAbout.pageNotes.toPlainText() == "Error loading release notes text ..."

    msgAbout._fillLicensePage()
    assert msgAbout.pageLicense.toPlainText() == "Error loading licence text ..."

    msgAbout.showReleaseNotes()
    assert msgAbout.tabBox.currentWidget() == msgAbout.pageNotes
    msgAbout._doClose()

    # Open Again from Menu
    nwGUI.mainMenu.aAboutNW.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiAbout") is not None, timeout=1000)
    msgAbout = getGuiItem("GuiAbout")
    assert msgAbout is not None
    msgAbout._doClose()

# END Test testDlgAbout_NWDialog


@pytest.mark.gui
def testDlgAbout_QtDialog(monkeypatch, nwGUI):
    """Test the Qt about dialogs.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "aboutQt", lambda *a, **k: None)

    # Open About
    # All it can do is check aigainst a crash
    assert nwGUI.showAboutQtDialog() is True
    nwGUI.mainMenu.aAboutQt.activate(QAction.Trigger)

# END Test testDlgAbout_QtDialog
