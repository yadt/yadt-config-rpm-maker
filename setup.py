#!/usr/bin/env python
import os

from setuptools import setup, find_packages
import sys

os.environ['TEST_CONFIG_FILE'] = 'test_config.yaml'
os.environ['YADT_CONFIG_RPM_MAKER_CONFIG_FILE'] = 'dev_config.yaml'

SRC_DIR = 'src'

sys.path.append(SRC_DIR)

setup(
    name = "yadt-config-rpm-maker2",
    version = "2.0",
    license = "GPL",
    url = "https://github.com/yadt/yadt-config-rpm-maker",
    packages=find_packages(where=SRC_DIR),
    package_dir = {'': SRC_DIR},
    test_suite = 'test',

    author = "Sebastian Herold",
    author_email = "sebastian.herold@immobilienscout24.de",

    description = "This program is called as a commit hook in a config SVN repository and automatically creates the necessary RPMs after every commit and puts them in the configured RPM repository.",
    keywords= "rpm config host svn hook",

    entry_points={
        'console_scripts': [
            'config-rpm-maker2 = config_rpm_maker:mainMethod',
            ],
    },
)
