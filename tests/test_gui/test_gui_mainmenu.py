"""
novelWriter – Main GUI Main Menu Class Tester
=============================================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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

from unittest.mock import MagicMock

import pytest

from PyQt5.QtGui import QDesktopServices, QTextBlock, QTextCursor
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox

from novelwriter import CONFIG, SHARED
from novelwriter.constants import nwKeyWords, nwShortcode, nwStats, nwUnicode
from novelwriter.enum import nwDocAction, nwDocInsert
from novelwriter.gui.doceditor import GuiDocEditor
from novelwriter.types import QtKeepAnchor, QtMoveRight

from tests.tools import C, buildTestProject, writeFile


@pytest.mark.gui
def testGuiMainMenu_Slots(qtbot, monkeypatch, nwGUI, projPath):
    """Test the main menu slots."""
    buildTestProject(nwGUI, projPath)

    # Open Manual
    with monkeypatch.context() as mp:
        openUrl = MagicMock()
        mp.setattr(QDesktopServices, "openUrl", openUrl)
        CONFIG.pdfDocs = projPath / "manual.pdf"
        CONFIG.pdfDocs.touch()
        nwGUI.mainMenu._openUserManualFile()
        assert openUrl.called is True
        assert "manual.pdf" in openUrl.call_args[0][0].url()

    # Spell Checking
    assert SHARED.project.data.spellLang is None
    nwGUI.mainMenu._changeSpelling("en")
    assert SHARED.project.data.spellLang == "en"


@pytest.mark.gui
def testGuiMainMenu_EditFormat(qtbot, monkeypatch, nwGUI, prjLipsum):
    """Test the main menu Edit and Format entries."""
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *a: True)
    mainMenu = nwGUI.mainMenu
    docEditor = nwGUI.docEditor

    # Test Document Action with No Project
    assert docEditor.docAction(nwDocAction.COPY) is False

    assert nwGUI.openProject(prjLipsum) is True

    # Split By Chapter
    assert nwGUI.openDocument("4c4f28287af27") is True
    docEditor.setCursorPosition(57)
    cleanText = docEditor.getText()[54:101]

    # Bold
    mainMenu.aFmtBold.activate(QAction.ActionEvent.Trigger)
    fmtStr = "**Pellentesque** nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:105] == fmtStr
    mainMenu.aFmtBold.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:101] == cleanText

    # Italic
    mainMenu.aFmtItalic.activate(QAction.ActionEvent.Trigger)
    fmtStr = "_Pellentesque_ nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:103] == fmtStr
    mainMenu.aFmtItalic.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:101] == cleanText

    # Strikethrough
    mainMenu.aFmtStrike.activate(QAction.ActionEvent.Trigger)
    fmtStr = "~~Pellentesque~~ nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:105] == fmtStr
    mainMenu.aFmtStrike.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:101] == cleanText

    # Should get us back to plain
    mainMenu.aFmtBold.activate(QAction.ActionEvent.Trigger)
    mainMenu.aFmtItalic.activate(QAction.ActionEvent.Trigger)
    mainMenu.aFmtItalic.activate(QAction.ActionEvent.Trigger)
    mainMenu.aFmtBold.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:101] == cleanText

    # Double Quotes
    mainMenu.aFmtDQuote.activate(QAction.ActionEvent.Trigger)
    fmtStr = "“Pellentesque” nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:103] == fmtStr
    mainMenu.aEditUndo.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:101] == cleanText

    # Single Quotes
    mainMenu.aFmtSQuote.activate(QAction.ActionEvent.Trigger)
    fmtStr = "‘Pellentesque’ nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:103] == fmtStr
    mainMenu.aEditUndo.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:101] == cleanText

    # Block Formats
    # =============
    # cSpell:ignore Pellentesque erat nulla posuere commodo
    docEditor.setCursorPosition(57)

    # Header 1
    mainMenu.aFmtHead1.activate(QAction.ActionEvent.Trigger)
    fmtStr = "# Pellentesque nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:103] == fmtStr

    # Header 2
    mainMenu.aFmtHead2.activate(QAction.ActionEvent.Trigger)
    fmtStr = "## Pellentesque nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:104] == fmtStr

    # Header 3
    mainMenu.aFmtHead3.activate(QAction.ActionEvent.Trigger)
    fmtStr = "### Pellentesque nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:105] == fmtStr

    # Header 4
    mainMenu.aFmtHead4.activate(QAction.ActionEvent.Trigger)
    fmtStr = "#### Pellentesque nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:106] == fmtStr

    # Title Format
    mainMenu.aFmtTitle.activate(QAction.ActionEvent.Trigger)
    fmtStr = "#! Pellentesque nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:104] == fmtStr

    # Unnumbered Chapter
    mainMenu.aFmtUnNum.activate(QAction.ActionEvent.Trigger)
    fmtStr = "##! Pellentesque nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:105] == fmtStr

    # Hard Scene
    mainMenu.aFmtHardSc.activate(QAction.ActionEvent.Trigger)
    fmtStr = "###! Pellentesque nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:106] == fmtStr

    # Clear Format
    mainMenu.aFmtNoFormat.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:101] == cleanText

    # Comment On
    mainMenu.aFmtComment.activate(QAction.ActionEvent.Trigger)
    fmtStr = "% Pellentesque nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:103] == fmtStr

    # Comment Off
    mainMenu.aFmtComment.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:101] == cleanText

    # Check comment with no space before text
    docEditor.setCursorPosition(54)
    docEditor.insertText("%")
    fmtStr = "%Pellentesque nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:102] == fmtStr

    mainMenu.aFmtNoFormat.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:101] == cleanText

    # Undo/Redo
    mainMenu.aEditUndo.activate(QAction.ActionEvent.Trigger)
    fmtStr = "%Pellentesque nec erat ut nulla posuere commodo."
    assert docEditor.getText()[54:102] == fmtStr
    mainMenu.aEditRedo.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:101] == cleanText

    # Cut, Copy and Paste
    docEditor.setCursorPosition(54)
    docEditor._makeSelection(QTextCursor.WordUnderCursor)

    mainMenu.aEditCut.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:104] == (
        " nec erat ut nulla posuere commodo. Curabitur nisi"
    )

    mainMenu.aEditPaste.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:104] == (
        "Pellentesque nec erat ut nulla posuere commodo. Cu"
    )

    docEditor.setCursorPosition(54)
    docEditor._makeSelection(QTextCursor.WordUnderCursor)

    mainMenu.aEditCopy.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:104] == (
        "Pellentesque nec erat ut nulla posuere commodo. Cu"
    )

    docEditor.setCursorPosition(54)
    mainMenu.aEditPaste.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[54:104] == (
        "PellentesquePellentesque nec erat ut nulla posuere"
    )
    mainMenu.aEditUndo.activate(QAction.ActionEvent.Trigger)

    # Select Paragraph/All
    docEditor.setCursorPosition(57)
    mainMenu.aSelectPar.activate(QAction.ActionEvent.Trigger)
    cursor = docEditor.textCursor()
    assert cursor.selectedText() == (
        "Pellentesque nec erat ut nulla posuere commodo. Curabitur nisi augue, imperdiet et porta "
        "imperdiet, efficitur id leo. Cras finibus arcu at nibh commodo congue. Proin suscipit "
        "placerat condimentum. Aenean ante enim, cursus id lorem a, blandit venenatis nibh. "
        "Maecenas suscipit porta elit, sit amet porta felis porttitor eu. Sed a dui nibh. "
        "Phasellus sed faucibus dui. Pellentesque felis nulla, ultrices non efficitur quis, "
        "rutrum id mi. Mauris tempus auctor nisl, in bibendum enim pellentesque sit amet. Proin "
        "nunc lacus, imperdiet nec posuere ac, interdum non lectus."
    )

    docEditor.setCursorPosition(57)
    mainMenu.aSelectAll.activate(QAction.ActionEvent.Trigger)
    cursor = docEditor.textCursor()
    assert len(cursor.selectedText()) == 1910

    # Clear the Text
    docEditor.clear()
    assert docEditor.isEmpty

    # Alignment & Indent
    # ==================

    cleanText = "A single, short paragraph.\n\n"
    docEditor.setPlainText(cleanText)
    docEditor.setCursorPosition(0)

    # Left Align
    mainMenu.aFmtAlignLeft.activate(QAction.ActionEvent.Trigger)
    fmtStr = "A single, short paragraph. <<"
    assert docEditor.getText()[:29] == fmtStr

    # Right Align
    mainMenu.aFmtAlignRight.activate(QAction.ActionEvent.Trigger)
    fmtStr = ">> A single, short paragraph."
    assert docEditor.getText()[:29] == fmtStr

    # Centre Align
    mainMenu.aFmtAlignCentre.activate(QAction.ActionEvent.Trigger)
    fmtStr = ">> A single, short paragraph. <<"
    assert docEditor.getText()[:32] == fmtStr

    # Left Indent
    mainMenu.aFmtIndentLeft.activate(QAction.ActionEvent.Trigger)
    fmtStr = "> A single, short paragraph."
    assert docEditor.getText()[:28] == fmtStr

    # Right Indent
    mainMenu.aFmtIndentRight.activate(QAction.ActionEvent.Trigger)
    fmtStr = "> A single, short paragraph. <"
    assert docEditor.getText()[:30] == fmtStr

    # No Format
    mainMenu.aFmtNoFormat.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[:30] == cleanText

    # Other Checks

    # Replace Quotes
    docEditor.setPlainText((
        "### New Text\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    ))

    mainMenu.aSelectAll.activate(QAction.ActionEvent.Trigger)
    mainMenu.aFmtReplSng.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == (
        "### New Text\n\n"
        "Text with ‘single’ quotes and ‘tricky stuff’s’.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    )

    mainMenu.aSelectAll.activate(QAction.ActionEvent.Trigger)
    mainMenu.aFmtReplDbl.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == (
        "### New Text\n\n"
        "Text with ‘single’ quotes and ‘tricky stuff’s’.\n\n"
        "Also text with “double” quotes which are “less tricky”.\n\n"
    )

    # Remove in-paragraph line breaks
    docEditor.setPlainText((
        "### New Text\n\n"
        "@char: Someone\n"
        "@location: Somewhere\n\n"
        "% Some comment ...\n\n"
        "Here is some text\non multiple\nlines.\n\n"
        "With another paragraph\nhere."
    ))
    mainMenu.aFmtRmBreaks.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == (
        "### New Text\n\n"
        "@char: Someone\n"
        "@location: Somewhere\n\n"
        "% Some comment ...\n\n"
        "Here is some text on multiple lines.\n\n"
        "With another paragraph here.\n"
    )

    docEditor.setPlainText((
        "### New Text\n\n"
        "@char: Someone\n"
        "@location: Somewhere\n\n"
        "% Some comment ...\n\n"
        "Here is some text\non multiple\nlines.\n\n"
        "With another paragraph\nhere."
    ))
    cursor = docEditor.textCursor()
    cursor.setPosition(74)
    cursor.movePosition(QtMoveRight, QtKeepAnchor, 29)
    docEditor.setTextCursor(cursor)
    mainMenu.aFmtRmBreaks.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == (
        "### New Text\n\n"
        "@char: Someone\n"
        "@location: Somewhere\n\n"
        "% Some comment ...\n\n"
        "Here is some text on multiple lines.\n\n"
        "With another paragraph\nhere."
    )

    # Test Invalid Document Action
    assert not docEditor.docAction(nwDocAction.NO_ACTION)

    # Test Invalid Formats
    docEditor.setPlainText((
        "### New Text\n\n"
        "@tag: Bod\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    ))

    # Cannot Format Tag
    docEditor.setCursorPosition(17)
    assert not docEditor._formatBlock(nwDocAction.BLOCK_TXT)

    # Invalid Action
    docEditor.setCursorPosition(30)
    assert not docEditor._formatBlock(nwDocAction.NO_ACTION)

    # Ensure No Changes
    assert docEditor.getText() == (
        "### New Text\n\n"
        "@tag: Bod\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    )

    # qtbot.stop()


@pytest.mark.gui
def testGuiMainMenu_Insert(qtbot, monkeypatch, nwGUI, fncPath, projPath, mockRnd):
    """Test the Insert menu."""
    buildTestProject(nwGUI, projPath)

    assert nwGUI.openDocument(C.hSceneDoc) is True
    mainMenu = nwGUI.mainMenu
    docEditor = nwGUI.docEditor
    docEditor.clear()

    # Test Faulty Inserts
    docEditor.insertText("hello world")
    assert docEditor.getText() == "hello world"
    docEditor.clear()

    docEditor.insertText(nwDocInsert.NO_INSERT)
    assert docEditor.isEmpty

    docEditor.insertText(None)
    assert docEditor.isEmpty

    # qtbot.stop()
    docEditor.clear()

    # Check Menu Entries
    mainMenu.aInsENDash.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_ENDASH
    docEditor.clear()

    mainMenu.aInsEMDash.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_EMDASH
    docEditor.clear()

    mainMenu.aInsHorBar.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_HBAR
    docEditor.clear()

    mainMenu.aInsFigDash.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_FGDASH
    docEditor.clear()

    mainMenu.aInsQuoteLS.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == CONFIG.fmtSQuoteOpen
    docEditor.clear()

    mainMenu.aInsQuoteRS.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == CONFIG.fmtSQuoteClose
    docEditor.clear()

    mainMenu.aInsQuoteLD.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == CONFIG.fmtDQuoteOpen
    docEditor.clear()

    mainMenu.aInsQuoteRD.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == CONFIG.fmtDQuoteClose
    docEditor.clear()

    mainMenu.aInsMSApos.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_MAPOS
    docEditor.clear()

    mainMenu.aInsEllipsis.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_HELLIP
    docEditor.clear()

    mainMenu.aInsPrime.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_PRIME
    docEditor.clear()

    mainMenu.aInsDPrime.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_DPRIME
    docEditor.clear()

    mainMenu.aInsBullet.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_BULL
    docEditor.clear()

    mainMenu.aInsHyBull.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_HYBULL
    docEditor.clear()

    mainMenu.aInsFlower.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_FLOWER
    docEditor.clear()

    mainMenu.aInsPerMille.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_PERMIL
    docEditor.clear()

    mainMenu.aInsDegree.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_DEGREE
    docEditor.clear()

    mainMenu.aInsMinus.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_MINUS
    docEditor.clear()

    mainMenu.aInsTimes.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_TIMES
    docEditor.clear()

    mainMenu.aInsDivide.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_DIVIDE
    docEditor.clear()

    mainMenu.aInsNBSpace.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_NBSP
    docEditor.clear()

    mainMenu.aInsThinSpace.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_THSP
    docEditor.clear()

    mainMenu.aInsThinNBSpace.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == nwUnicode.U_THNBSP
    docEditor.clear()

    # Insert Keywords
    # ===============

    for action, key in zip(mainMenu.mInsKeywords.actions(), nwKeyWords.ALL_KEYS):
        docEditor.setPlainText("Stuff")
        action.activate(QAction.ActionEvent.Trigger)
        assert docEditor.getText() == f"Stuff\n{key}: "

    # Faulty Keyword Inserts
    assert not docEditor.insertKeyWord("blabla")
    with monkeypatch.context() as mp:
        mp.setattr(QTextBlock, "isValid", lambda *a, **k: False)
        assert not docEditor.insertKeyWord(nwKeyWords.TAG_KEY)

    # Insert Fields
    # =============

    for action, field in zip(mainMenu.mInsField.actions(), nwStats.ALL_FIELDS):
        value = nwShortcode.FIELD_VALUE.format(field)
        docEditor.setPlainText("Stuff ")
        docEditor.setCursorPosition(6)
        action.activate(QAction.ActionEvent.Trigger)
        assert docEditor.getText() == f"Stuff {value}"

    docEditor.clear()

    # Insert Special Comments
    # =======================

    docEditor.setPlainText("Stuff\n")
    mainMenu.aInsSynopsis.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == "Stuff\n%Synopsis: \n"

    docEditor.setPlainText("Stuff\n")
    mainMenu.aInsShort.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == "Stuff\n%Short: \n"

    # Breaks and Vertical Space
    # =========================

    docEditor.setPlainText("### Stuff\n")
    mainMenu.aInsNewPage.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == "[newpage]\n### Stuff\n"

    docEditor.setPlainText("Line OneLine Two\n")
    docEditor.setCursorPosition(8)
    mainMenu.aInsLineBreak.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == "Line One[br]Line Two\n"

    docEditor.setPlainText("### Stuff\n")
    mainMenu.aInsVSpaceS.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == "[vspace]\n### Stuff\n"

    docEditor.setPlainText("### Stuff\n")
    mainMenu.aInsVSpaceM.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == "[vspace:2]\n### Stuff\n"

    docEditor.clear()

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
    iFile = fncPath / "import.txt"
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(iFile), ""))
    assert not nwGUI.importDocument()

    # Create the file and try again, but with no target document open
    writeFile(iFile, "Foo")
    assert not nwGUI.importDocument()

    # Open the document from before, and add some text to it
    nwGUI.openDocument(C.hSceneDoc)
    docEditor.setPlainText("Bar")
    assert docEditor.getText() == "Bar"

    # The document isn't empty, so the message box should pop
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a, **k: QMessageBox.StandardButton.No)
        assert not nwGUI.importDocument()
        assert docEditor.getText() == "Bar"

    # Finally, accept the replaced text, this time we use the menu entry to trigger it
    mainMenu.aImportFile.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText() == "Foo"

    # Reveal File Location
    # ====================

    mainMenu.aFileDetails.activate(QAction.ActionEvent.Trigger)
    path = str(projPath / "content" / "000000000000f.nwd")
    assert SHARED.lastAlert.endswith(f"File Location: {path}")

    # qtbot.stop()
