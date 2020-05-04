# -*- coding: utf-8 -*-
"""novelWriter Markdown Text Converter

 novelWriter – Markdown Text Converter
=======================================
 Extends the Tokenizer class to write Markdown

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

import textwrap
import logging
import re
import nw

from nw.convert.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

class ToMarkdown(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)
        return

    def doConvert(self):

        mdTags = {
            self.FMT_B_B : "**",
            self.FMT_B_E : "**",
            self.FMT_I_B : "_",
            self.FMT_I_E : "_",
            self.FMT_U_B : "__",
            self.FMT_U_E : "__",
        }

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
                tText = "    %s" % tText

            elif tType == self.T_TEXT:
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+mdTags[xFmt]+tTemp[xPos+xLen:]
                tText = tTemp

            tLen = len(tText)

            # The text can now be word wrapped, if we have requested
            # this and it's needed.
            if self.wordWrap > 0 and tLen > self.wordWrap:
                if tType == self.T_COMMENT:
                    tText = textwrap.fill(
                        tText.strip(),initial_indent="    ",subsequent_indent="    "
                    )
                else:
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
                self.theResult += "# %s\n\n" % tText

            elif tType == self.T_HEAD2:
                self.theResult += "## %s\n\n" % tText

            elif tType == self.T_HEAD3:
                self.theResult += "### %s\n\n" % tText

            elif tType == self.T_HEAD4:
                self.theResult += "#### %s\n\n" % tText

            elif tType == self.T_SEP:
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

# END Class ToMarkdown
