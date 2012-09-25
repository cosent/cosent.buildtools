from optparse import OptionParser
from ConfigParser import ConfigParser
import sys
import subprocess
import os

from jarn.mkrelease.mkrelease import main as jarn_mkrelease

import bumpversion as bv

BASEDIR = os.getcwd()


class VersionParser(object):

    def __init__(self, versionsfile):
        assert versionsfile
        self.versionsfile = versionsfile
        self.versions = ConfigParser()
        if not self.versions.read(versionsfile):
            raise(AssertionError("Invalid file: %s" % versionsfile))
        assert self.versions.has_section("versions")

    def get_version(self, pkg):
        if self.versions.has_option("versions", pkg):
            return self.versions.get("versions", pkg)
        return None

    def set_version(self, pkg, version):
        self.versions.set("versions", pkg, version)

    def write(self):
        with open(self.versionsfile, 'w') as fh:
            self.versions.write(fh)


def git_status(path):
    cmd = subprocess.Popen("git status",
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    return stdout.strip()


def is_git_clean(path):
    lines = git_status(path).split('\n')
    if 'nothing to commit (working directory clean)' in lines[-1]:
        return True
    else:
        return False


def is_all_clean():
    clean = True
    if not is_git_clean(BASEDIR):
        clean = False
    for (pkg, path) in devel_eggs().items():
        if not is_git_clean(path):
            clean = False
    return clean


def version_is_tagged(path):
    cmd = subprocess.Popen("git tag -l",
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    tags = stdout.strip().split('\n')
    version = bv.get_version("%s/setup.py" % path)
    return version in tags


def version_is_current(path):
    cmd = subprocess.Popen("git tag -l",
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    head = stdout.strip().split('\n')[0]
    version = bv.pkg_version(path)
    return version == head


def git_tag(path, tag, noact=False):
    git = "git tag %s" % tag
    print("%s: %s" % (path, git))
    if noact:
        return
    cmd = subprocess.Popen(git,
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()


def git_commit(path, tag, noact=False):
    git = "git commit -a -m 'Preparing release %s'" % tag
    print("%s: %s" % (path, git))
    if noact:
        return
    cmd = subprocess.Popen(git,
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()


def git_push(path, noact=False):
    git = "git push; git push --tags"
    print("%s: %s" % (path, git))
    if noact:
        return
    cmd = subprocess.Popen(git,
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()


def devel_eggs():
    cmd = subprocess.Popen("bin/develop ls -c",
                           shell=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    packages = stdout.strip().split('\n')
    pkginfo = {}
    for pkg in packages:
        cmd = subprocess.Popen(["bin/develop info -p", pkg],
                               shell=True,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
        stdout, stderr = cmd.communicate()
        pkgpath = stdout.strip()
        pkginfo[pkg] = pkgpath
    return pkginfo


def mkrelease(path, dist, noact=False):
    args = ["-CT"]  # already committed and tagged by us
    args.append("-q")  # quiet please
    if noact:
        args.append("-n")
    args.append("-d %s" % dist)
    args.append(path)
    print("mkrelease %s" % " ".join(args))
    jarn_mkrelease(args)


def buildtool_status():
    print(BASEDIR)
    print(git_status(BASEDIR))
    for (pkg, path) in devel_eggs().items():
        print('\n' + path)
        print(git_status(path))


def buildtool_cook(final=False, noact=False, force=False):
    if not force and not is_all_clean():
        print("Buildout is not clean, aborting!\n"
              "================================\n")
        return buildtool_status()

    # commit, and tag egg versions
    for (pkg, path) in devel_eggs().items():
        if not version_is_current(path):
            new_version = bv.bump_pkg(path, final, noact)
            git_commit(path, new_version, noact)
            git_tag(path, new_version, noact)
        else:
            print('%s: == %s' % (path, bv.pkg_version(path)))


def buildtool_release(versionsfile,
                      distlocation,
                      buildname=None,
                      final=False,
                      noact=False,
                      force=False):
    assert versionsfile
    assert distlocation
    if not buildname:
        buildname = BASEDIR.split('/')[-1]

    if not force and not is_all_clean():
        print("Buildout is not clean, aborting!\n"
              "================================\n")
        return buildtool_status()

    vp = VersionParser(versionsfile)

    # buildout version. requires a setup.py
    buildout_version = bv.bump_pkg(BASEDIR, final, noact)
    # release tag is identical across repos: build.name=0.4rc3
    release_tag = "%s=%s" % (buildname, buildout_version),

    # release, and tag buildout version on all eggs
    for (pkg, path) in devel_eggs().items():
        print("\n--- %s ---" % pkg)
        oldversion = vp.get_version(pkg)
        newversion = bv.pkg_version(path)
        if oldversion == newversion:
            print("%s: == %s" % (pkg, oldversion))
        else:
            print("%s: %s -> %s" % (pkg, oldversion, newversion))
            vp.set_version(pkg, newversion)
            mkrelease(path, distlocation, noact)
            # this adds the buildout version tag to all eggs
            git_tag(path, release_tag, noact)
            git_push(path, noact)

    if not noact:
        vp.write()

    print("\n====== %s ======" % buildname)
    vp.set_version(buildname, buildout_version)
    git_commit(BASEDIR, buildout_version, noact)
    git_tag(BASEDIR, release_tag, noact)
    mkrelease(BASEDIR, distlocation, noact)
    git_push(BASEDIR, noact)


def main(defaults={}):
    parser = OptionParser()
    if 'versions-file' in defaults:
        parser.set_defaults(versionsfile=defaults['versions-file'])
    if 'dist-location' in defaults:
        parser.set_defaults(distlocation=defaults['dist-location'])
    if 'build-name' in defaults:
        parser.set_defaults(buildname=defaults['build-name'])
    parser.add_option("-f", "--final",
                      action="store_true", dest="final", default=False,
                      help="Bump a final version")
    parser.add_option("-n", "--dry-run",
                      action="store_true", dest="noact", default=False,
                      help="Dry run. Don't change anything.")
    parser.add_option("-d", "--dist-location",
                      action="store", dest="distlocation",
                      help="scp location or .pypirc index server")
    parser.add_option("-v", "--versions-file",
                      action="store", dest="versionsfile",
                      help="Path to versions.txt.")
    parser.add_option("-b", "--build-name",
                      action="store", dest="buildname",
                      help="Name for this buildout.")
    parser.add_option("-s", "--skip-checks",
                      action="store_true", dest="force",
                      help="Skip sanity checks.")
    usage = _usage % dict(script=sys.argv[0])
    parser.set_usage(usage)
    (options, args) = parser.parse_args()
    if not args:
        print(usage)
        return

    for cmd in args:

        if cmd == 'status':
            buildtool_status()

        elif cmd == 'cook':
            buildtool_cook(options.final, options.noact, options.force)

        elif cmd == 'release':
            if not options.versionsfile:
                print("Missing argument: -v VERSIONSFILE")
                print(usage)
                return
            if not options.distlocation:
                print("Missing argument: -d DISTLOCATION")
                print(usage)
                return

            buildtool_release(options.versionsfile,
                              options.distlocation,
                              options.buildname,
                              options.final,
                              options.noact,
                              options.force)
        else:
            print "No such command: %s" % cmd
            print(usage)
            return

_usage = """

%(script)s status
    List uncommitted changes in all working trees.

%(script)s [-n] [-f] cook
    Bump version, commit and tag all eggs that have unreleased commits.

    [-n]          dry run, no changes
    [-f]          final version (0.1->0.2), else creates RC (0.1->0.2rc1)

%(script)s [-n] [-f] <-v versions> <-d dist> [-b name] release
    Release all changed eggs (via jarn.mkrelease).
    Update and commit buildout versionsfile to reflect the new egg versions.
    Tag the buildout and tag all eggs with the buildout version tag.
    Push all commits and tags in all eggs and the buildout.

    [-n]          dry run, no changes
    [-f]          final version (0.1->0.2), else creates RC (0.1->0.2rc1)
    <-v versions> path to buildout versions.txt file
    <-d dist>     pypirc dist location to use for uploading eggs
    [-b name]     build name, defaults to name of buildout directory

"""

if __name__ == '__main__':
    sys.exit(main())
