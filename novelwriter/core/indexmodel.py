"""
novelWriter – Project Index Model
=================================

File History:
Created: 2025-02-09 [2.7b2] IndexNode

This file is a part of novelWriter
Copyright (C) 2025 Veronica Berglyd Olsen and novelWriter contributors

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

from novelwriter.core.item import NWItem


class IndexNode:

    __slots__ = (
        "_item", "_key", "_line", "_level", "_title", "_summary",
        "_tag", "_refs", "_notes", "_counts",
    )

    def __init__(
        self, item: NWItem, key: str, line: int = 0, level: int = 0, title: str = ""
    ) -> None:
        self._item = item
        self._key = key
        self._line = line
        self._level = level
        self._title = title
        self._summary = ""
        self._tag = ""
        self._refs: dict[str, set[str]] = {}
        self._notes: dict[str, list[str]] = {}
        self._counts: tuple[int, int, int] = (0, 0, 0)
        return
