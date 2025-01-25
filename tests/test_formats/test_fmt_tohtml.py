"""
novelWriter – ToHtml Class Tester
=================================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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

from novelwriter import CONFIG
from novelwriter.constants import nwHeadFmt
from novelwriter.core.project import NWProject
from novelwriter.formats.shared import BlockFmt, BlockTyp
from novelwriter.formats.tohtml import ToHtml


@pytest.mark.core
def testFmtToHtml_ConvertHeaders(mockGUI):
    """Test header formats in the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)
    html.initDocument()

    # Novel Files Headers
    # ===================

    html._isNovel = True
    html._isFirst = True

    # Header 1
    html._text = "# Title\n"
    html.setPartitionFormat(f"Part{nwHeadFmt.BR}{nwHeadFmt.TITLE}")
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 class='title' style='text-align: center;'>Part<br>Title</h1>\n"
    )

    # Header 2
    html._text = "## Title\n"
    html.setChapterFormat(f"Chapter {nwHeadFmt.CH_NUM}{nwHeadFmt.BR}{nwHeadFmt.TITLE}")
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 style='page-break-before: always;'>Chapter 1<br>Title</h1>\n"
    )

    # Header 3
    html._text = "### Title\n"
    html.setSceneFormat(f"Scene {nwHeadFmt.SC_ABS}{nwHeadFmt.BR}{nwHeadFmt.TITLE}")
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == "<h2>Scene 1<br>Title</h2>\n"

    # Header 4
    html._text = "#### Title\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == "<h3>Title</h3>\n"

    # Title
    html._text = "#! Title\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 class='title' style='text-align: center; page-break-before: always;'>Title</h1>\n"
    )

    # Unnumbered
    html._text = "##! Prologue\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == "<h1 style='page-break-before: always;'>Prologue</h1>\n"

    # Note Files Headers
    # ==================

    html._isNovel = False
    html._isFirst = True
    html._handle = "0000000000000"
    html.setLinkHeadings(True)

    # Header 1
    html._text = "# Heading One\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == "<h1><a name='0000000000000:T0001'></a>Heading One</h1>\n"

    # Header 2
    html._text = "## Heading Two\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == "<h2><a name='0000000000000:T0001'></a>Heading Two</h2>\n"

    # Header 3
    html._text = "### Heading Three\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == "<h3><a name='0000000000000:T0001'></a>Heading Three</h3>\n"

    # Header 4
    html._text = "#### Heading Four\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == "<h4><a name='0000000000000:T0001'></a>Heading Four</h4>\n"

    # Title
    html._text = "#! Heading One\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 class='title' style='text-align: center; page-break-before: always;'>"
        "<a name='0000000000000:T0001'></a>Heading One</h1>\n"
    )

    # Unnumbered
    html._text = "##! Heading Two\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == "<h2><a name='0000000000000:T0001'></a>Heading Two</h2>\n"


