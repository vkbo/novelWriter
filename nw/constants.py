# -*- coding: utf-8 -*-
"""novelWriter Constants

 novelWriter – Constants
=========================
 Constants for translating flags and enums to text

 File History:
 Created: 2019-04-28 [0.0.1]

"""

from nw.enum import nwItemClass, nwItemLayout

class nwConst():

    tStampFmt = "%Y-%m-%d %H:%M:%S"

# END Class nwConst

class nwFiles():

    APP_ICON   = "novelWriter.svg"
    PROJ_FILE  = "nwProject.nwx"
    PROJ_DICT  = "wordlist.txt"
    SESS_INFO  = "sessionInfo.log"
    INDEX_FILE = "tagsIndex.json"
    EXPORT_OPT = "exportOptions.json"

# END Class nwFiles

class nwLabels():

    CLASS_NAME = {
        nwItemClass.NO_CLASS  : "None",
        nwItemClass.NOVEL     : "Novel",
        nwItemClass.PLOT      : "Plot",
        nwItemClass.CHARACTER : "Characters",
        nwItemClass.WORLD     : "Locations",
        nwItemClass.TIMELINE  : "Timeline",
        nwItemClass.OBJECT    : "Objects",
        nwItemClass.CUSTOM    : "Custom",
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
        nwItemClass.CUSTOM    : "X",
        nwItemClass.TRASH     : "R",
    }
    LAYOUT_NAME = {
        nwItemLayout.NO_LAYOUT  : "None",
        nwItemLayout.TITLE      : "Title Page",
        nwItemLayout.BOOK       : "Book",
        nwItemLayout.PAGE       : "Plain Page",
        nwItemLayout.PARTITION  : "Partition",
        nwItemLayout.UNNUMBERED : "Un-Numbered",
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

# END Class nwLabels

class nwQuotes():
    """Allowed quotation marks.
    Source: https://en.wikipedia.org/wiki/Quotation_mark
    """

    SYMBOLS = [
        "\u0022", # Quotation mark
        "\u0027", # Apostrophe
        "\u00ab", # Left-pointing double angle quotation mark
        "\u00bb", # Right-pointing double angle quotation mark
        "\u2018", # Left single quotation mark
        "\u2019", # Right single quotation mark
        "\u201a", # Single low-9 quotation mark
        "\u201b", # Single high-reversed-9 quotation mark
        "\u201c", # Left double quotation mark
        "\u201d", # Right double quotation mark
        "\u201e", # Double low-9 quotation mark
        "\u201f", # Double high-reversed-9 quotation mark
        "\u2039", # Single left-pointing angle quotation mark
        "\u203a", # Single right-pointing angle quotation mark
        "\u2e42", # Double low-reversed-9 quotation mark
        "\u300c", # Left corner bracket
        "\u300d", # Right corner bracket
        "\u300e", # Left white corner bracket
        "\u300f", # Right white corner bracket
    ]
    HTML = {
        "\u0022" : "&quot;",
        "\u0027" : "&#39;",
        "\u00ab" : "&laquo;",
        "\u00bb" : "&raquo;",
        "\u2018" : "&lsquo;",
        "\u2019" : "&rsquo;",
        "\u201a" : "&sbquo;",
        "\u201b" : "&#8219;",
        "\u201c" : "&ldquo;",
        "\u201d" : "&rdquo;",
        "\u201e" : "&bdquo;",
        "\u201f" : "&#8223;",
        "\u2039" : "&lsaquo;",
        "\u203a" : "&rsaquo;",
        "\u2e42" : "&#11842;",
        "\u300c" : "&#12300;",
        "\u300d" : "&#12301;",
        "\u300e" : "&#12302;",
        "\u300f" : "&#12303;",
    }

# END Class nwQuotes