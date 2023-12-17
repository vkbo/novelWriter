.. _a_references:

*******************
Tags and References
*******************

In novelWriter there are no forms or tables to fill in to define the characters, locations and
other elements of your story. Instead, you can mark your :term:`project notes` as representing
these story elements by creating a :term:`tag`. Whenever you want to link a piece of your story to
a note defining a story element, like a character, you create a :term:`reference` back to that tag.
You can also cross-link your project notes in the same way.

This is perhaps one of the features that makes novelWriter different from other, similar
applications. It is therefore not always obvious to new users how this is supposed to work, so
this chapter hopes to explains in more detail how to use the tags and references system.

.. tip::
   If you find the Tags and Reference system difficult to follow just from reading this chapter,
   you can create a new project in novelWriter and select to "Fill the project with example files"
   in the :guilabel:`New Project Wizard`. The example project contains several examples of tags and
   references.


.. _a_references_metadata:

Metadata in novelWriter
=======================

The structure of your novelWriter project is inferred from the :term:`headings` within the
documents, not the documents themselves. See :ref:`a_struct_heads` for more details. Therefore,
metadata is also associated with headings, and not the documents directly.

If you split your project into separate documents for each scene, this distinction may not matter.
However, there are several benefits to using documents at a larger structural scale when starting
your project. For instance, it may make more sense to define all your scenes, and even chapters, in
a single document at first, or perhaps a document per act. You can later split these documents up
using the document split feature. See :ref:`a_ui_tree_split_merge` for more details.

The implication here is that you can treat each heading as an independent element of your notes
that can be referenced somewhere else. In order to make it possible to reference a header section,
you need to assign it a tag.


.. _a_references_tags:

How to Use Tags
===============

A "tag" in novelWriter is a word or phrase that you define as belonging to a heading. Tags are set
by using the ``@tags`` :term:`keyword`. The full format of a tag is ``@tag: tagname``, where
``tagname`` is an identifier of your choosing. You can only set *one* tag per heading, and the tag
has to be unique across all documents in the project.

.. versionadded:: 2.2
   Tags are now case insensitive.

After the tags have been defined, they can then be referenced in the novel documents, or
cross-referenced in other notes. they will also show up in the :guilabel:`Outline View` and in the
back-reference panel when a document is opened in the viewer.

The syntax highlighter will indicate to you that the keyword is correctly used and that the tag is
allowed, that is, the tag is unique. Duplicate tags should be detected as long as the index is up
to date. An invalid tag should have a green wiggly line under it, and will not receive the syntax
colour that valid tags do.

The tag is the only part of these notes that novelWriter uses. The rest of the document content is
there for you to use in whatever way you wish. Of course, the content of the documents can be added
to the manuscript, or an outline document. If you want to compile a single document of all your
notes, you can do this from the :guilabel:`Manuscript Build` tool.

Example of a heading with a tag for a character of the story:

.. code-block:: none

   # Jane Doe

   @tag: Jane

   Some information about the character Jane Doe.

When this is done in a document in a :term:`Root Folder` of type "Characters", the tag is
automatically treated as an available character in your project, and you will be able to reference
it in any of your other documents using the reference keywords for characters. It will also show up
in the Character tab in the Reference panel below the document viewer, and in the reference
auto-completer menu in the editor when you fill in references. See :ref:`a_ui_view` and
:ref:`a_references_completer`.

It is the root folder type that defines what category of story elements the tag is indexed under.
See the :ref:`a_proj_roots` section for an overview of available root folder types. They are also
covered in the next section.


.. _a_references_references:

How to Use References
=====================

Each heading of any level in your project can contain references to tags set in project notes. The
references are gathered by the indexer and used to generate the :guilabel:`Outline View`, among
other things.

References are set as a :term:`keyword` and a list of corresponding tags. The valid keywords are
listed below. The format of a reference line is ``@keyword: value1, [value2] ... [valueN]``. All
reference keywords allow multiple values.

``@pov``
   The point-of-view character for the current section. The target must be a note tag in a
   :guilabel:`Character` type root folder.

``@focus``
   The character that has the focus for the current section. This can be used in cases where the
   focus is not a point-of-view character. The target must be a note tag in a :guilabel:`Character`
   type root folder.

``@char``
   Other characters in the current section. The target must be a note tag in a
   :guilabel:`Character` type root folder. This should not include the point-of-view or focus
   character if those references are used.

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
   Objects present in the current section. The target must be a note tag in a :guilabel:`Object`
   type root folder.

``@entity``
   Entities present in the current section. The target must be a note tag in a
   :guilabel:`Entities` type root folder.

``@custom``
   Custom references in the current section. The target must be a note tag in a :guilabel:`Custom`
   type root folder. The custom folder are for any other category of notes you may want to use.

The syntax highlighter will alert the user that the tags and references are used correctly, and
that the tags referenced exist.

.. note::
   The highlighter may be mistaken if the index of defined tags is out of date. If so, press
   :kbd:`F9` to regenerate it, or select :guilabel:`Rebuild Index` from the :guilabel:`Tools` menu.
   In general, the index for a document is regenerated when it is saved, so this shouldn't normally
   be necessary.

.. tip::
   If you add a reference in the editor to a tag that doesn't yet exist, you can right-click it and
   select :guilabel:`Create Note for Tag`. This will generate a new project note automatically with
   the new tag defined. In order for this to be possible, a root folder for that category of
   references must already exist.

One note can also reference another note in the same way novel documents do. When the note is
opened in the document viewer, the references become clickable links, making it easier to follow
connections in the plot. You can follow links in the document editor by clicking them with the
mouse while holding down the :kbd:`Ctrl` key. Clicked links are always opened in the view panel.

Project notes don't show up in the :guilabel:`Outline View`, so referencing between notes is only
meaningful if you want to be able to click-navigate between them, or of course if you just want to
highlight that two notes are related.

.. tip::
   If you cross-reference between notes and export your project as an HTML document using the
   :guilabel:`Manuscript Build` tool, the cross-references become clickable links in the exported
   HTML document as well.

Example of a novel document with references to characters and plots:

.. code-block:: none

   ## Chapter 1

   @pov: Jane

   ### Scene 1

   @char: John, Sam
   @plot: Main

   Once upon a time ...


.. _a_references_completer:

The References Auto-Completer
-----------------------------

An auto-completer context menu will show up automatically in the document editor when you type the
character ``@`` on a new line. It will first suggest tag or reference keywords for you to add, and
after the ``:`` has been added, suggest references from the list of tags you have already defined.

You can use the auto-completer to add multiple references with a ``,`` between them, and even type
new ones. New references can be created by right-clicking on them and selecting
:guilabel:`Create Note for Tag` from the menu.

.. versionadded:: 2.2
