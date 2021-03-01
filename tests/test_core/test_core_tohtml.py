# -*- coding: utf-8 -*-
"""
novelWriter – ToHtml Class Tester
=================================

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

from nw.core import NWProject, NWIndex, ToHtml

@pytest.mark.core
def testCoreToHtml_Format(dummyGUI):
    """Test all the formatters for the ToHtml class.
    """
    theProject = NWProject(dummyGUI)
    dummyGUI.theIndex = NWIndex(theProject, dummyGUI)
    theHtml = ToHtml(theProject, dummyGUI)

    # Export Mode
    # ===========

    assert theHtml._formatSynopsis("synopsis text") == (
        "<p class='synopsis'><strong>Synopsis:</strong> synopsis text</p>\n"
    )
    assert theHtml._formatComments("comment text") == (
        "<p class='comment'><strong>Comment:</strong> comment text</p>\n"
    )

    assert theHtml._formatKeywords("") == ""
    assert theHtml._formatKeywords("tag: Jane") == (
        "<div><span class='tags'>Tag:</span> <a name='tag_Jane'>Jane</a></div>\n"
    )
    assert theHtml._formatKeywords("char: Bod, Jane") == (
        "<div>"
        "<span class='tags'>Characters:</span> "
        "<a href='#tag_Bod'>Bod</a>, "
        "<a href='#tag_Jane'>Jane</a>"
        "</div>\n"
    )

    # Preview Mode
    # ============

    theHtml.setPreview(True, True)

    assert theHtml._formatSynopsis("synopsis text") == (
        "<p class='comment'><span class='synopsis'>Synopsis:</span> synopsis text</p>\n"
    )
    assert theHtml._formatComments("comment text") == (
        "<p class='comment'>comment text</p>\n"
    )

    assert theHtml._formatKeywords("") == ""
    assert theHtml._formatKeywords("tag: Jane") == (
        "<div><span class='tags'>Tag:</span> <a name='tag_Jane'>Jane</a></div>\n"
    )
    assert theHtml._formatKeywords("char: Bod, Jane") == (
        "<div>"
        "<span class='tags'>Characters:</span> "
        "<a href='#char=Bod'>Bod</a>, "
        "<a href='#char=Jane'>Jane</a>"
        "</div>\n"
    )

# END Test testCoreToHtml_Format

@pytest.mark.core
def testCoreToHtml_Convert(dummyGUI):
    """Test the converter of the ToHtml class.
    """
    theProject = NWProject(dummyGUI)
    dummyGUI.theIndex = NWIndex(theProject, dummyGUI)
    theHtml = ToHtml(theProject, dummyGUI)

    # Export Mode
    # ===========

    theHtml.isNovel = True

    # Header 1
    theHtml.theText = "# Title\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == "<h1 class='title'>Title</h1>\n"

    # Header 2
    theHtml.theText = "## Chapter Title\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == "<h1>Chapter Title</h1>\n"

    # Header 3
    theHtml.theText = "### Scene Title\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == "<h2>Scene Title</h2>\n"

    # Header 4
    theHtml.theText = "#### Section Title\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == "<h3>Section Title</h3>\n"

    theHtml.isNovel = False
    theHtml.setLinkHeaders(True)

    # Header 1
    theHtml.theText = "# Heading One\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == "<h1><a name='T000001'></a>Heading One</h1>\n"

    # Header 2
    theHtml.theText = "## Heading Two\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == "<h2><a name='T000001'></a>Heading Two</h2>\n"

    # Header 3
    theHtml.theText = "### Heading Three\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == "<h3><a name='T000001'></a>Heading Three</h3>\n"

    # Header 4
    theHtml.theText = "#### Heading Four\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == "<h4><a name='T000001'></a>Heading Four</h4>\n"

    # Text
    theHtml.theText = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<p>Some <strong>nested bold and <em>italic</em> and "
        "<del>strikethrough</del> text</strong> here</p>\n"
    )

    # Text w/Hard Break
    theHtml.theText = "Line one  \nLine two  \nLine three\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<p class='break'>Line one<br/>Line two<br/>Line three</p>\n"
    )

    # Synopsis
    theHtml.theText = "%synopsis: The synopsis ...\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == ""

    theHtml.setSynopsis(True)
    theHtml.theText = "%synopsis: The synopsis ...\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<p class='synopsis'><strong>Synopsis:</strong> The synopsis ...</p>\n"
    )

    # Comment
    theHtml.theText = "% A comment ...\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == ""

    theHtml.setComments(True)
    theHtml.theText = "% A comment ...\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<p class='comment'><strong>Comment:</strong> A comment ...</p>\n"
    )

    # Keywords
    theHtml.theText = "@char: Bod, Jane\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == ""

    theHtml.setKeywords(True)
    theHtml.theText = "@char: Bod, Jane\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<div><span class='tags'>Characters:</span> "
        "<a href='#tag_Bod'>Bod</a>, <a href='#tag_Jane'>Jane</a></div>\n"
    )

    # Direct Tests
    # ============

    theHtml.isNovel = True

    # Title
    theHtml.theTokens = [
        (theHtml.T_TITLE, 1, "A Title", None, theHtml.A_PBB_NO | theHtml.A_CENTRE),
        (theHtml.T_EMPTY, 1, "", None, theHtml.A_NONE),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title' style='text-align: center; page-break-before: never;'>"
        "<a name='T000001'></a>A Title</h1>\n"
    )

    # Separator
    theHtml.theTokens = [
        (theHtml.T_SEP, 1, "* * *", None, theHtml.A_CENTRE),
        (theHtml.T_EMPTY, 1, "", None, theHtml.A_NONE),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == "<p class='sep'>* * *</p>\n"

    # Skip
    theHtml.theTokens = [
        (theHtml.T_SKIP, 1, "", None, theHtml.A_NONE),
        (theHtml.T_EMPTY, 1, "", None, theHtml.A_NONE),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == "<p class='skip'>&nbsp;</p>\n"

    # Styles
    # ======

    theHtml.setLinkHeaders(False)

    # Align Left
    theHtml.setStyles(False)
    theHtml.theTokens = [
        (theHtml.T_HEAD1, 1, "A Title", None, theHtml.A_LEFT),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title'>A Title</h1>\n"
    )

    theHtml.setStyles(True)

    # Align Left
    theHtml.theTokens = [
        (theHtml.T_HEAD1, 1, "A Title", None, theHtml.A_LEFT),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title' style='text-align: left;'>A Title</h1>\n"
    )

    # Align Right
    theHtml.theTokens = [
        (theHtml.T_HEAD1, 1, "A Title", None, theHtml.A_RIGHT),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title' style='text-align: right;'>A Title</h1>\n"
    )

    # Align Centre
    theHtml.theTokens = [
        (theHtml.T_HEAD1, 1, "A Title", None, theHtml.A_CENTRE),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title' style='text-align: center;'>A Title</h1>\n"
    )

    # Align Justify
    theHtml.theTokens = [
        (theHtml.T_HEAD1, 1, "A Title", None, theHtml.A_JUSTIFY),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title' style='text-align: justify;'>A Title</h1>\n"
    )

    # Page Break Always
    theHtml.theTokens = [
        (theHtml.T_HEAD1, 1, "A Title", None, theHtml.A_PBB | theHtml.A_PBA),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title' "
        "style='page-break-before: always; page-break-after: always;'>A Title</h1>\n"
    )

    # Page Break Avoid
    theHtml.theTokens = [
        (theHtml.T_HEAD1, 1, "A Title", None, theHtml.A_PBB_AV | theHtml.A_PBA_AV),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title' "
        "style='page-break-before: avoid; page-break-after: avoid;'>A Title</h1>\n"
    )

    # Page Break ANever
    theHtml.theTokens = [
        (theHtml.T_HEAD1, 1, "A Title", None, theHtml.A_PBB_NO | theHtml.A_PBA_NO),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title' "
        "style='page-break-before: never; page-break-after: never;'>A Title</h1>\n"
    )

    # Preview Mode
    # ============

    theHtml.setPreview(True, True)

    # Text (HTML4)
    theHtml.theText = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<p>Some <b>nested bold and <i>italic</i> and "
        "<span style='text-decoration: line-through;'>strikethrough</span> "
        "text</b> here</p>\n"
    )

# END Test testCoreToHtml_Convert

@pytest.mark.core
def testCoreToHtml_Methods(dummyGUI):
    """Test all the other methods of the ToHtml class.
    """
    theProject = NWProject(dummyGUI)
    theHtml = ToHtml(theProject, dummyGUI)

    # Auto-Replace
    docText = "Text with <brackets> & short–dash, long—dash …\n"
    theHtml.theText = docText
    theHtml.doAutoReplace()
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<p>Text with &lt;brackets&gt; &amp; short&ndash;dash, long&mdash;dash &hellip;</p>\n"
    )

    # Revert on MD
    assert theHtml.theMarkdown == (
        "Text with &lt;brackets&gt; &amp; short&ndash;dash, long&mdash;dash &hellip;\n\n"
    )
    theHtml.doPostProcessing()
    assert theHtml.theMarkdown == docText + "\n"

    # With Preview, No Revert
    theHtml.setPreview(True, True)
    theHtml.theText = docText
    theHtml.doAutoReplace()
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theMarkdown == (
        "Text with &lt;brackets&gt; &amp; short&ndash;dash, long&mdash;dash &hellip;\n\n"
    )
    theHtml.doPostProcessing()
    assert theHtml.theMarkdown == (
        "Text with &lt;brackets&gt; &amp; short&ndash;dash, long&mdash;dash &hellip;\n\n"
    )

    # CSS
    # ===

    assert len(theHtml.getStyleSheet()) > 1
    assert "p {text-align: left;}" in theHtml.getStyleSheet()
    assert "p {text-align: justify;}" not in theHtml.getStyleSheet()

    theHtml.setJustify(True)
    assert "p {text-align: left;}" not in theHtml.getStyleSheet()
    assert "p {text-align: justify;}" in theHtml.getStyleSheet()

    theHtml.setStyles(False)
    assert theHtml.getStyleSheet() == []

# END Test testCoreToHtml_Methods
