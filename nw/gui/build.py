# -*- coding: utf-8 -*-
"""novelWriter GUI Build Novel Project

 novelWriter – GUI Build Novel Project
=======================================
 Class holding the build novel project dialog

 File History:
 Created: 2020-05-09 [0.5]

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

import nw
import logging
import json
import os

from time import time
from datetime import datetime

from PyQt5.QtCore import Qt, QByteArray, QTimer
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtGui import (
    QPalette, QColor, QTextDocumentWriter, QFont, QCursor
)
from PyQt5.QtWidgets import (
    qApp, QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QLabel,
    QLineEdit, QGroupBox, QGridLayout, QProgressBar, QMenu, QAction,
    QFileDialog, QFontDialog, QSpinBox, QScrollArea, QSplitter, QWidget,
    QSizePolicy
)

from nw.common import fuzzyTime, makeFileNameSafe
from nw.gui.custom import QSwitch
from nw.core import ToHtml
from nw.constants import (
    nwConst, nwAlert, nwFiles, nwItemType, nwItemLayout, nwItemClass
)

logger = logging.getLogger(__name__)

class GuiBuildNovel(QDialog):

    FMT_ODT    = 1
    FMT_PDF    = 2
    FMT_HTM    = 3
    FMT_MD     = 4
    FMT_NWD    = 5
    FMT_TXT    = 6
    FMT_JSON_H = 7
    FMT_JSON_M = 8

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiBuildNovel ...")
        self.setObjectName("GuiBuildNovel")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.optState   = self.theProject.optState

        self.htmlText  = [] # List of html documents
        self.htmlStyle = [] # List of html styles
        self.nwdText   = [] # List of markdown documents
        self.buildTime = 0  # The timestamp of the last build

        self.setWindowTitle("Build Novel Project")
        self.setMinimumWidth(self.mainConf.pxInt(700))
        self.setMinimumHeight(self.mainConf.pxInt(600))

        self.resize(
            self.mainConf.pxInt(self.optState.getInt("GuiBuildNovel", "winWidth",  900)),
            self.mainConf.pxInt(self.optState.getInt("GuiBuildNovel", "winHeight", 800))
        )

        self.docView = GuiBuildNovelDocView(self, self.theProject)

        # Title Formats
        # =============

        self.titleGroup = QGroupBox("Title Formats for Novel Files", self)
        self.titleForm  = QGridLayout(self)
        self.titleGroup.setLayout(self.titleForm)

        fmtHelp = (
            r"<b>Formatting Codes:</b><br>"
            r"%title% for the title as set in the document<br>"
            r"%ch% for chapter number (1, 2, 3)<br>"
            r"%chw% for chapter number as a word (one, two)<br>"
            r"%chI% for chapter number in upper case Roman<br>"
            r"%chi% for chapter number in lower case Roman<br>"
            r"%sc% for scene number within chapter<br>"
            r"%sca% for scene number within novel"
        )
        fmtScHelp = (
            r"<br><br>"
            r"Leave blank to skip this heading, or set to a static text, like "
            r"for instance '* * *', to make a separator. The separator will "
            r"be centred automatically and only appear between sections of "
            r"the same type."
        )
        xFmt = self.mainConf.pxInt(100)

        self.fmtTitle = QLineEdit()
        self.fmtTitle.setMaxLength(200)
        self.fmtTitle.setMinimumWidth(xFmt)
        self.fmtTitle.setToolTip(fmtHelp)
        self.fmtTitle.setText(
            self._reFmtCodes(self.theProject.titleFormat["title"])
        )

        self.fmtChapter = QLineEdit()
        self.fmtChapter.setMaxLength(200)
        self.fmtChapter.setMinimumWidth(xFmt)
        self.fmtChapter.setToolTip(fmtHelp)
        self.fmtChapter.setText(
            self._reFmtCodes(self.theProject.titleFormat["chapter"])
        )

        self.fmtUnnumbered = QLineEdit()
        self.fmtUnnumbered.setMaxLength(200)
        self.fmtUnnumbered.setMinimumWidth(xFmt)
        self.fmtUnnumbered.setToolTip(fmtHelp)
        self.fmtUnnumbered.setText(
            self._reFmtCodes(self.theProject.titleFormat["unnumbered"])
        )

        self.fmtScene = QLineEdit()
        self.fmtScene.setMaxLength(200)
        self.fmtScene.setMinimumWidth(xFmt)
        self.fmtScene.setToolTip(fmtHelp + fmtScHelp)
        self.fmtScene.setText(
            self._reFmtCodes(self.theProject.titleFormat["scene"])
        )

        self.fmtSection = QLineEdit()
        self.fmtSection.setMaxLength(200)
        self.fmtSection.setMinimumWidth(xFmt)
        self.fmtSection.setToolTip(fmtHelp + fmtScHelp)
        self.fmtSection.setText(
            self._reFmtCodes(self.theProject.titleFormat["section"])
        )

        # Dummy boxes due to QGridView and QLineEdit expand bug
        self.boxTitle = QHBoxLayout()
        self.boxTitle.addWidget(self.fmtTitle)
        self.boxChapter = QHBoxLayout()
        self.boxChapter.addWidget(self.fmtChapter)
        self.boxUnnumbered = QHBoxLayout()
        self.boxUnnumbered.addWidget(self.fmtUnnumbered)
        self.boxScene = QHBoxLayout()
        self.boxScene.addWidget(self.fmtScene)
        self.boxSection = QHBoxLayout()
        self.boxSection.addWidget(self.fmtSection)

        self.titleForm.addWidget(QLabel("Title"),      0, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addLayout(self.boxTitle,        0, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(QLabel("Chapter"),    1, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addLayout(self.boxChapter,      1, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(QLabel("Unnumbered"), 2, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addLayout(self.boxUnnumbered,   2, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(QLabel("Scene"),      3, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addLayout(self.boxScene,        3, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(QLabel("Section"),    4, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addLayout(self.boxSection,      4, 1, 1, 1, Qt.AlignRight)

        self.titleForm.setColumnStretch(0, 0)
        self.titleForm.setColumnStretch(1, 1)

        # Text Options
        # =============

        self.formatGroup = QGroupBox("Formatting Options", self)
        self.formatForm  = QGridLayout(self)
        self.formatGroup.setLayout(self.formatForm)

        ## Font Family
        self.textFont = QLineEdit()
        self.textFont.setReadOnly(True)
        self.textFont.setMinimumWidth(xFmt)
        self.textFont.setText(
            self.optState.getString("GuiBuildNovel", "textFont", self.mainConf.textFont)
        )
        self.fontButton = QPushButton("...")
        self.fontButton.setMaximumWidth(int(2.5*self.theTheme.getTextWidth("...")))
        self.fontButton.clicked.connect(self._selectFont)

        self.textSize = QSpinBox(self)
        self.textSize.setFixedWidth(5*self.theTheme.textNWidth)
        self.textSize.setMinimum(6)
        self.textSize.setMaximum(72)
        self.textSize.setSingleStep(1)
        self.textSize.setToolTip(
            "The size is used for PDF and printing. Other formats have no size set."
        )
        self.textSize.setValue(
            self.optState.getInt("GuiBuildNovel", "textSize", self.mainConf.textSize)
        )

        self.justifyText = QSwitch()
        self.justifyText.setToolTip(
            "Applies to PDF, printing, HTML, and Open Document exports."
        )
        self.justifyText.setChecked(
            self.optState.getBool("GuiBuildNovel", "justifyText", False)
        )

        self.noStyling = QSwitch()
        self.noStyling.setToolTip(
            "Disable all styling of the text."
        )
        self.noStyling.setChecked(
            self.optState.getBool("GuiBuildNovel", "noStyling", False)
        )

        # Dummy box due to QGridView and QLineEdit expand bug
        self.boxFont = QHBoxLayout()
        self.boxFont.addWidget(self.textFont)

        self.formatForm.addWidget(QLabel("Font family"),     0, 0, 1, 1, Qt.AlignLeft)
        self.formatForm.addLayout(self.boxFont,              0, 1, 1, 1, Qt.AlignRight)
        self.formatForm.addWidget(self.fontButton,           0, 2, 1, 1, Qt.AlignRight)
        self.formatForm.addWidget(QLabel("Font size"),       1, 0, 1, 1, Qt.AlignLeft)
        self.formatForm.addWidget(self.textSize,             1, 1, 1, 2, Qt.AlignRight)
        self.formatForm.addWidget(QLabel("Justify text"),    2, 0, 1, 1, Qt.AlignLeft)
        self.formatForm.addWidget(self.justifyText,          2, 1, 1, 2, Qt.AlignRight)
        self.formatForm.addWidget(QLabel("Disable styling"), 3, 0, 1, 1, Qt.AlignLeft)
        self.formatForm.addWidget(self.noStyling,            3, 1, 1, 2, Qt.AlignRight)

        self.formatForm.setColumnStretch(0, 0)
        self.formatForm.setColumnStretch(1, 1)
        self.formatForm.setColumnStretch(2, 0)

        # Include Switches
        # ================

        self.textGroup = QGroupBox("Text Options", self)
        self.textForm  = QGridLayout(self)
        self.textGroup.setLayout(self.textForm)

        self.includeSynopsis = QSwitch()
        self.includeSynopsis.setToolTip(
            "Include synopsis comments in the output."
        )
        self.includeSynopsis.setChecked(
            self.optState.getBool("GuiBuildNovel", "incSynopsis", False)
        )

        self.includeComments = QSwitch()
        self.includeComments.setToolTip(
            "Include plain comments in the output."
        )
        self.includeComments.setChecked(
            self.optState.getBool("GuiBuildNovel", "incComments", False)
        )

        self.includeKeywords = QSwitch()
        self.includeKeywords.setToolTip(
            "Include meta keywords (tags, references) in the output."
        )
        self.includeKeywords.setChecked(
            self.optState.getBool("GuiBuildNovel", "incKeywords", False)
        )

        self.includeBody = QSwitch()
        self.includeBody.setToolTip(
            "Include body text in the output."
        )
        self.includeBody.setChecked(
            self.optState.getBool("GuiBuildNovel", "incBodyText", True)
        )

        self.textForm.addWidget(QLabel("Include synopsis"),  0, 0, 1, 1, Qt.AlignLeft)
        self.textForm.addWidget(self.includeSynopsis,        0, 1, 1, 1, Qt.AlignRight)
        self.textForm.addWidget(QLabel("Include comments"),  1, 0, 1, 1, Qt.AlignLeft)
        self.textForm.addWidget(self.includeComments,        1, 1, 1, 1, Qt.AlignRight)
        self.textForm.addWidget(QLabel("Include keywords"),  2, 0, 1, 1, Qt.AlignLeft)
        self.textForm.addWidget(self.includeKeywords,        2, 1, 1, 1, Qt.AlignRight)
        self.textForm.addWidget(QLabel("Include body text"), 3, 0, 1, 1, Qt.AlignLeft)
        self.textForm.addWidget(self.includeBody,            3, 1, 1, 1, Qt.AlignRight)

        self.textForm.setColumnStretch(0, 1)
        self.textForm.setColumnStretch(1, 0)

        # File Filter Options
        # ===================

        self.fileGroup = QGroupBox("File Filter Options", self)
        self.fileForm  = QGridLayout(self)
        self.fileGroup.setLayout(self.fileForm)

        self.novelFiles = QSwitch()
        self.novelFiles.setToolTip(
            "Include files with layouts 'Book', 'Page', 'Partition', "
            "'Chapter', 'Unnumbered', and 'Scene'."
        )
        self.novelFiles.setChecked(
            self.optState.getBool("GuiBuildNovel", "addNovel", True)
        )

        self.noteFiles = QSwitch()
        self.noteFiles.setToolTip("Include files with layout 'Note'.")
        self.noteFiles.setChecked(
            self.optState.getBool("GuiBuildNovel", "addNotes", False)
        )

        self.ignoreFlag = QSwitch()
        self.ignoreFlag.setToolTip(
            "Ignore the 'Include when building project' setting and include "
            "all files in the output."
        )
        self.ignoreFlag.setChecked(
            self.optState.getBool("GuiBuildNovel", "ignoreFlag", False)
        )

        self.fileForm.addWidget(QLabel("Include novel files"), 0, 0, 1, 1, Qt.AlignLeft)
        self.fileForm.addWidget(self.novelFiles,               0, 1, 1, 1, Qt.AlignRight)
        self.fileForm.addWidget(QLabel("Include note files"),  1, 0, 1, 1, Qt.AlignLeft)
        self.fileForm.addWidget(self.noteFiles,                1, 1, 1, 1, Qt.AlignRight)
        self.fileForm.addWidget(QLabel("Ignore export flag"),  2, 0, 1, 1, Qt.AlignLeft)
        self.fileForm.addWidget(self.ignoreFlag,               2, 1, 1, 1, Qt.AlignRight)

        self.fileForm.setColumnStretch(0, 1)
        self.fileForm.setColumnStretch(1, 0)

        # Export Options
        # ==============

        self.exportGroup = QGroupBox("Export Options", self)
        self.exportForm  = QGridLayout(self)
        self.exportGroup.setLayout(self.exportForm)

        self.replaceTabs = QSwitch()
        self.replaceTabs.setToolTip(
            "Replace all tabs with eight spaces."
        )
        self.replaceTabs.setChecked(
            self.optState.getBool("GuiBuildNovel", "replaceTabs", False)
        )

        self.exportForm.addWidget(QLabel("Replace tabs with spaces"), 0, 0, 1, 1, Qt.AlignLeft)
        self.exportForm.addWidget(self.replaceTabs,                   0, 1, 1, 1, Qt.AlignRight)

        self.exportForm.setColumnStretch(0, 1)
        self.exportForm.setColumnStretch(1, 0)

        # Build Button
        # ============

        self.buildProgress = QProgressBar()
        self.buildProgress = QProgressBar()

        self.buildNovel = QPushButton("Build Project")
        self.buildNovel.clicked.connect(self._buildPreview)

        # Action Buttons
        # ==============

        self.buttonBox = QHBoxLayout()

        self.btnPrint = QPushButton("Print")
        self.btnPrint.clicked.connect(self._printDocument)

        self.btnSave = QPushButton("Save As")
        self.saveMenu = QMenu(self)
        self.btnSave.setMenu(self.saveMenu)

        self.saveODT = QAction("Open Document (.odt)", self)
        self.saveODT.triggered.connect(lambda: self._saveDocument(self.FMT_ODT))
        self.saveMenu.addAction(self.saveODT)

        self.savePDF = QAction("Portable Document Format (.pdf)", self)
        self.savePDF.triggered.connect(lambda: self._saveDocument(self.FMT_PDF))
        self.saveMenu.addAction(self.savePDF)

        self.saveHTM = QAction("novelWriter HTML (.htm)", self)
        self.saveHTM.triggered.connect(lambda: self._saveDocument(self.FMT_HTM))
        self.saveMenu.addAction(self.saveHTM)

        self.saveNWD = QAction("novelWriter Markdown (.nwd)", self)
        self.saveNWD.triggered.connect(lambda: self._saveDocument(self.FMT_NWD))
        self.saveMenu.addAction(self.saveNWD)

        if self.mainConf.verQtValue >= 51400:
            self.saveMD = QAction("Markdown (.md)", self)
            self.saveMD.triggered.connect(lambda: self._saveDocument(self.FMT_MD))
            self.saveMenu.addAction(self.saveMD)

        self.saveTXT = QAction("Plain Text (.txt)", self)
        self.saveTXT.triggered.connect(lambda: self._saveDocument(self.FMT_TXT))
        self.saveMenu.addAction(self.saveTXT)

        self.saveJsonH = QAction("JSON + novelWriter HTML (.json)", self)
        self.saveJsonH.triggered.connect(lambda: self._saveDocument(self.FMT_JSON_H))
        self.saveMenu.addAction(self.saveJsonH)

        self.saveJsonM = QAction("JSON + novelWriters Markdown (.json)", self)
        self.saveJsonM.triggered.connect(lambda: self._saveDocument(self.FMT_JSON_M))
        self.saveMenu.addAction(self.saveJsonM)

        self.btnClose = QPushButton("Close")
        self.btnClose.clicked.connect(self._doClose)

        self.buttonBox.addWidget(self.btnSave)
        self.buttonBox.addWidget(self.btnPrint)
        self.buttonBox.addWidget(self.btnClose)
        self.buttonBox.setSpacing(self.mainConf.pxInt(4))

        # Assemble GUI
        # ============

        # Splitter Position
        boxWidth = self.mainConf.pxInt(350)
        boxWidth = self.optState.getInt("GuiBuildNovel", "boxWidth", boxWidth)
        docWidth = max(self.width() - boxWidth, 100)
        docWidth = self.optState.getInt("GuiBuildNovel", "docWidth", docWidth)

        # The Tool Box
        self.toolsBox = QVBoxLayout()
        self.toolsBox.addWidget(self.titleGroup)
        self.toolsBox.addWidget(self.formatGroup)
        self.toolsBox.addWidget(self.textGroup)
        self.toolsBox.addWidget(self.fileGroup)
        self.toolsBox.addWidget(self.exportGroup)
        self.toolsBox.addStretch(1)

        # Tool Box Wrapper Widget
        self.toolsWidget = QWidget()
        self.toolsWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.toolsWidget.setLayout(self.toolsBox)

        # Tool Box Scroll Area
        self.toolsArea = QScrollArea()
        self.toolsArea.setMinimumWidth(self.mainConf.pxInt(250))
        self.toolsArea.setWidgetResizable(True)
        self.toolsArea.setWidget(self.toolsWidget)

        if self.mainConf.hideVScroll:
            self.toolsArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.toolsArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if self.mainConf.hideHScroll:
            self.toolsArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.toolsArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Tools and Buttons Layout
        tSp = self.mainConf.pxInt(8)
        self.innerBox = QVBoxLayout()
        self.innerBox.addWidget(self.toolsArea)
        self.innerBox.addSpacing(tSp)
        self.innerBox.addWidget(self.buildProgress)
        self.innerBox.addWidget(self.buildNovel)
        self.innerBox.addSpacing(tSp)
        self.innerBox.addLayout(self.buttonBox)

        # Tools and Buttons Wrapper Widget
        self.innerWidget = QWidget()
        self.innerWidget.setLayout(self.innerBox)

        # Main Dialog Splitter
        self.mainSplit = QSplitter(Qt.Horizontal)
        self.mainSplit.addWidget(self.innerWidget)
        self.mainSplit.addWidget(self.docView)
        self.mainSplit.setSizes([boxWidth, docWidth])

        self.idxSettings = self.mainSplit.indexOf(self.innerWidget)
        self.idxDocument = self.mainSplit.indexOf(self.docView)

        self.mainSplit.setCollapsible(self.idxSettings, False)
        self.mainSplit.setCollapsible(self.idxDocument, False)

        # Outer Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.mainSplit)

        self.setLayout(self.outerBox)
        self.buildNovel.setFocus()

        logger.debug("GuiBuildNovel initialisation complete")

        return

    def viewCachedDoc(self):
        """Load the previously generated document from cache.
        """
        if self._loadCache():
            textFont    = self.textFont.text()
            textSize    = self.textSize.value()
            justifyText = self.justifyText.isChecked()
            self.docView.setTextFont(textFont, textSize)
            self.docView.setJustify(justifyText)
            if self.noStyling.isChecked():
                self.docView.clearStyleSheet()
            else:
                self.docView.setStyleSheet(self.htmlStyle)

            htmlSize = sum([len(x) for x in self.htmlText])
            if htmlSize < nwConst.MAX_BUILDSIZE:
                qApp.processEvents()
                self.docView.setContent(self.htmlText, self.buildTime)
            else:
                self.docView.setText(
                    "Failed to generate preview. The result is too big."
                )
                self._enableQtSave(False)

        else:
            self.htmlText = []
            self.htmlStyle = []
            self.nwdText = []
            self.buildTime = 0
            return False

        return True

    ##
    #  Slots
    ##

    def _buildPreview(self):
        """Build a preview of the project in the document viewer.
        """
        # Get Settings
        fmtTitle      = self.fmtTitle.text().strip()
        fmtChapter    = self.fmtChapter.text().strip()
        fmtUnnumbered = self.fmtUnnumbered.text().strip()
        fmtScene      = self.fmtScene.text().strip()
        fmtSection    = self.fmtSection.text().strip()
        justifyText   = self.justifyText.isChecked()
        noStyling     = self.noStyling.isChecked()
        textFont      = self.textFont.text()
        textSize      = self.textSize.value()
        incSynopsis   = self.includeSynopsis.isChecked()
        incComments   = self.includeComments.isChecked()
        incKeywords   = self.includeKeywords.isChecked()
        novelFiles    = self.novelFiles.isChecked()
        noteFiles     = self.noteFiles.isChecked()
        ignoreFlag    = self.ignoreFlag.isChecked()
        includeBody   = self.includeBody.isChecked()
        replaceTabs   = self.replaceTabs.isChecked()

        makeHtml = ToHtml(self.theProject, self.theParent)
        makeHtml.setTitleFormat(fmtTitle)
        makeHtml.setChapterFormat(fmtChapter)
        makeHtml.setUnNumberedFormat(fmtUnnumbered)
        makeHtml.setSceneFormat(fmtScene, fmtScene == "")
        makeHtml.setSectionFormat(fmtSection, fmtSection == "")
        makeHtml.setBodyText(includeBody)
        makeHtml.setSynopsis(incSynopsis)
        makeHtml.setComments(incComments)
        makeHtml.setKeywords(incKeywords)
        makeHtml.setJustify(justifyText)
        makeHtml.setStyles(not noStyling)

        # Make sure the tree order is correct
        self.theParent.treeView.flushTreeOrder()

        self.buildProgress.setMaximum(len(self.theProject.projTree))
        self.buildProgress.setValue(0)

        tStart = int(time())

        self.htmlText = []
        self.htmlStyle = []
        self.nwdText = []

        htmlSize = 0

        for nItt, tItem in enumerate(self.theProject.projTree):

            noteRoot  = noteFiles
            noteRoot &= tItem.itemType == nwItemType.ROOT
            noteRoot &= tItem.itemClass != nwItemClass.NOVEL
            noteRoot &= tItem.itemClass != nwItemClass.ARCHIVE

            try:
                if noteRoot:
                    # Add headers for root folders of notes
                    makeHtml.addRootHeading(tItem.itemHandle)
                    makeHtml.doConvert()
                    self.htmlText.append(makeHtml.getResult())
                    self.nwdText.append(makeHtml.getFilteredMarkdown())
                    htmlSize += makeHtml.getResultSize()

                elif self._checkInclude(tItem, noteFiles, novelFiles, ignoreFlag):
                    makeHtml.setText(tItem.itemHandle)
                    makeHtml.doAutoReplace()
                    makeHtml.tokenizeText()
                    makeHtml.doHeaders()
                    makeHtml.doConvert()
                    makeHtml.doPostProcessing()
                    self.htmlText.append(makeHtml.getResult())
                    self.nwdText.append(makeHtml.getFilteredMarkdown())
                    htmlSize += makeHtml.getResultSize()

            except Exception as e:
                logger.error("Failed to generate html of document '%s'" % tItem.itemHandle)
                logger.error(str(e))
                self.docView.setText((
                    "Failed to generate preview. "
                    "Document with title '%s' could not be parsed."
                ) % tItem.itemName)
                return False

            # Update progress bar, also for skipped items
            self.buildProgress.setValue(nItt+1)

        if makeHtml.errData:
            self.theParent.makeAlert((
                "There were problems when building the project:"
                "<br>-&nbsp;%s"
            ) % "<br>-&nbsp;".join(makeHtml.errData), nwAlert.ERROR)

        if replaceTabs:
            htmlText = []
            eightSpace = "&nbsp;"*8
            for aLine in self.htmlText:
                htmlText.append(aLine.replace("\t", eightSpace))
            self.htmlText = htmlText

            nwdText = []
            for aLine in self.nwdText:
                nwdText.append(aLine.replace("\t", "        "))
            self.nwdText = nwdText

        tEnd = int(time())
        logger.debug("Built project in %.3f ms" % (1000*(tEnd-tStart)))
        self.htmlStyle = makeHtml.getStyleSheet()
        self.buildTime = tEnd

        # Load the preview document with the html data
        self.docView.setTextFont(textFont, textSize)
        self.docView.setJustify(justifyText)
        if noStyling:
            self.docView.clearStyleSheet()
        else:
            self.docView.setStyleSheet(self.htmlStyle)

        if htmlSize < nwConst.MAX_BUILDSIZE:
            self.docView.setContent(self.htmlText, self.buildTime)
            self._enableQtSave(True)
        else:
            self.docView.setText(
                "Failed to generate preview. The result is too big."
            )
            self._enableQtSave(False)

        self._saveCache()

        return

    def _checkInclude(self, theItem, noteFiles, novelFiles, ignoreFlag):
        """This function checks whether a file should be included in the
        export or not. For standard note and novel files, this is
        controlled by the options selected by the user. For other files
        classified as non-exportable, a few checks must be made, and the
        following are not:
        * Items that are not actual files.
        * Items that have been orphaned which are tagged as NO_LAYOUT
          and NO_CLASS.
        * Items that appear in the TRASH folder or have parent set to
          None (orphaned files).
        """
        if theItem is None:
            return False

        if not theItem.isExported and not ignoreFlag:
            return False

        isNone  = theItem.itemType != nwItemType.FILE
        isNone |= theItem.itemLayout == nwItemLayout.NO_LAYOUT
        isNone |= theItem.itemClass == nwItemClass.NO_CLASS
        isNone |= theItem.itemClass == nwItemClass.TRASH
        isNone |= theItem.itemParent == self.theProject.projTree.trashRoot()
        isNone |= theItem.itemParent is None
        isNote  = theItem.itemLayout == nwItemLayout.NOTE
        isNovel = not isNone and not isNote

        if isNone:
            return False
        if isNote and not noteFiles:
            return False
        if isNovel and not novelFiles:
            return False

        rootItem = self.theProject.projTree.getRootItem(theItem.itemHandle)
        if rootItem.itemClass == nwItemClass.ARCHIVE:
            return False

        return True

    def _saveDocument(self, theFormat):
        """Save the document to various formats.
        """
        byteFmt = QByteArray()
        fileExt = ""
        textFmt = ""
        outTool = ""

        # Create the settings
        if theFormat == self.FMT_ODT:
            byteFmt.append("odf")
            fileExt = "odt"
            textFmt = "Open Document"
            outTool = "Qt"

        elif theFormat == self.FMT_PDF:
            fileExt = "pdf"
            textFmt = "PDF"
            outTool = "QtPrint"

        elif theFormat == self.FMT_HTM:
            fileExt = "htm"
            textFmt = "Plain HTML"
            outTool = "NW"

        elif theFormat == self.FMT_MD:
            byteFmt.append("markdown")
            fileExt = "md"
            textFmt = "Markdown"
            outTool = "Qt"

        elif theFormat == self.FMT_NWD:
            fileExt = "nwd"
            textFmt = "%s Markdown" % nw.__package__
            outTool = "NW"

        elif theFormat == self.FMT_TXT:
            byteFmt.append("plaintext")
            fileExt = "txt"
            textFmt = "Plain Text"
            outTool = "Qt"

        elif theFormat == self.FMT_JSON_H:
            fileExt = "json"
            textFmt = "JSON + %s HTML" % nw.__package__
            outTool = "NW"

        elif theFormat == self.FMT_JSON_M:
            fileExt = "json"
            textFmt = "JSON + %s Markdown" % nw.__package__
            outTool = "NW"

        else:
            return False

        # Generate the file name
        if fileExt:

            cleanName = makeFileNameSafe(self.theProject.projName)
            fileName  = "%s.%s" % (cleanName, fileExt)
            saveDir   = self.mainConf.lastPath
            savePath  = os.path.join(saveDir, fileName)
            if not os.path.isdir(saveDir):
                saveDir = self.mainConf.homePath

            dlgOpt  = QFileDialog.Options()
            dlgOpt |= QFileDialog.DontUseNativeDialog
            savePath, _ = QFileDialog.getSaveFileName(
                self, "Save Document As", savePath, options=dlgOpt
            )
            if not savePath:
                return False

            self.mainConf.setLastPath(savePath)

        else:
            return False

        # Do the actual writing
        wSuccess = False
        errMsg = ""
        if outTool == "Qt":
            docWriter = QTextDocumentWriter()
            docWriter.setFileName(savePath)
            docWriter.setFormat(byteFmt)
            wSuccess = docWriter.write(self.docView.qDocument)

        elif outTool == "NW":
            try:
                with open(savePath, mode="w", encoding="utf8") as outFile:
                    if theFormat == self.FMT_HTM:
                        # Write novelWriter HTML data
                        theStyle = self.htmlStyle.copy()
                        theStyle.append(r"article {width: 800px; margin: 40px auto;}")
                        bodyText = "".join(self.htmlText)
                        bodyText = bodyText.replace("\t", "&#09;")

                        theHtml = (
                            "<!DOCTYPE html>\n"
                            "<html>\n"
                            "<head>\n"
                            "<meta charset='utf-8'>\n"
                            "<title>{projTitle:s}</title>\n"
                            "</head>\n"
                            "<style>\n"
                            "{htmlStyle:s}\n"
                            "</style>\n"
                            "<body>\n"
                            "<article>\n"
                            "{bodyText:s}\n"
                            "</article>\n"
                            "</body>\n"
                            "</html>\n"
                        ).format(
                            projTitle = self.theProject.projName,
                            htmlStyle = "\n".join(theStyle),
                            bodyText = bodyText,
                        )
                        outFile.write(theHtml)

                    elif theFormat == self.FMT_NWD:
                        # Write novelWriter markdown data
                        for aLine in self.nwdText:
                            outFile.write(aLine)

                    elif theFormat == self.FMT_JSON_H or theFormat == self.FMT_JSON_M:
                        jsonData = {
                            "meta" : {
                                "workingTitle" : self.theProject.projName,
                                "novelTitle"   : self.theProject.bookTitle,
                                "authors"      : self.theProject.bookAuthors,
                                "buildTime"    : self.buildTime,
                            }
                        }

                        if theFormat == self.FMT_JSON_H:
                            theBody = []
                            for htmlPage in self.htmlText:
                                theBody.append(htmlPage.rstrip("\n").split("\n"))
                            jsonData["text"] = {
                                "css"  : self.htmlStyle,
                                "html" : theBody,
                            }
                        elif theFormat == self.FMT_JSON_M:
                            theBody = []
                            for nwdPage in self.nwdText:
                                theBody.append(nwdPage.split("\n"))
                            jsonData["text"] = {
                                "nwd" : theBody,
                            }

                        outFile.write(json.dumps(jsonData, indent=2))

                wSuccess = True

            except Exception as e:
                errMsg = str(e)

        elif outTool == "QtPrint" and theFormat == self.FMT_PDF:
            try:
                thePrinter = QPrinter()
                thePrinter.setOutputFormat(QPrinter.PdfFormat)
                thePrinter.setOrientation(QPrinter.Portrait)
                thePrinter.setDuplex(QPrinter.DuplexLongSide)
                thePrinter.setFontEmbeddingEnabled(True)
                thePrinter.setColorMode(QPrinter.Color)
                thePrinter.setOutputFileName(savePath)
                self.docView.qDocument.print(thePrinter)
                wSuccess = True

            except Exception as e:
                errMsg - str(e)

        else:
            errMsg = "Unknown format"

        # Report to user
        if wSuccess:
            self.theParent.makeAlert(
                "%s file successfully written to:<br> %s" % (
                    textFmt, savePath
                ), nwAlert.INFO
            )
        else:
            self.theParent.makeAlert(
                "Failed to write %s file. %s" % (
                    textFmt, errMsg
                ), nwAlert.ERROR
            )

        return wSuccess

    def _printDocument(self):
        """Open the print preview dialog.
        """
        thePreview = QPrintPreviewDialog(self)
        thePreview.paintRequested.connect(self._doPrintPreview)
        thePreview.exec_()
        return

    def _doPrintPreview(self, thePrinter):
        """Connect the print preview painter to the document viewer.
        """
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        thePrinter.setOrientation(QPrinter.Portrait)
        self.docView.qDocument.print(thePrinter)
        qApp.restoreOverrideCursor()
        return

    def _selectFont(self):
        """Open the QFontDialog and set a font for the font style.
        """
        currFont = QFont()
        currFont.setFamily(self.textFont.text())
        currFont.setPointSize(self.textSize.value())
        theFont, theStatus = QFontDialog.getFont(currFont, self)
        if theStatus:
            self.textFont.setText(theFont.family())
            self.textSize.setValue(theFont.pointSize())

        self.raise_() # Move the dialog to front (fixes a bug on macOS)

        return

    def _loadCache(self):
        """Save the current data to cache.
        """
        buildCache = os.path.join(self.theProject.projCache, nwFiles.BUILD_CACHE)
        dataCount = 0
        if os.path.isfile(buildCache):

            logger.debug("Loading build cache")
            try:
                with open(buildCache, mode="r", encoding="utf8") as inFile:
                    theJson = inFile.read()
                theData = json.loads(theJson)
            except Exception as e:
                logger.error("Failed to load build cache")
                logger.error(str(e))
                return False

            if "htmlText" in theData.keys():
                self.htmlText = theData["htmlText"]
                dataCount += 1
            if "htmlStyle" in theData.keys():
                self.htmlStyle = theData["htmlStyle"]
                dataCount += 1
            if "nwdText" in theData.keys():
                self.nwdText = theData["nwdText"]
                dataCount += 1
            if "buildTime" in theData.keys():
                self.buildTime = theData["buildTime"]

        return dataCount == 3

    def _saveCache(self):
        """Save the current data to cache.
        """
        buildCache = os.path.join(self.theProject.projCache, nwFiles.BUILD_CACHE)

        if self.mainConf.debugInfo:
            nIndent = 2
        else:
            nIndent = None

        logger.debug("Saving build cache")
        try:
            with open(buildCache, mode="w+", encoding="utf8") as outFile:
                outFile.write(json.dumps({
                    "htmlText"  : self.htmlText,
                    "htmlStyle" : self.htmlStyle,
                    "nwdText"   : self.nwdText,
                    "buildTime" : self.buildTime,
                }, indent=nIndent))
        except Exception as e:
            logger.error("Failed to save build cache")
            logger.error(str(e))
            return False

        return True

    def _doClose(self):
        """Close button was clicked.
        """
        self.close()
        return

    ##
    #  Events
    ##

    def closeEvent(self, theEvent):
        """Capture the user closing the window so we can save settings.
        """
        self._saveSettings()
        self.docView.clear()
        theEvent.accept()
        return

    ##
    #  Internal Functions
    ##

    def _enableQtSave(self, theState):
        """Set the enabled status of Save menu entries that depend on
        the QTextDocument.
        """
        self.saveODT.setEnabled(theState)
        self.savePDF.setEnabled(theState)
        self.saveTXT.setEnabled(theState)
        if self.mainConf.verQtValue >= 51400:
            self.saveMD.setEnabled(theState)
        return

    def _saveSettings(self):
        """Save the various user settings.
        """
        logger.debug("Saving GuiBuildNovel settings")

        # Formatting
        self.theProject.setTitleFormat({
            "title"      : self.fmtTitle.text().strip(),
            "chapter"    : self.fmtChapter.text().strip(),
            "unnumbered" : self.fmtUnnumbered.text().strip(),
            "scene"      : self.fmtScene.text().strip(),
            "section"    : self.fmtSection.text().strip(),
        })

        winWidth    = self.mainConf.rpxInt(self.width())
        winHeight   = self.mainConf.rpxInt(self.height())
        justifyText = self.justifyText.isChecked()
        noStyling   = self.noStyling.isChecked()
        textFont    = self.textFont.text()
        textSize    = self.textSize.value()
        novelFiles  = self.novelFiles.isChecked()
        noteFiles   = self.noteFiles.isChecked()
        ignoreFlag  = self.ignoreFlag.isChecked()
        incSynopsis = self.includeSynopsis.isChecked()
        incComments = self.includeComments.isChecked()
        incKeywords = self.includeKeywords.isChecked()
        incBodyText = self.includeBody.isChecked()
        replaceTabs = self.replaceTabs.isChecked()

        mainSplit = self.mainSplit.sizes()
        if len(mainSplit) == 2:
            boxWidth = self.mainConf.rpxInt(mainSplit[0])
            docWidth = self.mainConf.rpxInt(mainSplit[1])
        else:
            boxWidth = 100
            docWidth = 100

        # GUI Settings
        self.optState.setValue("GuiBuildNovel", "winWidth",    winWidth)
        self.optState.setValue("GuiBuildNovel", "winHeight",   winHeight)
        self.optState.setValue("GuiBuildNovel", "boxWidth",    boxWidth)
        self.optState.setValue("GuiBuildNovel", "docWidth",    docWidth)
        self.optState.setValue("GuiBuildNovel", "justifyText", justifyText)
        self.optState.setValue("GuiBuildNovel", "noStyling",   noStyling)
        self.optState.setValue("GuiBuildNovel", "textFont",    textFont)
        self.optState.setValue("GuiBuildNovel", "textSize",    textSize)
        self.optState.setValue("GuiBuildNovel", "addNovel",    novelFiles)
        self.optState.setValue("GuiBuildNovel", "addNotes",    noteFiles)
        self.optState.setValue("GuiBuildNovel", "ignoreFlag",  ignoreFlag)
        self.optState.setValue("GuiBuildNovel", "incSynopsis", incSynopsis)
        self.optState.setValue("GuiBuildNovel", "incComments", incComments)
        self.optState.setValue("GuiBuildNovel", "incKeywords", incKeywords)
        self.optState.setValue("GuiBuildNovel", "incBodyText", incBodyText)
        self.optState.setValue("GuiBuildNovel", "replaceTabs", replaceTabs)
        self.optState.saveSettings()

        return

    def _reFmtCodes(self, theFormat):
        """Translates old formatting codes to new ones.
        """
        theFormat = theFormat.replace(r"%chnum%",     r"%ch%")
        theFormat = theFormat.replace(r"%scnum%",     r"%sc%")
        theFormat = theFormat.replace(r"%scabsnum%",  r"%sca%")
        theFormat = theFormat.replace(r"%chnumword%", r"%chw%")
        return theFormat

# END Class GuiBuildNovel

class GuiBuildNovelDocView(QTextBrowser):

    def __init__(self, theParent, theProject):
        QTextBrowser.__init__(self, theParent)

        logger.debug("Initialising GuiBuildNovelDocView ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.buildTime  = 0

        self.setMinimumWidth(40*self.theParent.theTheme.textNWidth)
        self.setOpenExternalLinks(False)

        self.qDocument = self.document()
        self.qDocument.setDocumentMargin(self.mainConf.getTextMargin())
        self.setPlaceholderText(
            "This area will show the content of the document to be "
            "exported or printed. Press the \"Build Project\" button "
            "to generate content."
        )

        theFont = QFont()
        if self.mainConf.textFont is None:
            # If none is defined, set the default back to config
            self.mainConf.textFont = self.qDocument.defaultFont().family()
        theFont.setFamily(self.mainConf.textFont)
        theFont.setPointSize(self.mainConf.textSize)
        self.setFont(theFont)

        # Set the tab stops
        if self.mainConf.verQtValue >= 51000:
            self.setTabStopDistance(self.mainConf.getTabWidth())
        else:
            self.setTabStopWidth(self.mainConf.getTabWidth())

        docPalette = self.palette()
        docPalette.setColor(QPalette.Base, QColor(255, 255, 255))
        docPalette.setColor(QPalette.Text, QColor(0, 0, 0))
        self.setPalette(docPalette)

        lblPalette = self.palette()
        lblPalette.setColor(QPalette.Background, lblPalette.toolTipBase().color())
        lblPalette.setColor(QPalette.Foreground, lblPalette.toolTipText().color())

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)

        fPx = int(1.1*self.theTheme.fontPixelSize)

        self.theTitle = QLabel("<b>Build Time:</b> Unknown", self)
        self.theTitle.setIndent(0)
        self.theTitle.setAutoFillBackground(True)
        self.theTitle.setAlignment(Qt.AlignCenter)
        self.theTitle.setFixedHeight(fPx)
        self.theTitle.setPalette(lblPalette)
        self.theTitle.setFont(lblFont)

        self._updateDocMargins()
        self.setStyleSheet()

        # Age Timer
        self.ageTimer = QTimer()
        self.ageTimer.setInterval(10000)
        self.ageTimer.timeout.connect(self._updateBuildAge)
        self.ageTimer.start()

        logger.debug("GuiBuildNovelDocView initialisation complete")

        return

    def setJustify(self, doJustify):
        """Set the justify text option.
        """
        theOpt = self.qDocument.defaultTextOption()
        if doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        else:
            theOpt.setAlignment(Qt.AlignAbsolute)
        self.qDocument.setDefaultTextOption(theOpt)
        return

    def setTextFont(self, textFont, textSize):
        """Set the text font properties.
        """
        theFont = QFont()
        theFont.setFamily(textFont)
        theFont.setPointSize(textSize)
        self.setFont(theFont)
        return

    def setContent(self, theText, timeStamp):
        """Set the content, either from text or list of text.
        """
        if isinstance(theText, list):
            theText = "".join(theText)

        self.buildTime = timeStamp
        sPos = self.verticalScrollBar().value()
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))

        theText = theText.replace("\t", "!!tab!!")
        theText = theText.replace("<del>", "<span style='text-decoration: line-through;'>")
        theText = theText.replace("</del>", "</span>")
        self.setHtml(theText)
        qApp.processEvents()

        while self.find("!!tab!!"):
            theCursor = self.textCursor()
            theCursor.insertText("\t")

        self.verticalScrollBar().setValue(sPos)
        self._updateBuildAge()

        # Since we change the content while it may still be rendering, we mark
        # the document dirty again to make sure it's re-rendered properly.
        self.qDocument.markContentsDirty(0, self.qDocument.characterCount())
        qApp.restoreOverrideCursor()

        return

    def setStyleSheet(self, theStyles=[]):
        """Set the stylesheet for the preview document.
        """
        if not theStyles:
            theStyles.append(r"h1, h2 {color: rgb(66, 113, 174);}")
            theStyles.append(r"h3, h4 {color: rgb(50, 50, 50);}")
            theStyles.append(r"a {color: rgb(66, 113, 174);}")
            theStyles.append(r".tags {color: rgb(245, 135, 31); font-weight: bold;}")

        self.qDocument.setDefaultStyleSheet("\n".join(theStyles))

        return

    def clearStyleSheet(self):
        """Clears the document stylesheet.
        """
        self.qDocument.setDefaultStyleSheet("")
        return

    ##
    #  Events
    ##

    def resizeEvent(self, theEvent):
        """Make sure the document title is the same width as the window.
        """
        QTextBrowser.resizeEvent(self, theEvent)
        self._updateDocMargins()
        return

    ##
    #  Internal Functions
    ##

    def _updateBuildAge(self):
        """Update the build time and the fuzzy age.
        """
        if self.buildTime > 0:
            strBuildTime = "%s (%s)" % (
                datetime.fromtimestamp(self.buildTime).strftime("%x %X"),
                fuzzyTime(time() - self.buildTime)
            )
        else:
            strBuildTime = "Unknown"
        self.theTitle.setText("<b>Build Time:</b> %s" % strBuildTime)

    def _updateDocMargins(self):
        """Automatically adjust the header to fill the top of the
        document within the viewport.
        """
        vBar = self.verticalScrollBar()
        if vBar.isVisible():
            sW = vBar.width()
        else:
            sW = 0

        tB = self.frameWidth()
        tW = self.width() - 2*tB - sW
        tH = self.theTitle.height()

        self.theTitle.setGeometry(tB, tB, tW, tH)
        self.setViewportMargins(0, tH, 0, 0)

        return

# END Class GuiBuildNovelDocView
