# -*- coding: utf-8 -*-
"""novelWriter GUI Export Tools

 novelWriter – GUI Export Tools
================================
 Tool for exporting project files to other formats

 File History:
 Created: 2019-10-13 [0.2.3]

"""

import logging
import time
import nw

from os import path

from PyQt5.QtCore    import Qt, QSize
from PyQt5.QtSvg     import QSvgWidget
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QGridLayout, QGroupBox, QCheckBox,
    QLabel, QComboBox, QLineEdit, QPushButton, QFileDialog, QProgressBar, QSpinBox
)

from nw.project.document      import NWDoc
from nw.tools.translate       import numberToWord
from nw.tools.optlaststate    import OptLastState
from nw.convert.file.text     import TextFile
from nw.convert.file.html     import HtmlFile
from nw.convert.file.markdown import MarkdownFile
from nw.convert.file.latex    import LaTeXFile
from nw.convert.file.concat   import ConcatFile
from nw.constants             import nwFiles
from nw.enum                  import nwItemType, nwAlert

logger = logging.getLogger(__name__)

class GuiExport(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiExport ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.optState   = ExportLastState(self.theProject,nwFiles.EXPORT_OPT)
        self.optState.loadSettings()

        self.outerBox   = QHBoxLayout()
        self.innerBox   = QVBoxLayout()
        self.setWindowTitle("Export Project")
        self.setLayout(self.outerBox)

        self.gradPath = path.abspath(path.join(self.mainConf.appPath,"graphics","export.svg"))
        self.svgGradient = QSvgWidget(self.gradPath)
        self.svgGradient.setFixedSize(QSize(64,64))

        self.theProject.countStatus()
        self.tabMain   = GuiExportMain(self.theParent, self.theProject, self.optState)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.tabMain, "Settings")

        self.outerBox.addWidget(self.svgGradient, 0, Qt.AlignTop)
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
        chFormat  = self.tabMain.chapterFormat.text()
        unFormat  = self.tabMain.unnumFormat.text()
        scFormat  = self.tabMain.sceneFormat.text()
        seFormat  = self.tabMain.sectionFormat.text()
        saveTo    = self.tabMain.exportPath.text()

        nItems = len(self.theProject.treeOrder)
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

        if outFile is None:
            return False

        if outFile.openFile(saveTo):
            outFile.setComments(wComments)
            outFile.setExportNovel(wNovel)
            outFile.setExportNotes(wNotes)
            outFile.setWordWrap(fixWidth)
            outFile.setChapterFormat(chFormat)
            outFile.setUnNumberedFormat(unFormat)
            outFile.setSceneFormat(scFormat)
            outFile.setSectionFormat(seFormat)
        else:
            self.exportStatus.setText("Failed to open file for writing ...")
            return False

        time.sleep(0.5)

        nDone = 0
        for tHandle in self.theProject.treeOrder:

            self.exportProgress.setValue(nDone)
            tItem = self.theProject.getItem(tHandle)

            self.exportStatus.setText("Exporting: %s" % tItem.itemName)
            logger.verbose("Exporting: %s" % tItem.itemName)

            if tItem is not None and tItem.itemType == nwItemType.FILE:
                outFile.addText(tHandle)

            nDone += 1

        outFile.closeFile()
        self.exportProgress.setValue(nDone)
        self.exportStatus.setText("Export to %s complete" % outFile.fileName)
        logger.verbose("Export to %s complete" % outFile.fileName)

        if eFormat == GuiExportMain.FMT_TEX:
            # Check that encoding was successful
            if outFile.texCodecFail:
                self.theParent.makeAlert((
                    "Failed to escape unicode characters while writing LaTeX file. "
                    "The genrated .tex file may not build properly. "
                    "Make sure the python package 'latexcodec' is installed and working."
                ), nwAlert.WARN)

        return

    def _doClose(self):

        logger.verbose("GuiExport close button clicked")

        wNovel    = self.tabMain.expNovel.isChecked()
        wNotes    = self.tabMain.expNotes.isChecked()
        eFormat   = self.tabMain.outputFormat.currentData()
        fixWidth  = self.tabMain.fixedWidth.value()
        wComments = self.tabMain.expComments.isChecked()
        chFormat  = self.tabMain.chapterFormat.text()
        unFormat  = self.tabMain.unnumFormat.text()
        scFormat  = self.tabMain.sceneFormat.text()
        seFormat  = self.tabMain.sectionFormat.text()
        saveTo    = self.tabMain.exportPath.text()

        self.optState.setSetting("wNovel",   wNovel)
        self.optState.setSetting("wNotes",   wNotes)
        self.optState.setSetting("eFormat",  eFormat)
        self.optState.setSetting("fixWidth", fixWidth)
        self.optState.setSetting("wComments",wComments)
        self.optState.setSetting("chFormat", chFormat)
        self.optState.setSetting("unFormat", unFormat)
        self.optState.setSetting("scFormat", scFormat)
        self.optState.setSetting("seFormat", seFormat)
        self.optState.setSetting("saveTo",   saveTo)

        self.optState.saveSettings()
        self.close()

        return

