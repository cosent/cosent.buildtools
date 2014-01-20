import unittest
import os
import tempfile

from cosent.buildtools import bumpversion as bv


class TestBumpVersion(unittest.TestCase):

    def test_splitversion_prefix(self):
        self.assertEquals(bv.splitversion('1.2-cosent-2.8'),
                          ('1.2-cosent', '2.8', '2.8', '', ''))

    def test_splitversion_final(self):
        self.assertEquals(bv.splitversion('2.8'),
                          ('', '2.8', '2.8', '', ''))

    def test_splitversion_dev(self):
        self.assertEquals(bv.splitversion('2.8dev'),
                          ('', '2.8dev', '2.8', '', ''))
        self.assertEquals(bv.splitversion('2.8dev2'),
                          ('', '2.8dev2', '2.8', '', '2'))

    def test_splitversion_rc(self):
        self.assertEquals(bv.splitversion('2.8rc'),
                          ('', '2.8rc', '2.8', '', ''))
        self.assertEquals(bv.splitversion('2.8rc1'),
                          ('', '2.8rc1', '2.8', '1', ''))

    def test_dev2rc(self):
        self.assertEquals(bv.bump_rc('2.8dev'), '2.8rc1')
        self.assertEquals(bv.bump_rc('2.8dev1'), '2.8rc1')
        self.assertEquals(bv.bump_rc('2.8.dev19'), '2.8.rc1')

    def test_dev2final(self):
        self.assertEquals(bv.bump_final('2.8dev'), '2.8')
        self.assertEquals(bv.bump_final('2.8dev1'), '2.8')
        self.assertEquals(bv.bump_final('2.8.dev19'), '2.8')

    def test_rc2rc(self):
        self.assertEquals(bv.bump_rc('2.8rc'), '2.8rc1')
        self.assertEquals(bv.bump_rc('2.8.rc0'), '2.8.rc1')
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

    def test_longnumbers(self):
        self.assertEquals(bv.bump_rc('3.4.5.6'), '3.4.5.7rc1')
        self.assertEquals(bv.bump_final('3.4.5.6'), '3.4.5.7')

    def test_weird(self):
        self.assertEquals(bv.bump_rc('3.4.rc5.7'), '3.4.rc6')
        self.assertEquals(bv.bump_final('3.4.rc5.7'), '3.4')

    def test_combined_dev(self):
        version = '1.1a2.dev0-cultact.1.0.dev'
        rc1 = '1.1a2.dev0-cultact.1.0.rc1'
        rc2 = '1.1a2.dev0-cultact.1.0.rc2'
        final = '1.1a2.dev0-cultact.1.0'
        self.assertEquals(bv.bump_rc(version), rc1)
        self.assertEquals(bv.bump_final(version), final)
        self.assertEquals(bv.bump_rc(rc1), rc2)
        self.assertEquals(bv.bump_final(rc1), final)

    def test_combined_rc(self):
        version = '1.1a2.rc2-cultact.1.0.devo'
        rc1 = '1.1a2.rc2-cultact.1.0.rc1'
        rc2 = '1.1a2.rc2-cultact.1.0.rc2'
        final = '1.1a2.rc2-cultact.1.0'
        self.assertEquals(bv.bump_rc(version), rc1)
        self.assertEquals(bv.bump_final(version), final)
        self.assertEquals(bv.bump_rc(rc1), rc2)
        self.assertEquals(bv.bump_final(rc1), final)


class TestRewriteSetup(unittest.TestCase):

    def setUp(self):
        # populate a tmp file from our dummy template
        setup_template = '%s/cosent/buildtools/tests/_dummysetup.py' % (
            os.getcwd())
        with open(setup_template, 'r') as fh:
            dummy_setup = fh.read()
        (_osfh, setup_filename) = tempfile.mkstemp()
        os.close(_osfh)  # don't use the low-level IO
        with open(setup_filename, 'w') as fh:
            fh.write(dummy_setup)

        # for use in tests
        self.setup_filename = setup_filename
        self.dummy_setup = dummy_setup

    def tearDown(self):
        os.remove(self.setup_filename)

    def test_get_version(self):
        self.assertEquals(bv.get_version(self.setup_filename), '0.1')

    def test_bump_setup_py_rc(self):
        bv.bump_setup_py(self.setup_filename, final=False)
        with open(self.setup_filename, 'r') as fh:
            new_setup = fh.read().splitlines()
        diff = []
        for oldline in self.dummy_setup.splitlines():
            newline = new_setup.pop(0)
            if oldline != newline:
                diff.append((oldline, newline))
        self.assertEquals(diff, [("version = '0.1'", "version = '0.2rc1'")])

    def test_bump_setup_py_final(self):
        old_setup = self.dummy_setup.splitlines()
        bv.bump_setup_py(self.setup_filename, final=True)
        with open(self.setup_filename, 'r') as fh:
            new_setup = fh.read().splitlines()
        diff = []
        self.assertEquals(len(old_setup), len(new_setup))
        for oldline in old_setup:
            newline = new_setup.pop(0)
            if oldline != newline:
                diff.append((oldline, newline))
        self.assertEquals(diff, [("version = '0.1'", "version = '0.2'")])
