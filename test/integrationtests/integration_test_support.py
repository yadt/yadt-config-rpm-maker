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

import shutil
import subprocess
import unittest

from os import makedirs
from os.path import abspath, exists, join

from config_rpm_maker import config
from config_rpm_maker.config import KEY_TEMPORARY_DIRECTORY


class IntegrationTestException(Exception):
    pass


class IntegrationTest(unittest.TestCase):

    def create_svn_repo(self):
        self._create_repository_directory()

        if subprocess.call('svnadmin create %s' % self.repo_dir, shell=True):
            raise IntegrationTestException('Could not create svn repo.')

        self.repo_url = 'file://%s' % self.repo_dir

        if subprocess.call('svn import -q -m import testdata/svn_repo %s' % self.repo_url, shell=True):
            raise IntegrationTestException('Could not import test data.')

        if subprocess.call('svn import -q -m import testdata/index.html %s/config/typ/web/data/index.html' % self.repo_url, shell=True):
            raise IntegrationTestException('Could not import test data.')

    def _create_repository_directory(self):

        print "Configuration is:"
        from pprint import pprint
        pprint(config.configuration)
        print "Configuration path is %s " % config.configuration_file_path
        print "Configuration path exists is %s" % str(exists(config.configuration_file_path))

        temporary_directory = config.get(KEY_TEMPORARY_DIRECTORY)
        self.repo_dir = abspath(join(temporary_directory, 'svn_repo'))

        if exists(self.repo_dir):
            shutil.rmtree(self.repo_dir)

        makedirs(self.repo_dir)
