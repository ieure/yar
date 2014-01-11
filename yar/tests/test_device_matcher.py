# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

import unittest

import yar.devices.matcher as m
from yar.devices.unipak2b import DEVICES

class DeviceMatcherTest(unittest.TestCase):

    def test_extract(self):
        self.assertEqual(("am", "2732dc"),
                         m.extract("am2732dc").groups())
        self.assertEqual(("am", "2732dc"),
                         m.extract("am 2732 dc").groups())
        self.assertEqual(("am", "2732dc"),
                         m.extract("  am 2732 dc  ").groups())

    def test_matches(self):
        print m.matches(DEVICES, "am2732dc")

    def test_match(self):
        self.assertRaises(ValueError, m.match, DEVICES, "am2732dc")
        self.assertEqual((0x19, 0x24), m.match(DEVICES, "am2732"))
        self.assertRaises(ValueError, m.match, DEVICES, "2732")


if __name__ == '__main__':
    unittest.main
