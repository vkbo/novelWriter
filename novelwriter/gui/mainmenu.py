"""
novelWriter – GUI Main Menu
===========================

File History:
Created: 2019-04-27 [0.0.1] GuiMainMenu

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

import logging

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAction, QMenuBar

from novelwriter import CONFIG, SHARED
from novelwriter.common import openExternalPath, qtLambda
from novelwriter.constants import (
    nwConst, nwKeyWords, nwLabels, nwShortcode, nwStats, nwStyles, nwUnicode,
    trConst
)
from novelwriter.enum import nwDocAction, nwDocInsert, nwFocus, nwView
from novelwriter.extensions.eventfilters import StatusTipFilter

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiMainMenu(QMenuBar):
    """The GUI main menu. All menu actions are defined here with the
    main menu as the owner. Each widget that need them elsewhere need to
    add them from this class.
    """

    requestDocAction = pyqtSignal(nwDocAction)
    requestDocInsert = pyqtSignal(nwDocInsert)
    requestDocInsertText = pyqtSignal(str)
    requestDocKeyWordInsert = pyqtSignal(str)
    requestFocusChange = pyqtSignal(nwFocus)
    requestViewChange = pyqtSignal(nwView)

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiMainMenu")

        self.mainGui = mainGui

        # Build Menu
        self._buildProjectMenu()
        self._buildDocumentMenu()
        self._buildEditMenu()
        self._buildViewMenu()
        self._buildInsertMenu()
        self._buildFormatMenu()
        self._buildSearchMenu()
        self._buildToolsMenu()
        self._buildHelpMenu()

        self.installEventFilter(StatusTipFilter(mainGui))

        logger.debug("Ready: GuiMainMenu")

        return

    ##
    #  Public Slots
    ##

    @pyqtSlot(bool)
    def setSpellCheckState(self, state: bool) -> None:
        """Forward spell check check state to its action."""
        self.aSpellCheck.setChecked(state)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _toggleSpellCheck(self) -> None:
        """Toggle spell checking. The active status of the spell check
        flag is handled by the document editor class, so we make no
        decision, just pass a None to the function and let it decide.
        """
        self.mainGui.docEditor.toggleSpellCheck(None)
        return

    @pyqtSlot()
    def _openUserManualFile(self) -> None:
        """Open the documentation in PDF format."""
        if isinstance(CONFIG.pdfDocs, Path):
            openExternalPath(CONFIG.pdfDocs)
        return

    @pyqtSlot(str)
    def _changeSpelling(self, language: str) -> None:
        """Change the spell check language."""
        SHARED.project.data.setSpellLang(language)
        SHARED.updateSpellCheckLanguage()
        return

    ##
    #  Internal Functions
    ##

    def _buildProjectMenu(self) -> None:
        """Assemble the Project menu."""
        # Project
        self.projMenu = self.addMenu(self.tr("&Project"))

        # Project > Create or Open Project
        self.aOpenProject = self.projMenu.addAction(self.tr("Create or Open Project"))
        self.aOpenProject.setShortcut("Ctrl+Shift+O")
        self.aOpenProject.triggered.connect(self.mainGui.showWelcomeDialog)

        # Project > Save Project
        self.aSaveProject = self.projMenu.addAction(self.tr("Save Project"))
        self.aSaveProject.setShortcut("Ctrl+Shift+S")
        self.aSaveProject.triggered.connect(qtLambda(self.mainGui.saveProject))
        self.mainGui.addAction(self.aSaveProject)

        # Project > Close Project
        self.aCloseProject = self.projMenu.addAction(self.tr("Close Project"))
        self.aCloseProject.setShortcut("Ctrl+Shift+W")
        self.aCloseProject.triggered.connect(qtLambda(self.mainGui.closeProject, False))

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Project Settings
        self.aProjectSettings = self.projMenu.addAction(self.tr("Project Settings"))
        self.aProjectSettings.setShortcut("Ctrl+Shift+,")
        self.aProjectSettings.triggered.connect(self.mainGui.showProjectSettingsDialog)

        # Project > Novel Details
        self.aNovelDetails = self.projMenu.addAction(self.tr("Novel Details"))
        self.aNovelDetails.setShortcut("Shift+F6")
        self.aNovelDetails.triggered.connect(self.mainGui.showNovelDetailsDialog)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Edit
        self.aEditItem = self.projMenu.addAction(self.tr("Rename Item"))
        self.aEditItem.setShortcut("F2")
        self.aEditItem.triggered.connect(qtLambda(self.mainGui.projView.renameTreeItem, None))
        self.mainGui.addAction(self.aEditItem)

        # Project > Delete
        self.aDeleteItem = self.projMenu.addAction(self.tr("Delete Item"))
        self.aDeleteItem.setShortcut("Ctrl+Shift+Del")  # Cannot be Ctrl+Del, see #629
        self.aDeleteItem.triggered.connect(qtLambda(self.mainGui.projView.requestDeleteItem, None))

        # Project > Empty Trash
        self.aEmptyTrash = self.projMenu.addAction(self.tr("Empty Trash"))
        self.aEmptyTrash.triggered.connect(qtLambda(self.mainGui.projView.emptyTrash))

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Exit
        self.aExitNW = self.projMenu.addAction(self.tr("Exit"))
        self.aExitNW.setShortcut("Ctrl+Q")
        self.aExitNW.setMenuRole(QAction.MenuRole.QuitRole)
        self.aExitNW.triggered.connect(qtLambda(self.mainGui.closeMain))
        self.mainGui.addAction(self.aExitNW)

        return

    def _buildDocumentMenu(self) -> None:
        """Assemble the Document menu."""
        # Document
        self.docuMenu = self.addMenu(self.tr("&Document"))

        # Document > Open
        self.aOpenDoc = self.docuMenu.addAction(self.tr("Open Document"))
        self.aOpenDoc.setShortcut("Ctrl+O")
        self.aOpenDoc.triggered.connect(self.mainGui.openSelectedItem)

        # Document > Save
        self.aSaveDoc = self.docuMenu.addAction(self.tr("Save Document"))
        self.aSaveDoc.setShortcut("Ctrl+S")
        self.aSaveDoc.triggered.connect(self.mainGui.forceSaveDocument)
        self.mainGui.addAction(self.aSaveDoc)

        # Document > Close
        self.aCloseDoc = self.docuMenu.addAction(self.tr("Close Document"))
        self.aCloseDoc.setShortcut("Ctrl+W")
        self.aCloseDoc.triggered.connect(self.mainGui.closeDocEditor)
        self.mainGui.addAction(self.aCloseDoc)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Preview
        self.aViewDoc = self.docuMenu.addAction(self.tr("View Document"))
        self.aViewDoc.setShortcut("Ctrl+R")
        self.aViewDoc.triggered.connect(qtLambda(self.mainGui.viewDocument, None))

        # Document > Close Preview
        self.aCloseView = self.docuMenu.addAction(self.tr("Close Document View"))
        self.aCloseView.setShortcut("Ctrl+Shift+R")
        self.aCloseView.triggered.connect(self.mainGui.closeDocViewer)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Show File Details
        self.aFileDetails = self.docuMenu.addAction(self.tr("Show File Details"))
        self.aFileDetails.triggered.connect(qtLambda(self.mainGui.docEditor.revealLocation))

        # Document > Import From File
        self.aImportFile = self.docuMenu.addAction(self.tr("Import Text from File"))
        self.aImportFile.triggered.connect(qtLambda(self.mainGui.importDocument))

        return

    def _buildEditMenu(self) -> None:
        """Assemble the Edit menu."""
        # Edit
        self.editMenu = self.addMenu(self.tr("&Edit"))

        # Edit > Undo
        self.aEditUndo = self.editMenu.addAction(self.tr("Undo"))
        self.aEditUndo.setShortcut("Ctrl+Z")
        self.aEditUndo.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.UNDO)
        )
        self.mainGui.addAction(self.aEditUndo)

        # Edit > Redo
        self.aEditRedo = self.editMenu.addAction(self.tr("Redo"))
        self.aEditRedo.setShortcut("Ctrl+Y")
        self.aEditRedo.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.REDO)
        )
        self.mainGui.addAction(self.aEditRedo)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Cut
        self.aEditCut = self.editMenu.addAction(self.tr("Cut"))
        self.aEditCut.setShortcut("Ctrl+X")
        self.aEditCut.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.CUT)
        )
        self.mainGui.addAction(self.aEditCut)

        # Edit > Copy
        self.aEditCopy = self.editMenu.addAction(self.tr("Copy"))
        self.aEditCopy.setShortcut("Ctrl+C")
        self.aEditCopy.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.COPY)
        )
        self.mainGui.addAction(self.aEditCopy)

        # Edit > Paste
        self.aEditPaste = self.editMenu.addAction(self.tr("Paste"))
        self.aEditPaste.setShortcut("Ctrl+V")
        self.aEditPaste.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.PASTE)
        )
        self.mainGui.addAction(self.aEditPaste)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Select All
        self.aSelectAll = self.editMenu.addAction(self.tr("Select All"))
        self.aSelectAll.setShortcut("Ctrl+A")
        self.aSelectAll.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SEL_ALL)
        )
        self.mainGui.addAction(self.aSelectAll)

        # Edit > Select Paragraph
        self.aSelectPar = self.editMenu.addAction(self.tr("Select Paragraph"))
        self.aSelectPar.setShortcut("Ctrl+Shift+A")
        self.aSelectPar.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SEL_PARA)
        )
        self.mainGui.addAction(self.aSelectPar)

        return

    def _buildViewMenu(self) -> None:
        """Assemble the View menu."""
        # View
        self.viewMenu = self.addMenu(self.tr("&View"))

        # View > TreeView
        self.aFocusTree = self.viewMenu.addAction(self.tr("Go to Tree View"))
        self.aFocusTree.setShortcut("Ctrl+T")
        self.aFocusTree.triggered.connect(
            lambda: self.requestFocusChange.emit(nwFocus.TREE)
        )

        # View > Document Editor
        self.aFocusDocument = self.viewMenu.addAction(self.tr("Go to Document"))
        self.aFocusDocument.setShortcut("Ctrl+E")
        self.aFocusDocument.triggered.connect(
            lambda: self.requestFocusChange.emit(nwFocus.DOCUMENT)
        )

        # View > Outline
        self.aFocusOutline = self.viewMenu.addAction(self.tr("Go to Outline"))
        self.aFocusOutline.setShortcut("Ctrl+Shift+T")
        self.aFocusOutline.triggered.connect(
            lambda: self.requestFocusChange.emit(nwFocus.OUTLINE)
        )

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Go Backward
        self.aViewPrev = self.viewMenu.addAction(self.tr("Navigate Backward"))
        self.aViewPrev.setShortcut("Alt+Left")
        self.aViewPrev.triggered.connect(self.mainGui.docViewer.navBackward)

        # View > Go Forward
        self.aViewNext = self.viewMenu.addAction(self.tr("Navigate Forward"))
        self.aViewNext.setShortcut("Alt+Right")
        self.aViewNext.triggered.connect(self.mainGui.docViewer.navForward)

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Focus Mode
        self.aFocusMode = self.viewMenu.addAction(self.tr("Focus Mode"))
        self.aFocusMode.setShortcut("F8")
        self.aFocusMode.triggered.connect(self.mainGui.toggleFocusMode)
        self.mainGui.addAction(self.aFocusMode)

        # View > Toggle Full Screen
        self.aFullScreen = self.viewMenu.addAction(self.tr("Full Screen Mode"))
        self.aFullScreen.setShortcut("F11")
        self.aFullScreen.triggered.connect(self.mainGui.toggleFullScreenMode)
        self.mainGui.addAction(self.aFullScreen)

        return

    def _buildInsertMenu(self) -> None:
        """Assemble the Insert menu."""
        # Insert
        self.insMenu = self.addMenu(self.tr("&Insert"))

        # Insert > Dashes and Dots
        self.mInsDashes = self.insMenu.addMenu(self.tr("Dashes"))

        # Insert > Short Dash
        self.aInsENDash = self.mInsDashes.addAction(self.tr("Short Dash"))
        self.aInsENDash.setShortcut("Ctrl+K, -")
        self.aInsENDash.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_ENDASH)
        )
        self.mainGui.addAction(self.aInsENDash)

        # Insert > Long Dash
        self.aInsEMDash = self.mInsDashes.addAction(self.tr("Long Dash"))
        self.aInsEMDash.setShortcut("Ctrl+K, _")
        self.aInsEMDash.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_EMDASH)
        )
        self.mainGui.addAction(self.aInsEMDash)

        # Insert > Long Dash
        self.aInsHorBar = self.mInsDashes.addAction(self.tr("Horizontal Bar"))
        self.aInsHorBar.setShortcut("Ctrl+K, Ctrl+_")
        self.aInsHorBar.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_HBAR)
        )
        self.mainGui.addAction(self.aInsHorBar)

        # Insert > Figure Dash
        self.aInsFigDash = self.mInsDashes.addAction(self.tr("Figure Dash"))
        self.aInsFigDash.setShortcut("Ctrl+K, ~")
        self.aInsFigDash.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_FGDASH)
        )
        self.mainGui.addAction(self.aInsFigDash)

        # Insert > Quote Marks
        self.mInsQuotes = self.insMenu.addMenu(self.tr("Quote Marks"))

        # Insert > Left Single Quote
        self.aInsQuoteLS = self.mInsQuotes.addAction(self.tr("Left Single Quote"))
        self.aInsQuoteLS.setShortcut("Ctrl+K, 1")
        self.aInsQuoteLS.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.QUOTE_LS)
        )
        self.mainGui.addAction(self.aInsQuoteLS)

        # Insert > Right Single Quote
        self.aInsQuoteRS = self.mInsQuotes.addAction(self.tr("Right Single Quote"))
        self.aInsQuoteRS.setShortcut("Ctrl+K, 2")
        self.aInsQuoteRS.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.QUOTE_RS)
        )
        self.mainGui.addAction(self.aInsQuoteRS)

        # Insert > Left Double Quote
        self.aInsQuoteLD = self.mInsQuotes.addAction(self.tr("Left Double Quote"))
        self.aInsQuoteLD.setShortcut("Ctrl+K, 3")
        self.aInsQuoteLD.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.QUOTE_LD)
        )
        self.mainGui.addAction(self.aInsQuoteLD)

        # Insert > Right Double Quote
        self.aInsQuoteRD = self.mInsQuotes.addAction(self.tr("Right Double Quote"))
        self.aInsQuoteRD.setShortcut("Ctrl+K, 4")
        self.aInsQuoteRD.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.QUOTE_RD)
        )
        self.mainGui.addAction(self.aInsQuoteRD)

        # Insert > Alternative Apostrophe
        self.aInsMSApos = self.mInsQuotes.addAction(self.tr("Alternative Apostrophe"))
        self.aInsMSApos.setShortcut("Ctrl+K, '")
        self.aInsMSApos.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_MAPOS)
        )
        self.mainGui.addAction(self.aInsMSApos)

        # Insert > Symbols
        self.mInsPunct = self.insMenu.addMenu(self.tr("General Punctuation"))

        # Insert > Ellipsis
        self.aInsEllipsis = self.mInsPunct.addAction(self.tr("Ellipsis"))
        self.aInsEllipsis.setShortcut("Ctrl+K, .")
        self.aInsEllipsis.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_HELLIP)
        )
        self.mainGui.addAction(self.aInsEllipsis)

        # Insert > Prime
        self.aInsPrime = self.mInsPunct.addAction(self.tr("Prime"))
        self.aInsPrime.setShortcut("Ctrl+K, Ctrl+'")
        self.aInsPrime.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_PRIME)
        )
        self.mainGui.addAction(self.aInsPrime)

        # Insert > Double Prime
        self.aInsDPrime = self.mInsPunct.addAction(self.tr("Double Prime"))
        self.aInsDPrime.setShortcut("Ctrl+K, Ctrl+\"")
        self.aInsDPrime.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_DPRIME)
        )
        self.mainGui.addAction(self.aInsDPrime)

        # Insert > White Spaces
        self.mInsSpace = self.insMenu.addMenu(self.tr("White Spaces"))

        # Insert > Non-Breaking Space
        self.aInsNBSpace = self.mInsSpace.addAction(self.tr("Non-Breaking Space"))
        self.aInsNBSpace.setShortcut("Ctrl+K, Space")
        self.aInsNBSpace.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_NBSP)
        )
        self.mainGui.addAction(self.aInsNBSpace)

        # Insert > Thin Space
        self.aInsThinSpace = self.mInsSpace.addAction(self.tr("Thin Space"))
        self.aInsThinSpace.setShortcut("Ctrl+K, Shift+Space")
        self.aInsThinSpace.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_THSP)
        )
        self.mainGui.addAction(self.aInsThinSpace)

        # Insert > Thin Non-Breaking Space
        self.aInsThinNBSpace = self.mInsSpace.addAction(self.tr("Thin Non-Breaking Space"))
        self.aInsThinNBSpace.setShortcut("Ctrl+K, Ctrl+Space")
        self.aInsThinNBSpace.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_THNBSP)
        )
        self.mainGui.addAction(self.aInsThinNBSpace)

        # Insert > Symbols
        self.mInsSymbol = self.insMenu.addMenu(self.tr("Other Symbols"))

        # Insert > List Bullet
        self.aInsBullet = self.mInsSymbol.addAction(self.tr("List Bullet"))
        self.aInsBullet.setShortcut("Ctrl+K, *")
        self.aInsBullet.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_BULL)
        )
        self.mainGui.addAction(self.aInsBullet)

        # Insert > Hyphen Bullet
        self.aInsHyBull = self.mInsSymbol.addAction(self.tr("Hyphen Bullet"))
        self.aInsHyBull.setShortcut("Ctrl+K, Ctrl+-")
        self.aInsHyBull.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_HYBULL)
        )
        self.mainGui.addAction(self.aInsHyBull)

        # Insert > Flower Mark
        self.aInsFlower = self.mInsSymbol.addAction(self.tr("Flower Mark"))
        self.aInsFlower.setShortcut("Ctrl+K, Ctrl+*")
        self.aInsFlower.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_FLOWER)
        )
        self.mainGui.addAction(self.aInsFlower)

        # Insert > Per Mille
        self.aInsPerMille = self.mInsSymbol.addAction(self.tr("Per Mille"))
        self.aInsPerMille.setShortcut("Ctrl+K, %")
        self.aInsPerMille.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_PERMIL)
        )
        self.mainGui.addAction(self.aInsPerMille)

        # Insert > Degree Symbol
        self.aInsDegree = self.mInsSymbol.addAction(self.tr("Degree Symbol"))
        self.aInsDegree.setShortcut("Ctrl+K, Ctrl+O")
        self.aInsDegree.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_DEGREE)
        )
        self.mainGui.addAction(self.aInsDegree)

        # Insert > Minus Sign
        self.aInsMinus = self.mInsSymbol.addAction(self.tr("Minus Sign"))
        self.aInsMinus.setShortcut("Ctrl+K, Ctrl+M")
        self.aInsMinus.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_MINUS)
        )
        self.mainGui.addAction(self.aInsMinus)

        # Insert > Times Sign
        self.aInsTimes = self.mInsSymbol.addAction(self.tr("Times Sign"))
        self.aInsTimes.setShortcut("Ctrl+K, Ctrl+X")
        self.aInsTimes.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_TIMES)
        )
        self.mainGui.addAction(self.aInsTimes)

        # Insert > Division
        self.aInsDivide = self.mInsSymbol.addAction(self.tr("Division Sign"))
        self.aInsDivide.setShortcut("Ctrl+K, Ctrl+D")
        self.aInsDivide.triggered.connect(
            lambda: self.requestDocInsertText.emit(nwUnicode.U_DIVIDE)
        )
        self.mainGui.addAction(self.aInsDivide)

        # Insert > Tags and References
        self.mInsKeywords = self.insMenu.addMenu(self.tr("Tags and References"))
        for key in nwKeyWords.ALL_KEYS:
            action = self.mInsKeywords.addAction(trConst(nwLabels.KEY_NAME[key]))
            action.setShortcut(nwLabels.KEY_SHORTCUT[key])
            action.triggered.connect(qtLambda(self.requestDocKeyWordInsert.emit, key))
            self.mainGui.addAction(action)

        # Insert > Special Comments
        self.mInsComments = self.insMenu.addMenu(self.tr("Special Comments"))

        # Insert > Synopsis Comment
        self.aInsSynopsis = self.mInsComments.addAction(self.tr("Synopsis Comment"))
        self.aInsSynopsis.setShortcut("Ctrl+K, S")
        self.aInsSynopsis.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.SYNOPSIS)
        )
        self.mainGui.addAction(self.aInsSynopsis)

        # Insert > Short Description Comment
        self.aInsShort = self.mInsComments.addAction(self.tr("Short Description Comment"))
        self.aInsShort.setShortcut("Ctrl+K, H")
        self.aInsShort.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.SHORT)
        )
        self.mainGui.addAction(self.aInsShort)

        # Insert > Word/Character Count
        self.mInsField = self.insMenu.addMenu(self.tr("Word/Character Count"))
        for field in nwStats.ALL_FIELDS:
            value = nwShortcode.FIELD_VALUE.format(field)
            action = self.mInsField.addAction(trConst(nwLabels.STATS_NAME[field]))
            action.triggered.connect(qtLambda(self.requestDocInsertText.emit, value))

        # Insert > Breaks and Vertical Space
        self.mInsBreaks = self.insMenu.addMenu(self.tr("Breaks and Vertical Space"))

        # Insert > New Page
        self.aInsNewPage = self.mInsBreaks.addAction(self.tr("Page Break"))
        self.aInsNewPage.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.NEW_PAGE)
        )

        # Insert > Forced Line Break
        self.aInsLineBreak = self.mInsBreaks.addAction(self.tr("Forced Line Break"))
        self.aInsLineBreak.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.LINE_BRK)
        )

        # Insert > Vertical Space (Single)
        self.aInsVSpaceS = self.mInsBreaks.addAction(self.tr("Vertical Space (Single)"))
        self.aInsVSpaceS.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.VSPACE_S)
        )

        # Insert > Vertical Space (Multi)
        self.aInsVSpaceM = self.mInsBreaks.addAction(self.tr("Vertical Space (Multi)"))
        self.aInsVSpaceM.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.VSPACE_M)
        )

        # Insert > Placeholder Text
        self.aLipsumText = self.insMenu.addAction(self.tr("Placeholder Text"))
        self.aLipsumText.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.LIPSUM)
        )

        # Insert > Footnote
        self.aFootnote = self.insMenu.addAction(self.tr("Footnote"))
        self.aFootnote.triggered.connect(
            lambda: self.requestDocInsert.emit(nwDocInsert.FOOTNOTE)
        )

        return

    def _buildFormatMenu(self) -> None:
        """Assemble the Format menu."""
        # Format
        self.fmtMenu = self.addMenu(self.tr("&Format"))

        # Format > Bold
        self.aFmtBold = self.fmtMenu.addAction(self.tr("Bold"))
        self.aFmtBold.setShortcut("Ctrl+B")
        self.aFmtBold.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.MD_BOLD)
        )
        self.mainGui.addAction(self.aFmtBold)

        # Format > Italic
        self.aFmtItalic = self.fmtMenu.addAction(self.tr("Italic"))
        self.aFmtItalic.setShortcut("Ctrl+I")
        self.aFmtItalic.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.MD_ITALIC)
        )
        self.mainGui.addAction(self.aFmtItalic)

        # Format > Strikethrough
        self.aFmtStrike = self.fmtMenu.addAction(self.tr("Strikethrough"))
        self.aFmtStrike.setShortcut("Ctrl+D")
        self.aFmtStrike.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.MD_STRIKE)
        )
        self.mainGui.addAction(self.aFmtStrike)

        # Edit > Separator
        self.fmtMenu.addSeparator()

        # Format > Double Quotes
        self.aFmtDQuote = self.fmtMenu.addAction(self.tr("Wrap Double Quotes"))
        self.aFmtDQuote.setShortcut("Ctrl+\"")
        self.aFmtDQuote.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.D_QUOTE)
        )
        self.mainGui.addAction(self.aFmtDQuote)

        # Format > Single Quotes
        self.aFmtSQuote = self.fmtMenu.addAction(self.tr("Wrap Single Quotes"))
        self.aFmtSQuote.setShortcut("Ctrl+'")
        self.aFmtSQuote.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.S_QUOTE)
        )
        self.mainGui.addAction(self.aFmtSQuote)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Shortcodes
        self.mShortcodes = self.fmtMenu.addMenu(self.tr("More Formats ..."))

        # Shortcode Bold
        self.aScBold = self.mShortcodes.addAction(self.tr("Bold (Shortcode)"))
        self.aScBold.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_BOLD)
        )

        # Shortcode Italic
        self.aScItalic = self.mShortcodes.addAction(self.tr("Italics (Shortcode)"))
        self.aScItalic.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_ITALIC)
        )

        # Shortcode Strikethrough
        self.aScStrike = self.mShortcodes.addAction(self.tr("Strikethrough (Shortcode)"))
        self.aScStrike.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_STRIKE)
        )

        # Shortcode Underline
        self.aScULine = self.mShortcodes.addAction(self.tr("Underline"))
        self.aScULine.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_ULINE)
        )

        # Shortcode Mark
        self.aScMark = self.mShortcodes.addAction(self.tr("Highlight"))
        self.aScMark.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_MARK)
        )

        # Shortcode Superscript
        self.aScSuper = self.mShortcodes.addAction(self.tr("Superscript"))
        self.aScSuper.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_SUP)
        )

        # Shortcode Subscript
        self.aScSub = self.mShortcodes.addAction(self.tr("Subscript"))
        self.aScSub.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_SUB)
        )

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Heading 1 (Partition)
        self.aFmtHead1 = self.fmtMenu.addAction(trConst(nwStyles.T_LABEL["H1"]))
        self.aFmtHead1.setShortcut("Ctrl+1")
        self.aFmtHead1.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.BLOCK_H1)
        )
        self.mainGui.addAction(self.aFmtHead1)

        # Format > Heading 2 (Chapter)
        self.aFmtHead2 = self.fmtMenu.addAction(trConst(nwStyles.T_LABEL["H2"]))
        self.aFmtHead2.setShortcut("Ctrl+2")
        self.aFmtHead2.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.BLOCK_H2)
        )
        self.mainGui.addAction(self.aFmtHead2)

        # Format > Heading 3 (Scene)
        self.aFmtHead3 = self.fmtMenu.addAction(trConst(nwStyles.T_LABEL["H3"]))
        self.aFmtHead3.setShortcut("Ctrl+3")
        self.aFmtHead3.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.BLOCK_H3)
        )
        self.mainGui.addAction(self.aFmtHead3)

        # Format > Heading 4 (Section)
        self.aFmtHead4 = self.fmtMenu.addAction(trConst(nwStyles.T_LABEL["H4"]))
        self.aFmtHead4.setShortcut("Ctrl+4")
        self.aFmtHead4.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.BLOCK_H4)
        )
        self.mainGui.addAction(self.aFmtHead4)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Novel Title
        self.aFmtTitle = self.fmtMenu.addAction(self.tr("Novel Title"))
        self.aFmtTitle.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.BLOCK_TTL)
        )

        # Format > Unnumbered Chapter
        self.aFmtUnNum = self.fmtMenu.addAction(self.tr("Unnumbered Chapter"))
        self.aFmtUnNum.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.BLOCK_UNN)
        )

        # Format > Alternative Scene
        self.aFmtHardSc = self.fmtMenu.addAction(self.tr("Alternative Scene"))
        self.aFmtHardSc.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.BLOCK_HSC)
        )

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Align Left
        self.aFmtAlignLeft = self.fmtMenu.addAction(self.tr("Align Left"))
        self.aFmtAlignLeft.setShortcut("Ctrl+5")
        self.aFmtAlignLeft.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.ALIGN_L)
        )
        self.mainGui.addAction(self.aFmtAlignLeft)

        # Format > Align Centre
        self.aFmtAlignCentre = self.fmtMenu.addAction(self.tr("Align Centre"))
        self.aFmtAlignCentre.setShortcut("Ctrl+6")
        self.aFmtAlignCentre.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.ALIGN_C)
        )
        self.mainGui.addAction(self.aFmtAlignCentre)

        # Format > Align Right
        self.aFmtAlignRight = self.fmtMenu.addAction(self.tr("Align Right"))
        self.aFmtAlignRight.setShortcut("Ctrl+7")
        self.aFmtAlignRight.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.ALIGN_R)
        )
        self.mainGui.addAction(self.aFmtAlignRight)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Indent Left
        self.aFmtIndentLeft = self.fmtMenu.addAction(self.tr("Indent Left"))
        self.aFmtIndentLeft.setShortcut("Ctrl+8")
        self.aFmtIndentLeft.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.INDENT_L)
        )
        self.mainGui.addAction(self.aFmtIndentLeft)

        # Format > Indent Right
        self.aFmtIndentRight = self.fmtMenu.addAction(self.tr("Indent Right"))
        self.aFmtIndentRight.setShortcut("Ctrl+9")
        self.aFmtIndentRight.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.INDENT_R)
        )
        self.mainGui.addAction(self.aFmtIndentRight)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Comment
        self.aFmtComment = self.fmtMenu.addAction(self.tr("Toggle Comment"))
        self.aFmtComment.setShortcut("Ctrl+/")
        self.aFmtComment.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.BLOCK_COM)
        )
        self.mainGui.addAction(self.aFmtComment)

        # Format > Ignore Text
        self.aFmtIgnore = self.fmtMenu.addAction(self.tr("Toggle Ignore Text"))
        self.aFmtIgnore.setShortcut("Ctrl+Shift+D")
        self.aFmtIgnore.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.BLOCK_IGN)
        )

        # Format > Remove Block Format
        self.aFmtNoFormat = self.fmtMenu.addAction(self.tr("Remove Block Format"))
        self.aFmtNoFormat.setShortcuts(["Ctrl+0", "Ctrl+Shift+/"])
        self.aFmtNoFormat.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.BLOCK_TXT)
        )
        self.mainGui.addAction(self.aFmtNoFormat)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Replace Straight Single Quotes
        self.aFmtReplSng = self.fmtMenu.addAction(self.tr("Replace Straight Single Quotes"))
        self.aFmtReplSng.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.REPL_SNG)
        )

        # Format > Replace Straight Double Quotes
        self.aFmtReplDbl = self.fmtMenu.addAction(self.tr("Replace Straight Double Quotes"))
        self.aFmtReplDbl.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.REPL_DBL)
        )

        # Format > Remove In-Paragraph Breaks
        self.aFmtRmBreaks = self.fmtMenu.addAction(self.tr("Remove In-Paragraph Breaks"))
        self.aFmtRmBreaks.triggered.connect(
            lambda: self.requestDocAction.emit(nwDocAction.RM_BREAKS)
        )

        return

    def _buildSearchMenu(self) -> None:
        """Assemble the Search menu."""
        # Search
        self.srcMenu = self.addMenu(self.tr("&Search"))

        # Search > Find
        self.aFind = self.srcMenu.addAction(self.tr("Find"))
        self.aFind.setShortcut("Ctrl+F")
        self.aFind.triggered.connect(qtLambda(self.mainGui.docEditor.beginSearch))
        self.mainGui.addAction(self.aFind)

        # Search > Replace
        self.aReplace = self.srcMenu.addAction(self.tr("Replace"))
        self.aReplace.setShortcut("Ctrl+=" if CONFIG.osDarwin else "Ctrl+H")
        self.aReplace.triggered.connect(qtLambda(self.mainGui.docEditor.beginReplace))
        self.mainGui.addAction(self.aReplace)

        # Search > Find Next
        self.aFindNext = self.srcMenu.addAction(self.tr("Find Next"))
        self.aFindNext.setShortcuts(["Ctrl+G", "F3"] if CONFIG.osDarwin else ["F3", "Ctrl+G"])
        self.aFindNext.triggered.connect(qtLambda(self.mainGui.docEditor.findNext))
        self.mainGui.addAction(self.aFindNext)

        # Search > Find Prev
        self.aFindPrev = self.srcMenu.addAction(self.tr("Find Previous"))
        self.aFindPrev.setShortcuts(
            ["Ctrl+Shift+G", "Shift+F3"] if CONFIG.osDarwin else ["Shift+F3", "Ctrl+Shift+G"]
        )
        self.aFindPrev.triggered.connect(qtLambda(self.mainGui.docEditor.findNext, goBack=True))
        self.mainGui.addAction(self.aFindPrev)

        # Search > Replace Next
        self.aReplaceNext = self.srcMenu.addAction(self.tr("Replace Next"))
        self.aReplaceNext.setShortcut("Ctrl+Shift+1")
        self.aReplaceNext.triggered.connect(qtLambda(self.mainGui.docEditor.replaceNext))
        self.mainGui.addAction(self.aReplaceNext)

        # Search > Separator
        self.srcMenu.addSeparator()

        # Search > Find in Project
        self.aFindProj = self.srcMenu.addAction(self.tr("Find in Project"))
        self.aFindProj.setShortcut("Ctrl+Shift+F")
        self.aFindProj.triggered.connect(lambda: self.requestViewChange.emit(nwView.SEARCH))

        return

    def _buildToolsMenu(self) -> None:
        """Assemble the Tools menu."""
        # Tools
        self.toolsMenu = self.addMenu(self.tr("&Tools"))

        # Tools > Check Spelling
        self.aSpellCheck = self.toolsMenu.addAction(self.tr("Check Spelling"))
        self.aSpellCheck.setCheckable(True)
        self.aSpellCheck.setChecked(SHARED.project.data.spellCheck)
        self.aSpellCheck.triggered.connect(self._toggleSpellCheck)  # triggered, not toggled!
        self.aSpellCheck.setShortcut("Ctrl+F7")
        self.mainGui.addAction(self.aSpellCheck)

        self.mSelectLanguage = self.toolsMenu.addMenu(self.tr("Spell Check Language"))
        languages = SHARED.spelling.listDictionaries()
        languages.insert(0, ("None", self.tr("Default")))
        for n, (tag, language) in enumerate(languages):
            aSpell = QAction(self.mSelectLanguage)
            aSpell.setText(language)
            aSpell.triggered.connect(lambda n, tag=tag: self._changeSpelling(tag))
            self.mSelectLanguage.addAction(aSpell)

        # Tools > Re-Run Spell Check
        self.aReRunSpell = self.toolsMenu.addAction(self.tr("Re-Run Spell Check"))
        self.aReRunSpell.setShortcut("F7")
        self.aReRunSpell.triggered.connect(qtLambda(self.mainGui.docEditor.spellCheckDocument))
        self.mainGui.addAction(self.aReRunSpell)

        # Tools > Project Word List
        self.aEditWordList = self.toolsMenu.addAction(self.tr("Project Word List"))
        self.aEditWordList.triggered.connect(self.mainGui.showProjectWordListDialog)

        # Tools > Add Dictionaries
        if CONFIG.osWindows or CONFIG.isDebug:
            self.aAddDicts = self.toolsMenu.addAction(self.tr("Add Dictionaries"))
            self.aAddDicts.triggered.connect(self.mainGui.showDictionariesDialog)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Rebuild Index
        self.aRebuildIndex = self.toolsMenu.addAction(self.tr("Rebuild Index"))
        self.aRebuildIndex.setShortcut("F9")
        self.aRebuildIndex.triggered.connect(qtLambda(self.mainGui.rebuildIndex))

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Backup Project
        self.aBackupProject = self.toolsMenu.addAction(self.tr("Backup Project"))
        self.aBackupProject.triggered.connect(qtLambda(SHARED.project.backupProject, True))

        # Tools > Build Manuscript
        self.aBuildManuscript = self.toolsMenu.addAction(self.tr("Build Manuscript"))
        self.aBuildManuscript.setShortcut("F5")
        self.aBuildManuscript.triggered.connect(self.mainGui.showBuildManuscriptDialog)

        # Tools > Writing Statistics
        self.aWritingStats = self.toolsMenu.addAction(self.tr("Writing Statistics"))
        self.aWritingStats.setShortcut("F6")
        self.aWritingStats.triggered.connect(self.mainGui.showWritingStatsDialog)

        # Tools > Preferences
        self.aPreferences = self.toolsMenu.addAction(self.tr("Preferences"))
        self.aPreferences.setShortcut("Ctrl+,")
        self.aPreferences.setMenuRole(QAction.MenuRole.PreferencesRole)
        self.aPreferences.triggered.connect(self.mainGui.showPreferencesDialog)
        self.mainGui.addAction(self.aPreferences)

        return

    def _buildHelpMenu(self) -> None:
        """Assemble the Help menu."""
        # Help
        self.helpMenu = self.addMenu(self.tr("&Help"))

        # Help > About
        self.aAboutNW = self.helpMenu.addAction(self.tr("About novelWriter"))
        self.aAboutNW.setMenuRole(QAction.MenuRole.AboutRole)
        self.aAboutNW.triggered.connect(self.mainGui.showAboutNWDialog)

        # Help > About Qt5
        self.aAboutQt = self.helpMenu.addAction(self.tr("About Qt5"))
        self.aAboutQt.setMenuRole(QAction.MenuRole.AboutQtRole)
        self.aAboutQt.triggered.connect(self.mainGui.showAboutQtDialog)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Help > User Manual (Online)
        self.aHelpDocs = self.helpMenu.addAction(self.tr("User Manual (Online)"))
        self.aHelpDocs.setShortcut("F1")
        self.aHelpDocs.triggered.connect(qtLambda(SHARED.openWebsite, nwConst.URL_DOCS))
        self.mainGui.addAction(self.aHelpDocs)

        # Help > User Manual (PDF)
        if isinstance(CONFIG.pdfDocs, Path):
            self.aPdfDocs = self.helpMenu.addAction(self.tr("User Manual (PDF)"))
            self.aPdfDocs.setShortcut("Shift+F1")
            self.aPdfDocs.triggered.connect(self._openUserManualFile)
            self.mainGui.addAction(self.aPdfDocs)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Document > Report an Issue
        self.aIssue = self.helpMenu.addAction(self.tr("Report an Issue (GitHub)"))
        self.aIssue.triggered.connect(qtLambda(SHARED.openWebsite, nwConst.URL_REPORT))

        # Document > Ask a Question
        self.aQuestion = self.helpMenu.addAction(self.tr("Ask a Question (GitHub)"))
        self.aQuestion.triggered.connect(qtLambda(SHARED.openWebsite, nwConst.URL_HELP))

        # Document > Main Website
        self.aWebsite = self.helpMenu.addAction(self.tr("The novelWriter Website"))
        self.aWebsite.triggered.connect(qtLambda(SHARED.openWebsite, nwConst.URL_WEB))

        return
