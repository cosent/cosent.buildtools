import unittest
import os
import subprocess

from cosent.buildtools import buildtool as bt
from cosent.buildtools import bumpversion as bv

dummypath = "%s/src/dummypackage" % os.getcwd()


class TestGit(unittest.TestCase):

    def setUp(self):
        cmd = subprocess.Popen("git reset --hard HEAD",
                               shell=True,
                               cwd=dummypath,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
        stdout, stderr = cmd.communicate()

    def test_git_clean_true(self):
        self.assertTrue(bt.is_git_clean(dummypath))

    def test_git_clean_false(self):
        marker = "%s/REMOVE_THIS_FILE" % dummypath
        subprocess.call(["touch", marker])
        self.assertFalse(bt.is_git_clean(dummypath))
        subprocess.call(["rm", marker])

    def test_version_is_tagged(self):
        self.assertFalse(bt.version_is_tagged(dummypath))

    def test_version_is_current(self):
        self.assertFalse(bt.version_is_current(dummypath))


class TestDevelEggs(unittest.TestCase):

    def test_devel_eggs(self):
        pkginfo = {'dummypackage': dummypath}
        self.assertEqual(bt.devel_eggs(),
                         pkginfo)
