Low-level buildout helper scripts to manage complex buildout releases.

Status: beta.

Summary
=======

Cosent.buildtools allows you to release a buildout with multiple development eggs in one go. 

The intent is, to offer at the buildout/project level, the convenience that `jarn.mkrelease`_ offers at the individual egg level.

Cosent.buildtools will:

* Generate a new version number for any development eggs with unreleased changes.
* Commit, tag and release all changed development eggs.
* Update the buildout version.txt to reflect the newly released eggs.
* Generate and store a new version number for the buildout itself.
* Tag all development eggs with the new buildout number as well.
* Commit, tag and release the buildout itself.



Assumptions/requirements/limitations
------------------------------------

* You have a buildout with multiple development eggs
* You have mr.developer installed, and use it to manage development status of eggs
* You have a [versions] section in the buildout configuration
* The buildout itself is a python egg with a setup.py version number
* The buildout and all development eggs are under git version control
* The versioning algorithm understands only a very simple versioning scheme, like 0.2 and 0.2rc4. See below.

This suites the release patterns used at `Cosent`_. YMMV.


Installation
============

Add the following to your buildout.cfg::

    [buildout]
    parts += buildtool

    [buildtool]
    recipe = zc.recipe.egg
    eggs = cosent.buildtools

This will install two scripts: buildtool, and bumpversion.


buildtool
=========

*buildtool status* checks your complete working tree for changes::

  buildtool status
    List uncommitted changes in all working trees.

*buildtool cook* prepares your eggs for release::

  buildtool [-n] [-f] [-s] cook
    Bump version, commit and tag all eggs that have unreleased commits.

    [-n]          dry run, no changes
    [-f]          final version (0.1->0.2), else creates RC (0.1->0.2rc1)
    [-s]          skip sanity check: force

*buildtool release* releases all eggs and the buildout itself in one go::

  buildtool [-n] [-f] [-s] <-v versions> <-d dist> [-b name] release
    Release all changed eggs (via jarn.mkrelease).
    Update and commit buildout versionsfile to reflect the new egg versions.
    Tag the buildout and tag all eggs with the buildout version tag.
    Push all commits and tags in all eggs and the buildout.

    [-n]          dry run, no changes
    [-f]          final version (0.1->0.2), else creates RC (0.1->0.2rc1)
    [-s]          skip sanity check: force
    <-v versions> path to buildout versions.txt file
    <-d dist>     pypirc dist location to use for uploading eggs
    [-b name]     name of current buildout, defaults to dirname

Example run::

    bin/buildtool status
    bin/buildtool -f cook
    bin/buildtool -f -v versions.txt -d scp://your.server/var/pypi release

Contrary to jarn.mkrelease, buildtool expects clean sandboxes. It will abort if it encounters uncommitted work.


bumpversion
===========

Enable automated version numbering. Handy for use in conjunction with `jarn.mkrelease`_ which breaks if the number isn't incremented.

This functionality is included in the buildtool wrapper, but also available as standalone utility.

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


.. _Cosent: http://cosent.nl
.. _jarn.mkrelease: http://pypi.python.org/pypi/jarn.mkrelease
