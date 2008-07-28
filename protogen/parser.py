try:
    from elementtree import ElementTree
except:
    from xml.etree import ElementTree

class XMLProtocolParser:

    TOP_TAG = "PropertyList"
    MID_TAG = "generic"
    PARENT_TAGS = ("output","input")

    ERROR_HEADER_MAGIC      = -1
    ERROR_FOOTER_MAGIC      = -2
    ERROR_HEADER_SIZE       = -3
    ERROR_FOOTER_SIZE       = -4
    ERROR_HEADER_CHECKSUM   = -5
    ERROR_FOOTER_CHECKSUM   = -6

    PARSE_ERRORS = {
        #value                  :   (name, description)
        ERROR_HEADER_MAGIC :        ("HEADER_MAGIC",    "Incorrect Header Magic Number"),
        ERROR_FOOTER_MAGIC :        ("FOOTER_MAGIC",    "Incorrect Header Magic Number"),
        ERROR_HEADER_SIZE :         ("HEADER_SIZE",     "Incorrect Header Size"),
        ERROR_FOOTER_SIZE :         ("FOOTER_SIZE",     "Incorrect Footer Size"),
        ERROR_HEADER_CHECKSUM :     ("HEADER_CHECKSUM", "Incorrect Header Checksum"),
        ERROR_FOOTER_CHECKSUM :     ("FOOTER_CHECKSUM", "Incorrect Footer Checksum")
    }

    def __init__(self, xml_file, lowercase, enable_strings, use_doubles):
        self.xml_file = xml_file
        self.reversed = True
        self.parse_tree=[]

        self.binary_mode = False
        self.binary_footer = []
        self.binary_header = []
        
        self.lowercase = lowercase
        self.enable_strings = enable_strings
        self.use_doubles = use_doubles

        self.has_strings = False

    def _fix_ordering(self):
        #Need to reverse the parsed tree once so that the struct is in the 
        #same order as the xml file.
        if self.reversed == True:
            self.parse_tree.reverse()
            self.reversed = False

    # Recursively parse XML file, building a parse tree
    def _parse(self, element, parent):
        #Check for binary mode stuff
        if parent.tag in self.PARENT_TAGS and element.tag == "binary_mode":
            self.binary_mode = True
        if parent.tag in self.PARENT_TAGS and element.tag == "binary_header":
            self.binary_header = element.text.strip().split(',')
        if parent.tag in self.PARENT_TAGS and element.tag == "binary_footer":
            self.binary_footer = element.text.strip().split(',')

        if parent.tag in self.PARENT_TAGS and element.tag == "chunk":
            self.parse_tree.insert(0, {"name":"", "type":"", "node":""})

        if element.text:
            text = element.text.strip()
            if text != "":
                if element.tag == "name":
                    self.parse_tree[0]["name"] = text
                elif element.tag == "type":
                    if self.use_doubles and text == "float":
                        text = "double"
                    self.parse_tree[0]["type"] = text
                elif element.tag == "node":
                    self.parse_tree[0]["node"] = text
                
        for child in element.getchildren():
            self.parse_tree = self._parse(child, element)

        return self.parse_tree

    # Returns the chunks type and name according to the 
    # lowercase option
    # @returns: a 2-tuple (type, name)
    def get_chunk_info(self, chunk):
        # Rename types
        type = chunk["type"]

        if self.lowercase:
            name = chunk["name"].lower()
        else:
            name = chunk["name"]

        return type, name

    def parse_protocol_file(self):
        # Open the file, check it has the "self.TOP_TAG/self.MID_TAG/output"
        root = ElementTree.ElementTree(file=self.xml_file).getroot()
        if root == None or root.tag != self.TOP_TAG:
            raise Exception("File is not a property list")

        # Get the input/output section
        io_sec = None
        for sn in ["%s/%s" % (self.MID_TAG, i) for i in self.PARENT_TAGS]:
            io_sec = root.find(sn)
            if io_sec:
                break 
        
        if io_sec == None:
            raise Exception("File has no %s/%s section" % (self.MID_TAG, self.PARENT_TAGS))
        
        # Parse the file
        self._parse(io_sec, io_sec)

        if not self.binary_mode:
            raise Exception("Only binary mode XML files are supported")

        # Only support strings if explicitly enabled
        for chunk in self.parse_tree[:]:
            if chunk["type"] == "string":
                if self.enable_strings:
                    self.has_strings = True
                else:
                    self.parse_tree.remove(chunk)

        # Reverse the list because when we built the tree we 
        # inserted everything into position 0
        self._fix_ordering()

    def get_errors(self):
        return self.PARSE_ERRORS.keys()

    def get_error_name(self, errorid):
        return self.PARSE_ERRORS[errorid][0]

    def get_error_description(self, errorid):
        return self.PARSE_ERRORS[errorid][1]


