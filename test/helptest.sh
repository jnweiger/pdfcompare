#!/bin/bash
#
# Script to test if 'pdfcompare --help' has an output and if the version number
# in '--help' and the specfile is the same.
#
#

if pdfcompare --help | tail -n 1; then
    help=$(pdfcompare --help | tail -n 1 | awk '{print $2}')
    if [ "$help" = "$1" ]; then
	echo "The version numbers match!"
	exit 0
    else
	echo "Version numbers don't match: Makefile has '$1', 'pdfcompare --help' says '$help' "
	exit 2
    fi
else
    echo "'pdfcompare --help' did not produce any output!"
    exit 1
fi

