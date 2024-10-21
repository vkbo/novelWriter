.. _a_custom:

**************
Customisations
**************

.. _Enchant: https://rrthomas.github.io/enchant/
.. _Free Desktop: https://cgit.freedesktop.org/libreoffice/dictionaries/tree/

There are a few ways you can customise novelWriter yourself. Currently, you can add new GUI themes,
your own syntax themes, and install additional dictionaries.


.. _a_custom_dict:

Spell Check Dictionaries
========================

novelWriter uses Enchant_ as the spell checking tool. Depending on your operating system, it may or
may not load all installed spell check dictionaries automatically.

Linux and MacOS
---------------

On Linux and MacOS, you generally only have to install hunspell, aspell or myspell dictionaries on
your system like you do for other applications. See your distro or OS documentation for how to do
this. These dictionaries should show up as available spell check languages in novelWriter.

Windows
-------

For Windows, English is included with the installation. For other languages you have to download
and add dictionaries yourself.

**Install Tool**

A small tool to assist with this can be found under **Tools > Add Dictionaries**. It will import
spell checking dictionaries from Free Office or Libre Office extensions. The dictionaries are then
installed in the install location for the Enchant library and should thus work for any application
that uses Enchant for spell checking.

**Manual Install**

If you prefer to do this manually or want to use a different source than the ones mentioned above,
You need to get compatible dictionary files for your language. You need two files files ending with
``.aff`` and ``.dic``. These files must then be copied to the following location: 

``C:\Users\<USER>\AppData\Local\enchant\hunspell``

This assumes your user profile is stored at ``C:\Users\<USER>``. The last one or two folders may
not exist, so you may need to create them.

You can find the various dictionaries on the `Free Desktop`_ website.

.. note::
   The Free Desktop link points to a repository, and what may look like file links inside the
   dictionary folder are actually links to web pages. If you right-click and download those, you
   get HTML files, not dictionaries!

   In order to download the actual dictionary files, right-click the "plain" label at the end of
   each line and download that.


.. _a_custom_theme:

Syntax and GUI Themes
=====================

Adding your own GUI and syntax themes is relatively easy, although it requires that you manually
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
file, otherwise you may not be able to distinguish them in **Preferences**.

For novelWriter to be able to locate the custom theme files, you must copy them to the
:ref:`a_locations_data` location in your home or user area. There should be a folder there named
``syntax`` for syntax themes, just ``themes`` for GUI themes, and ``icons`` for icon themes. These
folders are created the first time you start novelWriter.

Once the files are copied there, they should show up in **Preferences** with the label you
set as ``name`` inside the file.

.. versionadded:: 2.0
   The ``icontheme`` value was added to GUI themes. Make sure you set this value in existing custom
   themes. Otherwise, novelWriter will try to guess your icon theme, and may not pick the most
   suitable one.


Custom GUI and Icons Theme
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
   helptext        =   0,   0,   0
   fadedtext       = 128, 128, 128
   errortext       = 255,   0,   0
   statusnone      = 120, 120, 120
   statussaved     =   2, 133,  37
   statusunsaved   = 200,  15,  39

In the Main section you must at least define the ``name`` and ``icontheme`` settings. The
``icontheme`` settings should correspond to one of the internal icon themes, either
``typicons_light`` or ``typicons_dark``, or to an icon theme in your custom icons directory. The
setting must match the icon theme's folder name.

The Palette values correspond to the Qt enum values for ``QPalette::ColorRole``, see the
`Qt documentation <https://doc.qt.io/qt-5.15/qpalette.html#ColorRole-enum>`_ for more details. The
colour values are RGB numbers on the format ``r, g, b`` where each is an integer from ``0`` to
``255``. Omitted values are not loaded and will use default values. If the ``helptext`` colour is
not defined, it is computed as a colour between the ``window`` and ``windowtext`` colour.

.. versionadded:: 2.5
   The ``fadedtext`` and ``errortext`` theme colour entries were added.


Custom Syntax Theme
-------------------

A syntax theme ``.conf`` file consists of the following settings:

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
   dialog         =   0,   0,   0
   altdialog      =   0,   0,   0
   note           =   0,   0,   0
   hidden         =   0,   0,   0
   shortcode      =   0,   0,   0
   keyword        =   0,   0,   0
   tag            =   0,   0,   0
   value          =   0,   0,   0
   optional       =   0,   0,   0
   spellcheckline =   0,   0,   0
   errorline      =   0,   0,   0
   replacetag     =   0,   0,   0
   modifier       =   0,   0,   0
   texthighlight  = 255, 255, 255, 128

In the Main section, you must define at least the ``name`` setting. The Syntax colour values are
RGB(A) numbers of the format ``r, g, b, a`` where each is an integer from ``0`` to ``255``. The
fourth value is the alpha channel, which can be omitted.

Omitted syntax colours default to black, except ``background`` which defaults to white, and
``texthighlight`` which defaults to white with half transparency.

.. versionadded:: 2.2
   The ``shortcode`` syntax colour entry was added.

.. versionadded:: 2.3
   The ``optional`` syntax colour entry was added.

.. versionadded:: 2.4
   The ``texthighlight`` syntax colour entry was added.

.. versionadded:: 2.5
   The ``dialog``, ``altdialog``, ``note`` and ``tag`` syntax colour entries were added.
   ``straightquotes``, ``doublequotes`` and ``singlequotes`` were removed.