@pytest.mark.core
def testFmtToHtml_ConvertParagraphs(mockGUI):
    """Test paragraph formats in the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)
    html.initDocument()
    html._isNovel = True
    html._isFirst = True

    # Paragraphs
    # ==========

    # Text
    html._text = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Some <strong>nested bold and <em>italic</em> and "
        "<del>strikethrough</del> text</strong> here</p>\n"
    )

    # Shortcodes
    html._text = (
        "Some [b]bold[/b], [i]italic[/i], [s]strike[/s], [u]underline[/u], [m]mark[/m], "
        "super[sup]script[/sup], sub[sub]script[/sub] here\n"
    )
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Some <strong>bold</strong>, <em>italic</em>, <del>strike</del>, "
        "<span style='text-decoration: underline;'>underline</span>, <mark>mark</mark>, "
        "super<sup>script</sup>, sub<sub>script</sub> here</p>\n"
    )

    # Text w/Hard Break
    html._text = "Line one\nLine two\nLine three\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Line one<br>Line two<br>Line three</p>\n"
    )

    # Synopsis, Short
    html._text = "%synopsis: The synopsis ...\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == ""

    html.setSynopsis(True)
    html._text = "%synopsis: The synopsis ...\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p class='comment'>"
        "<strong><span style='color: #813709'>Synopsis:</span></strong> "
        "<span style='color: #813709'>The synopsis ...</span>"
        "</p>\n"
    )

    html.setSynopsis(True)
    html._text = "%short: A short description ...\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p class='comment'>"
        "<strong><span style='color: #813709'>Short Description:</span></strong> "
        "<span style='color: #813709'>A short description ...</span>"
        "</p>\n"
    )

    # Comment
    html._text = "% A comment ...\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == ""

    html.setComments(True)
    html._text = "% A comment ...\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p class='comment'>"
        "<strong><span style='color: #646464'>Comment:</span></strong> "
        "<span style='color: #646464'>A comment ...</span>"
        "</p>\n"
    )

    # Keywords
    html._text = "@char: Bod, Jane\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == ""

    html.setKeywords(True)
    html._text = "@char: Bod, Jane\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p class='meta meta-char'><strong><span style='color: #f5871f'>"
        "Characters:</span></strong> "
        "<span style='color: #4271ae'><a href='#tag_bod'>Bod</a></span>, "
        "<span style='color: #4271ae'><a href='#tag_jane'>Jane</a></span></p>\n"
    )

    # Tags
    html._text = "@tag: Bod\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p class='meta meta-tag'><strong><span style='color: #f5871f'>Tag:</span></strong> "
        "<span style='color: #4271ae'><a name='tag_bod'>Bod</a></span></p>\n"
    )

    html._text = "@tag: Bod | Nobody Owens\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p class='meta meta-tag'><strong><span style='color: #f5871f'>Tag:</span></strong> "
        "<span style='color: #4271ae'><a name='tag_bod'>Bod</a></span> | "
        "<span style='color: #4271ae'>Nobody Owens</span></p>\n"
    )

    # Multiple Keywords
    html._isFirst = False
    html.setKeywords(True)
    html._text = "## Chapter\n\n@pov: Bod\n@plot: Main\n@location: Europe\n\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 style='page-break-before: always;'>Chapter</h1>\n"
        "<p class='meta meta-pov' style='margin-bottom: 0;'>"
        "<strong><span style='color: #f5871f'>Point of View:</span></strong> "
        "<span style='color: #4271ae'><a href='#tag_bod'>Bod</a></span></p>\n"
        "<p class='meta meta-plot' style='margin-bottom: 0; margin-top: 0;'>"
        "<strong><span style='color: #f5871f'>Plot:</span></strong> "
        "<span style='color: #4271ae'><a href='#tag_main'>Main</a></span></p>\n"
        "<p class='meta meta-location' style='margin-top: 0;'>"
        "<strong><span style='color: #f5871f'>Locations:</span></strong> "
        "<span style='color: #4271ae'><a href='#tag_europe'>Europe</a></span></p>\n"
    )


@pytest.mark.core
def testFmtToHtml_Dialog(mockGUI):
    """Test paragraph formats in the ToHtml class."""
    CONFIG.altDialogOpen = "::"
    CONFIG.altDialogClose = "::"

    project = NWProject()
    html = ToHtml(project)
    html.initDocument()
    html.setDialogHighlight(True)
    html._isNovel = True
    html._isFirst = True

    # Dialog
    html.setDialogHighlight(True)
    html._text = "## Chapter\n\nThis text \u201chas dialogue\u201d in it.\n\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<h1>Chapter</h1>\n"
        "<p>This text <span style='color: #4271ae'>“has dialogue”</span> in it.</p>\n"
    )

    # Alt Dialog
    html._text = "## Chapter\n\nThis text ::has alt dialogue:: in it.\n\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 style='page-break-before: always;'>Chapter</h1>\n"
        "<p>This text <span style='color: #813709'>::has alt dialogue::</span> in it.</p>\n"
    )


@pytest.mark.core
def testFmtToHtml_Footnotes(mockGUI):
    """Test paragraph formats in the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)
    html.initDocument()
    html._isNovel = True
    html._isFirst = True

    html._text = (
        "Text with one[footnote:fa] or two[footnote:fb] footnotes.\n\n"
        "%footnote.fa: Footnote text A.\n\n"
    )
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Text with one<sup><a href='#footnote_1'>1</a></sup> "
        "or two<sup>ERR</sup> footnotes.</p>\n"
    )

    html.closeDocument()
    assert html._pages[-2] == (
        "<p>Text with one<sup><a href='#footnote_1'>1</a></sup> "
        "or two<sup>ERR</sup> footnotes.</p>\n"
    )
    assert html._pages[-1] == (
        "<h3>Footnotes</h3>\n"
        "<ol>\n"
        "<li id='footnote_1'><p>Footnote text A.</p></li>\n"
        "</ol>\n"
    )


@pytest.mark.core
def testFmtToHtml_CloseTags(mockGUI):
    """Test automatic closing of HTML tags for shortcodes."""
    project = NWProject()
    html = ToHtml(project)
    html.initDocument()

    html._isNovel = True
    html._isFirst = True

    # Unclosed Shortcodes
    html._text = "Text [b][i][s][u][m][sup][sub]text text text.\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Text <strong><em><del><span style='text-decoration: underline;'><mark><sup><sub>"
        "text text text.</strong></em></del></span></mark></sup></sub></p>\n"
    )

    # Double Shortcodes
    html._text = "Text [b][i][s][u][m][sup][sub]text [b][i][s][u][m][sup][sub]text text.\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Text <strong><em><del><span style='text-decoration: underline;'><mark><sup><sub>"
        "text text text.</strong></em></del></span></mark></sup></sub></p>\n"
    )

    # Redundant Close Shortcodes
    html._text = "Text text [/b][/i][/s][/u][/m][/sup][/sub]text text.\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Text text text text.</p>\n"
    )


