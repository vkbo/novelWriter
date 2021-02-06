.. _a_struct:

***************
Novel Structure
***************

This section covers the structure of a novel project.

It concerns documents under the :guilabel:`Novel` type root folder only. There are some
restrictions and features that only apply to these types of documents.


.. _a_struct_heads:

Importance of Headings
======================

Subfolders under root folders have no impact on the structure of the novel itself. The structure is
instead dictated by the heading level of the headers within the documents.

Four levels of headings are supported, signified by the number of hashes (``#``) preceding the
title. See also the :ref:`a_ui_md` section for more details about the markdown syntax.

.. note::
   The header levels are not only important when generating the exported novel file, they are also
   used by the indexer when building the outline tree in the :guilabel:`Outline` tab. Each heading
   also starts a new region where new references and tags can be set.

The different header levels are interpreted as specific section types of the novel in the following
way:

``# Header1``
   Header level one signifies that the text refers to either the novel title or the name of a top
   level partition. The latter is useful when you want to split the manuscript up into books,
   parts, or acts.

``## Header2``
   Header level two signifies a chapter level partition. Each time you want to start a new chapter,
   you must add such a heading. If you choose to split your manuscript up into one document per
   scene, you need a single chapter document with just the heading. You can of course also add a
   synopsis and reference keywords to the chapter document. If you want to open the chapter with a
   quote or other introductory text that isn't part of a scene, this is also where you'd put that
   text.

``### Header3``
   Header level three signifies a scene level partition. You must provide a title text, but the
   title text can be replaced with a scene separator or just skipped entirely when you export your
   manuscript.

``#### Header4``
   Header level four signifies a sub-scene level partition, usually called a "section" in the
   documentation and the user interface. These can be useful if you want to change tag references
   mid-scene, like if you change the point-of-view character. You are free to use sections as you
   wish, and can filter the titles out of the final manuscript just like with scene titles.

.. tip::
   There are multiple options of how to process novel titles when exporting the manuscript. For
   instance, chapter numbers can be applied automatically, and so can scene numbers if you want
   them in a draft manuscript. See the :ref:`a_export` page for more details.


.. _a_struct_heads_unnum:

Unnumbered Chapter Headings
---------------------------

If you use layout types for your documents, the automatic numbering feature for your chapters is
controlled by whether you use the :guilabel:`Chapter` or :guilabel:`Unnumbered` layout type for
your document. However, if you have a different document layout where this isn't practical, you can
also switch off chapter numbering for a chapter by making the first character of the chapter title
an asterisk (``*``). Like so:

``## *Unnumbered Chapter Title``

The leading asterisk is only considered by the :guilabel:`Build Novel Project` tool, and will be
removed before inserted at the location of the ``%title%`` label. See the :ref:`a_export` page for
more details.

.. note::
   If you need the first character of the title to be an actual asterisk, you must escape it:
   ``\*``.


.. _a_struct_tags:

Tag References
==============

Each text partition, indicated by a heading of any level, can contain references to tags set in the
supporting notes of the project. The references are gathered by the indexer and used to generate an
outline view on the :guilabel:`Outline` tab of how the different parts of the novel are connected.
This section covers how to set references to tags. See :ref:`a_notes_tags` for how to define tags
the references can point to.

References and tags are also clickable in the document editor and viewer, making it easy to
navigate between reference notes while writing. Clicked links are always opened in the view panel.

References are set as a keyword and a list of corresponding tags. The valid keywords are listed
below. The format of a reference line is ``@keyword: value1, [value2] ... [valueN]``. All keywords
allow multiple values.

``@pov``
   The point-of-view character for the current section. The target must be a note tag in the
   :guilabel:`Character` type root folder.

``@char``
   Other characters in the current section. The target must be a note tag in a
   :guilabel:`Character` type root folder. This should not include the point-of-view character.

``@plot``
   The plot or subplot advanced in the current section. The target must be a note tag in a
   :guilabel:`Plot` type root folder.

``@time``
   The timelines touched by the current section. The target must be a note tag in a
   :guilabel:`Timeline` type root folder.

``@location``
   The location the current section takes place in. The target must be a note tag in a
   :guilabel:`Locations` type root folder.

``@object``
   Objects present in the current section. The target must be a note tag in an :guilabel:`Object`
   type root folder.

``@entity``
   Entities present in the current section. The target must be a note tag in an
   :guilabel:`Entities` type root folder.

``@custom``
   Custom references in the current section. The target must be a note tag in a :guilabel:`Custom`
   type root folder.

The syntax highlighter will alert the user that the tags and references are used correctly, and
that the tags referenced exist.

The highlighter may be mistaken if the index of defined tags is out of date. If so, press :kbd:`F9`
to regenerate it, or select :guilabel:`Rebuild Index` from the :guilabel:`Tools` menu. In general,
the index for a document is regenerated when it is saved, so this shouldn't normally be necessary.


.. _a_struct_layout:

Novel Document Layout
=====================

All documents in the project can have a layout format set. These layouts are important when the
project is exported as they indicate how to treat the content in terms of text formatting,
headings, and page breaks. The layout for each document is indicated as the last set of characters
in the :guilabel:`Flags` column of the project tree.

Not all layout types are actually treated differently, they also help to indicate what each
document is intended for in your project. The :guilabel:`Book` layout is a generic novel document
layout that is formatted identically to :guilabel:`Chapter` and :guilabel:`Scene` layout documents,
but may help to indicate what each document does in your project.

You can for instance lay out your project using :guilabel:`Book` documents for each act, and then
later split those into chapter or scene documents by using the :guilabel:`Split Document` tool.
Scenes can also be contained within :guilabel:`Chapter` type documents, but you lose the drag and
drop feature that comes with having them in separate documents if you organise them this way.

Some layouts *do* have implications on how the project is exported. Documents with layout
:guilabel:`Title Page` and :guilabel:`Partition` have all headings and text centred, while the
:guilabel:`Unnumbered` layout disables the automatic chapter numbering feature for everything
contained within it. The latter is convenient for Prologue and Epilogue type chapters.

The above layout formats are only usable in the Novel root folder. Documents that are not a part of
the novel itself should have the :guilabel:`Note` layout. These documents are not getting any
special formatting, and it is possible to collectively filter them out during export. Notes can be
used anywhere in the project, also in the :guilabel:`Novel` root folder.

Below is an overview of all available layout formats.

:guilabel:`Title Page`
   The title page layout. The title should be formatted as a heading level one. All text is centred
   on export.

:guilabel:`Plain Page`
   A plain page layout useful for instance for front matter pages. Heading levels are ignored for
   this layout format, and so are formatting options like :guilabel:`Justify Text`. The page is
   exported with a page break before it.

:guilabel:`Book`
   This is the generic novel format that in principle can be used for all novel documents. Since
   the internal structure of the novel is controlled by the heading levels, this layout will
   produce the same result as a collection of :guilabel:`Partition`, :guilabel:`Chapter` and
   :guilabel:`Scene` layout documents. However, it does not provide the functionality of the
   :guilabel:`Unnumbered` layout format by default, but this can still be achieved by prefixing the
   chapter title with an asterisk (``*``).

:guilabel:`Partition`
   A partition can be used to split the novel into parts. Partition titles are indicated with a
   level one heading. You can also add text and meta data to the page. The :guilabel:`Partition`
   layout will in addition force a page break before the heading, and centre all content on the
   page.

:guilabel:`Chapter`
   Signifies the start of a new chapter. If the text itself is contained in scene documents, these
   documents should only contain the title, comments, synopsis, and tag references for characters,
   plot, etc. The heading for chapters should be level two. If you need an opening text, like a
   quote or other leading text before the first scene, this is also where you'd want to add this
   text.

:guilabel:`Unnumbered`
   Same as :guilabel:`Chapter`, but when exporting the project, and automatic chapter numbering is
   enabled, documents with this layout will not increment the chapter number. It also has a
   separate title formatting setting. This makes the layout suitable for Prologue and Epilogue type
   chapters.

:guilabel:`Scene`
   Used for scenes. This document should have a header of level three. Further sections can have
   headers of level four, but there are no layout specifically for sections.

:guilabel:`Note`
   A generic document that is optionally ignored when the novel project is exported. Use this
   layout for descriptions of content in the supporting root folders. Notes can also be added to
   the :guilabel:`Novel` root folder if you need to insert notes there. Note headers receive no
   special formatting when building the project. They are always exported as-is.

.. note::
   The layout granularity is entirely optional. In principle, you can write the entire novel in a
   single document with layout :guilabel:`Book`. You can also have a single document per chapter if
   that suits you better. The :guilabel:`Outline` will show your structure of chapters and scenes
   regardless of how your documents are organised.

.. tip::
   You can always start writing with a coarse layout with one or a few documents, and then later
   use the split tool to automatically split the documents into separate chapter and scene
   documents.
