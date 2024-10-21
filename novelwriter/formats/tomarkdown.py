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
from novelwriter.formats.tokenizer import BlockFmt, BlockTyp, T_Formats, TextFmt, Tokenizer

logger = logging.getLogger(__name__)


# Standard Markdown
STD_MD = {
    TextFmt.B_B: "**",
    TextFmt.B_E: "**",
    TextFmt.I_B: "_",
    TextFmt.I_E: "_",
    TextFmt.D_B: "",
    TextFmt.D_E: "",
    TextFmt.U_B: "",
    TextFmt.U_E: "",
    TextFmt.M_B: "",
    TextFmt.M_E: "",
    TextFmt.SUP_B: "",
    TextFmt.SUP_E: "",
    TextFmt.SUB_B: "",
    TextFmt.SUB_E: "",
    TextFmt.STRIP: "",
}

# Extended Markdown
EXT_MD = {
    TextFmt.B_B: "**",
    TextFmt.B_E: "**",
    TextFmt.I_B: "_",
    TextFmt.I_E: "_",
    TextFmt.D_B: "~~",
    TextFmt.D_E: "~~",
    TextFmt.U_B: "",
    TextFmt.U_E: "",
    TextFmt.M_B: "==",
    TextFmt.M_E: "==",
    TextFmt.SUP_B: "^",
    TextFmt.SUP_E: "^",
    TextFmt.SUB_B: "~",
    TextFmt.SUB_E: "~",
    TextFmt.STRIP: "",
}


class ToMarkdown(Tokenizer):
    """Core: Markdown Document Writer

    Extend the Tokenizer class to writer Markdown output. It supports
    both Standard Markdown and Extended Markdown. The class also
    supports concatenating novelWriter markup files.
    """

    def __init__(self, project: NWProject, extended: bool) -> None:
        super().__init__(project)
        self._fullMD: list[str] = []
        self._usedNotes: dict[str, int] = {}
        self._extended = extended
        return

    ##
    #  Properties
    ##

    @property
    def fullMD(self) -> list[str]:
        """Return the markdown as a list."""
        return self._fullMD

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

            if tType == BlockTyp.TEXT:
                tTemp = self._formatText(tText, tFormat, mTags).replace("\n", "  \n")
                lines.append(f"{tTemp}\n\n")

            elif tType == BlockTyp.TITLE:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                lines.append(f"# {tHead}\n\n")

            elif tType == BlockTyp.HEAD1:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                lines.append(f"# {tHead}\n\n")

            elif tType == BlockTyp.HEAD2:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                lines.append(f"## {tHead}\n\n")

            elif tType == BlockTyp.HEAD3:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                lines.append(f"### {tHead}\n\n")

            elif tType == BlockTyp.HEAD4:
                tHead = tText.replace(nwHeadFmt.BR, "\n")
                lines.append(f"#### {tHead}\n\n")

            elif tType == BlockTyp.SEP:
                lines.append(f"{tText}\n\n")

            elif tType == BlockTyp.SKIP:
                lines.append(f"{cSkip}\n\n")

            elif tType == BlockTyp.SYNOPSIS and self._doSynopsis:
                label = self._localLookup("Synopsis")
                lines.append(f"**{label}:** {self._formatText(tText, tFormat, mTags)}\n\n")

            elif tType == BlockTyp.SHORT and self._doSynopsis:
                label = self._localLookup("Short Description")
                lines.append(f"**{label}:** {self._formatText(tText, tFormat, mTags)}\n\n")

            elif tType == BlockTyp.COMMENT and self._doComments:
                label = self._localLookup("Comment")
                lines.append(f"**{label}:** {self._formatText(tText, tFormat, mTags)}\n\n")

            elif tType == BlockTyp.KEYWORD and self._doKeywords:
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

    def saveDocument(self, path: Path) -> None:
        """Save the data to a plain text file."""
        with open(path, mode="w", encoding="utf-8") as outFile:
            outFile.write("".join(self._fullMD))
        logger.info("Wrote file: %s", path)
        return

    def replaceTabs(self, nSpaces: int = 8, spaceChar: str = " ") -> None:
        """Replace tabs with spaces."""
        spaces = spaceChar*nSpaces
        self._fullMD = [p.replace("\t", spaces) for p in self._fullMD]
        return

    ##
    #  Internal Functions
    ##

    def _formatText(self, text: str, tFmt: T_Formats, tags: dict[TextFmt, str]) -> str:
        """Apply formatting tags to text."""
        temp = text
        for pos, fmt, data in reversed(tFmt):
            md = ""
            if fmt == TextFmt.FNOTE:
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

    def _formatKeywords(self, text: str, style: BlockFmt) -> str:
        """Apply Markdown formatting to keywords."""
        valid, bits, _ = self._project.index.scanThis("@"+text)
        if not valid or not bits:
            return ""

        result = ""
        if bits[0] in nwLabels.KEY_NAME:
            result += f"**{self._localLookup(nwLabels.KEY_NAME[bits[0]])}:** "
            if len(bits) > 1:
                result += ", ".join(bits[1:])

        result += "  \n" if style & BlockFmt.Z_BTMMRG else "\n\n"

        return result
