.. _a_glossary:

********
Glossary
********

.. glossary::
   :sorted:

   Root Folder
      A "Root Folder" is a top level folder of the project tree in novelWriter. Each type of root
      folder has a specific icon to identify it. For an overview of available root folder types,
      see :ref:`a_proj_roots`.

   Novel Documents
      These are documents that are created under a "Novel" :term:`Root Folder`. They behave
      differently than :term:`Project Notes`, and have some more restrictions. For instance, they
      can not exist in folders intended only for project notes. See the :ref:`a_struct` chapter for
      more details.

   Project Notes
      Project Notes are unrestricted documents that can be placed anywhere in your project. You
      should not use these documents for story elements, only for notes. Project notes are the
      source files used by the Tags and References system. See the :ref:`a_references` chapter for
      more details on how to use them.

   Tag
      A tag is a user defined value assigned as a tag to a section of your :term:`Project Notes`.
      It is optional, and can be defined once per heading. It is set using the :term:`keyword`
      syntax ``@tag: value``, where ``value`` is the user defined part. Each tag can be referenced
      in another file using one of the :term:`reference` keywords. See :ref:`a_references` chapter
      for more details.

   Reference
      A reference is one of a set of :term:`keywords<keyword>` that can be used to link to a
      :term:`tag` in another document. The reference keywords are specific to the different
      :term:`root folder` types. A full overview is available in the :ref:`a_references` chapter.

   Project Index
      The project index is a record of all headings in a project, with all their meta data like
      synopsis comments, :term:`tags<tag>` and :term:`references<reference>`. The project index is
      kept up to date automatically, but can also be regenerated manually from the
      :guilabel:`Tools` menu or by pressing :kbd:`F9`.

   Context Menu
      A context menu is a menu that pops up when you right click something in the user interface.
      In novelWriter, you can often also open a context menu by pressing the keyboard shortcut
      :kbd:`Ctrl+.`.

   Headings
      Each level of headings in :term:`Novel Documents` have a specific meaning in terms of the
      structure of the story. That is, they determine what novelWriter considers a partition, a
      chapter, a scene or a text section. For :term:`Project Notes`, the heading levels don't
      matter. For more details on headings in novel documents, see :ref:`a_struct_heads`.

   Keyword
      A keyword in novelWriter is a special command you put in the text of your documents. They are
      not standard Markdown, but are used in novelWriter to add information that is interpreted by
      the application. For instance, keywords are used for :term:`tags<tag>` and
      :term:`references<reference>`.

      Keywords must always be on their own line, and the first character of the line must always be
      the ``@`` character. The keyword must also always be followed by a ``:`` character, and the
      values passed to the command are added after this, separated by commas.
