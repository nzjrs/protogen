#!/bin/bash
../protogen.py -i test-string.xml -o test-string.c --name=test --protocol-endian=little --type=c -pcuPls && \
../protogen.py -i test-string.xml -o test-string.h --name=test --protocol-endian=little --type=header -pcuPls && \
echo -e "\n---Generated---\n" && \
gcc -o test-string -Wall -Werror -g -DBIG_ENDIAN test-main-string.c -DBIG_ENDIAN test-string.c && \
echo -e "\n---Compiled Example Program---\n" && \
./test-string && \
echo -e "\n---Ran Example C Program---\n" && \
echo -e "\n---Finished---\n" && exit 0

echo -e "\n---Failure---\n"
