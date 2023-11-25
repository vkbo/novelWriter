"""
novelWriter – ToHtml Class Tester
=================================

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

import pytest

from tools import readFile

from novelwriter.core.tohtml import ToHtml
from novelwriter.core.project import NWProject


@pytest.mark.core
def testCoreToHtml_ConvertFormat(mockGUI):
    """Test the tokenizer and converter chain using the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)

    # Novel Files Headers
    # ===================

    html._isNovel = True
    html._isNote = False
    html._isFirst = True

    # Header 1
    html._text = "# Partition\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<h1 class='title' style='text-align: center;'>Partition</h1>\n"
    )

    # Header 2
    html._text = "## Chapter Title\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<h1 style='page-break-before: always;'>Chapter Title</h1>\n"
    )

    # Header 3
    html._text = "### Scene Title\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == "<h2>Scene Title</h2>\n"

    # Header 4
    html._text = "#### Section Title\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == "<h3>Section Title</h3>\n"

    # Title
    html._text = "#! Title\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<h1 class='title' style='text-align: center;'>Title</h1>\n"
    )

    # Unnumbered
    html._text = "##! Prologue\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == "<h1 style='page-break-before: always;'>Prologue</h1>\n"

    # Note Files Headers
    # ==================

    html._isNovel = False
    html._isNote = True
    html._isFirst = True
    html.setLinkHeaders(True)

    # Header 1
    html._text = "# Heading One\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == "<h1><a name='T0001'></a>Heading One</h1>\n"

    # Header 2
    html._text = "## Heading Two\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == "<h2><a name='T0001'></a>Heading Two</h2>\n"

    # Header 3
    html._text = "### Heading Three\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == "<h3><a name='T0001'></a>Heading Three</h3>\n"

    # Header 4
    html._text = "#### Heading Four\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == "<h4><a name='T0001'></a>Heading Four</h4>\n"

    # Title
    html._text = "#! Heading One\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<h1 style='text-align: center;'><a name='T0001'></a>Heading One</h1>\n"
    )

    # Unnumbered
    html._text = "##! Heading Two\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == "<h2><a name='T0001'></a>Heading Two</h2>\n"

    # Paragraphs
    # ==========

    # Text
    html._text = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p>Some <strong>nested bold and <em>italic</em> and "
        "<del>strikethrough</del> text</strong> here</p>\n"
    )

    # Text w/Hard Break
    html._text = "Line one  \nLine two  \nLine three\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p class='break'>Line one<br/>Line two<br/>Line three</p>\n"
    )

    # Synopsis, Brief
    html._text = "%synopsis: The synopsis ...\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == ""

    html.setSynopsis(True)
    html._text = "%synopsis: The synopsis ...\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p class='synopsis'><strong>Synopsis:</strong> The synopsis ...</p>\n"
    )

    html.setSynopsis(True)
    html._text = "%brief: A description ...\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p class='synopsis'><strong>Brief:</strong> A description ...</p>\n"
    )

    # Comment
    html._text = "% A comment ...\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == ""

    html.setComments(True)
    html._text = "% A comment ...\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p class='comment'><strong>Comment:</strong> A comment ...</p>\n"
    )

    # Keywords
    html._text = "@char: Bod, Jane\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == ""

    html.setKeywords(True)
    html._text = "@char: Bod, Jane\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p><span class='tags'>Characters:</span> "
        "<a href='#tag_Bod'>Bod</a>, <a href='#tag_Jane'>Jane</a></p>\n"
    )

    # Multiple Keywords
    html.setKeywords(True)
    html._text = "## Chapter\n\n@pov: Bod\n@plot: Main\n@location: Europe\n\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<h2>"
        "<a name='T0001'></a>Chapter</h2>\n"
        "<p style='margin-bottom: 0;'>"
        "<span class='tags'>Point of View:</span> <a href='#tag_Bod'>Bod</a>"
        "</p>\n"
        "<p style='margin-bottom: 0; margin-top: 0;'>"
        "<span class='tags'>Plot:</span> <a href='#tag_Main'>Main</a>"
        "</p>\n"
        "<p style='margin-top: 0;'>"
        "<span class='tags'>Locations:</span> <a href='#tag_Europe'>Europe</a>"
        "</p>\n"
    )

    # Preview Mode
    # ============

    html.setPreview(True, True)

    # Text (HTML4)
    html._text = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p>Some <b>nested bold and <i>italic</i> and "
        "<span style='text-decoration: line-through;'>strikethrough</span> "
        "text</b> here</p>\n"
    )

