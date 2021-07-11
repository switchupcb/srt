Quickstart
==========

Parse an SRT to Python objects
------------------------------

.. code:: python

    >>> import srt
    >>> subtitle_generator = srt.parse('''\
    ... 1
    ... 00:31:37,894 --> 00:31:39,928
    ... OK, look, I think I have a plan here.
    ...
    ... 2
    ... 00:31:39,931 --> 00:31:41,931
    ... Using mainly spoons,
    ...
    ... 3
    ... 00:31:41,933 --> 00:31:43,435
    ... we dig a tunnel under the city and release it into the wild.
    ...
    ... ''')
    >>> subtitles = list(subtitle_generator)
    >>>
    >>> subtitles[0].start
    datetime.timedelta(0, 1897, 894000)
    >>> subtitles[1].content
    'Using mainly spoons,'

Compose an SRT from Python objects
----------------------------------

.. code:: python

    >>> print(srt.compose(subtitles))
    1
    00:31:37,894 --> 00:31:39,928
    OK, look, I think I have a plan here.
    <BLANKLINE>
    2
    00:31:39,931 --> 00:31:41,931
    Using mainly spoons,
    <BLANKLINE>
    3
    00:31:41,933 --> 00:31:43,435
    we dig a tunnel under the city and release it into the wild.
    <BLANKLINE>

Import Guide
------------

.. code:: python

    ### Use srt via srt.func()
    # import the whole srt package (including tools)
    import srt

    # only imports the srt.py module
    from srt import srt

    ### Use srt tools
    import srt
    # srt.tools.tool.func()
    srt.tools.find.find_by_timestamp()

    from srt import tools
    # tools.tool.func()
    tools.find.find_by_timestamp()

    # import all members from a tool module.
    from srt.tools.find import *
    find_by_timestamp()
