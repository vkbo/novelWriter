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

from novelwriter import CONFIG
from novelwriter.common import formatTimeStamp
from novelwriter.constants import nwHeadFmt, nwHtmlUnicode, nwKeyWords, nwLabels
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import T_Formats, Tokenizer, stripEscape

logger = logging.getLogger(__name__)

HTML4_TAGS = {
    Tokenizer.FMT_B_B: "<b>",
    Tokenizer.FMT_B_E: "</b>",
    Tokenizer.FMT_I_B: "<i>",
    Tokenizer.FMT_I_E: "</i>",
    Tokenizer.FMT_D_B: "<span style='text-decoration: line-through;'>",
    Tokenizer.FMT_D_E: "</span>",
    Tokenizer.FMT_U_B: "<u>",
    Tokenizer.FMT_U_E: "</u>",
    Tokenizer.FMT_M_B: "<mark>",
    Tokenizer.FMT_M_E: "</mark>",
    Tokenizer.FMT_SUP_B: "<sup>",
    Tokenizer.FMT_SUP_E: "</sup>",
    Tokenizer.FMT_SUB_B: "<sub>",
    Tokenizer.FMT_SUB_E: "</sub>",
    Tokenizer.FMT_STRIP: "",
}

HTML5_TAGS = {
    Tokenizer.FMT_B_B: "<strong>",
    Tokenizer.FMT_B_E: "</strong>",
    Tokenizer.FMT_I_B: "<em>",
    Tokenizer.FMT_I_E: "</em>",
    Tokenizer.FMT_D_B: "<del>",
    Tokenizer.FMT_D_E: "</del>",
    Tokenizer.FMT_U_B: "<span style='text-decoration: underline;'>",
    Tokenizer.FMT_U_E: "</span>",
    Tokenizer.FMT_M_B: "<mark>",
    Tokenizer.FMT_M_E: "</mark>",
    Tokenizer.FMT_SUP_B: "<sup>",
    Tokenizer.FMT_SUP_E: "</sup>",
    Tokenizer.FMT_SUB_B: "<sub>",
    Tokenizer.FMT_SUB_E: "</sub>",
    Tokenizer.FMT_STRIP: "",
}


