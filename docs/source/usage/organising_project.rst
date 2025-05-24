.. _docs_usage_project:

***********************
Organising Your Project
***********************

Your project is organised into a set of top level folders called "Root Folders", which each have
specific meaning in the project. Your project documents and notes are stored under these root
folders. All the content of your project is available in the **Project Content** panel on the left
side of the main window.

.. figure:: images/fig_project_tree.png

   The **Project Content** tree populated with example documents.

Each line in the project tree shows the label of each item, its word count (or alternatively
character count), an active/inactive icon (see :ref:`docs_features_active`), and a custom status
icon (see :ref:`docs_features_status`).

You can add, view and edit the documents in the project tree by right-clicking on them. Some
features are also located in the buttons along the top next to the **Project Content** label.


.. _docs_usage_project_roots:

How Root Folders Work
=====================

Projects are structured into a set of top level folders called "Root Folders". They are visible in
the project tree at the left side of the main window.

The documents that make up your story go into a root folder of type **Novel**. Your notes go into
the other root folders. These other root folder types are separated into types depending on what
kind of notes go into them. This is not only for organisation. It also matters to how you can
reference these notes later. We will come back to this in the :ref:`docs_usage_tags_refs` section.

A new project may not have all of the root folders present, but you can add the ones you want from
the project tree tool bar.

The intended usage of each type of root folder is listed below. However, aside from the **Novel**
folder, no restrictions are applied by the application on what you put in them. You can use them
however you want.


Root Folder Types
-----------------

**Novel** (Story)
   This is where you put the documents that are part of your story. You can create multiple Novel
   folders if you wish, but various parts of the application assumes each Novel folder belong to
   one novel.

   The Novel folder is somewhat special in that it can contain documents for chapters, scenes and
   story partitions. How this is indicated is covered in the section :ref:`docs_usage_headers`.

**Plot** (Notes)
   This is where you can keep notes and outlines of your story plots. Such notes can be
   particularly useful if you have outlines for sub plot. You can make references to these subplots
   from the scene documents, which makes it easier to track story progress.

**Characters** (Notes)
   Character notes go in this root folder type. For your main characters, you may want to make one
   document for each character. For smaller characters you can put multiple into the same document.
   In your chapters and scenes you can reference these character notes as Point of View or Focus
   characters.

**Locations** (Notes)
   The locations where your story takes place can be documented here. This, together with Plot and
   Characters are the particularly useful story elements to track, and to reference from your
   chapter and scene documents.

**Timeline** (Notes)
   If the story has multiple plot timelines or jumps in time within the same plot, this folder type
   can be used to track this.

**Objects** (Notes)
   Important objects in the story, for instance physical objects that change hands often, can be
   tracked here.

**Entities** (Notes)
   Does your plot have many powerful organisations or companies? Or other entities that are part of
   the plot? They can be organised here.

**Custom** (Notes)
   The custom root folder type can be used for tracking anything else not covered by the above
   options.

**Archive**
   If you don't want to delete a document, or put it in the **Trash** folder where it may be
   deleted, but still want it out of your main project, you can put it in this folder. The contents
   of the document will be ignored by the scanner that looks for tags, and it will be ignored in
   any outline view and in your manuscript.

**Trash**
   This folder behaves like you expect. Anything dropped in here can be deleted permanently from
   the project, and the content doesn't show up anywhere else in novelWriter.

The root folders are closely tied to the tags and reference system. Each folder type except
**Archive** and **Trash** corresponds to one or more categories of tags that can be used to
reference the content in them. See :ref:`docs_usage_tags_refs` for more details.

.. tip::

   The root folders have standard names, but you can rename them to whatever you want.


.. _docs_usage_project_folders:

Regular Folders
===============

Regular folders, those that are not root folders, have no structural significance to the project.
When novelWriter is processing the documents in a project, like for instance when you create a
manuscript from it, these folders are ignored. Only the order of the documents themselves matter.

The folders are there purely as a way for you to organise the documents in meaningful sections and
to be able to collapse and hide them in the project tree when you're not working on those
documents.
