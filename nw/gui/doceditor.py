# -*- coding: utf-8 -*
"""novelWriter GUI Document Editor

 novelWriter – GUI Document Editor
===================================
 Class holding the document editor

 File History:
 Created: 2018-09-29 [0.0.1]

"""

import logging
import nw

from PyQt5.QtWidgets import QWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QFrame, QSplitter, QToolBar, QAction, QScrollArea
from PyQt5.QtCore    import Qt, QSize, QSizeF
from PyQt5.QtGui     import QIcon, QFont

logger = logging.getLogger(__name__)

class GuiDocEditor(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        logger.debug("Initialising DocEditor ...")
        self.mainConf  = nw.CONFIG

        self.outerBox  = QVBoxLayout()
        self.guiEditor = QTextEdit()
        self.guiEditor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setLayout(self.outerBox)

        self.metaPane = QFrame()
        self.docPane = QScrollArea()
        self.metaPane.setFrameShape(QFrame.StyledPanel)
        self.docPane.setFrameShape(QFrame.StyledPanel)
        # self.docPane.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.splitEdit = QSplitter(Qt.Horizontal)
        self.splitEdit.addWidget(self.docPane)
        self.splitEdit.addWidget(self.metaPane)

        self.docBox = QHBoxLayout()
        self.docPane.setLayout(self.docBox)
        self.docBox.addStretch(0)
        self.docBox.addWidget(self.guiEditor)
        self.docBox.addStretch(0)
        self.editToolBar = QToolBar()
        self._buildTabToolBar()

        self.outerBox.addWidget(self.editToolBar)
        self.outerBox.addWidget(self.splitEdit)

        # self.guiEditor.setFixedWidth(600)
        self.guiEditor.setMinimumWidth(600)
        # self.guiEditor.setCurrentFont(self.docFont)
        # self.guiEditor.setContentsMargins(20,20,20,20)
        self.guiEditor.setStyleSheet(
            "QTextEdit {background-color: #ffffff;};"
        )
        theDoc = self.guiEditor.document()
        theDoc.setDefaultFont(QFont("Source Sans Pro",13))
        theDoc.setDocumentMargin(20)
        theDoc.setTextWidth(600)
        # theDoc.setPageSize(QSizeF(600,600))
        theDoc.setDefaultStyleSheet("""
            body {
                background-color: #ffffff;
            }
            p {
                text-indent: 0px;
                margin: 4px 0px;
                text-align: justify;
            }
            p+p {
                text-indent: 40px;
            }
        """)

        logger.debug("DocEditor initialisation complete")

        return

    def setText(self, docHtml):
        self.guiEditor.setPlainText(docHtml)
        return True

    def getText(self):
        theText = self.guiEditor.toPlainText()
        return theText

    def _buildTabToolBar(self):
        toolBar = self.editToolBar
        toolBar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        toolBar.setIconSize(QSize(16,16))

        # Text > Bold
        tbTextBold = QAction(QIcon.fromTheme("format-text-bold"), "Bold (Ctrl+B)", toolBar)
        tbTextBold.setShortcut("Ctrl+B")
        tbTextBold.setStatusTip("Toggle Selected Text Bold")
        toolBar.addAction(tbTextBold)

        # Text > Italics
        tbTextItalic = QAction(QIcon.fromTheme("format-text-italic"), "Italic (Ctrl+I)", toolBar)
        tbTextItalic.setShortcut("Ctrl+I")
        tbTextItalic.setStatusTip("Toggle Selected Text Italic")
        toolBar.addAction(tbTextItalic)

        # Text > Underline
        tbTextUnderline = QAction(QIcon.fromTheme("format-text-underline"), "Underline (Ctrl+U)", toolBar)
        tbTextUnderline.setShortcut("Ctrl+U")
        tbTextUnderline.setStatusTip("Toggle Selected Text Underline")
        toolBar.addAction(tbTextUnderline)

        # Text > Strikethrough
        tbTextStrikethrough = QAction(QIcon.fromTheme("format-text-strikethrough"), "Strikethrough (Ctrl+D)", toolBar)
        tbTextStrikethrough.setShortcut("Ctrl+D")
        tbTextStrikethrough.setStatusTip("Toggle Selected Text Strikethrough")
        toolBar.addAction(tbTextStrikethrough)

        # --------------------
        toolBar.addSeparator()

        # Edit > Cut
        tbEditCut = QAction(QIcon.fromTheme("edit-cut"), "Cut (Ctrl+X)", toolBar)
        tbEditCut.setShortcut("Ctrl+X")
        tbEditCut.setStatusTip("Cut Selected Text")
        toolBar.addAction(tbEditCut)

        # Edit > Copy
        tbEditCopy = QAction(QIcon.fromTheme("edit-copy"), "Copy (Ctrl+C)", toolBar)
        tbEditCopy.setShortcut("Ctrl+C")
        tbEditCopy.setStatusTip("Copy Selected Text")
        toolBar.addAction(tbEditCopy)

        # Edit > Paste
        tbEditPaste = QAction(QIcon.fromTheme("edit-paste"), "Paste (Ctrl+V)", toolBar)
        tbEditPaste.setShortcut("Ctrl+V")
        tbEditPaste.setStatusTip("Paste Text")
        toolBar.addAction(tbEditPaste)

        # --------------------
        toolBar.addSeparator()

        # Edit > Undo
        tbEditUndo = QAction(QIcon.fromTheme("edit-undo"), "Undo (Ctrl+Z)", toolBar)
        tbEditUndo.setShortcut("Ctrl+Z")
        tbEditUndo.setStatusTip("Undo Last Change")
        toolBar.addAction(tbEditUndo)

        # Edit > Redo
        tbEditRedo = QAction(QIcon.fromTheme("edit-redo"), "Redo (Ctrl+Y)", toolBar)
        tbEditRedo.setShortcut("Ctrl+Y")
        tbEditRedo.setStatusTip("Revert Last Undo")
        toolBar.addAction(tbEditRedo)

        return

# END Class GuiDocEditor
