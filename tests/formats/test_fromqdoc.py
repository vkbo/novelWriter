"""
novelWriter – QTextDocument to Text Converter Tests
===================================================

This file is a part of novelWriter
Copyright (C) 2026 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa

from __future__ import annotations

import pytest

from PyQt6.QtGui import QTextDocument

from novelwriter import CONFIG
from novelwriter.core.project import NWProject
from novelwriter.formats.fromqdoc import FromQTextDocument
from novelwriter.formats.toqdoc import ToQTextDocument


@pytest.mark.core
def testFromQTextDocument_General():
    """Test a single document that touches most of the features
    supported by the converter: headings, both regular and beyond
    H4, clean-edge and nested emphasis, a soft line break, a
    mid-word format that falls back to a shortcode, superscript and
    subscript, and both right and centre alignment.
    """
    html = (
        "<h1>Chapter One</h1>"
        "<p>Some <b>bold</b>, <i>italic</i>, <s>strike</s>, <u>underline</u> and "
        "<b><i>bold italic</i></b> text.</p>"
        "<h5>A Minor Note</h5>"
        "<p>Line one<br>Line two.</p>"
        "<p>Mixed<b>bo</b>ld and water<sup>2</sup>O with H<sub>2</sub>O.</p>"
        '<p style="text-align:right">Signed, the Author.</p>'
        '<p style="text-align:center">The End</p>'
    )
    document = QTextDocument()
    document.setHtml(html)

    converter = FromQTextDocument(document)
    result = converter.convertText()

    assert result == (
        "# Chapter One\n"
        "\n"
        "Some **bold**, _italic_, ~~strike~~, [u]underline[/u] and **_bold italic_** text.\n"
        "\n"
        "**A Minor Note**\n"
        "\n"
        "Line one\nLine two.\n"
        "\n"
        "Mixed[b]bo[/b]ld and water[sup]2[/sup]O with H[sub]2[/sub]O.\n"
        "\n"
        ">> Signed, the Author.\n"
        "\n"
        ">> The End <<\n"
    )

    # With soft breaks collapsed to a space instead of kept as a line break
    converter.setPreserveSoftBreak(False)
    result = converter.convertText()
    assert "Line one Line two.\n" in result
    assert "Line one\nLine two.\n" not in result

    # An empty paragraph contributes no text, just the blank separator
    document = QTextDocument()
    document.setHtml("<p>First</p><p><br></p><p>Second</p>")
    result = FromQTextDocument(document).convertText()
    assert result == "First\n\n\nSecond\n"


@pytest.mark.core
def testFromQTextDocument_MarkdownVsShortcode():
    """Test the edge cases that decide whether a format is written
    as Markdown or as a novelWriter shortcode: Markdown is only used
    when the formatted run sits on two clean word edges. Also checks
    that the single asterisk bold setting only affects the Markdown
    form, not the shortcode fallback.
    """

    def convert(html: str) -> str:
        """Convert an HTML fragment via FromQTextDocument."""
        document = QTextDocument()
        document.setHtml(html)
        return FromQTextDocument(document).convertText().strip()

    # Clean word edges convert to Markdown
    assert convert("<p>A <b>bold</b> word.</p>") == "A **bold** word."
    assert convert("<p><b>Bold</b> start.</p>") == "**Bold** start."
    assert convert("<p>This is <b>bold</b></p>") == "This is **bold**"
    assert convert("<p>Wait <b>(bold)</b> now.</p>") == "Wait **(bold)** now."
    assert convert("<p>Some <b> bold </b> text.</p>") == "Some **bold** text."

    # Dirty word edges fall back to shortcodes
    assert convert("<p>Mid<b>dle</b>man.</p>") == "Mid[b]dle[/b]man."
    assert convert("<p>Bold<b>ly</b> stated.</p>") == "Bold[b]ly[/b] stated."
    assert convert("<p>Very <b>bold</b>ly stated.</p>") == "Very [b]bold[/b]ly stated."

    # Formats with no Markdown equivalent always use shortcodes
    assert convert("<p>Some <u>underlined</u> word.</p>") == "Some [u]underlined[/u] word."
    assert convert("<p>E=mc<sup>2</sup> and H<sub>2</sub>O.</p>") == "E=mc[sup]2[/sup] and H[sub]2[/sub]O."

    # Nested formats on a clean edge nest their Markdown tags
    assert convert("<p>Some <b><i><s>combo</s></i></b> text.</p>") == "Some **_~~combo~~_** text."

    # A formatted fragment with no visible text contributes nothing
    assert convert("<p>A<b> </b>B</p>") == "A B"

    # Single asterisk bold only changes the Markdown form
    CONFIG.singleStarBold = True
    assert convert("<p>A <b>bold</b> word.</p>") == "A *bold* word."
    assert convert("<p>Mid<b>dle</b>man.</p>") == "Mid[b]dle[/b]man."


@pytest.mark.core
def testFromQTextDocument_DocumentRoundTrip(mockGUI):
    """Test a round trip of novelWriter text through ToQTextDocument
    and back again through FromQTextDocument.
    """
    project = NWProject()
    toDoc = ToQTextDocument(project)
    toDoc.initDocument()

    text = (
        "# Heading One\n"
        "\n"
        "## Heading Two\n"
        "\n"
        "Some **bold** and _italic_ and ~~strike~~ text.\n"
        "\n"
        "Some [u]underline[/u] and [sup]super[/sup] and [sub]sub[/sub] text.\n"
        "\n"
        ">> Right aligned text.\n"
        "\n"
        ">> Centered text. <<\n"
    )

    toDoc._text = text
    toDoc.tokenizeText()
    toDoc.doConvert()

    result = FromQTextDocument(toDoc.document).convertText()

    assert result == text
