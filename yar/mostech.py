# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""MOS codecs"""

import array
from yar.cksum import checksum

def sum(self, bytes):
    return reduce(lambda a, b: a + b % 2**256, bytes)

class MOSEncoder():

    record = 0
    record_size = 16
    rolling_sum = 0
    eol = "\n"
    next_final = False
    lines = []

    def __init__(self, record_size=16, eol="\n"):
        self.record_size = record_size
        self.eol = eol

    def encode(self, object):
        rs = len(object)
        addr = self.record * self.record_size
        bytes = "".join(["%02x" % b for b in object])
        cksum = checksum([rs, addr] + object)
        self.rolling_sum = checksum([self.rolling_sum, cksum])
        self.record += 1
        self.lines.append(";%02x%04x%s%04x" % (rs, addr, bytes, cksum))

    def finalize(self):
        self.lines.append(';00%04x%04x' % (self.record, self.rolling_sum))
        return self.eol.join(self.lines)


class MOSDecoder():

    record = 0
    sum = 0
    buf = array.array("B")

    def decode(self, object):
        if object[0] != ';':
            raise ValueError("Invalid input")

        rlen = int(object[1:3], 16)

        if rlen == 0:
            # Validate, end of input
            # FIXME
            return

        (_addr, _bytes, _ck) = (object[3:7],
                                object[7:7+rlen*2],
                                object[7+rlen*2:7+rlen*2+4])

        addr = int(_addr, 16)
        cksum = int(_ck, 16)

        r = range(0, len(_bytes) + 2, 2)
        bytes = [int(_bytes[s:e], 16) for (s, e) in zip(r, r[1:])]
        rsum = checksum([rlen, addr] + bytes)
        if rsum != cksum:
            raise ValueError(
                "Checksum mismatch on line %d. Expected %04x, got %04x" %
                (self.record, cksum, rsum))
        self.record += 1
        self.sum = checksum([self.sum, rsum])
        self.buf.extend(bytes)

    def finalize(self):
        return self.buf
