# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

import unittest
from yar.devices.prefixes import prefixes

class PrefixesTest(unittest.TestCase):

    def test_get_mfgrs(self):
        self.assertEqual(prefixes.get_mfgrs("sn"), set(['TEX', 'MOT']))

    def test_get_prefixes(self):
        self.assertEqual(
            prefixes.get_prefixes("TEX"),
            ('mc', 'ne', 'op', 'rc', 'sg', 'sn', 'tpbpal', 'til',
             'tip', 'tipal', 'tis', 'tl', 'tlc', 'tle', 'tm',
             'tms', 'ua', 'uln'))


if __name__ == '__main__':
    unittest.main()
