#include <inttypes.h>

#include "testn.h"

int main (int argc, char **argv) 
{
    int i = 1;
    uint8_t c = 1;
    float f = 1.23;
    
    testn_t packtest;
    
    packtest.header_magic = TESTN_T_HEADER_MAGIC;
	packtest.int_value = i;
	packtest.bool_value = c;
    packtest.float_value = f;
    packtest.footer_magic = TESTN_T_FOOTER_MAGIC;
    
    printf("Print csv\n");
    print_testn_t_csv_header();
    print_testn_t_csv_line(&packtest);
    printf("\n");
    
    //--------------------------------------------------------------------------
    //Test pack
    //--------------------------------------------------------------------------
    uint8_t packbuf[TESTN_T_MAX_SIZE] = {'\0'};
    int j,len;
    
    len = pack_testn_t(&packtest, packbuf);
    printf("Packed %d bytes\n", len);
    
    for (j = 0; j < len; j++)
        printf("0x%02X,", packbuf[j]);
    printf("\n");

    //--------------------------------------------------------------------------
    //Test unpack
    //--------------------------------------------------------------------------
    testn_t unpacktest;
    
    int size = unpack_testn_t(packbuf, &unpacktest);
    if (size > 0) {
        printf("Unpack OK (%d bytes)\n", size);
        print_testn_t_csv_line(&unpacktest);
    } else {
        printf("Parse Error: %d\n", size);
    }

    return 0;
}
