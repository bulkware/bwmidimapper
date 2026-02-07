scripts := $(wildcard bwmidimapper/*.py)
tests := $(wildcard test/test_*.py)

.PHONY: all checkstyle dist lint run test clean

all: checkstyle dist lint run test clean

checkstyle: $(scripts) $(tests) setup.py
	find . -name "*.py" -exec pycodestyle --max-line-length=100 \{\} \; | tee checkstyle

dist: $(scripts) $(tests) setup.py
	python3 setup.py sdist --format=gztar

lint:  $(scripts) $(tests) setup.py
	pylint --max-line-length 100 $(scripts) $(tests) setup.py

run:
	python -m bwmidimapper.main --help

test:
	PYTHONPATH=$(CURDIR) python -m pytest -q

clean:
	find . -name "*.pyc" -type f -delete
	rm -rf bwmidimapper/__pycache__
	rm -rf test/__pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	rm -rf dist
	rm -f checkstyle
