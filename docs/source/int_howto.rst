.. _a_howto:

*************
Tips & Tricks
*************

.. _Discussions Page: https://github.com/vkbo/novelWriter/discussions

This is a list of hopefully helpful little tips on how to get the most out of novelWriter.

.. note::
   This section will be expanded over time, and if you would like to have something added, feel
   free to contribute, or start a discussion on the project's `Discussions Page`_.


Managing the Project
====================

.. dropdown:: Merge Multiple Documents Into One
   :animate: fade-in-slide-down

   If you need to merge a set of documents in your project into a single document, you can achieve
   this by first making a new folder for just that purpose, and drag all the files you want merged
   into this folder. Then you can right click the folder, select :guilabel:`Transform` and
   :guilabel:`Merge Documents in Folder`.

   In the dialog that pops up, the documents will be in the same order as in the folder, but you
   can also rearrange them here of you wish. See :ref:`a_ui_tree_split_merge` for more details.


Layout Tricks
=============

.. dropdown:: Create a Simple Table
   :animate: fade-in-slide-down

   The formatting tools available in novelWriter don't allow for complex structures like tables.
   However, the editor does render tabs in a similar way that regular word processors do. You can
   set the width of a tab in :guilabel:`Preferences`.

   The tab key should have the same distance in the editor as in the viewer, so you can align text
   in columns using the tab key, and it should look the same when viewed next to the editor.

   This is most suitable for your notes, as the result in exported documents cannot be guaranteed
   to match.


Organising Your Text
====================

.. dropdown:: Add Introductory Text to Chapters
   :animate: fade-in-slide-down

   Sometimes chapters have a short preface, like a brief piece of text or a quote to set the stage
   before the first scene begins.

   If you add separate files for chapters and scenes, the chapter file is the perfect place to add
   such text. Separating chapter and scene files also allows you to make scene files child
   documents of the chapter (added in novelWriter 2.0).

.. dropdown:: Distinguishing Soft and Hard Scene Breaks
   :animate: fade-in-slide-down

   Depending on your writing style, you may need to separate between soft and hard scene breaks
   within chapters. Like for instance if you switch point-of-view character often.

   In such cases you may want to use the scene heading for hard scene breaks and section headings
   for soft scene breaks. the :guilabel:`Build Manuscript` tool will let you add separate
   formatting for the two when you generate your manuscript. You can for instance add the common
   "``* * *``" for hard breaks and select to hide section breaks, which will just insert an empty
   paragraph in their place. See :ref:`a_manuscript_settings` for more details.


Other Tools
===========

.. dropdown:: Convert Project to/from yWriter Format
   :animate: fade-in-slide-down

   There is a tool available that lets you convert a `yWriter <http://spacejock.com/yWriter7.html>`_
   project to a novelWriter project, and vice versa.

   The tool is available at `peter88213.github.io/yw2nw <https://peter88213.github.io/yw2nw/>`__
