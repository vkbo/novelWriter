# -*- coding: utf-8 -*-
"""novelWriter Enums

 novelWriter – Enums
=====================
 All enum values

 File History:
 Created: 2018-11-02 [0.0.1]

"""

from enum import Enum

class nwItemType(Enum):

    NONE   = 0
    ROOT   = 1
    FOLDER = 2
    FILE   = 3

# END Enum nwItemType

class nwItemClass(Enum):

    NONE      = 0
    NOVEL     = 1
    CHAPTER   = 2
    SCENE     = 3
    CHARACTER = 4
    WORLD     = 5

# END Enum nwItemClass
