# -*- coding: utf-8 -*-
"""
novelWriter – Tokenizer Class Tester
====================================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

import pytest

from nw.core import NWProject, NWDoc
from nw.core.tokenizer import Tokenizer

@pytest.mark.core
def testCoreToken_Setters(dummyGUI):
    """Test all the setters for the Tokenizer class.
    """
    theProject = NWProject(dummyGUI)
    theToken = Tokenizer(theProject, dummyGUI)

    # Verify defaults
    assert theToken.fmtTitle == "%title%"
    assert theToken.fmtChapter == "%title%"
    assert theToken.fmtUnNum == "%title%"
    assert theToken.fmtScene == "%title%"
    assert theToken.fmtSection == "%title%"
    assert theToken.hideScene is False
    assert theToken.hideSection is False
    assert theToken.linkHeaders is False
    assert theToken.doBodyText is True
    assert theToken.doSynopsis is False
    assert theToken.doComments is False
    assert theToken.doKeywords is False
    assert theToken.doJustify is False

    # Set new values
    theToken.setTitleFormat("T: %title%")
    theToken.setChapterFormat("C: %title%")
    theToken.setUnNumberedFormat("U: %title%")
    theToken.setSceneFormat("S: %title%", True)
    theToken.setSectionFormat("X: %title%", True)
    theToken.setLinkHeaders(True)
    theToken.setBodyText(False)
    theToken.setSynopsis(True)
    theToken.setComments(True)
    theToken.setKeywords(True)
    theToken.setJustify(True)

    # Check new values
    assert theToken.fmtTitle == "T: %title%"
    assert theToken.fmtChapter == "C: %title%"
    assert theToken.fmtUnNum == "U: %title%"
    assert theToken.fmtScene == "S: %title%"
    assert theToken.fmtSection == "X: %title%"
    assert theToken.hideScene is True
    assert theToken.hideSection is True
    assert theToken.linkHeaders is True
    assert theToken.doBodyText is False
    assert theToken.doSynopsis is True
    assert theToken.doComments is True
    assert theToken.doKeywords is True
    assert theToken.doJustify is True

# END Test testCoreToken_Setters

@pytest.mark.core
def testCoreToken_TextOps(monkeypatch, nwMinimal, dummyGUI):
    """Test handling files and text in the Tokenizer class.
    """
    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)
    theToken = Tokenizer(theProject, dummyGUI)

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

    nDoc = NWDoc(theProject, dummyGUI)
    nDoc.openDocument(sHandle)
    nDoc.saveDocument(docText)
    nDoc.clearDocument()

    theProject.setAutoReplace({"A": "this", "B": "that"})

    assert theProject.saveProject()

    # Root heading
    assert theToken.addRootHeading("dummy") is False
    assert theToken.addRootHeading(sHandle) is False
    assert theToken.addRootHeading("7695ce551d265") is True
    assert theToken.theMarkdown == "# Notes: Plot\n\n"

    # Set text
    assert theToken.setText("dummy") is False
    assert theToken.setText(sHandle) is True
    assert theToken.theText == docText

    monkeypatch.setattr("nw.constants.nwConst.MAX_DOCSIZE", 100)
    assert theToken.setText(sHandle, docText) is True
    assert theToken.theText == (
        "# ERROR\n\n"
        "Document 'New Scene' is too big (0.00 MB). Skipping.\n\n"
    )
    monkeypatch.undo()

    assert theToken.setText(sHandle, docText) is True
    assert theToken.theText == docText

    assert theToken.isNone is False
    assert theToken.isTitle is False
    assert theToken.isBook is False
    assert theToken.isPage is False
    assert theToken.isPart is False
    assert theToken.isUnNum is False
    assert theToken.isChap is False
    assert theToken.isScene is True
    assert theToken.isNote is False
    assert theToken.isNovel is True

    # Auto replace
    theToken.doAutoReplace()
    assert theToken.theText == docTextR

    # Access
    assert theToken.getResult() is None
    assert theToken.getResultSize() == 0
    theToken.theResult = ""
    assert theToken.getResultSize() == 0

    # Post Processing
    theToken.theResult = r"This is text with escapes: \** \~~ \__"
    theToken.doPostProcessing()
    assert theToken.theResult == "This is text with escapes: ** ~~ __"

# END Test testCoreToken_TextOps

@pytest.mark.core
def testCoreToken_Tokenize(dummyGUI):
    """Test the tokenization of the Tokenizer class.
    """
    theProject = NWProject(dummyGUI)
    theToken = Tokenizer(theProject, dummyGUI)

    # Header 1
    theToken.theText = "# Novel Title\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD1, 1, "Novel Title", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown == "# Novel Title\n\n"

    # Header 2
    theToken.theText = "## Chapter One\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter One", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown == "## Chapter One\n\n"

    # Header 3
    theToken.theText = "### Scene One\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD3, 1, "Scene One", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown == "### Scene One\n\n"

    # Header 4
    theToken.theText = "#### A Section\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD4, 1, "A Section", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown == "#### A Section\n\n"

    # Comment
    theToken.theText = "% A comment\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
        (Tokenizer.T_COMMENT, 1, "A comment", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown == "\n"

    theToken.setComments(True)
    theToken.tokenizeText()
    assert theToken.theMarkdown == "% A comment\n\n"

    # Symopsis
    theToken.theText = "%synopsis: The synopsis\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
        (Tokenizer.T_SYNOPSIS, 1, "The synopsis", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    theToken.theText = "% synopsis: The synopsis\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
        (Tokenizer.T_SYNOPSIS, 1, "The synopsis", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown == "\n"

    theToken.setSynopsis(True)
    theToken.tokenizeText()
    assert theToken.theMarkdown == "% synopsis: The synopsis\n\n"

    # Keyword
    theToken.theText = "@char: Bod\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
        (Tokenizer.T_KEYWORD, 1, "char: Bod", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown == "\n"

    theToken.setKeywords(True)
    theToken.tokenizeText()
    assert theToken.theMarkdown == "@char: Bod\n\n"

    # Text
    theToken.theText = "Some plain text\non two lines\n\n\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
        (Tokenizer.T_TEXT, 1, "Some plain text", [], Tokenizer.A_NONE),
        (Tokenizer.T_TEXT, 2, "on two lines", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 3, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown == "Some plain text\non two lines\n\n\n\n"

    theToken.setBodyText(False)
    theToken.tokenizeText()
    assert theToken.theTokens == [
        (Tokenizer.T_EMPTY, 3, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 4, "", None, Tokenizer.A_NONE),
    ]
    assert theToken.theMarkdown == "\n\n\n"
    theToken.setBodyText(True)

    # Text Emphasis
    theToken.theText = "Some **bolded text** on this lines\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
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
    assert theToken.theMarkdown == "Some **bolded text** on this lines\n\n"

    theToken.theText = "Some _italic text_ on this lines\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
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
    assert theToken.theMarkdown == "Some _italic text_ on this lines\n\n"

    theToken.theText = "Some **_bold italic text_** on this lines\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
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
    assert theToken.theMarkdown == "Some **_bold italic text_** on this lines\n\n"

    theToken.theText = "Some ~~strikethrough text~~ on this lines\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
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
    assert theToken.theMarkdown == "Some ~~strikethrough text~~ on this lines\n\n"

    theToken.theText = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    theToken.tokenizeText()
    assert theToken.theTokens == [
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
    assert theToken.theMarkdown == (
        "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n\n"
    )

    # Check the markdown function as well
    assert theToken.getFilteredMarkdown() == (
        "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n\n"
    )

# END Test testCoreToken_Tokenize

@pytest.mark.core
def testCoreToken_Headers(dummyGUI):
    """Test the header and page parser of the Tokenizer class.
    """
    theProject = NWProject(dummyGUI)
    theToken = Tokenizer(theProject, dummyGUI)

    # Nothing
    theToken.theText = "Some text ...\n"
    assert theToken.doHeaders() is True
    theToken.isNone = True
    assert theToken.doHeaders() is False
    theToken.isNone = False
    assert theToken.doHeaders() is True
    theToken.isNote = True
    assert theToken.doHeaders() is False
    theToken.isNote = False

    ##
    #  Novel
    ##

    theToken.isNovel = True

    # Titles
    # ======

    # H1: Title
    theToken.theText = "# Novel Title\n"
    theToken.setTitleFormat(r"T: %title%")
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD1, 1, "T: Novel Title", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Chapters
    # ========

    # H2: Chapter
    theToken.theText = "## Chapter One\n"
    theToken.setChapterFormat(r"C: %title%")
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD2, 1, "C: Chapter One", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Unnumbered Chapter
    theToken.theText = "## Chapter One\n"
    theToken.setUnNumberedFormat(r"U: %title%")
    theToken.isUnNum = True
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD2, 1, "U: Chapter One", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Unnumbered Chapter with Star
    theToken.theText = "## *Prologue\n"
    theToken.setUnNumberedFormat(r"U: %title%")
    theToken.isUnNum = False
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD2, 1, "U: Prologue", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Chapter Word Number
    theToken.theText = "## Chapter\n"
    theToken.setChapterFormat(r"Chapter %chw%")
    theToken.numChapter = 0
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter One", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Chapter Roman Number Upper Case
    theToken.theText = "## Chapter\n"
    theToken.setChapterFormat(r"Chapter %chI%")
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter II", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Chapter Roman Number Lower Case
    theToken.theText = "## Chapter\n"
    theToken.setChapterFormat(r"Chapter %chi%")
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter iii", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Scenes
    # ======

    # H3: Scene w/Title
    theToken.theText = "### Scene One\n"
    theToken.setSceneFormat(r"S: %title%", False)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD3, 1, "S: Scene One", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene Hidden wo/Format
    theToken.theText = "### Scene One\n"
    theToken.setSceneFormat(r"", True)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene wo/Format, first
    theToken.theText = "### Scene One\n"
    theToken.setSceneFormat(r"", False)
    theToken.firstScene = True
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene wo/Format, not first
    theToken.theText = "### Scene One\n"
    theToken.setSceneFormat(r"", False)
    theToken.firstScene = False
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_SKIP, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene Separator, first
    theToken.theText = "### Scene One\n"
    theToken.setSceneFormat(r"* * *", False)
    theToken.firstScene = True
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene Separator, not first
    theToken.theText = "### Scene One\n"
    theToken.setSceneFormat(r"* * *", False)
    theToken.firstScene = False
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_SEP, 1, "* * *", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene w/Absolute Number
    theToken.theText = "### A Scene\n"
    theToken.setSceneFormat(r"Scene %sca%", False)
    theToken.numAbsScene = 0
    theToken.numChScene = 0
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD3, 1, "Scene 1", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene w/Chapter Number
    theToken.theText = "### A Scene\n"
    theToken.setSceneFormat(r"Scene %ch%.%sc%", False)
    theToken.numAbsScene = 0
    theToken.numChScene = 1
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD3, 1, "Scene 3.2", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Sections
    # ========

    # H4: Section Hidden wo/Format
    theToken.theText = "#### A Section\n"
    theToken.setSectionFormat(r"", True)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H4: Section Visible wo/Format
    theToken.theText = "#### A Section\n"
    theToken.setSectionFormat(r"", False)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_SKIP, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H4: Section w/Format
    theToken.theText = "#### A Section\n"
    theToken.setSectionFormat(r"X: %title%", False)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD4, 1, "X: A Section", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H4: Section Separator
    theToken.theText = "#### A Section\n"
    theToken.setSectionFormat(r"* * *", False)
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_SEP, 1, "* * *", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Check the first scene detector
    assert theToken.firstScene is False
    theToken.firstScene = True
    assert theToken.firstScene is True
    theToken.theText = "Some text ...\n"
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.firstScene is False

    ##
    #  Title or Partition
    ##

    theToken.isNovel = False

    # H1: Title
    theToken.theText = "# Novel Title\n"
    theToken.tokenizeText()
    theToken.isTitle = True
    theToken.isPart = False
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_TITLE, 1, "Novel Title", None, Tokenizer.A_PBB_NO | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_PBA | Tokenizer.A_CENTRE),
    ]

    # H1: Partition
    theToken.theText = "# Partition Title\n"
    theToken.setTitleFormat(r"T: %title%")
    theToken.tokenizeText()
    theToken.isTitle = False
    theToken.isPart = True
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_HEAD1, 1, "Partition Title", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_PBA | Tokenizer.A_CENTRE),
    ]

    ##
    #  Page
    ##

    theToken.isNovel = False
    theToken.isTitle = False
    theToken.isPart = False
    theToken.isPage = True

    # Some Page Text
    theToken.theText = "Page text\n\nMore text\n"
    theToken.tokenizeText()
    theToken.doHeaders()
    assert theToken.theTokens == [
        (Tokenizer.T_TEXT, 1, "Page text", [], Tokenizer.A_PBB | Tokenizer.A_LEFT),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_LEFT),
        (Tokenizer.T_TEXT, 3, "More text", [], Tokenizer.A_LEFT),
        (Tokenizer.T_EMPTY, 3, "", None, Tokenizer.A_LEFT),
    ]

# END Test testCoreToken_Headers
