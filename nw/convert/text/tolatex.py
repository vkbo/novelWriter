# -*- coding: utf-8 -*-
"""novelWriter LaTeX Converter

 novelWriter – LaTeX Converter
===============================
 Extends the Tokenizer class to write LaTeX

 File History:
 Created: 2019-10-24 [0.3.1]

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
import codecs
import re
import nw

from nw.convert.tokenizer import Tokenizer
from nw.constants import nwUnicode

logger = logging.getLogger(__name__)

class ToLaTeX(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)
        self.texCodecFail = False
        return

    def doPostProcessing(self):
        """The latexcodec misses dashes and non-breaking spaces, so we
        do those here.
        """

        repDict = {
            nwUnicode.U_ENDASH : "--",
            nwUnicode.U_EMDASH : "---",
            nwUnicode.U_NBSP   : "~",
        }
        xRep = re.compile("|".join([re.escape(k) for k in repDict.keys()]), flags=re.DOTALL)
        self.theResult = xRep.sub(lambda x: repDict[x.group(0)], self.theResult)

        return

    def doConvert(self):

        texTags = {
            self.FMT_B_B : r"\textbf{",
            self.FMT_B_E : r"}",
            self.FMT_I_B : r"\textit{",
            self.FMT_I_E : r"}",
            self.FMT_U_B : r"\underline{",
            self.FMT_U_E : r"}",
        }

        self.theResult = ""
        thisPar = []
        for tType, tText, tFormat, tAlign in self.theTokens:

            begText = ""
            endText = "\n"
            if tAlign == self.A_CENTRE:
                begText = "\\begin{center}\n"
                endText = "\\end{center}\n\n"

            # First check if we have a comment or plain text, as they
            # need some extra replacing before we proceed to wrapping
            # and final formatting.
            if tType == self.T_COMMENT:
                tText = "%% %s" % tText

            elif tType == self.T_TEXT:
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+texTags[xFmt]+tTemp[xPos+xLen:]
                tText = tTemp

            tLen = len(tText)

            # Then the text can receive final formatting before we
            # append it to the results. We also store text lines in a
            # buffer and merge them only when we find an empty line
            # indicating a new paragraph.
            if tType == self.T_EMPTY:
                if len(thisPar) > 0:
                    self.theResult += begText
                    for tTemp in thisPar:
                        self.theResult += "%s\n" % tTemp
                    self.theResult += endText
                thisPar = []

            elif tType == self.T_HEAD1:
                self.theResult += begText
                self.theResult += "{\\Huge %s}\n" % self._escapeUnicode(tText)
                self.theResult += endText

            elif tType == self.T_HEAD2:
                self.theResult += "\\chapter*{%s}\n\n" % self._escapeUnicode(tText)

            elif tType == self.T_HEAD3:
                self.theResult += "\\section*{%s}\n\n" % self._escapeUnicode(tText)

            elif tType == self.T_HEAD4:
                self.theResult += "\\subsection*{%s}\n\n" % self._escapeUnicode(tText)

            elif tType == self.T_SEP:
                self.theResult += begText
                self.theResult += "%s\n" % self._escapeUnicode(tText)
                self.theResult += endText

            elif tType == self.T_SKIP:
                self.theResult += "\\bigskip\n"
                self.theResult += "\\bigskip\n\n"

            elif tType == self.T_TEXT:
                if tText.endswith("  "):
                    thisPar.append(self._escapeUnicode(tText.rstrip())+"\\newline")
                else:
                    thisPar.append(self._escapeUnicode(tText.rstrip()))

            elif tType == self.T_PBREAK:
                self.theResult += "\\newpage\n\n"

            elif tType == self.T_COMMENT and self.doComments:
                self.theResult += "%s\n\n" % tText

            elif tType == self.T_KEYWORD and self.doKeywords:
                self.theResult += "%% @%s\n\n" % tText

        return

    def _escapeUnicode(self, theText):
        try:
            import latexcodec
            return codecs.encode(theText, "ulatex+utf8")
        except:
            self.texCodecFail = True
            return theText

# END Class ToLaTeX
