"""
novelWriter – GUI Main Menu
===========================
GUI class for the main window menu

File History:
Created: 2019-04-27 [0.0.1]

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

import logging
import novelwriter

from pathlib import Path
from urllib.parse import urljoin
from urllib.request import pathname2url

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMenuBar, QAction

from novelwriter.enum import nwDocAction, nwDocInsert, nwWidget
from novelwriter.constants import trConst, nwKeyWords, nwLabels, nwUnicode

logger = logging.getLogger(__name__)


class GuiMainMenu(QMenuBar):
    """The GUI main menu. All menu actions are defined here with the
    main menu as the owner. Each widget that need them elsewhere need to
    add them from this class.
    """

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiMainMenu ...")
        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.theProject = mainGui.theProject

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

        # Function Pointers
        self._docAction     = self.mainGui.passDocumentAction
        self._docInsert     = self.mainGui.docEditor.insertText
        self._insertKeyWord = self.mainGui.docEditor.insertKeyWord

        logger.debug("GuiMainMenu initialisation complete")

        return

    ##
    #  Update Menu on Settings Changed
    ##

    def setSpellCheck(self, theMode):
        """Forward spell check check state to its action.
        """
        self.aSpellCheck.setChecked(theMode)
        return

    ##
    #  Slots
    ##

    def _toggleSpellCheck(self):
        """Toggle spell checking. The active status of the spell check
        flag is handled by the document editor class, so we make no
        decision, just pass a None to the function and let it decide.
        """
        self.mainGui.docEditor.toggleSpellCheck(None)
        return True

    def _openWebsite(self, theUrl):
        """Open a URL in the system's default browser.
        """
        QDesktopServices.openUrl(QUrl(theUrl))
        return True

    def _openUserManualFile(self):
        """Open the documentation in PDF format.
        """
        if isinstance(self.mainConf.pdfDocs, Path):
            QDesktopServices.openUrl(
                QUrl(urljoin("file:", pathname2url(str(self.mainConf.pdfDocs))))
            )
        return

    ##
    #  Menu Builders
    ##

    def _buildProjectMenu(self):
        """Assemble the Project menu.
        """
        # Project
        self.projMenu = self.addMenu(self.tr("&Project"))

        # Project > New Project
        self.aNewProject = QAction(self.tr("New Project"), self)
        self.aNewProject.triggered.connect(lambda: self.mainGui.newProject(None))
        self.projMenu.addAction(self.aNewProject)

        # Project > Open Project
        self.aOpenProject = QAction(self.tr("Open Project"), self)
        self.aOpenProject.setShortcut("Ctrl+Shift+O")
        self.aOpenProject.triggered.connect(lambda: self.mainGui.showProjectLoadDialog())
        self.projMenu.addAction(self.aOpenProject)

        # Project > Save Project
        self.aSaveProject = QAction(self.tr("Save Project"), self)
        self.aSaveProject.setShortcut("Ctrl+Shift+S")
        self.aSaveProject.triggered.connect(lambda: self.mainGui.saveProject())
        self.projMenu.addAction(self.aSaveProject)

        # Project > Close Project
        self.aCloseProject = QAction(self.tr("Close Project"), self)
        self.aCloseProject.setShortcut("Ctrl+Shift+W")
        self.aCloseProject.triggered.connect(lambda: self.mainGui.closeProject(False))
        self.projMenu.addAction(self.aCloseProject)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Project Settings
        self.aProjectSettings = QAction(self.tr("Project Settings"), self)
        self.aProjectSettings.setShortcut("Ctrl+Shift+,")
        self.aProjectSettings.triggered.connect(lambda: self.mainGui.showProjectSettingsDialog())
        self.projMenu.addAction(self.aProjectSettings)

        # Project > Project Details
        self.aProjectDetails = QAction(self.tr("Project Details"), self)
        self.aProjectDetails.setShortcut("Shift+F6")
        self.aProjectDetails.triggered.connect(lambda: self.mainGui.showProjectDetailsDialog())
        self.projMenu.addAction(self.aProjectDetails)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Edit
        self.aEditItem = QAction(self.tr("Rename Item"), self)
        self.aEditItem.setShortcut("F2")
        self.aEditItem.triggered.connect(lambda: self.mainGui.editItemLabel(None))
        self.projMenu.addAction(self.aEditItem)

        # Project > Delete
        self.aDeleteItem = QAction(self.tr("Delete Item"), self)
        self.aDeleteItem.setShortcut("Ctrl+Shift+Del")
        self.aDeleteItem.triggered.connect(lambda: self.mainGui.projView.requestDeleteItem(None))
        self.projMenu.addAction(self.aDeleteItem)

        # Project > Empty Trash
        self.aEmptyTrash = QAction(self.tr("Empty Trash"), self)
        self.aEmptyTrash.triggered.connect(lambda: self.mainGui.projView.emptyTrash())
        self.projMenu.addAction(self.aEmptyTrash)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Exit
        self.aExitNW = QAction(self.tr("Exit"), self)
        self.aExitNW.setShortcut("Ctrl+Q")
        self.aExitNW.setMenuRole(QAction.QuitRole)
        self.aExitNW.triggered.connect(lambda: self.mainGui.closeMain())
        self.projMenu.addAction(self.aExitNW)

        return

    def _buildDocumentMenu(self):
        """Assemble the Document menu.
        """
        # Document
        self.docuMenu = self.addMenu(self.tr("&Document"))

        # Document > Open
        self.aOpenDoc = QAction(self.tr("Open Document"), self)
        self.aOpenDoc.setShortcut("Ctrl+O")
        self.aOpenDoc.triggered.connect(lambda: self.mainGui.openSelectedItem())
        self.docuMenu.addAction(self.aOpenDoc)

        # Document > Save
        self.aSaveDoc = QAction(self.tr("Save Document"), self)
        self.aSaveDoc.setShortcut("Ctrl+S")
        self.aSaveDoc.triggered.connect(lambda: self.mainGui.saveDocument())
        self.docuMenu.addAction(self.aSaveDoc)

        # Document > Close
        self.aCloseDoc = QAction(self.tr("Close Document"), self)
        self.aCloseDoc.setShortcut("Ctrl+W")
        self.aCloseDoc.triggered.connect(lambda: self.mainGui.closeDocEditor())
        self.docuMenu.addAction(self.aCloseDoc)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Preview
        self.aViewDoc = QAction(self.tr("View Document"), self)
        self.aViewDoc.setShortcut("Ctrl+R")
        self.aViewDoc.triggered.connect(lambda: self.mainGui.viewDocument(None))
        self.docuMenu.addAction(self.aViewDoc)

        # Document > Close Preview
        self.aCloseView = QAction(self.tr("Close Document View"), self)
        self.aCloseView.setShortcut("Ctrl+Shift+R")
        self.aCloseView.triggered.connect(lambda: self.mainGui.closeDocViewer())
        self.docuMenu.addAction(self.aCloseView)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Show File Details
        self.aFileDetails = QAction(self.tr("Show File Details"), self)
        self.aFileDetails.triggered.connect(lambda: self.mainGui.docEditor.revealLocation())
        self.docuMenu.addAction(self.aFileDetails)

        # Document > Import From File
        self.aImportFile = QAction(self.tr("Import Text from File"), self)
        self.aImportFile.setShortcut("Ctrl+Shift+I")
        self.aImportFile.triggered.connect(lambda: self.mainGui.importDocument())
        self.docuMenu.addAction(self.aImportFile)

        return

    def _buildEditMenu(self):
        """Assemble the Edit menu.
        """
        # Edit
        self.editMenu = self.addMenu(self.tr("&Edit"))

        # Edit > Undo
        self.aEditUndo = QAction(self.tr("Undo"), self)
        self.aEditUndo.setShortcut("Ctrl+Z")
        self.aEditUndo.triggered.connect(lambda: self._docAction(nwDocAction.UNDO))
        self.editMenu.addAction(self.aEditUndo)

        # Edit > Redo
        self.aEditRedo = QAction(self.tr("Redo"), self)
        self.aEditRedo.setShortcut("Ctrl+Y")
        self.aEditRedo.triggered.connect(lambda: self._docAction(nwDocAction.REDO))
        self.editMenu.addAction(self.aEditRedo)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Cut
        self.aEditCut = QAction(self.tr("Cut"), self)
        self.aEditCut.setShortcut("Ctrl+X")
        self.aEditCut.triggered.connect(lambda: self._docAction(nwDocAction.CUT))
        self.editMenu.addAction(self.aEditCut)

        # Edit > Copy
        self.aEditCopy = QAction(self.tr("Copy"), self)
        self.aEditCopy.setShortcut("Ctrl+C")
        self.aEditCopy.triggered.connect(lambda: self._docAction(nwDocAction.COPY))
        self.editMenu.addAction(self.aEditCopy)

        # Edit > Paste
        self.aEditPaste = QAction(self.tr("Paste"), self)
        self.aEditPaste.setShortcut("Ctrl+V")
        self.aEditPaste.triggered.connect(lambda: self._docAction(nwDocAction.PASTE))
        self.editMenu.addAction(self.aEditPaste)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Select All
        self.aSelectAll = QAction(self.tr("Select All"), self)
        self.aSelectAll.setShortcut("Ctrl+A")
        self.aSelectAll.triggered.connect(lambda: self._docAction(nwDocAction.SEL_ALL))
        self.editMenu.addAction(self.aSelectAll)

        # Edit > Select Paragraph
        self.aSelectPar = QAction(self.tr("Select Paragraph"), self)
        self.aSelectPar.setShortcut("Ctrl+Shift+A")
        self.aSelectPar.triggered.connect(lambda: self._docAction(nwDocAction.SEL_PARA))
        self.editMenu.addAction(self.aSelectPar)

        return

    def _buildViewMenu(self):
        """Assemble the View menu.
        """
        # View
        self.viewMenu = self.addMenu(self.tr("&View"))

        # View > TreeView
        self.aFocusTree = QAction(self.tr("Go to Project Tree"), self)
        if self.mainConf.osWindows:
            self.aFocusTree.setShortcut("Ctrl+Alt+1")
        else:
            self.aFocusTree.setShortcut("Alt+1")
        self.aFocusTree.triggered.connect(lambda: self.mainGui.switchFocus(nwWidget.TREE))
        self.viewMenu.addAction(self.aFocusTree)

        # View > Document Pane 1
        self.aFocusEditor = QAction(self.tr("Go to Document Editor"), self)
        if self.mainConf.osWindows:
            self.aFocusEditor.setShortcut("Ctrl+Alt+2")
        else:
            self.aFocusEditor.setShortcut("Alt+2")
        self.aFocusEditor.triggered.connect(lambda: self.mainGui.switchFocus(nwWidget.EDITOR))
        self.viewMenu.addAction(self.aFocusEditor)

        # View > Document Pane 2
        self.aFocusView = QAction(self.tr("Go to Document Viewer"), self)
        if self.mainConf.osWindows:
            self.aFocusView.setShortcut("Ctrl+Alt+3")
        else:
            self.aFocusView.setShortcut("Alt+3")
        self.aFocusView.triggered.connect(lambda: self.mainGui.switchFocus(nwWidget.VIEWER))
        self.viewMenu.addAction(self.aFocusView)

        # View > Outline
        self.aFocusOutline = QAction(self.tr("Go to Outline"), self)
        if self.mainConf.osWindows:
            self.aFocusOutline.setShortcut("Ctrl+Alt+4")
        else:
            self.aFocusOutline.setShortcut("Alt+4")
        self.aFocusOutline.triggered.connect(lambda: self.mainGui.switchFocus(nwWidget.OUTLINE))
        self.viewMenu.addAction(self.aFocusOutline)

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Go Backward
        self.aViewPrev = QAction(self.tr("Navigate Backward"), self)
        self.aViewPrev.setShortcut("Alt+Left")
        self.aViewPrev.triggered.connect(lambda: self.mainGui.docViewer.navBackward())
        self.viewMenu.addAction(self.aViewPrev)

        # View > Go Forward
        self.aViewNext = QAction(self.tr("Navigate Forward"), self)
        self.aViewNext.setShortcut("Alt+Right")
        self.aViewNext.triggered.connect(lambda: self.mainGui.docViewer.navForward())
        self.viewMenu.addAction(self.aViewNext)

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Focus Mode
        self.aFocusMode = QAction(self.tr("Focus Mode"), self)
        self.aFocusMode.setShortcut("F8")
        self.aFocusMode.triggered.connect(lambda: self.mainGui.toggleFocusMode())
        self.viewMenu.addAction(self.aFocusMode)

        # View > Toggle Full Screen
        self.aFullScreen = QAction(self.tr("Full Screen Mode"), self)
        self.aFullScreen.setShortcut("F11")
        self.aFullScreen.triggered.connect(lambda: self.mainGui.toggleFullScreenMode())
        self.viewMenu.addAction(self.aFullScreen)

        return

    def _buildInsertMenu(self):
        """Assemble the Insert menu.
        """
        # Insert
        self.insertMenu = self.addMenu(self.tr("&Insert"))

        # Insert > Dashes and Dots
        self.mInsDashes = self.insertMenu.addMenu(self.tr("Dashes"))

        # Insert > Short Dash
        self.aInsENDash = QAction(self.tr("Short Dash"), self)
        self.aInsENDash.setShortcut("Ctrl+K, -")
        self.aInsENDash.triggered.connect(lambda: self._docInsert(nwUnicode.U_ENDASH))
        self.mInsDashes.addAction(self.aInsENDash)

        # Insert > Long Dash
        self.aInsEMDash = QAction(self.tr("Long Dash"), self)
        self.aInsEMDash.setShortcut("Ctrl+K, _")
        self.aInsEMDash.triggered.connect(lambda: self._docInsert(nwUnicode.U_EMDASH))
        self.mInsDashes.addAction(self.aInsEMDash)

        # Insert > Long Dash
        self.aInsHorBar = QAction(self.tr("Horizontal Bar"), self)
        self.aInsHorBar.setShortcut("Ctrl+K, Ctrl+_")
        self.aInsHorBar.triggered.connect(lambda: self._docInsert(nwUnicode.U_HBAR))
        self.mInsDashes.addAction(self.aInsHorBar)

        # Insert > Figure Dash
        self.aInsFigDash = QAction(self.tr("Figure Dash"), self)
        self.aInsFigDash.setShortcut("Ctrl+K, ~")
        self.aInsFigDash.triggered.connect(lambda: self._docInsert(nwUnicode.U_FGDASH))
        self.mInsDashes.addAction(self.aInsFigDash)

        # Insert > Quote Marks
        self.mInsQuotes = self.insertMenu.addMenu(self.tr("Quote Marks"))

        # Insert > Left Single Quote
        self.aInsQuoteLS = QAction(self.tr("Left Single Quote"), self)
        self.aInsQuoteLS.setShortcut("Ctrl+K, 1")
        self.aInsQuoteLS.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_LS))
        self.mInsQuotes.addAction(self.aInsQuoteLS)

        # Insert > Right Single Quote
        self.aInsQuoteRS = QAction(self.tr("Right Single Quote"), self)
        self.aInsQuoteRS.setShortcut("Ctrl+K, 2")
        self.aInsQuoteRS.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_RS))
        self.mInsQuotes.addAction(self.aInsQuoteRS)

        # Insert > Left Double Quote
        self.aInsQuoteLD = QAction(self.tr("Left Double Quote"), self)
        self.aInsQuoteLD.setShortcut("Ctrl+K, 3")
        self.aInsQuoteLD.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_LD))
        self.mInsQuotes.addAction(self.aInsQuoteLD)

        # Insert > Right Double Quote
        self.aInsQuoteRD = QAction(self.tr("Right Double Quote"), self)
        self.aInsQuoteRD.setShortcut("Ctrl+K, 4")
        self.aInsQuoteRD.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_RD))
        self.mInsQuotes.addAction(self.aInsQuoteRD)

        # Insert > Alternative Apostrophe
        self.aInsMSApos = QAction(self.tr("Alternative Apostrophe"), self)
        self.aInsMSApos.setShortcut("Ctrl+K, '")
        self.aInsMSApos.triggered.connect(lambda: self._docInsert(nwUnicode.U_MAPOSS))
        self.mInsQuotes.addAction(self.aInsMSApos)

        # Insert > Symbols
        self.mInsPunct = self.insertMenu.addMenu(self.tr("General Punctuation"))

        # Insert > Ellipsis
        self.aInsEllipsis = QAction(self.tr("Ellipsis"), self)
        self.aInsEllipsis.setShortcut("Ctrl+K, .")
        self.aInsEllipsis.triggered.connect(lambda: self._docInsert(nwUnicode.U_HELLIP))
        self.mInsPunct.addAction(self.aInsEllipsis)

        # Insert > Prime
        self.aInsPrime = QAction(self.tr("Prime"), self)
        self.aInsPrime.setShortcut("Ctrl+K, Ctrl+'")
        self.aInsPrime.triggered.connect(lambda: self._docInsert(nwUnicode.U_PRIME))
        self.mInsPunct.addAction(self.aInsPrime)

        # Insert > Double Prime
        self.aInsDPrime = QAction(self.tr("Double Prime"), self)
        self.aInsDPrime.setShortcut("Ctrl+K, Ctrl+\"")
        self.aInsDPrime.triggered.connect(lambda: self._docInsert(nwUnicode.U_DPRIME))
        self.mInsPunct.addAction(self.aInsDPrime)

        # Insert > White Spaces
        self.mInsSpace = self.insertMenu.addMenu(self.tr("White Spaces"))

        # Insert > Non-Breaking Space
        self.aInsNBSpace = QAction(self.tr("Non-Breaking Space"), self)
        self.aInsNBSpace.setShortcut("Ctrl+K, Space")
        self.aInsNBSpace.triggered.connect(lambda: self._docInsert(nwUnicode.U_NBSP))
        self.mInsSpace.addAction(self.aInsNBSpace)

        # Insert > Thin Space
        self.aInsThinSpace = QAction(self.tr("Thin Space"), self)
        self.aInsThinSpace.setShortcut("Ctrl+K, Shift+Space")
        self.aInsThinSpace.triggered.connect(lambda: self._docInsert(nwUnicode.U_THSP))
        self.mInsSpace.addAction(self.aInsThinSpace)

        # Insert > Thin Non-Breaking Space
        self.aInsThinNBSpace = QAction(self.tr("Thin Non-Breaking Space"), self)
        self.aInsThinNBSpace.setShortcut("Ctrl+K, Ctrl+Space")
        self.aInsThinNBSpace.triggered.connect(lambda: self._docInsert(nwUnicode.U_THNBSP))
        self.mInsSpace.addAction(self.aInsThinNBSpace)

        # Insert > Symbols
        self.mInsSymbol = self.insertMenu.addMenu(self.tr("Other Symbols"))

        # Insert > List Bullet
        self.aInsBullet = QAction(self.tr("List Bullet"), self)
        self.aInsBullet.setShortcut("Ctrl+K, *")
        self.aInsBullet.triggered.connect(lambda: self._docInsert(nwUnicode.U_BULL))
        self.mInsSymbol.addAction(self.aInsBullet)

        # Insert > Hyphen Bullet
        self.aInsHyBull = QAction(self.tr("Hyphen Bullet"), self)
        self.aInsHyBull.setShortcut("Ctrl+K, Ctrl+-")
        self.aInsHyBull.triggered.connect(lambda: self._docInsert(nwUnicode.U_HYBULL))
        self.mInsSymbol.addAction(self.aInsHyBull)

        # Insert > Flower Mark
        self.aInsFlower = QAction(self.tr("Flower Mark"), self)
        self.aInsFlower.setShortcut("Ctrl+K, Ctrl+*")
        self.aInsFlower.triggered.connect(lambda: self._docInsert(nwUnicode.U_FLOWER))
        self.mInsSymbol.addAction(self.aInsFlower)

        # Insert > Per Mille
        self.aInsPerMille = QAction(self.tr("Per Mille"), self)
        self.aInsPerMille.setShortcut("Ctrl+K, %")
        self.aInsPerMille.triggered.connect(lambda: self._docInsert(nwUnicode.U_PERMIL))
        self.mInsSymbol.addAction(self.aInsPerMille)

        # Insert > Degree Symbol
        self.aInsDegree = QAction(self.tr("Degree Symbol"), self)
        self.aInsDegree.setShortcut("Ctrl+K, Ctrl+O")
        self.aInsDegree.triggered.connect(lambda: self._docInsert(nwUnicode.U_DEGREE))
        self.mInsSymbol.addAction(self.aInsDegree)

        # Insert > Minus Sign
        self.aInsMinus = QAction(self.tr("Minus Sign"), self)
        self.aInsMinus.setShortcut("Ctrl+K, Ctrl+M")
        self.aInsMinus.triggered.connect(lambda: self._docInsert(nwUnicode.U_MINUS))
        self.mInsSymbol.addAction(self.aInsMinus)

        # Insert > Times Sign
        self.aInsTimes = QAction(self.tr("Times Sign"), self)
        self.aInsTimes.setShortcut("Ctrl+K, Ctrl+X")
        self.aInsTimes.triggered.connect(lambda: self._docInsert(nwUnicode.U_TIMES))
        self.mInsSymbol.addAction(self.aInsTimes)

        # Insert > Division
        self.aInsDivide = QAction(self.tr("Division Sign"), self)
        self.aInsDivide.setShortcut("Ctrl+K, Ctrl+D")
        self.aInsDivide.triggered.connect(lambda: self._docInsert(nwUnicode.U_DIVIDE))
        self.mInsSymbol.addAction(self.aInsDivide)

        # Insert > Tags and References
        self.mInsKeywords = self.insertMenu.addMenu(self.tr("Tags and References"))
        self.mInsKWItems = {}
        self.mInsKWItems[nwKeyWords.TAG_KEY]    = (QAction(self.mInsKeywords), "Ctrl+K, G")
        self.mInsKWItems[nwKeyWords.POV_KEY]    = (QAction(self.mInsKeywords), "Ctrl+K, V")
        self.mInsKWItems[nwKeyWords.FOCUS_KEY]  = (QAction(self.mInsKeywords), "Ctrl+K, F")
        self.mInsKWItems[nwKeyWords.CHAR_KEY]   = (QAction(self.mInsKeywords), "Ctrl+K, C")
        self.mInsKWItems[nwKeyWords.PLOT_KEY]   = (QAction(self.mInsKeywords), "Ctrl+K, P")
        self.mInsKWItems[nwKeyWords.TIME_KEY]   = (QAction(self.mInsKeywords), "Ctrl+K, T")
        self.mInsKWItems[nwKeyWords.WORLD_KEY]  = (QAction(self.mInsKeywords), "Ctrl+K, L")
        self.mInsKWItems[nwKeyWords.OBJECT_KEY] = (QAction(self.mInsKeywords), "Ctrl+K, O")
        self.mInsKWItems[nwKeyWords.ENTITY_KEY] = (QAction(self.mInsKeywords), "Ctrl+K, E")
        self.mInsKWItems[nwKeyWords.CUSTOM_KEY] = (QAction(self.mInsKeywords), "Ctrl+K, X")
        for n, keyWord in enumerate(self.mInsKWItems):
            self.mInsKWItems[keyWord][0].setText(trConst(nwLabels.KEY_NAME[keyWord]))
            self.mInsKWItems[keyWord][0].setShortcut(self.mInsKWItems[keyWord][1])
            self.mInsKWItems[keyWord][0].triggered.connect(
                lambda n, keyWord=keyWord: self._insertKeyWord(keyWord)
            )
            self.mInsKeywords.addAction(self.mInsKWItems[keyWord][0])

        # Insert > Special Comments
        self.mInsComments = self.insertMenu.addMenu(self.tr("Special Comments"))

        # Insert > Synopsis Comment
        self.aInsSynopsis = QAction(self.tr("Synopsis Comment"), self)
        self.aInsSynopsis.setShortcut("Ctrl+K, S")
        self.aInsSynopsis.triggered.connect(lambda: self._docInsert(nwDocInsert.SYNOPSIS))
        self.mInsComments.addAction(self.aInsSynopsis)

        # Insert > Symbols
        self.mInsBreaks = self.insertMenu.addMenu(self.tr("Page Break and Space"))

        # Insert > New Page
        self.aInsNewPage = QAction(self.tr("Page Break"), self)
        self.aInsNewPage.triggered.connect(lambda: self._docInsert(nwDocInsert.NEW_PAGE))
        self.mInsBreaks.addAction(self.aInsNewPage)

        # Insert > Vertical Space (Single)
        self.aInsVSpaceS = QAction(self.tr("Vertical Space (Single)"), self)
        self.aInsVSpaceS.triggered.connect(lambda: self._docInsert(nwDocInsert.VSPACE_S))
        self.mInsBreaks.addAction(self.aInsVSpaceS)

        # Insert > Vertical Space (Multi)
        self.aInsVSpaceM = QAction(self.tr("Vertical Space (Multi)"), self)
        self.aInsVSpaceM.triggered.connect(lambda: self._docInsert(nwDocInsert.VSPACE_M))
        self.mInsBreaks.addAction(self.aInsVSpaceM)

        # Insert > Placeholder Text
        self.aLipsumText = QAction(self.tr("Placeholder Text"), self)
        self.aLipsumText.triggered.connect(lambda: self.mainGui.showLoremIpsumDialog())
        self.insertMenu.addAction(self.aLipsumText)

        return

    def _buildFormatMenu(self):
        """Assemble the Format menu.
        """
        # Format
        self.fmtMenu = self.addMenu(self.tr("&Format"))

        # Format > Emphasis
        self.aFmtEmph = QAction(self.tr("Emphasis"), self)
        self.aFmtEmph.setShortcut("Ctrl+I")
        self.aFmtEmph.triggered.connect(lambda: self._docAction(nwDocAction.EMPH))
        self.fmtMenu.addAction(self.aFmtEmph)

        # Format > Strong Emphasis
        self.aFmtStrong = QAction(self.tr("Strong Emphasis"), self)
        self.aFmtStrong.setShortcut("Ctrl+B")
        self.aFmtStrong.triggered.connect(lambda: self._docAction(nwDocAction.STRONG))
        self.fmtMenu.addAction(self.aFmtStrong)

        # Format > Strikethrough
        self.aFmtStrike = QAction(self.tr("Strikethrough"), self)
        self.aFmtStrike.setShortcut("Ctrl+D")
        self.aFmtStrike.triggered.connect(lambda: self._docAction(nwDocAction.STRIKE))
        self.fmtMenu.addAction(self.aFmtStrike)

        # Edit > Separator
        self.fmtMenu.addSeparator()

        # Format > Double Quotes
        self.aFmtDQuote = QAction(self.tr("Wrap Double Quotes"), self)
        self.aFmtDQuote.setShortcut("Ctrl+\"")
        self.aFmtDQuote.triggered.connect(lambda: self._docAction(nwDocAction.D_QUOTE))
        self.fmtMenu.addAction(self.aFmtDQuote)

        # Format > Single Quotes
        self.aFmtSQuote = QAction(self.tr("Wrap Single Quotes"), self)
        self.aFmtSQuote.setShortcut("Ctrl+'")
        self.aFmtSQuote.triggered.connect(lambda: self._docAction(nwDocAction.S_QUOTE))
        self.fmtMenu.addAction(self.aFmtSQuote)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Header 1 (Partition)
        self.aFmtHead1 = QAction(self.tr("Header 1 (Partition)"), self)
        self.aFmtHead1.setShortcut("Ctrl+1")
        self.aFmtHead1.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H1))
        self.fmtMenu.addAction(self.aFmtHead1)

        # Format > Header 2 (Chapter)
        self.aFmtHead2 = QAction(self.tr("Header 2 (Chapter)"), self)
        self.aFmtHead2.setShortcut("Ctrl+2")
        self.aFmtHead2.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H2))
        self.fmtMenu.addAction(self.aFmtHead2)

        # Format > Header 3 (Scene)
        self.aFmtHead3 = QAction(self.tr("Header 3 (Scene)"), self)
        self.aFmtHead3.setShortcut("Ctrl+3")
        self.aFmtHead3.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H3))
        self.fmtMenu.addAction(self.aFmtHead3)

        # Format > Header 4 (Section)
        self.aFmtHead4 = QAction(self.tr("Header 4 (Section)"), self)
        self.aFmtHead4.setShortcut("Ctrl+4")
        self.aFmtHead4.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H4))
        self.fmtMenu.addAction(self.aFmtHead4)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Novel Title
        self.aFmtTitle = QAction(self.tr("Novel Title"), self)
        self.aFmtTitle.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_TTL))
        self.fmtMenu.addAction(self.aFmtTitle)

        # Format > Unnumbered Chapter
        self.aFmtUnNum = QAction(self.tr("Unnumbered Chapter"), self)
        self.aFmtUnNum.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_UNN))
        self.fmtMenu.addAction(self.aFmtUnNum)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Align Left
        self.aFmtAlignLeft = QAction(self.tr("Align Left"), self)
        self.aFmtAlignLeft.setShortcut("Ctrl+5")
        self.aFmtAlignLeft.triggered.connect(lambda: self._docAction(nwDocAction.ALIGN_L))
        self.fmtMenu.addAction(self.aFmtAlignLeft)

        # Format > Align Centre
        self.aFmtAlignCentre = QAction(self.tr("Align Centre"), self)
        self.aFmtAlignCentre.setShortcut("Ctrl+6")
        self.aFmtAlignCentre.triggered.connect(lambda: self._docAction(nwDocAction.ALIGN_C))
        self.fmtMenu.addAction(self.aFmtAlignCentre)

        # Format > Align Right
        self.aFmtAlignRight = QAction(self.tr("Align Right"), self)
        self.aFmtAlignRight.setShortcut("Ctrl+7")
        self.aFmtAlignRight.triggered.connect(lambda: self._docAction(nwDocAction.ALIGN_R))
        self.fmtMenu.addAction(self.aFmtAlignRight)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Indent Left
        self.aFmtIndentLeft = QAction(self.tr("Indent Left"), self)
        self.aFmtIndentLeft.setShortcut("Ctrl+8")
        self.aFmtIndentLeft.triggered.connect(lambda: self._docAction(nwDocAction.INDENT_L))
        self.fmtMenu.addAction(self.aFmtIndentLeft)

        # Format > Indent Right
        self.aFmtIndentRight = QAction(self.tr("Indent Right"), self)
        self.aFmtIndentRight.setShortcut("Ctrl+9")
        self.aFmtIndentRight.triggered.connect(lambda: self._docAction(nwDocAction.INDENT_R))
        self.fmtMenu.addAction(self.aFmtIndentRight)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Comment
        self.aFmtComment = QAction(self.tr("Toggle Comment"), self)
        self.aFmtComment.setShortcut("Ctrl+/")
        self.aFmtComment.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_COM))
        self.fmtMenu.addAction(self.aFmtComment)

        # Format > Remove Block Format
        self.aFmtNoFormat = QAction(self.tr("Remove Block Format"), self)
        self.aFmtNoFormat.setShortcuts(["Ctrl+0", "Ctrl+Shift+/"])
        self.aFmtNoFormat.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_TXT))
        self.fmtMenu.addAction(self.aFmtNoFormat)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Replace Single Quotes
        self.aFmtReplSng = QAction(self.tr("Convert Single Quotes"), self)
        self.aFmtReplSng.triggered.connect(lambda: self._docAction(nwDocAction.REPL_SNG))
        self.fmtMenu.addAction(self.aFmtReplSng)

        # Format > Replace Double Quotes
        self.aFmtReplDbl = QAction(self.tr("Convert Double Quotes"), self)
        self.aFmtReplDbl.triggered.connect(lambda: self._docAction(nwDocAction.REPL_DBL))
        self.fmtMenu.addAction(self.aFmtReplDbl)

        # Format > Remove In-Paragraph Breaks
        self.aFmtRmBreaks = QAction(self.tr("Remove In-Paragraph Breaks"), self)
        self.aFmtRmBreaks.triggered.connect(lambda: self._docAction(nwDocAction.RM_BREAKS))
        self.fmtMenu.addAction(self.aFmtRmBreaks)

        return

    def _buildSearchMenu(self):
        """Assemble the Search menu.
        """
        # Search
        self.srcMenu = self.addMenu(self.tr("&Search"))

        # Search > Find
        self.aFind = QAction(self.tr("Find"), self)
        self.aFind.setShortcut("Ctrl+F")
        self.aFind.triggered.connect(lambda: self.mainGui.docEditor.beginSearch())
        self.srcMenu.addAction(self.aFind)

        # Search > Replace
        self.aReplace = QAction(self.tr("Replace"), self)
        if self.mainConf.osDarwin:
            self.aReplace.setShortcut("Ctrl+=")
        else:
            self.aReplace.setShortcut("Ctrl+H")
        self.aReplace.triggered.connect(lambda: self.mainGui.docEditor.beginReplace())
        self.srcMenu.addAction(self.aReplace)

        # Search > Find Next
        self.aFindNext = QAction(self.tr("Find Next"), self)
        if self.mainConf.osDarwin:
            self.aFindNext.setShortcuts(["Ctrl+G", "F3"])
        else:
            self.aFindNext.setShortcuts(["F3", "Ctrl+G"])
        self.aFindNext.triggered.connect(lambda: self.mainGui.docEditor.findNext())
        self.srcMenu.addAction(self.aFindNext)

        # Search > Find Prev
        self.aFindPrev = QAction(self.tr("Find Previous"), self)
        if self.mainConf.osDarwin:
            self.aFindPrev.setShortcuts(["Ctrl+Shift+G", "Shift+F3"])
        else:
            self.aFindPrev.setShortcuts(["Shift+F3", "Ctrl+Shift+G"])
        self.aFindPrev.triggered.connect(lambda: self.mainGui.docEditor.findNext(goBack=True))
        self.srcMenu.addAction(self.aFindPrev)

        # Search > Replace Next
        self.aReplaceNext = QAction(self.tr("Replace Next"), self)
        self.aReplaceNext.setShortcut("Ctrl+Shift+1")
        self.aReplaceNext.triggered.connect(lambda: self.mainGui.docEditor.replaceNext())
        self.srcMenu.addAction(self.aReplaceNext)

        return

    def _buildToolsMenu(self):
        """Assemble the Tools menu.
        """
        # Tools
        self.toolsMenu = self.addMenu(self.tr("&Tools"))

        # Tools > Check Spelling
        self.aSpellCheck = QAction(self.tr("Check Spelling"), self)
        self.aSpellCheck.setCheckable(True)
        self.aSpellCheck.setChecked(self.theProject.data.spellCheck)
        self.aSpellCheck.triggered.connect(self._toggleSpellCheck)  # triggered, not toggled!
        self.aSpellCheck.setShortcut("Ctrl+F7")
        self.toolsMenu.addAction(self.aSpellCheck)

        # Tools > Re-Run Spell Check
        self.aReRunSpell = QAction(self.tr("Re-Run Spell Check"), self)
        self.aReRunSpell.setShortcut("F7")
        self.aReRunSpell.triggered.connect(lambda: self.mainGui.docEditor.spellCheckDocument())
        self.toolsMenu.addAction(self.aReRunSpell)

        # Tools > Project Word List
        self.aEditWordList = QAction(self.tr("Project Word List"), self)
        self.aEditWordList.triggered.connect(lambda: self.mainGui.showProjectWordListDialog())
        self.toolsMenu.addAction(self.aEditWordList)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Rebuild Indices
        self.aRebuildIndex = QAction(self.tr("Rebuild Index"), self)
        self.aRebuildIndex.setShortcut("F9")
        self.aRebuildIndex.triggered.connect(lambda: self.mainGui.rebuildIndex())
        self.toolsMenu.addAction(self.aRebuildIndex)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Backup
        self.aBackupProject = QAction(self.tr("Backup Project"), self)
        self.aBackupProject.triggered.connect(lambda: self.theProject.backupProject(True))
        self.toolsMenu.addAction(self.aBackupProject)

        # Tools > Export Project
        self.aBuildProject = QAction(self.tr("Build Novel Project"), self)
        self.aBuildProject.setShortcut("F5")
        self.aBuildProject.triggered.connect(lambda: self.mainGui.showBuildProjectDialog())
        self.toolsMenu.addAction(self.aBuildProject)

        # Tools > Writing Stats
        self.aWritingStats = QAction(self.tr("Writing Statistics"), self)
        self.aWritingStats.setShortcut("F6")
        self.aWritingStats.triggered.connect(lambda: self.mainGui.showWritingStatsDialog())
        self.toolsMenu.addAction(self.aWritingStats)

        # Tools > Settings
        self.aPreferences = QAction(self.tr("Preferences"), self)
        self.aPreferences.setShortcut("Ctrl+,")
        self.aPreferences.setMenuRole(QAction.PreferencesRole)
        self.aPreferences.triggered.connect(lambda: self.mainGui.showPreferencesDialog())
        self.toolsMenu.addAction(self.aPreferences)

        return

    def _buildHelpMenu(self):
        """Assemble the Help menu.
        """
        # Help
        self.helpMenu = self.addMenu(self.tr("&Help"))

        # Help > About
        self.aAboutNW = QAction(self.tr("About novelWriter"), self)
        self.aAboutNW.setMenuRole(QAction.AboutRole)
        self.aAboutNW.triggered.connect(lambda: self.mainGui.showAboutNWDialog())
        self.helpMenu.addAction(self.aAboutNW)

        # Help > About Qt5
        self.aAboutQt = QAction(self.tr("About Qt5"), self)
        self.aAboutQt.setMenuRole(QAction.AboutQtRole)
        self.aAboutQt.triggered.connect(lambda: self.mainGui.showAboutQtDialog())
        self.helpMenu.addAction(self.aAboutQt)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Help > User Manual (Online)
        if novelwriter.__version__[-2] == "f":
            docUrl = f"{novelwriter.__docurl__}/en/stable/"
        else:
            docUrl = f"{novelwriter.__docurl__}/en/latest/"

        self.aHelpDocs = QAction(self.tr("User Manual (Online)"), self)
        self.aHelpDocs.setShortcut("F1")
        self.aHelpDocs.triggered.connect(lambda: self._openWebsite(docUrl))
        self.helpMenu.addAction(self.aHelpDocs)

        # Help > User Manual (PDF)
        if isinstance(self.mainConf.pdfDocs, Path):
            self.aPdfDocs = QAction(self.tr("User Manual (PDF)"), self)
            self.aPdfDocs.setShortcut("Shift+F1")
            self.aPdfDocs.triggered.connect(self._openUserManualFile)
            self.helpMenu.addAction(self.aPdfDocs)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Document > Report an Issue
        self.aIssue = QAction(self.tr("Report an Issue (GitHub)"), self)
        self.aIssue.triggered.connect(lambda: self._openWebsite(novelwriter.__issuesurl__))
        self.helpMenu.addAction(self.aIssue)

        # Document > Ask a Question
        self.aQuestion = QAction(self.tr("Ask a Question (GitHub)"), self)
        self.aQuestion.triggered.connect(lambda: self._openWebsite(novelwriter.__helpurl__))
        self.helpMenu.addAction(self.aQuestion)

        # Document > Main Website
        self.aWebsite = QAction(self.tr("The novelWriter Website"), self)
        self.aWebsite.triggered.connect(lambda: self._openWebsite(novelwriter.__url__))
        self.helpMenu.addAction(self.aWebsite)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Document > Check for Updates
        self.aUpdates = QAction(self.tr("Check for New Release"), self)
        self.aUpdates.triggered.connect(lambda: self.mainGui.showUpdatesDialog())
        self.helpMenu.addAction(self.aUpdates)

        return

# END Class GuiMainMenu
