"""
novelWriter – GUI Editor Hover Card
===================================

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

import html
import logging

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from novelwriter import SHARED
from novelwriter.core.indexdata import TT_NONE

logger = logging.getLogger(__name__)


class GuiDocHoverCard(QFrame):
    """GUI: Editor Reference Tag Hover Card.

    A small, permanently owned popup used by the editor to show
    information about a reference tag when the mouse hovers over it.
    The widget is kept hidden until needed, and caches the assembled
    text so it does not need to be rebuilt every time the same tag is
    hovered again.
    """

    __slots__ = ("_cache", "_label", "_layout", "_tag")

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent, Qt.WindowType.ToolTip)

        self.setObjectName("GuiDocHoverCard")
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.setLineWidth(1)

        self._tag = ""
        self._cache: dict[str, str] = {}

        self._label = QLabel(self)
        self._label.setFrameStyle(QFrame.Shape.NoFrame)
        self._label.setTextFormat(Qt.TextFormat.RichText)
        self._label.setWordWrap(True)

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._label)
        self._layout.setContentsMargins(6, 6, 6, 6)

        self.setLayout(self._layout)

        self.updateTheme()
        self.hide()

    def updateTheme(self) -> None:
        """Update the widget's colours to match the editor's theme."""
        syntax = SHARED.theme.syntaxTheme
        self.setStyleSheet(
            f"#GuiDocHoverCard {{ background: {syntax.back.name()}; border: 1px solid {syntax.text.name()}; }}"
        )
        self._label.setStyleSheet(f"border: none; color: {syntax.text.name()};")

    def setTag(self, tag: str) -> bool:
        """Assemble and cache the hover text for a given reference tag,
        looked up from the project index, and update the label. Returns
        True if the tag resolved to any content to display.
        """
        if tag != self._tag:
            self._tag = tag
            if tag and tag not in self._cache:
                self._cache[tag] = self._buildText(tag)
            text = self._cache.get(tag, "")
            self._label.setText(text)
        return bool(self._label.text())

    def clearCache(self) -> None:
        """Clear the cached hover text, e.g. when the project index has
        changed and cached entries may be stale.
        """
        self._tag = ""
        self._cache = {}

    def showAt(self, pos: QPoint) -> None:
        """Show the hover card with its top-left corner at pos."""
        self.adjustSize()
        self.move(pos)
        self.show()

    def _buildText(self, tag: str) -> str:
        """Assemble the HTML hover text for a given reference tag."""
        index = SHARED.project.index
        name, _, iItem, hItem = index.getSingleTag(tag)
        if not name or iItem is None:
            return ""

        syntax = SHARED.theme.syntaxTheme
        name = html.escape(name)
        display = html.escape(index.getTagDisplay(tag))
        if name == display:
            lines = [f'<p><span style="color: {syntax.tag.name()};">{name}</span></p>']
        else:
            head = f'<p><span style="color: {syntax.tag.name()};">{name}</span>'
            sep = f'<span style="color: {syntax.text.name()};"> | </span>'
            tail = f'<span style="color: {syntax.opt.name()};">{display}</span></p>'
            lines = [head + sep + tail]

        if hItem:
            if hItem.key != TT_NONE and hItem.title:
                title = html.escape(hItem.title)
                titleSize = round(self._label.font().pointSizeF() * 1.25)
                style = f"color: {syntax.head.name()}; font-size: {titleSize}pt; font-weight: 600;"
                lines.append(f'<p><span style="{style}">{title}</span></p>')
            if synopsis := hItem.synopsis:
                lines.append(f'<p><span style="color: {syntax.note.name()};">{html.escape(synopsis)}</span></p>')

        return "".join(lines)
