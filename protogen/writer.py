class Writer:
    def __init__(self, parser, f, name, endian, include_convert_macros):
        self.parser = parser
        self.f = f
        self.name = name
        self.endian = endian
        self.include_convert_macros = include_convert_macros

    def write_header(self, filename):
        raise NotImplementedError

    def write_struct(self):
        raise NotImplementedError

    def write_print_function(self):
        raise NotImplementedError

    def write_csv_functions(self):
        raise NotImplementedError

    def write_pack_functions(self):
        raise NotImplementedError

    def write_unpack_function(self):
        raise NotImplementedError

    def write_footer(self):
        raise NotImplementedError
