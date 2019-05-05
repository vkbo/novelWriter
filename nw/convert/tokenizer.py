# -*- coding: utf-8 -*-
"""novelWriter Text Tokenizer

 novelWriter – Text Tokenizer
==============================
 Splits a piece of nW markdown text into its elements

 File History:
 Created: 2019-05-05 [0.0.1]

"""

import logging
import nw

from nw.project.document import NWDoc

logger = logging.getLogger(__name__)

class Tokenizer():

    def __init__(self, theProject, theParent):

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.theHandle  = None
        self.theItem    = None
        self.theTokens  = None

        return

    def tokenizeText(self, tHandle):

        self.theItem = self.theProject.getItem(tHandle)
        theDoc  = NWDoc(self.theProject, self.theParent)
        theText = theDoc.openDocument(tHandle)

        for aLine in theText.splitlines():
            print(aLine)

        return

# END Class Tokenizer
