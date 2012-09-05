from optparse import OptionParser
import sys


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


def bump_setup_py(filepath, final=False):
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


def main():
    parser = OptionParser()
    parser.add_option("-f", "--final",
                      action="store_true", dest="final", default=False,
                      help="Bump a final version")
    (options, args) = parser.parse_args()
    # rc: python bumpversion.py some.egg/setup.py
    # release: python --final bumpversion.py some.egg/setup.py
    if args:
        bump_setup_py(args[0], options.final)
    else:
        print(usage)

usage = """
To bump the version to the next rc:

    $ bumpversion ./path/some.egg/setup.py

To bump the version to the next final release:

    $ bumpversion --final ./path/some.egg/setup.py

"""

if __name__ == '__main__':
    sys.exit(main())
