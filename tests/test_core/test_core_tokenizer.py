"""
novelWriter – Tokenizer Class Tester
====================================

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

import pytest

from PyQt5.QtGui import QFont

from novelwriter.constants import nwHeadFmt
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import HeadingFormatter, Tokenizer, stripEscape
from novelwriter.core.tomarkdown import ToMarkdown

from tests.tools import C, buildTestProject, readFile


class BareTokenizer(Tokenizer):
    def doConvert(self):
        super().doConvert()  # type: ignore (deliberate check)


@pytest.mark.core
def testCoreToken_Setters(mockGUI):
    """Test all the setters for the Tokenizer class."""
    project = NWProject()
    tokens = BareTokenizer(project)

    # Verify defaults
    assert tokens._fmtTitle == nwHeadFmt.TITLE
    assert tokens._fmtChapter == nwHeadFmt.TITLE
    assert tokens._fmtUnNum == nwHeadFmt.TITLE
    assert tokens._fmtScene == nwHeadFmt.TITLE
    assert tokens._fmtHScene == nwHeadFmt.TITLE
    assert tokens._fmtSection == nwHeadFmt.TITLE
    assert tokens._textFont == QFont("Serif", 11)
    assert tokens._lineHeight == 1.15
    assert tokens._blockIndent == 4.0
    assert tokens._doJustify is False
    assert tokens._marginTitle == (1.000, 0.500)
    assert tokens._marginHead1 == (1.000, 0.500)
    assert tokens._marginHead2 == (0.834, 0.500)
    assert tokens._marginHead3 == (0.584, 0.500)
    assert tokens._marginHead4 == (0.584, 0.500)
    assert tokens._marginText == (0.000, 0.584)
    assert tokens._marginMeta == (0.000, 0.584)
    assert tokens._hideTitle is False
    assert tokens._hideChapter is False
    assert tokens._hideUnNum is False
    assert tokens._hideScene is False
    assert tokens._hideHScene is False
    assert tokens._hideSection is False
    assert tokens._linkHeadings is False
    assert tokens._doBodyText is True
    assert tokens._doSynopsis is False
    assert tokens._doComments is False
    assert tokens._doKeywords is False

    # Set new values
    tokens.setTitleFormat(f"T: {nwHeadFmt.TITLE}", True)
    tokens.setChapterFormat(f"C: {nwHeadFmt.TITLE}", True)
    tokens.setUnNumberedFormat(f"U: {nwHeadFmt.TITLE}", True)
    tokens.setSceneFormat(f"S: {nwHeadFmt.TITLE}", True)
    tokens.setHardSceneFormat(f"H: {nwHeadFmt.TITLE}", True)
    tokens.setSectionFormat(f"X: {nwHeadFmt.TITLE}", True)
    tokens.setFont(QFont("Monospace", 10))
    tokens.setLineHeight(2.0)
    tokens.setBlockIndent(6.0)
    tokens.setJustify(True)
    tokens.setTitleMargins(2.0, 2.0)
    tokens.setHead1Margins(2.0, 2.0)
    tokens.setHead2Margins(2.0, 2.0)
    tokens.setHead3Margins(2.0, 2.0)
    tokens.setHead4Margins(2.0, 2.0)
    tokens.setTextMargins(2.0, 2.0)
    tokens.setMetaMargins(2.0, 2.0)
    tokens.setLinkHeadings(True)
    tokens.setBodyText(False)
    tokens.setSynopsis(True)
    tokens.setComments(True)
    tokens.setKeywords(True)

    # Check new values
    assert tokens._fmtTitle == f"T: {nwHeadFmt.TITLE}"
    assert tokens._fmtChapter == f"C: {nwHeadFmt.TITLE}"
    assert tokens._fmtUnNum == f"U: {nwHeadFmt.TITLE}"
    assert tokens._fmtScene == f"S: {nwHeadFmt.TITLE}"
    assert tokens._fmtHScene == f"H: {nwHeadFmt.TITLE}"
    assert tokens._fmtSection == f"X: {nwHeadFmt.TITLE}"
    assert tokens._textFont == QFont("Monospace", 10)
    assert tokens._lineHeight == 2.0
    assert tokens._blockIndent == 6.0
    assert tokens._doJustify is True
    assert tokens._marginTitle == (2.0, 2.0)
    assert tokens._marginHead1 == (2.0, 2.0)
    assert tokens._marginHead2 == (2.0, 2.0)
    assert tokens._marginHead3 == (2.0, 2.0)
    assert tokens._marginHead4 == (2.0, 2.0)
    assert tokens._marginText == (2.0, 2.0)
    assert tokens._marginMeta == (2.0, 2.0)
    assert tokens._hideTitle is True
    assert tokens._hideChapter is True
    assert tokens._hideUnNum is True
    assert tokens._hideScene is True
    assert tokens._hideHScene is True
    assert tokens._hideSection is True
    assert tokens._linkHeadings is True
    assert tokens._doBodyText is False
    assert tokens._doSynopsis is True
    assert tokens._doComments is True
    assert tokens._doKeywords is True

    # Properties
    assert tokens.result == ""
    assert tokens.allMarkdown == []
    assert tokens.textStats == {}
    assert tokens.errData == []

    # Check Limits
    tokens.setLineHeight(0.0)
    assert tokens._lineHeight == 0.5
    tokens.setLineHeight(10.0)
    assert tokens._lineHeight == 5.0

    tokens.setBlockIndent(-6.0)
    assert tokens._blockIndent == 0.0
    tokens.setBlockIndent(60.0)
    assert tokens._blockIndent == 10.0


@pytest.mark.core
def testCoreToken_TextOps(monkeypatch, mockGUI, mockRnd, fncPath):
    """Test handling files and text in the Tokenizer class."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    project.data.setLanguage("en")
    project._loadProjectLocalisation()

    tokens = BareTokenizer(project)
    tokens.setKeepMarkdown(True)

    # Set some content to work with
    docText = (
        "### Scene Six\n\n"
        "This is text with _italic text_, some **bold text**, some ~~deleted text~~, "
        "and some **_mixed text_** and **some _nested_ text**.\n\n"
        "#### Replace\n\n"
        "Also, replace <A> and <B>.\n\n"
    )
    docTextR = docText.replace("<A>", "this").replace("<B>", "that")

    nDoc = project.storage.getDocument(C.hSceneDoc)
    assert nDoc.writeDocument(docText)

    project.data.setAutoReplace({"A": "this", "B": "that"})

    assert project.saveProject()

    # Root Heading
    assert len(tokens._tokens) == 0
    tokens.addRootHeading("stuff")
    tokens.addRootHeading(C.hSceneDoc)
    assert len(tokens._tokens) == 0

    # First Page
    tokens.addRootHeading(C.hPlotRoot)
    assert tokens.allMarkdown[-1] == "#! Notes: Plot\n\n"
    assert tokens._tokens[-1] == (
        Tokenizer.T_TITLE, 1, "Notes: Plot", [], Tokenizer.A_CENTRE
    )

    # Not First Page
    tokens.addRootHeading(C.hPlotRoot)
    assert tokens.allMarkdown[-1] == "#! Notes: Plot\n\n"
    assert tokens._tokens[-1] == (
        Tokenizer.T_TITLE, 1, "Notes: Plot", [], Tokenizer.A_CENTRE | Tokenizer.A_PBB
    )

    # Set Text
    tokens.setText("stuff")
    assert tokens._text == ""

    tokens.setText(C.hSceneDoc)
    assert tokens._text == docText

    tokens.setText(C.hSceneDoc, docText)
    assert tokens._text == docText

    assert tokens._isNovel is True

    # Pre Processing
    tokens.doPreProcessing()
    assert tokens._text == docTextR

    # Save File
    savePath = fncPath / "dump.nwd"
    tokens.saveRawMarkdown(savePath)
    assert readFile(savePath) == (
        "#! Notes: Plot\n\n"
        "#! Notes: Plot\n\n"
    )
    tokens.saveRawMarkdownJSON(savePath)
    assert json.loads(readFile(savePath))["text"] == {
        "nwd": [
            ["#! Notes: Plot"],
            ["#! Notes: Plot"]
        ]
    }

    # Check abstract method
    with pytest.raises(NotImplementedError):
        tokens.doConvert()


