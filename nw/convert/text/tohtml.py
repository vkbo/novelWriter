# -*- coding: utf-8 -*-
"""novelWriter HTML Text Converter

 novelWriter – HTML Text Converter
===================================
 Extends the Tokenizer class to write HTML

 File History:
 Created: 2019-05-07 [0.0.1]

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
import re
import nw

from nw.convert.tokenizer import Tokenizer
from nw.constants import nwUnicode, nwLabels

logger = logging.getLogger(__name__)

class ToHtml(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)
        self.forPreview = False
        return

    def setPreview(self, forPreview, doComments):
        """If we're using this class to generate markdown preview, we
        need to make a few changes to formatting, which is selected by
        this flag.
        """
        self.forPreview = forPreview
        if forPreview:
            self.doKeywords = True
            self.doComments = doComments
        return

    def doAutoReplace(self):
        Tokenizer.doAutoReplace(self)

        if self.forPreview:
            tabFmt = "&nbsp;"*8
        else:
            tabFmt = "&emsp;"

        repDict = {
            "<"  : "&lt;",
            ">"  : "&gt;",
            "&"  : "&amp;",
            "\t" : tabFmt,
            nwUnicode.U_ENDASH : nwUnicode.H_ENDASH,
            nwUnicode.U_EMDASH : nwUnicode.H_EMDASH,
            nwUnicode.U_HELLIP : nwUnicode.H_HELLIP,
            nwUnicode.U_NBSP   : nwUnicode.H_NBSP,
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

            aStyle = []
            if tAlign == self.A_CENTRE:
                aStyle.append("text-align: center;")

            if len(aStyle) > 0:
                hStyle = " style='%s'" % (" ".join(aStyle))
            else:
                hStyle = ""

            if tType == self.T_EMPTY:
                if len(thisPar) > 0:
                    tTemp = "".join(thisPar)
                    self.theResult += "<p%s>%s</p>\n" % (hStyle,tTemp.rstrip())
                thisPar = []

            elif tType == self.T_HEAD1:
                self.theResult += "<h1%s>%s</h1>\n" % (hStyle,tText)

            elif tType == self.T_HEAD2:
                self.theResult += "<h2%s>%s</h2>\n" % (hStyle,tText)

            elif tType == self.T_HEAD3:
                self.theResult += "<h3%s>%s</h3>\n" % (hStyle,tText)

            elif tType == self.T_HEAD4:
                self.theResult += "<h4%s>%s</h4>\n" % (hStyle,tText)

            elif tType == self.T_SEP:
                self.theResult += "<p%s>%s</p>\n" % (hStyle,tText)

            elif tType == self.T_SKIP:
                self.theResult += "<p>&nbsp;</p>\n"

            elif tType == self.T_TEXT:
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+htmlTags[xFmt]+tTemp[xPos+xLen:]
                if tText.endswith("  "):
                    thisPar.append(tTemp.rstrip()+"<br/>")
                else:
                    thisPar.append(tTemp.rstrip()+" ")

            elif tType == self.T_COMMENT and self.doComments:
                self.theResult += self._formatComments(tText)

            elif tType == self.T_KEYWORD and self.doKeywords:
                self.theResult += self._formatTags(tText)

        return

    ##
    #  Internal Functions
    ##

    def _formatTags(self, tText):

        if not self.forPreview:
            return "<pre>@%s</pre>\n" % tText

        tText = "@"+tText
        isValid, theBits, thePos = self.theParent.theIndex.scanThis(tText)
        if not isValid or not theBits:
            return ""

        retText = ""
        refTags = []
        if theBits[0] in nwLabels.KEY_NAME:
            retText += "<span class='tags'>%s:</span>&nbsp;" % nwLabels.KEY_NAME[theBits[0]]
            for tTag in theBits[1:]:
                refTags.append("<a href='#%s=%s'>%s</a>" % (
                    theBits[0][1:], tTag, tTag
                ))
            retText += ", ".join(refTags)

        return "<div>%s</div>" % retText

    def _formatComments(self, tText):

        if not self.forPreview:
            return "<div class='comment'>%s</div>\n" % tText

        return "<p class='comment'>%s</p>\n" % tText

# END Class ToHtml
