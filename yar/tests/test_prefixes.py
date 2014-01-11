# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

import unittest
from yar.devices.prefixes import prefixes

class PrefixesTest(unittest.TestCase):

    def test_get_mfgrs(self):
        print prefixes.get_mfgrs("sn")

    def test_get_prefixes(self):
        print prefixes.get_mfgrs("TEX")

if __name__ == '__main__':
    unittest.main()
