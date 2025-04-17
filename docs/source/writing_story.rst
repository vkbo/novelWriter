.. _a_story_structure:

************************
Story Structure Comments
************************

.. _The Story Grid: https://storygrid.com


As of version 2.7, story structure annotations using the ``%story`` style of comment is supported.
To use the feature, make the first word of a comment ``story``, followed by a period, a structure
term, a colon, a space and the text for that term.

Here's an example:

.. code-block:: md

   %story.term: text

.. versionadded:: 2.7


Usage
=====

The story term can be anything that you want to track in the manuscript. This construct is intended
to make it easier to extract metadata from a work to perform a structural analysis of the story.

There are probably as many ways to examine story structure as there are authors and editors
combined. For this reason the story tag is flexible. You can use any terms you want and track any
aspect of the story that serves your purposes.

An example method has been advanced by Shawn Coyne in `The Story Grid`_. This method asserts that a
story is composed of "beats", and that each beat has an inciting incident, a complication, a
crisis, and a resolution. One might capture these elements of a beat where a character overcomes
their fear of giving a speech as:

.. code-block:: md

   ### Scene

   %Synopsis: Carol overcomes her fear of giving a speech.

   %Story.incite: Carol is pleased to be invited to a conference to see her boss deliver a keynote.
   %Story.complication: Carol's boss calls in sick and asks her to deliver a big speech.
   %Story.crisis: Carol has a fear of appearing on stage.
   %Story.resolution: Carol engages the help of a coach who helps her overcome her fears and delivers a great speech.

Other analytical models propose tracking a scene's pace, how it affects the mood of the story, or
which element(s) of the story's genre are being satisfied. An author can use this mechanism to
track any element of a scene. Some examples include time of day, how much time passes in the scene,
or even the physical form of a shape-shifting character. If a story involves magic, one could track
which wand a main character has in hand. It's up to tha author.

When the story and other scene metadata is extracted into a tabular form, it is possible to get a
comprehensive overview of the story and to identify possible issues. For example, so many
fast-paced scenes without a break that readers might become fatigued or over-stimulated.


Output
======

The story structure comments can be included in the manuscript, and are formatted similarly to
the synopsis comments:

.. figure:: images/fig_story_structure_manuscript.png

   A set of story structure comments as shown in the Manuscript tool.

When you export your project data from the Outline View, all story structure terms are added as
columns to the exported file, which can then be opened in the spread sheet software of your choice.
