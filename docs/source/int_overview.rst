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
on Windows and MacOS due to being built with cross-platform tools. The author of the application
doesn't own a Mac, so on-going Mac support is dependant on user feedback and user contributions.

Spell checking in novelWriter is provided by a third party library called
`Enchant <https://abiword.github.io/enchant/>`_. Please see the section on :ref:`a_custom_dict` for
how to handle spell checking in different languages.

For install instructions, see :ref:`a_started`.


Using novelWriter
=================

In order to use novelWriter effectively, you need to know the basics of how it works. The following
sections will explain the main principles. It starts with the basics, and gets more detailed as you
read on.

:ref:`a_breakdown` – Essential Information
   This section explains the basics of how the application works and what it can and cannot do.

:ref:`a_ui` – Recommended Reading
   This section will give you a more detailed explanation of what the various elements on the user
   interface do and how you can use them more effectively.

:ref:`a_fmt` – Essential Information
   This section covers how you should format your text. The editor is plain text, so text
   formatting requires some basic markup. The structure of your novel is also inferred by how you
   use headings. Tags and references are implemented by special keywords.

:ref:`a_kb` – Optional / Lookup
   This section lists all the keyboard shortcuts in novelWriter and what they do. Most of the
   shortcuts are also listed next to the menu items inside the app, or in tool tips, so this
   section is mostly for reference.

:ref:`a_typ` – Optional
   This section gives you an overview of the special typographical symbols available in
   novelWriter. The auto-replace feature can handle the insertion of standard quote symbols for
   your language, and other special characters. If you use any symbols aside from these. their
   intended use is explained here.

:ref:`a_prjfmt` – Optional
   This section is more technical and has an overview of changes made to the way your project data
   is stored. The format has changed a bit from time to time, and sometimes the changes require
   that you make small modifications to your project. Everything you need to know is listed in this
   section.


Organising Your Projects
========================

In addition to manage a collection of plain text files, novelWriter can interpret and map the
structure of your novel and show you additional information about its flow and content. In order
to take advantage of these features, you must structure your text in a specific way and add some
meta data for it to extract.

:ref:`a_proj` – Essential Information
   This section explains how you organise the content of your project, and how to set up automated
   backups of your work.

:ref:`a_struct` – Essential Information
   This section covers the way your novel's structure is encoded into the text documents. It
   explains how the different levels of headings are used, and how you can include information
   about characters, plot elements, and other meta data in your text.

:ref:`a_notes` - Recommended Reading
   This section briefly describes what novelWriter does with the note files you add to your
   project. Generally, the application doesn't do much with them at all aside from looking through
   them for tags you've set so that it knows which file to open when you click on a reference.

:ref:`a_export` - Recommended Reading
   This section explains in more detail how the build tool works. In particular how you can
   control the way chapter titles are formatted, and how scene and section breaks are handled.
