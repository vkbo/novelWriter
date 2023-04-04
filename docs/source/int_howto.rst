.. _a_howto:

*************
Tips & Tricks
*************

.. _Discussions Page: https://github.com/vkbo/novelWriter/discussions

This is a list of hopefully helpful little tips on how to get the most out of novelWriter.

.. note::

    This section will be expanded over time, and if you would like to have something added, feel
    free to contribute, or start a discussion on the project's `Discussions Page`_


Overview
========

**Managing the Project**

* :ref:`a_howto_merge_documents`

**Layout Tricks**

* :ref:`a_howto_simple_table`

**Organising Your Text**

* :ref:`a_howto_chapter_intro`
* :ref:`a_howto_soft_hard_breaks`

**Other Tools**

* :ref:`a_howto_convert_ywriter`


How-Tos
=======


Managing the Project
--------------------


.. _a_howto_merge_documents:

Merge Multiple Documents Into One
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you need to merge a set of documents in your project into a single document, you can achieve
this by first making a new folder for just that purpose, and drag all the files you want merged
into this folder. Then you can right click the folder, select :guilabel:`Transform` and
:guilabel:`Merge Documents in Folder`.

In the dialog that pops up, the documents will be in the same order as in the folder, but you can
also rearrange them here of you wish.


Layout Tricks
-------------


.. _a_howto_simple_table:

Create a Simple Table
^^^^^^^^^^^^^^^^^^^^^

The formatting tools available in novelWriter don't allow for complex structures like tables.
However, the editor does render tabs in a similar way to regular word processors. You can set the
width of a tab in :guilabel:`Preferences`.

The tab key should have the same distance in the editor as in the viewer, so you can align text in
columns using the tab key, and it should look the same when viewed next to the editor.

This is most suitable for your notes, as the result in exported documents cannot be guaranteed to
match.


Organising Your Text
--------------------


.. _a_howto_chapter_intro:

Add Introductory Text to Chapters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes chapters have a short preface, like a brief piece of text or a quote to set the stage
before the first scene -- Some text that may not be a part of the actual following scene.

If you add separate files for chapters and scenes, this is the perfect place to add such text.
Separating chapter and scene files also allows you to set meta data for the whole chapter. Like
list all characters present in the chapter, etc.


.. _a_howto_soft_hard_breaks:

Distinguishing Soft and Hard Scene Breaks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on your writing style, you may need to separate between soft and hard scene breaks within
chapters. Like for instance if you switch point-of-view character often.

In such cases you may want to use the scene heading for hard scene breaks and section headings for
soft scene breaks. the :guilabel:`Project Build Tool` will let you add separate formatting for the
two when you generate your manuscript. You can for instance add the common "``* * *``" for hard
breaks and select to hide section breaks, which will just insert an empty paragraph in their place.


Other Tools
-----------


.. _a_howto_convert_ywriter:

Convert Project to/from yWriter Format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _yWriter: http://spacejock.com/yWriter7.html

There is a tool available that lets you convert a yWriter_ project to a novelWriter project, and
vice versa.

The tool is available at `peter88213.github.io/yw2nw <https://peter88213.github.io/yw2nw/>`__
