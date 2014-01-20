from optparse import OptionParser
import sys


def bump_rc(version):
    (prefix, base, final, rc, dev) = splitversion(version)
    if 'dev' in base:
        v = "%src1" % final
        return restoreprefix(prefix, v)
    elif 'rc' in base:
        if rc == '':
            rc = 0
        elif '.' in rc:
            rc = rc.split('.')[0]
        v = "%src%s" % (final, int(rc) + 1)
        return restoreprefix(prefix, v)
    else:
        return bump_final(version) + 'rc1'


def bump_final(version):
    (prefix, base, final, rc, dev) = splitversion(version)
    if 'rc' in base or 'dev' in base:
        v = final.strip('.')
        return restoreprefix(prefix, v)
    else:
        parts = version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        return '.'.join(parts).strip('.')


def splitversion(version):
    prefix = ''
    base = version
    final = ''
    rc = ''
    dev = ''
    if '-' in version:
        parts = version.split('-')
        prefix = '-'.join(parts[:-1])
        base = parts[-1]
    if 'dev' in base:
        final, dev = base.split('dev')
    elif 'rc' in base:
        final, rc = base.split('rc')
    else:
        final = base
    return (prefix, base, final, rc, dev)


def restoreprefix(prefix, base):
    return '-'.join([prefix, base]).strip('-')


def get_version(path, append_setup_py=False):
    if append_setup_py:
        path += "/setup.py"

    with open(path, 'r') as fh:
        setup = fh.read().splitlines()
    for line in setup:
        if line.startswith("version"):
            version = line.split('=')[1].strip()
            return version.replace('"', '').replace("'", "")
    raise AttributeError("no version in file:", setup)


def pkg_version(pkgpath):
    return get_version(pkgpath, True)


def bump_pkg(pkgpath, final=True, noact=False):
    return bump_setup_py("%s/setup.py" % pkgpath, final, noact)


def bump_setup_py(filepath, final=True, noact=False):
    """Update the version number in <filepath>
    which should be a setup.py file with egg metadata.

    if not final (the default): update the version as a pre-release.
    if final: bump the final release version number.

    Writes back the changed file.
    """
    version = get_version(filepath)
    with open(filepath, 'r+') as fh:
        setup = fh.readlines()
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
    if not noact:
        with open(filepath, 'w') as fh:
            fh.write(''.join(new_setup))
    print("%s: %s -> %s" % (filepath, version, new_version))
    return new_version


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
