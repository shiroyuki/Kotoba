package:
	python setup.py sdist

wheel_release:
	python setup.py sdist bdist_wheel upload

tests:
	@nosetests test/