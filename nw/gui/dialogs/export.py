# -*- coding: utf-8 -*-
"""novelWriter GUI Export Tools

 novelWriter – GUI Export Tools
================================
 Tool for exporting project files to other formats

 File History:
 Created: 2019-10-13 [0.2.3]

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
import time
import nw

from os import path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QGridLayout,
    QGroupBox, QCheckBox, QLabel, QComboBox, QLineEdit, QPushButton,
    QFileDialog, QProgressBar, QSpinBox, QMessageBox
)

from nw.convert import TextFile, HtmlFile, MarkdownFile, LaTeXFile, ConcatFile
from nw.common import packageRefURL
from nw.constants import nwFiles, nwItemType, nwAlert

logger = logging.getLogger(__name__)

class GuiExport(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiExport ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.optState   = self.theProject.optState

        self.outerBox   = QHBoxLayout()
        self.innerBox   = QVBoxLayout()
        self.setWindowTitle("Export Project")
        self.setLayout(self.outerBox)

        self.guiDeco = self.theParent.theTheme.loadDecoration("export",(64,64))

        self.tabMain   = GuiExportMain(self.theParent, self.theProject)
        self.tabPandoc = GuiExportPandoc(self.theParent, self.theProject)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.tabMain,   "Settings")
        self.tabWidget.addTab(self.tabPandoc, "Pandoc")

        self.outerBox.addWidget(self.guiDeco, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.doExportForm = QGridLayout()
        self.doExportForm.setContentsMargins(10,5,0,10)

        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self._doExport)

        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self._doClose)

        self.exportStatus   = QLabel("Ready ...")
        self.exportProgress = QProgressBar(self)

        self.doExportForm.addWidget(self.exportStatus,   0, 0, 1, 3)
        self.doExportForm.addWidget(self.exportProgress, 1, 0)
        self.doExportForm.addWidget(self.exportButton,   1, 1)
        self.doExportForm.addWidget(self.closeButton,    1, 2)

        self.innerBox.addWidget(self.tabWidget)
        self.innerBox.addLayout(self.doExportForm)

        self.rejected.connect(self._doClose)
        self.show()

        logger.debug("GuiExport initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doExport(self):

        logger.verbose("GuiExport export button clicked")

        wNovel    = self.tabMain.expNovel.isChecked()
        wNotes    = self.tabMain.expNotes.isChecked()
        eFormat   = self.tabMain.outputFormat.currentData()
        fixWidth  = self.tabMain.fixedWidth.value()
        wComments = self.tabMain.expComments.isChecked()
        wKeywords = self.tabMain.expKeywords.isChecked()
        chFormat  = self.tabMain.chapterFormat.text()
        unFormat  = self.tabMain.unnumFormat.text()
        scFormat  = self.tabMain.sceneFormat.text()
        seFormat  = self.tabMain.sectionFormat.text()
        saveTo    = self.tabMain.exportPath.text()
        hScene    = self.tabMain.hideScene.isChecked()
        hSection  = self.tabMain.hideSection.isChecked()

        pFormat   = self.tabPandoc.outputFormat.currentData()
        tFormat   = GuiExportPandoc.FMT_VIA[pFormat]

        if saveTo.startswith("~"):
            saveTo = path.expanduser(saveTo)

        exportDir = path.dirname(saveTo)
        if not path.isdir(exportDir):
            self.theParent.makeAlert("The export folder does not exist.",nwAlert.ERROR)
            self.exportStatus.setText("Export failed ...")
            return False

        nItems = len(self.theProject.projTree)
        if eFormat == GuiExportMain.FMT_PDOC:
            nItems += int(0.2*nItems)
        self.exportProgress.setMinimum(0)
        self.exportProgress.setMaximum(nItems)
        self.exportProgress.setValue(0)

        if not wNovel and not wNotes:
            self.exportStatus.setText("Nothing to export ...")
            return False

        outFile = None
        if eFormat == GuiExportMain.FMT_TXT:
            outFile = TextFile(self.theProject, self.theParent)
        elif eFormat == GuiExportMain.FMT_MD:
            outFile = MarkdownFile(self.theProject, self.theParent)
        elif eFormat == GuiExportMain.FMT_HTML:
            outFile = HtmlFile(self.theProject, self.theParent)
        elif eFormat == GuiExportMain.FMT_TEX:
            outFile = LaTeXFile(self.theProject, self.theParent)
        elif eFormat == GuiExportMain.FMT_NWD:
            outFile = ConcatFile(self.theProject, self.theParent)
        elif eFormat == GuiExportMain.FMT_PDOC:
            if tFormat == "html":
                outFile = HtmlFile(self.theProject, self.theParent)
            elif tFormat == "markdown":
                outFile = MarkdownFile(self.theProject, self.theParent)

        if outFile is None:
            return False

        if outFile.openFile(saveTo):
            outFile.setComments(wComments)
            outFile.setKeywords(wKeywords)
            outFile.setExportNovel(wNovel)
            outFile.setExportNotes(wNotes)
            outFile.setWordWrap(fixWidth)
            outFile.setChapterFormat(chFormat)
            outFile.setUnNumberedFormat(unFormat)
            outFile.setSceneFormat(scFormat, hScene)
            outFile.setSectionFormat(seFormat, hSection)
        else:
            self.exportStatus.setText("Failed to open file for writing ...")
            return False

        time.sleep(0.5)

        nDone = 0
        for tItem in self.theProject.projTree:

            self.exportProgress.setValue(nDone)
            self.exportStatus.setText("Exporting: %s" % tItem.itemName)
            logger.verbose("Exporting: %s" % tItem.itemName)

            if tItem is not None and tItem.itemType == nwItemType.FILE:
                outFile.addText(tItem.itemHandle)

            nDone += 1

        outFile.closeFile()
        self.exportProgress.setValue(nDone)
        self.exportStatus.setText("Export to %s complete" % outFile.fileName)
        logger.verbose("Export to %s complete" % outFile.fileName)

        if eFormat == GuiExportMain.FMT_TEX:
            # Check that encoding was successful
            if outFile.texCodecFail:
                self.theParent.makeAlert((
                    "Failed to escape unicode characters while writing LaTeX "
                    "file. The generated .tex file may not build properly. "
                    "Make sure the python package '{package:s}' is installed "
                    "and working."
                ).format(
                    package = packageRefURL("latexcodec")
                ), nwAlert.WARN)

        if eFormat != GuiExportMain.FMT_PDOC:
            return True

        # If we've reached this point, we're also running Pandoc

        if self._callPandoc(saveTo, tFormat, pFormat):
            self.exportProgress.setValue(nItems)
            self.exportStatus.setText("Pandoc conversion complete")
            logger.verbose("Pandoc conversion complete")
        else:
            self.exportProgress.setValue(nItems)
            self.exportStatus.setText("Pandoc conversion failed")
            logger.verbose("Pandoc conversion failed")
            return False

        return True

    def _callPandoc(self, inFile, inFmt, outFmt):

        pFmt = {
            GuiExportPandoc.FMT_ODT   : "odt",
            GuiExportPandoc.FMT_DOCX  : "docx",
            GuiExportPandoc.FMT_EPUB2 : "epub2",
            GuiExportPandoc.FMT_EPUB3 : "epub3",
            GuiExportPandoc.FMT_ZIM   : "zimwiki",
        }

        try:
            import pypandoc
        except:
            self.theParent.makeAlert((
                "Could not load the '{package:s}' package. "
                "Make sure it is installed, and try again."
            ).format(
                package = packageRefURL("pypandoc")
            ), nwAlert.ERROR)
            return False

        outFile  = path.splitext(inFile)[0]+GuiExportPandoc.FMT_EXT[outFmt]
        fileName = path.basename(outFile)

        if path.isfile(outFile) and self.mainConf.showGUI:
            msgBox = QMessageBox()
            msgRes = msgBox.question(
                self.theParent, "Overwrite",
                ("File '%s' already exists.<br>Do you want to overwrite it?" % fileName)
            )
            if msgRes != QMessageBox.Yes:
                return False

        try:
            pypandoc.convert_file(
                source_file = inFile,
                format      = inFmt,
                outputfile  = outFile,
                to          = pFmt[outFmt],
                extra_args  = (),
                encoding    = "utf-8",
                filters     = None
            )
        except Exception as e:
            self.theParent.makeAlert(
                ["Failed to convert file using pypandoc + Pandoc.",
                str(e)], nwAlert.ERROR
            )
            return False

        return True

    def _doClose(self):

        logger.verbose("GuiExport close button clicked")

        # General Settings
        wNovel    = self.tabMain.expNovel.isChecked()
        wNotes    = self.tabMain.expNotes.isChecked()
        eFormat   = self.tabMain.outputFormat.currentData()
        fixWidth  = self.tabMain.fixedWidth.value()
        wComments = self.tabMain.expComments.isChecked()
        wKeywords = self.tabMain.expKeywords.isChecked()
        chFormat  = self.tabMain.chapterFormat.text()
        unFormat  = self.tabMain.unnumFormat.text()
        scFormat  = self.tabMain.sceneFormat.text()
        seFormat  = self.tabMain.sectionFormat.text()
        saveTo    = self.tabMain.exportPath.text()
        hScene    = self.tabMain.hideScene.isChecked()
        hSection  = self.tabMain.hideSection.isChecked()

        if saveTo.startswith("~"):
            saveTo = path.expanduser(saveTo)

        self.optState.setValue("GuiExport", "wNovel",    wNovel)
        self.optState.setValue("GuiExport", "wNotes",    wNotes)
        self.optState.setValue("GuiExport", "eFormat",   eFormat)
        self.optState.setValue("GuiExport", "fixWidth",  fixWidth)
        self.optState.setValue("GuiExport", "wComments", wComments)
        self.optState.setValue("GuiExport", "wKeywords", wKeywords)
        self.optState.setValue("GuiExport", "chFormat",  chFormat)
        self.optState.setValue("GuiExport", "unFormat",  unFormat)
        self.optState.setValue("GuiExport", "scFormat",  scFormat)
        self.optState.setValue("GuiExport", "seFormat",  seFormat)
        self.optState.setValue("GuiExport", "saveTo",    saveTo)
        self.optState.setValue("GuiExport", "hScene",    hScene)
        self.optState.setValue("GuiExport", "hSection",  hSection)

        # Pandoc Settings
        pFormat   = self.tabPandoc.outputFormat.currentData()

        self.optState.setValue("GuiExport", "pFormat",  pFormat)

        self.optState.saveSettings()
        self.close()

        return

# END Class GuiExport

class GuiExportMain(QWidget):

    FMT_NWD  = 1 # novelWriter markdown
    FMT_TXT  = 2 # Plain text file
    FMT_MD   = 3 # Markdown file
    FMT_HTML = 4 # HTML file
    FMT_TEX  = 5 # LaTeX file
    FMT_PDOC = 6 # Pass to pandoc
    FMT_EXT  = {
        FMT_NWD  : ".nwd",
        FMT_TXT  : ".txt",
        FMT_MD   : ".md",
        FMT_HTML : ".htm",
        FMT_TEX  : ".tex",
        FMT_PDOC : ".tmp",
    }
    FMT_HELP  = {
        FMT_NWD : (
            "Exports a document using the novelWriter markdown format. "
            "The files selected by the filters are appended as-is, "
            "including comments and other settings."
        ),
        FMT_TXT : (
            "Exports a plain text file. All formatting is stripped and "
            "comments are in square brackets."
        ),
        FMT_MD : (
            "Exports a standard markdown file. Comments are converted "
            "to preformatted text blocks."
        ),
        FMT_HTML : (
            "Exports a plain html5 file. Comments are wrapped in "
            "blocks with a yellow background colour."
        ),
        FMT_TEX : (
            "Exports a LaTeX file that can be compiled to PDF using "
            "for instance PDFLaTeX. Comments are exported as LaTeX "
            "comments."
        ),
        FMT_PDOC : (
            "Exports first to markdown or html5. The file is then "
            "passed on to Pandoc for a second stage. Use the Pandoc "
            "tab for settings up the conversion."
        ),
    }

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme
        self.outerBox   = QGridLayout()
        self.optState   = self.theProject.optState
        self.currFormat = self.FMT_TXT

        # Select Files
        self.guiFiles     = QGroupBox("Selection", self)
        self.guiFilesForm = QGridLayout(self)
        self.guiFiles.setLayout(self.guiFilesForm)

        self.expNovel = QCheckBox("Novel files",self)
        self.expNovel.setChecked(
            self.optState.getBool("GuiExport", "wNovel", True)
        )
        self.expNovel.setToolTip("Include all novel files in the exported document")

        self.expNotes = QCheckBox("Note files",self)
        self.expNotes.setChecked(
            self.optState.getBool("GuiExport", "wNotes", False)
        )
        self.expNotes.setToolTip("Include all note files in the exported document")

        self.expComments = QCheckBox("Comments",self)
        self.expComments.setChecked(
            self.optState.getBool("GuiExport", "wComments", False)
        )
        self.expComments.setToolTip("Export comments from all files")

        self.expKeywords = QCheckBox("Keywords",self)
        self.expKeywords.setChecked(
            self.optState.getBool("GuiExport", "wKeywords", False)
        )
        self.expKeywords.setToolTip("Export @keywords from all files")

        self.guiFilesForm.addWidget(self.expNovel,    0, 1)
        self.guiFilesForm.addWidget(self.expComments, 0, 2)
        self.guiFilesForm.addWidget(self.expNotes,    1, 1)
        self.guiFilesForm.addWidget(self.expKeywords, 1, 2)
        self.guiFilesForm.setRowStretch(2, 1)

        # Chapter Settings
        self.guiChapters     = QGroupBox("Chapter Headings", self)
        self.guiChaptersForm = QGridLayout(self)
        self.guiChapters.setLayout(self.guiChaptersForm)

        self.chapterFormat = QLineEdit()
        self.chapterFormat.setMaxLength(200)
        self.chapterFormat.setText(
            self.optState.getString("GuiExport", "chFormat", "Chapter %numword%")
        )
        self.chapterFormat.setToolTip("Available formats: %num%, %numword%, %title%")
        self.chapterFormat.setMinimumWidth(250)

        self.unnumFormat = QLineEdit()
        self.unnumFormat.setMaxLength(200)
        self.unnumFormat.setText(
            self.optState.getString("GuiExport", "unFormat", "%title%")
        )
        self.unnumFormat.setToolTip("Available formats: %title%")
        self.unnumFormat.setMinimumWidth(250)

        self.guiChaptersForm.addWidget(QLabel("Numbered"),   0, 0)
        self.guiChaptersForm.addWidget(self.chapterFormat,   0, 1)
        self.guiChaptersForm.addWidget(QLabel("Unnumbered"), 1, 0)
        self.guiChaptersForm.addWidget(self.unnumFormat,     1, 1)

        # Scene and Section Settings
        self.guiScenes     = QGroupBox("Other Headings", self)
        self.guiScenesForm = QGridLayout(self)
        self.guiScenes.setLayout(self.guiScenesForm)

        self.sceneFormat = QLineEdit()
        self.sceneFormat.setMaxLength(200)
        self.sceneFormat.setText(
            self.optState.getString("GuiExport", "scFormat", "* * *")
        )
        self.sceneFormat.setToolTip("Available formats: %title%")
        self.sceneFormat.setMinimumWidth(100)

        self.sectionFormat = QLineEdit()
        self.sectionFormat.setMaxLength(200)
        self.sectionFormat.setText(
            self.optState.getString("GuiExport", "seFormat", "")
        )
        self.sectionFormat.setToolTip("Available formats: %title%")
        self.sectionFormat.setMinimumWidth(100)

        self.hideScene = QCheckBox("Skip",self)
        self.hideScene.setChecked(
            self.optState.getBool("GuiExport", "hScene", False)
        )
        self.hideScene.setToolTip("Skip scene titles in export")

        self.hideSection = QCheckBox("Skip",self)
        self.hideSection.setChecked(
            self.optState.getBool("GuiExport", "hSection", False)
        )
        self.hideSection.setToolTip("Skip section titles in export")

        self.guiScenesForm.addWidget(QLabel("Scenes"),   0, 0)
        self.guiScenesForm.addWidget(self.sceneFormat,   0, 1)
        self.guiScenesForm.addWidget(self.hideScene,     0, 2)
        self.guiScenesForm.addWidget(QLabel("Sections"), 1, 0)
        self.guiScenesForm.addWidget(self.sectionFormat, 1, 1)
        self.guiScenesForm.addWidget(self.hideSection,   1, 2)

        # Output Path
        self.exportTo     = QGroupBox("Export Folder", self)
        self.exportToForm = QGridLayout(self)
        self.exportTo.setLayout(self.exportToForm)

        self.exportPath = QLineEdit(
            self.optState.getString("GuiExport", "saveTo", "")
        )
        self.exportGetPath = QPushButton(self.theTheme.getIcon("folder"),"")
        self.exportGetPath.clicked.connect(self._exportFolder)

        self.exportToForm.addWidget(QLabel("Save to"),  0, 0)
        self.exportToForm.addWidget(self.exportPath,    0, 1)
        self.exportToForm.addWidget(self.exportGetPath, 0, 2)

        # Output Format
        self.guiOutput     = QGroupBox("Export", self)
        self.guiOutputForm = QGridLayout(self)
        self.guiOutput.setLayout(self.guiOutputForm)

        self.outputHelp = QLabel("")
        self.outputHelp.setWordWrap(True)
        self.outputHelp.setMinimumHeight(55)
        self.outputHelp.setAlignment(Qt.AlignTop)

        self.outputFormat = QComboBox(self)
        self.outputFormat.addItem("novelWriter Markdown (.nwd)", self.FMT_NWD)
        self.outputFormat.addItem("Plain Text (.txt)",           self.FMT_TXT)
        self.outputFormat.addItem("Markdown (.md)",              self.FMT_MD)
        self.outputFormat.addItem("HTML5 (.htm)",                self.FMT_HTML)
        self.outputFormat.addItem("LaTeX for PDF (.tex)",        self.FMT_TEX)
        self.outputFormat.addItem("Pandoc via Markdown or HTML", self.FMT_PDOC)
        self.outputFormat.currentIndexChanged.connect(self._updateFormat)

        optIdx = self.outputFormat.findData(
            self.optState.getInt("GuiExport", "eFormat", 1)
        )
        if optIdx == -1:
            self.outputFormat.setCurrentIndex(1)
            self._updateFormat(1)
        else:
            self.outputFormat.setCurrentIndex(optIdx)
            self._updateFormat(optIdx)

        self.guiOutputForm.addWidget(QLabel("Format"),  0, 0)
        self.guiOutputForm.addWidget(self.outputFormat, 0, 1)
        self.guiOutputForm.addWidget(self.outputHelp,   1, 0, 1, 3)
        self.guiOutputForm.setColumnStretch(2, 1)

        # Additional Settings
        self.addSettings     = QGroupBox("Additional Settings (Format Dependent)", self)
        self.addSettingsForm = QGridLayout(self)
        self.addSettings.setLayout(self.addSettingsForm)

        self.fixedWidth = QSpinBox(self)
        self.fixedWidth.setMinimum(0)
        self.fixedWidth.setMaximum(999)
        self.fixedWidth.setSingleStep(1)
        self.fixedWidth.setValue(
            self.optState.getInt("GuiExport", "fixWidth", 80)
        )
        self.fixedWidth.setToolTip(
            "Applies to .txt and .md files. A value of '0' disables the feature."
        )

        self.addSettingsForm.addWidget(QLabel("Fixed width"), 0, 0)
        self.addSettingsForm.addWidget(self.fixedWidth,       0, 1)
        self.addSettingsForm.setColumnStretch(2, 1)

        # Assemble
        self.outerBox.addWidget(self.guiOutput,   0, 0, 1, 2)
        self.outerBox.addWidget(self.guiFiles,    0, 2)
        self.outerBox.addWidget(self.guiChapters, 1, 0, 1, 2)
        self.outerBox.addWidget(self.guiScenes,   1, 2)
        self.outerBox.addWidget(self.addSettings, 2, 0, 1, 3)
        self.outerBox.addWidget(self.exportTo,    3, 0, 1, 3)
        self.outerBox.setColumnStretch(0, 1)
        self.outerBox.setColumnStretch(1, 1)
        self.outerBox.setColumnStretch(2, 1)
        self.setLayout(self.outerBox)

        return

    ##
    #  Internal Functions
    ##

    def _updateFormat(self, currIdx):
        """Update help text under output format selection and file
        extension in file box
        """
        if currIdx == -1:
            self.outputHelp.setText("")
        else:
            self.currFormat = self.outputFormat.itemData(currIdx)
            self.outputHelp.setText("<i>%s</i>" % self.FMT_HELP[self.currFormat])
            self._checkFileExtension()
        return

    def _exportFolder(self):

        currDir = self.exportPath.text()
        if not path.isdir(currDir):
            currDir = ""

        extFilter = [
            "novelWriter document files (*.nwd)",
            "Text files (*.txt)",
            "Markdown files (*.md)",
            "HTML files (*.htm *.html)",
            "LaTeX files (*.tex)",
            "All files (*.*)",
        ]

        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.DontUseNativeDialog
        saveTo  = QFileDialog.getSaveFileName(
            self, "Export File", self.exportPath.text(),
            options=dlgOpt, filter=";;".join(extFilter)
        )
        if saveTo:
            self.exportPath.setText(saveTo[0])
            self._checkFileExtension()
            return True

        return False

    def _checkFileExtension(self):
        saveTo   = self.exportPath.text()
        if saveTo.startswith("~"):
            saveTo = path.expanduser(saveTo)
        fileBits = path.splitext(saveTo)
        if self.currFormat > 0 and fileBits[0].strip() != "":
            saveTo = fileBits[0]+self.FMT_EXT[self.currFormat]
        self.exportPath.setText(saveTo)
        return

# END Class GuiExportMain

class GuiExportPandoc(QWidget):

    FMT_ODT   = 1
    FMT_DOCX  = 2
    FMT_EPUB2 = 4
    FMT_EPUB3 = 5
    FMT_ZIM   = 6
    FMT_EXT   = {
        FMT_ODT   : ".odt",
        FMT_DOCX  : ".docx",
        FMT_EPUB2 : ".epub",
        FMT_EPUB3 : ".epub",
        FMT_ZIM   : ".txt",
    }
    FMT_VIA = {
        FMT_ODT   : "html",
        FMT_DOCX  : "html",
        FMT_EPUB2 : "markdown",
        FMT_EPUB3 : "markdown",
        FMT_ZIM   : "markdown",
    }

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.theParent  = theParent
        self.theProject = theProject
        self.outerBox   = QGridLayout()
        self.optState   = self.theProject.optState

        try:
            import pypandoc
            self.hasPyPan = True
        except:
            self.hasPyPan = False

        # Information
        self.guiInfo    = QGroupBox("Information", self)
        self.guiInfoBox = QVBoxLayout(self)
        self.guiInfo.setLayout(self.guiInfoBox)

        self.infoHelp = QLabel("")
        self.infoHelp.setWordWrap(True)
        self.infoHelp.setMinimumHeight(55)
        self.infoHelp.setAlignment(Qt.AlignTop)

        self.guiInfoBox.addWidget(self.infoHelp)

        if self.hasPyPan:
            self.infoHelp.setText((
                "Additional export to other document formats than in the Settings tab is provided "
                "by Pandoc. the project is first exported to Markdown or HTML, depending on final "
                "format, and then processed by Pandoc into the desired format."
            ))
        else:
            self.infoHelp.setText((
                "The Python package 'pypandoc' is not installed or isn't working. This package is "
                "required for interfacing with Pandoc. Please install it before proceeding."
            ))

        # Output Format
        self.guiOutput     = QGroupBox("Pandoc Format", self)
        self.guiOutputForm = QGridLayout(self)
        self.guiOutput.setLayout(self.guiOutputForm)

        self.outputFormat = QComboBox(self)
        self.outputFormat.addItem("Open Office Document (.odt)", self.FMT_ODT)
        self.outputFormat.addItem("Word Document (.docx)",       self.FMT_DOCX)
        self.outputFormat.addItem("ePUB eBook v2 (.epub2)",      self.FMT_EPUB2)
        self.outputFormat.addItem("ePUB eBook v3 (.epub3)",      self.FMT_EPUB3)
        self.outputFormat.addItem("Zim Wiki (.txt)",             self.FMT_ZIM)

        optIdx = self.outputFormat.findData(
            self.optState.getInt("GuiExport", "pFormat", 1)
        )
        if optIdx == -1:
            self.outputFormat.setCurrentIndex(1)
        else:
            self.outputFormat.setCurrentIndex(optIdx)

        self.guiOutputForm.addWidget(QLabel("Format"),  0, 0)
        self.guiOutputForm.addWidget(self.outputFormat, 0, 1)
        self.guiOutputForm.setColumnStretch(2, 1)

        # Assemble
        self.outerBox.addWidget(self.guiInfo,   0, 0)
        self.outerBox.addWidget(self.guiOutput, 1, 0)
        self.outerBox.setRowStretch(2, 1)
        self.setLayout(self.outerBox)

        return

# END Class GuiExportPandoc
