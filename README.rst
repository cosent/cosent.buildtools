Low-level buildout helper scripts to manage complex buildout releases.

Status: alpha. Is limited to release patterns used at `Cosent`_.


bumpversion
===========

Enable automated version numbering. Handy for use in conjunction with `jarn.mkrelease`_ which breaks if the number isn't incremented.

To make the bumpversion script available in your buildout bin directory, add the following to buildout.cfg::

    [buildout]
    parts += bumpversion

    [bumpversion]
    recipe = zc.recipe.egg
    eggs = cosent.buildtools
    scripts = bumpversion


To bump a version to the next release candidate::

    $ bin/bumpversion ./src/some.egg/setup.py

To bump a version to the next final release::

    $ bin/bumpversion --final ./src/some.egg/setup.py

Version algorithm is as follows:

* rc (release candidate)::

    2.7    -> 2.8rc1
    2.8rc1 -> 2.8rc2

* final (actual release)::

    2.7    -> 2.8
    2.8rc2 -> 2.8

The algorithm is dumb and only understands major.minor + rc.
Different version numbers like 2.7dev4, 2.8b3, 2.8-fix2 will cause breakage. 

YMMV.


.. _Cosent: http://cosent.nl
.. _jarn.mkrelease: http://pypi.python.org/pypi/jarn.mkrelease
