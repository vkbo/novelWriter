from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QCompleter


class TagsCompleter(QCompleter):
    insertText = pyqtSignal(str)

    def __init__(self, items=[], parent=None):
        QCompleter.__init__(self, items, parent)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.highlighted.connect(self.setHighlighted)

    def setHighlighted(self, text):
        self.lastSelected = text

    def getSelected(self):
        return self.lastSelected
