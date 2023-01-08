"""
novelWriter – HTML Text Converter
=================================
Extends the Tokenizer class to generate HTML output

File History:
Created: 2019-05-07 [0.0.1]

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

from novelwriter.constants import nwKeyWords, nwLabels, nwHtmlUnicode
from novelwriter.core.tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class ToHtml(Tokenizer):

    M_PREVIEW = 0  # Tweak output for the DocViewer
    M_EXPORT  = 1  # Tweak output for saving to HTML or printing
    M_EBOOK   = 2  # Tweak output for converting to epub

    def __init__(self, theProject):
        super().__init__(theProject)

        self._genMode = self.M_EXPORT
        self._cssStyles = True
        self._fullHTML = []

        # Internals
        self._trMap = {}
        self.setReplaceUnicode(False)

        return

    ##
    #  Properties
    ##

    @property
    def fullHTML(self):
        return self._fullHTML

    ##
    #  Setters
    ##

    def setPreview(self, doComments, doSynopsis):
        """If we're using this class to generate markdown preview, we
        need to make a few changes to formatting, which is managed by
        these flags.
        """
        self._genMode = self.M_PREVIEW
        self._doKeywords = True
        self._doComments = doComments
        self._doSynopsis = doSynopsis
        return

    def setStyles(self, cssStyles):
        """Enable/disable CSS styling. Some elements may still have
        class tags.
        """
        self._cssStyles = cssStyles
        return

    def setReplaceUnicode(self, doReplace):
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

    def getFullResultSize(self):
        """Return the size of the full HTML result.
        """
        return sum([len(x) for x in self._fullHTML])

    def doPreProcessing(self):
        """Extend the auto-replace to also properly encode some unicode
        characters into their respective HTML entities.
        """
        super().doPreProcessing()
        self._theText = self._theText.translate(self._trMap)
        return

    def doConvert(self):
        """Convert the list of text tokens into a HTML document saved
        to theResult.
        """
        if self._genMode == self.M_PREVIEW:
            htmlTags = {  # HTML4 + CSS2 (for Qt)
                self.FMT_B_B: "<b>",
                self.FMT_B_E: "</b>",
                self.FMT_I_B: "<i>",
                self.FMT_I_E: "</i>",
                self.FMT_D_B: "<span style='text-decoration: line-through;'>",
                self.FMT_D_E: "</span>",
            }
        else:
            htmlTags = {  # HTML5 (for export)
                self.FMT_B_B: "<strong>",
                self.FMT_B_E: "</strong>",
                self.FMT_I_B: "<em>",
                self.FMT_I_E: "</em>",
                self.FMT_D_B: "<del>",
                self.FMT_D_E: "</del>",
            }

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

        self._theResult = ""

        thisPar = []
        parStyle = None
        tmpResult = []

        for tType, tLine, tText, tFormat, tStyle in self._theTokens:

            # Replace < and > with HTML entities
            if tFormat:
                # If we have formatting, we must recompute the locations
                cText = []
                i = 0
                for c in tText:
                    if c == "<":
                        cText.append("&lt;")
                        tFormat = [[a + 3 if a > i else a, b, c] for a, b, c in tFormat]
                        i += 4
                    elif c == ">":
                        cText.append("&gt;")
                        tFormat = [[a + 3 if a > i else a, b, c] for a, b, c in tFormat]
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
                    aStyle.append(f"margin-left: {self.mainConf.tabWidth:d}px;")
                if tStyle & self.A_IND_R:
                    aStyle.append(f"margin-right: {self.mainConf.tabWidth:d}px;")

            if len(aStyle) > 0:
                stVals = " ".join(aStyle)
                hStyle = f" style='{stVals}'"
            else:
                hStyle = ""

            if self._linkHeaders:
                aNm = f"<a name='T{tLine:06d}'></a>"
            else:
                aNm = ""

            # Process Text Type
            if tType == self.T_EMPTY:
                if parStyle is None:
                    parStyle = ""
                if len(thisPar) > 1 and self._cssStyles:
                    parClass = " class='break'"
                else:
                    parClass = ""
                if len(thisPar) > 0:
                    tTemp = "<br/>".join(thisPar)
                    tmpResult.append(f"<p{parClass+parStyle}>{tTemp.rstrip()}</p>\n")
                thisPar = []
                parStyle = None

            elif tType == self.T_TITLE:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append(f"<h1 class='title'{hStyle}>{aNm}{tHead}</h1>\n")

            elif tType == self.T_UNNUM:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append(f"<{h2}{hStyle}>{aNm}{tHead}</{h2}>\n")

            elif tType == self.T_HEAD1:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append(f"<{h1}{h1Cl}{hStyle}>{aNm}{tHead}</{h1}>\n")

            elif tType == self.T_HEAD2:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append(f"<{h2}{hStyle}>{aNm}{tHead}</{h2}>\n")

            elif tType == self.T_HEAD3:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append(f"<{h3}{hStyle}>{aNm}{tHead}</{h3}>\n")

            elif tType == self.T_HEAD4:
                tHead = tText.replace(r"\\", "<br/>")
                tmpResult.append(f"<{h4}{hStyle}>{aNm}{tHead}</{h4}>\n")

            elif tType == self.T_SEP:
                tmpResult.append(f"<p class='sep'{hStyle}>{tText}</p>\n")

            elif tType == self.T_SKIP:
                tmpResult.append(f"<p class='skip'{hStyle}>&nbsp;</p>\n")

            elif tType == self.T_TEXT:
                tTemp = tText
                if parStyle is None:
                    parStyle = hStyle
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos] + htmlTags[xFmt] + tTemp[xPos+xLen:]
                thisPar.append(tTemp.rstrip())

            elif tType == self.T_SYNOPSIS and self._doSynopsis:
                tmpResult.append(self._formatSynopsis(tText))

            elif tType == self.T_COMMENT and self._doComments:
                tmpResult.append(self._formatComments(tText))

            elif tType == self.T_KEYWORD and self._doKeywords:
                tTemp = f"<p{hStyle}>{self._formatKeywords(tText)}</p>\n"
                tmpResult.append(tTemp)

        self._theResult = "".join(tmpResult)
        tmpResult = []

        if self._genMode != self.M_PREVIEW:
            self._fullHTML.append(self._theResult)

        return

    def saveHTML5(self, savePath):
        """Save the data to an .html file.
        """
        with open(savePath, mode="w", encoding="utf-8") as outFile:
            theStyle = self.getStyleSheet()
            theStyle.append("article {width: 800px; margin: 40px auto;}")
            bodyText = "".join(self._fullHTML)
            bodyText = bodyText.replace("\t", "&#09;").rstrip()

            theHtml = (
                "<!DOCTYPE html>\n"
                "<html>\n"
                "<head>\n"
                "<meta charset='utf-8'>\n"
                "<title>{projTitle:s}</title>\n"
                "</head>\n"
                "<style>\n"
                "{htmlStyle:s}\n"
                "</style>\n"
                "<body>\n"
                "<article>\n"
                "{bodyText:s}\n"
                "</article>\n"
                "</body>\n"
                "</html>\n"
            ).format(
                projTitle=self.theProject.data.name,
                htmlStyle="\n".join(theStyle),
                bodyText=bodyText,
            )
            outFile.write(theHtml)

        return

    def replaceTabs(self, nSpaces=8, spaceChar="&nbsp;"):
        """Replace tabs with spaces in the html.
        """
        htmlText = []
        tabSpace = spaceChar*nSpaces
        for aLine in self._fullHTML:
            htmlText.append(aLine.replace("\t", tabSpace))

        self._fullHTML = htmlText
        return

    def getStyleSheet(self):
        """Generate a stylesheet appropriate for the current settings.
        """
        theStyles = []
        if not self._cssStyles:
            return theStyles

        mScale = self._lineHeight/1.15
        textAlign = "justify" if self._doJustify else "left"

        theStyles.append("body {{font-family: '{0:s}'; font-size: {1:d}pt;}}".format(
            self._textFont, self._textSize
        ))
        theStyles.append((
            "p {{"
            "text-align: {0}; line-height: {1:d}%; "
            "margin-top: {2:.2f}em; margin-bottom: {3:.2f}em;"
            "}}"
        ).format(
            textAlign,
            round(100 * self._lineHeight),
            mScale * self._marginText[0],
            mScale * self._marginText[1],
        ))
        theStyles.append((
            "h1 {{"
            "color: rgb(66, 113, 174); "
            "page-break-after: avoid; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale * self._marginHead1[0], mScale * self._marginHead1[1]
        ))
        theStyles.append((
            "h2 {{"
            "color: rgb(66, 113, 174); "
            "page-break-after: avoid; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale * self._marginHead2[0], mScale * self._marginHead2[1]
        ))
        theStyles.append((
            "h3 {{"
            "color: rgb(50, 50, 50); "
            "page-break-after: avoid; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale * self._marginHead3[0], mScale * self._marginHead3[1]
        ))
        theStyles.append((
            "h4 {{"
            "color: rgb(50, 50, 50); "
            "page-break-after: avoid; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale * self._marginHead4[0], mScale * self._marginHead4[1]
        ))
        theStyles.append((
            ".title {{"
            "font-size: 2.5em; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale * self._marginTitle[0], mScale * self._marginTitle[1]
        ))
        theStyles.append((
            ".sep, .skip {{"
            "text-align: center; "
            "margin-top: {0:.2f}em; "
            "margin-bottom: {1:.2f}em;"
            "}}"
        ).format(
            mScale, mScale
        ))

        theStyles.append("a {color: rgb(66, 113, 174);}")
        theStyles.append(".tags {color: rgb(245, 135, 31); font-weight: bold;}")
        theStyles.append(".break {text-align: left;}")
        theStyles.append(".synopsis {font-style: italic;}")
        theStyles.append(".comment {font-style: italic; color: rgb(100, 100, 100);}")

        return theStyles

    ##
    #  Internal Functions
    ##

    def _formatSynopsis(self, tText):
        """Apply HTML formatting to synopsis.
        """
        if self._genMode == self.M_PREVIEW:
            sSynop = self._trSynopsis
            return f"<p class='comment'><span class='synopsis'>{sSynop}:</span> {tText}</p>\n"
        else:
            sSynop = self._localLookup("Synopsis")
            return f"<p class='synopsis'><strong>{sSynop}:</strong> {tText}</p>\n"

    def _formatComments(self, tText):
        """Apply HTML formatting to comments.
        """
        if self._genMode == self.M_PREVIEW:
            return f"<p class='comment'>{tText}</p>\n"
        else:
            sComm = self._localLookup("Comment")
            return f"<p class='comment'><strong>{sComm}:</strong> {tText}</p>\n"

    def _formatKeywords(self, tText):
        """Apply HTML formatting to keywords.
        """
        isValid, theBits, _ = self.theProject.index.scanThis("@"+tText)
        if not isValid or not theBits:
            return ""

        retText = ""
        refTags = []
        if theBits[0] in nwLabels.KEY_NAME:
            retText += f"<span class='tags'>{nwLabels.KEY_NAME[theBits[0]]}:</span> "
            if len(theBits) > 1:
                if theBits[0] == nwKeyWords.TAG_KEY:
                    retText += f"<a name='tag_{theBits[1]}'>{theBits[1]}</a>"
                else:
                    if self._genMode == self.M_PREVIEW:
                        for tTag in theBits[1:]:
                            refTags.append(f"<a href='#{theBits[0][1:]}={tTag}'>{tTag}</a>")
                        retText += ", ".join(refTags)
                    else:
                        for tTag in theBits[1:]:
                            refTags.append(f"<a href='#tag_{tTag}'>{tTag}</a>")
                        retText += ", ".join(refTags)

        return retText

# END Class ToHtml
