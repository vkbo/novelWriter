.. _a_struct:

***************
Novel Structure
***************

This section covers the structure of a novel project.

.. note::
   This section concerns files under the Novel type root folder only. There are some restrictions
   and features that only applies to these type of files.


.. _a_struct_heads:

Importance of Headings
======================

Subfolders under root folders have no impact on the structure of the novel itself. The structure is
instead dictated by the heading level of the headers within the text files. Four levels of headings
are supported, signified by the number of hashes preceding the title. See also the :ref:`a_ui_md`
section.

.. note::
   The header levels are not only important when generating the exported novel file, but they are
   also used by the indexer when building the outline tree in the :guilabel:`Outline` tab. Each
   heading also starts a new region where new references to tags can be set.

The different header levels are interpreted as specific section types of the novel in the following
way:

``# Header1``
   Header level 1 signifies that the text refers to either the novel title or the name of a top
   level partition when you want to split the manuscript up into books, parts, or acts.

``## Header2``
   Header level 2 signifies a chapter level partition. Each time you want to start a new chapter,
   you must add such a heading. If you chose to split your manuscript up into one file per scene,
   you need a single chapeter file with just the heading. You can of course also add a synopsis and
   tags and references to the chapter file. If you want to open the chaper with a quote, this is
   also where you'd put the text for that.

``### Header3``
   Header level 3 signifies a scene level partition. The title itself can be replaced with a scene
   separator or just skipped entirely when you export your manuscript.

``#### Header4``
   Header level 4 signifies a sub-scene level partition (section). These can be useful if you want
   to change tag references mid-scene, like if you change the point of view character. You are free
   to use sections as you wish, and can filter the titles out of the final manuscript just like with
   scene titles.

There are multiple options of how to process novel titles when exporting the manuscript. For
instance, chapter numbers can be applied automatically, and so can scene numbers if you want them in
a draft manuscript. See the :ref:`a_export` page for more details.


.. _a_struct_tags:

Tag References
==============

Each partition, indicated by a heading, can contain references to tags set in the supporting files
of the project. The references are gathered by the indexer and used to generate the outline view on
the :guilabel:`Outline` tab of how the different parts of the novel are connected.

References and tags are also clickable in the document editor and viewer, making it easy to navigate
reference notes while writing.

References are set as keyword and a list of corresponding tags. The valid keywords are listed below.
The format of a meta line is ``@keyword: value1, [value2] ... [valueN]``. All keywords allow
multiple values.

``@pov``
   The point-of-view character for the current section. The target must be a note tag in the
   character type root folder.

``@char``
   Other characters in the current section. The target must be a note tag in a character type root
   folder. This should not include the point-of-view character.

``@plot``
   The plot or subplot touched by the current section. The target must be a note tag in a plot type
   root folder.

``@time``
   The timelines touched by the current section. The target must be a note tag in a timeline type
   root folder.

``@location``
   The location the current section takes place in. The target must be a note tag in a locations
   type root folder.

``@object``
   Objects present in the current section. The target must be a note tag in a object type root
   folder.

``@entity``
   Entities present in the current section. The target must be a note tag in an entities type root
   folder.

``@custom``
   Custom references in the current section. The target must be a note tag in a custom type root
   folder.

The syntax highlighter will alert the user that the tags and references are used correctly, and that
the tags referenced exist.

The highlighter may be mistake if the index of defined tags is out of date. If so, press :kbd:`F9`
to regenerate it, or select :guilabel:`Rebuild Index` from the :guilabel:`Tools` menu. In general,
the index for a file is regenerated when a file is saved, so this shouldn't normally be necessary.


.. _a_struct_layout:

Novel File Layout
=================

All files in a novelWriter project can have a layout format set. These layouts are important when
the project is exported as they indicate how to treat the content in terms of formatting, headings,
and page breaks. The layout for each file is indicated as the last set of characters in the
:guilabel:`Flags` column of the project tree.

Not all layout types are actually treated differently, but they also help to indicate what each file
is for in your project. The "Book" layout is a generic novel file layout that in formatting is
identical to "Chapter" and "Scene", but may help to indicate what files do in your project.

You can for instance lay out your project using Book files for each act, and then later split those
into chapter or scene files by using the :guilabel:`Split Document` tool. Scenes can also be
contained within chapter files, but you lose the drag and drop feature that comes with having them
in separate files if you organise them this way.

Some layouts *do* have implications on how the project is exported. Files with layout "Title" and
"Partition" have all headings and text centred, while the "Unnumbered" layout disables the automatic
chapter numbering feature for everything contained within it. The latter is convenient for Prologue
and Epilogue type chapters.

All of the above layout formats are only usable in the Novel root folder. Files that are not a part
of the novel itself should have the Note layout. These files are not getting any special formatting,
and it is possible to collectively filter them out during export. Note files can be used anywhere
in the project, also in the Novel root folder.

Below is an overview of all available layout formats.

Title Page
   The title page layout. The title should be formatted as a heading level one. All text is automatically centred on exports.

Plain Page
   A plain page layout useful for instance for front matter pages. Heading levels are ignored for this layout format, and so are
   formatting options like Justify Text. The page is exported with a page break before it.

Book
   This is the generic novel file format that in principle can be used for all novel files. Since the internal structure of the
   novel is controlled by the heading levels, this file will produce the same result as a collection of Partition, Chapter and Scene
   type files. However, it does not provide the functionality of the Unnumbered layout format.

Partition
   A partition can be used to split the novel into parts. Partition titles are indicated with a level one heading. You can also add
   text and meta data to the page. The Partition file layout will in addition force a page break before the heading, and centre all
   content on the page.

Chapter
   Signifies the start of a new chapter. If the text itself is contained in scene files, these files should only contain the title,
   comments, synopsis, and tag references for characters, plot, etc. The heading for chapters should be level two. If you need an
   opening text, like a quote or other leading text before the first scene, this is also where you'd want to add this text.

Unnumbered
   Same as Chapter, but when exporting the files and automatic chapter numbering is enabled, this file will not receive a number.
   This makes the layout suitable for Prologue and Epilogue type chapters.

Scene
   A scene file. This file should have a header of level three. Further sections can have headers of level four, but there are no
   file layout specifically for sections.

Note
   A generic file that is optionally ignored when the novel is exported. Use these files for descriptions of content in the
   supporting root folders. Note files can also be added to the Novel root folder if you need to insert notes there. Note file
   headers receive no formatting when building the project. They are always exported as-is.

.. note::
   The layout granularity is entirely optional. In principle, you can write the entire novel in a single file with layout "Book".
   You can also have a single file per chapter if that suits you better. The :guilabel:`Outline` will show your structure of
   chapters and scenes regardless of how your files are organised.
