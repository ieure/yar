# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

import unittest

from yar.cksum import checksum

class ChecksumTest(unittest.TestCase):

    def test_checksum(self):
        self.assertEqual(checksum([1, 2]), 3)
        self.assertEqual(checksum([256, 256]), 512)
        self.assertEqual(checksum([65530, 16384]), 16378)


if __name__ == '__main__':
    unittest.main()
