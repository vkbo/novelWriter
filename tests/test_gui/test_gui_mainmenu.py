"""
novelWriter – Main GUI Main Menu Class Tester
=============================================

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

import pytest

from PyQt5.QtGui import QTextCursor, QTextBlock
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox

from tools import C, writeFile, buildTestProject

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwDocAction, nwDocInsert
from novelwriter.constants import nwKeyWords, nwUnicode
from novelwriter.gui.doceditor import GuiDocEditor


@pytest.mark.gui
def testGuiMenu_EditFormat(qtbot, monkeypatch, nwGUI, prjLipsum):
    """Test the main menu Edit and Format entries.
    """
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *a: True)

    # Test Document Action with No Project
    assert nwGUI.docEditor.docAction(nwDocAction.COPY) is False

    assert nwGUI.openProject(prjLipsum) is True

    # Split By Chapter
    assert nwGUI.openDocument("4c4f28287af27") is True
    nwGUI.docEditor.setCursorPosition(42)
    cleanText = nwGUI.docEditor.getText()[39:86]

    # Bold
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    fmtStr = "**Pellentesque** nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:90] == fmtStr
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:86] == cleanText

    # Italic
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    fmtStr = "_Pellentesque_ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:88] == fmtStr
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:86] == cleanText

    # Strikethrough
    nwGUI.mainMenu.aFmtStrike.activate(QAction.Trigger)
    fmtStr = "~~Pellentesque~~ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:90] == fmtStr
    nwGUI.mainMenu.aFmtStrike.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:86] == cleanText

    # Should get us back to plain
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:86] == cleanText

    # Double Quotes
    nwGUI.mainMenu.aFmtDQuote.activate(QAction.Trigger)
    fmtStr = "“Pellentesque” nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:88] == fmtStr
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:86] == cleanText

    # Single Quotes
    nwGUI.mainMenu.aFmtSQuote.activate(QAction.Trigger)
    fmtStr = "‘Pellentesque’ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:88] == fmtStr
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:86] == cleanText

    # Block Formats
    # =============
    # cSpell:ignore Pellentesque erat nulla posuere commodo
    nwGUI.docEditor.setCursorPosition(42)

    # Header 1
    nwGUI.mainMenu.aFmtHead1.activate(QAction.Trigger)
    fmtStr = "# Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:88] == fmtStr

    # Header 2
    nwGUI.mainMenu.aFmtHead2.activate(QAction.Trigger)
    fmtStr = "## Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:89] == fmtStr

    # Header 3
    nwGUI.mainMenu.aFmtHead3.activate(QAction.Trigger)
    fmtStr = "### Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:90] == fmtStr

    # Header 4
    nwGUI.mainMenu.aFmtHead4.activate(QAction.Trigger)
    fmtStr = "#### Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:91] == fmtStr

    # Title Format
    nwGUI.mainMenu.aFmtTitle.activate(QAction.Trigger)
    fmtStr = "#! Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:89] == fmtStr

    # Unnumbered Chapter
    nwGUI.mainMenu.aFmtUnNum.activate(QAction.Trigger)
    fmtStr = "##! Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:90] == fmtStr

    # Clear Format
    nwGUI.mainMenu.aFmtNoFormat.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:86] == cleanText

    # Comment On
    nwGUI.mainMenu.aFmtComment.activate(QAction.Trigger)
    fmtStr = "% Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:88] == fmtStr

    # Comment Off
    nwGUI.mainMenu.aFmtComment.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:86] == cleanText

    # Check comment with no space before text
    nwGUI.docEditor.setCursorPosition(39)
    assert nwGUI.docEditor.insertText("%")
    fmtStr = "%Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:87] == fmtStr

    nwGUI.mainMenu.aFmtNoFormat.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:86] == cleanText

    # Undo/Redo
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)
    fmtStr = "%Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[39:87] == fmtStr
    nwGUI.mainMenu.aEditRedo.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:86] == cleanText

    # Cut, Copy and Paste
    nwGUI.docEditor.setCursorPosition(39)
    nwGUI.docEditor._makeSelection(QTextCursor.WordUnderCursor)

    nwGUI.mainMenu.aEditCut.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:89] == (
        " nec erat ut nulla posuere commodo. Curabitur nisi"
    )

    nwGUI.mainMenu.aEditPaste.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:89] == (
        "Pellentesque nec erat ut nulla posuere commodo. Cu"
    )

    nwGUI.docEditor.setCursorPosition(39)
    nwGUI.docEditor._makeSelection(QTextCursor.WordUnderCursor)

    nwGUI.mainMenu.aEditCopy.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:89] == (
        "Pellentesque nec erat ut nulla posuere commodo. Cu"
    )

    nwGUI.docEditor.setCursorPosition(39)
    nwGUI.mainMenu.aEditPaste.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[39:89] == (
        "PellentesquePellentesque nec erat ut nulla posuere"
    )
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)

    # Select Paragraph/All
    nwGUI.docEditor.setCursorPosition(42)
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

    nwGUI.docEditor.setCursorPosition(42)
    nwGUI.mainMenu.aSelectAll.activate(QAction.Trigger)
    theCursor = nwGUI.docEditor.textCursor()
    assert len(theCursor.selectedText()) == 1895

    # Clear the Text
    nwGUI.docEditor.clear()
    assert nwGUI.docEditor.isEmpty

    # Alignment & Indent
    # ==================

    cleanText = "A single, short paragraph.\n\n"
    nwGUI.docEditor.setPlainText(cleanText)
    nwGUI.docEditor.setCursorPosition(0)

    # Left Align
    nwGUI.mainMenu.aFmtAlignLeft.activate(QAction.Trigger)
    fmtStr = "A single, short paragraph. <<"
    assert nwGUI.docEditor.getText()[:29] == fmtStr

    # Right Align
    nwGUI.mainMenu.aFmtAlignRight.activate(QAction.Trigger)
    fmtStr = ">> A single, short paragraph."
    assert nwGUI.docEditor.getText()[:29] == fmtStr

    # Centre Align
    nwGUI.mainMenu.aFmtAlignCentre.activate(QAction.Trigger)
    fmtStr = ">> A single, short paragraph. <<"
    assert nwGUI.docEditor.getText()[:32] == fmtStr

    # Left Indent
    nwGUI.mainMenu.aFmtIndentLeft.activate(QAction.Trigger)
    fmtStr = "> A single, short paragraph."
    assert nwGUI.docEditor.getText()[:28] == fmtStr

    # Right Indent
    nwGUI.mainMenu.aFmtIndentRight.activate(QAction.Trigger)
    fmtStr = "> A single, short paragraph. <"
    assert nwGUI.docEditor.getText()[:30] == fmtStr

    # No Format
    nwGUI.mainMenu.aFmtNoFormat.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[:30] == cleanText

    # Other Checks

    # Replace Quotes
    nwGUI.docEditor.setPlainText((
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
    nwGUI.docEditor.setPlainText((
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

    nwGUI.docEditor.setPlainText((
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
    nwGUI.docEditor.setPlainText((
        "### New Text\n\n"
        "@tag: Bod\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    ))

    # Cannot Format Tag
    nwGUI.docEditor.setCursorPosition(17)
    assert not nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT)

    # Invalid Action
    nwGUI.docEditor.setCursorPosition(30)
    assert not nwGUI.docEditor._formatBlock(nwDocAction.NO_ACTION)

    # Ensure No Changes
    assert nwGUI.docEditor.getText() == (
        "### New Text\n\n"
        "@tag: Bod\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    )

    # qtbot.stop()

# END Test testGuiMenu_EditFormat


@pytest.mark.gui
def testGuiMenu_ContextMenus(qtbot, nwGUI, prjLipsum):
    """Test the context menus.
    """
    assert nwGUI.openProject(prjLipsum)
    assert nwGUI.openDocument("4c4f28287af27")

    # Editor Context Menu
    theCursor = nwGUI.docEditor.textCursor()
    theCursor.setPosition(112)
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
    theCursor.setPosition(112)
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
    assert nwGUI.docViewer.docHandle == "04468803b92e1"
    assert nwGUI.docViewer.docHeader.backButton.isEnabled()
    assert not nwGUI.docViewer.docHeader.forwardButton.isEnabled()

    qtbot.mouseClick(nwGUI.docViewer.docHeader.backButton, Qt.LeftButton)
    assert nwGUI.docViewer.docHandle == "4c4f28287af27"
    assert not nwGUI.docViewer.docHeader.backButton.isEnabled()
    assert nwGUI.docViewer.docHeader.forwardButton.isEnabled()

    qtbot.mouseClick(nwGUI.docViewer.docHeader.forwardButton, Qt.LeftButton)
    assert nwGUI.docViewer.docHandle == "04468803b92e1"
    assert nwGUI.docViewer.docHeader.backButton.isEnabled()
    assert not nwGUI.docViewer.docHeader.forwardButton.isEnabled()

    # qtbot.stop()

# END Test testGuiMenu_ContextMenus


@pytest.mark.gui
def testGuiMenu_Insert(qtbot, monkeypatch, nwGUI, fncPath, projPath, mockRnd):
    """Test the Insert menu.
    """
    buildTestProject(nwGUI, projPath)

    assert nwGUI.projView.projTree._getTreeItem(C.hSceneDoc) is not None
    assert nwGUI.openDocument(C.hSceneDoc) is True
    nwGUI.docEditor.clear()

    # Test Faulty Inserts
    assert nwGUI.docEditor.insertText("hello world")
    assert nwGUI.docEditor.getText() == "hello world"
    nwGUI.docEditor.clear()

    assert nwGUI.docEditor.insertText(nwDocInsert.NO_INSERT) is False
    assert nwGUI.docEditor.isEmpty

    assert nwGUI.docEditor.insertText(None) is False
    assert nwGUI.docEditor.isEmpty

    # qtbot.stop()

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
    assert nwGUI.docEditor.getText() == CONFIG.fmtSQuoteOpen
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteRS.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == CONFIG.fmtSQuoteClose
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteLD.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == CONFIG.fmtDQuoteOpen
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteRD.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == CONFIG.fmtDQuoteClose
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
    assert nwGUI.docEditor.getText() == nwUnicode.U_NBSP
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsThinSpace.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_THSP
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsThinNBSpace.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_THNBSP
    nwGUI.docEditor.clear()

    # Insert Keywords
    # ===============

    nwGUI.docEditor.setPlainText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.TAG_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.TAG_KEY

    nwGUI.docEditor.setPlainText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.POV_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.POV_KEY

    nwGUI.docEditor.setPlainText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.FOCUS_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.FOCUS_KEY

    nwGUI.docEditor.setPlainText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.CHAR_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.CHAR_KEY

    nwGUI.docEditor.setPlainText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.PLOT_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.PLOT_KEY

    nwGUI.docEditor.setPlainText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.TIME_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.TIME_KEY

    nwGUI.docEditor.setPlainText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.WORLD_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.WORLD_KEY

    nwGUI.docEditor.setPlainText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.OBJECT_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.OBJECT_KEY

    nwGUI.docEditor.setPlainText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.ENTITY_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.ENTITY_KEY

    nwGUI.docEditor.setPlainText("Stuff")
    nwGUI.mainMenu.mInsKWItems[nwKeyWords.CUSTOM_KEY][0].activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n%s: " % nwKeyWords.CUSTOM_KEY

    # Faulty Keyword Inserts
    assert not nwGUI.docEditor.insertKeyWord("blabla")
    with monkeypatch.context() as mp:
        mp.setattr(QTextBlock, "isValid", lambda *a, **k: False)
        assert not nwGUI.docEditor.insertKeyWord(nwKeyWords.TAG_KEY)

    nwGUI.docEditor.clear()

    # Insert Special Comments
    # =======================

    nwGUI.docEditor.setPlainText("Stuff\n")
    nwGUI.mainMenu.aInsSynopsis.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Stuff\n% Synopsis: \n"

    # Insert Break or Space
    # =====================

    nwGUI.docEditor.setPlainText("### Stuff\n")
    nwGUI.mainMenu.aInsNewPage.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "[newpage]\n### Stuff\n"

    nwGUI.docEditor.setPlainText("### Stuff\n")
    nwGUI.mainMenu.aInsVSpaceS.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "[vspace]\n### Stuff\n"

    nwGUI.docEditor.setPlainText("### Stuff\n")
    nwGUI.mainMenu.aInsVSpaceM.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "[vspace:2]\n### Stuff\n"

    nwGUI.docEditor.clear()

    # Insert Text from File
    # =====================

    nwGUI.closeDocument()

    # First, with no path
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: ("", ""))
    assert not nwGUI.importDocument()

    # Then with a path, but an invalid one
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (" ", ""))
    assert not nwGUI.importDocument()

    # Then a valid path, but bot a file that exists
    theFile = fncPath / "import.txt"
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(theFile), ""))
    assert not nwGUI.importDocument()

    # Create the file and try again, but with no target document open
    writeFile(theFile, "Foo")
    assert not nwGUI.importDocument()

    # Open the document from before, and add some text to it
    nwGUI.openDocument(C.hSceneDoc)
    nwGUI.docEditor.setPlainText("Bar")
    assert nwGUI.docEditor.getText() == "Bar"

    # The document isn't empty, so the message box should pop
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a, **k: QMessageBox.No)
        assert not nwGUI.importDocument()
        assert nwGUI.docEditor.getText() == "Bar"

    # Finally, accept the replaced text, this time we use the menu entry to trigger it
    nwGUI.mainMenu.aImportFile.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Foo"

    # Reveal File Location
    # ====================

    nwGUI.mainMenu.aFileDetails.activate(QAction.Trigger)
    path = str(projPath / "content" / "000000000000f.nwd")
    logMsg = SHARED.alert.logMessage if SHARED.alert else ""
    assert logMsg.endswith(f"File Location: {path}")

    # qtbot.stop()

# END Test testGuiMenu_Insert