@pytest.mark.core
def testCoreToken_StripEscape():
    """Test the stripEscape helper function."""
    text1 = "This is text with escapes: \\** \\~~ \\__"
    text2 = "This is text with escapes: ** ~~ __"
    assert stripEscape(text1) == "This is text with escapes: ** ~~ __"
    assert stripEscape(text2) == "This is text with escapes: ** ~~ __"


@pytest.mark.core
def testCoreToken_HeaderFormat(mockGUI):
    """Test the tokenization of header formats in the Tokenizer class."""
    project = NWProject()
    tokens = BareTokenizer(project)
    tokens.setKeepMarkdown(True)

    # Title
    # =====

    # Story File
    tokens._isNovel = True
    tokens._isFirst = True
    tokens._text = "#! Novel Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TITLE, 1, "Novel Title", [], Tokenizer.A_CENTRE),
    ]
    assert tokens.allMarkdown[-1] == "#! Novel Title\n\n"

    # Note File
    tokens._isNovel = False
    tokens._isFirst = True
    tokens._text = "#! Note Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TITLE, 1, "Note Title", [], Tokenizer.A_CENTRE),
    ]
    assert tokens.allMarkdown[-1] == "#! Note Title\n\n"

    # Header 1
    # ========

    # Story File
    tokens._isNovel = True
    tokens._isFirst = True
    tokens._text = "# Novel Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Novel Title", [], Tokenizer.A_CENTRE),
    ]
    assert tokens.allMarkdown[-1] == "# Novel Title\n\n"

    # Note File
    tokens._isNovel = False
    tokens._isFirst = True
    tokens._text = "# Note Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Note Title", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "# Note Title\n\n"

    # Header 2
    # ========

    # Story File
    tokens._isNovel = True
    tokens._text = "## Chapter One\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter One", [], Tokenizer.A_PBB),
    ]
    assert tokens.allMarkdown[-1] == "## Chapter One\n\n"

    # Note File
    tokens._isNovel = False
    tokens._text = "## Heading 2\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Heading 2", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "## Heading 2\n\n"

    # Header 3
    # ========

    # Story File
    tokens._isNovel = True
    tokens._text = "### Scene One\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD3, 1, "Scene One", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "### Scene One\n\n"

    # Note File
    tokens._isNovel = False
    tokens._text = "### Heading 3\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD3, 1, "Heading 3", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "### Heading 3\n\n"

    # Header 4
    # ========

    # Story File
    tokens._isNovel = True
    tokens._text = "#### A Section\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD4, 1, "A Section", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "#### A Section\n\n"

    # Note File
    tokens._isNovel = False
    tokens._text = "#### Heading 4\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD4, 1, "Heading 4", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "#### Heading 4\n\n"

    # Title
    # =====

    # Story File
    tokens._isNovel = True
    tokens._isFirst = False
    tokens._text = "#! Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TITLE, 1, "Title", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
    ]
    assert tokens.allMarkdown[-1] == "#! Title\n\n"

    # Note File
    tokens._isNovel = False
    tokens._isFirst = False
    tokens._text = "#! Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TITLE, 1, "Title", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
    ]
    assert tokens.allMarkdown[-1] == "#! Title\n\n"

    # Unnumbered
    # ==========

    # Story File
    tokens._isNovel = True
    tokens._text = "##! Prologue\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Prologue", [], Tokenizer.A_PBB),
    ]
    assert tokens.allMarkdown[-1] == "##! Prologue\n\n"

    # Note File
    tokens._isNovel = False
    tokens._text = "##! Prologue\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Prologue", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "##! Prologue\n\n"


