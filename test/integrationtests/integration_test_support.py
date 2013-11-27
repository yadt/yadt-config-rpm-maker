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
from config_rpm_maker.hostrpmbuilder import HostRpmBuilder


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

        temporary_directory = config.get(KEY_TEMPORARY_DIRECTORY)
        self.repo_dir = abspath(join(temporary_directory, 'svn_repo'))

        if exists(self.repo_dir):
            shutil.rmtree(self.repo_dir)

        makedirs(self.repo_dir)

    def assert_revision_file_contains_revision(self, hostname, revision):

        config_viewer_host_data = HostRpmBuilder.get_config_viewer_host_dir(hostname)
        error_message = 'Directory "%s" does not exist.' % config_viewer_host_data
        self.assertTrue(exists(config_viewer_host_data), error_message)

        revision_file_path = join(config_viewer_host_data, '%s.rev' % hostname)
        self.assert_file_content(revision_file_path, revision)

    def assert_file_content(self, path_to_file, expected_content):

        self.assertTrue(exists(path_to_file))

        with open(path_to_file) as revision_file:
            actual_content = revision_file.read()
            error_message = """File "{path_to_file}" did not have expected content.
Expected content: {expected_content}
  Actual content: {actual_content}
""".format(path_to_file=path_to_file, expected_content=expected_content, actual_content=actual_content)
            self.assertEqual(expected_content, actual_content, error_message)


