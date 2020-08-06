.. _a_export:

##################
Exporting Projects
##################

The novelWriter project can be exported in various formats using the build tool available from :menuselection:`Project --> Build Project` or by pressing :kbd:`F5`.

*****************
Header Formatting
*****************

The titles for the four levels of story structure can be formatted collectively in the export tool.
This is done through a series of keyword–replace steps.

The keyword ``%title%`` will always be replaced by the text you put after the ``#`` characters in your document.

The keywords ``%ch%`` and ``%chw%`` is replaced by a number, or a number word, respectively.
You can also use ``%chi%`` or ``%chI%`` for lower and upper case Roman numbers.
The number is incremented by one each time the build tool sees a new heading of level two in a file with layout "Chapter".
If the file has layout "Unnumbered", the counter is *not* incremented.
The latter is useful for for instance Prologue and Epilogue chapters.

Likewise, the keywords ``%sc%`` and ``%sca%`` are number counters for scene files.
These are incremented each time a heading of level three is encountered.
The former keyword is reset to one for each new chapter, while the latter is not reset but counts from first scene encountered in the project.

If you want to insert a line break in your title format, add two backslashes ``\\``.

.. note::
   Header formatting only applies to novel files.
   Headings in note files will will be left as-is, but heading levels 1 through 4 are converted to the correct heading level in the respective output formats.

****************
Scene Separators
****************

If you don't want any titles for your scenes (and for your sections if you have them), you can leave the boxes empty, and an empty paragraph will be inserted between the scenes or sections instead.
Alternatively, if you want a separator between them, like the common "\*\*\*", you can also enter that in the box.
In fact, if the format is a piece of static text, it will always be treated as a separator.

**************
File Selection
**************

Which files are selected for export can be controlled from the options on the left side of the dialog window.
The switch for "Include novel files" will select any file that isn't classified as a note.
That is, files with layout "Book", "Page", "Partition", "Chapet", "Unnumbered", or "Scene".
The switch for "Include note files" will select any file that is a note.
That is, files with layout "Note".
This is allows for exporting just the novel, just your notes, or both, as you see fit.

In addition, you can select to export the synopsis comments, regular comments, keywords, and even exclude the body text itself.
If you for instance want to export a document with an outline of the novel, you can enable keywords and synopsis export and disable body text, thus getting a document with each heading followed by the tags and references and the synopsis.

If you need to exclude specific files from your exports, like draft files or files you want to take out of your build, but don't want to delete, you can uncheck the "Include when building project" option for each file in the project tree.
An included file has a checkmark after the status icon in the "Flags" column.
The "Build Novel Project" tool has a switch to ignore this flag if you need to collectively override these settings.

**************
Export Formats
**************

Currently, six formats are supported for exporting.

OpenDocument Format
===================

This is produces an open document ``.odt`` file.
The document produced has very little formatting, and may require further editing afterwards.
For a better formatted office document, you may get a better result with exporting to HTML and the import that HTML document in your office word processor.

PDF Format
==========

The PDF export is just a shortcut for print to file.

novelWriter HTML
================

The HTML export format writes a single ``.htm`` file with minimal style formatting.
The exported HTML file is suitable for further processing by document conversion tools like Pandoc, for importing in word processors, or for printing from browser.

novelWriter Markdown
====================

This is simply a concatenation of the files selected by the filters.
The files in the project are stacked together in the order they appear in the tree view, with comments, tags, etc. included if they are selected.
This is a useful format for exporting the project for later import back into novelWriter.

Standard Markdown
=================

If you have Qt 5.14 or higher, the option to export to plain Markdown is available.
This feature uses Qt's own Markdown export feature.

Plain Text
==========

The plain text export format writes a simple ``.txt`` file without any formatting at all.

*************************
Additional Export Options
*************************

In addition to the above document formats, the novelWriter HTML and Markdown formats can also be wrapped in a JSON file.
The files will have a meta data entry and a body entry.
For HTML, also the accompanying css styles are exported.

The text body is saved in a two-level list.
The outer list contains one entry per exported file, in the order they appear in the project tree.
Each file is then split up into a lst as well, with one entry per line.

These files are mainly intended for scripted post-processing for those who want that option.
A JSON file can be imported directly into a Python dict object or a PHP array, to mentions a few options.
