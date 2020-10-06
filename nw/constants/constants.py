# -*- coding: utf-8 -*-
"""novelWriter Constants

 novelWriter – Constants
=========================
 Constants for translating flags and enums to text

 File History:
 Created: 2019-04-28 [0.0.1]

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

from nw.constants.enum import nwItemClass, nwItemLayout, nwOutline

class nwConst():

    tStampFmt = "%Y-%m-%d %H:%M:%S" # Default format
    fStampFmt = "%Y-%m-%d %H.%M.%S" # FileName safe format
    dStampFmt = "%Y-%m-%d"          # Date only format

    maxDepth     = 30       # Maximum folder depth of a project
    maxDocSize   = 5000000  # Maxium size of a single document
    maxBuildSize = 10000000 # Maxium size of a project build

# END Class nwConst

class nwRegEx():

    FMT_I  = r"(?<![\w\\])(_)(?![\s_])(.+?)(?<![\s\\])(\1)(?!\w)"
    FMT_B  = r"(?<![\w\\])([\*]{2})(?![\s\*])(.+?)(?<![\s\\])(\1)(?!\w)"
    FMT_ST = r"(?<![\w\\])([~]{2})(?![\s~])(.+?)(?<![\s\\])(\1)(?!\w)"

# END Class nwRegEx

class nwFiles():

    PROJ_FILE   = "nwProject.nwx"
    PROJ_DICT   = "wordlist.txt"
    PROJ_LOCK   = "nwProject.lock"
    TOC_TXT     = "ToC.txt"
    TOC_JSON    = "ToC.json"
    SESS_STATS  = "sessionStats.log"
    INDEX_FILE  = "tagsIndex.json"
    OPTS_FILE   = "guiOptions.json"
    RECENT_FILE = "recentProjects.json"
    BUILD_CACHE = "prevBuild.json"

# END Class nwFiles

class nwKeyWords:

    TAG_KEY    = "@tag"
    POV_KEY    = "@pov"
    CHAR_KEY   = "@char"
    PLOT_KEY   = "@plot"
    TIME_KEY   = "@time"
    WORLD_KEY  = "@location"
    OBJECT_KEY = "@object"
    ENTITY_KEY = "@entity"
    CUSTOM_KEY = "@custom"

# END Class nwKeyWords

class nwLabels():

    CLASS_NAME = {
        nwItemClass.NO_CLASS  : "None",
        nwItemClass.NOVEL     : "Novel",
        nwItemClass.PLOT      : "Plot",
        nwItemClass.CHARACTER : "Characters",
        nwItemClass.WORLD     : "Locations",
        nwItemClass.TIMELINE  : "Timeline",
        nwItemClass.OBJECT    : "Objects",
        nwItemClass.ENTITY    : "Entity",
        nwItemClass.CUSTOM    : "Custom",
        nwItemClass.ARCHIVE   : "Outtakes",
        nwItemClass.TRASH     : "Trash",
    }
    CLASS_FLAG = {
        nwItemClass.NO_CLASS  : "0",
        nwItemClass.NOVEL     : "N",
        nwItemClass.PLOT      : "P",
        nwItemClass.CHARACTER : "C",
        nwItemClass.WORLD     : "L",
        nwItemClass.TIMELINE  : "T",
        nwItemClass.OBJECT    : "O",
        nwItemClass.ENTITY    : "E",
        nwItemClass.CUSTOM    : "X",
        nwItemClass.ARCHIVE   : "U",
        nwItemClass.TRASH     : "R",
    }
    CLASS_ICON = {
        nwItemClass.NO_CLASS  : "cls_none",
        nwItemClass.NOVEL     : "cls_novel",
        nwItemClass.PLOT      : "cls_plot",
        nwItemClass.CHARACTER : "cls_character",
        nwItemClass.WORLD     : "cls_world",
        nwItemClass.TIMELINE  : "cls_timeline",
        nwItemClass.OBJECT    : "cls_object",
        nwItemClass.ENTITY    : "cls_entity",
        nwItemClass.CUSTOM    : "cls_custom",
        nwItemClass.ARCHIVE   : "cls_archive",
        nwItemClass.TRASH     : "cls_trash",
    }
    LAYOUT_NAME = {
        nwItemLayout.NO_LAYOUT  : "None",
        nwItemLayout.TITLE      : "Title Page",
        nwItemLayout.BOOK       : "Book",
        nwItemLayout.PAGE       : "Plain Page",
        nwItemLayout.PARTITION  : "Partition",
        nwItemLayout.UNNUMBERED : "Unnumbered",
        nwItemLayout.CHAPTER    : "Chapter",
        nwItemLayout.SCENE      : "Scene",
        nwItemLayout.NOTE       : "Note",
    }
    LAYOUT_FLAG = {
        nwItemLayout.NO_LAYOUT  : "Xo",
        nwItemLayout.TITLE      : "Tt",
        nwItemLayout.BOOK       : "Bk",
        nwItemLayout.PAGE       : "Pg",
        nwItemLayout.PARTITION  : "Pt",
        nwItemLayout.UNNUMBERED : "Un",
        nwItemLayout.CHAPTER    : "Ch",
        nwItemLayout.SCENE      : "Sc",
        nwItemLayout.NOTE       : "Nt",
    }
    KEY_NAME = {
        nwKeyWords.TAG_KEY    : "Tag",
        nwKeyWords.POV_KEY    : "Point of View",
        nwKeyWords.CHAR_KEY   : "Characters",
        nwKeyWords.PLOT_KEY   : "Plot",
        nwKeyWords.TIME_KEY   : "Time",
        nwKeyWords.WORLD_KEY  : "Locations",
        nwKeyWords.OBJECT_KEY : "Objects",
        nwKeyWords.ENTITY_KEY : "Entities",
        nwKeyWords.CUSTOM_KEY : "Custom",
    }
    OUTLINE_COLS = {
        nwOutline.TITLE  : "Title",
        nwOutline.LEVEL  : "Level",
        nwOutline.LABEL  : "Document",
        nwOutline.LINE   : "Line",
        nwOutline.CCOUNT : "Chars",
        nwOutline.WCOUNT : "Words",
        nwOutline.PCOUNT : "Pars",
        nwOutline.POV    : "POV",
        nwOutline.CHAR   : KEY_NAME[nwKeyWords.CHAR_KEY],
        nwOutline.PLOT   : KEY_NAME[nwKeyWords.PLOT_KEY],
        nwOutline.TIME   : KEY_NAME[nwKeyWords.TIME_KEY],
        nwOutline.WORLD  : KEY_NAME[nwKeyWords.WORLD_KEY],
        nwOutline.OBJECT : KEY_NAME[nwKeyWords.OBJECT_KEY],
        nwOutline.ENTITY : KEY_NAME[nwKeyWords.ENTITY_KEY],
        nwOutline.CUSTOM : KEY_NAME[nwKeyWords.CUSTOM_KEY],
        nwOutline.SYNOP  : "Synopsis",
    }

# END Class nwLabels

class nwQuotes():
    """Allowed quotation marks.
    Source: https://en.wikipedia.org/wiki/Quotation_mark
    """

    SYMBOLS = {
        "\u0027" : "Straight single quotation mark",
        "\u0022" : "Straight double quotation mark",

        "\u2018" : "Left single quotation mark",
        "\u2019" : "Right single quotation mark",
        "\u201a" : "Single low-9 quotation mark",
        "\u201b" : "Single high-reversed-9 quotation mark",
        "\u201c" : "Left double quotation mark",
        "\u201d" : "Right double quotation mark",
        "\u201e" : "Double low-9 quotation mark",
        "\u201f" : "Double high-reversed-9 quotation mark",
        "\u2e42" : "Double low-reversed-9 quotation mark",

        "\u2039" : "Single left-pointing angle quotation mark",
        "\u203a" : "Single right-pointing angle quotation mark",
        "\u00ab" : "Left-pointing double angle quotation mark",
        "\u00bb" : "Right-pointing double angle quotation mark",

        "\u300c" : "Left corner bracket",
        "\u300d" : "Right corner bracket",
        "\u300e" : "Left white corner bracket",
        "\u300f" : "Right white corner bracket",
    }

# END Class nwQuotes

class nwUnicode:
    """Supported unicode character constants and translation maps for HTML.
    """

    # Unicode Constants
    # =================

    ## Quotation Marks
    U_QUOT   = "\u0022" # Quotation mark
    U_APOS   = "\u0027" # Apostrophe
    U_LAQUO  = "\u00ab" # Left-pointing double angle quotation mark
    U_RAQUO  = "\u00bb" # Right-pointing double angle quotation mark
    U_LSQUO  = "\u2018" # Left single quotation mark
    U_RSQUO  = "\u2019" # Right single quotation mark
    U_SBQUO  = "\u201a" # Single low-9 quotation mark
    U_SUQUO  = "\u201b" # Single high-reversed-9 quotation mark
    U_LDQUO  = "\u201c" # Left double quotation mark
    U_RDQUO  = "\u201d" # Right double quotation mark
    U_BDQUO  = "\u201e" # Double low-9 quotation mark
    U_UDQUO  = "\u201f" # Double high-reversed-9 quotation mark
    U_LSAQUO = "\u2039" # Single left-pointing angle quotation mark
    U_RSAQUO = "\u203a" # Single right-pointing angle quotation mark
    U_BDRQUO = "\u2e42" # Double low-reversed-9 quotation mark
    U_LCQUO  = "\u300c" # Left corner bracket
    U_RCQUO  = "\u300d" # Right corner bracket
    U_LWCQUO = "\u300e" # Left white corner bracket
    U_RECQUO = "\u300f" # Right white corner bracket

    ## Punctuation
    U_ENDASH = "\u2013" # Short dash
    U_EMDASH = "\u2014" # Long dash
    U_HELLIP = "\u2026" # Ellipsis
    U_MAPOSS = "\u02bc" # Modifier letter single apostrophe

    ## Spaces and Lines
    U_NBSP   = "\u00a0" # Non-breaking space
    U_THNSP  = "\u2009" # Thin space
    U_THNBSP = "\u202f" # Thin non-breaking space
    U_LSEP   = "\u2028" # Line separator
    U_PSEP   = "\u2029" # Paragraph separator

    ## Symbols
    U_CHECK  = "\u2714" # Heavy check mark
    U_MULT   = "\u2715" # Multiplication x
    U_BULL   = "\u2022" # List bullet

    ## Arrows
    U_UTRI   = "\u25b2" # Up-pointing triangle
    U_UTRIS  = "\u25b4" # Up-pointing triangle, small
    U_RTRI   = "\u25b6" # Right-pointing triangle
    U_RTRIS  = "\u25b8" # Right-pointing triangle, small
    U_DTRI   = "\u25bc" # Down-pointing triangle
    U_DTRIS  = "\u25be" # Down-pointing triangle, small
    U_LTRI   = "\u25c0" # Left-pointing triangle
    U_LTRIS  = "\u25c2" # Left-pointing triangle, small

    # HTML Equivalents
    # ================

    ## Quotes
    H_QUOT   = "&quot;"
    H_APOS   = "&#39;"
    H_LAQUO  = "&laquo;"
    H_RAQUO  = "&raquo;"
    H_LSQUO  = "&lsquo;"
    H_RSQUO  = "&rsquo;"
    H_SBQUO  = "&sbquo;"
    H_SUQUO  = "&#8219;"
    H_LDQUO  = "&ldquo;"
    H_RDQUO  = "&rdquo;"
    H_BDQUO  = "&bdquo;"
    H_UDQUO  = "&#8223;"
    H_LSAQUO = "&lsaquo;"
    H_RSAQUO = "&rsaquo;"
    H_BDRQUO = "&#11842;"
    H_LCQUO  = "&#12300;"
    H_RCQUO  = "&#12301;"
    H_LWCQUO = "&#12302;"
    H_LWCQUO = "&#12302;"

    ## Punctuation
    H_ENDASH = "&ndash;"
    H_EMDASH = "&mdash;"
    H_HELLIP = "&hellip;"
    H_MAPOSS = "&#700;"

    ## Spaces
    H_NBSP   = "&nbsp;"
    H_THNSP  = "&thinsp;"
    H_THNBSP = "&#8239;"

    ## Symbols
    H_CHECK  = "&#10004;"
    H_MULT   = "&#10005;"
    H_BULL   = "&bull;"

    ## Arrows
    H_UTRI   = "&#9650;"
    H_UTRIS  = "&#9652;"
    H_RTRI   = "&#9654;"
    H_RTRIS  = "&#9656;"
    H_DTRI   = "&#9660;"
    H_DTRIS  = "&#9662;"
    H_LTRI   = "&#9664;"
    H_LTRIS  = "&#9666;"

# END Class nwUnicode
