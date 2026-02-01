scripts := $(wildcard bwmidimapper/*.py)
tests := $(wildcard test/test_*.py)

.PHONY: all checkstyle test dist clean 

all: clean checkstyle test dist

checkstyle: $(scripts) $(tests) setup.py
	find . -name "*.py" -exec pycodestyle --max-line-length=80 \{\} \; | tee checkstyle

test:
	PYTHONPATH=$(CURDIR) python -m pytest -q

dist: $(scripts) $(tests) setup.py
	python3 setup.py sdist --format=gztar

clean:
	find . -name "*.pyc" -type f -delete
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	rm -rf dist
	rm -f checkstyle
