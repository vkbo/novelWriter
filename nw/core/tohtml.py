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

from nw.core.tokenizer import Tokenizer
from nw.constants import nwUnicode, nwLabels

logger = logging.getLogger(__name__)

class ToHtml(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)
        self.forPreview = False
        return

    ##
    #  Setters
    ##

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

    ##
    #  Class Methods
    ##

    def doAutoReplace(self):
        """Extend the auto-replace to also properly encode some unicode
        characters into their respective HTML entities.
        """
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
        """Convert the list of text tokens into a HTML document saved
        to theResult.
        """

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
        for tType, tText, tFormat, tStyle in self.theTokens:

            # Styles
            aStyle = []
            if tStyle is not None:
                if tStyle & self.A_LEFT:
                    aStyle.append("text-align: left;")
                if tStyle & self.A_RIGHT:
                    aStyle.append("text-align: right;")
                if tStyle & self.A_CENTRE:
                    aStyle.append("text-align: center;")
                if tStyle & self.A_JUSTIFY:
                    aStyle.append("text-align: justify;")
                if tStyle & self.A_PBB:
                    aStyle.append("page-break-before: always;")
                if tStyle & self.A_PBB_L:
                    aStyle.append("page-break-before: left;")
                if tStyle & self.A_PBB_R:
                    aStyle.append("page-break-before: right;")
                if tStyle & self.A_PBB_AV:
                    aStyle.append("page-break-before: avoid;")
                if tStyle & self.A_PBA:
                    aStyle.append("page-break-after: always;")
                if tStyle & self.A_PBA_L:
                    aStyle.append("page-break-after: left;")
                if tStyle & self.A_PBA_R:
                    aStyle.append("page-break-after: right;")
                if tStyle & self.A_PBA_AV:
                    aStyle.append("page-break-after: avoid;")

            if len(aStyle) > 0:
                hStyle = " style='%s'" % (" ".join(aStyle))
            else:
                hStyle = ""

            # Process TextType
            if tType == self.T_EMPTY:
                if len(thisPar) > 0:
                    tTemp = "".join(thisPar)
                    self.theResult += "<p%s>%s</p>\n" % (hStyle,tTemp.rstrip())
                thisPar = []

            elif tType == self.T_HEAD1:
                tHead = tText.replace(r"\\", "<br/>")
                self.theResult += "<h1%s>%s</h1>\n" % (hStyle, tHead)

            elif tType == self.T_HEAD2:
                tHead = tText.replace(r"\\", "<br/>")
                self.theResult += "<h2%s>%s</h2>\n" % (hStyle, tHead)

            elif tType == self.T_HEAD3:
                tHead = tText.replace(r"\\", "<br/>")
                self.theResult += "<h3%s>%s</h3>\n" % (hStyle, tHead)

            elif tType == self.T_HEAD4:
                tHead = tText.replace(r"\\", "<br/>")
                self.theResult += "<h4%s>%s</h4>\n" % (hStyle, tHead)

            elif tType == self.T_SEP:
                self.theResult += "<p%s>%s</p>\n" % (hStyle, tText)

            elif tType == self.T_SKIP:
                self.theResult += "<p>&nbsp;</p>\n"

            elif tType == self.T_PBREAK:
                self.theResult += "<p style='page-break-after: always;'>&nbsp;</p>\n"

            elif tType == self.T_TEXT:
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+htmlTags[xFmt]+tTemp[xPos+xLen:]
                if tText.endswith("  "):
                    thisPar.append(tTemp.rstrip()+"<br/>")
                else:
                    thisPar.append(tTemp.rstrip()+" ")

            elif tType == self.T_SYNOPSIS and self.doSynopsis:
                self.theResult += self._formatSynopsis(tText)

            elif tType == self.T_COMMENT and self.doComments:
                self.theResult += self._formatComments(tText)

            elif tType == self.T_KEYWORD and self.doKeywords:
                self.theResult += self._formatKeywords(tText)

        return

    ##
    #  Internal Functions
    ##

    def _formatSynopsis(self, tText):
        """Apply HTML formatting to synopsis.
        """

        if not self.forPreview:
            return "<p class='synopsis'><strong>Synopsis: </strong>%s</p>\n" % tText

        return "<p class='comment'>%s</p>\n" % tText

    def _formatComments(self, tText):
        """Apply HTML formatting to comments.
        """

        if not self.forPreview:
            return "<p class='comment'><strong>Comment: </strong>%s</p>\n" % tText

        return "<p class='comment'>%s</p>\n" % tText

    def _formatKeywords(self, tText):
        """Apply HTML formatting to keywords.
        """

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

# END Class ToHtml
