# -*- coding: utf-8 -*-
"""novelWriter Concatenated File

 novelWriter – Concatenated File
=================================
 Concatenate the standard novelWriter files to a single file

 File History:
 Created: 2019-10-26 [0.3.1]

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
