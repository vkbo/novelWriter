# -*- coding: utf-8 -*-
"""novelWriter About Dialog Class Tester
"""

import pytest

from tools import getGuiItem

from PyQt5.QtWidgets import QAction, QMessageBox

from nw.gui import GuiAbout

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiAbout_Dialog(qtbot, monkeypatch, nwGUI):
    """Test the full about dialogs.
    """
    # NW About
    monkeypatch.setattr(GuiAbout, "exec_", lambda *args: None)
    nwGUI.mainMenu.aAboutNW.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiAbout") is not None, timeout=1000)

    msgAbout = getGuiItem("GuiAbout")
    assert isinstance(msgAbout, GuiAbout)
    msgAbout.show()

    assert msgAbout.pageAbout.document().characterCount() > 100
    assert msgAbout.pageNotes.document().characterCount() > 100
    assert msgAbout.pageLicense.document().characterCount() > 100

    msgAbout.mainConf.assetPath = "whatever"

    msgAbout._fillNotesPage()
    assert msgAbout.pageNotes.toPlainText() == "Error loading release notes text ..."

    msgAbout._fillLicensePage()
    assert msgAbout.pageLicense.toPlainText() == "Error loading license text ..."

    msgAbout.showReleaseNotes()
    assert msgAbout.tabBox.currentWidget() == msgAbout.pageNotes

    # Qt About
    monkeypatch.setattr(QMessageBox, "aboutQt", lambda *args, **kwargs: None)
    nwGUI.mainMenu.aAboutQt.activate(QAction.Trigger)

    # qtbot.stopForInteraction()
    msgAbout._doClose()

# END Test testGuiAbout_Dialog
