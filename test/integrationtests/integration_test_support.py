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

from Queue import Queue
from os import makedirs
from os.path import abspath, exists, join
from re import compile
from shutil import rmtree

from config_rpm_maker import configuration
from config_rpm_maker.svnservice import SvnService
from config_rpm_maker.configuration.properties import (is_no_clean_up_enabled,
                                                       get_temporary_directory,
                                                       get_svn_path_to_config)
from config_rpm_maker.configuration import build_config_viewer_host_directory

# This constant exists for debugging purposes.
# Switch this to True if you want to see the generated files after executing a test.
KEEP_TEMPORARY_DIRECTORY = False


class IntegrationTestException(Exception):
    pass


class IntegrationTest(unittest.TestCase):

    def setUp(self):
        configuration.set_property(is_no_clean_up_enabled, KEEP_TEMPORARY_DIRECTORY)
        temporary_directory = get_temporary_directory()
        self.clean_up_temporary_directory(temporary_directory)
        self.temporary_directory = temporary_directory
        self.create_svn_repo()

    def tearDown(self):

        self.clean_up_temporary_directory(self.temporary_directory)

    def create_empty_svn_repo(self):
        self._create_repository_directory()

        if subprocess.call('svnadmin create %s' % self.repository_directory, shell=True):
            raise IntegrationTestException('Could not create svn repo.')

        self.repo_url = 'file://%s' % self.repository_directory

    def create_svn_repo(self):
        self.create_empty_svn_repo()
        if subprocess.call('svn import -q -m import testdata/svn_repo %s' % self.repo_url, shell=True):
            raise IntegrationTestException('Could not import test data.')

        if subprocess.call('svn import -q -m import testdata/index.html %s/config/typ/web/data/index.html' % self.repo_url, shell=True):
            raise IntegrationTestException('Could not import test data.')

    def _create_repository_directory(self):

        self.repository_directory = abspath(join(self.temporary_directory, 'svn_repo'))

        if exists(self.repository_directory):
            shutil.rmtree(self.repository_directory)

        makedirs(self.repository_directory)

    def _given_config_rpm_maker(self, revision='2'):
        svn_service = SvnService(base_url=self.repo_url, path_to_config=get_svn_path_to_config())

        return ConfigRpmMaker(revision, svn_service)

    def write_revision_file_for_hostname(self, hostname, revision):

        config_viewer_host_directory = build_config_viewer_host_directory(hostname)

        if not exists(config_viewer_host_directory):
            makedirs(config_viewer_host_directory)

        revision_file_path = join(config_viewer_host_directory, '%s.rev' % hostname)
        with open(revision_file_path, "w") as revision_file:
            revision_file.write(revision)

    def assert_revision_file_contains_revision(self, hostname, revision):

        config_viewer_host_data = build_config_viewer_host_directory(hostname)
        error_message = 'Directory "%s" does not exist.' % config_viewer_host_data
        self.assertTrue(exists(config_viewer_host_data), error_message)

        revision_file_path = join(config_viewer_host_data, '%s.rev' % hostname)
        self.assert_file_content(revision_file_path, revision)

    def assert_file_content(self, path_to_file, expected_content):

        self.assert_path_exists(path_to_file)

        with open(path_to_file) as revision_file:
            actual_content = revision_file.read()

            error_message = """File "{path_to_file}" did not have expected content.
Expected: "{expected}"
 but was: "{actual}"
""".format(path_to_file=path_to_file, expected=expected_content, actual=actual_content)

            self.assertEqual(expected_content, actual_content, error_message)

    def assert_file_matches_content_line_by_line(self, path_to_file, expected_content):

        self.assert_path_exists(path_to_file)

        with open(path_to_file) as revision_file:
            actual_content = revision_file.read()

            expected_lines = expected_content.split('\n')
            actual_lines = actual_content.split('\n')

            line_number = 0
            for expected_line in expected_lines:
                actual_line = actual_lines[line_number]
                error_message = """File "{path_to_file}" did not have expected content in line {line_number} (white space is trimmed).
Expected: "{expected}"
 but was: "{actual}"
""".format(path_to_file=path_to_file, expected=expected_line, actual=actual_line, line_number=line_number + 1)

                pattern = expected_line.strip()
                string = actual_line.strip()

                regular_expression = compile(pattern)

                self.assertTrue(regular_expression.match(string), error_message)
                line_number += 1

    def create_svn_service_queue(self):
        svn_service = SvnService(base_url=self.repo_url, username=None, password=None,
                                 path_to_config=get_svn_path_to_config())
        svn_service_queue = Queue()
        svn_service_queue.put(svn_service)
        return svn_service_queue

    def assert_path_exists(self, path):
        self.assertTrue(exists(path), 'Path "%s" does not exist.' % path)

    def assert_path_does_not_exist(self, path):
        self.assertFalse(exists(path), 'Path "%s" should not exist!' % path)

    def clean_up_temporary_directory(self, temporary_directory):
        if not KEEP_TEMPORARY_DIRECTORY and exists(temporary_directory):
            rmtree(temporary_directory)


class IntegrationTestWithNonConfigCommitAndNoConfig(IntegrationTest):
    def setUp(self):
        configuration.set_property(is_no_clean_up_enabled, KEEP_TEMPORARY_DIRECTORY)
        temporary_directory = get_temporary_directory()
        self.clean_up_temporary_directory(temporary_directory)
        self.temporary_directory = temporary_directory
        self.create_empty_svn_repo()
        if subprocess.call('svn mkdir -q -m mkdir --parents  %s/XXXXXX/host/devweb01/' % self.repo_url, shell=True):
            raise IntegrationTestException('Could not import test data.')
