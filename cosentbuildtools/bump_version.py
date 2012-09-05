import unittest
from optparse import OptionParser


def bump_rc(version):
    if 'rc' in version:
        final, rc = version.split('rc')
        return "%src%s" % (final, int(rc) + 1)
    else:
        return bump_final(version) + 'rc1'


def bump_final(version):
    if 'rc' in version:
        final, rc = version.split('rc')
        return final.strip('.')
    else:
        parts = version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        return '.'.join(parts).strip('.')


def get_version(setup):
    for line in setup:
        if line.startswith("version"):
            version = line.split('=')[1].strip()
            return version.replace('"', '').replace("'", "")


def main(filepath, final=False):
    """Update the version number in <filepath>
    which should be a setup.py file with egg metadata.

    if not final (the default): update the version as a pre-release.
    if final: bump the final release version number.

    Writes back the changed file.
    """

    with open(filepath, 'r+') as fh:
        setup = fh.readlines()
        version = get_version(setup)
        if final:
            new_version = bump_final(version)
        else:
            new_version = bump_rc(version)
        new_setup = []
        for line in setup:
            if line.startswith("version"):
                new_setup.append("version = '%s'\n" % new_version)
            else:
                new_setup.append(line)
        fh.seek(0)
        fh.write(''.join(new_setup))


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

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", "--final",
                      action="store_true", dest="final", default=False,
                      help="Bump a final version")
    (options, args) = parser.parse_args()
    # rc: python bump_version.py ../setup.py
    # release: python --final bump_version.py ../setup.py
    if args:
        main(args[0], options.final)
    else:
        unittest.main()