@pytest.mark.core
def testFmtToHtml_ConvertDirect(mockGUI):
    """Test the converter directly using the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)
    html.initDocument()

    html._isNovel = True
    html._handle = "0000000000000"
    html.setLinkHeadings(True)

    tMeta = "0000000000000:T0001"

    # Special Titles
    # ==============

    # Title
    html._blocks = [
        (BlockTyp.TITLE, tMeta, "A Title", [], BlockFmt.PBB | BlockFmt.CENTRE),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 class='title' style='text-align: center; page-break-before: always;'>"
        "<a name='0000000000000:T0001'></a>A Title</h1>\n"
    )

    # Unnumbered
    html._blocks = [
        (BlockTyp.HEAD1, tMeta, "Prologue", [], BlockFmt.PBB),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 style='page-break-before: always;'>"
        "<a name='0000000000000:T0001'></a>Prologue</h1>\n"
    )

    # Separators
    # ==========

    # Separator
    html._blocks = [
        (BlockTyp.SEP, tMeta, "* * *", [], BlockFmt.CENTRE),
    ]
    html.doConvert()
    assert html._pages[-1] == "<p class='sep' style='text-align: center;'>* * *</p>\n"

    # Skip
    html._blocks = [
        (BlockTyp.SKIP, tMeta, "", [], BlockFmt.NONE),
    ]
    html.doConvert()
    assert html._pages[-1] == "<p>&nbsp;</p>\n"

    # Alignment
    # =========

    html.setLinkHeadings(False)

    # Align Left
    html.setStyles(False)
    html._blocks = [
        (BlockTyp.PART, tMeta, "A Title", [], BlockFmt.LEFT),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 class='title'>A Title</h1>\n"
    )

    html.setStyles(True)

    # Align Left
    html._blocks = [
        (BlockTyp.PART, tMeta, "A Title", [], BlockFmt.LEFT),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 class='title' style='text-align: left;'>A Title</h1>\n"
    )

    # Align Right
    html._blocks = [
        (BlockTyp.PART, tMeta, "A Title", [], BlockFmt.RIGHT),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 class='title' style='text-align: right;'>A Title</h1>\n"
    )

    # Align Centre
    html._blocks = [
        (BlockTyp.PART, tMeta, "A Title", [], BlockFmt.CENTRE),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 class='title' style='text-align: center;'>A Title</h1>\n"
    )

    # Align Justify
    html._blocks = [
        (BlockTyp.PART, tMeta, "A Title", [], BlockFmt.JUSTIFY),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 class='title' style='text-align: justify;'>A Title</h1>\n"
    )

    # Page Break
    # ==========

    # Page Break Always
    html._blocks = [
        (BlockTyp.PART, tMeta, "A Title", [], BlockFmt.PBB | BlockFmt.PBA),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 class='title' "
        "style='page-break-before: always; page-break-after: always;'>A Title</h1>\n"
    )

    # Indent
    # ======

    # Indent Left
    html._blocks = [
        (BlockTyp.TEXT, tMeta, "Some text ...", [], BlockFmt.IND_L),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<p style='margin-left: 4.00em;'>Some text ...</p>\n"
    )

    # Indent Right
    html._blocks = [
        (BlockTyp.TEXT, tMeta, "Some text ...", [], BlockFmt.IND_R),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<p style='margin-right: 4.00em;'>Some text ...</p>\n"
    )

    # Text Indent
    html._blocks = [
        (BlockTyp.TEXT, tMeta, "Some text ...", [], BlockFmt.IND_T),
    ]
    html.doConvert()
    assert html._pages[-1] == (
        "<p style='text-indent: 1.40em;'>Some text ...</p>\n"
    )


@pytest.mark.core
def testFmtToHtml_SpecialCases(mockGUI):
    """Test some special cases that have caused errors in the past."""
    project = NWProject()
    html = ToHtml(project)
    html.initDocument()
    html._isNovel = True

    # Greater/Lesser than symbols
    # ===========================

    html._text = "Text with > and < with some **bold text** in it.\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Text with &gt; and &lt; with some <strong>bold text</strong> in it.</p>\n"
    )

    html._text = "Text with some <**bold text**> in it.\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Text with some &lt;<strong>bold text</strong>&gt; in it.</p>\n"
    )

    html._text = "Let's > be > _difficult **shall** > we_?\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Let's &gt; be &gt; <em>difficult <strong>shall</strong> &gt; we</em>?</p>\n"
    )

    html._text = "Test > text _<**bold**>_ and more.\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Test &gt; text <em>&lt;<strong>bold</strong>&gt;</em> and more.</p>\n"
    )

    # Test for issue #950
    # ===================
    # See: https://github.com/vkbo/novelWriter/issues/950

    html.setComments(True)
    html._text = "% Test > text _<**bold**>_ and more.\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p class='comment'>"
        "<strong><span style='color: #646464'>Comment:</span></strong> "
        "<span style='color: #646464'>Test &gt; text <em>&lt;<strong>bold</strong>&gt;</em> "
        "and more.</span>"
        "</p>\n"
    )

    html._isFirst = False
    html._text = "## Heading <1>\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<h1 style='page-break-before: always;'>Heading &lt;1&gt;</h1>\n"
    )

    # Test for issue #1412
    # ====================
    # See: https://github.com/vkbo/novelWriter/issues/1412

    html._text = "Test text \\**_bold_** and more.\n"
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Test text **<em>bold</em>** and more.</p>\n"
    )


@pytest.mark.core
def testFmtToHtml_Save(mockGUI, fncPath):
    """Test the save method of the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)
    html.initDocument()
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
    resText = [(
        "<h1 class='title' style='text-align: center;'>My Novel</h1>\n"
        "<p><strong>By Jane Doh</strong></p>\n"
    ), (
        "<h1 style='page-break-before: always;'>Chapter 1</h1>\n"
        "<p>The text of chapter one.</p>\n"
    ), (
        "<h2>Scene 1</h2>\n"
        "<p>The text of scene one.</p>\n"
    ), (
        "<h3>A Section</h3>\n"
        "<p>More text in scene one.</p>\n"
    ), (
        "<h1 style='page-break-before: always;'>Chapter 2</h1>\n"
        "<p>The text of chapter two.</p>\n"
    ),  (
        "<h2>Scene 2</h2>\n"
        "<p>The text of scene two.</p>\n"
    ),  (
        "<h3>A Section</h3>\n"
        "<p>\tMore text in scene two.</p>\n"
    )]

    for i in range(len(docText)):
        html._text = docText[i]
        html.doPreProcessing()
        html.tokenizeText()
        html.doConvert()

    assert html._pages == resText

    html.replaceTabs(nSpaces=2, spaceChar="&nbsp;")
    resText[6] = "<h3>A Section</h3>\n<p>&nbsp;&nbsp;More text in scene two.</p>\n"

    # Check Files
    # ===========

    # HTML
    hStyle = html.getStyleSheet()
    htmlDoc = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        "<meta charset='utf-8'>\n"
        "<title></title>\n"
        "<style>\n"
        "{htmlStyle:s}\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        "{bodyText:s}\n"
        "</body>\n"
        "</html>\n"
    ).format(
        htmlStyle="\n".join(hStyle),
        bodyText="".join(resText).rstrip()
    )

    saveFile = fncPath / "outFile.htm"
    html.saveDocument(saveFile)
    assert saveFile.read_text(encoding="utf-8") == htmlDoc

    # JSON + HTML
    saveFile = fncPath / "outFile.json"
    html.saveDocument(saveFile)
    data = json.loads(saveFile.read_text(encoding="utf-8"))
    assert data["meta"]["projectName"] == ""
    assert data["meta"]["novelAuthor"] == ""
    assert data["meta"]["buildTime"] > 0
    assert data["meta"]["buildTimeStr"] != ""
    assert data["text"]["css"] == hStyle
    assert len(data["text"]["html"]) == len(resText)


