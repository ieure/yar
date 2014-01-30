# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure
#

from setuptools import setup, find_packages
# Dumb bug https://groups.google.com/forum/#!msg/nose-users/fnJ-kAUbYHQ/ngz3qjdnrioJ
import multiprocessing

setup(name="yar",
      version="0.1.0",
      packages=find_packages(),
      tests_require=['nose'],
      install_requires=["pyserial==2.7"],
      test_suite="nose.collector",
      entry_points = {
          'console_scripts': [
              'yar = yar.cli:main'
          ]
      })
