"""
novelWriter – Markdown Text Converter
=====================================

File History:
Created: 2021-02-06 [1.2b1] ToMarkdown

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

from novelwriter.constants import nwHeadFmt, nwLabels, nwUnicode
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import T_Formats, Tokenizer

logger = logging.getLogger(__name__)


# Standard Markdown
STD_MD = {
    Tokenizer.FMT_B_B: "**",
    Tokenizer.FMT_B_E: "**",
    Tokenizer.FMT_I_B: "_",
    Tokenizer.FMT_I_E: "_",
    Tokenizer.FMT_D_B: "",
    Tokenizer.FMT_D_E: "",
    Tokenizer.FMT_U_B: "",
    Tokenizer.FMT_U_E: "",
    Tokenizer.FMT_M_B: "",
    Tokenizer.FMT_M_E: "",
    Tokenizer.FMT_SUP_B: "",
    Tokenizer.FMT_SUP_E: "",
    Tokenizer.FMT_SUB_B: "",
    Tokenizer.FMT_SUB_E: "",
}

# Extended Markdown
EXT_MD = {
    Tokenizer.FMT_B_B: "**",
    Tokenizer.FMT_B_E: "**",
    Tokenizer.FMT_I_B: "_",
    Tokenizer.FMT_I_E: "_",
    Tokenizer.FMT_D_B: "~~",
    Tokenizer.FMT_D_E: "~~",
    Tokenizer.FMT_U_B: "",
    Tokenizer.FMT_U_E: "",
    Tokenizer.FMT_M_B: "==",
    Tokenizer.FMT_M_E: "==",
    Tokenizer.FMT_SUP_B: "^",
    Tokenizer.FMT_SUP_E: "^",
    Tokenizer.FMT_SUB_B: "~",
    Tokenizer.FMT_SUB_E: "~",
}


class ToMarkdown(Tokenizer):
    """Core: Markdown Document Writer

    Extend the Tokenizer class to writer Markdown output. It supports
    both Standard Markdown and Extended Markdown. The class also
    supports concatenating novelWriter markup files.
    """

    M_STD = 0  # Standard Markdown
    M_EXT = 1  # Extended Markdown

    def __init__(self, project: NWProject) -> None:
        super().__init__(project)
        self._genMode = self.M_STD
        self._fullMD: list[str] = []
        self._preserveBreaks = True
        return

    ##
    #  Properties
    ##

    @property
    def fullMD(self) -> list[str]:
        """Return the markdown as a list."""
        return self._fullMD

    ##
    #  Setters
    ##

    def setStandardMarkdown(self) -> None:
        """Set the converter to use standard Markdown formatting."""
        self._genMode = self.M_STD
        return

    def setExtendedMarkdown(self) -> None:
        """Set the converter to use Extended Markdown formatting."""
        self._genMode = self.M_EXT
        return

    def setPreserveBreaks(self, state: bool) -> None:
        """Preserve line breaks in paragraphs."""
        self._preserveBreaks = state
        return

    ##
    #  Class Methods
    ##

    def getFullResultSize(self) -> int:
        """Return the size of the full Markdown result."""
        return sum(len(x) for x in self._fullMD)

    def doConvert(self) -> None:
        """Convert the list of text tokens into a Markdown document."""
        self._result = ""

        if self._genMode == self.M_STD:
            mTags = STD_MD
            cSkip = ""
        else:
            mTags = EXT_MD
            cSkip = nwUnicode.U_MMSP

        para = []
        lines = []
        lineSep = "  \n" if self._preserveBreaks else " "

        for tType, _, tText, tFormat, tStyle in self._tokens:

            if tType == self.T_EMPTY:
                if para:
                    tTemp = (lineSep.join(para)).rstrip(" ")
                    lines.append(f"{tTemp}\n\n")
                para = []

            elif tType == self.T_TITLE:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                lines.append(f"# {tHead}\n\n")

            elif tType == self.T_HEAD1:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                lines.append(f"# {tHead}\n\n")

            elif tType == self.T_HEAD2:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                lines.append(f"## {tHead}\n\n")

            elif tType == self.T_HEAD3:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                lines.append(f"### {tHead}\n\n")

            elif tType == self.T_HEAD4:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                lines.append(f"#### {tHead}\n\n")

            elif tType == self.T_SEP:
                lines.append(f"{tText}\n\n")

            elif tType == self.T_SKIP:
                lines.append(f"{cSkip}\n\n")

            elif tType == self.T_TEXT:
                para.append(self._formatText(tText, tFormat, mTags).rstrip())

            elif tType == self.T_SYNOPSIS and self._doSynopsis:
                label = self._localLookup("Synopsis")
                lines.append(f"**{label}:** {self._formatText(tText, tFormat, mTags)}\n\n")

            elif tType == self.T_SHORT and self._doSynopsis:
                label = self._localLookup("Short Description")
                lines.append(f"**{label}:** {self._formatText(tText, tFormat, mTags)}\n\n")

            elif tType == self.T_COMMENT and self._doComments:
                label = self._localLookup("Comment")
                lines.append(f"**{label}:** {self._formatText(tText, tFormat, mTags)}\n\n")

            elif tType == self.T_KEYWORD and self._doKeywords:
                lines.append(self._formatKeywords(tText, tStyle))

        self._result = "".join(lines)
        self._fullMD.append(self._result)

        return

    def appendFootnotes(self) -> None:
        """Append the footnotes in the buffer."""
        if self._footnotes:
            tags = STD_MD if self._genMode == self.M_STD else EXT_MD
            footnotes = self._localLookup("Footnotes")

            lines = []
            lines.append(f"### {footnotes}\n\n")
            for index, content in self._footnotes.values():
                marker = f"{index}. "
                indent = "\n\n"+" "*len(marker)
                text = indent.join(self._formatText(t, f, tags) for t, f in content)
                lines.append(f"{marker}{text}\n")
            lines.append("\n")

            result = "".join(lines)
            self._result += result
            self._fullMD.append(result)

        return

    def saveMarkdown(self, path: str | Path) -> None:
        """Save the data to a plain text file."""
        with open(path, mode="w", encoding="utf-8") as outFile:
            outFile.write("".join(self._fullMD))
        logger.info("Wrote file: %s", path)
        return

    def replaceTabs(self, nSpaces: int = 8, spaceChar: str = " ") -> None:
        """Replace tabs with spaces."""
        spaces = spaceChar*nSpaces
        self._fullMD = [p.replace("\t", spaces) for p in self._fullMD]
        if self._keepMarkdown:
            self._allMarkdown = [p.replace("\t", spaces) for p in self._allMarkdown]
        return

    ##
    #  Internal Functions
    ##

    def _formatText(self, text: str, tFmt: T_Formats, tags: dict[int, str]) -> str:
        """Apply formatting tags to text."""
        temp = text
        for pos, fmt, data in reversed(tFmt):
            md = ""
            if fmt == self.FMT_FNOTE:
                index = self._footnotes.get(data, (0, ""))[0] or "ERR"
                md = f"[{index}]"
            else:
                md = tags.get(fmt, "")
            temp = f"{temp[:pos]}{md}{temp[pos:]}"
        return temp

    def _formatKeywords(self, text: str, style: int) -> str:
        """Apply Markdown formatting to keywords."""
        valid, bits, _ = self._project.index.scanThis("@"+text)
        if not valid or not bits:
            return ""

        result = ""
        if bits[0] in nwLabels.KEY_NAME:
            result += f"**{self._localLookup(nwLabels.KEY_NAME[bits[0]])}:** "
            if len(bits) > 1:
                result += ", ".join(bits[1:])

        result += "  \n" if style & self.A_Z_BTMMRG else "\n\n"

        return result

# END Class ToMarkdown
