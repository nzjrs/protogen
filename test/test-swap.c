#include <stdio.h>
#include <inttypes.h>

//#include <endian.h>
//#include <netinet/in.h>

#ifdef USE_OWN_BYTESWAP
    #define htons(A)  ((((uint16_t)(A) & 0xff00) >> 8) | \
                       (((uint16_t)(A) & 0x00ff) << 8))

    #define htonl(A)  ((((uint32_t)(A) & 0xff000000) >> 24) | \
                       (((uint32_t)(A) & 0x00ff0000) >> 8)  | \
                       (((uint32_t)(A) & 0x0000ff00) << 8)  | \
                       (((uint32_t)(A) & 0x000000ff) << 24))
#else
    #include <netinet/in.h>
#endif

// http://www.codeproject.com/KB/cpp/endianness.aspx           
#define htonll(A) (((uint64_t)  (ntohl((uint32_t)((A << 32) >> 32))) << 32) | \
                    (uint32_t)  ntohl(((uint32_t)(A >> 32))))

#ifdef USE_OWN_BYTESWAP
    #define ntohs     htons
    #define ntohl     htonl
#endif

#define ntohll    htonll

unsigned long long swap_double(double d)
{
    unsigned long long a;
    unsigned char *dst = (unsigned char *)&a;
    unsigned char *src = (unsigned char *)&d;

    dst[0] = src[7];
    dst[1] = src[6];
    dst[2] = src[5];
    dst[3] = src[4];
    dst[4] = src[3];
    dst[5] = src[2];
    dst[6] = src[1];
    dst[7] = src[0];

    return a;
}

double unswap_double(unsigned long long a) 
{

    double d;
    unsigned char *src = (unsigned char *)&a;
    unsigned char *dst = (unsigned char *)&d;

    dst[0] = src[7];
    dst[1] = src[6];
    dst[2] = src[5];
    dst[3] = src[4];
    dst[4] = src[3];
    dst[5] = src[2];
    dst[6] = src[1];
    dst[7] = src[0];

    return d;
}

unsigned long swap_float(float f)
{
    unsigned long a;
    unsigned char *dst = (unsigned char *)&a;
    unsigned char *src = (unsigned char *)&f;

    dst[0] = src[3];
    dst[1] = src[2];
    dst[2] = src[1];
    dst[3] = src[0];

    return a;
}

float unswap_float(unsigned long a) 
{

    float f;
    unsigned char *src = (unsigned char *)&a;
    unsigned char *dst = (unsigned char *)&f;

    dst[0] = src[3];
    dst[1] = src[2];
    dst[2] = src[1];
    dst[3] = src[0];

    return f;
}

void pbuf(char *buf, int len)
{
    int i;
    for (i = 0; i < len; i++)
        printf("0x%02X,", (uint8_t)buf[i]);
    printf("\n");
}

void cbuf(char *buf, int len)
{
    int i;
    for (i = 0; i < len; i++)
        buf[i] = '\0';
}

int main (int argc, char **argv) 
{

    char buf[8] = {'\0'};
    
    uint32_t fi; float f,f2;
    uint64_t di; double d, d2;


    int16_t s = 0xABCD;
    int32_t i = 0x1234ABCD;
    int64_t l = 0x0123456789ABCDEF;
    int16_t s2;
    int32_t i2;
    int64_t l2;

#ifdef USE_OWN_BYTESWAP
    printf("USING OWN BYTESWAP ROUTINES\n");
#else
    printf("USING SYSTEM BYTESWAP ROUTINES\n");
#endif

    // Swap float
    cbuf(buf, sizeof(buf));
    printf("\nfloat\n");
    f = 1.23;
    pbuf((char *)&f, sizeof(f));

    fi = swap_float(f);
    *(uint32_t *)(buf) = fi;
    pbuf(buf, sizeof(buf));

    f2 = unswap_float(*(uint32_t *)buf);
    printf("%f (orig) v %f (swapped) equal:%u\n", f, f2, f==f2);
    if (f!=f2) return 1;

    // Swap double
    cbuf(buf, sizeof(buf));
    printf("\ndouble\n");
    d = 1.23;
    pbuf((char *)&d, sizeof(d));
    di = swap_double(d);
    *(uint64_t *)(buf) = di;
    pbuf(buf, sizeof(buf));

    d2 = unswap_double(*(uint64_t *)buf);
    printf("%f (orig) v %f (swapped) equal:%u\n", d, d2, d==d2);
    if (d!=d2) return 1;

    // Swap short
    cbuf(buf, sizeof(buf));
    printf("\nshort\n");
    pbuf((char *)&s, sizeof(s));
    *(uint16_t *)(buf) = htons(s);
    pbuf(buf, sizeof(buf));

    s2 = ntohs(*(uint16_t *)buf);
    printf("%d (orig) v %d (swapped) equal:%u\n", s, s2, s==s2);
    if (s!=s2) return 1;

    // Swap int
    cbuf(buf, sizeof(buf));
    printf("\nint\n");
    pbuf((char *)&i, sizeof(i));
    *(uint32_t *)(buf) = htonl(i);
    pbuf(buf, sizeof(buf));

    i2 = ntohl(*(uint32_t *)buf);
    printf("%d (orig) v %d (swapped) equal:%u\n", i, i2, i==i2);
    if (i!=i2) return 1;

    // Swap long long
    cbuf(buf, sizeof(buf));
    printf("\nlong\n");
    pbuf((char *)&l, sizeof(l));
    *(uint64_t *)(buf) = htonll(l);
    pbuf(buf, sizeof(buf));

    l2 = ntohll(*(uint64_t *)buf);
    printf("%lld (orig) v %lld (swapped) equal:%u\n", l, l2, l==l2);
    if (l!=l2) return 1;

    return 0;
}