class ToHtml(Tokenizer):
    """Core: HTML Document Writer

    Extend the Tokenizer class to writer HTML output. This class is
    also used by the Document Viewer, and Manuscript Build Preview.
    """

    M_PREVIEW = 0  # Tweak output for the DocViewer
    M_EXPORT  = 1  # Tweak output for saving to HTML or printing
    M_EBOOK   = 2  # Tweak output for converting to epub

    def __init__(self, project: NWProject) -> None:
        super().__init__(project)

        self._genMode = self.M_EXPORT
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

    def setPreview(self, state: bool) -> None:
        """Set to preview generator mode."""
        self._genMode = self.M_PREVIEW if state else self.M_EXPORT
        return

    def setStyles(self, cssStyles: bool) -> None:
        """Enable or disable CSS styling. Some elements may still have
        class tags.
        """
        self._cssStyles = cssStyles
        return

    def setTextIndent(self, textIndent: float) -> None:
        """Set css text-indent value."""

        self._textIndent = textIndent
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

        hTags = HTML4_TAGS if self._genMode == self.M_PREVIEW else HTML5_TAGS
        if self._isNovel and self._genMode != self.M_PREVIEW:
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

        para = []
        lines = []
        pStyle = None
        tHandle = self._handle

        for tType, nHead, tText, tFormat, tStyle in self._tokens:

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
                if tStyle & self.A_LEFT:
                    aStyle.append("text-align: left;")
                elif tStyle & self.A_RIGHT:
                    aStyle.append("text-align: right;")
                elif tStyle & self.A_CENTRE:
                    aStyle.append("text-align: center;")
                elif tStyle & self.A_JUSTIFY:
                    aStyle.append("text-align: justify;")

                if tStyle & self.A_PBB:
                    aStyle.append("page-break-before: always;")

                if tStyle & self.A_PBA:
                    aStyle.append("page-break-after: always;")

                if tStyle & self.A_Z_BTMMRG:
                    aStyle.append("margin-bottom: 0;")
                if tStyle & self.A_Z_TOPMRG:
                    aStyle.append("margin-top: 0;")

                if tStyle & self.A_IND_L:
                    aStyle.append(f"margin-left: {CONFIG.tabWidth:d}px;")
                if tStyle & self.A_IND_R:
                    aStyle.append(f"margin-right: {CONFIG.tabWidth:d}px;")

            if len(aStyle) > 0:
                stVals = " ".join(aStyle)
                hStyle = f" style='{stVals}'"
            else:
                hStyle = ""

            if self._linkHeadings and tHandle:
                aNm = f"<a name='{tHandle}:T{nHead:04d}'></a>"
            else:
                aNm = ""

            # Process Text Type
            if tType == self.T_EMPTY:
                if pStyle is None:
                    pStyle = ""
                if len(para) > 1 and self._cssStyles:
                    pClass = " class='break'"
                else:
                    pClass = ""
                if len(para) > 0:
                    tTemp = "<br/>".join(para)
                    lines.append(f"<p{pClass+pStyle}>{tTemp.rstrip()}</p>\n")
                para = []
                pStyle = None

            elif tType == self.T_TITLE:
                tHead = tText.replace(nwHeadFmt.BR, "<br/>")
                lines.append(f"<h1 class='title'{hStyle}>{aNm}{tHead}</h1>\n")

            elif tType == self.T_HEAD1:
                tHead = tText.replace(nwHeadFmt.BR, "<br/>")
                lines.append(f"<{h1}{h1Cl}{hStyle}>{aNm}{tHead}</{h1}>\n")

            elif tType == self.T_HEAD2:
                tHead = tText.replace(nwHeadFmt.BR, "<br/>")
                lines.append(f"<{h2}{hStyle}>{aNm}{tHead}</{h2}>\n")

            elif tType == self.T_HEAD3:
                tHead = tText.replace(nwHeadFmt.BR, "<br/>")
                lines.append(f"<{h3}{hStyle}>{aNm}{tHead}</{h3}>\n")

            elif tType == self.T_HEAD4:
                tHead = tText.replace(nwHeadFmt.BR, "<br/>")
                lines.append(f"<{h4}{hStyle}>{aNm}{tHead}</{h4}>\n")

            elif tType == self.T_SEP:
                lines.append(f"<p class='sep'{hStyle}>{tText}</p>\n")

            elif tType == self.T_SKIP:
                lines.append(f"<p class='skip'{hStyle}>&nbsp;</p>\n")

            elif tType == self.T_TEXT:
                if pStyle is None:
                    pStyle = hStyle
                para.append(self._formatText(tText, tFormat, hTags).rstrip())

            elif tType == self.T_SYNOPSIS and self._doSynopsis:
                lines.append(self._formatSynopsis(self._formatText(tText, tFormat, hTags), True))

            elif tType == self.T_SHORT and self._doSynopsis:
                lines.append(self._formatSynopsis(self._formatText(tText, tFormat, hTags), False))

            elif tType == self.T_COMMENT and self._doComments:
                lines.append(self._formatComments(self._formatText(tText, tFormat, hTags)))

            elif tType == self.T_KEYWORD and self._doKeywords:
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
            tags = HTML4_TAGS if self._genMode == self.M_PREVIEW else HTML5_TAGS
            footnotes = self._localLookup("Footnotes")

            lines = []
            lines.append(f"<h3>{footnotes}</h3>\n")
            lines.append("<ol>\n")
            for key, index in self._usedNotes.items():
                if content := self._footnotes.get(key):
                    text = self._formatText(*content, tags)
                    lines.append(f"<li id='footnote_{index}'><p>{text}</p></li>\n")
            lines.append("</ol>\n")

            result = "".join(lines)
            self._result += result
            self._fullHTML.append(result)

        return

    def saveHtml5(self, path: str | Path) -> None:
        """Save the data to an HTML file."""
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

    def saveHtmlJson(self, path: str | Path) -> None:
        """Save the data to a JSON file."""
        timeStamp = time()
        data = {
            "meta": {
                "projectName": self._project.data.name,
                "novelAuthor": self._project.data.author,
                "buildTime": int(timeStamp),
                "buildTimeStr": formatTimeStamp(timeStamp),
            },
            "text": {
                "css": self.getStyleSheet(),
                "html": [t.replace("\t", "&#09;").rstrip().split("\n") for t in self.fullHTML],
            }
        }
        with open(path, mode="w", encoding="utf-8") as fObj:
            json.dump(data, fObj, indent=2)
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

        styles = []
        styles.append("body {{font-family: '{0:s}'; font-size: {1:d}pt;}}".format(
            self._textFont, self._textSize
        ))
        styles.append((
            "p {{"
            "text-align: {0}; line-height: {1:d}%; "
            "margin-top: {2:.2f}em; margin-bottom: {3:.2f}em; "
            "text-indent: {4:.1f}em;"
            "}}"
        ).format(
            "justify" if self._doJustify else "left",
            round(100 * self._lineHeight),
            mScale * self._marginText[0],
            mScale * self._marginText[1],
            self._textIndent
        ))
        styles.append((
            "h1 {{"
            "color: rgb(66, 113, 174); "
            "page-break-after: avoid; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale * self._marginHead1[0], mScale * self._marginHead1[1]
        ))
        styles.append((
            "h2 {{"
            "color: rgb(66, 113, 174); "
            "page-break-after: avoid; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale * self._marginHead2[0], mScale * self._marginHead2[1]
        ))
        styles.append((
            "h3 {{"
            "color: rgb(50, 50, 50); "
            "page-break-after: avoid; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale * self._marginHead3[0], mScale * self._marginHead3[1]
        ))
        styles.append((
            "h4 {{"
            "color: rgb(50, 50, 50); "
            "page-break-after: avoid; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale * self._marginHead4[0], mScale * self._marginHead4[1]
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

        return styles

    ##
    #  Internal Functions
    ##

    def _formatText(self, text: str, tFmt: T_Formats, tags: dict[int, str]) -> str:
        """Apply formatting tags to text."""
        temp = text
        for pos, fmt, data in reversed(tFmt):
            html = ""
            if fmt == self.FMT_FNOTE:
                if data in self._footnotes:
                    index = len(self._usedNotes) + 1
                    self._usedNotes[data] = index
                    html = f"<sup><a href='#footnote_{index}'>{index}</a></sup>"
                else:
                    html = "<sup>ERR</sup>"
            else:
                html = tags.get(fmt, "ERR")
            temp = f"{temp[:pos]}{html}{temp[pos:]}"
        return stripEscape(temp)

    def _formatSynopsis(self, text: str, synopsis: bool) -> str:
        """Apply HTML formatting to synopsis."""
        if synopsis:
            sSynop = self._localLookup("Synopsis")
        else:
            sSynop = self._localLookup("Short Description")
        if self._genMode == self.M_PREVIEW:
            return f"<p class='note'><span class='modifier'>{sSynop}:</span> {text}</p>\n"
        else:
            return f"<p class='synopsis'><strong>{sSynop}:</strong> {text}</p>\n"

    def _formatComments(self, text: str) -> str:
        """Apply HTML formatting to comments."""
        if self._genMode == self.M_PREVIEW:
            return f"<p class='comment'>{text}</p>\n"
        else:
            sComm = self._localLookup("Comment")
            return f"<p class='comment'><strong>{sComm}:</strong> {text}</p>\n"

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
                if self._genMode == self.M_PREVIEW:
                    result += ", ".join(
                        f"<a class='tag' href='#{bits[0][1:]}={t}'>{t}</a>" for t in bits[1:]
                    )
                else:
                    result += ", ".join(
                        f"<a class='tag' href='#tag_{t}'>{t}</a>" for t in bits[1:]
                    )

        return bits[0][1:], result

# END Class ToHtml
