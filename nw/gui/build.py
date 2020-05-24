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
import nw

from os import path
from time import time

from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtGui import (
    QTextOption, QPalette, QColor, QTextDocumentWriter, QFont
)
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QLabel,
    QLineEdit, QGroupBox, QGridLayout, QProgressBar, QMenu, QAction, QFileDialog
)

from nw.gui.additions import QSwitch
from nw.core import ToHtml
from nw.constants import (
    nwAlert, nwItemType, nwItemLayout, nwItemClass
)

logger = logging.getLogger(__name__)

class GuiBuildNovel(QDialog):

    FMT_ODT = 1
    FMT_PDF = 2
    FMT_HTM = 3
    FMT_MD  = 4
    FMT_NWD = 5
    FMT_TXT = 6

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

        self.setWindowTitle("Build Novel Project")
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)

        self.resize(
            self.optState.getInt("GuiBuildNovel", "winWidth", 800),
            self.optState.getInt("GuiBuildNovel", "winHeight", 800)
        )

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()
        self.toolsBox = QVBoxLayout()

        self.docView = GuiBuildNovelDocView(self, self.theProject)

        # Title Formats
        # =============
        self.titleGroup = QGroupBox("Novel Title Formats", self)
        self.titleForm  = QGridLayout(self)
        self.titleGroup.setLayout(self.titleForm)

        self.fmtTitle = QLineEdit()
        self.fmtTitle.setMaxLength(200)
        self.fmtTitle.setFixedWidth(200)
        self.fmtTitle.setText(self.theProject.titleFormat["title"])

        self.fmtChapter = QLineEdit()
        self.fmtChapter.setMaxLength(200)
        self.fmtChapter.setFixedWidth(200)
        self.fmtChapter.setText(self.theProject.titleFormat["chapter"])

        self.fmtUnnumbered = QLineEdit()
        self.fmtUnnumbered.setMaxLength(200)
        self.fmtUnnumbered.setFixedWidth(200)
        self.fmtUnnumbered.setText(self.theProject.titleFormat["unnumbered"])

        self.fmtScene = QLineEdit()
        self.fmtScene.setMaxLength(200)
        self.fmtScene.setFixedWidth(200)
        self.fmtScene.setText(self.theProject.titleFormat["scene"])

        self.fmtSection = QLineEdit()
        self.fmtSection.setMaxLength(200)
        self.fmtSection.setFixedWidth(200)
        self.fmtSection.setText(self.theProject.titleFormat["section"])

        self.titleForm.addWidget(QLabel("Title"),      0, 0)
        self.titleForm.addWidget(self.fmtTitle,        0, 1)
        self.titleForm.addWidget(QLabel("Chapter"),    1, 0)
        self.titleForm.addWidget(self.fmtChapter,      1, 1)
        self.titleForm.addWidget(QLabel("Unnumbered"), 2, 0)
        self.titleForm.addWidget(self.fmtUnnumbered,   2, 1)
        self.titleForm.addWidget(QLabel("Scene"),      3, 0)
        self.titleForm.addWidget(self.fmtScene,        3, 1)
        self.titleForm.addWidget(QLabel("Section"),    4, 0)
        self.titleForm.addWidget(self.fmtSection,      4, 1)

        self.titleForm.setColumnStretch(0, 1)
        self.titleForm.setColumnStretch(1, 0)

        # Text Options
        # =============
        self.textGroup = QGroupBox("Text Options", self)
        self.textForm  = QGridLayout(self)
        self.textGroup.setLayout(self.textForm)

        self.justifyText = QSwitch()
        self.justifyText.setChecked(self.optState.getBool("GuiBuildNovel", "justifyText", False))

        self.textForm.addWidget(QLabel("Justify text"), 0, 0)
        self.textForm.addWidget(self.justifyText,       0, 1)

        self.textForm.setColumnStretch(0, 1)
        self.textForm.setColumnStretch(1, 0)

        # Include Switches
        # ================
        self.includeGroup = QGroupBox("Include Non-Text Elements", self)
        self.includeForm  = QGridLayout(self)
        self.includeGroup.setLayout(self.includeForm)

        self.includeSynopsis = QSwitch()
        self.includeSynopsis.setChecked(self.theProject.titleFormat["withSynopsis"])
        self.includeComments = QSwitch()
        self.includeComments.setChecked(self.theProject.titleFormat["withComments"])
        self.includeKeywords = QSwitch()
        self.includeKeywords.setChecked(self.theProject.titleFormat["withKeywords"])

        self.includeForm.addWidget(QLabel("Include synopsis"), 0, 0)
        self.includeForm.addWidget(self.includeSynopsis,       0, 1)
        self.includeForm.addWidget(QLabel("Include comments"), 1, 0)
        self.includeForm.addWidget(self.includeComments,       1, 1)
        self.includeForm.addWidget(QLabel("Include keywords"), 2, 0)
        self.includeForm.addWidget(self.includeKeywords,       2, 1)

        self.includeForm.setColumnStretch(0, 1)
        self.includeForm.setColumnStretch(1, 0)

        # Additional Options
        # ==================
        self.addsGroup = QGroupBox("Additional Options", self)
        self.addsForm  = QGridLayout(self)
        self.addsGroup.setLayout(self.addsForm)

        self.novelFiles = QSwitch()
        self.novelFiles.setChecked(self.optState.getBool("GuiBuildNovel", "addNovel", True))
        self.noteFiles = QSwitch()
        self.noteFiles.setChecked(self.optState.getBool("GuiBuildNovel", "addNotes", False))
        self.ignoreFlag = QSwitch()
        self.ignoreFlag.setChecked(self.optState.getBool("GuiBuildNovel", "ignoreFlag", False))
        self.excludeBody = QSwitch()
        self.excludeBody.setChecked(self.optState.getBool("GuiBuildNovel", "excludeBody", False))

        self.addsForm.addWidget(QLabel("Include novel files"), 0, 0)
        self.addsForm.addWidget(self.novelFiles,               0, 1)
        self.addsForm.addWidget(QLabel("Include note files"),  1, 0)
        self.addsForm.addWidget(self.noteFiles,                1, 1)
        self.addsForm.addWidget(QLabel("Ignore export flag"),  2, 0)
        self.addsForm.addWidget(self.ignoreFlag,               2, 1)
        self.addsForm.addWidget(QLabel("Exclude body text"),   3, 0)
        self.addsForm.addWidget(self.excludeBody,              3, 1)

        self.addsForm.setColumnStretch(0, 1)
        self.addsForm.setColumnStretch(1, 0)

        # Build Button
        # ============
        self.buildProgress = QProgressBar()

        self.genPreview = QPushButton("Generate Preview")
        self.genPreview.clicked.connect(self._buildPreview)

        # Action Buttons
        # ==============
        self.buttonForm = QGridLayout()

        self.btnHelp = QPushButton("Help")
        self.btnHelp.clicked.connect(self._showHelp)

        self.btnPrint = QPushButton("Print")
        self.btnPrint.clicked.connect(self._printDocument)

        self.btnSave = QPushButton("Save As")
        self.saveMenu = QMenu(self)
        self.btnSave.setMenu(self.saveMenu)

        self.saveODT = QAction("Open Document (.odt)")
        self.saveODT.triggered.connect(lambda: self._saveDocument(self.FMT_ODT))
        self.saveMenu.addAction(self.saveODT)

        self.savePDF = QAction("Portable Document Format (.pdf)")
        self.savePDF.triggered.connect(lambda: self._saveDocument(self.FMT_PDF))
        self.saveMenu.addAction(self.savePDF)

        self.saveHTM = QAction("%s HTML (.htm)" % nw.__package__)
        self.saveHTM.triggered.connect(lambda: self._saveDocument(self.FMT_HTM))
        self.saveMenu.addAction(self.saveHTM)

        if self.mainConf.verQtValue >= 51400:
            self.saveMD = QAction("Markdown (.md)")
            self.saveMD.triggered.connect(lambda: self._saveDocument(self.FMT_MD))
            self.saveMenu.addAction(self.saveMD)

        self.saveNWD = QAction("novelWriter Markdown (.nwd)")
        self.saveNWD.triggered.connect(lambda: self._saveDocument(self.FMT_NWD))
        self.saveMenu.addAction(self.saveNWD)

        self.saveTXT = QAction("Plain Text (.txt)")
        self.saveTXT.triggered.connect(lambda: self._saveDocument(self.FMT_TXT))
        self.saveMenu.addAction(self.saveTXT)

        self.btnClose = QPushButton("Close")
        self.btnClose.clicked.connect(self._doClose)

        self.buttonForm.addWidget(self.btnHelp,  0, 0)
        self.buttonForm.addWidget(self.btnPrint, 0, 1)
        self.buttonForm.addWidget(self.btnSave,  1, 0)
        self.buttonForm.addWidget(self.btnClose, 1, 1)

        # Assemble GUI
        # ============
        self.toolsBox.addWidget(self.titleGroup)
        self.toolsBox.addWidget(self.textGroup)
        self.toolsBox.addWidget(self.includeGroup)
        self.toolsBox.addWidget(self.addsGroup)
        self.toolsBox.addStretch(1)
        self.toolsBox.addWidget(self.buildProgress)
        self.toolsBox.addWidget(self.genPreview)
        self.toolsBox.addSpacing(8)
        self.toolsBox.addLayout(self.buttonForm)

        self.innerBox.addLayout(self.toolsBox)
        self.innerBox.addWidget(self.docView)

        self.outerBox.addLayout(self.innerBox)
        self.setLayout(self.outerBox)

        self.innerBox.setStretch(0, 0)
        self.innerBox.setStretch(1, 1)

        self.show()

        logger.debug("GuiBuildNovel initialisation complete")

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
        incSynopsis   = self.includeSynopsis.isChecked()
        incComments   = self.includeComments.isChecked()
        incKeywords   = self.includeKeywords.isChecked()
        novelFiles    = self.novelFiles.isChecked()
        noteFiles     = self.noteFiles.isChecked()
        ignoreFlag    = self.ignoreFlag.isChecked()
        excludeBody   = self.excludeBody.isChecked()

        makeHtml = ToHtml(self.theProject, self.theParent)
        makeHtml.setTitleFormat(fmtTitle)
        makeHtml.setChapterFormat(fmtChapter)
        makeHtml.setUnNumberedFormat(fmtUnnumbered)
        makeHtml.setSceneFormat(fmtScene, fmtScene == "")
        makeHtml.setSectionFormat(fmtSection, fmtSection == "")
        makeHtml.setBodyText(not excludeBody)
        makeHtml.setSynopsis(incSynopsis)
        makeHtml.setComments(incComments)
        makeHtml.setKeywords(incKeywords)
        makeHtml.setJustify(justifyText)

        # Make sure the tree order is correct
        self.theParent.treeView.saveTreeOrder()

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

            # Update progress bar, also for skipped items
            self.buildProgress.setValue(nItt+1)

        tEnd = time()
        logger.debug("Built project in %.3f ms" % (1000*(tEnd-tStart)))
        self.htmlStyle = makeHtml.getStyleSheet()

        # Load the preview document with the html data
        self.docView.setStyleSheet(self.htmlStyle)
        self.docView.setContent(self.htmlText)

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

        # FMT_PDF

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
            textFmt = "%s markdown" % nw.__package__
            outTool = "NW"

        elif theFormat == self.FMT_TXT:
            byteFmt.append("plaintext")
            fileExt = "txt"
            textFmt = "Plain Text"
            outTool = "Qt"

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
        thePrinter.setOrientation(QPrinter.Portrait)
        self.docView.qDocument.print(thePrinter)
        return

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
            "title"        : self.fmtTitle.text().strip(),
            "chapter"      : self.fmtChapter.text().strip(),
            "unnumbered"   : self.fmtUnnumbered.text().strip(),
            "scene"        : self.fmtScene.text().strip(),
            "section"      : self.fmtSection.text().strip(),
            "withSynopsis" : self.includeSynopsis.isChecked(),
            "withComments" : self.includeComments.isChecked(),
            "withKeywords" : self.includeKeywords.isChecked(),
        })

        # GUI Settings
        self.optState.setValue("GuiBuildNovel", "winWidth",    self.width())
        self.optState.setValue("GuiBuildNovel", "winHeight",   self.height())
        self.optState.setValue("GuiBuildNovel", "justifyText", self.justifyText.isChecked())
        self.optState.setValue("GuiBuildNovel", "addNovel",    self.novelFiles.isChecked())
        self.optState.setValue("GuiBuildNovel", "addNotes",    self.noteFiles.isChecked())
        self.optState.setValue("GuiBuildNovel", "ignoreFlag",  self.ignoreFlag.isChecked())
        self.optState.setValue("GuiBuildNovel", "excludeBody", self.excludeBody.isChecked())
        self.optState.saveSettings()

        return

    def _showHelp(self):
        """Generate a help text and show it in the document window.
        """
        docName = "exportHelp_%s.htm" % self.mainConf.guiLang
        docPath = path.join(self.mainConf.assetPath, "text", docName)
        if path.isfile(docPath):
            with open(docPath, mode="r", encoding="utf8") as inFile:
                helpText = inFile.read()
            self.docView.setStyleSheet()
            self.docView.setContent(helpText)
        else:
            self.theParent.makeAlert(
                "Could not open help text file for Build Project.", nwAlert.ERROR
            )
        return

