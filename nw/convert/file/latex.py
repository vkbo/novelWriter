# -*- coding: utf-8 -*-
"""novelWriter LaTeX File

 novelWriter – LaTeX File
==========================
 Writes the project to a LaTeX file

 File History:
 Created: 2019-10-24 [0.3.1]

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

from nw.convert.file.text import TextFile
from nw.convert.text.tolatex import ToLaTeX
from nw.constants import nwAlert

logger = logging.getLogger(__name__)

class LaTeXFile(TextFile):

    def __init__(self, theProject, theParent):
        TextFile.__init__(self, theProject, theParent)
        self.theConv = ToLaTeX(self.theProject, self.theParent)
        self.texCodecFail = False
        return

    ##
    #  Internal Functions
    ##

    def _doOpenFile(self, filePath):
        try:
            self.outFile = open(filePath,mode="wt+",encoding="utf8")
            self.outFile.write("\\documentclass[12pt]{report}\n")
            self.outFile.write("\\usepackage[utf8]{inputenc}\n")
            self.outFile.write("\\usepackage[T1]{fontenc}\n")
            self.outFile.write("\n")
            self.outFile.write("\\begin{document}\n")
        except Exception as e:
            self.makeAlert(["Failed to open file.",str(e)], nwAlert.ERROR)
            return False
        return True

    def _doCloseFile(self):
        if self.outFile is not None:
            self.outFile.write("\\end{document}\n")
            self.outFile.close()
        self.texCodecFail = self.theConv.texCodecFail
        return True

# END Class LaTeXFile
