.. _a_overview:

********
Overview
********

.. only:: html

   .. image:: images/python_powered.png
      :align: right
      :width: 220

novelWriter is built on `Python 3 <https://www.python.org/>`_, a cross platform programming
language that doesn't require a compiler to build and run. That means that the code can run on your
computer right out of the box, or from a zip file.

While it is developed for Linux primarily, it runs just fine on Windows as well. It also works fine
on macOS, but the author is not a mac user, so support for mac is dependant on user feedback and
contributions.

In order to run novelWriter, you also need a few additional packages. The user interface is built
with `Qt 5 <https://www.qt.io/>`_, a cross platform library for building graphical user interface
applications. It also uses a third party XML package. If you want spell checking, you also need the
spell check package Enchant developed for AbiWord

For install instructions, see :ref:`a_started`.

For information on how to add spell check dictionaries, see :ref:`a_custom_dict`.


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
   use headings. Tags and references are implemented by simple codes.

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
