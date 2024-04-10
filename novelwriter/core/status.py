"""
novelWriter – Project Item Status Class
=======================================

File History:
Created:   2019-05-19 [0.1.3] NWStatus
Rewritten: 2022-04-05 [2.0b1] NWStatus

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

import dataclasses
import logging
import random

from collections.abc import Iterable
from math import cos, pi, sin
from typing import TYPE_CHECKING, Literal

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QIcon, QPainter, QPainterPath, QPixmap, QColor, QPolygonF

from novelwriter import SHARED
from novelwriter.common import simplified
from novelwriter.enum import nwStatusShape
from novelwriter.types import QtPaintAnitAlias, QtTransparent

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypeGuard  # Requires Python 3.10

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class StatusEntry:

    name: str
    color: QColor
    shape: nwStatusShape
    icon: QIcon
    count: int = 0

    @classmethod
    def duplicate(cls, source: StatusEntry) -> StatusEntry:
        """Create a shallow copy of the source object."""
        return dataclasses.replace(source)

# END Class StatusEntry


NO_ENTRY = StatusEntry("", QColor(0, 0, 0), nwStatusShape.SQUARE, QIcon(), 0)


class NWStatus:

    STATUS = 1
    IMPORT = 2

    def __init__(self, kind: Literal[1, 2]) -> None:

        self._type = kind
        self._store: dict[str, StatusEntry] = {}
        self._default = None

        self._iPx = SHARED.theme.baseIconHeight

        if self._type == self.STATUS:
            self._prefix = "s"
        elif self._type == self.IMPORT:
            self._prefix = "i"
        else:
            raise Exception("This is a bug!")

        return

    def __len__(self) -> int:
        return len(self._store)

    def __getitem__(self, key: str | None) -> StatusEntry:
        """Return the entry associated with a given key."""
        if key and key in self._store:
            return self._store[key]
        elif self._default is not None:
            return self._store[self._default]
        return NO_ENTRY

    ##
    #  Methods
    ##

    def add(self, key: str | None, name: str, color: tuple[int, int, int],
            shape: str, count: int) -> str:
        """Add or update a status entry. If the key is invalid, a new
        key is generated.
        """
        if isinstance(color, tuple) and len(color) == 3:
            qColor = QColor(*color)
        else:
            qColor = QColor(100, 100, 100)

        try:
            iShape = nwStatusShape[shape]
        except KeyError:
            iShape = nwStatusShape.SQUARE

        key = self._checkKey(key)
        name = simplified(name)
        icon = self.createIcon(self._iPx, qColor, iShape)
        self._store[key] = StatusEntry(name, qColor, iShape, icon, count)

        if self._default is None:
            self._default = key

        return key

    def update(self, update: list[tuple[str | None, StatusEntry]]) -> None:
        """Update the list of statuses, and from removed list."""
        self._store.clear()
        for key, entry in update:
            self._store[self._checkKey(key)] = entry

        # Check if we need a new default
        if self._default not in self._store:
            self._default = next(iter(self._store)) if self._store else None

        return

    def check(self, value: str) -> str:
        """Check the key against the stored status names."""
        if self._isKey(value) and value in self._store:
            return value
        elif self._default is not None:
            return self._default
        return ""

    def resetCounts(self) -> None:
        """Clear the counts of references to the status entries."""
        for key in self._store:
            self._store[key].count = 0
        return

    def increment(self, key: str | None) -> None:
        """Increment the counter for a given entry."""
        if key and key in self._store:
            self._store[key].count += 1
        return

    def pack(self) -> Iterable[tuple[str, dict]]:
        """Pack the status entries into a dictionary."""
        for key, entry in self._store.items():
            yield (entry.name, {
                "key":   key,
                "count": str(entry.count),
                "red":   str(entry.color.red()),
                "green": str(entry.color.green()),
                "blue":  str(entry.color.blue()),
                "shape": entry.shape.name,
            })
        return

    def iterItems(self) -> Iterable[tuple[str, StatusEntry]]:
        """Yield entries from the status icons."""
        yield from self._store.items()

    @staticmethod
    def createIcon(height: int, colour: QColor, shape: nwStatusShape) -> QIcon:
        """Generate an icon for a status label."""
        pixmap = QPixmap(48, 48)
        pixmap.fill(QtTransparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QtPaintAnitAlias)
        painter.fillPath(_SHAPES.getShape(shape), colour)
        painter.end()

        return QIcon(pixmap.scaled(
            height, height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

    ##
    #  Internal Functions
    ##

    def _newKey(self) -> str:
        """Generate a new key for a status flag. This method is
        recursive, but should only fail if there is an issue with the
        random number generator or the user has added a lot of status
        flags. The Python recursion limit is given the job to handle
        the extreme case and will cause an app crash.
        """
        key = f"{self._prefix}{random.getrandbits(24):06x}"
        if key in self._store:
            key = self._newKey()
        return key

    def _isKey(self, value: str | None) -> TypeGuard[str]:
        """Check if a value is a key or not."""
        if not isinstance(value, str):
            return False
        if len(value) != 7:
            return False
        if value[0] != self._prefix:
            return False
        for c in value[1:]:
            if c not in "0123456789abcdef":
                return False
        return True

    def _checkKey(self, key: str | None) -> str:
        """Check key is valid, and if not, generate one."""
        return key if self._isKey(key) else self._newKey()

# END Class NWStatus


class _ShapeCache:

    def __init__(self) -> None:
        self._cache: dict[nwStatusShape, QPainterPath] = {}
        return

    def getShape(self, shape: nwStatusShape) -> QPainterPath:
        """Return a painter shape for an icon."""
        if shape in self._cache:
            return self._cache[shape]

        def circ(r: float, a: float, x: float, y: float) -> QPointF:
            # print(round(x+r*sin(pi*a/180), 2), round(y-r*cos(pi*a/180), 2))
            return QPointF(round(x+r*sin(pi*a/180), 2), round(y-r*cos(pi*a/180), 2))

        path = QPainterPath()
        if shape == nwStatusShape.SQUARE:
            path.addRoundedRect(2.0, 2.0, 44.0, 44.0, 4.0, 4.0)
        elif shape == nwStatusShape.CIRCLE:
            path.addEllipse(2.0, 2.0, 44.0, 44.0)
        elif shape == nwStatusShape.TRIANGLE:
            path.addPolygon(QPolygonF([
                circ(23.0, 0.0, 24.0, 26.0),
                circ(23.0, 120.0, 24.0, 26.0),
                circ(23.0, 240.0, 24.0, 26.0),
            ]))
        elif shape == nwStatusShape.DIAMOND:
            path.addPolygon(QPolygonF([
                circ(22.0, 0.0, 24.0, 24.0),
                circ(20.0, 90.0, 24.0, 24.0),
                circ(22.0, 180.0, 24.0, 24.0),
                circ(20.0, 270.0, 24.0, 24.0),
            ]))
        elif shape == nwStatusShape.PENTAGON:
            path.addPolygon(QPolygonF([
                circ(23.0, 0.0, 24.0, 24.5),
                circ(23.0, 72.0, 24.0, 24.5),
                circ(23.0, 144.0, 24.0, 24.5),
                circ(23.0, 216.0, 24.0, 24.5),
                circ(23.0, 288.0, 24.0, 24.5),
            ]))
        elif shape == nwStatusShape.STAR:
            path.addPolygon(QPolygonF([
                circ(24.0, 0.0, 24.0, 24.5),
                circ(24.0, 144.0, 24.0, 24.5),
                circ(24.0, 288.0, 24.0, 24.5),
                circ(24.0, 72.0, 24.0, 24.5),
                circ(24.0, 216.0, 24.0, 24.5),
            ]))
            path.setFillRule(Qt.FillRule.WindingFill)
        elif shape == nwStatusShape.PACMAN:
            path.moveTo(24.0, 24.0)
            path.arcTo(2.0, 2.0, 44.0, 44.0, 40.0, 280.0)

        self._cache[shape] = path

        return path

# END Class _ShapeCache


# Create Singleton
_SHAPES = _ShapeCache()
