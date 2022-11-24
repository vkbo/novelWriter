.. _a_export:

***********************
Building the Manuscript
***********************

You can at any time build a manuscript, an outline of your notes, or any other type of document
from the text in your project. All of this is handled by the :guilabel:`Build Novel Project` tool.
You can activate it from the sidebar, the :guilabel:`Tools` menu, or by pressing :kbd:`F5`.

.. note::
   This tool is scheduled to receive a full update in novelWriter 2.1, adding many new features
   requested by users. See the `2.1 Milestone <https://github.com/vkbo/novelWriter/milestone/43>`_
   for an overview.


.. _a_export_headers:

Header Formatting
=================

The titles for the five types of headings (the chapter headings come in a numbered and unnumbered
version) of story structure can be formatted collectively in the build tool. This is done through
a series of keyword–replace steps. They are all on the format ``%keyword%``.

``%title%``
   This keyword will always be replaced with the title text you put after the ``#`` characters in
   your document.

``%ch%``
   This will be replaced by a chapter number. The number is incremented by one each time the build
   tool sees a new heading of level two in a document, unless the heading formatting code has the
   added ``!``. In the latter case, the counter is *not* incremented. This is useful for for
   instance Prologue and Epilogue chapters.

``%chw%``
   Behaves like ``%ch%``, but the number is represented as a number word. You can select between a
   number of different languages.

``%chi%``
   Begaves like ``%ch%``, but represented as a lower case Roman number from 1 to 4999.

``%chI%``
   Behaves like ``%ch%``, but represented as an upper case Roman number from 1 to 4999.

``%sc%``
   This is the number counter equivalent for scenes. These are incremented each time a heading of
   level three is encountered, but reset to 1 each time a chapter is encountered. They can thus be
   used for counting scenes within a chapter.

``%sca%``
   Behaves like ``%sc%``, but the number is *not* reset to 1 for each chapter. Instead it runs from
   1 from the beginning of the novel to produce an absolute scene count.

``\\``
   This inserts a line break within the title.

.. note::
   Header formatting only applies to novel documents. Headings in notes will be left as-is.

**Example**

* The format ``%title%`` just reproduces the title you set in the document.
* The format ``Chapter %ch%: %title%`` produces something like "Chapter 1: My Chapter Title".
* The format ``Scene %ch%.%sc%`` produces something like "Scene 1.2" for scene 2 in chapter 1.


.. _a_export_scenes:

Scene Separators
================

If you don't want any titles for your scenes (or for your sections if you have them), you can leave
the formatting boxes empty. If so, an empty paragraph will be inserted between the scenes or
sections instead, resulting in a gap in the text.

Alternatively, if you want a separator between them, like the common ``* * *``, you can enter the
desired separator text in the formatting box. In fact, if the format is a piece of static text, it
will always be treated as a separator.


.. _a_export_files:

File Selection
==============

Which documents and notes are selected for the build can be controlled from the options on the left
side of the dialog window. In addition, you can select to include the synopsis comments, regular
comments, keywords, and even exclude the body text itself if you just want an outline.

.. tip::
   If you for instance want to export a document with an outline of the novel, you can enable
   keywords and synopsis export and disable body text, thus getting a document with each heading
   followed by the tags and references and the synopsis.

If you need to exclude specific documents from your exports, like draft documents or documents you
want to take out of your manuscript, but don't want to delete, you can set the documents as
"inactive" in the project tree. :guilabel:`Build Novel Project` tool has a switch to collectively
exclude inactive documents.


.. _a_export_print:

Printing
========

The print button allows you to print the content in the preview window. You can either print to one
of your system's printers, or print directly to a file as PDF. You can also print to file from the
regular print dialog. The direct to file option is just a shortcut.

.. note::
   The paper format should in all cases default to whatever your system default is. Of you want to
   change it, you have to select it from the :guilabel:`Print Preview`` dialog.


.. _a_export_formats:

Export Formats
==============

Currently, six formats are supported.

Open Document Format
   The Build tool can produce either an ``.odt`` file, or an ``.fodt`` file. The latter is just a
   flat version of the document format as a single XML file. Most rich text editors support the
   former, and a few the latter.

novelWriter HTML
   The HTML format writes a single ``.htm`` file with minimal style formatting. The HTML document
   is suitable for further processing by document conversion tools like Pandoc, for importing in
   word processors, or for printing from browser.

novelWriter Markdown
   This is simply a concatenation of the project documents selected by the filters. The documents
   are stacked together in the order they appear in the project tree, with comments, tags, etc.
   included if they are selected. This is a useful format for exporting the project for later
   import back into novelWriter.

Standard/GitHub Markdown
   The Markdown format comes in both Standard and GitHub flavour. The *only* difference in terms of
   novelWriter functionality is the support for strikethrough text, which is not supported by the
   Standard flavour, but *is* supported by the GitHub flavour.


.. _a_export_options:

Additional Formats
==================

In addition to the above document formats, the novelWriter HTML and Markdown formats can also be
wrapped in a JSON file. These files will have a meta data entry and a body entry. For HTML, also
the accompanying css styles are included.

The text body is saved in a two-level list. The outer list contains one entry per document, in the
order they appear in the project tree. Each document is then split up into a list as well, with one
entry per paragraph it contains.

These files are mainly intended for scripted post-processing for those who want that option. A JSON
file can be imported directly into a Python dict object or a PHP array, to mentions a few options.
