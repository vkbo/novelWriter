"""
novelWriter – Enums
===================

File History:
Created: 2018-11-02 [0.0.1]

This file is a part of novelWriter
Copyright (C) 2018 Veronica Berglyd Olsen and novelWriter contributors

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


class nwItemLayout(Enum):

    NO_LAYOUT = 0
    DOCUMENT  = 1
    NOTE      = 2


class nwComment(Enum):

    PLAIN    = 0
    IGNORE   = 1
    SYNOPSIS = 2
    SHORT    = 3
    NOTE     = 4
    FOOTNOTE = 5
    COMMENT  = 6
    STORY    = 7


class nwChange(Enum):

    CREATE = 0
    UPDATE = 1
    DELETE = 2


class nwDocMode(Enum):

    VIEW = 0
    EDIT = 1


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
    MD_MARK   = 9
    S_QUOTE   = 10
    D_QUOTE   = 11
    SEL_ALL   = 12
    SEL_PARA  = 13
    BLOCK_H1  = 14
    BLOCK_H2  = 15
    BLOCK_H3  = 16
    BLOCK_H4  = 17
    BLOCK_COM = 18
    BLOCK_IGN = 19
    BLOCK_TXT = 20
    BLOCK_TTL = 21
    BLOCK_UNN = 22
    BLOCK_HSC = 23
    REPL_SNG  = 24
    REPL_DBL  = 25
    RM_BREAKS = 26
    ALIGN_L   = 27
    ALIGN_C   = 28
    ALIGN_R   = 29
    INDENT_L  = 30
    INDENT_R  = 31
    SC_ITALIC = 32
    SC_BOLD   = 33
    SC_STRIKE = 34
    SC_ULINE  = 35
    SC_MARK   = 36
    SC_SUP    = 37
    SC_SUB    = 38


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
    FOOTNOTE  = 11
    LINE_BRK  = 12


class nwView(Enum):

    EDITOR  = 0
    PROJECT = 1
    NOVEL   = 2
    OUTLINE = 3
    SEARCH  = 4


class nwFocus(Enum):

    TREE     = 1
    DOCUMENT = 2
    OUTLINE  = 3


class nwTheme(Enum):

    AUTO  = 0
    LIGHT = 1
    DARK  = 2


class nwOutline(Enum):

    TITLE   = 0
    LEVEL   = 1
    LABEL   = 2
    LINE    = 3
    STATUS  = 4
    CCOUNT  = 5
    WCOUNT  = 6
    PCOUNT  = 7
    POV     = 8
    FOCUS   = 9
    CHAR    = 10
    PLOT    = 11
    TIME    = 12
    WORLD   = 13
    OBJECT  = 14
    ENTITY  = 15
    CUSTOM  = 16
    STORY   = 17
    MENTION = 18
    SYNOP   = 19


class nwNovelExtra(Enum):

    HIDDEN = 0
    POV    = 1
    FOCUS  = 2
    PLOT   = 3


class nwBuildFmt(Enum):

    ODT    = 0
    FODT   = 1
    DOCX   = 2
    PDF    = 3
    HTML   = 4
    STD_MD = 5
    EXT_MD = 6
    NWD    = 7
    J_HTML = 8
    J_NWD  = 9


class nwStatusShape(Enum):

    SQUARE   = 0
    TRIANGLE = 1
    NABLA    = 2
    DIAMOND  = 3
    PENTAGON = 4
    HEXAGON  = 5
    STAR     = 6
    PACMAN   = 7
    CIRCLE_Q = 8
    CIRCLE_H = 9
    CIRCLE_T = 10
    CIRCLE   = 11
    BARS_1   = 12
    BARS_2   = 13
    BARS_3   = 14
    BARS_4   = 15
    BLOCK_1  = 16
    BLOCK_2  = 17
    BLOCK_3  = 18
    BLOCK_4  = 19

class nwVimMode(Enum):
    NORMAL = 0
    INSERT = 1
