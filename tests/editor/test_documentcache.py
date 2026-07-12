"""
novelWriter – Document Cache Tests
==================================

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

import gc
import weakref

from unittest.mock import MagicMock

from PyQt6.QtCore import QObject

from novelwriter.editor.documentcache import DocumentCache


def _entry() -> tuple[MagicMock, MagicMock]:
    """Create a stand-in (nwDocument, qDocument) pair for cache tests."""
    nwDocument = MagicMock()
    nwDocument.fileLocation = "mock.nwd"
    qDocument = MagicMock()
    return nwDocument, qDocument


class _StubDocument(QObject):
    """Minimal real QObject with a genuine softDelete, so eviction can
    be checked to actually free memory rather than just having its
    mocked softDelete method called.
    """

    def softDelete(self) -> None:
        """Detach from any Qt parent, matching GuiTextDocument.softDelete."""
        self.setParent(None)  # type: ignore


def testEditorDocCache_GetStoreRemove():
    """Test the basic get/store/remove operations of the cache."""
    cache = DocumentCache(maxSize=5)
    assert len(cache) == 0
    assert "aaa" not in cache
    assert cache.get("aaa") is None

    nwDoc, qDoc = _entry()
    cache.store("aaa", nwDoc, qDoc)
    assert len(cache) == 1
    assert "aaa" in cache

    entry = cache.get("aaa")
    assert entry is not None
    assert entry.nwDocument is nwDoc
    assert entry.qDocument is qDoc

    cache.remove("aaa")
    assert len(cache) == 0
    assert "aaa" not in cache
    assert cache.get("aaa") is None
    qDoc.softDelete.assert_called_once()

    # Removing a handle that isn't cached should be a no-op
    cache.remove("aaa")
    cache.remove("bbb")
    assert len(cache) == 0


def testEditorDocCache_StoreReplacesExistingEntry():
    """Test that storing a new document under an already cached handle
    discards the previous document.
    """
    cache = DocumentCache(maxSize=5)

    nwDocA, qDocA = _entry()
    cache.store("aaa", nwDocA, qDocA)
    assert cache.get("aaa") is not None
    qDocA.softDelete.assert_not_called()

    nwDocB, qDocB = _entry()
    cache.store("aaa", nwDocB, qDocB)
    assert len(cache) == 1

    entry = cache.get("aaa")
    assert entry is not None
    assert entry.nwDocument is nwDocB
    assert entry.qDocument is qDocB
    qDocA.softDelete.assert_called_once()
    qDocB.softDelete.assert_not_called()

    # Re-storing the same document under its own handle should not
    # trigger a deletion of itself
    cache.store("aaa", nwDocB, qDocB)
    qDocB.softDelete.assert_not_called()


def testEditorDocCache_Eviction():
    """Test that the least recently used entry is evicted once the
    cache exceeds its maximum size, and that its document is deleted.
    """
    cache = DocumentCache(maxSize=2)

    _, qDocA = _entry()
    _, qDocB = _entry()
    _, qDocC = _entry()

    cache.store("a", MagicMock(), qDocA)
    cache.store("b", MagicMock(), qDocB)
    assert len(cache) == 2

    # Adding a third entry should evict "a", the least recently used
    cache.store("c", MagicMock(), qDocC)

    assert len(cache) == 2
    assert "a" not in cache
    assert "b" in cache
    assert "c" in cache
    qDocA.softDelete.assert_called_once()
    qDocB.softDelete.assert_not_called()
    qDocC.softDelete.assert_not_called()


def testEditorDocCache_GetPromotesToMostRecentlyUsed():
    """Test that fetching an entry marks it as most recently used, so
    that it isn't the next one evicted.
    """
    cache = DocumentCache(maxSize=2)

    _, qDocA = _entry()
    _, qDocB = _entry()
    _, qDocC = _entry()

    cache.store("a", MagicMock(), qDocA)
    cache.store("b", MagicMock(), qDocB)

    # Touch "a" so that "b" becomes the least recently used
    assert cache.get("a") is not None
    cache.store("c", MagicMock(), qDocC)

    assert "a" in cache
    assert "b" not in cache
    assert "c" in cache
    qDocB.softDelete.assert_called_once()
    qDocA.softDelete.assert_not_called()


def testEditorDocCache_Clear():
    """Test that clearing the cache deletes all cached documents."""
    cache = DocumentCache(maxSize=5)

    _, qDocA = _entry()
    _, qDocB = _entry()
    cache.store("a", MagicMock(), qDocA)
    cache.store("b", MagicMock(), qDocB)

    cache.clear()

    assert len(cache) == 0
    assert cache.documents() == []
    qDocA.softDelete.assert_called_once()
    qDocB.softDelete.assert_called_once()


def testEditorDocCache_Documents():
    """Test that the documents helper returns all cached documents."""
    cache = DocumentCache(maxSize=5)

    _, qDocA = _entry()
    _, qDocB = _entry()
    cache.store("a", MagicMock(), qDocA)
    cache.store("b", MagicMock(), qDocB)

    assert set(cache.documents()) == {qDocA, qDocB}


def testEditorDocCache_EvictionFreesDocument(qtbot):
    """Test that an evicted document is freed by reference count alone
    (with the cyclic GC disabled) once the cache and the test both
    drop their references to it, i.e. that eviction doesn't leak.
    Mirrors the checkWidgetFreedOnRelease pattern used elsewhere in
    this codebase for the same class of QObject lifetime check.
    """
    cache = DocumentCache(maxSize=1)

    qDocA = _StubDocument()
    ref = weakref.ref(qDocA)
    cache.store("a", MagicMock(), qDocA)  # type: ignore[arg-type]
    del qDocA

    gc.disable()
    try:
        # Storing a second entry evicts "a" and calls its softDelete
        cache.store("b", MagicMock(), _StubDocument())  # type: ignore[arg-type]
        assert ref() is None, "Evicted document was not freed by reference count alone"
    finally:
        gc.enable()
