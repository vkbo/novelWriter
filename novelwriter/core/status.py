"""
novelWriter – Project Item Status Class
=======================================
Data class for the status/importance settings of a project item

File History:
Created:   2019-05-19 [0.1.3]
Rewritten: 2022-04-05 [1.7a0]

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import random
import logging
import novelwriter

from lxml import etree

from PyQt5.QtGui import QIcon, QPixmap, QColor

from novelwriter.common import checkInt, minmax, simplified

logger = logging.getLogger(__name__)


class NWStatus():

    STATUS = 1
    IMPORT = 2

    def __init__(self, type):

        self._type = type
        self._store = {}
        self._reverse = {}
        self._default = None

        self._iconSize = novelwriter.CONFIG.pxInt(32)
        pixmap = QPixmap(self._iconSize, self._iconSize)
        pixmap.fill(QColor(100, 100, 100))
        self._defaultIcon = QIcon(pixmap)

        if self._type == self.STATUS:
            self._prefix = "s"
        elif self._type == self.IMPORT:
            self._prefix = "i"
        else:
            raise Exception("This is a bug!")

        return

    def write(self, key, name, cols, count=None):
        """Add or update a status entry. If the key is invalid, a new
        key is generated.
        """
        if not self._isKey(key):
            key = self._newKey()
        if not isinstance(cols, tuple):
            cols = (100, 100, 100)
        if len(cols) != 3:
            cols = (100, 100, 100)

        pixmap = QPixmap(self._iconSize, self._iconSize)
        pixmap.fill(QColor(*cols))

        name = simplified(name)
        if count is None:
            count = self._store[key]["count"] if key in self._store else 0

        self._store[key] = {
            "name": name,
            "icon": QIcon(pixmap),
            "cols": cols,
            "count": count,
        }
        self._reverse[name] = key

        if self._default is None:
            self._default = key

        return key

    def remove(self, key):
        """Remove an entry in the list, but not if the count is larger
        than 0.
        """
        if key not in self._store:
            return False
        if self._store[key]["count"] > 0:
            return False

        del self._reverse[self._store[key]["name"]]
        del self._store[key]

        keys = list(self._store.keys())
        if key == self._default:
            if len(keys) > 0:
                self._default = keys[0]
            else:
                self._default = None

        return True

    def check(self, value):
        """Check the key against the stored status names.
        """
        if self._isKey(value) and value in self._store:
            return value
        elif value in self._reverse:
            return self._reverse[value]
        elif self._default is not None:
            return self._default
        else:
            return ""

    def name(self, key):
        """Return the name associated with a given key.
        """
        if key in self._store:
            return self._store[key]["name"]
        elif self._default is not None:
            return self._store[self._default]["name"]
        else:
            return ""

    def cols(self, key):
        """Return the colours associated with a given key.
        """
        if key in self._store:
            return self._store[key]["cols"]
        elif self._default is not None:
            return self._store[self._default]["cols"]
        else:
            return (100, 100, 100)

    def count(self, key):
        """Return the count associated with a given key.
        """
        if key in self._store:
            return self._store[key]["count"]
        elif self._default is not None:
            return self._store[self._default]["count"]
        else:
            return 0

    def icon(self, key):
        """Return the icon associated with a given key.
        """
        if key in self._store:
            return self._store[key]["icon"]
        elif self._default is not None:
            return self._store[self._default]["icon"]
        else:
            return self._defaultIcon

    def reorder(self, order):
        """Reorder the items according to list.
        """
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

    def resetCounts(self):
        """Clear the counts of references to the status entries.
        """
        for key in self._store:
            self._store[key]["count"] = 0
        return

    def increment(self, key):
        """Increment the counter for a given entry.
        """
        if key in self._store:
            self._store[key]["count"] += 1
        return

    def packXML(self, xParent):
        """Pack the status entries into an XML object for saving to the
        main project file.
        """
        for key, data in self._store.items():
            xSub = etree.SubElement(xParent, "entry", attrib={
                "key":   key,
                "count": str(data["count"]),
                "red":   str(data["cols"][0]),
                "green": str(data["cols"][1]),
                "blue":  str(data["cols"][2]),
            })
            xSub.text = data["name"]

        return True

    def unpackXML(self, xParent):
        """Unpack an XML tree and set the class values.
        """
        self._store = {}
        self._reverse = {}
        self._default = None

        for xChild in xParent:
            key   = xChild.attrib.get("key", None)
            name  = xChild.text.strip()
            count = max(checkInt(xChild.attrib.get("count", 0), 0), 0)
            red   = minmax(checkInt(xChild.attrib.get("red", 100), 100), 0, 255)
            green = minmax(checkInt(xChild.attrib.get("green", 100), 100), 0, 255)
            blue  = minmax(checkInt(xChild.attrib.get("blue", 100), 100), 0, 255)
            self.write(key, name, (red, green, blue), count)

        return True

    ##
    #  Internal Functions
    ##

    def _newKey(self):
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

    def _isKey(self, value):
        """Check if a value is a key or not.
        """
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

    ##
    #  Iterator Bits
    ##

    def __len__(self):
        return len(self._store)

    def __getitem__(self, key):
        return self._store[key]

    def __iter__(self):
        return iter(self._store)

    def keys(self):
        return self._store.keys()

    def items(self):
        return self._store.items()

    def values(self):
        return self._store.values()

# END Class NWStatus
