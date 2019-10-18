# -*- coding: utf-8 -*-
"""novelWriter HTML Text Converter

 novelWriter – HTML Text Converter
===================================
 Extends the Tokenizer class to write HTML

 File History:
 Created: 2019-05-07 [0.0.1]

"""

import logging
import re
import nw

from nw.convert.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

class ToHtml(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)

        return

    def doAutoReplace(self):
        Tokenizer.doAutoReplace(self)

        repDict = {
            "<" : "&lt;",
            ">" : "&gt;",
            "&" : "&amp;",
        }
        xRep = re.compile("|".join([re.escape(k) for k in repDict.keys()]), flags=re.DOTALL)
        self.theText = xRep.sub(lambda x: repDict[x.group(0)], self.theText)

        return

    def doConvert(self):

        htmlTags = {
            self.FMT_B_B : "<strong>",
            self.FMT_B_E : "</strong>",
            self.FMT_I_B : "<em>",
            self.FMT_I_E : "</em>",
            self.FMT_U_B : "<u>",
            self.FMT_U_E : "</u>",
        }

        self.theResult = ""
        thisPar = []
        for tType, tText, tFormat, tAlign in self.theTokens:

            if tType == self.T_EMPTY:
                if len(thisPar) > 0:
                    self.theResult += "<p>%s</p>\n" % " ".join(thisPar)
                thisPar = []
            elif tType == self.T_HEAD1:
                self.theResult += "<h1>%s</h1>\n" % tText
            elif tType == self.T_HEAD2:
                self.theResult += "<h2>%s</h2>\n" % tText
            elif tType == self.T_HEAD3:
                self.theResult += "<h3>%s</h3>\n" % tText
            elif tType == self.T_HEAD4:
                self.theResult += "<h4>%s</h4>\n" % tText
            elif tType == self.T_TEXT:
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+htmlTags[xFmt]+tTemp[xPos+xLen:]
                thisPar.append(tTemp)

        # print(self.theResult)

        return

# END Class ToHtml
