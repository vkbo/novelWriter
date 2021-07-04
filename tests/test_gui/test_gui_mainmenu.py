"""
novelWriter – Main GUI Main Menu Class Tester
=============================================

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
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QTextBlock
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox

from tools import writeFile

from nw.gui.doceditor import GuiDocEditor
from nw.enum import nwDocAction, nwDocInsert, nwWidget
from nw.constants import nwKeyWords, nwUnicode

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testGuiMenu_EditFormat(qtbot, monkeypatch, nwGUI, nwLipsum):
    """Test the main menu Edit and Format entries.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *a: True)

    # Test Document Action with No Project
    assert nwGUI.docEditor.docAction(nwDocAction.COPY) is False

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum) is True
    qtbot.wait(stepDelay)

    # Split By Chapter
    assert nwGUI.openDocument("4c4f28287af27") is True
    assert nwGUI.docEditor.setCursorPosition(30) is True

    cleanText = nwGUI.docEditor.getText()[27:74]

    # Bold
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    fmtStr = "**Pellentesque** nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:78] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Italic
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    fmtStr = "_Pellentesque_ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Strikethrough
    nwGUI.mainMenu.aFmtStrike.activate(QAction.Trigger)
    fmtStr = "~~Pellentesque~~ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:78] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtStrike.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Should get us back to plain
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Double Quotes
    nwGUI.mainMenu.aFmtDQuote.activate(QAction.Trigger)
    fmtStr = "“Pellentesque” nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Single Quotes
    nwGUI.mainMenu.aFmtSQuote.activate(QAction.Trigger)
    fmtStr = "‘Pellentesque’ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Block Formats
    # =============
    assert nwGUI.docEditor.setCursorPosition(30)

    # Header 1
    nwGUI.mainMenu.aFmtHead1.activate(QAction.Trigger)
    fmtStr = "# Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)

    # Header 2
    nwGUI.mainMenu.aFmtHead2.activate(QAction.Trigger)
    fmtStr = "## Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:77] == fmtStr
    qtbot.wait(stepDelay)

    # Header 3
    nwGUI.mainMenu.aFmtHead3.activate(QAction.Trigger)
    fmtStr = "### Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:78] == fmtStr
    qtbot.wait(stepDelay)

    # Header 4
    nwGUI.mainMenu.aFmtHead4.activate(QAction.Trigger)
    fmtStr = "#### Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:79] == fmtStr
    qtbot.wait(stepDelay)

    # Clear Format
    nwGUI.mainMenu.aFmtNoFormat.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Comment On
    nwGUI.mainMenu.aFmtComment.activate(QAction.Trigger)
    fmtStr = "% Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)

    # Comment Off
    nwGUI.mainMenu.aFmtComment.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Check comment with no space before text
    assert nwGUI.docEditor.setCursorPosition(27)
    assert nwGUI.docEditor.insertText("%")
    fmtStr = "%Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:75] == fmtStr
    qtbot.wait(stepDelay)

    nwGUI.mainMenu.aFmtNoFormat.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Undo/Redo
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)
    fmtStr = "%Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:75] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aEditRedo.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Cut, Copy and Paste
    assert nwGUI.docEditor.setCursorPosition(27)
    nwGUI.docEditor._makeSelection(QTextCursor.WordUnderCursor)

    nwGUI.mainMenu.aEditCut.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:77] == (
        " nec erat ut nulla posuere commodo. Curabitur nisi"
    )

    nwGUI.mainMenu.aEditPaste.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:77] == (
        "Pellentesque nec erat ut nulla posuere commodo. Cu"
    )

    assert nwGUI.docEditor.setCursorPosition(27)
    nwGUI.docEditor._makeSelection(QTextCursor.WordUnderCursor)

    nwGUI.mainMenu.aEditCopy.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:77] == (
        "Pellentesque nec erat ut nulla posuere commodo. Cu"
    )

    assert nwGUI.docEditor.setCursorPosition(27)
    nwGUI.mainMenu.aEditPaste.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:77] == (
        "PellentesquePellentesque nec erat ut nulla posuere"
    )
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)

    # Select Paragraph/All
    assert nwGUI.docEditor.setCursorPosition(30)
    nwGUI.mainMenu.aSelectPar.activate(QAction.Trigger)
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == (
        "Pellentesque nec erat ut nulla posuere commodo. Curabitur nisi augue, imperdiet et porta "
        "imperdiet, efficitur id leo. Cras finibus arcu at nibh commodo congue. Proin suscipit "
        "placerat condimentum. Aenean ante enim, cursus id lorem a, blandit venenatis nibh. "
        "Maecenas suscipit porta elit, sit amet porta felis porttitor eu. Sed a dui nibh. "
        "Phasellus sed faucibus dui. Pellentesque felis nulla, ultrices non efficitur quis, "
        "rutrum id mi. Mauris tempus auctor nisl, in bibendum enim pellentesque sit amet. Proin "
        "nunc lacus, imperdiet nec posuere ac, interdum non lectus."
    )

    assert nwGUI.docEditor.setCursorPosition(30)
    nwGUI.mainMenu.aSelectAll.activate(QAction.Trigger)
    theCursor = nwGUI.docEditor.textCursor()
    assert len(theCursor.selectedText()) == 1883

    # Clear the Text
    nwGUI.docEditor.clear()
    assert nwGUI.docEditor.isEmpty()

    # Alignment & Indent
    # ==================

    cleanText = "A single, short paragraph.\n\n"
    nwGUI.docEditor.setText(cleanText)
    assert nwGUI.docEditor.setCursorPosition(0)

    # Left Align
    nwGUI.mainMenu.aFmtAlignLeft.activate(QAction.Trigger)
    fmtStr = "A single, short paragraph. <<"
    assert nwGUI.docEditor.getText()[:29] == fmtStr
    qtbot.wait(stepDelay)

    # Right Align
    nwGUI.mainMenu.aFmtAlignRight.activate(QAction.Trigger)
    fmtStr = ">> A single, short paragraph."
    assert nwGUI.docEditor.getText()[:29] == fmtStr
    qtbot.wait(stepDelay)

    # Centre Align
    nwGUI.mainMenu.aFmtAlignCentre.activate(QAction.Trigger)
    fmtStr = ">> A single, short paragraph. <<"
    assert nwGUI.docEditor.getText()[:32] == fmtStr
    qtbot.wait(stepDelay)

    # Left Indent
    nwGUI.mainMenu.aFmtIndentLeft.activate(QAction.Trigger)
    fmtStr = "> A single, short paragraph."
    assert nwGUI.docEditor.getText()[:28] == fmtStr
    qtbot.wait(stepDelay)

    # Right Indent
    nwGUI.mainMenu.aFmtIndentRight.activate(QAction.Trigger)
    fmtStr = "> A single, short paragraph. <"
    assert nwGUI.docEditor.getText()[:30] == fmtStr
    qtbot.wait(stepDelay)

    # No Format
    nwGUI.mainMenu.aFmtNoFormat.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[:30] == cleanText
    qtbot.wait(stepDelay)

    # Other Checks

    # Replace Quotes
    nwGUI.docEditor.setText((
        "### New Text\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    ))

    nwGUI.mainMenu.aSelectAll.activate(QAction.Trigger)
    nwGUI.mainMenu.aFmtReplSng.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == (
        "### New Text\n\n"
        "Text with ‘single’ quotes and ‘tricky stuff’s’.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    )

    nwGUI.mainMenu.aSelectAll.activate(QAction.Trigger)
    nwGUI.mainMenu.aFmtReplDbl.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == (
        "### New Text\n\n"
        "Text with ‘single’ quotes and ‘tricky stuff’s’.\n\n"
        "Also text with “double” quotes which are “less tricky”.\n\n"
    )

    # Remove in-paragraph line breaks
    nwGUI.docEditor.setText((
        "### New Text\n\n"
        "@char: Someone\n"
        "@location: Somewhere\n\n"
        "% Some comment ...\n\n"
        "Here is some text\non multiple\nlines.\n\n"
        "With another paragraph\nhere."
    ))
    nwGUI.mainMenu.aFmtRmBreaks.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == (
        "### New Text\n\n"
        "@char: Someone\n"
        "@location: Somewhere\n\n"
        "% Some comment ...\n\n"
        "Here is some text on multiple lines.\n\n"
        "With another paragraph here.\n"
    )

    nwGUI.docEditor.setText((
        "### New Text\n\n"
        "@char: Someone\n"
        "@location: Somewhere\n\n"
        "% Some comment ...\n\n"
        "Here is some text\non multiple\nlines.\n\n"
        "With another paragraph\nhere."
    ))
    theCursor = nwGUI.docEditor.textCursor()
    theCursor.setPosition(74)
    theCursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 29)
    nwGUI.docEditor.setTextCursor(theCursor)
    nwGUI.mainMenu.aFmtRmBreaks.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == (
        "### New Text\n\n"
        "@char: Someone\n"
        "@location: Somewhere\n\n"
        "% Some comment ...\n\n"
        "Here is some text on multiple lines.\n\n"
        "With another paragraph\nhere."
    )

    # Test Invalid Document Action
    assert not nwGUI.docEditor.docAction(nwDocAction.NO_ACTION)

    # Test Invalid Formats
    nwGUI.docEditor.setText((
        "### New Text\n\n"
        "@tag: Bod\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    ))

    # Cannot Format Tag
    assert nwGUI.docEditor.setCursorPosition(17)
    assert not nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT)

    # Cannot Format Empty Line
    assert nwGUI.docEditor.setCursorPosition(13)
    assert not nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT)

    # Invalid Action
    assert nwGUI.docEditor.setCursorPosition(30)
    assert not nwGUI.docEditor._formatBlock(nwDocAction.NO_ACTION)

    # Ensure No Changes
    assert nwGUI.docEditor.getText() == (
        "### New Text\n\n"
        "@tag: Bod\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    )

    # qtbot.stopForInteraction()

# END Test testGuiMenu_EditFormat


@pytest.mark.gui
def testGuiMenu_ContextMenus(qtbot, monkeypatch, nwGUI, nwLipsum):
    """Test the context menus.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)
    assert nwGUI.openDocument("4c4f28287af27")
    qtbot.wait(stepDelay)

    # Editor Context Menu
    theCursor = nwGUI.docEditor.textCursor()
    theCursor.setPosition(100)
    nwGUI.docEditor.setTextCursor(theCursor)
    theRect = nwGUI.docEditor.cursorRect()

    nwGUI.docEditor._openContextMenu(theRect.bottomRight())
    qtbot.mouseClick(nwGUI.docEditor, Qt.LeftButton, pos=theRect.topLeft())

    nwGUI.docEditor._makePosSelection(QTextCursor.WordUnderCursor, theRect.center())
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == "imperdiet"

    nwGUI.docEditor._makePosSelection(QTextCursor.BlockUnderCursor, theRect.center())
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == (
        "Pellentesque nec erat ut nulla posuere commodo. Curabitur nisi augue, imperdiet et porta "
        "imperdiet, efficitur id leo. Cras finibus arcu at nibh commodo congue. Proin suscipit "
        "placerat condimentum. Aenean ante enim, cursus id lorem a, blandit venenatis nibh. "
        "Maecenas suscipit porta elit, sit amet porta felis porttitor eu. Sed a dui nibh. "
        "Phasellus sed faucibus dui. Pellentesque felis nulla, ultrices non efficitur quis, "
        "rutrum id mi. Mauris tempus auctor nisl, in bibendum enim pellentesque sit amet. Proin "
        "nunc lacus, imperdiet nec posuere ac, interdum non lectus."
    )

    # Viewer Context Menu
    assert nwGUI.viewDocument("4c4f28287af27")

    theCursor = nwGUI.docViewer.textCursor()
    theCursor.setPosition(100)
    nwGUI.docViewer.setTextCursor(theCursor)
    theRect = nwGUI.docViewer.cursorRect()

    nwGUI.docViewer._openContextMenu(theRect.bottomRight())
    qtbot.mouseClick(nwGUI.docViewer, Qt.LeftButton, pos=theRect.topLeft())

    nwGUI.docViewer._makePosSelection(QTextCursor.WordUnderCursor, theRect.center())
    theCursor = nwGUI.docViewer.textCursor()
    assert theCursor.selectedText() == "imperdiet"

    nwGUI.docEditor._makePosSelection(QTextCursor.BlockUnderCursor, theRect.center())
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == (
        "Pellentesque nec erat ut nulla posuere commodo. Curabitur nisi augue, imperdiet et porta "
        "imperdiet, efficitur id leo. Cras finibus arcu at nibh commodo congue. Proin suscipit "
        "placerat condimentum. Aenean ante enim, cursus id lorem a, blandit venenatis nibh. "
        "Maecenas suscipit porta elit, sit amet porta felis porttitor eu. Sed a dui nibh. "
        "Phasellus sed faucibus dui. Pellentesque felis nulla, ultrices non efficitur quis, "
        "rutrum id mi. Mauris tempus auctor nisl, in bibendum enim pellentesque sit amet. Proin "
        "nunc lacus, imperdiet nec posuere ac, interdum non lectus."
    )

    # Navigation History
    assert nwGUI.viewDocument("04468803b92e1")
    assert nwGUI.docViewer.docHandle() == "04468803b92e1"
    assert nwGUI.docViewer.docHeader.backButton.isEnabled()
    assert not nwGUI.docViewer.docHeader.forwardButton.isEnabled()

    qtbot.mouseClick(nwGUI.docViewer.docHeader.backButton, Qt.LeftButton)
    assert nwGUI.docViewer.docHandle() == "4c4f28287af27"
    assert not nwGUI.docViewer.docHeader.backButton.isEnabled()
    assert nwGUI.docViewer.docHeader.forwardButton.isEnabled()

    qtbot.mouseClick(nwGUI.docViewer.docHeader.forwardButton, Qt.LeftButton)
    assert nwGUI.docViewer.docHandle() == "04468803b92e1"
    assert nwGUI.docViewer.docHeader.backButton.isEnabled()
    assert not nwGUI.docViewer.docHeader.forwardButton.isEnabled()

    # qtbot.stopForInteraction()

# END Test testGuiMenu_ContextMenus


@pytest.mark.gui
def testGuiMenu_Insert(qtbot, monkeypatch, nwGUI, fncDir, fncProj):
    """Test the Insert menu.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj})

    assert nwGUI.treeView._getTreeItem("0e17daca5f3e1") is not None

    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("0e17daca5f3e1").setSelected(True)
    assert nwGUI.openSelectedItem()
    nwGUI.docEditor.clear()

    # Test Faulty Inserts
    assert nwGUI.docEditor.insertText("hello world")
    assert nwGUI.docEditor.getText() == "hello world"
    nwGUI.docEditor.clear()

    assert not nwGUI.docEditor.insertText(nwDocInsert.NO_INSERT)
    assert nwGUI.docEditor.isEmpty()

    assert not nwGUI.docEditor.insertText(None)
    assert nwGUI.docEditor.isEmpty()

    # qtbot.stopForInteraction()

    # Check Menu Entries
    nwGUI.mainMenu.aInsENDash.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_ENDASH
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsEMDash.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_EMDASH
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsHorBar.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_HBAR
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsFigDash.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_FGDASH
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteLS.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwGUI.mainConf.fmtSingleQuotes[0]
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteRS.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwGUI.mainConf.fmtSingleQuotes[1]
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteLD.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwGUI.mainConf.fmtDoubleQuotes[0]
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteRD.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwGUI.mainConf.fmtDoubleQuotes[1]
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsMSApos.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_MAPOSS
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsEllipsis.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_HELLIP
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsPrime.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_PRIME
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsDPrime.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_DPRIME
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsBullet.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_BULL
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsHyBull.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_HYBULL
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsFlower.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_FLOWER
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsPerMille.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_PERMIL
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsDegree.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_DEGREE
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsMinus.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_MINUS
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsTimes.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_TIMES
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsDivide.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_DIVIDE
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsNBSpace.activate(QAction.Trigger)
    if nwGUI.mainConf.verQtValue >= 50900:
        assert nwGUI.docEditor.getText() == nwUnicode.U_NBSP
    else:
        assert nwGUI.docEditor.getText() == " "
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsThinSpace.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_THSP
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsThinNBSpace.activate(QAction.Trigger)
    if nwGUI.mainConf.verQtValue >= 50900:
        assert nwGUI.docEditor.getText() == nwUnicode.U_THNBSP
    else:
        assert nwGUI.docEditor.getText() == " "
    nwGUI.docEditor.clear()

    ##
    #  Insert Keywords
    ##

    nwGUI.docEditor.setText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.TAG_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.TAG_KEY

    nwGUI.docEditor.setText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.POV_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.POV_KEY

    nwGUI.docEditor.setText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.FOCUS_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.FOCUS_KEY

    nwGUI.docEditor.setText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.CHAR_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.CHAR_KEY

    nwGUI.docEditor.setText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.PLOT_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.PLOT_KEY

    nwGUI.docEditor.setText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.TIME_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.TIME_KEY

    nwGUI.docEditor.setText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.WORLD_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.WORLD_KEY

    nwGUI.docEditor.setText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.OBJECT_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.OBJECT_KEY

    nwGUI.docEditor.setText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.ENTITY_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.ENTITY_KEY

    nwGUI.docEditor.setText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.CUSTOM_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.CUSTOM_KEY

    # Faulty Keyword Inserts
    assert not nwGUI.docEditor.insertKeyWord("blabla")
    with monkeypatch.context() as mp:
        mp.setattr(QTextBlock, "isValid", lambda *args, **kwards: False)
        assert not nwGUI.docEditor.insertKeyWord(nwKeyWords.TAG_KEY)

    nwGUI.docEditor.clear()

    ##
    #  Insert text from file
    ##

    nwGUI.closeDocument()

    # First, with no path
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwards: ("", ""))
    assert not nwGUI.importDocument()

    # Then with a path, but an invalid one
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwards: (" ", ""))
    assert not nwGUI.importDocument()

    # Then a valid path, but bot a file that exists
    theFile = os.path.join(fncDir, "import.txt")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwards: (theFile, ""))
    assert not nwGUI.importDocument()

    # Create the file and try again, but with no target document open
    writeFile(theFile, "Foo")
    assert not nwGUI.importDocument()

    # Open the document from before, and add some text to it
    nwGUI.openDocument("0e17daca5f3e1")
    nwGUI.docEditor.setText("Bar")
    assert nwGUI.docEditor.getText() == "Bar"

    # The document isn't empty, so the message box should pop
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.No)
    assert not nwGUI.importDocument()
    assert nwGUI.docEditor.getText() == "Bar"

    # Finally, accept the replaced text, this time we use the menu entry to trigger it
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)
    nwGUI.mainMenu.aImportFile.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Foo"

    ##
    #  Reveal file location
    ##

    theMessage = ""

    def recordMsg(*args):
        nonlocal theMessage
        theMessage = args[3]
        return None

    assert not theMessage
    monkeypatch.setattr(QMessageBox, "information", recordMsg)
    nwGUI.mainMenu.aFileDetails.activate(QAction.Trigger)

    theBits = theMessage.split("<br>")
    assert len(theBits) == 2
    assert theBits[0] == "The currently open file is saved in:"
    assert theBits[1] == os.path.join(fncProj, "content", "0e17daca5f3e1.nwd")

    # qtbot.stopForInteraction()

# END Test testGuiMenu_Insert
