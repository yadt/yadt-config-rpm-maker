#!/usr/bin/env python
#
# yadt-config-rpm-maker
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

SOURCE_DIRECTORY = 'src'
PATH_TO_VERSION_FILE = '{source_directory}/config_rpm_maker/version.py'.format(source_directory=SOURCE_DIRECTORY)

sys.path.append(SOURCE_DIRECTORY)

with open(PATH_TO_VERSION_FILE) as version_file:
    file_content = version_file.read()
    code = compile(file_content, PATH_TO_VERSION_FILE, 'exec')
    exec(code)

setup(name="yadt-config-rpm-maker",
      version=__version__,
      license="GPL",
      url="https://github.com/yadt/yadt-config-rpm-maker",
      author="Sebastian Herold",
      author_email="sebastian.herold@immobilienscout24.de",
      description="This program is called as a commit hook in a config SVN repository and automatically creates the necessary RPMs after every commit and puts them in the configured RPM repository.",
      keywords="rpm config host svn hook",

      entry_points={'console_scripts': ['config-rpm-maker = config_rpm_maker:main']},
      packages=find_packages(where=SOURCE_DIRECTORY),
      package_dir={'': SOURCE_DIRECTORY},
      test_suite='test')
