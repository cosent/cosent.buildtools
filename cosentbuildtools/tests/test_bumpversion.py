import unittest

from cosentbuildtools.bump_version import bump_rc
from cosentbuildtools.bump_version import bump_final
from cosentbuildtools.bump_version import get_version


class TestBumpVersion(unittest.TestCase):

    def test_rc2rc(self):
        self.assertEquals(bump_rc('2.8rc1'), '2.8rc2')
        self.assertEquals(bump_rc('2.8rc9'), '2.8rc10')
        self.assertEquals(bump_rc('2.8rc19'), '2.8rc20')
        self.assertEquals(bump_rc('2.8.rc19'), '2.8.rc20')

    def test_final2rc(self):
        self.assertEquals(bump_rc('2.7'), '2.8rc1')
        self.assertEquals(bump_rc('2.7.1'), '2.7.2rc1')

    def test_final2final(self):
        self.assertEquals(bump_final('1'), '2')
        self.assertEquals(bump_final('2.7'), '2.8')
        self.assertEquals(bump_final('2.7.9'), '2.7.10')

    def test_rc2final(self):
        self.assertEquals(bump_final('2.8rc3'), '2.8')
        self.assertEquals(bump_final('2.8.rc3'), '2.8')


class TestRewriteSetup(unittest.TestCase):

    def test_readsetup(self):
        setup = """
from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='cosent.testegg',
      version=version)""".splitlines()
        self.assertEquals(get_version(setup), '0.1')
