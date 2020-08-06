.. _a_notes:

************************
Supporting Files (Notes)
************************

Supporting files, or notes, are any file stored in root folders that are not a part of the novel
story itself. These files are intended for summaries and outlines of the various plot elements,
characters, locations, and so on, of the novel.

These files are not required, but making at least minimal files for each such plot element, and add
a tag to them, makes it possible to use the :guilabel:`Outline` feature to see how each element
intersects with each section of the novel itself, and add clickable cross-references between
documents in the editor and viewer.


.. _a_notes_tags:

Tags in Notes
=============

Each new heading in a note file can have a tag associated with it. The format of a tag is
``@tag: tagname``, where tagname is a unique identifier. Tags can then be referenced in the novel
files, or other note files, and will show up in the outline view and in the back-reference panel
when a document is being viewed.

The syntax highlighter will alert the user that the keyword is correctly used and that the tag is
allowed, that is, the tag is unique. Duplicate tags should be detected as long as the index is up
to date. An invalid tag should have a green wiggly line under it, and will not receive the syntax
colour that valid tags do.

The tag is the only part of these files that the application uses. The rest of the file content is
there for the writer to use in whatever way they wish. Of course, the content of the files can be
exported if you want to compile a single document of all your notes, or include them in an outline.

A note file can also reference other note files in the same way novel files do. When the note file
is opened in the view pane, these become clickable links, making it easier to follow connections in
the plot. Note files don't show up in the outline view though, so referencing between notes is only
meaningful if you want to be able to click-navigate between them.

.. tip::
   If you cross-reference between notes as well, and export your project as an HTML file using the
   export tool, the cross-references also become clickable in the exported document.
