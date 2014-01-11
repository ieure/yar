# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

import unittest

from yar.control import Control

class ErrorDecodeTest(unittest.TestCase):

    def test_error_decoding(self):
        c = Control(None)

        print c.decode_errors(0x80C80081)


if __name__ == '__main__':
    unittest.main()
