#!/usr/bin/python
#
#   yadt-config-rpm-maker
#   Copyright (C) 2011-2013 Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

from setuptools import setup, find_packages

SRC_DIR = 'src'

sys.path.append(SRC_DIR)

setup(name="yadt-config-rpm-maker",
      version="2.0",
      license="GPL",
      url="https://github.com/yadt/yadt-config-rpm-maker",
      author="Sebastian Herold",
      author_email="sebastian.herold@immobilienscout24.de",
      description="This program is called as a commit hook in a config SVN repository and automatically creates the necessary RPMs after every commit and puts them in the configured RPM repository.",
      keywords="rpm config host svn hook",

      entry_points={
          'console_scripts': ['config-rpm-maker = config_rpm_maker:mainMethod'],
      },
      setup_requires=[
          "flake8"
      ],
      packages=find_packages(where=SRC_DIR),
      package_dir={'': SRC_DIR},
      test_suite='tests')
