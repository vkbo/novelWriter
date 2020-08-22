.. _a_intro:

************
Introduction
************

novelWriter is a simple, multi-document plain text editor using a modified markdown syntax to apply
simple formatting. It is designed for writing novels, and allows for the component documents to be
ordered freely to create the desired structure of the novel. More details about how projects are
structured is covered on the :ref:`a_struct` page.

In addition, the project can contain notes on the various plot elements, characters, locations, etc,
that make up the story. These notes are organised in a set of category-specific top-level folders,
and each entry can be tagged and cross-referenced from within the novel files and other notes. These
tags make it possible to inter-link documents, and generate an overview of the entire novel project
and how the various files and plot elements are interconnected. This is covered on the :ref:`a_proj`
and :ref:`a_notes` pages.

These additional features are not standard in markdown, but are available through special meta
keywords. Syntax highlighting is provided to make it easier to verify that the markdown tags are
used correctly. The syntax is covered on the :ref:`a_ui` page.


.. _a_intro_design:

Design Philosophy
=================

The user interface of novelWriter is intended to be as minimalistic as practically possible, while
at the same time provide a complete set of features needed for writing a novel. 

.. note::
   novelWriter is not intended to be a full office type word processor. It doesn't support images,
   links, tables, and other complex structure and objects often needed for such document. Formatting
   is limited to headers, and bold, italicised and strikethrough text.

The main window does not have a toolbar like most other applications do. This reduces clutter, and
since the documents are formatted with markdown tags, is more or less redundant. However, all
formatting features supported are available through convenient keyboard shortcuts. They are also
available in the main menu. A full list of shortcuts can be found in the :ref:`a_ui_shortcuts`
section.

In addition, novelWriter offers a :guilabel:`Focus Mode` where all the user interface elements other
than the document editor itself are hidden away.

The colour scheme of the user interface defaults to that of the host operating system. In addition,
a dark theme is provided, and can be enabled in :guilabel:`Preferences` from the :guilabel:`Tools`
menu. A number of syntax highlighting themes are also available in :guilabel:`Preferences`. A set of
icon themes in colour and greyscale are also offered. The icons are based on the Typicon_ icon set
designed by Stephen Hutchings.

The main window is split in two, or optionally three, panels. The left-most contains the project
tree and all the files in your project. The second panel is the document editor, and the optional
third panel is a document viewer which can view any document in your project.

A second tab is also available on the main window. This is the :guilabel:`Outline` tab where the
entire novel structure can be displayed, with all the tags and references listed. Depending on how
you structure your novel project files, this outline can be quite different than your project tree.
Your project tree lists files, your Outline tree lists the structure of the novel itself.

.. _Typicon: https://github.com/stephenhutchings/typicons.font


.. _a_intro_project:

Project Layout
==============

You are free to structure your project files as you wish in subfolders, and split the text between
files in whatever way suits you. All that matters to novelWriter is the linear order the files
appear at in the project tree (top to bottom). The chapters, scenes and sections of the novel are
determined by the headings within those files.

The four heading levels (**H1** to **H4**) are treated as follows:

* **H1** is used for the book title, and for partitions.
* **H2** is used for chapter tiles.
* **H3** is used for scene titles – optionally replaced by separators.
* **H4** is for section titles within scenes, if such granularity is needed.

This header level structure is only taken into account for novel files. For the files designated as
project notes, the header levels imply no structural meaning, and the user is free to do whatever
they want. See the :ref:`a_struct` page for more details.


.. _a_intro_export:

Project Export
==============

The project can at any time be exported to a range of different formats. Natively, novelWriter
supports export to plain text file, HTML document, novelWriter flavoured markdown, standard
markdown (requires Qt 5.14), and to a basic Open Document.

In addition, printing and printing to PDF is also possible. The best supported export format is
HTML, which can be imported or converted by a number of other tools like Pandoc, or simply imported
into Libre Office Writer and similar word processors.

It is also possible to export the content of the project to a JSON file. This is useful if you want
to write your own processing script in for instance Python as the entire novel can be read into a
Python dictionary with a couple of lines of code.

A number of filter options can be applied to the produced document, allowing you to export a draft
manuscript, a reference document of notes, an outline based on chapter and scene titles with a
synopsis each, and so on. See the :ref:`a_export` page for more details on export features and
formats.


.. _a_intro_screenshots:

Screenshot
==========

**novelWriter with default system theme:**

.. image:: images/screenshot_default.png
   :width: 800

**novelWriter with dark theme:**

.. image:: images/screenshot_dark.png
   :width: 800
