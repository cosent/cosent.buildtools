import subprocess
import os
from bumpversion import get_version

BASEDIR = os.getcwd()


def is_git_clean(path):
    cmd = subprocess.Popen("git status",
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    lines = stdout.strip().split('\n')
    if 'nothing to commit (working directory clean)' in lines[-1]:
        return True
    else:
        return False


def version_is_tagged(path):
    cmd = subprocess.Popen("git tag -l",
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    tags = stdout.strip().split('\n')
    version = get_version("%s/setup.py" % path)
    return version in tags


def version_is_current(path):
    cmd = subprocess.Popen("git tag -l",
                           shell=True,
                           cwd=path,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    head = stdout.strip().split('\n')[0]
    version = get_version("%s/setup.py" % path)
    return version == head


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
