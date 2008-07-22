#!/bin/bash
../protogen.py -i testn.xml -o testn.h --name=testn --type=header -pcuPl --protocol-endian=network && \
../protogen.py -i testn.xml -o testn.c --name=testn --type=c -pcuPl --protocol-endian=network && \
echo -e "\n---Generated (system byte conversions)---\n" && \
gcc -o testn -Wall -Werror -g test-network.c testn.c && \
echo -e "\n---Compiled Example Program---\n" && \
./testn && \
echo -e "\n---Ran Example C Program---\n" && \
../protogen.py -i testn.xml -o testn.h --name=testn --type=header -pcuPl --protocol-endian=network --include-convert && \
../protogen.py -i testn.xml -o testn.c --name=testn --type=c -pcuPl --protocol-endian=network --include-convert && \
echo -e "\n---Generated (custom byte conversions)---\n" && \
gcc -o testn -Wall -Werror -g test-network.c testn.c && \
echo -e "\n---Compiled Example Program---\n" && \
./testn && \
echo -e "\n---Ran Example C Program---\n" && \
exit 0

echo -e "\n---Failure---\n"
