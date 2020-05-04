# -*- coding: utf-8 -*-
"""novelWriter Plain Text Converter

 novelWriter – Plain Text Converter
====================================
 Extends the Tokenizer class to convert to plain text

 File History:
 Created: 2019-10-26 [0.3.1]

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

import textwrap
import logging
import re
import nw

from nw.convert.tokenizer import Tokenizer
from nw.constants import nwUnicode

logger = logging.getLogger(__name__)

class ToText(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)
        return

    def doAutoReplace(self):
        Tokenizer.doAutoReplace(self)

        repDict = {
            "\t" : "    ",
            nwUnicode.U_NBSP : " ",
        }
        xRep = re.compile("|".join([re.escape(k) for k in repDict.keys()]), flags=re.DOTALL)
        self.theText = xRep.sub(lambda x: repDict[x.group(0)], self.theText)

        return

    def doConvert(self):
        """Converts the tokenized text into plain text.
        """

        if self.wordWrap > 0:
            tWrap = textwrap.TextWrapper(
                width                = self.wordWrap,
                initial_indent       = "",
                subsequent_indent    = "",
                expand_tabs          = True,
                replace_whitespace   = True,
                fix_sentence_endings = False,
                break_long_words     = True,
                drop_whitespace      = True,
                break_on_hyphens     = True,
                tabsize              = 8,
                max_lines            = None
            )

        self.theResult = ""
        thisPar = []
        for tType, tText, tFormat, tAlign in self.theTokens:

            # First check if we have a comment or plain text, as they
            # need some extra replacing before we proceed to wrapping
            # and final formatting.
            if tType == self.T_COMMENT:
                tText = "[%s]" % tText

            elif tType == self.T_TEXT:
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+tTemp[xPos+xLen:]
                tText = tTemp

            tLen = len(tText)

            # The text can now be word wrapped, if we have requested
            # this and it's needed.
            if tAlign == self.A_CENTRE:
                if self.wordWrap > 0:
                    if tLen > self.wordWrap:
                        aText = tWrap.wrap(tText)
                        for n in range(len(aText)):
                            aText[n] = self._centreText(aText[n],self.wordWrap)
                        tText = "\n".join(aText)
                    else:
                        tText = self._centreText(tText,self.wordWrap)
            else:
                if self.wordWrap > 0 and tLen > self.wordWrap:
                    tText = tWrap.fill(tText)

            # Then the text can receive final formatting before we
            # append it to the results. We also store text lines in a
            # buffer and merge them only when we find an empty line,
            # indicating a new paragraph.
            if tType == self.T_EMPTY:
                if len(thisPar) > 0:
                    tTemp = "\n".join(thisPar)
                    self.theResult += "%s\n\n" % tTemp.rstrip()
                thisPar = []

            elif tType == self.T_HEAD1:
                uLine = "="*min(tLen,self.wordWrap)
                if tAlign == self.A_CENTRE:
                    uLine = self._centreText(uLine,self.wordWrap)
                self.theResult += "%s\n%s\n\n" % (tText,uLine)

            elif tType == self.T_HEAD2:
                uLine = "~"*min(tLen,self.wordWrap)
                self.theResult += "%s\n%s\n\n" % (tText,uLine)

            elif tType == self.T_HEAD3:
                uLine = "-"*min(tLen,self.wordWrap)
                self.theResult += "%s\n%s\n\n" % (tText,uLine)

            elif tType == self.T_HEAD4:
                self.theResult += "%s\n\n" % tText

            elif tType == self.T_SEP:
                if self.wordWrap > 0 and tLen < self.wordWrap:
                    tText = self._centreText(tText,self.wordWrap)
                self.theResult += "%s\n\n" % tText

            elif tType == self.T_SKIP:
                self.theResult += "\n\n\n"

            elif tType == self.T_TEXT:
                thisPar.append(tText)

            elif tType == self.T_COMMENT and self.doComments:
                self.theResult += "%s\n\n" % tText

            elif tType == self.T_KEYWORD and self.doKeywords:
                self.theResult += "%s\n\n" % tText

        return

# END Class ToText
