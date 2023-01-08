"""
novelWriter – GUI Build Novel Project
=====================================
GUI classes for the build novel project dialog

File History:
Created: 2020-05-09 [0.5]

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

import json
import logging
import novelwriter

from time import time
from pathlib import Path
from datetime import datetime

from PyQt5.QtGui import (
    QPalette, QColor, QFont, QCursor, QFontInfo
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    qApp, QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QLabel,
    QLineEdit, QGroupBox, QGridLayout, QProgressBar, QMenu, QAction,
    QFileDialog, QFontDialog, QSpinBox, QScrollArea, QSplitter, QWidget,
    QSizePolicy, QDoubleSpinBox, QComboBox
)
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog

from novelwriter.enum import nwAlert, nwItemType, nwItemLayout, nwItemClass
from novelwriter.error import formatException, logException
from novelwriter.common import fuzzyTime, makeFileNameSafe
from novelwriter.custom import QSwitch
from novelwriter.constants import nwConst, nwFiles
from novelwriter.core.tomd import ToMarkdown
from novelwriter.core.toodt import ToOdt
from novelwriter.core.tohtml import ToHtml

logger = logging.getLogger(__name__)


class GuiBuildNovel(QDialog):

    FMT_PDF    = 1  # Print to PDF
    FMT_ODT    = 2  # Open Document file
    FMT_FODT   = 3  # Flat Open Document file
    FMT_HTM    = 4  # HTML5
    FMT_NWD    = 5  # nW Markdown
    FMT_MD     = 6  # Standard Markdown
    FMT_GH     = 7  # GitHub Markdown
    FMT_JSON_H = 8  # HTML5 wrapped in JSON
    FMT_JSON_M = 9  # nW Markdown wrapped in JSON

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiBuildNovel ...")
        self.setObjectName("GuiBuildNovel")

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self.htmlText  = []  # List of html documents
        self.htmlStyle = []  # List of html styles
        self.htmlSize  = 0   # Size of the html document
        self.buildTime = 0   # The timestamp of the last build

        self.setWindowTitle(self.tr("Build Novel Project"))
        self.setMinimumWidth(self.mainConf.pxInt(700))
        self.setMinimumHeight(self.mainConf.pxInt(600))

        pOptions = self.theProject.options
        self.resize(
            self.mainConf.pxInt(pOptions.getInt("GuiBuildNovel", "winWidth",  900)),
            self.mainConf.pxInt(pOptions.getInt("GuiBuildNovel", "winHeight", 800))
        )

        self.docView = GuiBuildNovelDocView(self, self.theProject)

        hS = self.mainTheme.fontPixelSize
        wS = 2*hS

        # Title Formats
        # =============

        self.titleGroup = QGroupBox(self.tr("Title Formats for Novel Files"), self)
        self.titleForm  = QGridLayout(self)
        self.titleGroup.setLayout(self.titleForm)

        fmtHelp = "<br>".join([
            "<b>%s</b>" % self.tr("Formatting Codes:"),
            self.tr("{0} for the title as set in the document").format(r"%title%"),
            self.tr("{0} for chapter number (1, 2, 3)").format(r"%ch%"),
            self.tr("{0} for chapter number as a word (one, two)").format(r"%chw%"),
            self.tr("{0} for chapter number in upper case Roman").format(r"%chI%"),
            self.tr("{0} for chapter number in lower case Roman").format(r"%chi%"),
            self.tr("{0} for scene number within chapter").format(r"%sc%"),
            self.tr("{0} for scene number within novel").format(r"%sca%"),
        ])
        fmtScHelp = "<br><br>%s" % self.tr(
            "Leave blank to skip this heading, or set to a static text, like "
            "for instance '{0}', to make a separator. The separator will "
            "be centred automatically and only appear between sections of "
            "the same type."
        ).format("* * *")
        xFmt = self.mainConf.pxInt(100)

        self.fmtTitle = QLineEdit()
        self.fmtTitle.setMaxLength(200)
        self.fmtTitle.setMinimumWidth(xFmt)
        self.fmtTitle.setToolTip(fmtHelp)
        self.fmtTitle.setText(
            self._reFmtCodes(self.theProject.data.getTitleFormat("title"))
        )

        self.fmtChapter = QLineEdit()
        self.fmtChapter.setMaxLength(200)
        self.fmtChapter.setMinimumWidth(xFmt)
        self.fmtChapter.setToolTip(fmtHelp)
        self.fmtChapter.setText(
            self._reFmtCodes(self.theProject.data.getTitleFormat("chapter"))
        )

        self.fmtUnnumbered = QLineEdit()
        self.fmtUnnumbered.setMaxLength(200)
        self.fmtUnnumbered.setMinimumWidth(xFmt)
        self.fmtUnnumbered.setToolTip(fmtHelp)
        self.fmtUnnumbered.setText(
            self._reFmtCodes(self.theProject.data.getTitleFormat("unnumbered"))
        )

        self.fmtScene = QLineEdit()
        self.fmtScene.setMaxLength(200)
        self.fmtScene.setMinimumWidth(xFmt)
        self.fmtScene.setToolTip(fmtHelp + fmtScHelp)
        self.fmtScene.setText(
            self._reFmtCodes(self.theProject.data.getTitleFormat("scene"))
        )

        self.fmtSection = QLineEdit()
        self.fmtSection.setMaxLength(200)
        self.fmtSection.setMinimumWidth(xFmt)
        self.fmtSection.setToolTip(fmtHelp + fmtScHelp)
        self.fmtSection.setText(
            self._reFmtCodes(self.theProject.data.getTitleFormat("section"))
        )

        self.buildLang = QComboBox()
        self.buildLang.setMinimumWidth(xFmt)
        theLangs = self.mainConf.listLanguages(self.mainConf.LANG_PROJ)
        self.buildLang.addItem("[%s]" % self.tr("Not Set"), "None")
        for langID, langName in theLangs:
            self.buildLang.addItem(langName, langID)

        langIdx = self.buildLang.findData(self.theProject.data.language)
        if langIdx != -1:
            self.buildLang.setCurrentIndex(langIdx)

        self.hideScene = QSwitch(width=wS, height=hS)
        self.hideScene.setChecked(
            pOptions.getBool("GuiBuildNovel", "hideScene", False)
        )

        self.hideSection = QSwitch(width=wS, height=hS)
        self.hideSection.setChecked(
            pOptions.getBool("GuiBuildNovel", "hideSection", True)
        )

        # Wrapper boxes due to QGridView and QLineEdit expand bug
        self.boxTitle = QHBoxLayout()
        self.boxTitle.addWidget(self.fmtTitle)
        self.boxChapter = QHBoxLayout()
        self.boxChapter.addWidget(self.fmtChapter)
        self.boxUnnumb = QHBoxLayout()
        self.boxUnnumb.addWidget(self.fmtUnnumbered)
        self.boxScene = QHBoxLayout()
        self.boxScene.addWidget(self.fmtScene)
        self.boxSection = QHBoxLayout()
        self.boxSection.addWidget(self.fmtSection)

        titleLabel    = QLabel(self.tr("Title"))
        chapterLabel  = QLabel(self.tr("Chapter"))
        unnumbLabel   = QLabel(self.tr("Unnumbered"))
        sceneLabel    = QLabel(self.tr("Scene"))
        sectionLabel  = QLabel(self.tr("Section"))
        langLabel     = QLabel(self.tr("Language"))
        hSceneLabel   = QLabel(self.tr("Hide scene"))
        hSectionLabel = QLabel(self.tr("Hide section"))

        self.titleForm.addWidget(titleLabel,       0, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addLayout(self.boxTitle,    0, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(chapterLabel,     1, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addLayout(self.boxChapter,  1, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(unnumbLabel,      2, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addLayout(self.boxUnnumb,   2, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(sceneLabel,       3, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addLayout(self.boxScene,    3, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(sectionLabel,     4, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addLayout(self.boxSection,  4, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(langLabel,        5, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addWidget(self.buildLang,   5, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(hSceneLabel,      6, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addWidget(self.hideScene,   6, 1, 1, 1, Qt.AlignRight)
        self.titleForm.addWidget(hSectionLabel,    7, 0, 1, 1, Qt.AlignLeft)
        self.titleForm.addWidget(self.hideSection, 7, 1, 1, 1, Qt.AlignRight)

        self.titleForm.setColumnStretch(0, 0)
        self.titleForm.setColumnStretch(1, 1)

        # Font Options
        # ============

        self.fontGroup = QGroupBox(self.tr("Font Options"), self)
        self.fontForm  = QGridLayout(self)
        self.fontGroup.setLayout(self.fontForm)

        # Font Family
        self.textFont = QLineEdit()
        self.textFont.setReadOnly(True)
        self.textFont.setMinimumWidth(xFmt)
        self.textFont.setText(
            pOptions.getString("GuiBuildNovel", "textFont", self.mainConf.textFont)
        )
        self.fontButton = QPushButton("...")
        self.fontButton.setMaximumWidth(int(2.5*self.mainTheme.getTextWidth("...")))
        self.fontButton.clicked.connect(self._selectFont)

        self.textSize = QSpinBox(self)
        self.textSize.setFixedWidth(6*self.mainTheme.textNWidth)
        self.textSize.setMinimum(6)
        self.textSize.setMaximum(72)
        self.textSize.setSingleStep(1)
        self.textSize.setValue(
            pOptions.getInt("GuiBuildNovel", "textSize", self.mainConf.textSize)
        )

        self.lineHeight = QDoubleSpinBox(self)
        self.lineHeight.setFixedWidth(6*self.mainTheme.textNWidth)
        self.lineHeight.setMinimum(0.8)
        self.lineHeight.setMaximum(3.0)
        self.lineHeight.setSingleStep(0.05)
        self.lineHeight.setDecimals(2)
        self.lineHeight.setValue(
            pOptions.getFloat("GuiBuildNovel", "lineHeight", 1.15)
        )

        # Wrapper box due to QGridView and QLineEdit expand bug
        self.boxFont = QHBoxLayout()
        self.boxFont.addWidget(self.textFont)

        fontFamilyLabel = QLabel(self.tr("Font family"))
        fontSizeLabel   = QLabel(self.tr("Font size"))
        lineHeightLabel = QLabel(self.tr("Line height"))
        justifyLabel    = QLabel(self.tr("Justify text"))
        stylingLabel    = QLabel(self.tr("Disable styling"))

        self.fontForm.addWidget(fontFamilyLabel,  0, 0, 1, 1, Qt.AlignLeft)
        self.fontForm.addLayout(self.boxFont,     0, 1, 1, 1, Qt.AlignRight)
        self.fontForm.addWidget(self.fontButton,  0, 2, 1, 1, Qt.AlignRight)
        self.fontForm.addWidget(fontSizeLabel,    1, 0, 1, 1, Qt.AlignLeft)
        self.fontForm.addWidget(self.textSize,    1, 1, 1, 2, Qt.AlignRight)
        self.fontForm.addWidget(lineHeightLabel,  2, 0, 1, 1, Qt.AlignLeft)
        self.fontForm.addWidget(self.lineHeight,  2, 1, 1, 2, Qt.AlignRight)

        self.fontForm.setColumnStretch(0, 0)
        self.fontForm.setColumnStretch(1, 1)
        self.fontForm.setColumnStretch(2, 0)

        # Styling Options
        # ===============

        self.styleGroup = QGroupBox(self.tr("Styling Options"), self)
        self.styleForm  = QGridLayout(self)
        self.styleGroup.setLayout(self.styleForm)

        self.justifyText = QSwitch(width=wS, height=hS)
        self.justifyText.setChecked(
            pOptions.getBool("GuiBuildNovel", "justifyText", False)
        )

        self.noStyling = QSwitch(width=wS, height=hS)
        self.noStyling.setChecked(
            pOptions.getBool("GuiBuildNovel", "noStyling", False)
        )

        self.styleForm.addWidget(justifyLabel,     1, 0, 1, 1, Qt.AlignLeft)
        self.styleForm.addWidget(self.justifyText, 1, 1, 1, 2, Qt.AlignRight)
        self.styleForm.addWidget(stylingLabel,     2, 0, 1, 1, Qt.AlignLeft)
        self.styleForm.addWidget(self.noStyling,   2, 1, 1, 2, Qt.AlignRight)

        self.styleForm.setColumnStretch(0, 0)
        self.styleForm.setColumnStretch(1, 1)

        # Include Options
        # ===============

        self.textGroup = QGroupBox(self.tr("Include Options"), self)
        self.textForm  = QGridLayout(self)
        self.textGroup.setLayout(self.textForm)

        self.includeSynopsis = QSwitch(width=wS, height=hS)
        self.includeSynopsis.setChecked(
            pOptions.getBool("GuiBuildNovel", "incSynopsis", False)
        )

        self.includeComments = QSwitch(width=wS, height=hS)
        self.includeComments.setChecked(
            pOptions.getBool("GuiBuildNovel", "incComments", False)
        )

        self.includeKeywords = QSwitch(width=wS, height=hS)
        self.includeKeywords.setChecked(
            pOptions.getBool("GuiBuildNovel", "incKeywords", False)
        )

        self.includeBody = QSwitch(width=wS, height=hS)
        self.includeBody.setChecked(
            pOptions.getBool("GuiBuildNovel", "incBodyText", True)
        )

        synopsisLabel = QLabel(self.tr("Include synopsis"))
        commentsLabel = QLabel(self.tr("Include comments"))
        keywordsLabel = QLabel(self.tr("Include keywords"))
        bodyLabel     = QLabel(self.tr("Include body text"))

        self.textForm.addWidget(synopsisLabel,        0, 0, 1, 1, Qt.AlignLeft)
        self.textForm.addWidget(self.includeSynopsis, 0, 1, 1, 1, Qt.AlignRight)
        self.textForm.addWidget(commentsLabel,        1, 0, 1, 1, Qt.AlignLeft)
        self.textForm.addWidget(self.includeComments, 1, 1, 1, 1, Qt.AlignRight)
        self.textForm.addWidget(keywordsLabel,        2, 0, 1, 1, Qt.AlignLeft)
        self.textForm.addWidget(self.includeKeywords, 2, 1, 1, 1, Qt.AlignRight)
        self.textForm.addWidget(bodyLabel,            3, 0, 1, 1, Qt.AlignLeft)
        self.textForm.addWidget(self.includeBody,     3, 1, 1, 1, Qt.AlignRight)

        self.textForm.setColumnStretch(0, 1)
        self.textForm.setColumnStretch(1, 0)

        # Root Filter Options
        # ===================

        self.rootGroup = QGroupBox(self.tr("Root Filter Options"), self)
        self.rootForm  = QGridLayout(self)
        self.rootGroup.setLayout(self.rootForm)

        rootFilter = pOptions.getValue("GuiBuildNovel", "rootFilter", [])
        if not isinstance(rootFilter, list):
            rootFilter = []

        iRow = 0
        self.rootSelection = {}
        for tHandle, nwItem in self.theProject.tree.iterRoots(None):
            if not nwItem.isInactive():
                rootLabel = QLabel(nwItem.itemName)
                rootLabel.setWordWrap(True)

                rootValue = QSwitch(width=wS, height=hS)
                rootValue.setChecked(tHandle not in rootFilter)

                self.rootSelection[tHandle] = rootValue
                self.rootForm.addWidget(rootLabel, iRow, 0, 1, 1, Qt.AlignLeft)
                self.rootForm.addWidget(rootValue, iRow, 1, 1, 1, Qt.AlignRight)

                iRow += 1

        self.rootForm.setColumnStretch(0, 1)
        self.rootForm.setColumnStretch(1, 0)

        # File Filter Options
        # ===================

        self.fileGroup = QGroupBox(self.tr("File Filter Options"), self)
        self.fileForm  = QGridLayout(self)
        self.fileGroup.setLayout(self.fileForm)

        self.novelFiles = QSwitch(width=wS, height=hS)
        self.novelFiles.setChecked(
            pOptions.getBool("GuiBuildNovel", "addNovel", True)
        )

        self.noteFiles = QSwitch(width=wS, height=hS)
        self.noteFiles.setChecked(
            pOptions.getBool("GuiBuildNovel", "addNotes", False)
        )

        self.ignoreFlag = QSwitch(width=wS, height=hS)
        self.ignoreFlag.setChecked(
            pOptions.getBool("GuiBuildNovel", "ignoreFlag", False)
        )

        novelLabel  = QLabel(self.tr("Include novel files"))
        notesLabel  = QLabel(self.tr("Include note files"))
        activeLabel = QLabel(self.tr("Include inactive files"))

        self.fileForm.addWidget(novelLabel,      0, 0, 1, 1, Qt.AlignLeft)
        self.fileForm.addWidget(self.novelFiles, 0, 1, 1, 1, Qt.AlignRight)
        self.fileForm.addWidget(notesLabel,      1, 0, 1, 1, Qt.AlignLeft)
        self.fileForm.addWidget(self.noteFiles,  1, 1, 1, 1, Qt.AlignRight)
        self.fileForm.addWidget(activeLabel,     2, 0, 1, 1, Qt.AlignLeft)
        self.fileForm.addWidget(self.ignoreFlag, 2, 1, 1, 1, Qt.AlignRight)

        self.fileForm.setColumnStretch(0, 1)
        self.fileForm.setColumnStretch(1, 0)

        # Export Options
        # ==============

        self.exportGroup = QGroupBox(self.tr("Export Options"), self)
        self.exportForm  = QGridLayout(self)
        self.exportGroup.setLayout(self.exportForm)

        self.replaceTabs = QSwitch(width=wS, height=hS)
        self.replaceTabs.setChecked(
            pOptions.getBool("GuiBuildNovel", "replaceTabs", False)
        )

        self.replaceUCode = QSwitch(width=wS, height=hS)
        self.replaceUCode.setChecked(
            pOptions.getBool("GuiBuildNovel", "replaceUCode", False)
        )

        tabsLabel  = QLabel(self.tr("Replace tabs with spaces"))
        uCodeLabel = QLabel(self.tr("Replace Unicode in HTML"))

        self.exportForm.addWidget(tabsLabel,         0, 0, 1, 1, Qt.AlignLeft)
        self.exportForm.addWidget(self.replaceTabs,  0, 1, 1, 1, Qt.AlignRight)
        self.exportForm.addWidget(uCodeLabel,        1, 0, 1, 1, Qt.AlignLeft)
        self.exportForm.addWidget(self.replaceUCode, 1, 1, 1, 1, Qt.AlignRight)

        self.exportForm.setColumnStretch(0, 1)
        self.exportForm.setColumnStretch(1, 0)

        # Build Button
        # ============

        self.buildProgress = QProgressBar()

        self.buildNovel = QPushButton(self.tr("Build Preview"))
        self.buildNovel.clicked.connect(self._buildPreview)

        # Action Buttons
        # ==============

        self.buttonBox = QHBoxLayout()

        # Printing

        self.printMenu = QMenu(self)
        self.btnPrint = QPushButton(self.tr("Print"))
        self.btnPrint.setMenu(self.printMenu)

        self.printSend = QAction(self.tr("Print Preview"), self)
        self.printSend.triggered.connect(self._printDocument)
        self.printMenu.addAction(self.printSend)

        self.printFile = QAction(self.tr("Print to PDF"), self)
        self.printFile.triggered.connect(lambda: self._saveDocument(self.FMT_PDF))
        self.printMenu.addAction(self.printFile)

        # Saving to File

        self.saveMenu = QMenu(self)
        self.btnSave = QPushButton(self.tr("Save As"))
        self.btnSave.setMenu(self.saveMenu)

        self.saveODT = QAction(self.tr("Open Document (.odt)"), self)
        self.saveODT.triggered.connect(lambda: self._saveDocument(self.FMT_ODT))
        self.saveMenu.addAction(self.saveODT)

        self.saveFODT = QAction(self.tr("Flat Open Document (.fodt)"), self)
        self.saveFODT.triggered.connect(lambda: self._saveDocument(self.FMT_FODT))
        self.saveMenu.addAction(self.saveFODT)

        self.saveHTM = QAction(self.tr("novelWriter HTML (.htm)"), self)
        self.saveHTM.triggered.connect(lambda: self._saveDocument(self.FMT_HTM))
        self.saveMenu.addAction(self.saveHTM)

        self.saveNWD = QAction(self.tr("novelWriter Markdown (.nwd)"), self)
        self.saveNWD.triggered.connect(lambda: self._saveDocument(self.FMT_NWD))
        self.saveMenu.addAction(self.saveNWD)

        self.saveMD = QAction(self.tr("Standard Markdown (.md)"), self)
        self.saveMD.triggered.connect(lambda: self._saveDocument(self.FMT_MD))
        self.saveMenu.addAction(self.saveMD)

        self.saveGH = QAction(self.tr("GitHub Markdown (.md)"), self)
        self.saveGH.triggered.connect(lambda: self._saveDocument(self.FMT_GH))
        self.saveMenu.addAction(self.saveGH)

        self.saveJsonH = QAction(self.tr("JSON + novelWriter HTML (.json)"), self)
        self.saveJsonH.triggered.connect(lambda: self._saveDocument(self.FMT_JSON_H))
        self.saveMenu.addAction(self.saveJsonH)

        self.saveJsonM = QAction(self.tr("JSON + novelWriter Markdown (.json)"), self)
        self.saveJsonM.triggered.connect(lambda: self._saveDocument(self.FMT_JSON_M))
        self.saveMenu.addAction(self.saveJsonM)

        self.btnClose = QPushButton(self.tr("Close"))
        self.btnClose.clicked.connect(self._doClose)

        self.buttonBox.addWidget(self.btnSave)
        self.buttonBox.addWidget(self.btnPrint)
        self.buttonBox.addWidget(self.btnClose)
        self.buttonBox.setSpacing(self.mainConf.pxInt(4))

        # Assemble GUI
        # ============

        # Splitter Position
        boxWidth = self.mainConf.pxInt(350)
        boxWidth = pOptions.getInt("GuiBuildNovel", "boxWidth", boxWidth)
        docWidth = max(self.width() - boxWidth, 100)
        docWidth = pOptions.getInt("GuiBuildNovel", "docWidth", docWidth)

        # The Tool Box
        self.toolsBox = QVBoxLayout()
        self.toolsBox.addWidget(self.titleGroup)
        self.toolsBox.addWidget(self.fontGroup)
        self.toolsBox.addWidget(self.styleGroup)
        self.toolsBox.addWidget(self.textGroup)
        self.toolsBox.addWidget(self.rootGroup)
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
            textFont = self.textFont.text()
            textSize = self.textSize.value()
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
                    self.tr("Failed to generate preview. The result is too big.")
                )

        else:
            self.htmlText = []
            self.htmlStyle = []
            self.buildTime = 0
            return False

        return True

    ##
    #  Slots and Related
    ##

    def _buildPreview(self):
        """Build a preview of the project in the document viewer.
        """
        # Get Settings
        justifyText = self.justifyText.isChecked()
        noStyling = self.noStyling.isChecked()
        textFont = self.textFont.text()
        textSize = self.textSize.value()
        replaceTabs = self.replaceTabs.isChecked()

        self.htmlText = []
        self.htmlStyle = []
        self.htmlSize = 0

        # Build Preview
        # =============

        makeHtml = ToHtml(self.theProject)
        self._doBuild(makeHtml, isPreview=True)
        if replaceTabs:
            makeHtml.replaceTabs()

        self.htmlText  = makeHtml.fullHTML
        self.htmlStyle = makeHtml.getStyleSheet()
        self.htmlSize  = makeHtml.getFullResultSize()
        self.buildTime = int(time())

        # Load Preview
        # ============

        self.docView.setTextFont(textFont, textSize)
        self.docView.setJustify(justifyText)
        if noStyling:
            self.docView.clearStyleSheet()
        else:
            self.docView.setStyleSheet(self.htmlStyle)

        if self.htmlSize < nwConst.MAX_BUILDSIZE:
            self.docView.setContent(self.htmlText, self.buildTime)
        else:
            self.docView.setText(
                "Failed to generate preview. The result is too big."
            )

        self._saveCache()

        return

    def _doBuild(self, bldObj, isPreview=False, doConvert=True):
        """Rund the build with a specific build object.
        """
        tStart = int(time())

        # Get Settings
        fmtTitle      = self.fmtTitle.text()
        fmtChapter    = self.fmtChapter.text()
        fmtUnnumbered = self.fmtUnnumbered.text()
        fmtScene      = self.fmtScene.text()
        fmtSection    = self.fmtSection.text()
        buildLang     = self.buildLang.currentData()
        hideScene     = self.hideScene.isChecked()
        hideSection   = self.hideSection.isChecked()
        textFont      = self.textFont.text()
        textSize      = self.textSize.value()
        lineHeight    = self.lineHeight.value()
        justifyText   = self.justifyText.isChecked()
        noStyling     = self.noStyling.isChecked()
        incSynopsis   = self.includeSynopsis.isChecked()
        incComments   = self.includeComments.isChecked()
        incKeywords   = self.includeKeywords.isChecked()
        novelFiles    = self.novelFiles.isChecked()
        noteFiles     = self.noteFiles.isChecked()
        ignoreFlag    = self.ignoreFlag.isChecked()
        includeBody   = self.includeBody.isChecked()
        replaceUCode  = self.replaceUCode.isChecked()

        # The language lookup dict is reloaded if needed
        self.theProject.setProjectLang(buildLang)

        # Get font information
        fontInfo = QFontInfo(QFont(textFont, textSize))
        textFixed = fontInfo.fixedPitch()

        isHtml = isinstance(bldObj, ToHtml)
        isOdt = isinstance(bldObj, ToOdt)

        bldObj.setTitleFormat(fmtTitle)
        bldObj.setChapterFormat(fmtChapter)
        bldObj.setUnNumberedFormat(fmtUnnumbered)
        bldObj.setSceneFormat(fmtScene, hideScene)
        bldObj.setSectionFormat(fmtSection, hideSection)

        bldObj.setFont(textFont, textSize, textFixed)
        bldObj.setJustify(justifyText)
        bldObj.setLineHeight(lineHeight)

        bldObj.setSynopsis(incSynopsis)
        bldObj.setComments(incComments)
        bldObj.setKeywords(incKeywords)
        bldObj.setBodyText(includeBody)

        if isHtml:
            bldObj.setStyles(not noStyling)
            bldObj.setReplaceUnicode(replaceUCode)

        if isOdt:
            bldObj.setColourHeaders(not noStyling)
            bldObj.setLanguage(buildLang)
            bldObj.initDocument()

        # Make sure the project and document is up to date
        self.mainGui.saveDocument()

        self.buildProgress.setMaximum(len(self.theProject.tree))
        self.buildProgress.setValue(0)

        rootFilter = set(self._generateRootFilter())
        for nItt, tItem in enumerate(self.theProject.tree):

            noteRoot = noteFiles
            noteRoot &= tItem.itemType == nwItemType.ROOT
            noteRoot &= tItem.itemClass != nwItemClass.NOVEL
            noteRoot &= tItem.itemClass != nwItemClass.ARCHIVE

            try:
                if noteRoot:
                    # Add headers for root folders of notes
                    bldObj.addRootHeading(tItem.itemHandle)
                    if doConvert:
                        bldObj.doConvert()

                elif self._checkInclude(tItem, noteFiles, novelFiles, ignoreFlag, rootFilter):
                    bldObj.setText(tItem.itemHandle)
                    bldObj.doPreProcessing()
                    bldObj.tokenizeText()
                    bldObj.doHeaders()
                    if doConvert:
                        bldObj.doConvert()
                    bldObj.doPostProcessing()

            except Exception:
                logger.error("Failed to build document '%s'", tItem.itemHandle)
                logException()
                if isPreview:
                    self.docView.setText((
                        "Failed to generate preview. "
                        "Document with title '%s' could not be parsed."
                    ) % tItem.itemName)

                return False

            # Update progress bar, also for skipped items
            self.buildProgress.setValue(nItt+1)

        if isOdt:
            bldObj.closeDocument()

        tEnd = int(time())
        logger.debug("Built project in %.3f ms", 1000*(tEnd - tStart))

        if bldObj.errData:
            self.mainGui.makeAlert([
                self.tr("There were problems when building the project:")
            ] + bldObj.errData, nwAlert.ERROR)

        return

    def _checkInclude(self, theItem, noteFiles, novelFiles, ignoreFlag, rootFilter):
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

        if not (theItem.isActive or ignoreFlag):
            return False

        if theItem.itemRoot in rootFilter:
            return False

        isNone  = not theItem.isFileType()
        isNone |= theItem.itemLayout == nwItemLayout.NO_LAYOUT
        isNone |= theItem.isInactive()
        isNone |= theItem.itemParent is None
        isNote  = theItem.isNoteLayout()
        isNovel = not isNone and not isNote

        if isNone:
            return False
        if isNote and not noteFiles:
            return False
        if isNovel and not novelFiles:
            return False

        return True

    def _saveDocument(self, theFmt):
        """Save the document to various formats.
        """
        replaceTabs = self.replaceTabs.isChecked()

        fileExt = ""
        textFmt = ""

        # Settings
        # ========

        if theFmt == self.FMT_ODT:
            fileExt = "odt"
            textFmt = self.tr("Open Document")

        elif theFmt == self.FMT_FODT:
            fileExt = "fodt"
            textFmt = self.tr("Flat Open Document")

        elif theFmt == self.FMT_HTM:
            fileExt = "htm"
            textFmt = self.tr("Plain HTML")

        elif theFmt == self.FMT_NWD:
            fileExt = "nwd"
            textFmt = self.tr("novelWriter Markdown")

        elif theFmt == self.FMT_MD:
            fileExt = "md"
            textFmt = self.tr("Standard Markdown")

        elif theFmt == self.FMT_GH:
            fileExt = "md"
            textFmt = self.tr("GitHub Markdown")

        elif theFmt == self.FMT_JSON_H:
            fileExt = "json"
            textFmt = self.tr("JSON + novelWriter HTML")

        elif theFmt == self.FMT_JSON_M:
            fileExt = "json"
            textFmt = self.tr("JSON + novelWriter Markdown")

        elif theFmt == self.FMT_PDF:
            fileExt = "pdf"
            textFmt = self.tr("PDF")

        else:
            return False

        # Generate File Name
        # ==================

        cleanName = makeFileNameSafe(self.theProject.data.name)
        fileName = "%s.%s" % (cleanName, fileExt)
        savePath = self.mainConf.lastPath() / fileName
        savePath, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save Document As"), str(savePath)
        )
        if not savePath:
            return False

        self.mainConf.setLastPath(savePath)

        # Build and Write
        # ===============

        errMsg = ""
        wSuccess = False

        if theFmt == self.FMT_ODT:
            makeOdt = ToOdt(self.theProject, isFlat=False)
            self._doBuild(makeOdt)
            try:
                makeOdt.saveOpenDocText(savePath)
                wSuccess = True
            except Exception as exc:
                errMsg = formatException(exc)

        elif theFmt == self.FMT_FODT:
            makeOdt = ToOdt(self.theProject, isFlat=True)
            self._doBuild(makeOdt)
            try:
                makeOdt.saveFlatXML(savePath)
                wSuccess = True
            except Exception as exc:
                errMsg = formatException(exc)

        elif theFmt == self.FMT_HTM:
            makeHtml = ToHtml(self.theProject)
            self._doBuild(makeHtml)
            if replaceTabs:
                makeHtml.replaceTabs()

            try:
                makeHtml.saveHTML5(savePath)
                wSuccess = True
            except Exception as exc:
                errMsg = formatException(exc)

        elif theFmt == self.FMT_NWD:
            makeNwd = ToMarkdown(self.theProject)
            makeNwd.setKeepMarkdown(True)
            self._doBuild(makeNwd, doConvert=False)
            if replaceTabs:
                makeNwd.replaceTabs(spaceChar=" ")

            try:
                makeNwd.saveRawMarkdown(savePath)
                wSuccess = True
            except Exception as exc:
                errMsg = formatException(exc)

        elif theFmt in (self.FMT_MD, self.FMT_GH):
            makeMd = ToMarkdown(self.theProject)
            if theFmt == self.FMT_GH:
                makeMd.setGitHubMarkdown()
            else:
                makeMd.setStandardMarkdown()

            self._doBuild(makeMd)
            if replaceTabs:
                makeMd.replaceTabs(nSpaces=4, spaceChar=" ")

            try:
                makeMd.saveMarkdown(savePath)
                wSuccess = True
            except Exception as exc:
                errMsg = formatException(exc)

        elif theFmt == self.FMT_JSON_H or theFmt == self.FMT_JSON_M:
            jsonData = {
                "meta": {
                    "projectName": self.theProject.data.name,
                    "novelTitle": self.theProject.data.title,
                    "novelAuthor": self.theProject.data.author,
                    "buildTime": self.buildTime,
                }
            }

            if theFmt == self.FMT_JSON_H:
                makeHtml = ToHtml(self.theProject)
                self._doBuild(makeHtml)
                if replaceTabs:
                    makeHtml.replaceTabs()

                theBody = []
                for htmlPage in makeHtml.fullHTML:
                    theBody.append(htmlPage.rstrip("\n").split("\n"))
                jsonData["text"] = {
                    "css": self.htmlStyle,
                    "html": theBody,
                }

            elif theFmt == self.FMT_JSON_M:
                makeMd = ToHtml(self.theProject)
                makeMd.setKeepMarkdown(True)
                self._doBuild(makeMd, doConvert=False)
                if replaceTabs:
                    makeMd.replaceTabs(spaceChar=" ")

                theBody = []
                for nwdPage in makeMd.theMarkdown:
                    theBody.append(nwdPage.split("\n"))
                jsonData["text"] = {
                    "nwd": theBody,
                }

            try:
                with open(savePath, mode="w", encoding="utf-8") as outFile:
                    outFile.write(json.dumps(jsonData, indent=2))
                    wSuccess = True
            except Exception as exc:
                errMsg = formatException(exc)

        elif theFmt == self.FMT_PDF:
            try:
                thePrinter = QPrinter()
                thePrinter.setOutputFormat(QPrinter.PdfFormat)
                thePrinter.setOrientation(QPrinter.Portrait)
                thePrinter.setDuplex(QPrinter.DuplexLongSide)
                thePrinter.setFontEmbeddingEnabled(True)
                thePrinter.setColorMode(QPrinter.Color)
                thePrinter.setOutputFileName(savePath)
                self.docView.document().print(thePrinter)
                wSuccess = True

            except Exception as exc:
                errMsg = formatException(exc)

        else:
            # If the if statements above and here match, it should not
            # be possible to reach this else statement.
            return False  # pragma: no cover

        # Report to User
        # ==============

        if wSuccess:
            self.mainGui.makeAlert([
                self.tr("{0} file successfully written to:").format(textFmt), savePath
            ], nwAlert.INFO)
        else:
            self.mainGui.makeAlert(self.tr(
                "Failed to write {0} file. {1}"
            ).format(textFmt, errMsg), nwAlert.ERROR)

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
        self.docView.document().print(thePrinter)
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

        self.raise_()  # Move the dialog to front (fixes a bug on macOS)

        return

    def _generateRootFilter(self):
        """Return a list of all root folders that are filtered out.
        """
        return [h for h, s in self.rootSelection.items() if not s.isChecked()]

    def _loadCache(self):
        """Save the current data to cache.
        """
        buildCache = self.theProject.storage.getCacheFile(nwFiles.BUILD_CACHE)
        if not isinstance(buildCache, Path):
            return False

        dataCount = 0
        if buildCache.exists():
            logger.debug("Loading build cache")
            try:
                with open(buildCache, mode="r", encoding="utf-8") as inFile:
                    theJson = inFile.read()
                theData = json.loads(theJson)
            except Exception:
                logger.error("Failed to load build cache")
                logException()
                return False

            if "buildTime" in theData.keys():
                self.buildTime = theData["buildTime"]
            if "htmlStyle" in theData.keys():
                self.htmlStyle = theData["htmlStyle"]
                dataCount += 1
            if "htmlText" in theData.keys():
                self.htmlText = theData["htmlText"]
                dataCount += 1

        return dataCount == 2

    def _saveCache(self):
        """Save the current data to cache.
        """
        buildCache = self.theProject.storage.getCacheFile(nwFiles.BUILD_CACHE)
        if not isinstance(buildCache, Path):
            return False

        logger.debug("Saving build cache")
        try:
            with open(buildCache, mode="w+", encoding="utf-8") as outFile:
                outFile.write(json.dumps({
                    "buildTime": self.buildTime,
                    "htmlStyle": self.htmlStyle,
                    "htmlText": self.htmlText,
                }, indent=2))
        except Exception:
            logger.error("Failed to save build cache")
            logException()
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

    def _saveSettings(self):
        """Save the various user settings.
        """
        logger.debug("Saving GuiBuildNovel settings")

        # Formatting
        self.theProject.data.setTitleFormat({
            "title":      self.fmtTitle.text().strip(),
            "chapter":    self.fmtChapter.text().strip(),
            "unnumbered": self.fmtUnnumbered.text().strip(),
            "scene":      self.fmtScene.text().strip(),
            "section":    self.fmtSection.text().strip(),
        })

        buildLang    = self.buildLang.currentData()
        hideScene    = self.hideScene.isChecked()
        hideSection  = self.hideSection.isChecked()
        winWidth     = self.mainConf.rpxInt(self.width())
        winHeight    = self.mainConf.rpxInt(self.height())
        justifyText  = self.justifyText.isChecked()
        noStyling    = self.noStyling.isChecked()
        textFont     = self.textFont.text()
        textSize     = self.textSize.value()
        lineHeight   = self.lineHeight.value()
        novelFiles   = self.novelFiles.isChecked()
        noteFiles    = self.noteFiles.isChecked()
        ignoreFlag   = self.ignoreFlag.isChecked()
        incSynopsis  = self.includeSynopsis.isChecked()
        incComments  = self.includeComments.isChecked()
        incKeywords  = self.includeKeywords.isChecked()
        incBodyText  = self.includeBody.isChecked()
        replaceTabs  = self.replaceTabs.isChecked()
        replaceUCode = self.replaceUCode.isChecked()
        rootFilter   = self._generateRootFilter()

        mainSplit = self.mainSplit.sizes()
        boxWidth  = self.mainConf.rpxInt(mainSplit[0])
        docWidth  = self.mainConf.rpxInt(mainSplit[1])

        self.theProject.setProjectLang(buildLang)

        # GUI Settings
        pOptions = self.theProject.options
        pOptions.setValue("GuiBuildNovel", "hideScene",    hideScene)
        pOptions.setValue("GuiBuildNovel", "hideSection",  hideSection)
        pOptions.setValue("GuiBuildNovel", "winWidth",     winWidth)
        pOptions.setValue("GuiBuildNovel", "winHeight",    winHeight)
        pOptions.setValue("GuiBuildNovel", "boxWidth",     boxWidth)
        pOptions.setValue("GuiBuildNovel", "docWidth",     docWidth)
        pOptions.setValue("GuiBuildNovel", "justifyText",  justifyText)
        pOptions.setValue("GuiBuildNovel", "noStyling",    noStyling)
        pOptions.setValue("GuiBuildNovel", "textFont",     textFont)
        pOptions.setValue("GuiBuildNovel", "textSize",     textSize)
        pOptions.setValue("GuiBuildNovel", "lineHeight",   lineHeight)
        pOptions.setValue("GuiBuildNovel", "addNovel",     novelFiles)
        pOptions.setValue("GuiBuildNovel", "addNotes",     noteFiles)
        pOptions.setValue("GuiBuildNovel", "ignoreFlag",   ignoreFlag)
        pOptions.setValue("GuiBuildNovel", "incSynopsis",  incSynopsis)
        pOptions.setValue("GuiBuildNovel", "incComments",  incComments)
        pOptions.setValue("GuiBuildNovel", "incKeywords",  incKeywords)
        pOptions.setValue("GuiBuildNovel", "incBodyText",  incBodyText)
        pOptions.setValue("GuiBuildNovel", "replaceTabs",  replaceTabs)
        pOptions.setValue("GuiBuildNovel", "replaceUCode", replaceUCode)
        pOptions.setValue("GuiBuildNovel", "rootFilter",   rootFilter)
        pOptions.saveSettings()

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

    def __init__(self, mainGui, theProject):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiBuildNovelDocView ...")

        self.mainConf   = novelwriter.CONFIG
        self.theProject = theProject
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.buildTime  = 0

        self.setMinimumWidth(40*self.mainGui.mainTheme.textNWidth)
        self.setOpenExternalLinks(False)

        self.document().setDocumentMargin(self.mainConf.getTextMargin())
        self.setPlaceholderText(self.tr(
            "This area will show the content of the document to be "
            "exported or printed. Press the \"Build Preview\" button "
            "to generate content."
        ))

        theFont = QFont()
        if self.mainConf.textFont is None:
            # If none is defined, set the default back to config
            self.mainConf.textFont = self.document().defaultFont().family()
        theFont.setFamily(self.mainConf.textFont)
        theFont.setPointSize(self.mainConf.textSize)
        self.setFont(theFont)

        # Set the tab stops
        self.setTabStopDistance(self.mainConf.getTabWidth())

        docPalette = self.palette()
        docPalette.setColor(QPalette.Base, QColor(255, 255, 255))
        docPalette.setColor(QPalette.Text, QColor(0, 0, 0))
        self.setPalette(docPalette)

        lblPalette = self.palette()
        lblPalette.setColor(QPalette.Background, lblPalette.toolTipBase().color())
        lblPalette.setColor(QPalette.Foreground, lblPalette.toolTipText().color())

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*self.mainTheme.fontPointSize)

        fPx = int(1.1*self.mainTheme.fontPixelSize)

        self.theTitle = QLabel("", self)
        self.theTitle.setIndent(0)
        self.theTitle.setAutoFillBackground(True)
        self.theTitle.setAlignment(Qt.AlignCenter)
        self.theTitle.setFixedHeight(fPx)
        self.theTitle.setPalette(lblPalette)
        self.theTitle.setFont(lblFont)

        self._updateDocMargins()
        self._updateBuildAge()
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
        theOpt = self.document().defaultTextOption()
        if doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        else:
            theOpt.setAlignment(Qt.AlignAbsolute)
        self.document().setDefaultTextOption(theOpt)
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
        self.document().markContentsDirty(0, self.document().characterCount())
        qApp.restoreOverrideCursor()

        return

    def setStyleSheet(self, theStyles=None):
        """Set the stylesheet for the preview document.
        """
        if theStyles is None:
            theStyles = []

        if not theStyles:
            theStyles.append("h1, h2 {color: rgb(66, 113, 174);}")
            theStyles.append("h3, h4 {color: rgb(50, 50, 50);}")
            theStyles.append("a {color: rgb(66, 113, 174);}")
            theStyles.append(".tags {color: rgb(245, 135, 31); font-weight: bold;}")

        self.document().setDefaultStyleSheet("\n".join(theStyles))

        return

    def clearStyleSheet(self):
        """Clears the document stylesheet.
        """
        self.document().setDefaultStyleSheet("")
        return

    ##
    #  Events
    ##

    def resizeEvent(self, theEvent):
        """Make sure the document title is the same width as the window.
        """
        super().resizeEvent(theEvent)
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
            strBuildTime = self.tr("Unknown")

        self.theTitle.setText("%s %s" % (self.tr("Build Time:"), strBuildTime))

        return

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
