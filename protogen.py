#!/usr/bin/python
# This script autogenerates functions to unpack binary packed data based upon
# an xml file describing the layout of that data.
# 
# (c) John Stowers 2008

import os.path
import sys
import getopt

import protogen.parser as parser
import protogen.cwriter as cwriter
import protogen.pywriter as pywriter
 
def usage():
    print   """
Protogen: 
Generates files for parsing packed binary data based upon an 
XML protocol definition files

./protogen.py -i XML_FILE -o HEADER_FILENAME -t TYPE [Options]

Options:
    -n, --name=                 The name of the generated struct. In C this
                                is the supplied name + _t. In python this is
                                made TitleCase. If not specified then the 
                                generated struct be the input filename, minus 
                                the extension.
    -l, --lowercase             Force struct members to lowercase names.
                                (default=No)
    -p, --print-function        Generate a function to print the struct.
                                (default=No)
    -c, --print-csv-function    Generate functions for printing struct.
                                to CSV format (default=No)
    -u, --unpack-function       Generate a function to unpack a struct.
                                from a byte array (default=No)
    -P, --pack-function         Generate function to pack data into the buffer.
                                (default=No)
    -t, --type=                 Type of file to generate.
                                (c,header,python)
    -e, --protocol-endian=      What endian should the packed data be in.
                                    network:    Convert to network endian before
                                                sending (uses htonxx)
                                    little:     Perform no conversion of endian
                                                before sending. In almost all
                                                cases (warning: not all), 
                                                this makes the data little endian
                                (default=little)
    -b, --include-convert       Include byte swap/convert macros, instead of using the
                                system provided ones in <netinet/in.h>
                                (default=use system macros)
    -s, --enable-strings        Enable string support in protocol pack/unpack
                                functions. Strings are send as pascal strings,
                                i.e prefixed by their length (0-255 bytes)
                                (default=no)
    -d, --use-doubles           Use doubles instead of floats for floating point
                                numbers
                                (default=no)
                                """

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                        "i:o:n:lpcPute:bsd",
                        ("input=", "output=", "name=", "lowercase", 
                            "print-function", "print-csv-function",
                            "pack-function", "unpack-function",
                            "type=", "protocol-endian=",
                            "include-convert", "enable-strings",
                            "use-doubles"))
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(1)

    #Command parsing rubbish....
    input_file = None
    output_file = None
    lowercase = False
    print_function = False
    print_csv_function = False
    pack_function = False
    unpack_function = False
    file_type = None
    name = None
    endian = "little"
    include_convert_macros = False
    enable_strings = False
    use_doubles = False

    for o, a in opts:
        if o in ("-i", "--input"):
            input_file = os.path.abspath(a)
        if o in ("-o", "--output"):
            output_file = os.path.abspath(a)
        if o in ("-l", "--lowercase"):
            lowercase = True
        if o in ("-p", "--print-function"):
            print_function = True
        if o in ("-c", "--print-csv-function"):
            print_csv_function = True
        if o in ("-P", "--pack-function"):
            pack_function = True
        if o in ("-u", "--unpack-function"):
            unpack_function = True
        if o in ("-n", "--name"):
            name = a
        if o in ("-t", "--type"):
            file_type = a
        if o in ("-e", "--protocol-endian"):
            endian = a
        if o in ("-s", "--enable-strings"):
            enable_strings = True
        if o in ("-b", "--include-convert"):
            include_convert_macros = True
        if o in ("-d", "--use-doubles"):
            use_doubles = True
        if o in ("-h", "--help"):
            usage()
            sys.exit(1)

    if None in [input_file, output_file]:
        print "Please specify input and output file\n"
        usage()
        sys.exit(1)

    # Check the input file exists
    if not os.path.isfile(input_file):
        print "Input file does not exist\n"
        usage()
        sys.exit(1)
        
    if endian not in ("network", "little"):
        print "Incorrect endian\n"
        usage()
        sys.exit(1)

    # Check for valid type of file to generate
    try:
        writerKlass = {
            "c"         :   cwriter.CBodyWriter,
            "header"    :   cwriter.CHeaderWriter,
            "python"    :   pywriter.PythonWriter}[file_type]
    except KeyError:
        print "Invalid file type to generate: %s\n" % file_type
        usage()
        sys.exit(1)

    # If the name was not specified use the input filename
    if name == None:
        # remove the extension        
        name = os.path.splitext(os.path.basename(input_file))[0]

    parser = parser.XMLProtocolParser(input_file, lowercase, enable_strings, use_doubles)
    
    try:
        parser.parse_protocol_file()
    except Exception, e:
        print "Error parsing file: %s\n" % e.message
        sys.exit(1)
        
    thefile = open(output_file, "w")

    try:
        writer = writerKlass(parser, thefile, name, endian, include_convert_macros)
    except Exception, e:
        print "Error configuring writer: %s\n" % e.message
        sys.exit(1)

    writer.write_header(output_file)
    writer.write_struct()

    if print_function:
        writer.write_print_function()

    if print_csv_function:
        writer.write_csv_functions()
    
    if pack_function:
        writer.write_pack_functions()

    if unpack_function:
        writer.write_unpack_function()
    
    writer.write_footer()

    thefile.close()
    sys.exit(0)
