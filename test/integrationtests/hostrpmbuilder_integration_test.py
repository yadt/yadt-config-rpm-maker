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
import shutil
from Queue import Queue

from integration_test_support import IntegrationTest

from config_rpm_maker.hostrpmbuilder import (CouldNotTarConfigurationDirectoryException,
                                             CouldNotBuildRpmException,
                                             ConfigDirAlreadyExistsException,
                                             HostRpmBuilder)
from config_rpm_maker.svnservice import SvnService
from config_rpm_maker.config import KEY_SVN_PATH_TO_CONFIG, KEY_TEMPORARY_DIRECTORY
from config_rpm_maker import config


class HostRpmBuilderTest(IntegrationTest):

    def test_should_raise_ConfigDirAlreadyExistsException(self):
        host_rpm_builder = HostRpmBuilder(thread_name="abc", hostname="def", revision=1, work_dir="", svn_service_queue={})
        self.assertRaises(ConfigDirAlreadyExistsException, host_rpm_builder.build)

    def test_should_raise_CouldNotTarConfigurationDirectoryException(self):
        working_directory = self.refresh_temporary_directory()
        self.create_svn_repo()
        svn_service_queue = self.create_svn_service_queue()

        host_rpm_builder = HostRpmBuilder(thread_name="Thread-0",
                                          hostname="--help berweb",
                                          revision='1',
                                          work_dir=working_directory,
                                          svn_service_queue=svn_service_queue)

        self.assertRaises(CouldNotTarConfigurationDirectoryException, host_rpm_builder.build)

    def test_should_raise_CouldNotBuildRpmException(self):
        working_directory = self.refresh_temporary_directory()
        self.create_svn_repo()
        svn_service_queue = self.create_svn_service_queue()

        host_rpm_builder = HostRpmBuilder(thread_name="Thread-0",
                                          hostname=" --help",
                                          revision='1',
                                          work_dir=working_directory,
                                          svn_service_queue=svn_service_queue)

        self.assertRaises(CouldNotBuildRpmException, host_rpm_builder.build)

    def create_svn_service_queue(self):
        svn_service = SvnService(base_url=self.repo_url, username=None, password=None,
                                 path_to_config=config.get(KEY_SVN_PATH_TO_CONFIG))
        svn_service_queue = Queue()
        svn_service_queue.put(svn_service)
        return svn_service_queue

    def refresh_temporary_directory(self):
        working_directory = config.get(KEY_TEMPORARY_DIRECTORY)
        if os.path.exists(working_directory):
            shutil.rmtree(working_directory)
        os.makedirs(working_directory)
        return working_directory
