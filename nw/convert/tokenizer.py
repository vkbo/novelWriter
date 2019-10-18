# -*- coding: utf-8 -*-
"""novelWriter Text Tokenizer

 novelWriter – Text Tokenizer
==============================
 Splits a piece of nW markdown text into its elements

 File History:
 Created: 2019-05-05 [0.0.1]

"""

import textwrap
import logging
import re
import nw

from operator            import itemgetter
from PyQt5.QtCore        import QRegularExpression

from nw.project.document import NWDoc
from nw.tools.translate  import numberToWord
from nw.enum             import nwItemLayout

logger = logging.getLogger(__name__)

class Tokenizer():

    FMT_B_B   = "" # Begin bold
    FMT_B_E   = "" # End bold
    FMT_I_B   = "" # Begin italics
    FMT_I_E   = "" # End italics
    FMT_U_B   = "" # Begin underline
    FMT_U_E   = "" # End underline

    T_EMPTY   = 1  # Empty line (new paragraph)
    T_COMMENT = 2  # Comment line
    T_COMMAND = 3  # Command line
    T_HEAD1   = 4  # Header 1 (title)
    T_HEAD2   = 5  # Header 2 (chapter)
    T_HEAD3   = 6  # Header 3 (scene)
    T_HEAD4   = 7  # Header 4
    T_TEXT    = 8  # Text line
    T_SEP     = 9  # Scene separator

    A_LEFT    = 1  # Left aligned
    A_RIGHT   = 2  # Right aligned
    A_CENTRE  = 3  # Centred
    A_JUSTIFY = 4  # Justified

    def __init__(self, theProject, theParent):

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.theText    = None
        self.theHandle  = None
        self.theItem    = None
        self.theTokens  = None
        self.theResult  = None

        self.wordWrap   = 80
        self.doComments = False
        self.doCommands = False

        self.fmtTitle   = "%title%"
        self.fmtUnNum   = "%title%"
        self.fmtChapter = "Chapter %numword%: %title%"
        self.fmtScene   = "* * *"
        self.fmtSection = "%title%"

        self.noSection  = True

        self.numChapter = 0
        self.firstScene = False

        return

    ##
    #  Setters
    ##

    def setComments(self, doComments):
        self.doComments = doComments
        return

    def setCommands(self, doCommands):
        self.doCommands = doCommands
        return

    def setWordWrap(self, wordWrap):
        if wordWrap >= 0:
            self.wordWrap = wordWrap
        else:
            self.wordWrap = 0
        return

    ##
    #  Class Methods
    ##

    def setText(self, theHandle, theText=None):

        self.theHandle = theHandle
        self.theItem   = self.theProject.getItem(theHandle)

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

    def tokenizeText(self):
        """Scan the text for either lines starting with specific characters that indicate headers,
        comments, commands etc, or just contains plain text. in the case of plain text, apply the
        same RegExes that the syntax highlighter uses and save the locations of these formatting
        tags into the token array.
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
            aLine = aLine.strip()

            # Tag lines starting with specific characters
            if len(aLine) == 0:
                self.theTokens.append((self.T_EMPTY,"",None,self.A_LEFT))
            elif aLine[0] == "%":
                self.theTokens.append((self.T_COMMENT,aLine[1:].strip(),None,self.A_LEFT))
            elif aLine[0] == "@":
                self.theTokens.append((self.T_COMMAND,aLine[1:].strip(),None,self.A_LEFT))
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

                # Save the line as is, but append the array of formatting locations sorted by position
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

        # No special header formatting for notes and no layout files
        if isNone: return
        if isNote: return

        # For novel files, we need to handle chapter numbering and scene breaks
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
                    if tTemp == self.fmtScene:
                        if self.firstScene:
                            self.theTokens[n] = (self.T_EMPTY,"",None,self.A_LEFT)
                        else:
                            self.theTokens[n] = (self.T_SEP,tTemp,None,self.A_LEFT)
                    else:
                        self.theTokens[n] = (tType,tTemp,None,self.A_LEFT)
                    self.firstScene = False

                elif tType == self.T_HEAD4:
                    if self.noSection:
                        self.theTokens[n] = (self.T_EMPTY,"",None,self.A_LEFT)
                    else:
                        tTemp = self._doFormatSection(tText)
                        self.theTokens[n] = (self.T_SEP,tTemp,None,self.A_LEFT)

        # For title page and partitions, we need to centre all text
        if isTitle or isPart:
            for n in range(len(self.theTokens)):
                tToken  = self.theTokens[n]
                tType   = tToken[0]
                tText   = tToken[1]
                tFormat = tToken[2]
                self.theTokens[n] = (tType,tText,tFormat,self.A_CENTRE)

        return

    def doConvert(self):
        """Converts the tokenized text into plain text.
        """

        if self.wordWrap > 0:
            tWrap = textwrap.TextWrapper(
                width                = self.wordWrap,
                initial_indent       = "",
                subsequent_indent    = "",
                expand_tabs          = True,
                replace_whitespace   = True,
                fix_sentence_endings = False,
                break_long_words     = True,
                drop_whitespace      = True,
                break_on_hyphens     = True,
                tabsize              = 8,
                max_lines            = None
            )

        self.theResult = ""
        thisPar = []
        for tType, tText, tFormat, tAlign in self.theTokens:

            # First check if we have a comment or plain text, as they need some
            # extra replacing before we proceed to wrapping and final formatting.
            if tType == self.T_COMMENT:
                tText = "[%s]" % tText

            elif tType == self.T_TEXT:
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+tTemp[xPos+xLen:]
                tText = tTemp

            tLen = len(tText)

            # The text can now be word wrapped, if we have requested this and it's needed.
            if tAlign == self.A_CENTRE:
                if self.wordWrap > 0:
                    if tLen > self.wordWrap:
                        aText = tWrap.wrap(tText)
                        for n in range(len(aText)):
                            aText[n] = self._centreText(aText[n],self.wordWrap)
                        tText = "\n".join(aText)
                    else:
                        tText = self._centreText(tText,self.wordWrap)
            else:
                if self.wordWrap > 0 and tLen > self.wordWrap:
                    tText = tWrap.fill(tText)

            # Then the text can receive final formatting before we append it to the results.
            # We also store text lines in a buffer and merge them only when we find an empty line,
            # indicating a new paragraph.
            if tType == self.T_EMPTY:
                if len(thisPar) > 0:
                    self.theResult += "%s\n\n" % " ".join(thisPar)
                thisPar = []

            elif tType == self.T_HEAD1:
                uLine = "="*min(tLen,self.wordWrap)
                if tAlign == self.A_CENTRE:
                    uLine = self._centreText(uLine,self.wordWrap)
                self.theResult += "%s\n%s\n\n" % (tText,uLine)

            elif tType == self.T_HEAD2:
                uLine = "~"*min(tLen,self.wordWrap)
                self.theResult += "%s\n%s\n\n" % (tText,uLine)

            elif tType == self.T_HEAD3:
                uLine = "-"*min(tLen,self.wordWrap)
                self.theResult += "%s\n%s\n\n" % (tText,uLine)

            elif tType == self.T_HEAD4:
                self.theResult += "%s\n\n" % tText

            elif tType == self.T_SEP:
                if self.wordWrap > 0 and tLen < self.wordWrap:
                    tText = self._centreText(tText,self.wordWrap)
                self.theResult += "%s\n\n" % tText

            elif tType == self.T_TEXT:
                thisPar.append(tText)

            elif tType == self.T_COMMENT and self.doComments:
                self.theResult += "%s\n\n" % tText

            elif tType == self.T_COMMAND and self.doCommands:
                self.theResult += "%s\n\n" % tText

        return

    def windowsEndings(self):
        self.theResult = self.theResult.replace("\n","\r\n")
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
