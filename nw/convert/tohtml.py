# -*- coding: utf-8 -*-
"""novelWriter HTML Text Converter

 novelWriter – HTML Text Converter
===================================
 Extends the Tokenizer class to write HTML

 File History:
 Created: 2019-05-07 [0.0.1]

"""

import logging
import nw

from nw.convert.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

class ToHtml(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)

        return

    def doConvert(self):

        htmlTags = {
            self.FMT_B_B : "<strong>",
            self.FMT_B_E : "</strong>",
            self.FMT_I_B : "<em>",
            self.FMT_I_E : "</em>",
            self.FMT_U_B : "<mark>",
            self.FMT_U_E : "</mark>",
        }

        self.theResult = ""
        thisPar = []
        for tType, tText, tFormat in self.theTokens:

            if tType == "empty":
                if len(thisPar) > 0:
                    self.theResult += "<p>%s</p>\n" % " ".join(thisPar)
                thisPar = []
            elif tType == "header1":
                self.theResult += "<h1>%s</h1>\n" % tText
            elif tType == "header2":
                self.theResult += "<h2>%s</h2>\n" % tText
            elif tType == "header3":
                self.theResult += "<h3>%s</h3>\n" % tText
            elif tType == "header4":
                self.theResult += "<h4>%s</h4>\n" % tText
            elif tType == "text":
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+htmlTags[xFmt]+tTemp[xPos+xLen:]
                thisPar.append(tTemp)

        print(self.theResult)

        return

# END Class ToHtml
