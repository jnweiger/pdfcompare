#! /bin/bash

## this takes ca 90 seconds, two huge 400 pages documents.
# python3 ./pdfcompare.py --log logfile.txt --no-op ./ATmega640-Atmel.pdf ./ATmega640-Microchip.pdf

python3 ./pdfcompare.py --log logfile.txt  ../test/test1.pdf ../test/test2.pdf
