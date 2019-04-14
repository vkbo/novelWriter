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

    NONE        = 0
    ROOT        = 1
    FOLDER      = 2
    FILE        = 3
    TRASHFOLDER = 4
    TRASHFILE   = 5

# END Enum nwItemType

class nwItemClass(Enum):

    NONE      = 0
    NOVEL     = 1
    CHAPTER   = 2
    SCENE     = 3
    PLOT      = 4
    CHARACTER = 6
    WORLD     = 6
    TIMELINE  = 7
    OBJECT    = 8

# END Enum nwItemClass

class nwItemAction(Enum):

    NONE        = 0
    ADD_ROOT    = 1
    ADD_FOLDER  = 2
    ADD_FILE    = 3
    MOVE_UP     = 4
    MOVE_DOWN   = 5
    MOVE_TO     = 6
    MOVE_TRASH  = 7
    SPLIT       = 8
    MERGE       = 9
    DELETE      = 10
    DELETE_ROOT = 11
    EMPTY_TRASH = 12

# END Enum nwItemAction
