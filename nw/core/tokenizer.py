# -*- coding: utf-8 -*-
"""novelWriter Text Tokenizer

 novelWriter – Text Tokenizer
==============================
 Splits a piece of nW markdown text into its elements

 File History:
 Created: 2019-05-05 [0.0.1]

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

import logging
import re
import nw

from operator import itemgetter
from PyQt5.QtCore import QRegularExpression

from nw.core.document import NWDoc
from nw.core.tools import numberToWord
from nw.constants import nwItemLayout

logger = logging.getLogger(__name__)

class Tokenizer():

    FMT_B_B   =  1 # Begin bold
    FMT_B_E   =  2 # End bold
    FMT_I_B   =  3 # Begin italics
    FMT_I_E   =  4 # End italics
    FMT_U_B   =  5 # Begin underline
    FMT_U_E   =  6 # End underline

    T_EMPTY   =  1 # Empty line (new paragraph)
    T_COMMENT =  2 # Comment line
    T_KEYWORD =  3 # Command line
    T_HEAD1   =  4 # Header 1 (title)
    T_HEAD2   =  5 # Header 2 (chapter)
    T_HEAD3   =  6 # Header 3 (scene)
    T_HEAD4   =  7 # Header 4
    T_TEXT    =  8 # Text line
    T_SEP     =  9 # Scene separator
    T_SKIP    = 10 # Paragraph break
    T_PBREAK  = 11 # Page break

    A_LEFT    =  1 # Left aligned
    A_RIGHT   =  2 # Right aligned
    A_CENTRE  =  3 # Centred
    A_JUSTIFY =  4 # Justified

    def __init__(self, theProject, theParent):

        self.mainConf    = nw.CONFIG
        self.theProject  = theProject
        self.theParent   = theParent

        self.theText     = None
        self.theHandle   = None
        self.theItem     = None
        self.theTokens   = None
        self.theResult   = None

        self.wordWrap    = 0
        self.doComments  = False
        self.doKeywords  = False

        self.fmtTitle    = "%title%"
        self.fmtChapter  = "%title%"
        self.fmtUnNum    = "%title%"
        self.fmtScene    = "%title%"
        self.fmtSection  = "%title%"

        self.hideScene   = False
        self.hideSection = False

        self.numChapter  = 0
        self.firstScene  = False

        return

    ##
    #  Setters
    ##

    def setComments(self, doComments):
        self.doComments = doComments
        return

    def setKeywords(self, doKeywords):
        self.doKeywords = doKeywords
        return

    def setWordWrap(self, wordWrap):
        if wordWrap >= 0:
            self.wordWrap = wordWrap
        else:
            self.wordWrap = 0
        return

    def setTitleFormat(self, fmtTitle):
        self.fmtTitle = fmtTitle
        return

    def setChapterFormat(self, fmtChapter):
        self.fmtChapter = fmtChapter
        return

    def setUnNumberedFormat(self, fmtUnNum):
        self.fmtUnNum = fmtUnNum
        return

    def setSceneFormat(self, fmtScene, hideScene):
        self.fmtScene  = fmtScene
        self.hideScene = hideScene
        return

    def setSectionFormat(self, fmtSection, hideSection):
        self.fmtSection  = fmtSection
        self.hideSection = hideSection
        return

    ##
    #  Class Methods
    ##

    def setText(self, theHandle, theText=None):

        self.theHandle = theHandle
        self.theItem   = self.theProject.projTree[theHandle]

        if theText is not None:
            # If the text is set, just use that
            self.theText = theText
        else:
            # Otherwise, load it from file
            theDocument  = NWDoc(self.theProject, self.theParent)
            self.theText = theDocument.openDocument(theHandle)

        return

    def doAutoReplace(self):
        if len(self.theProject.autoReplace) > 0:
            repDict = {}
            for aKey, aVal in self.theProject.autoReplace.items():
                repDict["<%s>" % aKey] = aVal
            xRep = re.compile("|".join([re.escape(k) for k in repDict.keys()]), flags=re.DOTALL)
            self.theText = xRep.sub(lambda x: repDict[x.group(0)], self.theText)
        return

    def doPostProcessing(self):
        return

    def tokenizeText(self):
        """Scan the text for either lines starting with specific
        characters that indicate headers, comments, commands etc, or
        just contains plain text. in the case of plain text, apply the
        same RegExes that the syntax highlighter uses and save the
        locations of these formatting tags into the token array.
        """

        # RegExes for adding formatting tags within text lines
        # Keep in sync with the DocHighlighter class
        rxFormats = [(
            QRegularExpression(r"(?<![\w|\\])([\*]{2})(?!\s)(?m:(.+?))(?<![\s|\\])(\1)(?!\w)"),
            [None, self.FMT_B_B, None, self.FMT_B_E]
        ),(
            QRegularExpression(r"(?<![\w|_|\\])([_])(?!\s|\1)(?m:(.+?))(?<![\s|\\])(\1)(?!\w)"),
            [None, self.FMT_I_B, None, self.FMT_I_E]
        ),(
            QRegularExpression(r"(?<![\w|\\])([_]{2})(?!\s)(?m:(.+?))(?<![\s|\\])(\1)(?!\w)"),
            [None, self.FMT_U_B, None, self.FMT_U_E]
        )]

        self.theTokens = []
        for aLine in self.theText.splitlines():

            # Tag lines starting with specific characters
            if len(aLine.strip()) == 0:
                self.theTokens.append((self.T_EMPTY,"",None,self.A_LEFT))
            elif aLine[0] == "%":
                self.theTokens.append((self.T_COMMENT,aLine[1:].strip(),None,self.A_LEFT))
            elif aLine[0] == "@":
                self.theTokens.append((self.T_KEYWORD,aLine[1:].strip(),None,self.A_LEFT))
            elif aLine[:2] == "# ":
                self.theTokens.append((self.T_HEAD1,aLine[2:].strip(),None,self.A_LEFT))
            elif aLine[:3] == "## ":
                self.theTokens.append((self.T_HEAD2,aLine[3:].strip(),None,self.A_LEFT))
            elif aLine[:4] == "### ":
                self.theTokens.append((self.T_HEAD3,aLine[4:].strip(),None,self.A_LEFT))
            elif aLine[:5] == "#### ":
                self.theTokens.append((self.T_HEAD4,aLine[5:].strip(),None,self.A_LEFT))
            else:
                # Otherwise we use RegEx to find formatting tags within a line of text
                fmtPos = []
                for theRX, theKeys in rxFormats:
                    rxThis = theRX.globalMatch(aLine, 0)
                    while rxThis.hasNext():
                        rxMatch = rxThis.next()
                        for n in range(1,len(theKeys)):
                            if theKeys[n] is not None:
                                xPos = rxMatch.capturedStart(n)
                                xLen = rxMatch.capturedLength(n)
                                fmtPos.append([xPos,xLen,theKeys[n]])

                # Save the line as is, but append the array of formatting locations
                # sorted by position
                fmtPos = sorted(fmtPos,key=itemgetter(0))
                self.theTokens.append((self.T_TEXT,aLine,fmtPos,self.A_LEFT))

        # Always add an empty line at the end
        self.theTokens.append((self.T_EMPTY,"",None,self.A_LEFT))

        return

    def doHeaders(self):

        isNone  = self.theItem.itemLayout == nwItemLayout.NO_LAYOUT
        isTitle = self.theItem.itemLayout == nwItemLayout.TITLE
        isBook  = self.theItem.itemLayout == nwItemLayout.BOOK
        isPage  = self.theItem.itemLayout == nwItemLayout.PAGE
        isPart  = self.theItem.itemLayout == nwItemLayout.PARTITION
        isUnNum = self.theItem.itemLayout == nwItemLayout.UNNUMBERED
        isChap  = self.theItem.itemLayout == nwItemLayout.CHAPTER
        isScene = self.theItem.itemLayout == nwItemLayout.SCENE
        isNote  = self.theItem.itemLayout == nwItemLayout.NOTE

        # No special header formatting for notes and no-layout files
        if isNone: return
        if isNote: return

        # For novel files, we need to handle chapter numbering and scene
        # breaks
        if isBook or isUnNum or isChap or isScene:
            for n in range(len(self.theTokens)):

                tToken = self.theTokens[n]
                tType  = tToken[0]
                tText  = tToken[1]

                if tType == self.T_TEXT:
                    self.firstScene = False

                elif tType == self.T_HEAD2:
                    if not isUnNum:
                        self.numChapter += 1
                    tText = self._doFormatChapter(tText,isUnNum)
                    self.theTokens[n] = (tType,tText,None,self.A_LEFT)
                    self.firstScene = True

                elif tType == self.T_HEAD3:
                    tTemp = self._doFormatScene(tText)
                    if tTemp == "" and self.hideScene:
                        self.theTokens[n] = (self.T_EMPTY,"",None,self.A_LEFT)
                    elif tTemp == "" and not self.hideScene:
                        if self.firstScene:
                            self.theTokens[n] = (self.T_EMPTY,"",None,self.A_LEFT)
                        else:
                            self.theTokens[n] = (self.T_SKIP,"",None,self.A_LEFT)
                    elif tTemp == self.fmtScene:
                        if self.firstScene:
                            self.theTokens[n] = (self.T_EMPTY,"",None,self.A_LEFT)
                        else:
                            self.theTokens[n] = (self.T_SEP,tTemp,None,self.A_CENTRE)
                    else:
                        self.theTokens[n] = (tType,tTemp,None,self.A_LEFT)
                    self.firstScene = False

                elif tType == self.T_HEAD4:
                    tTemp = self._doFormatSection(tText)
                    if tTemp == "" and self.hideSection:
                        self.theTokens[n] = (self.T_EMPTY,"",None,self.A_LEFT)
                    elif tTemp == "" and not self.hideSection:
                        self.theTokens[n] = (self.T_SKIP,"",None,self.A_LEFT)
                    elif tTemp == self.fmtSection:
                        self.theTokens[n] = (self.T_SEP,tTemp,None,self.A_CENTRE)
                    else:
                        self.theTokens[n] = (tType,tTemp,None,self.A_LEFT)

        # For title page and partitions, we need to centre all text
        # and for some formats, we need a page break
        if isTitle or isPart:
            for n in range(len(self.theTokens)):
                tToken  = self.theTokens[n]
                tType   = tToken[0]
                tText   = tToken[1]
                tFormat = tToken[2]
                self.theTokens[n] = (tType,tText,tFormat,self.A_CENTRE)

            self.theTokens.append((self.T_PBREAK,"",None,self.A_LEFT))

        return

    ##
    #  Internal Functions
    ##

    def _doFormatTitle(self, theText):
        theTitle = self.fmtTitle
        theTitle = theTitle.replace("%title%", theText)
        return theTitle

    def _doFormatChapter(self, theText, noNum):
        if noNum:
            theTitle = self.fmtUnNum
            theTitle = theTitle.replace("%title%", theText)
        else:
            theTitle = self.fmtChapter
            theTitle = theTitle.replace("%title%", theText)
            theTitle = theTitle.replace("%num%", str(self.numChapter))
            theTitle = theTitle.replace("%numword%", numberToWord(self.numChapter,"en"))
        return theTitle

    def _doFormatScene(self, theText):
        theTitle = self.fmtScene
        theTitle = theTitle.replace("%title%", theText)
        return theTitle

    def _doFormatSection(self, theText):
        theTitle = self.fmtSection
        theTitle = theTitle.replace("%title%", theText)
        return theTitle

    def _centreText(self, theText, theWidth):
        tLen = len(theText)
        if tLen < theWidth:
            return " "*int((theWidth-tLen)/2) + theText
        return theText

# END Class Tokenizer
