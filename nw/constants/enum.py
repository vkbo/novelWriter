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

    NO_ACTION  = 0
    UNDO       = 1
    REDO       = 2
    CUT        = 3
    COPY       = 4
    PASTE      = 5
    ITALIC     = 6
    BOLD       = 7
    BOLDITALIC = 8
    STRIKE     = 9
    S_QUOTE    = 10
    D_QUOTE    = 11
    SEL_ALL    = 12
    SEL_PARA   = 13
    FIND       = 14
    REPLACE    = 15
    GO_NEXT    = 16
    GO_PREV    = 17
    REPL_NEXT  = 18
    BLOCK_H1   = 19
    BLOCK_H2   = 20
    BLOCK_H3   = 21
    BLOCK_H4   = 22
    BLOCK_COM  = 23
    BLOCK_TXT  = 24
    REPL_SNG   = 25
    REPL_DBL   = 26

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
