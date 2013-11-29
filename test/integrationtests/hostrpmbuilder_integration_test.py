# coding=utf-8
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

import os

from os.path import join
from integration_test_support import IntegrationTest

from config_rpm_maker.hostrpmbuilder import (CouldNotTarConfigurationDirectoryException,
                                             CouldNotBuildRpmException,
                                             ConfigDirAlreadyExistsException,
                                             HostRpmBuilder)
from config_rpm_maker.config import build_config_viewer_host_directory


class HostRpmBuilderIntegrationTest(IntegrationTest):

    def test_should_write_revision_file(self):

        svn_service_queue = self.create_svn_service_queue()
        hostname = "berweb01"
        revision = '1'
        host_rpm_builder = HostRpmBuilder(thread_name="Thread-0",
                                          hostname=hostname,
                                          revision=revision,
                                          work_dir=self.temporary_directory,
                                          svn_service_queue=svn_service_queue)

        host_rpm_builder.build()

        temporary_path_of_revision_file = join(build_config_viewer_host_directory(hostname, revision=revision), hostname + '.rev')
        self.assert_path_exists(temporary_path_of_revision_file)
        self.assert_file_content(temporary_path_of_revision_file, revision)

    def test_should_raise_ConfigDirAlreadyExistsException(self):

        fake_host_directory = os.path.join(self.temporary_directory, 'yadt-config-fakehost')
        if not os.path.exists(fake_host_directory):
            os.makedirs(fake_host_directory)

        host_rpm_builder = HostRpmBuilder(thread_name="Thread-0",
                                          hostname="fakehost",
                                          revision='123',
                                          work_dir=self.temporary_directory,
                                          svn_service_queue={})

        self.assertRaises(ConfigDirAlreadyExistsException, host_rpm_builder.build)

    def test_should_raise_CouldNotTarConfigurationDirectoryException(self):

        svn_service_queue = self.create_svn_service_queue()

        host_rpm_builder = HostRpmBuilder(thread_name="Thread-0",
                                          hostname="--help berweb",
                                          revision='1',
                                          work_dir=self.temporary_directory,
                                          svn_service_queue=svn_service_queue)

        self.assertRaises(CouldNotTarConfigurationDirectoryException, host_rpm_builder.build)

    def test_should_raise_CouldNotBuildRpmException(self):

        svn_service_queue = self.create_svn_service_queue()

        host_rpm_builder = HostRpmBuilder(thread_name="Thread-0",
                                          hostname=" --help",
                                          revision='1',
                                          work_dir=self.temporary_directory,
                                          svn_service_queue=svn_service_queue)

        self.assertRaises(CouldNotBuildRpmException, host_rpm_builder.build)
