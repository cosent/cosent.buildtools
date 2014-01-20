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
        # disable the default lowercase transformation
        self.versions.optionxform = lambda option: option
        if not self.versions.read(versionsfile):
            raise(AssertionError("Invalid file: %s" % versionsfile))
        assert self.versions.has_section("versions")

    def get_version(self, pkg):
        pkg = self.escape(pkg)
        if self.versions.has_option("versions", pkg):
            return self.versions.get("versions", pkg)
        return None

    def set_version(self, pkg, version):
        pkg = self.escape(pkg)
        self.versions.set("versions", pkg, version)

    def write(self):
        with open(self.versionsfile, 'w') as fh:
            self.versions.write(fh)

    def escape(self, pkg):
        return pkg.replace("_", "-")


def git_status(path):
    cmd = subprocess.Popen("git status",
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    return stdout.strip()


def is_git_clean(path):
    status = git_status(path)
    if 'nothing to commit' in status:
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
    version = bv.get_version(path, True)
    return version in tags


def tagged_version_is_head(path):
    cmd = subprocess.Popen("git tag --contains HEAD",
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    tags = stdout.strip().split('\n')
    version = bv.pkg_version(path)
    return version in tags


def version_is_final(path):
    version = bv.pkg_version(path)
    return 'rc' not in version and 'dev' not in version


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
        cmd = subprocess.Popen("bin/develop info -p %s" % pkg,
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
    # merge and resplit
    args = " ".join(args).split()
    print("mkrelease %s" % args)
    exit_code = jarn_mkrelease(args)
    if exit_code != 0:
        print("jarn.mkrelease failed, aborting.")
        sys.exit(exit_code)


def buildtool_status():
    print(BASEDIR)
    print(git_status(BASEDIR))
    for (pkg, path) in devel_eggs().items():
        print('\n' + path)
        print(git_status(path))


def buildtool_cook(final=True, noact=False, skipchecks=False, force=False):
    if not skipchecks and not is_all_clean():
        print("Buildout is not clean, aborting!\n"
              "================================\n")
        return buildtool_status()

    # commit, and tag egg versions
    for (pkg, path) in devel_eggs().items():
        if should_cook(path, final, force):
            new_version = bv.bump_pkg(path, final, noact)
            git_commit(path, new_version, noact)
            git_tag(path, new_version, noact)
        else:
            # already released, unchanged
            print('%s: == %s' % (path, bv.pkg_version(path)))


def should_cook(path, final=True, force=False):
    if force:
        return True
    elif not version_is_tagged(path):
        # no tags at all, cook a release
        return True
    elif final and not version_is_final(path):
        # force rc->final version bump even if no code changes
        return True
    elif tagged_version_is_head(path):
        # already released, leave unchanged
        return False
    else:
        # code changed, cook
        return True


def buildtool_dist(versionsfile,
                   distlocation,
                   buildname=None,
                   final=True,
                   noact=False,
                   skipchecks=False,
                   force=False):
    assert versionsfile
    assert distlocation
    if not buildname:
        buildname = BASEDIR.split('/')[-1]

    if not skipchecks and not is_all_clean():
        print("Buildout is not clean, aborting!\n"
              "================================\n")
        return buildtool_status()

    vp = VersionParser(versionsfile)

    # release changed eggs
    changed = []
    for (pkg, path) in devel_eggs().items():
        print("\n--- %s ---" % pkg)
        oldversion = vp.get_version(pkg)
        newversion = bv.pkg_version(path)
        if oldversion == newversion and not force:
            print("%s: == %s" % (pkg, oldversion))
        else:
            changed.append(pkg)
            print("%s: %s -> %s" % (pkg, oldversion, newversion))
            vp.set_version(pkg, newversion)
            mkrelease(path, distlocation, noact)

    # force rc->final release even if *nothing* changed
    if final and not version_is_final(BASEDIR):
        changed.append(buildname)

    if not force and not changed and tagged_version_is_head(BASEDIR):
        print("Nothing changed, nothing to release. Aborting.")
        return

    print("\n====== %s ======" % buildname)
    # buildout version. requires a setup.py
    buildout_version = bv.bump_pkg(BASEDIR, final, noact)
    # release tag is identical across repos: build.name=0.4rc3
    release_tag = "%s=%s" % (buildname, buildout_version),

    # release, and tag buildout version on all eggs
    for (pkg, path) in devel_eggs().items():

        # this adds the buildout version tag to all eggs
        git_tag(path, release_tag, noact)
        git_push(path, noact)

    if not noact:
        vp.write()

    vp.set_version(buildname, buildout_version)
    git_commit(BASEDIR, buildout_version, noact)
    # version tag to match setup.py version
    git_tag(BASEDIR, buildout_version, noact)
    # release tag to match egg release tags
    git_tag(BASEDIR, release_tag, noact)
    mkrelease(BASEDIR, distlocation, noact)
    git_push(BASEDIR, noact)


def git_all(args, noact=False):
    print "Inspecting devel eggs, hang on..."
    for (pkg, path) in devel_eggs().items():
        print("\n--- %s ---" % pkg)
        git_cmd(path, args, noact)
    print("\n====== %s ======" % BASEDIR)
    git_cmd(BASEDIR, args, noact)


def git_cmd(path, args, noact=False):
    git = "git %s" % " ".join(args)
    print("%s: %s" % (path, git))
    if noact:
        return
    cmd = subprocess.Popen(git,
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    print(stdout)


def main(defaults={}):
    parser = OptionParser()
    if 'versions-file' in defaults:
        parser.set_defaults(versionsfile=defaults['versions-file'])
    if 'dist-location' in defaults:
        parser.set_defaults(distlocation=defaults['dist-location'])
    if 'build-name' in defaults:
        parser.set_defaults(buildname=defaults['build-name'])
    parser.add_option("-c", "--release-candidate",
                      action="store_false", dest="final", default=True,
                      help="Do not bump a final version, bump a RC instead.")
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
                      action="store_true", dest="skipchecks",
                      help="Skip sanity checks.")
    parser.add_option("-f", "--force",
                      action="store_true", dest="force",
                      help="Force release, even of unchanged packages.")
    usage = _usage % dict(script=sys.argv[0])
    parser.set_usage(usage)
    (options, args) = parser.parse_args()
    if not args:
        print(usage)
        return

    cmd = args[0]

    if cmd == 'status':
        buildtool_status()

    elif cmd == 'cook':
        buildtool_cook(options.final,
                       options.noact,
                       options.skipchecks,
                       options.force)

    elif cmd == 'dist':
        if not options.versionsfile:
            print("Missing argument: -v VERSIONSFILE")
            print(usage)
            return
        if not options.distlocation:
            print("Missing argument: -d DISTLOCATION")
            print(usage)
            return

        buildtool_dist(options.versionsfile,
                       options.distlocation,
                       options.buildname,
                       options.final,
                       options.noact,
                       options.skipchecks,
                       options.force)

    elif cmd == 'git':
        gitargs = args[1:]
        if gitargs:
            git_all(gitargs, options.noact)
        else:
            print("'%s git log', or '%s git whatchanged', or ...?"
                  % (sys.argv[0], sys.argv[0]))

    else:
        print "No such command: %s" % cmd
        print(usage)
        return

_usage = """

%(script)s status
    List uncommitted changes in all working trees.

%(script)s [-n] [-f] [-s] [-c] cook
    Bump version, commit and tag all eggs that have unreleased commits.

    [-n]          dry run, no changes
    [-f]          force a new release, even if no changes
    [-s]          skip sanity check, accept uncommitted changes
    [-c]          create RC (0.1->0.2rc1) instead of final version (0.1->0.2)


%(script)s [-n] [-f] [-s] [-c] <-v versions> <-d dist> [-b name] dist
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
    [-b name]     build name, defaults to name of buildout directory

%(script)s git <gitargs>
    Run 'git gitargs' on all development eggs, and on the buildout itself.
    Insert '--' or use extra quoting to escape arguments passed to git.
    Examples:
        bin/buildtool git -- log --oneline HEAD^^..
        bin/buildtool git "commit -a -m 'your commit message'"

"""

if __name__ == '__main__':
    sys.exit(main())
