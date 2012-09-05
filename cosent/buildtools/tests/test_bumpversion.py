import unittest
import os
import tempfile

from cosent.buildtools import bumpversion as bv


class TestBumpVersion(unittest.TestCase):

    def test_rc2rc(self):
        self.assertEquals(bv.bump_rc('2.8rc1'), '2.8rc2')
        self.assertEquals(bv.bump_rc('2.8rc9'), '2.8rc10')
        self.assertEquals(bv.bump_rc('2.8rc19'), '2.8rc20')
        self.assertEquals(bv.bump_rc('2.8.rc19'), '2.8.rc20')

    def test_final2rc(self):
        self.assertEquals(bv.bump_rc('2.7'), '2.8rc1')
        self.assertEquals(bv.bump_rc('2.7.1'), '2.7.2rc1')

    def test_final2final(self):
        self.assertEquals(bv.bump_final('1'), '2')
        self.assertEquals(bv.bump_final('2.7'), '2.8')
        self.assertEquals(bv.bump_final('2.7.9'), '2.7.10')

    def test_rc2final(self):
        self.assertEquals(bv.bump_final('2.8rc3'), '2.8')
        self.assertEquals(bv.bump_final('2.8.rc3'), '2.8')


class TestRewriteSetup(unittest.TestCase):

    def setUp(self):
        # populate a tmp file from our dummy template
        dummy_path = '%s/cosent/buildtools/tests/_dummysetup.py' % (
            os.getcwd())
        with open(dummy_path, 'r') as fh:
            dummy_setup = fh.read()
        (_osfh, setup_filename) = tempfile.mkstemp()
        os.close(_osfh)  # don't use the low-level IO
        with open(setup_filename, 'w') as fh:
            fh.write(dummy_setup)

        # for use in tests
        self.temp_filename = setup_filename
        self.dummy_filename = dummy_path
        self.dummy_setup = dummy_setup

    def tearDown(self):
        os.remove(self.temp_filename)

    def test_get_version(self):
        self.assertEquals(bv.get_version(self.dummy_setup.splitlines()), '0.1')

    def test_bump_setup_py_rc(self):
        bv.bump_setup_py(self.temp_filename)
        with open(self.temp_filename, 'r') as fh:
            new_setup = fh.read().splitlines()
        diff = []
        for oldline in self.dummy_setup.splitlines():
            newline = new_setup.pop(0)
            if oldline != newline:
                diff.append((oldline, newline))
        self.assertEquals(diff, [("version = '0.1'", "version = '0.2rc1'")])

    def test_bump_setup_py_final(self):
        bv.bump_setup_py(self.temp_filename, final=True)
        with open(self.temp_filename, 'r') as fh:
            new_setup = fh.read().splitlines()
        diff = []
        for oldline in self.dummy_setup.splitlines():
            newline = new_setup.pop(0)
            if oldline != newline:
                diff.append((oldline, newline))
        self.assertEquals(diff, [("version = '0.1'", "version = '0.2'")])
