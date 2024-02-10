"""
novelWriter – Enums
===================

File History:
Created: 2018-11-02 [0.0.1]

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

from enum import Enum


class nwItemType(Enum):

    NO_TYPE = 0
    ROOT    = 1
    FOLDER  = 2
    FILE    = 3

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
    TEMPLATE  = 10
    TRASH     = 11

# END Enum nwItemClass


class nwItemLayout(Enum):

    NO_LAYOUT = 0
    DOCUMENT  = 1
    NOTE      = 2

# END Enum nwItemLayout


class nwComment(Enum):

    PLAIN    = 0
    SYNOPSIS = 1
    SHORT    = 2

# END Enum nwComment


class nwTrinary(Enum):

    NEGATIVE = -1
    NEUTRAL  = 0
    POSITIVE = 1

# END Enum nwTrinary


class nwDocMode(Enum):

    VIEW = 0
    EDIT = 1

# END Enum nwDocMode


class nwDocAction(Enum):

    NO_ACTION = 0
    UNDO      = 1
    REDO      = 2
    CUT       = 3
    COPY      = 4
    PASTE     = 5
    MD_ITALIC = 6
    MD_BOLD   = 7
    MD_STRIKE = 8
    S_QUOTE   = 9
    D_QUOTE   = 10
    SEL_ALL   = 11
    SEL_PARA  = 12
    BLOCK_H1  = 13
    BLOCK_H2  = 14
    BLOCK_H3  = 15
    BLOCK_H4  = 16
    BLOCK_COM = 17
    BLOCK_IGN = 18
    BLOCK_TXT = 19
    BLOCK_TTL = 20
    BLOCK_UNN = 21
    REPL_SNG  = 22
    REPL_DBL  = 23
    RM_BREAKS = 24
    ALIGN_L   = 25
    ALIGN_C   = 26
    ALIGN_R   = 27
    INDENT_L  = 28
    INDENT_R  = 29
    SC_ITALIC = 30
    SC_BOLD   = 31
    SC_STRIKE = 32
    SC_ULINE  = 33
    SC_SUP    = 34
    SC_SUB    = 35

# END Enum nwDocAction


class nwDocInsert(Enum):

    NO_INSERT = 0
    QUOTE_LS  = 1
    QUOTE_RS  = 2
    QUOTE_LD  = 3
    QUOTE_RD  = 4
    SYNOPSIS  = 5
    SHORT     = 6
    NEW_PAGE  = 7
    VSPACE_S  = 8
    VSPACE_M  = 9
    LIPSUM    = 10

# END Enum nwDocInsert


class nwView(Enum):

    EDITOR  = 0
    PROJECT = 1
    NOVEL   = 2
    OUTLINE = 3

# END Enum nwView


class nwWidget(Enum):

    TREE    = 1
    EDITOR  = 2
    VIEWER  = 3
    OUTLINE = 4

# END Enum nwWidget


class nwOutline(Enum):

    TITLE  = 0
    LEVEL  = 1
    LABEL  = 2
    LINE   = 3
    CCOUNT = 4
    WCOUNT = 5
    PCOUNT = 6
    POV    = 7
    FOCUS  = 8
    CHAR   = 9
    PLOT   = 10
    TIME   = 11
    WORLD  = 12
    OBJECT = 13
    ENTITY = 14
    CUSTOM = 15
    SYNOP  = 16

# END Enum nwOutline


class nwBuildFmt(Enum):

    ODT    = 0
    FODT   = 1
    HTML   = 2
    NWD    = 3
    STD_MD = 4
    EXT_MD = 5
    J_HTML = 6
    J_NWD  = 7

# END Enum nwBuildFormat
