# -*- coding: utf-8 -*-
"""novelWriter Item Editor Dialog Class Tester
"""

import pytest
import os

from shutil import copyfile
from tools import cmpFiles, getGuiItem

from PyQt5.QtWidgets import QAction, QMessageBox

from nw.gui import GuiItemEditor
from nw.constants import nwItemLayout

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiItemEditor_Dialog(qtbot, monkeypatch, nwGUI, fncDir, fncProj, refDir, outDir):
    """Test the full item editor dialog.
    """
    projFile = os.path.join(fncProj, "nwProject.nwx")
    testFile = os.path.join(outDir, "guiItemEditor_Dialog_nwProject.nwx")
    compFile = os.path.join(refDir, "guiItemEditor_Dialog_nwProject.nwx")

    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)

    # Create new, save, open project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj})
    assert nwGUI.openDocument("0e17daca5f3e1")
    assert nwGUI.treeView.setSelectedHandle("0e17daca5f3e1", doScroll=True)

    monkeypatch.setattr(GuiItemEditor, "exec_", lambda *args: None)
    nwGUI.mainMenu.aEditItem.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiItemEditor") is not None, timeout=1000)

    itemEdit = getGuiItem("GuiItemEditor")
    assert isinstance(itemEdit, GuiItemEditor)
    itemEdit.show()

    qtbot.addWidget(itemEdit)

    assert itemEdit.editName.text()          == "New Scene"
    assert itemEdit.editStatus.currentData() == "New"
    assert itemEdit.editLayout.currentData() == nwItemLayout.SCENE

    for c in "Just a Page":
        qtbot.keyClick(itemEdit.editName, c, delay=typeDelay)
    itemEdit.editStatus.setCurrentIndex(1)
    layoutIdx = itemEdit.editLayout.findData(nwItemLayout.PAGE)
    itemEdit.editLayout.setCurrentIndex(layoutIdx)

    itemEdit.editExport.setChecked(False)
    assert not itemEdit.editExport.isChecked()
    itemEdit._doSave()

    nwGUI.mainMenu.aEditItem.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiItemEditor") is not None, timeout=1000)

    itemEdit = getGuiItem("GuiItemEditor")
    assert isinstance(itemEdit, GuiItemEditor)
    itemEdit.show()

    qtbot.addWidget(itemEdit)
    assert itemEdit.editName.text()          == "Just a Page"
    assert itemEdit.editStatus.currentData() == "Note"
    assert itemEdit.editLayout.currentData() == nwItemLayout.PAGE
    itemEdit._doClose()

    # Check that the header is updated
    nwGUI.docEditor.updateDocInfo("0e17daca5f3e1")
    assert nwGUI.docEditor.docHeader.theTitle.text() == "Novel  ›  New Chapter  ›  Just a Page"
    assert not nwGUI.docEditor.setCursorLine("where?")
    assert nwGUI.docEditor.setCursorLine(2)
    qtbot.wait(stepDelay)
    assert nwGUI.docEditor.getCursorPosition() == 15

    qtbot.wait(stepDelay)
    assert nwGUI.saveProject()
    qtbot.wait(stepDelay)

    # Check the files
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile,  [2, 6, 7, 8])

    # qtbot.stopForInteraction()

# END Test testGuiItemEditor_Dialog
