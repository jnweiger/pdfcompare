
VER=1.6.9	# keep in sync with pdfcompare.py:
D=dist/pdfcompare-$(VER)
EXCL=--exclude \*.orig --exclude \*~

all: check tar

check test:
	cd test; make test VER=$(VER)

testrefresh refreshtest:
	cd test; make test refresh=yes

clean:
	rm -rf dist *.orig *~
	rm -rf test/*.orig test/*~

tar dist:
	rm -rf dist
	mkdir -p $D
	ln -s ../../pdfcompare.py $D/pdfcompare.py
	ln -s ../../COPYING $D/
	ln -s ../../test $D/test
	cd dist; tar jhcvf ../pdfcompare-$(VER).tar.bz2 pdfcompare-$(VER) $(EXCL)
	rm -rf dist

