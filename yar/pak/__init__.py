# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Pak support"""

def load(pak):
    """Load a Pak"""
    pkg_name = "yar.pak.%s" % pak
    try:
        return __import__(pkg_name, fromlist=[None])
    except ImportError, e:
        raise ImportError("Unsupported pak `%s'" % pak)
