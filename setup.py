# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure
#

from setuptools import setup, find_packages

setup(name="yar",
      version="0.0.1",
      packages=find_packages(),
      tests_require=['nose'],
      install_requires=["pyserial==2.7"],
      test_suite="nose.collector",
      entry_points = {
          'console_scripts': [
              'yar = yar.cli:main'
          ]
      })
