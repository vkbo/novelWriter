# -*- coding: utf-8 -*-
"""novelWriter GUI Build Novel

 novelWriter – GUI Build Novel
===============================
 Class holding the build novel window

 File History:
 Created: 2020-05-09 [0.5]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import json
import nw

from os import path
from time import time
from datetime import datetime

from PyQt5.QtCore import Qt, QByteArray, QTimer
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtGui import (
    QPalette, QColor, QTextDocumentWriter, QFont
)
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QLabel,
    QLineEdit, QGroupBox, QGridLayout, QProgressBar, QMenu, QAction,
    QFileDialog, QFontDialog, QSpinBox
)

from nw.common import fuzzyTime
from nw.gui.custom import QSwitch
from nw.core import ToHtml
from nw.constants import (
    nwAlert, nwFiles, nwItemType, nwItemLayout, nwItemClass
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

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.optState   = self.theProject.optState

        self.htmlText  = [] # List of html document
        self.htmlStyle = [] # List of html styles
        self.nwdText   = [] # List of markdown documents
        self.buildTime = 0  # The timestamp of the last build

        self.setWindowTitle("Build Novel Project")
        self.setMinimumWidth(self.mainConf.pxInt(900))
        self.setMinimumHeight(self.mainConf.pxInt(800))

        self.resize(
            self.mainConf.pxInt(self.optState.getInt("GuiBuildNovel", "winWidth",  900)),
            self.mainConf.pxInt(self.optState.getInt("GuiBuildNovel", "winHeight", 800))
        )

        self.outerBox = QHBoxLayout()
        self.toolsBox = QVBoxLayout()

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
        xFmt = self.mainConf.pxInt(220)

        self.fmtTitle = QLineEdit()
        self.fmtTitle.setMaxLength(200)
        self.fmtTitle.setFixedWidth(xFmt)
        self.fmtTitle.setToolTip(fmtHelp)
        self.fmtTitle.setText(
            self._reFmtCodes(self.theProject.titleFormat["title"])
        )

        self.fmtChapter = QLineEdit()
        self.fmtChapter.setMaxLength(200)
        self.fmtChapter.setFixedWidth(xFmt)
        self.fmtChapter.setToolTip(fmtHelp)
        self.fmtChapter.setText(
            self._reFmtCodes(self.theProject.titleFormat["chapter"])
        )

        self.fmtUnnumbered = QLineEdit()
        self.fmtUnnumbered.setMaxLength(200)
        self.fmtUnnumbered.setFixedWidth(xFmt)
        self.fmtUnnumbered.setToolTip(fmtHelp)
        self.fmtUnnumbered.setText(
            self._reFmtCodes(self.theProject.titleFormat["unnumbered"])
        )

        self.fmtScene = QLineEdit()
        self.fmtScene.setMaxLength(200)
        self.fmtScene.setFixedWidth(xFmt)
        self.fmtScene.setToolTip(fmtHelp + fmtScHelp)
        self.fmtScene.setText(
            self._reFmtCodes(self.theProject.titleFormat["scene"])
        )

        self.fmtSection = QLineEdit()
        self.fmtSection.setMaxLength(200)
        self.fmtSection.setFixedWidth(xFmt)
        self.fmtSection.setToolTip(fmtHelp + fmtScHelp)
        self.fmtSection.setText(
            self._reFmtCodes(self.theProject.titleFormat["section"])
        )

        self.titleForm.addWidget(QLabel("Title"),      0, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addWidget(self.fmtTitle,        0, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(QLabel("Chapter"),    1, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addWidget(self.fmtChapter,      1, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(QLabel("Unnumbered"), 2, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addWidget(self.fmtUnnumbered,   2, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(QLabel("Scene"),      3, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addWidget(self.fmtScene,        3, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(QLabel("Section"),    4, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addWidget(self.fmtSection,      4, 1, 1, 1, Qt.AlignRight)

        self.titleForm.setColumnStretch(0, 1)
        self.titleForm.setColumnStretch(1, 0)

        # Text Options
        # =============
        self.formatGroup = QGroupBox("Formatting Options", self)
        self.formatForm  = QGridLayout(self)
        self.formatGroup.setLayout(self.formatForm)

        ## Font Family
        self.textFont = QLineEdit()
        self.textFont.setReadOnly(True)
        self.textFont.setFixedWidth(self.mainConf.pxInt(182))
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

        self.formatForm.addWidget(QLabel("Font family"),     0, 0, 1, 1, Qt.AlignLeft)
        self.formatForm.addWidget(self.textFont,             0, 1, 1, 1, Qt.AlignRight)
        self.formatForm.addWidget(self.fontButton,           0, 2, 1, 1, Qt.AlignRight)
        self.formatForm.addWidget(QLabel("Font size"),       1, 0, 1, 1, Qt.AlignLeft)
        self.formatForm.addWidget(self.textSize,             1, 1, 1, 2, Qt.AlignRight)
        self.formatForm.addWidget(QLabel("Justify text"),    2, 0, 1, 1, Qt.AlignLeft)
        self.formatForm.addWidget(self.justifyText,          2, 1, 1, 2, Qt.AlignRight)
        self.formatForm.addWidget(QLabel("Disable styling"), 3, 0, 1, 1, Qt.AlignLeft)
        self.formatForm.addWidget(self.noStyling,            3, 1, 1, 2, Qt.AlignRight)

        self.formatForm.setColumnStretch(0, 1)
        self.formatForm.setColumnStretch(1, 0)
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

        # Additional Options
        # ==================
        self.fileGroup = QGroupBox("File Options", self)
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

        # Build Button
        # ============
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

        self.saveHTM = QAction("%s HTML (.htm)" % nw.__package__, self)
        self.saveHTM.triggered.connect(lambda: self._saveDocument(self.FMT_HTM))
        self.saveMenu.addAction(self.saveHTM)

        if self.mainConf.verQtValue >= 51400:
            self.saveMD = QAction("Markdown (.md)", self)
            self.saveMD.triggered.connect(lambda: self._saveDocument(self.FMT_MD))
            self.saveMenu.addAction(self.saveMD)

        self.saveNWD = QAction("%s Markdown (.nwd)" % nw.__package__, self)
        self.saveNWD.triggered.connect(lambda: self._saveDocument(self.FMT_NWD))
        self.saveMenu.addAction(self.saveNWD)

        self.saveTXT = QAction("Plain Text (.txt)", self)
        self.saveTXT.triggered.connect(lambda: self._saveDocument(self.FMT_TXT))
        self.saveMenu.addAction(self.saveTXT)

        self.saveJsonH = QAction("JSON + %s HTML (.json)" % nw.__package__, self)
        self.saveJsonH.triggered.connect(lambda: self._saveDocument(self.FMT_JSON_H))
        self.saveMenu.addAction(self.saveJsonH)

        self.saveJsonM = QAction("JSON + %s Markdown (.json)" % nw.__package__, self)
        self.saveJsonM.triggered.connect(lambda: self._saveDocument(self.FMT_JSON_M))
        self.saveMenu.addAction(self.saveJsonM)

        self.btnClose = QPushButton("Close")
        self.btnClose.clicked.connect(self._doClose)

        self.buttonBox.addWidget(self.btnSave)
        self.buttonBox.addWidget(self.btnPrint)
        self.buttonBox.addWidget(self.btnClose)
        self.buttonBox.setSpacing(4)

        # Assemble GUI
        # ============
        self.toolsBox.addWidget(self.titleGroup)
        self.toolsBox.addWidget(self.formatGroup)
        self.toolsBox.addWidget(self.textGroup)
        self.toolsBox.addWidget(self.fileGroup)
        self.toolsBox.addStretch(1)
        self.toolsBox.addWidget(self.buildProgress)
        self.toolsBox.addWidget(self.buildNovel)
        self.toolsBox.addSpacing(8)
        self.toolsBox.addLayout(self.buttonBox)

        self.outerBox.addLayout(self.toolsBox)
        self.outerBox.addWidget(self.docView)
        self.outerBox.setStretch(0, 0)
        self.outerBox.setStretch(1, 1)

        self.setLayout(self.outerBox)
        self.buildNovel.setFocus()

        logger.debug("GuiBuildNovel initialisation complete")

        # Load from Cache
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
            self.docView.setContent(self.htmlText, self.buildTime)
        else:
            self.htmlText = []
            self.htmlStyle = []
            self.nwdText = []
            self.buildTime = 0

        return

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

        tStart = time()

        self.htmlText = []
        self.htmlStyle = []
        self.nwdText = []

        for nItt, tItem in enumerate(self.theProject.projTree):

            noteRoot  = noteFiles
            noteRoot &= tItem.itemType == nwItemType.ROOT
            noteRoot &= tItem.itemClass != nwItemClass.NOVEL

            try:
                if noteRoot:
                    # Add headers for root folders of notes
                    makeHtml.addRootHeading(tItem.itemHandle)
                    makeHtml.doConvert()
                    self.htmlText.append(makeHtml.getResult())
                    self.nwdText.append(makeHtml.getFilteredMarkdown())

                elif self._checkInclude(tItem, noteFiles, novelFiles, ignoreFlag):
                    makeHtml.setText(tItem.itemHandle)
                    makeHtml.doAutoReplace()
                    makeHtml.tokenizeText()
                    makeHtml.doHeaders()
                    makeHtml.doConvert()
                    makeHtml.doPostProcessing()
                    self.htmlText.append(makeHtml.getResult())
                    self.nwdText.append(makeHtml.getFilteredMarkdown())

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

        tEnd = time()
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
        self.docView.setContent(self.htmlText, self.buildTime)

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
        isNone |= theItem.parHandle == self.theProject.projTree.trashRoot()
        isNone |= theItem.parHandle is None
        isNote  = theItem.itemLayout == nwItemLayout.NOTE
        isNovel = not isNone and not isNote

        if isNone:
            return False
        if isNote and not noteFiles:
            return False
        if isNovel and not novelFiles:
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

            cleanName = self.theProject.getFileSafeProjectName()
            fileName  = "%s.%s" % (cleanName, fileExt)
            saveDir   = self.mainConf.lastPath
            savePath  = path.join(saveDir, fileName)
            if not path.isdir(saveDir):
                saveDir = self.mainConf.homePath

            if self.mainConf.showGUI:
                dlgOpt  = QFileDialog.Options()
                dlgOpt |= QFileDialog.DontUseNativeDialog
                saveTo  = QFileDialog.getSaveFileName(
                    self, "Save Document As", savePath, options=dlgOpt
                )
                if saveTo[0]:
                    savePath = saveTo[0]
                else:
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
                            bodyText = "".join(self.htmlText),
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
        if self.mainConf.showGUI:
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
        thePrinter.setOrientation(QPrinter.Portrait)
        self.docView.qDocument.print(thePrinter)
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
        return

    def _loadCache(self):
        """Save the current data to cache.
        """
        buildCache = path.join(self.theProject.projCache, nwFiles.BUILD_CACHE)
        dataCount = 0
        if path.isfile(buildCache):

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
        buildCache = path.join(self.theProject.projCache, nwFiles.BUILD_CACHE)

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
        QDialog.closeEvent(self, theEvent)
        return

    ##
    #  Internal Functions
    ##

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

        # GUI Settings
        self.optState.setValue("GuiBuildNovel", "winWidth",    winWidth)
        self.optState.setValue("GuiBuildNovel", "winHeight",   winHeight)
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
            "exported or printed. Press the \"Build Novel Project\" "
            "button to generate content."
        )

        theFont = QFont()
        if self.mainConf.textFont is None:
            # If none is defined, set the default back to config
            self.mainConf.textFont = self.qDocument.defaultFont().family()
        theFont.setFamily(self.mainConf.textFont)
        theFont.setPointSize(self.mainConf.textSize)
        self.setFont(theFont)

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
        mPx = self.mainConf.pxInt(4)

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

        theText = theText.replace("&emsp;", "&nbsp;"*4)
        theText = theText.replace("<del>", "<span style='text-decoration: line-through;'>")
        theText = theText.replace("</del>", "</span>")
        self.setHtml(theText)
        self._updateBuildAge()

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
