# From: http://mathieu.fenniak.net/import-zlib-vs-net-framework/

import System
from System import IO, Collections, Array

Z_SYNC_FLUSH = 2

def _string_to_bytearr(buf):
    retval = Array.CreateInstance(System.Byte, len(buf))
    for i in range(len(buf)):
        retval[i] = ord(buf[i])
    return retval

def _bytearr_to_string(bytes):
    retval = ""
    for i in range(bytes.Length):
        retval += chr(bytes[i])
    return retval

def _read_bytes(stream):
    ms = IO.MemoryStream()
    buf = Array.CreateInstance(System.Byte, 2048)
    while True:
        bytes = stream.Read(buf, 0, buf.Length)
        if bytes == 0:
            break
        else:
            ms.Write(buf, 0, bytes)
    retval = ms.ToArray()
    ms.Close()
    return retval

def decompress(data):
    bytes = _string_to_bytearr(data)
    ms = IO.MemoryStream()
    ms.Write(bytes, 0, bytes.Length)
    ms.Position = 0  # fseek 0
    gz = IO.Compression.DeflateStream(ms, IO.Compression.CompressionMode.Decompress)
    bytes = _read_bytes(gz)
    retval = _bytearr_to_string(bytes)
    gz.Close()
    return retval

def compress(data):
    bytes = _string_to_bytearr(data)
    ms = IO.MemoryStream()
    gz = IO.Compression.DeflateStream(ms, IO.Compression.CompressionMode.Compress, True)
    gz.Write(bytes, 0, bytes.Length)
    gz.Close()
    ms.Position = 0 # fseek 0
    bytes = ms.ToArray()
    retval = _bytearr_to_string(bytes)
    ms.Close()
    return retval

