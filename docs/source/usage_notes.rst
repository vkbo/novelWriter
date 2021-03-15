.. _a_notes:

*************
Project Notes
*************

novelWriter doesn't have a database and complicated forms for filling in details about plot
elements, characters, and all sorts of additional information that isn't a part of the novel text
itself. Instead, all such information is saved in notes that are written and maintained just like
all other text in your project.

The relation between all these additional elements is extracted from the documents and notes by the
project indexer, based on the tags and references you set within them.

Using notes is not required, but making at least minimal notes for each plot element, and adding a
tag to them, makes it possible to use the :guilabel:`Outline` feature to see how each element
intersects with each section of the novel itself, and adds clickable cross-references between
documents in the editor and viewer.


.. _a_notes_tags:

Tags in Notes
=============

Each new heading in a note can have a tag associated with it. The format of a tag is
``@tag: tagname``, where tagname is a unique identifier. Tags can then be referenced in the novel
documents, or cross-referenced in other notes, and will show up in the outline view and in the
back-reference panel when a document is being viewed. See :ref:`a_struct_tags` for how to reference
notes.

The syntax highlighter will alert the user that the keyword is correctly used and that the tag is
allowed, that is, the tag is unique. Duplicate tags should be detected as long as the index is up
to date. An invalid tag should have a green wiggly line under it, and will not receive the syntax
colour that valid tags do.

The tag is the only part of these notes that the application uses. The rest of the document content
is there for the writer to use in whatever way they wish. Of course, the content of the documents
can be exported if you want to compile a single document of all your notes, or include them in an
outline.

A note can also reference other notes in the same way novel documents do. When the note is opened
in the view panel, the references become clickable links, making it easier to follow connections in
the plot. Notes don't show up in the outline view though, so referencing between notes is only
meaningful if you want to be able to click-navigate between them.

.. tip::
   If you cross-reference between notes and export your project as an HTML document using the
   :guilabel:`Build Novel Project` tool, the cross-references become clickable links in the
   exported HTML document.