# END Class GuiExport

class GuiExportMain(QWidget):

    FMT_NWD   = 1 # novelWriter markdown
    FMT_TXT   = 2 # Plain text file
    FMT_MD    = 3 # Markdown file
    FMT_HTML  = 4 # HTML file
    FMT_EBOOK = 5 # E-book friendly HTML
    FMT_ODT   = 6 # Open document
    FMT_TEX   = 7 # LaTeX file
    FMT_EXT   = {
        FMT_NWD   : ".nwd",
        FMT_TXT   : ".txt",
        FMT_MD    : ".md",
        FMT_HTML  : ".htm",
        FMT_EBOOK : ".htm",
        FMT_ODT   : ".odt",
        FMT_TEX   : ".tex",
    }
    FMT_HELP  = {
        FMT_NWD : (
            "Exports a document using the novelWriter markdown format. "
            "The files selected by the filters are appended as-is, including comments and other settings."
        ),
        FMT_TXT : (
            "Exports a plain text file. "
            "All formatting is stripped and comments are in square brackets."
        ),
        FMT_MD : (
            "Exports a standard markdown file. "
            "Comments are converted to preformatted text blocks."
        ),
        FMT_HTML : (
            "Exports a plain html5 file. "
            "Comments are wrapped in blocks with a yellow background colour."
        ),
        FMT_EBOOK : (
            "Exports an html5 file that can be converted to eBook with Calibre. "
            "Comments are not exported in this format."
        ),
        FMT_ODT : (
            "Exports an open document file that can be read by office applications. "
            "Comments are exported as grey text."
        ),
        FMT_TEX : (
            "Exports a LaTeX file that can be compiled to PDF using for instance PDFLaTeX. "
            "Comments are exported as LaTeX comments."
        ),
    }

    def __init__(self, theParent, theProject, optState):
        QWidget.__init__(self, theParent)

        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme
        self.outerBox   = QGridLayout()
        self.optState   = optState
        self.currFormat = self.FMT_TXT

        # Select Files
        self.guiFiles     = QGroupBox("Selection", self)
        self.guiFilesForm = QGridLayout(self)
        self.guiFiles.setLayout(self.guiFilesForm)

        self.expNovel = QCheckBox(self)
        self.expNovel.setChecked(self.optState.getSetting("wNovel"))
        self.expNovel.setToolTip("Include all novel files in the exported document")

        self.expNotes = QCheckBox(self)
        self.expNotes.setChecked(self.optState.getSetting("wNotes"))
        self.expNotes.setToolTip("Include all note files in the exported document")

        self.expComments = QCheckBox(self)
        self.expComments.setChecked(self.optState.getSetting("wComments"))
        self.expComments.setToolTip("Export comments from all files")

        self.guiFilesForm.addWidget(QLabel("Novel files"), 0, 0)
        self.guiFilesForm.addWidget(self.expNovel,         0, 1)
        self.guiFilesForm.addWidget(QLabel("Note files"),  1, 0)
        self.guiFilesForm.addWidget(self.expNotes,         1, 1)
        self.guiFilesForm.addWidget(QLabel("Comments"),    2, 0)
        self.guiFilesForm.addWidget(self.expComments,      2, 1)

        # Chapter Settings
        self.guiChapters     = QGroupBox("Chapter Headings", self)
        self.guiChaptersForm = QGridLayout(self)
        self.guiChapters.setLayout(self.guiChaptersForm)

        self.chapterFormat = QLineEdit()
        self.chapterFormat.setText(self.optState.getSetting("chFormat"))
        self.chapterFormat.setToolTip("Available formats: %num%, %numword%, %title%")
        self.chapterFormat.setMinimumWidth(250)

        self.unnumFormat = QLineEdit()
        self.unnumFormat.setText(self.optState.getSetting("unFormat"))
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
        self.sceneFormat.setText(self.optState.getSetting("scFormat"))
        self.sceneFormat.setToolTip("Available formats: %title%")
        self.sceneFormat.setMinimumWidth(100)

        self.sectionFormat = QLineEdit()
        self.sectionFormat.setText(self.optState.getSetting("seFormat"))
        self.sectionFormat.setToolTip("Available formats: %title%")
        self.sectionFormat.setMinimumWidth(100)

        self.guiScenesForm.addWidget(QLabel("Scenes"),   0, 0)
        self.guiScenesForm.addWidget(self.sceneFormat,   0, 1)
        self.guiScenesForm.addWidget(QLabel("Sections"), 1, 0)
        self.guiScenesForm.addWidget(self.sectionFormat, 1, 1)

        # Output Path
        self.exportTo     = QGroupBox("Export Folder", self)
        self.exportToForm = QGridLayout(self)
        self.exportTo.setLayout(self.exportToForm)

        self.exportPath = QLineEdit(self.optState.getSetting("saveTo"))

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
        # self.outputFormat.addItem("HTML5 for eBook (.htm)",    self.FMT_EBOOK)
        # self.outputFormat.addItem("Open Document (.odt)",      self.FMT_ODT)
        self.outputFormat.addItem("LaTeX for PDF (.tex)",        self.FMT_TEX)
        self.outputFormat.currentIndexChanged.connect(self._updateFormat)

        optIdx = self.outputFormat.findData(self.optState.getSetting("eFormat"))
        if optIdx != -1:
            self.outputFormat.setCurrentIndex(optIdx)
            self._updateFormat(optIdx)

        self.guiOutputForm.addWidget(QLabel("Format"),  0, 0)
        self.guiOutputForm.addWidget(self.outputFormat, 0, 1)
        self.guiOutputForm.addWidget(self.outputHelp,   1, 0, 1, 3)
        self.guiOutputForm.setColumnStretch(2, 1)

        # Additional Settings
        self.addSettings     = QGroupBox("Additional Settings", self)
        self.addSettingsForm = QGridLayout(self)
        self.addSettings.setLayout(self.addSettingsForm)

        self.fixedWidth = QSpinBox(self)
        self.fixedWidth.setMinimum(0)
        self.fixedWidth.setMaximum(999)
        self.fixedWidth.setSingleStep(1)
        self.fixedWidth.setValue(self.optState.getSetting("fixWidth"))
        self.fixedWidth.setToolTip("Applies to .txt, .md and .tex files. 0 disables the feature.")

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
        """Update help text under output format selection and file extension in file box
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
            # "Open document files (*.odt)",
            "LaTeX files (*.tex)",
            "All files (*.*)",
        ]

        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        saveTo  = QFileDialog.getSaveFileName(
            self,"Export File",self.exportPath.text(),options=dlgOpt,filter=";;".join(extFilter)
        )
        if saveTo:
            self.exportPath.setText(saveTo[0])
            self._checkFileExtension()
            return True

        return False

    def _checkFileExtension(self):
        saveTo   = self.exportPath.text()
        fileBits = path.splitext(saveTo)
        if self.currFormat > 0:
            saveTo = fileBits[0]+self.FMT_EXT[self.currFormat]
        self.exportPath.setText(saveTo)
        return

# END Class GuiExportMain

class ExportLastState(OptLastState):

    def __init__(self, theProject, theFile):
        OptLastState.__init__(self, theProject, theFile)
        self.theState   = {
            "wNovel"    : True,
            "wNotes"    : False,
            "eFormat"   : 1,
            "fixWidth"  : 80,
            "wComments" : False,
            "chFormat"  : "Chapter %numword%",
            "unFormat"  : "%title%",
            "scFormat"  : "* * *",
            "seFormat"  : "",
            "saveTo"    : "",
        }
        self.stringOpt = ("chFormat","unFormat","scFormat","seFormat","saveTo")
        self.boolOpt   = ("wNovel","wNotes","wComments")
        self.intOpt    = ("eFormat","fixWidth")
        return

# END Class ExportLastState
