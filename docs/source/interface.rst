.. _a_ui:

***************
User Interface
***************

The user interface is kept as simple as possible to avoid distractions when writing. This page lists
all the main GUI elements, and explains what they do.

.. _a_ui_tree:

The Project Tree
================

The main window contains a project tree in the left-most panel. It shows the entire structure of the
project. It has four columns:

:guilabel:`Label`
   The first column shows the item icon and its label. The labels can be edited from the menu, or by
   pressing :kbd:`F2` or :kbd:`Ctrl`:kbd:`E`. The label is not the same as the title you set inside
   the document, but it will appear in the header above the document text itself.

:guilabel:`Words`
   The second column shows the word count of the file, or the sum of words in the child items if it
   is a folder. If the counts seem incorrect, they can be updated by rebuilding the project index
   from the :guilabel:`Tools` menu, or by pressing :kbd:`F9`.

:guilabel:`Inc`
   The third column indicates whether the file is included in the final project build or not. You
   may want to filter out files that you no longer want to keep in the final manuscript, but want to
   keep in the project for reference.

:guilabel:`Flags`
   The fourth column shows various meta data flags for the item. The first is an icon indicating the
   importance or status of the file. These are colour coded status levels that you control and
   define yourself. They can be changed in :guilabel:`Project Settings` from the :guilabel:`Project`
   menu. The first character after the icon indicates the class of the item, that is ``N`` for
   **Novel**, ``C`` for **Character**, etc (see :ref:`a_struct_tags`. The second character indicates
   the file layout type (see :ref:`a_proj_roots`).

Below the project tree you will find a small details panel showing the full information of the
currently selected item. This panel also includes the latest paragraph and character counts in
addition to the word count.


.. _a_ui_tree_dnd:

Project Tree Drag and Drop
--------------------------

The project tree allows dragging and drop to a certain extent. This feature is primarily intended
for rearranging the order of your files within each root folder, and has only limited support for
moving files elsewhere in the project tree. In general, bulk actions are not allowed. This is
deliberate to avoid accidentally messing up your project. The project tree has no undo function.

Document files and their folders can be rearranged freely within their root folders. Novel files
cannot be moved out of the :guilabel:`Novel` folder, except to :guilabel:`Trash` and the
:guilabel:`Outtakes` folder. Note files can be moved freely anywhere.

Folders cannot be moved at all outside their root tree. Neither can a folder containing files be
deleted. You must first delete the files.

Root folders in the project tree cannot be dragged and dropped at all. However, if you want to
reorder them, you can move them up or down with respect to eachother from the :guilabel:`Tools`
menu, or by pressing :kbd:`Ctrl`:kbd:`Shift` and the :kbd:`Up` or :kbd:`Down` key.


.. _a_ui_edit:

Editing and Viewing Documents
=============================

To edit a document, double-click the file in the project tree, or press the :kbd:`Return` key while
having it selected. This will open the file in the document editor. The editor uses a simplified
markdown format. The format is described in the :ref:`a_ui_md` section below. The editor has a
maximise button (activates :guilabel:`Focus Mode`) and a close button in the top-right corner.

Any document in the project tree can also be viewed in parallel in a right hand side document viewer
To view a document, press :kbd:`Ctrl`:kbd:`R`, or select :guilabel:`View Document` in the menu. The
document viewed does not have to be the same document currently being edited. However, If you *are*
viewing the same document, pressing :kbd:`Ctrl`:kbd:`R` again will update the document with your
latest changes. You can also press the little reload button in the top-right corner of the view
panel next to the close button to achieve the same thing.

Both the document editor and viewer will show the label of the document in the header at the top of
the edit or view panel. Optionally, the full project path to the file can be shown. This can be set
in the :guilabel:`Preferences` dialog from the :guilabel:`Tools` menu. Clicking on the document
title bar will select and reveal the file in the project tree, making it easier to find the project
location of the file in a large project.

Any reference to a tag in the editor can be opened in the viewer by moving the cursor to the label
and pressing :kbd:`Ctrl`:kbd:`Return`. In the viewer, the references become clickable links.
Clicking them will replace the content of the viewer with the content of the document the reference
points to.

At the bottom of the view panel there is a :guilabel:`References` panel. (If it is hidden, click the
icon to reveal it.) This panel will show links to all documents referring back to it, if any has
been defined. The :guilabel:`Sticky` button will freeze the content of the panel to the current
document, even if you navigate to another document. This is convenient if you want to quickly look
through all documents in the list in the :guilabel:`References` panel.

.. note::
   The :guilabel:`References` panel relies on an up-to-date index of the project. If anything is
   missing, or seems wrong, the index can always be rebuilt by selecting :guilabel:`Rebuild Index`
   from the :guilabel:`Tools` menu, or by pressing :kbd:`F9`.


.. _a_ui_edit_auto:

Auto-Replace as You Type
========================

A few auto-replace features are supported by the editor. You can control every aspect of the
auto-replace feature from :guilabel:`Preferences`.

.. tip::
   If you don't like auto-replacement, all symbols inserted by this feature are also available in
   the :guilabel:`Insert` menu, and via convenient :ref:`a_ui_shortcuts_ins`.

The editor is able to replace two and three hyphens with short and long dashes, triple points with
ellipsis, and replace straight single and double quotes with user-defined quote symbols. It will
also try to determine whether to use the opening or closing symbol, but this feature isn't always
accurate.

.. tip::
   If the editor changes a symbol when you did not want it to change, pressing :kbd:`Ctrl`:kbd:`Z`
   immediately after the auto-replacement will undo it without undoing the character you typed.


.. _a_ui_md:

Markdown Format
===============

The document editor uses a simplified markdown format. That is, it supports basic formatting like
emphasis (italic), strong importance (bold) and strikethrough text, as well as four levels of
headings.

Some non-standard markdown features have been added. For instance, novelWriter allows for comments,
a synopsis tag, and a set of keyword and value sets used for tags and references.


.. _a_ui_md_head:

Headings
--------

Four levels of headings are allowed. For files of type "Note", they are free to be used as you see
fit, but for all other file layouts used for the novel text itself, they indicate the structural
level of the novel. See :ref:`a_struct_heads` for more details.

``# Title``
   Heading level one. If the file is a novel file, the header level indicates the start of a new
   partition. This heading level can also be used for the title page novel title.

``## Title``
   Heading level two. If the file is a novel file, the header level indicates the start of a new
   chapter.

``### Title``
   Heading level three. If the file is a novel file, the header level indicates the start of a new
   scene.

``#### Title``
   Heading level four. If the file is a novel file, the header level indicates the start of a new
   section.

.. note::
   The space after the ``#`` characters is mandatory. The syntaxhighlighter will change colour and
   font size when the heading is correctly formatted.


.. _a_ui_md_emph:

Text Emphasis
-------------

A minimal set of text emphasis styles are supported.

``_text_``
   The text is rendered as emphasised text (italicised).

``**text**``
   The text is rendered as strongly important text (bold).

``~~text~~``
   Strikethrough text.

In markdown guides it is often recommended to differentiate between strong importance and emphasis
by using ``**`` for strong and ``_`` for emphasis, although markdown generally supports also ``__``
for strong and ``*`` fdr emphasis. However, since the differentiation makes the highlighting and
conversion significantly simpler and faster, in novelWriter this is a rule, not just a
recommendation. The following is therefore the only supported formatting syntax:

There are also some additional rules:

1. The emphasis and strikethrough formatting tags do not allow spaces between the words and the tag
   itself. That is, ``**text**`` is valid, ``**text **`` is not.
2. More generally, the delimiters must be on the outer edge of words. That is, ``some **text in
   bold** here`` is valid, ``some** text in bold** here`` is not.
3. If using both ``**`` and ``_`` to wrap the same text, the underscore must be the inner wrapper.
   This is due to the underscore also being a valid word character, so if they are on the outside,
   they violate rule 2.


.. _a_ui_md_comm:

Comments and Synopsis
---------------------

In addition to these standard markdown features, novelWriter also allows for comments in the text
files. The text of the comment is ignored by the word counter and not exported or, optionally,
hidden when viewing the document. If the first word of a comment is ``Synopsis:`` (with the colon),
the comment is treated specially, and will show up in the :ref:`a_ui_outline` in a dedicated column.

``% text...``
   A comment. The text is not exported by default (this can be overridden), seen in the Viewer, or
   counted towards word counts.

``% Synopsis: text...``
   A synopsis comment. It is generally treated in the same way as regular comments, except that it
   is captured by the indexing algorithm and displayed in the :ref:`a_ui_outline`. It can also be
   filtered separately when exporting the project to for instance generate an outline document of
   the whole project.


.. _a_ui_md_tags:

Tags and References
-------------------

The document editor supports a minimal set of keywords used for setting tags, and making references
between files. The tags and references can be set once per section defined by a heading. Using them
multiple times under the same heading will just override the previous setting.

``@keyword: value``
   A keyword argument followed by a value, or a comma separated list of values.

The available tag and reference keywords are listed in the :ref:`a_struct_tags` section.


.. _a_ui_md_add:

Additional Markdown and Non-Standard Features
---------------------------------------------

The editor and viewer also supports markdown standard hard line breaks, and preserves non-breaking
spaces if running with Qt 5.9 or higher. For older versions, the non-breaking spaces are lost when
the file is saved. This is unfortunately hard-coded in the Qt text editor.

* A hard line break is achieved by leaving two or more spaces at the end of the line. Alternatively,
  the user can press :kbd:`Ctrl`:kbd:`K`, :kbd:`Return` to insert this.
* A non-breaking space is inserted with :kbd:`Ctrl`:kbd:`K`, :kbd:`Space`.
* Thin spaces are also supported, and can be inserted with :kbd:`Ctrl`:kbd:`K`, :kbd:`Shift`:kbd:`Space`.
* Non-breaking thin space can be inserted  with :kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`Space`.

These are all insert features, and the :guilabel:`Insert` menu has more. They are also listed
in :ref:`a_ui_shortcuts_ins`.

Both hard line breaks and non-breaking spaces are highlighted by the syntax highlighter as an
alternate coloured background, depending on the selected theme.


.. _a_ui_outline:

Project Outline View
====================

The project's Outline view is available as the second tab on the right hand side of the main window
labelled :guilabel:`Outline`. The outline provides an overview of the novel structure, displaying a
tree hierarchy of the elements of the novel, that is, the level 1 to 4 headings, not the files.

The document file containing the heading can also be displayed as a separate column, as well as the
line number where it occurs. Double-clicking an entry will open the corresponding file in the
editor.

.. note::
   Since the internal structure of the novel does not depend on the file structure of the project
   tree, these will not necessarily look the same, depending how you chose to organise your files.
   See the :ref:`a_struct` page for more details.

Various meta data and information extracted from tags can be displayed in columns in the outline.
A default set of such columns is visible, but you can turn on or off more columns by right clicking
the header and selecting the columns you want to show. The order of the columns can also be
rearranged by dragging them to a different position.

.. note::
   The :guilabel:`Title` column cannot be disabled or moved.

The information viewed in the outline is based on the project's main index. While novelWriter does
its best to keep the index up to date when content changes, you can always rebuild it manually by
pressing :kbd:`F9` if something isn't right.

The outline view itself can be regenerated by pressing :kbd:`F10`. You can also enable automatic
updating in the :guilabel:`Tools` menu, which will trigger an update whenever the index is updated
and the :guilabel:`Outline` tab is active. You may want to disable this feature if your project is
very large,


.. _a_ui_outline_synopsis:

Synopsis Column
---------------

The :guilabel:`Synopsis` column of the outline view takes its information from a specially formatted
comment. See :ref:`a_ui_md_comm`. In order to flag a comment as a synopsis, add the word
``Synopsis:`` as the first word of the comment. The ``:`` is required, and the word ``synopsis`` is
not case sensitive. If it is correctly formatted, the syntax highlighter will indicate this by
altering the colour of the word.

.. note::
   Only one comment can be flagged as a synopsis comment for each heading. If multiple comments are
   flagged as a synopsis comment, the last one will be used.


.. _a_ui_shortcuts:

Keyboard Shortcuts
==================

Most features are available as keyboard shortcuts. These are as follows:

.. csv-table:: Keyboard Shortcuts
   :header: "Shortcut", "Description"
   :widths: 30, 70
   :class: "tight-table"

   ":kbd:`Alt`:kbd:`1`",                 "Switch focus to the project tree."
   ":kbd:`Alt`:kbd:`2`",                 "Switch focus to document editor."
   ":kbd:`Alt`:kbd:`3`",                 "Switch focus to document viewer."
   ":kbd:`Ctrl`:kbd:`.`",                "Open menu to correct word under cursor."
   ":kbd:`Ctrl`:kbd:`,`",                "Open the :guilabel:`Preferences` dialog."
   ":kbd:`Ctrl`:kbd:`/`",                "Change block format to comment."
   ":kbd:`Ctrl`:kbd:`-`",                "Strikethrough selected text, or word under cursor."
   ":kbd:`Ctrl`:kbd:`0`",                "Remove block formatting for block under cursor."
   ":kbd:`Ctrl`:kbd:`1`",                "Change block format to header level 1."
   ":kbd:`Ctrl`:kbd:`2`",                "Change block format to header level 2."
   ":kbd:`Ctrl`:kbd:`3`",                "Change block format to header level 3."
   ":kbd:`Ctrl`:kbd:`4`",                "Change block format to header level 4."
   ":kbd:`Ctrl`:kbd:`A`",                "Select all text in the document."
   ":kbd:`Ctrl`:kbd:`B`",                "Format selected text, or word under cursor, with strong emphasis (bold)."
   ":kbd:`Ctrl`:kbd:`C`",                "Copy selected text to clipboard."
   ":kbd:`Ctrl`:kbd:`D`",                "Wrap selected text, or word under cursor, in double quotes."
   ":kbd:`Ctrl`:kbd:`E`",                "If in the project tree, edit a document or folder settings. (Same as :kbd:`F2`)"
   ":kbd:`Ctrl`:kbd:`F`",                "Open the search bar and search for the selected word, if any is selected."
   ":kbd:`Ctrl`:kbd:`G`",                "Find next occurrence of search word in current document. (Same as :kbd:`F3`)"
   ":kbd:`Ctrl`:kbd:`H`",                "Open the search and replace bar and search for the selected word, if any is selected. (On Mac, this is :kbd:`Cmd`:kbd:`=`)"
   ":kbd:`Ctrl`:kbd:`I`",                "Format selected text, or word under cursor, with emphasis (italic)."
   ":kbd:`Ctrl`:kbd:`N`",                "Create new document."
   ":kbd:`Ctrl`:kbd:`O`",                "Open selected document."
   ":kbd:`Ctrl`:kbd:`Q`",                "Exit novelWriter."
   ":kbd:`Ctrl`:kbd:`R`",                "If in the project tree, open a document for viewing. If the editor has focus, open current document for viewing."
   ":kbd:`Ctrl`:kbd:`S`",                "Save the current document in the document editor."
   ":kbd:`Ctrl`:kbd:`V`",                "Paste text from clipboard to cursor position."
   ":kbd:`Ctrl`:kbd:`W`",                "Close the current document in the document editor."
   ":kbd:`Ctrl`:kbd:`X`",                "Cut selected text to clipboard."
   ":kbd:`Ctrl`:kbd:`Y`",                "Redo latest undo."
   ":kbd:`Ctrl`:kbd:`Z`",                "Undo latest changes."
   ":kbd:`Ctrl`:kbd:`F7`",               "Toggle spell checking."
   ":kbd:`Ctrl`:kbd:`F10`",              "Toggle automatic updating of project outline."
   ":kbd:`Ctrl`:kbd:`Del`",              "If in the project tree, move a document to trash, or delete a folder."
   ":kbd:`Ctrl`:kbd:`Enter`",            "Open the tag or reference under the cursor in the Viewer."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`,`",    "Open the :guilabel:`Project Settings` dialog."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`/`",    "Remove block formatting for block under cursor."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`1`",    "Replace occurrence of search word in current document, and search for next occurrence."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`A`",    "Select all text in current paragraph."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`D`",    "Wrap selected text, or word under cursor, in single quotes."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`G`",    "Find previous occurrence of search word in current document. (Same as :kbd:`Shift`:kbd:`F3`)"
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`I`",    "Import text to the current document from a text file."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`N`",    "Create new folder."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`O`",    "Open a project."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`R`",    "Close the document viewer."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`S`",    "Save the current project."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`W`",    "Close the current project."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`Z`",    "Alternative sequence for redo last undo."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`Up`",   "Move item one step up in the project tree."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`Down`", "Move item one step down in the project tree."
   ":kbd:`F1`",                          "Open the documentation. This will either open the Qt Assistant, if available, or send you to the documentation website."
   ":kbd:`F2`",                          "If in the project tree, edit a document or folder settings. (Same as :kbd:`Ctrl`:kbd:`E`)"
   ":kbd:`F3`",                          "Find next occurrence of search word in current document. (Same as :kbd:`Ctrl`:kbd:`G`)"
   ":kbd:`F5`",                          "Open the :guilabel:`Build Novel Project` dialog."
   ":kbd:`F6`",                          "Open the :guilabel:`Writing Statistics` dialog."
   ":kbd:`F7`",                          "Re-run spell checker."
   ":kbd:`F8`",                          "Activate :guilabel:`Focus Mode`, hiding the project tree and document viewer."
   ":kbd:`F9`",                          "Re-build the project index."
   ":kbd:`F10`",                         "Re-build the project outline."
   ":kbd:`F11`",                         "Activate full screen mode."
   ":kbd:`Shift`:kbd:`F1`",              "Open the online documentation in the system default browser."
   ":kbd:`Shift`:kbd:`F3`",              "Find previous occurrence of search word in current document. (Same as :kbd:`Ctrl`:kbd:`Shift`:kbd:`G`)"
   ":kbd:`Return`",                      "If in the project tree, open a document for editing."

.. note::
   On macOS, replace :kbd:`Ctrl` with :kbd:`Cmd`.


.. _a_ui_shortcuts_ins:

Insert Shortcuts
----------------

A set of insert features are also available through shortcuts, but they require a double combination
of key sequences. The insert feature is activated with :kbd:`Ctrl-K`, followed by a key or
combination for the inserted character or punctuation.

.. csv-table:: Keyboard Shortcuts
   :header: "Shortcut", "Description"
   :widths: 40, 60
   :class: "tight-table"

   ":kbd:`Ctrl`:kbd:`K`, :kbd:`-`",                 "Insert a short dash (en dash)."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`_`",                 "Insert a long dash (em dash)."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`.`",                 "Insert ellipsis."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`1`",                 "Insert left single quote."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`2`",                 "Insert right single quote."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`3`",                 "Insert left double quote."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`4`",                 "Insert right double quote."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Return`",            "Insert a hard line break."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Space`",             "Insert a non-breaking space."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Shift`:kbd:`Space`", "Insert a thin space."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`Space`",  "Insert a thin non-breaking space."
