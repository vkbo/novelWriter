#
# Configuration file for the Sphinx documentation builder.
# Documentation: http://www.sphinx-doc.org/en/master/config
#

# -- Imports -----------------------------------------------------------------

import os
import time
import datetime

# -- Project Information -----------------------------------------------------

project = "novelWriter"
copyright = f"{datetime.date.today().year}, Veronica Berglyd Olsen"
author = "Veronica Berglyd Olsen"

initFile = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir,
    "novelwriter", "__init__.py"
)
with open(initFile) as inFile:
    for aLine in inFile:
        if aLine.startswith("__version__"):
            release = aLine.split('"')[1].strip()
            break
    else:
        release = "unknown"

version = release.split("-")[0]

# -- General Configuration ---------------------------------------------------

os.environ["TZ"] = "Europe/Oslo"
time.tzset()

needs_sphinx = "4.0"
extensions = []
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
today_fmt = "%A, %d %B %Y at %H:%M"
language = "en"
exclude_patterns = []

# -- Options for HTML Output -------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "light_logo": "novelwriter-light.png",
    "dark_logo": "novelwriter-dark.png",
    "navigation_with_keys": True,
    "dark_css_variables": {
        "admonition-font-size": "92%",
    },
    "light_css_variables": {
        "admonition-font-size": "92%",
    },
}
html_title = f"<div style='text-align: center'>Documentation Version {release}</div>"
pygments_style = "tango"
pygments_dark_style = "native"

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
