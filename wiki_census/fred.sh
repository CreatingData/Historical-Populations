#! /bin/bash

gawk -f bob.awk -v place=$1 ALPop.csv
