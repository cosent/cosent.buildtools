import unittest
import os
import subprocess
import tempfile

from cosent.buildtools import buildtool as bt
from cosent.buildtools import bumpversion as bv

dummypath = "%s/src/cosent.dummypackage" % os.getcwd()


class TestGit(unittest.TestCase):

    def setUp(self):
        # reset src/cosent.dummypackage
        cmd = subprocess.Popen("git reset --hard HEAD",
                               shell=True,
                               cwd=dummypath,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
        stdout, stderr = cmd.communicate()
        # stash cosent.buildtools
        cmd = subprocess.Popen("git stash",
                               shell=True,
                               cwd=os.getcwd(),
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
        stdout, stderr = cmd.communicate()
        if 'HEAD is now at' in stdout:
            self.stashed = True
        else:
            self.stashed = False

    def tearDown(self):
        if not self.stashed:
            return
        cmd = subprocess.Popen("git stash pop",
                               shell=True,
                               cwd=os.getcwd(),
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
        stdout, stderr = cmd.communicate()

    def test_git_clean_true(self):
        self.assertTrue(bt.is_git_clean(dummypath),
                        bt.git_status(dummypath))

    def test_git_clean_false(self):
        marker = "%s/REMOVE_THIS_FILE" % dummypath
        subprocess.call(["touch", marker])
        self.assertFalse(bt.is_git_clean(dummypath))
        subprocess.call(["rm", marker])

    def test_all_clean_true(self):
        self.assertTrue(
            bt.is_all_clean(),
            "\n%s:\n%s\n\n%s:\n%s" % (
                dummypath, bt.git_status(dummypath),
                bt.BASEDIR, bt.git_status(bt.BASEDIR)))

    def test_all_clean_false(self):
        marker = "%s/REMOVE_THIS_FILE" % dummypath
        subprocess.call(["touch", marker])
        self.assertFalse(bt.is_all_clean())
        subprocess.call(["rm", marker])

    def test_version_is_tagged(self):
        self.assertTrue(bt.version_is_tagged(dummypath),
                        bv.pkg_version(dummypath))

    def test_tagged_version_is_head(self):
        self.assertTrue(bt.tagged_version_is_head(dummypath),
                        bv.pkg_version(dummypath))

    def test_version_is_final(self):
        bv.bump_pkg(dummypath, final=False)
        self.assertFalse(bt.version_is_final(dummypath),
                         bv.pkg_version(dummypath))
        bv.bump_pkg(dummypath, final=True)
        self.assertTrue(bt.version_is_final(dummypath),
                        bv.pkg_version(dummypath))


class TestDevelEggs(unittest.TestCase):

    def test_devel_eggs(self):
        pkginfo = {'cosent.dummypackage': dummypath}
        self.assertEqual(bt.devel_eggs(),
                         pkginfo)


class TestVersionParser(unittest.TestCase):

    def setUp(self):
        (_osfh, _filename) = tempfile.mkstemp()
        os.close(_osfh)  # don't use the low-level IO
        with open(_filename, 'w') as fh:
            fh.write(dummy_versions)
        self._versions = _filename

    def tearDown(self):
        os.remove(self._versions)

    def test_init_noarg(self):
        self.assertRaises(AssertionError, bt.VersionParser, None)

    def test_init_nosection(self):
        with open(self._versions, 'w') as fh:
            fh.write("[duh]\nfoo=bar")
        self.assertRaises(AssertionError, bt.VersionParser, self._versions)

    def test_get_ok(self):
        vp = bt.VersionParser(self._versions)
        self.assertEquals(vp.get_version('foo.bar'), '0.2rc3')

    def test_get_nosuch(self):
        vp = bt.VersionParser(self._versions)
        self.assertEquals(vp.get_version('boo.baz'), None)

    def test_set_update(self):
        vp = bt.VersionParser(self._versions)
        vp.set_version('foo.bar', '0.2rc4')
        self.assertEquals(vp.get_version('foo.bar'), '0.2rc4')

    def test_set_new(self):
        vp = bt.VersionParser(self._versions)
        vp.set_version('boo.baz', '1.1')
        self.assertEquals(vp.get_version('boo.baz'), '1.1')

    def test_get_underscored(self):
        vp = bt.VersionParser(self._versions)
        self.assertEquals(vp.get_version('silly_me.pkg'), '2.1')
        self.assertEquals(vp.get_version('silly-me.pkg'), '2.1')

    def test_set_update_underscored(self):
        vp = bt.VersionParser(self._versions)
        vp.set_version('silly_me.pkg', '2.2')
        self.assertEquals(vp.get_version('silly_me.pkg'), '2.2')
        self.assertEquals(vp.get_version('silly-me.pkg'), '2.2')

    def test_write(self):
        vp = bt.VersionParser(self._versions)
        vp.set_version('foo.bar', '0.2rc4')
        vp.write()
        with open(self._versions, 'r') as fh:
            versions = fh.read()
        self.assertEqual(versions.strip(), new_versions.strip())

dummy_versions = """
[buildout]
eggs += foo.bar

[versions]
foo.bar = 0.2rc3
Products.baz = 0.3.rc5
silly-me.pkg = 2.1
"""

new_versions = """
[buildout]
eggs += foo.bar

[versions]
foo.bar = 0.2rc4
Products.baz = 0.3.rc5
silly-me.pkg = 2.1
"""
