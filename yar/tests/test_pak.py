# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

import unittest

import types
import yar.pak as pak


class PakTest(unittest.TestCase):

    def test_load(self):
        p = pak.load("unipak2b")
        self.assertTrue(isinstance(p, types.ModuleType))
        self.assertTrue(hasattr(p, 'DEVICES'))
        self.assertTrue(isinstance(p.DEVICES, tuple))


if __name__ == '__main__':
    unittest.main()
