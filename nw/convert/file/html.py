# -*- coding: utf-8 -*-
"""novelWriter HTML File

 novelWriter – HTML File
=========================
 Writes the project to a html file

 File History:
 Created: 2019-10-19 [0.3]

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
from nw.convert.text.tohtml import ToHtml
from nw.constants import nwAlert

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
            self.outFile = open(filePath,mode="wt+",encoding="utf8")
            self.outFile.write("<!DOCTYPE html>\n")
            self.outFile.write("<html>\n")
            self.outFile.write("<head>\n")
            self.outFile.write("  <meta charset='utf-8'>\n")
            self.outFile.write("  <style>\n")
            self.outFile.write("    #page {\n")
            self.outFile.write("      margin: 40px auto;\n")
            self.outFile.write("      max-width: 769px;\n")
            self.outFile.write("    }\n")
            self.outFile.write("    .comment {\n")
            self.outFile.write("      background-color: #fbfabd;\n")
            self.outFile.write("      border: 1px solid #b4b000;\n")
            self.outFile.write("      margin: 10px 20px;\n")
            self.outFile.write("      padding: 6px;\n")
            self.outFile.write("    }\n")
            self.outFile.write("  </style>\n")
            self.outFile.write("</head>\n")
            self.outFile.write("<body>\n")
            self.outFile.write("<article id='page'>\n")
        except Exception as e:
            self.makeAlert(["Failed to open file.",str(e)], nwAlert.ERROR)
            return False
        return True

    def _doCloseFile(self):
        if self.outFile is not None:
            self.outFile.write("</article>\n")
            self.outFile.write("</body>\n")
            self.outFile.write("</html>\n")
            self.outFile.close()
        return True

# END Class HtmlFile
