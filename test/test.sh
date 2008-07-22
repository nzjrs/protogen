#!/bin/bash
../protogen.py -i test.xml -o test.c --name=test --type=c -pcuPl && \
../protogen.py -i test.xml -o test.h --name=test --type=header -pcuPl && \
../protogen.py -i test.xml -o test.py --name=test --type=python -pcuPl && \
echo -e "\n---Generated---\n" && \
gcc -o test -Wall -Werror -g test-main.c test.c && \
echo -e "\n---Compiled Example Program---\n" && \
./test && \
echo -e "\n---Ran Example C Program---\n" && \
python test-main.py && 
echo -e "\n---Ran Example Python Program---\n" && \
echo -e "\n---Finished---\n" && exit 0

echo -e "\n---Failure---\n"