@pytest.mark.core
def testCoreToken_HeaderStyle(mockGUI):
    """Test the styling of headers in the Tokenizer class."""
    project = NWProject()
    tokens = BareTokenizer(project)

    def processStyle(text: str, first: bool) -> int:
        tokens._text = text
        tokens._isFirst = first
        tokens.tokenizeText()
        return tokens._tokens[0][4]

    # No Styles
    # =========

    tokens.setTitleStyle(False, False)
    tokens.setChapterStyle(False, False)
    tokens.setSceneStyle(False, False)

    assert tokens._titleStyle == Tokenizer.A_NONE
    assert tokens._chapterStyle == Tokenizer.A_NONE
    assert tokens._sceneStyle == Tokenizer.A_NONE

    # Novel Docs
    tokens._isNovel = True

    # First Document is False
    assert processStyle("# Title\n", False) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", False) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", False) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_NONE

    # First Document is True
    assert processStyle("# Title\n", True) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", True) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", True) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", True) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", True) == Tokenizer.A_CENTRE
    assert processStyle("##! Prologue\n", True) == Tokenizer.A_NONE

    # Note Docs
    tokens._isNovel = False

    # First Document is False
    assert processStyle("# Title\n", False) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", False) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", False) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_NONE

    # First Document is True
    assert processStyle("# Title\n", True) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", True) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", True) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", True) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", True) == Tokenizer.A_CENTRE
    assert processStyle("##! Prologue\n", True) == Tokenizer.A_NONE

    # Center Headers
    # ==============

    tokens.setTitleStyle(True, False)
    tokens.setChapterStyle(True, False)
    tokens.setSceneStyle(True, False)

    assert tokens._titleStyle == Tokenizer.A_CENTRE
    assert tokens._chapterStyle == Tokenizer.A_CENTRE
    assert tokens._sceneStyle == Tokenizer.A_CENTRE

    # Novel Docs
    tokens._isNovel = True

    # First Document is False
    assert processStyle("# Title\n", False) == Tokenizer.A_CENTRE
    assert processStyle("## Chapter\n", False) == Tokenizer.A_CENTRE
    assert processStyle("### Scene\n", False) == Tokenizer.A_CENTRE
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_CENTRE

    # First Document is True
    assert processStyle("# Title\n", True) == Tokenizer.A_CENTRE
    assert processStyle("## Chapter\n", True) == Tokenizer.A_CENTRE
    assert processStyle("### Scene\n", True) == Tokenizer.A_CENTRE
    assert processStyle("#### Section\n", True) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", True) == Tokenizer.A_CENTRE
    assert processStyle("##! Prologue\n", True) == Tokenizer.A_CENTRE

    # Note Docs
    tokens._isNovel = False

    # First Document is False
    assert processStyle("# Title\n", False) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", False) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", False) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_NONE

    # First Document is True
    assert processStyle("# Title\n", True) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", True) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", True) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", True) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", True) == Tokenizer.A_CENTRE
    assert processStyle("##! Prologue\n", True) == Tokenizer.A_NONE

    # Page Break Headers
    # ==================

    tokens.setTitleStyle(False, True)
    tokens.setChapterStyle(False, True)
    tokens.setSceneStyle(False, True)

    assert tokens._titleStyle == Tokenizer.A_PBB
    assert tokens._chapterStyle == Tokenizer.A_PBB
    assert tokens._sceneStyle == Tokenizer.A_PBB

    # Novel Docs
    tokens._isNovel = True

    # First Document is False
    assert processStyle("# Title\n", False) == Tokenizer.A_PBB
    assert processStyle("## Chapter\n", False) == Tokenizer.A_PBB
    assert processStyle("### Scene\n", False) == Tokenizer.A_PBB
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_PBB

    # First Document is True
    assert processStyle("# Title\n", True) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", True) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", True) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", True) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", True) == Tokenizer.A_CENTRE
    assert processStyle("##! Prologue\n", True) == Tokenizer.A_NONE

    # Note Docs
    tokens._isNovel = False

    # First Document is False
    assert processStyle("# Title\n", False) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", False) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", False) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_NONE

    # First Document is True
    assert processStyle("# Title\n", True) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", True) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", True) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", True) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", True) == Tokenizer.A_CENTRE
    assert processStyle("##! Prologue\n", True) == Tokenizer.A_NONE

    # Page Break and Centre Headers
    # =============================

    tokens.setTitleStyle(True, True)
    tokens.setChapterStyle(True, True)
    tokens.setSceneStyle(True, True)

    assert tokens._titleStyle == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert tokens._chapterStyle == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert tokens._sceneStyle == Tokenizer.A_CENTRE | Tokenizer.A_PBB

    # Novel Docs
    tokens._isNovel = True

    # First Document is False
    assert processStyle("# Title\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("## Chapter\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("### Scene\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB

    # First Document is True
    assert processStyle("# Title\n", True) == Tokenizer.A_CENTRE
    assert processStyle("## Chapter\n", True) == Tokenizer.A_CENTRE
    assert processStyle("### Scene\n", True) == Tokenizer.A_CENTRE
    assert processStyle("#### Section\n", True) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", True) == Tokenizer.A_CENTRE
    assert processStyle("##! Prologue\n", True) == Tokenizer.A_CENTRE

    # Note Docs
    tokens._isNovel = False

    # First Document is False
    assert processStyle("# Title\n", False) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", False) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", False) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_NONE

    # First Document is True
    assert processStyle("# Title\n", True) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", True) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", True) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", True) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", True) == Tokenizer.A_CENTRE
    assert processStyle("##! Prologue\n", True) == Tokenizer.A_NONE

    # Check Separation
    # ================
    tokens._isNovel = True

    # Title Styles
    tokens.setTitleStyle(True, True)
    tokens.setChapterStyle(False, False)
    tokens.setSceneStyle(False, False)

    assert tokens._titleStyle == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert tokens._chapterStyle == Tokenizer.A_NONE
    assert tokens._sceneStyle == Tokenizer.A_NONE

    assert processStyle("# Title\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("## Chapter\n", False) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", False) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_NONE

    # Chapter Styles
    tokens.setTitleStyle(False, False)
    tokens.setChapterStyle(True, True)
    tokens.setSceneStyle(False, False)

    assert tokens._titleStyle == Tokenizer.A_NONE
    assert tokens._chapterStyle == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert tokens._sceneStyle == Tokenizer.A_NONE

    assert processStyle("# Title\n", False) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("### Scene\n", False) == Tokenizer.A_NONE
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB

    # Scene Styles
    tokens.setTitleStyle(False, False)
    tokens.setChapterStyle(False, False)
    tokens.setSceneStyle(True, True)

    assert tokens._titleStyle == Tokenizer.A_NONE
    assert tokens._chapterStyle == Tokenizer.A_NONE
    assert tokens._sceneStyle == Tokenizer.A_CENTRE | Tokenizer.A_PBB

    assert processStyle("# Title\n", False) == Tokenizer.A_NONE
    assert processStyle("## Chapter\n", False) == Tokenizer.A_NONE
    assert processStyle("### Scene\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("#### Section\n", False) == Tokenizer.A_NONE
    assert processStyle("#! My Novel\n", False) == Tokenizer.A_CENTRE | Tokenizer.A_PBB
    assert processStyle("##! Prologue\n", False) == Tokenizer.A_NONE


@pytest.mark.core
def testCoreToken_MetaFormat(mockGUI):
    """Test the tokenization of meta formats in the Tokenizer class."""
    project = NWProject()
    tokens = BareTokenizer(project)
    tokens.setKeepMarkdown(True)

    # Comment
    tokens._text = "% A comment\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_COMMENT, 0, "A comment", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "\n"

    tokens.setComments(True)
    tokens.tokenizeText()
    assert tokens.allMarkdown[-1] == "% A comment\n\n"

    # Ignore Text
    tokens._text = "%~ Some text\n"
    tokens.tokenizeText()
    assert tokens._tokens == []
    assert tokens.allMarkdown[-1] == "\n"

    # Synopsis
    tokens._text = "%synopsis: The synopsis\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_SYNOPSIS, 0, "The synopsis", [], Tokenizer.A_NONE),
    ]
    tokens._text = "% synopsis: The synopsis\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_SYNOPSIS, 0, "The synopsis", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "\n"

    tokens.setSynopsis(True)
    tokens.tokenizeText()
    assert tokens.allMarkdown[-1] == "% synopsis: The synopsis\n\n"

    # Short
    tokens.setSynopsis(False)
    tokens._text = "% short: A short description\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_SHORT, 0, "A short description", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "\n"

    tokens.setSynopsis(True)
    tokens.tokenizeText()
    assert tokens.allMarkdown[-1] == "% short: A short description\n\n"

    # Keyword
    tokens._text = "@char: Bod\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_KEYWORD, 0, "char: Bod", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "\n"

    tokens.setKeywords(True)
    tokens.tokenizeText()
    assert tokens.allMarkdown[-1] == "@char: Bod\n\n"

    tokens._text = "@pov: Bod\n@plot: Main\n@location: Europe\n"
    tokens.tokenizeText()
    styTop = Tokenizer.A_NONE | Tokenizer.A_Z_BTMMRG
    styMid = Tokenizer.A_NONE | Tokenizer.A_Z_BTMMRG | Tokenizer.A_Z_TOPMRG
    styBtm = Tokenizer.A_NONE | Tokenizer.A_Z_TOPMRG
    assert tokens._tokens == [
        (Tokenizer.T_KEYWORD, 0, "pov: Bod", [], styTop),
        (Tokenizer.T_KEYWORD, 0, "plot: Main", [], styMid),
        (Tokenizer.T_KEYWORD, 0, "location: Europe", [], styBtm),
    ]
    assert tokens.allMarkdown[-1] == "@pov: Bod\n@plot: Main\n@location: Europe\n\n"

    # Ignored keywords
    tokens._text = "@pov: Bod\n@plot: Main\n@location: Europe\n"
    tokens.setIgnoredKeywords("@plot, @location")
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_KEYWORD, 0, "pov: Bod", [], Tokenizer.A_NONE),
    ]


@pytest.mark.core
def testCoreToken_MarginFormat(mockGUI):
    """Test the tokenization of margin formats in the Tokenizer class."""
    project = NWProject()
    tokens = BareTokenizer(project)
    tokens.setKeepMarkdown(True)

    # Alignment and Indentation
    dblIndent = Tokenizer.A_IND_L | Tokenizer.A_IND_R
    rIndAlign = Tokenizer.A_RIGHT | Tokenizer.A_IND_R
    tokens._text = (
        "Some regular text\n\n"
        "Some left-aligned text <<\n\n"
        ">> Some right-aligned text\n\n"
        ">> Some centered text <<\n\n"
        "> Left-indented block\n\n"
        "Right-indented block <\n\n"
        "> Double-indented block <\n\n"
        ">> Right-indent, right-aligned <\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TEXT,  0, "Some regular text", [], Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  0, "Some left-aligned text", [], Tokenizer.A_LEFT),
        (Tokenizer.T_TEXT,  0, "Some right-aligned text", [], Tokenizer.A_RIGHT),
        (Tokenizer.T_TEXT,  0, "Some centered text", [], Tokenizer.A_CENTRE),
        (Tokenizer.T_TEXT,  0, "Left-indented block", [], Tokenizer.A_IND_L),
        (Tokenizer.T_TEXT,  0, "Right-indented block", [], Tokenizer.A_IND_R),
        (Tokenizer.T_TEXT,  0, "Double-indented block", [], dblIndent),
        (Tokenizer.T_TEXT,  0, "Right-indent, right-aligned", [], rIndAlign),
    ]
    assert tokens.allMarkdown[-1] == (
        "Some regular text\n\n"
        "Some left-aligned text\n\n"
        "Some right-aligned text\n\n"
        "Some centered text\n\n"
        "Left-indented block\n\n"
        "Right-indented block\n\n"
        "Double-indented block\n\n"
        "Right-indent, right-aligned\n\n\n"
    )


