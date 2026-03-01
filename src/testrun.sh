#! /bin/bash

## this takes ca 90 seconds, two huge 400 pages documents.
# python3 ./pdfcompare.py --log logfile.txt --no-op ./ATmega640-Atmel.pdf ./ATmega640-Microchip.pdf

## a quickie with a text file for easy manual input manipulation
./pdfcompare.py --dump-words test1.txt ../test/test1.pdf
./pdfcompare.py --log logfile.txt --no-op test1.txt ../test/test2.pdf
