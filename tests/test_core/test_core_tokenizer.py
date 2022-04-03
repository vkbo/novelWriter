"""
novelWriter – Tokenizer Class Tester
====================================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import os
import pytest

from tools import readFile

from novelwriter.core import NWProject, NWDoc
from novelwriter.core.tokenizer import Tokenizer


class BareTokenizer(Tokenizer):
    def doConvert(self):
        super().doConvert()


@pytest.mark.core
def testCoreToken_Setters(mockGUI):
    """Test all the setters for the Tokenizer class.
    """
    theProject = NWProject(mockGUI)
    theToken = BareTokenizer(theProject)

    # Verify defaults
    assert theToken._fmtTitle == "%title%"
    assert theToken._fmtChapter == "%title%"
    assert theToken._fmtUnNum == "%title%"
    assert theToken._fmtScene == "%title%"
    assert theToken._fmtSection == "%title%"
    assert theToken._textFont == "Serif"
    assert theToken._textSize == 11
    assert theToken._textFixed is False
    assert theToken._lineHeight == 1.15
    assert theToken._blockIndent == 4.0
    assert theToken._doJustify is False
    assert theToken._marginTitle == (1.000, 0.500)
    assert theToken._marginHead1 == (1.000, 0.500)
    assert theToken._marginHead2 == (0.834, 0.500)
    assert theToken._marginHead3 == (0.584, 0.500)
    assert theToken._marginHead4 == (0.584, 0.500)
    assert theToken._marginText == (0.000, 0.584)
    assert theToken._marginMeta == (0.000, 0.584)
    assert theToken._hideScene is False
    assert theToken._hideSection is False
    assert theToken._linkHeaders is False
    assert theToken._doBodyText is True
    assert theToken._doSynopsis is False
    assert theToken._doComments is False
    assert theToken._doKeywords is False

    # Set new values
    theToken.setTitleFormat("T: %title%")
    theToken.setChapterFormat("C: %title%")
    theToken.setUnNumberedFormat("U: %title%")
    theToken.setSceneFormat("S: %title%", True)
    theToken.setSectionFormat("X: %title%", True)
    theToken.setFont("Monospace", 10, True)
    theToken.setLineHeight(2.0)
    theToken.setBlockIndent(6.0)
    theToken.setJustify(True)
    theToken.setTitleMargins(2.0, 2.0)
    theToken.setHead1Margins(2.0, 2.0)
    theToken.setHead2Margins(2.0, 2.0)
    theToken.setHead3Margins(2.0, 2.0)
    theToken.setHead4Margins(2.0, 2.0)
    theToken.setTextMargins(2.0, 2.0)
    theToken.setMetaMargins(2.0, 2.0)
    theToken.setLinkHeaders(True)
    theToken.setBodyText(False)
    theToken.setSynopsis(True)
    theToken.setComments(True)
    theToken.setKeywords(True)

    # Check new values
    assert theToken._fmtTitle == "T: %title%"
    assert theToken._fmtChapter == "C: %title%"
    assert theToken._fmtUnNum == "U: %title%"
    assert theToken._fmtScene == "S: %title%"
    assert theToken._fmtSection == "X: %title%"
    assert theToken._textFont == "Monospace"
    assert theToken._textSize == 10
    assert theToken._textFixed is True
    assert theToken._lineHeight == 2.0
    assert theToken._blockIndent == 6.0
    assert theToken._doJustify is True
    assert theToken._marginTitle == (2.0, 2.0)
    assert theToken._marginHead1 == (2.0, 2.0)
    assert theToken._marginHead2 == (2.0, 2.0)
    assert theToken._marginHead3 == (2.0, 2.0)
    assert theToken._marginHead4 == (2.0, 2.0)
    assert theToken._marginText == (2.0, 2.0)
    assert theToken._marginMeta == (2.0, 2.0)
    assert theToken._hideScene is True
    assert theToken._hideSection is True
    assert theToken._linkHeaders is True
    assert theToken._doBodyText is False
    assert theToken._doSynopsis is True
    assert theToken._doComments is True
    assert theToken._doKeywords is True

    # Check Limits
    theToken.setLineHeight(0.0)
    assert theToken._lineHeight == 0.5
    theToken.setLineHeight(10.0)
    assert theToken._lineHeight == 5.0

    theToken.setBlockIndent(-6.0)
    assert theToken._blockIndent == 0.0
    theToken.setBlockIndent(60.0)
    assert theToken._blockIndent == 10.0

# END Test testCoreToken_Setters


@pytest.mark.core
def testCoreToken_TextOps(monkeypatch, nwMinimal, mockGUI):
    """Test handling files and text in the Tokenizer class.
    """
    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)
    theProject.projLang = "en"
    theProject._loadProjectLocalisation()

    theToken = BareTokenizer(theProject)
    theToken.setKeepMarkdown(True)

    assert theProject.openProject(nwMinimal)
    sHandle = "8c659a11cd429"

    # Set some content to work with

    docText = (
        "### Scene Six\n\n"
        "This is text with _italic text_, some **bold text**, some ~~deleted text~~, "
        "and some **_mixed text_** and **some _nested_ text**.\n\n"
        "#### Replace\n\n"
        "Also, replace <A> and <B>.\n\n"
    )
    docTextR = docText.replace("<A>", "this").replace("<B>", "that")

    nDoc = NWDoc(theProject, sHandle)
    assert nDoc.writeDocument(docText)

    theProject.setAutoReplace({"A": "this", "B": "that"})

    assert theProject.saveProject()

    # Root Heading
    assert theToken.addRootHeading("stuff") is False
    assert theToken.addRootHeading(sHandle) is False

    # First Page
    assert theToken.addRootHeading("7695ce551d265") is True
    assert theToken.theMarkdown[-1] == "# Notes: Plot\n\n"
    assert theToken._theTokens[-1] == (
        Tokenizer.T_TITLE, 0, "Notes: Plot", None, Tokenizer.A_CENTRE
    )

    # Not First Page
    assert theToken.addRootHeading("7695ce551d265") is True
    assert theToken.theMarkdown[-1] == "# Notes: Plot\n\n"
    assert theToken._theTokens[-1] == (
        Tokenizer.T_TITLE, 0, "Notes: Plot", None, Tokenizer.A_CENTRE | Tokenizer.A_PBB
    )

    # Set Text
    assert theToken.setText("stuff") is False
    assert theToken.setText(sHandle) is True
    assert theToken._theText == docText

    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.constants.nwConst.MAX_DOCSIZE", 100)
        assert theToken.setText(sHandle, docText) is True
        assert theToken._theText == (
            "# ERROR\n\n"
            "Document 'New Scene' is too big (0.00 MB). Skipping.\n\n"
        )

    assert theToken.setText(sHandle, docText) is True
    assert theToken._theText == docText

    assert theToken._isNone is False
    assert theToken._isNovel is True
    assert theToken._isNote is False

    # Pre Processing
    theToken.doPreProcessing()
    assert theToken._theText == docTextR

    # Post Processing
    theToken._theResult = r"This is text with escapes: \** \~~ \__"
    theToken.doPostProcessing()
    assert theToken.theResult == "This is text with escapes: ** ~~ __"

    # Save File
    savePath = os.path.join(nwMinimal, "dump.nwd")
    theToken.saveRawMarkdown(savePath)
    assert readFile(savePath) == (
        "# Notes: Plot\n\n"
        "# Notes: Plot\n\n"
    )

    # Ckeck abstract method
    with pytest.raises(NotImplementedError):
        theToken.doConvert()

# END Test testCoreToken_TextOps


@pytest.mark.core
def testCoreToken_HeaderFormat(mockGUI):
    """Test the tokenization of header formats in the Tokenizer class.
    """
    theProject = NWProject(mockGUI)
    theToken = BareTokenizer(theProject)
    theToken.setKeepMarkdown(True)

    # Title
    # =====

    # Story File
    theToken._isNovel = True
    theToken._isNote  = False
    theToken._isFirst = True
    theToken._theText = "#! Novel Title\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_TITLE, 1, "Novel Title", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "#! Novel Title\n\n"

    # Note File
    theToken._isNovel = False
    theToken._isNote  = True
    theToken._isFirst = True
    theToken._theText = "#! Note Title\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Note Title", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "#! Note Title\n\n"

    # Header 1
    # ========

    # Story File
    theToken._isNovel = True
    theToken._isNote  = False
    theToken._isFirst = True
    theToken._theText = "# Novel Title\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Novel Title", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "# Novel Title\n\n"

    # Note File
    theToken._isNovel = False
    theToken._isNote  = True
    theToken._isFirst = True
    theToken._theText = "# Note Title\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Note Title", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "# Note Title\n\n"

    # Header 2
    # ========

    # Story File
    theToken._isNovel = True
    theToken._isNote  = False
    theToken._theText = "## Chapter One\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter One", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "## Chapter One\n\n"

    # Note File
    theToken._isNovel = False
    theToken._isNote  = True
    theToken._theText = "## Heading 2\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD2, 1, "Heading 2", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "## Heading 2\n\n"

    # Header 3
    # ========

    # Story File
    theToken._isNovel = True
    theToken._isNote  = False
    theToken._theText = "### Scene One\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD3, 1, "Scene One", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "### Scene One\n\n"

    # Note File
    theToken._isNovel = False
    theToken._isNote  = True
    theToken._theText = "### Heading 3\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD3, 1, "Heading 3", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "### Heading 3\n\n"

    # Header 4
    # ========

    # Story File
    theToken._isNovel = True
    theToken._isNote  = False
    theToken._theText = "#### A Section\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD4, 1, "A Section", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "#### A Section\n\n"

    # Note File
    theToken._isNovel = False
    theToken._isNote  = True
    theToken._theText = "#### Heading 4\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD4, 1, "Heading 4", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "#### Heading 4\n\n"

    # Title
    # =====

    # Story File
    theToken._isNovel = True
    theToken._isNote  = False
    theToken._theText = "#! Title\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_TITLE, 1, "Title", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "#! Title\n\n"

    # Note File
    theToken._isNovel = False
    theToken._isNote  = True
    theToken._theText = "#! Title\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Title", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "#! Title\n\n"

    # Unnumbered
    # ==========

    # Story File
    theToken._isNovel = True
    theToken._isNote  = False
    theToken._theText = "##! Prologue\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_UNNUM, 1, "Prologue", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "##! Prologue\n\n"

    # Note File
    theToken._isNovel = False
    theToken._isNote  = True
    theToken._theText = "##! Prologue\n"

    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD2, 1, "Prologue", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "##! Prologue\n\n"

# END Test testCoreToken_HeaderFormat


@pytest.mark.core
def testCoreToken_MetaFormat(mockGUI):
    """Test the tokenization of meta formats in the Tokenizer class.
    """
    theProject = NWProject(mockGUI)
    theToken = BareTokenizer(theProject)
    theToken.setKeepMarkdown(True)

    # Comment
    theToken._theText = "% A comment\n"
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_COMMENT, 1, "A comment", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "\n"

    theToken.setComments(True)
    theToken.tokenizeText()
    assert theToken.theMarkdown[-1] == "% A comment\n\n"

    # Symopsis
    theToken._theText = "%synopsis: The synopsis\n"
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_SYNOPSIS, 1, "The synopsis", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    theToken._theText = "% synopsis: The synopsis\n"
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_SYNOPSIS, 1, "The synopsis", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "\n"

    theToken.setSynopsis(True)
    theToken.tokenizeText()
    assert theToken.theMarkdown[-1] == "% synopsis: The synopsis\n\n"

    # Keyword
    theToken._theText = "@char: Bod\n"
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_KEYWORD, 1, "char: Bod", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "\n"

    theToken.setKeywords(True)
    theToken.tokenizeText()
    assert theToken.theMarkdown[-1] == "@char: Bod\n\n"

    theToken._theText = "@pov: Bod\n@plot: Main\n@location: Europe\n"
    theToken.tokenizeText()
    styTop = Tokenizer.A_NONE | Tokenizer.A_Z_BTMMRG
    styMid = Tokenizer.A_NONE | Tokenizer.A_Z_BTMMRG | Tokenizer.A_Z_TOPMRG
    styBtm = Tokenizer.A_NONE | Tokenizer.A_Z_TOPMRG
    assert theToken._theTokens == [
        (Tokenizer.T_KEYWORD, 1, "pov: Bod", None, styTop),
        (Tokenizer.T_KEYWORD, 2, "plot: Main", None, styMid),
        (Tokenizer.T_KEYWORD, 3, "location: Europe", None, styBtm),
        (Tokenizer.T_EMPTY, 3, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "@pov: Bod\n@plot: Main\n@location: Europe\n\n"

# END Test testCoreToken_MetaFormat


@pytest.mark.core
def testCoreToken_MarginFormat(mockGUI):
    """Test the tokenization of margin formats in the Tokenizer class.
    """
    theProject = NWProject(mockGUI)
    theToken = BareTokenizer(theProject)
    theToken.setKeepMarkdown(True)

    # Alignment and Indentation
    dblIndent = Tokenizer.A_IND_L | Tokenizer.A_IND_R
    rIndAlign = Tokenizer.A_RIGHT | Tokenizer.A_IND_R
    theToken._theText = (
        "Some regular text\n\n"
        "Some left-aligned text <<\n\n"
        ">> Some right-aligned text\n\n"
        ">> Some centered text <<\n\n"
        "> Left-indented block\n\n"
        "Right-indented block <\n\n"
        "> Double-indented block <\n\n"
        ">> Right-indent, right-aligned <\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_TEXT,  1, "Some regular text", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  3, "Some left-aligned text", [], Tokenizer.A_LEFT),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  5, "Some right-aligned text", [], Tokenizer.A_RIGHT),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  7, "Some centered text", [], Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 8, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  9, "Left-indented block", [], Tokenizer.A_IND_L),
        (Tokenizer.T_EMPTY, 10, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  11, "Right-indented block", [], Tokenizer.A_IND_R),
        (Tokenizer.T_EMPTY, 12, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  13, "Double-indented block", [], dblIndent),
        (Tokenizer.T_EMPTY, 14, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  15, "Right-indent, right-aligned", [], rIndAlign),
        (Tokenizer.T_EMPTY, 16, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 16, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == (
        "Some regular text\n\n"
        "Some left-aligned text\n\n"
        "Some right-aligned text\n\n"
        "Some centered text\n\n"
        "Left-indented block\n\n"
        "Right-indented block\n\n"
        "Double-indented block\n\n"
        "Right-indent, right-aligned\n\n\n"
    )

# END Test testCoreToken_MarginFormat


@pytest.mark.core
def testCoreToken_TextFormat(mockGUI):
    """Test the tokenization of text formats in the Tokenizer class.
    """
    theProject = NWProject(mockGUI)
    theToken = BareTokenizer(theProject)
    theToken.setKeepMarkdown(True)

    # Text
    theToken._theText = "Some plain text\non two lines\n\n\n"
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_TEXT, 1, "Some plain text", [], Tokenizer.A_NONE),
        (Tokenizer.T_TEXT, 2, "on two lines", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 3, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "Some plain text\non two lines\n\n\n\n"

    theToken.setBodyText(False)
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_EMPTY, 3, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "\n\n\n"
    theToken.setBodyText(True)

    # Text Emphasis
    theToken._theText = "Some **bolded text** on this lines\n"
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (
            Tokenizer.T_TEXT, 1,
            "Some **bolded text** on this lines",
            [
                [5,  2, Tokenizer.FMT_B_B],
                [18, 2, Tokenizer.FMT_B_E],
            ],
            Tokenizer.A_NONE
        ),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "Some **bolded text** on this lines\n\n"

    theToken._theText = "Some _italic text_ on this lines\n"
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (
            Tokenizer.T_TEXT, 1,
            "Some _italic text_ on this lines",
            [
                [5,  1, Tokenizer.FMT_I_B],
                [17, 1, Tokenizer.FMT_I_E],
            ],
            Tokenizer.A_NONE
        ),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "Some _italic text_ on this lines\n\n"

    theToken._theText = "Some **_bold italic text_** on this lines\n"
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (
            Tokenizer.T_TEXT, 1,
            "Some **_bold italic text_** on this lines",
            [
                [5,  2, Tokenizer.FMT_B_B],
                [7,  1, Tokenizer.FMT_I_B],
                [24, 1, Tokenizer.FMT_I_E],
                [25, 2, Tokenizer.FMT_B_E],
            ],
            Tokenizer.A_NONE
        ),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "Some **_bold italic text_** on this lines\n\n"

    theToken._theText = "Some ~~strikethrough text~~ on this lines\n"
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (
            Tokenizer.T_TEXT, 1,
            "Some ~~strikethrough text~~ on this lines",
            [
                [5,  2, Tokenizer.FMT_D_B],
                [25, 2, Tokenizer.FMT_D_E],
            ],
            Tokenizer.A_NONE
        ),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == "Some ~~strikethrough text~~ on this lines\n\n"

    theToken._theText = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (
            Tokenizer.T_TEXT, 1,
            "Some **nested bold and _italic_ and ~~strikethrough~~ text** here",
            [
                [5,  2, Tokenizer.FMT_B_B],
                [23, 1, Tokenizer.FMT_I_B],
                [30, 1, Tokenizer.FMT_I_E],
                [36, 2, Tokenizer.FMT_D_B],
                [51, 2, Tokenizer.FMT_D_E],
                [58, 2, Tokenizer.FMT_B_E],
            ],
            Tokenizer.A_NONE
        ),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown[-1] == (
        "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n\n"
    )

# END Test testCoreToken_TextFormat


@pytest.mark.core
def testCoreToken_SpecialFormat(mockGUI):
    """Test the tokenization of special formats in the Tokenizer class.
    """
    theProject = NWProject(mockGUI)
    theToken = BareTokenizer(theProject)

    theToken._isNovel = True

    # New Page
    # ========

    correctResp = [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_HEAD1, 5, "Title Two", None, Tokenizer.A_CENTRE | Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
    ]

    # Command wo/Space
    theToken._isFirst = True
    theToken._theText = (
        "# Title One\n\n"
        "[NEWPAGE]\n\n"
        "# Title Two\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == correctResp

    # Command w/Space
    theToken._isFirst = True
    theToken._theText = (
        "# Title One\n\n"
        "[NEW PAGE]\n\n"
        "# Title Two\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == correctResp

    # Trailing Spaces
    theToken._isFirst = True
    theToken._theText = (
        "# Title One\n\n"
        "[NEW PAGE]   \t\n\n"
        "# Title Two\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == correctResp

    # Single Empty Paragraph
    # ======================

    theToken._theText = (
        "# Title One\n\n"
        "[VSPACE] \n\n"
        "Some text to go here ...\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  3, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  5, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
    ]

    # Multiple Empty Paragraphs
    # =========================

    # One Skip
    theToken._theText = (
        "# Title One\n\n"
        "[VSPACE:1] \n\n"
        "Some text to go here ...\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  3, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  5, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
    ]

    # Three Skips
    theToken._theText = (
        "# Title One\n\n"
        "[VSPACE:3] \n\n"
        "Some text to go here ...\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  3, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  3, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  3, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  5, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
    ]

    # Malformed Command, Case 1
    theToken._theText = (
        "# Title One\n\n"
        "[VSPACE:3xa] \n\n"
        "Some text to go here ...\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  5, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
    ]

    # Malformed Command, Case 2
    theToken._theText = (
        "# Title One\n\n"
        "[VSPACE:3.5]\n\n"
        "Some text to go here ...\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  5, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
    ]

    # Malformed Command, Case 3
    theToken._theText = (
        "# Title One\n\n"
        "[VSPACE:-1]\n\n"
        "Some text to go here ...\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  5, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
    ]

    # Empty Paragraph and Page Break
    # ==============================

    # Single Skip
    theToken._theText = (
        "# Title One\n\n"
        "[NEW PAGE]\n\n"
        "[VSPACE]\n\n"
        "Some text to go here ...\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  5, "", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  7, "Some text to go here ...", [], 0),
        (Tokenizer.T_EMPTY, 8, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 8, "", None, Tokenizer.A_NONE),
    ]

    # Multiple Skip
    theToken._theText = (
        "# Title One\n\n"
        "[NEW PAGE]\n\n"
        "[VSPACE:3]\n\n"
        "Some text to go here ...\n\n"
    )
    theToken.tokenizeText()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  5, "", None, Tokenizer.A_PBB),
        (Tokenizer.T_SKIP,  5, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  5, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 6, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  7, "Some text to go here ...", [], 0),
        (Tokenizer.T_EMPTY, 8, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 8, "", None, Tokenizer.A_NONE),
    ]

# END Test testCoreToken_SpecialFormat


@pytest.mark.core
def testCoreToken_ProcessHeaders(mockGUI):
    """Test the header and page parser of the Tokenizer class.
    """
    theProject = NWProject(mockGUI)
    theProject.projLang = "en"
    theProject._loadProjectLocalisation()
    theToken = BareTokenizer(theProject)

    # Nothing
    theToken._theText = "Some text ...\n"
    assert theToken.doHeaders() is False
    theToken._isNone = True
    assert theToken.doHeaders() is False
    theToken._isNone = False
    assert theToken.doHeaders() is False
    theToken._isNote = True
    assert theToken.doHeaders() is False
    theToken._isNote = False

    ##
    #  Story FIles
    ##

    theToken._isNone  = False
    theToken._isNote  = False
    theToken._isNovel = True

    # Titles
    # ======

    # H1: Title, First Page
    assert theToken._isFirst is True
    theToken._theText = "# Part One\n"
    theToken.setTitleFormat(r"T: %title%")
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "T: Part One", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H1: Title, Not First Page
    assert theToken._isFirst is False
    theToken._theText = "# Part One\n"
    theToken.setTitleFormat(r"T: %title%")
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD1, 1, "T: Part One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Chapters
    # ========

    # H2: Chapter
    theToken._theText = "## Chapter One\n"
    theToken.setChapterFormat(r"C: %title%")
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD2, 1, "C: Chapter One", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Unnumbered Chapter
    theToken._theText = "##! Prologue\n"
    theToken.setUnNumberedFormat(r"U: %title%")
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_UNNUM, 1, "U: Prologue", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Chapter Word Number
    theToken._theText = "## Chapter\n"
    theToken.setChapterFormat(r"Chapter %chw%")
    theToken._numChapter = 0
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter One", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Chapter Roman Number Upper Case
    theToken._theText = "## Chapter\n"
    theToken.setChapterFormat(r"Chapter %chI%")
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter II", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Chapter Roman Number Lower Case
    theToken._theText = "## Chapter\n"
    theToken.setChapterFormat(r"Chapter %chi%")
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter iii", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Scenes
    # ======

    # H3: Scene w/Title
    theToken._theText = "### Scene One\n"
    theToken.setSceneFormat(r"S: %title%", False)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD3, 1, "S: Scene One", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene Hidden wo/Format
    theToken._theText = "### Scene One\n"
    theToken.setSceneFormat(r"", True)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene wo/Format, first
    theToken._theText = "### Scene One\n"
    theToken.setSceneFormat(r"", False)
    theToken._firstScene = True
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene wo/Format, not first
    theToken._theText = "### Scene One\n"
    theToken.setSceneFormat(r"", False)
    theToken._firstScene = False
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_SKIP, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene Separator, first
    theToken._theText = "### Scene One\n"
    theToken.setSceneFormat(r"* * *", False)
    theToken._firstScene = True
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene Separator, not first
    theToken._theText = "### Scene One\n"
    theToken.setSceneFormat(r"* * *", False)
    theToken._firstScene = False
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_SEP, 1, "* * *", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene w/Absolute Number
    theToken._theText = "### A Scene\n"
    theToken.setSceneFormat(r"Scene %sca%", False)
    theToken._numAbsScene = 0
    theToken._numChScene = 0
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD3, 1, "Scene 1", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene w/Chapter Number
    theToken._theText = "### A Scene\n"
    theToken.setSceneFormat(r"Scene %ch%.%sc%", False)
    theToken._numAbsScene = 0
    theToken._numChScene = 1
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD3, 1, "Scene 3.2", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Sections
    # ========

    # H4: Section Hidden wo/Format
    theToken._theText = "#### A Section\n"
    theToken.setSectionFormat(r"", True)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H4: Section Visible wo/Format
    theToken._theText = "#### A Section\n"
    theToken.setSectionFormat(r"", False)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_SKIP, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H4: Section w/Format
    theToken._theText = "#### A Section\n"
    theToken.setSectionFormat(r"X: %title%", False)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_HEAD4, 1, "X: A Section", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H4: Section Separator
    theToken._theText = "#### A Section\n"
    theToken.setSectionFormat(r"* * *", False)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._theTokens == [
        (Tokenizer.T_SEP, 1, "* * *", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Check the first scene detector
    assert theToken._firstScene is False
    theToken._firstScene = True
    theToken._theText = "Some text ...\n"
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken._firstScene is False

# END Test testCoreToken_ProcessHeaders
