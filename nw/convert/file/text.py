# -*- coding: utf-8 -*-
"""novelWriter Text File

 novelWriter – Text File
=========================
 Writes the project to a plain text file

 File History:
 Created: 2019-10-18 [0.2.3]

"""

import logging
import nw

from os              import path
from PyQt5.QtWidgets import QMessageBox

from nw.convert.text.totext import ToText
from nw.enum                import nwAlert, nwItemLayout

logger = logging.getLogger(__name__)

class TextFile():

    def __init__(self, theProject, theParent):

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.outFile    = None
        self.fileName   = ""
        self.theText    = ""
        self.expNovel   = True
        self.expNotes   = False

        self.theConv    = ToText(self.theProject, self.theParent)
        self.makeAlert  = self.theParent.makeAlert

        self.setComments(False)
        self.setMeta(False)
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

    def setMeta(self, doMeta):
        self.theConv.setCommands(doMeta)
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

    def setSceneFormat(self, fmtScene):
        self.theConv.setSceneFormat(fmtScene)
        return

    def setSectionFormat(self, fmtSection):
        self.theConv.setSectionFormat(fmtSection)
        return

    ##
    #  Core Methods
    ##

    def openFile(self, filePath):

        self.fileName = path.basename(filePath)
        if path.isfile(filePath) and self.mainConf.showGUI:
            msgBox = QMessageBox()
            msgRes = msgBox.question(
                self.theParent, "Overwrite", ("File '%s' already exists.<br>Do you want to overwrite it?" % self.fileName)
            )
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

        theItem = self.theProject.getItem(tHandle)
        isNone  = theItem.itemLayout == nwItemLayout.NO_LAYOUT
        isNote  = theItem.itemLayout == nwItemLayout.NOTE
        isNovel = not isNone and not isNote

        if isNone:
            return False
        if isNote and not self.expNotes:
            return False
        if isNovel and not self.expNovel:
            return False

        self.theConv.setText(tHandle)
        self.theConv.doAutoReplace()
        self.theConv.tokenizeText()
        self.theConv.doHeaders()
        self.theConv.doConvert()

        if self.theConv.theResult is not None and self.outFile is not None:
            self.outFile.write(self.theConv.theResult)

        return True

    ##
    #  Internal Functions
    ##

    def _doOpenFile(self, filePath):
        """This function does the actual opening of the file, and can be overloaded by a subclass
        that uses a different file format that requires a different approach.
        """
        try:
            self.outFile = open(filePath,mode="wt+",encoding="utf8")
            self.outFile.write("\n\n")
        except Exception as e:
            self.makeAlert(["Failed to open file.",str(e)], nwAlert.ERROR)
            return False
        return True

    def _doCloseFile(self):
        """This function closes the file, and is meant to be overloaded by the subclass for other
        file formats.
        """
        if self.outFile is not None:
            self.outFile.close()
        return True

# END Class OutFile
