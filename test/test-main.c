#include <inttypes.h>

#include "test.h"

int main (int argc, char **argv) {
    //--------------------------------------------------------------------------
    //Test size of types
    //--------------------------------------------------------------------------
    printf(
        "sizeof:\n"
        "\tuint8_t  : %d\n"
        "\tint8_t   : %d\n"
        "\tuint16_t : %d\n"
        "\tint16_t  : %d\n"
        "\tuint32_t : %d\n"
        "\tint32_t  : %d\n"
        "\tuint64_t : %d\n"
        "\tint64_t  : %d\n"
        "\tfloat    : %d\n"
        "\tdouble   : %d\n"
        "\tint      : %d\n"
        "\tlong     : %d\n"
        "\tlong long: %d\n"
        "\n",
        sizeof(uint8_t),
        sizeof(int8_t),
        sizeof(uint16_t),
        sizeof(int16_t),
        sizeof(uint32_t),
        sizeof(int32_t),
        sizeof(uint64_t),
        sizeof(int64_t),
        sizeof(float),
        sizeof(double),
        sizeof(int),
        sizeof(long),
        sizeof(long long));
    printf("\n\n");
        
    //--------------------------------------------------------------------------
    //Test cast/uncast ops
    //--------------------------------------------------------------------------
    char cbuf[8];
    int ci = 5, ci2 = 0;
    float cf = 1.23, cf2 = 0.0;
    unsigned char cc = 'j', cc2 = 0;
    double cd = 4.56, cd2 = 0.0;

    //int
    *(uint32_t *)(cbuf) = /*htonl*/(*(uint32_t *)&ci);
    ci2 = (int)/*ntohl*/(*(int*)(cbuf));
    printf("test cast int: %d v %d\n",ci,ci2);    
    
    //float
    *(uint32_t *)(cbuf) = /*htonl*/(*(uint32_t *)&cf);
    cf2 = (float)/*ntohl*/(*(float*)(cbuf));
    printf("test cast float: %f v %f\n",cf,cf2);
    
    //unsigned char (aka bool)
    *(cbuf) = (*(unsigned char *)&cc);
    cc2 = (unsigned char)(*(unsigned char*)(cbuf));
    printf("test cast unsigned char: %c v %c\n",cc,cc2);
    
    //double
    *(uint64_t *)(cbuf) = /*htonl*/(*(uint64_t *)&cd);
    cd2 = (double)/*ntohl*/(*(double*)(cbuf));
    printf("test cast double: %f v %f\n",cd,cd2);
    printf("\n\n");
    
    //--------------------------------------------------------------------------
    //Test print
    //--------------------------------------------------------------------------
    int i = 1;
    float f = 1.23;
    double d = 4.56;

#if TEST_T_CAN_HANDLE_STRINGS    
    char *s = "hello";
    char *s2 = "world";
#endif

    unsigned char c = 1;
    
    test_t packtest;
    
    packtest.header_magic = TEST_T_HEADER_MAGIC;
    packtest.float_value = f;
	packtest.double_value = d;
#if TEST_T_CAN_HANDLE_STRINGS    
	packtest.string_value = s;
	packtest.another_string_value = s2;
#endif
	packtest.int_value = i;
	packtest.bool_value = c;
	packtest.another_float_value = f;
    packtest.footer_magic = TEST_T_FOOTER_MAGIC;
    
    printf("Print csv\n");
    print_test_t_csv_header();
    print_test_t_csv_line(&packtest);
    printf("\n\n");
    
    //--------------------------------------------------------------------------
    //Test pack
    //--------------------------------------------------------------------------
    unsigned char packbuf[TEST_T_MAX_SIZE] = {'\0'};
    int j,len;
    
    len = pack_test_t(&packtest, packbuf);
    printf("Packed %d bytes\n", len);
    
    for (j = 0; j < len; j++)
        printf("0x%02X,", packbuf[j]);
    printf("\n\n\n");
    

    //--------------------------------------------------------------------------
    //Test unpack
    //--------------------------------------------------------------------------
#if TEST_T_CAN_HANDLE_STRINGS
    unsigned char unpackbuf[] = {0x54,0x54,0x45,0x45,0xA4,0x70,0x9D,0x3F,0x3D,0x0A,0xD7,0xA3,0x70,0x3D,0x12,0x40,0x06,0x68,0x65,0x6C,0x6C,0x6F,0x00,0x01,0x00,0x00,0x00,0x01,0x06,0x77,0x6F,0x72,0x6C,0x64,0x00,0xA4,0x70,0x9D,0x3F,0x0D,0x0C,0x0B,0x0A};
#else
    unsigned char unpackbuf[] = {0x54,0x54,0x45,0x45,0xA4,0x70,0x9D,0x3F,0x3D,0x0A,0xD7,0xA3,0x70,0x3D,0x12,0x40,0x01,0x00,0x00,0x00,0x01,0xA4,0x70,0x9D,0x3F,0x0D,0x0C,0x0B,0x0A};
#endif
    test_t unpacktest;
    
    
    if (unpack_test_t(unpackbuf, &unpacktest)) {
        printf("Unpack OK\n");
        print_test_t_csv_line(&unpacktest);
    } else {
        printf("Parse Error\n");
    }
    
    return 0;
}
