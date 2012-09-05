Low-level buildout helper scripts to manage complex buildout releases.

Status: alpha. Is limited to release patterns used at `Cosent`_.

See Makefile and buildout for examples of providing the script entry points in a buildout.


bumpversion
===========

To bump the version to the next rc::

    $ bumpversion ./path/some.egg/setup.py

To bump the version to the next final release::

    $ bumpversion --final ./path/some.egg/setup.py

Version algorithm is as follows:

* rc (release candidate)::

    2.7    -> 2.8rc1
    2.8rc1 -> 2.8rc2

* final (actual release)::

    2.7    -> 2.8
    2.8rc2 -> 2.8

The algorithm is dump and only understands major/minor and rc.
Different version numbers like 2.7dev4, 2.8b3, 2.8-fix2 will cause breakage. 

YMMV.


.. _Cosent: http://cosent.nl
