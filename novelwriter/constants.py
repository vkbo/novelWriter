"""
novelWriter – Constants
=======================

File History:
Created: 2019-04-28 [0.0.1]

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
from __future__ import annotations

from PyQt5.QtCore import QT_TRANSLATE_NOOP, QCoreApplication

from novelwriter.enum import (
    nwBuildFmt, nwComment, nwItemClass, nwItemLayout, nwOutline, nwStatusShape
)


def trConst(text: str) -> str:
    """Wrapper function for locally translating constants."""
    return QCoreApplication.translate("Constant", text)


class nwConst:

    # Date and Time Formats
    FMT_TSTAMP = "%Y-%m-%d %H:%M:%S"  # Default format
    FMT_FSTAMP = "%Y-%m-%d %H.%M.%S"  # FileName safe format
    FMT_DSTAMP = "%Y-%m-%d"           # Date only format

    # URLs
    URL_WEB      = "https://novelwriter.io"
    URL_DOCS     = "https://docs.novelwriter.io"
    URL_RELEASES = "https://releases.novelwriter.io"
    URL_CODE     = "https://github.com/vkbo/novelWriter"
    URL_REPORT   = "https://github.com/vkbo/novelWriter/issues"
    URL_HELP     = "https://github.com/vkbo/novelWriter/discussions"

    # Requests
    USER_AGENT = "Mozilla/5.0 (compatible; novelWriter (Python))"

    # Gui Settings
    STATUS_MSG_TIMEOUT = 15000  # milliseconds
    MAX_SEARCH_RESULT = 1000


class nwRegEx:

    FMT_EI = r"(?<![\w\\])(_)(?![\s_])(.+?)(?<![\s\\])(\1)(?!\w)"
    FMT_EB = r"(?<![\w\\])(\*{2})(?![\s\*])(.+?)(?<![\s\\])(\1)(?!\w)"
    FMT_ST = r"(?<![\w\\])(~{2})(?![\s~])(.+?)(?<![\s\\])(\1)(?!\w)"
    FMT_SC = r"(?i)(?<!\\)(\[[\/\!]?(?:b|i|s|u|m|sup|sub)\])"
    FMT_SV = r"(?i)(?<!\\)(\[(?:footnote):)(.+?)(?<!\\)(\])"


class nwShortcode:

    BOLD_O   = "[b]"
    BOLD_C   = "[/b]"
    ITALIC_O = "[i]"
    ITALIC_C = "[/i]"
    STRIKE_O = "[s]"
    STRIKE_C = "[/s]"
    ULINE_O  = "[u]"
    ULINE_C  = "[/u]"
    MARK_O   = "[m]"
    MARK_C   = "[/m]"
    SUP_O    = "[sup]"
    SUP_C    = "[/sup]"
    SUB_O    = "[sub]"
    SUB_C    = "[/sub]"

    FOOTNOTE_B = "[footnote:"

    COMMENT_STYLES = {
        nwComment.FOOTNOTE: "[footnote:{0}]",
        nwComment.COMMENT:  "[comment:{0}]",
    }


class nwHeaders:

    H_VALID = ("H0", "H1", "H2", "H3", "H4")
    H_LEVEL = {"H0": 0, "H1": 1, "H2": 2, "H3": 3, "H4": 4}
    H_SIZES = {0: 2.50, 1: 2.00, 2: 1.75, 3: 1.50, 4: 1.25}


class nwFiles:

    # Config Files
    CONF_FILE   = "novelwriter.conf"
    RECENT_FILE = "recentProjects.json"
    RECENT_PATH = "recentPaths.json"

    # Project Root Files
    PROJ_FILE   = "nwProject.nwx"
    PROJ_LOCK   = "nwProject.lock"
    TOC_TXT     = "ToC.txt"

    # Project Meta Files
    BUILDS_FILE = "builds.json"
    INDEX_FILE  = "index.json"
    OPTS_FILE   = "options.json"
    DICT_FILE   = "userdict.json"
    SESS_FILE   = "sessions.jsonl"


class nwKeyWords:

    TAG_KEY    = "@tag"
    POV_KEY    = "@pov"
    FOCUS_KEY  = "@focus"
    CHAR_KEY   = "@char"
    PLOT_KEY   = "@plot"
    TIME_KEY   = "@time"
    WORLD_KEY  = "@location"
    OBJECT_KEY = "@object"
    ENTITY_KEY = "@entity"
    CUSTOM_KEY = "@custom"

    # Set of Valid Keys
    VALID_KEYS = {
        TAG_KEY, POV_KEY, FOCUS_KEY, CHAR_KEY, PLOT_KEY, TIME_KEY,
        WORLD_KEY, OBJECT_KEY, ENTITY_KEY, CUSTOM_KEY
    }

    # Map from Keys to Item Class
    KEY_CLASS = {
        POV_KEY:    nwItemClass.CHARACTER,
        FOCUS_KEY:  nwItemClass.CHARACTER,
        CHAR_KEY:   nwItemClass.CHARACTER,
        PLOT_KEY:   nwItemClass.PLOT,
        TIME_KEY:   nwItemClass.TIMELINE,
        WORLD_KEY:  nwItemClass.WORLD,
        OBJECT_KEY: nwItemClass.OBJECT,
        ENTITY_KEY: nwItemClass.ENTITY,
        CUSTOM_KEY: nwItemClass.CUSTOM,
    }


class nwLists:

    USER_CLASSES = [
        nwItemClass.CHARACTER,
        nwItemClass.PLOT,
        nwItemClass.WORLD,
        nwItemClass.TIMELINE,
        nwItemClass.OBJECT,
        nwItemClass.ENTITY,
        nwItemClass.CUSTOM,
    ]


class nwLabels:

    CLASS_NAME = {
        nwItemClass.NO_CLASS:  QT_TRANSLATE_NOOP("Constant", "None"),
        nwItemClass.NOVEL:     QT_TRANSLATE_NOOP("Constant", "Novel"),
        nwItemClass.PLOT:      QT_TRANSLATE_NOOP("Constant", "Plot"),
        nwItemClass.CHARACTER: QT_TRANSLATE_NOOP("Constant", "Characters"),
        nwItemClass.WORLD:     QT_TRANSLATE_NOOP("Constant", "Locations"),
        nwItemClass.TIMELINE:  QT_TRANSLATE_NOOP("Constant", "Timeline"),
        nwItemClass.OBJECT:    QT_TRANSLATE_NOOP("Constant", "Objects"),
        nwItemClass.ENTITY:    QT_TRANSLATE_NOOP("Constant", "Entities"),
        nwItemClass.CUSTOM:    QT_TRANSLATE_NOOP("Constant", "Custom"),
        nwItemClass.ARCHIVE:   QT_TRANSLATE_NOOP("Constant", "Archive"),
        nwItemClass.TEMPLATE:  QT_TRANSLATE_NOOP("Constant", "Templates"),
        nwItemClass.TRASH:     QT_TRANSLATE_NOOP("Constant", "Trash"),
    }
    CLASS_ICON = {
        nwItemClass.NO_CLASS:  "cls_none",
        nwItemClass.NOVEL:     "cls_novel",
        nwItemClass.PLOT:      "cls_plot",
        nwItemClass.CHARACTER: "cls_character",
        nwItemClass.WORLD:     "cls_world",
        nwItemClass.TIMELINE:  "cls_timeline",
        nwItemClass.OBJECT:    "cls_object",
        nwItemClass.ENTITY:    "cls_entity",
        nwItemClass.CUSTOM:    "cls_custom",
        nwItemClass.ARCHIVE:   "cls_archive",
        nwItemClass.TEMPLATE:  "cls_template",
        nwItemClass.TRASH:     "cls_trash",
    }
    LAYOUT_NAME = {
        nwItemLayout.NO_LAYOUT: QT_TRANSLATE_NOOP("Constant", "None"),
        nwItemLayout.DOCUMENT:  QT_TRANSLATE_NOOP("Constant", "Novel Document"),
        nwItemLayout.NOTE:      QT_TRANSLATE_NOOP("Constant", "Project Note"),
    }
    ITEM_DESCRIPTION = {
        "none":     QT_TRANSLATE_NOOP("Constant", "None"),
        "root":     QT_TRANSLATE_NOOP("Constant", "Root Folder"),
        "folder":   QT_TRANSLATE_NOOP("Constant", "Folder"),
        "document": QT_TRANSLATE_NOOP("Constant", "Novel Document"),
        "doc_h1":   QT_TRANSLATE_NOOP("Constant", "Novel Title Page"),
        "doc_h2":   QT_TRANSLATE_NOOP("Constant", "Novel Chapter"),
        "doc_h3":   QT_TRANSLATE_NOOP("Constant", "Novel Scene"),
        "doc_h4":   QT_TRANSLATE_NOOP("Constant", "Novel Section"),
        "note":     QT_TRANSLATE_NOOP("Constant", "Project Note"),
    }
    KEY_NAME = {
        nwKeyWords.TAG_KEY:    QT_TRANSLATE_NOOP("Constant", "Tag"),
        nwKeyWords.POV_KEY:    QT_TRANSLATE_NOOP("Constant", "Point of View"),
        nwKeyWords.FOCUS_KEY:  QT_TRANSLATE_NOOP("Constant", "Focus"),
        nwKeyWords.CHAR_KEY:   QT_TRANSLATE_NOOP("Constant", "Characters"),
        nwKeyWords.PLOT_KEY:   QT_TRANSLATE_NOOP("Constant", "Plot"),
        nwKeyWords.TIME_KEY:   QT_TRANSLATE_NOOP("Constant", "Timeline"),
        nwKeyWords.WORLD_KEY:  QT_TRANSLATE_NOOP("Constant", "Locations"),
        nwKeyWords.OBJECT_KEY: QT_TRANSLATE_NOOP("Constant", "Objects"),
        nwKeyWords.ENTITY_KEY: QT_TRANSLATE_NOOP("Constant", "Entities"),
        nwKeyWords.CUSTOM_KEY: QT_TRANSLATE_NOOP("Constant", "Custom"),
    }
    OUTLINE_COLS = {
        nwOutline.TITLE:  QT_TRANSLATE_NOOP("Constant", "Title"),
        nwOutline.LEVEL:  QT_TRANSLATE_NOOP("Constant", "Level"),
        nwOutline.LABEL:  QT_TRANSLATE_NOOP("Constant", "Document"),
        nwOutline.LINE:   QT_TRANSLATE_NOOP("Constant", "Line"),
        nwOutline.CCOUNT: QT_TRANSLATE_NOOP("Constant", "Chars"),
        nwOutline.WCOUNT: QT_TRANSLATE_NOOP("Constant", "Words"),
        nwOutline.PCOUNT: QT_TRANSLATE_NOOP("Constant", "Pars"),
        nwOutline.POV:    QT_TRANSLATE_NOOP("Constant", "POV"),
        nwOutline.FOCUS:  QT_TRANSLATE_NOOP("Constant", "Focus"),
        nwOutline.CHAR:   KEY_NAME[nwKeyWords.CHAR_KEY],
        nwOutline.PLOT:   KEY_NAME[nwKeyWords.PLOT_KEY],
        nwOutline.WORLD:  KEY_NAME[nwKeyWords.WORLD_KEY],
        nwOutline.TIME:   KEY_NAME[nwKeyWords.TIME_KEY],
        nwOutline.OBJECT: KEY_NAME[nwKeyWords.OBJECT_KEY],
        nwOutline.ENTITY: KEY_NAME[nwKeyWords.ENTITY_KEY],
        nwOutline.CUSTOM: KEY_NAME[nwKeyWords.CUSTOM_KEY],
        nwOutline.SYNOP:  QT_TRANSLATE_NOOP("Constant", "Synopsis"),
    }
    BUILD_FMT = {
        nwBuildFmt.ODT:    QT_TRANSLATE_NOOP("Constant", "Open Document (.odt)"),
        nwBuildFmt.FODT:   QT_TRANSLATE_NOOP("Constant", "Flat Open Document (.fodt)"),
        nwBuildFmt.HTML:   QT_TRANSLATE_NOOP("Constant", "novelWriter HTML (.html)"),
        nwBuildFmt.NWD:    QT_TRANSLATE_NOOP("Constant", "novelWriter Markup (.txt)"),
        nwBuildFmt.STD_MD: QT_TRANSLATE_NOOP("Constant", "Standard Markdown (.md)"),
        nwBuildFmt.EXT_MD: QT_TRANSLATE_NOOP("Constant", "Extended Markdown (.md)"),
        nwBuildFmt.J_HTML: QT_TRANSLATE_NOOP("Constant", "JSON + novelWriter HTML (.json)"),
        nwBuildFmt.J_NWD:  QT_TRANSLATE_NOOP("Constant", "JSON + novelWriter Markup (.json)"),
    }
    BUILD_EXT = {
        nwBuildFmt.ODT:    ".odt",
        nwBuildFmt.FODT:   ".fodt",
        nwBuildFmt.HTML:   ".html",
        nwBuildFmt.NWD:    ".txt",
        nwBuildFmt.STD_MD: ".md",
        nwBuildFmt.EXT_MD: ".md",
        nwBuildFmt.J_HTML: ".json",
        nwBuildFmt.J_NWD:  ".json",
    }
    SHAPES_PLAIN = {
        nwStatusShape.SQUARE:   QT_TRANSLATE_NOOP("Constant", "Square"),
        nwStatusShape.TRIANGLE: QT_TRANSLATE_NOOP("Constant", "Triangle"),
        nwStatusShape.NABLA:    QT_TRANSLATE_NOOP("Constant", "Nabla"),
        nwStatusShape.DIAMOND:  QT_TRANSLATE_NOOP("Constant", "Diamond"),
        nwStatusShape.PENTAGON: QT_TRANSLATE_NOOP("Constant", "Pentagon"),
        nwStatusShape.HEXAGON:  QT_TRANSLATE_NOOP("Constant", "Hexagon"),
        nwStatusShape.STAR:     QT_TRANSLATE_NOOP("Constant", "Star"),
        nwStatusShape.PACMAN:   QT_TRANSLATE_NOOP("Constant", "Pacman"),
    }
    SHAPES_CIRCLE = {
        nwStatusShape.CIRCLE_Q: QT_TRANSLATE_NOOP("Constant", "1/4 Circle"),
        nwStatusShape.CIRCLE_H: QT_TRANSLATE_NOOP("Constant", "Half Circle"),
        nwStatusShape.CIRCLE_T: QT_TRANSLATE_NOOP("Constant", "3/4 Circle"),
        nwStatusShape.CIRCLE:   QT_TRANSLATE_NOOP("Constant", "Full Circle"),
    }
    SHAPES_BARS = {
        nwStatusShape.BARS_1: QT_TRANSLATE_NOOP("Constant", "1 Bar"),
        nwStatusShape.BARS_2: QT_TRANSLATE_NOOP("Constant", "2 Bars"),
        nwStatusShape.BARS_3: QT_TRANSLATE_NOOP("Constant", "3 Bars"),
        nwStatusShape.BARS_4: QT_TRANSLATE_NOOP("Constant", "4 Bars"),
    }
    SHAPES_BLOCKS = {
        nwStatusShape.BLOCK_1: QT_TRANSLATE_NOOP("Constant", "1 Block"),
        nwStatusShape.BLOCK_2: QT_TRANSLATE_NOOP("Constant", "2 Blocks"),
        nwStatusShape.BLOCK_3: QT_TRANSLATE_NOOP("Constant", "3 Blocks"),
        nwStatusShape.BLOCK_4: QT_TRANSLATE_NOOP("Constant", "4 Blocks"),
    }
    FILE_FILTERS = {
        "*.txt": QT_TRANSLATE_NOOP("Constant", "Text files"),
        "*.md":  QT_TRANSLATE_NOOP("Constant", "Markdown files"),
        "*.nwd": QT_TRANSLATE_NOOP("Constant", "novelWriter files"),
        "*.csv": QT_TRANSLATE_NOOP("Constant", "CSV files"),
        "*":     QT_TRANSLATE_NOOP("Constant", "All files"),
    }
    UNIT_NAME = {
        "mm": QT_TRANSLATE_NOOP("Constant", "Millimetres"),
        "cm": QT_TRANSLATE_NOOP("Constant", "Centimetres"),
        "in": QT_TRANSLATE_NOOP("Constant", "Inches"),
    }
    UNIT_SCALE = {
        "mm": 1.0,
        "cm": 10.0,
        "in": 25.4,
    }
    PAPER_NAME = {
        "A4":     QT_TRANSLATE_NOOP("Constant", "A4"),
        "A5":     QT_TRANSLATE_NOOP("Constant", "A5"),
        "A6":     QT_TRANSLATE_NOOP("Constant", "A6"),
        "Legal":  QT_TRANSLATE_NOOP("Constant", "US Legal"),
        "Letter": QT_TRANSLATE_NOOP("Constant", "US Letter"),
        "Custom": QT_TRANSLATE_NOOP("Constant", "Custom"),
    }
    PAPER_SIZE = {
        "A4":     (210.0, 297.0),
        "A5":     (148.0, 210.0),
        "A6":     (105.0, 148.0),
        "Legal":  (215.9, 355.6),
        "Letter": (215.9, 279.4),
        "Custom": (-1.0, -1.0),
    }


class nwHeadFmt:

    BR         = "{BR}"
    TITLE      = "{Title}"
    CH_NUM     = "{Chapter}"
    CH_WORD    = "{Chapter:Word}"
    CH_ROMU    = "{Chapter:URoman}"
    CH_ROML    = "{Chapter:LRoman}"
    SC_NUM     = "{Scene}"
    SC_ABS     = "{Scene:Abs}"
    CHAR_POV   = "{Char:POV}"
    CHAR_FOCUS = "{Char:Focus}"

    PAGE_HEADERS = [
        TITLE, CH_NUM, CH_WORD, CH_ROMU, CH_ROML, SC_NUM, SC_ABS,
        CHAR_POV, CHAR_FOCUS
    ]

    # ODT Document Page Header
    ODT_PROJECT = "{Project}"
    ODT_AUTHOR = "{Author}"
    ODT_PAGE = "{Page}"
    ODT_AUTO = "{Project} / {Author} / {Page}"


class nwQuotes:
    """Allowed quotation marks.
    Source: https://en.wikipedia.org/wiki/Quotation_mark
    """
    SYMBOLS = {
        "\u0027": QT_TRANSLATE_NOOP("Constant", "Straight single quotation mark"),
        "\u0022": QT_TRANSLATE_NOOP("Constant", "Straight double quotation mark"),

        "\u2018": QT_TRANSLATE_NOOP("Constant", "Left single quotation mark"),
        "\u2019": QT_TRANSLATE_NOOP("Constant", "Right single quotation mark"),
        "\u201a": QT_TRANSLATE_NOOP("Constant", "Single low-9 quotation mark"),
        "\u201b": QT_TRANSLATE_NOOP("Constant", "Single high-reversed-9 quotation mark"),
        "\u201c": QT_TRANSLATE_NOOP("Constant", "Left double quotation mark"),
        "\u201d": QT_TRANSLATE_NOOP("Constant", "Right double quotation mark"),
        "\u201e": QT_TRANSLATE_NOOP("Constant", "Double low-9 quotation mark"),
        "\u201f": QT_TRANSLATE_NOOP("Constant", "Double high-reversed-9 quotation mark"),
        "\u2e42": QT_TRANSLATE_NOOP("Constant", "Double low-reversed-9 quotation mark"),

        "\u2039": QT_TRANSLATE_NOOP("Constant", "Single left-pointing angle quotation mark"),
        "\u203a": QT_TRANSLATE_NOOP("Constant", "Single right-pointing angle quotation mark"),
        "\u00ab": QT_TRANSLATE_NOOP("Constant", "Double left-pointing angle quotation mark"),
        "\u00bb": QT_TRANSLATE_NOOP("Constant", "Double right-pointing angle quotation mark"),

        "\u300c": QT_TRANSLATE_NOOP("Constant", "Left corner bracket"),
        "\u300d": QT_TRANSLATE_NOOP("Constant", "Right corner bracket"),
        "\u300e": QT_TRANSLATE_NOOP("Constant", "Left white corner bracket"),
        "\u300f": QT_TRANSLATE_NOOP("Constant", "Right white corner bracket"),
    }


class nwUnicode:
    """Supported unicode character constants and their HTML equivalents."""
    # Unicode Constants
    # =================

    # Quotation Marks
    U_QUOT   = "\u0022"  # Quotation mark
    U_APOS   = "\u0027"  # Apostrophe
    U_LAQUO  = "\u00ab"  # Left-pointing double angle quotation mark
    U_RAQUO  = "\u00bb"  # Right-pointing double angle quotation mark
    U_LSQUO  = "\u2018"  # Left single quotation mark
    U_RSQUO  = "\u2019"  # Right single quotation mark
    U_SBQUO  = "\u201a"  # Single low-9 quotation mark
    U_SUQUO  = "\u201b"  # Single high-reversed-9 quotation mark
    U_LDQUO  = "\u201c"  # Left double quotation mark
    U_RDQUO  = "\u201d"  # Right double quotation mark
    U_BDQUO  = "\u201e"  # Double low-9 quotation mark
    U_UDQUO  = "\u201f"  # Double high-reversed-9 quotation mark
    U_LSAQUO = "\u2039"  # Single left-pointing angle quotation mark
    U_RSAQUO = "\u203a"  # Single right-pointing angle quotation mark
    U_BDRQUO = "\u2e42"  # Double low-reversed-9 quotation mark
    U_LCQUO  = "\u300c"  # Left corner bracket
    U_RCQUO  = "\u300d"  # Right corner bracket
    U_LWCQUO = "\u300e"  # Left white corner bracket
    U_RWCQUO = "\u300f"  # Right white corner bracket

    # Punctuation
    U_FGDASH = "\u2012"  # Figure dash
    U_ENDASH = "\u2013"  # Short dash
    U_EMDASH = "\u2014"  # Long dash
    U_HBAR   = "\u2015"  # Horizontal bar
    U_HELLIP = "\u2026"  # Ellipsis
    U_MAPOS  = "\u02bc"  # Modifier letter single apostrophe
    U_PRIME  = "\u2032"  # Prime
    U_DPRIME = "\u2033"  # Double prime

    # Spaces and Lines
    U_NBSP   = "\u00a0"  # Non-breaking space
    U_THSP   = "\u2009"  # Thin space
    U_THNBSP = "\u202f"  # Thin non-breaking space
    U_ENSP   = "\u2002"  # Short (en) space
    U_EMSP   = "\u2003"  # Long (em) space
    U_MMSP   = "\u205f"  # Medium mathematical space
    U_LSEP   = "\u2028"  # Line separator
    U_PSEP   = "\u2029"  # Paragraph separator

    # Symbols
    U_CHECK  = "\u2714"  # Heavy check mark
    U_CROSS  = "\u2715"  # Heavy cross mark
    U_BULL   = "\u2022"  # List bullet
    U_TRBULL = "\u2023"  # Triangle bullet
    U_HYBULL = "\u2043"  # Hyphen bullet
    U_FLOWER = "\u2055"  # Flower punctuation mark
    U_PERMIL = "\u2030"  # Per mille sign
    U_DEGREE = "\u00b0"  # Degree symbol
    U_MINUS  = "\u2212"  # Minus sign
    U_TIMES  = "\u00d7"  # Multiplication sign
    U_DIVIDE = "\u00f7"  # Division sign

    # Arrows
    U_UTRI   = "\u25b2"  # Up-pointing triangle
    U_UTRIS  = "\u25b4"  # Up-pointing triangle, small
    U_RTRI   = "\u25b6"  # Right-pointing triangle
    U_RTRIS  = "\u25b8"  # Right-pointing triangle, small
    U_DTRI   = "\u25bc"  # Down-pointing triangle
    U_DTRIS  = "\u25be"  # Down-pointing triangle, small
    U_LTRI   = "\u25c0"  # Left-pointing triangle
    U_LTRIS  = "\u25c2"  # Left-pointing triangle, small

    # HTML Equivalents
    # ================

    # Quotes
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
    H_RWCQUO = "&#12303;"

    # Punctuation
    H_FGDASH = "&#8210;"
    H_ENDASH = "&ndash;"
    H_EMDASH = "&mdash;"
    H_HBAR   = "&#8213;"
    H_HELLIP = "&hellip;"
    H_MAPOS  = "&#700;"
    H_PRIME  = "&prime;"
    H_DPRIME = "&#8243;"

    # Spaces
    H_NBSP   = "&nbsp;"
    H_THSP   = "&thinsp;"
    H_THNBSP = "&#8239;"
    H_ENSP   = "&ensp;"
    H_EMSP   = "&emsp;"

    # Symbols
    H_CHECK  = "&#10004;"
    H_CROSS  = "&#10005;"
    H_BULL   = "&bull;"
    H_TRBULL = "&#8227;"
    H_HYBULL = "&hybull;"
    H_FLOWER = "&#8277;"
    H_PERMIL = "&#8240;"
    H_DEGREE = "&deg;"
    H_MINUS  = "&minus;"
    H_TIMES  = "&times;"
    H_DIVIDE = "&divide;"

    # Arrows
    H_UTRI   = "&#9650;"
    H_UTRIS  = "&#9652;"
    H_RTRI   = "&#9654;"
    H_RTRIS  = "&#9656;"
    H_DTRI   = "&#9660;"
    H_DTRIS  = "&#9662;"
    H_LTRI   = "&#9664;"
    H_LTRIS  = "&#9666;"


class nwHtmlUnicode():

    U_TO_H = {
        # Quotes
        nwUnicode.U_QUOT:   nwUnicode.H_QUOT,
        nwUnicode.U_APOS:   nwUnicode.H_APOS,
        nwUnicode.U_LAQUO:  nwUnicode.H_LAQUO,
        nwUnicode.U_RAQUO:  nwUnicode.H_RAQUO,
        nwUnicode.U_LSQUO:  nwUnicode.H_LSQUO,
        nwUnicode.U_RSQUO:  nwUnicode.H_RSQUO,
        nwUnicode.U_SBQUO:  nwUnicode.H_SBQUO,
        nwUnicode.U_SUQUO:  nwUnicode.H_SUQUO,
        nwUnicode.U_LDQUO:  nwUnicode.H_LDQUO,
        nwUnicode.U_RDQUO:  nwUnicode.H_RDQUO,
        nwUnicode.U_BDQUO:  nwUnicode.H_BDQUO,
        nwUnicode.U_UDQUO:  nwUnicode.H_UDQUO,
        nwUnicode.U_LSAQUO: nwUnicode.H_LSAQUO,
        nwUnicode.U_RSAQUO: nwUnicode.H_RSAQUO,
        nwUnicode.U_BDRQUO: nwUnicode.H_BDRQUO,
        nwUnicode.U_LCQUO:  nwUnicode.H_LCQUO,
        nwUnicode.U_RCQUO:  nwUnicode.H_RCQUO,
        nwUnicode.U_LWCQUO: nwUnicode.H_LWCQUO,
        nwUnicode.U_RWCQUO: nwUnicode.H_RWCQUO,

        # Punctuation
        nwUnicode.U_FGDASH: nwUnicode.H_FGDASH,
        nwUnicode.U_ENDASH: nwUnicode.H_ENDASH,
        nwUnicode.U_EMDASH: nwUnicode.H_EMDASH,
        nwUnicode.U_HBAR:   nwUnicode.H_HBAR,
        nwUnicode.U_HELLIP: nwUnicode.H_HELLIP,
        nwUnicode.U_MAPOS:  nwUnicode.H_MAPOS,
        nwUnicode.U_PRIME:  nwUnicode.H_PRIME,
        nwUnicode.U_DPRIME: nwUnicode.H_DPRIME,

        # Spaces
        nwUnicode.U_NBSP:   nwUnicode.H_NBSP,
        nwUnicode.U_THSP:   nwUnicode.H_THSP,
        nwUnicode.U_THNBSP: nwUnicode.H_THNBSP,
        nwUnicode.U_ENSP:   nwUnicode.H_ENSP,
        nwUnicode.U_EMSP:   nwUnicode.H_EMSP,

        # Symbols
        nwUnicode.U_CHECK:  nwUnicode.H_CHECK,
        nwUnicode.U_CROSS:  nwUnicode.H_CROSS,
        nwUnicode.U_BULL:   nwUnicode.H_BULL,
        nwUnicode.U_TRBULL: nwUnicode.H_TRBULL,
        nwUnicode.U_HYBULL: nwUnicode.H_HYBULL,
        nwUnicode.U_FLOWER: nwUnicode.H_FLOWER,
        nwUnicode.U_PERMIL: nwUnicode.H_PERMIL,
        nwUnicode.U_DEGREE: nwUnicode.H_DEGREE,
        nwUnicode.U_MINUS:  nwUnicode.H_MINUS,
        nwUnicode.U_TIMES:  nwUnicode.H_TIMES,
        nwUnicode.U_DIVIDE: nwUnicode.H_DIVIDE,
    }
