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
from nw.constants import nwItemLayout, nwItemType

logger = logging.getLogger(__name__)

class Tokenizer():

    FMT_B_B    =  1 # Begin bold
    FMT_B_E    =  2 # End bold
    FMT_I_B    =  3 # Begin italics
    FMT_I_E    =  4 # End italics
    FMT_U_B    =  5 # Begin underline
    FMT_U_E    =  6 # End underline

    T_EMPTY    =  1 # Empty line (new paragraph)
    T_SYNOPSIS =  2 # Synopsis comment
    T_COMMENT  =  3 # Comment line
    T_KEYWORD  =  4 # Command line
    T_TITLE    =  5 # Title
    T_HEAD1    =  6 # Header 1
    T_HEAD2    =  7 # Header 2
    T_HEAD3    =  8 # Header 3
    T_HEAD4    =  9 # Header 4
    T_TEXT     = 10 # Text line
    T_SEP      = 11 # Scene separator
    T_SKIP     = 12 # Paragraph break

    A_NONE     =   0 # No special style
    A_LEFT     =   1 # Left aligned
    A_RIGHT    =   2 # Right aligned
    A_CENTRE   =   4 # Centred
    A_JUSTIFY  =   8 # Justified
    A_PBB      =  16 # Page break before always
    A_PBB_AV   =  32 # Page break before avoid
    A_PBB_NO   =  64 # Page break before never
    A_PBA      = 128 # Page break after always
    A_PBA_AV   = 256 # Page break after avoid
    A_PBA_NO   = 512 # Page break after avoid

    def __init__(self, theProject, theParent):

        self.mainConf    = nw.CONFIG
        self.theProject  = theProject
        self.theParent   = theParent

        # Data Variables
        self.theText     = None # The raw text to be tokenized
        self.theHandle   = None # The handle associated with the text
        self.theItem     = None # The NWItem associated with the handle
        self.theTokens   = None # The list of the processed tokens
        self.theResult   = None # The result text after conversion
        self.theMarkdown = None # The result text in novelWriter markdown

        # User Settings
        self.doBodyText  = True  # Include body text
        self.doSynopsis  = False # Also process synopsis comments
        self.doComments  = False # Also process comments
        self.doKeywords  = False # Also process keywords like tags and references
        self.doJustify   = False # Justify text

        self.fmtTitle    = "%title%" # Formatting for titles
        self.fmtChapter  = "%title%" # Formatting for numbered chapters
        self.fmtUnNum    = "%title%" # Formatting for unnumbered chapters
        self.fmtScene    = "%title%" # Formatting for scenes
        self.fmtSection  = "%title%" # Formatting for sections

        self.hideScene   = False # Do not include scene headers
        self.hideSection = False # Do not include section headers

        self.linkHeaders = False # Add an anchor before headers

        # Instance Variables
        self.numChapter  = 0     # Counter for chapter numbers
        self.numChScene  = 0     # Counter for scene number within chapter
        self.numAbsScene = 0     # Counter for scene number within novel
        self.firstScene  = False # Flag to indicate that the first scene of the chapter

        # This File
        self.isNone  = False
        self.isTitle = False
        self.isBook  = False
        self.isPage  = False
        self.isPart  = False
        self.isUnNum = False
        self.isChap  = False
        self.isScene = False
        self.isNote  = False
        self.isNovel = False

        return

    def clearData(self):
        """Clear the data arrays and variables, but not settings, so the class
        can be reused for multiple documents.
        """
        self.theText     = None
        self.theHandle   = None
        self.theItem     = None
        self.theTokens   = None
        self.theResult   = None
        self.theMarkdown = None
        self.numChapter  = 0
        self.firstScene  = False

        self.isNone  = False
        self.isTitle = False
        self.isBook  = False
        self.isPage  = False
        self.isPart  = False
        self.isUnNum = False
        self.isChap  = False
        self.isScene = False
        self.isNote  = False
        self.isNovel = False

        return

    ##
    #  Setters
    ##

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

    def setLinkHeaders(self, linkHeaders):
        self.linkHeaders = linkHeaders
        return

    def setBodyText(self, doBodyText):
        self.doBodyText = doBodyText
        return

    def setSynopsis(self, doSynopsis):
        self.doSynopsis = doSynopsis
        return

    def setComments(self, doComments):
        self.doComments = doComments
        return

    def setKeywords(self, doKeywords):
        self.doKeywords = doKeywords
        return

    def setJustify(self, doJustify):
        self.doJustify = doJustify
        return

    ##
    #  Class Methods
    ##

    def addRootHeading(self, theHandle):
        """Add a heading at the start if a new root folder.
        """
        theItem = self.theProject.projTree[theHandle]
        if theItem is None:
            return False

        if theItem.itemType != nwItemType.ROOT:
            return False

        theTitle = "Notes: %s" % theItem.itemName
        self.theTokens = []
        self.theTokens.append((
            self.T_TITLE, 0, theTitle, None, self.A_PBB | self.A_CENTRE
        ))
        self.theMarkdown = "# %s\n\n" % theTitle

        return True

    def setText(self, theHandle, theText=None):
        """Set the text for the tokenizer from a handle. If theText is
        not set, load it from the file.
        """

        self.theHandle = theHandle
        self.theItem   = self.theProject.projTree[theHandle]
        if self.theItem is None:
            return

        if theText is not None:
            # If the text is set, just use that
            self.theText = theText
        else:
            # Otherwise, load it from file
            theDocument  = NWDoc(self.theProject, self.theParent)
            self.theText = theDocument.openDocument(theHandle)

        self.isNone  = self.theItem.itemLayout == nwItemLayout.NO_LAYOUT
        self.isTitle = self.theItem.itemLayout == nwItemLayout.TITLE
        self.isBook  = self.theItem.itemLayout == nwItemLayout.BOOK
        self.isPage  = self.theItem.itemLayout == nwItemLayout.PAGE
        self.isPart  = self.theItem.itemLayout == nwItemLayout.PARTITION
        self.isUnNum = self.theItem.itemLayout == nwItemLayout.UNNUMBERED
        self.isChap  = self.theItem.itemLayout == nwItemLayout.CHAPTER
        self.isScene = self.theItem.itemLayout == nwItemLayout.SCENE
        self.isNote  = self.theItem.itemLayout == nwItemLayout.NOTE
        self.isNovel = self.isBook or self.isUnNum or self.isChap or self.isScene

        return

    def getResult(self):
        """Return the result from the conversion.
        """
        return self.theResult

    def getFilteredMarkdown(self):
        """Return the novelWriter markdown after the filters have been applied.
        """
        return self.theMarkdown

    def doAutoReplace(self):
        """Run through the user's auto-replace dictionary.
        """

        if len(self.theProject.autoReplace) > 0:
            repDict = {}
            for aKey, aVal in self.theProject.autoReplace.items():
                repDict["<%s>" % aKey] = aVal
            xRep = re.compile("|".join([re.escape(k) for k in repDict.keys()]), flags=re.DOTALL)
            self.theText = xRep.sub(lambda x: repDict[x.group(0)], self.theText)

        return

    def doPostProcessing(self):
        """Do some postprocessing. Overloaded by subclasses.
        """
        return

    def tokenizeText(self):
        """Scan the text for either lines starting with specific
        characters that indicate headers, comments, commands etc, or
        just contains plain text. in the case of plain text, apply the
        same RegExes that the syntax highlighter uses and save the
        locations of these formatting tags into the token array.

        The format of the token list is an entry with a four-tuple for
        each line in the file. The tuple is as follows:
          1: The type of the block, self.T_*
          2: The text content of the block, without leading tags
          3: The internal formatting map of the text, self.FMT_*
          4: The style of the block, self.A_*
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
        self.theMarkdown = ""
        tmpMarkdown = []
        nLine = 0
        for aLine in self.theText.splitlines():
            nLine += 1

            # Tag lines starting with specific characters
            if len(aLine.strip()) == 0:
                self.theTokens.append((
                    self.T_EMPTY,
                    nLine,
                    "",
                    None,
                    self.A_NONE
                ))
                tmpMarkdown.append("\n")

            elif aLine[0] == "%":
                cLine = aLine[1:].strip()
                if cLine.lower().startswith("synopsis:"):
                    self.theTokens.append((
                        self.T_SYNOPSIS,
                        nLine,
                        cLine[9:].strip(),
                        None,
                        self.A_NONE
                    ))
                    if self.doSynopsis:
                        tmpMarkdown.append("%s\n" % aLine)
                else:
                    self.theTokens.append((
                        self.T_COMMENT,
                        nLine,
                        aLine[1:].strip(),
                        None,
                        self.A_NONE
                    ))
                    if self.doComments:
                        tmpMarkdown.append("%s\n" % aLine)

            elif aLine[0] == "@":
                self.theTokens.append((
                    self.T_KEYWORD,
                    nLine,
                    aLine[1:].strip(),
                    None,
                    self.A_NONE
                ))
                if self.doKeywords:
                    tmpMarkdown.append("%s\n" % aLine)

            elif aLine[:2] == "# ":
                self.theTokens.append((
                    self.T_HEAD1,
                    nLine,
                    aLine[2:].strip(),
                    None,
                    self.A_NONE
                ))
                tmpMarkdown.append("%s\n" % aLine)

            elif aLine[:3] == "## ":
                self.theTokens.append((
                    self.T_HEAD2,
                    nLine,
                    aLine[3:].strip(),
                    None,
                    self.A_NONE
                ))
                tmpMarkdown.append("%s\n" % aLine)

            elif aLine[:4] == "### ":
                self.theTokens.append((
                    self.T_HEAD3,
                    nLine,
                    aLine[4:].strip(),
                    None,
                    self.A_NONE
                ))
                tmpMarkdown.append("%s\n" % aLine)

            elif aLine[:5] == "#### ":
                self.theTokens.append((
                    self.T_HEAD4,
                    nLine,
                    aLine[5:].strip(),
                    None,
                    self.A_NONE
                ))
                tmpMarkdown.append("%s\n" % aLine)

            else:
                if not self.doBodyText:
                    # Skip all body text
                    continue

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
                fmtPos = sorted(fmtPos, key=itemgetter(0))
                self.theTokens.append((
                    self.T_TEXT,
                    nLine,
                    aLine,
                    fmtPos,
                    self.A_NONE
                ))
                tmpMarkdown.append("%s\n" % aLine)

        # Always add an empty line at the end
        self.theTokens.append((
            self.T_EMPTY,
            nLine,
            "",
            None,
            self.A_NONE
        ))
        tmpMarkdown.append("\n")

        self.theMarkdown = "".join(tmpMarkdown)
        tmpMarkdown = []

        return

    def doHeaders(self):
        """Apply formatting to the text headers according to document
        layout and user settings.
        """

        # No special header formatting for notes and no-layout files
        if self.isNone or self.isNote:
            return

        # For novel files, we need to handle chapter numbering, scene
        # numbering, and scene breaks
        if self.isNovel:
            for n in range(len(self.theTokens)):

                tToken = self.theTokens[n]

                # In case we see text before a scene, we reset the flag
                if tToken[0] == self.T_TEXT:
                    self.firstScene = False

                elif tToken[0] == self.T_HEAD1:
                    # Main Title
                    # ==========

                    tTemp = self._formatHeading(self.fmtTitle, tToken[2])
                    self.theTokens[n] = (
                        tToken[0],
                        tToken[1],
                        tTemp,
                        None,
                        self.A_NONE
                    )

                elif tToken[0] == self.T_HEAD2:
                    # Novel Chapter
                    # =============

                    # Numbered or Unnumbered
                    if self.isUnNum:
                        tTemp = self._formatHeading(self.fmtUnNum, tToken[2])
                    else:
                        self.numChapter += 1
                        tTemp = self._formatHeading(self.fmtChapter, tToken[2])

                    # Format the chapter header
                    self.theTokens[n] = (
                        tToken[0],
                        tToken[1],
                        tTemp,
                        None,
                        self.A_PBB
                    )

                    # Set scene variables
                    self.firstScene = True
                    self.numChScene = 0

                elif tToken[0] == self.T_HEAD3:
                    # Novel Scene
                    # ===========

                    self.numChScene += 1
                    self.numAbsScene += 1

                    tTemp = self._formatHeading(self.fmtScene, tToken[2])
                    if tTemp == "" and self.hideScene:
                        self.theTokens[n] = (
                            self.T_EMPTY,
                            tToken[1],
                            "",
                            None,
                            self.A_NONE
                        )
                    elif tTemp == "" and not self.hideScene:
                        if self.firstScene:
                            self.theTokens[n] = (
                                self.T_EMPTY,
                                tToken[1],
                                "",
                                None,
                                self.A_NONE
                            )
                        else:
                            self.theTokens[n] = (
                                self.T_SKIP,
                                tToken[1],
                                "",
                                None,
                                self.A_NONE
                            )
                    elif tTemp == self.fmtScene:
                        if self.firstScene:
                            self.theTokens[n] = (
                                self.T_EMPTY,
                                tToken[1],
                                "",
                                None,
                                self.A_NONE
                            )
                        else:
                            self.theTokens[n] = (
                                self.T_SEP,
                                tToken[1],
                                tTemp,
                                None,
                                self.A_CENTRE
                            )
                    else:
                        self.theTokens[n] = (
                            tToken[0],
                            tToken[1],
                            tTemp,
                            None,
                            self.A_NONE
                        )

                    # Definitely no longer the first scene
                    self.firstScene = False

                elif tToken[0] == self.T_HEAD4:
                    # Novel Section
                    # =============

                    tTemp = self._formatHeading(self.fmtSection, tToken[2])
                    if tTemp == "" and self.hideSection:
                        self.theTokens[n] = (
                            self.T_EMPTY,
                            tToken[1],
                            "",
                            None,
                            self.A_NONE
                        )
                    elif tTemp == "" and not self.hideSection:
                        self.theTokens[n] = (
                            self.T_SKIP,
                            tToken[1],
                            "",
                            None,
                            self.A_NONE
                        )
                    elif tTemp == self.fmtSection:
                        self.theTokens[n] = (
                            self.T_SEP,
                            tToken[1],
                            tTemp,
                            None,
                            self.A_CENTRE
                        )
                    else:
                        self.theTokens[n] = (
                            tToken[0],
                            tToken[1],
                            tTemp,
                            None,
                            self.A_NONE
                        )

        # For title page and partitions, we need to centre all text.
        # For partition, we also add a page break before, and for
        # both types we always add a page break after the content.
        # We also swap header level 1 with a title type instead.
        if self.isTitle or self.isPart:
            for n, tToken in enumerate(self.theTokens):
                if tToken[0] == self.T_HEAD1:
                    if self.isTitle:
                        self.theTokens[n] = (
                            self.T_TITLE,
                            tToken[1],
                            tToken[2],
                            tToken[3],
                            self.A_PBB_NO | self.A_CENTRE
                        )
                    else:
                        self.theTokens[n] = (
                            tToken[0],
                            tToken[1],
                            tToken[2],
                            tToken[3],
                            self.A_PBB | self.A_CENTRE
                        )
                else:
                    self.theTokens[n] = (
                        tToken[0],
                        tToken[1],
                        tToken[2],
                        tToken[3],
                        self.A_CENTRE
                    )

            # Add a page break after the last entry
            n = len(self.theTokens) - 1
            if n >= 0:
                tToken = self.theTokens[n]
                self.theTokens[n] = (
                    tToken[0],
                    tToken[1],
                    tToken[2],
                    tToken[3],
                    tToken[4] | self.A_PBA
                )

        # A single page is always left-aligned and starts on a fresh
        # page, unless it's empty.
        if self.isPage:
            for n, tToken in enumerate(self.theTokens):
                if n == 0:
                    self.theTokens[n] = (
                        tToken[0],
                        tToken[1],
                        tToken[2],
                        tToken[3],
                        self.A_LEFT | self.A_PBB
                    )
                else:
                    self.theTokens[n] = (
                        tToken[0],
                        tToken[1],
                        tToken[2],
                        tToken[3],
                        self.A_LEFT
                    )

        return

    ##
    #  Internal Functions
    ##

    def _formatHeading(self, theTitle, theText):
        """Replaces the %keyword% strings.
        """
        theTitle = theTitle.replace(r"%title%", theText)
        theTitle = theTitle.replace(r"%ch%", str(self.numChapter))
        theTitle = theTitle.replace(r"%sc%", str(self.numChScene))
        theTitle = theTitle.replace(r"%sca%", str(self.numAbsScene))
        if r"%chw%" in theTitle:
            theTitle = theTitle.replace(r"%chw%", numberToWord(self.numChapter,"en"))
        return theTitle

# END Class Tokenizer
