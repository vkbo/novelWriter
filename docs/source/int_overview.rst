.. _a_overview:

********
Overview
********

.. only:: html

   .. image:: images/python_powered.png
      :align: right
      :width: 220

novelWriter is built as a cross-platform application using `Python 3 <https://www.python.org/>`_ as
the programming language, and `Qt 5 <https://www.qt.io/>`_ for the user interface.

novelWriter is built for Linux first, and this is where it works best. However, it also runs fine
on Windows and MacOS due to the cross-platform framework it's built on. The author of the
application doesn't own a Mac, so on-going Mac support is dependent on user feedback and user
contributions.

Spell checking in novelWriter is provided by a third party library called
`Enchant <https://abiword.github.io/enchant/>`_. Please see the section on :ref:`a_custom_dict` for
how to install spell checking languages.

For install instructions, see :ref:`a_started`.


Using novelWriter
=================

In order to use novelWriter effectively, you need to know the basics of how it works. The following
chapters will explain the main principles. It starts with the basics, and gets more detailed as you
read on.

:ref:`a_breakdown` – Essential Information
   This chapter explains the basics of how the application works and what it can and cannot do.

:ref:`a_ui_project` – Recommended Reading
   This chapter will give you a more detailed explanation of how you can use the user interface components
   to organise and view your project work.

:ref:`a_ui_writing` – Recommended Reading
   This chapter will give you a more detailed explanation of how the text editor and viewer work.

:ref:`a_fmt` – Essential Information
   This chapter covers how you should format your text. The editor is plain text, so text
   formatting requires some basic markup. The structure of your novel is also inferred by how you
   use headings. Tags and references are implemented by special keywords.

:ref:`a_kb` – Optional / Lookup
   This chapter lists all the keyboard shortcuts in novelWriter and what they do. Most of the
   shortcuts are also listed next to their menu entries inside the app, or in tool tips. This
   chapter is mostly for reference.

:ref:`a_typ` – Optional
   This chapter gives you an overview of the special typographical symbols available in
   novelWriter. The auto-replace feature can handle the insertion of standard quote symbols for
   your language, and other special characters. If you use any symbols aside from these. their
   intended use is explained here.

:ref:`a_prjfmt` – Optional
   This chapter is more technical and has an overview of changes made to the way your project data
   is stored. The format has changed a bit from time to time, and sometimes the changes require
   that you make small modifications to your project. Everything you need to know is listed in this
   chapter.


Organising Your Projects
========================

In addition to managing a collection of plain text files, novelWriter can interpret and map the
structure of your novel and show you additional information about its flow and content. In order
to take advantage of these features, you must structure your text in a specific way and add some
meta data for it to extract.

:ref:`a_proj` – Essential Information
   This chapter explains how you organise the content of your project, and how to set up automated
   backups of your work.

:ref:`a_struct` – Essential Information
   This chapter covers the way your novel's structure is encoded into the text documents. It
   explains how the different levels of headings are used, and some special formatting for
   different kinds of headings.

:ref:`a_references` - Recommended Reading
   This chapter explains how you organise your notes, and how the Tags and References system works.
   This system lets you cross-link your documents in your project, and display these references in
   the application interface.

:ref:`a_manuscript` - Recommended Reading
   This chapter explains how the :guilabel:`Manuscript Build` tool works, how you can control the
   way chapter titles are formatted, and how scene and section breaks are handled.
