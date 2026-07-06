"""
novelWriter – GUI Editor Search
===============================

This file is a part of novelWriter
Copyright (C) 2026 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa

from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from PyQt6.QtCore import QRegularExpression, Qt, pyqtSlot
from PyQt6.QtGui import QAction, QPalette
from PyQt6.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, QLineEdit, QToolBar

from novelwriter import CONFIG, SHARED
from novelwriter.constants import nwConst
from novelwriter.extensions.modified import NIconToggleButton, NIconToolButton
from novelwriter.types import QtAlignLeft, QtAlignRight, QtModShift

if TYPE_CHECKING:
    from novelwriter.editor.editor import GuiDocEditor

logger = logging.getLogger(__name__)


class GuiDocEditSearch(QFrame):
    """The Embedded Document Search/Replace Feature.

    Only used by DocEditor, and is at a fixed position in the
    QTextEdit's viewport.
    """

    def __init__(self, docEditor: GuiDocEditor) -> None:
        super().__init__(parent=docEditor)

        logger.debug("Create: GuiDocEditSearch")

        self.docEditor = docEditor

        iSz = SHARED.theme.baseIconSize

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)

        self.mainBox = QGridLayout(self)
        self.setLayout(self.mainBox)

        # Text Boxes
        # ==========

        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText(self.tr("Search for"))
        self.searchBox.returnPressed.connect(self._doSearch)

        self.replaceBox = QLineEdit(self)
        self.replaceBox.setPlaceholderText(self.tr("Replace with"))
        self.replaceBox.returnPressed.connect(self._doReplace)

        self.searchOpt = QToolBar(self)
        self.searchOpt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.searchOpt.setIconSize(iSz)
        self.searchOpt.setContentsMargins(0, 0, 0, 0)

        self.searchLabel = QLabel(self.tr("Search"), self)
        self.searchLabel.setIndent(6)

        self.resultLabel = QLabel("?/?", self)

        self.toggleCase = QAction(self.tr("Case Sensitive"), self)
        self.toggleCase.setCheckable(True)
        self.toggleCase.setChecked(CONFIG.searchCase)
        self.toggleCase.toggled.connect(self._doToggleCase)
        self.searchOpt.addAction(self.toggleCase)

        self.toggleWord = QAction(self.tr("Whole Words Only"), self)
        self.toggleWord.setCheckable(True)
        self.toggleWord.setChecked(CONFIG.searchWord)
        self.toggleWord.toggled.connect(self._doToggleWord)
        self.searchOpt.addAction(self.toggleWord)

        self.toggleRegEx = QAction(self.tr("RegEx Mode"), self)
        self.toggleRegEx.setCheckable(True)
        self.toggleRegEx.setChecked(CONFIG.searchRegEx)
        self.toggleRegEx.toggled.connect(self._doToggleRegEx)
        self.searchOpt.addAction(self.toggleRegEx)

        self.toggleLoop = QAction(self.tr("Loop Search"), self)
        self.toggleLoop.setCheckable(True)
        self.toggleLoop.setChecked(CONFIG.searchLoop)
        self.toggleLoop.toggled.connect(self._doToggleLoop)
        self.searchOpt.addAction(self.toggleLoop)

        self.toggleProject = QAction(self.tr("Search Next File"), self)
        self.toggleProject.setCheckable(True)
        self.toggleProject.setChecked(CONFIG.searchNextFile)
        self.toggleProject.toggled.connect(self._doToggleProject)
        self.searchOpt.addAction(self.toggleProject)

        self.searchOpt.addSeparator()

        self.toggleMatchCap = QAction(self.tr("Preserve Case"), self)
        self.toggleMatchCap.setCheckable(True)
        self.toggleMatchCap.setChecked(CONFIG.searchMatchCap)
        self.toggleMatchCap.toggled.connect(self._doToggleMatchCap)
        self.searchOpt.addAction(self.toggleMatchCap)

        self.searchOpt.addSeparator()

        self.cancelSearch = QAction(self.tr("Close Search"), self)
        self.cancelSearch.triggered.connect(self.closeSearch)
        self.searchOpt.addAction(self.cancelSearch)

        # Buttons
        # =======

        self.showReplace = NIconToggleButton(self, iSz)
        self.showReplace.toggled.connect(self._doToggleReplace)

        self.searchButton = NIconToolButton(self, iSz)
        self.searchButton.setToolTip(self.tr("Find in current document"))
        self.searchButton.clicked.connect(self._doSearch)

        self.replaceButton = NIconToolButton(self, iSz)
        self.replaceButton.setToolTip(self.tr("Find and replace in current document"))
        self.replaceButton.clicked.connect(self._doReplace)

        self.mainBox.addWidget(self.searchLabel, 0, 0, 1, 2, QtAlignLeft)
        self.mainBox.addWidget(self.searchOpt, 0, 2, 1, 3, QtAlignRight)
        self.mainBox.addWidget(self.showReplace, 1, 0, 1, 1)
        self.mainBox.addWidget(self.searchBox, 1, 1, 1, 2)
        self.mainBox.addWidget(self.searchButton, 1, 3, 1, 1)
        self.mainBox.addWidget(self.resultLabel, 1, 4, 1, 1)
        self.mainBox.addWidget(self.replaceBox, 2, 1, 1, 2)
        self.mainBox.addWidget(self.replaceButton, 2, 3, 1, 1)

        self.mainBox.setColumnStretch(0, 0)
        self.mainBox.setColumnStretch(1, 0)
        self.mainBox.setColumnStretch(2, 1)
        self.mainBox.setColumnStretch(3, 0)
        self.mainBox.setColumnStretch(4, 0)
        self.mainBox.setColumnStretch(5, 0)
        self.mainBox.setSpacing(2)
        self.mainBox.setContentsMargins(6, 6, 6, 6)

        self.searchBox.setFixedWidth(200)
        self.replaceBox.setFixedWidth(200)
        self.replaceBox.setVisible(False)
        self.replaceButton.setVisible(False)
        self.adjustSize()

        self.updateFont()
        self.updateTheme()

        logger.debug("Ready: GuiDocEditSearch")

    ##
    #  Properties
    ##

    @property
    def searchText(self) -> str:
        """Return the current search text."""
        return self.searchBox.text()

    @property
    def replaceText(self) -> str:
        """Return the current replace text."""
        return self.replaceBox.text()

    ##
    #  Getters
    ##

    def getSearchObject(self) -> str | QRegularExpression:
        """Return the current search text either as text or as a regular
        expression object.
        """
        text = self.searchBox.text()
        if CONFIG.searchRegEx:
            rxOpt = QRegularExpression.PatternOption.UseUnicodePropertiesOption
            if not CONFIG.searchCase:
                rxOpt |= QRegularExpression.PatternOption.CaseInsensitiveOption
            regEx = QRegularExpression(text, rxOpt)
            self._alertSearchValid(regEx.isValid())
            return regEx
        return text

    ##
    #  Setters
    ##

    def setSearchText(self, text: str | None) -> None:
        """Open the search bar and set the search text to the text
        provided, if any.
        """
        if not self.isVisible():
            self.setVisible(True)
        if text is not None:
            self.searchBox.setText(text)
        self.searchBox.setFocus()
        self.searchBox.selectAll()
        if CONFIG.searchRegEx:
            self._alertSearchValid(True)

    def setReplaceText(self, text: str) -> None:
        """Set the replace text."""
        self.showReplace.setChecked(True)
        self.replaceBox.setFocus()
        self.replaceBox.setText(text)

    def setResultCount(self, currRes: int | None, resCount: int | None) -> None:
        """Set the count values for the current search."""
        lim = nwConst.MAX_SEARCH_RESULT
        numCount = f"{lim:n}+" if (resCount or 0) > lim else f"{resCount:n}"
        sCurrRes = "?" if currRes is None else str(currRes)
        sResCount = "?" if resCount is None else numCount
        minWidth = SHARED.theme.getTextWidth(f"{sResCount}//{sResCount}", SHARED.theme.guiFontSmall)
        self.resultLabel.setText(f"{sCurrRes}/{sResCount}")
        self.resultLabel.setMinimumWidth(minWidth)
        self.adjustSize()
        self.docEditor.updateDocMargins()

    ##
    #  Methods
    ##

    def updateFont(self) -> None:
        """Update the font settings."""
        self.setFont(SHARED.theme.guiFont)
        self.searchBox.setFont(SHARED.theme.guiFontSmall)
        self.replaceBox.setFont(SHARED.theme.guiFontSmall)
        self.searchLabel.setFont(SHARED.theme.guiFontSmall)
        self.resultLabel.setFont(SHARED.theme.guiFontSmall)
        self.resultLabel.setMinimumWidth(SHARED.theme.getTextWidth("?/?", SHARED.theme.guiFontSmall))

    def updateTheme(self) -> None:
        """Update theme elements."""
        logger.debug("Theme Update: GuiDocEditSearch")

        palette = QApplication.palette()
        self.setPalette(palette)
        self.searchBox.setPalette(palette)
        self.replaceBox.setPalette(palette)

        # Set icons
        self.toggleCase.setIcon(SHARED.theme.getIcon("search_case", "tool"))
        self.toggleWord.setIcon(SHARED.theme.getIcon("search_word", "tool"))
        self.toggleRegEx.setIcon(SHARED.theme.getIcon("search_regex", "tool"))
        self.toggleLoop.setIcon(SHARED.theme.getIcon("search_loop", "tool"))
        self.toggleProject.setIcon(SHARED.theme.getIcon("search_project", "tool"))
        self.toggleMatchCap.setIcon(SHARED.theme.getIcon("search_preserve", "tool"))
        self.cancelSearch.setIcon(SHARED.theme.getIcon("search_cancel", "tool"))
        self.searchButton.setThemeIcon("search", "action")
        self.replaceButton.setThemeIcon("search_replace", "apply")
        self.showReplace.setThemeIcon("unfold", "default")

        # Set stylesheets
        self.searchOpt.setStyleSheet("QToolBar {padding: 0;}")
        self.showReplace.setStyleSheet("QToolButton {border: none; background: transparent;}")

    def cycleFocus(self) -> bool:
        """Cycle focus on tab key press. This just alternates focus
        between the two input boxes, if the replace box is visible.
        """
        if self.searchBox.hasFocus():
            self.replaceBox.setFocus()
            return True
        elif self.replaceBox.hasFocus():
            self.searchBox.setFocus()
            return True
        return False

    def anyFocus(self) -> bool:
        """Return True if any of the input boxes have focus."""
        return self.hasFocus() or self.isAncestorOf(QApplication.focusWidget())

    ##
    #  Public Slots
    ##

    @pyqtSlot()
    def closeSearch(self) -> None:
        """Close the search box."""
        self.showReplace.setChecked(False)
        self.setVisible(False)
        self.docEditor.updateDocMargins()
        self.docEditor.setFocus()

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _doSearch(self) -> None:
        """Call the search action function for the document editor."""
        self.docEditor.findNext(goBack=(QApplication.keyboardModifiers() == QtModShift))

    @pyqtSlot()
    def _doReplace(self) -> None:
        """Call the replace action function for the document editor."""
        self.docEditor.replaceNext()

    @pyqtSlot(bool)
    def _doToggleReplace(self, state: bool) -> None:
        """Toggle the show/hide of the replace box."""
        self.replaceBox.setVisible(state)
        self.replaceButton.setVisible(state)
        self.adjustSize()
        self.docEditor.updateDocMargins()

    @pyqtSlot(bool)
    def _doToggleCase(self, state: bool) -> None:
        """Enable/disable case sensitive mode."""
        CONFIG.searchCase = state

    @pyqtSlot(bool)
    def _doToggleWord(self, state: bool) -> None:
        """Enable/disable whole word search mode."""
        CONFIG.searchWord = state

    @pyqtSlot(bool)
    def _doToggleRegEx(self, state: bool) -> None:
        """Enable/disable regular expression search mode."""
        CONFIG.searchRegEx = state

    @pyqtSlot(bool)
    def _doToggleLoop(self, state: bool) -> None:
        """Enable/disable looping the search."""
        CONFIG.searchLoop = state

    @pyqtSlot(bool)
    def _doToggleProject(self, state: bool) -> None:
        """Enable/disable continuing search in next project file."""
        CONFIG.searchNextFile = state

    @pyqtSlot(bool)
    def _doToggleMatchCap(self, state: bool) -> None:
        """Enable/disable preserving capitalisation when replacing."""
        CONFIG.searchMatchCap = state

    ##
    #  Internal Functions
    ##

    def _alertSearchValid(self, isValid: bool) -> None:
        """Highlight the search box to indicate the search string is or
        isn't valid. Take the colour from the replace box.
        """
        palette = self.replaceBox.palette()
        palette.setColor(QPalette.ColorRole.Text, palette.text().color() if isValid else SHARED.theme.errorText)
        self.searchBox.setPalette(palette)
