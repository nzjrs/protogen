import os.path
import writer
import byte_conversions

PRINTF_MAP = {
    "float"     : "%f",
    "double"    : "%g",
    "int"       : "%d",
    "bool"      : "%u",
    "char"      : "%c",
    "string"    : "%s"
}

TYPE_SIZE_MAP = {
    "double"    : 8,
    "float"     : 4,
    "int"       : 4,
    "bool"      : 1,
    "char"      : 1,
    "string"    : 1     #Length of string size indicator
}  


CPP_TO_C_TYPE_MAP = {
    "float"     : "float",
    "double"    : "double",
    "int"       : "int",
    "bool"      : "unsigned char",
    "char"      : "char",
    "string"    : "char *"
}

class CWriter(writer.Writer):

    #Buffer to variable assignment (little endian)
    BUF_TO_VAR_LE = {
        "int"       : "%(dest)s = *((int *)(%(source_pointer)s))",
        "float"     : "%(dest)s = *((float *)(%(source_pointer)s))",
        "double"    : "%(dest)s = *((double *)(%(source_pointer)s))",
        "bool"      : "%(dest)s = *((unsigned char *)(%(source_pointer)s))",
        "char"      : "%(dest)s = *((char *)(%(source_pointer)s))"
    }

    #Variable to buffer assignment (little endian)
    VAR_TO_BUF_LE = {
        "int"       : "*(uint32_t *)(%(dest_pointer)s) = (*(uint32_t *)&%(source)s)",
        "float"     : "*(uint32_t *)(%(dest_pointer)s) = (*(uint32_t *)&%(source)s)",
        "double"    : "*(uint64_t *)(%(dest_pointer)s) = (*(uint64_t *)&%(source)s)",
        "bool"      : "*(%(dest_pointer)s) = (*(unsigned char *)&%(source)s)",
        "char"      : "*(%(dest_pointer)s) = (*(char *)&%(source)s)"
    }

    #Buffer to variable assignment (big aka network endian)
    BUF_TO_VAR_BE = {
        "int"       : "%(dest)s = (int)ntohl(*(uint32_t *)(%(source_pointer)s))",
        "float"     : "%(dest)s = (float)unswap_float(*(uint32_t *)(%(source_pointer)s))",
        "double"    : "%(dest)s = (double)unswap_double(*(uint64_t *)(%(source_pointer)s))",
        "bool"      : "%(dest)s = *((unsigned char *)(%(source_pointer)s))",
        "char"      : "%(dest)s = *((char *)(%(source_pointer)s))"
    }

    #Variable to buffer assignment (big aka network endian)
    VAR_TO_BUF_BE = {
        "int"       : "*(uint32_t *)(%(dest_pointer)s) = htonl(%(source)s)",
        "float"     : "*(uint32_t *)(%(dest_pointer)s) = swap_float(%(source)s)",
        "double"    : "*(uint64_t *)(%(dest_pointer)s) = swap_double(%(source)s)",
        "bool"      : "*(%(dest_pointer)s) = (*(unsigned char *)&%(source)s)",
        "char"      : "*(%(dest_pointer)s) = (*(char *)&%(source)s)"
    }

    def __init__(self, *args):
        writer.Writer.__init__(self, *args)
        #the name of the c structure is suffixed with _t    
        self.name += "_t"

    def _unpack_from_buffer(self, type, dest, source_pointer):
        if self.endian == "little":
            return self.BUF_TO_VAR_LE[type] % {
                            "dest"              :       dest,
                            "source_pointer"    :       source_pointer}
        elif self.endian == "network":
            return self.BUF_TO_VAR_BE[type] % {
                            "dest"              :       dest,
                            "source_pointer"    :       source_pointer}
        else:
            raise Exception("Endian not supported")

    def _pack_into_buffer(self, type, source, dest_pointer):
        if self.endian == "little":
            return self.VAR_TO_BUF_LE[type] % {
                            "source"        :       source,
                            "dest_pointer"  :       dest_pointer}
        elif self.endian == "network":
            return self.VAR_TO_BUF_BE[type] % {
                            "source"        :       source,
                            "dest_pointer"  :       dest_pointer}

        else:
            raise Exception("Endian not supported")

    def _get_print_function_name(self):
        return "void print_%s(%s *data)" % (self.name.lower(), self.name)

    def _get_print_csv_header_function_name(self):
        return "void print_%s_csv_header(void)" % self.name.lower()

    def _get_print_csv_line_function_name(self):
        return "void print_%s_csv_line(%s *data)" % (self.name.lower(), self.name)

    def _get_pack_function_name(self):
        return "unsigned int pack_%s(const %s *data, unsigned char *buffer)" % (self.name.lower(), self.name)

    def _get_unpack_function_name(self):
        return "int unpack_%s(const unsigned char *buffer, %s *data)" % (self.name.lower(), self.name)

    def _get_error_define(self, errorid):
        return "%s_ERROR_%s" % (self.name.upper(), self.parser.get_error_name(errorid))