@pytest.mark.core
def testCoreToken_ExtractFormats(mockGUI):
    """Test the extraction of formats in the Tokenizer class."""
    project = NWProject()
    tokens = BareTokenizer(project)
    tokens.setKeepMarkdown(True)

    # Markdown
    # ========

    # Plain bold
    text, fmt = tokens._extractFormats("Text with **bold** in it.")
    assert text == "Text with bold in it."
    assert fmt == [(10, tokens.FMT_B_B, ""), (14, tokens.FMT_B_E, "")]

    # Plain italics
    text, fmt = tokens._extractFormats("Text with _italics_ in it.")
    assert text == "Text with italics in it."
    assert fmt == [(10, tokens.FMT_I_B, ""), (17, tokens.FMT_I_E, "")]

    # Plain strikethrough
    text, fmt = tokens._extractFormats("Text with ~~strikethrough~~ in it.")
    assert text == "Text with strikethrough in it."
    assert fmt == [(10, tokens.FMT_D_B, ""), (23, tokens.FMT_D_E, "")]

    # Nested bold/italics
    text, fmt = tokens._extractFormats("Text with **bold and _italics_** in it.")
    assert text == "Text with bold and italics in it."
    assert fmt == [
        (10, tokens.FMT_B_B, ""), (19, tokens.FMT_I_B, ""),
        (26, tokens.FMT_I_E, ""), (26, tokens.FMT_B_E, ""),
    ]

    # Bold with overlapping italics
    # Here, bold is ignored because it is not on word boundary
    text, fmt = tokens._extractFormats("Text with **bold and overlapping _italics**_ in it.")
    assert text == "Text with **bold and overlapping italics** in it."
    assert fmt == [(33, tokens.FMT_I_B, ""), (42, tokens.FMT_I_E, "")]

    # Shortcodes
    # ==========

    # Plain bold
    text, fmt = tokens._extractFormats("Text with [b]bold[/b] in it.")
    assert text == "Text with bold in it."
    assert fmt == [(10, tokens.FMT_B_B, ""), (14, tokens.FMT_B_E, "")]

    # Plain italics
    text, fmt = tokens._extractFormats("Text with [i]italics[/i] in it.")
    assert text == "Text with italics in it."
    assert fmt == [(10, tokens.FMT_I_B, ""), (17, tokens.FMT_I_E, "")]

    # Plain strikethrough
    text, fmt = tokens._extractFormats("Text with [s]strikethrough[/s] in it.")
    assert text == "Text with strikethrough in it."
    assert fmt == [(10, tokens.FMT_D_B, ""), (23, tokens.FMT_D_E, "")]

    # Plain underline
    text, fmt = tokens._extractFormats("Text with [u]underline[/u] in it.")
    assert text == "Text with underline in it."
    assert fmt == [(10, tokens.FMT_U_B, ""), (19, tokens.FMT_U_E, "")]

    # Plain mark
    text, fmt = tokens._extractFormats("Text with [m]highlight[/m] in it.")
    assert text == "Text with highlight in it."
    assert fmt == [(10, tokens.FMT_M_B, ""), (19, tokens.FMT_M_E, "")]

    # Plain superscript
    text, fmt = tokens._extractFormats("Text with super[sup]script[/sup] in it.")
    assert text == "Text with superscript in it."
    assert fmt == [(15, tokens.FMT_SUP_B, ""), (21, tokens.FMT_SUP_E, "")]

    # Plain subscript
    text, fmt = tokens._extractFormats("Text with sub[sub]script[/sub] in it.")
    assert text == "Text with subscript in it."
    assert fmt == [(13, tokens.FMT_SUB_B, ""), (19, tokens.FMT_SUB_E, "")]

    # Nested bold/italics
    text, fmt = tokens._extractFormats("Text with [b]bold and [i]italics[/i][/b] in it.")
    assert text == "Text with bold and italics in it."
    assert fmt == [
        (10, tokens.FMT_B_B, ""), (19, tokens.FMT_I_B, ""),
        (26, tokens.FMT_I_E, ""), (26, tokens.FMT_B_E, ""),
    ]

    # Bold with overlapping italics
    # With shortcodes, this works
    text, fmt = tokens._extractFormats(
        "Text with [b]bold and overlapping [i]italics[/b][/i] in it."
    )
    assert text == "Text with bold and overlapping italics in it."
    assert fmt == [
        (10, tokens.FMT_B_B, ""), (31, tokens.FMT_I_B, ""),
        (38, tokens.FMT_B_E, ""), (38, tokens.FMT_I_E, ""),
    ]

    # So does this
    text, fmt = tokens._extractFormats(
        "Text with [b]bold and overlapping [i]italics[/b] in[/i] it."
    )
    assert text == "Text with bold and overlapping italics in it."
    assert fmt == [
        (10, tokens.FMT_B_B, ""), (31, tokens.FMT_I_B, ""),
        (38, tokens.FMT_B_E, ""), (41, tokens.FMT_I_E, ""),
    ]


@pytest.mark.core
def testCoreToken_Paragraphs(mockGUI):
    """Test the splitting of paragraphs."""
    project = NWProject()
    tokens = BareTokenizer(project)
    tokens.setKeepMarkdown(True)

    # Collapse empty lines
    tokens._text = "First paragraph\n\n\nSecond paragraph\n\n\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TEXT, 0, "First paragraph", [], Tokenizer.A_NONE),
        (Tokenizer.T_TEXT, 0, "Second paragraph", [], Tokenizer.A_NONE),
    ]

    # Combine multi-line paragraphs, keep breaks
    tokens._text = "This is text\nspanning multiple\nlines"
    tokens.setKeepLineBreaks(True)
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TEXT, 0, "This is text\nspanning multiple\nlines", [], Tokenizer.A_NONE),
    ]

    # Combine multi-line paragraphs, remove breaks
    tokens._text = "This is text\nspanning multiple\nlines"
    tokens.setKeepLineBreaks(False)
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TEXT, 0, "This is text spanning multiple lines", [], Tokenizer.A_NONE),
    ]

    # Combine multi-line paragraphs, remove breaks, with formatting
    tokens._text = "This **is text**\nspanning _multiple_\nlines"
    tokens.setKeepLineBreaks(False)
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "This is text spanning multiple lines",
            [
                (5,  Tokenizer.FMT_B_B, ""),
                (12, Tokenizer.FMT_B_E, ""),
                (22, Tokenizer.FMT_I_B, ""),
                (30, Tokenizer.FMT_I_E, ""),
            ],
            Tokenizer.A_NONE
        ),
    ]

    # Make sure titles break a paragraph
    tokens._text = "# Title\nText _on_\ntwo lines.\n## Chapter\nMore **text**\n_here_.\n\n\n"
    tokens.setKeepLineBreaks(False)
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title", [], Tokenizer.A_NONE),
        (
            Tokenizer.T_TEXT, 1, "Text on two lines.", [
                (5, Tokenizer.FMT_I_B, ""),
                (7, Tokenizer.FMT_I_E, ""),
            ], Tokenizer.A_NONE
        ),
        (Tokenizer.T_HEAD2, 2, "Chapter", [], Tokenizer.A_NONE),
        (
            Tokenizer.T_TEXT, 2, "More text here.", [
                (5,  Tokenizer.FMT_B_B, ""),
                (9,  Tokenizer.FMT_B_E, ""),
                (10, Tokenizer.FMT_I_B, ""),
                (14, Tokenizer.FMT_I_E, ""),
            ], Tokenizer.A_NONE
        ),
    ]


@pytest.mark.core
def testCoreToken_TextFormat(mockGUI):
    """Test the tokenization of text formats in the Tokenizer class."""
    project = NWProject()
    tokens = BareTokenizer(project)
    tokens.setKeepMarkdown(True)

    # Text
    tokens._text = "Some plain text\non two lines\n\n\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TEXT, 0, "Some plain text\non two lines", [], Tokenizer.A_NONE),
    ]
    assert tokens.allMarkdown[-1] == "Some plain text\non two lines\n\n\n\n"

    tokens.setBodyText(False)
    tokens.tokenizeText()
    assert tokens._tokens == []
    assert tokens.allMarkdown[-1] == "\n\n\n"
    tokens.setBodyText(True)

    # Text Emphasis
    tokens._text = "Some **bolded text** on this lines\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "Some bolded text on this lines",
            [
                (5,  Tokenizer.FMT_B_B, ""),
                (16, Tokenizer.FMT_B_E, ""),
            ],
            Tokenizer.A_NONE
        ),
    ]
    assert tokens.allMarkdown[-1] == "Some **bolded text** on this lines\n\n"

    tokens._text = "Some _italic text_ on this lines\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "Some italic text on this lines",
            [
                (5,  Tokenizer.FMT_I_B, ""),
                (16, Tokenizer.FMT_I_E, ""),
            ],
            Tokenizer.A_NONE
        ),
    ]
    assert tokens.allMarkdown[-1] == "Some _italic text_ on this lines\n\n"

    tokens._text = "Some **_bold italic text_** on this lines\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "Some bold italic text on this lines",
            [
                (5,  Tokenizer.FMT_B_B, ""),
                (5,  Tokenizer.FMT_I_B, ""),
                (21, Tokenizer.FMT_I_E, ""),
                (21, Tokenizer.FMT_B_E, ""),
            ],
            Tokenizer.A_NONE
        ),
    ]
    assert tokens.allMarkdown[-1] == "Some **_bold italic text_** on this lines\n\n"

    tokens._text = "Some ~~strikethrough text~~ on this lines\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "Some strikethrough text on this lines",
            [
                (5,  Tokenizer.FMT_D_B, ""),
                (23, Tokenizer.FMT_D_E, ""),
            ],
            Tokenizer.A_NONE
        ),
    ]
    assert tokens.allMarkdown[-1] == "Some ~~strikethrough text~~ on this lines\n\n"

    tokens._text = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "Some nested bold and italic and strikethrough text here",
            [
                (5,  Tokenizer.FMT_B_B, ""),
                (21, Tokenizer.FMT_I_B, ""),
                (27, Tokenizer.FMT_I_E, ""),
                (32, Tokenizer.FMT_D_B, ""),
                (45, Tokenizer.FMT_D_E, ""),
                (50, Tokenizer.FMT_B_E, ""),
            ],
            Tokenizer.A_NONE
        ),
    ]
    assert tokens.allMarkdown[-1] == (
        "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n\n"
    )


