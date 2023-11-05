.. _a_custom:

**************
Customisations
**************

.. _Enchant: https://abiword.github.io/enchant
.. _Free Desktop: https://cgit.freedesktop.org/libreoffice/dictionaries/tree/

There are a few ways you can customise novelWriter youself. Currently, you can add new GUI themes,
your own syntax themes, and install additional dictionaries.


.. _a_custom_dict:

Spell Check Dictionaries
========================

novelWriter uses Enchant_ as the spell checking tool. Depending on your operating system, it may or
may not load all installed spell check dictionaries automatically.

Linux and MacOS
---------------

On Linux and MacOS, you generally only have to install hunspell or aspell dictionaries on your
system like you do for other applications. See your distro or OS documentation for how to do this.
These dictionaries should show up as available spell check languages in novelWriter.

Windows
-------

For Windows, English is included with the installation. For other languages you have to download
and add dictionaries yourself. You can find the various dictionaries on the `Free Desktop`_
website. You should find a folder for your language, if it is available at all, and download the
files ending with ``.aff`` and ``.dic``. These files must then be copied to the following location:

``C:\Users\<USER>\AppData\Local\enchant\hunspell``

This assumes your user profile is stored at ``C:\Users\<USER>``. The last one or two folders may
not exist, so you may need to create them.

.. note::
   The Free Desktop link points to a repository, and what may look like file links inside the
   dictionary folder are actually links to web pages. If you right-click and download those, you
   get HTML files, not dictionaries!

   In order to download the actual dictionary files, right-click the "plain" label at the end of
   each line and download that.


.. _a_custom_theme:

Syntax and GUI Themes
=====================

Adding your own GUI and syntax themes is relatively easy, altough it requires that you manually
edit config files with colour values. The themes are defined by simple plain text config files with
meta data and colour settings.

In order to make your own versions, first copy one of the existing files to your local computer and
modify it as you like.

* The existing syntax themes are stored in
  `novelwriter/assets/syntax <https://github.com/vkbo/novelWriter/tree/main/novelwriter/assets/syntax>`_.
* The existing GUI themes are stored in
  `novelwriter/assets/themes <https://github.com/vkbo/novelWriter/tree/main/novelwriter/assets/themes>`_.
* The existing icon themes are stored in
  `novelwriter/assets/icons <https://github.com/vkbo/novelWriter/tree/main/novelwriter/assets/icons>`_.

Remember to also change the name of your theme by modifying the ``name`` setting at the top of the
file, otherwise you may not be able to distinguish them in :guilabel:`Preferences`.

For novelWriter to be able to locate the custom theme files, you must copy them to the
:ref:`a_locations_data` location in your home or user area. There should be a folder there named
``syntax`` for syntax themes, just ``themes`` for GUI themes, and ``icons`` for icon themes. These
folders are created the first time you start novelWriter.

Once the files are copied there, they should show up in :guilabel:`Preferences` with the label you
set as ``name`` inside the file.

.. versionadded:: 2.0
   The ``icontheme`` value was added to GUI themes. Make sure you set this value in existing custom
   themes. Otherwise, novelWriter will try to guess your icon theme, and may not pick the most
   suitable one.


Gustom GUI and Icons Theme
--------------------------

A GUI theme ``.conf`` file consists of the following settings:

.. code-block:: cfg

   [Main]
   name        = My Custom Theme
   description = A description of my custom theme
   author      = Jane Doe
   credit      = John Doe
   url         = https://example.com
   license     = CC BY-SA 4.0
   licenseurl  = https://creativecommons.org/licenses/by-sa/4.0/
   icontheme   = typicons_light

   [Palette]
   window          = 100, 100, 100
   windowtext      = 100, 100, 100
   base            = 100, 100, 100
   alternatebase   = 100, 100, 100
   text            = 100, 100, 100
   tooltipbase     = 100, 100, 100
   tooltiptext     = 100, 100, 100
   button          = 100, 100, 100
   buttontext      = 100, 100, 100
   brighttext      = 100, 100, 100
   highlight       = 100, 100, 100
   highlightedtext = 100, 100, 100
   link            = 100, 100, 100
   linkvisited     = 100, 100, 100

   [GUI]
   statusnone      = 100, 100, 100
   statussaved     = 100, 100, 100
   statusunsaved   = 100, 100, 100

In the Main section you must at least define the ``name`` and ``icontheme`` settings. The
``icontheme`` settings should correspond to one of the internal icon themes, either
``typicons_light`` or ``typicons_dark``, or to an icon theme in your custom icons directory. The
setting must match the icon theme's folder name.

The Palette values correspond to the Qt enum values for QPalette::ColorRole, see the
`Qt documentation <https://doc.qt.io/qt-5.15/qpalette.html#ColorRole-enum>`_ for more details. The
colour values are RGB numbers on the format ``r, g, b`` where each is an integer from  to 255.
Omitted values are not loaded and will use default values.


Custom Syntax Theme
-------------------

A syntax theme ``.conf`` file consists of the follwing settings:

.. code-block:: cfg

   [Main]
   name       = My Syntax Theme
   author     = Jane Doe
   credit     = John Doe
   url        = https://example.com
   license    = CC BY-SA 4.0
   licenseurl = https://creativecommons.org/licenses/by-sa/4.0/

   [Syntax]
   background     = 255, 255, 255
   text           =   0,   0,   0
   link           =   0,   0,   0
   headertext     =   0,   0,   0
   headertag      =   0,   0,   0
   emphasis       =   0,   0,   0
   straightquotes =   0,   0,   0
   doublequotes   =   0,   0,   0
   singlequotes   =   0,   0,   0
   hidden         =   0,   0,   0
   keyword        =   0,   0,   0
   value          =   0,   0,   0
   spellcheckline =   0,   0,   0
   errorline      =   0,   0,   0
   replacetag     =   0,   0,   0
   modifier       =   0,   0,   0

In the Main section, you must define at least the ``name`` setting. The Syntax colour values are
RGB numbers of the format ``r, g, b`` where each is an integer from  to 255. Omitted values default
to black, except ``background`` which defaults to white,