class CBodyWriter(CWriter):
    def write_header(self, filename):
        self.f.write("// Autogenerated file, do no edit\n\n")
        self.f.write("#include \"%s.h\"\n" % os.path.splitext(os.path.basename(filename))[0])

        #write all the endianess conversion macros
        if self.endian == "network":
            self.f.write(byte_conversions.float_swap_functions)

    def write_struct(self):
        pass

    def write_print_function(self):
        #Horizontal position at which the value is printed    
        VALUE_COLUMN = 30

        self.f.write("\n\n%s\n{\n" % self._get_print_function_name())
        for chunk in self.parser.parse_tree:
            #Get chunks type and name
            type, name = self.parser.get_chunk_info(chunk)
            #Pad the member name with spaces so the values line up
            num_spaces = VALUE_COLUMN - len(name)
            #Write the printf statement in the form name:       value   (type)
            format_string = "\tprintf(\"%s:%s%s\\n\",data->%s); // %s\n"
            self.f.write(format_string % (name, "".ljust(num_spaces), PRINTF_MAP[type], name, chunk["node"]))

        self.f.write("}\n")


    def write_csv_functions(self):
        format_str = ""
        value_str = ""
        name_str = ""

        #PRINT CSV HEADER
        self.f.write("\n\n%s\n{\n" % self._get_print_csv_header_function_name())
        for chunk in self.parser.parse_tree:
            #Get chunks type and name
            type, name = self.parser.get_chunk_info(chunk)
            #Append the chunk type and value to the name string
            name_str += "%s," % name

        #Print the completed strings minus the trailing commas
        self.f.write("\tprintf(\"%s\\n\");\n" % name_str[0:-1])
        self.f.write("}\n")

        #PRINT A CSV LINE
        self.f.write("\n\n%s\n{\n" % self._get_print_csv_line_function_name())
        for chunk in self.parser.parse_tree:
            #Get chunks type and name
            type, name = self.parser.get_chunk_info(chunk)
            #Append the chunk type and value to the format and value string
            format_str += "%s," % PRINTF_MAP[type]
            value_str += "data->%s," % name

        #Print the completed strings minus the trailing commas
        self.f.write("\tprintf(\"%s\\n\",%s);\n" % (format_str[0:-1], value_str[0:-1]))
        self.f.write("}\n")

    def write_pack_functions(self):
        offset = 0
        self.f.write("\n\n// Packs %s into buffer\n" % self.name.lower())
        self.f.write("%s\n{\n" % self._get_pack_function_name())

        #variables        
        #values for head/bin footers
        if self.parser.binary_header:
            if self.parser.binary_header[0] == "magic":
                self.f.write("\tstatic int binary_header = %s;\n" % self.parser.binary_header[1])
        if self.parser.binary_footer:
            if self.parser.binary_footer[0] == "magic":
                self.f.write("\tstatic int binary_footer = %s;\n" % self.parser.binary_footer[1])
                
        if self.parser.has_strings:                    
            #We need one temp variable for calculating the string len
            self.f.write("\tunsigned char str_len = 0;\n")
        #And one for a running offset due to string lengths
        self.f.write("\tunsigned int str_offset = 0;\n")
        
        #Did the user specify a binary header?. 
        #If so, write and check it
        if self.parser.binary_header:
            if self.parser.binary_header[0] == "magic":
                assignment = self._pack_into_buffer(
                                    "int",
                                    source="binary_header",
                                    dest_pointer="buffer+%d+str_offset" % offset)
                self.f.write("\n\t%s;\n" % assignment)
            offset += TYPE_SIZE_MAP["int"] #magic number is an integer
            
        self.f.write("\n")
        for chunk in self.parser.parse_tree:
            #Get chunks type and name
            type, name = self.parser.get_chunk_info(chunk)
            #Write each unpack function
            if type in ("float", "double", "int", "bool"):
                assignment = self._pack_into_buffer(
                                    type,
                                    source="data->%s" % name,
                                    dest_pointer="buffer+%d+str_offset" % offset)
                self.f.write("\t%s;\n" % assignment)
                offset += TYPE_SIZE_MAP[type]
            elif type == "string":
                #First read the string length, max 254 bytes (excluding NULL)
                self.f.write("\n\t//Packing string: %s\n" % name)
                self.f.write("\tstr_len = (data->%s ? strlen(data->%s) : 0);\n" % (name,name))
                #limit string size to 254, add one because we also copy the NULL
                self.f.write("\tstr_len = (str_len > 254 ? 254 : str_len + 1);\n")
                #write size
                self.f.write("\t*(buffer+%d+str_offset) = str_len;\n" % offset)
                self.f.write("\tstr_offset += 1;\n")
                #write string
                self.f.write("\tif (data->%s)\n" % name)
                self.f.write("\t\tstrncpy((char *)(buffer+%d+str_offset), data->%s, str_len);\n" % (offset,name))
                self.f.write("\tstr_offset += str_len;\n")
                #Guarentee null termination
                self.f.write("\t*(buffer+%d+str_offset) = '\\0';\n\n" % offset)

        #Did the user specify a binary header?. 
        #If so, write and check it
        if self.parser.binary_footer:
            if self.parser.binary_footer[0] == "magic":
                assignment = self._pack_into_buffer(
                                "int",
                                source="binary_footer",
                                dest_pointer="buffer+%d+str_offset" % offset)
                self.f.write("\n\t%s;\n" % assignment)
            offset += TYPE_SIZE_MAP["int"] #magic number is an integer
                
        self.f.write("\n\treturn %d+str_offset;\n" % offset)
        self.f.write("}\n")

    def write_unpack_function(self):
        offset = 0
        #Write out some header stuff
        self.f.write("\n\n// Unpacks buffer into %s. Returns address of end of processed data or NULL on failure\n" % self.name.lower())
        self.f.write("%s\n{\n" % self._get_unpack_function_name())

        if self.parser.has_strings:
            #We need one temp variable for calculating the string len
            self.f.write("\tunsigned char str_len = 0;\n")
        #And one for a running offset due to string lengths
        self.f.write("\tunsigned int str_offset = 0;\n")
        
        #Did the user specify a binary header?. 
        #If so, write and check it
        if self.parser.binary_header:
            if self.parser.binary_header[0] == "magic":
                assignment = self._unpack_from_buffer(
                                    "int",
                                    dest="data->header_magic",
                                    source_pointer="buffer+%d+str_offset" % offset)
                self.f.write("\n\t%s;\n" % assignment)
                self.f.write("\tif (data->header_magic != %s) return %s;\n" % (
                                    self.parser.binary_header[1],
                                    self._get_error_define(self.parser.ERROR_HEADER_MAGIC)))
            offset += TYPE_SIZE_MAP["int"] #magic number is an integer

        self.f.write("\n")
        for chunk in self.parser.parse_tree:
            #Get chunks type and name
            type, name = self.parser.get_chunk_info(chunk)
            #Write each unpack function
            if type in ("float", "double", "int", "bool"):
                assignment = self._unpack_from_buffer(
                                    type,
                                    dest="data->%s" % name,
                                    source_pointer="buffer+%d+str_offset" % offset)
                self.f.write("\t%s;\n" % assignment)
                offset += TYPE_SIZE_MAP[type]
            elif type == "string":
                #First read the string len
                self.f.write("\n\t//Unpacking string: %s\n" % name)
                assignment = self._unpack_from_buffer(
                                    "bool",
                                    dest="str_len",
                                    source_pointer="buffer+%d+str_offset" % offset)
                self.f.write("\t%s;\n" % assignment)
                #Free old
                self.f.write("\tif (data->%s != NULL) free(data->%s);\n" % (name, name))
                #Jump over the strlen byte
                self.f.write("\tstr_offset += 1;");
                #Now copy the new string
                self.f.write("\tdata->%s = strndup(((char *)(buffer+%d+str_offset)), str_len);\n" % (name, offset))
                #Adjust the offset due to the string
                self.f.write("\tstr_offset += str_len;\n\n")

        #Did the user specify a binary footer?. 
        #If so, write and check it
        if self.parser.binary_footer:
            if self.parser.binary_footer[0] == "magic":
                assignment = self._unpack_from_buffer(
                                    "int",
                                    dest="data->footer_magic",
                                    source_pointer="buffer+%d+str_offset" % offset)
                self.f.write("\n\t%s;\n" % assignment)
                self.f.write("\tif (data->footer_magic != %s) return %s;\n" % (
                                    self.parser.binary_footer[1],
                                    self._get_error_define(self.parser.ERROR_FOOTER_MAGIC)))
            offset += TYPE_SIZE_MAP["int"] #magic number is an integer

        self.f.write("\n\treturn %d+str_offset;\n" % offset)
        self.f.write("}\n")

    def write_footer(self):
        pass