@pytest.mark.core
def testCoreToken_SpecialFormat(mockGUI):
    """Test the tokenization of special formats in the Tokenizer class."""
    project = NWProject()
    tokens = BareTokenizer(project)

    tokens._isNovel = True

    # New Page
    # ========

    correctResp = [
        (Tokenizer.T_HEAD1, 1, "Title One", [], Tokenizer.A_CENTRE),
        (Tokenizer.T_HEAD1, 2, "Title Two", [], Tokenizer.A_CENTRE | Tokenizer.A_PBB),
    ]

    # Command wo/Space
    tokens._isFirst = True
    tokens._text = (
        "# Title One\n\n"
        "[newpage]\n\n"
        "# Title Two\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == correctResp

    # Command w/Space
    tokens._isFirst = True
    tokens._text = (
        "# Title One\n\n"
        "[new page]\n\n"
        "# Title Two\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == correctResp

    # Trailing Spaces
    tokens._isFirst = True
    tokens._text = (
        "# Title One\n\n"
        "[new page]   \t\n\n"
        "# Title Two\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == correctResp

    # Single Empty Paragraph
    # ======================

    tokens._text = (
        "# Title One\n\n"
        "[vspace] \n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_SKIP,  1, "", [], Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
    ]

    # Multiple Empty Paragraphs
    # =========================

    # One Skip
    tokens._text = (
        "# Title One\n\n"
        "[vspace:1] \n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_SKIP,  1, "", [], Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
    ]

    # Three Skips
    tokens._text = (
        "# Title One\n\n"
        "[vspace:3] \n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_SKIP,  1, "", [], Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", [], Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", [], Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
    ]

    # Malformed Command, Case 1
    tokens._text = (
        "# Title One\n\n"
        "[vspace:3xa] \n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
    ]

    # Malformed Command, Case 2
    tokens._text = (
        "# Title One\n\n"
        "[vspace:3.5]\n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
    ]

    # Malformed Command, Case 3
    tokens._text = (
        "# Title One\n\n"
        "[vspace:-1]\n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
    ]

    # Empty Paragraph and Page Break
    # ==============================

    # Single Skip
    tokens._text = (
        "# Title One\n\n"
        "[new page]\n\n"
        "[vspace]\n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_SKIP,  1, "", [], Tokenizer.A_PBB),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], 0),
    ]

    # Multiple Skip
    tokens._text = (
        "# Title One\n\n"
        "[new page]\n\n"
        "[vspace:3]\n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_SKIP,  1, "", [], Tokenizer.A_PBB),
        (Tokenizer.T_SKIP,  1, "", [], Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", [], Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], 0),
    ]


@pytest.mark.core
def testCoreToken_ProcessHeaders(mockGUI):
    """Test the header and page parser of the Tokenizer class."""
    project = NWProject()
    project.data.setLanguage("en")
    project._loadProjectLocalisation()
    tokens = BareTokenizer(project)

    ##
    #  Story Files
    ##

    tokens._isNovel = True

    # Titles
    # ======

    # H1: Title, First Page
    assert tokens._isFirst is True
    tokens._text = "# Part One\n"
    tokens.setTitleFormat(f"T: {nwHeadFmt.TITLE}")
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "T: Part One", [], Tokenizer.A_CENTRE),
    ]

    # H1: Title, Not First Page
    assert tokens._isFirst is False
    tokens._text = "# Part One\n"
    tokens.setTitleFormat(f"T: {nwHeadFmt.TITLE}")
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "T: Part One", [], Tokenizer.A_PBB | Tokenizer.A_CENTRE),
    ]

    # Chapters
    # ========

    # H2: Chapter
    tokens._text = "## Chapter One\n"
    tokens.setChapterFormat(f"C: {nwHeadFmt.TITLE}")
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "C: Chapter One", [], Tokenizer.A_PBB),
    ]

    # H2: Unnumbered Chapter
    tokens._text = "##! Prologue\n"
    tokens.setUnNumberedFormat(f"U: {nwHeadFmt.TITLE}")
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "U: Prologue", [], Tokenizer.A_PBB),
    ]

    # H2: Chapter Word Number
    tokens._text = "## Chapter\n"
    tokens.setChapterFormat(f"Chapter {nwHeadFmt.CH_WORD}")
    tokens._hFormatter._chCount = 0
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter One", [], Tokenizer.A_PBB),
    ]

    # H2: Chapter Roman Number Upper Case
    tokens._text = "## Chapter\n"
    tokens.setChapterFormat(f"Chapter {nwHeadFmt.CH_ROMU}")
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter II", [], Tokenizer.A_PBB),
    ]

    # H2: Chapter Roman Number Lower Case
    tokens._text = "## Chapter\n"
    tokens.setChapterFormat(f"Chapter {nwHeadFmt.CH_ROML}")
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter iii", [], Tokenizer.A_PBB),
    ]

    # Scenes
    # ======

    # H3: Scene w/Title
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat(f"S: {nwHeadFmt.TITLE}", False)
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD3, 1, "S: Scene One", [], Tokenizer.A_NONE),
    ]

    # H3: Scene Hidden wo/Format
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat("", True)
    tokens.tokenizeText()
    assert tokens._tokens == []

    # H3: Scene wo/Format, first
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat("", False)
    tokens._noSep = True
    tokens.tokenizeText()
    assert tokens._tokens == []

    # H3: Scene wo/Format, not first
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat("", False)
    tokens._noSep = False
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_SKIP, 1, "", [], Tokenizer.A_NONE),
    ]

    # H3: Scene Separator, first
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat("* * *", False)
    tokens._noSep = True
    tokens.tokenizeText()
    assert tokens._tokens == []

    # H3: Scene Separator, not first
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat("* * *", False)
    tokens._noSep = False
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_SEP, 1, "* * *", [], Tokenizer.A_CENTRE),
    ]

    # H3: Scene w/Absolute Number
    tokens._text = "### A Scene\n"
    tokens.setSceneFormat(f"Scene {nwHeadFmt.SC_ABS}", False)
    tokens._hFormatter._scAbsCount = 0
    tokens._hFormatter._scChCount = 0
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD3, 1, "Scene 1", [], Tokenizer.A_NONE),
    ]

    # H3: Scene w/Chapter Number
    tokens._text = "### A Scene\n"
    tokens.setSceneFormat(f"Scene {nwHeadFmt.CH_NUM}.{nwHeadFmt.SC_NUM}", False)
    tokens._hFormatter._scAbsCount = 0
    tokens._hFormatter._scChCount = 1
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD3, 1, "Scene 3.2", [], Tokenizer.A_NONE),
    ]

    # Sections
    # ========

    # H4: Section Hidden wo/Format
    tokens._text = "#### A Section\n"
    tokens.setSectionFormat("", True)
    tokens.tokenizeText()
    assert tokens._tokens == []

    # H4: Section Visible wo/Format
    tokens._text = "#### A Section\n"
    tokens.setSectionFormat("", False)
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_SKIP, 1, "", [], Tokenizer.A_NONE),
    ]

    # H4: Section w/Format
    tokens._text = "#### A Section\n"
    tokens.setSectionFormat(f"X: {nwHeadFmt.TITLE}", False)
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD4, 1, "X: A Section", [], Tokenizer.A_NONE),
    ]

    # H4: Section Separator
    tokens._text = "#### A Section\n"
    tokens.setSectionFormat("* * *", False)
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_SEP, 1, "* * *", [], Tokenizer.A_CENTRE),
    ]

    # Check the first scene detector, plain text
    tokens._noSep = True
    tokens._text = "Some text ...\n"
    tokens.tokenizeText()
    assert tokens._noSep is True

    # Check the first scene detector, text plus scene
    tokens._noSep = True
    tokens._text = "Some text ...\n\n### Scene\n\nText"
    tokens.tokenizeText()
    assert tokens._noSep is False


