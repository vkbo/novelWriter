.. _a_custom:

**************
Customisations
**************

There are a few ways you can customise novelWriter youself. Currently, you can add new GUI themes,
your own syntax themes, and install additional dictionaries.


.. _a_custom_dict:

Spell Check Dictionaries
========================

novelWriter uses `Enchant <https://abiword.github.io/enchant/>`_ as the spell checking tool.
Depending on you operating system, it may or may not load installed spell check dictionaries.

Linux
   On Linux, you generally only have to install hunspell or aspell dictionaries on your system like
   you do for other applications. See your distro's documentation for how to do this.

Windows
   For Windows, English is included with the installation. For other languages you have to download
   and add dictionaries yourself. You can find the various dictionaries on the
   `Free Desktop <https://cgit.freedesktop.org/libreoffice/dictionaries/tree/>`_ website. You should
   find a folder for your language, if it is available at all, and download the files ending with
   ``.aff`` and ``.dic``. These files must then be copied to the following location:

   ``C:\Users\<USER>\AppData\Local\enchant\hunspell``

   This assumes your user profile is stored at ``C:\Users\<USER>``. The last one or two folders may
   not exist, so you may need to create them.


.. _a_custom_theme:

Syntax and GUI Themes
=====================

Adding your own GUI and syntax themes is relatively easy. The themes are defined by simple plain
text config files with meta data and colour settings.

In order to make your own versions, first copy one of the existing files to your local computer and
modify it as you like.

* The existing syntax themes are stored in
  `novelwriter/assets/syntax <https://github.com/vkbo/novelWriter/tree/main/novelwriter/assets/syntax>`_.
* The existing GUI themes are stored in
  `novelwriter/assets/themes <https://github.com/vkbo/novelWriter/tree/main/novelwriter/assets/themes>`_.

Remember to also change the name of your theme by modifying the ``name`` setting at the top of the
file.

For novelWriter to be able to locate the custom theme files, you must copy them to the
:ref:`a_locations_data` location in your home or user area. There should be a folder there named
``syntax`` for syntax themes and just ``themes`` for GUI themes.

Once the files are copied there, they should show up in :guilabel:`Preferences` with the label you
set as ``name`` inside the file.


Theme CSS Files
---------------

If you wish, you can also modify the CSS styles of the GUI in addition to change colour settings.
This is only available for GUI themes, and you do this by creating a file with the exact same file
name as the ``.conf`` file with colour settings and give it the ``.qss`` extension.

On Windows, file extensions may not be visible by default, so make sure you only have one file
extension, and don't end up with two.

The QSS files are Qt Style Sheet files. See Qt's
`The Style Sheet Syntax <https://doc.qt.io/qt-5/stylesheet-syntax.html>`_` documentation for more
details.
