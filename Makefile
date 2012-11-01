default: buildout test

buildout: bin/buildout
	@bin/buildout

test:
	@bin/test --with-coverage --cover-package=cosent.buildtools --cover-erase

bin/buildout: bin/python2.6
	@wget http://svn.zope.org/repos/main/zc.buildout/trunk/bootstrap/bootstrap.py
	@bin/python2.6 bootstrap.py
	@rm bootstrap.*

bin/python2.6:
	@virtualenv --clear -p python2.6 --no-site-packages --distribute .

travis:
	wget http://svn.zope.org/repos/main/zc.buildout/trunk/bootstrap/bootstrap.py
	python bootstrap.py
	rm bootstrap.*
	bin/buildout

clean:
	rm -rf bin/* .installed.cfg bootstrap.*