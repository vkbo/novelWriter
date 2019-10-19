# -*- coding: utf-8 -*-
"""novelWriter HTML File

 novelWriter – HTML File
=========================
 Writes the project to a html file

 File History:
 Created: 2019-10-19 [0.3]

"""

import logging
import nw

from nw.convert.textfile import TextFile
from nw.convert.tohtml   import ToHtml

logger = logging.getLogger(__name__)

class HtmlFile(TextFile):

    def __init__(self, theProject, theParent):
        TextFile.__init__(self, theProject, theParent)

        self.theConv = ToHtml(self.theProject, self.theParent)

        return

    ##
    #  Internal Functions
    ##

    def _doOpenFile(self, filePath):
        try:
            self.outFile = open(filePath,mode="w+")
            self.outFile.write("<!DOCTYPE html>\n")
            self.outFile.write("<html>\n")
            self.outFile.write("<head>\n")
            self.outFile.write("<style>\n")
            self.outFile.write("  pre {background-color: #ffff99;}\n")
            self.outFile.write("</style>\n")
            self.outFile.write("</head>\n")
            self.outFile.write("<body>\n")
        except Exception as e:
            self.makeAlert(["Failed to open file.",str(e)], nwAlert.ERROR)
            return False
        return True

    def _doCloseFile(self):
        if self.outFile is not None:
            self.outFile.write("</body>\n")
            self.outFile.write("</html>\n")
            self.outFile.close()
        return True

# END Class HtmlFile