# END Class GuiBuildNovel

class GuiBuildNovelDocView(QTextBrowser):

    def __init__(self, theParent, theProject):
        QTextBrowser.__init__(self, theParent)

        logger.debug("Initialising GuiBuildNovelDocView ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.setMinimumWidth(400)
        self.setOpenExternalLinks(False)

        self.qDocument = self.document()
        self.qDocument.setDocumentMargin(self.mainConf.textMargin)

        theFont = QFont()
        if self.mainConf.textFont is None:
            # If none is defined, set the default back to config
            self.mainConf.textFont = self.qDocument.defaultFont().family()
        theFont.setFamily(self.mainConf.textFont)
        theFont.setPointSize(self.mainConf.textSize)
        self.setFont(theFont)

        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.qDocument.setDefaultTextOption(theOpt)

        docPalette = self.palette()
        docPalette.setColor(QPalette.Base, QColor(255, 255, 255))
        docPalette.setColor(QPalette.Text, QColor(  0,   0,   0))
        self.setPalette(docPalette)

        self.setStyleSheet()

        self.show()

        logger.debug("GuiBuildNovelDocView initialisation complete")

        return

    def setContent(self, theText):
        """Set the content, either from text or list of text.
        """
        if isinstance(theText, list):
            theText = "".join(theText)
        theText = theText.replace("&emsp;","&nbsp;"*4)
        self.setHtml(theText)
        return

    def setStyleSheet(self, theStyles=[]):
        """Set the stylesheet for the preview document.
        """
        if not theStyles:
            theStyles.append(r"h1, h2 {color: rgb(66, 113, 174);}")
            theStyles.append(r"h3, h4 {color: rgb(50, 50, 50);}")
            theStyles.append(r"a {color: rgb(137, 89, 168);}")
            theStyles.append(r"mark {background-color: rgb(240, 198, 116);}")
            theStyles.append(r".tags {color: rgb(245, 135, 31); font-weight: bold;}")

        self.qDocument.setDefaultStyleSheet("\n".join(theStyles))

        return

# END Class GuiBuildNovelDocView
