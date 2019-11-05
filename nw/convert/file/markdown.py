# -*- coding: utf-8 -*-
"""novelWriter Markdown File

 novelWriter – Markdown File
=============================
 Writes the project to a markdown file

 File History:
 Created: 2019-10-19 [0.3]

"""

import logging
import nw

from nw.convert.file.text import TextFile
from nw.convert.text.tomarkdown import ToMarkdown
from nw.constants import nwAlert

logger = logging.getLogger(__name__)

class MarkdownFile(TextFile):

    def __init__(self, theProject, theParent):
        TextFile.__init__(self, theProject, theParent)
        self.theConv = ToMarkdown(self.theProject, self.theParent)
        return

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

# END Class MarkdownFile
