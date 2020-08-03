.. _a_intro:

************
Introduction
************

novelWriter is a simple, multi-document plain text editor using a modified markdown syntax to apply
simple formatting. It is designed for writing novels, and allow for the component documents to be
ordered freely to create the desired structure of the novel project.

In addition, the project can contain notes on the various plot elements, characters, locations, etc,
that make up the story. These notes are organised in a set of category-specific folders, and each
entry can be tagged and cross referenced from within the novel files and other notes. These tags
make it possible to inter-link documents, and generate an overview of the entire novel project and
how the various files and plot elements are interconnected.

These additional features are not standard in markdown, but are available through special meta
keywords. Syntax highlighting is provided to make it easier to verify that the markdown tags are
used correctly.


.. _a_intro_design:

Design Philosophy
=================

The user interface of novelWriter is intended to be as minimalistic as practically possible, while
at the same time provide a complete set of features needed for writing a novel. 

.. note::
   novelWriter is not intended to be a full office type word processor. It doesn't support images,
   links, tables, and its formatting is limited to headers, and bold, italicised and strikethrough
   text.

The main window does not have a tool bar like most other applications do. This reduces clutter, and
since the documents are formatted with markdown tags, more or less redundant. However, all
formatting features supported are available through convenient keyboard shortcuts. They are also
available in the main menu.

The colour scheme of the user interface defaults to that of the host operating system. In addition,
a dark theme is provided, and can be enabled in Preferences. A number of syntax highlighting themes
are also available in Preferences. Coloured and grayscale icon themes are also available.

The main window is split in two, or optionally three, panels. The left-most contains the project
tree and all the files in your project. The second panel is the document editor, and the optional
third panel is a document viewer which can view any document in your project.

A second tab is also available on the main window. This is the Outline tab where the entire novel
structure can be displayed, with all the tags and references listed. Depending on how you structure
your novel project files, this outline can be quite different than your project tree.


.. _a_intro_project:

Project Layout
==============

You are free to structure your project files as you wish in subfolders and split between files. All
that matters to novelWriter is the linear order they appear in the project tree (top to bottom) and
the chapters, scenes and sections of the novel is determined by the headings within those files.

The four heading levels (H1 to H4) are treated as follows:

* H1 is used for the book title, and for partitions.
* H2 is used for chapter tiles.
* H3 is reserved for scene titles.
* H4 is for section titles within scenes, if such granularity is needed.

This structure is only considered on novel files. For the files designated as project notes, the
usage of headers imply no structural meaning, and the user is free to do whatever they want.


.. _a_intro_export:

Project Export
==============

The project can at any time be exported to a range of different formats. Natively, novelWriter
supports export to plain text file, HTML document, novelWriter flavoured markdown, standard
markdown (requires Qt 5.14), and to a basic Open Document.

In addition, printing and printing to PDF is also possible. The best supported export format is
HTML, which can be imported or converted by a number of other tools like Pandoc, or simply imported
into Libre Office and similar.

It is also possible to export the content of the project to a JSON file. This is useful if you want
to write your own processing script in for instance Python, as the entire novel can be read into a
Python dictionary with a couple of lines of code.


.. _a_intro_screenshots:

Screenshot
==========

**novelWriter with default system theme:**

.. image:: images/screenshot_default.png
   :width: 800

**novelWriter with dark theme:**

.. image:: images/screenshot_dark.png
   :width: 800
