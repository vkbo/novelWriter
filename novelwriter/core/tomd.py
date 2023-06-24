"""
novelWriter – Markdown Text Converter
=====================================

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
from __future__ import annotations

import logging

from pathlib import Path

from novelwriter.constants import nwLabels
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class ToMarkdown(Tokenizer):
    """Core: Markdown Document Writer

    Extend the Tokenizer class to writer Markdown output. It supports
    both Standard Markdown and GitHub Flavour Markdown (Extended). The
    class also supports concatenating novelWriter markup files.
    """

    M_STD = 0  # Standard Markdown
    M_GH  = 1  # GitHub Markdown

    def __init__(self, project: NWProject):
        super().__init__(project)

        self._genMode = self.M_STD
        self._fullMD = []

        return

    ##
    #  Properties
    ##

    @property
    def fullMD(self) -> list:
        """Return the markdown as a list."""
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

    def getFullResultSize(self) -> int:
        """Return the size of the full Markdown result."""
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

        self._result = ""

        thisPar = []
        tmpResult = []

        for tType, _, tText, tFormat, tStyle in self._tokens:

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

        self._result = "".join(tmpResult)
        tmpResult = []

        self._fullMD.append(self._result)

        return

    def saveMarkdown(self, path: str | Path):
        """Save the data to a plain text file."""
        with open(path, mode="w", encoding="utf-8") as outFile:
            outFile.write("".join(self._fullMD))
        logger.info("Wrote file: %s", path)
        return

    def replaceTabs(self, nSpaces: int = 8, spaceChar: str = " "):
        """Replace tabs with spaces."""
        spaces = spaceChar*nSpaces
        self._fullMD = [p.replace("\t", spaces) for p in self._fullMD]
        if self._keepMarkdown:
            self._allMarkdown = [p.replace("\t", spaces) for p in self._allMarkdown]
        return

    ##
    #  Internal Functions
    ##

    def _formatKeywords(self, text: str, style: int) -> str:
        """Apply Markdown formatting to keywords."""
        valid, bits, _ = self._project.index.scanThis("@"+text)
        if not valid or not bits:
            return ""

        result = ""
        if bits[0] in nwLabels.KEY_NAME:
            result += f"**{nwLabels.KEY_NAME[bits[0]]}:** "
            if len(bits) > 1:
                result += ", ".join(bits[1:])

        result += "  \n" if style & self.A_Z_BTMMRG else "\n\n"

        return result

# END Class ToMarkdown
