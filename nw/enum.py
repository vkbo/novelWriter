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

    NO_TYPE = 0
    ROOT    = 1
    FOLDER  = 2
    FILE    = 3
    TRASH   = 4

# END Enum nwItemType

class nwItemClass(Enum):

    NO_CLASS  = 0
    NOVEL     = 1
    PLOT      = 2
    CHARACTER = 3
    WORLD     = 4
    TIMELINE  = 5
    OBJECT    = 6
    ENTITY    = 7
    CUSTOM    = 8
    TRASH     = 9

# END Enum nwItemClass

class nwItemLayout(Enum):

    NO_LAYOUT  = 0
    TITLE      = 1
    BOOK       = 2
    PAGE       = 3
    PARTITION  = 4
    UNNUMBERED = 5
    CHAPTER    = 6
    SCENE      = 7
    NOTE       = 8

# END Enum nwItemLayout

class nwDocAction(Enum):

    NO_ACTION = 0
    UNDO      = 1
    REDO      = 2
    CUT       = 3
    COPY      = 4
    PASTE     = 5
    BOLD      = 6
    ITALIC    = 7
    U_LINE    = 8
    S_QUOTE   = 9
    D_QUOTE   = 10
    SEL_ALL   = 11
    SEL_PARA  = 12
    FIND      = 13
    REPLACE   = 14
    GO_NEXT   = 15
    GO_PREV   = 16
    REPL_NEXT = 17

# END Enum nwDocAction

class nwAlert(Enum):

    INFO  = 0
    WARN  = 1
    ERROR = 2
    BUG   = 3

# END Enum nwAlert
