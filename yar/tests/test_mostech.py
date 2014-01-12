# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

import unittest

from yar.mostech import MOSEncoder, MOSDecoder

class MOSCodecTest(unittest.TestCase):

    bytes = [0xf3, 0xed, 0x56, 0xc3, 0xe6, 0x00, 0xfd, 0x00,
             0x87, 0x30, 0x05, 0x24, 0xc3, 0x10, 0x00, 0x00,

             0x85, 0x6f, 0xd0, 0x24, 0xc9, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

    def test_codec(self):
        e = MOSEncoder()
        e.encode(self.bytes[0:16])
        e.encode(self.bytes[16:32])
        encd = e.finalize()

        d = MOSDecoder()
        for line in encd.split("\n"):
            d.decode(line)
        self.assertEqual(d.finalize().tolist(), self.bytes)


if __name__ == '__main__':
    unittest.main()
