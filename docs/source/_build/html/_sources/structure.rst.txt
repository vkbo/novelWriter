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
For setting the targets of references, see the "Supporting Files" section.

References are set as keyword and a list of corresponding tags.
The valid keywords are listed below. The format of such a line is ``@keyword: value1, [value2] ... [valueN]``.
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

Files that exist under the Novel type root folder can have a number of layouts set.
See overview below.
These layouts are important when the project is exported, as they indicate how to treat the content in terms of formatting, headings and page breaks.
the layout selected also shows up as flags in the tree view, making it easier to track what kind of files they are.

* **Title Page**: The title page layout.
  The title should be formatted as a heading level one.
* **Book**: In principle, the entire novel can be contained in a single file.
  In that case, use the Book layout on this file.
  The internal structure is then controlled by the heading levels.
* **Plain Page**: A plain page is just that,
  It is not included into content and the heading levels are ignored.
* **Partition**: A partition can be used to split a the novel into parts.
  Use a level one heading for this.
* **Chapter**: Signifies the start of a new chapter.
  If the text itself is contained in scene files, these files should only contain the title and tag references for characters, plot, etc.
  The heading for chapters should be level two.
* **Unnumbered**: Same as Chapter, but when exporting the files and automatic chapter numbering is enabled, this file will not receive a number.
* **Scene**: A scene file.
  This file should have a header of level three.
  Further sections can have headers of level four.
  These will not impact the overall structure, but will allow for setting new characters and plot references in parts of a scene if such granularity is needed.
* **Note**: A generic file that is optionally ignored when the novel is exported.

.. note::
   The layout granularity is entirely optional.
   In principle, you can write the entire novel in a single file with layout "Book".
   You can also have a single file per chapter.
