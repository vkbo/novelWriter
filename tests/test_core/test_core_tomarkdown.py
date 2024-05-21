"""
novelWriter – ToMd Class Tester
===============================

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

import pytest

from novelwriter.core.project import NWProject
from novelwriter.core.tomarkdown import ToMarkdown


@pytest.mark.core
def testCoreToMarkdown_ConvertHeaders(mockGUI):
    """Test header formats in the ToMarkdown class."""
    project = NWProject()
    toMD = ToMarkdown(project)

    toMD._isNovel = True
    toMD._isFirst = True

    # Header 1
    toMD._text = "# Partition\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "# Partition\n\n"

    # Header 2
    toMD._text = "## Chapter Title\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "## Chapter Title\n\n"

    # Header 3
    toMD._text = "### Scene Title\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "### Scene Title\n\n"

    # Header 4
    toMD._text = "#### Section Title\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "#### Section Title\n\n"

    # Title
    toMD._text = "#! Title\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "# Title\n\n"

    # Unnumbered
    toMD._text = "##! Prologue\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "## Prologue\n\n"


@pytest.mark.core
def testCoreToMarkdown_ConvertParagraphs(mockGUI):
    """Test paragraph formats in the ToMarkdown class."""
    project = NWProject()
    toMD = ToMarkdown(project)

    toMD._isNovel = True
    toMD._isFirst = True

    # Text for Extended Markdown
    toMD.setExtendedMarkdown()
    toMD._text = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == (
        "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n\n"
    )

    # Text for Standard Markdown
    toMD.setStandardMarkdown()
    toMD._text = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == (
        "Some **nested bold and _italic_ and strikethrough text** here\n\n"
    )

    # Shortcodes for Extended Markdown
    toMD.setExtendedMarkdown()
    toMD._text = (
        "Some [b]bold[/b], [i]italic[/i], [s]strike[/s], [u]underline[/u], [m]mark[/m], "
        "super[sup]script[/sup], sub[sub]script[/sub] here\n"
    )
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == (
        "Some **bold**, _italic_, ~~strike~~, underline, ==mark==, "
        "super^script^, sub~script~ here\n\n"
    )

    # Shortcodes for Standard Markdown
    toMD.setStandardMarkdown()
    toMD._text = (
        "Some [b]bold[/b], [i]italic[/i], [s]strike[/s], [u]underline[/u], [m]mark[/m], "
        "super[sup]script[/sup], sub[sub]script[/sub] here\n"
    )
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == (
        "Some **bold**, _italic_, strike, underline, mark, superscript, subscript here\n\n"
    )

    # Text w/Hard Break
    toMD._text = "Line one\nLine two\nLine three\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "Line one  \nLine two  \nLine three\n\n"

    # Text wo/Hard Break
    toMD._text = "Line one\nLine two\nLine three\n"
    toMD.setKeepLineBreaks(False)
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "Line one Line two Line three\n\n"

    # Synopsis, Short
    toMD._text = "%synopsis: The synopsis ...\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == ""

    toMD.setSynopsis(True)
    toMD._text = "%synopsis: The synopsis ...\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "**Synopsis:** The synopsis ...\n\n"

    toMD.setSynopsis(True)
    toMD._text = "%short: A description ...\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "**Short Description:** A description ...\n\n"

    # Comment
    toMD._text = "% A comment ...\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == ""

    toMD.setComments(True)
    toMD._text = "% A comment ...\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "**Comment:** A comment ...\n\n"

    # Keywords
    toMD._text = "@char: Bod, Jane\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == ""

    toMD.setKeywords(True)
    toMD._text = "@char: Bod, Jane\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "**Characters:** Bod, Jane\n\n"

    # Multiple Keywords
    toMD.setKeywords(True)
    toMD._text = "## Chapter\n\n@pov: Bod\n@plot: Main\n@location: Europe\n\n"
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == (
        "## Chapter\n\n"
        "**Point of View:** Bod  \n"
        "**Plot:** Main  \n"
        "**Locations:** Europe\n\n"
    )

    # Footnotes
    toMD._text = (
        "Text with one[footnote:fa] or two[footnote:fb] footnotes.\n\n"
        "%footnote.fa: Footnote text A.\n\n"
    )
    toMD.tokenizeText()
    toMD.doConvert()
    assert toMD.result == "Text with one[1] or two[ERR] footnotes.\n\n"

    toMD.appendFootnotes()
    assert toMD.result == (
        "Text with one[1] or two[ERR] footnotes.\n\n"
        "### Footnotes\n\n"
        "1. Footnote text A.\n\n"
    )


@pytest.mark.core
def testCoreToMarkdown_ConvertDirect(mockGUI):
    """Test the converter directly using the ToMarkdown class."""
    project = NWProject()
    toMD = ToMarkdown(project)

    toMD._isNovel = True

    # Special Titles
    # ==============

    # Title
    toMD._tokens = [
        (toMD.T_TITLE, 1, "A Title", [], toMD.A_PBB | toMD.A_CENTRE),
        (toMD.T_EMPTY, 1, "", [], toMD.A_NONE),
    ]
    toMD.doConvert()
    assert toMD.result == "# A Title\n\n"

    # Separators
    # ==========

    # Separator
    toMD._tokens = [
        (toMD.T_SEP, 1, "* * *", [], toMD.A_CENTRE),
        (toMD.T_EMPTY, 1, "", [], toMD.A_NONE),
    ]
    toMD.doConvert()
    assert toMD.result == "* * *\n\n"

    # Skip
    toMD._tokens = [
        (toMD.T_SKIP, 1, "", [], toMD.A_NONE),
        (toMD.T_EMPTY, 1, "", [], toMD.A_NONE),
    ]
    toMD.doConvert()
    assert toMD.result == "\n\n"


@pytest.mark.core
def testCoreToMarkdown_Save(mockGUI, fncPath):
    """Test the save method of the ToMarkdown class."""
    project = NWProject()
    toMD = ToMarkdown(project)
    toMD.setKeepMarkdown(True)
    toMD._isNovel = True

    # Build Project
    # =============

    docText = [
        "# My Novel\n\n**By Jane Doh**\n",
        "## Chapter 1\n\nThe text of chapter one.\n",
        "### Scene 1\n\nThe text of scene one.\n",
        "#### A Section\n\nMore text in scene one.\n",
        "## Chapter 2\n\nThe text of chapter two.\n",
        "### Scene 2\n\nThe text of scene two.\n",
        "#### A Section\n\n\tMore text in scene two.\n",
    ]
    resText = [
        "# My Novel\n\n**By Jane Doh**\n\n",
        "## Chapter 1\n\nThe text of chapter one.\n\n",
        "### Scene 1\n\nThe text of scene one.\n\n",
        "#### A Section\n\nMore text in scene one.\n\n",
        "## Chapter 2\n\nThe text of chapter two.\n\n",
        "### Scene 2\n\nThe text of scene two.\n\n",
        "#### A Section\n\n\tMore text in scene two.\n\n",
    ]

    for i in range(len(docText)):
        toMD._text = docText[i]
        toMD.doPreProcessing()
        toMD.tokenizeText()
        toMD.doConvert()
        assert toMD.result == resText[i]

    assert toMD.fullMD == resText
    assert toMD.getFullResultSize() == len("".join(resText))

    toMD.replaceTabs(nSpaces=4, spaceChar=" ")
    resText[6] = "#### A Section\n\n    More text in scene two.\n\n"
    assert toMD.allMarkdown == resText

    # Check File
    # ==========

    saveFile = fncPath / "outFile.md"
    toMD.saveMarkdown(saveFile)
    assert saveFile.read_text(encoding="utf-8") == "".join(resText)


@pytest.mark.core
def testCoreToMarkdown_Format(mockGUI):
    """Test all the formatters for the ToMarkdown class."""
    project = NWProject()
    toMD = ToMarkdown(project)

    assert toMD._formatKeywords("", toMD.A_NONE) == ""
    assert toMD._formatKeywords("tag: Jane", toMD.A_NONE) == "**Tag:** Jane\n\n"
    assert toMD._formatKeywords("tag: Jane, John", toMD.A_NONE) == "**Tag:** Jane, John\n\n"
    assert toMD._formatKeywords("tag: Jane", toMD.A_Z_BTMMRG) == "**Tag:** Jane  \n"
