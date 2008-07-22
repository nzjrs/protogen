#!/bin/bash
gcc -o test-swap -Wall -Werror -g -std=c99 test-swap.c && \
echo -e "\n---Compiled Example Program---\n" && \
./test-swap && \
echo -e "\n---Ran Example C Program---\n" && \
gcc -o test-swap -Wall -Werror -g -std=c99 -DUSE_OWN_BYTESWAP test-swap.c && \
echo -e "\n---Compiled Example Program---\n" && \
./test-swap && \
echo -e "\n---Ran Example C Program---\n" && \
exit 0

echo -e "\n---Failure---\n"
