.. _a_intro:

************
Introduction
************

novelWriter is a simple, multi-document plain text editor using a markup syntax inspired by
markdown to apply simple formatting to the text. It is designed for writing novels, so the
formatting features are limited.

The idea is to let the user focus on writing instead of spending time messing with the formatting
of headers and text. Therefore you cannot change the look of the text in the editor window.
Instead, you provide formatting tags where they're needed, like for instance which text is a
header, where you want text bolded or italicised, and what alignment you want for paragraphs. The
actual formatting is then added to the text when you run the :guilabel:`Build Novel Project` tool.

A document viewer to the right of the editor can also show a renderred version of any document if
you want to inspect the result, or just want to keep a second document open for reference when
you're writing.

You can split your novel project up into as many individual files as you want to. The files are
glued together when you build the project, in the top-to-bottom order in which they appear in the
project tree. Splitting the project up into chapter and scene files means you can easily reorder
them using the drag and drop feature. More details about how projects are structured is covered in
:ref:`a_struct`.

In addition to novel text documents, the project can contain notes on the various plot elements,
characters, locations, etc, that make up the story. These notes are organised in a set of
category-specific top-level folders referred to as *Root Folders*. Each note can be assigned one or
more tags (one tag is allowed for each heading in the note), and these tags can be referenced from
within the novel documents and other notes.

These tags make it possible to inter-link documents, and you can also generate an overview of the
entire novel project and how the various documents and plot elements are interconnected. The tag
and reference syntax is covered in :ref:`a_proj` and :ref:`a_notes`.

These features are available through special meta keywords described in :ref:`a_struct_tags`.
Syntax highlighting is provided to make it easier to verify that the markdown tags are used
correctly.

An overview of the supported formatting syntax is covered in :ref:`a_ui`.


.. _a_intro_design:

Design Philosophy
=================

The user interface of novelWriter is intended to be as minimalistic as practically possible, while
at the same time provide a complete set of features needed for writing a novel.

.. note::
   novelWriter is not intended to be a full office type word processor. It doesn't support images,
   links, tables, and other complex structures and objects often needed for such documents.
   Formatting is limited to headers, emphasis, text alignment, and a few other simple features.

.. tip::
   If you do need to align information in rows and columns in your notes, you can achieve this with
   tabs and line breaks. The tab stop width can be specified in :guilabel:`Preferences`.

The main window does not have a toolbar like many other applications do. This reduces clutter, and
since the documents are formatted with style tags, is more or less redundant. However, most
formatting features supported are available through convenient keyboard shortcuts. They are also
available in the main menu so you don't have to look up formatting codes every time you need them.
A full list of shortcuts can be found in the :ref:`a_kb` section.

In addition, novelWriter has a :guilabel:`Focus Mode` where all the user interface elements other
than the document editor itself are hidden away.

The colour scheme of the user interface defaults to that of the host operating system. Some other
light and dark colour themes are provided, and can be enabled in :guilabel:`Preferences` from the
:guilabel:`Tools` menu. A number of syntax highlighting themes are also available in
:guilabel:`Preferences`. A set of icon themes in colour and greyscale are also offered. The icons
are based on the Typicons_ icon set designed by Stephen Hutchings.

The main window is split in two, or optionally three, panels. The left-most panel contains the
project tree and all the documents in your project. The second panel is the document editor. An
optional third panel is a document viewer which can view any document in your project independently
of what is open in the document editor. It is not intended as a preview window, although you can
use it for this. The main purpose of the viewer is for viewing your notes next to your editor
while you're writing.

A second tab is also available on the main window. This is the :guilabel:`Outline` tab where the
entire novel structure can be displayed, with all the tags and references listed. Depending on how
you structure your novel documents, this outline can be quite different from your project tree.
Your project tree lists individual documents, your Outline tree lists the structure of the novel
itself in terms of partitions, chapters and scenes as it appears in the text of those documents.

.. _Typicons: https://github.com/stephenhutchings/typicons.font


.. _a_intro_project:

Project Layout
==============

You are free to organise your project documents as you wish into subfolders, and split the text
between documents in whatever way suits you. All that matters to novelWriter is the linear order
the documents appear at in the project tree (top to bottom). The chapters, scenes and sections of
the novel are determined by the headings within those documents.

The four heading levels (**H1** to **H4**) are treated as follows:

* **H1** is used for the book title, and for partitions.
* **H2** is used for chapter tiles.
* **H3** is used for scene titles – optionally replaced by separators.
* **H4** is for section titles within scenes, if such granularity is needed.

This header level structure is only taken into account for novel documents. For the project notes,
the header levels have no structural meaning, and the user is free to do whatever they want. See
:ref:`a_struct` and :ref:`a_notes` for more details.


.. _a_intro_export:

Project Export
==============

The project can at any time be exported to a range of different formats through the
:guilabel:`Build Novel Project` tool. Natively, novelWriter supports export to Open Document,
HTML5, and various flavours of Markdown.

The HTML5 export format is suitable for conversion by a number of other tools like Pandoc, or for
importing into word processors if the Open Document format isn't suitable. In addition, printing
and printing to PDF is also possible. 

You can also export the content of the project to a JSON file. This is useful if you want to write
your own processing script in for instance Python as the entire novel can be read into a Python
dictionary with a couple of lines of code. The JSON file can be populated either with HTML
formatted text, or with the raw text as typed into the novel documents. See :ref:`a_export_options`
for more details.

A number of filter options can be applied to the Build tool, allowing you to export a draft
manuscript, a reference document of notes, an outline based on chapter and scene titles with a
synopsis each, and so on. See :ref:`a_export` for more details on export features and formats.


.. _a_intro_screenshots:

Screenshots
===========

**novelWriter with default system theme:**

.. image:: images/screenshot_default.png
   :width: 800

**novelWriter with dark theme:**

.. image:: images/screenshot_dark.png
   :width: 800
