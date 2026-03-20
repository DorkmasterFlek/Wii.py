import array
import fnmatch
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import wave

try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2
    from urllib2 import urlopen

from Crypto.Cipher import AES


def align(x, boundary):
    while x % boundary != 0:
        x += 1
    return x

def clamp(var, min, max):
    if var < min: var = min
    if var > max: var = max
    return var

def abs(var):
    if var < 0:
        var = var + (2 * var)
    return var

def hexdump(s, sep=" "): # just dumps hex values
    if s and isinstance(s[0], int):
        return sep.join(["%02x" % x for x in s])
    else:
        return sep.join(["%02x" % ord(x) for x in s])

def hexdump2(src, length = 16): # dumps to a "hex editor" style output
    result = []
    for i in range(0, len(src), length):
        s = src[i:i + length]
        if(len(s) % 4 == 0):
            mod = 0
        else:
            mod = 1
        hexa = ''
        for j in range((len(s) // 4) + mod):
            if s and isinstance(s[0], int):
                hexa += ' '.join(["%02X" % x for x in s[j * 4:j * 4 + 4]])
            else:
                hexa += ' '.join(["%02X" % ord(x) for x in s[j * 4:j * 4 + 4]])
            if(j != ((len(s) // 4) + mod) - 1):
                hexa += '  '
        printable = s.translate(''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)]))
        result.append("0x%04X   %-*s   %s\n" % (i, (length * 3) + 2, hexa, printable))
    return ''.join(result)

class Crypto(object):
    """This is a Cryptographic/hash class used to abstract away things (to make changes easier)"""
    align = 64

    def decryptData(self, key, iv, data, align = True):
        """Decrypts some data (aligns to 64 bytes, if needed)."""
        if((len(data) % self.align) != 0 and align):
            return AES.new(key, AES.MODE_CBC, iv).decrypt(data + (b"\x00" * (self.align - (len(data) % self.align))))
        else:
            return AES.new(key, AES.MODE_CBC, iv).decrypt(data)
    decryptData = classmethod(decryptData)

    def encryptData(self, key, iv, data, align = True):
        """Encrypts some data (aligns to 64 bytes, if needed)."""
        if((len(data) % self.align) != 0 and align):
            return AES.new(key, AES.MODE_CBC, iv).encrypt(data + (b"\x00" * (self.align - (len(data) % self.align))))
        else:
            return AES.new(key, AES.MODE_CBC, iv).encrypt(data)
    encryptData = classmethod(encryptData)

    def decryptContent(self, titlekey, idx, data):
        """Decrypts a Content."""
        iv = struct.pack(">H", idx) + b"\x00" * 14
        return self.decryptData(titlekey, iv, data)
    decryptContent = classmethod(decryptContent)

    def decryptTitleKey(self, commonkey, tid, enckey):
        """Decrypts a Content."""
        iv = struct.pack(">Q", tid) + b"\x00" * 8
        return self.decryptData(commonkey, iv, enckey, False)
    decryptTitleKey = classmethod(decryptTitleKey)

    def encryptContent(self, titlekey, idx, data):
        """Encrypts a Content."""
        iv = struct.pack(">H", idx) + b"\x00" * 14
        return self.encryptData(titlekey, iv, data)
    encryptContent = classmethod(encryptContent)

    def createSHAHash(self, data): #tested WORKING (without padding)
        return hashlib.sha1(data).digest()
    createSHAHash = classmethod(createSHAHash)

    def createSHAHashHex(self, data):
        return hashlib.sha1(data).hexdigest()
    createSHAHashHex = classmethod(createSHAHashHex)

    def createMD5HashHex(self, data):
        return hashlib.md5(data).hexdigest()
    createMD5HashHex = classmethod(createMD5HashHex)

    def createMD5Hash(self, data):
        return hashlib.md5(data).digest()
    createMD5Hash = classmethod(createMD5Hash)

    def validateSHAHash(self, data, hash):
        contentHash = hashlib.sha1(data).digest()
        return 1
    validateSHAHash = classmethod(validateSHAHash)

class WiiObject(object):
    def load(cls, data, *args, **kwargs):
        self = cls()
        self._load(data, *args, **kwargs)
        return self
    load = classmethod(load)

    def loadFile(cls, filename, *args, **kwargs):
        return cls.load(open(filename, "rb").read(), *args, **kwargs)
    loadFile = classmethod(loadFile)

    def dump(self, *args, **kwargs):
        return self._dump(*args, **kwargs)
    def dumpFile(self, filename, *args, **kwargs):
        open(filename, "wb").write(self.dump(*args, **kwargs))
        return filename

class WiiArchive(WiiObject):
    def loadDir(cls, dirname):
        self = cls()
        self._loadDir(dirname)
        return self
    loadDir = classmethod(loadDir)

    def dumpDir(self, dirname):
        if(not os.path.isdir(dirname)):
            os.mkdir(dirname)
        self._dumpDir(dirname)
        return dirname

class WiiHeader(object):
    def __init__(self, data):
        self.data = data
    def addFile(self, filename):
        open(filename, "wb").write(self.add())
    def removeFile(self, filename):
        open(filename, "wb").write(self.remove())
    def loadFile(cls, filename, *args, **kwargs):
        return cls(open(filename, "rb").read(), *args, **kwargs)
    loadFile = classmethod(loadFile)


