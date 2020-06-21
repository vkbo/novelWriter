***************
User Interface
***************

The user interface is kept as simple as possible to avoid distractions when writing.
The main window contains a tree view pane with the entire structure of the project, and a small details panel below it to display additional information about the currently selected item.

Edit View
=========

Editing a document can be done by either double-clicking on it, or hitting the return key when a file is selected.
This will open the document editor, which uses a simplified markdown format, described in the section below.

The document currently being edited can also be viewed in parallel in a right hand side view pane.
To view a document, simply press :kbd:`Ctrl-R`, or select a file and go to :menuselection:`Document --> View Document` in the menu.
The document viewed does not need to be the same document currently being edited.
If you are viewing the same document as the one you're editing, pressing :kbd:`Ctrl-R` again will update the document with your last changes.

References to tags can be opened in the view pane from the document editor by moving the cursor to a reference to a tag and hitting :kbd:`Ctrl-Enter`.
In the view panel, the references become clickable links, and the "Referenced By" panel at the bottom will show links to all documents referring back to it.

.. note::
   The "Referenced By" panel relies on an up-to-date index of the project.
   If anything is missing, or seems wrong, the index can always be rebuilt from :menuselection:`Tools --> Rebuild Index` or by pressing :kbd:`F9`.

Both the document editor and the viewer will show the label of the document as set in the Project Tree.
Optionally, the full project path to the file can be shown.
This can be set the Preferences.

Clicking on the document title bar will select and reveal the file in the Project Tree, making it easier to find the project location of the file in a large project.

Markdown Format
===============

The document editor uses a simplified markdown format.
That is, it supports basic formatting like bold, italics and strikethrough, as well as four levels of headings.
The preference of novelWriter is to use `*` for wrapping emphasised text, but `_` is partially supported when typed, but not by the automatic formatting features and keyboard shortcuts.

In addition to these standard markdown features, the editor also allows for comments, that is text that is ignored by the word counter and not exported or, optionally, hidden in the document viewer.
If the first word of a comment is "Synopsis:" (with the colon), the comment is treated specially, and will show up in the Outline View.
The editor also has a minimal set of keywords used for setting tags and references between files.

.. csv-table:: Formatting Syntax
   :header: "Format", "Description"
   :widths: 15, 50

   "``# Title``",             "Heading level one. The space after the # is mandatory."
   "``## Title``",            "Heading level two. The space after the # is mandatory."
   "``### Title``",           "Heading level three. The space after the # is mandatory."
   "``#### Title``",          "Heading level four. The space after the # is mandatory."
   "``*text*``",              "The text is rendered as italicised text."
   "``**text**``",            "The text is rendered as bold text."
   "``***text***``",          "The text is rendered as bold italicised text."
   "``_text_``",              "Alternative format for italicised text."
   "``__text__``",            "Alternative format for bold text."
   "``~~text~~``",            "Strikethrough text."
   "``% text...``",           "A comment. The text is not exported by default, seen in viewer, or counted towards word counts."
   "``% Synopsis: text...``", "A synopsis comment. Shows up in the Synopsis column of the Outline View, but is otherwise treated as a comment."
   "``@keyword: value``",     "A keyword argument followed by a value, or a comma separated list of values."

The editor and viewer also supports markdown standard hard line breaks, and preserves non-breaking spaces.
A hard line break is achieved by leaving two or more spaces at the end of the line.
Alternatively, the user can press :kbd:`Ctrl-K, Return` to insert this.
A non-breaking space is inserted with :kbd:`Ctrl-K, Space`.

Thin spaces are also supported, and can be inserted with :kbd:`Ctrl-K, Shift-Space`, and the non-breaking version of it with :kbd:`Ctrl-K, Ctrl-Space`.

Both hard line breaks and non-breaking spaces are highlighted by the syntax highlighter as an alternate coloured background, depending on the selected theme.

Project Outline View
====================