@pytest.mark.core
def testFmtToHtml_Methods(mockGUI):
    """Test all the other methods of the ToHtml class."""
    project = NWProject()
    html = ToHtml(project)
    html.initDocument()

    # Auto-Replace, keep Unicode
    docText = "Text with <brackets> & short–dash, long—dash …\n"
    html._text = docText
    html.setReplaceUnicode(False)
    html.doPreProcessing()
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Text with &lt;brackets&gt; &amp; short–dash, long—dash …</p>\n"
    )

    # Auto-Replace, replace Unicode
    docText = "Text with <brackets> & short–dash, long—dash …\n"
    html._text = docText
    html.setReplaceUnicode(True)
    html.doPreProcessing()
    html.tokenizeText()
    html.doConvert()
    assert html._pages[-1] == (
        "<p>Text with &lt;brackets&gt; &amp; short&ndash;dash, long&mdash;dash &hellip;</p>\n"
    )

    # Result Size
    assert html.getFullResultSize() == 147

    # CSS
    # ===

    assert len(html.getStyleSheet()) > 1
    assert "p {text-align: left;" in " ".join(html.getStyleSheet())
    assert "p {text-align: justify;" not in " ".join(html.getStyleSheet())

    html.setStyles(False)
    assert html.getStyleSheet() == []
