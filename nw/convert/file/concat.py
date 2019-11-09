# -*- coding: utf-8 -*-
"""novelWriter Concatenated File

 novelWriter – Concatenated File
=================================
 Concatenate the standard novelWriter files to a single file

 File History:
 Created: 2019-10-26 [0.3.1]

"""

import logging
import nw

from os import path

from nw.convert.file.text import TextFile
from nw.convert.tokenizer import Tokenizer
from nw.constants import nwAlert

logger = logging.getLogger(__name__)

class ConcatFile(TextFile):

    def __init__(self, theProject, theParent):
        TextFile.__init__(self, theProject, theParent)
        self.theConv = Tokenizer(self.theProject, self.theParent)
        return

    def addText(self, tHandle):

        logger.verbose("Parsing content of item '%s'" % tHandle)

        if not self.checkInclude(tHandle):
            return False

        self.theConv.setText(tHandle)

        theResult = self.theConv.theText

        if theResult is not None and self.outFile is not None:
            self.outFile.write(theResult.rstrip())
            self.outFile.write("\n\n")

        return True

    ##
    #  Internal Functions
    ##

    def _doOpenFile(self, filePath):
        try:
            self.outFile = open(filePath,mode="wt+",encoding="utf8")
        except Exception as e:
            self.makeAlert(["Failed to open file.",str(e)], nwAlert.ERROR)
            return False
        return True

    def _doCloseFile(self):
        if self.outFile is not None:
            self.outFile.close()
        return True

# END Class ConcatFile
