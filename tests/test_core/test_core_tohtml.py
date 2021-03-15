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

import os
import pytest

from tools import readFile

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
        "<span class='tags'>Tag:</span> <a name='tag_Jane'>Jane</a>"
    )
    assert theHtml._formatKeywords("char: Bod, Jane") == (
        "<span class='tags'>Characters:</span> "
        "<a href='#tag_Bod'>Bod</a>, "
        "<a href='#tag_Jane'>Jane</a>"
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
        "<span class='tags'>Tag:</span> <a name='tag_Jane'>Jane</a>"
    )
    assert theHtml._formatKeywords("char: Bod, Jane") == (
        "<span class='tags'>Characters:</span> "
        "<a href='#char=Bod'>Bod</a>, "
        "<a href='#char=Jane'>Jane</a>"
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
        "<p><span class='tags'>Characters:</span> "
        "<a href='#tag_Bod'>Bod</a>, <a href='#tag_Jane'>Jane</a></p>\n"
    )

    # Multiple Keywords
    theHtml.setKeywords(True)
    theHtml.theText = "## Chapter\n\n@pov: Bod\n@plot: Main\n@location: Europe\n\n"
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h2>"
        "<a name='T000001'></a>Chapter</h2>\n"
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

    # Direct Tests
    # ============

    theHtml.isNovel = True

    # Title
    theHtml.theTokens = [
        (theHtml.T_TITLE, 1, "A Title", None, theHtml.A_PBB_AUT | theHtml.A_CENTRE),
        (theHtml.T_EMPTY, 1, "", None, theHtml.A_NONE),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title' style='text-align: center; page-break-before: auto;'>"
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

    # Page Break Auto
    theHtml.theTokens = [
        (theHtml.T_HEAD1, 1, "A Title", None, theHtml.A_PBB_AUT | theHtml.A_PBA_AUT),
    ]
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<h1 class='title' "
        "style='page-break-before: auto; page-break-after: auto;'>A Title</h1>\n"
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

def testCoreToHtml_Complex(dummyGUI, fncDir):
    """Test the ave method of the ToHtml class.
    """
    theProject = NWProject(dummyGUI)
    theHtml = ToHtml(theProject, dummyGUI)

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
        "<h1>My Novel</h1>\n<p><strong>By Jane Doh</strong></p>\n",
        "<h2>Chapter 1</h2>\n<p>The text of chapter one.</p>\n",
        "<h3>Scene 1</h3>\n<p>The text of scene one.</p>\n",
        "<h4>A Section</h4>\n<p>More text in scene one.</p>\n",
        "<h2>Chapter 2</h2>\n<p>The text of chapter two.</p>\n",
        "<h3>Scene 2</h3>\n<p>The text of scene two.</p>\n",
        "<h4>A Section</h4>\n<p>\tMore text in scene two.</p>\n",
    ]

    for i in range(len(docText)):
        theHtml.theText = docText[i]
        theHtml.doPreProcessing()
        theHtml.tokenizeText()
        theHtml.doConvert()
        assert theHtml.theResult == resText[i]

    assert theHtml.fullHTML == resText

    theHtml.replaceTabs(nSpaces=2, spaceChar="&nbsp;")
    resText[6] = "<h4>A Section</h4>\n<p>&nbsp;&nbsp;More text in scene two.</p>\n"

    # Check File
    # ==========

    theStyle = theHtml.getStyleSheet()
    theStyle.append("article {width: 800px; margin: 40px auto;}")
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
        htmlStyle = "\n".join(theStyle),
        bodyText = "".join(resText).rstrip()
    )

    saveFile = os.path.join(fncDir, "outFile.htm")
    theHtml.saveHTML5(saveFile)
    assert readFile(saveFile) == htmlDoc

# END Test testCoreToHtml_Save

@pytest.mark.core
def testCoreToHtml_Methods(dummyGUI):
    """Test all the other methods of the ToHtml class.
    """
    theProject = NWProject(dummyGUI)
    theHtml = ToHtml(theProject, dummyGUI)
    theHtml.setKeepMarkdown(True)

    # Auto-Replace, keep Unicode
    docText = "Text with <brackets> & short–dash, long—dash …\n"
    theHtml.theText = docText
    theHtml.setReplaceUnicode(False)
    theHtml.doPreProcessing()
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<p>Text with &lt;brackets&gt; &amp; short–dash, long—dash …</p>\n"
    )

    # Auto-Replace, replace Unicode
    docText = "Text with <brackets> & short–dash, long—dash …\n"
    theHtml.theText = docText
    theHtml.setReplaceUnicode(True)
    theHtml.doPreProcessing()
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theResult == (
        "<p>Text with &lt;brackets&gt; &amp; short&ndash;dash, long&mdash;dash &hellip;</p>\n"
    )

    # With Preview
    theHtml.setPreview(True, True)
    theHtml.theText = docText
    theHtml.doPreProcessing()
    theHtml.tokenizeText()
    theHtml.doConvert()
    assert theHtml.theMarkdown[-1] == (
        "Text with &lt;brackets&gt; &amp; short&ndash;dash, long&mdash;dash &hellip;\n\n"
    )
    theHtml.doPostProcessing()
    assert theHtml.theMarkdown[-1] == (
        "Text with &lt;brackets&gt; &amp; short&ndash;dash, long&mdash;dash &hellip;\n\n"
    )

    # Result Size
    assert theHtml.getFullResultSize() == 147

    # CSS
    # ===

    assert len(theHtml.getStyleSheet()) > 1
    assert "p {text-align: left;" in " ".join(theHtml.getStyleSheet())
    assert "p {text-align: justify;" not in " ".join(theHtml.getStyleSheet())

    theHtml.setJustify(True)
    assert "p {text-align: left;" not in " ".join(theHtml.getStyleSheet())
    assert "p {text-align: justify;" in " ".join(theHtml.getStyleSheet())

    theHtml.setStyles(False)
    assert theHtml.getStyleSheet() == []

# END Test testCoreToHtml_Methods
