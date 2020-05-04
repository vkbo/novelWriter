# -*- coding: utf-8 -*-
"""novelWriter Enums

 novelWriter – Enums
=====================
 All enum values

 File History:
 Created: 2018-11-02 [0.0.1]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
    BLOCK_H1  = 18
    BLOCK_H2  = 19
    BLOCK_H3  = 20
    BLOCK_H4  = 21
    BLOCK_COM = 22
    BLOCK_TXT = 23

# END Enum nwDocAction

class nwAlert(Enum):

    INFO  = 0
    WARN  = 1
    ERROR = 2
    BUG   = 3

# END Enum nwAlert

class nwOutline(Enum):

    TITLE  = 0
    HANDLE = 1
    LEVEL  = 2
    LABEL  = 3
    LINE   = 4
    CCOUNT = 5
    WCOUNT = 6
    PCOUNT = 7
    POV    = 8
    CHAR   = 9
    PLOT   = 10
    TIME   = 11
    WORLD  = 12
    OBJECT = 13
    ENTITY = 14
    CUSTOM = 15
    SYNOP  = 16

# END Enum nwOutline
