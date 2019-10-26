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

from nw.convert.file.text    import TextFile
from nw.convert.text.tolatex import ToLaTeX
from nw.enum                 import nwAlert

logger = logging.getLogger(__name__)

class LaTeXFile(TextFile):

    def __init__(self, theProject, theParent):
        TextFile.__init__(self, theProject, theParent)

        self.theConv = ToLaTeX(self.theProject, self.theParent)

        return

    ##
    #  Internal Functions
    ##

    def _doOpenFile(self, filePath):

        if self.winEnding:
            tN = "\r\n"
        else:
            tN = "\n"

        try:
            self.outFile = open(filePath,mode="w+")
            self.outFile.write(r"\documentclass[12pt]{report}"+tN+tN)
            self.outFile.write(r"\usepackage[utf8]{inputenc}"+tN+tN)
            self.outFile.write(r"\begin{document}"+tN+tN)
        except Exception as e:
            self.makeAlert(["Failed to open file.",str(e)], nwAlert.ERROR)
            return False

        return True

    def _doCloseFile(self):

        if self.winEnding:
            tN = "\r\n"
        else:
            tN = "\n"

        if self.outFile is not None:
            self.outFile.write(r"\end{document}"+tN)
            self.outFile.close()

        return True

# END Class LaTeXFile