class CHeaderWriter(CWriter):
    def write_header(self, filename):
        self.f.write("#ifndef _%s_\n#define _%s_\n" % (self.name.upper(),self.name.upper()))
        self.f.write("// Autogenerated file, do no edit\n\n")
        self.f.write("#include <inttypes.h>\n")
        self.f.write("#include <stdlib.h>\n")
        self.f.write("#include <stdio.h>\n")
        self.f.write("#ifndef __USE_GNU\n")
        self.f.write("#define __USE_GNU\n")
        self.f.write("#endif\n")
        self.f.write("#include <string.h>\n")

        #write all the endianess conversion macros
        if self.endian == "network":
            self.f.write(byte_conversions.header)
            if self.include_convert_macros:
                self.f.write(byte_conversions.custom_conversion_funtions)
            else:
                self.f.write(byte_conversions.system_conversion_functions)

        #so we can be included from c++ code
        self.f.write("\n#ifdef __cplusplus\n")
        self.f.write("extern \"C\"\n")
        self.f.write("{\n")
        self.f.write("#endif\n")

        #write the #defines for the error constants
        self.f.write("\n")
        for err in self.parser.get_errors():
            self.f.write("#define %s %d\n" % (self._get_error_define(err), err))
        
        #calculate the maximum size of buffer needed to hold the struct
        max_size = 0
        for chunk in self.parser.parse_tree:
            type, name = self.parser.get_chunk_info(chunk)
            if type in ("float", "double", "int", "bool"):
                max_size += TYPE_SIZE_MAP[type]
            elif type == "string":
                #strings are max 255 chars, + 1 size byte long
                max_size += 256

        if self.parser.binary_header:
            max_size += TYPE_SIZE_MAP["int"] #magic number is an integer

        if self.parser.binary_footer:
            max_size += TYPE_SIZE_MAP["int"] #magic number is an integer
        self.f.write("\n#define %s_MAX_SIZE %s\n" % (self.name.upper(), max_size))
        
        #defines for the header and footer magic
        if self.parser.binary_header:
            self.f.write("#define %s_HEADER_MAGIC %s\n" % (self.name.upper(), self.parser.binary_header[1]))
        if self.parser.binary_footer:
            self.f.write("#define %s_FOOTER_MAGIC %s\n" % (self.name.upper(), self.parser.binary_footer[1]))

        #can we pack/unpack strings
        self.f.write("#define %s_CAN_HANDLE_STRINGS %s\n" % (self.name.upper(), int(self.parser.has_strings)))

    def write_struct(self):
        self.f.write("\ntypedef struct {\n")

        #Did the user specify a binary header?
        if len(self.parser.binary_header) != 0:
            self.f.write("\tint header_%s;\n" % self.parser.binary_header[0]);

        self.f.write("\n")
        for chunk in self.parser.parse_tree:
            #Get chunks type and name
            type, name = self.parser.get_chunk_info(chunk)
            #Write the struct member definition                
            self.f.write("\t%s %s;\t// %s\n" % (CPP_TO_C_TYPE_MAP[type], name, chunk["node"]))

        #Did the user specify a binary footer?
        if len(self.parser.binary_footer) != 0:
            self.f.write("\n\tint footer_%s;\n" % self.parser.binary_footer[0]);

        self.f.write("} %s;\n" % self.name)

    def write_print_function(self):
        self.f.write("\n%s;\n" % self._get_print_function_name())

    def write_csv_functions(self):
        self.f.write("\n%s;\n" % self._get_print_csv_header_function_name())
        self.f.write("\n%s;\n" % self._get_print_csv_line_function_name())

    def write_pack_functions(self):
        self.f.write("\n%s;\n" % self._get_pack_function_name())

    def write_unpack_function(self):
        self.f.write("\n%s;\n" % self._get_unpack_function_name())

    def write_footer(self):
        #so we can be included from c++ code
        self.f.write("\n#ifdef __cplusplus\n")
        self.f.write("}\n")
        self.f.write("#endif\n")
        self.f.write("\n#endif // _%s_\n" % self.name.upper())
