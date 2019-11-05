# -*- coding: utf-8 -*-
"""novelWriter LaTeX File

 novelWriter – LaTeX File
==========================
 Writes the project to a LaTeX file

 File History:
 Created: 2019-10-24 [0.3.1]

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
