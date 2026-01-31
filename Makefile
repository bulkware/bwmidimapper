scripts := $(wildcard bw_*.py)
tests := $(wildcard test_bw*.py)

all: clean checkstyle test dist

checkstyle: $(scripts) $(tests) setup.py
	find . -name "*.py" -exec pycodestyle --max-line-length=80 \{\} \; | tee checkstyle

test:
	pytest -q $(tests)

dist: $(scripts) $(tests) setup.py
	python3 setup.py sdist --format=gztar

clean:
	find . -name "*.pyc" -type f -delete
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	rm -rf dist
	rm -f checkstyle
