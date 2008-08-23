header = """
/* WHICH ENDIAN AM I??
 * 
 * http://en.wikipedia.org/wiki/Endianness#Endianness_and_hardware
 * Little-endian:   6502, Z80, x86, VAX, and, largely, PDP-11.
 * Big-endian:      Motorola 6800 and 68000, 
 *                  PowerPC (includes Apple  prior to the Intel switch)
 *                  System/370 also adopt big-endian.
 *                  SPARC historically used big-endian, though version 9 is bi-endian
 *
 * http://handhelds.org/minihowto/porting-software.html
 * ARM processors:  Support either mode, but usually are used in 
 *                  little endian mode.
 *
 * http://blog.coldtobi.de/1_coldtobis_blog/archive/87_little_endianess_guide_for_atmel_avr.html
 * All 8-bt AVRs:  Little-endian
 * AVR32:          Big-endian
 *
 * Remember: Network byte order is big-endian
 */

#include <endian.h>
#if  __BYTE_ORDER == __LITTLE_ENDIAN
    #define COMMS_LITTLE_ENDIAN
#elif __BYTE_ORDER == __BIG_ENDIAN
    #define COMMS_BIG_ENDIAN
#else
    #warning Could not determine endianess. Please define
    #warning COMMS_BIG_ENDIAN or COMMS_LITTLE_ENDIAN
#endif
"""

system_conversion_functions = """
#include <netinet/in.h>

/* htonll/ntohll
 * <netinet/in.h> does not include a definition for
 * swapping 8 byte long longs, so we define our own
 * http://www.codeproject.com/KB/cpp/endianness.aspx
 */
#if defined(COMMS_BIG_ENDIAN) && !defined(COMMS_LITTLE_ENDIAN)

    #define htonll(A) (A)
    #define ntohll(A) (A)

#elif defined(COMMS_LITTLE_ENDIAN) && !defined(COMMS_BIG_ENDIAN)

    #define htonll(A) (((uint64_t)  (ntohl((uint32_t)((A << 32) >> 32))) << 32) | \\
                        (uint32_t)  ntohl(((uint32_t)(A >> 32))))
    #define ntohll    htonll

#else

    #error "Must define one of COMMS_BIG_ENDIAN or COMMS_LITTLE_ENDIAN"

#endif
"""

custom_conversion_funtions = """
#if defined(COMMS_BIG_ENDIAN) && !defined(COMMS_LITTLE_ENDIAN)

    #define htons(A)  (A)
    #define htonl(A)  (A)
    #define htonll(A) (A)
    #define ntohs(A)  (A)
    #define ntohl(A)  (A)
    #define ntohll(A) (A)

#elif defined(COMMS_LITTLE_ENDIAN) && !defined(COMMS_BIG_ENDIAN)

    #define htons(A)  ((((uint16_t)(A) & 0xff00) >> 8) | \\
                       (((uint16_t)(A) & 0x00ff) << 8))

    #define htonl(A)  ((((uint32_t)(A) & 0xff000000) >> 24) | \\
                       (((uint32_t)(A) & 0x00ff0000) >> 8)  | \\
                       (((uint32_t)(A) & 0x0000ff00) << 8)  | \\
                       (((uint32_t)(A) & 0x000000ff) << 24))

    /* http://www.codeproject.com/KB/cpp/endianness.aspx */
    #define htonll(A) (((uint64_t)  (ntohl((uint32_t)((A << 32) >> 32))) << 32) | \\
                        (uint32_t)  ntohl(((uint32_t)(A >> 32))))

    #define ntohs     htons
    #define ntohl     htonl
    #define ntohll    htonll

#else

    #error "Must define one of COMMS_BIG_ENDIAN or COMMS_LITTLE_ENDIAN"

#endif
"""

float_swap_functions = """
/* Once you byte swap a double or a float, 
 * you cant use it again as a double or float until it is unswapped.
 *
 * This means you must be careful when casting it to/from
 * int types. See http://www.dmh2000.com/cpp/dswap.shtml
 *
 * In this case it is easier to do it with a function
 */

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

"""

