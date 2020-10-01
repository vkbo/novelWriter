# -*- coding: utf-8 -*-
"""novelWriter Enums

 novelWriter – Enums
=====================
 All enum values

 File History:
 Created: 2018-11-02 [0.0.1]

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

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
    ARCHIVE   = 9
    TRASH     = 10

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
    EMPH      = 6
    STRONG    = 7
    STRIKE    = 8
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
    REPL_SNG  = 24
    REPL_DBL  = 25

# END Enum nwDocAction

class nwDocInsert(Enum):

    NO_INSERT     = 0
    HARD_BREAK    = 1
    NB_SPACE      = 2
    THIN_SPACE    = 3
    THIN_NB_SPACE = 4
    SHORT_DASH    = 5
    LONG_DASH     = 6
    ELLIPSIS      = 7
    QUOTE_LS      = 8
    QUOTE_RS      = 9
    QUOTE_LD      = 10
    QUOTE_RD      = 11
    MODAPOS_S     = 12

# END Enum nwDocInsert

class nwAlert(Enum):

    INFO  = 0
    WARN  = 1
    ERROR = 2
    BUG   = 3

# END Enum nwAlert

class nwOutline(Enum):

    TITLE  = 0
    LEVEL  = 1
    LABEL  = 2
    LINE   = 3
    CCOUNT = 4
    WCOUNT = 5
    PCOUNT = 6
    POV    = 7
    CHAR   = 8
    PLOT   = 9
    TIME   = 10
    WORLD  = 11
    OBJECT = 12
    ENTITY = 13
    CUSTOM = 14
    SYNOP  = 15

# END Enum nwOutline
