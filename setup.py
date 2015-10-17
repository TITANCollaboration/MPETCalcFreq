#!/usr/bin/env python
from setuptools import setup

setup(name='CalcFreq',
      version='1.0',
      packages=["calcFreq"],
      package_data={'calcFreq': ['data/*.dat']},
      author="Aaron Gallant",
      author_email="agallant@triumf.ca",
      description="Module to calculate ion frequencies",
      )
