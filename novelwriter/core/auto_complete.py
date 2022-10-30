"""
novelWriter – Tags auto completer
===========================
Simple wrapper for completer based on QCompleter,

File History:
Created: 2022-10-30 [2.0rc1] TagsCompleter

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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


from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QCompleter


class TagsCompleter(QCompleter):
    insertText = pyqtSignal(str)

    def __init__(self, items=[], parent=None):
        QCompleter.__init__(self, items, parent)
        # add settings to switch
        self.setCompletionMode(QCompleter.UnfilteredPopupCompletion) # all possible completion
        #self.setCompletionMode(QCompleter.PopupCompletion)  # completion by startswith
        self.highlighted.connect(self.setHighlighted)

    def setHighlighted(self, text):
        self.lastSelected = text

    def getSelected(self):
        return self.lastSelected