The Project Outline View is available as the second tab on the right hand side of the main window marked "Outline".
The Outline View provides an overview of the novel structure, displaying a tree hierarchy of the elements of the novel, that is, the level 1 to 4 headings.

Various meta data and information extracted from tags can be displayed in columns in the Outline View.
To turn on or off specific columns, right click the header and select the columns you want to show.
The order of the columns can be rearranged by dragging them to a different position.

.. note::
   The "Title" columns cannot be disabled or moved.

The information viewed in teh Outline View is based on the Project Index.
While novelWriter does its best to keep the index up-to-date when content changes, you can always rebuild it manually by pressing :kbd:`F9`.

The Outline View itself can be regenerated by pressing :kbd:`F10`.
You can also enable automatic updating in the :menuselection:`Tools` menu, which will trigger an update whenever the index is updated.
You may want to disable this feature if your project is very large,

Synopsis Feature
================

The "Synopsis" column of the Outline View takes its information from a specially formatted comment.
In order to flag a comment as a Synopsis, add the word "Synopsis:" as the first word of the comment.
The ":" is required, and "synopsis" is not case sensitive.
If it is correctly formatted, the syntax highlighter will indicate this by altering the colour of the word.

.. note::
   Only one comment can be flagged as a synopsis comment for each heading.
   If multiple comments are flagged as a synopsis, the last one will be used.

Keyboard Shortcuts
==================

Most features are available as keyboard shortcuts.
These are as following:

.. csv-table:: Keyboard Shortcuts
   :header: "Shortcut", "Description"
   :widths: 15, 50

   ":kbd:`Alt-1`",           "Switch focus to tree view pane."
   ":kbd:`Alt-2`",           "Switch focus to document editor pane."
   ":kbd:`Alt-3`",           "Switch focus to document viewer pane."
   ":kbd:`Ctrl-.`",          "Correct word under cursor."
   ":kbd:`Ctrl-,`",          "Open the Preferences dialog."
   ":kbd:`Ctrl-/`",          "Change block format to comment."
   ":kbd:`Ctrl--`",          "Strikethrough selected text, or word under cursor."
   ":kbd:`Ctrl-0`",          "Remove block formatting for block under cursor."
   ":kbd:`Ctrl-1`",          "Change block format to header level 1."
   ":kbd:`Ctrl-2`",          "Change block format to header level 2."
   ":kbd:`Ctrl-3`",          "Change block format to header level 3."
   ":kbd:`Ctrl-4`",          "Change block format to header level 4."
   ":kbd:`Ctrl-A`",          "Select all text in document."
   ":kbd:`Ctrl-B`",          "Format selected text, or word under cursor, as bold."
   ":kbd:`Ctrl-C`",          "Copy selected text to clipboard."
   ":kbd:`Ctrl-D`",          "Wrap selected text, or word under cursor, in double quotes."
   ":kbd:`Ctrl-E`",          "If in tree view, edit a document or folder settings. (Same as :kbd:`F2`)"
   ":kbd:`Ctrl-F`",          "Open the search bar and search for selected word, if any is selected."
   ":kbd:`Ctrl-G`",          "Find next occurrence of word in current document. (Same as :kbd:`F3`)"
   ":kbd:`Ctrl-H`",          "Open the search and replace bar and search for selected word, if any is selected. (On Mac, this is :kbd:`Cmd-=`)"
   ":kbd:`Ctrl-I`",          "Format selected text, or word under cursor, as italic."
   ":kbd:`Ctrl-N`",          "Create new document."
   ":kbd:`Ctrl-O`",          "Open selected document."
   ":kbd:`Ctrl-Q`",          "Exit novelWriter."
   ":kbd:`Ctrl-R`",          "If in tree view, open a document for viewing. If editor pane has focus, open current document for viewing."
   ":kbd:`Ctrl-S`",          "Save the current document in the editor."
   ":kbd:`Ctrl-V`",          "Paste text from clipboard to cursor position."
   ":kbd:`Ctrl-W`",          "Close the current document in the editor."
   ":kbd:`Ctrl-X`",          "Cut selected text to clipboard."
   ":kbd:`Ctrl-Y`",          "Redo latest undo."
   ":kbd:`Ctrl-Z`",          "Undo latest changes."
   ":kbd:`Ctrl-F7`",         "Toggle spell checking."
   ":kbd:`Ctrl-F10`",        "Toggle automatic updating of project outline."
   ":kbd:`Ctrl-Del`",        "If in tree view, move a document to trash, or delete a folder."
   ":kbd:`Ctrl-Enter`",      "Open the tag or reference under the cursor in the view panel."
   ":kbd:`Ctrl-Shift-,`",    "Open the Project Settings dialog."
   ":kbd:`Ctrl-Shift-/`",    "Remove block formatting for block under cursor."
   ":kbd:`Ctrl-Shift-1`",    "Replace occurrence of word in current document, and search for next occurrence."
   ":kbd:`Ctrl-Shift-A`",    "Select all text in current paragraph."
   ":kbd:`Ctrl-Shift-B`",    "Format selected text, or word under cursor, as bold and italic."
   ":kbd:`Ctrl-Shift-D`",    "Wrap selected text, or word under cursor, in single quotes."
   ":kbd:`Ctrl-Shift-G`",    "Find previous occurrence of word in current document. (Same as :kbd:`Shift-F3`"
   ":kbd:`Ctrl-Shift-I`",    "Import text to the current document from a text file."
   ":kbd:`Ctrl-Shift-N`",    "Create new folder."
   ":kbd:`Ctrl-Shift-O`",    "Open a project."
   ":kbd:`Ctrl-Shift-R`",    "Close the document view pane."
   ":kbd:`Ctrl-Shift-S`",    "Save the current project."
   ":kbd:`Ctrl-Shift-W`",    "Close the current project."
   ":kbd:`Ctrl-Shift-Up`",   "Move item one step up in the tree view."
   ":kbd:`Ctrl-Shift-Down`", "Move item one step down in the tree view."
   ":kbd:`F1`",              "Open documentation. This just tries to send the documentation URL ti your browser."
   ":kbd:`F2`",              "If in tree view, edit a document or folder settings. (Same as :kbd:`Ctrl-E`)"
   ":kbd:`F3`",              "Find next occurrence of word in current document. (Same as :kbd:`Ctrl-G`)"
   ":kbd:`F5`",              "Open the Build Novel Project dialog."
   ":kbd:`F7`",              "Re-run spell checker."
   ":kbd:`F8`",              "Activate Zen Mode, hiding project tree and view panel."
   ":kbd:`F9`",              "Re-build project index."
   ":kbd:`F10`",             "Re-build project outline."
   ":kbd:`F11`",             "Activate full screen mode."
   ":kbd:`Shift-Enter`",     "Insert a hard line break at the cursor position."
   ":kbd:`Shift-F3`",        "Find previous occurrence of word in current document. (Same as :kbd:`Ctrl-Shift-G`"
   ":kbd:`Shift-Space`",     "Insert a non-breaking space at the cursor position."
   ":kbd:`Enter`",           "If in tree view, open a document for editing."

.. note::
   On macOS, replace :kbd:`Ctrl` with :kbd:`Cmd`.

A set of insert features are also available through shortcuts, but they require a double combination of shortcuts.

.. csv-table:: Keyboard Shortcuts
   :header: "Shortcut", "Description"
   :widths: 30, 50

   ":kbd:`Ctrl-K, -`",           "Insert a short dash (en dash)."
   ":kbd:`Ctrl-K, _`",           "Insert a long dash (em dash)."
   ":kbd:`Ctrl-K, .`",           "Insert ellipsis."
   ":kbd:`Ctrl-K, Return`",      "Insert a hard line break."
   ":kbd:`Ctrl-K, Space`",       "Insert a non-breaking space."
   ":kbd:`Ctrl-K, Shift-Space`", "Insert a thin space."
   ":kbd:`Ctrl-K, Ctrl-Space`",  "Insert a thin non-breaking space."
