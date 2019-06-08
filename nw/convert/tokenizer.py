# -*- coding: utf-8 -*-
"""novelWriter Text Tokenizer

 novelWriter – Text Tokenizer
==============================
 Splits a piece of nW markdown text into its elements

 File History:
 Created: 2019-05-05 [0.0.1]

"""

import logging
import re
import nw

from operator            import itemgetter
from PyQt5.QtCore        import QRegularExpression
from nw.project.document import NWDoc

logger = logging.getLogger(__name__)

class Tokenizer():

    FMT_B_B = 1 # Begin Bold
    FMT_B_E = 2 # End Bold
    FMT_I_B = 3 # Begin Italics
    FMT_I_E = 4 # End Italics
    FMT_U_B = 5 # Begin Underline
    FMT_U_E = 6 # End Underline

    def __init__(self, theProject, theParent):

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.theText    = None
        self.theHandle  = None
        self.theItem    = None
        self.theTokens  = None
        self.theResult  = None

        return

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
            theDict = {}
            for aKey, aVal in self.theProject.autoReplace.items():
                theDict["<%s>" % aKey] = aVal
            xRep = re.compile("|".join([re.escape(k) for k in theDict.keys()]), flags=re.DOTALL)
            self.theText = xRep.sub(lambda x: theDict[x.group(0)], self.theText)
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
                self.theTokens.append(("empty","",None))
            elif aLine[0] == "%":
                self.theTokens.append(("comment",aLine[1:].strip(),None))
            elif aLine[0] == "@":
                self.theTokens.append(("command",aLine[1:].strip(),None))
            elif aLine[:2] == "# ":
                self.theTokens.append(("header1",aLine[2:].strip(),None))
            elif aLine[:3] == "## ":
                self.theTokens.append(("header2",aLine[3:].strip(),None))
            elif aLine[:4] == "### ":
                self.theTokens.append(("header3",aLine[4:].strip(),None))
            elif aLine[:5] == "#### ":
                self.theTokens.append(("header4",aLine[5:].strip(),None))
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
                self.theTokens.append(("text",aLine,fmtPos))

        # Always add an empty line at the end
        self.theTokens.append(("empty","",None))
        # print(self.theTokens)

        return

# END Class Tokenizer
