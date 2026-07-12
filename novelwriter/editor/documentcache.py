"""
novelWriter – Document Cache
=============================

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

import logging

from collections import OrderedDict
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from novelwriter.core.document import ProjectDocument
    from novelwriter.editor.editordocument import GuiTextDocument

logger = logging.getLogger(__name__)

DEFAULT_CACHE_SIZE = 5


class CacheEntry(NamedTuple):
    """Core: A single cached document entry."""

    nwDocument: ProjectDocument
    qDocument: GuiTextDocument


class DocumentCache:
    """Core: LRU Cache of Recently Opened Editor Documents.

    Keeps a bounded number of ProjectDocument/GuiTextDocument pairs
    alive in memory so that switching back to a recently opened
    document restores its Qt-native undo/redo history and syntax
    highlighting, instead of reloading the document from scratch.
    """

    def __init__(self, maxSize: int = DEFAULT_CACHE_SIZE) -> None:
        self._maxSize = max(1, maxSize)
        self._entries: OrderedDict[str, CacheEntry] = OrderedDict()

    def __len__(self) -> int:
        """Return the number of cached entries."""
        return len(self._entries)

    def __contains__(self, tHandle: str) -> bool:
        """Check if a document handle is cached."""
        return tHandle in self._entries

    def get(self, tHandle: str) -> CacheEntry | None:
        """Return a cached entry, and mark it as most recently used."""
        if entry := self._entries.get(tHandle):
            self._entries.move_to_end(tHandle)
            return entry
        return None

    def store(self, tHandle: str, nwDocument: ProjectDocument, qDocument: GuiTextDocument) -> None:
        """Add or replace a cache entry as the most recently used one,
        evicting the least recently used entry if the cache is full.
        """
        if (old := self._entries.get(tHandle)) and old.qDocument is not qDocument:
            old.qDocument.softDelete()

        self._entries[tHandle] = CacheEntry(nwDocument, qDocument)
        self._entries.move_to_end(tHandle)
        while len(self._entries) > self._maxSize:
            eHandle, evicted = self._entries.popitem(last=False)
            logger.debug("Evicted document '%s' from cache", eHandle)
            evicted.qDocument.softDelete()

    def remove(self, tHandle: str) -> None:
        """Remove and discard a cached entry, if present."""
        if entry := self._entries.pop(tHandle, None):
            entry.qDocument.softDelete()
            logger.debug("Removed document '%s' from cache", tHandle)

    def clear(self) -> None:
        """Discard all cached entries."""
        for entry in self._entries.values():
            entry.qDocument.softDelete()
        self._entries.clear()
        logger.debug("Cleared document cache")

    def documents(self) -> list[GuiTextDocument]:
        """Return the text documents of all cached entries."""
        return [entry.qDocument for entry in self._entries.values()]
