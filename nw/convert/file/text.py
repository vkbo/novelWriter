# -*- coding: utf-8 -*-
"""novelWriter Text File

 novelWriter – Text File
=========================
 Writes the project to a plain text file

 File History:
 Created: 2019-10-18 [0.2.3]

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

from PyQt5.QtWidgets import QMessageBox

from nw.convert.text.totext import ToText
from nw.constants import nwAlert, nwItemType, nwItemLayout, nwItemClass

logger = logging.getLogger(__name__)

class TextFile():

    def __init__(self, theProject, theParent):

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.outFile  = None
        self.fileName = ""
        self.theText  = ""
        self.expNovel = True
        self.expNotes = False

        self.theConv   = ToText(self.theProject, self.theParent)
        self.makeAlert = self.theParent.makeAlert

        self.setComments(False)
        self.setKeywords(False)
        self.setWordWrap(80)

        return

    ##
    #  Setters
    ##

    def setExportNovel(self, doNovel):
        self.expNovel = doNovel
        return

    def setExportNotes(self, doNotes):
        self.expNotes = doNotes
        return

    def setComments(self, doComments):
        self.theConv.setComments(doComments)
        return

    def setKeywords(self, doKeywords):
        self.theConv.setKeywords(doKeywords)
        return

    def setWordWrap(self, wordWrap):
        if wordWrap >= 0:
            self.theConv.setWordWrap(wordWrap)
        else:
            self.theConv.setWordWrap(0)
        return

    def setTitleFormat(self, fmtTitle):
        self.theConv.setTitleFormat(fmtTitle)
        return

    def setChapterFormat(self, fmtChapter):
        self.theConv.setChapterFormat(fmtChapter)
        return

    def setUnNumberedFormat(self, fmtUnNum):
        self.theConv.setUnNumberedFormat(fmtUnNum)
        return

    def setSceneFormat(self, fmtScene, hideScene):
        self.theConv.setSceneFormat(fmtScene, hideScene)
        return

    def setSectionFormat(self, fmtSection, hideSection):
        self.theConv.setSectionFormat(fmtSection, hideSection)
        return

    ##
    #  Core Methods
    ##

    def openFile(self, filePath):

        self.fileName = path.basename(filePath)
        if path.isfile(filePath) and self.mainConf.showGUI:
            msgBox = QMessageBox()
            msgRes = msgBox.question(self.theParent, "Overwrite", (
                "File '%s' already exists.<br>Do you want to overwrite it?" % self.fileName
            ))
            if msgRes != QMessageBox.Yes:
                return False

        self._doOpenFile(filePath)

        if self.outFile is None:
            return False

        return True

    def closeFile(self):
        self._doCloseFile()
        return True

    def addText(self, tHandle):

        logger.verbose("Parsing content of item '%s'" % tHandle)
        
        if not self.checkInclude(tHandle):
            return False

        self.theConv.setText(tHandle)
        self.theConv.doAutoReplace()
        self.theConv.tokenizeText()
        self.theConv.doHeaders()
        self.theConv.doConvert()
        self.theConv.doPostProcessing()

        if self.theConv.theResult is not None and self.outFile is not None:
            self.outFile.write(self.theConv.theResult)

        return True

    def checkInclude(self, tHandle):
        """This function checks whether a file should be included in the
        export or not. For standard note and novel files, this is
        controlled by the options selected by the user. For other files
        classified as non-exportable, a few checks must be made, and the
        following are not:
        * Items that are not actual files.
        * Items that have been orphaned which are tagged as NO_LAYOUT
          and NO_CLASS.
        * Items that appear in the TRASH folder
        """

        theItem = self.theProject.projTree[tHandle]
        isNone  = theItem.itemType != nwItemType.FILE
        isNone |= theItem.itemLayout == nwItemLayout.NO_LAYOUT
        isNone |= theItem.itemClass == nwItemClass.NO_CLASS
        isNone |= theItem.itemClass == nwItemClass.TRASH
        isNone |= theItem.parHandle == self.theProject.projTree.trashRoot()
        isNote  = theItem.itemLayout == nwItemLayout.NOTE
        isNovel = not isNone and not isNote

        if isNone:
            return False
        if isNote and not self.expNotes:
            return False
        if isNovel and not self.expNovel:
            return False

        return True

    ##
    #  Internal Functions
    ##

    def _doOpenFile(self, filePath):
        """This function does the actual opening of the file, and can be
        overloaded by a subclass that uses a different file format that
        requires a different approach.
        """
        try:
            self.outFile = open(filePath,mode="wt+",encoding="utf8")
            self.outFile.write("\n\n")
        except Exception as e:
            self.makeAlert(["Failed to open file.",str(e)], nwAlert.ERROR)
            return False
        return True

    def _doCloseFile(self):
        """This function closes the file, and is meant to be overloaded
        by the subclass for other file formats.
        """
        if self.outFile is not None:
            self.outFile.close()
        return True

# END Class OutFile
