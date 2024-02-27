"""
novelWriter – Counter Module Tester
===================================

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

from novelwriter.text.counting import standardCounter


@pytest.mark.core
def testTextCounting_standardCounter():
    """Test the word counter and the exclusion filers."""
    # Non-Text
    assert standardCounter(None) == (0, 0, 0)  # type: ignore
    assert standardCounter(1234) == (0, 0, 0)  # type: ignore

    # General Text
    cC, wC, pC = standardCounter((
        "# Heading One\n"
        "## Heading Two\n"
        "### Heading Three\n"
        "#### Heading Four\n\n"
        "@tag: value\n\n"
        "% A comment that should not be counted.\n\n"
        "The first paragraph.\n\n"
        "The second paragraph.\n\n\n"
        "The third paragraph.\n\n"
        "Dashes\u2013and even longer\u2014dashes."
    ))
    assert cC == 138
    assert wC == 22
    assert pC == 4

    # Text Alignment
    cC, wC, pC = standardCounter((
        "# Title\n\n"
        "Left aligned<<\n\n"
        "Left aligned <<\n\n"
        "Right indent<\n\n"
        "Right indent <\n\n"
    ))
    assert cC == 53
    assert wC == 9
    assert pC == 4

    cC, wC, pC = standardCounter((
        "# Title\n\n"
        ">>Right aligned\n\n"
        ">> Right aligned\n\n"
        ">Left indent\n\n"
        "> Left indent\n\n"
    ))
    assert cC == 53
    assert wC == 9
    assert pC == 4

    cC, wC, pC = standardCounter((
        "# Title\n\n"
        ">>Centre aligned<<\n\n"
        ">> Centre aligned <<\n\n"
        ">Double indent<\n\n"
        "> Double indent <\n\n"
    ))
    assert cC == 59
    assert wC == 9
    assert pC == 4

    # Formatting Codes, Upper Case (Old Implementation)
    cC, wC, pC = standardCounter((
        "Some text\n\n"
        "[NEWPAGE]\n\n"
        "more text\n\n"
        "[NEW PAGE]\n\n"
        "even more text\n\n"
        "[VSPACE]\n\n"
        "and some final text\n\n"
        "[VSPACE:4]\n\n"
        "THE END\n\n"
    ))
    assert cC == 58
    assert wC == 13
    assert pC == 5

    # Formatting Codes, Lower Case (Current Implementation)
    cC, wC, pC = standardCounter((
        "Some text\n\n"
        "[newpage]\n\n"
        "more text\n\n"
        "[new page]\n\n"
        "even more text\n\n"
        "[vspace]\n\n"
        "and some final text\n\n"
        "[vspace:4]\n\n"
        "THE END\n\n"
    ))
    assert cC == 58
    assert wC == 13
    assert pC == 5

    # Check ShortCodes
    cC, wC, pC = standardCounter((
        "Text with [b]bold[/b] text and padded [b] bold [/b] text.\n\n"
        "Text with [b][i] nested [/i] emphasis [/b] in it.\n\n"
    ))
    assert cC == 78
    assert wC == 14
    assert pC == 2

# END Test testTextCounting_standardCounter
