# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

import unittest

import yar.devices.matcher as m
import yar.pak as pak

class DeviceSimilarTest(unittest.TestCase):

    devs = pak.load("unipak2b").DEVICES

    def test_similarity(self):
        self.assertEqual(100, m.similarity("am", "2732", self.devs[21]))
        self.assertTrue(m.similarity("am", "2732", self.devs[20]) < 100)

    def test_similar(self):

        ds = m.similar(self.devs, "am2732")[:10]
        self.assertEqual(ds, [('AMD', '2732', 'EPROM', 'DIP', 25, 36),
                              ('AMD', '2732A', 'EPROM', 'DIP', 39, 36),
                              ('AMD', '2732B', 'EPROM', 'DIP', 194, 36),
                              ('AMD', '27S32', 'PROM', 'DIP', 22, 56),
                              ('AMD', '9732', 'EPROM', 'DIP', 25, 36),
                              ('AMD', '1736', 'EEPROM', 'DIP', 295, 238),
                              ('AMD', '2708', 'EPROM', 'DIP', 33, 39),
                              ('AMD', '27128', 'EPROM', 'DIP', 175, 81),
                              ('AMD', '2716', 'EPROM', 'DIP', 25, 35),
                              ('AMD', '27512', 'EPROM', 'DIP', 221, 164)])


if __name__ == '__main__':
    unittest.main
