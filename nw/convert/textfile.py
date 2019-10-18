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

from nw.convert.tokenizer import Tokenizer
from nw.enum              import nwAlert

logger = logging.getLogger(__name__)

class TextFile():

    def __init__(self, theProject, theParent):

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.fileExt    = "txt"

        self.outFile    = None
        self.fileName   = ""
        self.theText    = ""
        self.doComments = False
        self.doMeta     = False
        self.wordWrap   = 80
        self.winEnding  = False

        self.makeAlert = self.theParent.makeAlert

        return

    ##
    #  Setters
    ##

    def setComments(self, doComments):
        self.doComments = doComments
        return

    def setMeta(self, doMeta):
        self.doMeta = doMeta
        return

    ##
    #  Core Methods
    ##

    def openFile(self, saveTo, baseName):

        fileName = "%s.%s" % (baseName.strip(),self.fileExt)
        filePath = path.join(saveTo,fileName)

        self.fileName = fileName

        if path.isfile(filePath)and self.mainConf.showGUI:
            msgBox = QMessageBox()
            msgRes = msgBox.question(
                self.theParent, "Overwrite", ("File '%s' already exists.<br>Do you want to overwrite it?" % fileName)
            )
            if msgRes != QMessageBox.Yes:
                return False

        self._doOpenFile(filePath)

        return True

    def closeFile(self):
        self._doCloseFile()
        return True

    def addText(self, tHandle):

        logger.verbose("Parsing content of item '%s'" % tHandle)

        aDoc = Tokenizer(self.theProject, self.theParent)
        aDoc.setText(tHandle)
        aDoc.doAutoReplace()
        aDoc.tokenizeText()

        aDoc.setComments(self.doComments)
        aDoc.setCommands(self.doMeta)
        aDoc.setWordWrap(self.wordWrap)

        aDoc.doConvert()

        theText = ""
        if aDoc.theResult is not None:
            theText = aDoc.theResult

        if self.winEnding:
            theText = theText.replace("\n","\r\n")

        self.outFile.write(theText)

        return True

    ##
    #  Internal Functions
    ##

    def _doOpenFile(self, filePath):
        try:
            self.outFile = open(filePath,mode="w+")
        except Exception as e:
            self.makeAlert(["Failed to open file.",str(e)], nwAlert.ERROR)
            return False
        return True

    def _doCloseFile(self):
        self.outFile.close()
        return True

# END Class OutFile
