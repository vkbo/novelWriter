*****************
Project Structure
*****************

This section covers the structure of a novel project.

.. note::
   This section concerns files under the Novel type root folder only.
   There are some restrictions and features that only applies to these type of files.

Importance of Headings
======================

Subfolders under root folders have no impact on the structure of the novel itself.
The structure is instead dictated by the heading level.
Four levels of headings are supported, signified by the number of hashes preceding the title.
See the Markdown section.

The header levels are not only important when generating the exported novel file, but they are also used by the indexer and Outline View.
Each heading starts a new region where new references to tags can be set.

The different header levels are interpreted as specific section types of the novel.

* ``# Header1``: Header level 1 signifies that the text refers to either the novel title or the name of a top level partition.
* ``## Header2``: Header level 2 signifies a chapter level partition.
* ``### Header3``: Header level 3 signifies a scene level partition.
* ``#### Header4``: Header level 4 signifies a sub-scene level partition (section).

Tag References
==============

Each partition, indicated by a heading, can contain references to tags set in the supporting files of the project.

The references are gathered by the indexer and used to generate the Outline View of how the different parts of the novel are connected.
References and tags are also clickable in the view panel, and makes it easy to navigate reference notes while writing.
The targets of references can also be set per header.
This is covered in the "Supporting Files" section.

References are set as keyword and a list of corresponding tags.
The valid keywords are listed below.
The format of a meta line is ``@keyword: value1, [value2] ... [valueN]``.
All keywords allow multiple values.

* ``@pov``: The point-of-view character for the current section.
  The target must be a note tag in the character root folder.
* ``@char``: Other characters in the current section.
  The target must be a note tag in the character root folder.
  This should not include the point-of-view character.
* ``@plot``: The plot timelines touched by the current section.
  The target must be a note tag in the plot root folder.
* ``@time``: The timelines touched by the current section.
  The target must be a note tag in the timeline root folder.
* ``@location``: The location the current section takes place in.
  The target must be a note tag in the locations root folder.
* ``@object``: Objects present in the current section.
  The target must be a note tag in the object root folder.
* ``@entity``: Entities present in the current section.
  The target must be a note tag in the entities root folder.
* ``@custom``: Custom references in the current section.
  The target must be a note tag in the custom root folder.

The syntax highlighter will alert the user that only the correct keywords are used, and that the tags referenced exist.
If the index of defined tags is out of date, press :kbd:`F9` to regenerate it, or select :menuselection:`Tools --> Rebuild Index` from the menu.
In general, the index for a file is regenerated when a file is saved, so this shouldn't normally be necessary.

Novel File Layout
=================

Files in a novelWriter project can have a layout format set.
These layouts are important when the project is exported, as they indicate how to treat the content in terms of formatting, headings and page breaks.
The layout for each file is indicated as the last set of characters in the Flags column of the project tree.
They also help to indicate what each file is for in your project.

Some of these layout types are different, some are just cosmetic.
The "Book" layout is a generic novel file layout that in formatting is identical to "Chapter" and "Scene", but may help to indicate what files do in your project.
You can lay out your project using Book files for each act, and then later split those into chapter or scene files by using the "Split Document" tool.
Scenes can also be contained within chapter files, but you lose the drag and drop feature that comes with having them in separate files.

Some layouts have implications on how the project is exported.
Files with layout "Title" and "Partition" have all headings and text centred, while the "Unnumbered" layout disables the automatic chapter numbering feature for everything contained within it.

All of the above layout formats are only usable in the Novel root folder.
Files that are not a part of the novel itself should have the Note layout.
These files are not getting any special formatting, and it is possible to collectively filter them out during export.
Note files can be used anywhere in the project.

Below is an overview of all available layout formats.

* **Title Page**: The title page layout.
  The title should be formatted as a heading level one.
  All text is automatically centred on exports.
* **Plain Page**: A plain page layout useful for instance for front matter pages.
  Heading levels are ignored for this layout format, and so are formatting options like Justify Text.
  The page is exported with a page break before it.
* **Book**: This is the generic novel file format that in principle can be used for all novel files.
  Since the internal structure of the novel is controlled by the heading levels, this file will produce the same result as a collection of Partition, Chapter and Scene type files.
  However, it does not provide the functionality of the Unnumbered layout format.
* **Partition**: A partition can be used to split the novel into parts.
  Partition titles are indicated with a level one heading.
  You can also add text and meta data to the page.
  The Partition file layout will in addition force a page break before the heading, and centre all content on the page.
* **Chapter**: Signifies the start of a new chapter.
  If the text itself is contained in scene files, these files should only contain the title, comments, synopsis, and tag references for characters, plot, etc.
  The heading for chapters should be level two.
  If you need an opening text, like a quote or other leading text before the first scene, this is also where you'd want to add this text.
* **Unnumbered**: Same as Chapter, but when exporting the files and automatic chapter numbering is enabled, this file will not receive a number.
  This makes the layout suitable for Prologue and Epilogue type chapters.
* **Scene**: A scene file.
  This file should have a header of level three.
  Further sections can have headers of level four, but there are no file layout specifically for sections.
* **Note**: A generic file that is optionally ignored when the novel is exported.
  Use these files for descriptions of content in the supporting root folders.
  Note files can also be added to the Novel root folder if you need to insert notes there.
  Note file headers receive no formatting when building the project.
  They are always exported as-is.

.. note::
   The layout granularity is entirely optional.
   In principle, you can write the entire novel in a single file with layout "Book".
   You can also have a single file per chapter.
