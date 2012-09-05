default: buildout test

buildout: bin/buildout
	@bin/buildout

test: buildout
	@bin/test -i bump_version

bin/buildout: bin/python2.6
	@wget http://svn.zope.org/repos/main/zc.buildout/trunk/bootstrap/bootstrap.py
	@bin/python2.6 bootstrap.py
	@rm bootstrap.*

bin/python2.6:
	@virtualenv --clear -p python2.6 --no-site-packages --distribute .
