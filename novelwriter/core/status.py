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

import logging
import random

from collections.abc import ItemsView, Iterable, Iterator, KeysView, ValuesView
from math import cos, pi, sin
from typing import TYPE_CHECKING, Literal

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QIcon, QPainter, QPainterPath, QPixmap, QColor, QPolygonF

from novelwriter import CONFIG
from novelwriter.common import minmax, simplified
from novelwriter.enum import nwStatusShape
from novelwriter.types import QtPaintAnitAlias, QtTransparent

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypeGuard  # Requires Python 3.10

logger = logging.getLogger(__name__)


class NWStatus:

    STATUS = 1
    IMPORT = 2

    def __init__(self, kind: Literal[1, 2]) -> None:

        self._type = kind
        self._store = {}
        self._default = None

        self._iPX = CONFIG.pxInt(24)
        self._defaultIcon = self._createIcon(100, 100, 100, nwStatusShape.SQUARE)

        if self._type == self.STATUS:
            self._prefix = "s"
        elif self._type == self.IMPORT:
            self._prefix = "i"
        else:
            raise Exception("This is a bug!")

        return

    def write(self, key: str | None, name: str, col: tuple, shape: nwStatusShape | str,
              count: int | None = None) -> str:
        """Add or update a status entry. If the key is invalid, a new
        key is generated.
        """
        if not self._isKey(key):
            key = self._newKey()
        if not isinstance(col, tuple):
            col = (100, 100, 100)
        if len(col) != 3:
            col = (100, 100, 100)

        cR = minmax(col[0], 0, 255)
        cG = minmax(col[1], 0, 255)
        cB = minmax(col[2], 0, 255)
        name = simplified(name)
        if not isinstance(shape, nwStatusShape):
            if shape in nwStatusShape.__members__:
                shape = nwStatusShape[shape]
            else:
                shape = nwStatusShape.SQUARE

        if count is None:
            count = self._store.get(key, {}).get("count", 0)

        self._store[key] = {
            "name": name,
            "icon": self._createIcon(cR, cG, cB, shape),
            "cols": (cR, cG, cB),
            "count": count,
            "shape": shape,
        }

        if self._default is None:
            self._default = key

        return key

    def remove(self, key: str) -> bool:
        """Remove an entry in the list, except if the count > 0."""
        if key not in self._store:
            return False
        if self._store[key]["count"] > 0:
            return False

        del self._store[key]

        keys = list(self._store.keys())
        if key == self._default:
            if len(keys) > 0:
                self._default = keys[0]
            else:
                self._default = None

        return True

    def check(self, value: str) -> str:
        """Check the key against the stored status names."""
        if self._isKey(value) and value in self._store:
            return value
        elif self._default is not None:
            return self._default
        return ""

    def name(self, key: str | None) -> str:
        """Return the name associated with a given key."""
        if key and key in self._store:
            return self._store[key]["name"]
        elif self._default is not None:
            return self._store[self._default]["name"]
        return ""

    def cols(self, key: str | None) -> tuple[int, int, int]:
        """Return the colours associated with a given key."""
        if key and key in self._store:
            return self._store[key]["cols"]
        elif self._default is not None:
            return self._store[self._default]["cols"]
        return 100, 100, 100

    def count(self, key: str | None) -> int:
        """Return the count associated with a given key."""
        if key and key in self._store:
            return self._store[key]["count"]
        elif self._default is not None:
            return self._store[self._default]["count"]
        return 0

    def icon(self, key: str | None) -> QIcon:
        """Return the icon associated with a given key."""
        if key and key in self._store:
            return self._store[key]["icon"]
        elif self._default is not None:
            return self._store[self._default]["icon"]
        return self._defaultIcon

    def reorder(self, order: list[str]) -> bool:
        """Reorder the items according to list."""
        if len(order) != len(self._store):
            logger.error("Length mismatch between new and old order")
            return False

        if order == list(self._store.keys()):
            return False

        store = {}
        for key in order:
            if key in self._store:
                store[key] = self._store[key]
            else:
                logger.error("Unknown key '%s' in order", key)
                return False

        self._store = store

        return True

    def resetCounts(self) -> None:
        """Clear the counts of references to the status entries."""
        for key in self._store:
            self._store[key]["count"] = 0
        return

    def increment(self, key: str | None) -> None:
        """Increment the counter for a given entry."""
        if key and key in self._store:
            self._store[key]["count"] += 1
        return

    def pack(self) -> Iterable[tuple[str, dict]]:
        """Pack the status entries into a dictionary."""
        for key, data in self._store.items():
            yield (data["name"], {
                "key":   key,
                "count": str(data["count"]),
                "red":   str(data["cols"][0]),
                "green": str(data["cols"][1]),
                "blue":  str(data["cols"][2]),
                "shape": data["shape"].name,
            })
        return

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

    def _createIcon(self, red: int, green: int, blue: int, shape: nwStatusShape) -> QIcon:
        """Generate an icon for a status label."""
        pixmap = QPixmap(48, 48)
        pixmap.fill(QtTransparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QtPaintAnitAlias)
        painter.fillPath(_SHAPES.getShape(shape), QColor(red, green, blue))
        painter.end()

        return QIcon(pixmap.scaled(
            self._iPX, self._iPX,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

    ##
    #  Iterator Bits
    ##

    def __len__(self) -> int:
        return len(self._store)

    def __getitem__(self, key: str) -> dict:
        return self._store[key]

    def __iter__(self) -> Iterator[dict]:
        return iter(self._store)

    def keys(self) -> KeysView[str]:
        return self._store.keys()

    def items(self) -> ItemsView[str, dict]:
        return self._store.items()

    def values(self) -> ValuesView[dict]:
        return self._store.values()

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
