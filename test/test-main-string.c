#include <inttypes.h>

#include "test-string.h"

int main (int argc, char **argv) {
    unsigned int j,len;
    test_t *test,*test2;
    unsigned char *buf;

    buf = (unsigned char*)malloc(sizeof(unsigned char)*TEST_T_MAX_SIZE);
    test = (test_t *)malloc(sizeof(test_t));
    test2 = (test_t *)malloc(sizeof(test_t));


    float f =           1.23f;
    float f2 =          4.56f;
    double d =          0.123456e8;
    char *s =           "hello";
    char *s2 =          "worldjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj";
    char *s3 =          NULL;
    int i =             5;
    unsigned char b =   1;

    test->header_magic =            TEST_T_HEADER_MAGIC;
    test->float_value =             f;
	test->double_value =            d;
	test->string_value =            s;
	test->another_string_value =    s2;
	test->int_value =               i;
	test->bool_value =              b;
	test->another_float_value =     f2;
    test->float_value2 =            f;
	test->double_value2 =           d;
	test->string_value2 =           s3;
	test->int_value2 =              i;
    test->footer_magic =            TEST_T_FOOTER_MAGIC;

    printf("Print csv\n");
    print_test_t_csv_header();
    print_test_t_csv_line(test);
    printf("\n");
    
    len = pack_test_t(test, buf);
    printf("Packed %d bytes\n", len);
    
    printf("{");
    for (j = 0; j < len; j++)
        printf("0x%02X,", buf[j]);
    printf("};\n");
    printf("\n");

    if (unpack_test_t(buf, test2)) {
        printf("Unpack OK\n");
        print_test_t_csv_line(test2);
    } else {
        printf("Parse Error\n");
    }

    return 0;        
}
