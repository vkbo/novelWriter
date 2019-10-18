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
                self.theTokens.append((self.T_EMPTY,"",None))
            elif aLine[0] == "%":
                self.theTokens.append((self.T_COMMENT,aLine[1:].strip(),None))
            elif aLine[0] == "@":
                self.theTokens.append((self.T_COMMENT,aLine[1:].strip(),None))
            elif aLine[:2] == "# ":
                self.theTokens.append((self.T_HEAD1,aLine[2:].strip(),None))
            elif aLine[:3] == "## ":
                self.theTokens.append((self.T_HEAD2,aLine[3:].strip(),None))
            elif aLine[:4] == "### ":
                self.theTokens.append((self.T_HEAD3,aLine[4:].strip(),None))
            elif aLine[:5] == "#### ":
                self.theTokens.append((self.T_HEAD4,aLine[5:].strip(),None))
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
                self.theTokens.append((self.T_TEXT,aLine,fmtPos))

        # Always add an empty line at the end
        self.theTokens.append((self.T_EMPTY,"",None))

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
        for tType, tText, tFormat in self.theTokens:

            # First check if we have a comment or plain text, as they need some
            # extra replacing before we proceed to wrapping and final formatting.
            if tType == self.T_COMMAND:
                tText = "[%s]" % tText

            elif tType == self.T_TEXT:
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+tTemp[xPos+xLen:]
                tText = tTemp

            tLen = len(tText)

            # The text can now be word wrapped, if we have requested this and it's needed.
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
                self.theResult += "%s\n%s\n\n" % (tText,uLine)

            elif tType == self.T_HEAD2:
                uLine = "~"*min(tLen,self.wordWrap)
                self.theResult += "%s\n%s\n\n" % (tText,uLine)

            elif tType == self.T_HEAD3:
                uLine = "-"*min(tLen,self.wordWrap)
                self.theResult += "%s\n%s\n\n" % (tText,uLine)

            elif tType == self.T_HEAD4:
                self.theResult += "%s\n\n" % tText

            elif tType == self.T_TEXT:
                thisPar.append(tText)

            elif tType == self.T_COMMENT and self.doComments:
                self.theResult += "%s\n\n" % tText

            elif tType == self.T_COMMAND and self.doCommands:
                self.theResult += "%s\n\n" % tText

        return

# END Class Tokenizer