@pytest.mark.core
def testCoreToken_BuildOutline(mockGUI, ipsumText):
    """Test stats counter of the Tokenizer class."""
    project = NWProject()
    project.data.setLanguage("en")
    project._loadProjectLocalisation()
    tokens = BareTokenizer(project)

    # Novel
    tokens._isNovel = True
    tokens._handle = "0000000000000"
    tokens._text = (
        "#! My Novel\n\n"
        "# Part One\n\n"
        "## Chapter One\n\n"
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "###! Scene Four\n\n"
        "Text\n\n"
        "#### Section\n\n"
        "Text\n\n"
    )
    tokens.tokenizeText()
    tokens.buildOutline()

    # Note
    tokens._isNovel = False
    tokens._handle = "0000000000001"
    tokens._text = (
        "#! My Notes\n\n"
        "# Header 1\n\n"
        "Text\n\n"
        "## Header 2\n\n"
        "Text\n\n"
        "### Header 3\n\n"
        "Text\n\n"
        "#### Header 4\n\n"
        "Text\n\n"
    )
    tokens.tokenizeText()
    tokens.buildOutline()

    # Check Outline
    assert tokens.textOutline == {
        "0000000000000:T0001": "TT|My Novel",
        "0000000000000:T0002": "PT|Part One",
        "0000000000000:T0003": "CH|Chapter One",
        "0000000000000:T0004": "SC|Scene One",
        "0000000000000:T0005": "SC|Scene Two",
        "0000000000000:T0006": "CH|Chapter Two",
        "0000000000000:T0007": "SC|Scene Three",
        "0000000000000:T0008": "SC|Scene Four",
        "0000000000001:T0001": "TT|My Notes",
        "0000000000001:T0002": "H1|Header 1",
        "0000000000001:T0003": "H2|Header 2",
        "0000000000001:T0004": "H3|Header 3",
    }


@pytest.mark.core
def testCoreToken_CountStats(mockGUI, ipsumText):
    """Test stats counter of the Tokenizer class."""
    project = NWProject()
    project.data.setLanguage("en")
    project._loadProjectLocalisation()
    tokens = BareTokenizer(project)
    tokens._isNovel = True

    # Short Text
    # ==========

    # Header wo/Format
    tokens._text = "## A Chapter Title\n\n"
    tokens._counts = {}
    tokens.tokenizeText()
    tokens.countStats()
    assert tokens._tokens[0][2] == "A Chapter Title"
    assert tokens.textStats == {
        "titleCount": 1, "paragraphCount": 0,
        "allWords": 3, "textWords": 0, "titleWords": 3,
        "allChars": 15, "textChars": 0, "titleChars": 15,
        "allWordChars": 13, "textWordChars": 0, "titleWordChars": 13
    }

    # Header w/Format
    tokens._text = "## A Chapter Title\n\n"
    tokens._counts = {}
    tokens.setChapterFormat(f"C {nwHeadFmt.CH_NUM}: {nwHeadFmt.TITLE}")
    tokens._hFormatter.resetAll()
    tokens.tokenizeText()
    tokens.countStats()
    assert tokens._tokens[0][2] == "C 1: A Chapter Title"
    assert tokens.textStats == {
        "titleCount": 1, "paragraphCount": 0,
        "allWords": 5, "textWords": 0, "titleWords": 5,
        "allChars": 20, "textChars": 0, "titleChars": 20,
        "allWordChars": 16, "textWordChars": 0, "titleWordChars": 16
    }

    # Two Paragraphs
    # First break should be counted, the double breaks not.
    tokens._text = "Some text\non two lines.\n\nWith a second paragraph.\n\n"
    tokens._counts = {}
    tokens.tokenizeText()
    tokens.countStats()
    assert tokens.textStats == {
        "titleCount": 0, "paragraphCount": 2,
        "allWords": 9, "textWords": 9, "titleWords": 0,
        "allChars": 47, "textChars": 47, "titleChars": 0,
        "allWordChars": 40, "textWordChars": 40, "titleWordChars": 0
    }

    # Two Scenes w/Separator
    tokens._text = "## Chapter\n\n### Scene\n\nText\n\n### Scene\n\nText"
    tokens._counts = {}
    tokens.setChapterFormat(nwHeadFmt.TITLE)
    tokens.setSceneFormat("* * *", False)
    tokens.tokenizeText()
    tokens.countStats()
    assert [t[2] for t in tokens._tokens] == ["Chapter", "Text", "* * *", "Text"]
    assert tokens.textStats == {
        "titleCount": 1, "paragraphCount": 2,
        "allWords": 6, "textWords": 2, "titleWords": 1,
        "allChars": 20, "textChars": 8, "titleChars": 7,
        "allWordChars": 18, "textWordChars": 8, "titleWordChars": 7
    }

    # Scene w/Synopsis
    # Synopsis does not count as a paragraph, and counts as "Synopsis: Stuff"
    tokens._text = "## Chapter\n\n### Scene\n\n%Synopsis: Stuff\n\nText"
    tokens._counts = {}
    tokens.setChapterFormat(nwHeadFmt.TITLE)
    tokens.setSceneFormat("* * *", False)
    tokens.setSynopsis(True)
    tokens.tokenizeText()
    tokens.countStats()
    assert [t[2] for t in tokens._tokens] == ["Chapter", "Stuff", "Text"]
    assert tokens.textStats == {
        "titleCount": 1, "paragraphCount": 1,
        "allWords": 4, "textWords": 1, "titleWords": 1,
        "allChars": 26, "textChars": 4, "titleChars": 7,
        "allWordChars": 25, "textWordChars": 4, "titleWordChars": 7
    }

    # Scene w/Short
    # Short does not count as a paragraph, and counts as "Short Description: Stuff"
    tokens._text = "## Chapter\n\n### Scene\n\n%Short: Stuff\n\nText"
    tokens._counts = {}
    tokens.setChapterFormat(nwHeadFmt.TITLE)
    tokens.setSceneFormat("* * *", False)
    tokens.setSynopsis(True)
    tokens.tokenizeText()
    tokens.countStats()
    assert [t[2] for t in tokens._tokens] == ["Chapter", "Stuff", "Text"]
    assert tokens.textStats == {
        "titleCount": 1, "paragraphCount": 1,
        "allWords": 5, "textWords": 1, "titleWords": 1,
        "allChars": 35, "textChars": 4, "titleChars": 7,
        "allWordChars": 33, "textWordChars": 4, "titleWordChars": 7
    }

    # Scene w/Comment
    # Comment does not count as a paragraph, and counts as "Comment: Stuff"
    tokens._text = "## Chapter\n\n### Scene\n\n% Stuff\n\nText"
    tokens._counts = {}
    tokens.setChapterFormat(nwHeadFmt.TITLE)
    tokens.setSceneFormat("* * *", False)
    tokens.setComments(True)
    tokens.tokenizeText()
    tokens.countStats()
    assert [t[2] for t in tokens._tokens] == ["Chapter", "Stuff", "Text"]
    assert tokens.textStats == {
        "titleCount": 1, "paragraphCount": 1,
        "allWords": 4, "textWords": 1, "titleWords": 1,
        "allChars": 25, "textChars": 4, "titleChars": 7,
        "allWordChars": 24, "textWordChars": 4, "titleWordChars": 7
    }

    # Scene w/Keyword
    # Keyword does not count as a paragraph, and counts as "Point of View: Jane"
    tokens._text = "## Chapter\n\n### Scene\n\n@pov: Jane\n\nText"
    tokens._counts = {}
    tokens.setChapterFormat(nwHeadFmt.TITLE)
    tokens.setSceneFormat("* * *", False)
    tokens.setKeywords(True)
    tokens.tokenizeText()
    tokens.countStats()
    assert [t[2] for t in tokens._tokens] == ["Chapter", "pov: Jane", "Text"]
    assert tokens.textStats == {
        "titleCount": 1, "paragraphCount": 1,
        "allWords": 6, "textWords": 1, "titleWords": 1,
        "allChars": 30, "textChars": 4, "titleChars": 7,
        "allWordChars": 27, "textWordChars": 4, "titleWordChars": 7
    }

    # Long Text
    # =========
    tokens._text = (
        "# Act One\n\n"

        "## Chapter\n\n"

        "### Scene\n\n"
        "@pov: Jane\n"
        "@char: Jane, John\n\n"
        "%Synopsis: A scene\n\n"
        f"{ipsumText[0]}.\n\n"

        "### Scene\n\n"
        "@pov: Jane\n"
        "@char: Jane, John\n\n"
        "%Synopsis: A scene\n\n"
        f"{ipsumText[1]}.\n\n"

        "## Chapter\n\n"

        "### Scene\n\n"
        "@pov: Jane\n"
        "@char: Jane, John\n\n"
        "%Synopsis: A scene\n\n"
        f"{ipsumText[2]}.\n\n"

        "### Scene\n\n"
        "@pov: Jane\n"
        "@char: Jane, John\n\n"
        "%Synopsis: A scene\n\n"
        f"{ipsumText[3]}.\n\n"

        "## Chapter\n\n"

        "### Scene\n\n"
        "@pov: Jane\n"
        "@char: Jane, John\n\n"
        "%Synopsis: A scene\n\n"
        f"{ipsumText[4]}.\n\n"
    )
    tokens._counts = {}

    tokens.setTitleFormat(f"T: {nwHeadFmt.TITLE}")
    tokens.setChapterFormat(f"C {nwHeadFmt.CH_NUM}: {nwHeadFmt.TITLE}")
    tokens.setSceneFormat("* * *", False)
    tokens.setSynopsis(True)
    tokens.setComments(True)
    tokens.setKeywords(True)

    tokens.tokenizeText()
    tokens.countStats()
    assert tokens.textStats == {
        "titleCount": 4, "paragraphCount": 5,
        "allWords": 596, "textWords": 528, "titleWords": 12,
        "allChars": 3859, "textChars": 3513, "titleChars": 46,
        "allWordChars": 3289, "textWordChars": 2990, "titleWordChars": 38
    }


