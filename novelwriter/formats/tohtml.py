"""
novelWriter – HTML Text Converter
=================================

File History:
Created: 2019-05-07 [0.0.1] ToHtml

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

import json
import logging

from pathlib import Path
from time import time

from novelwriter.common import formatTimeStamp
from novelwriter.constants import nwHeadFmt, nwHtmlUnicode, nwKeyWords, nwLabels
from novelwriter.core.project import NWProject
from novelwriter.formats.shared import BlockFmt, BlockTyp, T_Formats, TextFmt, stripEscape
from novelwriter.formats.tokenizer import Tokenizer
from novelwriter.types import FONT_STYLE, FONT_WEIGHTS, QtHexRgb

logger = logging.getLogger(__name__)

# Each opener tag, with the id of its corresponding closer and tag format
HTML_OPENER: dict[int, tuple[int, str]] = {
    TextFmt.B_B:   (TextFmt.B_E,   "<strong>"),
    TextFmt.I_B:   (TextFmt.I_E,   "<em>"),
    TextFmt.D_B:   (TextFmt.D_E,   "<del>"),
    TextFmt.U_B:   (TextFmt.U_E,   "<span style='text-decoration: underline;'>"),
    TextFmt.M_B:   (TextFmt.M_E,   "<mark>"),
    TextFmt.SUP_B: (TextFmt.SUP_E, "<sup>"),
    TextFmt.SUB_B: (TextFmt.SUB_E, "<sub>"),
    TextFmt.DL_B:  (TextFmt.DL_E,  "<span class='dialog'>"),
    TextFmt.ADL_B: (TextFmt.ADL_E, "<span class='altdialog'>"),
}

# Each closer tag, with the id of its corresponding opener and tag format
HTML_CLOSER: dict[int, tuple[int, str]] = {
    TextFmt.B_E:   (TextFmt.B_B,   "</strong>"),
    TextFmt.I_E:   (TextFmt.I_B,   "</em>"),
    TextFmt.D_E:   (TextFmt.D_B,   "</del>"),
    TextFmt.U_E:   (TextFmt.U_B,   "</span>"),
    TextFmt.M_E:   (TextFmt.M_B,   "</mark>"),
    TextFmt.SUP_E: (TextFmt.SUP_B, "</sup>"),
    TextFmt.SUB_E: (TextFmt.SUB_B, "</sub>"),
    TextFmt.DL_E:  (TextFmt.DL_B,  "</span>"),
    TextFmt.ADL_E: (TextFmt.ADL_B, "</span>"),
}

# Empty HTML tag record
HTML_NONE = (0, "")


class ToHtml(Tokenizer):
    """Core: HTML Document Writer

    Extend the Tokenizer class to writer HTML output. This class is
    also used by the Document Viewer, and Manuscript Build Preview.
    """

    def __init__(self, project: NWProject) -> None:
        super().__init__(project)

        self._cssStyles = True
        self._fullHTML: list[str] = []

        # Internals
        self._trMap = {}
        self._usedNotes: dict[str, int] = {}
        self.setReplaceUnicode(False)

        return

    ##
    #  Properties
    ##

    @property
    def fullHTML(self) -> list[str]:
        return self._fullHTML

    ##
    #  Setters
    ##

    def setStyles(self, cssStyles: bool) -> None:
        """Enable or disable CSS styling. Some elements may still have
        class tags.
        """
        self._cssStyles = cssStyles
        return

    def setReplaceUnicode(self, doReplace: bool) -> None:
        """Set the translation map to either minimal or full unicode for
        html entities replacement.
        """
        # Control characters must always be replaced
        # Angle brackets are replaced later as they are also used in
        # formatting codes
        self._trMap = str.maketrans({"&": "&amp;"})
        if doReplace:
            # Extend to all relevant Unicode characters
            self._trMap.update(str.maketrans(nwHtmlUnicode.U_TO_H))
        return

    ##
    #  Class Methods
    ##

    def getFullResultSize(self) -> int:
        """Return the size of the full HTML result."""
        return sum(len(x) for x in self._fullHTML)

    def doPreProcessing(self) -> None:
        """Extend the auto-replace to also properly encode some unicode
        characters into their respective HTML entities.
        """
        super().doPreProcessing()
        self._text = self._text.translate(self._trMap)
        return

    def doConvert(self) -> None:
        """Convert the list of text tokens into an HTML document."""
        self._result = ""

        if self._isNovel:
            # For story files, we bump the titles one level up
            h1Cl = " class='title'"
            h1 = "h1"
            h2 = "h1"
            h3 = "h2"
            h4 = "h3"
        else:
            h1Cl = ""
            h1 = "h1"
            h2 = "h2"
            h3 = "h3"
            h4 = "h4"

        lines = []
        tHandle = self._handle

        for tType, nHead, tText, tFormat, tStyle in self._blocks:

            # Replace < and > with HTML entities
            if tFormat:
                # If we have formatting, we must recompute the locations
                cText = []
                i = 0
                for c in tText:
                    if c == "<":
                        cText.append("&lt;")
                        tFormat = [(p + 3 if p > i else p, f, k) for p, f, k in tFormat]
                        i += 4
                    elif c == ">":
                        cText.append("&gt;")
                        tFormat = [(p + 3 if p > i else p, f, k) for p, f, k in tFormat]
                        i += 4
                    else:
                        cText.append(c)
                        i += 1
                tText = "".join(cText)
            else:
                # If we don't have formatting, we can do a plain replace
                tText = tText.replace("<", "&lt;").replace(">", "&gt;")

            # Styles
            aStyle = []
            if tStyle is not None and self._cssStyles:
                if tStyle & BlockFmt.LEFT:
                    aStyle.append("text-align: left;")
                elif tStyle & BlockFmt.RIGHT:
                    aStyle.append("text-align: right;")
                elif tStyle & BlockFmt.CENTRE:
                    aStyle.append("text-align: center;")
                elif tStyle & BlockFmt.JUSTIFY:
                    aStyle.append("text-align: justify;")

                if tStyle & BlockFmt.PBB:
                    aStyle.append("page-break-before: always;")
                if tStyle & BlockFmt.PBA:
                    aStyle.append("page-break-after: always;")

                if tStyle & BlockFmt.Z_BTMMRG:
                    aStyle.append("margin-bottom: 0;")
                if tStyle & BlockFmt.Z_TOPMRG:
                    aStyle.append("margin-top: 0;")

                if tStyle & BlockFmt.IND_L:
                    aStyle.append(f"margin-left: {self._blockIndent:.2f}em;")
                if tStyle & BlockFmt.IND_R:
                    aStyle.append(f"margin-right: {self._blockIndent:.2f}em;")
                if tStyle & BlockFmt.IND_T:
                    aStyle.append(f"text-indent: {self._firstWidth:.2f}em;")

            if aStyle:
                stVals = " ".join(aStyle)
                hStyle = f" style='{stVals}'"
            else:
                hStyle = ""

            if self._linkHeadings and tHandle:
                aNm = f"<a name='{tHandle}:T{nHead:04d}'></a>"
            else:
                aNm = ""

            # Process Text Type
            if tType == BlockTyp.TEXT:
                lines.append(f"<p{hStyle}>{self._formatText(tText, tFormat)}</p>\n")

            elif tType == BlockTyp.TITLE:
                tHead = tText.replace(nwHeadFmt.BR, "<br>")
                lines.append(f"<h1 class='title'{hStyle}>{aNm}{tHead}</h1>\n")

            elif tType == BlockTyp.HEAD1:
                tHead = tText.replace(nwHeadFmt.BR, "<br>")
                lines.append(f"<{h1}{h1Cl}{hStyle}>{aNm}{tHead}</{h1}>\n")

            elif tType == BlockTyp.HEAD2:
                tHead = tText.replace(nwHeadFmt.BR, "<br>")
                lines.append(f"<{h2}{hStyle}>{aNm}{tHead}</{h2}>\n")

            elif tType == BlockTyp.HEAD3:
                tHead = tText.replace(nwHeadFmt.BR, "<br>")
                lines.append(f"<{h3}{hStyle}>{aNm}{tHead}</{h3}>\n")

            elif tType == BlockTyp.HEAD4:
                tHead = tText.replace(nwHeadFmt.BR, "<br>")
                lines.append(f"<{h4}{hStyle}>{aNm}{tHead}</{h4}>\n")

            elif tType == BlockTyp.SEP:
                lines.append(f"<p class='sep'{hStyle}>{tText}</p>\n")

            elif tType == BlockTyp.SKIP:
                lines.append(f"<p class='skip'{hStyle}>&nbsp;</p>\n")

            elif tType == BlockTyp.SUMMARY:
                lines.append(f"<p class='synopsis'>{self._formatText(tText, tFormat)}</p>\n")

            elif tType == BlockTyp.COMMENT and self._doComments:
                lines.append(f"<p class='comment'>{self._formatText(tText, tFormat)}</p>\n")

            elif tType == BlockTyp.KEYWORD and self._doKeywords:
                tag, text = self._formatKeywords(tText)
                kClass = f" class='meta meta-{tag}'" if tag else ""
                tTemp = f"<p{kClass}{hStyle}>{text}</p>\n"
                lines.append(tTemp)

        self._result = "".join(lines)
        self._fullHTML.append(self._result)

        return

    def appendFootnotes(self) -> None:
        """Append the footnotes in the buffer."""
        if self._usedNotes:
            footnotes = self._localLookup("Footnotes")

            lines = []
            lines.append(f"<h3>{footnotes}</h3>\n")
            lines.append("<ol>\n")
            for key, index in self._usedNotes.items():
                if content := self._footnotes.get(key):
                    text = self._formatText(*content)
                    lines.append(f"<li id='footnote_{index}'><p>{text}</p></li>\n")
            lines.append("</ol>\n")

            result = "".join(lines)
            self._result += result
            self._fullHTML.append(result)

        return

    def saveDocument(self, path: Path) -> None:
        """Save the data to an HTML file."""
        if path.suffix.lower() == ".json":
            ts = time()
            data = {
                "meta": {
                    "projectName": self._project.data.name,
                    "novelAuthor": self._project.data.author,
                    "buildTime": int(ts),
                    "buildTimeStr": formatTimeStamp(ts),
                },
                "text": {
                    "css": self.getStyleSheet(),
                    "html": [t.replace("\t", "&#09;").rstrip().split("\n") for t in self.fullHTML],
                }
            }
            with open(path, mode="w", encoding="utf-8") as fObj:
                json.dump(data, fObj, indent=2)

        else:
            with open(path, mode="w", encoding="utf-8") as fObj:
                fObj.write((
                    "<!DOCTYPE html>\n"
                    "<html>\n"
                    "<head>\n"
                    "<meta charset='utf-8'>\n"
                    "<title>{title:s}</title>\n"
                    "</head>\n"
                    "<style>\n"
                    "{style:s}\n"
                    "</style>\n"
                    "<body>\n"
                    "<article>\n"
                    "{body:s}\n"
                    "</article>\n"
                    "</body>\n"
                    "</html>\n"
                ).format(
                    title=self._project.data.name,
                    style="\n".join(self.getStyleSheet()),
                    body=("".join(self._fullHTML)).replace("\t", "&#09;").rstrip(),
                ))

        logger.info("Wrote file: %s", path)

        return

    def replaceTabs(self, nSpaces: int = 8, spaceChar: str = "&nbsp;") -> None:
        """Replace tabs with spaces in the html."""
        htmlText = []
        tabSpace = spaceChar*nSpaces
        for aLine in self._fullHTML:
            htmlText.append(aLine.replace("\t", tabSpace))

        self._fullHTML = htmlText
        return

    def getStyleSheet(self) -> list[str]:
        """Generate a stylesheet for the current settings."""
        if not self._cssStyles:
            return []

        mScale = self._lineHeight/1.15
        tColor = self._theme.text.name(QtHexRgb)
        hColor = self._theme.head.name(QtHexRgb) if self._colorHeads else tColor

        styles = []
        font = self._textFont
        styles.append((
            "body {{"
            "color: {0:s}; font-family: '{1:s}'; font-size: {2:d}pt; "
            "font-weight: {3:d}; font-style: {4:s};"
            "}}"
        ).format(
            tColor, font.family(), font.pointSize(),
            FONT_WEIGHTS.get(font.weight(), 400),
            FONT_STYLE.get(font.style(), "normal"),
        ))
        styles.append((
            "p {{"
            "text-align: {0}; line-height: {1:d}%; "
            "margin-top: {2:.2f}em; margin-bottom: {3:.2f}em;"
            "}}"
        ).format(
            self._defaultAlign,
            round(100 * self._lineHeight),
            mScale * self._marginText[0],
            mScale * self._marginText[1],
        ))
        styles.append((
            "h1 {{"
            "color: {0:s}; "
            "page-break-after: avoid; "
            "margin-top: {1:.2f}em; "
            "margin-bottom: {2:.2f}em;"
            "}}"
        ).format(
            hColor, mScale * self._marginHead1[0], mScale * self._marginHead1[1]
        ))
        styles.append((
            "h2 {{"
            "color: {0:s}; "
            "page-break-after: avoid; "
            "margin-top: {1:.2f}em; "
            "margin-bottom: {2:.2f}em;"
            "}}"
        ).format(
            hColor, mScale * self._marginHead2[0], mScale * self._marginHead2[1]
        ))
        styles.append((
            "h3 {{"
            "color: {0:s}; "
            "page-break-after: avoid; "
            "margin-top: {1:.2f}em; "
            "margin-bottom: {2:.2f}em;"
            "}}"
        ).format(
            hColor, mScale * self._marginHead3[0], mScale * self._marginHead3[1]
        ))
        styles.append((
            "h4 {{"
            "color: {0:s}; "
            "page-break-after: avoid; "
            "margin-top: {1:.2f}em; "
            "margin-bottom: {2:.2f}em;"
            "}}"
        ).format(
            hColor, mScale * self._marginHead4[0], mScale * self._marginHead4[1]
        ))
        styles.append((
            ".title {{"
            "font-size: 2.5em; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale * self._marginTitle[0], mScale * self._marginTitle[1]
        ))
        styles.append((
            ".sep, .skip {{"
            "text-align: center; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale, mScale
        ))

        styles.append("a {color: rgb(66, 113, 174);}")
        styles.append("mark {background: rgb(255, 255, 166);}")
        styles.append(".keyword {color: rgb(245, 135, 31); font-weight: bold;}")
        styles.append(".break {text-align: left;}")
        styles.append(".synopsis {font-style: italic;}")
        styles.append(".comment {font-style: italic; color: rgb(100, 100, 100);}")
        styles.append(".dialog {color: rgb(66, 113, 174);}")
        styles.append(".altdialog {color: rgb(129, 55, 9);}")

        return styles

    ##
    #  Internal Functions
    ##

    def _formatText(self, text: str, tFmt: T_Formats) -> str:
        """Apply formatting tags to text."""
        temp = text

        # Build a list of all html tags that need to be inserted in the text.
        # This is done in the forward direction, and a tag is only opened if it
        # isn't already open, and only closed if it has previously been opened.
        tags: list[tuple[int, str]] = []
        state = dict.fromkeys(HTML_OPENER, False)
        for pos, fmt, data in tFmt:
            if m := HTML_OPENER.get(fmt):
                if not state.get(fmt, True):
                    tags.append((pos, m[1]))
                    state[fmt] = True
            elif m := HTML_CLOSER.get(fmt):
                if state.get(m[0], False):
                    tags.append((pos, m[1]))
                    state[m[0]] = False
            elif fmt == TextFmt.FNOTE:
                if data in self._footnotes:
                    index = len(self._usedNotes) + 1
                    self._usedNotes[data] = index
                    tags.append((pos, f"<sup><a href='#footnote_{index}'>{index}</a></sup>"))
                else:
                    tags.append((pos, "<sup>ERR</sup>"))

        # Check all format types and close any tag that is still open. This
        # ensures that unclosed tags don't spill over to the next paragraph.
        end = len(text)
        for opener, active in state.items():
            if active:
                closer = HTML_OPENER.get(opener, HTML_NONE)[0]
                tags.append((end, HTML_CLOSER.get(closer, HTML_NONE)[1]))

        # Insert all tags at their correct position, starting from the back.
        # The reverse order ensures that the positions are not shifted while we
        # insert tags.
        for pos, tag in reversed(tags):
            temp = f"{temp[:pos]}{tag}{temp[pos:]}"

        # Replace all line breaks with proper HTML break tags
        temp = temp.replace("\n", "<br>")

        return stripEscape(temp)

    def _formatKeywords(self, text: str) -> tuple[str, str]:
        """Apply HTML formatting to keywords."""
        valid, bits, _ = self._project.index.scanThis("@"+text)
        if not valid or not bits or bits[0] not in nwLabels.KEY_NAME:
            return "", ""

        result = f"<span class='keyword'>{self._localLookup(nwLabels.KEY_NAME[bits[0]])}:</span> "
        if len(bits) > 1:
            if bits[0] == nwKeyWords.TAG_KEY:
                one, two = self._project.index.parseValue(bits[1])
                result += f"<a class='tag' name='tag_{one}'>{one}</a>"
                if two:
                    result += f" | <span class='optional'>{two}</a>"
            else:
                result += ", ".join(
                    f"<a class='tag' href='#tag_{t}'>{t}</a>" for t in bits[1:]
                )

        return bits[0][1:], result
