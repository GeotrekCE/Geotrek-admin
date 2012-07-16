baseurl=http://localhost:8000

bin/ lib/:
	virtualenv .
	wget http://python-distribute.org/bootstrap.py
	bin/python bootstrap.py
	rm bootstrap.py

install: bin/

clean:
	rm -rf bin/ lib/ local/ include/ *.egg-info/ develop-eggs/ parts/
	rm -rf reports/ var/
	rm -f .installed.cfg 

unit_tests: bin/
	bin/buildout -Nvc buildout-tests.cfg
	bin/django jenkins --coverage-rcfile=.coveragerc auth

functional_tests: 
	casperjs --baseurl=$(baseurl) --save=reports/FUNC-auth.xml caminae/tests/auth.js

tests: unit_tests functional_tests

serve: bin/
	bin/buildout -Nvc buildout-dev.cfg
	bin/django syncdb --migrate
	bin/django runserver

deploy: bin/
	bin/buildout -Nvc buildout-prod.cfg
	bin/django syncdb --noinput --migrate
	bin/supervisorctl restart all
