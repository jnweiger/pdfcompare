VER=1.3
refresh=

all: test

test:
	ln -sf ../pdf_highlight.py pdfcompare
	env PATH=.:$$PATH sh ./helptest.sh $(VER) VER=$(VER)
	env PATH=.:$$PATH sh ./python3.sh
	env PATH=.:$$PATH refresh=$(refresh) sh ./restest.sh
	rm pdfcompare

# updates the testsuite after code changes 
# that affect the visual representation.
refresh:
	# we only need to refresh restest.sh
	env PATH=.:$$PATH refresh=yes sh ./restest.sh
	# make test refresh=yes
