"""
novelWriter – Markdown Text Converter
=====================================
Extends the Tokenizer class to generate Makrdown output

File History:
Created: 2021-02-06 [1.2b1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

from novelwriter.constants import nwLabels
from novelwriter.core.tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class ToMarkdown(Tokenizer):

    M_STD = 0  # Standard Markdown
    M_GH  = 1  # GitHub Markdown

    def __init__(self, theProject):
        super().__init__(theProject)

        self._genMode = self.M_STD
        self._fullMD = []

        return

    ##
    #  Properties
    ##

    @property
    def fullMD(self):
        return self._fullMD

    ##
    #  Setters
    ##

    def setStandardMarkdown(self):
        self._genMode = self.M_STD
        return

    def setGitHubMarkdown(self):
        self._genMode = self.M_GH
        return

    ##
    #  Class Methods
    ##

    def getFullResultSize(self):
        """Return the size of the full Markdown result.
        """
        return sum([len(x) for x in self._fullMD])

    def doConvert(self):
        """Convert the list of text tokens into a HTML document saved
        to theResult.
        """
        if self._genMode == self.M_STD:
            # Standard
            mdTags = {
                self.FMT_B_B: "**",
                self.FMT_B_E: "**",
                self.FMT_I_B: "_",
                self.FMT_I_E: "_",
                self.FMT_D_B: "",
                self.FMT_D_E: "",
            }
        else:
            # GitHub
            mdTags = {
                self.FMT_B_B: "**",
                self.FMT_B_E: "**",
                self.FMT_I_B: "_",
                self.FMT_I_E: "_",
                self.FMT_D_B: "~~",
                self.FMT_D_E: "~~",
            }

        self._theResult = ""

        thisPar = []
        tmpResult = []

        for tType, _, tText, tFormat, tStyle in self._theTokens:

            # Process Text Type
            if tType == self.T_EMPTY:
                if len(thisPar) > 0:
                    tTemp = ("  \n".join(thisPar)).rstrip(" ")
                    tmpResult.append(f"{tTemp}\n\n")
                thisPar = []

            elif tType == self.T_TITLE:
                tHead = tText.replace(r"\\", "\n")
                tmpResult.append(f"# {tHead}\n\n")

            elif tType == self.T_UNNUM:
                tHead = tText.replace(r"\\", "\n")
                tmpResult.append(f"## {tHead}\n\n")

            elif tType == self.T_HEAD1:
                tHead = tText.replace(r"\\", "\n")
                tmpResult.append(f"# {tHead}\n\n")

            elif tType == self.T_HEAD2:
                tHead = tText.replace(r"\\", "\n")
                tmpResult.append(f"## {tHead}\n\n")

            elif tType == self.T_HEAD3:
                tHead = tText.replace(r"\\", "\n")
                tmpResult.append(f"### {tHead}\n\n")

            elif tType == self.T_HEAD4:
                tHead = tText.replace(r"\\", "\n")
                tmpResult.append(f"#### {tHead}\n\n")

            elif tType == self.T_SEP:
                tmpResult.append("%s\n\n" % tText)

            elif tType == self.T_SKIP:
                tmpResult.append("\n\n\n")

            elif tType == self.T_TEXT:
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos] + mdTags[xFmt] + tTemp[xPos+xLen:]
                thisPar.append(tTemp.rstrip())

            elif tType == self.T_SYNOPSIS and self._doSynopsis:
                locName = self._localLookup("Synopsis")
                tmpResult.append(f"**{locName}:** {tText}\n\n")

            elif tType == self.T_COMMENT and self._doComments:
                locName = self._localLookup("Comment")
                tmpResult.append(f"**{locName}:** {tText}\n\n")

            elif tType == self.T_KEYWORD and self._doKeywords:
                tmpResult.append(self._formatKeywords(tText, tStyle))

        self._theResult = "".join(tmpResult)
        tmpResult = []

        self._fullMD.append(self._theResult)

        return

    def saveMarkdown(self, savePath):
        """Save the data to a plain text file.
        """
        with open(savePath, mode="w", encoding="utf-8") as outFile:
            theText = "".join(self._fullMD)
            outFile.write(theText)

        return

    def replaceTabs(self, nSpaces=8, spaceChar=" "):
        """Replace tabs with spaces.
        """
        fullMD = []
        eightSpace = spaceChar*nSpaces
        for aPage in self._fullMD:
            fullMD.append(aPage.replace("\t", eightSpace))

        self._fullMD = fullMD
        return

    ##
    #  Internal Functions
    ##

    def _formatKeywords(self, tText, tStyle):
        """Apply Markdown formatting to keywords.
        """
        isValid, theBits, _ = self.theProject.index.scanThis("@"+tText)
        if not isValid or not theBits:
            return ""

        retText = ""
        if theBits[0] in nwLabels.KEY_NAME:
            retText += f"**{nwLabels.KEY_NAME[theBits[0]]}:** "

            if len(theBits) > 1:
                retText += ", ".join(theBits[1:])

        if tStyle & self.A_Z_BTMMRG:
            retText += "  \n"
        else:
            retText += "\n\n"

        return retText

# END Class ToMarkdown
