# -*- coding: utf-8 -*-
"""novelWriter HTML Text Converter

 novelWriter – HTML Text Converter
===================================
 Extends the Tokenizer class to write HTML

 File History:
 Created: 2019-05-07 [0.0.1]

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

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

from nw.core.tokenizer import Tokenizer
from nw.constants import nwUnicode, nwLabels, nwKeyWords

logger = logging.getLogger(__name__)

class ToHtml(Tokenizer):

    M_PREVIEW = 0 # Tweak output for the DocViewer
    M_EXPORT  = 1 # Tweak output for saving to HTML or printing
    M_EBOOK   = 2 # Tweak output for converting to epub

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)
        self.genMode = self.M_EXPORT
        self.cssStyles = True

        self.repDict = {
            "<" : "&lt;",
            ">" : "&gt;",
            "&" : "&amp;",
            nwUnicode.U_ENDASH : nwUnicode.H_ENDASH,
            nwUnicode.U_EMDASH : nwUnicode.H_EMDASH,
            nwUnicode.U_HELLIP : nwUnicode.H_HELLIP,
            nwUnicode.U_NBSP   : nwUnicode.H_NBSP,
            nwUnicode.U_THNSP  : nwUnicode.H_THNSP,
            nwUnicode.U_THNBSP : nwUnicode.H_THNBSP,
            nwUnicode.U_MAPOSS : nwUnicode.H_RSQUO,
        }
        self.revDict = {}
        self.reReplace = []
        self.reReverse = []
        self._buildRegEx()

        return

    ##
    #  Setters
    ##

    def setPreview(self, forPreview, doComments, doSynopsis):
        """If we're using this class to generate markdown preview, we
        need to make a few changes to formatting, which is managed by
        these flags.
        """
        if forPreview:
            self.genMode    = self.M_PREVIEW
            self.doKeywords = True
            self.doComments = doComments
            self.doSynopsis = doSynopsis
        return

    def setStyles(self, cssStyles):
        """Enable/disable CSS styling. Some elements may still have
        class tags.
        """
        self.cssStyles = cssStyles
        return

    ##
    #  Class Methods
    ##

    def doAutoReplace(self):
        """Extend the auto-replace to also properly encode some unicode
        characters into their respective HTML entities.
        """
        Tokenizer.doAutoReplace(self)
        self.theText = self.reReplace.sub(
            lambda x: self.repDict[x.group(0)], self.theText
        )
        return

    def doPostProcessing(self):
        """Reverse the html entities replacement on the markdown text.
        Otherwise, all the &something; bits will also be in there.
        """
        Tokenizer.doPostProcessing(self)
        if self.genMode == self.M_PREVIEW:
            # Doesn't matter for preview as we don't use the markdown
            return
        self.theMarkdown = self.reReverse.sub(
            lambda x: self.revDict[x.group(0)], self.theMarkdown
        )
        return

    def doConvert(self):
        """Convert the list of text tokens into a HTML document saved
        to theResult.
        """
        if self.genMode == self.M_PREVIEW:
            htmlTags = {     # HTML4 + CSS2
                self.FMT_B_B : "<b>",
                self.FMT_B_E : "</b>",
                self.FMT_I_B : "<i>",
                self.FMT_I_E : "</i>",
                self.FMT_D_B : "<span style='text-decoration: line-through;'>",
                self.FMT_D_E : "</span>",
            }
        else:
            htmlTags = {     # HTML5
                self.FMT_B_B : "<strong>",
                self.FMT_B_E : "</strong>",
                self.FMT_I_B : "<em>",
                self.FMT_I_E : "</em>",
                self.FMT_D_B : "<del>",
                self.FMT_D_E : "</del>",
            }

        if self.isNovel and self.genMode != self.M_PREVIEW:
            # For novel files for export, we bump the titles one level
            # up as this is more useful for printing and word processor
            # imports.
            h1 = "h1 class='title'"
            h2 = "h1"
            h3 = "h2"
            h4 = "h3"
        else:
            h1 = "h1"
            h2 = "h2"
            h3 = "h3"
            h4 = "h4"

        self.theResult = ""

        thisPar = []
        parStyle = None
        tmpResult = []
        hasHardBreak = False
        for tType, tLine, tText, tFormat, tStyle in self.theTokens:

            # Styles
            aStyle = []
            if tStyle is not None and self.cssStyles:
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
                if tStyle & self.A_PBB_AV:
                    aStyle.append("page-break-before: avoid;")
                if tStyle & self.A_PBB_NO:
                    aStyle.append("page-break-before: never;")
                if tStyle & self.A_PBA:
                    aStyle.append("page-break-after: always;")
                if tStyle & self.A_PBA_AV:
                    aStyle.append("page-break-after: avoid;")
                if tStyle & self.A_PBA_NO:
                    aStyle.append("page-break-after: never;")

            if len(aStyle) > 0:
                hStyle = " style='%s'" % (" ".join(aStyle))
            else:
                hStyle = ""

            if self.linkHeaders:
                aNm = "<a name='T%06d'></a>" % tLine
            else:
                aNm = ""

            # Process TextType
            if tType == self.T_EMPTY:
                if parStyle is None:
                    parStyle = ""
                if hasHardBreak and self.cssStyles:
                    parClass = " class='break'"
                else:
                    parClass = ""
                if len(thisPar) > 0:
                    tTemp = "".join(thisPar)
                    tmpResult.append("<p%s%s>%s</p>\n" % (parStyle, parClass, tTemp.rstrip()))
                thisPar = []
                parStyle = None
                hasHardBreak = False

            elif tType == self.T_TITLE:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append("<h1 class='title'%s>%s%s</h1>\n" % (hStyle, aNm, tHead))

            elif tType == self.T_HEAD1:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append("<%s%s>%s%s</%s>\n" % (h1, hStyle, aNm, tHead, h1))

            elif tType == self.T_HEAD2:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append("<%s%s>%s%s</%s>\n" % (h2, hStyle, aNm, tHead, h2))

            elif tType == self.T_HEAD3:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append("<%s%s>%s%s</%s>\n" % (h3, hStyle, aNm, tHead, h3))

            elif tType == self.T_HEAD4:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append("<%s%s>%s%s</%s>\n" % (h4, hStyle, aNm, tHead, h4))

            elif tType == self.T_SEP:
                tmpResult.append("<p class='sep'>%s</p>\n" % tText)

            elif tType == self.T_SKIP:
                tmpResult.append("<p class='skip'>&nbsp;</p>\n")

            elif tType == self.T_TEXT:
                tTemp = tText
                if parStyle is None:
                    parStyle = hStyle
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+htmlTags[xFmt]+tTemp[xPos+xLen:]
                if tText.endswith("  "):
                    thisPar.append(tTemp.rstrip()+"<br/>")
                    hasHardBreak = True
                else:
                    thisPar.append(tTemp.rstrip()+" ")

            elif tType == self.T_SYNOPSIS and self.doSynopsis:
                tmpResult.append(self._formatSynopsis(tText))

            elif tType == self.T_COMMENT and self.doComments:
                tmpResult.append(self._formatComments(tText))

            elif tType == self.T_KEYWORD and self.doKeywords:
                tmpResult.append(self._formatKeywords(tText))

        self.theResult = "".join(tmpResult)
        tmpResult = []

        return

    def getStyleSheet(self):
        """Generate a stylesheet appropriate for the current settings.
        """
        theStyles = []
        if not self.cssStyles:
            return theStyles

        if self.doJustify:
            theStyles.append(r"p {text-align: justify;}")
        else:
            theStyles.append(r"p {text-align: left;}")

        theStyles.append(r"h1, h2 {color: rgb(66, 113, 174);}")
        theStyles.append(r"h3, h4 {color: rgb(50, 50, 50);}")
        theStyles.append(r"h1, h2, h3, h4 {page-break-after: avoid;}")
        theStyles.append(r"a {color: rgb(66, 113, 174);}")
        theStyles.append(r".title {font-size: 2.5em;}")
        theStyles.append(r".tags {color: rgb(245, 135, 31); font-weight: bold;}")
        theStyles.append(r".break {text-align: left;}")
        theStyles.append(r".sep {text-align: center; margin-top: 1em; margin-bottom: 1em;}")
        theStyles.append(r".skip {margin-top: 1em; margin-bottom: 1em;}")
        theStyles.append(r".synopsis {font-style: italic;}")
        theStyles.append(r".comment {font-style: italic; color: rgb(100, 100, 100);}")

        return theStyles

    ##
    #  Internal Functions
    ##

    def _formatSynopsis(self, tText):
        """Apply HTML formatting to synopsis.
        """
        if self.genMode == self.M_PREVIEW:
            return "<p class='comment'><span class='synopsis'>Synopsis: </span>%s</p>\n" % tText
        else:
            return "<p class='synopsis'><strong>Synopsis: </strong>%s</p>\n" % tText

    def _formatComments(self, tText):
        """Apply HTML formatting to comments.
        """
        if self.genMode == self.M_PREVIEW:
            return "<p class='comment'>%s</p>\n" % tText
        else:
            return "<p class='comment'><strong>Comment: </strong>%s</p>\n" % tText

    def _formatKeywords(self, tText):
        """Apply HTML formatting to keywords.
        """
        isValid, theBits, thePos = self.theParent.theIndex.scanThis("@"+tText)
        if not isValid or not theBits:
            return ""

        retText = ""
        refTags = []
        if theBits[0] in nwLabels.KEY_NAME:
            retText += "<span class='tags'>%s:</span> " % nwLabels.KEY_NAME[theBits[0]]
            if len(theBits) > 1:
                if theBits[0] == nwKeyWords.TAG_KEY:
                    retText += "<a name='tag_%s'>%s</a>" % (
                        theBits[1], theBits[1]
                    )
                else:
                    if self.genMode == self.M_PREVIEW:
                        for tTag in theBits[1:]:
                            refTags.append("<a href='#%s=%s'>%s</a>" % (
                                theBits[0][1:], tTag, tTag
                            ))
                        retText += ", ".join(refTags)
                    else:
                        for tTag in theBits[1:]:
                            refTags.append("<a href='#tag_%s'>%s</a>" % (
                                tTag, tTag
                            ))
                        retText += ", ".join(refTags)

        return "<div>%s</div>" % retText

    def _buildRegEx(self):
        """Build the regular expressions
        """
        self.revDict = dict(map(reversed, self.repDict.items()))
        self.reReplace = re.compile(
            "|".join([re.escape(k) for k in self.repDict.keys()]), flags=re.DOTALL
        )
        self.reReverse = re.compile(
            "|".join([re.escape(k) for k in self.revDict.keys()]), flags=re.DOTALL
        )
        return

# END Class ToHtml
