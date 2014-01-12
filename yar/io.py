# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""IO functions"""

from array import array
from contextlib import closing
import zipfile

def file_to_bytes(inp, bs=4096):
    """Return an array of bytes read from inp."""
    buf = array("B")
    done = False
    while not done:
        temp = inp.read(bs)
        buf.fromstring(temp)
        done = len(temp) < bs
    return buf


def gen_fds(args, unzip=True):
    """Return a generator of tuples of (filename, fd) for the inputs.

       If unzip is set to False, ZIP files will be checksummed, rather
       than the files inside them."""
    for inpf in args:
        with open(inpf, "rb") as fd:
            if unzip and zipfile.is_zipfile(inpf):
                yield gen_zip_fds(inpf, fd)
            else:
                yield ((inpf, fd),)


def gen_zip_fds(inpf, fd):
    """Return a generator of (filename, fd).

       The generator returns the files inside the ZIP archive.
    """
    with closing(zipfile.ZipFile(fd)) as zfd:
        for zfn in zfd.namelist():
            with closing(zfd.open(zfn)) as fd:
                yield ("%s:%s" % (inpf, zfn), fd)
