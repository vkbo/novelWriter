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
    Tokenizer.FMT_STRIP: "",
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
    Tokenizer.FMT_STRIP: "",
}


class ToMarkdown(Tokenizer):
    """Core: Markdown Document Writer

    Extend the Tokenizer class to writer Markdown output. It supports
    both Standard Markdown and Extended Markdown. The class also
    supports concatenating novelWriter markup files.
    """

    def __init__(self, project: NWProject) -> None:
        super().__init__(project)
        self._fullMD: list[str] = []
        self._usedNotes: dict[str, int] = {}
        self._extended = True
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

    def setExtendedMarkdown(self, state: bool) -> None:
        """Set the converter to use Extended Markdown formatting."""
        self._extended = state
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

        if self._extended:
            mTags = EXT_MD
            cSkip = nwUnicode.U_MMSP
        else:
            mTags = STD_MD
            cSkip = ""

        lines = []
        for tType, _, tText, tFormat, tStyle in self._tokens:

            if tType == self.T_TEXT:
                tTemp = self._formatText(tText, tFormat, mTags).replace("\n", "  \n")
                lines.append(f"{tTemp}\n\n")

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
        if self._usedNotes:
            tags = EXT_MD if self._extended else STD_MD
            footnotes = self._localLookup("Footnotes")

            lines = []
            lines.append(f"### {footnotes}\n\n")
            for key, index in self._usedNotes.items():
                if content := self._footnotes.get(key):
                    marker = f"{index}. "
                    text = self._formatText(*content, tags)
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
        if self._keepMD:
            self._markdown = [p.replace("\t", spaces) for p in self._markdown]
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
                if data in self._footnotes:
                    index = len(self._usedNotes) + 1
                    self._usedNotes[data] = index
                    md = f"[{index}]"
                else:
                    md = "[ERR]"
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