# END Test testCoreToHtml_ConvertFormat


@pytest.mark.core
def testCoreToHtml_ConvertDirect(mockGUI):
    """Test the converter directly using the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)

    html._isNovel = True
    html._isNote = False
    html.setLinkHeaders(True)

    # Special Titles
    # ==============

    # Title
    html._tokens = [
        (html.T_TITLE, 1, "A Title", None, html.A_PBB | html.A_CENTRE),
        (html.T_EMPTY, 1, "", None, html.A_NONE),
    ]
    html.doConvert()
    assert html.theResult == (
        "<h1 class='title' style='text-align: center; page-break-before: always;'>"
        "<a name='T0001'></a>A Title</h1>\n"
    )

    # Unnumbered
    html._tokens = [
        (html.T_UNNUM, 1, "Prologue", None, html.A_PBB),
        (html.T_EMPTY, 1, "", None, html.A_NONE),
    ]
    html.doConvert()
    assert html.theResult == (
        "<h1 style='page-break-before: always;'>"
        "<a name='T0001'></a>Prologue</h1>\n"
    )

    # Separators
    # ==========

    # Separator
    html._tokens = [
        (html.T_SEP, 1, "* * *", None, html.A_CENTRE),
        (html.T_EMPTY, 1, "", None, html.A_NONE),
    ]
    html.doConvert()
    assert html.theResult == "<p class='sep' style='text-align: center;'>* * *</p>\n"

    # Skip
    html._tokens = [
        (html.T_SKIP, 1, "", None, html.A_NONE),
        (html.T_EMPTY, 1, "", None, html.A_NONE),
    ]
    html.doConvert()
    assert html.theResult == "<p class='skip'>&nbsp;</p>\n"

    # Alignment
    # =========

    html.setLinkHeaders(False)

    # Align Left
    html.setStyles(False)
    html._tokens = [
        (html.T_HEAD1, 1, "A Title", None, html.A_LEFT),
    ]
    html.doConvert()
    assert html.theResult == (
        "<h1 class='title'>A Title</h1>\n"
    )

    html.setStyles(True)

    # Align Left
    html._tokens = [
        (html.T_HEAD1, 1, "A Title", None, html.A_LEFT),
    ]
    html.doConvert()
    assert html.theResult == (
        "<h1 class='title' style='text-align: left;'>A Title</h1>\n"
    )

    # Align Right
    html._tokens = [
        (html.T_HEAD1, 1, "A Title", None, html.A_RIGHT),
    ]
    html.doConvert()
    assert html.theResult == (
        "<h1 class='title' style='text-align: right;'>A Title</h1>\n"
    )

    # Align Centre
    html._tokens = [
        (html.T_HEAD1, 1, "A Title", None, html.A_CENTRE),
    ]
    html.doConvert()
    assert html.theResult == (
        "<h1 class='title' style='text-align: center;'>A Title</h1>\n"
    )

    # Align Justify
    html._tokens = [
        (html.T_HEAD1, 1, "A Title", None, html.A_JUSTIFY),
    ]
    html.doConvert()
    assert html.theResult == (
        "<h1 class='title' style='text-align: justify;'>A Title</h1>\n"
    )

    # Page Break
    # ==========

    # Page Break Always
    html._tokens = [
        (html.T_HEAD1, 1, "A Title", None, html.A_PBB | html.A_PBA),
    ]
    html.doConvert()
    assert html.theResult == (
        "<h1 class='title' "
        "style='page-break-before: always; page-break-after: always;'>A Title</h1>\n"
    )

    # Indent
    # ======

    # Indent Left
    html._tokens = [
        (html.T_TEXT,  1, "Some text ...", [], html.A_IND_L),
        (html.T_EMPTY, 2, "", None, html.A_NONE),
    ]
    html.doConvert()
    assert html.theResult == (
        "<p style='margin-left: 40px;'>Some text ...</p>\n"
    )

    # Indent Right
    html._tokens = [
        (html.T_TEXT,  1, "Some text ...", [], html.A_IND_R),
        (html.T_EMPTY, 2, "", None, html.A_NONE),
    ]
    html.doConvert()
    assert html.theResult == (
        "<p style='margin-right: 40px;'>Some text ...</p>\n"
    )

# END Test testCoreToHtml_ConvertDirect


@pytest.mark.core
def testCoreToHtml_SpecialCases(mockGUI):
    """Test some special cases that have caused errors in the past."""
    project = NWProject()
    html = ToHtml(project)
    html._isNovel = True

    # Greater/Lesser than symbols
    # ===========================

    html._text = "Text with > and < with some **bold text** in it.\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p>Text with &gt; and &lt; with some <strong>bold text</strong> in it.</p>\n"
    )

    html._text = "Text with some <**bold text**> in it.\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p>Text with some &lt;<strong>bold text</strong>&gt; in it.</p>\n"
    )

    html._text = "Let's > be > _difficult **shall** > we_?\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p>Let's &gt; be &gt; <em>difficult <strong>shall</strong> &gt; we</em>?</p>\n"
    )

    html._text = "Test > text _<**bold**>_ and more.\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p>Test &gt; text <em>&lt;<strong>bold</strong>&gt;</em> and more.</p>\n"
    )

    # Test for issue #950
    # ===================
    # See: https://github.com/vkbo/novelWriter/issues/950

    html.setComments(True)
    html._text = "% Test > text _<**bold**>_ and more.\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p class='comment'>"
        "<strong>Comment:</strong> Test &gt; text _&lt;**bold**&gt;_ and more."
        "</p>\n"
    )

    html._text = "## Heading <1>\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<h1 style='page-break-before: always;'>Heading &lt;1&gt;</h1>\n"
    )

    # Test for issue #1412
    # ====================
    # See: https://github.com/vkbo/novelWriter/issues/1412

    html._text = "Test text \\**_bold_** and more.\n"
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p>Test text **<em>bold</em>** and more.</p>\n"
    )

# END Test testCoreToHtml_SpecialCases


@pytest.mark.core
def testCoreToHtml_Complex(mockGUI, fncPath):
    """Test the save method of the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)
    html._isNovel = True

    # Build Project
    # =============

    docText = [
        "# My Novel\n**By Jane Doh**\n",
        "## Chapter 1\n\nThe text of chapter one.\n",
        "### Scene 1\n\nThe text of scene one.\n",
        "#### A Section\n\nMore text in scene one.\n",
        "## Chapter 2\n\nThe text of chapter two.\n",
        "### Scene 2\n\nThe text of scene two.\n",
        "#### A Section\n\n\tMore text in scene two.\n",
    ]
    resText = [
        (
            "<h1 class='title' style='text-align: center;'>My Novel</h1>\n"
            "<p><strong>By Jane Doh</strong></p>\n"
        ),
        (
            "<h1 style='page-break-before: always;'>Chapter 1</h1>\n"
            "<p>The text of chapter one.</p>\n"
        ),
        (
            "<h2>Scene 1</h2>\n"
            "<p>The text of scene one.</p>\n"
        ),
        (
            "<h3>A Section</h3>\n"
            "<p>More text in scene one.</p>\n"
        ),
        (
            "<h1 style='page-break-before: always;'>Chapter 2</h1>\n"
            "<p>The text of chapter two.</p>\n"
        ),
        (
            "<h2>Scene 2</h2>\n"
            "<p>The text of scene two.</p>\n"
        ),
        (
            "<h3>A Section</h3>\n"
            "<p>\tMore text in scene two.</p>\n"
        ),
    ]

    for i in range(len(docText)):
        html._text = docText[i]
        html.doPreProcessing()
        html.tokenizeText()
        html.doConvert()
        assert html.theResult == resText[i]

    assert html.fullHTML == resText

    html.replaceTabs(nSpaces=2, spaceChar="&nbsp;")
    resText[6] = "<h3>A Section</h3>\n<p>&nbsp;&nbsp;More text in scene two.</p>\n"

    # Check File
    # ==========

    theStyle = html.getStyleSheet()
    htmlDoc = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        "<meta charset='utf-8'>\n"
        "<title></title>\n"
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
        htmlStyle="\n".join(theStyle),
        bodyText="".join(resText).rstrip()
    )

    saveFile = fncPath / "outFile.htm"
    html.saveHtml5(saveFile)
    assert readFile(saveFile) == htmlDoc

