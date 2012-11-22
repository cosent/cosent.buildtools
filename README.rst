.. image:: https://secure.travis-ci.org/cosent/cosent.buildtools.png
    :target: http://travis-ci.org/cosent/cosent.buildtools


Introduction
============

Cosent.buildtools allows you to release a buildout with multiple development eggs in one go. 

The intent is, to offer at the buildout/project level, the convenience that `jarn.mkrelease`_ offers at the individual egg level.

Cosent.buildtools will:

* Generate a new version number for any development eggs with unreleased changes; also for any RC released eggs if you're doing a 'final' release.
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
* The versioning algorithm understands only a very simple versioning scheme, like 0.2, 0.2dev and 0.2rc4. See below.

This suites the release patterns used at `Cosent`_. YMMV.


Installation
============

Add the following to your buildout.cfg::

    [buildout]
    parts += buildtools

    [buildtools]
    recipe = zc.recipe.egg
    eggs = cosent.buildtools

This will install two scripts: buildtool, and bumpversion.


buildtool
=========

*buildtool status* checks your complete working tree for changes::

  buildtool status
    List uncommitted changes in all working trees.

*buildtool cook* prepares your eggs for release::

  buildtool [-n] [-f] [-s] [-c] cook
    Bump version, commit and tag all eggs that have unreleased commits.

    [-n]          dry run, no changes
    [-f]          force a new release, even if no changes
    [-s]          skip sanity check, accept uncommitted changes
    [-c]          create RC (0.1->0.2rc1) instead of final version (0.1->0.2)

*buildtool dist* releases all eggs and the buildout itself in one go::

  buildtool [-n] [-f] [-s] [-c] <-v versions> <-d dist> [-b name] dist
    Release and upload all changed eggs to distserver (via jarn.mkrelease).
    Update and commit buildout versionsfile to reflect the new egg versions.
    Tag the buildout and tag all eggs with the buildout version tag.
    Push all commits and tags in all eggs and the buildout.

    [-n]          dry run, no changes
    [-f]          force a new release, even if no changes
    [-s]          skip sanity check, accept uncommitted changes
    [-c]          create RC (0.1->0.2rc1) instead of final version (0.1->0.2)

    <-v versions> path to buildout versions.txt file
    <-d dist>     pypirc dist location to use for uploading eggs
    [-b name]     name of current buildout, defaults to dirname

*buildtool git* runs a git command on all eggs and on the buildout::

  buildtool git <gitargs>
    Run 'git gitargs' on all development eggs, and on the buildout itself.
    Insert '--' or use extra quoting to escape arguments passed to git.
    Examples:
        bin/buildtool git -- log --oneline HEAD^^..
        bin/buildtool git "commit -a -m 'your commit message'"


Example run::

    bin/buildtool git tag                  # list tags
    bin/buildtool git whatchanged sometag  # list changes since last release

    bin/buildtool status                   # check that we're clean
    bin/buildtool cook                     # prepare release
    # the actual release
    bin/buildtool -v versions.txt -d your.server:/var/pypi dist

Contrary to jarn.mkrelease, buildtool expects clean sandboxes. It will abort if it encounters uncommitted work, unless you use the -s (--skip-checks) switch.

Specifying default arguments
----------------------------

You can specify default settings by initializing a 'defaults' dictionary, and then feed the defaults as an argument to the script. Due to some script generation snafu, you'll have to specify a different script name for this to work.

If you modify your buildout like this::

    [buildtools]
    recipe = zc.recipe.egg
    eggs = cosent.buildtools
    scripts = buildtool=release
    initialization = defaults = {
      'versions-file':'versions.txt',
      'dist-location':'pypi',
      'build-name': 'cosent.buildtools'}
    arguments = defaults

Where of course you'll need to supply your own dist-location, for example 'your.server.net:/var/www/packages/local' and set build-name to your own project name. You can use any dist-location jarn.mkrelease accepts, including aliases defined in your .pypirc.

You will now have a separate ``bin/release`` script that is set up with the defaults, which means you can simply run::

    bin/release status
    bin/release cook
    bin/release dist


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
    2.8dev -> 2.8rc1
    2.8rc1 -> 2.8rc2

* final (actual release)::

    2.7    -> 2.8
    2.8dev -> 2.8
    2.8rc2 -> 2.8

The algorithm is dumb and only understands major.minor + "rc|dev" + seq.
Different version numbers like 2.8b3, 2.8-fix2 will cause breakage. 


.. _Cosent: http://cosent.nl
.. _jarn.mkrelease: http://pypi.python.org/pypi/jarn.mkrelease
