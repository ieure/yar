# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""IO functions"""

from array import array
from contextlib import closing
import zipfile
import time

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


class Progress():

    """An object representing progress."""

    _start = 0                  # Time the process started
    _finish = None              # Time the process finished
    _bytes = 0                  # Bytes to process
    _done = 0                   # Bytes processed

    def __init__(self, bytes):
        self._bytes = bytes

    def start(self):
        """Start processing"""
        self._start = time.time()

    def complete(self):
        self._finish = time.time()

    def update(self, processed):
        """Update the number of bytes processed."""
        if self._start == 0:
            self._start = time.time()
        self._done = processed

    def bytes_sec(self):
        return self._done / (time.time() - self._start)

    def percent_done(self):
        return int((float(self._done) / self._bytes) * 100)

    def eta(self):
        msecs_rem = (self._bytes - self._done) / self.bytes_sec()
        return (msecs_rem / 60, msecs_rem % 60)

    def __repr__(self):
        args = (self._done, self._bytes, self.percent_done(),
                self.bytes_sec()) + self.eta()
        return "[%d/%d] bytes, %02d%% @%db/s, eta %dm%02ds" % args