# END Test testCoreToHtml_Complex


@pytest.mark.core
def testCoreToHtml_Methods(mockGUI):
    """Test all the other methods of the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)
    html.setKeepMarkdown(True)

    # Auto-Replace, keep Unicode
    docText = "Text with <brackets> & short–dash, long—dash …\n"
    html._text = docText
    html.setReplaceUnicode(False)
    html.doPreProcessing()
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p>Text with &lt;brackets&gt; &amp; short–dash, long—dash …</p>\n"
    )

    # Auto-Replace, replace Unicode
    docText = "Text with <brackets> & short–dash, long—dash …\n"
    html._text = docText
    html.setReplaceUnicode(True)
    html.doPreProcessing()
    html.tokenizeText()
    html.doConvert()
    assert html.theResult == (
        "<p>Text with &lt;brackets&gt; &amp; short&ndash;dash, long&mdash;dash &hellip;</p>\n"
    )

    # With Preview
    html.setPreview(True, True)
    html._text = docText
    html.doPreProcessing()
    html.tokenizeText()
    html.doConvert()
    assert html.theMarkdown[-1] == (
        "Text with <brackets> &amp; short&ndash;dash, long&mdash;dash &hellip;\n\n"
    )

    # Result Size
    assert html.getFullResultSize() == 147

    # CSS
    # ===

    assert len(html.getStyleSheet()) > 1
    assert "p {text-align: left;" in " ".join(html.getStyleSheet())
    assert "p {text-align: justify;" not in " ".join(html.getStyleSheet())

    html.setJustify(True)
    assert "p {text-align: left;" not in " ".join(html.getStyleSheet())
    assert "p {text-align: justify;" in " ".join(html.getStyleSheet())

    html.setStyles(False)
    assert html.getStyleSheet() == []

# END Test testCoreToHtml_Methods


@pytest.mark.core
def testCoreToHtml_Format(mockGUI):
    """Test all the formatters for the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)

    # Export Mode
    # ===========

    assert html._formatSynopsis("synopsis text", True) == (
        "<p class='synopsis'><strong>Synopsis:</strong> synopsis text</p>\n"
    )
    assert html._formatSynopsis("brief text", False) == (
        "<p class='synopsis'><strong>Brief:</strong> brief text</p>\n"
    )
    assert html._formatComments("comment text") == (
        "<p class='comment'><strong>Comment:</strong> comment text</p>\n"
    )

    assert html._formatKeywords("") == ""
    assert html._formatKeywords("tag: Jane") == (
        "<span class='tags'>Tag:</span> <a name='tag_Jane'>Jane</a>"
    )
    assert html._formatKeywords("char: Bod, Jane") == (
        "<span class='tags'>Characters:</span> "
        "<a href='#tag_Bod'>Bod</a>, "
        "<a href='#tag_Jane'>Jane</a>"
    )

    # Preview Mode
    # ============

    html.setPreview(True, True)

    assert html._formatSynopsis("synopsis text", True) == (
        "<p class='comment'><span class='synopsis'>Synopsis:</span> synopsis text</p>\n"
    )
    assert html._formatSynopsis("brief text", False) == (
        "<p class='comment'><span class='synopsis'>Brief:</span> brief text</p>\n"
    )
    assert html._formatComments("comment text") == (
        "<p class='comment'>comment text</p>\n"
    )

    assert html._formatKeywords("") == ""
    assert html._formatKeywords("tag: Jane") == (
        "<span class='tags'>Tag:</span> <a name='tag_Jane'>Jane</a>"
    )
    assert html._formatKeywords("char: Bod, Jane") == (
        "<span class='tags'>Characters:</span> "
        "<a href='#char=Bod'>Bod</a>, "
        "<a href='#char=Jane'>Jane</a>"
    )

# END Test testCoreToHtml_Format
