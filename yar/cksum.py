# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Checksumming utilities."""

from array import array

def file_to_bytes(fp, bs=4096):
    """Read a file into a byte array.

       fp MUST be opened in binary mode
       bs is the block size to read"""
    buf = array("B")
    try:
        buf.fromfile(fp, bs)
    except EOFError:
        pass
    return buf


def checksum(bytes):
    """Return the simple checksum of a sequence of bytes."""
    return reduce(lambda a, b: a + b % 2**16, bytes)
