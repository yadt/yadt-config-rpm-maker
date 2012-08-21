#!/usr/bin/env python
import os

from setuptools import setup, find_packages
import sys

sys.path.append('src')

os.environ['TEST_CONFIG_FILE'] = 'test_config.yaml'
os.environ['YADT_CONFIG_RPM_MAKER_CONFIG_FILE'] = 'dev_config.yaml'

setup(
    name = "yadt-config-rpm-maker",
    version = "2.0",
    license = "GPL",
    url = "http://code.google.com/p/yadt",
    packages = find_packages(),
    test_suite = 'test',
)
