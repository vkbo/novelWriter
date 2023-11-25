"""
novelWriter – Tokenizer Class Tester
====================================

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
from __future__ import annotations

import json
import pytest

from tools import C, buildTestProject, readFile

from novelwriter.constants import nwHeadFmt
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import Tokenizer, stripEscape


class BareTokenizer(Tokenizer):
    def doConvert(self):
        super().doConvert()


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
    assert tokens._fmtSection == nwHeadFmt.TITLE
    assert tokens._textFont == "Serif"
    assert tokens._textSize == 11
    assert tokens._textFixed is False
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
    assert tokens._hideScene is False
    assert tokens._hideSection is False
    assert tokens._linkHeaders is False
    assert tokens._doBodyText is True
    assert tokens._doSynopsis is False
    assert tokens._doComments is False
    assert tokens._doKeywords is False

    # Set new values
    tokens.setTitleFormat(f"T: {nwHeadFmt.TITLE}")
    tokens.setChapterFormat(f"C: {nwHeadFmt.TITLE}")
    tokens.setUnNumberedFormat(f"U: {nwHeadFmt.TITLE}")
    tokens.setSceneFormat(f"S: {nwHeadFmt.TITLE}", True)
    tokens.setSectionFormat(f"X: {nwHeadFmt.TITLE}", True)
    tokens.setFont("Monospace", 10, True)
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
    tokens.setLinkHeaders(True)
    tokens.setBodyText(False)
    tokens.setSynopsis(True)
    tokens.setComments(True)
    tokens.setKeywords(True)

    # Check new values
    assert tokens._fmtTitle == f"T: {nwHeadFmt.TITLE}"
    assert tokens._fmtChapter == f"C: {nwHeadFmt.TITLE}"
    assert tokens._fmtUnNum == f"U: {nwHeadFmt.TITLE}"
    assert tokens._fmtScene == f"S: {nwHeadFmt.TITLE}"
    assert tokens._fmtSection == f"X: {nwHeadFmt.TITLE}"
    assert tokens._textFont == "Monospace"
    assert tokens._textSize == 10
    assert tokens._textFixed is True
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
    assert tokens._hideScene is True
    assert tokens._hideSection is True
    assert tokens._linkHeaders is True
    assert tokens._doBodyText is False
    assert tokens._doSynopsis is True
    assert tokens._doComments is True
    assert tokens._doKeywords is True

    # Check Limits
    tokens.setLineHeight(0.0)
    assert tokens._lineHeight == 0.5
    tokens.setLineHeight(10.0)
    assert tokens._lineHeight == 5.0

    tokens.setBlockIndent(-6.0)
    assert tokens._blockIndent == 0.0
    tokens.setBlockIndent(60.0)
    assert tokens._blockIndent == 10.0

# END Test testCoreToken_Setters


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
    assert tokens.addRootHeading("stuff") is False
    assert tokens.addRootHeading(C.hSceneDoc) is False

    # First Page
    assert tokens.addRootHeading(C.hPlotRoot) is True
    assert tokens.theMarkdown[-1] == "# Notes: Plot\n\n"
    assert tokens._tokens[-1] == (
        Tokenizer.T_TITLE, 0, "Notes: Plot", None, Tokenizer.A_CENTRE
    )

    # Not First Page
    assert tokens.addRootHeading(C.hPlotRoot) is True
    assert tokens.theMarkdown[-1] == "# Notes: Plot\n\n"
    assert tokens._tokens[-1] == (
        Tokenizer.T_TITLE, 0, "Notes: Plot", None, Tokenizer.A_CENTRE | Tokenizer.A_PBB
    )

    # Set Text
    assert tokens.setText("stuff") is False
    assert tokens.setText(C.hSceneDoc) is True
    assert tokens._text == docText

    assert tokens.setText(C.hSceneDoc, docText) is True
    assert tokens._text == docText

    assert tokens._isNone is False
    assert tokens._isNovel is True
    assert tokens._isNote is False

    # Pre Processing
    tokens.doPreProcessing()
    assert tokens._text == docTextR

    # Save File
    savePath = fncPath / "dump.nwd"
    tokens.saveRawMarkdown(savePath)
    assert readFile(savePath) == (
        "# Notes: Plot\n\n"
        "# Notes: Plot\n\n"
    )
    tokens.saveRawMarkdownJSON(savePath)
    assert json.loads(readFile(savePath))["text"] == {
        "nwd": [
            ["# Notes: Plot"],
            ["# Notes: Plot"]
        ]
    }

    # Check abstract method
    with pytest.raises(NotImplementedError):
        tokens.doConvert()

# END Test testCoreToken_TextOps


@pytest.mark.core
def testCoreToken_StripEscape():
    """Test the stripEscape helper function."""
    text1 = "This is text with escapes: \\** \\~~ \\__"
    text2 = "This is text with escapes: ** ~~ __"
    assert stripEscape(text1) == "This is text with escapes: ** ~~ __"
    assert stripEscape(text2) == "This is text with escapes: ** ~~ __"

# END Test testCoreToken_StripEscape


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
    tokens._isNote  = False
    tokens._isFirst = True
    tokens._text = "#! Novel Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TITLE, 1, "Novel Title", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "#! Novel Title\n\n"

    # Note File
    tokens._isNovel = False
    tokens._isNote  = True
    tokens._isFirst = True
    tokens._text = "#! Note Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Note Title", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "#! Note Title\n\n"

    # Header 1
    # ========

    # Story File
    tokens._isNovel = True
    tokens._isNote  = False
    tokens._isFirst = True
    tokens._text = "# Novel Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Novel Title", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "# Novel Title\n\n"

    # Note File
    tokens._isNovel = False
    tokens._isNote  = True
    tokens._isFirst = True
    tokens._text = "# Note Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Note Title", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "# Note Title\n\n"

    # Header 2
    # ========

    # Story File
    tokens._isNovel = True
    tokens._isNote  = False
    tokens._text = "## Chapter One\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter One", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "## Chapter One\n\n"

    # Note File
    tokens._isNovel = False
    tokens._isNote  = True
    tokens._text = "## Heading 2\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Heading 2", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "## Heading 2\n\n"

    # Header 3
    # ========

    # Story File
    tokens._isNovel = True
    tokens._isNote  = False
    tokens._text = "### Scene One\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD3, 1, "Scene One", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "### Scene One\n\n"

    # Note File
    tokens._isNovel = False
    tokens._isNote  = True
    tokens._text = "### Heading 3\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD3, 1, "Heading 3", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "### Heading 3\n\n"

    # Header 4
    # ========

    # Story File
    tokens._isNovel = True
    tokens._isNote  = False
    tokens._text = "#### A Section\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD4, 1, "A Section", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "#### A Section\n\n"

    # Note File
    tokens._isNovel = False
    tokens._isNote  = True
    tokens._text = "#### Heading 4\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD4, 1, "Heading 4", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "#### Heading 4\n\n"

    # Title
    # =====

    # Story File
    tokens._isNovel = True
    tokens._isNote  = False
    tokens._text = "#! Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_TITLE, 1, "Title", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "#! Title\n\n"

    # Note File
    tokens._isNovel = False
    tokens._isNote  = True
    tokens._text = "#! Title\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "#! Title\n\n"

    # Unnumbered
    # ==========

    # Story File
    tokens._isNovel = True
    tokens._isNote  = False
    tokens._text = "##! Prologue\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_UNNUM, 1, "Prologue", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "##! Prologue\n\n"

    # Note File
    tokens._isNovel = False
    tokens._isNote  = True
    tokens._text = "##! Prologue\n"

    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Prologue", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "##! Prologue\n\n"

# END Test testCoreToken_HeaderFormat


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
        (Tokenizer.T_COMMENT, 0, "A comment", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "\n"

    tokens.setComments(True)
    tokens.tokenizeText()
    assert tokens.theMarkdown[-1] == "% A comment\n\n"

    # Synopsis
    tokens._text = "%synopsis: The synopsis\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_SYNOPSIS, 0, "The synopsis", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    tokens._text = "% synopsis: The synopsis\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_SYNOPSIS, 0, "The synopsis", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "\n"

    tokens.setSynopsis(True)
    tokens.tokenizeText()
    assert tokens.theMarkdown[-1] == "% synopsis: The synopsis\n\n"

    # Brief
    tokens.setSynopsis(False)
    tokens._text = "% brief: A description\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_BRIEF, 0, "A description", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "\n"

    tokens.setSynopsis(True)
    tokens.tokenizeText()
    assert tokens.theMarkdown[-1] == "% brief: A description\n\n"

    # Keyword
    tokens._text = "@char: Bod\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_KEYWORD, 0, "char: Bod", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "\n"

    tokens.setKeywords(True)
    tokens.tokenizeText()
    assert tokens.theMarkdown[-1] == "@char: Bod\n\n"

    tokens._text = "@pov: Bod\n@plot: Main\n@location: Europe\n"
    tokens.tokenizeText()
    styTop = Tokenizer.A_NONE | Tokenizer.A_Z_BTMMRG
    styMid = Tokenizer.A_NONE | Tokenizer.A_Z_BTMMRG | Tokenizer.A_Z_TOPMRG
    styBtm = Tokenizer.A_NONE | Tokenizer.A_Z_TOPMRG
    assert tokens._tokens == [
        (Tokenizer.T_KEYWORD, 0, "pov: Bod", None, styTop),
        (Tokenizer.T_KEYWORD, 0, "plot: Main", None, styMid),
        (Tokenizer.T_KEYWORD, 0, "location: Europe", None, styBtm),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "@pov: Bod\n@plot: Main\n@location: Europe\n\n"

# END Test testCoreToken_MetaFormat


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
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  0, "Some left-aligned text", [], Tokenizer.A_LEFT),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  0, "Some right-aligned text", [], Tokenizer.A_RIGHT),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  0, "Some centered text", [], Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  0, "Left-indented block", [], Tokenizer.A_IND_L),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  0, "Right-indented block", [], Tokenizer.A_IND_R),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  0, "Double-indented block", [], dblIndent),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  0, "Right-indent, right-aligned", [], rIndAlign),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == (
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
    assert fmt == [(10, tokens.FMT_B_B), (14, tokens.FMT_B_E)]

    # Plain italics
    text, fmt = tokens._extractFormats("Text with _italics_ in it.")
    assert text == "Text with italics in it."
    assert fmt == [(10, tokens.FMT_I_B), (17, tokens.FMT_I_E)]

    # Plain strikethrough
    text, fmt = tokens._extractFormats("Text with ~~strikethrough~~ in it.")
    assert text == "Text with strikethrough in it."
    assert fmt == [(10, tokens.FMT_D_B), (23, tokens.FMT_D_E)]

    # Nested bold/italics
    text, fmt = tokens._extractFormats("Text with **bold and _italics_** in it.")
    assert text == "Text with bold and italics in it."
    assert fmt == [
        (10, tokens.FMT_B_B), (19, tokens.FMT_I_B), (26, tokens.FMT_I_E), (26, tokens.FMT_B_E)
    ]

    # Bold with overlapping italics
    # Here, bold is ignored because it is not on word boundary
    text, fmt = tokens._extractFormats("Text with **bold and overlapping _italics**_ in it.")
    assert text == "Text with **bold and overlapping italics** in it."
    assert fmt == [(33, tokens.FMT_I_B), (42, tokens.FMT_I_E)]

    # Shortcodes
    # ==========

    # Plain bold
    text, fmt = tokens._extractFormats("Text with [b]bold[/b] in it.")
    assert text == "Text with bold in it."
    assert fmt == [(10, tokens.FMT_B_B), (14, tokens.FMT_B_E)]

    # Plain italics
    text, fmt = tokens._extractFormats("Text with [i]italics[/i] in it.")
    assert text == "Text with italics in it."
    assert fmt == [(10, tokens.FMT_I_B), (17, tokens.FMT_I_E)]

    # Plain strikethrough
    text, fmt = tokens._extractFormats("Text with [s]strikethrough[/s] in it.")
    assert text == "Text with strikethrough in it."
    assert fmt == [(10, tokens.FMT_D_B), (23, tokens.FMT_D_E)]

    # Plain underline
    text, fmt = tokens._extractFormats("Text with [u]underline[/u] in it.")
    assert text == "Text with underline in it."
    assert fmt == [(10, tokens.FMT_U_B), (19, tokens.FMT_U_E)]

    # Plain superscript
    text, fmt = tokens._extractFormats("Text with super[sup]script[/sup] in it.")
    assert text == "Text with superscript in it."
    assert fmt == [(15, tokens.FMT_SUP_B), (21, tokens.FMT_SUP_E)]

    # Plain subscript
    text, fmt = tokens._extractFormats("Text with sub[sub]script[/sub] in it.")
    assert text == "Text with subscript in it."
    assert fmt == [(13, tokens.FMT_SUB_B), (19, tokens.FMT_SUB_E)]

    # Nested bold/italics
    text, fmt = tokens._extractFormats("Text with [b]bold and [i]italics[/i][/b] in it.")
    assert text == "Text with bold and italics in it."
    assert fmt == [
        (10, tokens.FMT_B_B), (19, tokens.FMT_I_B), (26, tokens.FMT_I_E), (26, tokens.FMT_B_E)
    ]

    # Bold with overlapping italics
    # With shortcodes, this works
    text, fmt = tokens._extractFormats(
        "Text with [b]bold and overlapping [i]italics[/b][/i] in it."
    )
    assert text == "Text with bold and overlapping italics in it."
    assert fmt == [
        (10, tokens.FMT_B_B), (31, tokens.FMT_I_B), (38, tokens.FMT_B_E), (38, tokens.FMT_I_E)
    ]

# END Test testCoreToken_ExtractFormats


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
        (Tokenizer.T_TEXT, 0, "Some plain text", [], Tokenizer.A_NONE),
        (Tokenizer.T_TEXT, 0, "on two lines", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "Some plain text\non two lines\n\n\n\n"

    tokens.setBodyText(False)
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "\n\n\n"
    tokens.setBodyText(True)

    # Text Emphasis
    tokens._text = "Some **bolded text** on this lines\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "Some bolded text on this lines",
            [
                (5,  Tokenizer.FMT_B_B),
                (16, Tokenizer.FMT_B_E),
            ],
            Tokenizer.A_NONE
        ),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "Some **bolded text** on this lines\n\n"

    tokens._text = "Some _italic text_ on this lines\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "Some italic text on this lines",
            [
                (5,  Tokenizer.FMT_I_B),
                (16, Tokenizer.FMT_I_E),
            ],
            Tokenizer.A_NONE
        ),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "Some _italic text_ on this lines\n\n"

    tokens._text = "Some **_bold italic text_** on this lines\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "Some bold italic text on this lines",
            [
                (5,  Tokenizer.FMT_B_B),
                (5,  Tokenizer.FMT_I_B),
                (21, Tokenizer.FMT_I_E),
                (21, Tokenizer.FMT_B_E),
            ],
            Tokenizer.A_NONE
        ),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "Some **_bold italic text_** on this lines\n\n"

    tokens._text = "Some ~~strikethrough text~~ on this lines\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "Some strikethrough text on this lines",
            [
                (5,  Tokenizer.FMT_D_B),
                (23, Tokenizer.FMT_D_E),
            ],
            Tokenizer.A_NONE
        ),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == "Some ~~strikethrough text~~ on this lines\n\n"

    tokens._text = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    tokens.tokenizeText()
    assert tokens._tokens == [
        (
            Tokenizer.T_TEXT, 0,
            "Some nested bold and italic and strikethrough text here",
            [
                (5,  Tokenizer.FMT_B_B),
                (21, Tokenizer.FMT_I_B),
                (27, Tokenizer.FMT_I_E),
                (32, Tokenizer.FMT_D_B),
                (45, Tokenizer.FMT_D_E),
                (50, Tokenizer.FMT_B_E),
            ],
            Tokenizer.A_NONE
        ),
        (Tokenizer.T_EMPTY, 0, "", None, Tokenizer.A_NONE),
    ]
    assert tokens.theMarkdown[-1] == (
        "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n\n"
    )

# END Test testCoreToken_TextFormat


@pytest.mark.core
def testCoreToken_SpecialFormat(mockGUI):
    """Test the tokenization of special formats in the Tokenizer class."""
    project = NWProject()
    tokens = BareTokenizer(project)

    tokens._isNovel = True

    # New Page
    # ========

    correctResp = [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_HEAD1, 2, "Title Two", None, Tokenizer.A_CENTRE | Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 2, "", None, Tokenizer.A_NONE),
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
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
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
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Three Skips
    tokens._text = (
        "# Title One\n\n"
        "[vspace:3] \n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Malformed Command, Case 1
    tokens._text = (
        "# Title One\n\n"
        "[vspace:3xa] \n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Malformed Command, Case 2
    tokens._text = (
        "# Title One\n\n"
        "[vspace:3.5]\n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Malformed Command, Case 3
    tokens._text = (
        "# Title One\n\n"
        "[vspace:-1]\n\n"
        "Some text to go here ...\n\n"
    )
    tokens.tokenizeText()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
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
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], 0),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
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
        (Tokenizer.T_HEAD1, 1, "Title One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", None, Tokenizer.A_PBB),
        (Tokenizer.T_SKIP,  1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_SKIP,  1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_TEXT,  1, "Some text to go here ...", [], 0),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

# END Test testCoreToken_SpecialFormat


@pytest.mark.core
def testCoreToken_ProcessHeaders(mockGUI):
    """Test the header and page parser of the Tokenizer class."""
    project = NWProject()
    project.data.setLanguage("en")
    project._loadProjectLocalisation()
    tokens = BareTokenizer(project)

    # Nothing
    tokens._text = "Some text ...\n"
    assert tokens.doHeaders() is False
    tokens._isNone = True
    assert tokens.doHeaders() is False
    tokens._isNone = False
    assert tokens.doHeaders() is False
    tokens._isNote = True
    assert tokens.doHeaders() is False
    tokens._isNote = False

    ##
    #  Story FIles
    ##

    tokens._isNone  = False
    tokens._isNote  = False
    tokens._isNovel = True

    # Titles
    # ======

    # H1: Title, First Page
    assert tokens._isFirst is True
    tokens._text = "# Part One\n"
    tokens.setTitleFormat(f"T: {nwHeadFmt.TITLE}")
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "T: Part One", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H1: Title, Not First Page
    assert tokens._isFirst is False
    tokens._text = "# Part One\n"
    tokens.setTitleFormat(f"T: {nwHeadFmt.TITLE}")
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD1, 1, "T: Part One", None, Tokenizer.A_PBB | Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Chapters
    # ========

    # H2: Chapter
    tokens._text = "## Chapter One\n"
    tokens.setChapterFormat(f"C: {nwHeadFmt.TITLE}")
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "C: Chapter One", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Unnumbered Chapter
    tokens._text = "##! Prologue\n"
    tokens.setUnNumberedFormat(f"U: {nwHeadFmt.TITLE}")
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_UNNUM, 1, "U: Prologue", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Chapter Word Number
    tokens._text = "## Chapter\n"
    tokens.setChapterFormat(f"Chapter {nwHeadFmt.CH_WORD}")
    tokens._hFormatter._chCount = 0
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter One", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Chapter Roman Number Upper Case
    tokens._text = "## Chapter\n"
    tokens.setChapterFormat(f"Chapter {nwHeadFmt.CH_ROMU}")
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter II", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H2: Chapter Roman Number Lower Case
    tokens._text = "## Chapter\n"
    tokens.setChapterFormat(f"Chapter {nwHeadFmt.CH_ROML}")
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD2, 1, "Chapter iii", None, Tokenizer.A_PBB),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Scenes
    # ======

    # H3: Scene w/Title
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat(f"S: {nwHeadFmt.TITLE}", False)
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD3, 1, "S: Scene One", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene Hidden wo/Format
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat("", True)
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene wo/Format, first
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat("", False)
    tokens._firstScene = True
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene wo/Format, not first
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat("", False)
    tokens._firstScene = False
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_SKIP, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene Separator, first
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat("* * *", False)
    tokens._firstScene = True
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene Separator, not first
    tokens._text = "### Scene One\n"
    tokens.setSceneFormat("* * *", False)
    tokens._firstScene = False
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_SEP, 1, "* * *", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene w/Absolute Number
    tokens._text = "### A Scene\n"
    tokens.setSceneFormat(f"Scene {nwHeadFmt.SC_ABS}", False)
    tokens._hFormatter._scAbsCount = 0
    tokens._hFormatter._scChCount = 0
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD3, 1, "Scene 1", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H3: Scene w/Chapter Number
    tokens._text = "### A Scene\n"
    tokens.setSceneFormat(f"Scene {nwHeadFmt.CH_NUM}.{nwHeadFmt.SC_NUM}", False)
    tokens._hFormatter._scAbsCount = 0
    tokens._hFormatter._scChCount = 1
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD3, 1, "Scene 3.2", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Sections
    # ========

    # H4: Section Hidden wo/Format
    tokens._text = "#### A Section\n"
    tokens.setSectionFormat(r"", True)
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H4: Section Visible wo/Format
    tokens._text = "#### A Section\n"
    tokens.setSectionFormat("", False)
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_SKIP, 1, "", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H4: Section w/Format
    tokens._text = "#### A Section\n"
    tokens.setSectionFormat(f"X: {nwHeadFmt.TITLE}", False)
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_HEAD4, 1, "X: A Section", None, Tokenizer.A_NONE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # H4: Section Separator
    tokens._text = "#### A Section\n"
    tokens.setSectionFormat("* * *", False)
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._tokens == [
        (Tokenizer.T_SEP, 1, "* * *", None, Tokenizer.A_CENTRE),
        (Tokenizer.T_EMPTY, 1, "", None, Tokenizer.A_NONE),
    ]

    # Check the first scene detector
    assert tokens._firstScene is False
    tokens._firstScene = True
    tokens._text = "Some text ...\n"
    tokens.tokenizeText()
    tokens.doHeaders()
    assert tokens._firstScene is False

# END Test testCoreToken_ProcessHeaders
