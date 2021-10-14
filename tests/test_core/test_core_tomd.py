"""
novelWriter – ToMd Class Tester
===============================

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

from novelwriter.core import NWProject, NWIndex, ToMarkdown


@pytest.mark.core
def testCoreToMarkdown_ConvertFormat(mockGUI):
    """Test the tokenizer and converter chain using the ToMarkdown class.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)
    theMD = ToMarkdown(theProject)

    # Headers
    # =======

    theMD.isNovel = True
    theMD.isNote = False
    theMD.isFirst = True

    # Header 1
    theMD.theText = "# Partition\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == "# Partition\n\n"

    # Header 2
    theMD.theText = "## Chapter Title\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == "## Chapter Title\n\n"

    # Header 3
    theMD.theText = "### Scene Title\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == "### Scene Title\n\n"

    # Header 4
    theMD.theText = "#### Section Title\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == "#### Section Title\n\n"

    # Title
    theMD.theText = "#! Title\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == "# Title\n\n"

    # Unnumbered
    theMD.theText = "##! Prologue\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == "## Prologue\n\n"

    # Paragraphs
    # ==========

    # Text for GitHub Markdown
    theMD.setGitHubMarkdown()
    theMD.theText = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == (
        "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n\n"
    )

    # Text for Standard Markdown
    theMD.setStandardMarkdown()
    theMD.theText = "Some **nested bold and _italic_ and ~~strikethrough~~ text** here\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == (
        "Some **nested bold and _italic_ and strikethrough text** here\n\n"
    )

    # Text w/Hard Break
    theMD.theText = "Line one  \nLine two  \nLine three\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == "Line one  \nLine two  \nLine three\n\n"

    # Synopsis
    theMD.theText = "%synopsis: The synopsis ...\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == ""

    theMD.setSynopsis(True)
    theMD.theText = "%synopsis: The synopsis ...\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == "**Synopsis:** The synopsis ...\n\n"

    # Comment
    theMD.theText = "% A comment ...\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == ""

    theMD.setComments(True)
    theMD.theText = "% A comment ...\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == "**Comment:** A comment ...\n\n"

    # Keywords
    theMD.theText = "@char: Bod, Jane\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == ""

    theMD.setKeywords(True)
    theMD.theText = "@char: Bod, Jane\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == "**Characters:** Bod, Jane\n\n"

    # Multiple Keywords
    theMD.setKeywords(True)
    theMD.theText = "## Chapter\n\n@pov: Bod\n@plot: Main\n@location: Europe\n\n"
    theMD.tokenizeText()
    theMD.doConvert()
    assert theMD.theResult == (
        "## Chapter\n\n"
        "**Point of View:** Bod  \n"
        "**Plot:** Main  \n"
        "**Locations:** Europe\n\n"
    )

# END Test testCoreToMarkdown_ConvertFormat


@pytest.mark.core
def testCoreToMarkdown_ConvertDirect(mockGUI):
    """Test the converter directly using the ToMarkdown class.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)
    theMD = ToMarkdown(theProject)

    theMD.isNovel = True
    theMD.isNote = False

    # Special Titles
    # ==============

    # Title
    theMD.theTokens = [
        (theMD.T_TITLE, 1, "A Title", None, theMD.A_PBB | theMD.A_CENTRE),
        (theMD.T_EMPTY, 1, "", None, theMD.A_NONE),
    ]
    theMD.doConvert()
    assert theMD.theResult == "# A Title\n\n"

    # Unnumbered
    theMD.theTokens = [
        (theMD.T_UNNUM, 1, "Prologue", None, theMD.A_PBB),
        (theMD.T_EMPTY, 1, "", None, theMD.A_NONE),
    ]
    theMD.doConvert()
    assert theMD.theResult == "## Prologue\n\n"

    # Separators
    # ==========

    # Separator
    theMD.theTokens = [
        (theMD.T_SEP, 1, "* * *", None, theMD.A_CENTRE),
        (theMD.T_EMPTY, 1, "", None, theMD.A_NONE),
    ]
    theMD.doConvert()
    assert theMD.theResult == "* * *\n\n"

    # Skip
    theMD.theTokens = [
        (theMD.T_SKIP, 1, "", None, theMD.A_NONE),
        (theMD.T_EMPTY, 1, "", None, theMD.A_NONE),
    ]
    theMD.doConvert()
    assert theMD.theResult == "\n\n\n"

# END Test testCoreToMarkdown_ConvertDirect


@pytest.mark.core
def testCoreToMarkdown_Complex(mockGUI, fncDir):
    """Test the save method of the ToMarkdown class.
    """
    theProject = NWProject(mockGUI)
    theMD = ToMarkdown(theProject)
    theMD.isNovel = True

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
        "# My Novel\n\n**By Jane Doh**\n\n",
        "## Chapter 1\n\nThe text of chapter one.\n\n",
        "### Scene 1\n\nThe text of scene one.\n\n",
        "#### A Section\n\nMore text in scene one.\n\n",
        "## Chapter 2\n\nThe text of chapter two.\n\n",
        "### Scene 2\n\nThe text of scene two.\n\n",
        "#### A Section\n\n\tMore text in scene two.\n\n",
    ]

    for i in range(len(docText)):
        theMD.theText = docText[i]
        theMD.doPreProcessing()
        theMD.tokenizeText()
        theMD.doConvert()
        assert theMD.theResult == resText[i]

    assert theMD.fullMD == resText
    assert theMD.getFullResultSize() == len("".join(resText))

    theMD.replaceTabs(nSpaces=4, spaceChar=" ")
    resText[6] = "#### A Section\n\n    More text in scene two.\n\n"

    # Check File
    # ==========

    saveFile = os.path.join(fncDir, "outFile.md")
    theMD.saveMarkdown(saveFile)
    assert readFile(saveFile) == "".join(resText)

# END Test testCoreToHtml_Complex


@pytest.mark.core
def testCoreToMarkdown_Format(mockGUI):
    """Test all the formatters for the ToMarkdown class.
    """
    theProject = NWProject(mockGUI)
    mockGUI.theIndex = NWIndex(theProject)
    theMD = ToMarkdown(theProject)

    assert theMD._formatKeywords("", theMD.A_NONE) == ""
    assert theMD._formatKeywords("tag: Jane", theMD.A_NONE) == "**Tag:** Jane\n\n"
    assert theMD._formatKeywords("tag: Jane, John", theMD.A_NONE) == "**Tag:** Jane, John\n\n"
    assert theMD._formatKeywords("tag: Jane", theMD.A_Z_BTMMRG) == "**Tag:** Jane  \n"

# END Test testCoreToMarkdown_Format
