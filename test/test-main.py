import test

if __name__ == "__main__":
    i = int(1)
    f = float(1.23)
    d = float(4.56)
    s = "hello";
    c = int(1);
    
    t = test.test()

    ############################################################################
    # Pack
    ############################################################################
    buf = t.pack_into_buffer(
                    float_value=f,
                    double_value=d,
                    int_value=i,
                    bool_value=c,
                    another_float_value=f)
    #array init for C test prog
    init = "{"
    init += ','.join(["0x%02X" % ord(b) for b in buf])
    init += "};"
    print "Python Packed OK\n\n",init
      
    ############################################################################
    # Pack
    ############################################################################
    data = t.unpack_from_buffer(buf)
    print "Python Unpacked OK\n",data