@pytest.mark.core
def testCoreToken_SceneSeparators(mockGUI):
    """Test the section and scene separators of the Tokenizer class."""
    project = NWProject()
    project.data.setLanguage("en")
    project._loadProjectLocalisation()
    md = ToMarkdown(project)
    md._isNovel = True

    # Separator Handling, Titles
    # ==========================

    md._text = (
        "# Title One\n\n"
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "Text\n\n"
        "# Title Two\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "###! Scene Four\n\n"
        "Text\n\n"
    )
    md.setTitleFormat(f"T: {nwHeadFmt.TITLE}")
    md.setChapterFormat(f"C: {nwHeadFmt.TITLE}")
    md.setSectionFormat("", True)

    # Static Separator
    md.setSceneFormat("~", False)
    md.setHardSceneFormat("* * *", False)
    md.tokenizeText()
    md.doConvert()
    assert md.result == (
        "# T: Title One\n\n"
        "Text\n\n"
        "~\n\n"
        "Text\n\n"
        "# T: Title Two\n\n"
        "Text\n\n"
        "* * *\n\n"
        "Text\n\n"
    )

    # Scene Title Formatted
    md.setSceneFormat(f"S: {nwHeadFmt.TITLE}", False)
    md.setHardSceneFormat(f"H: {nwHeadFmt.TITLE}", False)
    md.tokenizeText()
    md.doConvert()
    assert md.result == (
        "# T: Title One\n\n"
        "### S: Scene One\n\n"
        "Text\n\n"
        "### S: Scene Two\n\n"
        "Text\n\n"
        "# T: Title Two\n\n"
        "### S: Scene Three\n\n"
        "Text\n\n"
        "### H: Scene Four\n\n"
        "Text\n\n"
    )

    # Separator Handling, Chapters
    # ============================

    md._text = (
        "# Title One\n\n"
        "## Chapter One\n\n"
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "###! Scene Four\n\n"
        "Text\n\n"
    )
    md.setTitleFormat(f"T: {nwHeadFmt.TITLE}")
    md.setChapterFormat(f"C: {nwHeadFmt.TITLE}")
    md.setSectionFormat("", True)

    # Static Separator
    md.setSceneFormat("* * *", False)
    md.setHardSceneFormat("* * *", False)
    md.tokenizeText()
    md.doConvert()
    assert md.result == (
        "# T: Title One\n\n"
        "## C: Chapter One\n\n"
        "Text\n\n"
        "* * *\n\n"
        "Text\n\n"
        "## C: Chapter Two\n\n"
        "Text\n\n"
        "* * *\n\n"
        "Text\n\n"
    )

    # Scene Title Formatted
    md.setSceneFormat(f"S: {nwHeadFmt.TITLE}", False)
    md.setHardSceneFormat(f"H: {nwHeadFmt.TITLE}", False)
    md.tokenizeText()
    md.doConvert()
    assert md.result == (
        "# T: Title One\n\n"
        "## C: Chapter One\n\n"
        "### S: Scene One\n\n"
        "Text\n\n"
        "### S: Scene Two\n\n"
        "Text\n\n"
        "## C: Chapter Two\n\n"
        "### S: Scene Three\n\n"
        "Text\n\n"
        "### H: Scene Four\n\n"
        "Text\n\n"
    )

    # Separators with Scenes Only
    # ===========================
    # Requires a fresh builder class
    md = ToMarkdown(project)
    md.setExtendedMarkdown(True)
    md._isNovel = True

    md._text = (
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "Text\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "###! Scene Four\n\n"
        "Text\n\n"
    )

    md.setSceneFormat("", False)
    md.setHardSceneFormat("* * *", False)
    md.tokenizeText()
    md.doConvert()
    assert md.result == (
        "Text\n\n"
        "\u205f\n\n"
        "Text\n\n"
        "\u205f\n\n"
        "Text\n\n"
        "* * *\n\n"
        "Text\n\n"
    )


@pytest.mark.core
def testCoreToken_HeaderVisibility(mockGUI):
    """Test the heading visibility settings of the Tokenizer class."""
    project = NWProject()
    project.data.setLanguage("en")
    project._loadProjectLocalisation()
    md = ToMarkdown(project)

    md._text = (
        "#! Novel\n\n"
        "# Title One\n\n"
        "##! Prologue\n\n"
        "Text\n\n"
        "## Chapter One\n\n"
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "#### Section Two\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "###! Scene Four\n\n"
        "Text\n\n"
    )

    # Novel Files
    # ===========

    md._isNovel = True

    # Show All
    md.setTitleFormat(nwHeadFmt.TITLE, False)
    md.setChapterFormat(nwHeadFmt.TITLE, False)
    md.setUnNumberedFormat(nwHeadFmt.TITLE, False)
    md.setSceneFormat(nwHeadFmt.TITLE, False)
    md.setHardSceneFormat(nwHeadFmt.TITLE, False)
    md.setSectionFormat(nwHeadFmt.TITLE, False)

    md.tokenizeText()
    md.doConvert()
    assert md.result == (
        "# Novel\n\n"
        "# Title One\n\n"
        "## Prologue\n\n"
        "Text\n\n"
        "## Chapter One\n\n"
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "#### Section Two\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "### Scene Four\n\n"
        "Text\n\n"
    )

    # Hide All
    md.setTitleFormat(nwHeadFmt.TITLE, True)
    md.setChapterFormat(nwHeadFmt.TITLE, True)
    md.setUnNumberedFormat(nwHeadFmt.TITLE, True)
    md.setSceneFormat(nwHeadFmt.TITLE, True)
    md.setHardSceneFormat(nwHeadFmt.TITLE, True)
    md.setSectionFormat(nwHeadFmt.TITLE, True)

    md.tokenizeText()
    md.doConvert()
    assert md.result == (
        "# Novel\n\n"
        "Text\n\n"
        "Text\n\n"
        "Text\n\n"
        "Text\n\n"
        "Text\n\n"
    )

    # Note Files
    # ==========

    md._isNovel = False

    # Hide All
    md.setTitleFormat(nwHeadFmt.TITLE, True)
    md.setChapterFormat(nwHeadFmt.TITLE, True)
    md.setUnNumberedFormat(nwHeadFmt.TITLE, True)
    md.setSceneFormat(nwHeadFmt.TITLE, True)
    md.setHardSceneFormat(nwHeadFmt.TITLE, True)
    md.setSectionFormat(nwHeadFmt.TITLE, True)

    md.tokenizeText()
    md.doConvert()
    assert md.result == (
        "# Novel\n\n"
        "# Title One\n\n"
        "## Prologue\n\n"
        "Text\n\n"
        "## Chapter One\n\n"
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "#### Section Two\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "### Scene Four\n\n"
        "Text\n\n"
    )


