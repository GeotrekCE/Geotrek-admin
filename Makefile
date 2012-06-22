#sudo aptitude install python-virtualenv make

bin/ lib/:
	virtualenv .
	wget http://python-distribute.org/bootstrap.py
	bin/python bootstrap.py
	rm bootstrap.py

install: bin/

clean:
	rm -rf bin/ lib/ local/ include/

unit_tests: bin/
	bin/buildout -Nvc buildout-tests.cfg
	bin/django jenkins --coverage-exclude=django

tests: unit_tests

serve: bin/
	bin/buildout -Nvc buildout-dev.cfg
	bin/django syncdb --migrate
	bin/django runserver

deploy: bin/
	bin/buildout -Nvc buildout-prod.cfg
