# -*- makefile -*-

VERSION:=$(shell python3 -c 'from notspam import __VERSION__; print(__VERSION__)')

.PHONY: all
all:

.PHONY: dist
dist:
	python3 ./setup.py sdist

.PHONY: deb-snapshot
deb-snapshot: DIST=notspam-$(VERSION)
deb-snapshot: dist
	mkdir -p build
	cd build; tar zxf ../dist/$(DIST).tar.gz
	mkdir -p build/$(DIST)/debian
	git archive debian:debian | tar -x -C build/$(DIST)/debian
	cd build/$(DIST); dch -b -v $(VERSION) -D UNRELEASED 'test build, not for upload'
	cd build/$(DIST); echo '3.0 (native)' > debian/source/format
	cd build/$(DIST); debuild -us -uc

.PHONY: clean
clean:
	rm -rf __pycache__
	rm -rf notspam_classifiers/__pycache__
	rm -rf dist
	rm -rf build
	rm -rf MANIFEST
