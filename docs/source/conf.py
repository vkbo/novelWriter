#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config
#

# -- Imports -----------------------------------------------------------------

import os
import time
import sphinx_rtd_theme  # noqa: F401

# -- Project Information -----------------------------------------------------

project = "novelWriter"
copyright = "2018–2021, Veronica Berglyd Olsen"
author = "Veronica Berglyd Olsen"

# The short X.Y version
version = "1.5.5"
# The full version, including alpha/beta/rc tags
release = "1.5.5"

# -- General Configuration ---------------------------------------------------

os.environ["TZ"] = "Europe/Oslo"
time.tzset()

# needs_sphinx = "1.0"
extensions = [
    "sphinx_rtd_theme",
]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
today_fmt = "%A, %d %B %Y at %H:%M"
language = None
exclude_patterns = []
pygments_style = None

# -- Options for HTML Output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_logo = "images/novelwriter.png"
html_theme_options = {
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "includehidden": True,
    "titles_only": False,
    "logo_only": True,
}

html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]

# -- Options for HTMLHelp Output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "novelWriterDoc"

# -- Options for LaTeX Output ------------------------------------------------

latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
    "preamble": (
        "\\usepackage[utf8]{inputenc}\n"
        "\\DeclareUnicodeCharacter{2212}{\\textendash}\n"
    ),
    "figure_align": "htbp",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [(
    master_doc, "manual.tex", "novelWriter Documentation",
    author, "manual"
)]

# -- Options for Man Page Output ---------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(
    master_doc, "novelwriter", "novelWriter Documentation", [author], 1
)]

# -- Options for Texinfo Output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [(
    master_doc, "novelWriter", "novelWriter Documentation", author,
    "novelWriter", "Markdown-like editor for novels.", "Miscellaneous"
)]

# -- Options for EPub Output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
# epub_identifier = ""

# A unique identification for the text.
# epub_uid = ""

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]
