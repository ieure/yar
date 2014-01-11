# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

import unittest

from yar.control import decode_errors

class ErrorDecodeTest(unittest.TestCase):

    def test_error_decoding(self):

        self.assertEqual(
            decode_errors(0x80C80081),
            "Error: Programming error Start line not set high Device not blank RAM error RAM end not on 1K boundary")

if __name__ == '__main__':
    unittest.main()
