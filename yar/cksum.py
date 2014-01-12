# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Checksumming utilities."""

def checksum(bytes):
    """Return the simple checksum of a sequence of bytes."""
    return reduce(lambda a, b: a + b % 2**16, bytes)