@pytest.mark.core
def testCoreToken_CounterHandling(mockGUI):
    """Test the heading counter of the Tokenizer class."""
    project = NWProject()
    project.data.setLanguage("en")
    project._loadProjectLocalisation()
    md = ToMarkdown(project)
    md._isNovel = True

    # Counter Handling, Novel Titles
    # ==============================
    # This also checks that only numbered chapters bump the counter

    md._text = (
        "#! Novel One\n\n"
        "##! Prologue\n\n"
        "Text\n\n"
        "## Chapter One\n\n"
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "###! Scene Four\n\n"
        "Text\n\n"
        "#! Novel Two\n\n"
        "##! Prologue\n\n"
        "Text\n\n"
        "## Chapter One\n\n"
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "###! Scene Four\n\n"
        "Text\n\n"
    )
    md.setTitleFormat(f"T: {nwHeadFmt.TITLE}")
    md.setChapterFormat(f"C {nwHeadFmt.CH_NUM}: {nwHeadFmt.TITLE}")
    md.setUnNumberedFormat(f"U: {nwHeadFmt.TITLE}")
    md.setSceneFormat(
        f"S {nwHeadFmt.CH_NUM}.{nwHeadFmt.SC_NUM} ({nwHeadFmt.SC_ABS}): {nwHeadFmt.TITLE}", False
    )
    md.setHardSceneFormat(
        f"H {nwHeadFmt.CH_NUM}.{nwHeadFmt.SC_NUM} ({nwHeadFmt.SC_ABS}): {nwHeadFmt.TITLE}", False
    )
    md.setSectionFormat("", True)

    # Two Novel Format
    md.tokenizeText()
    md.doConvert()
    assert md.result == (
        "# Novel One\n\n"
        "## U: Prologue\n\n"
        "Text\n\n"
        "## C 1: Chapter One\n\n"
        "### S 1.1 (1): Scene One\n\n"
        "Text\n\n"
        "### S 1.2 (2): Scene Two\n\n"
        "Text\n\n"
        "## C 2: Chapter Two\n\n"
        "### S 2.1 (3): Scene Three\n\n"
        "Text\n\n"
        "### H 2.2 (4): Scene Four\n\n"
        "Text\n\n"
        "# Novel Two\n\n"
        "## U: Prologue\n\n"
        "Text\n\n"
        "## C 1: Chapter One\n\n"
        "### S 1.1 (1): Scene One\n\n"
        "Text\n\n"
        "### S 1.2 (2): Scene Two\n\n"
        "Text\n\n"
        "## C 2: Chapter Two\n\n"
        "### S 2.1 (3): Scene Three\n\n"
        "Text\n\n"
        "### H 2.2 (4): Scene Four\n\n"
        "Text\n\n"
    )


@pytest.mark.core
def testCoreToken_HeadingFormatter(fncPath, mockGUI, mockRnd):
    """Check the HeadingFormatter class."""
    project = NWProject()
    project.setProjectLang("en_GB")
    mockRnd.reset()
    buildTestProject(project, fncPath)

    nHandle = project.newFile("Hello", C.hNovelRoot)
    cHandle = project.newFile("Jane",  C.hCharRoot)
    dHandle = project.newFile("John",  C.hCharRoot)

    assert isinstance(nHandle, str)
    assert isinstance(cHandle, str)
    assert isinstance(dHandle, str)

    assert project.index.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane | Jane Smith\n"
    ))
    assert project.index.scanText(dHandle, (
        "# John Smith\n"
        "@tag: John | John Smith\n"
    ))
    assert project.index.scanText(nHandle, (
        "## Hi Bob\n"
        "@pov: Jane\n"
        "@focus: John\n"
        "@char: Jane, John\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n"
    ))

    formatter = HeadingFormatter(project)
    formatter.setHandle(nHandle)

    # Counters
    # ========
    cFormat = (
        f"Chapter {nwHeadFmt.CH_NUM}.{nwHeadFmt.SC_NUM} - "
        f"Scene {nwHeadFmt.SC_ABS} - {nwHeadFmt.TITLE}"
    )

    # Initial
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter 0.0 - Scene 0 - Hi Bob"

    # First Chapter and Scene
    formatter.incChapter()
    formatter.incScene()
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter 1.1 - Scene 1 - Hi Bob"

    # Next Scenes
    formatter.incScene()
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter 1.2 - Scene 2 - Hi Bob"
    formatter.incScene()
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter 1.3 - Scene 3 - Hi Bob"
    formatter.incScene()
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter 1.4 - Scene 4 - Hi Bob"

    # Next Chapter and Scene
    formatter.incChapter()
    formatter.resetScene()
    formatter.incScene()
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter 2.1 - Scene 5 - Hi Bob"

    # New Main Title
    formatter.resetAll()
    formatter.incChapter()
    formatter.incScene()
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter 1.1 - Scene 1 - Hi Bob"

    # Special Formats
    # ===============
    formatter._chCount = 2
    formatter._scChCount = 3
    formatter._scAbsCount = 8

    # Chapter Number Word
    cFormat = f"Chapter {nwHeadFmt.CH_WORD}, Scene {nwHeadFmt.SC_NUM} - {nwHeadFmt.TITLE}"
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter Two, Scene 3 - Hi Bob"

    # Chapter Upper Case Roman
    cFormat = f"Chapter {nwHeadFmt.CH_ROMU}, Scene {nwHeadFmt.SC_NUM} - {nwHeadFmt.TITLE}"
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter II, Scene 3 - Hi Bob"

    # Chapter Lower Case Roman
    cFormat = f"Chapter {nwHeadFmt.CH_ROML}, Scene {nwHeadFmt.SC_NUM} - {nwHeadFmt.TITLE}"
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter ii, Scene 3 - Hi Bob"

    # Chapter w/PoV Character
    cFormat = f"Chapter {nwHeadFmt.CH_NUM}, Scene {nwHeadFmt.SC_NUM} - {nwHeadFmt.CHAR_POV}"
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter 2, Scene 3 - Jane Smith"

    # Chapter w/Focus Character
    cFormat = f"Chapter {nwHeadFmt.CH_NUM}, Scene {nwHeadFmt.SC_NUM} - {nwHeadFmt.CHAR_FOCUS}"
    assert formatter.apply(cFormat, "Hi Bob", 1) == "Chapter 2, Scene 3 - John Smith"

    # Chapter w/Fallback PoV
    cFormat = f"Chapter {nwHeadFmt.CH_NUM}, Scene {nwHeadFmt.SC_NUM} - {nwHeadFmt.CHAR_POV}"
    assert formatter.apply(cFormat, "Hi Bob", 0) == "Chapter 2, Scene 3 - Point of View"

    # Chapter w/Fallback Focus
    cFormat = f"Chapter {nwHeadFmt.CH_NUM}, Scene {nwHeadFmt.SC_NUM} - {nwHeadFmt.CHAR_FOCUS}"
    assert formatter.apply(cFormat, "Hi Bob", 0) == "Chapter 2, Scene 3 - Focus"
